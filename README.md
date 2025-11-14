# Zeffy Grant Finder

A Flask web application that helps users discover foundations and the grants they award, powered by IRS Form 990 data.

## Features

### Dual View Interface
- **Individual Grants View**: Search and filter specific grants by foundation name, recipient state/city, and grant amount
- **Foundations View**: Browse foundations by giving patterns, total donations, median grant size, and geographic focus

### Foundation Profiles
Detailed foundation pages include:
- Key statistics (assets, average grant size, total grants)
- Financial overview with detailed breakdowns
- Comprehensive grants table with search and sorting
- Interactive US map showing geographic distribution
- Leadership and staff information with compensation data

### Data Source
All data is sourced from IRS Form 990 filings, providing transparent insight into:
- Grant amounts and purposes
- Foundation financials (assets, revenue, expenses)
- Geographic giving patterns
- Leadership compensation

## Project Structure

```
grant_finder/
├── app.py                              # Flask application
├── requirements.txt                    # Python dependencies
├── public/                             # Static assets (Vercel CDN)
│   ├── style.css                      # Application styles
│   ├── script.js                      # Client-side functionality
│   ├── zeffy-logo-white.png
│   └── zeffy-logo.png
├── templates/                          # Jinja2 templates
│   ├── index.html                     # Main search page
│   └── foundation.html                # Foundation profile page
├── grants_information_summary.csv      # Grants data
├── foundations_information_summary.csv # Foundation data
└── officers_information_summary.csv    # Leadership data
```

## Installation & Local Development

### Prerequisites
- Python 3.9+
- pip

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser:
```
http://localhost:5000
```

## Deployment

This application is ready for deployment to Vercel with zero configuration required.

See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy
```bash
vercel deploy
```

## API Endpoints

### Main Routes
- `GET /` - Homepage with dual view search
- `GET /foundation/<ein>` - Foundation profile page

### API Endpoints
- `GET /api/grants` - Get all grants data
- `POST /api/grants/search` - Search grants with filters
- `GET /api/foundations` - Get all foundations data
- `POST /api/foundations/search` - Search foundations with filters
- `GET /api/foundation/<ein>/stats` - Get detailed foundation statistics
- `GET /api/states` - Get all states with grant counts

## Features in Detail

### Search & Filtering
**Grants View:**
- Foundation name (autocomplete)
- Recipient state
- Recipient city
- Grant amount range (min/max)

**Foundations View:**
- Foundation name (autocomplete)
- States they give to
- Minimum number of grants
- Total giving range
- Median grant range

### Foundation Profile Tabs
1. **Overview** - Key stats, contact info, about section
2. **Financials** - Assets, revenue, expenses, distributions
3. **Grants** - Searchable/sortable table, geographic map
4. **People** - Leadership and staff compensation

### Data Processing
The app loads and preprocesses CSV data on startup:
- Numeric conversions for all financial fields
- Foundation-level aggregations
- Geographic data compilation
- Top purposes analysis

## Technology Stack

- **Backend**: Flask 3.0
- **Data Processing**: pandas, numpy
- **Frontend**: Vanilla JavaScript
- **Visualization**: D3.js for geographic mapping
- **Styling**: Custom CSS with Zeffy branding

## Data Files

### Required CSV Files
1. **grants_information_summary.csv**
   - Individual grant records
   - Fields: EIN, foundation name, recipient info, amounts, purposes

2. **foundations_information_summary.csv**
   - Foundation financial data
   - Fields: Assets, revenue, expenses, distributions, contact info

3. **officers_information_summary.csv**
   - Leadership information
   - Fields: Name, title, compensation, hours per week

## Configuration

The app runs on port 5000 by default. To change:
```python
if __name__ == '__main__':
    app.run(debug=True, port=YOUR_PORT)
```

## Performance

- Client-side pagination (100 results per page)
- Efficient data loading with pandas
- Lazy loading for foundation profiles
- Interactive map loads on demand

## Security

- Input sanitization for all search queries
- XSS protection in templates
- Secure headers via Flask defaults
- HTTPS enforced on Vercel deployment

## License

© 2025 Zeffy. All rights reserved.

## Support

For issues or questions about the Grant Finder application, please contact the Zeffy development team.


