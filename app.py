from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Global variables for lazy loading
_data_loaded = False
df = None
foundations_df = None
officers_df = None
foundations_agg = None


def load_data():
    """Lazy load and process data on first request"""
    global _data_loaded, df, foundations_df, officers_df, foundations_agg
    
    if _data_loaded:
        return
    
    # Load the grants data
    csv_path = os.path.join(os.path.dirname(__file__), 'grants_information_summary.csv')
    df = pd.read_csv(csv_path)
    
    # Load the foundations data
    foundations_csv_path = os.path.join(os.path.dirname(__file__), 'foundations_information_summary.csv')
    foundations_df = pd.read_csv(foundations_csv_path)
    
    # Load the officers data
    officers_csv_path = os.path.join(os.path.dirname(__file__), 'officers_information_summary.csv')
    officers_df = pd.read_csv(officers_csv_path)
    
    # Data preprocessing for grants
    df['grant_amount'] = pd.to_numeric(df['grant_amount'], errors='coerce')
    df['cash_grant_amount'] = pd.to_numeric(df['cash_grant_amount'], errors='coerce')
    df['non_cash_grant_amount'] = pd.to_numeric(df['non_cash_grant_amount'], errors='coerce')
    df = df.dropna(subset=['grant_amount'])
    
    # Data preprocessing for officers
    for col in ['compensation', 'benefits', 'other_compensation', 'hours_per_week']:
        if col in officers_df.columns:
            officers_df[col] = pd.to_numeric(officers_df[col], errors='coerce')
    
    # Data preprocessing for foundations
    for col in ['total_assets_eoy', 'fair_market_value_eoy', 'total_revenue', 'total_expenses', 
                'total_distributions', 'investment_income']:
        if col in foundations_df.columns:
            foundations_df[col] = pd.to_numeric(foundations_df[col], errors='coerce')
    
    # Create foundation-level aggregation
    foundations_agg = df.groupby(['filer_ein', 'filer_organization_name']).agg({
        'grant_amount': ['count', 'sum', 'median', 'mean', 'min', 'max'],
        'recipient_state': lambda x: list(x.dropna().unique()),
        'recipient_city': lambda x: list(x.dropna().unique())[:10],
        'grant_purpose': lambda x: x.value_counts().head(3).index.tolist() if len(x) > 0 else [],
        'tax_period_end': 'max'
    }).reset_index()
    
    # Flatten column names
    foundations_agg.columns = ['filer_ein', 'filer_organization_name', 'grant_count', 'total_amount', 
                               'median_grant', 'avg_grant', 'min_grant', 'max_grant',
                               'states_served', 'cities_served', 'top_purposes', 'latest_period']
    
    # Calculate primary state of activity (state with highest total grant amount)
    def get_primary_state(ein):
        """Get the state where the foundation gave the most money"""
        foundation_grants = df[df['filer_ein'] == ein]
        state_totals = foundation_grants.groupby('recipient_state')['grant_amount'].sum()
        if len(state_totals) > 0:
            primary_state = state_totals.idxmax()
            return primary_state if pd.notna(primary_state) else ''
        return ''
    
    foundations_agg['primary_state'] = foundations_agg['filer_ein'].apply(get_primary_state)
    
    # Merge foundation-level data from the foundations CSV
    # Get the most recent record for each foundation (by tax_period_end)
    foundations_df['tax_period_end'] = pd.to_datetime(foundations_df['tax_period_end'], errors='coerce')
    foundations_latest = foundations_df.sort_values('tax_period_end').groupby('filer_ein').last().reset_index()
    
    # Merge foundation data into aggregation
    foundations_agg = foundations_agg.merge(
        foundations_latest[[
            'filer_ein', 'formation_year', 'foundation_address_line1', 'foundation_address_line2',
            'foundation_city', 'foundation_state', 'foundation_zip', 'foundation_phone',
            'foundation_website', 'legal_domicile_state', 'total_assets_eoy', 
            'fair_market_value_eoy', 'total_revenue', 'total_expenses', 'total_distributions',
            'investment_income', 'is_private_operating_foundation', 'is_501c3', 'mission_description'
        ]],
        on='filer_ein',
        how='left'
    )
    
    # Convert to int where appropriate
    foundations_agg['grant_count'] = foundations_agg['grant_count'].astype(int)
    foundations_agg['total_amount'] = foundations_agg['total_amount'].astype(int)
    foundations_agg['median_grant'] = foundations_agg['median_grant'].astype(int)
    foundations_agg['avg_grant'] = foundations_agg['avg_grant'].astype(int)
    foundations_agg['min_grant'] = foundations_agg['min_grant'].astype(int)
    foundations_agg['max_grant'] = foundations_agg['max_grant'].astype(int)
    
    _data_loaded = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/stats')
def get_stats():
    """Get basic statistics about the dataset"""
    load_data()
    stats = {
        'total_grants': len(df),
        'total_foundations': df['filer_organization_name'].nunique(),
        'total_amount': int(df['grant_amount'].sum()),
        'avg_grant': int(df['grant_amount'].mean()),
        'min_grant': int(df['grant_amount'].min()),
        'max_grant': int(df['grant_amount'].max()),
        'states': sorted(df['recipient_state'].dropna().unique().tolist()),
        # Foundation-level stats
        'avg_grants_per_foundation': int(foundations_agg['grant_count'].mean()),
        'median_grants_per_foundation': int(foundations_agg['grant_count'].median()),
        'avg_total_per_foundation': int(foundations_agg['total_amount'].mean()),
        'median_total_per_foundation': int(foundations_agg['total_amount'].median())
    }
    return jsonify(stats)


@app.route('/api/search')
def search_grants():
    """Search and filter grants"""
    load_data()
    # Get query parameters
    foundation_name = request.args.get('foundation', '').strip().upper()
    min_amount = request.args.get('min_amount', type=int)
    max_amount = request.args.get('max_amount', type=int)
    state = request.args.get('state', '').strip().upper()
    city = request.args.get('city', '').strip().upper()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Start with full dataset
    filtered_df = df.copy()
    
    # Apply filters
    if foundation_name:
        filtered_df = filtered_df[
            filtered_df['filer_organization_name'].str.contains(foundation_name, case=False, na=False)
        ]
    
    if min_amount is not None:
        filtered_df = filtered_df[filtered_df['grant_amount'] >= min_amount]
    
    if max_amount is not None:
        filtered_df = filtered_df[filtered_df['grant_amount'] <= max_amount]
    
    if state:
        filtered_df = filtered_df[
            filtered_df['recipient_state'].str.upper() == state
        ]
    
    if city:
        filtered_df = filtered_df[
            filtered_df['recipient_city'].str.contains(city, case=False, na=False)
        ]
    
    # Sort by grant amount descending
    filtered_df = filtered_df.sort_values('grant_amount', ascending=False)
    
    # Pagination
    total_results = len(filtered_df)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_df = filtered_df.iloc[start_idx:end_idx]
    
    # Convert to JSON-friendly format
    results = []
    for _, row in page_df.iterrows():
        results.append({
            'foundation_name': row['filer_organization_name'],
            'foundation_ein': row['filer_ein'],
            'recipient_name': row['recipient_name'],
            'recipient_city': row['recipient_city'] if pd.notna(row['recipient_city']) else '',
            'recipient_state': row['recipient_state'] if pd.notna(row['recipient_state']) else '',
            'recipient_relationship': row.get('recipient_relationship', '') if pd.notna(row.get('recipient_relationship')) else '',
            'recipient_foundation_status': row.get('recipient_foundation_status', '') if pd.notna(row.get('recipient_foundation_status')) else '',
            'grant_amount': int(row['grant_amount']),
            'cash_amount': int(row.get('cash_grant_amount', 0)) if pd.notna(row.get('cash_grant_amount')) else 0,
            'non_cash_amount': int(row.get('non_cash_grant_amount', 0)) if pd.notna(row.get('non_cash_grant_amount')) else 0,
            'grant_purpose': row['grant_purpose'] if pd.notna(row['grant_purpose']) else 'No purpose specified',
            'tax_period': row['tax_period_end'] if pd.notna(row['tax_period_end']) else ''
        })
    
    return jsonify({
        'results': results,
        'total': total_results,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_results + per_page - 1) // per_page
    })


@app.route('/api/foundations')
def get_foundations():
    """Get list of all foundation names for autocomplete"""
    load_data()
    query = request.args.get('q', '').strip().upper()
    
    foundations = df['filer_organization_name'].dropna().unique()
    
    if query:
        foundations = [f for f in foundations if query in f.upper()]
    
    # Limit to 50 results for autocomplete
    foundations = sorted(foundations)[:50]
    
    return jsonify(foundations)


@app.route('/api/foundations_aggregated')
def get_foundations_aggregated():
    """Get aggregated foundation data with filters"""
    load_data()
    # Get query parameters
    foundation_name = request.args.get('foundation', '').strip()
    state = request.args.get('state', '').strip().upper()
    min_total = request.args.get('min_total', type=int)
    max_total = request.args.get('max_total', type=int)
    min_grants = request.args.get('min_grants', type=int)
    min_median = request.args.get('min_median', type=int)
    max_median = request.args.get('max_median', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Start with full foundation dataset
    filtered_df = foundations_agg.copy()
    
    # Apply filters
    if foundation_name:
        filtered_df = filtered_df[
            filtered_df['filer_organization_name'].str.contains(foundation_name, case=False, na=False)
        ]
    
    if state:
        filtered_df = filtered_df[
            filtered_df['states_served'].apply(lambda x: state in x if isinstance(x, list) else False)
        ]
    
    if min_total is not None:
        filtered_df = filtered_df[filtered_df['total_amount'] >= min_total]
    
    if max_total is not None:
        filtered_df = filtered_df[filtered_df['total_amount'] <= max_total]
    
    if min_grants is not None:
        filtered_df = filtered_df[filtered_df['grant_count'] >= min_grants]
    
    if min_median is not None:
        filtered_df = filtered_df[filtered_df['median_grant'] >= min_median]
    
    if max_median is not None:
        filtered_df = filtered_df[filtered_df['median_grant'] <= max_median]
    
    # Sort by total amount descending
    filtered_df = filtered_df.sort_values('total_amount', ascending=False)
    
    # Pagination
    total_results = len(filtered_df)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_df = filtered_df.iloc[start_idx:end_idx]
    
    # Convert to JSON-friendly format
    results = []
    for _, row in page_df.iterrows():
        results.append({
            'foundation_name': row['filer_organization_name'],
            'foundation_ein': int(row['filer_ein']),
            'grant_count': int(row['grant_count']),
            'total_amount': int(row['total_amount']),
            'median_grant': int(row['median_grant']),
            'avg_grant': int(row['avg_grant']),
            'min_grant': int(row['min_grant']),
            'max_grant': int(row['max_grant']),
            'states_served': row['states_served'] if isinstance(row['states_served'], list) else [],
            'cities_served': row['cities_served'] if isinstance(row['cities_served'], list) else [],
            'top_purposes': row['top_purposes'] if isinstance(row['top_purposes'], list) else [],
            'latest_period': row['latest_period'] if pd.notna(row['latest_period']) else '',
            'primary_state': row['primary_state'] if pd.notna(row['primary_state']) else ''
        })
    
    return jsonify({
        'results': results,
        'total': total_results,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_results + per_page - 1) // per_page
    })


def get_foundation_officers(ein):
    """Get list of officers/directors for a foundation."""
    load_data()
    foundation_officers = officers_df[officers_df['foundation_ein'] == ein]
    
    officers_list = []
    for _, officer in foundation_officers.iterrows():
        # Calculate total compensation
        total_comp = 0
        if pd.notna(officer.get('compensation')):
            total_comp += float(officer.get('compensation', 0))
        if pd.notna(officer.get('benefits')):
            total_comp += float(officer.get('benefits', 0))
        if pd.notna(officer.get('other_compensation')):
            total_comp += float(officer.get('other_compensation', 0))
        
        officers_list.append({
            'name': officer.get('person_name', ''),
            'title': officer.get('title', ''),
            'compensation': int(officer.get('compensation', 0)) if pd.notna(officer.get('compensation')) else 0,
            'total_compensation': int(total_comp) if total_comp > 0 else 0,
            'hours_per_week': float(officer.get('hours_per_week', 0)) if pd.notna(officer.get('hours_per_week')) else 0,
            'is_paid': total_comp > 0
        })
    
    # Sort by compensation (highest first), then by title
    officers_list.sort(key=lambda x: (-x['total_compensation'], x['title']))
    
    return officers_list


@app.route('/api/foundation/<int:ein>')
def get_foundation_detail(ein):
    """Get detailed information for a specific foundation including all grants"""
    load_data()
    # Get foundation aggregate data
    foundation = foundations_agg[foundations_agg['filer_ein'] == ein]
    
    if len(foundation) == 0:
        return jsonify({'error': 'Foundation not found'}), 404
    
    foundation_row = foundation.iloc[0]
    
    # Get all grants for this foundation
    foundation_grants = df[df['filer_ein'] == ein].sort_values('grant_amount', ascending=False)
    
    grants = []
    for _, grant in foundation_grants.iterrows():
        grants.append({
            'recipient_name': grant['recipient_name'],
            'recipient_ein': grant.get('recipient_ein', '') if pd.notna(grant.get('recipient_ein')) else '',
            'recipient_city': grant['recipient_city'] if pd.notna(grant['recipient_city']) else '',
            'recipient_state': grant['recipient_state'] if pd.notna(grant['recipient_state']) else '',
            'recipient_relationship': grant.get('recipient_relationship', '') if pd.notna(grant.get('recipient_relationship')) else '',
            'recipient_foundation_status': grant.get('recipient_foundation_status', '') if pd.notna(grant.get('recipient_foundation_status')) else '',
            'grant_amount': int(grant['grant_amount']),
            'cash_amount': int(grant.get('cash_grant_amount', 0)) if pd.notna(grant.get('cash_grant_amount')) else 0,
            'non_cash_amount': int(grant.get('non_cash_grant_amount', 0)) if pd.notna(grant.get('non_cash_grant_amount')) else 0,
            'grant_purpose': grant['grant_purpose'] if pd.notna(grant['grant_purpose']) else 'No purpose specified',
            'tax_period': grant['tax_period_end'] if pd.notna(grant['tax_period_end']) else ''
        })
    
    # Helper for safe value extraction
    def safe_get(key, default=''):
        val = foundation_row.get(key, default)
        if pd.isna(val):
            return default
        return val
    
    return jsonify({
        'foundation_name': foundation_row['filer_organization_name'],
        'foundation_ein': int(foundation_row['filer_ein']),
        'grant_count': int(foundation_row['grant_count']),
        'total_amount': int(foundation_row['total_amount']),
        'median_grant': int(foundation_row['median_grant']),
        'avg_grant': int(foundation_row['avg_grant']),
        'min_grant': int(foundation_row['min_grant']),
        'max_grant': int(foundation_row['max_grant']),
        'states_served': foundation_row['states_served'] if isinstance(foundation_row['states_served'], list) else [],
        'cities_served': foundation_row['cities_served'] if isinstance(foundation_row['cities_served'], list) else [],
        'top_purposes': foundation_row['top_purposes'] if isinstance(foundation_row['top_purposes'], list) else [],
        'latest_period': safe_get('latest_period'),
        'primary_state': safe_get('primary_state'),
        # NEW: Foundation contact info
        'foundation_website': safe_get('foundation_website'),
        'foundation_phone': safe_get('foundation_phone'),
        'foundation_city': safe_get('foundation_city'),
        'foundation_state': safe_get('foundation_state'),
        'grants': grants
    })


@app.route('/foundation/<int:ein>')
def foundation_profile(ein):
    """Render the foundation profile page"""
    return render_template('foundation.html', ein=ein)


@app.route('/api/foundation/<int:ein>/stats')
def get_foundation_stats(ein):
    """Get detailed statistics for a foundation including state-by-state breakdown"""
    load_data()
    # Get foundation aggregate data
    foundation = foundations_agg[foundations_agg['filer_ein'] == ein]
    
    if len(foundation) == 0:
        return jsonify({'error': 'Foundation not found'}), 404
    
    foundation_row = foundation.iloc[0]
    
    # Get all grants for this foundation
    foundation_grants = df[df['filer_ein'] == ein]
    
    # Calculate state-by-state statistics
    state_stats = foundation_grants.groupby('recipient_state').agg({
        'grant_amount': ['count', 'sum', 'mean', 'median']
    }).reset_index()
    
    state_stats.columns = ['state', 'grant_count', 'total_amount', 'avg_grant', 'median_grant']
    
    # Convert to dictionary for JSON
    states_data = []
    for _, row in state_stats.iterrows():
        if pd.notna(row['state']) and row['state']:
            states_data.append({
                'state': row['state'],
                'grant_count': int(row['grant_count']),
                'total_amount': int(row['total_amount']),
                'avg_grant': int(row['avg_grant']),
                'median_grant': int(row['median_grant'])
            })
    
    # Sort by grant count descending
    states_data.sort(key=lambda x: x['grant_count'], reverse=True)
    
    # Get top 10 grants
    top_grants = foundation_grants.nlargest(10, 'grant_amount')
    top_grants_list = []
    for _, grant in top_grants.iterrows():
        top_grants_list.append({
            'recipient_name': grant['recipient_name'],
            'recipient_city': grant['recipient_city'] if pd.notna(grant['recipient_city']) else '',
            'recipient_state': grant['recipient_state'] if pd.notna(grant['recipient_state']) else '',
            'grant_amount': int(grant['grant_amount']),
            'grant_purpose': grant['grant_purpose'] if pd.notna(grant['grant_purpose']) else 'No purpose specified',
            'tax_period': grant['tax_period_end'] if pd.notna(grant['tax_period_end']) else ''
        })
    
    # Get sample of recent grants (10 most recent by tax period)
    recent_grants = foundation_grants.sort_values('tax_period_end', ascending=False).head(10)
    recent_grants_list = []
    for _, grant in recent_grants.iterrows():
        recent_grants_list.append({
            'recipient_name': grant['recipient_name'],
            'recipient_city': grant['recipient_city'] if pd.notna(grant['recipient_city']) else '',
            'recipient_state': grant['recipient_state'] if pd.notna(grant['recipient_state']) else '',
            'grant_amount': int(grant['grant_amount']),
            'grant_purpose': grant['grant_purpose'] if pd.notna(grant['grant_purpose']) else 'No purpose specified',
            'tax_period': grant['tax_period_end'] if pd.notna(grant['tax_period_end']) else ''
        })
    
    # Helper function to safely get values
    def safe_get(key, default=''):
        val = foundation_row.get(key, default)
        if pd.isna(val):
            return default
        return val
    
    def safe_int(key, default=0):
        val = foundation_row.get(key, default)
        if pd.isna(val):
            return default
        try:
            return int(val)
        except (ValueError, TypeError):
            return default
    
    return jsonify({
        'foundation_name': foundation_row['filer_organization_name'],
        'foundation_ein': int(foundation_row['filer_ein']),
        'grant_count': int(foundation_row['grant_count']),
        'total_amount': int(foundation_row['total_amount']),
        'median_grant': int(foundation_row['median_grant']),
        'avg_grant': int(foundation_row['avg_grant']),
        'min_grant': int(foundation_row['min_grant']),
        'max_grant': int(foundation_row['max_grant']),
        'states_served': foundation_row['states_served'] if isinstance(foundation_row['states_served'], list) else [],
        'cities_served': foundation_row['cities_served'] if isinstance(foundation_row['cities_served'], list) else [],
        'top_purposes': foundation_row['top_purposes'] if isinstance(foundation_row['top_purposes'], list) else [],
        'latest_period': safe_get('latest_period'),
        'primary_state': safe_get('primary_state'),
        'states_data': states_data,
        'top_grants': top_grants_list,
        'recent_grants': recent_grants_list,
        # NEW: Foundation-level information
        'formation_year': safe_get('formation_year'),
        'foundation_address': safe_get('foundation_address_line1'),
        'foundation_address2': safe_get('foundation_address_line2'),
        'foundation_city': safe_get('foundation_city'),
        'foundation_state': safe_get('foundation_state'),
        'foundation_zip': safe_get('foundation_zip'),
        'foundation_phone': safe_get('foundation_phone'),
        'foundation_website': safe_get('foundation_website'),
        'legal_domicile_state': safe_get('legal_domicile_state'),
        'total_assets': safe_int('total_assets_eoy'),
        'fair_market_value': safe_int('fair_market_value_eoy'),
        'total_revenue': safe_int('total_revenue'),
        'total_expenses': safe_int('total_expenses'),
        'total_distributions_paid': safe_int('total_distributions'),
        'investment_income': safe_int('investment_income'),
        'is_private_operating_foundation': safe_get('is_private_operating_foundation') in ['true', 'True', '1', 'X'],
        'is_501c3': safe_get('is_501c3') in ['true', 'True', '1', 'X'],
        'mission': safe_get('mission_description'),
        # NEW: Officers/Directors
        'officers': get_foundation_officers(ein)
    })


@app.route('/api/foundation/<int:ein>')
def get_foundation_basic(ein):
    """Get basic foundation information (used for display pages)"""
    load_data()
    # This endpoint was being used before but we'll keep it for compatibility
    # Just return simple foundation info
    foundation = foundations_agg[foundations_agg['filer_ein'] == ein]
    
    if len(foundation) == 0:
        return jsonify({'error': 'Foundation not found'}), 404
    
    foundation_row = foundation.iloc[0]
    
    return jsonify({
        'foundation_name': foundation_row['filer_organization_name'],
        'foundation_ein': int(foundation_row['filer_ein']),
        'grant_count': int(foundation_row['grant_count']),
        'total_amount': int(foundation_row['total_amount']),
    })


if __name__ == '__main__':
    load_data()  # Load data in development mode
    print("Starting Zeffy Grant Finder webapp...")
    print(f"Loaded {len(df)} grants from {len(foundations_agg)} foundations")
    print(f"Foundation aggregation complete!")
    print("\n" + "="*60)
    print("🚀 Zeffy Grant Finder is running!")
    print("📍 Open your browser and visit: http://localhost:5001")
    print("   • Grant-level view: Search individual grants")
    print("   • Foundation-level view: Browse foundations with stats")
    print("="*60 + "\n")
    app.run(debug=True, port=5001, host='127.0.0.1')
