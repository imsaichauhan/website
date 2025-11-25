#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import json

URL = 'http://127.0.0.1:8001/photos/banaras/index.html#photo-109'
VIEWPORT = {'width':1440,'height':900}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport=VIEWPORT)
    page = context.new_page()
    page.goto(URL, wait_until='load')
    page.wait_for_selector('#photo-viewer', state='visible', timeout=5000)
    page.wait_for_function("() => document.getElementById('viewer-image') && document.getElementById('viewer-image').naturalWidth > 0", timeout=5000)
    info = page.evaluate('''() => {
        const img = document.getElementById('viewer-image');
        const comp = window.getComputedStyle(img);
        const c = img.closest('.viewer-image-container');
        const compC = c ? window.getComputedStyle(c) : null;
        return {
            naturalWidth: img.naturalWidth,
            naturalHeight: img.naturalHeight,
            inlineWidth: img.style.width || null,
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
    print(json.dumps(info, indent=2))
    browser.close()
