"""
Supabase API functions for grant_finder application.
Replaces CSV-based pandas operations with Supabase queries.
"""

from utils.supabase_client import supabase
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, Counter


def get_foundation_by_ein(ein: int) -> Optional[Dict]:
    """
    Get foundation record by EIN.
    Returns the most recent tax filing for the foundation.
    """
    try:
        response = supabase.table('foundation')\
            .select('*')\
            .eq('ein', str(ein))\
            .order('tax_period_end', desc=True)\
            .limit(1)\
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error fetching foundation by EIN {ein}: {e}")
        return None


def get_all_foundation_eins() -> List[str]:
    """Get all unique foundation organization names for autocomplete."""
    try:
        # Get distinct organization names
        response = supabase.table('foundation')\
            .select('organization_name')\
            .execute()
        
        if response.data:
            # Get unique names
            names = list(set([f['organization_name'] for f in response.data if f.get('organization_name')]))
            return sorted(names)
        return []
    except Exception as e:
        print(f"Error fetching foundation names: {e}")
        return []


def search_grants(
    foundation_name: Optional[str] = None,
    min_amount: Optional[int] = None,
    max_amount: Optional[int] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
    page: int = 1,
    per_page: int = 20
) -> Tuple[List[Dict], int]:
    """
    Search grants with filters and pagination.
    Returns (results, total_count).
    """
    try:
        # Start building query
        query = supabase.table('grants').select('*', count='exact')
        
        # Apply filters
        if foundation_name:
            # Need to join with foundation table to filter by name
            # First get foundation IDs that match the name
            foundation_response = supabase.table('foundation')\
                .select('foundation_id')\
                .ilike('organization_name', f'%{foundation_name}%')\
                .execute()
            
            if foundation_response.data:
                foundation_ids = [f['foundation_id'] for f in foundation_response.data]
                if foundation_ids:
                    # Filter grants by these foundation IDs
                    query = query.in_('foundation_id', foundation_ids)
                else:
                    # No matching foundations, return empty
                    return [], 0
            else:
                return [], 0
        
        if min_amount is not None:
            query = query.gte('grant_amount', min_amount)
        
        if max_amount is not None:
            query = query.lte('grant_amount', max_amount)
        
        if state:
            query = query.eq('recipient_state', state.upper())
        
        if city:
            query = query.ilike('recipient_city', f'%{city}%')
        
        # Sort by grant amount descending
        query = query.order('grant_amount', desc=True)
        
        # Get total count first (before pagination)
        count_response = query.execute()
        total_count = count_response.count if hasattr(count_response, 'count') else len(count_response.data)
        
        # Apply pagination
        start_idx = (page - 1) * per_page
        query = query.range(start_idx, start_idx + per_page - 1)
        
        response = query.execute()
        
        if not response.data:
            return [], 0
        
        # Now we need to enrich with foundation names
        # Get unique foundation IDs from results
        foundation_ids = list(set([g['foundation_id'] for g in response.data]))
        
        # Fetch foundation names
        foundation_map = {}
        if foundation_ids:
            foundation_response = supabase.table('foundation')\
                .select('foundation_id, ein, organization_name')\
                .in_('foundation_id', foundation_ids)\
                .execute()
            
            if foundation_response.data:
                for f in foundation_response.data:
                    foundation_map[f['foundation_id']] = {
                        'name': f['organization_name'],
                        'ein': f['ein']
                    }
        
        # Format results
        results = []
        for grant in response.data:
            foundation_info = foundation_map.get(grant['foundation_id'], {})
            results.append({
                'foundation_name': foundation_info.get('name', ''),
                'foundation_ein': foundation_info.get('ein', ''),
                'recipient_name': grant.get('recipient_name', ''),
                'recipient_city': grant.get('recipient_city', ''),
                'recipient_state': grant.get('recipient_state', ''),
                'recipient_relationship': grant.get('recipient_relationship', ''),
                'recipient_foundation_status': grant.get('recipient_foundation_status', ''),
                'grant_amount': int(grant.get('grant_amount', 0)) if grant.get('grant_amount') else 0,
                'cash_amount': int(grant.get('cash_grant_amount', 0)) if grant.get('cash_grant_amount') else 0,
                'non_cash_amount': int(grant.get('non_cash_grant_amount', 0)) if grant.get('non_cash_grant_amount') else 0,
                'grant_purpose': grant.get('grant_purpose', 'No purpose specified') or 'No purpose specified',
                'tax_period': str(grant.get('tax_period_end', ''))
            })
        
        return results, total_count
        
    except Exception as e:
        print(f"Error searching grants: {e}")
        return [], 0


def get_stats() -> Dict:
    """Get global statistics about all grants and foundations."""
    try:
        # Get total grants and sum
        grants_response = supabase.table('grants')\
            .select('grant_amount', count='exact')\
            .execute()
        
        total_grants = grants_response.count if hasattr(grants_response, 'count') else len(grants_response.data)
        
        # Calculate statistics from grant amounts
        grant_amounts = [g['grant_amount'] for g in grants_response.data if g.get('grant_amount')]
        
        if grant_amounts:
            total_amount = sum(grant_amounts)
            avg_grant = total_amount / len(grant_amounts) if grant_amounts else 0
            min_grant = min(grant_amounts)
            max_grant = max(grant_amounts)
        else:
            total_amount = avg_grant = min_grant = max_grant = 0
        
        # Get unique states
        states_response = supabase.table('grants')\
            .select('recipient_state')\
            .execute()
        
        states = sorted(list(set([
            g['recipient_state'] for g in states_response.data 
            if g.get('recipient_state')
        ])))
        
        # Get unique foundations count
        foundations_response = supabase.table('foundation')\
            .select('organization_name')\
            .execute()
        
        unique_foundations = len(set([
            f['organization_name'] for f in foundations_response.data 
            if f.get('organization_name')
        ]))
        
        # Calculate foundation-level stats (need to aggregate grants per foundation)
        foundation_grants = defaultdict(list)
        for grant in grants_response.data:
            if grant.get('grant_amount') and grant.get('foundation_id'):
                foundation_grants[grant['foundation_id']].append(grant['grant_amount'])
        
        grants_per_foundation = [len(grants) for grants in foundation_grants.values()]
        totals_per_foundation = [sum(grants) for grants in foundation_grants.values()]
        
        return {
            'total_grants': total_grants,
            'total_foundations': unique_foundations,
            'total_amount': int(total_amount),
            'avg_grant': int(avg_grant),
            'min_grant': int(min_grant),
            'max_grant': int(max_grant),
            'states': states,
            'avg_grants_per_foundation': int(sum(grants_per_foundation) / len(grants_per_foundation)) if grants_per_foundation else 0,
            'median_grants_per_foundation': int(sorted(grants_per_foundation)[len(grants_per_foundation) // 2]) if grants_per_foundation else 0,
            'avg_total_per_foundation': int(sum(totals_per_foundation) / len(totals_per_foundation)) if totals_per_foundation else 0,
            'median_total_per_foundation': int(sorted(totals_per_foundation)[len(totals_per_foundation) // 2]) if totals_per_foundation else 0
        }
        
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {
            'total_grants': 0,
            'total_foundations': 0,
            'total_amount': 0,
            'avg_grant': 0,
            'min_grant': 0,
            'max_grant': 0,
            'states': [],
            'avg_grants_per_foundation': 0,
            'median_grants_per_foundation': 0,
            'avg_total_per_foundation': 0,
            'median_total_per_foundation': 0
        }


def get_foundation_officers(ein: int) -> List[Dict]:
    """Get list of officers/directors for a foundation by EIN."""
    try:
        # First get foundation by EIN
        foundation = get_foundation_by_ein(ein)
        if not foundation:
            return []
        
        foundation_id = foundation['foundation_id']
        
        # Get leaders for this foundation
        response = supabase.table('Leaders')\
            .select('*')\
            .eq('foundation_id', foundation_id)\
            .execute()
        
        if not response.data:
            return []
        
        officers_list = []
        for officer in response.data:
            # Calculate total compensation
            total_comp = 0
            compensation = officer.get('compensation', 0) or 0
            benefits = officer.get('benefits', 0) or 0
            other_comp = officer.get('other_compensation', 0) or 0
            
            if compensation:
                total_comp += float(compensation)
            if benefits:
                total_comp += float(benefits)
            if other_comp:
                total_comp += float(other_comp)
            
            officers_list.append({
                'name': officer.get('person_name', ''),
                'title': officer.get('title', ''),
                'compensation': int(compensation) if compensation else 0,
                'total_compensation': int(total_comp) if total_comp > 0 else 0,
                'hours_per_week': float(officer.get('hours_per_week', 0)) if officer.get('hours_per_week') else 0,
                'is_paid': total_comp > 0
            })
        
        # Sort by compensation (highest first), then by title
        officers_list.sort(key=lambda x: (-x['total_compensation'], x['title']))
        
        return officers_list
        
    except Exception as e:
        print(f"Error getting foundation officers for EIN {ein}: {e}")
        return []


def get_foundation_aggregated_stats(ein: int) -> Optional[Dict]:
    """
    Get aggregated statistics for a single foundation.
    Includes grant counts, totals, medians, states served, etc.
    """
    try:
        # Get foundation record
        foundation = get_foundation_by_ein(ein)
        if not foundation:
            return None
        
        foundation_id = foundation['foundation_id']
        
        # Get all grants for this foundation
        grants_response = supabase.table('grants')\
            .select('*')\
            .eq('foundation_id', foundation_id)\
            .execute()
        
        if not grants_response.data:
            return None
        
        grants = grants_response.data
        grant_amounts = [g['grant_amount'] for g in grants if g.get('grant_amount')]
        
        if not grant_amounts:
            return None
        
        # Calculate aggregations
        grant_count = len(grant_amounts)
        total_amount = sum(grant_amounts)
        avg_grant = total_amount / grant_count
        min_grant = min(grant_amounts)
        max_grant = max(grant_amounts)
        
        # Calculate median
        sorted_amounts = sorted(grant_amounts)
        median_grant = sorted_amounts[len(sorted_amounts) // 2]
        
        # Get unique states and cities
        states = list(set([g['recipient_state'] for g in grants if g.get('recipient_state')]))
        cities = list(set([g['recipient_city'] for g in grants if g.get('recipient_city')]))[:10]
        
        # Get top purposes (top 3)
        purposes = [g['grant_purpose'] for g in grants if g.get('grant_purpose')]
        purpose_counts = Counter(purposes)
        top_purposes = [purpose for purpose, count in purpose_counts.most_common(3)]
        
        # Get latest period
        periods = [g['tax_period_end'] for g in grants if g.get('tax_period_end')]
        latest_period = max(periods) if periods else ''
        
        # Calculate primary state (state with highest total grant amount)
        state_totals = defaultdict(float)
        for grant in grants:
            if grant.get('recipient_state') and grant.get('grant_amount'):
                state_totals[grant['recipient_state']] += grant['grant_amount']
        
        primary_state = max(state_totals.items(), key=lambda x: x[1])[0] if state_totals else ''
        
        return {
            'foundation_id': foundation_id,
            'foundation_ein': int(foundation['ein']),
            'foundation_name': foundation['organization_name'],
            'grant_count': grant_count,
            'total_amount': int(total_amount),
            'median_grant': int(median_grant),
            'avg_grant': int(avg_grant),
            'min_grant': int(min_grant),
            'max_grant': int(max_grant),
            'states_served': states,
            'cities_served': cities,
            'top_purposes': top_purposes,
            'latest_period': str(latest_period),
            'primary_state': primary_state,
            # Include foundation-level data
            'formation_year': foundation.get('formation_year', ''),
            'foundation_address_line1': foundation.get('address_line1', ''),
            'foundation_address_line2': foundation.get('address_line2', ''),
            'foundation_city': foundation.get('city', ''),
            'foundation_state': foundation.get('state', ''),
            'foundation_zip': foundation.get('zip', ''),
            'foundation_phone': foundation.get('phone', ''),
            'foundation_website': foundation.get('website', ''),
            'legal_domicile_state': foundation.get('legal_domicile_state', ''),
            'total_assets_eoy': foundation.get('total_assets_eoy'),
            'fair_market_value_eoy': foundation.get('fair_market_value_eoy'),
            'total_revenue': foundation.get('total_revenue'),
            'total_expenses': foundation.get('total_expenses'),
            'total_distributions': foundation.get('total_distributions'),
            'investment_income': foundation.get('investment_income'),
            'is_private_operating_foundation': foundation.get('is_private_operating_foundation', False),
            'is_501c3': foundation.get('is_501c3', False),
            'mission_description': foundation.get('mission_description', '')
        }
        
    except Exception as e:
        print(f"Error getting aggregated stats for EIN {ein}: {e}")
        return None


def get_all_foundations_aggregated(
    foundation_name: Optional[str] = None,
    state: Optional[str] = None,
    min_total: Optional[int] = None,
    max_total: Optional[int] = None,
    min_grants: Optional[int] = None,
    min_median: Optional[int] = None,
    max_median: Optional[int] = None,
    page: int = 1,
    per_page: int = 20
) -> Tuple[List[Dict], int]:
    """
    Get all foundations with aggregated grant statistics.
    Returns (results, total_count).
    """
    try:
        # Get all foundations
        foundations_query = supabase.table('foundation').select('*')
        
        if foundation_name:
            foundations_query = foundations_query.ilike('organization_name', f'%{foundation_name}%')
        
        foundations_response = foundations_query.execute()
        
        if not foundations_response.data:
            return [], 0
        
        # Get all grants
        grants_response = supabase.table('grants')\
            .select('foundation_id, grant_amount, recipient_state, recipient_city, grant_purpose, tax_period_end')\
            .execute()
        
        # Group grants by foundation
        foundation_grants = defaultdict(list)
        for grant in grants_response.data:
            if grant.get('foundation_id') and grant.get('grant_amount'):
                foundation_grants[grant['foundation_id']].append(grant)
        
        # Build aggregated data for each foundation
        aggregated = []
        for foundation in foundations_response.data:
            foundation_id = foundation['foundation_id']
            grants = foundation_grants.get(foundation_id, [])
            
            if not grants:
                continue
            
            grant_amounts = [g['grant_amount'] for g in grants]
            grant_count = len(grant_amounts)
            total_amount = sum(grant_amounts)
            avg_grant = total_amount / grant_count
            min_grant = min(grant_amounts)
            max_grant = max(grant_amounts)
            sorted_amounts = sorted(grant_amounts)
            median_grant = sorted_amounts[len(sorted_amounts) // 2]
            
            # Get unique states and cities
            states = list(set([g['recipient_state'] for g in grants if g.get('recipient_state')]))
            cities = list(set([g['recipient_city'] for g in grants if g.get('recipient_city')]))[:10]
            
            # Get top purposes
            purposes = [g['grant_purpose'] for g in grants if g.get('grant_purpose')]
            purpose_counts = Counter(purposes)
            top_purposes = [purpose for purpose, count in purpose_counts.most_common(3)]
            
            # Latest period
            periods = [g['tax_period_end'] for g in grants if g.get('tax_period_end')]
            latest_period = max(periods) if periods else ''
            
            # Primary state
            state_totals = defaultdict(float)
            for grant in grants:
                if grant.get('recipient_state') and grant.get('grant_amount'):
                    state_totals[grant['recipient_state']] += grant['grant_amount']
            primary_state = max(state_totals.items(), key=lambda x: x[1])[0] if state_totals else ''
            
            # Apply filters
            if state and state not in states:
                continue
            if min_total is not None and total_amount < min_total:
                continue
            if max_total is not None and total_amount > max_total:
                continue
            if min_grants is not None and grant_count < min_grants:
                continue
            if min_median is not None and median_grant < min_median:
                continue
            if max_median is not None and median_grant > max_median:
                continue
            
            aggregated.append({
                'filer_ein': int(foundation['ein']),
                'filer_organization_name': foundation['organization_name'],
                'grant_count': grant_count,
                'total_amount': int(total_amount),
                'median_grant': int(median_grant),
                'avg_grant': int(avg_grant),
                'min_grant': int(min_grant),
                'max_grant': int(max_grant),
                'states_served': states,
                'cities_served': cities,
                'top_purposes': top_purposes,
                'latest_period': str(latest_period),
                'primary_state': primary_state
            })
        
        # Sort by total amount descending
        aggregated.sort(key=lambda x: x['total_amount'], reverse=True)
        
        # Pagination
        total_count = len(aggregated)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_results = aggregated[start_idx:end_idx]
        
        return page_results, total_count
        
    except Exception as e:
        print(f"Error getting all foundations aggregated: {e}")
        return [], 0


def get_foundation_grants(ein: int) -> List[Dict]:
    """Get all grants for a specific foundation."""
    try:
        foundation = get_foundation_by_ein(ein)
        if not foundation:
            return []
        
        foundation_id = foundation['foundation_id']
        
        # Get all grants
        response = supabase.table('grants')\
            .select('*')\
            .eq('foundation_id', foundation_id)\
            .order('grant_amount', desc=True)\
            .execute()
        
        if not response.data:
            return []
        
        grants = []
        for grant in response.data:
            grants.append({
                'recipient_name': grant.get('recipient_name', ''),
                'recipient_ein': grant.get('recipient_ein', ''),
                'recipient_city': grant.get('recipient_city', ''),
                'recipient_state': grant.get('recipient_state', ''),
                'recipient_relationship': grant.get('recipient_relationship', ''),
                'recipient_foundation_status': grant.get('recipient_foundation_status', ''),
                'grant_amount': int(grant.get('grant_amount', 0)) if grant.get('grant_amount') else 0,
                'cash_amount': int(grant.get('cash_grant_amount', 0)) if grant.get('cash_grant_amount') else 0,
                'non_cash_amount': int(grant.get('non_cash_grant_amount', 0)) if grant.get('non_cash_grant_amount') else 0,
                'grant_purpose': grant.get('grant_purpose', 'No purpose specified') or 'No purpose specified',
                'tax_period': str(grant.get('tax_period_end', ''))
            })
        
        return grants
        
    except Exception as e:
        print(f"Error getting foundation grants for EIN {ein}: {e}")
        return []


def get_foundation_state_breakdown(ein: int) -> List[Dict]:
    """Get state-by-state breakdown of grants for a foundation."""
    try:
        foundation = get_foundation_by_ein(ein)
        if not foundation:
            return []
        
        foundation_id = foundation['foundation_id']
        
        # Get all grants for this foundation
        response = supabase.table('grants')\
            .select('recipient_state, grant_amount')\
            .eq('foundation_id', foundation_id)\
            .execute()
        
        if not response.data:
            return []
        
        # Group by state
        state_data = defaultdict(lambda: {'grants': [], 'count': 0})
        for grant in response.data:
            state = grant.get('recipient_state')
            amount = grant.get('grant_amount')
            if state and amount:
                state_data[state]['grants'].append(amount)
                state_data[state]['count'] += 1
        
        # Calculate statistics for each state
        states_list = []
        for state, data in state_data.items():
            grants = data['grants']
            total = sum(grants)
            avg = total / len(grants)
            sorted_grants = sorted(grants)
            median = sorted_grants[len(sorted_grants) // 2]
            
            states_list.append({
                'state': state,
                'grant_count': data['count'],
                'total_amount': int(total),
                'avg_grant': int(avg),
                'median_grant': int(median)
            })
        
        # Sort by grant count descending
        states_list.sort(key=lambda x: x['grant_count'], reverse=True)
        
        return states_list
        
    except Exception as e:
        print(f"Error getting state breakdown for EIN {ein}: {e}")
        return []

