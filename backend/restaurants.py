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
        data = resp.get("data", resp)  # Handle both formats
        if data and len(data) > 0 and len(data[0]) > 0:
            place = data[0][0]
            return {
                "name": place.get("name"),
                "busyness": get_current_busyness(place.get("popular_times")),
                "rating": place.get("rating"),
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
                result[plaza].append({"name": name, "busyness": None, "rating": None})
    
    # Save cache
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump({"timestamp": datetime.now().timestamp(), "data": result}, f)
    
    return result

if __name__ == '__main__':
    import json
    print(json.dumps(fetch_all_restaurants(), indent=2))
