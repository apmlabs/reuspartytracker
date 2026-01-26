import os

# Screenshot interval (seconds)
SCREENSHOT_INTERVAL = int(os.getenv('SCREENSHOT_INTERVAL', 300))  # 5 min default

# Party level thresholds: (max_people, level)
PARTY_THRESHOLDS = [(1, 0), (10, 2), (50, 7), (100, 8), (200, 10)]

# YouTube stream
YOUTUBE_URL = "https://www.youtube.com/watch?v=L9HyLjRVN8E"

# Server
PORT = int(os.getenv('PORT', 5050))
