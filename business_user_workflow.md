# Business User Workflow - Natural Language to QuickSight Visualizations

## Complete User Journey Diagram

```mermaid
flowchart TD
    A[Business User] --> B[Streamlit Chat Interface]
    B --> C{Natural Language Input}
    C --> D["Ask Question:<br/>'Show me Q1 sales by region'"]
    
    D --> E[NLP Processing Engine]
    E --> F{Query Clarification Needed?}
    F -->|Yes| G[Ask Clarifying Questions]
    G --> H[User Provides Details]
    H --> E
    F -->|No| I[Generate SQL Query]
    
    I --> J[Display Generated SQL<br/>with Explanation]
    J --> K{User Approves Query?}
    K -->|No| L[Edit SQL Query]
    L --> J
    K -->|Yes| M[Execute Query on Athena]
    
    M --> N[Query Results]
    N --> O[Format & Display Results]
    O --> P{Export Data?}
    
    P -->|CSV/Excel| Q[Download File]
    P -->|QuickSight| R[Export to S3]
    R --> S[Create QuickSight Dataset]
    
    S --> T[QuickSight Analysis]
    T --> U[Create Visualizations]
    U --> V[Build Dashboard]
    V --> W[Generate Data Story]
    W --> X[Executive Summary]
    
    Q --> Y[End: File Downloaded]
    X --> Z[End: Complete Analysis]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style M fill:#fff3e0
    style S fill:#e8f5e8
    style T fill:#e8f5e8
    style U fill:#e8f5e8
    style V fill:#e8f5e8
    style W fill:#e8f5e8
    style X fill:#ffebee
```

## Detailed Component Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[Streamlit Chat Interface]
        AUTH[AWS SSO Authentication]
    end
    
    subgraph "Processing Layer"
        NLP[Natural Language Processor]
        QG[SQL Query Generator]
        QV[Query Validator]
        QO[Query Optimizer]
    end
    
    subgraph "Data Layer"
        ATHENA[Amazon Athena]
        S3[Amazon S3]
        GLUE[AWS Glue Catalog]
    end
    
    subgraph "Analytics Layer"
        QS[Amazon QuickSight]
        DS[Dataset Management]
        VIZ[Visualization Engine]
        DASH[Dashboard Builder]
        STORY[Data Stories]
    end
    
    subgraph "Data Sources"
        SALES[(Sales Database)]
        CUSTOMER[(Customer Database)]
        INVENTORY[(Inventory Database)]
    end
    
    UI --> AUTH
    AUTH --> NLP
    NLP --> QG
    QG --> QV
    QV --> QO
    QO --> ATHENA
    
    ATHENA --> GLUE
    GLUE --> SALES
    GLUE --> CUSTOMER
    GLUE --> INVENTORY
    
    ATHENA --> S3
    S3 --> QS
    QS --> DS
    DS --> VIZ
    VIZ --> DASH
    DASH --> STORY
    
    style UI fill:#e1f5fe
    style ATHENA fill:#fff3e0
    style QS fill:#e8f5e8
    style STORY fill:#ffebee
```

## User Interaction Flow

```mermaid
sequenceDiagram
    participant U as Business User
    participant S as Streamlit App
    participant A as Athena
    participant S3 as S3 Storage
    participant Q as QuickSight
    
    U->>S: Login via SSO
    U->>S: "Show me top 10 customers by revenue"
    S->>S: Process natural language
    S->>S: Generate SQL query
    S->>U: Display SQL + explanation
    U->>S: Approve query
    S->>A: Execute SQL query
    A->>S: Return results
    S->>U: Display formatted results
    U->>S: Export to QuickSight
    S->>S3: Save dataset to S3
    S->>Q: Create QuickSight dataset
    Q->>U: Dataset ready for analysis
    U->>Q: Create visualizations
    U->>Q: Build dashboard
    U->>Q: Generate data story
    U->>Q: Create executive summary
```

## QuickSight Integration Workflow

```mermaid
flowchart LR
    subgraph "Streamlit Application"
        A[Query Results] --> B[Data Validation]
        B --> C[Format for Export]
        C --> D[Export Options]
    end
    
    subgraph "Data Transfer"
        D --> E[Save to S3 Bucket]
        E --> F[Generate Manifest File]
        F --> G[Trigger QuickSight Import]
    end
    
    subgraph "QuickSight Processing"
        G --> H[Create Dataset]
        H --> I[Data Preparation]
        I --> J[Schema Detection]
        J --> K[Data Types Mapping]
    end
    
    subgraph "Visualization Creation"
        K --> L[Analysis Creation]
        L --> M[Chart Selection]
        M --> N[Visual Configuration]
        N --> O[Dashboard Assembly]
    end
    
    subgraph "Reporting & Sharing"
        O --> P[Data Story Creation]
        P --> Q[Executive Summary]
        Q --> R[Share & Collaborate]
    end
    
    style A fill:#f3e5f5
    style E fill:#fff3e0
    style H fill:#e8f5e8
    style L fill:#e8f5e8
    style P fill:#ffebee
```
