import os

# Screenshot interval (seconds)
SCREENSHOT_INTERVAL = int(os.getenv('SCREENSHOT_INTERVAL', 30))  # 30 sec default

# Party level thresholds: (max_people, level)
PARTY_THRESHOLDS = [(0, 0), (2, 1), (5, 2), (10, 3), (20, 4), (50, 5), (70, 7), (100, 9), (999, 10)]

# YouTube stream
YOUTUBE_URL = "https://www.youtube.com/watch?v=L9HyLjRVN8E"

# Server
PORT = int(os.getenv('PORT', 5050))
