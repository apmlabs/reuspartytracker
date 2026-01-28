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

def analyze_image(image_path):
    """Use kiro-cli to analyze screenshot for people, cars, and police."""
    print(f"[DEBUG] Starting analysis of: {image_path}", flush=True)
    
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}", flush=True)
        return {"people": 0, "cars": 0, "police_cars": 0, "police_vans": 0, "police_uniformed": 0}
    
    prompt = f"""Look at this image: {image_path}
Count and respond with ONLY a JSON object (no other text):
{{"people": <number of people>, "cars": <number of cars/trucks/vans>, "police_cars": <police cars>, "police_vans": <police vans>, "police_uniformed": <uniformed police officers>}}"""
    
    print(f"[DEBUG] Calling kiro-cli...", flush=True)
    
    try:
        result = subprocess.run(
            ['/home/ubuntu/.local/bin/kiro-cli', 'chat', '--trust-all-tools', prompt],
            capture_output=True, text=True, timeout=120, input=''
        )
        
        print(f"[DEBUG] Exit code: {result.returncode}", flush=True)
        print(f"[DEBUG] Stdout: {result.stdout}", flush=True)
        
        # Strip ANSI codes
        response = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', result.stdout).strip()
        
        # Find JSON in response
        match = re.search(r'\{[^}]+\}', response)
        if match:
            data = json.loads(match.group())
            print(f"[DEBUG] Parsed: {data}", flush=True)
            return {
                "people": data.get("people", 0),
                "cars": data.get("cars", 0),
                "police_cars": data.get("police_cars", 0),
                "police_vans": data.get("police_vans", 0),
                "police_uniformed": data.get("police_uniformed", 0)
            }
        
        # Fallback: try to extract just people count (old format)
        lines = [l.strip() for l in response.split('\n') if l.strip()]
        last_line = lines[-1] if lines else ''
        numbers = re.findall(r'\d+', last_line)
        if numbers:
            return {"people": int(numbers[0]), "cars": 0, "police_cars": 0, "police_vans": 0, "police_uniformed": 0}
        
        return {"people": 0, "cars": 0, "police_cars": 0, "police_vans": 0, "police_uniformed": 0}
        
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        return {"people": 0, "cars": 0, "police_cars": 0, "police_vans": 0, "police_uniformed": 0}

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
