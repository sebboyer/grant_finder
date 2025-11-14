# Normalized IRS Data Schema

This document describes the normalized database structure created from the raw IRS 990PF data.

## Overview

The transformation script (`scripts/transform_to_normalized_schema.py`) has successfully converted the raw IRS data into four normalized tables ready for import into Supabase or any other database system.

## Generated Files

- **foundations_normalized.csv** (779 KB, 2,292 records)
- **grants_normalized.csv** (4.9 MB, 20,998 records)
- **leaders_normalized.csv** (1.0 MB, 6,622 records)
- **recipients_normalized.csv** (2.8 MB, 18,473 unique recipients)

## Table Schemas

### FOUNDATIONS Table
Primary table containing foundation information per tax filing period.

**Primary Key:** `foundation_id` (UUID)

**Columns:**
- `foundation_id` - Unique identifier (UUID)
- `ein` - IRS Employer Identification Number
- `organization_name` - Foundation legal name
- `tax_period_begin`, `tax_period_end` - Tax filing period dates
- `address_line1`, `address_line2`, `city`, `state`, `zip` - Contact address
- `phone`, `website` - Contact information
- `formation_year` - Year foundation was established
- `legal_domicile_state` - State of incorporation
- `total_assets_boy` - Total assets beginning of year
- `total_assets_eoy` - Total assets end of year
- `total_liabilities_eoy` - Total liabilities end of year
- `net_assets_eoy` - Net assets end of year
- `fair_market_value_eoy` - Fair market value end of year
- `total_revenue` - Total revenue for the period
- `total_expenses` - Total expenses for the period
- `investment_income` - Investment income
- `distributable_amount` - Amount required to distribute
- `total_distributions` - Total distributions made
- `undistributed_income` - Income not yet distributed
- `is_private_operating_foundation` - Boolean indicator
- `is_501c3` - Boolean indicator for 501(c)(3) status
- `mission_description` - Foundation mission statement
- `leader_ids` - JSON array of leader UUIDs (references LEADERS table)
- `source_file` - Original IRS XML filename

**Relationships:**
- One-to-Many with GRANTS (via foundation_id)
- One-to-Many with LEADERS (via foundation_id and leader_ids array)

### GRANTS Table
Individual grant awards made by foundations.

**Primary Key:** `grant_id` (UUID)
**Foreign Keys:** `foundation_id`, `recipient_id`

**Columns:**
- `grant_id` - Unique identifier (UUID)
- `foundation_id` - References FOUNDATIONS table
- `recipient_id` - References RECIPIENTS table
- `grant_amount` - Total grant amount
- `cash_grant_amount` - Cash portion of grant
- `non_cash_grant_amount` - Non-cash portion of grant
- `grant_purpose` - Description of grant purpose
- `recipient_relationship` - Relationship to foundation (e.g., NONE, RELATED)
- `recipient_foundation_status` - Type of recipient (e.g., PC = Public Charity)
- `recipient_irc_section` - IRS code section
- `non_cash_description` - Description of non-cash assets
- `valuation_method` - How non-cash assets were valued
- **Denormalized fields** (for easier querying):
  - `recipient_name` - Name of grant recipient
  - `recipient_ein` - Recipient's EIN (if available)
  - `recipient_city` - Recipient's city
  - `recipient_state` - Recipient's state
- `tax_period_end` - Tax period when grant was awarded
- `source_file` - Original IRS XML filename

**Relationships:**
- Many-to-One with FOUNDATIONS
- Many-to-One with RECIPIENTS

### LEADERS Table
Officers, directors, trustees, and key employees of foundations.

**Primary Key:** `leader_id` (UUID)
**Foreign Key:** `foundation_id`

**Columns:**
- `leader_id` - Unique identifier (UUID)
- `foundation_id` - References FOUNDATIONS table
- `person_name` - Full name
- `title` - Position/role (e.g., President, Treasurer)
- `compensation` - Base compensation
- `benefits` - Benefits received
- `other_compensation` - Other forms of compensation
- `hours_per_week` - Hours worked per week
- `is_officer` - Boolean indicator
- `is_director` - Boolean indicator
- `is_trustee` - Boolean indicator
- `is_key_employee` - Boolean indicator
- `tax_period_end` - Tax period when they held this role
- `source_file` - Original IRS XML filename

**Relationships:**
- Many-to-One with FOUNDATIONS

**Note:** The same person can appear multiple times if they hold multiple positions or serve across different tax periods.

### RECIPIENTS Table
Unique grant recipients (organizations and individuals).

**Primary Key:** `recipient_id` (UUID)

**Columns:**
- `recipient_id` - Unique identifier (UUID)
- `recipient_name` - Organization or individual name
- `recipient_ein` - EIN (if available)
- `address_line1`, `address_line2` - Street address
- `city`, `state`, `zip` - Location
- `country` - Country (usually US)
- `grant_ids` - JSON array of grant UUIDs (references GRANTS table)

**Relationships:**
- One-to-Many with GRANTS (via grant_ids array)

**Deduplication Logic:**
Recipients are considered unique based on the combination of:
- Name (normalized, uppercase)
- EIN (if available)
- City and State

This handles cases where the same organization receives multiple grants.

## Data Statistics

### Validation Results
✅ **All source records successfully transformed:**
- Source foundations: 2,292 → Output foundations: 2,292 (100%)
- Source grants: 20,998 → Output grants: 20,998 (100%)
- Source officers: 6,622 → Output leaders: 6,622 (100%)
- Unique recipients identified: 18,473

✅ **No orphaned records:**
- 0 grants without matching foundation
- 0 leaders without matching foundation

✅ **Sample validation passed:**
- Foundation "PAUL & RUTH SCHULTZ FDN AGY"
  - Foundation ID: 2d078947-1559-45eb-8da5-d410db663b5a
  - 30 related grants found
  - 4 related leaders found
  - All leader IDs properly linked

## Importing to Supabase

### Step 1: Create Tables
Use the following SQL to create tables in Supabase:

```sql
-- FOUNDATIONS table
CREATE TABLE foundations (
    foundation_id UUID PRIMARY KEY,
    ein TEXT,
    organization_name TEXT,
    tax_period_begin DATE,
    tax_period_end DATE,
    address_line1 TEXT,
    address_line2 TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    phone TEXT,
    website TEXT,
    formation_year TEXT,
    legal_domicile_state TEXT,
    total_assets_boy NUMERIC,
    total_assets_eoy NUMERIC,
    total_liabilities_eoy NUMERIC,
    net_assets_eoy NUMERIC,
    fair_market_value_eoy NUMERIC,
    total_revenue NUMERIC,
    total_expenses NUMERIC,
    investment_income NUMERIC,
    distributable_amount NUMERIC,
    total_distributions NUMERIC,
    undistributed_income NUMERIC,
    is_private_operating_foundation BOOLEAN,
    is_501c3 BOOLEAN,
    mission_description TEXT,
    leader_ids JSONB,
    source_file TEXT
);

-- RECIPIENTS table
CREATE TABLE recipients (
    recipient_id UUID PRIMARY KEY,
    recipient_name TEXT,
    recipient_ein TEXT,
    address_line1 TEXT,
    address_line2 TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    country TEXT,
    grant_ids JSONB
);

-- GRANTS table
CREATE TABLE grants (
    grant_id UUID PRIMARY KEY,
    foundation_id UUID REFERENCES foundations(foundation_id),
    recipient_id UUID REFERENCES recipients(recipient_id),
    grant_amount NUMERIC,
    cash_grant_amount NUMERIC,
    non_cash_grant_amount NUMERIC,
    grant_purpose TEXT,
    recipient_relationship TEXT,
    recipient_foundation_status TEXT,
    recipient_irc_section TEXT,
    non_cash_description TEXT,
    valuation_method TEXT,
    recipient_name TEXT,
    recipient_ein TEXT,
    recipient_city TEXT,
    recipient_state TEXT,
    tax_period_end DATE,
    source_file TEXT
);

-- LEADERS table
CREATE TABLE leaders (
    leader_id UUID PRIMARY KEY,
    foundation_id UUID REFERENCES foundations(foundation_id),
    person_name TEXT,
    title TEXT,
    compensation NUMERIC,
    benefits NUMERIC,
    other_compensation NUMERIC,
    hours_per_week NUMERIC,
    is_officer BOOLEAN,
    is_director BOOLEAN,
    is_trustee BOOLEAN,
    is_key_employee BOOLEAN,
    tax_period_end DATE,
    source_file TEXT
);

-- Indexes for better query performance
CREATE INDEX idx_grants_foundation_id ON grants(foundation_id);
CREATE INDEX idx_grants_recipient_id ON grants(recipient_id);
CREATE INDEX idx_leaders_foundation_id ON leaders(foundation_id);
CREATE INDEX idx_foundations_ein ON foundations(ein);
CREATE INDEX idx_recipients_name ON recipients(recipient_name);
CREATE INDEX idx_grants_amount ON grants(grant_amount);
```

### Step 2: Import Data
1. In Supabase Dashboard, go to Table Editor
2. Import CSVs in this order (to respect foreign key constraints):
   1. `foundations_normalized.csv` → foundations table
   2. `recipients_normalized.csv` → recipients table
   3. `grants_normalized.csv` → grants table
   4. `leaders_normalized.csv` → leaders table

### Step 3: Configure Row Level Security (Optional)
If you want public read access:

```sql
-- Enable RLS
ALTER TABLE foundations ENABLE ROW LEVEL SECURITY;
ALTER TABLE grants ENABLE ROW LEVEL SECURITY;
ALTER TABLE leaders ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipients ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Public foundations read" ON foundations FOR SELECT USING (true);
CREATE POLICY "Public grants read" ON grants FOR SELECT USING (true);
CREATE POLICY "Public leaders read" ON leaders FOR SELECT USING (true);
CREATE POLICY "Public recipients read" ON recipients FOR SELECT USING (true);
```

## Example Queries

### Find all grants from a specific foundation
```sql
SELECT g.*, r.recipient_name, r.city, r.state
FROM grants g
JOIN recipients r ON g.recipient_id = r.recipient_id
WHERE g.foundation_id = '2d078947-1559-45eb-8da5-d410db663b5a'
ORDER BY g.grant_amount DESC;
```

### Get foundation details with leaders
```sql
SELECT 
    f.organization_name,
    f.total_assets_eoy,
    f.city,
    f.state,
    json_agg(json_build_object(
        'name', l.person_name,
        'title', l.title,
        'compensation', l.compensation
    )) as leaders
FROM foundations f
LEFT JOIN leaders l ON l.foundation_id = f.foundation_id
WHERE f.foundation_id = '2d078947-1559-45eb-8da5-d410db663b5a'
GROUP BY f.foundation_id;
```

### Top recipients by total grants received
```sql
SELECT 
    r.recipient_name,
    r.city,
    r.state,
    COUNT(g.grant_id) as grant_count,
    SUM(g.grant_amount) as total_received
FROM recipients r
JOIN grants g ON g.recipient_id = r.recipient_id
GROUP BY r.recipient_id, r.recipient_name, r.city, r.state
ORDER BY total_received DESC
LIMIT 20;
```

### Foundations by total giving
```sql
SELECT 
    organization_name,
    city,
    state,
    total_distributions,
    total_assets_eoy,
    jsonb_array_length(leader_ids) as leader_count
FROM foundations
WHERE total_distributions > 0
ORDER BY total_distributions DESC
LIMIT 20;
```

## Using with Your Grant Finder App

To adapt your Flask application to use Supabase:

1. Install Supabase client: `pip install supabase`

2. Update your `app.py` to use Supabase instead of CSV files:

```python
from supabase import create_client, Client

# Initialize Supabase
SUPABASE_URL = "your-project-url"
SUPABASE_KEY = "your-anon-key"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Example: Get foundation with grants
def get_foundation_detail(foundation_id):
    # Get foundation
    foundation = supabase.table('foundations').select('*').eq('foundation_id', foundation_id).single().execute()
    
    # Get grants
    grants = supabase.table('grants').select('*, recipients(*)').eq('foundation_id', foundation_id).execute()
    
    # Get leaders
    leaders = supabase.table('leaders').select('*').eq('foundation_id', foundation_id).execute()
    
    return {
        'foundation': foundation.data,
        'grants': grants.data,
        'leaders': leaders.data
    }
```

## Benefits of This Schema

1. **No Data Duplication**: Each entity (foundation, grant, recipient, leader) exists once with a unique ID
2. **Easy Relationships**: UUID-based foreign keys make relationships explicit and reliable
3. **Flexible Queries**: Normalized structure allows complex queries across relationships
4. **Historical Data**: Multiple tax periods for same foundation are preserved
5. **Scalable**: JSON arrays for many-to-many relationships work well in modern databases
6. **Import Ready**: CSV format is compatible with Supabase, PostgreSQL, MySQL, etc.

## Regenerating Data

To regenerate the normalized CSV files from updated source data:

```bash
cd /Users/sebboyer/Documents/Zeffy/grant_finder
python3 scripts/transform_to_normalized_schema.py
```

The script will:
1. Load the source CSVs
2. Generate new UUIDs for all records
3. Build relationships
4. Validate data integrity
5. Output new normalized CSV files

**Note:** Running the script multiple times will generate different UUIDs each time, so treat each run as a fresh database import.


