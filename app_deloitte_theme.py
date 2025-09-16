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

# Configuration selector - Same as original
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
    "Account 2 (476169753480) - Demo": {
        'aws_region': 'us-east-1',
        'aws_account_id': '476169753480',
        'athena_workgroup': 'primary',
        's3_results_bucket': 'aws-athena-query-results-us-east-1-476169753480',
        'glue_database': 's3-glue-athena-enterprise-analytics-db',
        's3_raw_data': 's3://s3-glue-athena-aidlc/contracts/',
        'quicksight_account_id': '476169753480'
    }
}

# Page configuration
st.set_page_config(
    page_title="Athena Query Generator - Deloitte Theme",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deloitte-inspired CSS theme
st.markdown("""
<style>
    /* Deloitte Color Variables */
    :root {
        --deloitte-green: #86BC25;
        --deloitte-dark-green: #62A70F;
        --deloitte-light-green: #A3D154;
        --deloitte-black: #000000;
        --deloitte-charcoal: #2C2C2C;
        --deloitte-gray: #8C8C8C;
        --deloitte-light-gray: #F5F5F5;
        --deloitte-navy: #003366;
        --deloitte-steel: #4A90A4;
        --deloitte-white: #FFFFFF;
    }
    
    /* Main App Background */
    .stApp {
        background-color: var(--deloitte-white);
        color: var(--deloitte-black);
    }
    
    /* Header Styling */
    .deloitte-header {
        background: linear-gradient(135deg, var(--deloitte-white) 0%, var(--deloitte-light-gray) 100%);
        padding: 2rem;
        border-radius: 8px;
        border-left: 6px solid var(--deloitte-green);
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .deloitte-header h1 {
        color: var(--deloitte-charcoal);
        margin: 0;
        font-weight: 600;
    }
    
    .deloitte-header p {
        color: var(--deloitte-gray);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: var(--deloitte-light-gray);
        border-right: 2px solid var(--deloitte-green);
    }
    
    /* Metric Cards */
    .deloitte-metric {
        background: var(--deloitte-white);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        border-left: 4px solid var(--deloitte-green);
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .deloitte-metric h3 {
        color: var(--deloitte-green);
        margin: 0;
        font-size: 2rem;
        font-weight: bold;
    }
    
    .deloitte-metric p {
        color: var(--deloitte-charcoal);
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--deloitte-green), var(--deloitte-dark-green));
        color: var(--deloitte-white);
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(134, 188, 37, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--deloitte-dark-green), var(--deloitte-green));
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(134, 188, 37, 0.4);
    }
    
    /* Secondary Button */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, var(--deloitte-navy), var(--deloitte-steel));
        box-shadow: 0 2px 4px rgba(0, 51, 102, 0.3);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, var(--deloitte-steel), var(--deloitte-navy));
        box-shadow: 0 4px 8px rgba(0, 51, 102, 0.4);
    }
    
    /* Query Container */
    .deloitte-query-container {
        background: var(--deloitte-white);
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        margin: 1rem 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background-color: rgba(163, 209, 84, 0.1);
        border-left: 4px solid var(--deloitte-light-green);
    }
    
    .stError {
        background-color: rgba(220, 53, 69, 0.1);
        border-left: 4px solid #dc3545;
    }
    
    .stInfo {
        background-color: rgba(74, 144, 164, 0.1);
        border-left: 4px solid var(--deloitte-steel);
    }
    
    .stWarning {
        background-color: rgba(255, 193, 7, 0.1);
        border-left: 4px solid #ffc107;
    }
    
    /* Selectbox and Input Styling */
    .stSelectbox > div > div {
        border: 2px solid #E0E0E0;
        border-radius: 6px;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: var(--deloitte-green);
        box-shadow: 0 0 0 2px rgba(134, 188, 37, 0.2);
    }
    
    .stTextArea > div > div > textarea {
        border: 2px solid #E0E0E0;
        border-radius: 6px;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--deloitte-green);
        box-shadow: 0 0 0 2px rgba(134, 188, 37, 0.2);
    }
    
    /* Dataframe Styling */
    .stDataFrame {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: var(--deloitte-light-gray);
        border-left: 4px solid var(--deloitte-green);
    }
    
    /* Code Block Styling */
    .stCodeBlock {
        border-left: 4px solid var(--deloitte-green);
        background-color: #F8F9FA;
    }
    
    /* Professional Links */
    .deloitte-link {
        display: inline-block;
        padding: 0.75rem 1.5rem;
        background: linear-gradient(135deg, var(--deloitte-charcoal), var(--deloitte-navy));
        color: var(--deloitte-white);
        text-decoration: none;
        border-radius: 6px;
        font-weight: 600;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(44, 44, 44, 0.3);
    }
    
    .deloitte-link:hover {
        background: linear-gradient(135deg, var(--deloitte-navy), var(--deloitte-charcoal));
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(44, 44, 44, 0.4);
        color: var(--deloitte-white);
        text-decoration: none;
    }
    
    /* Status Indicators */
    .status-connected {
        background: linear-gradient(135deg, var(--deloitte-light-green), var(--deloitte-green));
        color: var(--deloitte-white);
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-disconnected {
        background: linear-gradient(135deg, #dc3545, #c82333);
        color: var(--deloitte-white);
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Professional Card Layout */
    .deloitte-card {
        background: var(--deloitte-white);
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .deloitte-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

def check_password():
    """Simple password protection for demo sharing - Deloitte theme"""
    def password_entered():
        # Safe password check to prevent KeyError
        password_value = st.session_state.get("password", "")
        if password_value == "deloitte-demo-2024":
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
        <div style="text-align: center; padding: 3rem; background: var(--deloitte-light-gray); border-radius: 12px; border-left: 6px solid var(--deloitte-green);">
            <h2 style="color: var(--deloitte-charcoal); margin-bottom: 1rem;">🟢 Athena Query Generator</h2>
            <h3 style="color: var(--deloitte-green); margin-bottom: 2rem;">Deloitte Professional Theme</h3>
            <p style="color: var(--deloitte-gray); font-size: 1.1rem;">Enter password to access the demo</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show error only if password was attempted
        if "password_attempted" in st.session_state and st.session_state["password_attempted"]:
            st.error("❌ Incorrect password. Please try again.")
        
        password_input = st.text_input("Password", type="password", key="password_input", 
                     placeholder="Enter demo password")
        
        if st.button("🔐 Access Demo", type="primary"):
            st.session_state["password_attempted"] = True
            if password_input == "deloitte-demo-2024":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.session_state["password_correct"] = False
                st.rerun()
        
        st.info("💡 Password: deloitte-demo-2024")
        return False
    else:
        return True

def main():
    # Password protection - must be first
    try:
        if not check_password():
            st.stop()
        
        # Header with Deloitte styling
        st.markdown("""
        <div class="deloitte-header">
            <h1>🟢 Athena Query Generator</h1>
            <p>Professional Analytics Platform - Deloitte Theme</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar configuration
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
                **Professional Theme Demo:**
                
                • **Deloitte-inspired** color scheme and styling
                • **Enterprise-grade** visual design
                • **Professional** user experience
                
                **Multi-Account Capability:**
                • Account 2: Live data and full functionality
                • Account 1: UI demonstration
                
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
    """Main query interface with Deloitte professional styling"""
    
    # Professional metrics dashboard
    st.markdown("### 📊 Business Intelligence Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="deloitte-metric">
            <h3>1,234</h3>
            <p>Total Contracts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="deloitte-metric">
            <h3>45</h3>
            <p>High Risk</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="deloitte-metric">
            <h3>23</h3>
            <p>Expiring Soon</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="deloitte-metric">
            <h3>94%</h3>
            <p>Compliance Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Query interface with professional styling
    st.markdown("### 💼 Natural Language Query Interface")
    
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
        selected_example = st.selectbox("📝 Professional Query Templates:", [""] + example_questions)
        
        # Handle quick actions
        default_question = ""
        if 'quick_question' in st.session_state:
            default_question = st.session_state.quick_question
            del st.session_state.quick_question
        elif selected_example:
            default_question = selected_example
        
        user_question = st.text_area(
            "Business Question:",
            value=default_question,
            placeholder="Example: Show me the executive dashboard overview",
            height=100,
            key="question_input"
        )
        
        # Data source selector
        available_tables = get_available_tables(config)
        if available_tables:
            auto_selected = predict_data_source(user_question, available_tables) if user_question else "Auto-select based on question"
            
            data_source_options = ["🤖 Smart Selection"] + available_tables
            selected_data_source = st.selectbox(
                f"🎯 Data Source (Recommended: {auto_selected}):",
                data_source_options,
                help="Choose 'Smart Selection' for intelligent data source selection"
            )
            
            st.session_state.manual_data_source = selected_data_source if selected_data_source != "🤖 Smart Selection" else None
    
    with col2:
        st.markdown("**🎯 Quick Actions**")
        
        if st.button("📈 Executive Dashboard", use_container_width=True):
            question = "Show me the executive dashboard overview"
            st.session_state.quick_question = question
            generated_sql = generate_enterprise_sql(question, config)
            st.session_state.current_sql = generated_sql
            st.session_state.current_question = question
            st.rerun()
        
        if st.button("📋 Contract Renewals", use_container_width=True):
            question = "Display contracts up for renewal"
            st.session_state.quick_question = question
            generated_sql = generate_enterprise_sql(question, config)
            st.session_state.current_sql = generated_sql
            st.session_state.current_question = question
            st.rerun()
        
        if st.button("⚠️ Risk Assessment", use_container_width=True):
            question = "Which contracts are high risk?"
            st.session_state.quick_question = question
            generated_sql = generate_enterprise_sql(question, config)
            st.session_state.current_sql = generated_sql
            st.session_state.current_question = question
            st.rerun()
        
        if st.button("📊 Data Explorer", use_container_width=True):
            st.session_state.show_tables = True
    
    # Show tables in professional expandable section
    if st.session_state.get('show_tables', False):
        with st.expander("📊 Available Data Sources", expanded=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                show_available_tables(config)
            with col2:
                if st.button("❌ Close Explorer", use_container_width=True):
                    st.session_state.show_tables = False
                    st.rerun()
    
    # Generate and Execute buttons with professional styling
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Generate Query", type="primary", use_container_width=True):
            current_question = user_question
            if current_question and current_question.strip():
                with st.spinner("🤖 Processing your business question..."):
                    generated_sql = generate_enterprise_sql(current_question, config)
                    st.session_state.current_sql = generated_sql
                    st.session_state.current_question = current_question
                    st.success("✅ Query generated successfully! Review and execute below.")
            else:
                st.warning("Please enter a business question first.")
    
    with col2:
        if st.button("▶️ Execute Analysis", type="secondary", use_container_width=True):
            if 'current_sql' in st.session_state:
                execute_enterprise_query(st.session_state.current_sql, config)
            else:
                st.warning("Please generate a query first.")
    
    # Display generated SQL with professional styling
    if 'current_sql' in st.session_state:
        st.markdown("### 📝 Generated SQL Query")
        st.code(st.session_state.current_sql, language="sql")
        
        # Professional action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✏️ Edit Query", use_container_width=True):
                st.session_state.edit_mode = True
        
        with col2:
            if st.button("💾 Save Template", use_container_width=True):
                save_query_template(st.session_state.current_question, st.session_state.current_sql)
        
        with col3:
            athena_console_url = f"https://{config['aws_region']}.console.aws.amazon.com/athena/home?region={config['aws_region']}#/query-editor"
            st.markdown(f"""
            <a href="{athena_console_url}" target="_blank" class="deloitte-link">
                🔗 Athena Console
            </a>
            """, unsafe_allow_html=True)
        
        with col4:
            if 'query_results' in st.session_state:
                quicksight_datasets_url = f"https://{config['aws_region']}.quicksight.aws.amazon.com/sn/start/data-sets"
                st.markdown(f"""
                <a href="{quicksight_datasets_url}" target="_blank" class="deloitte-link">
                    📊 QuickSight
                </a>
                """, unsafe_allow_html=True)
            else:
                st.button("📊 QuickSight", disabled=True, help="Execute query first", use_container_width=True)
    
    # Edit mode with professional styling
    if st.session_state.get('edit_mode', False):
        st.markdown("### ✏️ Query Editor")
        edited_sql = st.text_area(
            "Modify SQL Query:",
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
            if st.button("❌ Cancel Changes", use_container_width=True):
                st.session_state.edit_mode = False
                st.rerun()
    
    # Results Section with professional styling
    if 'query_results' in st.session_state:
        st.markdown("### 📊 Analysis Results")
        
        df = st.session_state.query_results
        
        # Professional results summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Records Retrieved", len(df))
        with col2:
            st.metric("Data Columns", len(df.columns))
        with col3:
            st.metric("Query Status", "✅ Success")
        
        # Professional data display
        st.dataframe(df, use_container_width=True, height=400)
        
        # Professional export options with QuickSight integration
        st.markdown("### 📤 Business Intelligence Export")
        
        # Render QuickSight export UI
        render_quicksight_export_ui(config, df, st.session_state.get('query_execution_id'))
        
        # Professional guidance
        if 'query_execution_id' in st.session_state:
            s3_location = f"s3://{config['s3_results_bucket']}/{st.session_state.query_execution_id}.csv"
            st.info(f"""
            **💡 Professional Integration Guide:**
            1. Use the QuickSight export above to create visualizations
            2. Data location: `{s3_location}`
            3. Database: `{config['glue_database']}`
            """)
    
    # Professional saved queries section
    if 'saved_queries' in st.session_state and st.session_state.saved_queries:
        st.markdown("### 💾 Query Template Library")
        
        for i, template in enumerate(reversed(st.session_state.saved_queries[-3:])):
            with st.expander(f"📝 {template['question']} - {template['timestamp']}"):
                st.code(template['sql'], language="sql")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("🔄 Load Template", key=f"load_{i}", use_container_width=True):
                        st.session_state.current_sql = template['sql']
                        st.session_state.current_question = template['question']
                        st.success(f"✅ Loaded: {template['question']}")
                        
                with col2:
                    if st.button("▶️ Execute Now", key=f"exec_{i}", use_container_width=True):
                        st.session_state.current_sql = template['sql']
                        st.session_state.current_question = template['question']
                        execute_enterprise_query(template['sql'], config)
                        
                with col3:
                    if st.button("🗑️ Remove", key=f"delete_{i}", use_container_width=True):
                        actual_index = len(st.session_state.saved_queries) - 1 - i
                        st.session_state.saved_queries.pop(actual_index)
                        st.rerun()

# Include all helper functions from the original app
def get_aws_clients(config):
    """Get AWS clients - works for both localhost and Streamlit Cloud"""
    try:
        # Try Streamlit Cloud secrets first
        if hasattr(st, 'secrets') and 'aws' in st.secrets:
            return {
                'athena': boto3.client(
                    'athena', 
                    region_name=config['aws_region'],
                    aws_access_key_id=st.secrets['aws']['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=st.secrets['aws']['AWS_SECRET_ACCESS_KEY']
                ),
                'glue': boto3.client(
                    'glue', 
                    region_name=config['aws_region'],
                    aws_access_key_id=st.secrets['aws']['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=st.secrets['aws']['AWS_SECRET_ACCESS_KEY']
                )
            }
    except Exception:
        pass
    
    # Try environment variables or AWS profiles (localhost)
    try:
        if config['aws_account_id'] == '476169753480':
            session = boto3.Session(profile_name='brew-demo')
            return {
                'athena': session.client('athena', region_name=config['aws_region']),
                'glue': session.client('glue', region_name=config['aws_region'])
            }
        else:
            return {
                'athena': boto3.client('athena', region_name=config['aws_region']),
                'glue': boto3.client('glue', region_name=config['aws_region'])
            }
    except Exception as e:
        st.error(f"AWS client creation error: {str(e)}")
        return {
            'athena': boto3.client('athena', region_name=config['aws_region']),
            'glue': boto3.client('glue', region_name=config['aws_region'])
        }

def test_connection_status(config):
    """Test connection with professional status display"""
    try:
        clients = get_aws_clients(config)
        athena_client = clients['athena']
        
        response = athena_client.list_databases(CatalogName='AwsDataCatalog')
        databases = [db['Name'] for db in response['DatabaseList']]
        
        if config['glue_database'] in databases:
            st.markdown('<div class="status-connected">✅ Connected Successfully</div>', unsafe_allow_html=True)
            st.success(f"Database accessible: {config['glue_database']}")
            
            glue_client = clients['glue']
            tables_response = glue_client.get_tables(DatabaseName=config['glue_database'])
            table_count = len(tables_response['TableList'])
            st.info(f"📊 Available data sources: {table_count}")
        else:
            st.markdown('<div class="status-disconnected">❌ Connection Failed</div>', unsafe_allow_html=True)
            st.error(f"Database not found: {config['glue_database']}")
            
    except Exception as e:
        st.markdown('<div class="status-disconnected">❌ Connection Error</div>', unsafe_allow_html=True)
        st.error(f"Connection failed: {str(e)}")

# Add all other helper functions (same as original)
def predict_data_source(question, available_tables):
    if not question:
        return "No question entered"
    
    question_lower = question.lower()
    views = [t for t in available_tables if 'view' in t.lower() or '_detailed' in t.lower()]
    tables = [t for t in available_tables if t not in views]
    
    if ("executive" in question_lower and "dashboard" in question_lower):
        return "executive_dashboard_detailed" if "executive_dashboard_detailed" in views else "First available view"
    if "renewal" in question_lower or "expiring" in question_lower:
        return "renewals_contracts_detailed" if "renewals_contracts_detailed" in views else "First available view"
    if "high risk" in question_lower or ("risk" in question_lower and "high" in question_lower):
        return "compliance_contracts_detailed" if "compliance_contracts_detailed" in views else "First available view"
    if "compliance" in question_lower:
        return "compliance_contracts_detailed" if "compliance_contracts_detailed" in views else "First available view"
    
    return tables[0] if tables else (views[0] if views else "No tables available")

def get_available_tables(config):
    try:
        clients = get_aws_clients(config)
        glue_client = clients['glue']
        response = glue_client.get_tables(DatabaseName=config['glue_database'])
        return [table['Name'] for table in response['TableList']]
    except:
        return []

def show_available_tables(config):
    try:
        clients = get_aws_clients(config)
        glue_client = clients['glue']
        response = glue_client.get_tables(DatabaseName=config['glue_database'])
        
        if response['TableList']:
            total_tables = len(response['TableList'])
            views = [t for t in response['TableList'] if 'view' in t['Name'].lower() or '_detailed' in t['Name'].lower()]
            tables = [t for t in response['TableList'] if t not in views]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Sources", total_tables)
            with col2:
                st.metric("Business Views", len(views))
            with col3:
                st.metric("Data Tables", len(tables))
            
            if views:
                st.markdown("**📈 Business Intelligence Views**")
                for view in views:
                    with st.expander(f"📈 {view['Name']}", expanded=False):
                        st.write(f"**Location:** {view['StorageDescriptor'].get('Location', 'N/A')}")
                        st.write("**Key Columns:**")
                        for col in view['StorageDescriptor']['Columns'][:5]:
                            st.write(f"• {col['Name']} ({col['Type']})")
            
            if tables:
                st.markdown("**📋 Data Tables**")
                show_all_tables = st.checkbox("Show all tables", key="show_all_tables")
                tables_to_show = tables if show_all_tables else tables[:5]
                
                for table in tables_to_show:
                    with st.expander(f"📋 {table['Name']}", expanded=False):
                        st.write(f"**Columns:** {len(table['StorageDescriptor']['Columns'])}")
                        st.write(f"**Location:** {table['StorageDescriptor'].get('Location', 'N/A')}")
        else:
            st.warning("No data sources found.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def generate_enterprise_sql(question, config):
    available_tables = get_available_tables(config)
    
    if not available_tables:
        return f"""-- Error: No tables found in database
-- Database: {config['glue_database']}
SELECT 'No tables available' as message;"""
    
    database_name = f'"{config["glue_database"]}"'
    manual_source = st.session_state.get('manual_data_source', None)
    
    if manual_source and manual_source in available_tables:
        return f"""-- Generated from: "{question}"
-- Using manually selected: {manual_source}
SELECT *
FROM {database_name}.{manual_source}
LIMIT 100;"""
    
    views = [t for t in available_tables if 'view' in t.lower() or '_detailed' in t.lower()]
    tables = [t for t in available_tables if t not in views]
    question_lower = question.lower()
    
    if ("executive" in question_lower and "dashboard" in question_lower):
        if "executive_dashboard_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Auto-selected: Executive Dashboard View
SELECT *
FROM {database_name}.executive_dashboard_detailed
ORDER BY Value DESC
LIMIT 100;"""
    
    if "renewal" in question_lower or "expiring" in question_lower:
        if "renewals_contracts_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Auto-selected: Renewals Team View
SELECT *
FROM {database_name}.renewals_contracts_detailed
WHERE End_Date <= DATE_ADD('month', 6, CURRENT_DATE)
ORDER BY End_Date ASC
LIMIT 100;"""
    
    if "high risk" in question_lower or ("risk" in question_lower and "high" in question_lower):
        if "compliance_contracts_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Auto-selected: Compliance Team View (High Risk Filter)
SELECT *
FROM {database_name}.compliance_contracts_detailed
WHERE Risk_Level = 'High'
ORDER BY Performance_Score ASC
LIMIT 100;"""
    
    if "compliance" in question_lower:
        if "compliance_contracts_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Auto-selected: Compliance Team View
SELECT *
FROM {database_name}.compliance_contracts_detailed
ORDER BY Risk_Level, Performance_Score DESC
LIMIT 100;"""
    
    if views:
        first_view = views[0]
        return f"""-- Generated from: "{question}"
-- Auto-selected: First available view
SELECT *
FROM {database_name}.{first_view}
LIMIT 100;"""
    else:
        first_table = available_tables[0]
        return f"""-- Generated from: "{question}"
-- Auto-selected: First available table
SELECT *
FROM {database_name}.{first_table}
LIMIT 100;"""

def execute_enterprise_query(sql_query, config):
    try:
        clients = get_aws_clients(config)
        athena_client = clients['athena']
        
        response = athena_client.start_query_execution(
            QueryString=sql_query,
            WorkGroup=config['athena_workgroup'],
            ResultConfiguration={'OutputLocation': f"s3://{config['s3_results_bucket']}/"}
        )
        
        query_execution_id = response['QueryExecutionId']
        st.success(f"✅ Query submitted successfully! ID: {query_execution_id}")
        
        with st.spinner("⏳ Executing analysis..."):
            status = monitor_query_execution(athena_client, query_execution_id)
        
        if status == 'SUCCEEDED':
            display_query_results(athena_client, query_execution_id)
        elif status == 'FAILED':
            st.error("❌ Query execution failed. Please review your SQL.")
        
    except Exception as e:
        st.error(f"❌ Query execution error: {str(e)}")

def monitor_query_execution(athena_client, query_execution_id):
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
    try:
        results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
        
        columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        rows = []
        
        for row in results['ResultSet']['Rows'][1:]:
            row_data = [field.get('VarCharValue', '') for field in row['Data']]
            rows.append(row_data)
        
        if rows:
            df = pd.DataFrame(rows, columns=columns)
            st.session_state.query_results = df
            st.session_state.query_execution_id = query_execution_id
            st.success(f"✅ Analysis completed! {len(df)} records retrieved.")
        else:
            st.info("Query executed successfully but returned no results.")
            
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")

def save_query_template(question, sql):
    """Save query as template with modern functionality"""
    import json
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
                f"Query {i+1}: {query['question'][:40]}..." 
                for i, query in enumerate(st.session_state.saved_queries)
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
                    st.session_state.current_question = query['question']
                    st.rerun()

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
                
                if access_key and secret_key:
                    account_config['aws_access_key_id'] = access_key
                    account_config['aws_secret_access_key'] = secret_key
                
                user_accounts[account_name] = account_config
                
                if save_user_accounts(user_accounts):
                    st.success(f"✅ Account '{account_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to save account configuration")
            else:
                st.error("Please fill in all required fields")

if __name__ == "__main__":
    main()
