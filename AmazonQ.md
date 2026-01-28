# Reus Party Tracker - Session History

## Session 1 - January 26, 2026

### Goals
- [x] Create project documentation (AGENTS.md, AMAZONQ.md, README.md)
- [x] Create GitHub repository
- [x] Set up basic project structure
- [x] Screenshot capture working

### Progress

**20:38** - Project kickoff
- User wants to build a party tracker for Plaça Mercadal in Reus
- Inspired by pizzint.watch
- Key features:
  - YouTube live stream embed
  - AI-powered crowd counting (screenshots every 5 min, configurable)
  - Restaurant busyness from Google Maps
  - Dark + light themes

**Research completed:**
- YouTube stream: https://www.youtube.com/watch?v=L9HyLjRVN8E
- Backup webcam found: https://www.skylinewebcams.com/webcam/espana/cataluna/tarragona/reus.html
- Restaurants on Plaça Mercadal: Museu del Vermut, Casa Coder, La Presó, Vermuts Rofes, Bar L'Àmfora
- Restaurants on Plaça del Teatre: Oplontina, As de Copas

**Party level formula defined:**
- 0-1 people = Level 0
- 2-10 people = Level 2
- 11-50 people = Level 7
- 51-100 people = Level 8
- 101-200+ people = Level 10

### Decisions Made
1. Tech stack: Python/Flask backend, vanilla HTML/CSS/JS frontend
2. Host on current EC2 instance (careful of existing services)
3. GitHub repo: apmlabs/reuspartytracker
4. Screenshot interval: 5 min default, easily configurable

**20:42** - GitHub repo created, docs pushed

**20:45** - Tried yt-dlp but YouTube requires auth/cookies now

**20:47** - Switched to headless Chromium approach

**20:52** - Screenshot capture working!
- Using `chromium-browser --headless --screenshot` directly
- Selenium was hanging, direct CLI works
- Captured 180KB PNG from YouTube stream
- BUT: YouTube showed "sign in to confirm not a bot"

**21:02** - Cookies approach
- User exported cookies from Chrome using EditThisCookie extension
- Uploaded youtube_cookies.json

**21:07** - Playwright working!
- Switched from Selenium to Playwright (better headless support)
- Cookies loaded successfully
- **Screenshot captured showing actual Plaça Mercadal!**
- Night view, plaza nearly empty (~0 people)

**21:08** - Flask app + Frontend working!
- Flask API on port 5050
- Basic dark-themed frontend with YouTube embed
- Scheduler configured (default 5min, testing 1hr)
- API endpoints: /api/party, /api/update, /api/refresh

**21:44** - Cookie expiration issue
- Screenshots started showing "Sign in to confirm you're not a bot"
- YouTube cookies had expired/rotated
- User exported fresh cookies, screenshot capture working again

**21:58** - Systemd service created
- `reusparty.service` installed and enabled
- Auto-restarts on failure

**22:01** - Frontend updated
- Added restaurant section with two plazas
- Added light/dark theme toggle (persists to localStorage)

**22:12** - Outscraper integration
- Integrated Outscraper API for restaurant Popular Times data
- Added 15-minute caching to reduce API calls
- API key stored in `.env` file (gitignored)

### Current Status
- ✅ Screenshot capture: WORKING (Playwright + cookies)
- ✅ YouTube auth via cookies: WORKING (fresh cookies needed periodically)
- ✅ Flask API: WORKING on port 5050
- ✅ Systemd service: RUNNING (auto-restart enabled)
- ✅ Frontend: WORKING (dark/light themes, restaurant section)
- ✅ Restaurant data: WORKING (Outscraper API with caching)
- 🔄 AI analysis: Manual via Kiro CLI for now
- ⏳ OpenAI integration for auto crowd counting

### Next Steps
1. Integrate OpenAI GPT-4 Vision for automatic crowd counting
2. Mobile responsive improvements
3. Historical data tracking (optional)

---

## Notes

### Useful Commands
```bash
# Check what's running on ports
sudo netstat -tlnp

# Start Flask dev server
cd backend && python app.py

# Test yt-dlp screenshot
yt-dlp --skip-download --write-thumbnail https://www.youtube.com/watch?v=L9HyLjRVN8E
```

### API Keys Needed
- OpenAI API key (for GPT-4 Vision)
- Google Maps API key (for Places API - restaurant data)


---

## Session 3 - January 28, 2026

### Goals
- [x] Fix API cost issues - too many calls overnight
- [x] Fix cache name mismatch bug
- [x] Fix closed restaurants showing wrong busyness

### Progress

**08:35** - Investigated API calls from last 6 hours
- Found 54 calls for Tacos La Mexicanita and Xivarri Gastronomía overnight
- Both were closed but still being fetched

**08:44** - Fixed cache name mismatch in `fetch_top_restaurants`
- Same bug as plaza restaurants: query name "Tacos La Mexicanita" didn't match cache key "Tacos La Mexicanita Reus"
- Added `find_cached()` substring matching function

**08:40** - Fixed closed restaurants showing cached busyness
- Closed restaurants were returning old busyness from cache instead of 0
- Fixed in both API response and DB save logic
- Now: closed = 0 busyness always

**09:03** - Verified fix working
- All closed restaurants now being skipped
- Zero API calls for closed restaurants since fix

### Bugs Fixed
1. **Cache name mismatch** (fetch_top_restaurants) - query names don't match API-returned names
2. **Closed restaurants busyness** - was showing cached value, now shows 0
3. **DB save order** - was checking busyness before is_open, now checks is_open first

### Current State
- **Whitelist**: 11 restaurants (6 plaza + 5 top)
- **API calls**: ~0-11 per 15-min refresh (only open + whitelist)
- **21:00 check**: Fetches all archived to discover new Popular Times data
- **Estimated daily cost**: ~$0.50-1.00 (down from $9+)

### Top 5 Restaurants (by reviews, with busyness data)
1. Restaurant del Museu del Vermut (4,300 reviews)
2. Tacos La Mexicanita (2,197 reviews)
3. Khirganga Restaurant (1,884 reviews)
4. Xivarri Gastronomía (1,763 reviews)
5. Ciutat Gaudí (1,623 reviews)
