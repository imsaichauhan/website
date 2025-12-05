#!/usr/bin/env python3
"""
Enhanced RSS generator for the site.

Scans `projects/`, `bookmarks/`, `photos/`, and `now/` for `.qmd` files,
extracts YAML front-matter (title/date/description/image) and content, and writes
`rss.xml` at the project root (RSS 2.0).

Enhanced features:
- Full HTML content in description with proper formatting
- Images converted to absolute URLs
- Better markdown-to-HTML conversion
- Support for content:encoded for full article content
- Proper metadata extraction (author, categories)
"""
import os
import re
import sys
from datetime import datetime, UTC
from email.utils import format_datetime
from html import escape

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


def markdown_to_html(text):
    """Convert markdown to HTML with proper formatting."""
    # Remove Quarto div syntax
    text = re.sub(r':::\s*\{[^}]+\}\s*', '', text)
    text = re.sub(r'^:::$', '', text, flags=re.MULTILINE)
    # Remove HTML blocks
    text = re.sub(r'```\{=html\}.*?```', '', text, flags=re.DOTALL)
    # Remove code blocks but preserve their content as <pre><code>
    def code_replacer(match):
        code = match.group(1) if match.group(1) else match.group(0)
        return f'<pre><code>{escape(code)}</code></pre>'
    text = re.sub(r'```(?:[a-z]+)?\n(.*?)```', code_replacer, text, flags=re.DOTALL)
    
    # Convert headings
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Convert bold and italic
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    
    # Convert links
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)
    
    # Convert images to absolute URLs
    text = re.sub(r'!\[([^\]]*)\]\((/[^\)]+)\)', rf'<img src="{SITE_URL}\2" alt="\1" />', text)
    text = re.sub(r'!\[([^\]]*)\]\((\.\./[^\)]+)\)', lambda m: f'<img src="{SITE_URL}/{m.group(2).replace("../", "")}" alt="{m.group(1)}" />', text)
    
    # Convert paragraphs
    lines = text.split('\n')
    html_lines = []
    in_paragraph = False
    for line in lines:
        line = line.strip()
        if not line:
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
        elif line.startswith('<h') or line.startswith('<pre>') or line.startswith('<img'):
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            html_lines.append(line)
        else:
            if not in_paragraph:
                html_lines.append('<p>')
                in_paragraph = True
            else:
                html_lines.append(' ')
            html_lines.append(line)
    if in_paragraph:
        html_lines.append('</p>')
    
    text = ''.join(html_lines)
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
                # Use pagetitle if title is empty, then fallback to filename
                title = fm.get('title') or fm.get('pagetitle') or fm.get('name') or os.path.splitext(fn)[0]
                dt = guess_date(fm, path)
                url = make_url(path)
                description = fm.get('description', '')
                image = fm.get('image', '')
                tag = fm.get('tag', '')
                
                # Convert relative image paths to absolute URLs
                if image and image.startswith('../'):
                    image = SITE_URL + '/' + image.replace('../', '')
                elif image and not image.startswith('http'):
                    image = SITE_URL + image
                
                content_html = markdown_to_html(body)
                items.append({
                    'title': title,
                    'date': dt,
                    'url': url,
                    'description': description,
                    'content': content_html,
                    'image': image,
                    'tag': tag
                })

    # sort descending by date
    items.sort(key=lambda x: x['date'], reverse=True)
    # limit to recent 30
    items = items[:30]

    channel_title = 'Sai Prakash'
    channel_link = SITE_URL
    channel_desc = 'Writing on climate, science, and ideas that shape the future'

    parts = []
    parts.append('<?xml version="1.0" encoding="utf-8"?>')
    parts.append('<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom">')
    parts.append('<channel>')
    parts.append(f'<title>{channel_title}</title>')
    parts.append(f'<link>{channel_link}</link>')
    parts.append(f'<description>{channel_desc}</description>')
    parts.append(f'<lastBuildDate>{format_datetime(datetime.now(UTC))}</lastBuildDate>')
    parts.append(f'<atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml" />')
    parts.append(f'<language>en</language>')

    for it in items:
        pub = format_datetime(it['date'])
        title = escape(it['title'])
        link = SITE_URL + it['url']
        guid = link
        description = it.get('description', '')
        content = escape_cdata(it['content'])
        image = it.get('image', '')
        tag = it.get('tag', '')
        
        parts.append('<item>')
        parts.append(f'<title>{title}</title>')
        parts.append(f'<link>{link}</link>')
        parts.append(f'<guid isPermaLink="true">{guid}</guid>')
        parts.append(f'<pubDate>{pub}</pubDate>')
        
        # Add category/tag if available
        if tag:
            parts.append(f'<category>{escape(tag)}</category>')
        
        # Short description in description field
        if description:
            parts.append(f'<description><![CDATA[{escape_cdata(description)}]]></description>')
        else:
            # Fallback to truncated content
            plain_content = re.sub(r'<[^>]+>', '', content)[:200]
            parts.append(f'<description><![CDATA[{escape_cdata(plain_content)}...]]></description>')
        
        # Full HTML content in content:encoded
        full_content = content
        # Add featured image at the top of content if available
        if image:
            full_content = f'<p><img src="{escape(image)}" alt="{escape(title)}" style="max-width: 100%; height: auto;" /></p>' + full_content
        
        parts.append('<content:encoded><![CDATA[')
        parts.append(full_content)
        parts.append(']]></content:encoded>')
        parts.append('</item>')

    parts.append('</channel>')
    parts.append('</rss>')

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(parts))

    print(f'Wrote {OUT_FILE} with {len(items)} items')


if __name__ == '__main__':
    main()
