import json
import os
import glob
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, send_file, request
from apscheduler.schedulers.background import BackgroundScheduler

from config import SCREENSHOT_INTERVAL, YOUTUBE_URL, PORT
from screenshot import capture_youtube_frame
from analyzer import get_party_level, analyze_image
from restaurants import fetch_all_restaurants, fetch_top_restaurants
from database import save_party_data, save_restaurant_data, save_top_restaurant_data, get_party_history, get_restaurant_history, get_top_restaurant_history

app = Flask(__name__, static_folder='../frontend')
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'party_data.json')
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'screenshots')

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"people_count": 0, "party_level": 0, "last_updated": None, "error": None}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def get_restaurant_busyness_avg():
    """Get average busyness of open Plaça Mercadal restaurants."""
    try:
        data, _ = fetch_all_restaurants()
        mercadal = data.get('placa_mercadal', [])
        values = [r['busyness'] for r in mercadal if r.get('is_open') and r.get('busyness') is not None]
        return sum(values) / len(values) if values else None
    except:
        return None

def get_combined_party_level(people_count):
    """Combine people count with restaurant busyness for final party level."""
    people_level = get_party_level(people_count)
    rest_avg = get_restaurant_busyness_avg()
    if rest_avg is None:
        return people_level
    # Restaurant contribution: 100% busyness = level 5, scale linearly
    rest_level = min(10, rest_avg / 20)  # 100% -> 5, 200% -> 10
    # Average both signals
    return round((people_level + rest_level) / 2)

def update_party_data():
    """Capture screenshot and analyze with AI."""
    data = load_data()
    try:
        image_path = capture_youtube_frame(YOUTUBE_URL)
        people_count = analyze_image(image_path)
        data["last_screenshot"] = image_path
        data["people_count"] = people_count
        data["party_level"] = get_combined_party_level(people_count)
        data["last_updated"] = datetime.now().isoformat()
        data["error"] = None
        save_party_data(people_count, data["party_level"])
        print(f"Screenshot: {image_path}, People: {people_count}, Level: {data['party_level']}")
    except Exception as e:
        data["error"] = str(e)
        data["last_updated"] = datetime.now().isoformat()
        print(f"Error: {e}")
    save_data(data)

@app.route('/api/party')
def get_party():
    return jsonify(load_data())

@app.route('/api/restaurants')
def get_restaurants():
    """Return restaurant list with busyness from cache."""
    data, timestamp = fetch_all_restaurants()
    return jsonify({"data": data, "last_updated": timestamp})

@app.route('/api/top-restaurants')
def get_top_restaurants():
    """Return top 25 restaurants with busyness from cache."""
    data, timestamp = fetch_top_restaurants()
    return jsonify({"data": data, "last_updated": timestamp})

@app.route('/api/history')
def get_history():
    """Return party history for charts."""
    hours = request.args.get('hours', 24, type=int)
    return jsonify(get_party_history(hours))

@app.route('/api/history/restaurants')
def get_rest_history():
    """Return restaurant history for charts."""
    hours = request.args.get('hours', 24, type=int)
    return jsonify(get_restaurant_history(hours))

@app.route('/api/history/top-restaurants')
def get_top_rest_history():
    """Return top restaurant history for charts."""
    hours = request.args.get('hours', 24, type=int)
    return jsonify(get_top_restaurant_history(hours))

@app.route('/api/screenshot')
def get_screenshot():
    """Serve the latest screenshot."""
    files = sorted(glob.glob(os.path.join(SCREENSHOTS_DIR, 'frame_*.png')))
    if files:
        return send_file(files[-1], mimetype='image/png')
    return '', 404

@app.route('/api/update', methods=['POST'])
def update_count():
    """Manually update people count (called after Kiro analysis)."""
    data = load_data()
    count = request.json.get('people_count', 0)
    data['people_count'] = count
    data['party_level'] = get_combined_party_level(count)
    data['last_updated'] = datetime.now().isoformat()
    save_data(data)
    return jsonify(data)

@app.route('/api/refresh', methods=['POST'])
def refresh():
    update_party_data()
    return jsonify(load_data())

def refresh_restaurant_data():
    """Background job to refresh restaurant data from Outscraper."""
    try:
        data, _ = fetch_all_restaurants(force_refresh=True)
        save_restaurant_data(data)
        top_data, _ = fetch_top_restaurants(force_refresh=True)
        save_top_restaurant_data(top_data)
        print(f"[{datetime.now().isoformat()}] Restaurant data refreshed")
    except Exception as e:
        print(f"Error refreshing restaurant data: {e}")

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_party_data, 'interval', seconds=SCREENSHOT_INTERVAL)
    scheduler.add_job(refresh_restaurant_data, 'interval', minutes=15)
    scheduler.start()
    # Schedule first update in 5 seconds (don't block startup)
    scheduler.add_job(update_party_data, 'date', run_date=datetime.now().replace(microsecond=0).isoformat())
    print(f"Starting server on port {PORT}, screenshot interval: {SCREENSHOT_INTERVAL}s")
    app.run(host='0.0.0.0', port=PORT, debug=False)
