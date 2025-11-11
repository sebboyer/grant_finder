// Global state
let currentView = 'grants';
let grantsCurrentPage = 1;
let foundationsCurrentPage = 1;
let grantsFilters = {};
let foundationsFilters = {};
let debounceTimer;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadStates();
    setupGrantsEventListeners();
    setupFoundationsEventListeners();
    
    // Load initial data for grants view
    performGrantsSearch();
});

// ===== VIEW SWITCHING =====

function switchView(viewName) {
    currentView = viewName;
    
    // Hide all views
    document.querySelectorAll('.view-container').forEach(view => {
        view.classList.remove('active');
    });
    
    // Show selected view
    document.getElementById(`${viewName}-view`).classList.add('active');
    
    // Update button states
    document.querySelectorAll('.view-toggle button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`${viewName}-view-btn`).classList.add('active');
    
    // Load data for the view if not already loaded
    if (viewName === 'foundations' && document.getElementById('foundations-results-container').children.length === 0) {
        performFoundationsSearch();
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ===== STATS LOADING =====

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        // Grants view summary
        const grantsSummary = `${stats.total_grants.toLocaleString()} grants • ${stats.total_foundations.toLocaleString()} foundations • $${(stats.total_amount / 1000000000).toFixed(1)}B total`;
        document.getElementById('grants-stats-summary').textContent = grantsSummary;
        
        // Foundations view summary
        const foundationsSummary = `${stats.total_foundations.toLocaleString()} foundations • Avg ${stats.avg_grants_per_foundation} grants/foundation • Median $${(stats.median_total_per_foundation / 1000).toLocaleString()}K total`;
        document.getElementById('foundations-stats-summary').textContent = foundationsSummary;
        
        return stats;
    } catch (error) {
        console.error('Error loading stats:', error);
        document.getElementById('grants-stats-summary').textContent = 'Database ready';
        document.getElementById('foundations-stats-summary').textContent = 'Database ready';
    }
}

async function loadStates() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        // Populate both state dropdowns
        const grantsStateSelect = document.getElementById('grants-state-filter');
        const foundationsStateSelect = document.getElementById('foundations-state-filter');
        
        data.states.forEach(state => {
            if (state) {
                const option1 = document.createElement('option');
                option1.value = state;
                option1.textContent = state;
                grantsStateSelect.appendChild(option1);
                
                const option2 = document.createElement('option');
                option2.value = state;
                option2.textContent = state;
                foundationsStateSelect.appendChild(option2);
            }
        });
    } catch (error) {
        console.error('Error loading states:', error);
    }
}

// ===== GRANTS VIEW =====

function setupGrantsEventListeners() {
    // Search button
    document.getElementById('grants-search-btn').addEventListener('click', () => {
        grantsCurrentPage = 1;
        performGrantsSearch();
    });

    // Clear button
    document.getElementById('grants-clear-btn').addEventListener('click', clearGrantsFilters);

    // Enter key on inputs
    const inputs = ['grants-foundation-search', 'grants-city-filter', 'grants-min-amount', 'grants-max-amount'];
    inputs.forEach(id => {
        const element = document.getElementById(id);
        element.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                grantsCurrentPage = 1;
                performGrantsSearch();
            }
        });
    });

    // State filter change
    document.getElementById('grants-state-filter').addEventListener('change', () => {
        grantsCurrentPage = 1;
        performGrantsSearch();
    });

    // Foundation name autocomplete
    const foundationInput = document.getElementById('grants-foundation-search');
    foundationInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            if (e.target.value.length >= 2) {
                fetchFoundationSuggestions(e.target.value, 'grants');
            } else {
                hideSuggestions('grants');
            }
        }, 300);
    });

    // Click outside to close suggestions
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.filter-group')) {
            hideSuggestions('grants');
        }
    });
}

function clearGrantsFilters() {
    document.getElementById('grants-foundation-search').value = '';
    document.getElementById('grants-state-filter').value = '';
    document.getElementById('grants-city-filter').value = '';
    document.getElementById('grants-min-amount').value = '';
    document.getElementById('grants-max-amount').value = '';
    grantsCurrentPage = 1;
    performGrantsSearch();
}

async function performGrantsSearch() {
    // Gather filters
    grantsFilters = {
        foundation: document.getElementById('grants-foundation-search').value,
        state: document.getElementById('grants-state-filter').value,
        city: document.getElementById('grants-city-filter').value,
        min_amount: document.getElementById('grants-min-amount').value,
        max_amount: document.getElementById('grants-max-amount').value,
        page: grantsCurrentPage,
        per_page: 20
    };

    // Remove empty filters
    Object.keys(grantsFilters).forEach(key => {
        if (!grantsFilters[key]) {
            delete grantsFilters[key];
        }
    });

    // Show loading
    showLoading('grants');

    try {
        const queryString = new URLSearchParams(grantsFilters).toString();
        const response = await fetch(`/api/search?${queryString}`);
        const data = await response.json();
        
        displayGrantsResults(data);
        displayPagination(data, 'grants');
    } catch (error) {
        console.error('Error performing grants search:', error);
        showError('grants');
    }
}

function displayGrantsResults(data) {
    const resultsContainer = document.getElementById('grants-results-container');
    const resultsCount = document.getElementById('grants-results-count');
    const loadingIndicator = document.getElementById('grants-loading-indicator');
    
    loadingIndicator.style.display = 'none';
    resultsContainer.style.display = 'grid';
    
    // Update count
    resultsCount.textContent = `${data.total.toLocaleString()} grants found`;
    
    // Clear previous results
    resultsContainer.innerHTML = '';
    
    if (data.results.length === 0) {
        showEmptyState('grants');
        return;
    }
    
    // Display grant cards
    data.results.forEach(grant => {
        const card = createGrantCard(grant);
        resultsContainer.appendChild(card);
    });
}

function createGrantCard(grant) {
    const card = document.createElement('div');
    card.className = 'grant-card';
    
    const location = [grant.recipient_city, grant.recipient_state]
        .filter(Boolean)
        .join(', ') || 'Location not specified';
    
    card.innerHTML = `
        <div class="grant-header">
            <div class="grant-amount">$${grant.grant_amount.toLocaleString()}</div>
            <div class="foundation-name">${escapeHtml(grant.foundation_name)}</div>
        </div>
        
        <div class="grant-divider"></div>
        
        <div class="grant-details">
            <div class="grant-detail-row">
                <span class="detail-label">Recipient:</span>
                <span class="detail-value">${escapeHtml(grant.recipient_name)}</span>
            </div>
            <div class="grant-detail-row">
                <span class="detail-label">Location:</span>
                <span class="detail-value">
                    <span class="location-tag">${escapeHtml(location)}</span>
                </span>
            </div>
            ${grant.tax_period ? `
                <div class="grant-detail-row">
                    <span class="detail-label">Period:</span>
                    <span class="detail-value">${escapeHtml(grant.tax_period)}</span>
                </div>
            ` : ''}
        </div>
        
        <div class="grant-purpose">${escapeHtml(grant.grant_purpose)}</div>
    `;
    
    return card;
}

// ===== FOUNDATIONS VIEW =====

function setupFoundationsEventListeners() {
    // Search button
    document.getElementById('foundations-search-btn').addEventListener('click', () => {
        foundationsCurrentPage = 1;
        performFoundationsSearch();
    });

    // Clear button
    document.getElementById('foundations-clear-btn').addEventListener('click', clearFoundationsFilters);

    // Enter key on inputs
    const inputs = ['foundations-name-search', 'foundations-min-grants', 'foundations-min-total', 
                   'foundations-max-total', 'foundations-min-median', 'foundations-max-median'];
    inputs.forEach(id => {
        const element = document.getElementById(id);
        element.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                foundationsCurrentPage = 1;
                performFoundationsSearch();
            }
        });
    });

    // State filter change
    document.getElementById('foundations-state-filter').addEventListener('change', () => {
        foundationsCurrentPage = 1;
        performFoundationsSearch();
    });

    // Foundation name autocomplete
    const nameInput = document.getElementById('foundations-name-search');
    nameInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            if (e.target.value.length >= 2) {
                fetchFoundationSuggestions(e.target.value, 'foundations');
            } else {
                hideSuggestions('foundations');
            }
        }, 300);
    });
}

function clearFoundationsFilters() {
    document.getElementById('foundations-name-search').value = '';
    document.getElementById('foundations-state-filter').value = '';
    document.getElementById('foundations-min-grants').value = '';
    document.getElementById('foundations-min-total').value = '';
    document.getElementById('foundations-max-total').value = '';
    document.getElementById('foundations-min-median').value = '';
    document.getElementById('foundations-max-median').value = '';
    foundationsCurrentPage = 1;
    performFoundationsSearch();
}

async function performFoundationsSearch() {
    // Gather filters
    foundationsFilters = {
        foundation: document.getElementById('foundations-name-search').value,
        state: document.getElementById('foundations-state-filter').value,
        min_grants: document.getElementById('foundations-min-grants').value,
        min_total: document.getElementById('foundations-min-total').value,
        max_total: document.getElementById('foundations-max-total').value,
        min_median: document.getElementById('foundations-min-median').value,
        max_median: document.getElementById('foundations-max-median').value,
        page: foundationsCurrentPage,
        per_page: 20
    };

    // Remove empty filters
    Object.keys(foundationsFilters).forEach(key => {
        if (!foundationsFilters[key]) {
            delete foundationsFilters[key];
        }
    });

    // Show loading
    showLoading('foundations');

    try {
        const queryString = new URLSearchParams(foundationsFilters).toString();
        const response = await fetch(`/api/foundations_aggregated?${queryString}`);
        const data = await response.json();
        
        displayFoundationsResults(data);
        displayPagination(data, 'foundations');
    } catch (error) {
        console.error('Error performing foundations search:', error);
        showError('foundations');
    }
}

function displayFoundationsResults(data) {
    const resultsContainer = document.getElementById('foundations-results-container');
    const resultsCount = document.getElementById('foundations-results-count');
    const loadingIndicator = document.getElementById('foundations-loading-indicator');
    
    loadingIndicator.style.display = 'none';
    resultsContainer.style.display = 'grid';
    
    // Update count
    resultsCount.textContent = `${data.total.toLocaleString()} foundations found`;
    
    // Clear previous results
    resultsContainer.innerHTML = '';
    
    if (data.results.length === 0) {
        showEmptyState('foundations');
        return;
    }
    
    // Display foundation cards
    data.results.forEach(foundation => {
        const card = createFoundationCard(foundation);
        resultsContainer.appendChild(card);
    });
}

function createFoundationCard(foundation) {
    const card = document.createElement('div');
    card.className = 'foundation-card';
    card.style.cursor = 'pointer';
    
    const statesBadges = foundation.states_served.slice(0, 8).map(state => 
        `<span class="state-badge">${escapeHtml(state)}</span>`
    ).join('');
    
    const moreStates = foundation.states_served.length > 8 ? 
        `<span class="state-badge">+${foundation.states_served.length - 8} more</span>` : '';
    
    const purposeTags = foundation.top_purposes.slice(0, 3).map(purpose => 
        `<span class="purpose-tag">${escapeHtml(purpose.substring(0, 30))}</span>`
    ).join('');
    
    card.innerHTML = `
        <div class="foundation-header">
            <h3 class="foundation-name">${escapeHtml(foundation.foundation_name)}</h3>
            <div class="foundation-ein">EIN: ${foundation.foundation_ein}</div>
            ${foundation.primary_state ? `
                <div class="primary-state-tag">
                    <span class="primary-state-icon">📍</span>
                    <span class="primary-state-label">Primary State of Activity:</span>
                    <span class="primary-state-value">${escapeHtml(foundation.primary_state)}</span>
                </div>
            ` : ''}
        </div>
        
        <div class="foundation-stats">
            <div class="stat">
                <div class="stat-label">Total Grants</div>
                <div class="stat-value">${foundation.grant_count.toLocaleString()}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Total Given</div>
                <div class="stat-value">$${formatLargeNumber(foundation.total_amount)}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Median Grant</div>
                <div class="stat-value secondary">$${foundation.median_grant.toLocaleString()}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Grant Range</div>
                <div class="stat-value">$${formatNumber(foundation.min_grant)} - $${formatNumber(foundation.max_grant)}</div>
            </div>
        </div>
        
        <div class="foundation-details">
            ${foundation.states_served.length > 0 ? `
                <div class="detail-item">
                    <strong>Geographic Reach:</strong><br>
                    ${statesBadges}${moreStates}
                </div>
            ` : ''}
            ${foundation.top_purposes.length > 0 ? `
                <div class="detail-item">
                    <strong>Focus Areas:</strong><br>
                    ${purposeTags}
                </div>
            ` : ''}
        </div>
        
        <button class="expand-grants-btn">
            View Full Profile <span class="arrow">→</span>
        </button>
    `;
    
    // Add click event to navigate to profile page
    card.addEventListener('click', () => {
        window.location.href = `/foundation/${foundation.foundation_ein}`;
    });
    
    return card;
}

// ===== SHARED FUNCTIONS =====

async function fetchFoundationSuggestions(query, view) {
    try {
        const response = await fetch(`/api/foundations?q=${encodeURIComponent(query)}`);
        const foundations = await response.json();
        showSuggestions(foundations, view);
    } catch (error) {
        console.error('Error fetching suggestions:', error);
    }
}

function showSuggestions(foundations, view) {
    const dropdown = document.getElementById(`${view}-foundation-suggestions`) || 
                     document.getElementById(`${view}-name-suggestions`);
    dropdown.innerHTML = '';
    
    if (foundations.length === 0) {
        dropdown.classList.remove('show');
        return;
    }
    
    foundations.forEach(foundation => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.textContent = foundation;
        item.addEventListener('click', () => {
            const input = document.getElementById(`${view}-foundation-search`) || 
                         document.getElementById(`${view}-name-search`);
            input.value = foundation;
            hideSuggestions(view);
            
            if (view === 'grants') {
                grantsCurrentPage = 1;
                performGrantsSearch();
            } else {
                foundationsCurrentPage = 1;
                performFoundationsSearch();
            }
        });
        dropdown.appendChild(item);
    });
    
    dropdown.classList.add('show');
}

function hideSuggestions(view) {
    const dropdown1 = document.getElementById(`${view}-foundation-suggestions`);
    const dropdown2 = document.getElementById(`${view}-name-suggestions`);
    if (dropdown1) dropdown1.classList.remove('show');
    if (dropdown2) dropdown2.classList.remove('show');
}

function displayPagination(data, view) {
    const paginationContainer = document.getElementById(`${view}-pagination-container`);
    paginationContainer.style.display = 'flex';
    paginationContainer.innerHTML = '';
    
    if (data.total_pages <= 1) {
        return;
    }
    
    const currentPage = view === 'grants' ? grantsCurrentPage : foundationsCurrentPage;
    
    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '← Previous';
    prevBtn.disabled = currentPage === 1;
    prevBtn.addEventListener('click', () => {
        if (view === 'grants') {
            grantsCurrentPage--;
            performGrantsSearch();
        } else {
            foundationsCurrentPage--;
            performFoundationsSearch();
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    paginationContainer.appendChild(prevBtn);
    
    // Page info
    const pageInfo = document.createElement('div');
    pageInfo.className = 'page-info';
    pageInfo.textContent = `Page ${currentPage} of ${data.total_pages}`;
    paginationContainer.appendChild(pageInfo);
    
    // Page buttons (show current page and a few around it)
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(data.total_pages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = i === currentPage ? 'active' : '';
        pageBtn.addEventListener('click', () => {
            if (view === 'grants') {
                grantsCurrentPage = i;
                performGrantsSearch();
            } else {
                foundationsCurrentPage = i;
                performFoundationsSearch();
            }
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        paginationContainer.insertBefore(pageBtn, pageInfo.nextSibling);
    }
    
    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Next →';
    nextBtn.disabled = currentPage === data.total_pages;
    nextBtn.addEventListener('click', () => {
        if (view === 'grants') {
            grantsCurrentPage++;
            performGrantsSearch();
        } else {
            foundationsCurrentPage++;
            performFoundationsSearch();
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    paginationContainer.appendChild(nextBtn);
}

function showLoading(view) {
    document.getElementById(`${view}-loading-indicator`).style.display = 'block';
    document.getElementById(`${view}-results-container`).style.display = 'none';
    document.getElementById(`${view}-pagination-container`).style.display = 'none';
}

function showEmptyState(view) {
    const resultsContainer = document.getElementById(`${view}-results-container`);
    resultsContainer.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">🔍</div>
            <h3>No ${view} found</h3>
            <p>Try adjusting your filters to see more results</p>
        </div>
    `;
}

function showError(view) {
    document.getElementById(`${view}-loading-indicator`).style.display = 'none';
    const resultsContainer = document.getElementById(`${view}-results-container`);
    resultsContainer.style.display = 'block';
    resultsContainer.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">⚠️</div>
            <h3>Something went wrong</h3>
            <p>Please try again later</p>
        </div>
    `;
}

// ===== UTILITY FUNCTIONS =====

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatLargeNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
}

function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(0) + 'K';
    }
    return num.toLocaleString();
}
