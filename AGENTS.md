# Reus Party Tracker - Agent Context

## 🎯 PROJECT GOAL

**Real-time party activity tracker for Plaça Mercadal in Reus, Spain** - monitors crowd levels via YouTube live stream AI analysis and displays restaurant busyness from Google Maps data.

Inspired by https://www.pizzint.watch/ but for tracking party vibes in Reus.

---

## 📋 PROJECT STATUS

**Phase**: Phase 6 - Polish (complete)
**Started**: January 26, 2026
**GitHub**: apmlabs/reuspartytracker

---

## 🏗️ ARCHITECTURE

### Complete Data Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SCHEDULED TASKS                                 │
│                         (APScheduler in app.py)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Every 30 seconds: update_party_data()                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  1. SCREENSHOT CAPTURE (screenshot.py)                              │   │
│  │     └─► Playwright loads YouTube with cookies                       │   │
│  │     └─► Captures frame → screenshots/latest.png                     │   │
│  │                                                                     │   │
│  │  2. AI ANALYSIS (analyzer.py)                                       │   │
│  │     └─► Kiro CLI vision analyzes screenshot                         │   │
│  │     └─► Returns: people_count (int)                                 │   │
│  │                                                                     │   │
│  │  3. RESTAURANT DATA (restaurants.py)                                │   │
│  │     └─► Check cache (15 min TTL)                                    │   │
│  │     └─► If expired: call Outscraper API for Google Popular Times    │   │
│  │     └─► Returns: {plaza: [{name, is_open, busyness}, ...]}          │   │
│  │                                                                     │   │
│  │  4. CALCULATE PARTY LEVEL                                           │   │
│  │     └─► people_level = f(people_count)  [0-10 scale]                │   │
│  │     └─► restaurant_level = avg_busyness / 20  [0-5 scale]           │   │
│  │     └─► party_level = (people_level + restaurant_level) / 2         │   │
│  │                                                                     │   │
│  │  5. SAVE TO INFLUXDB (database.py)                                  │   │
│  │     └─► Party: people_count, party_level                            │   │
│  │     └─► Restaurants: per-restaurant busyness (see rules below)      │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              FLASK API (app.py)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GET /api/party          → Current party data (people, level, timestamp)   │
│  GET /api/restaurants    → Current restaurant busyness by plaza            │
│  GET /api/top-restaurants → Top 20 restaurants with busyness/rating/reviews│
│  GET /api/screenshot     → Latest screenshot image                         │
│  GET /api/history?hours=N        → Party history from InfluxDB             │
│  GET /api/history/restaurants?hours=N → Restaurant avg history by plaza    │
│  GET /api/history/top-restaurants?hours=N → Top restaurant history         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (index.html)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Auto-refresh intervals:                                                    │
│  • Screenshot image: 30 seconds                                             │
│  • Party data: 60 seconds                                                   │
│  • Restaurant data + charts: 15 minutes                                     │
│                                                                             │
│  Layout:                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Header: Title | Party Level | People Count | Theme Toggle           │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ Screenshot from YouTube live stream                                 │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ People Charts: 24h (stacked) | 7d (stacked)                         │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ Plaza Teatre:      Restaurants (20%) | Charts 24h/7d (80%)          │   │
│  │ Plaza Mercadal:    Restaurants (20%) | Charts 24h/7d (80%)          │   │
│  │ Plaza Evarist:     Restaurants (20%) | Charts 24h/7d (80%)          │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │ Top 20 Restaurants: Each with name, reviews, rating, 24h/7d charts  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Restaurant Busyness Rules (for charts)
```
Restaurant State          │ Saved to DB │ Color in UI │ Effect on Average
──────────────────────────┼─────────────┼─────────────┼───────────────────
Open + has busyness %     │ actual %    │ Green       │ Included
Closed                    │ 0           │ Red         │ Included (as 0)
Open + no data from Google│ NOT saved   │ Grey        │ Excluded
```

### InfluxDB Schema
```
Bucket: party_data (infinite retention)

Measurement: party
  Fields: people_count (int), party_level (int)
  
Measurement: restaurant  
  Tags: name (string), plaza (string)
  Fields: busyness (int)
  
Query for charts: aggregateWindow(every: 5m, fn: mean) grouped by plaza
```

### File Structure (Actual)
```
reuspartytracker/
├── AGENTS.md                    # This file - architecture & context
├── README.md                    # User documentation
├── .gitignore
├── youtube_cookies.json         # YouTube auth (gitignored)
│
├── backend/
│   ├── app.py                   # Flask server + scheduler
│   ├── analyzer.py              # Kiro CLI vision analysis
│   ├── screenshot.py            # Playwright YouTube capture
│   ├── restaurants.py           # Outscraper API + caching
│   ├── database.py              # InfluxDB read/write
│   ├── config.py                # Intervals, thresholds, URLs
│   ├── requirements.txt
│   ├── .env                     # API keys (gitignored)
│   └── venv/                    # Python virtual environment
│
├── frontend/
│   └── index.html               # Single-page app (HTML+CSS+JS)
│
├── data/
│   ├── party_data.json          # Current state cache
│   └── restaurants_cache.json   # Restaurant API cache (gitignored)
│
└── screenshots/
    └── latest.png               # Most recent capture (gitignored)
```

### Party Level Formula
```
People Count → Base Level (0-10)
─────────────────────────────────
0 people     → Level 0
1-2 people   → Level 1
3-5 people   → Level 2
6-10 people  → Level 3
11-20 people → Level 4
21-50 people → Level 5
51-70 people → Level 7
71-100 people → Level 9
100+ people  → Level 10

Combined Formula:
─────────────────
Restaurant Avg Busyness: 100% = Level 5 (scales linearly)
Final Party Level = (People Level + Restaurant Level) / 2
```

### Timing & Intervals
```
Component                │ Interval    │ Source
─────────────────────────┼─────────────┼─────────────────────────
Screenshot capture       │ 30 sec      │ config.py SCREENSHOT_INTERVAL
AI analysis              │ 30 sec      │ (with screenshot)
Restaurant API call      │ 15 min      │ restaurants.py CACHE_TTL
Save to InfluxDB         │ 30 sec      │ (with screenshot)
Frontend screenshot      │ 30 sec      │ index.html setInterval
Frontend party data      │ 60 sec      │ index.html setInterval
Frontend restaurants     │ 15 min      │ index.html setInterval
Chart aggregation window │ 5 min       │ database.py InfluxDB query
```

### Tech Stack
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Backend**: Python 3, Flask
- **AI**: Kiro CLI (vision analysis via subprocess)
- **Video**: yt-dlp + ffmpeg for YouTube screenshots
- **Scheduling**: APScheduler
- **Hosting**: This AWS EC2 instance

---

## 📁 FILE STRUCTURE (Planned)

```
reuspartytracker/
├── AGENTS.md              # This file - agent context
├── AMAZONQ.md             # Session history
├── README.md              # User documentation
├── .gitignore
│
├── backend/
│   ├── app.py             # Flask server
│   ├── analyzer.py        # AI vision analysis
│   ├── screenshot.py      # YouTube screenshot capture
│   ├── restaurants.py     # Google Maps data scraper
│   ├── scheduler.py       # Scheduled tasks
│   ├── config.py          # Configuration (intervals, thresholds)
│   └── requirements.txt
│
├── frontend/
│   ├── index.html         # Main page
│   ├── style.css          # Styling (dark + light themes)
│   └── script.js          # Frontend logic
│
├── data/
│   └── party_data.json    # Current state
│
└── screenshots/           # Captured frames (gitignored)
```

---

## 📍 DATA SOURCES

### YouTube Live Stream
- **Primary**: https://www.youtube.com/watch?v=L9HyLjRVN8E (Plaça Mercadal)
- **Backup**: https://www.skylinewebcams.com/webcam/espana/cataluna/tarragona/reus.html

### Restaurants - Plaça Mercadal
- Casa Coder
- Roslena Mercadal
- Goofretti
- El Mestral
- Vivari
- Maiki Poké
- DITALY
- Déu n'hi Do

### Restaurants - Plaça Evarist Fàbregas
- La Presó
- Sibuya Urban Sushi Bar
- Yokoso
- Saona Reus

### Restaurants - Plaça del Teatre
- Oplontina
- As de Copas

---

## 🚀 DEPLOYMENT

### Current Server
- **Host**: 54.80.204.92 (AWS EC2)
- **Port**: 5050
- **URL**: http://54.80.204.92:5050
- Process: Flask dev server (needs systemd for production)

### Existing Services (DO NOT TOUCH)
- Port 5001: OnyxPoker server
- Port 5050: Reus Party Tracker ✅

---

## 📋 IMPLEMENTATION PHASES

### Phase 1: Basic Setup ✅
- [x] Create project structure
- [x] Create documentation (AGENTS.md, AMAZONQ.md, README.md)
- [x] Create GitHub repo (apmlabs/reuspartytracker)
- [x] Basic Flask app skeleton

### Phase 2: YouTube Integration ✅
- [x] Playwright screenshot capture
- [x] YouTube cookies authentication
- [x] Party level calculation
- [x] Scheduled capture task (30 sec interval)

### Phase 3: Frontend ✅
- [x] YouTube embed
- [x] Party level display
- [x] People count display
- [x] Dark/light theme toggle
- [x] Auto-refresh (30s screenshots, 15min restaurants)

### Phase 4: Restaurant Data ✅
- [x] Outscraper API integration (Popular Times)
- [x] Restaurant list for all 3 plazas (14 restaurants)
- [x] Busyness data display with "Closed"/"Open" status
- [x] 15-minute caching
- [x] Combined party level (people + restaurant avg)

### Phase 5: Historical Data & Charts ✅
- [x] InfluxDB time-series database (infinite retention)
- [x] Party history API endpoint
- [x] Restaurant history API endpoint
- [x] Daily (24h) and Weekly (7d) charts for people count
- [x] Daily and Weekly charts for each plaza's avg busyness
- [x] Chart.js visualization

### Phase 6: Polish (in progress)
- [ ] Error handling improvements
- [ ] Fallback to backup webcam
- [ ] Mobile responsive
- [ ] Admin interface for historical data

---

## 🔑 CRITICAL LESSONS

### From This Project
1. **YouTube cookies expire** - They rotate for security. When screenshots show "Sign in to confirm you're not a bot", export fresh cookies from browser
2. **Use Netscape format for yt-dlp** - JSON cookies work for Playwright, but yt-dlp needs Netscape .txt format
3. **yt-dlp validates cookies** - It tells you if cookies are expired, useful for debugging

### From Other Projects
1. **Don't mess with existing services** - Check ports before deploying
2. **Configuration over hardcoding** - Make intervals easily changeable
3. **Document everything** - Context files are agent memory
4. **Test incrementally** - Get each phase working before next

---

## 🐛 KNOWN ISSUES / RISKS

1. **YouTube cookies expire** - Cookies rotate periodically, need fresh export when bot prompt appears
2. **YouTube stream availability** - May go offline, need fallback
3. **AI accuracy** - Crowd counting in low light may be inaccurate
4. **Google Maps rate limits** - May need caching strategy
5. **Cost** - AI API calls cost money, optimize frequency

---

## 📚 DOCUMENTATION STRUCTURE

- **AGENTS.md** (this file) - Permanent knowledge, architecture
- **AMAZONQ.md** - Session history, progress tracking
- **README.md** - User-facing quick start guide
