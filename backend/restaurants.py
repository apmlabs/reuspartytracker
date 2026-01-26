import os
import requests
import json
from datetime import datetime

API_KEY = os.getenv('OUTSCRAPER_API_KEY')
CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'restaurants_cache.json')
CACHE_TTL = 900  # 15 minutes

RESTAURANTS = {
    "placa_mercadal": [
        "Restaurant Museu del Vermut, Reus",
        "Casa Coder, Reus",
        "La Presó, Reus",
        "Vermuts Rofes, Reus",
        "Bar L'Àmfora, Reus",
    ],
    "placa_del_teatre": [
        "Oplontina, Reus",
        "As de Copas, Reus",
    ]
}

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def is_open_now(working_hours):
    """Check if restaurant is currently open based on working_hours."""
    if not working_hours:
        return True  # Assume open if no data
    now = datetime.now()
    day_name = DAYS[now.weekday()]
    hours = working_hours.get(day_name, [])
    if not hours or hours == ['Closed']:
        return False
    # Parse hours like "12PM-12AM" or "12-7PM"
    for slot in hours:
        try:
            parts = slot.replace(' ', '').split('-')
            if len(parts) != 2:
                continue
            def parse_time(t):
                t = t.upper()
                pm = 'PM' in t
                t = t.replace('AM', '').replace('PM', '')
                h = int(t)
                if pm and h != 12:
                    h += 12
                if not pm and h == 12:
                    h = 0
                return h
            open_h, close_h = parse_time(parts[0]), parse_time(parts[1])
            if close_h == 0:
                close_h = 24
            if open_h <= now.hour < close_h:
                return True
        except:
            return True  # Assume open on parse error
    return False

def get_current_busyness(popular_times):
    """Extract current hour's busyness from popular_times data."""
    if not popular_times:
        return None
    now = datetime.now()
    day = now.isoweekday()  # 1=Mon, 7=Sun
    hour = now.hour
    for d in popular_times:
        if d.get('day') == day:
            for h in d.get('popular_times', []):
                if h.get('hour') == hour:
                    return h.get('percentage')
    return None

def fetch_restaurant_data(query):
    """Fetch restaurant data from Outscraper."""
    url = "https://api.app.outscraper.com/maps/search-v3"
    params = {"query": query, "limit": 1, "async": "false"}
    headers = {"X-API-KEY": API_KEY}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=60)
        resp = r.json()
        data = resp.get("data", resp)
        if data and len(data) > 0 and len(data[0]) > 0:
            place = data[0][0]
            is_open = is_open_now(place.get("working_hours"))
            return {
                "name": place.get("name"),
                "busyness": get_current_busyness(place.get("popular_times")) if is_open else None,
                "rating": place.get("rating"),
                "is_open": is_open,
            }
    except Exception as e:
        print(f"Error fetching {query}: {e}")
    return None

def fetch_all_restaurants():
    """Fetch data for all restaurants with caching."""
    # Check cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            cache = json.load(f)
        if datetime.now().timestamp() - cache.get('timestamp', 0) < CACHE_TTL:
            return cache.get('data', {})
    
    # Fetch fresh data
    result = {}
    for plaza, restaurants in RESTAURANTS.items():
        result[plaza] = []
        for query in restaurants:
            data = fetch_restaurant_data(query)
            if data:
                result[plaza].append(data)
            else:
                name = query.split(',')[0]
                result[plaza].append({"name": name, "busyness": None, "rating": None, "is_open": True})
    
    # Save cache
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump({"timestamp": datetime.now().timestamp(), "data": result}, f)
    
    return result

if __name__ == '__main__':
    import json
    print(json.dumps(fetch_all_restaurants(), indent=2))
