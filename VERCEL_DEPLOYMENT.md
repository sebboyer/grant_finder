# Vercel Deployment Guide - Zeffy Grant Finder

## ✅ Your App is Ready for Vercel!

The Zeffy Grant Finder Flask application has been configured for deployment to Vercel with **zero configuration required**. All setup follows [Vercel's Flask deployment best practices](https://vercel.com/docs/frameworks/backend/flask).

## Changes Made for Vercel

### 1. Directory Structure ✅
```
grant_finder/
├── app.py                    # Flask entrypoint with app instance ✅
├── requirements.txt          # Consolidated dependencies ✅
├── public/                   # Static files (served via Vercel CDN) ✅
│   ├── style.css
│   ├── script.js
│   ├── zeffy-logo-white.png
│   └── zeffy-logo.png
├── templates/                # Jinja2 templates ✅
│   ├── index.html
│   └── foundation.html
└── *.csv                     # Data files ✅
```

### 2. Static Files → Public Directory
- **Before**: `static/`
- **After**: `public/` (Vercel serves these via global CDN)

Static files are now accessible at root paths:
- `public/style.css` → `/style.css`
- `public/script.js` → `/script.js`
- `public/zeffy-logo-white.png` → `/zeffy-logo-white.png`

### 3. Template Updates
All templates updated to use direct paths:
```html
<!-- Before -->
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">

<!-- After -->
<link rel="stylesheet" href="/style.css">
```

### 4. Consolidated Requirements
Single `requirements.txt` with all necessary dependencies:
- Flask==3.0.0
- pandas==2.1.4
- numpy==1.26.3
- Werkzeug==3.0.1

### 5. Flask App Configuration
Your `app.py` correctly exports the Flask app instance:
```python
app = Flask(__name__)  # Line 6 - Vercel auto-detects this ✅
```

## Deployment Options

### Option 1: Vercel CLI (Recommended)

1. **Install Vercel CLI** (if not already installed):
```bash
npm install -g vercel
```

2. **Deploy from project directory**:
```bash
cd /Users/sebboyer/Documents/Zeffy/grant_finder
vercel deploy
```

3. **Follow the prompts**:
   - Link to your Vercel account
   - Set project name
   - Confirm settings
   - Deploy!

4. **Promote to production** (after testing preview):
```bash
vercel --prod
```

### Option 2: Git Integration (Continuous Deployment)

1. **Push to GitHub/GitLab/Bitbucket**:
```bash
git init
git add .
git commit -m "Prepare grant_finder for Vercel deployment"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

2. **Connect to Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your repository
   - Vercel auto-detects Flask configuration
   - Deploy!

3. **Auto-deploy on every push**:
   - Every commit to `main` deploys to production
   - Every PR creates a preview deployment

## What Vercel Does Automatically

✅ **Detects Flask app** in `app.py`  
✅ **Finds app instance** (line 6)  
✅ **Installs dependencies** from `requirements.txt`  
✅ **Serves public/** files via global CDN  
✅ **Routes** all other requests to Flask  
✅ **Provides HTTPS** with automatic SSL  
✅ **Auto-scales** based on traffic  

## Data Files

Your CSV data files will be included in the deployment:
- `grants_information_summary.csv` (~4.3 MB)
- `foundations_information_summary.csv` (~428 KB)
- `officers_information_summary.csv` (~546 KB)
- `foundation_profiles_export_20251110.csv` (~533 KB)
- Others...

**Total app size**: ~15-20 MB (well under Vercel's 250 MB limit)

## Environment Variables (Optional)

If you need to add environment variables:

1. **Via Vercel Dashboard**:
   - Project Settings → Environment Variables
   - Add key-value pairs
   - Available in Flask via `os.environ`

2. **Via CLI**:
```bash
vercel env add SECRET_KEY
```

## URL Structure

After deployment:

```
Production URLs:
├── /                          → Homepage (dual view)
├── /foundation/<ein>          → Foundation profile
├── /api/grants                → All grants data
├── /api/grants/search         → Search grants
├── /api/foundations           → All foundations
├── /api/foundations/search    → Search foundations
├── /api/foundation/<ein>/stats → Foundation stats
├── /api/states                → States data
├── /style.css                 → Public CSS (CDN)
├── /script.js                 → Public JS (CDN)
└── /zeffy-logo-white.png      → Public assets (CDN)
```

## Performance Optimization

### Vercel Provides:
- **Global CDN**: Static files served from 200+ edge locations
- **Fluid Compute**: Auto-scaling serverless functions
- **Smart caching**: Automatic asset optimization
- **Compression**: Automatic gzip/brotli compression

### Your App:
- **Data loading**: CSVs load on first function invocation (~3-5 seconds cold start)
- **Subsequent requests**: Fast (<100ms) with warmed function
- **Client-side pagination**: 100 results per page for performance

## Testing Your Deployment

### 1. Test Preview Deployment
After first deploy, you'll get a preview URL:
```
https://grant-finder-xyz123.vercel.app
```

Test all features:
- [ ] Homepage loads
- [ ] Search grants works
- [ ] Search foundations works
- [ ] Foundation profiles load
- [ ] Interactive map displays
- [ ] CSS and JS load correctly

### 2. Check Logs
View real-time logs in Vercel Dashboard:
- Function logs
- Build logs
- Error tracking

### 3. Performance
Use Vercel Analytics to monitor:
- Page load times
- API response times
- Error rates

## Local Development

Test locally before deploying:

```bash
cd /Users/sebboyer/Documents/Zeffy/grant_finder
python app.py
```

Visit: http://localhost:5000

## Troubleshooting

### CSV Files Not Loading
- Ensure CSV files are in the root directory
- Check file paths in `app.py` (lines 9, 13, 17)
- Verify files are committed to git

### Static Files 404
- Confirm files are in `public/` directory
- Check template paths use direct paths (`/style.css`)
- No `url_for('static', ...)` references

### Function Timeout
- Default: 10 seconds
- Upgrade to Pro for 60 seconds
- Consider caching or async loading for large datasets

### Build Fails
- Check `requirements.txt` for invalid packages
- Ensure pandas/numpy versions are compatible
- View build logs in Vercel Dashboard

## Vercel Plans & Limits

### Hobby (Free):
- 100 GB bandwidth/month
- Serverless function executions
- Automatic HTTPS
- Perfect for testing!

### Pro ($20/month):
- 1 TB bandwidth
- Advanced analytics
- Password protection
- Team collaboration

## Post-Deployment

### Custom Domain
1. Add domain in Vercel Dashboard
2. Configure DNS records
3. Automatic SSL provisioning

### Monitoring
- Set up Vercel Analytics
- Enable error tracking
- Monitor function performance

### Updates
```bash
# Make changes
git add .
git commit -m "Update description"
git push

# Or via CLI
vercel --prod
```

## Production Checklist

Before going live:

- [ ] All features tested on preview deployment
- [ ] CSV data files are up-to-date
- [ ] Error handling tested
- [ ] Performance acceptable
- [ ] Custom domain configured (optional)
- [ ] Analytics enabled
- [ ] Team access configured

## Ready to Deploy! 🚀

Your Grant Finder application is fully configured and ready for Vercel deployment:

```bash
cd /Users/sebboyer/Documents/Zeffy/grant_finder
vercel deploy
```

## Resources

- [Vercel Flask Documentation](https://vercel.com/docs/frameworks/backend/flask)
- [Vercel CLI Documentation](https://vercel.com/docs/cli)
- [Vercel Dashboard](https://vercel.com/dashboard)
- [Deployment Documentation](https://vercel.com/docs/deployments/overview)

---

**Questions?** Check the [Vercel Documentation](https://vercel.com/docs) or contact support.

