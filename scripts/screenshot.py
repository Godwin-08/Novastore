"""Simple screenshot helper using Playwright (Chromium).
Usage:
  pip install playwright
  python -m playwright install chromium
  python scripts/screenshot.py http://localhost:5000/ landing.png
"""
import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5000/'
out = sys.argv[2] if len(sys.argv) > 2 else 'landing.png'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width":1366, "height":768})
    try:
        print('DEBUG: Navigating to', url)
        page.goto(url, timeout=15000)
    except Exception as e:
        print('WARN: page.goto failed, fetching HTML via requests fallback:', e)
        import requests
        r = requests.get(url, timeout=5)
        html = r.text.replace('href="/static', 'href="http://127.0.0.1:5000/static')
        html = html.replace('src="/static', 'src="http://127.0.0.1:5000/static')
        page.set_content(html)
    # wait a bit for animations / images
    page.wait_for_timeout(1000)
    print('DEBUG: Attempting screenshot to', out)
    page.screenshot(path=out, full_page=True)
    print('Saved', out)
    browser.close()
