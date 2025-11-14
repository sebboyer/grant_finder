"""
Supabase client configuration for grant_finder
"""
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://evgvqffabyfdubglqima.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV2Z3ZxZmZhYnlmZHViZ2xxaW1hIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4NjY0ODQsImV4cCI6MjA3ODQ0MjQ4NH0.jrxNWaHn5_MEB9YBRhw-mup5FhOZ9l06qO4rVCE9NUs"

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


