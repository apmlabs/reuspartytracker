# Reus Party Tracker 🎉

Real-time party activity tracker for Plaça Mercadal in Reus, Spain.

Watch the live stream, see how many people are partying, and check which restaurants are busy!

**Live**: http://54.80.204.92:5050

## Features

- 📺 Live YouTube stream screenshot of Plaça Mercadal
- 🎉 AI-powered party level indicator (0-10)
- 👥 Estimated crowd count via GPT-4 Vision
- 🍽️ Restaurant busyness levels from Google Maps (14 plaza restaurants + Top 20 in Reus)
- 📊 Historical charts (24h and 7d) for people count and restaurant busyness
- 🌙 Dark & light themes
- 💾 InfluxDB time-series storage with infinite retention

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

### Top 20 Restaurants in Reus (by reviews)
1. Restaurant del Museu del Vermut (4,300 reviews)
2. La Presó (2,278 reviews)
3. Tacos La Mexicanita (2,197 reviews)
4. Vermuts Rofes (2,117 reviews)
5. Khirganga Restaurant (1,883 reviews)
6. Xivarri Gastronomía (1,763 reviews)
7. Ciutat Gaudí (1,622 reviews)
8. Saona Reus (1,589 reviews)
9. Cerveseria Tower (1,429 reviews)
10. Bar Bon-Mar (1,352 reviews)
11. Il Cuore (1,286 reviews)
12. Casa Coder (1,206 reviews)
13. Little Bangkok (1,166 reviews)
14. Brasería Costillar (1,159 reviews)
15. Mirall de Tres (1,075 reviews)
16. Xapatti (1,045 reviews)
17. Ferran Cerro Restaurant (1,043 reviews)
18. Vill Rus Restaurant (1,027 reviews)
19. Restaurant Cal Marc (1,013 reviews)
20. Acarigua Arepera (970 reviews)

## Tech Stack

- **Backend**: Python, Flask, APScheduler
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **AI**: OpenAI GPT-4 Vision
- **Video**: Playwright for YouTube screenshots
- **Database**: InfluxDB (time-series)
- **Restaurant Data**: Outscraper API (Google Maps)

## Quick Start

```bash
cd backend
pip install -r requirements.txt

# Set environment variables in .env
OPENAI_API_KEY=your-key
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
