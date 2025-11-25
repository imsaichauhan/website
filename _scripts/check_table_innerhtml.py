#!/usr/bin/env python3
"""Check table.innerHTML at a large viewport using Playwright if available.

Falls back to fetching the static HTML and extracting the <table> element if Playwright
or browsers are unavailable.
"""
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None

URL = "http://127.0.0.1:8001/photos/index.html"

def fetch_with_playwright():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(viewport={"width":1920,"height":1080})
        page = context.new_page()
        page.goto(URL)
        # Wait for table to be present
        page.wait_for_selector("table", timeout=5000)
        inner = page.eval_on_selector("table", "el => el.innerHTML")
        print(inner)
        browser.close()

def fetch_static():
    import requests
    from bs4 import BeautifulSoup
    r = requests.get(URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    if table:
        print(table.decode_contents())
    else:
        print("<table> not found", file=sys.stderr)
        sys.exit(2)

if __name__ == '__main__':
    if sync_playwright:
        try:
            fetch_with_playwright()
            sys.exit(0)
        except Exception as e:
            print("Playwright check failed:", e, file=sys.stderr)
            print("Falling back to static fetch...", file=sys.stderr)
    # Fallback
    try:
        fetch_static()
    except Exception as e:
        print("Static fetch failed:", e, file=sys.stderr)
        sys.exit(3)
