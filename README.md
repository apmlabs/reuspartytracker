# Reus Party Tracker 🎉

Real-time party activity tracker for Plaça Mercadal in Reus, Spain.

Watch the live stream, see how many people are partying, and check which restaurants are busy!

**Live**: http://54.80.204.92:5050

## Features

- 📺 Live YouTube stream screenshot of Plaça Mercadal
- 🎉 AI-powered party level indicator (0-10)
- 👥 People counting split by street vs terrace
- 🚗 Vehicle count tracking
- 🚔 Police presence detection with alert
- 📊 Unified chart with 5 metrics + time range selector (24h/7d/30d/1y)
- 🍽️ Restaurant busyness levels from Google Maps
- 🗺️ Interactive heatmap showing restaurant busyness
- 🌙 Dark & light themes

## Tracked Locations

### Plazas
- **Plaça del Teatre**: Oplontina PizzaBar, As De Copes Gastropub
- **Plaça Mercadal**: Casa Coder, Roslena Mercadal, Goofretti, El Mestral, Vivari, Maiki Poké, DITALY, Déu n'hi Do
- **Plaça Evarist Fàbregas**: La Presó, Sibuya Urban Sushi Bar, Yokoso, Saona Reus

### Top 5 Restaurants (by reviews)
1. Restaurant del Museu del Vermut (4,300 reviews)
2. Tacos La Mexicanita (2,197 reviews)
3. Khirganga Restaurant (1,884 reviews)
4. Xivarri Gastronomía (1,763 reviews)
5. Ciutat Gaudí (1,623 reviews)

## Tech Stack

- **Backend**: Python, Flask, APScheduler
- **Frontend**: HTML, CSS, JavaScript, Chart.js, Leaflet
- **AI**: Kiro CLI Vision
- **Video**: Playwright for YouTube screenshots
- **Database**: InfluxDB (time-series)
- **Restaurant Data**: Outscraper API (Google Maps)

## Setup

### Prerequisites
- Python 3.10+
- InfluxDB 2.x
- Kiro CLI installed

### Installation

```bash
# Clone repo
git clone https://github.com/apmlabs/reuspartytracker.git
cd reuspartytracker

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys:
#   OUTSCRAPER_API_KEY=your-key
#   INFLUXDB_TOKEN=your-token

# Setup InfluxDB
influx bucket create -n party_data -o reusparty

# Run
python app.py
```

Visit `http://localhost:5050`

### Systemd Service (Production)

```bash
sudo cp reusparty.service /etc/systemd/system/
sudo systemctl enable reusparty
sudo systemctl start reusparty
```

## Troubleshooting

### YouTube Screenshot Fails
- Check if cookies expired: look for "bot prompt" in screenshot
- Export fresh cookies from browser to `youtube_cookies.json`

### Restaurant Data Missing
- Check `logs/outscraper.log` for API errors
- Verify API key in `.env`
- Some restaurants don't have Google Popular Times data

### InfluxDB Connection Issues
- Verify InfluxDB is running: `systemctl status influxdb`
- Check token in `.env` matches InfluxDB

## Data Sources

- **Live Stream**: [Plaça Mercadal YouTube](https://www.youtube.com/watch?v=L9HyLjRVN8E)
- **Restaurant Data**: Google Maps via Outscraper API

## License

MIT
