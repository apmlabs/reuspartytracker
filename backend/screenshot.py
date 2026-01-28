import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'screenshots')
COOKIES_FILE = os.path.join(os.path.dirname(__file__), '..', 'youtube_cookies.json')

def capture_youtube_frame(url):
    """Capture screenshot from YouTube live stream - fullscreen, playing."""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(SCREENSHOTS_DIR, f'frame_{timestamp}.png')
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        
        # Load cookies
        if os.path.exists(COOKIES_FILE):
            with open(COOKIES_FILE) as f:
                raw_cookies = json.load(f)
            cookies = []
            for c in raw_cookies:
                cookie = {
                    'name': c['name'],
                    'value': c['value'],
                    'domain': c['domain'],
                    'path': c['path'],
                    'secure': c.get('secure', False),
                    'httpOnly': c.get('httpOnly', False),
                }
                if c.get('expirationDate'):
                    cookie['expires'] = int(c['expirationDate'])
                ss = c.get('sameSite', '').lower()
                if ss in ('strict', 'lax', 'none'):
                    cookie['sameSite'] = ss.capitalize()
                cookies.append(cookie)
            context.add_cookies(cookies)
        
        page = context.new_page()
        # Visit youtube.com first to establish cookies
        page.goto('https://www.youtube.com', timeout=60000)
        page.wait_for_timeout(2000)
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)
        
        # Click play button if visible
        try:
            page.click('button.ytp-large-play-button', timeout=3000)
            page.wait_for_timeout(2000)
        except:
            pass
        
        # Set quality to 720p
        try:
            page.click('button.ytp-settings-button', timeout=2000)
            page.wait_for_timeout(500)
            page.click('text=Quality', timeout=2000)
            page.wait_for_timeout(500)
            page.click('text=720p', timeout=2000)
            page.wait_for_timeout(1000)
        except:
            pass
        
        # Click fullscreen
        try:
            page.click('button.ytp-fullscreen-button', timeout=2000)
            page.wait_for_timeout(1000)
        except:
            pass
        
        # Move mouse away to hide controls
        page.mouse.move(0, 0)
        page.wait_for_timeout(2000)
        
        page.screenshot(path=output_path)
        browser.close()
    
    return output_path

if __name__ == '__main__':
    from config import YOUTUBE_URL
    path = capture_youtube_frame(YOUTUBE_URL)
    print(f"Captured: {path}")
