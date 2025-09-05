# User Personas for Athena Query Generator

## Primary User Personas

### Persona 1: Business Analyst (Sarah)
**Role:** Business Analyst  
**Technical Level:** Intermediate  
**Experience:** 3-5 years in data analysis  

**Characteristics:**
- Understands business requirements but limited SQL knowledge
- Needs to generate reports and insights quickly
- Values transparency in how data is retrieved
- Wants to learn and understand the underlying queries

**Goals:**
- Generate accurate business reports without writing SQL
- Understand how data is being queried for validation
- Create ad-hoc analyses for stakeholder requests
- Learn SQL concepts through generated examples

**Pain Points:**
- Dependent on IT/Data teams for complex queries
- Long turnaround times for data requests
- Difficulty validating query accuracy without SQL knowledge
- Limited ability to modify existing reports

**Use Cases:**
- Monthly sales performance analysis
- Customer segmentation reports
- Inventory trend analysis
- Cross-departmental data requests

---

### Persona 2: Department Manager (Michael)
**Role:** Department Manager (Sales/Marketing/Operations)  
**Technical Level:** Beginner  
**Experience:** 10+ years in business, minimal technical background  

**Characteristics:**
- Focused on business outcomes and KPIs
- Needs quick answers to business questions
- Prefers simple, intuitive interfaces
- Values speed and accuracy over technical details

**Goals:**
- Get immediate answers to business questions
- Access real-time data for decision making
- Generate executive-level reports and dashboards
- Self-serve data needs without technical dependencies

**Pain Points:**
- No SQL or technical query knowledge
- Frustrated by delays in getting data insights
- Needs data in business-friendly formats
- Requires confidence in data accuracy

**Use Cases:**
- Weekly team performance reviews
- Budget planning and forecasting
- Competitive analysis reports
- Executive dashboard creation

---

## Secondary User Personas

### Persona 3: Advanced Business User (Jennifer)
**Role:** Senior Business Analyst/Data-Savvy Manager  
**Technical Level:** Advanced  
**Experience:** 5+ years, some SQL knowledge  

**Characteristics:**
- Has basic to intermediate SQL skills
- Wants to review and potentially modify generated queries
- Values control and customization options
- Acts as a bridge between business and technical teams

**Goals:**
- Validate and optimize generated SQL queries
- Customize queries for specific business needs
- Mentor other users on data analysis best practices
- Ensure data governance and compliance

**Pain Points:**
- Generated queries may not always match exact requirements
- Needs ability to fine-tune queries for performance
- Wants to maintain query standards and best practices

**Use Cases:**
- Complex multi-table analysis
- Query optimization and validation
- Training other business users
- Data quality auditing

---

## User Journey Mapping

### Common User Flow:
1. **Access Application** → Authentication via existing AWS/SSO
2. **Ask Business Question** → Natural language input
3. **Review Generated Query** → Understand what data will be retrieved
4. **Execute Query** → Run against Athena database
5. **Analyze Results** → View formatted results and insights
6. **Export/Share** → Save or distribute findings

### Success Metrics:
- Time to insight (from question to answer)
- Query accuracy and relevance
- User adoption and engagement
- Reduction in IT support requests
- User satisfaction scores
