# Grant Finder - Quick Reference Guide

## 🚀 Starting the Application

```bash
cd /Users/sebboyer/Documents/Zeffy/grant_finder
source venv/bin/activate
python app.py
```

Then open: **http://localhost:5001**

## 🎯 Two Views Available

### 1. Individual Grants View (Default)
**Use this when you want to:**
- Find specific grant amounts
- Search grants to specific cities/states
- See what individual grants look like
- Browse all grants from a foundation

**Example Queries:**
- "Show me all grants over $100,000"
- "Find grants given to organizations in California"
- "What grants did the Gates Foundation give?"

### 2. Foundations View
**Use this when you want to:**
- Find foundations that give to your state
- Discover foundations by their giving patterns
- See foundation statistics at a glance
- Find foundations with specific median grant sizes

**Example Queries:**
- "Show me foundations giving to Texas with median grant $50K+"
- "Find large foundations (100+ grants)"
- "Which foundations give to California?"
- "Foundations with total giving over $1M"

## 🔍 Search Tips

### Grants View Filters
| Filter | Purpose | Example |
|--------|---------|---------|
| Foundation Name | Find grants from specific foundation | "Gates", "Ford" |
| Recipient State | Where grants were given | "CA", "NY" |
| Recipient City | Specific city | "San Francisco" |
| Min/Max Amount | Grant size range | Min: 50000, Max: 200000 |

### Foundations View Filters
| Filter | Purpose | Example |
|--------|---------|---------|
| Foundation Name | Search by name | "Community Foundation" |
| States They Give To | Geographic reach | "CA" (shows foundations giving to CA) |
| Min # of Grants | Activity level | 20 (foundations with 20+ grants) |
| Min/Max Total Giving | Foundation size | Min: 1000000 (foundations giving $1M+) |
| Min/Max Median Grant | Typical grant size | 50000 (median grant of $50K+) |

## 💡 Pro Tips

1. **Finding Your Perfect Match:**
   - Use **Foundations View** to find foundations that serve your area
   - Filter by **median grant** to find those giving grants your size
   - Click **"View Grants"** to see examples of what they fund

2. **Research Strategy:**
   - Start with **Foundations View** to identify prospects
   - Note the EIN numbers of interesting foundations
   - Switch to **Grants View** to see all their giving history
   - Look at grant purposes to see if you're a good fit

3. **Smart Filtering:**
   - **Median grant** is often more useful than average (avoids outliers)
   - **States served** shows geographic reach
   - **Min grants** filter helps find active foundations vs one-time donors

4. **Expanding Grant Lists:**
   - Click "View X Grants" on any foundation card
   - Grants load instantly
   - Click again to collapse
   - Great for seeing patterns in their giving

## 📊 Understanding the Data

### Foundation Cards Show:
- **Total Grants**: How many grants they've given
- **Total Given**: Sum of all their grants
- **Median Grant**: Middle value (typical grant size)
- **Grant Range**: Smallest to largest grant
- **Geographic Reach**: States they give to
- **Focus Areas**: Top 3 grant purposes

### Grant Cards Show:
- **Grant Amount**: Size of individual grant
- **Foundation Name**: Who gave it
- **Recipient**: Who received it
- **Location**: Where recipient is based
- **Purpose**: What it was for
- **Tax Period**: When it was reported

## 🎨 Design Philosophy

**Simplified, Clean Interface:**
- No visual clutter or gradients
- Solid Zeffy brand colors (Periwinkle, Sea foam green, Midnight blue)
- Focus on information, not decoration
- Easy to scan and compare
- Professional appearance

## 🔢 Database Stats

```
20,998 total grants
1,687 unique foundations
$1.05 billion total giving

Average per foundation:
- 12 grants
- $618,000 total giving

Median per foundation:
- 4 grants
- $50,000 total giving
```

## ⌨️ Keyboard Shortcuts

- **Enter** in any search field = Perform search
- **Tab** = Navigate between filters
- **Click foundation name** in autocomplete = Auto-search

## 📱 Mobile Support

The interface is fully responsive:
- Touch-friendly buttons
- Collapsible filters
- Card layouts adapt to screen size
- Easy navigation on phone/tablet

## ❓ Common Questions

**Q: Why can't I find a foundation?**
A: Check spelling, try searching just part of the name, or use the autocomplete.

**Q: What does "States They Give To" mean?**
A: It shows foundations that have given grants to organizations in that state.

**Q: Why use median vs average?**
A: Median is more representative of typical grants. A few very large grants can skew the average.

**Q: Can I export results?**
A: Not yet - this is a planned future enhancement.

**Q: What's the date range of this data?**
A: Tax periods shown in the data (typically 2023-2024).

## 🛠️ Technical Details

**Backend:** Flask (Python)  
**Data Processing:** Pandas  
**Frontend:** Vanilla JavaScript  
**Styling:** Custom CSS (Zeffy brand)  
**Data Source:** IRS Form 990 filings  

**API Endpoints:**
- `/api/stats` - Database statistics
- `/api/search` - Search individual grants
- `/api/foundations_aggregated` - Search foundations
- `/api/foundation/<ein>` - Foundation details with grants
- `/api/foundations` - Name autocomplete

## 📞 Need Help?

Check these files for more info:
- `DUAL_VIEW_SUMMARY.md` - Complete implementation details
- `IMPLEMENTATION_PLAN.md` - Original design plan
- `README_WEBAPP.md` - Technical documentation
- `ZEFFY_BRAND_IMPLEMENTATION.md` - Design guidelines

---

**Happy Grant Hunting! 🎯**

