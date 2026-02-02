# Reus Party Tracker - Session History

## Session 1 - January 26, 2026

### Summary
Initial project setup and core functionality.

### Changes
- Created project structure (AGENTS.md, README.md)
- Set up GitHub repo: apmlabs/reuspartytracker
- Implemented screenshot capture via Playwright + YouTube cookies
- Built Flask API on port 5050
- Created dark-themed frontend with YouTube embed
- Integrated Outscraper API for restaurant Popular Times
- Set up systemd service (reusparty.service)

### Issues Resolved
- YouTube requires auth - solved with exported cookies
- Selenium hanging - switched to Playwright

---

## Session 2 - January 27, 2026

### Summary
Added InfluxDB storage and historical charts.

### Changes
- Integrated InfluxDB for time-series storage
- Added party history charts (24h/7d)
- Added restaurant busyness charts per plaza
- Implemented daily backup script

---

## Session 3 - January 28, 2026 (morning)

### Summary
Fixed API cost issues from overnight calls.

### Changes
- Fixed cache name mismatch bug (query name vs API-returned name)
- Fixed closed restaurants showing cached busyness instead of 0
- Added whitelist for restaurants with confirmed Popular Times data
- Added 21:00 daily check for archived restaurants

### Bugs Fixed
1. Cache name mismatch in fetch_top_restaurants
2. Closed restaurants returning old busyness
3. DB save order (check is_open before busyness)

---

## Session 4 - January 28, 2026 (afternoon)

### Summary
Added vehicle and police tracking.

### Changes
- Added car_count to AI analysis
- Added police detection (cars, vans, uniformed)
- Added police_score formula: cars×2 + vans×4 + uniformed×1
- Added 4 new charts (Cars 24h/7d, Police 24h/7d)
- Added red header alert when police detected
- Saved raw police data to InfluxDB

---

## Session 5 - January 28, 2026 (afternoon cont.)

### Summary
Improved AI counting accuracy and unified charts.

### Changes
- Split people counting: street vs terrace
- Created unified chart with 5 metrics (Total, Street, Terrace, Cars, Police)
- Added time range selector (24h, 7d, 30d, 1y)
- Added clickable legend to toggle chart lines
- Hide plazas with no busyness data

### Bugs Fixed
- AI overcounting people (47 vs ~20 actual) - updated prompt to be conservative

---

## Session 6 - January 28, 2026 (evening)

### Summary
Split AI analysis and improved police detection.

### Changes
- Split analyzer.py into 2 kiro-cli calls (people/cars + police)
- Created test_screenshots.md with 16 test images
- Refined police detection prompt for Policía Local (yellow/blue/white)

### Results
- False positives: 0/6 (100% precision)
- True positives: 4/10 (40% recall) - misses obscured/distant

---

## Session 7 - January 28, 2026 (night)

### Summary
Fixed is_open cache bug and major code refactor.

### Changes
- Fixed is_open not recalculating on cached data (all 6 return paths)
- Refactored restaurants.py: unified fetch_restaurants() function
- Refactored database.py: single 'restaurant' measurement with category tag
- Migrated InfluxDB data (3752 top_restaurant + 3274 plaza records)
- Merged cache files into single restaurants_cache.json
- Fixed frontend "Top 25" → "Top 5"
- Cleaned up documentation (AGENTS.md, AmazonQ.md, README.md)

### Bugs Fixed
- is_open returning stale cached value instead of recalculating
- Duplicate code in fetch_all_restaurants/fetch_top_restaurants
- Duplicate code in save_restaurant_data/save_top_restaurant_data

---

## Session 8 - January 29, 2026 (night)

### Summary
API endpoint consolidation and frontend fixes.

### Changes
- Consolidated 6 API endpoints → 3 endpoints
  - Removed `/api/top-restaurants` (merged into `/api/restaurants`)
  - Removed `/api/history/restaurants` and `/api/history/top-restaurants`
  - Added `/api/history?type=restaurants` with optional `&category=top`
- Fixed frontend not showing plaza sections when restaurants closed
- Added auto-hide for `placa_del_teatre` (no Popular Times data yet)
- Cleaned corrupted cache entry with null name

### Bugs Fixed
- Plaza sections hidden when all restaurants closed (canvas elements not created)
- Query string bug: `?category=top?hours=` → `?category=top&hours=`

---

## Session 9 - January 29, 2026 (night)

### Summary
Fixed stale cache bugs causing ~300+ unnecessary API calls per day.

### Changes
- Fixed `should_fetch()` reading stale `is_open` from cache instead of recalculating
- Fixed hardcoded `is_open=True` for unknown restaurants (now uses hour-based default)
- Fixed cache not updating when all API calls skipped (closed restaurants kept stale busyness)

### Bugs Fixed
1. `should_fetch()` checked `cached.get('is_open')` which was stale - now recalculates from `working_hours`
2. Unknown restaurants defaulted to `is_open=True` - now uses `9 <= hour < 23`
3. Cache only saved when `got_any=True` - now always saves with recalculated values

## Session 10 - January 29, 2026 (afternoon)

### Summary
Added police sightings page with screenshot viewer.

### Changes
- Added `/api/police-sightings` endpoint - returns all police detections with matched screenshot filenames
- Added `/api/screenshot/<filename>` endpoint - serve specific screenshot by name
- Created `police.html` - dedicated page for browsing police sightings
  - Full-width screenshot with prev/next navigation (keyboard arrows supported)
  - Info bar: position counter, timestamp, police score, breakdown, people count
  - Interactive chart (police score + people) - click to jump to sighting
  - Scrollable list of all sightings (newest first)
  - Dark/light theme toggle

### New Files
- `frontend/police.html`

### Modified Files
- `backend/app.py` - added 3 new routes
- `backend/database.py` - added `get_police_sightings()` function

## Session 11 - January 29, 2026 (evening)

### Summary
Reduced restaurant list and API call frequency to cut costs.

### Changes
- Reduced active restaurants from 18 to 7
- Changed API refresh interval from 15 → 30 minutes
- Updated frontend to hide restaurants with no busyness data
- Estimated cost: ~$0.38/day (~$11/month)

### Active Restaurants
- Plaça Mercadal: Casa Coder, Goofretti
- Plaça Evarist Fàbregas: La Presó, Sibuya
- Top: Museu del Vermut, Khirganga, Ciutat Gaudí

### Archived (moved from active)
- Roslena Mercadal, El Mestral, Vivari, Maiki Poké, DITALY, Déu n'hi Do, Xivarri
- Yokoso, Saona Reus
- Oplontina, As de Copas (entire placa_del_teatre)
- Tacos La Mexicanita

## Session 12 - February 2, 2026

### Summary
Further reduced restaurant list to minimize API costs.

### Changes
- Reduced active restaurants from 7 to 3
- Removed entire "top" category
- Disabled 21:00 archived check (commented out, not deleted)
- Estimated cost: ~$0.14/day (~$4/month)

### Active Restaurants
- Plaça Mercadal: Casa Coder, Goofretti
- Plaça Evarist Fàbregas: La Presó

### Archived (moved from active)
- Sibuya Urban Sushi Bar
- Restaurant del Museu del Vermut, Khirganga Restaurant, Ciutat Gaudí (entire top category)
