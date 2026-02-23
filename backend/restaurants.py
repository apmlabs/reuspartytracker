import os
import requests
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import pytz

load_dotenv()

# Logging
LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'outscraper.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
api_logger = logging.getLogger('outscraper')
api_logger.setLevel(logging.INFO)
if not api_logger.handlers:
    handler = logging.FileHandler(LOG_FILE)
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    api_logger.addHandler(handler)

API_KEY = os.getenv('OUTSCRAPER_API_KEY')
CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'restaurants_cache.json')
SPAIN_TZ = pytz.timezone('Europe/Madrid')
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# All restaurants by category
RESTAURANTS = {
    "placa_mercadal": [
        "Casa Coder, Reus", "Goofretti, Reus",
    ],
    "placa_evarist_fabregas": [
        "La Presó, Reus",
    ],
    "archived": [
        # Moved from placa_mercadal
        "Roslena Mercadal, Reus", "El Mestral, Reus", "Vivari, Reus", 
        "Maiki Poké, Reus", "DITALY, Reus", "Déu n'hi Do, Reus",
        "Xivarri Gastronomía, Reus",
        # Moved from placa_evarist_fabregas
        "Sibuya Urban Sushi Bar, Reus", "Yokoso, Reus", "Saona Reus",
        # Moved from placa_del_teatre
        "Oplontina, Reus", "As de Copas, Reus",
        # Moved from top
        "Restaurant del Museu del Vermut, Reus", "Khirganga Restaurant, Reus", 
        "Ciutat Gaudí, Reus", "Tacos La Mexicanita, Reus",
        # Moved from top
        "Tacos La Mexicanita, Reus",
        # Original archived
        "Vermuts Rofes, Reus", "Cerveseria Tower, Reus", "Bar Bon-Mar, Reus",
        "Xapatti, Reus", "Restaurant Cal Marc, Reus", "Flaps, Reus",
        "VÍTRIC Taverna Gastronòmica, Reus", "Il Cuore, Reus", "Little Bangkok, Reus",
        "Brasería Costillar de Reus", "Mirall de Tres, Reus", "Ferran Cerro Restaurant, Reus",
        "Acarigua Arepera, Reus", "Restaurant Lo Bon Profit, Reus", "Restaurant La Comarca, Reus",
        "Tapes i Tapes, Reus", "VÍTRIC Taverna Gastronòmica, Reus",
    ],
}

# Restaurants with confirmed Popular Times data
HAS_POPULAR_TIMES = {
    'La Presó', 'Casa Coder', 'Goofretti'
}


def is_open_now(working_hours):
    """Check if restaurant is open. Returns (is_open, hours_known)."""
    now = datetime.now(SPAIN_TZ)
    if not working_hours:
        return (9 <= now.hour < 23, False)
    
    hours = working_hours.get(DAYS[now.weekday()], [])
    if not hours or hours == ['Closed']:
        return (False, True)
    
    for slot in hours:
        try:
            parts = slot.replace(' ', '').split('-')
            if len(parts) != 2:
                continue
            def parse_time(t, other=''):
                t = t.upper()
                pm, am = 'PM' in t, 'AM' in t
                if not pm and not am:
                    pm = 'PM' in other.upper()
                h = int(float(t.replace('AM','').replace('PM','').replace(':','.')))
                if pm and h != 12: h += 12
                if am and h == 12: h = 0
                return h
            open_h, close_h = parse_time(parts[0], parts[1]), parse_time(parts[1], parts[0])
            if close_h == 0: close_h = 24
            if open_h <= now.hour < close_h:
                return (True, True)
        except:
            return (9 <= now.hour < 23, False)
    return (False, True)


def get_current_busyness(popular_times):
    """Extract current hour's busyness percentage."""
    if not popular_times:
        return None
    now = datetime.now()
    for d in popular_times:
        if d.get('day') == now.isoweekday():
            for h in d.get('popular_times', []):
                if h.get('hour') == now.hour:
                    return h.get('percentage')
    return None


def should_fetch(cached, name=""):
    """Determine if we should fetch fresh data."""
    hour = datetime.now(SPAIN_TZ).hour
    
    if not cached:
        return True
    
    has_pt = any(pt in name for pt in HAS_POPULAR_TIMES)
    if not has_pt:
        # NOTE: 21:00 archived check disabled to reduce API costs
        # Uncomment below to re-enable daily check for archived restaurants
        # if hour != 21:
        #     api_logger.info(f" Skipping {name}: no popular times, not 21:00")
        #     return False
        # return True
        api_logger.info(f" Skipping {name}: no popular times (archived check disabled)")
        return False
    
    if cached.get('hours_known'):
        is_open, _ = is_open_now(cached.get('working_hours'))
        if not is_open:
            api_logger.info(f" Skipping {name}: closed")
            return False
    
    if not cached.get('hours_known') and not (9 <= hour < 23):
        api_logger.info(f" Skipping {name}: unknown hours, outside 9-23")
        return False
    
    return True


def fetch_from_api(query):
    """Fetch single restaurant from Outscraper API."""
    try:
        api_logger.info(f" Calling API for: {query}")
        r = requests.get(
            "https://api.app.outscraper.com/maps/search-v3",
            params={"query": query, "limit": 1, "async": "false"},
            headers={"X-API-KEY": API_KEY},
            timeout=60
        )
        data = r.json().get("data", r.json())
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


def _recalc_is_open(r):
    """Recalculate is_open for a restaurant dict, return new dict."""
    is_open, hours_known = is_open_now(r.get('working_hours'))
    result = {**r, 'is_open': is_open, 'hours_known': hours_known}
    if not is_open:
        result['busyness'] = 0
    return result


def _find_cached(name, cache_by_name):
    """Find cached restaurant by substring match."""
    q = name.lower()
    for cached_name, data in cache_by_name.items():
        c = cached_name.lower()
        if q in c or c in q:
            return data
        shorter, longer = (q, c) if len(q) < len(c) else (c, q)
        matches = sum(1 for i, ch in enumerate(shorter) if i < len(longer) and ch == longer[i])
        if matches / len(shorter) > 0.6:
            return data
    return None


def fetch_restaurants(categories=None, force_refresh=False):
    """
    Unified fetch for all restaurant types.
    categories: list of keys from RESTAURANTS dict, or None for all non-archived
    Returns: {category: [restaurants]}, timestamp
    """
    if categories is None:
        categories = [k for k in RESTAURANTS if k != 'archived']
    
    # Load cache
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            cache = json.load(f)
    cached_data = cache.get('data', {})
    
    # Early return if not forcing refresh
    if not force_refresh and cached_data:
        result = {}
        for cat in categories:
            result[cat] = [_recalc_is_open(r) for r in cached_data.get(cat, [])]
        return result, cache.get('timestamp', 0)
    
    # Build name lookup from all cached data
    cache_by_name = {}
    for cat_list in cached_data.values():
        for r in cat_list:
            cache_by_name[r.get('name', '')] = r
    
    # Fetch fresh data
    hour = datetime.now(SPAIN_TZ).hour
    cats_to_fetch = list(categories)
    # NOTE: Archived check at 21:00 disabled to reduce API costs
    # Uncomment below to re-enable:
    # if hour == 21 and 'archived' not in cats_to_fetch:
    #     cats_to_fetch.append('archived')
    
    result = {}
    got_any = False
    
    for cat in cats_to_fetch:
        result[cat] = []
        for query in RESTAURANTS.get(cat, []):
            name = query.split(',')[0]
            cached = _find_cached(name, cache_by_name)
            
            if should_fetch(cached, name):
                data = fetch_from_api(query)
                if data:
                    result[cat].append(data)
                    got_any = True
                    # If archived restaurant has busyness, log it
                    if cat == 'archived' and data.get('busyness') is not None:
                        api_logger.info(f" FOUND busyness for archived: {name} = {data.get('busyness')}%")
                elif cached:
                    result[cat].append(_recalc_is_open(cached))
                else:
                    is_open_default = 9 <= hour < 23
                    result[cat].append({"name": name, "busyness": None, "rating": None, "reviews": None, "is_open": is_open_default, "hours_known": False})
            elif cached:
                result[cat].append(_recalc_is_open(cached))
            else:
                is_open_default = 9 <= hour < 23
                result[cat].append({"name": name, "busyness": None, "rating": None, "reviews": None, "is_open": is_open_default, "hours_known": False})
    
    # Save cache with recalculated values
    ts = datetime.now().timestamp()
    save_data = {**cached_data}
    for cat in result:
        save_data[cat] = result[cat]
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump({"timestamp": ts, "data": save_data}, f)
    
    # Return only requested categories (not archived unless requested)
    return {k: v for k, v in result.items() if k in categories}, ts


if __name__ == '__main__':
    import json
    data, ts = fetch_restaurants()
    print(json.dumps(data, indent=2))
