# Reus Party Tracker 🎉

Real-time party activity tracker for Plaça Mercadal in Reus, Spain.

Watch the live stream, see how many people are partying, and check which restaurants are busy!

## Features

- 📺 Live YouTube stream of Plaça Mercadal
- 🎉 AI-powered party level indicator (0-10)
- 👥 Estimated crowd count
- 🍽️ Restaurant busyness levels (Google Maps data)
- 🌙 Dark & light themes

## Quick Start

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key"

# Run the server
python app.py
```

Visit `http://localhost:5050` in your browser.

## Configuration

Edit `backend/config.py` to change:
- Screenshot interval (default: 5 minutes)
- Party level thresholds
- YouTube stream URL

## Data Sources

- **Live Stream**: [Plaça Mercadal YouTube](https://www.youtube.com/watch?v=L9HyLjRVN8E)
- **Restaurant Data**: Google Maps Places API

## Restaurants Tracked

### Plaça Mercadal
- Restaurant Museu del Vermut
- Casa Coder
- La Presó
- Vermuts Rofes
- Bar L'Àmfora
- (and more)

### Plaça del Teatre
- Oplontina
- As de Copas

## Tech Stack

- Backend: Python, Flask
- Frontend: HTML, CSS, JavaScript
- AI: OpenAI GPT-4 Vision
- Video: yt-dlp + ffmpeg

## License

MIT
