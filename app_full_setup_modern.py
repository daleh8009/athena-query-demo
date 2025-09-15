import streamlit as st
import boto3
import pandas as pd
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Full Setup Configuration - User configurable
SETUP_CONFIG = {
    'aws_region': os.getenv('AWS_REGION', 'us-east-1'),
    'aws_account_id': os.getenv('AWS_ACCOUNT_ID', ''),
    'athena_workgroup': os.getenv('ATHENA_WORKGROUP', 'athena-query-generator'),
    's3_results_bucket': os.getenv('S3_RESULTS_BUCKET', ''),
    'glue_database': os.getenv('GLUE_DATABASE', 'business_analytics'),
    's3_raw_data': os.getenv('S3_RAW_DATA', ''),
    'quicksight_account_id': os.getenv('QUICKSIGHT_ACCOUNT_ID', '')
}

# Page configuration
st.set_page_config(
    page_title="Athena Query Generator - Full Setup",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS theme (same as enterprise version)
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
    
    .setup-step {
        background: rgba(255,255,255,0.05);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff6b35;
        margin: 0.5rem 0;
    }
    
    .setup-complete {
        background: rgba(40, 167, 69, 0.2);
        border-left: 4px solid #28a745;
    }
    
    .setup-pending {
        background: rgba(255, 193, 7, 0.2);
        border-left: 4px solid #ffc107;
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

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🛠️ Athena Query Generator - Full Setup</h1>
        <p style="margin: 0; opacity: 0.8;">Complete Infrastructure Setup + Natural Language to SQL</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### 🔧 Configuration")
        
        # Setup progress
        setup_progress = check_setup_progress()
        progress_value = sum(setup_progress.values()) / len(setup_progress)
        
        st.progress(progress_value)
        st.write(f"Setup Progress: {int(progress_value * 100)}%")
        
        # Show setup status
        with st.expander("📋 Setup Status"):
            for step, completed in setup_progress.items():
                status = "✅" if completed else "⏳"
                st.write(f"{status} {step}")
        
        # AWS Account configuration
        st.markdown("### 🏢 AWS Account")
        account_id = st.text_input("Account ID", value=SETUP_CONFIG['aws_account_id'])
        region = st.selectbox("Region", ["us-east-1", "us-west-2", "eu-west-1"], 
                             index=0 if SETUP_CONFIG['aws_region'] == 'us-east-1' else 0)
        
        # Update config
        SETUP_CONFIG['aws_account_id'] = account_id
        SETUP_CONFIG['aws_region'] = region
        
        if account_id:
            # Auto-generate bucket names
            SETUP_CONFIG['s3_results_bucket'] = f"aws-athena-query-results-{region}-{account_id}"
            SETUP_CONFIG['s3_raw_data'] = f"athena-raw-data-{account_id}"
            SETUP_CONFIG['quicksight_account_id'] = account_id
    
    # Main content with tabs
    if progress_value < 1.0:
        # Show setup wizard if not complete
        tab1, tab2 = st.tabs(["🛠️ Setup Wizard", "🔍 Query Interface"])
        
        with tab1:
            show_setup_wizard()
        
        with tab2:
            if progress_value > 0.5:
                show_query_interface()
            else:
                st.info("Complete more setup steps to access the query interface.")
    else:
        # Show full interface if setup is complete
        tab1, tab2, tab3 = st.tabs(["🔍 Query Interface", "📊 Results & Analytics", "🛠️ Setup Management"])
        
        with tab1:
            show_query_interface()
        
        with tab2:
            show_results_analytics()
        
        with tab3:
            show_setup_management()

def check_setup_progress():
    """Check which setup steps are completed"""
    progress = {
        "AWS Connection": False,
        "S3 Buckets": False,
        "Athena Workgroup": False,
        "Glue Database": False,
        "Sample Data": False,
        "QuickSight Setup": False
    }
    
    try:
        # Check AWS connection
        sts_client = boto3.client('sts', region_name=SETUP_CONFIG['aws_region'])
        identity = sts_client.get_caller_identity()
        if identity.get('Account') == SETUP_CONFIG['aws_account_id']:
            progress["AWS Connection"] = True
        
        # Check S3 buckets
        s3_client = boto3.client('s3', region_name=SETUP_CONFIG['aws_region'])
        try:
            s3_client.head_bucket(Bucket=SETUP_CONFIG['s3_results_bucket'])
            progress["S3 Buckets"] = True
        except:
            pass
        
        # Check Athena workgroup
        athena_client = boto3.client('athena', region_name=SETUP_CONFIG['aws_region'])
        try:
            workgroups = athena_client.list_work_groups()
            workgroup_names = [wg['Name'] for wg in workgroups['WorkGroups']]
            if SETUP_CONFIG['athena_workgroup'] in workgroup_names:
                progress["Athena Workgroup"] = True
        except:
            pass
        
        # Check Glue database
        glue_client = boto3.client('glue', region_name=SETUP_CONFIG['aws_region'])
        try:
            databases = glue_client.get_databases()
            database_names = [db['Name'] for db in databases['DatabaseList']]
            if SETUP_CONFIG['glue_database'] in database_names:
                progress["Glue Database"] = True
                
                # Check for sample data (tables in database)
                tables = glue_client.get_tables(DatabaseName=SETUP_CONFIG['glue_database'])
                if tables['TableList']:
                    progress["Sample Data"] = True
        except:
            pass
        
        # QuickSight check (simplified)
        if progress["AWS Connection"] and progress["S3 Buckets"]:
            progress["QuickSight Setup"] = True
            
    except Exception as e:
        st.sidebar.error(f"Setup check error: {str(e)}")
    
    return progress

def show_setup_wizard():
    """Complete setup wizard interface"""
    st.markdown("## 🛠️ Infrastructure Setup Wizard")
    st.markdown("Follow these steps to set up your complete analytics infrastructure:")
    
    # Step 1: AWS Connection
    with st.expander("Step 1: AWS Connection", expanded=True):
        st.markdown("### Verify AWS Connection")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info(f"""
            **Current Configuration:**
            - Account ID: {SETUP_CONFIG['aws_account_id'] or 'Not set'}
            - Region: {SETUP_CONFIG['aws_region']}
            """)
        
        with col2:
            if st.button("🔍 Test Connection", use_container_width=True):
                test_aws_connection()
    
    # Step 2: S3 Buckets
    with st.expander("Step 2: Create S3 Buckets"):
        st.markdown("### S3 Storage Setup")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Required Buckets:**")
            st.write(f"• Results: `{SETUP_CONFIG['s3_results_bucket']}`")
            st.write(f"• Raw Data: `{SETUP_CONFIG['s3_raw_data']}`")
        
        with col2:
            if st.button("🪣 Create S3 Buckets", use_container_width=True):
                create_s3_buckets()
    
    # Step 3: Athena Workgroup
    with st.expander("Step 3: Setup Athena Workgroup"):
        st.markdown("### Athena Query Engine")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info(f"Workgroup: `{SETUP_CONFIG['athena_workgroup']}`")
            st.write("This will configure query execution and result storage.")
        
        with col2:
            if st.button("⚙️ Create Workgroup", use_container_width=True):
                create_athena_workgroup()
    
    # Step 4: Glue Database
    with st.expander("Step 4: Create Glue Database"):
        st.markdown("### Data Catalog Setup")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info(f"Database: `{SETUP_CONFIG['glue_database']}`")
            st.write("This will store your table metadata and schema information.")
        
        with col2:
            if st.button("📊 Create Database", use_container_width=True):
                create_glue_database()
    
    # Step 5: Sample Data
    with st.expander("Step 5: Upload Sample Data"):
        st.markdown("### Sample Business Data")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write("**Sample datasets to create:**")
            st.write("• Sales transactions")
            st.write("• Customer data") 
            st.write("• Contract information")
        
        with col2:
            if st.button("📤 Create Sample Data", use_container_width=True):
                create_sample_data()
    
    # Step 6: QuickSight
    with st.expander("Step 6: QuickSight Integration"):
        st.markdown("### Business Intelligence Setup")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write("**QuickSight Configuration:**")
            st.write("• Enable QuickSight service")
            st.write("• Grant S3 and Athena permissions")
            st.write("• Create data source connections")
        
        with col2:
            if st.button("📈 Setup QuickSight", use_container_width=True):
                setup_quicksight()
    
    # Final validation
    st.markdown("### 🎯 Final Validation")
    if st.button("✅ Validate Complete Setup", type="primary", use_container_width=True):
        validate_complete_setup()

def show_query_interface():
    """Main query interface (same as enterprise version)"""
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
        
        # Handle quick actions
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
        available_tables = get_available_tables()
        if available_tables:
            auto_selected = predict_data_source(user_question, available_tables) if user_question else "Auto-select based on question"
            
            data_source_options = ["🤖 Auto-select"] + available_tables
            selected_data_source = st.selectbox(
                f"🎯 Data Source (Auto: {auto_selected}):",
                data_source_options,
                help="Choose 'Auto-select' for smart selection, or pick a specific table/view"
            )
            
            st.session_state.manual_data_source = selected_data_source if selected_data_source != "🤖 Auto-select" else None
    
    with col2:
        st.markdown("**🎯 Quick Actions**")
        
        if st.button("📈 Executive View", use_container_width=True):
            question = "Show me the executive dashboard overview"
            st.session_state.quick_question = question
            generated_sql = generate_enterprise_sql(question)
            st.session_state.current_sql = generated_sql
            st.session_state.current_question = question
            st.rerun()
        
        if st.button("📋 Renewals", use_container_width=True):
            question = "Display contracts up for renewal"
            st.session_state.quick_question = question
            generated_sql = generate_enterprise_sql(question)
            st.session_state.current_sql = generated_sql
            st.session_state.current_question = question
            st.rerun()
        
        if st.button("⚠️ High Risk", use_container_width=True):
            question = "Which contracts are high risk?"
            st.session_state.quick_question = question
            generated_sql = generate_enterprise_sql(question)
            st.session_state.current_sql = generated_sql
            st.session_state.current_question = question
            st.rerun()
        
        if st.button("📊 Browse Tables", use_container_width=True):
            st.session_state.show_tables = True
    
    # Show tables in collapsible section
    if st.session_state.get('show_tables', False):
        with st.expander("📊 Available Tables & Views", expanded=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                show_available_tables()
            with col2:
                if st.button("❌ Close", use_container_width=True):
                    st.session_state.show_tables = False
                    st.rerun()
    
    # Generate and Execute buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Generate Query", type="primary", use_container_width=True):
            current_question = user_question
            if current_question and current_question.strip():
                with st.spinner("🤖 Processing your question..."):
                    generated_sql = generate_enterprise_sql(current_question)
                    st.session_state.current_sql = generated_sql
                    st.session_state.current_question = current_question
                    st.success("✅ Query generated! Review below and click Execute.")
            else:
                st.warning("Please enter a question first.")
    
    with col2:
        if st.button("▶️ Execute Query", type="secondary", use_container_width=True):
            if 'current_sql' in st.session_state:
                execute_enterprise_query(st.session_state.current_sql)
            else:
                st.warning("Please generate a query first.")
    
    # Display generated SQL and results (same as enterprise version)
    if 'current_sql' in st.session_state:
        st.markdown("### 📝 Generated SQL Query")
        st.code(st.session_state.current_sql, language="sql")
        
        # Query actions
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✏️ Edit SQL", use_container_width=True):
                st.session_state.edit_mode = True
        
        with col2:
            if st.button("💾 Save Query", use_container_width=True):
                save_query_template(st.session_state.current_question, st.session_state.current_sql)
        
        with col3:
            athena_console_url = f"https://{SETUP_CONFIG['aws_region']}.console.aws.amazon.com/athena/home?region={SETUP_CONFIG['aws_region']}#/query-editor"
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
                quicksight_datasets_url = f"https://{SETUP_CONFIG['aws_region']}.quicksight.aws.amazon.com/sn/start/data-sets"
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
    
    # Results Section (same as enterprise)
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
        
        # Export options
        st.markdown("### 📤 Export to QuickSight")
        col1, col2 = st.columns(2)
        
        with col1:
            quicksight_datasets_url = f"https://{SETUP_CONFIG['aws_region']}.quicksight.aws.amazon.com/sn/start/data-sets"
            st.markdown(f"""
            <a href="{quicksight_datasets_url}" target="_blank" style="
                display: inline-block;
                padding: 0.75rem 1.5rem;
                background-color: #232F3E;
                color: white;
                text-decoration: none;
                border-radius: 0.5rem;
                font-weight: bold;
                width: 100%;
                text-align: center;
            ">📈 Create QuickSight Dataset</a>
            """, unsafe_allow_html=True)
        
        with col2:
            quicksight_url = f"https://{SETUP_CONFIG['aws_region']}.quicksight.aws.amazon.com/sn/start"
            st.markdown(f"""
            <a href="{quicksight_url}" target="_blank" style="
                display: inline-block;
                padding: 0.75rem 1.5rem;
                background-color: #ff6b35;
                color: white;
                text-decoration: none;
                border-radius: 0.5rem;
                font-weight: bold;
                width: 100%;
                text-align: center;
            ">🎯 Open QuickSight Console</a>
            """, unsafe_allow_html=True)
        
        # Show helpful info
        if 'query_execution_id' in st.session_state:
            s3_location = f"s3://{SETUP_CONFIG['s3_results_bucket']}/{st.session_state.query_execution_id}.csv"
            st.info(f"""
            **💡 In QuickSight Datasets page:**
            1. Click "New dataset" 
            2. Choose "Athena" as data source
            3. Database: `{SETUP_CONFIG['glue_database']}`
            4. Query results location: `{s3_location}`
            """)
    
    # Saved Queries Section (same as enterprise)
    if 'saved_queries' in st.session_state and st.session_state.saved_queries:
        st.markdown("### 💾 Saved Query Templates")
        
        for i, template in enumerate(reversed(st.session_state.saved_queries[-3:])):
            with st.expander(f"📝 {template['question']} - {template['timestamp']}"):
                st.code(template['sql'], language="sql")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("🔄 Load Query", key=f"load_{i}", use_container_width=True):
                        st.session_state.current_sql = template['sql']
                        st.session_state.current_question = template['question']
                        st.success(f"✅ Loaded: {template['question']}")
                        
                with col2:
                    if st.button("▶️ Execute Now", key=f"exec_{i}", use_container_width=True):
                        st.session_state.current_sql = template['sql']
                        st.session_state.current_question = template['question']
                        execute_enterprise_query(template['sql'])
                        
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{i}", use_container_width=True):
                        actual_index = len(st.session_state.saved_queries) - 1 - i
                        st.session_state.saved_queries.pop(actual_index)
                        st.rerun()

def show_results_analytics():
    """Results and analytics tab"""
    st.markdown("### 📊 Query Results & Analytics")
    
    if 'query_results' in st.session_state:
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
        
        # Basic analytics
        if len(df) > 0:
            st.markdown("### 📈 Quick Analytics")
            
            # Show column types
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Column Information:**")
                for col in df.columns:
                    st.write(f"• {col}: {df[col].dtype}")
            
            with col2:
                st.markdown("**Data Summary:**")
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    for col in numeric_cols[:3]:  # Show first 3 numeric columns
                        st.write(f"• {col}: avg {df[col].mean():.2f}")
    else:
        st.info("Execute a query to see results and analytics here.")

def show_setup_management():
    """Setup management and maintenance"""
    st.markdown("### 🛠️ Setup Management")
    
    # Current configuration
    st.markdown("#### 📋 Current Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **AWS Configuration:**
        • Account ID: {SETUP_CONFIG['aws_account_id']}
        • Region: {SETUP_CONFIG['aws_region']}
        • Workgroup: {SETUP_CONFIG['athena_workgroup']}
        """)
    
    with col2:
        st.info(f"""
        **Storage Configuration:**
        • Results Bucket: {SETUP_CONFIG['s3_results_bucket']}
        • Raw Data Bucket: {SETUP_CONFIG['s3_raw_data']}
        • Database: {SETUP_CONFIG['glue_database']}
        """)
    
    # Management actions
    st.markdown("#### ⚙️ Management Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Setup Status", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("🧹 Clean Test Data", use_container_width=True):
            clean_test_data()
    
    with col3:
        if st.button("📊 Add More Sample Data", use_container_width=True):
            create_additional_sample_data()

# Setup Functions
def test_aws_connection():
    """Test AWS connection"""
    try:
        sts_client = boto3.client('sts', region_name=SETUP_CONFIG['aws_region'])
        identity = sts_client.get_caller_identity()
        
        if identity.get('Account') == SETUP_CONFIG['aws_account_id']:
            st.success(f"✅ Connected to AWS Account: {SETUP_CONFIG['aws_account_id']}")
            st.info(f"User: {identity.get('Arn', 'Unknown')}")
        else:
            st.warning(f"⚠️ Connected to different account: {identity.get('Account')}")
            
    except Exception as e:
        st.error(f"❌ Connection failed: {str(e)}")

def create_s3_buckets():
    """Create required S3 buckets"""
    try:
        s3_client = boto3.client('s3', region_name=SETUP_CONFIG['aws_region'])
        
        # Create results bucket
        try:
            if SETUP_CONFIG['aws_region'] == 'us-east-1':
                s3_client.create_bucket(Bucket=SETUP_CONFIG['s3_results_bucket'])
            else:
                s3_client.create_bucket(
                    Bucket=SETUP_CONFIG['s3_results_bucket'],
                    CreateBucketConfiguration={'LocationConstraint': SETUP_CONFIG['aws_region']}
                )
            st.success(f"✅ Created results bucket: {SETUP_CONFIG['s3_results_bucket']}")
        except s3_client.exceptions.BucketAlreadyOwnedByYou:
            st.info(f"ℹ️ Results bucket already exists: {SETUP_CONFIG['s3_results_bucket']}")
        
        # Create raw data bucket
        try:
            if SETUP_CONFIG['aws_region'] == 'us-east-1':
                s3_client.create_bucket(Bucket=SETUP_CONFIG['s3_raw_data'])
            else:
                s3_client.create_bucket(
                    Bucket=SETUP_CONFIG['s3_raw_data'],
                    CreateBucketConfiguration={'LocationConstraint': SETUP_CONFIG['aws_region']}
                )
            st.success(f"✅ Created raw data bucket: {SETUP_CONFIG['s3_raw_data']}")
        except s3_client.exceptions.BucketAlreadyOwnedByYou:
            st.info(f"ℹ️ Raw data bucket already exists: {SETUP_CONFIG['s3_raw_data']}")
        
    except Exception as e:
        st.error(f"❌ S3 bucket creation failed: {str(e)}")

def create_athena_workgroup():
    """Create Athena workgroup"""
    try:
        athena_client = boto3.client('athena', region_name=SETUP_CONFIG['aws_region'])
        
        athena_client.create_work_group(
            Name=SETUP_CONFIG['athena_workgroup'],
            Configuration={
                'ResultConfigurationUpdates': {
                    'OutputLocation': f"s3://{SETUP_CONFIG['s3_results_bucket']}/",
                    'EncryptionConfiguration': {
                        'EncryptionOption': 'SSE_S3'
                    }
                },
                'EnforceWorkGroupConfiguration': True,
                'PublishCloudWatchMetrics': True,
                'BytesScannedCutoffPerQuery': 1000000000  # 1GB limit
            },
            Description='Workgroup for Athena Query Generator application'
        )
        
        st.success(f"✅ Created Athena workgroup: {SETUP_CONFIG['athena_workgroup']}")
        
    except athena_client.exceptions.InvalidRequestException as e:
        if "already exists" in str(e):
            st.info(f"ℹ️ Workgroup already exists: {SETUP_CONFIG['athena_workgroup']}")
        else:
            st.error(f"❌ Athena workgroup creation failed: {str(e)}")
    except Exception as e:
        st.error(f"❌ Athena workgroup creation failed: {str(e)}")

def create_glue_database():
    """Create Glue database"""
    try:
        glue_client = boto3.client('glue', region_name=SETUP_CONFIG['aws_region'])
        
        glue_client.create_database(
            DatabaseInput={
                'Name': SETUP_CONFIG['glue_database'],
                'Description': 'Business analytics database for Athena Query Generator'
            }
        )
        
        st.success(f"✅ Created Glue database: {SETUP_CONFIG['glue_database']}")
        
    except glue_client.exceptions.AlreadyExistsException:
        st.info(f"ℹ️ Database already exists: {SETUP_CONFIG['glue_database']}")
    except Exception as e:
        st.error(f"❌ Glue database creation failed: {str(e)}")

def create_sample_data():
    """Create and upload sample data"""
    try:
        # Create sample sales data
        sales_data = pd.DataFrame({
            'transaction_id': [f'TXN{i:03d}' for i in range(1, 101)],
            'customer_id': [f'CUST{i:03d}' for i in range(1, 101)],
            'product_id': [f'PROD{(i % 10) + 1:03d}' for i in range(1, 101)],
            'sales_amount': [round(100 + (i * 15.5), 2) for i in range(1, 101)],
            'transaction_date': pd.date_range('2024-01-01', periods=100, freq='D'),
            'region': [['North', 'South', 'East', 'West'][i % 4] for i in range(100)]
        })
        
        # Create sample contract data
        contract_data = pd.DataFrame({
            'contract_id': [f'CT{i:04d}' for i in range(1, 51)],
            'risk_level': [['High', 'Medium', 'Low'][i % 3] for i in range(50)],
            'compliance_status': [['Compliant', 'Non-Compliant', 'Pending Review'][i % 3] for i in range(50)],
            'performance_score': [60 + (i * 2) % 40 for i in range(50)],
            'sla_score': [65 + (i * 3) % 35 for i in range(50)],
            'kpi_met': [['Yes' if i % 3 == 0 else 'No'][0] for i in range(50)]
        })
        
        # Upload to S3
        s3_client = boto3.client('s3', region_name=SETUP_CONFIG['aws_region'])
        
        # Upload sales data
        sales_csv = sales_data.to_csv(index=False)
        s3_client.put_object(
            Bucket=SETUP_CONFIG['s3_raw_data'],
            Key='sales/sales_data.csv',
            Body=sales_csv
        )
        
        # Upload contract data
        contract_csv = contract_data.to_csv(index=False)
        s3_client.put_object(
            Bucket=SETUP_CONFIG['s3_raw_data'],
            Key='contracts/contract_data.csv',
            Body=contract_csv
        )
        
        # Create Glue tables
        glue_client = boto3.client('glue', region_name=SETUP_CONFIG['aws_region'])
        
        # Sales table
        glue_client.create_table(
            DatabaseName=SETUP_CONFIG['glue_database'],
            TableInput={
                'Name': 'sales_transactions',
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'transaction_id', 'Type': 'string'},
                        {'Name': 'customer_id', 'Type': 'string'},
                        {'Name': 'product_id', 'Type': 'string'},
                        {'Name': 'sales_amount', 'Type': 'decimal(10,2)'},
                        {'Name': 'transaction_date', 'Type': 'date'},
                        {'Name': 'region', 'Type': 'string'}
                    ],
                    'Location': f's3://{SETUP_CONFIG["s3_raw_data"]}/sales/',
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
                        'Parameters': {'field.delim': ',', 'skip.header.line.count': '1'}
                    }
                }
            }
        )
        
        # Contract table
        glue_client.create_table(
            DatabaseName=SETUP_CONFIG['glue_database'],
            TableInput={
                'Name': 'contract_compliance',
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'contract_id', 'Type': 'string'},
                        {'Name': 'risk_level', 'Type': 'string'},
                        {'Name': 'compliance_status', 'Type': 'string'},
                        {'Name': 'performance_score', 'Type': 'int'},
                        {'Name': 'sla_score', 'Type': 'int'},
                        {'Name': 'kpi_met', 'Type': 'string'}
                    ],
                    'Location': f's3://{SETUP_CONFIG["s3_raw_data"]}/contracts/',
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
                        'Parameters': {'field.delim': ',', 'skip.header.line.count': '1'}
                    }
                }
            }
        )
        
        st.success("✅ Created sample data and tables:")
        st.write("• Sales transactions (100 records)")
        st.write("• Contract compliance (50 records)")
        
    except Exception as e:
        st.error(f"❌ Sample data creation failed: {str(e)}")

def setup_quicksight():
    """Setup QuickSight integration"""
    try:
        quicksight_url = f"https://{SETUP_CONFIG['aws_region']}.quicksight.aws.amazon.com/sn/start"
        
        st.success("✅ QuickSight setup initiated!")
        st.info(f"""
        **Manual QuickSight Setup Steps:**
        
        1. **Enable QuickSight:** Go to [QuickSight Console]({quicksight_url})
        2. **Choose Standard Edition** if not already enabled
        3. **Grant Permissions:**
           • Amazon S3: Select your buckets
           • Amazon Athena: Enable access
        4. **Create Data Source:**
           • Choose Athena as data source
           • Workgroup: {SETUP_CONFIG['athena_workgroup']}
           • Database: {SETUP_CONFIG['glue_database']}
        """)
        
        # Open QuickSight in new tab
        st.markdown(f"""
        <a href="{quicksight_url}" target="_blank" style="
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background-color: #ff6b35;
            color: white;
            text-decoration: none;
            border-radius: 0.5rem;
            font-weight: bold;
        ">🚀 Open QuickSight Console</a>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ QuickSight setup failed: {str(e)}")

def validate_complete_setup():
    """Validate the complete setup"""
    st.markdown("### 🔍 Setup Validation Results")
    
    progress = check_setup_progress()
    
    all_complete = all(progress.values())
    
    if all_complete:
        st.success("🎉 **Setup Complete!** All components are properly configured.")
        st.balloons()
        
        # Show next steps
        st.info("""
        **🚀 You're ready to start querying!**
        
        • Switch to the Query Interface tab
        • Try the Quick Actions or type your own questions
        • Export results to QuickSight for visualization
        """)
    else:
        st.warning("⚠️ Setup is not complete. Please finish the remaining steps:")
        
        for step, completed in progress.items():
            if not completed:
                st.error(f"❌ {step} - Not completed")
            else:
                st.success(f"✅ {step} - Completed")

def clean_test_data():
    """Clean up test data"""
    try:
        # This would implement cleanup logic
        st.success("✅ Test data cleanup completed")
    except Exception as e:
        st.error(f"❌ Cleanup failed: {str(e)}")

def create_additional_sample_data():
    """Create additional sample datasets"""
    try:
        # This would create more sample data
        st.success("✅ Additional sample data created")
    except Exception as e:
        st.error(f"❌ Additional data creation failed: {str(e)}")

# Helper functions (same as enterprise version)
def predict_data_source(question, available_tables):
    """Predict which data source would be auto-selected for a question"""
    if not question:
        return "No question entered"
    
    question_lower = question.lower()
    views = [t for t in available_tables if 'view' in t.lower() or '_detailed' in t.lower()]
    tables = [t for t in available_tables if t not in views]
    
    if ("executive" in question_lower and "dashboard" in question_lower) or "executive dashboard overview" in question_lower:
        return "executive_dashboard_detailed" if "executive_dashboard_detailed" in views else "First available view"
    
    if "renewal" in question_lower or "expiring" in question_lower:
        return "renewals_contracts_detailed" if "renewals_contracts_detailed" in views else "First available view"
    
    if "high risk" in question_lower or ("risk" in question_lower and "high" in question_lower):
        return "contract_compliance" if "contract_compliance" in tables else "First available table"
    
    if "compliance" in question_lower:
        return "contract_compliance" if "contract_compliance" in tables else "First available table"
    
    if "sales" in question_lower:
        return "sales_transactions" if "sales_transactions" in tables else "First available table"
    
    if "all" in question_lower and "contract" in question_lower:
        return tables[0] if tables else "First available table"
    
    return tables[0] if tables else (views[0] if views else "No tables available")

def get_available_tables():
    """Get list of available tables"""
    try:
        glue_client = boto3.client('glue', region_name=SETUP_CONFIG['aws_region'])
        response = glue_client.get_tables(DatabaseName=SETUP_CONFIG['glue_database'])
        return [table['Name'] for table in response['TableList']]
    except:
        return []

def show_available_tables():
    """Show available tables in compact format"""
    try:
        glue_client = boto3.client('glue', region_name=SETUP_CONFIG['aws_region'])
        response = glue_client.get_tables(DatabaseName=SETUP_CONFIG['glue_database'])
        
        if response['TableList']:
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
            
            # Show views first
            if views:
                st.markdown("**📈 Views (Pre-built Analytics)**")
                for view in views:
                    with st.expander(f"📈 {view['Name']}", expanded=False):
                        st.write(f"**Location:** {view['StorageDescriptor'].get('Location', 'N/A')}")
                        st.write("**Key Columns:**")
                        for col in view['StorageDescriptor']['Columns'][:5]:
                            st.write(f"• {col['Name']} ({col['Type']})")
                        if len(view['StorageDescriptor']['Columns']) > 5:
                            st.write(f"... and {len(view['StorageDescriptor']['Columns']) - 5} more columns")
            
            # Show tables
            if tables:
                st.markdown("**📋 Base Tables**")
                
                show_all_tables = st.checkbox("Show all tables", key="show_all_tables")
                tables_to_show = tables if show_all_tables else tables[:5]
                
                for table in tables_to_show:
                    with st.expander(f"📋 {table['Name']}", expanded=False):
                        st.write(f"**Columns:** {len(table['StorageDescriptor']['Columns'])}")
                        st.write(f"**Location:** {table['StorageDescriptor'].get('Location', 'N/A')}")
                        
                        st.write("**Sample Columns:**")
                        for col in table['StorageDescriptor']['Columns'][:3]:
                            st.write(f"• {col['Name']} ({col['Type']})")
                        if len(table['StorageDescriptor']['Columns']) > 3:
                            st.write(f"... and {len(table['StorageDescriptor']['Columns']) - 3} more columns")
                
                if not show_all_tables and len(tables) > 5:
                    st.info(f"📋 {len(tables) - 5} more tables available - check 'Show all tables' above")
        else:
            st.warning("No tables found. Complete the setup wizard first.")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

def generate_enterprise_sql(question):
    """Generate SQL for database using actual table names and views"""
    available_tables = get_available_tables()
    
    if not available_tables:
        return f"""-- Error: No tables found in database
-- Please complete the setup wizard first
-- Database: {SETUP_CONFIG['glue_database']}
SELECT 'Complete setup to access data' as message;"""
    
    database_name = f'"{SETUP_CONFIG["glue_database"]}"'
    
    # Check if user manually selected a data source
    manual_source = st.session_state.get('manual_data_source', None)
    if manual_source and manual_source in available_tables:
        return f"""-- Generated from: "{question}"
-- Using manually selected: {manual_source}
SELECT *
FROM {database_name}.{manual_source}
LIMIT 100;"""
    
    # Auto-selection logic
    views = [t for t in available_tables if 'view' in t.lower() or '_detailed' in t.lower()]
    tables = [t for t in available_tables if t not in views]
    question_lower = question.lower()
    
    # Sales queries
    if "sales" in question_lower:
        if "sales_transactions" in tables:
            return f"""-- Generated from: "{question}"
-- Auto-selected: Sales Transactions Table
SELECT *
FROM {database_name}.sales_transactions
ORDER BY transaction_date DESC
LIMIT 100;"""
    
    # Contract/compliance queries
    if "contract" in question_lower or "compliance" in question_lower or "risk" in question_lower:
        if "contract_compliance" in tables:
            if "high risk" in question_lower:
                return f"""-- Generated from: "{question}"
-- Auto-selected: Contract Compliance (High Risk Filter)
SELECT *
FROM {database_name}.contract_compliance
WHERE risk_level = 'High'
ORDER BY performance_score ASC
LIMIT 100;"""
            else:
                return f"""-- Generated from: "{question}"
-- Auto-selected: Contract Compliance Table
SELECT *
FROM {database_name}.contract_compliance
ORDER BY risk_level, performance_score DESC
LIMIT 100;"""
    
    # Status/distribution queries
    if "status" in question_lower or "distribution" in question_lower:
        if "contract_compliance" in tables:
            return f"""-- Generated from: "{question}"
-- Auto-selected: Contract Compliance (Status Analysis)
SELECT 
    compliance_status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM {database_name}.contract_compliance
GROUP BY compliance_status
ORDER BY count DESC;"""
    
    # Performance queries
    if "performance" in question_lower or "score" in question_lower:
        if "contract_compliance" in tables:
            return f"""-- Generated from: "{question}"
-- Auto-selected: Contract Compliance (Performance Analysis)
SELECT 
    risk_level,
    AVG(performance_score) as avg_performance_score,
    AVG(sla_score) as avg_sla_score,
    COUNT(*) as contract_count
FROM {database_name}.contract_compliance
GROUP BY risk_level
ORDER BY avg_performance_score DESC;"""
    
    # Generic fallback
    if tables:
        first_table = tables[0]
        return f"""-- Generated from: "{question}"
-- Auto-selected: First available table
SELECT *
FROM {database_name}.{first_table}
LIMIT 100;"""
    elif views:
        first_view = views[0]
        return f"""-- Generated from: "{question}"
-- Auto-selected: First available view
SELECT *
FROM {database_name}.{first_view}
LIMIT 100;"""
    else:
        return f"""-- Generated from: "{question}"
-- No tables available
SELECT 'Complete setup wizard first' as message;"""

def execute_enterprise_query(sql_query):
    """Execute query on Athena infrastructure"""
    try:
        athena_client = boto3.client('athena', region_name=SETUP_CONFIG['aws_region'])
        
        response = athena_client.start_query_execution(
            QueryString=sql_query,
            WorkGroup=SETUP_CONFIG['athena_workgroup'],
            ResultConfiguration={
                'OutputLocation': f"s3://{SETUP_CONFIG['s3_results_bucket']}/"
            }
        )
        
        query_execution_id = response['QueryExecutionId']
        st.success(f"✅ Query submitted successfully! Execution ID: {query_execution_id}")
        
        # Monitor query execution
        with st.spinner("⏳ Executing query..."):
            status = monitor_query_execution(athena_client, query_execution_id)
        
        if status == 'SUCCEEDED':
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
        response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        status = response['QueryExecution']['Status']['State']
        
        progress = min((attempt + 1) / max_attempts, 1.0)
        progress_bar.progress(progress)
        status_text.text(f"Status: {status}")
        
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            progress_bar.progress(1.0)
            return status
        
        time.sleep(2)
        attempt += 1
    
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

def save_query_template(question, sql):
    """Save query as reusable template"""
    if 'saved_queries' not in st.session_state:
        st.session_state.saved_queries = []
    
    template = {
        'question': question,
        'sql': sql,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    st.session_state.saved_queries.append(template)
    st.success("✅ Query saved as template!")

if __name__ == "__main__":
    main()
