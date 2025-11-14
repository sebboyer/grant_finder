# Static Assets Fix - Grant Finder Deployment

## Problem
The Grant Finder app was deploying successfully but the UI was not rendering correctly. The page was showing only unstyled HTML without CSS, JavaScript, or images.

## Root Cause
The Flask application was not configured to serve static files from the `public/` directory at the root URL path. The HTML templates were referencing assets like:
- `/style.css`
- `/script.js`
- `/zeffy-logo-white.png`
- `/favicon.ico`

But Flask was not serving these files, and the `vercel.json` configuration was not properly routing static assets.

## Solution

### 1. Flask Configuration (`app.py`)
```python
# Before:
app = Flask(__name__)

# After:
app = Flask(__name__, static_folder='public', static_url_path='')
```

This tells Flask to:
- Serve static files from the `public/` directory
- Serve them at the root URL path (empty string means `/style.css` maps to `public/style.css`)

### 2. Removed Custom Favicon Route
The custom `/favicon.ico` route was removed since Flask now handles it automatically with the static file configuration.

### 3. Updated Vercel Configuration (`vercel.json`)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    },
    {
      "src": "public/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(favicon\\.ico|style\\.css|script\\.js|.*\\.(png|jpg|jpeg|gif|svg|webp))",
      "dest": "/public/$1"
    },
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

Changes:
- Added `public/**` to builds with `@vercel/static` for efficient static file serving
- Updated routes to catch static file requests (CSS, JS, images, favicon) and route them to the `public/` directory
- All other requests go to the Flask app

## Deployment
To deploy the fix:
```bash
git push origin master
```

Vercel will automatically detect the changes and redeploy the application with proper static asset serving.

## Testing Locally
To test locally:
```bash
cd grant_finder
python3 app.py
```

Visit `http://localhost:5001` and verify that:
- The page has full styling
- JavaScript is working (search functionality, filters)
- Images are loading (Zeffy logo)
- Favicon is visible in the browser tab

## Files Changed
- `app.py`: Updated Flask static file configuration, removed custom favicon route
- `vercel.json`: Updated to properly serve static assets
- `STATIC_ASSETS_FIX.md`: This documentation file

## Verified
✅ All static files are tracked in git (`public/` directory)
✅ Flask correctly configured to serve from `public/` at root path
✅ Vercel configuration routes static files properly
✅ No files are ignored that should be deployed


