# Athena Query Generator - Streamlit Application

A natural language to SQL query generator for Amazon Athena with QuickSight integration, enabling business users to create data insights through conversational interface.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [AWS Services Configuration](#aws-services-configuration)
- [Application Deployment](#application-deployment)
- [QuickSight Integration](#quicksight-integration)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)

## 🎯 Project Overview

This application allows business users to:
- Ask questions in natural language (e.g., "Show me Q1 sales by region")
- Generate optimized SQL queries for Amazon Athena
- Execute queries and view formatted results
- Export data directly to Amazon QuickSight for visualization
- Create dashboards, data stories, and executive summaries

## 🔧 Prerequisites

### Required AWS Services
- **Amazon Athena** - Query execution engine
- **AWS Glue** - Data catalog and metadata management
- **Amazon S3** - Data storage and query results
- **Amazon QuickSight** - Business intelligence and visualization
- **AWS IAM** - Identity and access management
- **AWS SSO/Identity Center** (optional) - Single sign-on

### Development Environment
- Python 3.8+
- AWS CLI configured with appropriate permissions
- Docker (for containerized deployment)
- Git for version control

### Required Python Packages
```bash
streamlit>=1.28.0
boto3>=1.26.0
pandas>=1.5.0
openai>=1.0.0  # or your preferred NLP service
sqlparse>=0.4.0
plotly>=5.15.0
```

## 🚀 Quick Start

### 1. Initialize Repository (First Time Setup)
```bash
# You're already in the project directory
cd athena-query-generator

# Initialize git repository
git init
git add .
git commit -m "Initial commit: User stories, documentation, and basic app"

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure AWS Credentials
```bash
aws configure
# OR use AWS SSO
aws sso login --profile your-profile
```

### 3. Configure Environment Variables
```bash
# Copy the environment template
cp .env.template .env

# Edit .env file with your AWS configuration
# AWS_REGION=us-east-1
# ATHENA_WORKGROUP=your-workgroup
# S3_RESULTS_BUCKET=your-athena-results-bucket
# QUICKSIGHT_ACCOUNT_ID=your-aws-account-id
# OPENAI_API_KEY=your-openai-key
```

### 4. Run Application
```bash
streamlit run app.py
```

### 5. Optional: Create GitHub Repository
```bash
# Create a new repository on GitHub named 'athena-query-generator'
# Then connect your local repository:

git remote add origin https://github.com/YOUR-USERNAME/athena-query-generator.git
git branch -M main
git push -u origin main
```

## 🔨 Detailed Setup

### Step 1: AWS Infrastructure Setup

#### 1.1 Create S3 Buckets
```bash
# Create buckets for different purposes
aws s3 mb s3://your-athena-results-bucket
aws s3 mb s3://your-quicksight-data-bucket
aws s3 mb s3://your-raw-data-bucket
```

#### 1.2 Setup AWS Glue Data Catalog
```bash
# Create database in Glue catalog
aws glue create-database --database-input Name=business_analytics
```

#### 1.3 Configure Athena Workgroup
```bash
# Create Athena workgroup with result location
aws athena create-work-group \
  --name athena-query-generator \
  --configuration ResultConfigurationUpdates='{
    "OutputLocation": "s3://your-athena-results-bucket/"
  }'
```

### Step 2: IAM Permissions Setup

#### 2.1 Create IAM Role for Application
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "athena:*",
        "glue:GetDatabase",
        "glue:GetTable",
        "glue:GetTables",
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "quicksight:CreateDataSet",
        "quicksight:CreateAnalysis"
      ],
      "Resource": "*"
    }
  ]
}
```

#### 2.2 Create User Roles with Data Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "athena:GetQueryExecution",
        "athena:GetQueryResults",
        "athena:StartQueryExecution"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "athena:workgroup": "athena-query-generator"
        }
      }
    }
  ]
}
```

### Step 3: Application Configuration

#### 3.1 Create Configuration File
```yaml
# config.yaml
aws:
  region: us-east-1
  athena_workgroup: athena-query-generator
  s3_results_bucket: your-athena-results-bucket
  quicksight_account_id: your-aws-account-id

database:
  glue_catalog: business_analytics
  tables:
    - sales_transactions
    - customer_data
    - inventory_levels

nlp:
  provider: openai  # or aws_comprehend
  model: gpt-3.5-turbo
  max_tokens: 1000

security:
  enable_sso: true
  session_timeout: 3600
  audit_logging: true
```

#### 3.2 Environment Variables
```bash
# .env file
AWS_REGION=us-east-1
ATHENA_WORKGROUP=athena-query-generator
S3_RESULTS_BUCKET=your-athena-results-bucket
QUICKSIGHT_ACCOUNT_ID=your-aws-account-id
OPENAI_API_KEY=your-openai-key
```

## ☁️ AWS Services Configuration

### Amazon Athena Setup

#### 1. Create Workgroup
```python
import boto3

athena_client = boto3.client('athena')

athena_client.create_work_group(
    Name='athena-query-generator',
    Configuration={
        'ResultConfigurationUpdates': {
            'OutputLocation': 's3://your-athena-results-bucket/',
            'EncryptionConfiguration': {
                'EncryptionOption': 'SSE_S3'
            }
        },
        'EnforceWorkGroupConfiguration': True,
        'PublishCloudWatchMetrics': True
    }
)
```

#### 2. Setup Query Cost Controls
```python
athena_client.update_work_group(
    WorkGroup='athena-query-generator',
    ConfigurationUpdates={
        'BytesScannedCutoffPerQuery': 1000000000,  # 1GB limit
        'RequesterPaysEnabled': False
    }
)
```

### AWS Glue Configuration

#### 1. Create Tables from S3 Data
```python
import boto3

glue_client = boto3.client('glue')

# Example: Create sales table
glue_client.create_table(
    DatabaseName='business_analytics',
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
            'Location': 's3://your-raw-data-bucket/sales/',
            'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
            'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
            'SerdeInfo': {
                'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
                'Parameters': {'field.delim': ','}
            }
        },
        'PartitionKeys': [
            {'Name': 'year', 'Type': 'string'},
            {'Name': 'month', 'Type': 'string'}
        ]
    }
)
```

## 🚀 Application Deployment

### Option 1: Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py --server.port 8501
```

### Option 2: Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

```bash
# Build and run
docker build -t athena-query-generator .
docker run -p 8501:8501 athena-query-generator
```

### Option 3: AWS ECS Deployment
```yaml
# docker-compose.yml for ECS
version: '3.8'
services:
  athena-query-generator:
    image: your-account.dkr.ecr.region.amazonaws.com/athena-query-generator:latest
    ports:
      - "8501:8501"
    environment:
      - AWS_REGION=us-east-1
      - ATHENA_WORKGROUP=athena-query-generator
    task_role_arn: arn:aws:iam::account:role/ECSTaskRole
```

### Option 4: AWS App Runner Deployment
```yaml
# apprunner.yaml
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  runtime-version: 3.9
  command: streamlit run app.py --server.address 0.0.0.0 --server.port 8080
  network:
    port: 8080
    env: PORT
```

## 📊 QuickSight Integration

### Step 1: Setup QuickSight Data Source
```python
import boto3

quicksight = boto3.client('quicksight')

# Create Athena data source
quicksight.create_data_source(
    AwsAccountId='your-account-id',
    DataSourceId='athena-data-source',
    Name='Athena Business Analytics',
    Type='ATHENA',
    DataSourceParameters={
        'AthenaParameters': {
            'WorkGroup': 'athena-query-generator'
        }
    }
)
```

### Step 2: Create QuickSight Dataset from Query Results
```python
def create_quicksight_dataset(query_results_s3_path, dataset_name):
    quicksight.create_data_set(
        AwsAccountId='your-account-id',
        DataSetId=f'dataset-{dataset_name}',
        Name=dataset_name,
        PhysicalTableMap={
            'table1': {
                'S3Source': {
                    'DataSourceArn': 'arn:aws:quicksight:region:account:datasource/athena-data-source',
                    'InputColumns': [
                        {'Name': 'column1', 'Type': 'STRING'},
                        {'Name': 'column2', 'Type': 'DECIMAL'}
                    ]
                }
            }
        }
    )
```

### Step 3: Automated Dashboard Creation
```python
def create_dashboard_from_dataset(dataset_id, dashboard_name):
    # Create analysis first
    analysis_response = quicksight.create_analysis(
        AwsAccountId='your-account-id',
        AnalysisId=f'analysis-{dashboard_name}',
        Name=f'Analysis for {dashboard_name}',
        Definition={
            'DataSetIdentifierDeclarations': [
                {
                    'DataSetArn': f'arn:aws:quicksight:region:account:dataset/{dataset_id}',
                    'Identifier': 'dataset1'
                }
            ]
        }
    )
    
    # Create dashboard from analysis
    quicksight.create_dashboard(
        AwsAccountId='your-account-id',
        DashboardId=f'dashboard-{dashboard_name}',
        Name=dashboard_name,
        SourceEntity={
            'SourceTemplate': {
                'DataSetReferences': [
                    {
                        'DataSetArn': f'arn:aws:quicksight:region:account:dataset/{dataset_id}',
                        'DataSetPlaceholder': 'dataset1'
                    }
                ],
                'Arn': 'arn:aws:quicksight:region:account:template/business-template'
            }
        }
    )
```

## 🔄 Development Workflow

### 1. Project Structure
```
athena-query-generator/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env.template                   # Environment variables template
├── .env                           # Your environment configuration (create from template)
├── .gitignore                     # Git ignore rules
├── config.yaml                     # Application configuration
├── Dockerfile                      # Container configuration
├── README.md                       # This file
├── business_user_workflow.md       # Mermaid diagrams for user workflows
├── aws_architecture_diagram.md     # AWS services architecture diagrams
├── 01_user_stories/               # User stories and documentation
│   ├── user_stories_plan.md       # Development plan with checkboxes
│   ├── 01_user_personas.md
│   ├── 02_user_journeys.md
│   ├── 03_database_schema_requirements.md
│   ├── 04_authentication_stories.md
│   ├── 05_chat_interface_stories.md
│   ├── 06_query_generation_stories.md
│   ├── 07_query_execution_stories.md
│   ├── 08_error_handling_stories.md
│   ├── 09_acceptance_criteria.md
│   ├── 10_story_prioritization.md
│   └── 11_final_story_collection.md
├── src/                           # Source code (to be created)
│   ├── nlp/                       # Natural language processing
│   ├── query_generator/           # SQL generation logic
│   ├── athena_client/            # Athena integration
│   ├── quicksight_client/        # QuickSight integration
│   └── auth/                     # Authentication logic
├── tests/                        # Unit and integration tests (to be created)
├── docs/                         # Additional documentation
└── deployment/                   # Deployment configurations (to be created)
    ├── cloudformation/
    ├── terraform/
    └── kubernetes/
```

### 2. Development Process
1. **Setup Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run Tests**
   ```bash
   pytest tests/
   ```

3. **Local Development**
   ```bash
   streamlit run app.py
   ```

4. **Build and Test Docker Image**
   ```bash
   docker build -t athena-query-generator .
   docker run -p 8501:8501 athena-query-generator
   ```

### 3. CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Build and push Docker image
        run: |
          docker build -t athena-query-generator .
          docker tag athena-query-generator:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/athena-query-generator:latest
          docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/athena-query-generator:latest
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service --cluster production --service athena-query-generator --force-new-deployment
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Athena Permission Errors
```bash
# Check IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::account:role/your-role \
  --action-names athena:StartQueryExecution \
  --resource-arns "*"
```

#### 2. S3 Access Issues
```bash
# Test S3 access
aws s3 ls s3://your-athena-results-bucket/
```

#### 3. QuickSight Integration Issues
```bash
# Check QuickSight permissions
aws quicksight describe-user \
  --aws-account-id your-account-id \
  --namespace default \
  --user-name your-username
```

### Performance Optimization

#### 1. Athena Query Optimization
- Use partition pruning in WHERE clauses
- Limit data scanned with appropriate filters
- Use columnar formats (Parquet, ORC)
- Implement query result caching

#### 2. Application Performance
- Implement query result caching in Streamlit
- Use connection pooling for AWS services
- Optimize Docker image size
- Enable CloudFront for static assets

### Monitoring and Logging

#### 1. CloudWatch Metrics
```python
import boto3

cloudwatch = boto3.client('cloudwatch')

# Custom metrics for application
cloudwatch.put_metric_data(
    Namespace='AthenaQueryGenerator',
    MetricData=[
        {
            'MetricName': 'QueriesExecuted',
            'Value': 1,
            'Unit': 'Count'
        }
    ]
)
```

#### 2. Application Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

## 📞 Support and Resources

- **User Stories Documentation**: See `01_user_stories/` directory
- **AWS Documentation**: [Amazon Athena](https://docs.aws.amazon.com/athena/), [Amazon QuickSight](https://docs.aws.amazon.com/quicksight/)
- **Streamlit Documentation**: [streamlit.io](https://streamlit.io/)
- **Issue Tracking**: Use GitHub Issues for bug reports and feature requests

## 🎯 Next Steps

1. **Review User Stories**: Start with the comprehensive user stories in `01_user_stories/`
2. **Setup AWS Infrastructure**: Follow the AWS services configuration section
3. **Develop MVP**: Begin with Phase 1 features from the prioritization document
4. **Test Integration**: Validate Athena and QuickSight connections
5. **Deploy and Iterate**: Use the CI/CD pipeline for continuous deployment

---

**Ready to transform your data analysis workflow? Start with the MVP features and iterate based on user feedback!**
