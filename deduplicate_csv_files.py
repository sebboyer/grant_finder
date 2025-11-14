"""
Remove duplicate records from normalized CSV files before uploading to Supabase.
Deduplicates based on primary key fields.
"""
import pandas as pd
import sys

def deduplicate_csv(input_file, output_file, id_column, description):
    """Remove duplicates from a CSV file based on ID column."""
    print(f"\n{'='*60}")
    print(f"Deduplicating {description}...")
    print(f"{'='*60}")
    
    # Read CSV
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file, low_memory=False)
    initial_count = len(df)
    print(f"  Initial records: {initial_count:,}")
    
    # Check for duplicates
    duplicates = df.duplicated(subset=[id_column], keep='first')
    duplicate_count = duplicates.sum()
    
    if duplicate_count > 0:
        print(f"  Found {duplicate_count:,} duplicate records")
        
        # Remove duplicates (keep first occurrence)
        df_clean = df[~duplicates]
        final_count = len(df_clean)
        
        print(f"  Final records: {final_count:,}")
        print(f"  Removed: {duplicate_count:,} duplicates")
        
        # Save cleaned CSV
        print(f"  Writing to {output_file}...")
        df_clean.to_csv(output_file, index=False)
        print(f"  ✓ Saved cleaned file")
        
        return duplicate_count
    else:
        print(f"  ✓ No duplicates found!")
        # Copy file as-is
        df.to_csv(output_file, index=False)
        return 0

def main():
    """Clean all normalized CSV files."""
    print("="*60)
    print("CSV DEDUPLICATION TOOL")
    print("="*60)
    
    files_to_clean = [
        ('foundations_normalized.csv', 'foundations_normalized_clean.csv', 'foundation_id', 'Foundations'),
        ('recipients_normalized.csv', 'recipients_normalized_clean.csv', 'recipient_id', 'Recipients'),
        ('grants_normalized.csv', 'grants_normalized_clean.csv', 'grant_id', 'Grants'),
        ('leaders_normalized.csv', 'leaders_normalized_clean.csv', 'leader_id', 'Leaders'),
    ]
    
    total_duplicates = 0
    
    for input_file, output_file, id_column, description in files_to_clean:
        try:
            duplicates = deduplicate_csv(input_file, output_file, id_column, description)
            total_duplicates += duplicates
        except Exception as e:
            print(f"  ✗ Error processing {description}: {e}")
            sys.exit(1)
    
    print("\n" + "="*60)
    if total_duplicates == 0:
        print("✓ ALL FILES ARE CLEAN - NO DUPLICATES FOUND")
    else:
        print(f"✓ DEDUPLICATION COMPLETE - Removed {total_duplicates:,} total duplicates")
    print("="*60)
    
    print("\nCleaned files created:")
    for _, output_file, _, _ in files_to_clean:
        print(f"  - {output_file}")

if __name__ == '__main__':
    main()


