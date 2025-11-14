"""
Monitor upload progress by checking record counts
"""
from utils.supabase_client import supabase
import time
import sys

def get_count_fast(table_name):
    """Get approximate count using a quick query."""
    try:
        # Try to get count with short timeout
        response = supabase.table(table_name).select('*', count='exact').limit(1).execute()
        return response.count if hasattr(response, 'count') else '?'
    except:
        return '?'

def monitor():
    """Monitor upload progress."""
    print("Monitoring upload progress...")
    print("Press Ctrl+C to stop monitoring\n")
    
    tables = [
        ('foundation', 270033),
        ('Recipients', 843542),
        ('grants', 1115134),
        ('Leaders', 1588912)
    ]
    
    iteration = 0
    try:
        while True:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"Progress Check #{iteration} at {time.strftime('%H:%M:%S')}")
            print(f"{'='*60}")
            
            for table, expected in tables:
                count = get_count_fast(table)
                if count == '?':
                    print(f"{table:15} : Checking... (large table)")
                else:
                    pct = (count / expected * 100) if count != '?' else 0
                    status = '✓' if count == expected else '⏳'
                    print(f"{table:15} : {count:>10,} / {expected:,} ({pct:.1f}%) {status}")
            
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        sys.exit(0)

if __name__ == '__main__':
    monitor()


