# Reus Party Tracker - Session History

## Session 1 - January 26, 2026

### Goals
- [x] Create project documentation (AGENTS.md, AMAZONQ.md, README.md)
- [ ] Create GitHub repository
- [ ] Set up basic project structure

### Progress

**20:38** - Project kickoff
- User wants to build a party tracker for Plaça Mercadal in Reus
- Inspired by pizzint.watch
- Key features:
  - YouTube live stream embed
  - AI-powered crowd counting (screenshots every 5 min, configurable)
  - Restaurant busyness from Google Maps
  - Dark + light themes

**Research completed:**
- YouTube stream: https://www.youtube.com/watch?v=L9HyLjRVN8E
- Backup webcam found: https://www.skylinewebcams.com/webcam/espana/cataluna/tarragona/reus.html
- Restaurants on Plaça Mercadal: Museu del Vermut, Casa Coder, La Presó, Vermuts Rofes, Bar L'Àmfora
- Restaurants on Plaça del Teatre: Oplontina, As de Copas

**Party level formula defined:**
- 0-1 people = Level 0
- 2-10 people = Level 2
- 11-50 people = Level 7
- 51-100 people = Level 8
- 101-200+ people = Level 10

### Decisions Made
1. Tech stack: Python/Flask backend, vanilla HTML/CSS/JS frontend
2. Host on current EC2 instance (careful of existing services)
3. GitHub repo: apmlabs/reuspartytracker
4. Screenshot interval: 5 min default, easily configurable

### Next Steps
1. Create GitHub repo
2. Set up basic Flask skeleton
3. Implement YouTube screenshot capture
4. Test AI vision analysis

---

## Notes

### Useful Commands
```bash
# Check what's running on ports
sudo netstat -tlnp

# Start Flask dev server
cd backend && python app.py

# Test yt-dlp screenshot
yt-dlp --skip-download --write-thumbnail https://www.youtube.com/watch?v=L9HyLjRVN8E
```

### API Keys Needed
- OpenAI API key (for GPT-4 Vision)
- Google Maps API key (for Places API - restaurant data)
