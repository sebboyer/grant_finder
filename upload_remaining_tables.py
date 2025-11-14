"""
Upload only grants and leaders tables (foundation and recipients are already uploaded)
"""
import pandas as pd
from utils.supabase_client import supabase
import json
import sys

def upload_table(table_name, csv_file, batch_size=500):
    """Upload data to a table."""
    print(f"\n{'='*60}")
    print(f"Uploading {table_name}...")
    print(f"{'='*60}")
    
    # Load CSV
    print(f"Reading {csv_file}...")
    df = pd.read_csv(csv_file, low_memory=False)
    total_records = len(df)
    print(f"Total records: {total_records:,}")
    
    # Convert to records
    data = df.to_dict('records')
    
    # Clean up data
    for record in data:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
            elif key in ['leader_ids', 'grant_ids'] and value:
                try:
                    record[key] = json.loads(value) if isinstance(value, str) else value
                except:
                    record[key] = []
    
    total_batches = (total_records + batch_size - 1) // batch_size
    
    # Upload in batches
    uploaded = 0
    for i in range(0, total_records, batch_size):
        batch = data[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        try:
            supabase.table(table_name).insert(batch).execute()
            uploaded += len(batch)
            
            if batch_num % 100 == 0 or batch_num == total_batches:
                print(f"  ✓ Batch {batch_num}/{total_batches} ({uploaded:,}/{total_records:,})")
        except Exception as e:
            # Try individual inserts for this batch
            for record in batch:
                try:
                    supabase.table(table_name).insert([record]).execute()
                    uploaded += 1
                except:
                    pass  # Skip duplicates
    
    print(f"✓ {table_name} complete! ({uploaded:,} records)")
    return True

def main():
    print("="*60)
    print("UPLOADING REMAINING TABLES (GRANTS & LEADERS)")
    print("="*60)
    
    # Upload grants first (has foreign keys to foundation and recipients)
    upload_table('grants', 'grants_normalized_clean.csv', batch_size=500)
    
    # Upload leaders (has foreign key to foundation)
    upload_table('Leaders', 'leaders_normalized_clean.csv', batch_size=500)
    
    print("\n" + "="*60)
    print("✓ UPLOAD COMPLETE!")
    print("="*60)

if __name__ == '__main__':
    main()


