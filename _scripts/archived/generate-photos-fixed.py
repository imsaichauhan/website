#!/usr/bin/env python3
"""Deprecated: generate-photos-fixed.py

This file was a temporary duplicate of `generate-photos.py`. The project
now uses `_scripts/generate-photos.py` (referenced by the Makefile).

Keeping this small wrapper in place to avoid surprises if anything calls
the old filename; it prints a short note and exits.
"""

import sys

def main():
    print("generate-photos-fixed.py is deprecated. Use _scripts/generate-photos.py instead.")
    print("Invoking that script will produce the canonical outputs.")
    # Exit with success so callers that accidentally run this do not fail builds.
    return 0

if __name__ == '__main__':
    sys.exit(main())


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
    month_year_raw = collection.get("month_year", "") or ""

    def month_year_to_iso(s):
        if not s or not isinstance(s, str):
            return ""
        parts = s.strip().split()
        if len(parts) < 2:
            return ""
        year = parts[-1]
        month_name = " ".join(parts[:-1]).lower()
        months = {
            'january':'01','february':'02','march':'03','april':'04','may':'05','june':'06',
            'july':'07','august':'08','september':'09','october':'10','november':'11','december':'12'
        }
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
        "<link rel=\"stylesheet\" href=\"/_assets/css/photos.css\">\n\n"
    )

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
        '</div>\n'
    )

    viewer_html = '```{=html}\n' + viewer_inner + '\n```\n'

