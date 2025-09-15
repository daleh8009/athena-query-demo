import React, { useState } from 'react';
import quicksightService from '../services/quicksightService';

const QuickSightExport = ({ sqlQuery, queryDescription, userPrompt, isVisible }) => {
  const [exportStatus, setExportStatus] = useState('idle'); // idle, loading, success, error
  const [exportResult, setExportResult] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  if (!isVisible || !sqlQuery) {
    return null;
  }

  const handleExportToQuickSight = async () => {
    setExportStatus('loading');
    setExportResult(null);

    try {
      const result = await quicksightService.exportToQuickSight(
        sqlQuery,
        queryDescription,
        userPrompt
      );

      setExportResult(result);
      setExportStatus(result.success ? 'success' : 'error');
      
      if (result.success) {
        setShowDetails(true);
      }
    } catch (error) {
      setExportResult({
        success: false,
        error: error.message,
        message: 'Export failed. Please check your AWS configuration.'
      });
      setExportStatus('error');
    }
  };

  const openQuickSightUrl = (url) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-blue-900">
            📊 Export to Amazon QuickSight
          </h3>
          <p className="text-sm text-blue-700">
            Create interactive dashboards and visualizations from your query results
          </p>
        </div>
        
        {exportStatus === 'idle' && (
          <button
            onClick={handleExportToQuickSight}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            🚀 Export to QuickSight
          </button>
        )}
        
        {exportStatus === 'loading' && (
          <div className="flex items-center px-6 py-2 bg-blue-100 text-blue-800 rounded-lg">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            Creating Dataset...
          </div>
        )}
      </div>

      {/* Export Results */}
      {exportStatus === 'success' && exportResult && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-semibold text-green-900 mb-2">
                ✅ Export Successful!
              </h4>
              <p className="text-green-800 mb-3">
                {exportResult.message}
              </p>
              <p className="text-sm text-green-700">
                <strong>Dataset Name:</strong> {exportResult.dataset.name}
              </p>
            </div>
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="text-green-600 hover:text-green-800 text-sm"
            >
              {showDetails ? 'Hide Details' : 'Show Options'}
            </button>
          </div>

          {showDetails && (
            <div className="mt-4 pt-4 border-t border-green-200">
              <h5 className="font-medium text-green-900 mb-3">
                🎯 Next Steps - Choose Your Action:
              </h5>
              
              <div className="grid md:grid-cols-2 gap-3">
                <button
                  onClick={() => openQuickSightUrl(exportResult.urls.createAnalysis)}
                  className="flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  📈 Create Analysis
                  <span className="ml-2 text-xs">(Recommended)</span>
                </button>
                
                <button
                  onClick={() => openQuickSightUrl(exportResult.urls.createDashboard)}
                  className="flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  📊 Create Dashboard
                </button>
                
                <button
                  onClick={() => openQuickSightUrl(exportResult.urls.dataset)}
                  className="flex items-center justify-center px-4 py-3 border border-green-600 text-green-600 rounded-lg hover:bg-green-50 transition-colors"
                >
                  🗂️ View Dataset
                </button>
                
                <button
                  onClick={() => openQuickSightUrl(exportResult.urls.quickSightHome)}
                  className="flex items-center justify-center px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  🏠 QuickSight Home
                </button>
              </div>

              <div className="mt-4 p-3 bg-green-100 rounded-lg">
                <h6 className="font-medium text-green-900 mb-2">💡 Pro Tips:</h6>
                <ul className="text-sm text-green-800 space-y-1">
                  <li>• <strong>Analysis</strong> - Best for exploring and creating visualizations</li>
                  <li>• <strong>Dashboard</strong> - Best for sharing insights with others</li>
                  <li>• <strong>Dataset</strong> - Manage data refresh and permissions</li>
                  <li>• Data is imported to SPICE for faster performance</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      )}

      {exportStatus === 'error' && exportResult && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <h4 className="font-semibold text-red-900 mb-2">
            ❌ Export Failed
          </h4>
          <p className="text-red-800 mb-3">
            {exportResult.message}
          </p>
          
          {exportResult.error && (
            <details className="text-sm text-red-700">
              <summary className="cursor-pointer font-medium">Technical Details</summary>
              <pre className="mt-2 p-2 bg-red-100 rounded text-xs overflow-x-auto">
                {exportResult.error}
              </pre>
            </details>
          )}

          <div className="mt-4 p-3 bg-red-100 rounded-lg">
            <h6 className="font-medium text-red-900 mb-2">🔧 Manual Workaround:</h6>
            <ol className="text-sm text-red-800 space-y-1 list-decimal list-inside">
              <li>Go to <a href="https://quicksight.aws.amazon.com" target="_blank" rel="noopener noreferrer" className="underline">QuickSight Console</a></li>
              <li>Click "New dataset" → "Athena"</li>
              <li>Database: <code className="bg-red-200 px-1 rounded">s3-glue-athena-enterprise-analytics-db</code></li>
              <li>Use "Custom SQL" and paste your generated query</li>
            </ol>
          </div>

          <button
            onClick={() => {
              setExportStatus('idle');
              setExportResult(null);
            }}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Query Preview */}
      <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
        <details>
          <summary className="cursor-pointer font-medium text-gray-700 mb-2">
            📝 SQL Query to Export
          </summary>
          <pre className="text-sm text-gray-600 bg-white p-3 rounded border overflow-x-auto">
            {sqlQuery}
          </pre>
        </details>
      </div>

      {/* Configuration Help */}
      {exportStatus === 'error' && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h6 className="font-medium text-yellow-900 mb-2">⚙️ Configuration Check:</h6>
          <p className="text-sm text-yellow-800 mb-2">
            Make sure these environment variables are set:
          </p>
          <ul className="text-xs text-yellow-700 space-y-1 font-mono">
            <li>• REACT_APP_AWS_ACCOUNT_ID</li>
            <li>• REACT_APP_AWS_REGION</li>
            <li>• REACT_APP_QUICKSIGHT_USER</li>
            <li>• REACT_APP_GLUE_DATABASE</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default QuickSightExport;
