"""
Clear all data from Supabase tables before uploading new data.
"""
from utils.supabase_client import supabase

def clear_all_tables():
    """Clear all records from all tables in the correct order (respecting foreign keys)."""
    
    # Delete in reverse order of dependencies
    tables_to_clear = [
        'grants',      # Has foreign keys to foundation and Recipients
        'Leaders',     # Has foreign key to foundation
        'Recipients',  # Referenced by grants
        'foundation',  # Base table
    ]
    
    print("Clearing Supabase tables...")
    
    for table in tables_to_clear:
        try:
            print(f"\nClearing table: {table}")
            
            # Count records before deletion
            count_response = supabase.table(table).select('*', count='exact').execute()
            record_count = count_response.count if hasattr(count_response, 'count') else 0
            print(f"  Found {record_count} records")
            
            if record_count > 0:
                # Delete all records (using a filter that matches all records)
                # Note: This is a dangerous operation - deletes ALL data
                delete_response = supabase.table(table).delete().neq('foundation_id' if table == 'foundation' else 
                                                                      'grant_id' if table == 'grants' else
                                                                      'leader_id' if table == 'Leaders' else
                                                                      'recipient_id', '00000000-0000-0000-0000-000000000000').execute()
                print(f"  ✓ Cleared {table}")
            else:
                print(f"  ✓ {table} was already empty")
                
        except Exception as e:
            print(f"  ✗ Error clearing {table}: {e}")
            # Continue with other tables even if one fails
    
    print("\n✓ All tables cleared!")

if __name__ == '__main__':
    print("WARNING: This will delete ALL data from the database!")
    print("Press Ctrl+C to cancel, or wait 3 seconds to proceed...")
    
    import time
    time.sleep(3)
    
    clear_all_tables()


