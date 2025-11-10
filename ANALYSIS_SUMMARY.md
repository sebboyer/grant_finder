# 990PF Data Analysis - Quick Summary

## What I Did

I analyzed **50 IRS forms** (mix of 990 and 990PF files) from your `irs_data` folder using Python scripts to:
1. Identify all available fields in the XML files
2. Categorize them by usefulness
3. Check how often each field appears
4. Provide specific recommendations

## Key Statistics

```
📊 Files Analyzed:        50 files
📋 Grant Entries Found:   282 individual grants
🗂️  Unique Fields Found:   990+ XML paths
💎 High-Value Fields:     22 recommended for extraction
✅ Files with Grants:     49 out of 50 (98%)
```

## Current vs. Potential Data Extraction

### What You're Extracting Now ✅
- Foundation name
- Foundation EIN  
- Recipient name
- Recipient city
- Recipient state
- Grant amount
- Grant purpose
- Tax period

**Total: 8 fields per grant**

### What's Available but NOT Extracted 🎯

#### Foundation Information (22 new fields available):
- ✨ **Foundation website** (80% of files)
- ✨ **Total assets** (100% of files) 
- ✨ **Fair market value** (100% of files)
- ✨ **Foundation full address** (100% of files)
- ✨ **Foundation phone** (100% of files)
- ✨ **Formation year** (70% of files)
- ✨ **Foundation type** (operating vs grant-making)
- Total revenue & expenses
- Investment income
- Distribution requirements (990PF specific)
- Mission statement
- Officers/Directors with compensation
- Legal domicile state

#### Grant-Level Enhancements (9 new fields available):
- ✨ **Recipient EIN** (12% of grants - varies by foundation)
- ✨ **Recipient organization type** (88% of grants)
  - Example: "PC" = Public Charity, "PF" = Private Foundation
- ✨ **Relationship to donor** (88% of grants)
  - Flags related-party grants
- ✨ **Cash vs non-cash amounts** (32% of grants)
- IRS section classification
- Multiple address lines
- Valuation methods
- Grant type categorization

**Potential: 8 → 39 fields (5x increase)**

## Top 10 High-Impact Recommendations

### 🥇 Must-Have (Implement First)

1. **Foundation Website** 
   - Quick link for users to learn more
   - Available in 80% of files
   - Easy to implement

2. **Total Assets (End of Year)**
   - Shows foundation size/capacity  
   - Available in 100% of files
   - Critical for filtering by foundation size
   - Example: "$2.8M"

3. **Foundation Contact Info** (Address + Phone)
   - Complete foundation contact details
   - Available in 100% of files
   - Currently you only show recipient addresses

4. **Recipient Organization Type**
   - Shows if recipient is public charity, private foundation, etc.
   - Available in 88% of grant entries
   - Great for filtering

5. **Formation Year**
   - Shows how established the foundation is
   - Available in 70% of files
   - Display as "Est. 1968" or "Founded 45 years ago"

### 🥈 High Value (Implement Second)

6. **Foundation Type** (Operating vs Grant-Making)
   - Available in 100% of 990PF files
   - Critical: Operating foundations typically don't make grants
   - Saves users time filtering

7. **Recipient EIN**
   - Track repeat grantees
   - Verify organizations
   - Available in ~12% (varies by foundation)
   - When available, very valuable

8. **Relationship to Donor**
   - Transparency: shows grants to related parties
   - Available in 88% of entries
   - Example: "NONE" vs "DIRECTOR"
   - Helps identify truly available grants

9. **Total Revenue/Expenses**
   - Shows foundation activity level
   - Available in 90%+ of files
   - Calculate giving capacity

10. **Cash vs Non-Cash Amounts**
    - Distinguish cash grants from in-kind
    - Available in 32% of entries
    - Example: "Cash: $50K, Food: $10K"

## Sample Enhanced Grant Display

### Before (Current):
```
Foundation: SMITH FAMILY FOUNDATION
Recipient: Boys & Girls Club of Boston
Location: Boston, MA
Amount: $75,000
Purpose: General Operating
```

### After (With New Fields):
```
🏛️ SMITH FAMILY FOUNDATION
   EIN: 12-3456789  |  Est. 1995  |  Private Foundation
   Assets: $2.8M  |  Pittsburgh, PA
   📞 (412) 555-1234  🌐 smithfoundation.org
   
   💰 Recent Grant:
   ├─ Recipient: Boys & Girls Club of Boston
   ├─ Type: 501(c)(3) Public Charity 
   ├─ Location: Boston, MA
   ├─ Amount: $75,000 (Cash Grant)
   ├─ Purpose: General Operating
   ├─ Relationship: None
   └─ Tax Period: 2024
```

## What Makes These Fields Valuable?

### For Grant Seekers:
- **Foundation Website** → Apply directly
- **Total Assets** → Know if foundation size matches their needs
- **Formation Year** → Target established vs new foundations
- **Contact Info** → Reach out for questions
- **Foundation Type** → Don't waste time on operating foundations
- **Recipient Type** → See what type of orgs get funded
- **Relationship Flags** → Know if grants go to insiders

### For Your App:
- **Better Filtering** → By asset size, foundation age, grant type
- **Better Sorting** → By foundation wealth, activity level
- **Better Discovery** → Match grant seekers to right foundations
- **Competitive Advantage** → More data than other grant databases
- **User Trust** → Transparency about related-party grants

## New Features You Could Build

With the additional data, you could add:

### Filters:
- ✅ Foundation asset size ranges ($100K-$1M, $1M-$10M, etc.)
- ✅ Foundation age (Established <5yr, 5-20yr, 20+yr)
- ✅ Grant type (Cash only, includes in-kind)
- ✅ Exclude related-party grants
- ✅ Only foundations that accept outside applications

### Sorting:
- ✅ By foundation total assets
- ✅ By foundation age (newest/oldest)
- ✅ By average grant size (already have)
- ✅ By foundation activity (total annual grants)

### Analytics:
- ✅ "Similar foundations" (by asset size, location, focus)
- ✅ "Repeat grantees" tracking (via recipient EIN)
- ✅ Foundation health indicators (assets, distributions)
- ✅ Grant trends over time (if you have multiple years)

### Foundation Profile Enhancements:
- ✅ Contact section with website, phone, address
- ✅ About section with mission and history
- ✅ Financials section with assets, revenue, expenses
- ✅ Leadership section with officers and directors
- ✅ Grant requirements (if available in data)

## Data Quality Insights

### Good News ✅
- 98% of files contain grant data
- Basic info fields have 90-100% availability
- Grant recipient data is consistently structured
- Phone, address, website widely available

### Watch Outs ⚠️
- Only ~10% of your files are true 990PF forms (rest are 990)
- 990PF-specific fields (distribution requirements) only in PF files
- Recipient EIN only provided by ~12% of foundations
- Some fields show "SEE FOOTNOTE" instead of actual data
- Field names vary slightly across form years

### Recommendations 💡
- Prioritize fields with 70%+ availability first
- Handle missing data gracefully (show "N/A" vs hiding)
- Consider collecting multiple years for trend analysis
- Validate EINs when provided (9 digits, check format)

## Implementation Effort

### Easy (1-2 hours):
- Foundation website
- Foundation contact info (address, phone)
- Formation year
- Total assets

### Medium (2-4 hours):
- Recipient organization type
- Foundation type
- Relationship to donor
- Revenue/expense data

### Complex (4-8 hours):
- Cash vs non-cash split (multiple field formats)
- Officer/director extraction (repeating groups)
- Mission statement (multiple possible fields)
- Distribution requirements (990PF-specific calculations)

## Files Created

I created 3 Python analysis scripts in your `grant_finder` folder:

1. **`analyze_990pf.py`**
   - Broad XML structure analysis
   - Identifies all unique paths in files
   - Categorizes by type

2. **`analyze_990pf_detailed.py`**
   - Deep dive into 990PF-specific fields
   - Extracts sample foundation data
   - Shows field availability statistics

3. **`analyze_grant_fields.py`**
   - Grant-specific field analysis
   - Shows example grant entries
   - Categorizes grant-related fields

You can run these on new data batches to verify field availability.

## Next Steps

1. **Review Recommendations** → Prioritize which fields to add
2. **Choose Implementation Phase** → Start with Quick Wins
3. **Update Extraction Logic** → Modify your XML parser
4. **Update Database** → Add new columns
5. **Update UI** → Display new information
6. **Test** → Verify across full dataset

## Questions to Consider

Before implementing:
- Which features matter most to your target users?
- Do you want foundation-level OR grant-level enhancements first?
- Should you filter out operating foundations (don't make grants)?
- How to handle missing data in the UI?
- Will you retroactively extract data from existing files?

---

**Bottom Line**: You're currently using ~10% of the available data. Adding even just the top 10 fields would make your app significantly more valuable for grant seekers.

Let me know which fields you'd like to implement, and I can help you update the extraction code! 🚀

