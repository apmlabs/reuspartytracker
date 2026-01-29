import json
import os
import glob
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, send_file, request
from apscheduler.schedulers.background import BackgroundScheduler

from config import SCREENSHOT_INTERVAL, YOUTUBE_URL, PORT
from screenshot import capture_youtube_frame
from analyzer import get_party_level, analyze_image, calc_police_score
from restaurants import fetch_restaurants
from database import save_party_data, save_restaurant_data, get_party_history, get_restaurant_history, get_restaurant_history_by_name, get_police_sightings

app = Flask(__name__, static_folder='../frontend')
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'party_data.json')
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'screenshots')


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"people_count": 0, "party_level": 0, "car_count": 0, "police_count": 0, 
            "police_score": 0, "police_cars": 0, "police_vans": 0, "police_uniformed": 0, 
            "last_updated": None, "error": None}


def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)


def get_restaurant_busyness_avg():
    """Get average busyness of open Plaça Mercadal restaurants."""
    try:
        data, _ = fetch_restaurants(['placa_mercadal'])
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
    rest_level = min(10, rest_avg / 20)
    return round((people_level + rest_level) / 2)


def update_party_data():
    """Capture screenshot and analyze with AI."""
    data = load_data()
    try:
        image_path = capture_youtube_frame(YOUTUBE_URL)
        analysis = analyze_image(image_path)
        
        people_count = analysis["people"]
        street_count = analysis.get("street", 0)
        terrace_count = analysis.get("terrace", 0)
        car_count = analysis["cars"]
        police_cars = analysis["police_cars"]
        police_vans = analysis["police_vans"]
        police_uniformed = analysis["police_uniformed"]
        police_score = calc_police_score(police_cars, police_vans, police_uniformed)
        
        data.update({
            "last_screenshot": image_path,
            "people_count": people_count,
            "street_count": street_count,
            "terrace_count": terrace_count,
            "car_count": car_count,
            "police_count": police_cars + police_vans + police_uniformed,
            "police_score": police_score,
            "police_cars": police_cars,
            "police_vans": police_vans,
            "police_uniformed": police_uniformed,
            "party_level": get_combined_party_level(people_count),
            "last_updated": datetime.now().isoformat(),
            "error": None
        })
        
        save_party_data(people_count, data["party_level"], car_count, police_score,
                       police_cars, police_vans, police_uniformed, street_count, terrace_count)
        print(f"Screenshot: {image_path}, People: {people_count} (street: {street_count}, terrace: {terrace_count}), "
              f"Cars: {car_count}, Police: {data['police_count']} (score: {police_score}), Level: {data['party_level']}")
    except Exception as e:
        data["error"] = str(e)
        data["last_updated"] = datetime.now().isoformat()
        print(f"Error: {e}")
    save_data(data)


def refresh_restaurant_data():
    """Background job to refresh all restaurant data."""
    try:
        # Fetch all categories (plazas + top), archived checked at 21:00 automatically
        data, _ = fetch_restaurants(force_refresh=True)
        save_restaurant_data(data)
        print(f"[{datetime.now().isoformat()}] Restaurant data refreshed")
    except Exception as e:
        print(f"Error refreshing restaurant data: {e}")


@app.route('/api/party')
def get_party():
    return jsonify(load_data())


@app.route('/api/restaurants')
def get_restaurants():
    """Return all restaurants by category."""
    data, timestamp = fetch_restaurants()  # All non-archived
    return jsonify({"data": data, "last_updated": timestamp})


@app.route('/api/history')
def get_history():
    """Get history data. type=party (default) or restaurants. category=top for top restaurants."""
    hours = request.args.get('hours', 24, type=int)
    data_type = request.args.get('type', 'party')
    if data_type == 'restaurants':
        category = request.args.get('category')
        if category == 'top':
            return jsonify(get_restaurant_history_by_name(hours, ['top']))
        return jsonify(get_restaurant_history(hours))
    return jsonify(get_party_history(hours))


@app.route('/api/screenshot')
def get_screenshot():
    files = sorted(glob.glob(os.path.join(SCREENSHOTS_DIR, 'frame_*.png')))
    if files:
        return send_file(files[-1], mimetype='image/png')
    return '', 404


@app.route('/api/screenshot/<filename>')
def get_screenshot_by_name(filename):
    """Serve a specific screenshot by filename."""
    path = os.path.join(SCREENSHOTS_DIR, filename)
    if os.path.exists(path):
        return send_file(path, mimetype='image/png')
    return '', 404


@app.route('/api/police-sightings')
def get_police_sightings_api():
    """Return all police sightings with matched screenshot filenames."""
    sightings = get_police_sightings()
    files = sorted(glob.glob(os.path.join(SCREENSHOTS_DIR, 'frame_*.png')))
    file_times = []
    for f in files:
        name = os.path.basename(f)
        # frame_20260129_121152.png -> 2026-01-29T12:11:52
        try:
            ts = name[6:21]  # 20260129_121152
            file_times.append((name, ts))
        except:
            pass
    
    for s in sightings:
        # Find closest screenshot to this timestamp
        ts = s['timestamp'][:19].replace('-', '').replace('T', '_').replace(':', '')  # 20260129_121746
        best = None
        for fname, ftime in file_times:
            if ftime <= ts:
                best = fname
            else:
                break
        s['screenshot'] = best
    
    return jsonify(sightings)


@app.route('/api/update', methods=['POST'])
def update_count():
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


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/police')
def police_page():
    return send_from_directory(app.static_folder, 'police.html')


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_party_data, 'interval', seconds=SCREENSHOT_INTERVAL)
    scheduler.add_job(refresh_restaurant_data, 'interval', minutes=30)
    scheduler.start()
    scheduler.add_job(update_party_data, 'date', run_date=datetime.now().replace(microsecond=0).isoformat())
    print(f"Starting server on port {PORT}, screenshot interval: {SCREENSHOT_INTERVAL}s")
    app.run(host='0.0.0.0', port=PORT, debug=False)
