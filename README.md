# Reus Party Tracker 🎉

Real-time party activity tracker for Plaça Mercadal in Reus, Spain.

Watch the live stream, see how many people are partying, and check which restaurants are busy!

**Live**: http://54.80.204.92:5050

## Features

- 📺 Live YouTube stream screenshot of Plaça Mercadal
- 🎉 AI-powered party level indicator (0-10)
- 👥 Estimated crowd count via Kiro CLI Vision
- 🍽️ Restaurant busyness levels from Google Maps (14 plaza + 8 top restaurants)
- 📊 Historical charts (24h and 7d) for people count and restaurant busyness
- 🗺️ Interactive heatmap showing restaurant busyness across Reus
- 🌙 Dark & light themes
- 💾 InfluxDB time-series storage with infinite retention
- 💰 Smart API optimization to minimize Outscraper costs

## Tracked Locations

### Plaça del Teatre
- Oplontina PizzaBar
- As De Copes Gastropub

### Plaça Mercadal
- Casa Coder
- Roslena Mercadal
- Goofretti
- El Mestral
- Vivari
- Maiki Poké
- DITALY
- Déu n'hi Do

### Plaça Evarist Fàbregas
- La Presó
- Sibuya Urban Sushi Bar
- Yokoso
- Saona Reus

### Top 8 Restaurants in Reus (by reviews)
1. Restaurant del Museu del Vermut (4,300 reviews)
2. Tacos La Mexicanita (2,197 reviews)
3. Vermuts Rofes (2,117 reviews)
4. Khirganga Restaurant (1,883 reviews)
5. Xivarri Gastronomía (1,763 reviews)
6. Ciutat Gaudí (1,622 reviews)
7. Cerveseria Tower (1,429 reviews)
8. Bar Bon-Mar (1,352 reviews)
19. Restaurant Cal Marc (1,013 reviews)
20. Acarigua Arepera (970 reviews)
21. Restaurant Lo Bon Profit (842 reviews)
## Tech Stack

- **Backend**: Python, Flask, APScheduler
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **AI**: Kiro CLI Vision
- **Video**: Playwright for YouTube screenshots
- **Database**: InfluxDB (time-series)
- **Restaurant Data**: Outscraper API (Google Maps)

## Quick Start

```bash
cd backend
pip install -r requirements.txt

# Set environment variables in .env
OUTSCRAPER_API_KEY=your-key
INFLUXDB_TOKEN=your-token

python app.py
```

Visit `http://localhost:5050`

## Data Sources

- **Live Stream**: [Plaça Mercadal YouTube](https://www.youtube.com/watch?v=L9HyLjRVN8E)
- **Restaurant Data**: Google Maps via Outscraper API

## License

MIT
