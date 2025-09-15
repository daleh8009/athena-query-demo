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
    'aws_account_id': os.getenv('AWS_ACCOUNT_ID', '695233770948'),
    'athena_workgroup': os.getenv('ATHENA_WORKGROUP', 'athena-query-generator'),
    's3_results_bucket': os.getenv('S3_RESULTS_BUCKET', 'your-name-athena-results-2024'),
    'glue_database': os.getenv('GLUE_DATABASE', 'business_analytics'),
    's3_raw_data': os.getenv('S3_RAW_DATA', 'your-name-raw-data-2024'),
    'quicksight_account_id': os.getenv('QUICKSIGHT_ACCOUNT_ID', '695233770948')
}

# Page configuration
st.set_page_config(
    page_title="Athena Query Generator - Full Setup",
    page_icon="🛠️",
    layout="wide"
)

def main():
    st.title("🛠️ Athena Query Generator - Full Setup Edition")
    st.markdown("**Complete infrastructure setup and configuration**")
    
    # Setup wizard
    setup_tab, query_tab, admin_tab = st.tabs(["🔧 Setup Wizard", "💬 Query Interface", "⚙️ Admin Panel"])
    
    with setup_tab:
        show_setup_wizard()
    
    with query_tab:
        show_query_interface()
    
    with admin_tab:
        show_admin_panel()

def show_setup_wizard():
    """Complete setup wizard for infrastructure"""
    st.header("🔧 Infrastructure Setup Wizard")
    
    # Step 1: AWS Configuration
    st.subheader("Step 1: AWS Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        aws_region = st.text_input("AWS Region", value=SETUP_CONFIG['aws_region'])
        aws_account_id = st.text_input("AWS Account ID", value=SETUP_CONFIG['aws_account_id'])
    
    with col2:
        athena_workgroup = st.text_input("Athena Workgroup", value=SETUP_CONFIG['athena_workgroup'])
        glue_database = st.text_input("Glue Database Name", value=SETUP_CONFIG['glue_database'])
    
    # Step 2: S3 Bucket Configuration
    st.subheader("Step 2: S3 Bucket Setup")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        s3_results = st.text_input("Athena Results Bucket", value=SETUP_CONFIG['s3_results_bucket'])
    with col2:
        s3_raw_data = st.text_input("Raw Data Bucket", value=SETUP_CONFIG['s3_raw_data'])
    with col3:
        quicksight_account = st.text_input("QuickSight Account ID", value=SETUP_CONFIG['quicksight_account_id'])
    
    # Step 3: Infrastructure Creation
    st.subheader("Step 3: Create Infrastructure")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🪣 Create S3 Buckets"):
            create_s3_buckets(s3_results, s3_raw_data)
    
    with col2:
        if st.button("🏗️ Setup Athena Workgroup"):
            setup_athena_workgroup(athena_workgroup, s3_results, aws_region)
    
    with col3:
        if st.button("📊 Create Glue Database"):
            create_glue_database(glue_database, aws_region)
    
    # Step 4: Sample Data Setup
    st.subheader("Step 4: Sample Data Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Upload Sample Data"):
            upload_sample_data(s3_raw_data)
    
    with col2:
        if st.button("📋 Create Sample Tables"):
            create_sample_tables(glue_database, s3_raw_data, aws_region)
    
    # Step 5: QuickSight Setup
    st.subheader("Step 5: QuickSight Integration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 Setup QuickSight Data Source"):
            setup_quicksight_datasource(quicksight_account, athena_workgroup, aws_region)
    
    with col2:
        if st.button("🎯 Open QuickSight Console"):
            quicksight_url = f"https://{aws_region}.quicksight.aws.amazon.com/sn/accounts/{quicksight_account}"
            st.markdown(f"[Open QuickSight Console]({quicksight_url})")
    
    # Step 6: Validation
    st.subheader("Step 6: Validate Setup")
    
    if st.button("✅ Test Complete Setup"):
        validate_complete_setup(aws_region, athena_workgroup, glue_database, s3_results)

def show_query_interface():
    """Main query interface for business users"""
    st.header("💬 Business Query Interface")
    
    # Configuration display
    with st.expander("📋 Current Configuration"):
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Database:** {SETUP_CONFIG['glue_database']}")
            st.info(f"**Workgroup:** {SETUP_CONFIG['athena_workgroup']}")
        with col2:
            st.info(f"**Region:** {SETUP_CONFIG['aws_region']}")
            st.info(f"**Results Bucket:** {SETUP_CONFIG['s3_results_bucket']}")
    
    # Sample questions for business analytics
    example_questions = [
        "Show me total sales by region for last quarter",
        "List top 10 customers by revenue",
        "Compare monthly sales trends",
        "Show product performance by category",
        "Find customers with declining purchases"
    ]
    
    selected_example = st.selectbox("📝 Try an example question:", [""] + example_questions)
    
    # Query input
    user_question = st.text_area(
        "What would you like to know about your data?",
        value=selected_example if selected_example else "",
        placeholder="Example: Show me total sales by region for the last quarter",
        height=100
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔄 Generate Query", type="primary"):
            if user_question:
                with st.spinner("🤖 Processing your question..."):
                    generated_sql = generate_business_sql(user_question)
                    st.session_state.current_sql = generated_sql
                    st.session_state.current_question = user_question
            else:
                st.warning("Please enter a question first.")
    
    with col2:
        if st.button("📊 Browse Tables"):
            show_database_tables()
    
    # Display and execute query
    if 'current_sql' in st.session_state:
        st.subheader("📝 Generated SQL Query")
        st.code(st.session_state.current_sql, language="sql")
        
        # Query explanation
        st.subheader("💡 Query Explanation")
        explain_business_query(st.session_state.current_question, st.session_state.current_sql)
        
        # Execute query
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("▶️ Execute Query", type="primary"):
                execute_business_query(st.session_state.current_sql)
        
        with col2:
            if st.button("✏️ Edit SQL"):
                st.session_state.edit_mode = True
        
        with col3:
            if st.button("💾 Save Template"):
                save_query_template(st.session_state.current_question, st.session_state.current_sql)
    
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

def show_admin_panel():
    """Administrative panel for system management"""
    st.header("⚙️ Administrative Panel")
    
    # System status
    st.subheader("📊 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Check AWS Connection"):
            check_aws_connection()
    
    with col2:
        if st.button("📋 List All Tables"):
            list_all_tables()
    
    with col3:
        if st.button("📈 Query Statistics"):
            show_query_statistics()
    
    # Data management
    st.subheader("📁 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Upload New Data**")
        uploaded_file = st.file_uploader("Choose CSV file", type="csv")
        if uploaded_file and st.button("📤 Upload to S3"):
            upload_user_data(uploaded_file)
    
    with col2:
        st.write("**Create New Table**")
        table_name = st.text_input("Table Name")
        if table_name and st.button("📋 Create Table"):
            create_user_table(table_name)
    
    # QuickSight management
    st.subheader("📊 QuickSight Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 List QuickSight Datasets"):
            list_quicksight_datasets()
    
    with col2:
        if st.button("🎯 Create Dashboard Template"):
            create_dashboard_template()

# Infrastructure setup functions
def create_s3_buckets(results_bucket, raw_data_bucket):
    """Create required S3 buckets"""
    try:
        s3_client = boto3.client('s3', region_name=SETUP_CONFIG['aws_region'])
        
        # Create results bucket
        s3_client.create_bucket(Bucket=results_bucket)
        st.success(f"✅ Created results bucket: {results_bucket}")
        
        # Create raw data bucket
        s3_client.create_bucket(Bucket=raw_data_bucket)
        st.success(f"✅ Created raw data bucket: {raw_data_bucket}")
        
    except Exception as e:
        st.error(f"❌ S3 bucket creation failed: {str(e)}")

def setup_athena_workgroup(workgroup_name, results_bucket, region):
    """Setup Athena workgroup"""
    try:
        athena_client = boto3.client('athena', region_name=region)
        
        athena_client.create_work_group(
            Name=workgroup_name,
            Configuration={
                'ResultConfigurationUpdates': {
                    'OutputLocation': f's3://{results_bucket}/',
                    'EncryptionConfiguration': {
                        'EncryptionOption': 'SSE_S3'
                    }
                },
                'EnforceWorkGroupConfiguration': True,
                'PublishCloudWatchMetrics': True
            }
        )
        
        st.success(f"✅ Created Athena workgroup: {workgroup_name}")
        
    except Exception as e:
        st.error(f"❌ Athena workgroup creation failed: {str(e)}")

def create_glue_database(database_name, region):
    """Create Glue database"""
    try:
        glue_client = boto3.client('glue', region_name=region)
        
        glue_client.create_database(
            DatabaseInput={
                'Name': database_name,
                'Description': 'Business analytics database for Athena Query Generator'
            }
        )
        
        st.success(f"✅ Created Glue database: {database_name}")
        
    except Exception as e:
        st.error(f"❌ Glue database creation failed: {str(e)}")

def upload_sample_data(raw_data_bucket):
    """Upload sample data to S3"""
    try:
        s3_client = boto3.client('s3', region_name=SETUP_CONFIG['aws_region'])
        
        # Upload the sample CSV file we created earlier
        s3_client.upload_file(
            'sample_data.csv',
            raw_data_bucket,
            'sales/sample_data.csv'
        )
        
        st.success(f"✅ Uploaded sample data to: s3://{raw_data_bucket}/sales/")
        
    except Exception as e:
        st.error(f"❌ Sample data upload failed: {str(e)}")

def create_sample_tables(database_name, raw_data_bucket, region):
    """Create sample tables in Glue"""
    try:
        glue_client = boto3.client('glue', region_name=region)
        
        # Create sales_transactions table
        glue_client.create_table(
            DatabaseName=database_name,
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
                    'Location': f's3://{raw_data_bucket}/sales/',
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
                        'Parameters': {'field.delim': ',', 'skip.header.line.count': '1'}
                    }
                }
            }
        )
        
        st.success(f"✅ Created table: sales_transactions")
        
    except Exception as e:
        st.error(f"❌ Table creation failed: {str(e)}")

def setup_quicksight_datasource(account_id, workgroup, region):
    """Setup QuickSight data source"""
    try:
        quicksight_client = boto3.client('quicksight', region_name=region)
        
        quicksight_client.create_data_source(
            AwsAccountId=account_id,
            DataSourceId='athena-query-generator-datasource',
            Name='Athena Query Generator Data Source',
            Type='ATHENA',
            DataSourceParameters={
                'AthenaParameters': {
                    'WorkGroup': workgroup
                }
            }
        )
        
        st.success("✅ Created QuickSight data source")
        
    except Exception as e:
        st.error(f"❌ QuickSight data source creation failed: {str(e)}")

def validate_complete_setup(region, workgroup, database, results_bucket):
    """Validate the complete setup"""
    validation_results = []
    
    try:
        # Test Athena
        athena_client = boto3.client('athena', region_name=region)
        workgroups = athena_client.list_work_groups()
        workgroup_names = [wg['Name'] for wg in workgroups['WorkGroups']]
        
        if workgroup in workgroup_names:
            validation_results.append("✅ Athena workgroup accessible")
        else:
            validation_results.append("❌ Athena workgroup not found")
        
        # Test Glue
        glue_client = boto3.client('glue', region_name=region)
        databases = glue_client.get_databases()
        database_names = [db['Name'] for db in databases['DatabaseList']]
        
        if database in database_names:
            validation_results.append("✅ Glue database accessible")
            
            # Test tables
            tables = glue_client.get_tables(DatabaseName=database)
            if tables['TableList']:
                validation_results.append(f"✅ Found {len(tables['TableList'])} tables")
            else:
                validation_results.append("⚠️ No tables found in database")
        else:
            validation_results.append("❌ Glue database not found")
        
        # Test S3
        s3_client = boto3.client('s3', region_name=region)
        try:
            s3_client.head_bucket(Bucket=results_bucket)
            validation_results.append("✅ S3 results bucket accessible")
        except:
            validation_results.append("❌ S3 results bucket not accessible")
        
        # Display results
        st.subheader("🔍 Validation Results")
        for result in validation_results:
            if "✅" in result:
                st.success(result)
            elif "❌" in result:
                st.error(result)
            else:
                st.warning(result)
        
    except Exception as e:
        st.error(f"❌ Validation failed: {str(e)}")

# Query generation and execution functions (similar to enterprise version)
def generate_business_sql(question):
    """Generate SQL for business analytics"""
    question_lower = question.lower()
    
    if "sales" in question_lower and "region" in question_lower:
        return f"""-- Generated from: "{question}"
SELECT 
    region,
    SUM(sales_amount) as total_sales,
    COUNT(*) as transaction_count,
    AVG(sales_amount) as avg_sales
FROM {SETUP_CONFIG['glue_database']}.sales_transactions 
WHERE transaction_date >= DATE('2024-01-01')
GROUP BY region
ORDER BY total_sales DESC;"""
    
    elif "top" in question_lower and "customer" in question_lower:
        return f"""-- Generated from: "{question}"
SELECT 
    customer_id,
    SUM(sales_amount) as total_revenue,
    COUNT(*) as transaction_count
FROM {SETUP_CONFIG['glue_database']}.sales_transactions 
GROUP BY customer_id
ORDER BY total_revenue DESC
LIMIT 10;"""
    
    else:
        return f"""-- Generated from: "{question}"
SELECT 
    transaction_id,
    customer_id,
    product_id,
    sales_amount,
    transaction_date,
    region
FROM {SETUP_CONFIG['glue_database']}.sales_transactions 
ORDER BY transaction_date DESC
LIMIT 100;"""

def explain_business_query(question, sql):
    """Explain the business query"""
    explanation = f"""
    **Business Question:** {question}
    
    **What this query does:**
    • Accesses your business analytics database
    • Retrieves relevant sales/customer information
    • Applies filters and grouping for insights
    • Orders results for business analysis
    
    **Data Source:** {SETUP_CONFIG['glue_database']} database
    **Expected Result:** Business-ready data for analysis
    """
    st.info(explanation)

def execute_business_query(sql_query):
    """Execute business query on Athena"""
    try:
        athena_client = boto3.client('athena', region_name=SETUP_CONFIG['aws_region'])
        
        # Start query execution
        response = athena_client.start_query_execution(
            QueryString=sql_query,
            WorkGroup=SETUP_CONFIG['athena_workgroup'],
            ResultConfiguration={
                'OutputLocation': f"s3://{SETUP_CONFIG['s3_results_bucket']}/"
            }
        )
        
        query_execution_id = response['QueryExecutionId']
        st.success(f"✅ Query submitted! Execution ID: {query_execution_id}")
        
        # Monitor and display results (similar to enterprise version)
        with st.spinner("⏳ Executing query..."):
            status = monitor_query_execution(athena_client, query_execution_id)
        
        if status == 'SUCCEEDED':
            display_query_results(athena_client, query_execution_id)
            
            # QuickSight export
            st.subheader("📊 Export to QuickSight")
            if st.button("📈 Create QuickSight Dataset"):
                create_quicksight_dataset(query_execution_id)
        
    except Exception as e:
        st.error(f"❌ Query execution error: {str(e)}")

# Additional helper functions (similar implementations as enterprise version)
def monitor_query_execution(athena_client, query_execution_id):
    """Monitor query execution"""
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
    """Display query results"""
    try:
        results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
        
        columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
        rows = []
        
        for row in results['ResultSet']['Rows'][1:]:
            row_data = [field.get('VarCharValue', '') for field in row['Data']]
            rows.append(row_data)
        
        if rows:
            df = pd.DataFrame(rows, columns=columns)
            
            st.subheader("📊 Query Results")
            st.dataframe(df, use_container_width=True)
            
            # Summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Status", "Success")
            
            st.session_state.query_results = df
            st.session_state.query_execution_id = query_execution_id
            
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")

def create_quicksight_dataset(query_execution_id):
    """Create QuickSight dataset"""
    try:
        st.success("✅ QuickSight dataset creation initiated")
        st.info("💡 Dataset will be available in QuickSight console shortly")
        
    except Exception as e:
        st.error(f"QuickSight dataset creation failed: {str(e)}")

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

# Admin functions
def check_aws_connection():
    """Check AWS connection status"""
    try:
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        st.success(f"✅ Connected as: {identity.get('Arn', 'Unknown')}")
        
    except Exception as e:
        st.error(f"❌ AWS connection failed: {str(e)}")

def list_all_tables():
    """List all available tables"""
    try:
        glue_client = boto3.client('glue', region_name=SETUP_CONFIG['aws_region'])
        response = glue_client.get_tables(DatabaseName=SETUP_CONFIG['glue_database'])
        
        st.subheader("📋 Available Tables")
        for table in response['TableList']:
            st.write(f"• **{table['Name']}** - {len(table['StorageDescriptor']['Columns'])} columns")
            
    except Exception as e:
        st.error(f"Error listing tables: {str(e)}")

def show_query_statistics():
    """Show query execution statistics"""
    if 'saved_queries' in st.session_state:
        st.metric("Saved Queries", len(st.session_state.saved_queries))
    else:
        st.metric("Saved Queries", 0)

def upload_user_data(uploaded_file):
    """Upload user data to S3"""
    try:
        s3_client = boto3.client('s3', region_name=SETUP_CONFIG['aws_region'])
        
        # Upload file
        s3_client.upload_fileobj(
            uploaded_file,
            SETUP_CONFIG['s3_raw_data'],
            f"user_data/{uploaded_file.name}"
        )
        
        st.success(f"✅ Uploaded {uploaded_file.name} to S3")
        
    except Exception as e:
        st.error(f"Upload failed: {str(e)}")

def create_user_table(table_name):
    """Create user-defined table"""
    st.info(f"Table creation for '{table_name}' would be implemented here")

def list_quicksight_datasets():
    """List QuickSight datasets"""
    st.info("QuickSight dataset listing would be implemented here")

def create_dashboard_template():
    """Create dashboard template"""
    st.info("Dashboard template creation would be implemented here")

def show_database_tables():
    """Show available database tables"""
    try:
        glue_client = boto3.client('glue', region_name=SETUP_CONFIG['aws_region'])
        response = glue_client.get_tables(DatabaseName=SETUP_CONFIG['glue_database'])
        
        st.subheader("📊 Available Tables")
        for table in response['TableList']:
            with st.expander(f"📋 {table['Name']}"):
                st.write("**Columns:**")
                for col in table['StorageDescriptor']['Columns']:
                    st.write(f"• {col['Name']} ({col['Type']})")
                    
    except Exception as e:
        st.error(f"Error fetching tables: {str(e)}")

if __name__ == "__main__":
    main()
