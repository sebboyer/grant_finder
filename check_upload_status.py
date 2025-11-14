"""
Check how many records have been uploaded to each table
"""
from utils.supabase_client import supabase

tables = ['foundation', 'Recipients', 'grants', 'Leaders']

print("Checking upload status...\n")
for table in tables:
    try:
        response = supabase.table(table).select('*', count='exact').limit(1).execute()
        count = response.count if hasattr(response, 'count') else 0
        print(f"{table}: {count:,} records")
    except Exception as e:
        print(f"{table}: Error - {e}")


