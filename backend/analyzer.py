"""
Analyze screenshot using Kiro CLI vision
"""
import subprocess
import sys
import re
import os
import json

from config import PARTY_THRESHOLDS

def get_party_level(people_count):
    """Convert people count to party level 0-10"""
    for max_ppl, level in PARTY_THRESHOLDS:
        if people_count <= max_ppl:
            return level
    return 10

def _run_kiro(prompt):
    """Run kiro-cli and return parsed JSON or None."""
    try:
        result = subprocess.run(
            ['/home/ubuntu/.local/bin/kiro-cli', 'chat', '--trust-all-tools', prompt],
            capture_output=True, text=True, timeout=120, input=''
        )
        response = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', result.stdout).strip()
        match = re.search(r'\{[^}]+\}', response)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"[ERROR] kiro-cli: {e}", flush=True)
    return None

def analyze_image(image_path):
    """Use kiro-cli to analyze screenshot - two calls: people/cars + police."""
    print(f"[DEBUG] Starting analysis of: {image_path}", flush=True)
    
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}", flush=True)
        return {"people": 0, "street": 0, "terrace": 0, "cars": 0, "police_cars": 0, "police_vans": 0, "police_uniformed": 0}
    
    # Call 1: People and cars
    people_prompt = f"""Look at this image: {image_path}

Count people and vehicles in this plaza image.

PEOPLE - Count in TWO categories:
- "street": People walking/standing in the plaza (not at restaurants)
- "terrace": People sitting at restaurant terraces/outdoor seating
Be CONSERVATIVE - if unsure, don't count.

CARS - Count all vehicles (cars, vans, trucks).

Return ONLY JSON: {{"street": N, "terrace": N, "cars": N}}"""

    print(f"[DEBUG] Call 1: people/cars...", flush=True)
    people_data = _run_kiro(people_prompt) or {}
    print(f"[DEBUG] People result: {people_data}", flush=True)
    
    # Call 2: Police detection
    police_prompt = f"""Look at this image: {image_path}

POLICE DETECTION ONLY - Ignore people and regular cars.

### Policía Local (Reus) - MOST COMMON
Small car (NOT a van) with THREE-TONE paint:
- Bottom/lower body: BRIGHT YELLOW
- Middle/upper doors: DARK BLUE  
- Roof: WHITE

### Other Police Types
- Mossos d'Esquadra: Dark blue car with RED stripe
- Guardia Civil: Dark GREEN vehicles
- Policía Nacional: Blue and white vehicles
- Any vehicle with BLUE FLASHING LIGHTS

### NOT Police
- DHL/Correos: Large yellow VANS (solid yellow, no blue)

Return ONLY JSON: {{"police_cars": N, "police_vans": N, "police_uniformed": N}}"""

    print(f"[DEBUG] Call 2: police...", flush=True)
    police_data = _run_kiro(police_prompt) or {}
    print(f"[DEBUG] Police result: {police_data}", flush=True)
    
    street = people_data.get("street", 0)
    terrace = people_data.get("terrace", 0)
    
    return {
        "people": street + terrace,
        "street": street,
        "terrace": terrace,
        "cars": people_data.get("cars", 0),
        "police_cars": police_data.get("police_cars", 0),
        "police_vans": police_data.get("police_vans", 0),
        "police_uniformed": police_data.get("police_uniformed", 0)
    }

def calc_police_score(police_cars, police_vans, police_uniformed):
    """Calculate police score: cars×2 + vans×4 + uniformed×1"""
    return police_cars * 2 + police_vans * 4 + police_uniformed * 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = analyze_image(sys.argv[1])
        score = calc_police_score(result["police_cars"], result["police_vans"], result["police_uniformed"])
        print(f"Result: {result}, Police Score: {score}")
    else:
        print("Usage: python analyzer.py <image_path>")
