# Grant Finder Web Application

A modern, minimalist web application for searching and discovering foundation grants, designed with Zeffy brand guidelines.

## Features

- 🔍 **Smart Search**: Search by foundation name with autocomplete
- 📍 **Location Filters**: Filter grants by state and city
- 💰 **Amount Range**: Set minimum and maximum grant amounts
- 🎨 **Zeffy Brand Design**: Beautiful UI following Zeffy's brand guidelines
  - Periwinkle (#5555e7) and Sea foam green (#09cfaf) color scheme
  - Poppins typography
  - Rounded corners and organic shapes
  - Wind-inspired decorative elements

## Quick Start

### 1. Install Dependencies

```bash
cd grant_finder
source venv/bin/activate
pip install Flask pandas Werkzeug
```

### 2. Run the Application

```bash
python app.py
```

### 3. Open in Browser

Visit: **http://localhost:5001**

## Data

The application uses `grants_information_summary.csv` which contains:
- **20,998 grants** from **1,687 foundations**
- Total grant amount: **$1.05 billion**

## API Endpoints

### Get Statistics
```
GET /api/stats
```
Returns database statistics including total grants, foundations, and available states.

### Search Grants
```
GET /api/search?foundation=NAME&state=STATE&min_amount=MIN&max_amount=MAX&city=CITY
```
Search grants with optional filters. Supports pagination.

### Foundation Autocomplete
```
GET /api/foundations?q=QUERY
```
Get foundation name suggestions for autocomplete.

## Design Features

### Colors
- **Periwinkle** (#5555e7): Primary actions and text
- **Sea foam green** (#09cfaf): Accents and decorative elements
- **Midnight blue** (#0f0e5b): Dark text and gradients

### Typography
- **Poppins** font family (Medium, Semi-Bold, Bold)
- Clear hierarchy with appropriate font weights

### UI Elements
- Rounded corners (12-20px border radius)
- Smooth transitions and hover effects
- Gradient backgrounds with brand colors
- Organic wave decorations
- Card-based grant display with hover animations

## File Structure

```
grant_finder/
├── app.py                           # Flask backend
├── grants_information_summary.csv   # Data source
├── templates/
│   └── index.html                  # Main HTML template
├── static/
│   ├── style.css                   # Zeffy-branded styles
│   └── script.js                   # Frontend JavaScript
└── requirements_webapp.txt         # Python dependencies
```

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Responsive design for mobile and desktop
- Optimized for performance with 20K+ records

## Development

The application runs in debug mode by default. For production deployment:

1. Set `debug=False` in `app.py`
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure proper environment variables

## Notes

- Port 5001 is used to avoid conflicts with macOS AirPlay (which uses 5000)
- The app automatically loads all grant data on startup
- Search results are paginated (20 per page) for performance

---

Built with ❤️ following Zeffy brand guidelines

