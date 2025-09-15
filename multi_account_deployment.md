# Multi-Account Deployment Guide

## 🚀 **Easy Account Switching**

### **Option 1: Use Configurable App (Recommended)**

Run the multi-account version:
```bash
streamlit run app_enterprise_configurable.py --server.port 8504
```

**Features:**
- ✅ **Dropdown selector** for different AWS accounts
- ✅ **Pre-configured settings** for both accounts
- ✅ **Same functionality** as single-account version
- ✅ **Easy switching** without code changes

### **Option 2: Create Separate App Files**

Copy and modify the enterprise app for the new account.

## 📋 **Account Configurations**

### **Account 1 (Original)**
```
AWS Account ID: 695233770948
Athena Results Bucket: aws-athena-query-results-us-east-1-695233770948
S3 Raw Data: s3://s3-glue-athena-demo-archive/contracts/
Glue Database: s3-athena-glue-enterprise-analytics-db
```

### **Account 2 (New)**
```
AWS Account ID: 476169753480
Athena Results Bucket: aws-athena-query-results-us-east-1-476169753480
S3 Raw Data: s3://s3-glue-athena-aidlc/contracts/
Glue Database: s3-athena-glue-enterprise-analytics-db
```

## 🔧 **Setup Steps for New Account**

### **Step 1: AWS Credentials**
```bash
# Configure AWS CLI for new account
aws configure --profile account2
# OR
aws sso login --profile account2
```

### **Step 2: Verify Infrastructure**
```bash
# Test Athena access
aws athena list-databases --catalog-name AwsDataCatalog --profile account2

# Test S3 access
aws s3 ls s3://aws-athena-query-results-us-east-1-476169753480/ --profile account2

# Test Glue database
aws glue get-database --name s3-athena-glue-enterprise-analytics-db --profile account2
```

### **Step 3: Run Multi-Account App**
```bash
streamlit run app_enterprise_configurable.py --server.port 8504
```

### **Step 4: Test Both Accounts**
1. **Select Account 1** from dropdown → Test connection
2. **Select Account 2** from dropdown → Test connection
3. **Execute queries** on both accounts
4. **Verify QuickSight links** work for both

## 🎯 **Benefits of Multi-Account App**

### **For Demos:**
- ✅ **Show scalability** across multiple AWS accounts
- ✅ **Demonstrate flexibility** of the solution
- ✅ **Easy switching** during presentations
- ✅ **Same codebase** for multiple environments

### **For Production:**
- ✅ **Dev/Test/Prod** environments
- ✅ **Multi-tenant** deployments
- ✅ **Regional** deployments
- ✅ **Customer-specific** configurations

## 📊 **QuickSight URLs by Account**

### **Account 1 (695233770948):**
- Console: https://us-east-1.quicksight.aws.amazon.com/sn/start
- Datasets: https://us-east-1.quicksight.aws.amazon.com/sn/start/data-sets

### **Account 2 (476169753480):**
- Console: https://us-east-1.quicksight.aws.amazon.com/sn/start
- Datasets: https://us-east-1.quicksight.aws.amazon.com/sn/start/data-sets

*Note: QuickSight URLs are the same - AWS automatically detects the account from your login session.*

## 🔄 **Adding More Accounts**

To add additional accounts, simply update the `ACCOUNT_CONFIGS` dictionary in `app_enterprise_configurable.py`:

```python
ACCOUNT_CONFIGS = {
    "Account 1 (695233770948)": { ... },
    "Account 2 (476169753480)": { ... },
    "Account 3 (NEW_ACCOUNT_ID)": {
        'aws_region': 'us-east-1',
        'aws_account_id': 'NEW_ACCOUNT_ID',
        'athena_workgroup': 'primary',
        's3_results_bucket': 'aws-athena-query-results-us-east-1-NEW_ACCOUNT_ID',
        'glue_database': 'your-database-name',
        's3_raw_data': 's3://your-raw-data-bucket/',
        'quicksight_account_id': 'NEW_ACCOUNT_ID'
    }
}
```

## 🎯 **Recommended Approach**

**Use the configurable app** (`app_enterprise_configurable.py`) because:

1. **Single codebase** - easier to maintain
2. **Easy switching** - dropdown selector
3. **Consistent functionality** - same features across accounts
4. **Demo-friendly** - impressive for customer presentations
5. **Production-ready** - scales to multiple environments

## 📞 **Testing Checklist**

For each account, verify:
- [ ] **Connection test** passes
- [ ] **Tables are discoverable** 
- [ ] **Queries execute successfully**
- [ ] **Results display correctly**
- [ ] **QuickSight links work**
- [ ] **Athena console link works**
- [ ] **Save/load queries work**

## 🚀 **Ready to Demo!**

The multi-account app demonstrates:
- **Enterprise scalability**
- **Multi-environment support** 
- **Easy configuration management**
- **Consistent user experience**
- **Production-ready architecture**
