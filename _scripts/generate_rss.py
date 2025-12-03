#!/usr/bin/env python3
"""
Lightweight RSS generator for the site.

Scans `projects/`, `bookmarks/`, `photos/`, and `now/` for `.qmd` files,
extracts simple YAML front-matter (title/date) and content, and writes
`rss.xml` at the project root (RSS 2.0). Description uses the raw
markdown content wrapped in CDATA so content is preserved.

This script avoids external dependencies and uses a simple front-matter
parser that supports common title/date keys. It's intentionally minimal.
"""
import os
import re
import sys
from datetime import datetime, UTC
from email.utils import format_datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCAN_DIRS = ['projects', 'bookmarks', 'photos', 'now']
OUT_FILE = os.path.join(ROOT, 'rss.xml')
SITE_URL = 'https://imsaichauhan.pages.dev'


def read_front_matter(path):
    """Return dict with title, date (ISO), and the body (markdown)"""
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    fm = {}
    body = text
    # Look for YAML front-matter at top
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.S)
    if m:
        fm_block = m.group(1)
        body = m.group(2)
        # find simple key: value pairs
        for line in fm_block.splitlines():
            line = line.strip()
            if not line or ':' not in line:
                continue
            k, v = line.split(':', 1)
            k = k.strip()
            v = v.strip().strip('"\'')
            fm[k.lower()] = v

    return fm, body


def guess_date(fm, path):
    # front-matter date if available
    date_str = fm.get('date') or fm.get('date-posted') or fm.get('posted')
    if date_str:
        # try common formats
        for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S', '%B %Y'):
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt
            except Exception:
                continue
        try:
            # ISO parse fallback
            return datetime.fromisoformat(date_str)
        except Exception:
            pass
    # fallback to filesystem mtime
    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts)


def make_url(path):
    # path relative to root
    rel = os.path.relpath(path, ROOT).replace('\\\\', '/')
    # if index.qmd -> directory
    if rel.endswith('index.qmd'):
        url = '/' + os.path.dirname(rel) + '/'
    else:
        url = '/' + rel.replace('.qmd', '.html')
    url = url.replace('//', '/')
    return url


def escape_cdata(s):
    return s.replace(']]>', ']]]]><![CDATA[>')


def clean_content(text):
    """Strip Quarto divs and other markup for cleaner RSS content."""
    # Remove Quarto div syntax
    text = re.sub(r':::\s*\{[^}]+\}\s*', '', text)
    text = re.sub(r'^:::$', '', text, flags=re.MULTILINE)
    # Remove HTML blocks
    text = re.sub(r'```\{=html\}.*?```', '', text, flags=re.DOTALL)
    # Remove code blocks
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    # Clean up excessive whitespace
    text = re.sub(r'\n\n\n+', '\n\n', text)
    return text.strip()


def main():
    items = []
    for d in SCAN_DIRS:
        dirpath = os.path.join(ROOT, d)
        if not os.path.isdir(dirpath):
            continue
        for root_dir, _, files in os.walk(dirpath):
            for fn in files:
                if not fn.endswith('.qmd'):
                    continue
                path = os.path.join(root_dir, fn)
                fm, body = read_front_matter(path)
                title = fm.get('title') or fm.get('name') or os.path.splitext(fn)[0]
                dt = guess_date(fm, path)
                url = make_url(path)
                content = clean_content(body)
                items.append({'title': title, 'date': dt, 'url': url, 'content': content})

    # sort descending by date
    items.sort(key=lambda x: x['date'], reverse=True)
    # limit to recent 30
    items = items[:30]

    channel_title = 'Sai Prakash'
    channel_link = SITE_URL
    channel_desc = 'Recent content from Sai Prakash'

    parts = []
    parts.append('<?xml version="1.0" encoding="utf-8"?>')
    parts.append('<rss version="2.0">')
    parts.append('<channel>')
    parts.append(f'<title>{channel_title}</title>')
    parts.append(f'<link>{channel_link}</link>')
    parts.append(f'<description>{channel_desc}</description>')
    parts.append(f'<lastBuildDate>{format_datetime(datetime.now(UTC))}</lastBuildDate>')

    for it in items:
        pub = format_datetime(it['date'])
        title = it['title']
        link = SITE_URL + it['url']
        guid = link
        content = escape_cdata(it['content'])
        parts.append('<item>')
        parts.append(f'<title>{title}</title>')
        parts.append(f'<link>{link}</link>')
        parts.append(f'<guid isPermaLink="true">{guid}</guid>')
        parts.append(f'<pubDate>{pub}</pubDate>')
        parts.append('<description><![CDATA[')
        parts.append(content)
        parts.append(']]></description>')
        parts.append('</item>')

    parts.append('</channel>')
    parts.append('</rss>')

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(parts))

    print(f'Wrote {OUT_FILE} with {len(items)} items')


if __name__ == '__main__':
    main()
