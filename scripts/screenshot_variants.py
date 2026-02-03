"""Capture hero variants (A and B) using Playwright.

Usage:
  python scripts/screenshot_variants.py [--url=http://127.0.0.1:5000] [--outdir=artifacts]

Requirements:
  pip install playwright requests
  python -m playwright install chromium

The script will:
  - health-check the server (retries)
  - open Chromium headless
  - for each variant (a, b): set localStorage key 'novastore_hero_variant', trigger the JS switch, wait for the DOM reflection of the variant, and take a screenshot of the hero area.
"""

import os
import sys
import time
import argparse

try:
    import requests
except Exception:
    print("Please install requests: pip install requests")
    sys.exit(2)

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Playwright is not installed. Run: pip install playwright && python -m playwright install chromium")
    sys.exit(2)


def wait_for_server(url, retries=12, delay=1.0):
    for i in range(retries):
        try:
            r = requests.get(url, timeout=2.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(delay)
    return False


def capture_variant(page, variant, outpath):
    name = variant.lower()
    print(f"- Setting variant '{name}'")
    try:
        # set localStorage and try to call exposed setter
        page.evaluate(f"localStorage.setItem('novastore_hero_variant', '{name}');")
        # if the helper is present, use it
        page.evaluate("if(window.setHeroVariant) window.setHeroVariant(localStorage.getItem('novastore_hero_variant'))")
    except Exception as e:
        print("  Warning: could not set localStorage / call setHeroVariant:", e)

    # give the page a moment to update
    try:
        selector = f".hero-grid.variant-{name}"
        page.wait_for_selector(selector, timeout=3000)
        print(f"  Variant class {selector} present.")
    except PlaywrightTimeout:
        print(f"  Timeout waiting for .hero-grid.variant-{name}; proceeding to capture full hero anyway.")

    # try to capture the hero area; fallback to full page
    try:
        hero = page.query_selector('.hero-landing')
        if hero:
            hero.screenshot(path=outpath)
        else:
            page.screenshot(path=outpath, full_page=True)
        print(f"  Saved screenshot: {outpath}")
    except Exception as e:
        print("  Error while capturing screenshot:", e)
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default=os.environ.get('NOVASTORE_URL', 'http://127.0.0.1:5000/'))
    parser.add_argument('--outdir', default='artifacts')
    args = parser.parse_args()

    base = args.url.rstrip('/') + '/'
    print(f"Checking server at {base}")
    ok = wait_for_server(base)
    if not ok:
        print(f"Server did not respond at {base}. Start your Flask server (e.g. flask run) and retry.")
        sys.exit(3)

    os.makedirs(args.outdir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1366, "height": 900})
        print("Opening page...")
        page.goto(base, wait_until='networkidle')

        variants = [('a', os.path.join(args.outdir, 'hero-A.png')),
                    ('b', os.path.join(args.outdir, 'hero-B.png'))]

        for v, path in variants:
            capture_variant(page, v, path)
            # small pause between captures
            time.sleep(0.6)

        browser.close()

    print('\nDone. Screenshots saved to:', os.path.abspath(args.outdir))
