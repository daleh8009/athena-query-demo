import streamlit as st
import boto3
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Athena Query Generator",
    page_icon="🔍",
    layout="wide"
)

def main():
    st.title("🔍 Athena Query Generator")
    st.markdown("Ask questions in natural language and get SQL queries for Amazon Athena")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # AWS Configuration
        aws_region = st.text_input("AWS Region", value=os.getenv("AWS_REGION", "us-east-1"))
        athena_workgroup = st.text_input("Athena Workgroup", value=os.getenv("ATHENA_WORKGROUP", "primary"))
        s3_results_bucket = st.text_input("S3 Results Bucket", value=os.getenv("S3_RESULTS_BUCKET", ""))
        
        if st.button("Test AWS Connection"):
            test_aws_connection(aws_region)
    
    # Main chat interface
    st.header("💬 Ask Your Question")
    
    # Chat input
    user_question = st.text_area(
        "What would you like to know about your data?",
        placeholder="Example: Show me total sales by region for the last quarter",
        height=100
    )
    
    if st.button("Generate Query", type="primary"):
        if user_question:
            with st.spinner("Processing your question..."):
                # Placeholder for NLP processing
                generated_sql = process_natural_language(user_question)
                
                # Display generated SQL
                st.subheader("Generated SQL Query")
                st.code(generated_sql, language="sql")
                
                # Query explanation
                st.subheader("Query Explanation")
                st.info("This query will retrieve the requested data from your Athena database.")
                
                # Execute query button
                if st.button("Execute Query"):
                    execute_athena_query(generated_sql, aws_region, athena_workgroup, s3_results_bucket)
        else:
            st.warning("Please enter a question first.")
    
    # Display recent queries (placeholder)
    with st.expander("Recent Queries"):
        st.info("Recent query history will appear here.")

def test_aws_connection(region):
    """Test AWS connection and permissions"""
    try:
        # Test Athena connection
        athena_client = boto3.client('athena', region_name=region)
        workgroups = athena_client.list_work_groups()
        
        st.success(f"✅ Successfully connected to AWS Athena in {region}")
        st.json({"workgroups": [wg['Name'] for wg in workgroups['WorkGroups'][:3]]})
        
    except Exception as e:
        st.error(f"❌ AWS connection failed: {str(e)}")

def process_natural_language(question):
    """Convert natural language to SQL (placeholder implementation)"""
    # This is a placeholder - implement actual NLP processing here
    sample_sql = f"""
-- Generated from: "{question}"
SELECT 
    region,
    SUM(sales_amount) as total_sales,
    COUNT(*) as transaction_count
FROM sales_transactions 
WHERE transaction_date >= DATE('2024-01-01')
    AND transaction_date < DATE('2024-04-01')
GROUP BY region
ORDER BY total_sales DESC;
"""
    return sample_sql.strip()

def execute_athena_query(sql_query, region, workgroup, s3_bucket):
    """Execute query on Amazon Athena"""
    try:
        athena_client = boto3.client('athena', region_name=region)
        
        # Start query execution
        response = athena_client.start_query_execution(
            QueryString=sql_query,
            WorkGroup=workgroup,
            ResultConfiguration={
                'OutputLocation': f's3://{s3_bucket}/'
            }
        )
        
        query_execution_id = response['QueryExecutionId']
        st.success(f"✅ Query submitted successfully! Execution ID: {query_execution_id}")
        
        # Placeholder for results display
        st.subheader("Query Results")
        st.info("Query results will appear here once execution is complete.")
        
        # Placeholder for QuickSight export
        if st.button("Export to QuickSight"):
            st.info("Export to QuickSight functionality will be implemented here.")
            
    except Exception as e:
        st.error(f"❌ Query execution failed: {str(e)}")

if __name__ == "__main__":
    main()
