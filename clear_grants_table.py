"""
Clear only the grants table to restart its upload
"""
from utils.supabase_client import supabase
import time

def clear_table_in_batches(table_name, batch_size=500):
    """Clear a table by deleting records in batches."""
    print(f"\nClearing {table_name} in batches...")
    
    total_deleted = 0
    id_field = 'grant_id'
    
    while True:
        try:
            # Get a batch of IDs
            response = supabase.table(table_name).select(id_field).limit(batch_size).execute()
            
            if not response.data or len(response.data) == 0:
                print(f"\r  ✓ {table_name} cleared (total: {total_deleted:,} records)")
                break
            
            # Extract IDs
            ids = [record[id_field] for record in response.data]
            
            # Delete this batch
            supabase.table(table_name).delete().in_(id_field, ids).execute()
            
            total_deleted += len(ids)
            print(f"  Deleted {total_deleted:,} records...", end='\r')
            
            time.sleep(0.05)
            
        except Exception as e:
            print(f"\n  Error: {e}")
            print(f"  Total deleted so far: {total_deleted:,}")
            break

if __name__ == '__main__':
    print("Clearing grants table...")
    clear_table_in_batches('grants')
    print("\n✓ Done!")


