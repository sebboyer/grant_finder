"""
Upload normalized CSV data to Supabase tables
"""
import pandas as pd
from utils.supabase_client import supabase
import json

print("Loading CSV files...")

# Load CSV files
foundations_df = pd.read_csv('foundations_normalized.csv')
recipients_df = pd.read_csv('recipients_normalized.csv')
grants_df = pd.read_csv('grants_normalized.csv')
leaders_df = pd.read_csv('leaders_normalized.csv')

print(f"Loaded {len(foundations_df)} foundations")
print(f"Loaded {len(recipients_df)} recipients")
print(f"Loaded {len(grants_df)} grants")
print(f"Loaded {len(leaders_df)} leaders")
print()

# Upload foundations (in batches to avoid timeout)
print("Uploading foundations...")
batch_size = 100
foundations_data = foundations_df.to_dict('records')

# Clean up the data - convert NaN to None and handle JSON fields
for record in foundations_data:
    for key, value in record.items():
        if pd.isna(value):
            record[key] = None
        elif key == 'leader_ids' and value:
            # Parse JSON string
            try:
                record[key] = json.loads(value) if isinstance(value, str) else value
            except:
                record[key] = []
        elif key in ['zip', 'phone'] and value is not None:
            # Convert zip and phone to strings (remove .0)
            record[key] = str(int(float(value))) if value != '' else None

for i in range(0, len(foundations_data), batch_size):
    batch = foundations_data[i:i+batch_size]
    try:
        response = supabase.table('foundation').insert(batch).execute()
        print(f"  Uploaded batch {i//batch_size + 1}/{(len(foundations_data) + batch_size - 1)//batch_size}")
    except Exception as e:
        print(f"  Error uploading foundations batch {i//batch_size + 1}: {e}")

# Upload recipients
print("\nUploading recipients...")
recipients_data = recipients_df.to_dict('records')
for record in recipients_data:
    for key, value in record.items():
        if pd.isna(value):
            record[key] = None
        elif key == 'grant_ids' and value:
            try:
                record[key] = json.loads(value) if isinstance(value, str) else value
            except:
                record[key] = []
        elif key == 'zip' and value is not None:
            # Convert zip to string (remove .0)
            try:
                record[key] = str(int(float(value))) if value != '' else None
            except:
                record[key] = None

for i in range(0, len(recipients_data), batch_size):
    batch = recipients_data[i:i+batch_size]
    try:
        response = supabase.table('Recipients').insert(batch).execute()
        print(f"  Uploaded batch {i//batch_size + 1}/{(len(recipients_data) + batch_size - 1)//batch_size}")
    except Exception as e:
        print(f"  Error uploading recipients batch {i//batch_size + 1}: {e}")

# Upload grants
print("\nUploading grants...")
grants_data = grants_df.to_dict('records')
for record in grants_data:
    for key, value in record.items():
        if pd.isna(value):
            record[key] = None

for i in range(0, len(grants_data), batch_size):
    batch = grants_data[i:i+batch_size]
    try:
        response = supabase.table('grants').insert(batch).execute()
        print(f"  Uploaded batch {i//batch_size + 1}/{(len(grants_data) + batch_size - 1)//batch_size}")
    except Exception as e:
        print(f"  Error uploading grants batch {i//batch_size + 1}: {e}")

# Upload leaders
print("\nUploading leaders...")
leaders_data = leaders_df.to_dict('records')
for record in leaders_data:
    for key, value in record.items():
        if pd.isna(value):
            record[key] = None

for i in range(0, len(leaders_data), batch_size):
    batch = leaders_data[i:i+batch_size]
    try:
        response = supabase.table('Leaders').insert(batch).execute()
        print(f"  Uploaded batch {i//batch_size + 1}/{(len(leaders_data) + batch_size - 1)//batch_size}")
    except Exception as e:
        print(f"  Error uploading leaders batch {i//batch_size + 1}: {e}")

print("\n✓ Data upload complete!")

