import AWS from 'aws-sdk';

// Configure AWS SDK
const quicksight = new AWS.QuickSight({
  region: process.env.REACT_APP_AWS_REGION || 'us-east-1'
});

const athena = new AWS.Athena({
  region: process.env.REACT_APP_AWS_REGION || 'us-east-1'
});

export class QuickSightService {
  constructor() {
    this.accountId = process.env.REACT_APP_AWS_ACCOUNT_ID;
    this.workGroup = process.env.REACT_APP_ATHENA_WORKGROUP || 'primary';
    this.database = process.env.REACT_APP_GLUE_DATABASE || 's3-glue-athena-enterprise-analytics-db';
  }

  /**
   * Auto-export query results to QuickSight
   */
  async exportToQuickSight(sqlQuery, queryDescription, userPrompt) {
    try {
      console.log('🚀 Starting QuickSight export...');
      
      // Step 1: Create a unique dataset name
      const datasetName = this.generateDatasetName(queryDescription, userPrompt);
      const datasetId = this.generateDatasetId(datasetName);
      
      // Step 2: Create QuickSight data source (if not exists)
      await this.ensureAthenaDataSource();
      
      // Step 3: Create QuickSight dataset with custom SQL
      const dataset = await this.createDataset(datasetId, datasetName, sqlQuery);
      
      // Step 4: Generate QuickSight URLs
      const urls = this.generateQuickSightUrls(datasetId);
      
      console.log('✅ QuickSight export completed!');
      
      return {
        success: true,
        dataset: {
          id: datasetId,
          name: datasetName,
          arn: dataset.Arn
        },
        urls: urls,
        message: `Dataset "${datasetName}" created successfully in QuickSight!`
      };
      
    } catch (error) {
      console.error('❌ QuickSight export failed:', error);
      
      return {
        success: false,
        error: error.message,
        message: 'Failed to export to QuickSight. Please try manual import.'
      };
    }
  }

  /**
   * Generate a clean dataset name from user prompt
   */
  generateDatasetName(queryDescription, userPrompt) {
    // Use user prompt if available, otherwise use query description
    const baseName = userPrompt || queryDescription || 'Athena Query Results';
    
    // Clean and format the name
    const cleanName = baseName
      .replace(/[^a-zA-Z0-9\s]/g, '') // Remove special characters
      .replace(/\s+/g, ' ') // Normalize spaces
      .trim()
      .substring(0, 50); // Limit length
    
    // Add timestamp for uniqueness
    const timestamp = new Date().toISOString().slice(0, 16).replace(/[-:]/g, '');
    
    return `${cleanName} (${timestamp})`;
  }

  /**
   * Generate QuickSight-compatible dataset ID
   */
  generateDatasetId(datasetName) {
    return datasetName
      .toLowerCase()
      .replace(/[^a-z0-9]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '')
      .substring(0, 128);
  }

  /**
   * Ensure Athena data source exists in QuickSight
   */
  async ensureAthenaDataSource() {
    const dataSourceId = 'athena-enterprise-analytics';
    
    try {
      // Check if data source exists
      await quicksight.describeDataSource({
        AwsAccountId: this.accountId,
        DataSourceId: dataSourceId
      }).promise();
      
      console.log('✅ Athena data source already exists');
      return dataSourceId;
      
    } catch (error) {
      if (error.code === 'ResourceNotFoundException') {
        // Create new Athena data source
        console.log('📝 Creating new Athena data source...');
        
        await quicksight.createDataSource({
          AwsAccountId: this.accountId,
          DataSourceId: dataSourceId,
          Name: 'Enterprise Analytics - Athena',
          Type: 'ATHENA',
          DataSourceParameters: {
            AthenaParameters: {
              WorkGroup: this.workGroup
            }
          },
          Permissions: [
            {
              Principal: `arn:aws:quicksight:${process.env.REACT_APP_AWS_REGION}:${this.accountId}:user/default/${process.env.REACT_APP_QUICKSIGHT_USER || 'Admin'}`,
              Actions: [
                'quicksight:DescribeDataSource',
                'quicksight:DescribeDataSourcePermissions',
                'quicksight:PassDataSource'
              ]
            }
          ]
        }).promise();
        
        console.log('✅ Athena data source created');
        return dataSourceId;
      }
      
      throw error;
    }
  }

  /**
   * Create QuickSight dataset with custom SQL
   */
  async createDataset(datasetId, datasetName, sqlQuery) {
    const dataSourceId = 'athena-enterprise-analytics';
    
    const params = {
      AwsAccountId: this.accountId,
      DataSetId: datasetId,
      Name: datasetName,
      PhysicalTableMap: {
        'athena-query-table': {
          CustomSql: {
            DataSourceArn: `arn:aws:quicksight:${process.env.REACT_APP_AWS_REGION}:${this.accountId}:datasource/${dataSourceId}`,
            Name: datasetName,
            SqlQuery: sqlQuery,
            Columns: [] // QuickSight will auto-detect columns
          }
        }
      },
      ImportMode: 'SPICE', // Import to SPICE for better performance
      Permissions: [
        {
          Principal: `arn:aws:quicksight:${process.env.REACT_APP_AWS_REGION}:${this.accountId}:user/default/${process.env.REACT_APP_QUICKSIGHT_USER || 'Admin'}`,
          Actions: [
            'quicksight:DescribeDataSet',
            'quicksight:DescribeDataSetPermissions',
            'quicksight:PassDataSet',
            'quicksight:DescribeIngestion',
            'quicksight:ListIngestions'
          ]
        }
      ]
    };

    const result = await quicksight.createDataSet(params).promise();
    
    // Trigger SPICE ingestion
    await this.triggerSpiceIngestion(datasetId);
    
    return result;
  }

  /**
   * Trigger SPICE ingestion for faster queries
   */
  async triggerSpiceIngestion(datasetId) {
    try {
      const ingestionId = `ingestion-${Date.now()}`;
      
      await quicksight.createIngestion({
        AwsAccountId: this.accountId,
        DataSetId: datasetId,
        IngestionId: ingestionId,
        IngestionType: 'FULL_REFRESH'
      }).promise();
      
      console.log('✅ SPICE ingestion triggered');
    } catch (error) {
      console.warn('⚠️ SPICE ingestion failed (dataset still usable):', error.message);
    }
  }

  /**
   * Generate QuickSight URLs for easy access
   */
  generateQuickSightUrls(datasetId) {
    const baseUrl = `https://${process.env.REACT_APP_AWS_REGION}.quicksight.aws.amazon.com/sn/accounts/${this.accountId}`;
    
    return {
      dataset: `${baseUrl}/datasets/${datasetId}`,
      createAnalysis: `${baseUrl}/analyses/new?dataset=${datasetId}`,
      createDashboard: `${baseUrl}/dashboards/new?dataset=${datasetId}`,
      quickSightHome: baseUrl
    };
  }

  /**
   * Check QuickSight dataset status
   */
  async getDatasetStatus(datasetId) {
    try {
      const result = await quicksight.describeDataSet({
        AwsAccountId: this.accountId,
        DataSetId: datasetId
      }).promise();
      
      return {
        exists: true,
        status: result.DataSet.ImportMode,
        lastUpdated: result.DataSet.LastUpdatedTime,
        rowCount: result.DataSet.ConsumedSpiceCapacityInBytes
      };
    } catch (error) {
      return {
        exists: false,
        error: error.message
      };
    }
  }
}

export default new QuickSightService();
