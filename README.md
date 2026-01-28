# Reus Party Tracker 🎉

Real-time party activity tracker for Plaça Mercadal in Reus, Spain.

Watch the live stream, see how many people are partying, and check which restaurants are busy!

**Live**: http://54.80.204.92:5050

## Features

- 📺 Live YouTube stream screenshot of Plaça Mercadal
- 🎉 AI-powered party level indicator (0-10)
- 👥 Estimated crowd count via Kiro CLI Vision
- 🍽️ Restaurant busyness levels from Google Maps (14 plaza + 5 top restaurants)
- 📊 Historical charts (24h and 7d) for people count and restaurant busyness
- 🗺️ Interactive heatmap showing restaurant busyness across Reus
- 🌙 Dark & light themes
- 💾 InfluxDB time-series storage with infinite retention
- 💰 Smart API optimization (~$0.50-1.00/day vs $9+)

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

### Top 5 Restaurants in Reus (by reviews, with busyness data)
1. Restaurant del Museu del Vermut (4,300 reviews)
2. Tacos La Mexicanita (2,197 reviews)
3. Khirganga Restaurant (1,884 reviews)
4. Xivarri Gastronomía (1,763 reviews)
5. Ciutat Gaudí (1,623 reviews)

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
