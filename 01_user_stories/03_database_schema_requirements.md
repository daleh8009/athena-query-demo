# Database Schema Requirements for Athena Query Generator

## Core Business Databases

### 1. Sales Database
**Purpose:** Track sales transactions, performance, and revenue metrics

**Key Tables:**
- `sales_transactions` - Individual sale records
- `sales_representatives` - Sales team information
- `sales_territories` - Geographic sales regions
- `sales_targets` - Goals and quotas by period

**Common Query Patterns:**
- Revenue by time period (daily, weekly, monthly, quarterly)
- Sales performance by representative/territory
- Product performance analysis
- Customer purchase patterns
- Comparative period analysis

**Key Relationships:**
- Sales transactions → Products (product performance)
- Sales transactions → Customers (customer analysis)
- Sales representatives → Territories (territory management)

---

### 2. Inventory Database
**Purpose:** Track product inventory, stock levels, and supply chain metrics

**Key Tables:**
- `inventory_levels` - Current stock quantities
- `inventory_movements` - Stock in/out transactions
- `products` - Product catalog and details
- `suppliers` - Vendor information
- `warehouses` - Storage location data

**Common Query Patterns:**
- Current stock levels by product/location
- Inventory turnover analysis
- Stock movement trends
- Supplier performance metrics
- Reorder point analysis

**Key Relationships:**
- Inventory → Products (product details)
- Inventory → Warehouses (location-based analysis)
- Products → Suppliers (supplier performance)

---

### 3. Customer Database
**Purpose:** Store customer information, demographics, and interaction history

**Key Tables:**
- `customers` - Customer master data
- `customer_interactions` - Support, sales contacts
- `customer_segments` - Marketing/business segments
- `customer_preferences` - Buying patterns and preferences

**Common Query Patterns:**
- Customer segmentation analysis
- Customer lifetime value calculations
- Churn analysis and retention metrics
- Geographic customer distribution
- Customer satisfaction trends

**Key Relationships:**
- Customers → Sales transactions (purchase history)
- Customers → Interactions (service history)
- Customers → Segments (marketing analysis)

---

## Data Field Categories

### Frequently Used Fields

**Temporal Fields:**
- `transaction_date`, `created_date`, `modified_date`
- `fiscal_year`, `fiscal_quarter`, `fiscal_month`
- `week_ending_date`, `business_day_flag`

**Financial Fields:**
- `revenue`, `cost`, `profit`, `margin_percent`
- `quantity`, `unit_price`, `total_amount`
- `budget`, `actual`, `variance`

**Geographic Fields:**
- `region`, `territory`, `country`, `state`, `city`
- `postal_code`, `sales_district`

**Product Fields:**
- `product_id`, `product_name`, `product_category`
- `brand`, `model`, `sku`

**Customer Fields:**
- `customer_id`, `customer_name`, `customer_type`
- `industry`, `company_size`, `acquisition_channel`

---

## Query Complexity Levels

### Level 1: Simple Single-Table Queries
**Examples:**
- "Show me total sales for last month"
- "List all products in Electronics category"
- "How many customers do we have in California?"

**Characteristics:**
- Single table access
- Basic aggregations (SUM, COUNT, AVG)
- Simple WHERE clauses
- Basic date filtering

---

### Level 2: Multi-Table Joins
**Examples:**
- "Show sales by product category for Q1"
- "List customers with their total purchase amounts"
- "Compare inventory levels across warehouses"

**Characteristics:**
- 2-3 table joins
- GROUP BY operations
- Multiple filtering conditions
- Cross-table calculations

---

### Level 3: Complex Analytics
**Examples:**
- "Calculate customer lifetime value by acquisition channel"
- "Show year-over-year growth by product and region"
- "Identify top 10% customers by profitability"

**Characteristics:**
- Multiple table joins (3+ tables)
- Window functions and ranking
- Complex date calculations
- Nested queries or CTEs

---

## Data Access Patterns

### Real-Time vs Historical Data
- **Real-Time:** Current inventory, today's sales, active customers
- **Historical:** Trend analysis, year-over-year comparisons, seasonal patterns
- **Mixed:** Performance dashboards combining current and historical data

### Aggregation Levels
- **Detail Level:** Individual transactions, specific customer records
- **Summary Level:** Daily/weekly/monthly aggregates
- **Executive Level:** High-level KPIs and trend summaries

---

## Performance Considerations

### Partitioning Strategy
- **Date Partitioning:** Most tables partitioned by date (daily/monthly)
- **Geographic Partitioning:** Large datasets partitioned by region
- **Product Partitioning:** Inventory data partitioned by product category

### Indexing Requirements
- Primary keys on all dimension tables
- Date indexes for time-based queries
- Foreign key indexes for join performance

### Query Optimization Guidelines
- Encourage date range filtering for large tables
- Promote use of pre-aggregated summary tables
- Suggest appropriate partition pruning
- Recommend LIMIT clauses for exploratory queries

---

## Data Governance Requirements

### Sensitive Data Fields
- Customer PII: `customer_name`, `email`, `phone`, `address`
- Financial: Detailed pricing, cost data, individual salaries
- Strategic: Future product plans, competitive analysis data

### Access Control Levels
- **Public:** Aggregated sales data, general product information
- **Internal:** Detailed customer data, operational metrics
- **Restricted:** Financial details, strategic planning data
- **Confidential:** Individual performance data, sensitive customer information

### Data Masking Rules
- Customer names → Generic identifiers (Customer_001, Customer_002)
- Email addresses → Masked format (***@domain.com)
- Phone numbers → Partial masking (***-***-1234)
- Addresses → City/State only, no street addresses
