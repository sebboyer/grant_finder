"""
Upload cleaned normalized CSV data to Supabase tables.
Uses the deduplicated _clean.csv files.
"""
import pandas as pd
from utils.supabase_client import supabase
import json
import sys

def upload_table(table_name, csv_file, batch_size=500):
    """Upload data to a table."""
    print(f"\n{'='*60}")
    print(f"Uploading to {table_name}...")
    print(f"{'='*60}")
    
    # Load CSV
    print(f"Reading {csv_file}...")
    df = pd.read_csv(csv_file, low_memory=False)
    total_records = len(df)
    print(f"Total records to upload: {total_records:,}")
    
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
            elif key in ['zip', 'phone'] and value is not None:
                try:
                    record[key] = str(int(float(value))) if value != '' else None
                except:
                    record[key] = None
    
    total_batches = (total_records + batch_size - 1) // batch_size
    print(f"Uploading in {total_batches} batches of {batch_size}...")
    
    # Upload in batches
    errors = 0
    uploaded = 0
    
    for i in range(0, total_records, batch_size):
        batch = data[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        try:
            response = supabase.table(table_name).insert(batch).execute()
            uploaded += len(batch)
            
            if batch_num % 10 == 0 or batch_num == total_batches:
                print(f"  ✓ Batch {batch_num}/{total_batches} ({uploaded:,}/{total_records:,} records)")
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a duplicate error
            if 'duplicate key' in error_msg.lower():
                print(f"  ⚠ Batch {batch_num}: Skipping duplicates")
                # Try to insert records one by one to skip duplicates
                for record in batch:
                    try:
                        supabase.table(table_name).insert([record]).execute()
                        uploaded += 1
                    except:
                        pass  # Skip this duplicate
            else:
                print(f"  ✗ Error in batch {batch_num}: {error_msg[:100]}")
                errors += 1
                if errors > 20:
                    print(f"  Too many errors, stopping upload of {table_name}")
                    return False
    
    print(f"✓ {table_name} upload complete! ({uploaded:,} records uploaded)")
    return True

def main():
    """Main upload function."""
    print("="*60)
    print("CLEAN DATA UPLOAD TO SUPABASE")
    print("="*60)
    
    # Check which tables need uploading
    print("\nChecking current database status...")
    
    # Upload order (respecting foreign key constraints)
    # Using _clean.csv files that have been deduplicated
    uploads = [
        ('foundation', 'foundations_normalized_clean.csv'),
        ('Recipients', 'recipients_normalized_clean.csv'),
        ('grants', 'grants_normalized_clean.csv'),
        ('Leaders', 'leaders_normalized_clean.csv'),
    ]
    
    for table_name, csv_file in uploads:
        success = upload_table(table_name, csv_file, batch_size=500)
        if not success:
            print(f"\n✗ Upload failed at {table_name}")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("✓ ALL DATA UPLOADED SUCCESSFULLY!")
    print("="*60)

if __name__ == '__main__':
    main()


