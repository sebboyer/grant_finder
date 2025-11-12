from flask import Flask, render_template, request, jsonify
from api import supabase_api

app = Flask(__name__, static_folder='public', static_url_path='')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/stats')
def get_stats():
    """Get basic statistics about the dataset"""
    stats = supabase_api.get_stats()
    return jsonify(stats)


@app.route('/api/search')
def search_grants():
    """Search and filter grants"""
    # Get query parameters
    foundation_name = request.args.get('foundation', '').strip()
    min_amount = request.args.get('min_amount', type=int)
    max_amount = request.args.get('max_amount', type=int)
    state = request.args.get('state', '').strip().upper()
    city = request.args.get('city', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Search grants using Supabase API
    results, total_results = supabase_api.search_grants(
        foundation_name=foundation_name if foundation_name else None,
        min_amount=min_amount,
        max_amount=max_amount,
        state=state if state else None,
        city=city if city else None,
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'results': results,
        'total': total_results,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_results + per_page - 1) // per_page if total_results > 0 else 0
    })


@app.route('/api/foundations')
def get_foundations():
    """Get list of all foundation names for autocomplete"""
    query = request.args.get('q', '').strip().upper()
    
    foundations = supabase_api.get_all_foundation_eins()
    
    if query:
        foundations = [f for f in foundations if query in f.upper()]
    
    # Limit to 50 results for autocomplete
    foundations = foundations[:50]
    
    return jsonify(foundations)


@app.route('/api/foundations_aggregated')
def get_foundations_aggregated():
    """Get aggregated foundation data with filters"""
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
    
    # Get aggregated foundations
    results, total_results = supabase_api.get_all_foundations_aggregated(
        foundation_name=foundation_name if foundation_name else None,
        state=state if state else None,
        min_total=min_total,
        max_total=max_total,
        min_grants=min_grants,
        min_median=min_median,
        max_median=max_median,
        page=page,
        per_page=per_page
    )
    
    # Format results to match original response
    formatted_results = []
    for row in results:
        formatted_results.append({
            'foundation_name': row['filer_organization_name'],
            'foundation_ein': row['filer_ein'],
            'grant_count': row['grant_count'],
            'total_amount': row['total_amount'],
            'median_grant': row['median_grant'],
            'avg_grant': row['avg_grant'],
            'min_grant': row['min_grant'],
            'max_grant': row['max_grant'],
            'states_served': row['states_served'],
            'cities_served': row['cities_served'],
            'top_purposes': row['top_purposes'],
            'latest_period': row['latest_period'],
            'primary_state': row['primary_state']
        })
    
    return jsonify({
        'results': formatted_results,
        'total': total_results,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_results + per_page - 1) // per_page if total_results > 0 else 0
    })


@app.route('/api/foundation/<int:ein>')
def get_foundation_detail(ein):
    """Get detailed information for a specific foundation including all grants"""
    # Get foundation aggregated stats
    foundation_data = supabase_api.get_foundation_aggregated_stats(ein)
    
    if not foundation_data:
        return jsonify({'error': 'Foundation not found'}), 404
    
    # Get all grants for this foundation
    grants = supabase_api.get_foundation_grants(ein)
    
    # Helper for safe value extraction
    def safe_get(data, key, default=''):
        val = data.get(key, default)
        if val is None:
            return default
        return val
    
    return jsonify({
        'foundation_name': foundation_data['foundation_name'],
        'foundation_ein': foundation_data['foundation_ein'],
        'grant_count': foundation_data['grant_count'],
        'total_amount': foundation_data['total_amount'],
        'median_grant': foundation_data['median_grant'],
        'avg_grant': foundation_data['avg_grant'],
        'min_grant': foundation_data['min_grant'],
        'max_grant': foundation_data['max_grant'],
        'states_served': foundation_data['states_served'],
        'cities_served': foundation_data['cities_served'],
        'top_purposes': foundation_data['top_purposes'],
        'latest_period': safe_get(foundation_data, 'latest_period'),
        'primary_state': safe_get(foundation_data, 'primary_state'),
        # Foundation contact info
        'foundation_website': safe_get(foundation_data, 'foundation_website'),
        'foundation_phone': safe_get(foundation_data, 'foundation_phone'),
        'foundation_city': safe_get(foundation_data, 'foundation_city'),
        'foundation_state': safe_get(foundation_data, 'foundation_state'),
        'grants': grants
    })


@app.route('/foundation/<int:ein>')
def foundation_profile(ein):
    """Render the foundation profile page"""
    return render_template('foundation.html', ein=ein)


@app.route('/api/foundation/<int:ein>/stats')
def get_foundation_stats(ein):
    """Get detailed statistics for a foundation including state-by-state breakdown"""
    # Get foundation aggregated data
    foundation_data = supabase_api.get_foundation_aggregated_stats(ein)
    
    if not foundation_data:
        return jsonify({'error': 'Foundation not found'}), 404
    
    # Get all grants for state breakdown and top/recent grants
    all_grants = supabase_api.get_foundation_grants(ein)
    
    # Calculate state-by-state statistics
    states_data = supabase_api.get_foundation_state_breakdown(ein)
    
    # Get top 10 grants (already sorted by amount descending)
    top_grants_list = []
    for grant in all_grants[:10]:
        top_grants_list.append({
            'recipient_name': grant['recipient_name'],
            'recipient_city': grant['recipient_city'],
            'recipient_state': grant['recipient_state'],
            'grant_amount': grant['grant_amount'],
            'grant_purpose': grant['grant_purpose'],
            'tax_period': grant['tax_period']
        })
    
    # Get most recent 10 grants (sort by tax period)
    recent_grants_sorted = sorted(all_grants, key=lambda x: x['tax_period'], reverse=True)
    recent_grants_list = []
    for grant in recent_grants_sorted[:10]:
        recent_grants_list.append({
            'recipient_name': grant['recipient_name'],
            'recipient_city': grant['recipient_city'],
            'recipient_state': grant['recipient_state'],
            'grant_amount': grant['grant_amount'],
            'grant_purpose': grant['grant_purpose'],
            'tax_period': grant['tax_period']
        })
    
    # Get officers
    officers = supabase_api.get_foundation_officers(ein)
    
    # Helper functions to safely get values
    def safe_get(key, default=''):
        val = foundation_data.get(key, default)
        if val is None:
            return default
        return val
    
    def safe_int(key, default=0):
        val = foundation_data.get(key, default)
        if val is None or val == '':
            return default
        try:
            return int(val)
        except (ValueError, TypeError):
            return default
    
    def safe_bool(key):
        val = foundation_data.get(key, False)
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() in ['true', '1', 'x', 't']
        return bool(val)
    
    return jsonify({
        'foundation_name': foundation_data['foundation_name'],
        'foundation_ein': foundation_data['foundation_ein'],
        'grant_count': foundation_data['grant_count'],
        'total_amount': foundation_data['total_amount'],
        'median_grant': foundation_data['median_grant'],
        'avg_grant': foundation_data['avg_grant'],
        'min_grant': foundation_data['min_grant'],
        'max_grant': foundation_data['max_grant'],
        'states_served': foundation_data['states_served'],
        'cities_served': foundation_data['cities_served'],
        'top_purposes': foundation_data['top_purposes'],
        'latest_period': safe_get('latest_period'),
        'primary_state': safe_get('primary_state'),
        'states_data': states_data,
        'top_grants': top_grants_list,
        'recent_grants': recent_grants_list,
        # Foundation-level information
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
        'is_private_operating_foundation': safe_bool('is_private_operating_foundation'),
        'is_501c3': safe_bool('is_501c3'),
        'mission': safe_get('mission_description'),
        # Officers/Directors
        'officers': officers
    })


@app.route('/api/foundation/<int:ein>')
def get_foundation_basic(ein):
    """Get basic foundation information (used for display pages)"""
    # Get foundation data
    foundation_data = supabase_api.get_foundation_aggregated_stats(ein)
    
    if not foundation_data:
        return jsonify({'error': 'Foundation not found'}), 404
    
    return jsonify({
        'foundation_name': foundation_data['foundation_name'],
        'foundation_ein': foundation_data['foundation_ein'],
        'grant_count': foundation_data['grant_count'],
        'total_amount': foundation_data['total_amount'],
    })


if __name__ == '__main__':
    print("Starting Zeffy Grant Finder webapp...")
    print("Connected to Supabase database")
    print("\n" + "="*60)
    print("🚀 Zeffy Grant Finder is running!")
    print("📍 Open your browser and visit: http://localhost:5001")
    print("   • Grant-level view: Search individual grants")
    print("   • Foundation-level view: Browse foundations with stats")
    print("="*60 + "\n")
    app.run(debug=True, port=5001, host='127.0.0.1')
