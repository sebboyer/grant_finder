# Implementation Plan: Foundation-Level View

## Overview
Create a dual-view system where users can toggle between:
1. **Grant-level view** (current): Individual grants displayed as cards
2. **Foundation-level view** (new): Foundations with aggregated statistics

## Data Processing Strategy

### Foundation Aggregation
For each foundation, calculate:
- **Total grants given**: Count of all grants
- **Total amount given**: Sum of all grant amounts
- **Median grant amount**: Middle value of their grants
- **Average grant amount**: Mean of their grants
- **Grant range**: Min and max grant amounts
- **Geographic reach**: States and cities where they give grants
- **Most common grant purpose**: Top 3 purposes by frequency
- **Recent activity**: Tax period information

### Data Structure (Backend)
```python
{
  "foundation_name": "Example Foundation",
  "foundation_ein": "123456789",
  "total_grants": 150,
  "total_amount": 5000000,
  "median_grant": 25000,
  "average_grant": 33333,
  "min_grant": 1000,
  "max_grant": 500000,
  "states_served": ["CA", "NY", "TX"],
  "top_cities": ["Los Angeles", "New York", "Austin"],
  "top_purposes": ["EDUCATION", "HEALTH", "ARTS"],
  "latest_period": "2024-06-30",
  "grants": [...]  // Full grant details for expansion
}
```

## Backend Changes (app.py)

### New Endpoints

1. **GET /api/foundations_aggregated**
   - Returns aggregated foundation data
   - Supports filters:
     - `foundation_name`: Search by name
     - `state`: Foundations that give to this state
     - `min_total`: Minimum total giving amount
     - `max_total`: Maximum total giving amount
     - `min_grants`: Minimum number of grants
     - `min_median`: Minimum median grant amount
   - Returns paginated results

2. **GET /api/foundation/{ein}**
   - Returns detailed info for one foundation
   - Includes all grants with full details

3. **Update /api/stats**
   - Add foundation-level stats
   - Median grants per foundation
   - Average giving per foundation

### Implementation Steps
```python
# 1. On startup, create foundation aggregation
foundations_df = df.groupby(['filer_ein', 'filer_organization_name']).agg({
    'grant_amount': ['count', 'sum', 'median', 'mean', 'min', 'max'],
    'recipient_state': lambda x: list(x.dropna().unique()),
    'recipient_city': lambda x: list(x.dropna().unique())[:5],
    'grant_purpose': lambda x: x.value_counts().head(3).index.tolist(),
    'tax_period_end': 'max'
}).reset_index()

# 2. Create search function for foundations
# 3. Add pagination at foundation level
```

## Frontend Changes

### HTML Structure (templates/index.html)

```html
<header>
  <!-- Existing header -->
  <nav class="view-toggle">
    <button id="grants-view-btn" class="active">Individual Grants</button>
    <button id="foundations-view-btn">Foundations</button>
  </nav>
</header>

<main>
  <!-- Grant-level view (existing) -->
  <div id="grants-view" class="view-container active">
    <!-- Current content -->
  </div>

  <!-- Foundation-level view (new) -->
  <div id="foundations-view" class="view-container hidden">
    <section class="search-section">
      <div class="filters-container">
        <!-- Foundation name -->
        <!-- States they give to -->
        <!-- Total giving range -->
        <!-- Number of grants range -->
        <!-- Median grant range -->
      </div>
    </section>

    <section class="results-section">
      <div id="foundations-container" class="foundations-grid">
        <!-- Foundation cards -->
      </div>
    </section>
  </div>
</main>
```

### Foundation Card Design
```html
<div class="foundation-card">
  <div class="foundation-header">
    <h3>Foundation Name</h3>
    <span class="foundation-ein">EIN: 123456789</span>
  </div>
  
  <div class="foundation-stats">
    <div class="stat">
      <span class="stat-label">Total Grants</span>
      <span class="stat-value">150</span>
    </div>
    <div class="stat">
      <span class="stat-label">Total Given</span>
      <span class="stat-value">$5.0M</span>
    </div>
    <div class="stat">
      <span class="stat-label">Median Grant</span>
      <span class="stat-value">$25,000</span>
    </div>
    <div class="stat">
      <span class="stat-label">Grant Range</span>
      <span class="stat-value">$1K - $500K</span>
    </div>
  </div>

  <div class="foundation-details">
    <div class="detail-item">
      <strong>States:</strong> CA, NY, TX
    </div>
    <div class="detail-item">
      <strong>Focus:</strong> Education, Health, Arts
    </div>
  </div>

  <button class="expand-grants-btn">
    View 150 Grants <span class="arrow">↓</span>
  </button>

  <div class="grants-list hidden">
    <!-- Mini grant cards -->
  </div>
</div>
```

## CSS Simplification (static/style.css)

### Changes to Make

1. **Remove Gradients**
   - Replace gradient backgrounds with solid colors
   - Header: Solid Periwinkle (#5555e7)
   - Buttons: Solid colors with subtle hover effects
   - Text: Remove gradient text effects

2. **Simplified Color Palette**
   - Primary: Periwinkle (#5555e7) - buttons, accents
   - Secondary: Sea foam green (#09cfaf) - badges, tags only
   - Background: Light gray (#f8f9fa)
   - Text: Midnight blue (#0f0e5b)
   - Borders: Light gray (#e0e0e0)

3. **Clean Typography**
   - Remove decorative elements
   - Focus on clear hierarchy
   - More whitespace

4. **Simplified Cards**
   - Remove hover effects with color changes
   - Simple shadow elevation on hover
   - Clean borders
   - More padding

### Example Before/After
```css
/* BEFORE (with gradients) */
.btn-primary {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--dark-blue) 100%);
}

.grant-amount {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* AFTER (simplified) */
.btn-primary {
    background-color: var(--primary-color);
}

.grant-amount {
    color: var(--primary-color);
}
```

## JavaScript Updates (static/script.js)

### New Functions Needed

1. **View Toggle**
   ```javascript
   function switchView(viewName) {
       // Hide all views
       // Show selected view
       // Update URL hash
       // Load appropriate data
   }
   ```

2. **Foundation Search**
   ```javascript
   async function searchFoundations() {
       // Gather foundation-level filters
       // Call /api/foundations_aggregated
       // Render foundation cards
   }
   ```

3. **Foundation Card Rendering**
   ```javascript
   function createFoundationCard(foundation) {
       // Create card with stats
       // Add expand/collapse functionality
       // Render grant list on expand
   }
   ```

4. **Grant List Expansion**
   ```javascript
   function toggleGrantList(foundationEin) {
       // Load grants for foundation if not loaded
       // Animate expansion
       // Show/hide grant list
   }
   ```

## UI/UX Improvements

### Navigation
- Tab-style navigation at top
- Clear active state
- Persistent selection (use URL hash)
- Smooth transitions between views

### Foundation View Features
- Compact foundation cards
- Key metrics prominently displayed
- Expandable grant details
- "Show more" for long lists
- Export/share foundation profile

### Grant View (Existing)
- Keep current functionality
- Simplify visual design
- Remove decorative elements
- Focus on information clarity

## Implementation Order

### Phase 1: Data Aggregation (Backend)
1. ✓ Create foundation aggregation logic
2. ✓ Add `/api/foundations_aggregated` endpoint
3. ✓ Test with various filters
4. ✓ Add `/api/foundation/{ein}` detail endpoint

### Phase 2: UI Simplification (Both Views)
1. ✓ Remove all gradients from CSS
2. ✓ Simplify color usage
3. ✓ Clean up card designs
4. ✓ Reduce decorative elements
5. ✓ Test grant view still works

### Phase 3: Foundation View (Frontend)
1. ✓ Add view toggle navigation
2. ✓ Create foundation filter UI
3. ✓ Build foundation card component
4. ✓ Add expand/collapse for grants
5. ✓ Implement search and pagination

### Phase 4: Testing & Polish
1. ✓ Test both views thoroughly
2. ✓ Ensure data consistency
3. ✓ Mobile responsiveness
4. ✓ Performance optimization
5. ✓ Documentation updates

## Technical Considerations

### Performance
- Pre-aggregate foundation data on startup (20K grants → ~1.7K foundations)
- Cache foundation aggregations
- Lazy load grant details on expansion
- Consider pagination at 20 foundations per page

### Data Consistency
- Ensure filters work correctly at both levels
- Foundation count should match grants when drilling down
- Handle edge cases (foundations with 1 grant, etc.)

### User Experience
- Clear indication of which view is active
- Filters persist when switching views (where applicable)
- Breadcrumb or back button for detail views
- Loading states for data fetching

## Success Metrics

1. ✓ Foundation view loads in < 2 seconds
2. ✓ Both views accessible and functional
3. ✓ Clean, simplified UI with no gradients
4. ✓ Foundation aggregations accurate
5. ✓ Smooth transitions between views
6. ✓ All filters work correctly
7. ✓ Mobile responsive

## Future Enhancements (Out of Scope)

- Compare multiple foundations side-by-side
- Download foundation profiles as PDF
- Advanced analytics (trend over time, geographic heatmap)
- Grant recommendation engine
- Email alerts for matching foundations

