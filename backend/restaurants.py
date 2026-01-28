import os
import requests
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Setup file logging for Outscraper API calls
LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'outscraper.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
api_logger = logging.getLogger('outscraper')
api_logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
api_logger.addHandler(handler)

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

# Top 5 restaurants with confirmed Popular Times data (not in plaza lists)
TOP_RESTAURANTS = [
    "Restaurant del Museu del Vermut, Reus",
    "Tacos La Mexicanita, Reus",
    "Khirganga Restaurant, Reus",
    "Xivarri Gastronomía, Reus",
    "Ciutat Gaudí, Reus",
]

# Archived - no Popular Times data or lower priority
TOP_RESTAURANTS_ARCHIVED = [
    "Vermuts Rofes, Reus",
    "Cerveseria Tower, Reus",
    "Bar Bon-Mar, Reus",
    "Xapatti, Reus",
    "Restaurant Cal Marc, Reus",
    "Flaps, Reus",
    "VÍTRIC Taverna Gastronòmica, Reus",
    "Il Cuore, Reus",
    "Little Bangkok, Reus",
    "Brasería Costillar de Reus",
    "Mirall de Tres, Reus",
    "Ferran Cerro Restaurant, Reus",
    "Acarigua Arepera, Reus",
    "Restaurant Lo Bon Profit, Reus",
    "Restaurant La Comarca, Reus",
    "Tapes i Tapes, Reus",
    "VÍTRIC Taverna Gastronòmica, Reus",
]

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Restaurants confirmed to have Google Popular Times data (based on historical DB analysis)
RESTAURANTS_WITH_POPULAR_TIMES = {
    # Plaza restaurants
    'Roslena Mercadal', 'Déu n\'hi Do', 'La Presó', 'Casa Coder', 'Saona Reus', 'Sibuya',
    # Top 5 restaurants
    'Restaurant del Museu del Vermut', 'Tacos La Mexicanita', 'Khirganga Restaurant',
    'Xivarri Gastronomía', 'Ciutat Gaudí'
}

def should_fetch_restaurant(cached_restaurant, name=""):
    """Determine if we should fetch fresh data for this restaurant."""
    import pytz
    spain = pytz.timezone('Europe/Madrid')
    now = datetime.now(spain)
    hour = now.hour
    
    # No cache at all - must fetch to get working_hours
    if not cached_restaurant:
        return True
    
    hours_known = cached_restaurant.get('hours_known', False)
    is_open = cached_restaurant.get('is_open', True)
    
    # Check whitelist
    has_popular_times = any(pt in name for pt in RESTAURANTS_WITH_POPULAR_TIMES)
    
    # No Popular Times data - only fetch at 21:00 (to discover new data)
    if not has_popular_times:
        if hour != 21:
            api_logger.info(f" Skipping {name}: no popular times, not 21:00")
            return False
        return True
    
    # Closed - skip
    if hours_known and not is_open:
        api_logger.info(f" Skipping {name}: closed")
        return False
    
    # Unknown hours - only fetch 9-23
    if not hours_known:
        if not (9 <= hour < 23):
            api_logger.info(f" Skipping {name}: unknown hours, outside 9-23")
            return False
    
    return True

def is_open_now(working_hours):
    """Check if restaurant is currently open based on working_hours. Returns (is_open, hours_known)."""
    import pytz
    spain = pytz.timezone('Europe/Madrid')
    now = datetime.now(spain)
    if not working_hours:
        # No hours data - assume open 9am-11pm
        return (9 <= now.hour < 23, False)
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
            def parse_time(t, other_t=''):
                t = t.upper()
                pm = 'PM' in t
                am = 'AM' in t
                # If no AM/PM, inherit from other part of range
                if not pm and not am:
                    pm = 'PM' in other_t.upper()
                t = t.replace('AM', '').replace('PM', '').replace(':', '.')
                h = int(float(t))
                if pm and h != 12:
                    h += 12
                if am and h == 12:
                    h = 0
                return h
            open_h = parse_time(parts[0], parts[1])
            close_h = parse_time(parts[1], parts[0])
            if close_h == 0:
                close_h = 24
            if open_h <= now.hour < close_h:
                return (True, True)
        except:
            spain = pytz.timezone('Europe/Madrid')
            hour = datetime.now(spain).hour
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
        api_logger.info(f" Calling API for: {query}")
        r = requests.get(url, params=params, headers=headers, timeout=60)
        resp = r.json()
        data = resp.get("data", resp)
        if data and len(data) > 0 and len(data[0]) > 0:
            place = data[0][0]
            is_open, hours_known = is_open_now(place.get("working_hours"))
            api_logger.info(f" Success: {query} (open={is_open})")
            return {
                "name": place.get("name"),
                "busyness": get_current_busyness(place.get("popular_times")),
                "rating": place.get("rating"),
                "reviews": place.get("reviews"),
                "is_open": is_open,
                "hours_known": hours_known,
                "working_hours": place.get("working_hours"),
            }
        api_logger.info(f" No data for: {query}")
    except Exception as e:
        api_logger.info(f" Error fetching {query}: {e}")
    return None

def fetch_all_restaurants(force_refresh=False):
    """Return cached data immediately with timestamp. Refresh only if forced."""
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            cache = json.load(f)
    
    cached_data = cache.get('data', {})
    
    # Return cached data if not forcing refresh
    if not force_refresh and cached_data:
        # Zero busyness for closed restaurants
        for plaza, items in cached_data.items():
            for r in items:
                if not r.get('is_open'):
                    r['busyness'] = 0
        return cached_data, cache.get('timestamp', 0)
    
    # Build lookup of cached restaurants by query name (substring match)
    cached_by_name = {}
    for plaza_list in cached_data.values():
        for r in plaza_list:
            cached_by_name[r.get('name', '')] = r
    
    def find_cached(query_name):
        """Find cached restaurant by character overlap (>60% match)."""
        q = query_name.lower()
        for cached_name, data in cached_by_name.items():
            c = cached_name.lower()
            # Check substring first
            if q in c or c in q:
                return data
            # Check character overlap
            shorter, longer = (q, c) if len(q) < len(c) else (c, q)
            matches = sum(1 for i, ch in enumerate(shorter) if i < len(longer) and ch == longer[i])
            if matches / len(shorter) > 0.6:
                return data
        return None
    
    # Fetch fresh data (smart: skip closed restaurants)
    result = {}
    got_any = False
    for plaza, restaurants in RESTAURANTS.items():
        result[plaza] = []
        for query in restaurants:
            name = query.split(',')[0]
            cached_r = find_cached(name)
            
            if should_fetch_restaurant(cached_r, name):
                data = fetch_restaurant_data(query)
                if data:
                    result[plaza].append(data)
                    got_any = True
                elif cached_r:
                    result[plaza].append(cached_r)  # Keep old data
                else:
                    result[plaza].append({"name": name, "busyness": None, "rating": None, "reviews": None, "is_open": True, "hours_known": False})
            elif cached_r:
                # Recalculate is_open based on current time
                is_open, hours_known = is_open_now(cached_r.get('working_hours'))
                cached_r = {**cached_r, 'is_open': is_open, 'hours_known': hours_known}
                if not is_open:
                    cached_r = {**cached_r, 'busyness': 0}
                result[plaza].append(cached_r)
            else:
                result[plaza].append({"name": name, "busyness": None, "rating": None, "reviews": None, "is_open": True, "hours_known": False})
    
    # Only save if we got some real data
    if got_any:
        ts = datetime.now().timestamp()
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w') as f:
            json.dump({"timestamp": ts, "data": result}, f)
        return result, ts
    
    # Return old cache if refresh failed
    return cache.get('data', {}), cache.get('timestamp', 0)

def fetch_top_restaurants(force_refresh=False):
    """Return cached data immediately with timestamp. Refresh only if forced."""
    import pytz
    spain = pytz.timezone('Europe/Madrid')
    hour = datetime.now(spain).hour
    
    cache_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'top_restaurants_cache.json')
    cache = {}
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            cache = json.load(f)
    
    cached_data = cache.get('data', [])
    top_names = {q.split(',')[0] for q in TOP_RESTAURANTS}
    
    if not force_refresh and cached_data:
        # Only return the 5 TOP_RESTAURANTS, not archived ones
        filtered = []
        for r in cached_data:
            if any(n in r.get('name', '') for n in top_names):
                # Recalculate is_open based on current time
                is_open, hours_known = is_open_now(r.get('working_hours'))
                r = {**r, 'is_open': is_open, 'hours_known': hours_known}
                if not is_open:
                    r = {**r, 'busyness': 0}
                filtered.append(r)
        return filtered, cache.get('timestamp', 0)
    
    # Build lookup by name
    cached_by_name = {r.get('name', ''): r for r in cached_data}
    
    def find_cached(query_name):
        q = query_name.lower()
        for cached_name, data in cached_by_name.items():
            c = cached_name.lower()
            if q in c or c in q:
                return data
            shorter, longer = (q, c) if len(q) < len(c) else (c, q)
            matches = sum(1 for i, ch in enumerate(shorter) if i < len(longer) and ch == longer[i])
            if matches / len(shorter) > 0.6:
                return data
        return None
    
    # Fetch main top restaurants
    result = []
    for query in TOP_RESTAURANTS:
        name = query.split(',')[0]
        cached_r = find_cached(name)
        
        if should_fetch_restaurant(cached_r, name):
            data = fetch_restaurant_data(query)
            if data:
                result.append(data)
            elif cached_r:
                result.append(cached_r)
        elif cached_r:
            # Recalculate is_open based on current time
            is_open, hours_known = is_open_now(cached_r.get('working_hours'))
            cached_r = {**cached_r, 'is_open': is_open, 'hours_known': hours_known}
            if not is_open:
                cached_r = {**cached_r, 'busyness': 0}
            result.append(cached_r)
        else:
            # No cache, fetch anyway to get basic info
            data = fetch_restaurant_data(query)
            if data:
                result.append(data)
    
    # Fetch archived restaurants only at 21:00
    if hour == 21:
        for query in TOP_RESTAURANTS_ARCHIVED:
            name = query.split(',')[0]
            data = fetch_restaurant_data(query)
            if data and data.get('busyness') is not None:
                api_logger.info(f" FOUND busyness for archived: {name} = {data.get('busyness')}%")
                result.append(data)
    
    # Only save if we got some data
    if result:
        ts = datetime.now().timestamp()
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump({"timestamp": ts, "data": result}, f)
        # Return only TOP_RESTAURANTS (not archived)
        filtered = [r for r in result if any(n in r.get('name', '') for n in top_names)]
        return filtered, ts
    
    # Return old cache if refresh failed
    filtered = [r for r in cached_data if any(n in r.get('name', '') for n in top_names)]
    return filtered, cache.get('timestamp', 0)

if __name__ == '__main__':
    import json
    print(json.dumps(fetch_all_restaurants(), indent=2))
