#!/usr/bin/env python3
"""generate-photos.py

Clean photos generator: reads `_data/photos.yml` and writes
`photos/index.qmd` and `photos/<slug>/index.qmd`.

The generator computes collection counts from the `images` list, emits
preview thumbnails (up to three), and places viewer HTML as raw HTML
fences so Quarto/Pandoc preserves the inner markup.
"""

import json
import logging
import sys
from pathlib import Path

try:
    import yaml
except Exception:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    raise

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "_data" / "photos.yml"
PHOTOS_DIR = ROOT / "photos"


def load_yaml(path: Path):
    if not path.exists():
        logging.error("YAML data file not found: %s", path)
        sys.exit(2)
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    logging.info("Wrote: %s", path)


def find_image_meta(images, filename):
    if not images:
        return {}
    for img in images:
        if img.get("file") == filename:
            return img
    return {}


def generate_landing_page(collections):
    front = """---
title: "Photos"
page-layout: full
listing: false

---

"""

    rows = []
    for c in collections:
        slug = c.get("slug")
        title = c.get("title", "")
        images = c.get("images") or []

        if not slug or not title or not isinstance(images, list):
            logging.warning("Skipping collection with missing required fields: %s", slug)
            continue

        date_raw = c.get("date", "")
        count = len(images)
        count_number = str(count) if count else ""

        previews = c.get("preview_images", []) or []
        first_preview = previews[0] if len(previews) > 0 else None
        second_preview = previews[1] if len(previews) > 1 else None
        third_preview = previews[2] if len(previews) > 2 else None

        preview_parts = []
        if first_preview:
            img_meta = find_image_meta(images, first_preview)
            alt = img_meta.get("alt", "") or ""
            src = f"/_assets/images/photos/{slug}/thumbnails/{first_preview}"
            preview_parts.append(f'  <div class="thumb-4-3">\n    <img src="{src}" alt="{alt}">\n  </div>')
        if second_preview:
            img_meta = find_image_meta(images, second_preview)
            alt = img_meta.get("alt", "") or ""
            src = f"/_assets/images/photos/{slug}/thumbnails/{second_preview}"
            preview_parts.append(f'  <div class="thumb-4-3 hidden sm:inline-block">\n    <img src="{src}" alt="{alt}">\n  </div>')
        if third_preview:
            img_meta = find_image_meta(images, third_preview)
            alt = img_meta.get("alt", "") or ""
            src = f"/_assets/images/photos/{slug}/thumbnails/{third_preview}"
            preview_parts.append(f'  <div class="thumb-4-3 hidden sm:inline-block">\n    <img src="{src}" alt="{alt}">\n  </div>')

        preview_block = '<div class="preview-thumbnails inline-flex gap-2">\n' + "\n".join(preview_parts) + "\n" + '</div>'

        row = (
            f"    <tr onclick=\"window.location.href='/photos/{slug}/'\" class=\"cursor-pointer hover:bg-gray-50 border-b border-neutral-300\">\n"
            f"      <td class=\"px-4 py-3\">\n"
            f"        <div class=\"collection-name font-semibold\">{title}</div>\n"
            f"      </td>\n"
            f"      <td class=\"px-4 py-3 hidden md:table-cell text-center\"><span class=\"count-number\">{count_number}</span></td>\n"
            f"      <td class=\"px-4 py-3 hidden md:table-cell text-left\">{date_raw}</td>\n"
            f"      <td class=\"px-4 py-3 text-right\">\n"
            f"        {preview_block}\n"
            f"      </td>\n"
            f"    </tr>\n"
        )
        rows.append(row)

    table = (
        "<div class=\"overflow-x-auto\">\n"
        "<table class=\"collections-table w-full text-left\">\n"
        "<thead>\n"
        "<tr class=\"border-b\">\n"
        "<th class=\"px-4 py-3 text-left\">Collection</th>\n"
        "<th class=\"px-4 py-3 hidden md:table-cell text-center\">Count</th>\n"
        "<th class=\"px-4 py-3 hidden md:table-cell text-left\">Date</th>\n"
        "<th class=\"px-4 py-3 text-right\">Photos</th>\n"
        "</tr>\n</thead>\n<tbody>\n"
        + "".join(rows)
        + "</tbody>\n</table>\n</div>\n"
    )

    content = front + '<link rel="stylesheet" href="/_assets/css/photos.css">\n\n' + '```{=html}\n' + table + '\n```\n'
    write_file(PHOTOS_DIR / "index.qmd", content)


def generate_collection_page(collection):
    slug = collection.get("slug")
    title = collection.get("title", "")
    images = collection.get("images", [])

    if not slug or not title or not isinstance(images, list):
        logging.warning("Skipping collection with missing required fields: %s", slug)
        return

    ensure_dir(PHOTOS_DIR / slug)
    out_path = PHOTOS_DIR / slug / "index.qmd"

    count = len(images) if isinstance(images, list) else 0
    description = collection.get("description", "") or ""
    # month_year is expected like "November 2025"; emit human text and a
    # machine-readable datetime if possible (YYYY-MM). Falls back to raw
    # text if parsing fails.
    month_year_raw = collection.get("month_year", "") or ""

    def month_year_to_iso(s):
        if not s or not isinstance(s, str):
            return ""
        parts = s.strip().split()
        if len(parts) < 2:
            return ""
        # last part is year, first part(s) are month name(s)
        year = parts[-1]
        month_name = " ".join(parts[:-1]).lower()
        months = {
            'january':'01','february':'02','march':'03','april':'04','may':'05','june':'06',
            'july':'07','august':'08','september':'09','october':'10','november':'11','december':'12'
        }
        # accept month name or abbreviated
        month_short = month_name[:3]
        for k in months:
            if k.startswith(month_short):
                return f"{year}-{months[k]}"
        return ""

    month_year_iso = month_year_to_iso(month_year_raw)

    front = (
        "---\n"
        f"title: \"{title}\"\n"
        "page-layout: full\n"
        "listing: false\n"
        "---\n\n"
        "<link rel=\"stylesheet\" href=\"/_assets/css/photos.css\">\n"
        "<script src=\"/_assets/js/photos-viewer-fallback.js\" defer></script>\n\n"
    )

    # Build header markup with optional month_year metadata
    month_html = ""
    if month_year_raw:
        if month_year_iso:
            month_html = f'  <p class="collection-month text-sm"><time datetime="{month_year_iso}">{month_year_raw}</time></p>\n'
        else:
            month_html = f'  <p class="collection-month text-sm">{month_year_raw}</p>\n'

    header = (
        f'<div class="collection-header mb-8">\n'
        f'  <div class="collection-header-left">\n'
        f'    <h1 class="text-4xl font-bold mb-2">{title}</h1>\n'
        f'    <p class="text-gray-700 mt-2">{description}</p>\n'
        f'  </div>\n'
        f'{month_html}'
        '</div>\n'
    )

    # Wrap header in a raw HTML fence so Quarto/Pandoc treats it as literal
    # HTML and doesn't escape or reflow inner tags. This makes output
    # consistent across pages.
    header_html = '```{=html}\n' + header + '\n```\n'

    grid_items = []
    for i, img in enumerate(images, start=1):
        file = img.get("file", "")
        alt = img.get("alt", "") or ""
        thumb = f"/_assets/images/photos/{slug}/thumbnails/{file}"
        grid_items.append(
            f'  <a href="#photo-{i}" data-image-index="{i}" class="photo-grid-item">\n'
            f'    <span class="thumb-4-3 inline-block">\n'
            f'      <img src="{thumb}" alt="{alt}" loading="lazy" class="w-full h-auto" />\n'
            '    </span>\n'
            '  </a>\n'
        )

    grid_html = '<section aria-label="Photo grid" class="photo-grid" id="photo-grid">\n' + "".join(grid_items) + '</section>\n'

    viewer_inner = (
        '<div class="photo-viewer" id="photo-viewer" style="display:none;">\n'
        '<div class="viewer-header">\n'
        '<div class="viewer-meta">\n'
        f'<span id="viewer-title">{title}</span> · \n'
        f'<span id="photo-counter">1 / {count}</span>\n'
        '</div>\n'
        '<button class="close-btn" onclick="closeViewer()">✕</button>\n'
        '</div>\n'
        '<div class="viewer-content">\n'
        '  <div class="viewer-nav-left" onclick="navigatePrev()">\n'
        '    <span class="nav-arrow" aria-hidden="true">\n'
        '      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" role="img" aria-hidden="true" focusable="false">\n'
        '        <path d="M15 6 L9 12 L15 18"/>\n'
        '      </svg>\n'
        '    </span>\n'
        '  </div>\n'
        '  <div class="viewer-main">\n'
        '    <div class="viewer-image-container"><img id="viewer-image" src="" alt="" /></div>\n'
        '    <div class="viewer-caption"><div id="caption-text" class="text-center"></div></div>\n'
        '  </div>\n'
        '  <div class="viewer-nav-right" onclick="navigateNext()">\n'
        '    <span class="nav-arrow" aria-hidden="true">\n'
        '      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" role="img" aria-hidden="true" focusable="false">\n'
        '        <path d="M9 6 L15 12 L9 18"/>\n'
        '      </svg>\n'
        '    </span>\n'
        '  </div>\n'
        '</div>\n'
        '<div class="viewer-nav-mobile">\n'
        '  <button id="prev-btn-mobile" onclick="navigatePrev()">Prev</button>\n'
        '  <button id="next-btn-mobile" onclick="navigateNext()">Next</button>\n'
        '</div>\n'
        '</div>\n'
    )

    viewer_html = '```{=html}\n' + viewer_inner + '\n```\n'

    images_json_list = []
    for img in images:
        images_json_list.append({
            "file": img.get("file", ""),
            "caption": img.get("caption", "") or "",
            "alt": img.get("alt", "") or "",
        })

    images_json = json.dumps(images_json_list, ensure_ascii=False)

    js_lines = []
    js_lines.append('<script>')
    js_lines.append('(function(){')
    js_lines.append('  var images = ' + images_json + ';')
    js_lines.append('  var slug = "' + slug + '";')
    js_lines.append('  var totalImages = images.length;')
    js_lines.append('  var currentIndex = 0;')
    js_lines.append('  var grid = document.getElementById("photo-grid");')
    js_lines.append('  var viewer = document.getElementById("photo-viewer");')
    js_lines.append('  var viewerImage = document.getElementById("viewer-image");')
    js_lines.append('  var captionText = document.getElementById("caption-text");')
    js_lines.append('  var photoCounter = document.getElementById("photo-counter");')
    js_lines.append('  function showGrid(){ if(grid) grid.style.display="grid"; if(viewer) { viewer.style.display="none"; viewer.classList.remove("active"); } document.body.style.overflow="auto"; }')
    js_lines.append('  function showViewer(index){ currentIndex = index; if(grid) grid.style.display="none"; if(!viewer) viewer = document.getElementById("photo-viewer"); if(viewer){ viewer.style.display="flex"; viewer.classList.add("active"); } document.body.style.overflow="hidden"; loadPhoto(index); }')
    js_lines.append('  function loadPhoto(index){ try{ if(!viewerImage) viewerImage = document.getElementById("viewer-image"); if(!captionText) captionText = document.getElementById("caption-text"); if(!photoCounter) photoCounter = document.getElementById("photo-counter"); var img = images[index]; if(!img) return; var src = "/_assets/images/photos/" + slug + "/originals/" + (img.file||""); if(viewerImage) { viewerImage.src = src; viewerImage.alt = img.alt || ""; } if(captionText) captionText.textContent = img.caption || ""; if(photoCounter) photoCounter.textContent = (index+1) + " / " + totalImages; currentIndex = index; }catch(e){console.error("loadPhoto error",e);} }')
    js_lines.append('  window.navigatePrev = function(){ var newIndex = currentIndex===0 ? totalImages-1 : currentIndex-1; var hash = "#photo-" + (newIndex+1); history.pushState({index:newIndex}, "", hash); loadPhoto(newIndex); }')
    js_lines.append('  window.navigateNext = function(){ var newIndex = currentIndex===totalImages-1 ? 0 : currentIndex+1; var hash = "#photo-" + (newIndex+1); history.pushState({index:newIndex}, "", hash); loadPhoto(newIndex); }')
    js_lines.append('  window.closeViewer = function(){ try{ history.replaceState(null, "", window.location.pathname); showGrid(); }catch(e){} }')
    js_lines.append('  window.openPhoto = function(evt, num){ try{ if(evt && typeof evt.preventDefault === "function") evt.preventDefault(); var idx = (typeof num === "number") ? num-1 : (parseInt(num,10)-1); if(isNaN(idx)) idx = 0; var hash = "#photo-" + (idx+1); history.pushState({index:idx}, "", hash); showViewer(idx); }catch(e){console.error("openPhoto error",e);} };')
    js_lines.append('  function handleHash(){ var hash = window.location.hash; if(!hash || hash==="#") { showGrid(); } else { var m = hash.match(/#photo-(\\d+)/); if(m){ var num = parseInt(m[1],10); if(num>=1 && num<=totalImages){ showViewer(num-1); } else { showGrid(); } } } }')
    js_lines.append('  document.addEventListener("keydown", function(e){ try{ if(viewer && (viewer.classList && viewer.classList.contains("active") || viewer.style.display==="flex")){ if(e.key==="ArrowLeft") navigatePrev(); else if(e.key==="ArrowRight") navigateNext(); else if(e.key==="Escape") closeViewer(); } }catch(e){} });')
    js_lines.append('  window.addEventListener("hashchange", handleHash);')
    js_lines.append('  window.addEventListener("popstate", handleHash);')
    js_lines.append('  handleHash();')
    js_lines.append('  document.addEventListener("click", function(e){ try{ var a = e.target.closest && e.target.closest("a[data-image-index]"); if(a){ var idx = parseInt(a.getAttribute("data-image-index"),10)-1; if(!isNaN(idx)){ var hash = "#photo-" + (idx+1); history.pushState({index:idx}, "", hash); showViewer(idx); e.preventDefault(); } } }catch(e){} });')
    js_lines.append('})();')
    js_lines.append('</script>')

    js = "\n".join(js_lines)

    content = front + header_html + grid_html + "\n" + viewer_html + "\n" + js
    write_file(out_path, content)


def main():
    data = load_yaml(DATA_FILE)
    collections = data.get('collections', []) if data else []

    ensure_dir(PHOTOS_DIR)
    generate_landing_page(collections)

    for c in collections:
        generate_collection_page(c)

    logging.info("Generation complete: 1 landing page + %d collection pages", len(collections))


if __name__ == '__main__':
    main()
