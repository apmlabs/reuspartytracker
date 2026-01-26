# Reus Party Tracker - Agent Context

## 🎯 PROJECT GOAL

**Real-time party activity tracker for Plaça Mercadal in Reus, Spain** - monitors crowd levels via YouTube live stream AI analysis and displays restaurant busyness from Google Maps data.

Inspired by https://www.pizzint.watch/ but for tracking party vibes in Reus.

---

## 📋 PROJECT STATUS

**Phase**: Phase 5 - Polish (in progress)
**Started**: January 26, 2026
**GitHub**: apmlabs/reuspartytracker

---

## 🏗️ ARCHITECTURE

### System Overview
```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (HTML/CSS/JS)                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │         YouTube Embed (Plaça Mercadal Live)         │   │
│  │         https://youtube.com/watch?v=L9HyLjRVN8E     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Party Level  │  │ People Count │  │ Last Updated     │  │
│  │    🎉 7/10   │  │    ~50       │  │ 5 min ago        │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              RESTAURANT ACTIVITY                     │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │ PLAÇA MERCADAL                              │    │   │
│  │  │ • Restaurant Museu del Vermut  ████░░ 80%  │    │   │
│  │  │ • Casa Coder                   ███░░░ 60%  │    │   │
│  │  │ • La Presó                     █████░ 90%  │    │   │
│  │  │ • Vermuts Rofes                ██░░░░ 40%  │    │   │
│  │  │ • ...more                                   │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │ PLAÇA DEL TEATRE                            │    │   │
│  │  │ • Oplontina                    ████░░ 75%  │    │   │
│  │  │ • As de Copas                  ███░░░ 55%  │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Python/Flask)                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────┐    │
│  │ Screenshot      │───▶│ AI Vision Analysis          │    │
│  │ Capture         │    │ (GPT-4 Vision / Claude)     │    │
│  │ (yt-dlp/ffmpeg) │    │ "Count people in image"     │    │
│  └─────────────────┘    └─────────────────────────────┘    │
│           │                         │                       │
│           ▼                         ▼                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   party_data.json                    │   │
│  │  {                                                   │   │
│  │    "people_count": 50,                              │   │
│  │    "party_level": 7,                                │   │
│  │    "last_updated": "2026-01-26T20:30:00Z",         │   │
│  │    "restaurants": {...}                             │   │
│  │  }                                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Scheduled Tasks (cron/APScheduler)      │   │
│  │  • Screenshot + AI analysis: every 5 min (config)   │   │
│  │  • Google Maps scrape: every 15 min                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
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

### Tech Stack
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Backend**: Python 3, Flask
- **AI**: OpenAI GPT-4 Vision API (or Claude)
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

## 🔧 CONFIGURATION

### Configurable Parameters (config.py)
```python
# Screenshot interval (seconds) - easy to change for testing
SCREENSHOT_INTERVAL = 300  # 5 minutes default

# Party level thresholds
PARTY_THRESHOLDS = {
    0: 1,      # 0-1 people = level 0
    2: 10,     # 2-10 people = level 2
    7: 50,     # 11-50 people = level 7
    8: 100,    # 51-100 people = level 8
    10: 200,   # 101+ people = level 10
}

# YouTube stream
YOUTUBE_URL = "https://www.youtube.com/watch?v=L9HyLjRVN8E"

# Backup webcam (if YouTube fails)
BACKUP_WEBCAM = "https://www.skylinewebcams.com/webcam/espana/cataluna/tarragona/reus.html"
```

---

## 📍 DATA SOURCES

### YouTube Live Stream
- **Primary**: https://www.youtube.com/watch?v=L9HyLjRVN8E (Plaça Mercadal)
- **Backup**: https://www.skylinewebcams.com/webcam/espana/cataluna/tarragona/reus.html

### Restaurants - Plaça Mercadal
(To be populated from Google Maps search)
- Restaurant Museu del Vermut
- Casa Coder
- La Presó
- Vermuts Rofes
- Bar L'Àmfora
- (more to discover)

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
- [x] Restaurant list for both plazas
- [x] Busyness data display with "Closed" status
- [x] 15-minute caching
- [x] Combined party level (people + restaurant avg)

### Phase 5: Polish (in progress)
- [ ] Error handling
- [ ] Fallback to backup webcam
- [ ] Mobile responsive
- [ ] Historical data (optional)

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
