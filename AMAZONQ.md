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

### Current Status
- ✅ Screenshot capture: WORKING (Playwright + cookies)
- ✅ YouTube auth via cookies: WORKING
- ✅ Flask API: WORKING on port 5050
- ✅ Frontend: WORKING (basic dark theme)
- 🔄 AI analysis: Manual via Kiro CLI for now
- ⏳ Restaurant data: Not started
- ⏳ Light theme: Not started

### Next Steps
1. Set up systemd service for persistence
2. Add restaurant data from Google Maps
3. Improve frontend (light theme toggle, restaurant section)

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
