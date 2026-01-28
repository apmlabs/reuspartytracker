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
