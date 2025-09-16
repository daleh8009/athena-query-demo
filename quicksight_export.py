import boto3
import streamlit as st
import re
import os
from datetime import datetime
import json

class QuickSightExporter:
    def __init__(self, config):
        # Set all attributes first
        self.account_id = config['aws_account_id']
        self.region = config['aws_region']
        self.database = config['glue_database']
        self.workgroup = config['athena_workgroup']
        
        # Streamlit Cloud: Try secrets (only if they actually exist and work)
        secrets_worked = False
        try:
            if hasattr(st, 'secrets') and 'aws' in st.secrets:
                # Test if we can actually access the secret values
                test_key = st.secrets['aws']['AWS_ACCESS_KEY_ID']
                if test_key:  # If we got here, secrets exist and work
                    self.quicksight = boto3.client(
                        'quicksight', 
                        region_name=config['aws_region'],
                        aws_access_key_id=st.secrets['aws']['AWS_ACCESS_KEY_ID'],
                        aws_secret_access_key=st.secrets['aws']['AWS_SECRET_ACCESS_KEY']
                    )
                    secrets_worked = True
        except:
            secrets_worked = False
        
        # Local: Use profiles (only if secrets didn't work)
        if not secrets_worked:
            if config['aws_account_id'] == '476169753480':
                # Account 2 - use brew-demo profile
                session = boto3.Session(profile_name='brew-demo')
                self.quicksight = session.client('quicksight', region_name=config['aws_region'])
            else:
                # Account 1 - use default profile
                self.quicksight = boto3.client('quicksight', region_name=config['aws_region'])

    def generate_dataset_name(self, user_prompt, query_description="", custom_name=None):
        """Generate a clean dataset name with format: dept_project_date_time"""
        if custom_name:
            # For custom names, preserve underscores and clean format
            clean_name = re.sub(r'[^a-zA-Z0-9_\s]', '', custom_name)
            clean_name = re.sub(r'\s+', '_', clean_name).strip().lower()[:30]
        else:
            # Use the corrected table name format
            clean_name = "executive_dashboard_detailed"
        
        # Add date and time for uniqueness (YYYYMMDD_HHMM format)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        return f"{clean_name}_{timestamp}"
    
    def generate_dataset_id(self, dataset_name):
        """Generate QuickSight-compatible dataset ID"""
        dataset_id = dataset_name.lower()
        dataset_id = re.sub(r'[^a-z0-9]', '-', dataset_id)
        dataset_id = re.sub(r'-+', '-', dataset_id)
        dataset_id = dataset_id.strip('-')[:128]
        return dataset_id
    
    def ensure_athena_datasource(self):
        """Ensure Athena data source exists in QuickSight"""
        datasource_id = "athena-enterprise-analytics"
        
        try:
            # Check if data source exists
            self.quicksight.describe_data_source(
                AwsAccountId=self.account_id,
                DataSourceId=datasource_id
            )
            return datasource_id
            
        except self.quicksight.exceptions.ResourceNotFoundException:
            # Create new Athena data source
            try:
                self.quicksight.create_data_source(
                    AwsAccountId=self.account_id,
                    DataSourceId=datasource_id,
                    Name="Enterprise Analytics - Athena",
                    Type="ATHENA",
                    DataSourceParameters={
                        'AthenaParameters': {
                            'WorkGroup': self.workgroup
                        }
                    }
                )
                return datasource_id
            except Exception as e:
                st.error(f"Failed to create Athena data source: {str(e)}")
                return None
    
    def create_dataset(self, dataset_id, dataset_name, sql_query):
        """Create QuickSight dataset with direct table reference"""
        datasource_id = self.ensure_athena_datasource()
        
        if not datasource_id:
            return None
            
        try:
            # For now, create a simple dataset pointing to the executive_dashboard_detailed table
            # This will be more reliable than CustomSql
            params = {
                'AwsAccountId': self.account_id,
                'DataSetId': dataset_id,
                'Name': dataset_name,
                'PhysicalTableMap': {
                    'executive-dashboard-table': {
                        'RelationalTable': {
                            'DataSourceArn': f"arn:aws:quicksight:{self.region}:{self.account_id}:datasource/{datasource_id}",
                            'Catalog': 'awsdatacatalog',
                            'Schema': self.database,
                            'Name': 'executive_dashboard_detailed',
                            'InputColumns': [
                                {'Name': 'contract_id', 'Type': 'STRING'},
                                {'Name': 'contract_name', 'Type': 'STRING'},
                                {'Name': 'vendor', 'Type': 'STRING'},
                                {'Name': 'value', 'Type': 'INTEGER'},
                                {'Name': 'status', 'Type': 'STRING'},
                                {'Name': 'end_date', 'Type': 'STRING'},
                                {'Name': 'department', 'Type': 'STRING'},
                                {'Name': 'compliance_status', 'Type': 'STRING'},
                                {'Name': 'performance_score', 'Type': 'INTEGER'},
                                {'Name': 'outstanding_balance', 'Type': 'INTEGER'},
                                {'Name': 'auto_renewal', 'Type': 'STRING'},
                                {'Name': 'contract_owner', 'Type': 'STRING'}
                            ]
                        }
                    }
                },
                'ImportMode': 'DIRECT_QUERY'
            }
            
            result = self.quicksight.create_data_set(**params)
            
            # Grant permissions to the current user so they can see the dataset
            try:
                self.quicksight.update_data_set_permissions(
                    AwsAccountId=self.account_id,
                    DataSetId=dataset_id,
                    GrantPermissions=[
                        {
                            'Principal': f"arn:aws:quicksight:{self.region}:{self.account_id}:user/default/Admin/dlholder-Isengard",
                            'Actions': [
                                'quicksight:DescribeDataSet',
                                'quicksight:DescribeDataSetPermissions', 
                                'quicksight:PassDataSet',
                                'quicksight:DescribeIngestion',
                                'quicksight:ListIngestions',
                                'quicksight:UpdateDataSet',
                                'quicksight:DeleteDataSet',
                                'quicksight:CreateIngestion',
                                'quicksight:CancelIngestion',
                                'quicksight:UpdateDataSetPermissions'
                            ]
                        }
                    ]
                )
            except Exception as e:
                st.warning(f"Dataset created but permission grant failed: {str(e)}")
            
            return result
            
        except Exception as e:
            st.error(f"Failed to create dataset: {str(e)}")
            return None
    
    def trigger_spice_ingestion(self, dataset_id):
        """Trigger SPICE ingestion for faster queries"""
        try:
            ingestion_id = f"ingestion-{int(datetime.now().timestamp())}"
            
            self.quicksight.create_ingestion(
                AwsAccountId=self.account_id,
                DataSetId=dataset_id,
                IngestionId=ingestion_id,
                IngestionType='FULL_REFRESH'
            )
            
        except Exception as e:
            st.warning(f"SPICE ingestion failed (dataset still usable): {str(e)}")
    
    def generate_quicksight_urls(self, dataset_id):
        """Generate QuickSight URLs for easy access"""
        base_url = f"https://{self.region}.quicksight.aws.amazon.com/sn"
        
        return {
            'dataset': f"{base_url}/start/data-sets",
            'create_analysis': f"{base_url}/start/analyses",
            'create_dashboard': f"{base_url}/start/dashboards", 
            'quicksight_home': f"{base_url}/start"
        }
    
    def export_to_quicksight(self, sql_query, user_prompt, query_description="", custom_name=None):
        """Main export function"""
        try:
            # Generate dataset details
            dataset_name = self.generate_dataset_name(user_prompt, query_description, custom_name)
            dataset_id = self.generate_dataset_id(dataset_name)
            
            # Create dataset
            result = self.create_dataset(dataset_id, dataset_name, sql_query)
            
            if result:
                urls = self.generate_quicksight_urls(dataset_id)
                
                return {
                    'success': True,
                    'dataset': {
                        'id': dataset_id,
                        'name': dataset_name,
                        'arn': result.get('Arn', '')
                    },
                    'urls': urls,
                    'message': f'Dataset "{dataset_name}" created successfully!'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create QuickSight dataset'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Export failed: {str(e)}'
            }

def render_quicksight_export_ui(sql_query, user_prompt, query_description="", config=None):
    """Render QuickSight export UI in Streamlit"""
    
    if not sql_query or not config:
        return
    
    st.markdown("---")
    
    # Dataset name customization
    st.markdown("### 📊 QuickSight Workflow")
    
    # Generate default name preview
    exporter = QuickSightExporter(config)
    default_name = exporter.generate_dataset_name(user_prompt, query_description)
    
    col_name, col_preview = st.columns([2, 1])
    with col_name:
        custom_dataset_name = st.text_input(
            "Dataset Name (optional):",
            placeholder="e.g., hr_analytics or finance_budget",
            help="Leave blank to use auto-generated name"
        )
    
    with col_preview:
        if custom_dataset_name:
            preview_name = exporter.generate_dataset_name("", "", custom_dataset_name)
        else:
            preview_name = default_name
        st.text_input("Preview:", value=preview_name, disabled=True)
    
    # Initialize session state for export status
    if 'qs_export_success' not in st.session_state:
        st.session_state.qs_export_success = False
        st.session_state.qs_urls = {}
    
    # Custom CSS for button colors
    st.markdown("""
    <style>
    /* Target all link buttons first */
    .stLinkButton > a {
        text-decoration: none !important;
        border-radius: 0.5rem !important;
        padding: 0.5rem 1rem !important;
        font-weight: 400 !important;
        border: 1px solid transparent !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }
    
    /* Black button for View Dataset (2nd column) */
    div[data-testid="column"]:nth-child(2) .stLinkButton > a {
        background-color: #1e1e1e !important;
        color: white !important;
        border-color: #1e1e1e !important;
    }
    
    div[data-testid="column"]:nth-child(2) .stLinkButton > a:hover {
        background-color: #333333 !important;
        border-color: #333333 !important;
    }
    
    /* Orange buttons for Create Analysis and Create Dashboard (3rd and 4th columns) */
    div[data-testid="column"]:nth-child(3) .stLinkButton > a,
    div[data-testid="column"]:nth-child(4) .stLinkButton > a {
        background-color: #ff6b35 !important;
        color: white !important;
        border-color: #ff6b35 !important;
    }
    
    div[data-testid="column"]:nth-child(3) .stLinkButton > a:hover,
    div[data-testid="column"]:nth-child(4) .stLinkButton > a:hover {
        background-color: #e55a2b !important;
        border-color: #e55a2b !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create 4 equal columns for inline buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        export_button = st.button(
            "🚀 Export to QuickSight",
            type="primary",  # This keeps it red/pink as intended
            help="Create QuickSight dataset from executive_dashboard_detailed table",
            use_container_width=True,
            key="export_qs_btn"
        )
    
    with col2:
        if st.session_state.qs_export_success:
            st.markdown(f'''
            <a href="{st.session_state.qs_urls.get('dataset', '')}" target="_blank" 
               style="display: inline-flex; align-items: center; justify-content: center;
                      padding: 0.5rem 1rem; background-color: #1e1e1e; 
                      color: white; text-decoration: none; border-radius: 0.5rem; 
                      text-align: center; width: 100%; box-sizing: border-box;
                      height: 2.5rem; font-size: 0.875rem;">
                🗂️ View Dataset
            </a>
            ''', unsafe_allow_html=True)
        else:
            st.button("🗂️ View Dataset", disabled=True, help="Export first", use_container_width=True, key="view_dataset_btn")
    
    with col3:
        if st.session_state.qs_export_success:
            st.markdown(f'''
            <a href="{st.session_state.qs_urls.get('create_analysis', '')}" target="_blank" 
               style="display: inline-flex; align-items: center; justify-content: center;
                      padding: 0.5rem 1rem; background-color: #ff6b35; 
                      color: white; text-decoration: none; border-radius: 0.5rem; 
                      text-align: center; width: 100%; box-sizing: border-box;
                      height: 2.5rem; font-size: 0.875rem;">
                📈 Create Analysis
            </a>
            ''', unsafe_allow_html=True)
        else:
            st.button("📈 Create Analysis", disabled=True, help="Export first", use_container_width=True, key="create_analysis_btn")
    
    with col4:
        if st.session_state.qs_export_success:
            st.markdown(f'''
            <a href="{st.session_state.qs_urls.get('create_dashboard', '')}" target="_blank" 
               style="display: inline-flex; align-items: center; justify-content: center;
                      padding: 0.5rem 1rem; background-color: #ff6b35; 
                      color: white; text-decoration: none; border-radius: 0.5rem; 
                      text-align: center; width: 100%; box-sizing: border-box;
                      height: 2.5rem; font-size: 0.875rem;">
                📊 Create Dashboard
            </a>
            ''', unsafe_allow_html=True)
        else:
            st.button("📊 Create Dashboard", disabled=True, help="Export first", use_container_width=True, key="create_dashboard_btn")
    
    # Handle export
    if export_button:
        with st.spinner("🔄 Creating QuickSight dataset..."):
            result = exporter.export_to_quicksight(
                sql_query, 
                user_prompt, 
                query_description,
                custom_name=custom_dataset_name if custom_dataset_name else None
            )
        
        if result['success']:
            st.success(f"✅ {result['message']}")
            st.session_state.qs_export_success = True
            st.session_state.qs_urls = result['urls']
        else:
            st.error(f"❌ {result['message']}")
            st.session_state.qs_export_success = False

def render_quicksight_tips_sidebar():
    """Render QuickSight tips in the sidebar as expandable section"""
    with st.expander("💡 QuickSight Tips"):
        st.markdown("""
        **Dataset** - Manage refresh schedules and permissions
        
        **Analysis** - Best for data exploration and creating visualizations
        
        **Dashboard** - Best for sharing insights with stakeholders
        
        **Custom SQL** - Real-time querying against Athena data
        """)

def add_query_results_location_to_sidebar(config):
    """Add query results location to Account Details"""
    if config and 's3_results_bucket' in config:
        st.write(f"**Query Results:** `s3://{config['s3_results_bucket']}/`")

# Export the main function for use in your Streamlit app
__all__ = ['render_quicksight_export_ui', 'QuickSightExporter']
