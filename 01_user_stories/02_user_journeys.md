# Core User Journeys for Athena Query Generator

## Journey 1: First-Time User Onboarding

**User:** Department Manager (Michael)  
**Goal:** Get first business insight from the application

### Steps:
1. **Authentication** → Login via existing AWS SSO
2. **Welcome & Guidance** → Brief tutorial on how to ask questions
3. **First Query** → "Show me last month's sales by region"
4. **Query Review** → See generated SQL with plain English explanation
5. **Execute & Results** → View formatted results in business-friendly format
6. **Success Confirmation** → Export results or save query for future use

**Success Criteria:**
- User completes first query within 5 minutes
- Results are accurate and formatted appropriately
- User understands what data was retrieved

---

## Journey 2: Regular Business Analysis

**User:** Business Analyst (Sarah)  
**Goal:** Generate weekly performance report

### Steps:
1. **Quick Access** → Login and navigate to saved queries or start new
2. **Natural Language Query** → "Compare this week's sales to last week by product category"
3. **Query Validation** → Review generated SQL for accuracy
4. **Refinement** → Modify query if needed: "Also include profit margins"
5. **Execution** → Run query against Athena database
6. **Analysis** → Review results, identify trends and insights
7. **Documentation** → Save query with business context for team use
8. **Sharing** → Export to Excel or share via dashboard

**Success Criteria:**
- Query generates accurate comparative analysis
- Results include all requested metrics
- Query can be saved and reused
- Export functionality works seamlessly

---

## Journey 3: Advanced Query Customization

**User:** Advanced Business User (Jennifer)  
**Goal:** Create complex multi-table analysis with custom modifications

### Steps:
1. **Complex Question** → "Show customer lifetime value by acquisition channel with churn analysis"
2. **Initial SQL Generation** → Review auto-generated multi-table query
3. **SQL Editing** → Modify query to add specific business logic
4. **Validation** → Test query with sample data
5. **Optimization** → Adjust for performance and cost efficiency
6. **Documentation** → Add comments and business context
7. **Template Creation** → Save as reusable template for team
8. **Knowledge Sharing** → Train other users on the analysis approach

**Success Criteria:**
- Generated SQL provides good starting point for complex analysis
- User can successfully modify and optimize query
- Query performs efficiently on large datasets
- Template can be reused by other team members

---

## Journey 4: Error Recovery and Learning

**User:** Business Analyst (Sarah)  
**Goal:** Resolve query issues and learn from mistakes

### Steps:
1. **Ambiguous Query** → "Show me the best performing products"
2. **Clarification Request** → System asks: "Best performing by sales, profit, or units sold?"
3. **Refinement** → "Best performing by sales revenue in the last quarter"
4. **Query Generation** → Review generated SQL
5. **Error Detection** → Notice query doesn't include expected filters
6. **Feedback** → "This should only include active products"
7. **Query Adjustment** → System updates SQL with additional filter
8. **Learning** → User understands how to be more specific in future queries

**Success Criteria:**
- System provides helpful clarification questions
- User can iteratively refine queries
- Error messages are clear and actionable
- User learns to ask better questions over time

---

## Journey 5: Compliance and Audit Trail

**User:** Advanced Business User (Jennifer)  
**Goal:** Ensure data access compliance and maintain audit trail

### Steps:
1. **Sensitive Data Query** → Request involving customer PII
2. **Access Validation** → System checks user permissions for sensitive data
3. **Data Masking** → Apply appropriate masking for PII fields
4. **Query Logging** → Record query details for audit purposes
5. **Results Review** → Verify masked data meets compliance requirements
6. **Audit Documentation** → Generate audit trail report
7. **Approval Workflow** → Route sensitive queries through approval process if required

**Success Criteria:**
- Sensitive data is properly masked or access denied
- All queries are logged with user, timestamp, and data accessed
- Compliance requirements are automatically enforced
- Audit trails are easily accessible for review

---

## Cross-Journey Success Metrics

### Performance Metrics:
- **Time to First Insight:** < 2 minutes for simple queries
- **Query Accuracy:** > 95% of generated queries produce expected results
- **User Adoption:** 80% of target users actively using within 30 days
- **Self-Service Rate:** 70% reduction in IT data request tickets

### User Experience Metrics:
- **Ease of Use:** Average user rating > 4.0/5.0
- **Learning Curve:** New users productive within first session
- **Error Recovery:** < 3 iterations to get desired results
- **Feature Discovery:** Users utilize 80% of core features within 30 days

### Technical Metrics:
- **Query Performance:** Average execution time < 30 seconds
- **System Availability:** 99.5% uptime during business hours
- **Data Accuracy:** 100% consistency with source systems
- **Security Compliance:** Zero unauthorized data access incidents
