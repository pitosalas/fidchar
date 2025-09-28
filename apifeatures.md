## General Requirement

* use apis to certain web sites that provuide research on charities
* goal is to have an api that given an ein prepares a comprehesnive datastructure which will allow us to determine whether its a good one for me to support
* put key parameters into a yaml config file
* write this as a separate python module/package so that it can be incorporated into fidchar but also elsewhere
* Dont do any coding just study this document and prepare a comprehesnive to do list


### **1. ProPublica Nonprofit Explorer API (FREE - IMPLEMENT FIRST)**
- **URL**: `https://projects.propublica.org/nonprofits/api/v2/`
- **Endpoints**: 
  - Search: `/search.json?q={query}`
  - Organization: `/organizations/{ein}.json`
- **Key Fields**: `totrevenue`, `totfuncexpns`, `totprogrevexp`, `totadminexp`, `totfndrsexp`, `pct_compnsatncurrofcr`, `totassetsend`, `totliabend`, `tax_prd_yr`

### **2. IRS Tax Exempt Organization Search (FREE - IMPLEMENT SECOND)**
- **URL**: `https://www.irs.gov/charities-non-profits/tax-exempt-organization-search-bulk-data-downloads`
- **Downloads**:
  - Pub. 78 Data (tax-deductible eligible): CSV format
  - Auto-revocation list: CSV format
  - EO Business Master File Extract: CSV format by state
- **Key Fields**: EIN, tax-exempt status, revocation status, filing compliance

### **3. Charity Navigator API (FREE - IMPLEMENT THIRD)**
- **URL**: `https://developer.charitynavigator.org/`
- **Registration**: Required at developer portal
- **Key Fields**: Overall rating (1-4 stars), financial score, accountability score, advisory alerts

### **4. CharityAPI.org (LOW COST - IMPLEMENT FOURTH)**
- **URL**: `https://www.charityapi.org/`
- **Endpoint**: Lookup by EIN for real-time IRS status
- **Key Fields**: Current IRS standing, public charity status

### **5. Candid APIs (COMMERCIAL $6K+ - IMPLEMENT LAST)**
- **URL**: `https://candid.org/use-our-data/apis`
- **Key Fields**: Seal of Transparency, news alerts, compliance validation

## **Charity Evaluation Algorithm**

### **Core Financial Health Score (0-100 points)**
```python
def calculate_financial_score(filing_data):
    # Extract financial data from most recent filing
    total_expenses = filing_data.get('totfuncexpns', 0)
    program_expenses = filing_data.get('totprogrevexp', 0) 
    admin_expenses = filing_data.get('totadminexp', 0)
    fundraising_expenses = filing_data.get('totfndrsexp', 0)
    total_assets = filing_data.get('totassetsend', 0)
    total_liabilities = filing_data.get('totliabend', 0)
    
    # Calculate ratios
    program_ratio = program_expenses / total_expenses if total_expenses > 0 else 0
    admin_ratio = admin_expenses / total_expenses if total_expenses > 0 else 0
    fundraising_ratio = fundraising_expenses / total_expenses if total_expenses > 0 else 0
    net_assets = total_assets - total_liabilities
    
    # Score components (0-100 scale)
    program_score = min(40 * (program_ratio / 0.75), 40)  # 40 pts max, target 75%+
    admin_score = max(0, 20 * (0.15 - admin_ratio) / 0.15)  # 20 pts max, target <15%
    fundraising_score = max(0, 20 * (0.15 - fundraising_ratio) / 0.15)  # 20 pts max, target <15%
    stability_score = 20 if net_assets > 0 else 0  # 20 pts for positive net assets
    
    return program_score + admin_score + fundraising_score + stability_score
```

### **Multi-Year Trend Analysis (±20 points)**
```python
def calculate_trend_modifier(multi_year_filings):
    revenues = [filing.get('totrevenue', 0) for filing in multi_year_filings[:5]]
    
    # Revenue growth consistency (±10 points)
    growth_rates = [(revenues[i] - revenues[i+1]) / revenues[i+1] 
                   for i in range(len(revenues)-1) if revenues[i+1] > 0]
    
    if len(growth_rates) >= 3:
        avg_growth = sum(growth_rates) / len(growth_rates)
        volatility = sum(abs(rate - avg_growth) for rate in growth_rates) / len(growth_rates)
        
        growth_score = min(10, max(-10, avg_growth * 100))  # ±10 based on avg growth
        stability_score = max(-10, 10 - volatility * 50)    # Penalty for volatility
    else:
        growth_score = stability_score = 0
    
    return growth_score + stability_score
```

### **Compliance Check (Pass/Fail with -50 penalty)**
```python
def check_compliance(ein, irs_data):
    compliance_issues = []
    
    # Check if in Pub. 78 (tax-deductible eligible)
    if ein not in irs_data['pub78_eins']:
        compliance_issues.append("Not in Pub. 78 - donations may not be tax-deductible")
    
    # Check auto-revocation list
    if ein in irs_data['revoked_eins']:
        compliance_issues.append("Tax-exempt status revoked")
    
    # Check recent filing (within 3 years)
    if not has_recent_filing(ein, irs_data):
        compliance_issues.append("No recent Form 990 filing")
    
    return len(compliance_issues) == 0, compliance_issues
```

### **External Validation Bonus (0-45 points)**
```python
def calculate_external_validation(charity_nav_data, candid_data=None):
    bonus_points = 0
    
    # Charity Navigator rating
    if charity_nav_data:
        stars = charity_nav_data.get('rating', 0)
        bonus_points += stars * 5  # 5-20 points for 1-4 stars
        
        # No advisory alerts bonus
        if not charity_nav_data.get('advisory_alerts'):
            bonus_points += 5
    
    # Candid Seal of Transparency (if available)
    if candid_data and candid_data.get('transparency_seal'):
        bonus_points += 10
    
    # Recent negative news penalty (if available)
    if candid_data and candid_data.get('negative_news_alerts'):
        bonus_points -= 10
    
    return min(45, bonus_points)
```

### **Final Scoring Algorithm**
```python
def evaluate_charity(ein):
    # Step 1: Get ProPublica data
    propublica_data = get_propublica_data(ein)
    
    # Step 2: Calculate base financial score
    financial_score = calculate_financial_score(propublica_data['latest_filing'])
    
    # Step 3: Add trend analysis
    trend_modifier = calculate_trend_modifier(propublica_data['all_filings'])
    
    # Step 4: Check compliance
    compliance_pass, issues = check_compliance(ein, irs_data)
    compliance_penalty = 0 if compliance_pass else -50
    
    # Step 5: Add external validation
    charity_nav_data = get_charity_navigator_data(ein)
    validation_bonus = calculate_external_validation(charity_nav_data)
    
    # Final score
    total_score = financial_score + trend_modifier + validation_bonus + compliance_penalty
    
    # Grade assignment
    if total_score >= 90: grade = 'A'
    elif total_score >= 75: grade = 'B'
    elif total_score >= 60: grade = 'C'
    elif total_score >= 45: grade = 'D'
    else: grade = 'F'
    
    return {
        'total_score': total_score,
        'grade': grade,
        'financial_score': financial_score,
        'trend_modifier': trend_modifier,
        'validation_bonus': validation_bonus,
        'compliance_pass': compliance_pass,
        'compliance_issues': issues
    }
```

## **Implementation Order**

### **Phase 1: Basic System (Week 1)**
1. Implement ProPublica API client
2. Build core financial analysis functions
3. Create basic scoring algorithm
4. Test with known organizations

### **Phase 2: Add Compliance (Week 2)**
1. Download and process IRS bulk CSV files
2. Implement compliance checking functions
3. Add penalty system for non-compliant organizations
4. Integrate with existing scoring

### **Phase 3: Add Professional Ratings (Week 3)**
1. Register for Charity Navigator API
2. Implement external validation functions
3. Add bonus point system
4. Refine scoring weightings

### **Phase 4: Optimization (Week 4)**
1. Add CharityAPI.org for real-time verification
2. Implement error handling and data quality checks
3. Add batch processing capabilities
4. Validate algorithm against known good/bad charities

### **Phase 5: Enhancement (Future)**
1. Add Candid APIs when budget allows
2. Implement news sentiment analysis
3. Add sector-specific benchmarking
4. Create comparative ranking system

## **Data Processing Notes**
- Handle missing fields gracefully (use 0 or skip in calculations)
- Different form types (990, 990-EZ, 990-PF) may have different field names
- Implement caching for API calls to avoid rate limits
- Store processed data locally to enable historical analysis
- Account for inflation when comparing multi-year financial data