import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('OUTSCRAPER_API_KEY')
CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'restaurants_cache.json')
CACHE_TTL = 900  # 15 minutes

RESTAURANTS = {
    "placa_mercadal": [
        "Casa Coder, Reus",
        "Roslena Mercadal, Reus",
        "Goofretti, Reus",
        "El Mestral, Reus",
        "Vivari, Reus",
        "Maiki Poké, Reus",
        "DITALY, Reus",
        "Déu n'hi Do, Reus",
    ],
    "placa_evarist_fabregas": [
        "La Presó, Reus",
        "Sibuya Urban Sushi Bar, Reus",
        "Yokoso, Reus",
        "Saona Reus",
    ],
    "placa_del_teatre": [
        "Oplontina, Reus",
        "As de Copas, Reus",
    ]
}

TOP_RESTAURANTS = [
    "Restaurant del Museu del Vermut, Reus",
    "La Presó, Reus",
    "Tacos La Mexicanita, Reus",
    "Vermuts Rofes, Reus",
    "Khirganga Restaurant, Reus",
    "Xivarri Gastronomía, Reus",
    "Ciutat Gaudí, Reus",
    "Saona Reus",
    "Cerveseria Tower, Reus",
    "Bar Bon-Mar, Reus",
    "Il Cuore, Reus",
    "Casa Coder, Reus",
    "Little Bangkok, Reus",
    "Brasería Costillar de Reus",
    "Mirall de Tres, Reus",
    "Xapatti, Reus",
    "Ferran Cerro Restaurant, Reus",
    "Vill Rus Restaurant, Reus",
    "Restaurant Cal Marc, Reus",
    "Acarigua Arepera, Reus",
    "Restaurant Lo Bon Profit, Reus",
    "Restaurant La Comarca, Reus",
    "Tapes i Tapes, Reus",
    "Flaps, Reus",
    "VÍTRIC Taverna Gastronòmica, Reus",
]

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def is_open_now(working_hours):
    """Check if restaurant is currently open based on working_hours. Returns (is_open, hours_known)."""
    if not working_hours:
        # No hours data - assume open 9am-11pm
        hour = datetime.now().hour
        return (9 <= hour < 23, False)
    now = datetime.now()
    day_name = DAYS[now.weekday()]
    hours = working_hours.get(day_name, [])
    if not hours or hours == ['Closed']:
        return (False, True)
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
                return (True, True)
        except:
            hour = datetime.now().hour
            return (9 <= hour < 23, False)  # Parse error - assume 9am-11pm
    return (False, True)

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
            is_open, hours_known = is_open_now(place.get("working_hours"))
            return {
                "name": place.get("name"),
                "busyness": get_current_busyness(place.get("popular_times")) if is_open else None,
                "rating": place.get("rating"),
                "reviews": place.get("reviews"),
                "is_open": is_open,
                "hours_known": hours_known,
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
                result[plaza].append({"name": name, "busyness": None, "rating": None, "reviews": None, "is_open": True, "hours_known": False})
    
    # Save cache
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump({"timestamp": datetime.now().timestamp(), "data": result}, f)
    
    return result

def fetch_top_restaurants():
    """Fetch data for top 20 restaurants with caching."""
    cache_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'top_restaurants_cache.json')
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            cache = json.load(f)
        if datetime.now().timestamp() - cache.get('timestamp', 0) < CACHE_TTL:
            return cache.get('data', [])
    
    result = []
    for query in TOP_RESTAURANTS:
        data = fetch_restaurant_data(query)
        if data:
            result.append(data)
    
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump({"timestamp": datetime.now().timestamp(), "data": result}, f)
    
    return result

if __name__ == '__main__':
    import json
    print(json.dumps(fetch_all_restaurants(), indent=2))
