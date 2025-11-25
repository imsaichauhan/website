# Bookmarks Management

This directory contains the bookmarks section of the website.

## Structure

```
bookmarks/
├── index.qmd              # AUTO-GENERATED - do not edit
├── reading/
│   └── index.qmd          # Articles, essays, research papers, quotes, books
├── media/
│   └── index.qmd          # Videos, films, podcasts, music albums
├── digital/
│   └── index.qmd          # Software, extensions, workflows, online projects, substacks, blogs
└── curiosities/
    └── index.qmd          # Stray links, odd visuals, marginal discoveries

../_data/
└── bookmarks.yml          # Central data file - edit this!

../_assets/css/
└── bookmarks.css          # Styles for bookmark cards and lists

../_scripts/
├── generate-bookmarks.py  # Generation script
└── gen-bookmarks.sh       # Wrapper script
```

**Note:** Each bookmark category now has its own subdirectory with an `index.qmd` file. This creates clean URLs like `/bookmarks/reading/` instead of `/bookmarks/reading.html`.

## Workflow

### To Add a Bookmark Card

1. **Edit `../_data/bookmarks.yml`** - Add a new entry:
   ```yaml
   - id: videos
     title: Videos
     description: Talks, documentaries, and video content
     image: https://images.unsplash.com/photo-xxxxx?w=455&h=449&fit=crop
     color_light: orange-light
     color_dark: orange-dark
     color_accent: orange
   ```

2. **Create the detail page** - Create `bookmarks/videos/index.qmd`:
   ```yaml
   ---
   title: "Videos"
   page-layout: article
   css: ../../_assets/css/bookmarks.css
   ---

   <div class="bookmark-list">
   # Videos
   <!-- Add your bookmark items here -->
   </div>
   ```
   
   **Important:** Create the subdirectory first: `mkdir bookmarks/videos`

3. **Add colors to CSS if needed** - In `../_assets/css/bookmarks.css`:
   ```css
   .orange-light { background-color: #fff3e0; }
   .orange-dark { color: #e65100; }
   .orange { background-color: #ff9800; }
   ```

4. **Regenerate and rebuild**:
   ```bash
   # Easy way - use the wrapper script
   _scripts/gen-bookmarks.sh
   quarto render
   
   # Or use venv Python directly
   /home/theodore/progress/.venv/bin/python _scripts/generate-bookmarks.py
   quarto render
   ```

### To Remove a Bookmark Card

1. Remove the entry from `../_data/bookmarks.yml`
2. (Optional) Delete the corresponding `.qmd` file
3. Run: `_scripts/gen-bookmarks.sh && quarto render`

### To Edit a Card (title, description, image, colors)

1. Edit the entry in `../_data/bookmarks.yml`
2. Run: `_scripts/gen-bookmarks.sh && quarto render`

### To Add Bookmarks to a Category

Edit the corresponding `.qmd` file (e.g., `reading.qmd`, `tools.qmd`) directly. Use this **pure Markdown** template for each bookmark:

```markdown
### [Title](URL){target="_blank"}
*domain.com*

Description of the bookmark.

---
```

**That's it!** No divs, no special syntax. Just:
- `###` for the title (h3) with a link
- `*italic*` for the URL/domain  
- Regular text for description
- `---` to separate bookmarks

The CSS automatically styles standard Markdown elements!

## Important Notes

- **NEVER edit `bookmarks/index.qmd` directly** - it's auto-generated
- Card metadata lives in `bookmarks-data.yml`
- Individual bookmarks live in category `.qmd` files
- Always run `generate-bookmarks.py` after editing `bookmarks-data.yml`
- Similar workflow to `generate-projects.py` for consistency

## Available Colors

Current color schemes defined in `bookmarks.css`:
- `blue` - Reading
- `teal` - Tools  
- `purple` - Design
- `navy` - Ideas
- `green` - References
- `brown` - Archive

Add new color schemes as needed for new categories.
