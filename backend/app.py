import json
import os
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, request
from apscheduler.schedulers.background import BackgroundScheduler

from config import SCREENSHOT_INTERVAL, YOUTUBE_URL, PORT
from screenshot import capture_youtube_frame
from analyzer import get_party_level

app = Flask(__name__, static_folder='../frontend')
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'party_data.json')

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"people_count": 0, "party_level": 0, "last_updated": None, "error": None}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def update_party_data():
    """Capture screenshot. Analysis done separately via Kiro."""
    data = load_data()
    try:
        image_path = capture_youtube_frame(YOUTUBE_URL)
        data["last_screenshot"] = image_path
        data["last_updated"] = datetime.now().isoformat()
        data["error"] = None
        print(f"Screenshot saved: {image_path}")
    except Exception as e:
        data["error"] = str(e)
        data["last_updated"] = datetime.now().isoformat()
        print(f"Error: {e}")
    save_data(data)

@app.route('/api/party')
def get_party():
    return jsonify(load_data())

@app.route('/api/update', methods=['POST'])
def update_count():
    """Manually update people count (called after Kiro analysis)."""
    data = load_data()
    count = request.json.get('people_count', 0)
    data['people_count'] = count
    data['party_level'] = get_party_level(count)
    data['last_updated'] = datetime.now().isoformat()
    save_data(data)
    return jsonify(data)

@app.route('/api/refresh', methods=['POST'])
def refresh():
    update_party_data()
    return jsonify(load_data())

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_party_data, 'interval', seconds=SCREENSHOT_INTERVAL)
    scheduler.start()
    print(f"Starting server on port {PORT}, screenshot interval: {SCREENSHOT_INTERVAL}s")
    app.run(host='0.0.0.0', port=PORT, debug=False)
