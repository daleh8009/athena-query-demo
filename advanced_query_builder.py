"""
Advanced Query Builder for Technical Users & Developer Learning
Extends Athena Query Generator with complex SQL capabilities
"""

import streamlit as st
import re
from datetime import datetime

def add_sql_explanations(sql_query):
    """Add educational comments to generated SQL"""
    explanations = {
        'JOIN': '-- JOIN: Combines data from multiple tables based on relationships',
        'LEFT JOIN': '-- LEFT JOIN: Keeps all records from left table, matches from right',
        'WHERE': '-- WHERE: Filters rows based on conditions',
        'GROUP BY': '-- GROUP BY: Groups rows for aggregation functions',
        'HAVING': '-- HAVING: Filters groups after GROUP BY',
        'UNION': '-- UNION: Combines results from multiple SELECT statements',
        'CASE WHEN': '-- CASE WHEN: Creates conditional logic (if-then-else)',
        'WITH': '-- WITH: Common Table Expression (CTE) for complex queries'
    }
    
    explained_sql = sql_query
    for keyword, explanation in explanations.items():
        if keyword in sql_query.upper():
            # Add explanation before first occurrence
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            explained_sql = pattern.sub(f"{explanation}\n{keyword}", explained_sql, count=1)
    
    return explained_sql

def get_learning_level_sql(question, complexity_level="beginner", available_tables=None):
    """Generate SQL based on developer skill level"""
    
    if complexity_level == "beginner":
        return f"""-- BEGINNER LEVEL: Simple query with explanations
-- Question: {question}
-- Concept: Basic SELECT with single table

SELECT *                    -- SELECT: Choose which columns to return
FROM executive_dashboard_detailed  -- FROM: Specify the source table
WHERE status = 'Active'     -- WHERE: Filter for only active contracts
LIMIT 10;                   -- LIMIT: Restrict number of results

-- Next step: Try adding ORDER BY to sort results"""

    elif complexity_level == "intermediate":
        return f"""-- INTERMEDIATE LEVEL: Multi-table joins
-- Question: {question}
-- Concepts: INNER JOIN, table aliases, calculated fields

SELECT 
    cm.Contract_Name,       -- Use table alias (cm) for clarity
    cc.Risk_Level,
    cc.Performance_Score,
    CASE                    -- CASE: Create conditional logic
        WHEN cc.Performance_Score >= 90 THEN 'Excellent'
        WHEN cc.Performance_Score >= 80 THEN 'Good'
        ELSE 'Needs Improvement'
    END as Rating
FROM contract_master cm     -- Alias: cm = contract_master
INNER JOIN contract_compliance cc  -- INNER JOIN: Only matching records
    ON cm.Contract_ID = cc.Contract_ID  -- Join condition: matching IDs
WHERE cc.Risk_Level = 'High'
ORDER BY cc.Performance_Score DESC;

-- Learning: Try changing INNER JOIN to LEFT JOIN to see the difference"""

    else:  # advanced
        return f"""-- ADVANCED LEVEL: Complex multi-table analysis
-- Question: {question}
-- Concepts: Multiple JOINs, subqueries, window functions

WITH risk_summary AS (      -- CTE: Common Table Expression (temporary result set)
    SELECT 
        Department,
        AVG(Performance_Score) as avg_performance,
        COUNT(*) as contract_count
    FROM contract_master cm
    JOIN contract_compliance cc ON cm.Contract_ID = cc.Contract_ID
    JOIN contract_ownership co ON cm.Contract_ID = co.Contract_ID
    GROUP BY Department
),
high_risk_contracts AS (
    SELECT Contract_ID, Risk_Level
    FROM contract_compliance 
    WHERE Risk_Level IN ('High', 'Critical')
)
SELECT 
    rs.Department,
    rs.avg_performance,
    rs.contract_count,
    COUNT(hrc.Contract_ID) as high_risk_count,
    ROUND(COUNT(hrc.Contract_ID) * 100.0 / rs.contract_count, 2) as risk_percentage
FROM risk_summary rs
LEFT JOIN contract_ownership co ON rs.Department = co.Department
LEFT JOIN high_risk_contracts hrc ON co.Contract_ID = hrc.Contract_ID
GROUP BY rs.Department, rs.avg_performance, rs.contract_count
ORDER BY risk_percentage DESC;

-- Advanced concepts used:
-- 1. CTE (WITH clause) for readable complex queries
-- 2. Multiple JOINs across several tables
-- 3. Subqueries for filtering
-- 4. Aggregate functions with GROUP BY
-- 5. Calculated percentages"""

def generate_complex_sql(question, user_skill_level, available_tables=None):
    """Enhanced NL processing for technical users"""
    
    if user_skill_level == "technical_business":
        # Technical business users - complex but guided
        return generate_guided_complex_sql(question, available_tables)
    
    elif user_skill_level == "developer_learning":
        # Developers learning SQL - educational approach
        return generate_educational_sql(question, available_tables)
    
    else:
        # Regular business users - suggest pre-built views
        return suggest_prebuilt_views(question, available_tables)

def generate_guided_complex_sql(question, available_tables):
    """Generate complex SQL with intermediate steps for technical business users"""
    
    # Analyze question for complexity indicators
    question_lower = question.lower()
    complexity_indicators = {
        'joins_needed': any(word in question_lower for word in ['across', 'with', 'including', 'combined']),
        'aggregation': any(word in question_lower for word in ['total', 'average', 'count', 'sum', 'by department']),
        'filtering': any(word in question_lower for word in ['where', 'only', 'excluding', 'high', 'low']),
        'time_series': any(word in question_lower for word in ['trend', 'over time', 'monthly', 'quarterly'])
    }
    
    # Build SQL step by step
    steps = []
    sql_parts = []
    
    # Step 1: Base selection
    if 'risk' in question_lower and 'compliance' in question_lower:
        steps.append("Step 1: Start with contract master data")
        sql_parts.append("SELECT cm.Contract_ID, cm.Contract_Name, cm.Status")
        sql_parts.append("FROM contract_master cm")
        
        # Step 2: Add joins
        if complexity_indicators['joins_needed']:
            steps.append("Step 2: Join compliance data for risk analysis")
            sql_parts.append("JOIN contract_compliance cc ON cm.Contract_ID = cc.Contract_ID")
            
            steps.append("Step 3: Add ownership data for department analysis")
            sql_parts.append("JOIN contract_ownership co ON cm.Contract_ID = co.Contract_ID")
        
        # Step 3: Add calculated fields
        steps.append("Step 4: Add performance rating calculation")
        sql_parts.insert(1, """    cc.Risk_Level,
    cc.Compliance_Status,
    cc.Performance_Score,
    co.Department,
    co.Contract_Owner,
    CASE 
        WHEN cc.Performance_Score >= 90 THEN 'Excellent'
        WHEN cc.Performance_Score >= 80 THEN 'Good'
        WHEN cc.Performance_Score >= 70 THEN 'Fair'
        ELSE 'Poor'
    END as Performance_Rating""")
    
    # Combine SQL parts
    final_sql = "\n".join(sql_parts) + ";"
    
    # Add step-by-step explanation
    explanation = f"""-- TECHNICAL BUSINESS USER QUERY
-- Question: {question}
-- Complexity Analysis: {len([k for k, v in complexity_indicators.items() if v])} complex features detected

-- STEP-BY-STEP BREAKDOWN:
""" + "\n".join(f"-- {step}" for step in steps) + f"""

-- FINAL QUERY:
{final_sql}

-- PERFORMANCE NOTES:
-- • This query joins {len([p for p in sql_parts if 'JOIN' in p]) + 1} tables
-- • Expected execution time: 5-15 seconds
-- • Result set size: Estimated 100-1000 rows"""
    
    return explanation

def generate_educational_sql(question, available_tables):
    """Generate SQL with educational focus for developers"""
    
    # Determine appropriate learning level based on question complexity
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['simple', 'basic', 'show me']):
        complexity = "beginner"
    elif any(word in question_lower for word in ['analysis', 'compare', 'breakdown']):
        complexity = "intermediate"
    else:
        complexity = "advanced"
    
    return get_learning_level_sql(question, complexity, available_tables)

def suggest_prebuilt_views(question, available_tables):
    """Suggest pre-built views for regular business users"""
    
    question_lower = question.lower()
    
    suggestions = []
    
    if 'executive' in question_lower or 'dashboard' in question_lower:
        suggestions.append("executive_dashboard_detailed")
    
    if 'risk' in question_lower or 'compliance' in question_lower:
        suggestions.append("contract_risk_analysis")
    
    if 'renewal' in question_lower:
        suggestions.append("renewals_contracts_detailed")
    
    if not suggestions and available_tables:
        suggestions = [t for t in available_tables if 'detailed' in t or 'view' in t.lower()][:3]
    
    suggested_view = suggestions[0] if suggestions else "executive_dashboard_detailed"
    
    return f"""-- BUSINESS USER RECOMMENDATION
-- Question: {question}
-- Suggested approach: Use pre-built view

SELECT *
FROM {suggested_view}
WHERE status = 'Active'  -- Modify this condition as needed
ORDER BY contract_name
LIMIT 100;

-- ALTERNATIVE VIEWS AVAILABLE:
{chr(10).join(f'-- • {view}' for view in suggestions[:5])}

-- For more complex analysis, consider asking:
-- "Show me risk analysis across departments"
-- "Compare performance by contract type"
-- "Analyze renewal trends over time" """

def render_advanced_query_ui():
    """Render advanced query builder UI"""
    
    st.markdown("### 🚀 Advanced Query Builder")
    
    # User skill level selector
    col1, col2 = st.columns(2)
    
    with col1:
        user_type = st.selectbox(
            "User Type:",
            [
                "business_user",
                "technical_business", 
                "developer_learning",
                "sql_expert"
            ],
            format_func=lambda x: {
                "business_user": "📊 Business User",
                "technical_business": "🔧 Technical Business User", 
                "developer_learning": "🎓 Developer (Learning)",
                "sql_expert": "⚡ SQL Expert"
            }[x]
        )
    
    with col2:
        if user_type == "developer_learning":
            complexity = st.selectbox(
                "Learning Level:",
                ["beginner", "intermediate", "advanced"]
            )
        else:
            complexity = "auto"
    
    # Enhanced question input
    st.markdown("#### 💬 Describe Your Analysis Need")
    
    question = st.text_area(
        "What insights do you need?",
        placeholder="Examples:\n• Show me risk analysis across all departments with performance ratings\n• Create a comprehensive view of contract compliance and financial metrics\n• Analyze renewal trends with 14-table deep joins for executive reporting",
        height=100
    )
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        show_steps = st.checkbox("Show step-by-step breakdown", value=True)
        show_performance = st.checkbox("Show performance estimates", value=True)
        show_alternatives = st.checkbox("Suggest alternative approaches", value=True)
        
        if user_type == "developer_learning":
            show_concepts = st.checkbox("Show learning concepts", value=True)
            show_examples = st.checkbox("Include related examples", value=True)
    
    # Generate button
    if st.button("🔄 Generate Advanced Query", type="primary"):
        if question:
            with st.spinner("🤖 Analyzing requirements and generating optimized SQL..."):
                
                # Get available tables (you'll need to integrate with your existing function)
                available_tables = ["contract_master", "contract_compliance", "contract_ownership", 
                                  "executive_dashboard_detailed", "renewals_contracts_detailed"]
                
                # Generate SQL based on user type
                if user_type == "developer_learning":
                    sql_result = get_learning_level_sql(question, complexity, available_tables)
                else:
                    sql_result = generate_complex_sql(question, user_type, available_tables)
                
                # Store in session state
                st.session_state.advanced_sql = sql_result
                st.session_state.advanced_question = question
                st.session_state.user_type = user_type
                
                st.success("✅ Advanced query generated!")
        else:
            st.warning("Please describe your analysis needs first.")
    
    # Display generated SQL
    if 'advanced_sql' in st.session_state:
        st.markdown("### 📝 Generated Advanced SQL")
        st.code(st.session_state.advanced_sql, language="sql")
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("▶️ Execute Query"):
                st.info("Integration with your existing execute_enterprise_query function")
        
        with col2:
            if st.button("✏️ Edit SQL"):
                st.session_state.edit_advanced_mode = True
        
        with col3:
            if st.button("💾 Save Template"):
                st.info("Save as reusable template for similar analyses")
        
        with col4:
            if st.button("📊 Explain Query"):
                show_query_explanation(st.session_state.advanced_sql)

def show_query_explanation(sql_query):
    """Show detailed explanation of the SQL query"""
    
    st.markdown("#### 🔍 Query Explanation")
    
    # Analyze query components
    components = {
        'Tables Used': len(re.findall(r'FROM|JOIN', sql_query, re.IGNORECASE)),
        'Joins': len(re.findall(r'JOIN', sql_query, re.IGNORECASE)),
        'Filters': len(re.findall(r'WHERE|HAVING', sql_query, re.IGNORECASE)),
        'Aggregations': len(re.findall(r'GROUP BY|COUNT|SUM|AVG', sql_query, re.IGNORECASE)),
        'Calculations': len(re.findall(r'CASE WHEN', sql_query, re.IGNORECASE))
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        for key, value in list(components.items())[:2]:
            st.metric(key, value)
    
    with col2:
        for key, value in list(components.items())[2:4]:
            st.metric(key, value)
    
    with col3:
        for key, value in list(components.items())[4:]:
            st.metric(key, value)
    
    # Performance estimate
    complexity_score = sum(components.values())
    
    if complexity_score <= 3:
        performance = "⚡ Fast (< 5 seconds)"
        color = "green"
    elif complexity_score <= 7:
        performance = "⏳ Moderate (5-30 seconds)"
        color = "orange"
    else:
        performance = "🐌 Complex (30+ seconds)"
        color = "red"
    
    st.markdown(f"**Performance Estimate:** :{color}[{performance}]")

def main():
    """Main function for the Advanced Query Builder app"""
    
    st.set_page_config(
        page_title="Advanced Query Builder",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 Advanced Query Builder")
    st.markdown("*For Technical Business Users & Developer Learning*")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Query Builder Modes")
        
        st.markdown("""
        **📊 Business User**
        - Pre-built views
        - Simple recommendations
        
        **🔧 Technical Business**
        - Complex multi-table joins
        - Step-by-step breakdowns
        - Performance guidance
        
        **🎓 Developer Learning**
        - Educational SQL examples
        - Concept explanations
        - Progressive complexity
        
        **⚡ SQL Expert**
        - Full complexity
        - Optimization hints
        - Advanced patterns
        """)
    
    # Main interface
    render_advanced_query_ui()
    
    # Edit mode
    if st.session_state.get('edit_advanced_mode', False):
        st.markdown("### ✏️ Edit Advanced SQL")
        edited_sql = st.text_area(
            "Modify the SQL query:",
            value=st.session_state.get('advanced_sql', ''),
            height=300
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Update Query"):
                st.session_state.advanced_sql = edited_sql
                st.session_state.edit_advanced_mode = False
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel Edit"):
                st.session_state.edit_advanced_mode = False
                st.rerun()

if __name__ == "__main__":
    main()
