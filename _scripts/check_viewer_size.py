#!/usr/bin/env python3
import os
import threading
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json

SITE_DIR = Path(__file__).resolve().parents[1] / '_site'
PORT = 8001

class SilentHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def serve_site():
    os.chdir(SITE_DIR)
    httpd = ThreadingHTTPServer(('127.0.0.1', PORT), SilentHandler)
    print(f"Serving {SITE_DIR} on http://127.0.0.1:{PORT}")
    httpd.serve_forever()


def run_checks():
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        print('Playwright not available:', e)
        return 1

    viewports = [1440, 1200, 390]
    results = {}
    url = f'http://127.0.0.1:{PORT}/photos/banaras/index.html'
    # Allow caller to specify which image index to open via env var IMAGE_INDEX
    image_index = os.environ.get('IMAGE_INDEX', '1')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for w in viewports:
            height = 900 if w > 400 else 844
            context = browser.new_context(viewport={'width': w, 'height': height})
            page = context.new_page()
            page.goto(url, wait_until='load')
            # click the requested thumbnail anchor (default 1)
            selector = f'a[data-image-index="{image_index}"]'
            try:
                page.click(selector)
            except Exception as e:
                print('Click failed for', selector, e)
                page.close()
                continue
            # wait for viewer to appear
            page.wait_for_selector('#photo-viewer', state='visible', timeout=5000)
            # wait for image to have naturalWidth > 0
            page.wait_for_function("() => document.getElementById('viewer-image') && document.getElementById('viewer-image').naturalWidth > 0", timeout=5000)
            info = page.evaluate('''() => {
                const img = document.getElementById('viewer-image');
                const comp = window.getComputedStyle(img);
                const container = img.closest('.viewer-image-container');
                const compC = container ? window.getComputedStyle(container) : null;
                return {
                    naturalWidth: img.naturalWidth,
                    naturalHeight: img.naturalHeight,
                    inlineWidth: img.style.width || null,
                    inlineMaxWidth: img.style.maxWidth || null,
                    clientWidth: img.clientWidth,
                    clientHeight: img.clientHeight,
                    computedWidth: comp.width,
                    computedHeight: comp.height,
                    cssMaxWidth: comp.maxWidth,
                    cssMaxHeight: comp.maxHeight,
                    containerComputedWidth: compC ? compC.width : null,
                    containerComputedHeight: compC ? compC.height : null,
                    viewportWidth: window.innerWidth,
                    viewportHeight: window.innerHeight,
                    rem: parseFloat(getComputedStyle(document.documentElement).fontSize) || 16
                };
            }''')
            results[str(w)] = info
            page.close()
            context.close()
        browser.close()

    print(json.dumps(results, indent=2))
    return 0


if __name__ == '__main__':
    t = threading.Thread(target=serve_site, daemon=True)
    t.start()
    # wait briefly for server
    time.sleep(0.6)
    code = run_checks()
    # allow server thread to terminate by exiting process
    raise SystemExit(code)
