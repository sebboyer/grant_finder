"""
Clear Supabase tables in batches to avoid timeout
"""
from utils.supabase_client import supabase
import time

def clear_table_in_batches(table_name, batch_size=1000):
    """Clear a table by deleting records in batches."""
    print(f"\nClearing {table_name}...")
    
    total_deleted = 0
    while True:
        try:
            # Get a batch of IDs
            id_field = ('foundation_id' if table_name == 'foundation' else 
                       'grant_id' if table_name == 'grants' else
                       'leader_id' if table_name == 'Leaders' else
                       'recipient_id')
            
            response = supabase.table(table_name).select(id_field).limit(batch_size).execute()
            
            if not response.data or len(response.data) == 0:
                print(f"  ✓ {table_name} cleared (total: {total_deleted:,} records)")
                break
            
            # Extract IDs
            ids = [record[id_field] for record in response.data]
            
            # Delete this batch
            delete_response = supabase.table(table_name).delete().in_(id_field, ids).execute()
            
            total_deleted += len(ids)
            print(f"  Deleted {total_deleted:,} records...", end='\r')
            
            time.sleep(0.1)  # Small delay to avoid rate limiting
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            break

def main():
    """Clear all tables in correct order."""
    print("Clearing all Supabase tables in batches...")
    
    # Delete in reverse order of dependencies
    tables = ['grants', 'Leaders', 'Recipients', 'foundation']
    
    for table in tables:
        clear_table_in_batches(table, batch_size=500)
    
    print("\n✓ All tables cleared!")

if __name__ == '__main__':
    main()


