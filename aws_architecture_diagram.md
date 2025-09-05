# AWS Architecture Diagram - Athena Query Generator

## Complete AWS Services Architecture

```mermaid
graph TB
    subgraph "User Access Layer"
        USER[Business Users]
        BROWSER[Web Browser]
    end
    
    subgraph "Application Layer"
        STREAMLIT[Streamlit Application<br/>Chat Interface]
        ALB[Application Load Balancer]
        ECS[Amazon ECS<br/>Container Service]
    end
    
    subgraph "Authentication & Security"
        SSO[AWS SSO/<br/>Identity Center]
        IAM[AWS IAM<br/>Roles & Policies]
        COGNITO[Amazon Cognito<br/>User Pool]
    end
    
    subgraph "Data Processing Services"
        ATHENA[Amazon Athena<br/>Query Engine]
        GLUE[AWS Glue<br/>Data Catalog]
        LAMBDA[AWS Lambda<br/>Query Processing]
    end
    
    subgraph "Storage Services"
        S3_RAW[Amazon S3<br/>Raw Data Bucket]
        S3_PROCESSED[Amazon S3<br/>Processed Data Bucket]
        S3_RESULTS[Amazon S3<br/>Query Results Bucket]
        S3_QS[Amazon S3<br/>QuickSight Data Bucket]
    end
    
    subgraph "Analytics & Visualization"
        QUICKSIGHT[Amazon QuickSight<br/>BI & Analytics]
        SPICE[SPICE Engine<br/>In-Memory Analytics]
    end
    
    subgraph "Monitoring & Logging"
        CLOUDWATCH[Amazon CloudWatch<br/>Monitoring & Logs]
        CLOUDTRAIL[AWS CloudTrail<br/>Audit Logging]
        XRAY[AWS X-Ray<br/>Distributed Tracing]
    end
    
    subgraph "Data Sources"
        RDS[Amazon RDS<br/>Transactional Data]
        REDSHIFT[Amazon Redshift<br/>Data Warehouse]
        EXTERNAL[External Data Sources<br/>APIs, Files]
    end
    
    %% User Flow
    USER --> BROWSER
    BROWSER --> ALB
    ALB --> ECS
    ECS --> STREAMLIT
    
    %% Authentication Flow
    STREAMLIT --> SSO
    SSO --> IAM
    STREAMLIT --> COGNITO
    
    %% Query Processing Flow
    STREAMLIT --> LAMBDA
    LAMBDA --> ATHENA
    ATHENA --> GLUE
    GLUE --> S3_RAW
    GLUE --> S3_PROCESSED
    
    %% Data Sources to Storage
    RDS --> S3_RAW
    REDSHIFT --> S3_RAW
    EXTERNAL --> S3_RAW
    
    %% Query Results Flow
    ATHENA --> S3_RESULTS
    S3_RESULTS --> STREAMLIT
    S3_RESULTS --> S3_QS
    
    %% QuickSight Integration
    S3_QS --> QUICKSIGHT
    QUICKSIGHT --> SPICE
    ATHENA --> QUICKSIGHT
    
    %% Monitoring
    STREAMLIT --> CLOUDWATCH
    ATHENA --> CLOUDWATCH
    LAMBDA --> CLOUDWATCH
    QUICKSIGHT --> CLOUDWATCH
    
    %% Audit Logging
    SSO --> CLOUDTRAIL
    IAM --> CLOUDTRAIL
    ATHENA --> CLOUDTRAIL
    S3_RESULTS --> CLOUDTRAIL
    
    %% Distributed Tracing
    STREAMLIT --> XRAY
    LAMBDA --> XRAY
    
    %% Styling
    style USER fill:#e1f5fe
    style STREAMLIT fill:#f3e5f5
    style ATHENA fill:#fff3e0
    style QUICKSIGHT fill:#e8f5e8
    style S3_RAW fill:#fff8e1
    style S3_PROCESSED fill:#fff8e1
    style S3_RESULTS fill:#fff8e1
    style S3_QS fill:#fff8e1
```

## Data Flow Architecture

```mermaid
flowchart TD
    subgraph "Data Ingestion"
        A[Raw Data Sources] --> B[AWS Glue ETL Jobs]
        B --> C[Amazon S3 Data Lake]
    end
    
    subgraph "Data Catalog & Discovery"
        C --> D[AWS Glue Data Catalog]
        D --> E[Table Schemas & Metadata]
    end
    
    subgraph "Query Processing"
        F[Streamlit App] --> G[Natural Language Processing]
        G --> H[SQL Query Generation]
        H --> I[Amazon Athena]
        I --> D
        I --> C
    end
    
    subgraph "Results & Analytics"
        I --> J[Query Results in S3]
        J --> K[Streamlit Display]
        J --> L[QuickSight Dataset]
        L --> M[QuickSight Analysis]
        M --> N[Dashboards & Reports]
    end
    
    subgraph "Security & Governance"
        O[AWS IAM] --> F
        O --> I
        O --> M
        P[AWS CloudTrail] --> Q[Audit Logs]
        R[Amazon CloudWatch] --> S[Monitoring & Alerts]
    end
    
    style A fill:#ffcdd2
    style C fill:#fff8e1
    style F fill:#f3e5f5
    style I fill:#fff3e0
    style M fill:#e8f5e8
    style O fill:#e0f2f1
```

## Security & Compliance Architecture

```mermaid
graph LR
    subgraph "Identity & Access Management"
        A[AWS SSO/Identity Center] --> B[User Authentication]
        B --> C[AWS IAM Roles]
        C --> D[Fine-grained Permissions]
    end
    
    subgraph "Data Security"
        E[S3 Bucket Encryption] --> F[KMS Key Management]
        G[Athena Query Encryption] --> F
        H[QuickSight Data Encryption] --> F
    end
    
    subgraph "Network Security"
        I[VPC with Private Subnets] --> J[Security Groups]
        J --> K[NACLs]
        K --> L[WAF Protection]
    end
    
    subgraph "Compliance & Auditing"
        M[AWS CloudTrail] --> N[API Call Logging]
        O[AWS Config] --> P[Resource Compliance]
        Q[Amazon GuardDuty] --> R[Threat Detection]
    end
    
    D --> E
    D --> G
    D --> H
    L --> M
    
    style A fill:#e0f2f1
    style E fill:#fff3e0
    style I fill:#e8eaf6
    style M fill:#fce4ec
```

## Cost Optimization Architecture

```mermaid
flowchart TB
    subgraph "Cost Management"
        A[AWS Cost Explorer] --> B[Usage Analytics]
        C[AWS Budgets] --> D[Cost Alerts]
        E[Athena Query Optimization] --> F[Partition Pruning]
        G[S3 Intelligent Tiering] --> H[Storage Cost Optimization]
    end
    
    subgraph "Performance Optimization"
        I[QuickSight SPICE] --> J[In-Memory Performance]
        K[Athena Result Caching] --> L[Query Performance]
        M[S3 Transfer Acceleration] --> N[Data Transfer Speed]
    end
    
    subgraph "Resource Management"
        O[ECS Auto Scaling] --> P[Application Scaling]
        Q[Lambda Concurrency] --> R[Processing Optimization]
        S[CloudWatch Metrics] --> T[Performance Monitoring]
    end
    
    B --> E
    D --> G
    J --> K
    L --> M
    P --> Q
    R --> S
    
    style A fill:#e8f5e8
    style I fill:#fff3e0
    style O fill:#f3e5f5
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_STREAMLIT[Streamlit Dev Instance]
        DEV_S3[Development S3 Buckets]
        DEV_ATHENA[Athena Dev Workgroup]
    end
    
    subgraph "Staging Environment"
        STAGE_ALB[Staging Load Balancer]
        STAGE_ECS[Staging ECS Cluster]
        STAGE_S3[Staging S3 Buckets]
        STAGE_ATHENA[Athena Staging Workgroup]
    end
    
    subgraph "Production Environment"
        PROD_ALB[Production Load Balancer]
        PROD_ECS[Production ECS Cluster]
        PROD_S3[Production S3 Buckets]
        PROD_ATHENA[Athena Production Workgroup]
        PROD_QS[Production QuickSight]
    end
    
    subgraph "CI/CD Pipeline"
        GITHUB[GitHub Repository]
        CODEBUILD[AWS CodeBuild]
        CODEPIPELINE[AWS CodePipeline]
        ECR[Amazon ECR]
    end
    
    GITHUB --> CODEPIPELINE
    CODEPIPELINE --> CODEBUILD
    CODEBUILD --> ECR
    ECR --> STAGE_ECS
    ECR --> PROD_ECS
    
    DEV_STREAMLIT --> STAGE_ALB
    STAGE_ECS --> PROD_ALB
    
    style GITHUB fill:#f3e5f5
    style PROD_ECS fill:#e8f5e8
    style PROD_QS fill:#e8f5e8
```
