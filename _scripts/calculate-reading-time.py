#!/usr/bin/env python3
"""
Calculate estimated reading time for .qmd files and add/update reading-time field
in front matter.

Usage:
  python calculate-reading-time.py [file.qmd]          # Single file
  python calculate-reading-time.py --all               # All project files
  python calculate-reading-time.py --dir projects/     # Specific directory
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
WORDS_PER_MINUTE = 200  # Average reading speed


def count_words(text):
    """Count words in markdown text, excluding code blocks and front matter."""
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`[^`]+`', '', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove URLs
    text = re.sub(r'https?://[^\s]+', '', text)
    # Remove markdown links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove images
    text = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', text)
    # Count words
    words = re.findall(r'\b\w+\b', text)
    return len(words)


def calculate_reading_time(word_count):
    """Calculate reading time in minutes."""
    minutes = max(1, round(word_count / WORDS_PER_MINUTE))
    return minutes


def parse_qmd_file(filepath):
    """Parse .qmd file and return (front_matter_lines, body, front_matter_dict)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match front matter
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return [], content, {}
    
    fm_text = match.group(1)
    body = match.group(2)
    fm_lines = fm_text.split('\n')
    
    # Parse simple key-value pairs
    fm_dict = {}
    for line in fm_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"\'')
            fm_dict[key] = value
    
    return fm_lines, body, fm_dict


def update_front_matter(fm_lines, reading_time):
    """Update or add reading-time field in front matter lines."""
    # Check if reading-time already exists
    updated = False
    new_lines = []
    
    for line in fm_lines:
        if line.strip().startswith('reading-time:'):
            new_lines.append(f'reading-time: "{reading_time} min read"')
            updated = True
        else:
            new_lines.append(line)
    
    # If not found, add after description or at the end
    if not updated:
        inserted = False
        final_lines = []
        for i, line in enumerate(new_lines):
            final_lines.append(line)
            if line.strip().startswith('description:') and not inserted:
                final_lines.append(f'reading-time: "{reading_time} min read"')
                inserted = True
        
        if not inserted:
            final_lines.append(f'reading-time: "{reading_time} min read"')
        
        new_lines = final_lines
    
    return new_lines


def process_file(filepath):
    """Process a single .qmd file and add reading time."""
    print(f"Processing: {filepath}")
    
    fm_lines, body, fm_dict = parse_qmd_file(filepath)
    
    if not fm_lines:
        print(f"  ⚠️  No front matter found, skipping")
        return
    
    word_count = count_words(body)
    reading_time = calculate_reading_time(word_count)
    
    print(f"  📊 Words: {word_count}, Reading time: {reading_time} min")
    
    # Update front matter
    new_fm_lines = update_front_matter(fm_lines, reading_time)
    
    # Reconstruct file
    new_content = '---\n' + '\n'.join(new_fm_lines) + '\n---\n' + body
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✅ Updated with reading time: {reading_time} min")


def find_qmd_files(directory):
    """Find all .qmd files in directory recursively."""
    return list(Path(directory).rglob('*.qmd'))


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python calculate-reading-time.py [file.qmd]")
        print("  python calculate-reading-time.py --all")
        print("  python calculate-reading-time.py --dir projects/")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    if arg == '--all':
        # Process all projects
        files = find_qmd_files(ROOT / 'projects')
        print(f"Found {len(files)} .qmd files in projects/")
        for f in files:
            if f.name != 'index.qmd' or 'projects/' not in str(f):
                continue
            process_file(f)
    elif arg == '--dir':
        if len(sys.argv) < 3:
            print("Error: --dir requires a directory path")
            sys.exit(1)
        directory = ROOT / sys.argv[2]
        files = find_qmd_files(directory)
        print(f"Found {len(files)} .qmd files in {sys.argv[2]}")
        for f in files:
            process_file(f)
    else:
        # Process single file
        filepath = Path(arg)
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
        process_file(filepath)


if __name__ == '__main__':
    main()
