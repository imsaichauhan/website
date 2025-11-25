from playwright.sync_api import sync_playwright
import time

URL = "http://localhost:8000/photos/banaras/"


def gather_diagnostics(page):
    # Returns a dict with viewer diagnostics
    return page.evaluate("""() => {
        var out = {};
        var v = document.getElementById('photo-viewer');
        out.exists = !!v;
        if(!v) return out;
        var cs = window.getComputedStyle(v);
        out.display = cs.display;
        out.visibility = cs.visibility;
        out.opacity = cs.opacity;
        out.zIndex = cs.zIndex;
        var rect = v.getBoundingClientRect();
        out.rect = { top: rect.top, left: rect.left, width: rect.width, height: rect.height };
        var img = document.getElementById('viewer-image');
        out.img = img ? { src: img.src || null, alt: img.alt || null, naturalWidth: img.naturalWidth || 0, naturalHeight: img.naturalHeight || 0 } : null;
        out.caption = (document.getElementById('caption-text') || {}).textContent || null;
        out.classList = v.className || null;
        return out;
    }""")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL)
    try:
        page.wait_for_selector("a[data-image-index='1']", timeout=5000)
    except Exception as e:
        print("ERROR: thumbnail selector not found:", e)
        browser.close()
        raise

    # Before click diagnostics
    before = gather_diagnostics(page)

    # Click the first thumbnail
    page.click("a[data-image-index='1']")
    # Wait for potential image load and UI updates
    page.wait_for_timeout(700)

    # After click diagnostics
    after = gather_diagnostics(page)
    print('URL after click:', page.url)
    print('BEFORE:', before)
    print('AFTER:', after)
    browser.close()
