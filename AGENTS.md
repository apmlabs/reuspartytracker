# Reus Party Tracker - Agent Context

## Project Goal

Real-time party activity tracker for Plaça Mercadal in Reus, Spain. Monitors crowd levels via YouTube live stream AI analysis and displays restaurant busyness from Google Maps data.

Inspired by https://www.pizzint.watch/

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SCHEDULED TASKS (APScheduler)               │
├─────────────────────────────────────────────────────────────────┤
│ Every 5 min: update_party_data()                                │
│   1. Playwright captures YouTube screenshot                     │
│   2. Kiro CLI analyzes image (2 calls: people/cars + police)    │
│   3. Saves to InfluxDB + party_data.json                        │
│                                                                 │
│ Every 15 min: refresh_restaurant_data()                         │
│   - Fetches from Outscraper API (smart: skips closed)           │
│   - Saves to InfluxDB + restaurants_cache.json                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     FLASK API (port 5050)                       │
├─────────────────────────────────────────────────────────────────┤
│ GET /api/party              → Current party data                │
│ GET /api/restaurants        → All restaurants by category       │
│ GET /api/screenshot         → Latest screenshot                 │
│ GET /api/history?hours=N    → Party history (default)           │
│ GET /api/history?type=restaurants → Plaza busyness by category  │
│ GET /api/history?type=restaurants&category=top → Top by name    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (index.html)                       │
├─────────────────────────────────────────────────────────────────┤
│ Header: Party Level | People | Cars | Police | Theme Toggle     │
│ Screenshot from YouTube live stream                             │
│ Unified Chart: Total, Street, Terrace, Cars, Police (24h-1y)    │
│ Plaza sections: Restaurant list + 24h/7d charts                 │
│ Restaurant Heatmap (Leaflet)                                    │
│ Top 5 Restaurants with individual charts                        │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
reuspartytracker/
├── AGENTS.md                 # Architecture & config (this file)
├── AmazonQ.md                # Session progress log
├── README.md                 # User documentation
├── backend/
│   ├── app.py                # Flask server + scheduler
│   ├── analyzer.py           # Kiro CLI vision analysis
│   ├── screenshot.py         # Playwright YouTube capture
│   ├── restaurants.py        # Outscraper API + caching (unified)
│   ├── database.py           # InfluxDB operations (unified)
│   ├── config.py             # Intervals, thresholds, URLs
│   ├── requirements.txt
│   └── .env                  # API keys (gitignored)
├── frontend/
│   └── index.html            # Single-page app
├── data/
│   ├── party_data.json       # Current state cache
│   └── restaurants_cache.json # All restaurants cache (unified)
├── screenshots/              # Captured frames (gitignored)
└── logs/
    └── outscraper.log        # API call log
```

## Configuration

### Timing
| Component | Interval | Location |
|-----------|----------|----------|
| Screenshot capture | 5 min | config.py SCREENSHOT_INTERVAL |
| Restaurant refresh | 15 min | app.py scheduler |
| Frontend screenshot | 30 sec | index.html |
| Frontend party data | 60 sec | index.html |
| Frontend restaurants | 15 min | index.html |

### Party Level Formula
```
People: 0→L0, 1-2→L1, 3-5→L2, 6-10→L3, 11-20→L4, 21-50→L5, 51-70→L7, 71-100→L9, 100+→L10
Restaurant: 100% busyness = L5 (linear scale)
Final = (People Level + Restaurant Level) / 2
```

### Police Score
```
police_score = police_cars × 2 + police_vans × 4 + police_uniformed × 1
```

### Restaurant Busyness Rules
| State | Saved to DB | Chart Effect |
|-------|-------------|--------------|
| Closed | 0 | Included as 0 |
| Open + busyness | actual % | Included |
| Open + no data | NOT saved | Excluded |

## Data Sources

### YouTube Live Stream
- Primary: https://www.youtube.com/watch?v=L9HyLjRVN8E (Plaça Mercadal)
- Requires cookies (youtube_cookies.json) - refresh when expired

### Restaurants
**Plaza Mercadal**: Casa Coder, Roslena Mercadal, Goofretti, El Mestral, Vivari, Maiki Poké, DITALY, Déu n'hi Do

**Plaza Evarist Fàbregas**: La Presó, Sibuya Urban Sushi Bar, Yokoso, Saona Reus

**Plaza del Teatre**: Oplontina, As de Copas

**Top 5** (by reviews, with Popular Times): Restaurant del Museu del Vermut, Tacos La Mexicanita, Khirganga Restaurant, Xivarri Gastronomía, Ciutat Gaudí

## InfluxDB Schema

```
Bucket: party_data (infinite retention)

Measurement: party
  Fields: people_count, street_count, terrace_count, party_level, 
          car_count, police_score, police_cars, police_vans, police_uniformed

Measurement: restaurant
  Tags: name, category (placa_mercadal|placa_evarist_fabregas|placa_del_teatre|top)
  Fields: busyness
```

## Deployment

- Host: 54.80.204.92 (AWS EC2)
- Port: 5050
- Service: `sudo systemctl restart reusparty`
- Daily backup: 3am, keeps 7 days

## Known Issues

1. YouTube cookies expire periodically - refresh from browser when bot prompt appears
2. AI crowd counting less accurate in low light
3. Some restaurants lack Google Popular Times data
