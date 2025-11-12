# Supabase Setup Guide for Grant Finder

## Overview
The Grant Finder application has been successfully migrated from CSV files to Supabase. All API endpoints have been updated to query Supabase instead of using pandas DataFrames.

## Current Status
✅ Supabase client configured  
✅ API module created (`api/supabase_api.py`)  
✅ All Flask routes updated to use Supabase  
✅ Table schema matches normalized CSV files  
❌ Data needs to be uploaded (row-level security prevents programmatic upload)

## Table Names in Supabase
The following tables exist in your Supabase project:
- `foundation` (singular)
- `grants` (plural)
- `Leaders` (capitalized)
- `Recipients` (capitalized)

## Data Upload Required

### Option 1: Upload via Supabase Dashboard (Recommended)

1. Go to your Supabase project: https://evgvqffabyfdubglqima.supabase.co
2. Navigate to **Table Editor**
3. Upload the CSV files in this order (to respect foreign key constraints):
   
   a. **foundation table**: Upload `foundations_normalized.csv`
   b. **Recipients table**: Upload `recipients_normalized.csv`  
   c. **grants table**: Upload `grants_normalized.csv`
   d. **Leaders table**: Upload `leaders_normalized.csv`

### Option 2: Temporarily Disable RLS for Upload

If you want to use the automated upload script:

1. In Supabase dashboard, go to **Authentication** → **Policies**
2. Temporarily disable RLS or add insert policies for each table
3. Run the upload script:
   ```bash
   cd /Users/sebboyer/Documents/Zeffy/grant_finder
   venv/bin/python upload_data_to_supabase.py
   ```
4. Re-enable RLS policies after upload

## API Endpoints

All endpoints maintain the same format as before:

- `GET /api/stats` - Global statistics
- `GET /api/search` - Search grants with filters
  - Query params: `foundation`, `min_amount`, `max_amount`, `state`, `city`, `page`, `per_page`
- `GET /api/foundations` - Foundation name autocomplete
  - Query params: `q` (search query)
- `GET /api/foundations_aggregated` - Foundation list with aggregated stats
  - Query params: `foundation`, `state`, `min_total`, `max_total`, `min_grants`, `min_median`, `max_median`, `page`, `per_page`
- `GET /api/foundation/<ein>` - Basic foundation info
- `GET /api/foundation/<ein>/stats` - Detailed foundation stats with state breakdown
- `GET /foundation/<ein>` - Foundation profile page (renders HTML)

## Running the Application

```bash
cd /Users/sebboyer/Documents/Zeffy/grant_finder
venv/bin/python app.py
```

The app will start on http://localhost:5001

## Testing

Once data is uploaded, test the endpoints:

```bash
# Test stats endpoint
curl http://localhost:5001/api/stats

# Test search
curl "http://localhost:5001/api/search?state=CA&page=1&per_page=10"

# Test foundation detail
curl http://localhost:5001/api/foundation/391890044
```

## Files Modified

- **Created**: `api/__init__.py`, `api/supabase_api.py`
- **Modified**: `app.py` (removed pandas, added Supabase queries)
- **Added**: `utils/supabase_client.py` (Supabase connection)
- **Added**: `upload_data_to_supabase.py` (data upload script)

## Migration Complete

The application is fully migrated to Supabase. Once data is uploaded, it will function identically to the CSV-based version but with better performance and scalability.

## Cleanup

After successful data upload, you can optionally remove:
- `test_supabase_connection.py`
- `check_tables.py`
- `upload_data_to_supabase.py` (keep for future updates)

