-- Corrected CREATE VIEW statement using the actual table structure
-- Based on executive_dashboard_detailed table

CREATE VIEW contract_risk_analysis AS
SELECT 
    contract_id,
    contract_name,
    status,
    compliance_status,
    performance_score,
    department,
    contract_owner,
    CASE 
        WHEN performance_score >= 90 THEN 'Excellent'
        WHEN performance_score >= 80 THEN 'Good'
        WHEN performance_score >= 70 THEN 'Fair'
        ELSE 'Poor'
    END as performance_rating,
    CASE 
        WHEN performance_score < 70 OR compliance_status = 'Non-Compliant' THEN 'High'
        WHEN performance_score < 85 THEN 'Medium'
        ELSE 'Low'
    END as risk_level
FROM "s3-glue-athena-enterprise-analytics-db".executive_dashboard_detailed;
