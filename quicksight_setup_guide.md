# QuickSight Setup Guide

## 🚀 Quick Setup for QuickSight Integration

### **Step 1: Enable QuickSight**
1. Go to [AWS QuickSight Console](https://us-east-1.quicksight.aws.amazon.com/sn/accounts/695233770948/start)
2. If not already signed up, choose **Standard Edition**
3. Select your region: **US East (N. Virginia)**

### **Step 2: Grant S3 Access**
1. In QuickSight → **Manage QuickSight** → **Security & permissions**
2. Click **Add or remove**
3. Check **Amazon S3**
4. Select these buckets:
   - `aws-athena-query-results-us-east-1-695233770948`
   - `s3-glue-athena-demo-archive`
5. Click **Update**

### **Step 3: Grant Athena Access**
1. In **Security & permissions**
2. Check **Amazon Athena**
3. This allows QuickSight to read from your Athena databases

### **Step 4: Create Data Source**
1. In QuickSight → **Datasets** → **New dataset**
2. Choose **Athena**
3. Data source name: `Enterprise Analytics`
4. Athena workgroup: `primary`
5. Click **Create data source**

### **Step 5: Create Dataset from Query Results**

#### **Option A: From Athena Table**
1. Choose database: `s3-athena-glue-enterprise-analytics-db`
2. Select your table
3. Choose **Import to SPICE** for faster performance
4. Click **Visualize**

#### **Option B: From S3 Query Results**
1. Choose **S3** as data source
2. Upload manifest file pointing to query results
3. Configure data types
4. Import to SPICE

### **Step 6: Create Your First Visualization**

#### **Compliance Status Pie Chart**
1. Drag `compliance_status` to **Group/Color**
2. Drag `contract_id` to **Value** (set to Count)
3. Change visual type to **Pie chart**
4. Title: "Contract Compliance Distribution"

#### **Performance by Risk Level**
1. Drag `risk_level` to **X axis**
2. Drag `performance_score` to **Value** (set to Average)
3. Change visual type to **Bar chart**
4. Title: "Average Performance by Risk Level"

#### **KPI Achievement Dashboard**
1. Create multiple visuals:
   - KPI cards for total contracts, avg performance
   - Pie chart for compliance status
   - Bar chart for risk level distribution
   - Line chart for performance trends

### **Step 7: Create Dashboard**
1. Click **Share** → **Publish dashboard**
2. Name: "Contract Analytics Dashboard"
3. Add description and tags
4. Set permissions for your team

### **Step 8: Schedule Reports**
1. In dashboard → **Share** → **Email report**
2. Set schedule (daily, weekly, monthly)
3. Add recipients
4. Configure format (PDF, Excel)

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **"Access Denied" Errors**
- Check S3 bucket permissions in QuickSight settings
- Ensure Athena access is enabled
- Verify IAM roles have proper permissions

#### **"Table Not Found" Errors**
- Confirm Glue catalog is accessible
- Check database name spelling
- Verify table exists in Athena

#### **Slow Performance**
- Import data to SPICE instead of direct query
- Use incremental refresh for large datasets
- Optimize Athena queries with partitioning

### **Performance Tips:**
- **Use SPICE** for datasets under 10GB
- **Partition large tables** by date or region
- **Create calculated fields** in QuickSight instead of SQL
- **Use filters** to reduce data volume

## 📊 **Sample Dashboard Ideas**

### **Executive Dashboard**
- Total contracts count
- Compliance rate percentage
- Average performance score
- Risk distribution
- Monthly trends

### **Operational Dashboard**
- Non-compliant contracts list
- High-risk contracts requiring attention
- Performance scores by contract manager
- SLA achievement rates

### **Analytical Dashboard**
- Performance correlation analysis
- Risk vs compliance patterns
- Seasonal performance trends
- Predictive insights

## 🎯 **Next Steps**

1. **Test the setup** with sample data
2. **Create template dashboards** for different user roles
3. **Set up automated reports** for stakeholders
4. **Train business users** on QuickSight basics
5. **Implement row-level security** if needed

## 📞 **Support Resources**

- [QuickSight User Guide](https://docs.aws.amazon.com/quicksight/)
- [Athena Integration Guide](https://docs.aws.amazon.com/quicksight/latest/user/create-a-data-set-athena.html)
- [SPICE Performance Guide](https://docs.aws.amazon.com/quicksight/latest/user/spice.html)
