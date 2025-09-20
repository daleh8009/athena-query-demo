import streamlit as st
import boto3
import pandas as pd
import time
from datetime import datetime
import os
from dotenv import load_dotenv
from quicksight_export import render_quicksight_export_ui, render_quicksight_tips_sidebar, add_query_results_location_to_sidebar

# Load environment variables
load_dotenv()

# Configuration selector
ACCOUNT_CONFIGS = {
    "Account 1 (695233770948)": {
        'aws_region': 'us-east-1',
        'aws_account_id': '695233770948',
        'athena_workgroup': 'primary',
        's3_results_bucket': 'aws-athena-query-results-us-east-1-695233770948',
        'glue_database': 's3-athena-glue-enterprise-analytics-db',
        's3_raw_data': 's3://s3-glue-athena-demo-archive/contracts/',
        'quicksight_account_id': '695233770948'
    },
    "Account 2 (476169753480)": {
        'aws_region': 'us-east-1',
        'aws_account_id': '476169753480',
        'athena_workgroup': 'primary',
        's3_results_bucket': 'aws-athena-query-results-us-east-1-476169753480',
        'glue_database': 's3-glue-athena-enterprise-analytics-db',
        's3_raw_data': 's3://s3-glue-athena-aidlc/contracts/',
        'quicksight_account_id': '476169753480'
    }
}

# Override with Streamlit secrets if available (for cloud deployment)
try:
    if 'config' in st.secrets:
        # Update Account 2 with secrets configuration
        ACCOUNT_CONFIGS["Account 2 (476169753480)"].update({
            'aws_region': st.secrets['config']['AWS_REGION'],
            'aws_account_id': st.secrets['config']['QUICKSIGHT_ACCOUNT_ID'],
            'athena_workgroup': st.secrets['config']['ATHENA_WORKGROUP'],
            's3_results_bucket': st.secrets['config']['S3_RESULTS_BUCKET'],
            'quicksight_account_id': st.secrets['config']['QUICKSIGHT_ACCOUNT_ID']
        })
except Exception:
    pass  # Use default configs if secrets not available

# Page configuration
st.set_page_config(
    page_title="Athena Query Generator - Modern",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simplified modern CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-header {
        background: rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .metric-card {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(5px);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #ff6b35, #f7931e);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def check_password():
    """Simple password protection for demo sharing - v2.1"""
    def password_entered():
        # Safe password check to prevent KeyError
        password_value = st.session_state.get("password", "")
        if password_value == "athena-demo-2024":
            st.session_state["password_correct"] = True
            # Clear password from state
            if "password" in st.session_state:
                del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # Initialize password state if not exists
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if not st.session_state["password_correct"]:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h2>🔐 Athena Query Generator</h2>
            <p>Enter password to access the demo</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show error only if password was attempted
        if "password_attempted" in st.session_state and st.session_state["password_attempted"]:
            st.error("❌ Incorrect password. Please try again.")
        
        password_input = st.text_input("Password", type="password", key="password_input", 
                     placeholder="Enter demo password")
        
        if st.button("Login", type="primary"):
            st.session_state["password_attempted"] = True
            if password_input == "athena-demo-2024":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.session_state["password_correct"] = False
                st.rerun()
        
        st.info("💡 Contact the administrator for access credentials")
        return False
    else:
        return True

def main():
    # Password protection - must be first
    try:
        if not check_password():
            st.stop()
        
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🚀 Athena Query Generator - Enterprise Edition</h1>
            <p style="margin: 0; opacity: 0.8;">Natural Language to SQL with QuickSight Integration</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        with st.sidebar:
            st.markdown("### 🔧 Configuration")
            
            # Combine default and user accounts
            user_accounts = load_user_accounts()
            all_accounts = {**ACCOUNT_CONFIGS, **user_accounts}
            
            selected_account = st.selectbox(
                "Select AWS Account:",
                list(all_accounts.keys()),
                index=1 if len(all_accounts) > 1 else 0
            )
            
            current_config = all_accounts[selected_account]
            st.session_state.current_config = current_config
            
            # Connection test
            if st.button("🔍 Test Connection", use_container_width=True):
                test_connection_status(current_config)
            
            # Account info
            with st.expander("📋 Account Details"):
                st.write(f"**Account:** {current_config['aws_account_id']}")
                st.write(f"**Database:** {current_config['glue_database']}")
                add_query_results_location_to_sidebar(current_config)
            
            # QuickSight Tips as separate expandable section
            render_quicksight_tips_sidebar()
            
            # Saved Queries section
            render_saved_queries_sidebar()
            
            # Account Management
            render_account_management()
            
            # Demo explanation
            with st.expander("ℹ️ Demo Information"):
                st.info("""
                **Multi-Account Demo:**
                
                • **Account 2**: Live data and full functionality
                • **Account 1**: UI demonstration (credential simulation)
                
                **Production Deployment:**
                • Cross-account IAM roles
                • Federated SSO access
                • True multi-account authentication
                
                **Local Demo**: Shows full multi-account capability
                """)
        
        # Main interface - Single page with better organization
        show_main_interface(current_config)
        
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please refresh the page and try again.")

def show_main_interface(config):
    """Main query interface with better workflow"""
    
    # Query Builder Section
    st.markdown("### 💬 Ask Your Question")
    
    # Example questions
    example_questions = [
        "Show me all contract data",
        "Show me the executive dashboard overview",
        "Display contracts up for renewal", 
        "Show compliance status across all contracts",
        "Which contracts are high risk?",
        "Show performance scores by department"
    ]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_example = st.selectbox("📝 Quick Questions:", [""] + example_questions)
        
        # Handle quick actions by setting default value
        default_question = ""
        if 'quick_question' in st.session_state:
            default_question = st.session_state.quick_question
            del st.session_state.quick_question
        elif selected_example:
            default_question = selected_example
        
        user_question = st.text_area(
            "What would you like to know?",
            value=default_question,
            placeholder="Example: Show me the executive dashboard overview",
            height=100,
            key="question_input"
        )
        
        # Data source selector
        available_tables = get_available_tables(config)
        if available_tables:
            # Predict what table/view would be auto-selected
            auto_selected = predict_data_source(user_question, available_tables) if user_question else "Auto-select based on question"
            
            data_source_options = ["🤖 Auto-select"] + available_tables
            selected_data_source = st.selectbox(
                f"🎯 Data Source (Auto: {auto_selected}):",
                data_source_options,
                help="Choose 'Auto-select' for smart selection, or pick a specific table/view"
            )
            
            # Store the selection
            st.session_state.manual_data_source = selected_data_source if selected_data_source != "🤖 Auto-select" else None
    
    with col2:
        st.markdown("**🎯 Quick Actions**")
        
        if st.button("📈 Executive View", use_container_width=True):
            question = "Show me the executive dashboard overview"
            st.session_state.quick_question = question
            # Auto-generate query
            generated_sql = generate_enterprise_sql(question, config)
            st.session_state.current_sql = generated_sql
            st.session_state.current_question = question
            # Store for QuickSight export
            st.session_state.last_query = generated_sql
            st.session_state.last_prompt = question
            st.rerun()
        
        if st.button("📋 Renewals", use_container_width=True):
            question = "Display contracts up for renewal"
            st.session_state.quick_question = question
            # Auto-generate query
            generated_sql = generate_enterprise_sql(question, config)
            st.session_state.current_sql = generated_sql
            st.session_state.current_question = question
            # Store for QuickSight export
            st.session_state.last_query = generated_sql
            st.session_state.last_prompt = question
            st.rerun()
        
        if st.button("⚠️ High Risk", use_container_width=True):
            question = "Which contracts are high risk?"
            st.session_state.quick_question = question
            # Auto-generate query
            generated_sql = generate_enterprise_sql(question, config)
            st.session_state.current_sql = generated_sql
            st.session_state.current_question = question
            # Store for QuickSight export
            st.session_state.last_query = generated_sql
            st.session_state.last_prompt = question
            st.rerun()
        
        if st.button("📊 Browse Tables", use_container_width=True):
            st.session_state.show_tables = True
    
    # Show tables in collapsible section
    if st.session_state.get('show_tables', False):
        with st.expander("📊 Available Tables & Views", expanded=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                show_available_tables(config)
            with col2:
                if st.button("❌ Close", use_container_width=True):
                    st.session_state.show_tables = False
                    st.rerun()
    
    # Generate and Execute buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Generate Query", type="primary", use_container_width=True):
            # Get the current question from the text area or quick action
            current_question = user_question
            if current_question and current_question.strip():
                with st.spinner("🤖 Processing your question..."):
                    generated_sql = generate_enterprise_sql(current_question, config)
                    st.session_state.current_sql = generated_sql
                    st.session_state.current_question = current_question
                    # Store for QuickSight export
                    st.session_state.last_query = generated_sql
                    st.session_state.last_prompt = current_question
                    st.success("✅ Query generated! Review below and click Execute.")
            else:
                st.warning("Please enter a question first.")
    
    with col2:
        if st.button("▶️ Execute Query", type="secondary", use_container_width=True):
            if 'current_sql' in st.session_state:
                execute_enterprise_query(st.session_state.current_sql, config)
            else:
                st.warning("Please generate a query first.")
    
    # Display generated SQL
    if 'current_sql' in st.session_state:
        st.markdown("### 📝 Generated SQL Query")
        st.code(st.session_state.current_sql, language="sql")
        
        # Query actions
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✏️ Edit SQL", use_container_width=True):
                st.session_state.edit_mode = True
        
        with col2:
            # Always show save button when there's a query, regardless of execution status
            if 'current_sql' in st.session_state and 'current_question' in st.session_state:
                if st.button("💾 Save Query", use_container_width=True):
                    save_query_template(st.session_state.current_question, st.session_state.current_sql)
            else:
                st.button("💾 Save Query", disabled=True, help="Generate query first", use_container_width=True)
        
        with col3:
            athena_console_url = "https://us-east-1.console.aws.amazon.com/athena/home?region=us-east-1#/query-editor"
            st.markdown(f"""
            <a href="{athena_console_url}" target="_blank" style="
                display: inline-block;
                padding: 0.375rem 0.75rem;
                background-color: #232F3E;
                color: white;
                text-decoration: none;
                border-radius: 0.25rem;
                font-size: 0.875rem;
                font-weight: bold;
                width: 100%;
                text-align: center;
            ">🔗 Run in Athena</a>
            """, unsafe_allow_html=True)
        
        with col4:
            if 'query_results' in st.session_state:
                quicksight_datasets_url = "https://us-east-1.quicksight.aws.amazon.com/sn/start/data-sets"
                st.markdown(f"""
                <a href="{quicksight_datasets_url}" target="_blank" style="
                    display: inline-block;
                    padding: 0.375rem 0.75rem;
                    background-color: #ff6b35;
                    color: white;
                    text-decoration: none;
                    border-radius: 0.25rem;
                    font-size: 0.875rem;
                    font-weight: bold;
                    width: 100%;
                    text-align: center;
                ">📊 QuickSight</a>
                """, unsafe_allow_html=True)
            else:
                st.button("📊 QuickSight", disabled=True, help="Execute query first", use_container_width=True)
    
    # Edit mode
    if st.session_state.get('edit_mode', False):
        st.markdown("### ✏️ Edit SQL Query")
        edited_sql = st.text_area(
            "Modify the SQL query:",
            value=st.session_state.current_sql,
            height=200
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Update Query", use_container_width=True):
                st.session_state.current_sql = edited_sql
                st.session_state.edit_mode = False
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel Edit", use_container_width=True):
                st.session_state.edit_mode = False
                st.rerun()
    
    # Results Section
    if 'query_results' in st.session_state:
        st.markdown("### 📊 Query Results")
        
        df = st.session_state.query_results
        
        # Results summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            st.metric("Status", "Success ✅")
        
        # Data display
        st.dataframe(df, use_container_width=True, height=400)
        
        # Auto-export to QuickSight
        render_quicksight_export_ui(
            sql_query=st.session_state.get('last_query', ''),
            user_prompt=st.session_state.get('last_prompt', ''),
            query_description=f"Query results from: {st.session_state.get('last_prompt', 'Athena Query')}",
            config=config
        )
        
    # Saved Queries Section
    if 'saved_queries' in st.session_state and st.session_state.saved_queries:
        st.markdown("### 💾 Saved Query Templates")
        
        for i, template in enumerate(reversed(st.session_state.saved_queries[-3:])):  # Show last 3
            with st.expander(f"📝 {template.get('name', template.get('question', 'Unnamed Template'))} - {template['timestamp']}"):
                st.code(template['sql'], language="sql")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("🔄 Load Query", key=f"load_{i}", use_container_width=True):
                        st.session_state.current_sql = template['sql']
                        st.session_state.current_question = template.get('name', template.get('question', 'Loaded Template'))
                        st.success(f"✅ Loaded: {template.get('name', template.get('question', 'Template'))}")
                        
                with col2:
                    if st.button("▶️ Execute Now", key=f"exec_{i}", use_container_width=True):
                        st.session_state.current_sql = template['sql']
                        st.session_state.current_question = template.get('name', template.get('question', 'Loaded Template'))
                        execute_enterprise_query(template['sql'], config)
                        
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{i}", use_container_width=True):
                        actual_index = len(st.session_state.saved_queries) - 1 - i
                        st.session_state.saved_queries.pop(actual_index)
                        st.rerun()

# All the helper functions from the working version
def predict_data_source(question, available_tables):
    """Predict which data source would be auto-selected for a question"""
    if not question:
        return "No question entered"
    
    question_lower = question.lower()
    views = [t for t in available_tables if 'view' in t.lower() or '_detailed' in t.lower()]
    tables = [t for t in available_tables if t not in views]
    
    # Same logic as generate_enterprise_sql but just return the table name
    if ("executive" in question_lower and "dashboard" in question_lower) or "executive dashboard overview" in question_lower:
        return "executive_dashboard_detailed" if "executive_dashboard_detailed" in views else "First available view"
    
    if "renewal" in question_lower or "expiring" in question_lower:
        return "renewals_contracts_detailed" if "renewals_contracts_detailed" in views else "First available view"
    
    if "high risk" in question_lower or ("risk" in question_lower and "high" in question_lower):
        return "compliance_contracts_detailed" if "compliance_contracts_detailed" in views else "First available view"
    
    if "compliance" in question_lower:
        return "compliance_contracts_detailed" if "compliance_contracts_detailed" in views else "First available view"
    
    if "status" in question_lower or "distribution" in question_lower:
        return "compliance_contracts_detailed" if "compliance_contracts_detailed" in views else "First available view"
    
    if "performance" in question_lower or "score" in question_lower:
        return "compliance_contracts_detailed" if "compliance_contracts_detailed" in views else "First available view"
    
    if "department" in question_lower:
        return "executive_dashboard_detailed" if "executive_dashboard_detailed" in views else "First available view"
    
    if "all" in question_lower and "contract" in question_lower:
        return tables[0] if tables else "First available table"
    
    # Generic fallback
    if "contract" in question_lower and tables:
        for table in tables:
            if "contract" in table.lower():
                return table
    
    return tables[0] if tables else (views[0] if views else "No tables available")

def get_aws_clients(config):
    """Get AWS clients - works for both localhost and Streamlit Cloud"""
    try:
        # Check if user provided credentials in config
        if 'aws_access_key_id' in config and 'aws_secret_access_key' in config:
            return {
                'athena': boto3.client(
                    'athena', 
                    region_name=config['aws_region'],
                    aws_access_key_id=config['aws_access_key_id'],
                    aws_secret_access_key=config['aws_secret_access_key']
                ),
                'glue': boto3.client(
                    'glue', 
                    region_name=config['aws_region'],
                    aws_access_key_id=config['aws_access_key_id'],
                    aws_secret_access_key=config['aws_secret_access_key']
                )
            }
        
        # Try Streamlit Cloud secrets first
        if hasattr(st, 'secrets') and 'aws' in st.secrets:
            # Check if session token is available
            session_token = st.secrets['aws'].get('AWS_SESSION_TOKEN', None)
            
            return {
                'athena': boto3.client(
                    'athena', 
                    region_name=config['aws_region'],
                    aws_access_key_id=st.secrets['aws']['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=st.secrets['aws']['AWS_SECRET_ACCESS_KEY'],
                    aws_session_token=session_token
                ),
                'glue': boto3.client(
                    'glue', 
                    region_name=config['aws_region'],
                    aws_access_key_id=st.secrets['aws']['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=st.secrets['aws']['AWS_SECRET_ACCESS_KEY'],
                    aws_session_token=session_token
                )
            }
    
    except Exception:
        pass  # Fall through to other methods
    
    # Try local AWS profiles (localhost only)
    try:
        # Check if we're running locally (has AWS credentials file)
        if os.path.exists(os.path.expanduser('~/.aws/credentials')):
            # For Account 2, use the brew-demo profile (localhost only)
            if config['aws_account_id'] == '476169753480':
                session = boto3.Session(profile_name='brew-demo')
                return {
                    'athena': session.client('athena', region_name=config['aws_region']),
                    'glue': session.client('glue', region_name=config['aws_region'])
                }
            else:
                # For Account 1, use default credentials
                return {
                    'athena': boto3.client('athena', region_name=config['aws_region']),
                    'glue': boto3.client('glue', region_name=config['aws_region'])
                }
        else:
            # Streamlit Cloud - use default credentials (environment variables)
            return {
                'athena': boto3.client('athena', region_name=config['aws_region']),
                'glue': boto3.client('glue', region_name=config['aws_region'])
            }
    except Exception as e:
        st.error(f"AWS client creation error: {str(e)}")
        st.info("💡 For localhost: Ensure AWS profiles are configured. For Streamlit Cloud: Check secrets configuration.")
        # Return basic clients as fallback
        return {
            'athena': boto3.client('athena', region_name=config['aws_region']),
            'glue': boto3.client('glue', region_name=config['aws_region'])
        }
def test_connection_status(config):
    """Test connection and show status"""
    try:
        clients = get_aws_clients(config)
        athena_client = clients['athena']
        
        response = athena_client.list_databases(CatalogName='AwsDataCatalog')
        databases = [db['Name'] for db in response['DatabaseList']]
        
        if config['glue_database'] in databases:
            st.success(f"✅ Connected to database: {config['glue_database']}")
            
            # Get table count
            glue_client = clients['glue']
            tables_response = glue_client.get_tables(DatabaseName=config['glue_database'])
            table_count = len(tables_response['TableList'])
            st.info(f"📊 Found {table_count} tables/views available")
        else:
            st.error(f"❌ Database not found: {config['glue_database']}")
            
    except Exception as e:
        st.error(f"❌ Connection failed: {str(e)}")

def show_available_tables(config):
    """Show available tables in compact format"""
    try:
        clients = get_aws_clients(config)
        glue_client = clients['glue']
        
        response = glue_client.get_tables(DatabaseName=config['glue_database'])
        
        if response['TableList']:
            # Show summary first
            total_tables = len(response['TableList'])
            views = [t for t in response['TableList'] if 'view' in t['Name'].lower() or '_detailed' in t['Name'].lower()]
            tables = [t for t in response['TableList'] if t not in views]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Items", total_tables)
            with col2:
                st.metric("Views", len(views))
            with col3:
                st.metric("Tables", len(tables))
            
            # Show views first (more important)
            if views:
                st.markdown("**📈 Views (Pre-built Analytics)**")
                for view in views:
                    with st.expander(f"📈 {view['Name']}", expanded=False):
                        st.write(f"**Location:** {view['StorageDescriptor'].get('Location', 'N/A')}")
                        st.write("**Key Columns:**")
                        for col in view['StorageDescriptor']['Columns'][:5]:  # Show first 5 columns
                            st.write(f"• {col['Name']} ({col['Type']})")
                        if len(view['StorageDescriptor']['Columns']) > 5:
                            st.write(f"... and {len(view['StorageDescriptor']['Columns']) - 5} more columns")
            
            # Show tables with option to expand all
            if tables:
                st.markdown("**📋 Base Tables**")
                
                # Option to show all tables
                show_all_tables = st.checkbox("Show all tables", key="show_all_tables")
                
                tables_to_show = tables if show_all_tables else tables[:5]
                
                for table in tables_to_show:
                    with st.expander(f"📋 {table['Name']}", expanded=False):
                        st.write(f"**Columns:** {len(table['StorageDescriptor']['Columns'])}")
                        st.write(f"**Location:** {table['StorageDescriptor'].get('Location', 'N/A')}")
                        
                        # Show first few columns
                        st.write("**Sample Columns:**")
                        for col in table['StorageDescriptor']['Columns'][:3]:
                            st.write(f"• {col['Name']} ({col['Type']})")
                        if len(table['StorageDescriptor']['Columns']) > 3:
                            st.write(f"... and {len(table['StorageDescriptor']['Columns']) - 3} more columns")
                
                if not show_all_tables and len(tables) > 5:
                    st.info(f"📋 {len(tables) - 5} more tables available - check 'Show all tables' above")
        else:
            st.warning("No tables found.")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

def get_available_tables(config):
    """Get list of available tables"""
    try:
        clients = get_aws_clients(config)
        glue_client = clients['glue']
        response = glue_client.get_tables(DatabaseName=config['glue_database'])
        return [table['Name'] for table in response['TableList']]
    except:
        return []

def generate_enterprise_sql(question, config):
    """Generate SQL for enterprise database using actual table names and views"""
    available_tables = get_available_tables(config)
    
    if not available_tables:
        return f"""-- Error: No tables found in database
-- Please check your Glue catalog setup
-- Database: {config['glue_database']}
SELECT 'No tables available' as message;"""
    
    database_name = f'"{config["glue_database"]}"'
    
    # Extract LIMIT from question (top N, first N, etc.)
    import re
    limit_match = re.search(r'\b(?:top|first)\s+(\d+)\b', question.lower())
    limit_clause = f"LIMIT {limit_match.group(1)}" if limit_match else "LIMIT 100"
    
    # Check if user manually selected a data source
    manual_source = st.session_state.get('manual_data_source', None)
    if manual_source and manual_source in available_tables:
        return f"""-- Generated from: "{question}"
-- Using manually selected: {manual_source}
SELECT *
FROM {database_name}.{manual_source}
{limit_clause};"""
    
    # Continue with auto-selection logic
    views = [t for t in available_tables if 'view' in t.lower() or '_detailed' in t.lower()]
    tables = [t for t in available_tables if t not in views]
    question_lower = question.lower()
    
    # Executive Dashboard queries - HIGHEST PRIORITY
    if ("executive" in question_lower and "dashboard" in question_lower) or "executive dashboard overview" in question_lower:
        if "executive_dashboard_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Auto-selected: Executive Dashboard View
SELECT *
FROM {database_name}.executive_dashboard_detailed
ORDER BY Value DESC
{limit_clause};"""
    
    # Top contracts by value
    if "top" in question_lower and "contract" in question_lower and "value" in question_lower:
        if "executive_dashboard_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Auto-selected: Executive Dashboard View (Top by Value)
SELECT *
FROM {database_name}.executive_dashboard_detailed
ORDER BY Value DESC
{limit_clause};"""
    
    # Department with highest number of high-risk contracts
    if "department" in question_lower and "highest number" in question_lower and "high" in question_lower and "risk" in question_lower:
        if "compliance_contracts_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Auto-selected: Compliance Team View for Department Risk Analysis
SELECT 
    Department,
    COUNT(*) as high_risk_count
FROM {database_name}.compliance_contracts_detailed
WHERE Risk_Level = 'High'
GROUP BY Department
ORDER BY high_risk_count DESC
{limit_clause};"""
        elif "executive_dashboard_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Using Executive Dashboard for Department Analysis
-- Note: Risk_Level column not found, showing all contracts by department
SELECT 
    Department,
    COUNT(*) as contract_count
FROM {database_name}.executive_dashboard_detailed
GROUP BY Department
ORDER BY contract_count DESC
{limit_clause};"""
    
    # Performance score filtering
    if "performance" in question_lower and "score" in question_lower:
        # Extract numeric threshold (below 75, above 80, etc.)
        threshold_match = re.search(r'(?:below|under|less than|<)\s*(\d+)', question_lower)
        above_match = re.search(r'(?:above|over|greater than|>)\s*(\d+)', question_lower)
        
        if threshold_match:
            threshold = threshold_match.group(1)
            if "compliance_contracts_detailed" in views:
                return f"""-- Generated from: "{question}"
-- Auto-selected: Compliance Team View for Performance Analysis
SELECT Contract_Name, Performance_Score, Risk_Level
FROM {database_name}.compliance_contracts_detailed
WHERE Performance_Score < {threshold}
ORDER BY Performance_Score ASC
{limit_clause};"""
            elif "executive_dashboard_detailed" in views:
                return f"""-- Generated from: "{question}"
-- Using Executive Dashboard for Performance Analysis
SELECT Contract_Name, Performance_Score
FROM {database_name}.executive_dashboard_detailed
WHERE Performance_Score < {threshold}
ORDER BY Performance_Score ASC
{limit_clause};"""
        elif above_match:
            threshold = above_match.group(1)
            if "compliance_contracts_detailed" in views:
                return f"""-- Generated from: "{question}"
-- Auto-selected: Compliance Team View for Performance Analysis
SELECT Contract_Name, Performance_Score, Risk_Level
FROM {database_name}.compliance_contracts_detailed
WHERE Performance_Score > {threshold}
ORDER BY Performance_Score DESC
{limit_clause};"""
    
    # Performance by department analysis
    if "performance" in question_lower and "department" in question_lower:
        if "compliance_contracts_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Auto-selected: Compliance Team View for Department Performance Analysis
SELECT 
    Department,
    AVG(Performance_Score) as avg_performance_score,
    MIN(Performance_Score) as min_performance_score,
    MAX(Performance_Score) as max_performance_score,
    COUNT(*) as contract_count
FROM {database_name}.compliance_contracts_detailed
GROUP BY Department
ORDER BY avg_performance_score DESC
{limit_clause};"""
        elif "executive_dashboard_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Using Executive Dashboard for Department Performance Analysis
SELECT 
    Department,
    AVG(Performance_Score) as avg_performance_score,
    COUNT(*) as contract_count
FROM {database_name}.executive_dashboard_detailed
GROUP BY Department
ORDER BY avg_performance_score DESC
{limit_clause};"""
    
    # Expiring contracts - check renewals view first, then executive view
    if "expiring" in question_lower or "renewal" in question_lower:
        if "renewals_contracts_detailed" in views:
            # Extract days if specified (30 days, 60 days, etc.)
            days_match = re.search(r'(\d+)\s+days?', question_lower)
            days = days_match.group(1) if days_match else "180"  # default 6 months
            
            return f"""-- Generated from: "{question}"
-- Auto-selected: Renewals Team View
SELECT *
FROM {database_name}.renewals_contracts_detailed
WHERE DATE(End_Date) BETWEEN CURRENT_DATE AND DATE_ADD('day', {days}, CURRENT_DATE)
ORDER BY {"Value DESC" if "value" in question_lower else "End_Date ASC"}
{limit_clause};"""
        elif "executive_dashboard_detailed" in views:
            # Fallback to executive view for expiring contracts
            days_match = re.search(r'(\d+)\s+days?', question_lower)
            days = days_match.group(1) if days_match else "180"
            
            return f"""-- Generated from: "{question}"
-- Using Executive Dashboard for expiring contracts
SELECT Contract_Name, Status, End_Date, Value
FROM {database_name}.executive_dashboard_detailed
WHERE DATE(End_Date) BETWEEN CURRENT_DATE AND DATE_ADD('day', {days}, CURRENT_DATE)
ORDER BY {"Value DESC" if "value" in question_lower else "End_Date ASC"}
{limit_clause};"""
    
    # High risk queries - HIGH PRIORITY
    if "high risk" in question_lower or ("risk" in question_lower and "high" in question_lower) or "which contracts are high risk" in question_lower:
        if "compliance_contracts_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Using Compliance Team View for High Risk
SELECT *
FROM {database_name}.compliance_contracts_detailed
WHERE Risk_Level = 'High'
ORDER BY Performance_Score ASC
{limit_clause};"""
        elif "contract_compliance" in tables:
            return f"""-- Generated from: "{question}"
-- Using Contract Compliance for High Risk Analysis
SELECT *
FROM {database_name}.contract_compliance
WHERE risk_level = 'High'
ORDER BY performance_score ASC
{limit_clause};"""
    
    # Compliance status queries - HIGH PRIORITY
    if "compliance status" in question_lower or "show compliance" in question_lower or "non-compliant contracts" in question_lower or "display all non-compliant" in question_lower:
        if "compliance_contracts_detailed" in views:
            if "non-compliant" in question_lower or "not compliant" in question_lower:
                return f"""-- Generated from: "{question}"
-- Using Compliance Team View for Non-Compliant Analysis
SELECT *
FROM {database_name}.compliance_contracts_detailed
WHERE Compliance_Status = 'Non-Compliant'
ORDER BY Risk_Level DESC, Performance_Score ASC
{limit_clause};"""
            else:
                return f"""-- Generated from: "{question}"
-- Using Compliance Team View for Status Distribution
SELECT 
    Compliance_Status,
    COUNT(*) as contract_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM {database_name}.compliance_contracts_detailed
GROUP BY Compliance_Status
ORDER BY contract_count DESC;"""
        elif "contract_compliance" in tables:
            if "non-compliant" in question_lower or "not compliant" in question_lower:
                return f"""-- Generated from: "{question}"
-- Using Contract Compliance for Non-Compliant Analysis
SELECT *
FROM {database_name}.contract_compliance
WHERE compliance_status = 'Non-Compliant'
ORDER BY risk_level DESC, performance_score ASC
{limit_clause};"""
            else:
                return f"""-- Generated from: "{question}"
-- Using Contract Compliance for Status Distribution
SELECT 
    compliance_status,
    COUNT(*) as contract_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM {database_name}.contract_compliance
GROUP BY compliance_status
ORDER BY contract_count DESC;"""
    
    # Compliance queries - MEDIUM PRIORITY
    if "compliance" in question_lower:
        if "compliance_contracts_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Using Compliance Team View
SELECT *
FROM {database_name}.compliance_contracts_detailed
ORDER BY Risk_Level, Performance_Score DESC
{limit_clause};"""
    
    # Status/distribution queries - MEDIUM PRIORITY
    if "status" in question_lower or "distribution" in question_lower:
        if "compliance_contracts_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Using Compliance Team View for Status Analysis
SELECT 
    Compliance_Status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM {database_name}.compliance_contracts_detailed
GROUP BY Compliance_Status
ORDER BY count DESC;"""
    
    # Performance queries - MEDIUM PRIORITY
    if "performance" in question_lower or "score" in question_lower:
        if "compliance_contracts_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Using Compliance Team View for Performance Analysis
SELECT 
    Risk_Level,
    AVG(Performance_Score) as avg_performance_score,
    AVG(SLA_Score) as avg_sla_score,
    COUNT(*) as contract_count
FROM {database_name}.compliance_contracts_detailed
GROUP BY Risk_Level
ORDER BY avg_performance_score DESC;"""
    
    # Department queries - MEDIUM PRIORITY
    if "department" in question_lower:
        if "executive_dashboard_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Using Executive Dashboard View for Department Analysis
SELECT 
    Department,
    COUNT(*) as contract_count,
    AVG(Performance_Score) as avg_performance,
    SUM(Value) as total_value
FROM {database_name}.executive_dashboard_detailed
GROUP BY Department
ORDER BY total_value DESC;"""
    
    # Risk analysis with performance ratings - ADVANCED QUERY
    if "risk analysis" in question_lower and "department" in question_lower and "performance" in question_lower:
        if "contract_master" in available_tables and "contract_compliance" in available_tables:
            return f"""-- Generated from: "{question}"
-- Concepts: INNER JOIN, table aliases, calculated fields
SELECT 
    cm.Contract_Name,       -- Use table alias (cm) for clarity
    cc.Risk_Level,
    cc.Performance_Score,
    CASE                    -- CASE: Create conditional logic
        WHEN cc.Performance_Score >= 90 THEN 'Excellent'
        WHEN cc.Performance_Score >= 80 THEN 'Good'
        ELSE 'Needs Improvement'
    END as Rating
FROM {database_name}.contract_master cm     -- Alias: cm = contract_master
INNER JOIN {database_name}.contract_compliance cc  -- INNER JOIN: Only matching records
    ON cm.Contract_ID = cc.Contract_ID  -- Join condition: matching IDs
WHERE cc.Risk_Level = 'High'
ORDER BY cc.Performance_Score DESC;"""
    
    # "All contract data" - SPECIFIC MATCH
    if "all" in question_lower and "contract" in question_lower:
        # Use the first table (not view) for raw data
        if tables:
            first_table = tables[0]
            return f"""-- Generated from: "{question}"
-- Using base table for all contract data
SELECT *
FROM {database_name}.{first_table}
{limit_clause};"""
    
    # Generic fallback - ALWAYS RETURN SOMETHING
    # For contract-related questions, prefer contract tables
    if "contract" in question_lower and tables:
        contract_table = None
        for table in tables:
            if "contract" in table.lower():
                contract_table = table
                break
        
        if contract_table:
            return f"""-- Generated from: "{question}"
-- Using contract table for general query
SELECT *
FROM {database_name}.{contract_table}
{limit_clause};"""
    
    # Final fallback - use first available item
    if tables:
        first_table = tables[0]
        return f"""-- Generated from: "{question}"
-- Using base table: {first_table}
SELECT *
FROM {database_name}.{first_table}
{limit_clause};"""
    elif views:
        first_view = views[0]
        return f"""-- Generated from: "{question}"
-- Using view: {first_view}
SELECT *
FROM {database_name}.{first_view}
{limit_clause};"""
    else:
        return f"""-- Generated from: "{question}"
-- No suitable tables or views found
SELECT 'No data available' as message;"""

def execute_enterprise_query(sql_query, config):
    """Execute query on enterprise Athena infrastructure"""
    try:
        clients = get_aws_clients(config)
        athena_client = clients['athena']
        
        response = athena_client.start_query_execution(
            QueryString=sql_query,
            QueryExecutionContext={
                'Database': config['glue_database']
            },
            WorkGroup=config['athena_workgroup'],
            ResultConfiguration={
                'OutputLocation': f"s3://{config['s3_results_bucket']}/"
            }
        )
        
        query_execution_id = response['QueryExecutionId']
        st.success(f"✅ Query submitted successfully! Execution ID: {query_execution_id}")
        
        # Monitor query execution
        with st.spinner("⏳ Executing query..."):
            status = monitor_query_execution(athena_client, query_execution_id)
        
        if status == 'SUCCEEDED':
            # Check if this is a DDL statement (CREATE, DROP, ALTER)
            if sql_query.strip().upper().startswith(('CREATE', 'DROP', 'ALTER')):
                st.success("✅ DDL statement executed successfully!")
                if sql_query.strip().upper().startswith('CREATE VIEW'):
                    st.info("📋 View created. You can now query it with SELECT statements.")
            else:
                display_query_results(athena_client, query_execution_id)
        elif status == 'FAILED':
            st.error("❌ Query execution failed. Please check your SQL and try again.")
        
    except Exception as e:
        st.error(f"❌ Query execution error: {str(e)}")

def monitor_query_execution(athena_client, query_execution_id):
    """Monitor Athena query execution status"""
    max_attempts = 30
    attempt = 0
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    while attempt < max_attempts:
        try:
            response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            status = response['QueryExecution']['Status']['State']
            
            # Check for failure reason
            if status == 'FAILED':
                failure_reason = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown error')
                st.error(f"❌ Query failed: {failure_reason}")
                return status
            
            progress = min((attempt + 1) / max_attempts, 1.0)
            progress_bar.progress(progress)
            status_text.text(f"Status: {status}")
            
            if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                progress_bar.progress(1.0)
                return status
            
            time.sleep(2)
            attempt += 1
        except Exception as e:
            st.error(f"❌ Error monitoring query: {str(e)}")
            return 'FAILED'
    
    return 'TIMEOUT'

def display_query_results(athena_client, query_execution_id):
    """Display query results in Streamlit"""
    try:
        results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
        
        columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        rows = []
        
        for row in results['ResultSet']['Rows'][1:]:  # Skip header row
            row_data = [field.get('VarCharValue', '') for field in row['Data']]
            rows.append(row_data)
        
        if rows:
            df = pd.DataFrame(rows, columns=columns)
            st.session_state.query_results = df
            st.session_state.query_execution_id = query_execution_id
            st.success(f"✅ Query completed! {len(df)} rows returned.")
        else:
            st.info("Query executed successfully but returned no results.")
            
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")

def load_user_accounts():
    """Load user-added accounts from file"""
    import json
    try:
        with open('user_accounts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception:
        return {}

def save_user_accounts(accounts):
    """Save user accounts to file"""
    import json
    try:
        with open('user_accounts.json', 'w') as f:
            json.dump(accounts, f, indent=2)
        return True
    except Exception:
        return False

def render_account_management():
    """Render account management UI"""
    st.sidebar.markdown("---")
    
    with st.sidebar.expander("➕ Add AWS Account"):
        st.markdown("**Add Your AWS Account**")
        
        account_name = st.text_input("Account Name:", placeholder="My Company Account")
        account_id = st.text_input("AWS Account ID:", placeholder="123456789012")
        region = st.selectbox("Region:", ["us-east-1", "us-west-2", "eu-west-1"])
        database = st.text_input("Glue Database:", placeholder="my-analytics-db")
        workgroup = st.text_input("Athena Workgroup:", value="primary")
        
        st.markdown("**AWS Credentials (Optional)**")
        st.info("💡 Leave blank if using AWS CLI, IAM roles, or SSO")
        access_key = st.text_input("Access Key ID:", type="password")
        secret_key = st.text_input("Secret Access Key:", type="password")
        
        if st.button("Add Account"):
            if account_name and account_id and database:
                user_accounts = load_user_accounts()
                account_config = {
                    'aws_region': region,
                    'aws_account_id': account_id,
                    'athena_workgroup': workgroup,
                    's3_results_bucket': f'aws-athena-query-results-{region}-{account_id}',
                    'glue_database': database,
                    's3_raw_data': f's3://your-data-bucket/',
                    'quicksight_account_id': account_id
                }
                
                # Add credentials if provided
                if access_key and secret_key:
                    account_config['aws_access_key_id'] = access_key
                    account_config['aws_secret_access_key'] = secret_key
                
                user_accounts[f"{account_name} ({account_id})"] = account_config
                
                if save_user_accounts(user_accounts):
                    st.success("✅ Account added!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save account")
            else:
                st.error("Please fill required fields")

def save_query_template(question, sql):
    """Save query as reusable template with file persistence"""
    import json
    
    # Initialize session state
    if 'saved_queries' not in st.session_state:
        st.session_state.saved_queries = load_saved_queries()
    
    template = {
        'question': question,
        'sql': sql,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    st.session_state.saved_queries.append(template)
    
    # Save to file
    try:
        with open('saved_queries.json', 'w') as f:
            json.dump(st.session_state.saved_queries, f, indent=2)
        st.success("✅ Query saved as template!")
    except Exception as e:
        st.error(f"Failed to save query: {str(e)}")

def load_saved_queries():
    """Load saved queries from file"""
    import json
    try:
        with open('saved_queries.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception:
        return []

def render_saved_queries_sidebar():
    """Render saved queries in sidebar as compact expandable section"""
    if 'saved_queries' not in st.session_state:
        st.session_state.saved_queries = load_saved_queries()
    
    if st.session_state.saved_queries:
        with st.sidebar.expander("💾 Saved Queries"):
            # Create dropdown options
            query_options = ["Select a saved query..."] + [
                f"{query.get('name', query.get('question', 'Unnamed Template'))} ({query['timestamp']})" 
                for query in st.session_state.saved_queries
            ]
            
            selected_query = st.selectbox(
                "Load Query:",
                query_options,
                key="saved_query_selector"
            )
            
            if selected_query != "Select a saved query...":
                query_index = query_options.index(selected_query) - 1
                query = st.session_state.saved_queries[query_index]
                
                st.write(f"**Date:** {query['timestamp']}")
                st.code(query['sql'][:200] + "..." if len(query['sql']) > 200 else query['sql'], language='sql')
                
                if st.button("Load This Query", key=f"load_query_{query_index}"):
                    st.session_state.current_sql = query['sql']
                    st.session_state.current_question = query.get('name', query.get('question', 'Loaded Template'))
                    st.rerun()

if __name__ == "__main__":
    main()
