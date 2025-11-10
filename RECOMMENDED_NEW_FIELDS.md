# 990PF Data Analysis: Recommended New Fields to Extract

## Executive Summary

I analyzed 50+ IRS 990 and 990PF forms from your `irs_data` folder to identify valuable information that could enhance your grant finder application. The analysis found **282 grant entries** across **49 files**, with **46 unique grant-related fields** available.

## Current State

Your app currently extracts:
- Foundation name & EIN
- Recipient name
- Recipient address (city, state)
- Grant amount
- Grant purpose
- Tax period

## Recommended New Fields to Add

### 🔥 HIGH PRIORITY - Foundation-Level Information

These fields provide context about the foundations themselves, helping users assess foundation size, stability, and capacity:

#### 1. **Foundation Website** 
- **Benefit**: Direct links for users to learn more and potentially apply
- **Availability**: Found in 80% of 990PF files
- **XML Field**: `WebsiteAddressTxt`
- **Display**: Add as clickable link on foundation profile pages
- **Example**: "saintandrews.org", "www.lakewildwood.net"

#### 2. **Total Assets (End of Year)**
- **Benefit**: Shows foundation financial capacity/size
- **Availability**: 100% of 990PF files
- **XML Field**: `TotalAssetsEOYAmt` or `Form990TotalAssetsGrp/EOYAmt`
- **Display**: Show as "Total Assets: $2.8M" on foundation cards
- **Example Values**: $2,851,293 / $2,438,052 / $1,255,057

#### 3. **Fair Market Value of Assets**
- **Benefit**: True asset value (more accurate than book value)
- **Availability**: 100% of 990PF files  
- **XML Field**: `FMVAssetsEOYAmt`
- **Display**: "Asset Value: $3.1M"
- **Use Case**: Better indicator of foundation wealth than book value

#### 4. **Foundation Address (Full)**
- **Benefit**: Complete contact information for foundations
- **Availability**: 100% of files
- **XML Fields**: `AddressLine1Txt`, `CityNm`, `StateAbbreviationCd`, `ZIPCd`
- **Display**: Add to foundation detail page
- **Note**: Currently you only extract recipient addresses, not foundation addresses

#### 5. **Foundation Phone Number**
- **Benefit**: Direct contact for grant seekers
- **Availability**: 100% of files
- **XML Field**: `PhoneNum` (in BooksInCareOfDetail or Filer section)
- **Display**: "Contact: (617) 722-7626"

#### 6. **Formation Year**
- **Benefit**: Shows how established/mature the foundation is
- **Availability**: ~70% of files
- **XML Field**: `FormationYr`
- **Display**: "Established: 1968" or "Founded 45 years ago"
- **Example Values**: 1968, 1970, 2000

#### 7. **Foundation Type**
- **Benefit**: Distinguishes operating foundations from grant-making foundations
- **Availability**: 100% of 990PF files
- **XML Field**: `PrivateOperatingFoundationInd`
- **Display**: Badge showing "Private Foundation" vs "Operating Foundation"
- **Why Important**: Operating foundations typically don't make grants to others

### 🎯 HIGH PRIORITY - Grant-Level Information

These fields add valuable context to individual grants:

#### 8. **Recipient EIN/Tax ID**
- **Benefit**: 
  - Identify and track repeat grantees
  - Link to recipient's own 990 data
  - Verify recipient organization status
- **Availability**: Found in ~12% of grant entries (varies by foundation)
- **XML Field**: `RecipientTable.RecipientEIN` or `RecipientEIN`
- **Display**: Show on grant detail, link to IRS org lookup
- **Example Values**: "31-1728910", "94-1156347"

#### 9. **Recipient Foundation Status**
- **Benefit**: Shows if recipient is a 501(c)(3) public charity, private foundation, or other
- **Availability**: 88% of grant entries
- **XML Field**: `RecipientFoundationStatusTxt`
- **Display**: Badge/tag on grant entries
- **Example Values**: "PC" (Public Charity), "PF" (Private Foundation)
- **Why Important**: Helps grant seekers identify what types of orgs get funded

#### 10. **Recipient Relationship to Donor**
- **Benefit**: Transparency - shows grants to related parties
- **Availability**: 88% of grant entries
- **XML Field**: `RecipientRelationshipTxt`
- **Display**: Warning icon if not "NONE"
- **Example Values**: "NONE", "DIRECTOR", "FAMILY MEMBER"
- **Why Important**: Related-party grants may not be available to outside applicants

#### 11. **Cash vs Non-Cash Grant Amount**
- **Benefit**: Distinguishes cash grants from in-kind donations
- **Availability**: ~32% of grant entries explicitly separate this
- **XML Fields**: `CashGrantAmt`, `NonCashAssistanceAmt`, `NonCashAssistanceDesc`
- **Display**: Show split: "Cash: $50K, In-Kind: $10K (Food)"
- **Example**: One foundation gave $0 cash but $15K in food donations

#### 12. **IRS Section/Tax Classification**
- **Benefit**: Shows recipient's tax-exempt category
- **Availability**: ~10% of entries
- **XML Field**: `IRCSectionDesc`
- **Display**: "501(c)(3) Organization"
- **Example Values**: "501(C)(3)", "3", "501 (C) (3)"

### 📊 MEDIUM PRIORITY - Financial Context

#### 13. **Total Revenue & Expenses** (Foundation-level)
- **Benefit**: Shows foundation activity level beyond just assets
- **Availability**: 90%+ of 990PF files
- **XML Fields**: `TotalRevenueAmt`, `TotalExpensesAmt`
- **Display**: "Annual Revenue: $2.5M" / "Annual Expenses: $2.4M"
- **Use Case**: Calculate expense ratio, understand grant-making capacity

#### 14. **Investment Income** (Foundation-level)
- **Benefit**: Shows how foundation generates funds
- **Availability**: 90% of files
- **XML Fields**: `DividendsAndInterestFromSecAmt`, `NetGainSaleAstRevAndExpnssAmt`, `GrossInvestmentIncome509Amt`
- **Display**: "Investment Income: $215K (86% of revenue)"
- **Why Important**: High investment income = sustainable grant-making

#### 15. **Total Distributions** (Foundation-level, 990PF specific)
- **Benefit**: Total amount given in grants that year
- **Availability**: ~40% of 990PF files
- **XML Field**: `TotalDistributionAmt` or `QualifyingDistributions`
- **Display**: "Total Grants Paid: $1.2M"
- **Note**: This is already partially calculated in your aggregation, but having the official number is better

#### 16. **Distributable Amount** (990PF specific)
- **Benefit**: Minimum amount foundation must distribute (5% rule)
- **Availability**: ~40% of 990PF files
- **XML Field**: `DistributableAmountAmt`
- **Display**: "Required Distribution: $150K"
- **Why Important**: Shows if foundation is meeting legal requirements

#### 17. **Undistributed Income** (990PF specific)
- **Benefit**: Shows if foundation has excess income that must be distributed
- **Availability**: ~40% of 990PF files
- **XML Field**: `UndistributedIncomeAmt`
- **Display**: Warning if high: "Foundation has $500K to distribute"

### 📋 MEDIUM PRIORITY - Enhanced Discovery

#### 18. **Mission Statement / Primary Purpose**
- **Benefit**: Helps grant seekers understand foundation focus
- **Availability**: ~40% of files
- **XML Fields**: `PrimaryExemptPurposeTxt`, `ActivityOrMissionDesc`, `MissionDesc`
- **Display**: Show on foundation profile page
- **Examples**: 
  - "Providing emergency care and transportation for residents"
  - "Promotion of civil and religious freedom through television"
  - "Community service membership organization"

#### 19. **Officer/Director Information** (Foundation-level)
- **Benefit**: Key contacts and leadership transparency
- **Availability**: Most files have this
- **XML Fields**: `OfficerDirectorTrusteeEmplGrp/*`, including:
  - `PersonNm`: Name
  - `TitleTxt`: Title (President, Secretary, etc.)
  - `CompensationAmt`: Compensation
  - `AverageHoursPerWeekRt`: Time commitment
- **Display**: "Leadership" section with names and titles
- **Why Important**: Shows if foundation has professional staff vs all-volunteer

#### 20. **Legal Domicile State** (Foundation-level)
- **Benefit**: Shows where foundation is legally registered
- **Availability**: High
- **XML Field**: `LegalDomicileStateCd`
- **Display**: "Registered in: California"
- **Use Case**: Some foundations only give to orgs in their home state

### 🔍 LOWER PRIORITY - Nice to Have

#### 21. **Application Process Information** (990PF specific)
- **Benefit**: Grant application guidelines
- **Availability**: Rare (~2% explicitly)
- **XML Fields**: `ApplicationSubmissionInfoGrp/*` including:
  - `FormAndInfoAndMaterialsTxt`
  - `SubmissionDeadlinesTxt`
  - `RestrictionsOnAwardsTxt`
- **Display**: Dedicated "How to Apply" section
- **Note**: Most show "SEE FOOTNOTE" so limited usefulness

#### 22. **Valuation Method** (Grant-level)
- **Benefit**: How non-cash grants were valued
- **Availability**: ~10% of grants
- **XML Field**: `ValuationMethodUsedDesc`
- **Display**: Show for non-cash grants
- **Example Values**: "CASH", "ACTUAL COST", "Book Value"

## Implementation Priority

### Phase 1 (Quick Wins - Highest User Value)
1. Foundation Website (easy link out)
2. Total Assets (shows foundation size)
3. Foundation Address & Phone (complete contact info)
4. Recipient Foundation Status (better grant filtering)
5. Formation Year (foundation age/maturity)

### Phase 2 (Enhanced Grant Data)
6. Recipient EIN (tracking repeat grantees)
7. Relationship to Donor (transparency)
8. Cash vs Non-Cash split
9. Foundation Type (operating vs grant-making)

### Phase 3 (Financial Analysis)
10. Total Revenue/Expenses
11. Investment Income
12. Distribution Requirements (990PF specific)
13. Officer/Director information

### Phase 4 (Discovery & Context)
14. Mission Statement
15. Legal Domicile State
16. IRS Section Classification

## Data Quality Notes

- **990 vs 990PF**: Your data contains mostly 990 (public charity) forms with some 990PF (private foundation) forms mixed in
  - Only ~10% are true 990PF forms
  - 990PF-specific fields (distributions, qualifying distributions) only in PF forms
  - Most other fields available in both form types

- **Field Availability**: 
  - Basic info: 90-100% availability
  - Financial info: 80-100% availability  
  - Specialized fields: 10-40% availability
  - Grant recipient details vary widely by foundation

- **Data Consistency**: 
  - Field names vary slightly across years
  - Some foundations provide minimal data
  - Consider null/missing data handling

## Technical Extraction Notes

1. **XML Namespace**: All fields use IRS efile namespace: `{http://www.irs.gov/efile}`
2. **Multiple Paths**: Some fields exist at different XML paths (e.g., phone numbers in multiple places)
3. **Grant Tables**: Grants can appear as:
   - `GrantOrContributionPdDuringYrGrp` (990PF)
   - `RecipientTable` (Schedule I)
   - Multiple formats exist
4. **Business Names**: Often nested as `BusinessNameLine1Txt` + `BusinessNameLine2Txt`

## Database Schema Suggestions

### New Foundation Table Columns
```sql
foundation_website VARCHAR(255)
foundation_address VARCHAR(255)
foundation_city VARCHAR(100)
foundation_state VARCHAR(2)
foundation_zip VARCHAR(10)
foundation_phone VARCHAR(20)
formation_year INTEGER
total_assets_eoy BIGINT
fair_market_value BIGINT
total_revenue BIGINT
total_expenses BIGINT
investment_income BIGINT
is_operating_foundation BOOLEAN
primary_purpose TEXT
legal_domicile_state VARCHAR(2)
```

### New Grant Table Columns
```sql
recipient_ein VARCHAR(20)
recipient_foundation_status VARCHAR(10)  -- PC, PF, etc.
recipient_relationship VARCHAR(100)
cash_amount BIGINT
non_cash_amount BIGINT
non_cash_description TEXT
recipient_irc_section VARCHAR(50)
```

### New Officer Table
```sql
foundation_ein VARCHAR(20)
officer_name VARCHAR(200)
officer_title VARCHAR(100)
compensation BIGINT
hours_per_week DECIMAL(4,2)
tax_period VARCHAR(10)
```

## UI/UX Enhancement Ideas

1. **Foundation Card Enhancements**:
   - Asset size badge ("$1M-$10M")
   - Website icon/link
   - "Established YYYY" label
   - Operating vs Grant-making indicator

2. **Grant Detail Enhancements**:
   - Recipient org type badge
   - Related party warning icon
   - Cash/in-kind split visualization
   - Link to recipient's profile (if in your data)

3. **New Filter Options**:
   - Foundation asset size ranges
   - Foundation age (established date)
   - Operating vs grant-making
   - Exclude related-party grants
   - Cash-only grants

4. **New Sort Options**:
   - By foundation total assets
   - By foundation age
   - By grant recency

5. **Foundation Profile Page New Sections**:
   - "About" (mission, formation year, type)
   - "Contact" (address, phone, website)
   - "Financials" (assets, revenue, expenses)
   - "Leadership" (officers/directors)
   - "Grant Requirements" (if available)

## Example Enhanced Display

```
╔════════════════════════════════════════════════════════════════╗
║ SMITH FAMILY FOUNDATION                                   🔗   ║
║ EIN: 12-3456789  •  Est. 1995  •  Private Foundation          ║
║ Pittsburgh, PA  •  (412) 555-1234                              ║
╠════════════════════════════════════════════════════════════════╣
║ Total Assets: $2.8M  •  Annual Grants: ~$125K                  ║
║ Focus: Education, Youth Development                            ║
╠════════════════════════════════════════════════════════════════╣
║ Recent Grants (2024):                                          ║
║   • Boys & Girls Club - $75K 💰 [501(c)(3) PC]                ║
║     Purpose: Youth programming                                 ║
║   • Local School District - $50K 💰 [Government]              ║
║     Purpose: STEM education equipment                          ║
╚════════════════════════════════════════════════════════════════╝
```

## Next Steps

1. **Review & Prioritize**: Choose which fields to implement first based on user needs
2. **Update Extraction Script**: Modify your XML parsing to capture new fields
3. **Database Migration**: Add new columns to your database
4. **Update CSV Generation**: Include new fields in your data export
5. **Update UI**: Design and implement enhanced displays
6. **Testing**: Verify data quality across your full dataset

## Analysis Scripts Created

The following Python scripts were created during this analysis and are available in your `grant_finder` directory:

1. `analyze_990pf.py` - Broad structure analysis
2. `analyze_990pf_detailed.py` - Deep 990PF field analysis  
3. `analyze_grant_fields.py` - Grant-specific field analysis

You can run these scripts on different subsets of your data to verify field availability as your dataset grows.

---

**Total Analysis**: 50 files, 282 grants, 990+ unique XML paths discovered
**Key Finding**: You're currently extracting ~6 fields but 40+ valuable fields are available
**Biggest Opportunities**: Foundation financials, contact info, and grant relationship data

