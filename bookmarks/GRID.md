Bookmarks grid usage

This folder's index pages (for example `curiosities/index.qmd`) can be written as a simple markdown bullet list and converted to the site's project-style grid automatically at build time.

Format

- Add `bookmarks_grid: true` to the page frontmatter to enable the conversion filter.
- Use a single bullet per bookmark with this pattern:

  - [Title](URL) | Short description | Tag

  Use a pipe `|` to separate the title, description, and optional tag. The tag is optional but recommended (single word or short phrase).

Alternatives for the separator

- If typing an em-dash is inconvenient on your keyboard, you can use a pipe `|` (recommended) or `--` (double hyphen) instead. The filter accepts em-dash, en-dash, single hyphen, or pipe as separators. Examples:

  - [Title](URL) | Short description | Tag
  - [Title](URL) -- Short description -- Tag

Using `|` is the simplest and safest: it's easy to type and unlikely to appear in normal descriptions.

Example

---
bookmarks_grid: true
---

- [Some neat thing](https://example.com) | A short summary of the link. | Culture
- [Another one](https://example.org) | Why it's interesting. | Science

Implementation details

- The filter is a Pandoc Lua filter located at `_filters/bookmarks-grid.lua`.
- It runs only when `bookmarks_grid: true` is present in the page metadata, so it won't affect other pages.
- The filter turns the bullet list into the same block structure used by `projects/index.qmd` (classes: `.projects-grid`, `.project-grid-card`, `.project-grid-title`, `.project-grid-description`, `.project-grid-tag`).

Editing

- To change the title, description, or tag for an item, edit the corresponding bullet line in the page's `.qmd` file.
- If you prefer to hand-author the full `::: {.project-grid-card}` blocks, that's still supported; the filter is opt-in.

Notes

- The Lua filter generates the same `:::` block markup as the projects pages so the existing CSS in `_assets/css/custom.css` applies unchanged.
- If you want more structured metadata (author, date), we can extend the syntax and filter to parse extra fields.
