# QuickSight Auto-Export Setup Guide

## 🎯 **What This Does**

The auto-export feature automatically creates QuickSight datasets from your Athena queries, eliminating the manual steps and confusion. 

**Before**: Generate SQL → Copy query → Go to QuickSight → Manual import → Create dataset
**After**: Generate SQL → Click "Export to QuickSight" → Done! ✨

## ⚙️ **Setup Requirements**

### **1. Streamlit Secrets Configuration**

Add these to your Streamlit secrets (Settings → Secrets):

```toml
# Required for QuickSight Export
AWS_ACCOUNT_ID = "476169753480"  # Your AWS Account ID
AWS_REGION = "us-east-1"         # Your AWS Region
GLUE_DATABASE = "s3-glue-athena-enterprise-analytics-db"  # Your Glue Database
ATHENA_WORKGROUP = "primary"     # Your Athena Workgroup (optional)
```

### **2. AWS Permissions**

Your AWS credentials need these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "quicksight:CreateDataSource",
        "quicksight:DescribeDataSource",
        "quicksight:CreateDataSet",
        "quicksight:DescribeDataSet",
        "quicksight:CreateIngestion",
        "quicksight:DescribeIngestion"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "athena:GetQueryExecution",
        "athena:GetQueryResults",
        "athena:StartQueryExecution"
      ],
      "Resource": "*"
    }
  ]
}
```

### **3. QuickSight Setup**

1. **Enable QuickSight** in your AWS account
2. **Add Athena permissions** to QuickSight:
   - Go to QuickSight → Manage QuickSight → Security & permissions
   - Add Amazon Athena access
   - Select your S3 buckets for Athena results

## 🚀 **How to Use**

### **Step 1: Generate Query**
- Ask your question: "Display contracts up for renewal"
- Review the generated SQL
- Click "Execute Query" to see results

### **Step 2: Auto-Export**
- Scroll down to see "📊 Export to Amazon QuickSight" section
- Click "🚀 Export to QuickSight" button
- Wait for "✅ Dataset created successfully!" message

### **Step 3: Create Visualizations**
Choose your next action:
- **📈 Create Analysis** - Best for exploring and creating charts
- **📊 Create Dashboard** - Best for sharing with stakeholders
- **🗂️ View Dataset** - Manage data refresh and permissions

## 🎯 **What Gets Created**

### **Dataset Name Format**
```
"Display contracts up for renewal (20241212_0930)"
```
- Uses your original question
- Adds timestamp for uniqueness
- Automatically cleaned for QuickSight compatibility

### **Dataset Features**
- ✅ **SPICE Import** - Fast query performance
- ✅ **Auto-detected columns** - Proper data types
- ✅ **Custom SQL** - Uses your exact query
- ✅ **Refresh capability** - Update data anytime

## 🔧 **Troubleshooting**

### **"AWS Account ID not configured"**
- Add `AWS_ACCOUNT_ID` to Streamlit secrets
- Make sure it matches your actual AWS account

### **"Failed to create dataset"**
- Check AWS permissions (see above)
- Verify QuickSight is enabled in your account
- Ensure Athena data source permissions in QuickSight

### **"Data source creation failed"**
- QuickSight needs permission to access Athena
- Go to QuickSight → Manage QuickSight → Security & permissions
- Enable Amazon Athena access

### **Manual Workaround**
If auto-export fails, you can still create datasets manually:

1. Go to [QuickSight Console](https://quicksight.aws.amazon.com)
2. Click "New dataset" → "Athena"
3. Database: `s3-glue-athena-enterprise-analytics-db`
4. Use "Custom SQL" and paste your generated query

## 💡 **Pro Tips**

### **Best Practices**
- ✅ **Test queries first** - Execute and verify results before exporting
- ✅ **Use descriptive questions** - They become your dataset names
- ✅ **Export frequently used queries** - Build a library of datasets
- ✅ **Set up refresh schedules** - Keep data current in QuickSight

### **Performance Tips**
- 📊 **SPICE import** - Faster than direct query mode
- 🔄 **Refresh datasets** - Update when underlying data changes
- 📈 **Create analyses** - Better performance than dashboards for exploration
- 🎯 **Filter early** - Use WHERE clauses to limit data size

## 🎉 **Success Workflow**

```
1. Ask Question → 2. Generate SQL → 3. Execute Query → 4. Export to QuickSight → 5. Create Analysis → 6. Build Dashboard → 7. Share Insights
```

**No more manual CSV imports or complex QuickSight setup!** 🚀

## 📞 **Need Help?**

- **Configuration Issues**: Check Streamlit secrets and AWS permissions
- **QuickSight Problems**: Verify QuickSight setup and Athena access
- **Dataset Errors**: Try the manual workaround process
- **Performance Issues**: Use SPICE import and proper filtering

---

**Transform your data analysis workflow with one-click QuickSight exports!** ✨
