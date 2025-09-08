import streamlit as st
import boto3
import pandas as pd
import time
from datetime import datetime
import os
from dotenv import load_dotenv

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
    """Simple password protection for demo sharing"""
    def password_entered():
        if st.session_state.get("password", "") == "athena-demo-2024":
            st.session_state["password_correct"] = True
            if "password" in st.session_state:
                del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h2>🔐 Athena Query Generator</h2>
            <p>Enter password to access the demo</p>
        </div>
        """, unsafe_allow_html=True)
        st.text_input("Password", type="password", on_change=password_entered, key="password", 
                     placeholder="Enter demo password")
        st.info("💡 Contact the administrator for access credentials")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h2>🔐 Athena Query Generator</h2>
            <p>Enter password to access the demo</p>
        </div>
        """, unsafe_allow_html=True)
        st.text_input("Password", type="password", on_change=password_entered, key="password",
                     placeholder="Enter demo password")
        st.error("❌ Incorrect password. Please try again.")
        return False
    else:
        return True

def main():
    # Password protection - must be first
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
        
        selected_account = st.selectbox(
            "Select AWS Account:",
            list(ACCOUNT_CONFIGS.keys())
        )
        
        current_config = ACCOUNT_CONFIGS[selected_account]
        st.session_state.current_config = current_config
        
        # Connection test
        if st.button("🔍 Test Connection", use_container_width=True):
            test_connection_status(current_config)
        
        # Account info
        with st.expander("📋 Account Details"):
            st.write(f"**Account:** {current_config['aws_account_id']}")
            st.write(f"**Database:** {current_config['glue_database']}")
    
    # Main interface - Single page with better organization
    show_main_interface(current_config)

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
            st.rerun()
        
        if st.button("📋 Renewals", use_container_width=True):
            question = "Display contracts up for renewal"
            st.session_state.quick_question = question
            # Auto-generate query
            generated_sql = generate_enterprise_sql(question, config)
            st.session_state.current_sql = generated_sql
            st.session_state.current_question = question
            st.rerun()
        
        if st.button("⚠️ High Risk", use_container_width=True):
            question = "Which contracts are high risk?"
            st.session_state.quick_question = question
            # Auto-generate query
            generated_sql = generate_enterprise_sql(question, config)
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
        
        # Export options
        st.markdown("### 📤 Export to QuickSight")
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
        
        # Show helpful info
        if 'query_execution_id' in st.session_state:
            s3_location = f"s3://{config['s3_results_bucket']}/{st.session_state.query_execution_id}.csv"
            st.info(f"""
            **💡 In QuickSight Datasets page:**
            1. Click "New dataset" 
            2. Choose "Athena" as data source
            3. Database: `{config['glue_database']}`
            4. Query results location: `{s3_location}`
            """)
    
    # Saved Queries Section
    if 'saved_queries' in st.session_state and st.session_state.saved_queries:
        st.markdown("### 💾 Saved Query Templates")
        
        for i, template in enumerate(reversed(st.session_state.saved_queries[-3:])):  # Show last 3
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
    """Get AWS clients - simplified for Streamlit Cloud"""
    # Use environment variables from Streamlit secrets (no profiles)
    return {
        'athena': boto3.client('athena', region_name=config['aws_region']),
        'glue': boto3.client('glue', region_name=config['aws_region'])
    }
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
    
    # Check if user manually selected a data source
    manual_source = st.session_state.get('manual_data_source', None)
    if manual_source and manual_source in available_tables:
        return f"""-- Generated from: "{question}"
-- Using manually selected: {manual_source}
SELECT *
FROM {database_name}.{manual_source}
LIMIT 100;"""
    
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
LIMIT 100;"""
    
    # Renewals queries - HIGH PRIORITY
    if "renewal" in question_lower or "expiring" in question_lower:
        if "renewals_contracts_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Auto-selected: Renewals Team View
SELECT *
FROM {database_name}.renewals_contracts_detailed
WHERE End_Date <= DATE_ADD('month', 6, CURRENT_DATE)
ORDER BY End_Date ASC
LIMIT 100;"""
    
    # High risk queries - HIGH PRIORITY
    if "high risk" in question_lower or ("risk" in question_lower and "high" in question_lower):
        if "compliance_contracts_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Using Compliance Team View for High Risk
SELECT *
FROM {database_name}.compliance_contracts_detailed
WHERE Risk_Level = 'High'
ORDER BY Performance_Score ASC
LIMIT 100;"""
    
    # Compliance queries - MEDIUM PRIORITY
    if "compliance" in question_lower:
        if "compliance_contracts_detailed" in views:
            return f"""-- Generated from: "{question}"
-- Using Compliance Team View
SELECT *
FROM {database_name}.compliance_contracts_detailed
ORDER BY Risk_Level, Performance_Score DESC
LIMIT 100;"""
    
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
    
    # "All contract data" - SPECIFIC MATCH
    if "all" in question_lower and "contract" in question_lower:
        # Use the first table (not view) for raw data
        if tables:
            first_table = tables[0]
            return f"""-- Generated from: "{question}"
-- Using base table for all contract data
SELECT *
FROM {database_name}.{first_table}
LIMIT 100;"""
    
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
LIMIT 100;"""
    
    # Final fallback - use first available item
    if tables:
        first_table = tables[0]
        return f"""-- Generated from: "{question}"
-- Using base table: {first_table}
SELECT *
FROM {database_name}.{first_table}
LIMIT 100;"""
    elif views:
        first_view = views[0]
        return f"""-- Generated from: "{question}"
-- Using view: {first_view}
SELECT *
FROM {database_name}.{first_view}
LIMIT 100;"""
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
