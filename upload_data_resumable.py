"""
Resumable upload of normalized CSV data to Supabase tables.
Checks what's already uploaded and continues from there.
"""
import pandas as pd
from utils.supabase_client import supabase
import json
import sys

def get_table_count(table_name):
    """Get current count of records in a table."""
    try:
        response = supabase.table(table_name).select('*', count='exact').limit(1).execute()
        return response.count if hasattr(response, 'count') else 0
    except:
        return 0

def upload_table(table_name, csv_file, columns_to_check, batch_size=100, start_batch=0):
    """Upload data to a table with resume capability."""
    print(f"\n{'='*60}")
    print(f"Uploading to {table_name}...")
    print(f"{'='*60}")
    
    # Load CSV
    df = pd.read_csv(csv_file)
    total_records = len(df)
    print(f"Total records in CSV: {total_records:,}")
    
    # Check current count
    current_count = get_table_count(table_name)
    print(f"Records already in database: {current_count:,}")
    
    if current_count >= total_records:
        print(f"✓ {table_name} already fully uploaded, skipping...")
        return True
    
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
    
    # Calculate starting point
    start_index = start_batch * batch_size
    if start_index < current_count:
        start_index = current_count
    
    total_batches = (total_records + batch_size - 1) // batch_size
    start_batch_num = start_index // batch_size
    
    print(f"Starting upload from record {start_index:,} (batch {start_batch_num + 1}/{total_batches})")
    
    # Upload in batches
    errors = 0
    for i in range(start_index, total_records, batch_size):
        batch = data[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        try:
            response = supabase.table(table_name).insert(batch).execute()
            if batch_num % 10 == 0 or batch_num == total_batches:
                print(f"  ✓ Batch {batch_num}/{total_batches} ({i+len(batch):,}/{total_records:,} records)")
        except Exception as e:
            print(f"  ✗ Error in batch {batch_num}: {e}")
            errors += 1
            if errors > 10:
                print(f"  Too many errors, stopping upload of {table_name}")
                return False
    
    print(f"✓ {table_name} upload complete!")
    return True

def main():
    """Main upload function."""
    print("="*60)
    print("RESUMABLE SUPABASE DATA UPLOAD")
    print("="*60)
    
    # Upload order (respecting foreign key constraints)
    uploads = [
        ('foundation', 'foundations_normalized.csv', ['foundation_id']),
        ('Recipients', 'recipients_normalized.csv', ['recipient_id']),
        ('grants', 'grants_normalized.csv', ['grant_id']),
        ('Leaders', 'leaders_normalized.csv', ['leader_id']),
    ]
    
    for table_name, csv_file, check_cols in uploads:
        success = upload_table(table_name, csv_file, check_cols, batch_size=500)
        if not success:
            print(f"\n✗ Upload failed at {table_name}")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("✓ ALL DATA UPLOADED SUCCESSFULLY!")
    print("="*60)
    
    # Print final counts
    print("\nFinal record counts:")
    for table_name, _, _ in uploads:
        count = get_table_count(table_name)
        print(f"  {table_name}: {count:,}")

if __name__ == '__main__':
    main()


