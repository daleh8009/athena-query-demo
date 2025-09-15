import streamlit as st
import boto3
import pandas as pd
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enterprise Configuration - Pre-configured infrastructure
ENTERPRISE_CONFIG = {
    'aws_region': 'us-east-1',
    'aws_account_id': '695233770948',
    'athena_workgroup': 'primary',
    's3_results_bucket': 'aws-athena-query-results-us-east-1-695233770948',
    'glue_database': 's3-athena-glue-enterprise-analytics-db',
    's3_raw_data': 's3://s3-glue-athena-demo-archive/contracts/',
    'quicksight_account_id': '695233770948'
}

# Page configuration
st.set_page_config(
    page_title="Athena Query Generator - Enterprise",
    page_icon="🏢",
    layout="wide"
)

def main():
    st.title("🏢 Athena Query Generator - Enterprise Edition")
    st.markdown("**Pre-configured for existing enterprise infrastructure**")
    
    # Display current configuration
    with st.expander("📋 Current Configuration"):
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Database:** {ENTERPRISE_CONFIG['glue_database']}")
            st.info(f"**Region:** {ENTERPRISE_CONFIG['aws_region']}")
            st.info(f"**Workgroup:** {ENTERPRISE_CONFIG['athena_workgroup']}")
        with col2:
            st.info(f"**Results Bucket:** {ENTERPRISE_CONFIG['s3_results_bucket']}")
            st.info(f"**Raw Data:** {ENTERPRISE_CONFIG['s3_raw_data']}")
    
    # Test connection
    if st.button("🔍 Test Enterprise Connection"):
        test_enterprise_connection()
    
    # Main chat interface
    st.header("💬 Ask Your Business Question")
    
    # Pre-defined example questions for enterprise contracts
    example_questions = [
        "Show me all contract data",
        "Show compliance status distribution",
        "List top 10 contracts by performance score",
        "Show performance by risk level",
        "Show KPI achievement rates",
        "Find high risk contracts"
    ]
    
    selected_example = st.selectbox("📝 Try an example question:", [""] + example_questions)
    
    # Chat input
    user_question = st.text_area(
        "What would you like to know about your contracts data?",
        value=selected_example if selected_example else "",
        placeholder="Example: Show me total contract values by region for Q1 2024",
        height=100
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔄 Generate Query", type="primary"):
            if user_question:
                with st.spinner("🤖 Processing your question..."):
                    generated_sql = generate_enterprise_sql(user_question)
                    st.session_state.current_sql = generated_sql
                    st.session_state.current_question = user_question
            else:
                st.warning("Please enter a question first.")
    
    with col2:
        if st.button("📊 Browse Available Tables"):
            show_available_tables()
    
    # Display generated SQL
    if 'current_sql' in st.session_state:
        st.subheader("📝 Generated SQL Query")
        st.code(st.session_state.current_sql, language="sql")
        
        # Query explanation
        st.subheader("💡 Query Explanation")
        explain_query(st.session_state.current_question, st.session_state.current_sql)
        
        # Execute query section
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("▶️ Execute Query", type="primary"):
                execute_enterprise_query(st.session_state.current_sql)
        
        with col2:
            if st.button("✏️ Edit SQL"):
                st.session_state.edit_mode = True
        
        with col3:
            if st.button("💾 Save Query"):
                save_query_template(st.session_state.current_question, st.session_state.current_sql)
                
        with col4:
            # Copy to clipboard for Athena console
            athena_console_url = f"https://us-east-1.console.aws.amazon.com/athena/home?region=us-east-1#/query-editor"
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
            ">🔗 Run in Athena</a>
            """, unsafe_allow_html=True)
    
    # Edit mode
    if st.session_state.get('edit_mode', False):
        st.subheader("✏️ Edit SQL Query")
        edited_sql = st.text_area(
            "Modify the SQL query:",
            value=st.session_state.current_sql,
            height=200
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("💾 Update Query"):
                st.session_state.current_sql = edited_sql
                st.session_state.edit_mode = False
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel Edit"):
                st.session_state.edit_mode = False
                st.rerun()
    
    # Display saved query templates
    st.header("📚 Saved Query Templates")
    if 'saved_queries' in st.session_state and st.session_state.saved_queries:
        for i, template in enumerate(reversed(st.session_state.saved_queries[-5:])):  # Show last 5
            with st.expander(f"📝 {template['question']} - {template['timestamp']}"):
                st.code(template['sql'], language="sql")
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("🔄 Load Query", key=f"load_{i}"):
                        st.session_state.current_sql = template['sql']
                        st.session_state.current_question = template['question']
                        st.success(f"✅ Loaded: {template['question']}")
                        st.info("👆 Scroll up to see the loaded query and click 'Execute Query'")
                        
                with col2:
                    if st.button("▶️ Execute Now", key=f"exec_{i}"):
                        st.session_state.current_sql = template['sql']
                        st.session_state.current_question = template['question']
                        # Execute immediately
                        execute_enterprise_query(template['sql'])
                        
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{i}"):
                        # Remove from saved queries
                        actual_index = len(st.session_state.saved_queries) - 1 - i
                        st.session_state.saved_queries.pop(actual_index)
                        st.rerun()
    else:
        st.info("💡 No saved queries yet. Execute a query and click 'Save Query' to see templates here!")

def test_enterprise_connection():
    """Test connection to enterprise AWS infrastructure"""
    try:
        # Test Athena connection
        athena_client = boto3.client('athena', region_name=ENTERPRISE_CONFIG['aws_region'])
        
        # List databases
        response = athena_client.list_databases(CatalogName='AwsDataCatalog')
        databases = [db['Name'] for db in response['DatabaseList']]
        
        if ENTERPRISE_CONFIG['glue_database'] in databases:
            st.success(f"✅ Connected to Glue Database: {ENTERPRISE_CONFIG['glue_database']}")
            
            # Test table access
            glue_client = boto3.client('glue', region_name=ENTERPRISE_CONFIG['aws_region'])
            tables_response = glue_client.get_tables(DatabaseName=ENTERPRISE_CONFIG['glue_database'])
            tables = [table['Name'] for table in tables_response['TableList']]
            
            st.success(f"✅ Found {len(tables)} tables in database")
            with st.expander("📋 Available Tables"):
                for table in tables[:10]:  # Show first 10 tables
                    st.write(f"• {table}")
                if len(tables) > 10:
                    st.write(f"... and {len(tables) - 10} more tables")
        else:
            st.error(f"❌ Database '{ENTERPRISE_CONFIG['glue_database']}' not found")
            st.write("Available databases:", databases)
            
    except Exception as e:
        st.error(f"❌ Connection failed: {str(e)}")
        st.write("Please check your AWS credentials and permissions.")

def show_available_tables():
    """Show available tables in the enterprise database"""
    try:
        glue_client = boto3.client('glue', region_name=ENTERPRISE_CONFIG['aws_region'])
        response = glue_client.get_tables(DatabaseName=ENTERPRISE_CONFIG['glue_database'])
        
        st.subheader("📊 Available Tables")
        
        if not response['TableList']:
            st.warning("No tables found in the database. Please check your Glue catalog setup.")
            return []
        
        table_names = []
        for table in response['TableList']:
            table_names.append(table['Name'])
            with st.expander(f"📋 {table['Name']}"):
                st.write(f"**Location:** {table['StorageDescriptor'].get('Location', 'N/A')}")
                st.write("**Columns:**")
                for col in table['StorageDescriptor']['Columns']:
                    st.write(f"• {col['Name']} ({col['Type']})")
        
        # Store available tables in session state
        st.session_state.available_tables = table_names
        return table_names
                    
    except Exception as e:
        st.error(f"Error fetching tables: {str(e)}")
        return []

def get_available_tables():
    """Get list of available tables"""
    try:
        glue_client = boto3.client('glue', region_name=ENTERPRISE_CONFIG['aws_region'])
        response = glue_client.get_tables(DatabaseName=ENTERPRISE_CONFIG['glue_database'])
        return [table['Name'] for table in response['TableList']]
    except:
        return []

def generate_enterprise_sql(question):
    """Generate SQL for enterprise database using actual table names"""
    # Get available tables
    available_tables = get_available_tables()
    
    if not available_tables:
        return f"""-- Error: No tables found in database
-- Please check your Glue catalog setup
-- Database: {ENTERPRISE_CONFIG['glue_database']}
SELECT 'No tables available' as message;"""
    
    # Properly quote database name with hyphens
    database_name = f'"{ENTERPRISE_CONFIG["glue_database"]}"'
    
    # Use the first available table as default
    table_name = available_tables[0]
    
    # Enhanced SQL generation based on actual table structure
    question_lower = question.lower()
    
    if "region" in question_lower and ("total" in question_lower or "sum" in question_lower):
        return f"""-- Generated from: "{question}"
-- Using table: {table_name}
SELECT 
    risk_level,
    COUNT(*) as contract_count,
    AVG(performance_score) as avg_performance,
    AVG(sla_score) as avg_sla
FROM {database_name}.{table_name}
WHERE risk_level IS NOT NULL
GROUP BY risk_level
ORDER BY contract_count DESC;"""
    
    elif "top" in question_lower and ("10" in question_lower or "ten" in question_lower):
        return f"""-- Generated from: "{question}"
-- Using table: {table_name}
SELECT 
    contract_id,
    risk_level,
    compliance_status,
    performance_score,
    sla_score,
    kpi_met
FROM {database_name}.{table_name}
ORDER BY performance_score DESC
LIMIT 10;"""
    
    elif "status" in question_lower or "pie chart" in question_lower or "distribution" in question_lower:
        return f"""-- Generated from: "{question}"
-- Using table: {table_name}
SELECT 
    compliance_status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM {database_name}.{table_name}
WHERE compliance_status IS NOT NULL
GROUP BY compliance_status
ORDER BY count DESC;"""
    
    elif "performance" in question_lower or "score" in question_lower:
        return f"""-- Generated from: "{question}"
-- Using table: {table_name}
SELECT 
    risk_level,
    AVG(performance_score) as avg_performance_score,
    AVG(sla_score) as avg_sla_score,
    COUNT(*) as contract_count
FROM {database_name}.{table_name}
GROUP BY risk_level
ORDER BY avg_performance_score DESC;"""
    
    elif "kpi" in question_lower or "met" in question_lower:
        return f"""-- Generated from: "{question}"
-- Using table: {table_name}
SELECT 
    kpi_met,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage,
    AVG(performance_score) as avg_performance
FROM {database_name}.{table_name}
GROUP BY kpi_met
ORDER BY count DESC;"""
    
    elif "high" in question_lower and "risk" in question_lower:
        return f"""-- Generated from: "{question}"
-- Using table: {table_name}
SELECT 
    contract_id,
    risk_level,
    compliance_status,
    performance_score,
    sla_score
FROM {database_name}.{table_name}
WHERE risk_level = 'High'
ORDER BY performance_score DESC;"""
    
    else:
        # Generic query - show all data from the first table
        return f"""-- Generated from: "{question}"
-- Available tables: {', '.join(available_tables)}
-- Using table: {table_name}
SELECT *
FROM {database_name}.{table_name}
LIMIT 100;"""

def explain_query(question, sql):
    """Provide business-friendly explanation of the SQL query"""
    explanation = f"""
    **Business Question:** {question}
    
    **What this query does:**
    • Accesses the enterprise contracts database
    • Retrieves relevant contract information
    • Applies appropriate filters and grouping
    • Orders results for business insights
    
    **Data Source:** {ENTERPRISE_CONFIG['glue_database']} database
    **Expected Result:** Formatted business data ready for analysis
    """
    st.info(explanation)

def execute_enterprise_query(sql_query):
    """Execute query on enterprise Athena infrastructure"""
    try:
        athena_client = boto3.client('athena', region_name=ENTERPRISE_CONFIG['aws_region'])
        
        # Start query execution
        response = athena_client.start_query_execution(
            QueryString=sql_query,
            WorkGroup=ENTERPRISE_CONFIG['athena_workgroup'],
            ResultConfiguration={
                'OutputLocation': f"s3://{ENTERPRISE_CONFIG['s3_results_bucket']}/"
            }
        )
        
        query_execution_id = response['QueryExecutionId']
        st.success(f"✅ Query submitted! Execution ID: {query_execution_id}")
        
        # Monitor query execution
        with st.spinner("⏳ Executing query..."):
            status = monitor_query_execution(athena_client, query_execution_id)
        
        if status == 'SUCCEEDED':
            # Get and display results
            display_query_results(athena_client, query_execution_id)
            
            # QuickSight export option
            st.subheader("📊 Export to QuickSight")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Direct HTML link like the Open QS Console button
                quicksight_datasets_url = "https://us-east-1.quicksight.aws.amazon.com/sn/start/data-sets"
                st.markdown(f"""
                <a href="{quicksight_datasets_url}" target="_blank" style="
                    display: inline-block;
                    padding: 0.5rem 1rem;
                    background-color: #232F3E;
                    color: white;
                    text-decoration: none;
                    border-radius: 0.25rem;
                    font-weight: bold;
                ">📈 Create QuickSight Dataset</a>
                """, unsafe_allow_html=True)
            
            with col2:
                # Fixed QuickSight URL for enterprise
                quicksight_url = f"https://us-east-1.quicksight.aws.amazon.com/sn/start"
                st.markdown(f"""
                <a href="{quicksight_url}" target="_blank" style="
                    display: inline-block;
                    padding: 0.5rem 1rem;
                    background-color: #ff6b35;
                    color: white;
                    text-decoration: none;
                    border-radius: 0.25rem;
                    font-weight: bold;
                ">🎯 Open QuickSight Console</a>
                """, unsafe_allow_html=True)
            
            # Show helpful dataset creation info
            s3_location = f"s3://{ENTERPRISE_CONFIG['s3_results_bucket']}/{st.session_state.query_execution_id}.csv"
            st.info(f"""
            **💡 In QuickSight Datasets page:**
            1. Click "New dataset" 
            2. Choose "Athena" as data source
            3. Database: `{ENTERPRISE_CONFIG['glue_database']}`
            4. Query results location: `{s3_location}`
            """)
        
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
        # Get query results
        results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
        
        # Convert to DataFrame
        columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        rows = []
        
        for row in results['ResultSet']['Rows'][1:]:  # Skip header row
            row_data = [field.get('VarCharValue', '') for field in row['Data']]
            rows.append(row_data)
        
        if rows:
            df = pd.DataFrame(rows, columns=columns)
            
            st.subheader("📊 Query Results")
            st.dataframe(df, use_container_width=True)
            
            # Summary statistics
            st.subheader("📈 Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Execution Time", "< 30s")
            
            # Store results for QuickSight export
            st.session_state.query_results = df
            st.session_state.query_execution_id = query_execution_id
            
        else:
            st.info("Query executed successfully but returned no results.")
            
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")

# Removed create_quicksight_dataset function - now using direct HTML links

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
    
    # Keep the current query displayed after saving
    # Don't reset the session state

if __name__ == "__main__":
    main()
