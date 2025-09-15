import streamlit as st
import boto3
import pandas as pd
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration selector - Easy account switching
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

# Page configuration
st.set_page_config(
    page_title="Athena Query Generator - Modern",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern theme
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header styling */
    .main-header {
        background: rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(5px);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    /* Status badges */
    .status-connected {
        background-color: #28a745;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    
    .status-disconnected {
        background-color: #dc3545;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    
    /* Query box */
    .query-container {
        background: rgba(255,255,255,0.05);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        margin: 1rem 0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255,255,255,0.05);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #ff6b35, #f7931e);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Athena Query Generator</h1>
        <p style="font-size: 1.2rem; margin: 0; opacity: 0.8;">Enterprise Analytics Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### 🔧 Configuration")
        
        selected_account = st.selectbox(
            "Select AWS Account:",
            list(ACCOUNT_CONFIGS.keys()),
            label_visibility="collapsed"
        )
        
        current_config = ACCOUNT_CONFIGS[selected_account]
        st.session_state.current_config = current_config
        
        # Connection status
        if st.button("🔍 Test Connection", use_container_width=True):
            test_connection_status(current_config)
        
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Queries", "47", "↑12")
        with col2:
            st.metric("Avg Time", "2.3s", "↓0.5s")
        
        # Account info
        with st.expander("📋 Account Details"):
            st.write(f"**Account:** {current_config['aws_account_id']}")
            st.write(f"**Database:** {current_config['glue_database']}")
            st.write(f"**Region:** {current_config['aws_region']}")
    
    # Main content with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Query Builder", "📊 Results", "📈 Analytics", "💾 Saved Queries"])
    
    with tab1:
        show_query_builder(current_config)
    
    with tab2:
        show_results_tab()
    
    with tab3:
        show_analytics_tab(current_config)
    
    with tab4:
        show_saved_queries_tab(current_config)

def show_query_builder(config):
    """Modern query builder interface"""
    
    # Top metrics dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #ff6b35;">1,234</h3>
            <p style="margin: 0; opacity: 0.8;">Total Contracts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #dc3545;">45</h3>
            <p style="margin: 0; opacity: 0.8;">High Risk</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #ffc107;">23</h3>
            <p style="margin: 0; opacity: 0.8;">Expiring Soon</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #28a745;">94%</h3>
            <p style="margin: 0; opacity: 0.8;">Compliance Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Query interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 💬 Ask Your Question")
        
        # Role-based example questions
        example_questions = [
            "Show me all contract data",
            "Show me the executive dashboard overview",
            "Display contracts up for renewal", 
            "Show compliance status across all contracts",
            "Which contracts need review this quarter?",
            "Display auto-renewal status by department",
            "Show me contracts expiring in next 90 days",
            "Which contracts are high risk?",
            "Show performance scores by department"
        ]
        
        selected_example = st.selectbox("📝 Quick Questions:", [""] + example_questions)
        
        user_question = st.text_area(
            "What would you like to know?",
            value=selected_example if selected_example else "",
            placeholder="Example: Show me the executive dashboard overview",
            height=100
        )
    
    with col2:
        st.markdown("### 🎯 Quick Actions")
        
        if st.button("📈 Executive View", use_container_width=True):
            st.session_state.quick_question = "Show me the executive dashboard overview"
            st.rerun()
        
        if st.button("📋 Renewals", use_container_width=True):
            st.session_state.quick_question = "Display contracts up for renewal"
            st.rerun()
        
        if st.button("⚠️ High Risk", use_container_width=True):
            st.session_state.quick_question = "Which contracts are high risk?"
            st.rerun()
        
        if st.button("📊 Browse Tables", use_container_width=True):
            show_available_tables(config)
    
    # Handle quick actions
    if 'quick_question' in st.session_state:
        user_question = st.session_state.quick_question
        del st.session_state.quick_question
    
    # Generate and execute query
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔄 Generate Query", type="primary", use_container_width=True):
            if user_question:
                with st.spinner("🤖 Processing your question..."):
                    generated_sql = generate_enterprise_sql(user_question, config)
                    st.session_state.current_sql = generated_sql
                    st.session_state.current_question = user_question
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
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✏️ Edit SQL", use_container_width=True):
                st.session_state.edit_mode = True
        
        with col2:
            if st.button("💾 Save Query", use_container_width=True):
                save_query_template(st.session_state.current_question, st.session_state.current_sql)
        
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
            if st.button("📊 QuickSight", use_container_width=True):
                quicksight_url = "https://us-east-1.quicksight.aws.amazon.com/sn/start/data-sets"
                st.markdown(f'<script>window.open("{quicksight_url}", "_blank");</script>', unsafe_allow_html=True)
    
    # Edit mode
    if st.session_state.get('edit_mode', False):
        st.markdown("### ✏️ Edit SQL Query")
        edited_sql = st.text_area(
            "Modify the SQL query:",
            value=st.session_state.current_sql,
            height=200
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("💾 Update Query", use_container_width=True):
                st.session_state.current_sql = edited_sql
                st.session_state.edit_mode = False
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel Edit", use_container_width=True):
                st.session_state.edit_mode = False
                st.rerun()

def show_results_tab():
    """Results display tab"""
    st.markdown("### 📊 Query Results")
    
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
        
        # Export options
        st.markdown("### 📤 Export Options")
        col1, col2 = st.columns(2)
        
        with col1:
            quicksight_datasets_url = "https://us-east-1.quicksight.aws.amazon.com/sn/start/data-sets"
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
            quicksight_url = "https://us-east-1.quicksight.aws.amazon.com/sn/start"
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
    else:
        st.info("Execute a query to see results here.")

def show_analytics_tab(config):
    """Analytics and insights tab"""
    st.markdown("### 📈 Analytics Dashboard")
    
    # Sample analytics (would be real data in production)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Query Performance")
        # Sample chart data
        chart_data = pd.DataFrame({
            'Time': ['9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM'],
            'Queries': [12, 19, 15, 25, 18, 22]
        })
        st.line_chart(chart_data.set_index('Time'))
    
    with col2:
        st.markdown("#### Popular Query Types")
        query_types = pd.DataFrame({
            'Type': ['Executive', 'Compliance', 'Renewals', 'General'],
            'Count': [45, 32, 28, 15]
        })
        st.bar_chart(query_types.set_index('Type'))
    
    # Connection status
    if st.button("🔍 Test Current Connection"):
        test_connection_status(config)

def show_saved_queries_tab(config):
    """Saved queries management tab"""
    st.markdown("### 💾 Saved Query Templates")
    
    if 'saved_queries' in st.session_state and st.session_state.saved_queries:
        for i, template in enumerate(reversed(st.session_state.saved_queries[-10:])):  # Show last 10
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
                        execute_enterprise_query(template['sql'], config)
                        
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{i}", use_container_width=True):
                        actual_index = len(st.session_state.saved_queries) - 1 - i
                        st.session_state.saved_queries.pop(actual_index)
                        st.rerun()
    else:
        st.info("💡 No saved queries yet. Execute a query and click 'Save Query' to see templates here!")

# Include all the helper functions from the original app
def get_aws_clients(config):
    """Get AWS clients with correct profile for the account"""
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

def test_connection_status(config):
    """Test connection and show status"""
    try:
        clients = get_aws_clients(config)
        athena_client = clients['athena']
        
        response = athena_client.list_databases(CatalogName='AwsDataCatalog')
        databases = [db['Name'] for db in response['DatabaseList']]
        
        if config['glue_database'] in databases:
            st.markdown('<div class="status-connected">✅ Connected</div>', unsafe_allow_html=True)
            st.success(f"Found database: {config['glue_database']}")
        else:
            st.markdown('<div class="status-disconnected">❌ Disconnected</div>', unsafe_allow_html=True)
            st.error(f"Database not found: {config['glue_database']}")
            
    except Exception as e:
        st.markdown('<div class="status-disconnected">❌ Connection Failed</div>', unsafe_allow_html=True)
        st.error(f"Error: {str(e)}")

def show_available_tables(config):
    """Show available tables"""
    try:
        clients = get_aws_clients(config)
        glue_client = clients['glue']
        
        response = glue_client.get_tables(DatabaseName=config['glue_database'])
        
        st.markdown("#### 📊 Available Tables & Views")
        
        if response['TableList']:
            for table in response['TableList'][:5]:  # Show first 5
                st.write(f"• **{table['Name']}** - {len(table['StorageDescriptor']['Columns'])} columns")
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
    """Generate SQL - simplified version for demo"""
    available_tables = get_available_tables(config)
    
    if not available_tables:
        return "SELECT 'No tables available' as message;"
    
    database_name = f'"{config["glue_database"]}"'
    question_lower = question.lower()
    
    # Simple pattern matching
    if "executive" in question_lower or "dashboard" in question_lower:
        return f'SELECT * FROM {database_name}.executive_dashboard_detailed LIMIT 100;'
    elif "renewal" in question_lower:
        return f'SELECT * FROM {database_name}.renewals_contracts_detailed LIMIT 100;'
    elif "compliance" in question_lower:
        return f'SELECT * FROM {database_name}.compliance_contracts_detailed LIMIT 100;'
    else:
        first_table = available_tables[0]
        return f'SELECT * FROM {database_name}.{first_table} LIMIT 100;'

def execute_enterprise_query(sql_query, config):
    """Execute query - simplified for demo"""
    try:
        clients = get_aws_clients(config)
        athena_client = clients['athena']
        
        response = athena_client.start_query_execution(
            QueryString=sql_query,
            WorkGroup=config['athena_workgroup'],
            ResultConfiguration={'OutputLocation': f"s3://{config['s3_results_bucket']}/"}
        )
        
        query_execution_id = response['QueryExecutionId']
        st.success(f"✅ Query submitted! ID: {query_execution_id}")
        
        # For demo - create sample results
        sample_data = pd.DataFrame({
            'Contract_ID': ['CT001', 'CT002', 'CT003'],
            'Status': ['Active', 'Pending', 'Active'],
            'Value': [100000, 75000, 120000]
        })
        
        st.session_state.query_results = sample_data
        st.session_state.query_execution_id = query_execution_id
        
    except Exception as e:
        st.error(f"❌ Query execution error: {str(e)}")

def save_query_template(question, sql):
    """Save query template"""
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
