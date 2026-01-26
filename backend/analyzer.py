"""
Analyze screenshot using Kiro CLI vision
"""
import subprocess
import sys
import re
import os

def get_party_level(people_count):
    """Convert people count to party level 0-10"""
    if people_count <= 1:
        return 0
    elif people_count <= 10:
        return 2
    elif people_count <= 50:
        return 7
    elif people_count <= 100:
        return 8
    else:
        return 10

def analyze_image(image_path):
    """Use kiro-cli to count people in screenshot"""
    print(f"[DEBUG] Starting analysis of: {image_path}", flush=True)
    
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}", flush=True)
        return 0
    
    prompt = f"Look at this image: {image_path} - Count the number of people visible in the plaza. Just respond with a single number, nothing else."
    
    print(f"[DEBUG] Calling kiro-cli...", flush=True)
    
    try:
        result = subprocess.run(
            ['/home/ubuntu/.local/bin/kiro-cli', 'chat', '--trust-all-tools', prompt],
            capture_output=True,
            text=True,
            timeout=120,
            input=''  # Non-interactive mode
        )
        
        print(f"[DEBUG] Exit code: {result.returncode}", flush=True)
        print(f"[DEBUG] Stdout: {result.stdout}", flush=True)
        if result.stderr:
            print(f"[DEBUG] Stderr: {result.stderr[:200]}", flush=True)
        
        # Strip ANSI codes
        response = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', result.stdout).strip()
        
        # Get last line (the actual response after "> ")
        lines = [l.strip() for l in response.split('\n') if l.strip()]
        last_line = lines[-1] if lines else ''
        print(f"[DEBUG] Last line: {last_line}", flush=True)
        
        # Extract number from last line only
        numbers = re.findall(r'\d+', last_line)
        if numbers:
            count = int(numbers[0])
            print(f"[DEBUG] Extracted count: {count}", flush=True)
            return count
        
        return 0
        
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Kiro CLI timeout", flush=True)
        return 0
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        return 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        count = analyze_image(sys.argv[1])
        print(f"Final count: {count}")
    else:
        print("Usage: python analyzer.py <image_path>")
