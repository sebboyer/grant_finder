# Grant Finder - Supabase Integration

## Quick Start

1. **Start the application:**
   ```bash
   cd /Users/sebboyer/Documents/Zeffy/grant_finder
   venv/bin/python app.py
   ```

2. **Access the application:**
   - Open browser: http://localhost:5001

3. **Test the API:**
   ```bash
   # Get statistics
   curl http://localhost:5001/api/stats
   
   # Search grants
   curl "http://localhost:5001/api/search?state=CA&min_amount=10000"
   
   # Get foundation detail
   curl http://localhost:5001/api/foundation/391890044
   ```

## Architecture

### Before (CSV-based)
- Loaded 3 CSV files into pandas DataFrames on startup
- All queries processed in-memory with pandas
- Slow startup time
- Limited scalability

### After (Supabase-based)
- Direct database queries via Supabase API
- No startup delay
- Efficient SQL queries with proper indexing
- Infinitely scalable

## API Layer

All database interactions go through `api/supabase_api.py`:

```python
from api import supabase_api

# Get foundation by EIN
foundation = supabase_api.get_foundation_by_ein(391890044)

# Search grants
results, total = supabase_api.search_grants(
    foundation_name="schultz",
    state="WI",
    page=1,
    per_page=20
)

# Get statistics
stats = supabase_api.get_stats()
```

## Key Functions

### Core Query Functions
- `get_foundation_by_ein(ein)` - Fetch foundation record by EIN
- `search_grants(...)` - Search and filter grants with pagination
- `get_all_foundation_eins()` - Get foundation names for autocomplete
- `get_stats()` - Global statistics

### Aggregation Functions
- `get_foundation_aggregated_stats(ein)` - Calculate stats for one foundation
- `get_all_foundations_aggregated(...)` - Get all foundations with stats
- `get_foundation_state_breakdown(ein)` - State-by-state grant analysis
- `get_foundation_officers(ein)` - Officers/directors list
- `get_foundation_grants(ein)` - All grants for a foundation

## Data Model

### Tables in Supabase
1. **foundation** - Foundation records (one per tax filing)
   - Primary key: `foundation_id` (UUID)
   - Indexed on: `ein`
   
2. **grants** - Individual grants
   - Primary key: `grant_id` (UUID)
   - Foreign key: `foundation_id` → foundation
   - Indexed on: `foundation_id`, `grant_amount`

3. **Leaders** - Officers and directors
   - Primary key: `leader_id` (UUID)
   - Foreign key: `foundation_id` → foundation

4. **Recipients** - Grant recipients
   - Primary key: `recipient_id` (UUID)
   - Contains: name, EIN, address, list of grant IDs

### Key Design Decisions

1. **EIN-based API** - All public endpoints use EIN (integer) for foundation lookup, UUIDs used internally
2. **Denormalized grant data** - Recipient info stored in grants table for faster queries
3. **Aggregations on-demand** - Stats calculated per request (could add caching later)

## Updating Data

To refresh data from updated CSV files:

```bash
cd /Users/sebboyer/Documents/Zeffy/grant_finder
venv/bin/python upload_data_to_supabase.py
```

**Note:** This will append data. To replace, truncate tables in Supabase first.

## Configuration

Supabase credentials are in `utils/supabase_client.py`:
- URL: https://evgvqffabyfdubglqima.supabase.co
- API key: Configured (stored in code for this project)

## Monitoring & Debugging

### Check data counts:
```python
from utils.supabase_client import supabase

# Count records
foundation_count = supabase.table('foundation').select('*', count='exact').execute().count
grants_count = supabase.table('grants').select('*', count='exact').execute().count

print(f"Foundations: {foundation_count}")
print(f"Grants: {grants_count}")
```

### View Supabase logs:
1. Go to Supabase dashboard
2. Click "Logs" in left sidebar
3. View API requests and errors

## Known Limitations

1. **Row-level security** - Currently disabled for ease of use. Enable RLS in production.
2. **No caching** - Each request queries database. Add Redis for high traffic.
3. **No rate limiting** - Supabase has built-in limits, but no app-level throttling.

## Troubleshooting

### API returns empty results
- Check if data is uploaded: Run verification script
- Check table names match: `foundation`, `grants`, `Leaders`, `Recipients`

### Connection errors
- Verify Supabase credentials in `utils/supabase_client.py`
- Check internet connection
- Verify Supabase project is active

### Slow queries
- Check Supabase dashboard for query performance
- Ensure proper indexes exist
- Consider adding caching layer

## Next Steps

Potential enhancements:
1. Add Redis caching for frequently accessed foundations
2. Enable row-level security policies
3. Add API rate limiting
4. Implement full-text search on grant purposes
5. Add user authentication for saved searches
6. Create admin panel for data management

## Support

For issues or questions:
1. Check `MIGRATION_COMPLETE.md` for migration details
2. Review `SUPABASE_SETUP.md` for setup instructions
3. Test endpoints using provided curl commands

