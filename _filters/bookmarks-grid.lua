-- bookmarks-grid.lua
-- Pandoc Lua filter: convert a simple BulletList into a projects-style grid
-- Trigger: document metadata key `bookmarks_grid: true`
-- Input list format (Markdown bullet list):
-- - [Title](url) — Description — Tag
-- Tag is optional. Em dash (—) separates description and tag; a simple hyphen or ` - ` also accepted.
-- The filter will replace the BulletList with a Div having class "projects-grid" and each list item
-- becomes a Div with classes matching the project's grid card structure.

-- We'll implement a Pandoc(doc) handler instead of Meta/BulletList
-- so we can reliably check document metadata and transform lists.

-- helper to split by em dash or triple-dash fallbacks
local function split_item(text)
  -- trim
  text = text:gsub('^%s+', ''):gsub('%s+$', '')
  -- prefer em-dash
  local parts = {}
  local em = utf8 and '—' or '\226\128\147'
  if text:find('—') then
    for part in text:gmatch('[^—]+') do
      table.insert(parts, (part:gsub('^%s+', ''):gsub('%s+$', '')))
    end
  else
    -- fallback split on ' - ' or ' -- ' or ' — '
    local s = text
    local found = false
    for sep in {' %-%- ', ' %-%s', ' %-%s ', ' %s%- ', ' %-%s '} do end
    -- split on ' — ', ' - ', ' -- '
    if s:find(' %-%- ') then
      for part in s:gmatch('[^%-%-]+') do table.insert(parts, (part:gsub('^%s+', ''):gsub('%s+$', ''))) end
    elseif s:find(' %- ') then
      for part in s:gmatch('[^%-]+') do table.insert(parts, (part:gsub('^%s+', ''):gsub('%s+$', ''))) end
    else
      parts = {s}
    end
  end
  return parts
end

-- Convert an inline link to text and url
local function link_to_text_url(inlines)
  -- inlines is a list of inline elements; we expect a single Link or simple text
  for i, el in ipairs(inlines) do
    if el.t == 'Link' then
      local title = pandoc.utils.stringify(el.c[2])
      local url = el.c[1].target or pandoc.utils.stringify(el.c[1])
      return title, url
    end
  end
  -- fallback: stringify whole inlines
  return pandoc.utils.stringify(inlines), ''
end

-- We won't use a BulletList handler (ordering issues). Instead transform in Pandoc(doc).

function Pandoc(doc)
  local m = doc.meta
  if not (m.bookmarks_grid ~= nil and tostring(m.bookmarks_grid) ~= 'false') then
    return doc
  end

  local new_blocks = {}
  for _, blk in ipairs(doc.blocks) do
    if blk.t == 'BulletList' then
      local cards = {}
      for i, item in ipairs(blk.content) do
        -- Prefer parsing the AST inlines so we preserve links and unicode
        local first_block = item[1]
        local inlines = {}
        if first_block and (first_block.t == 'Para' or first_block.t == 'Plain') then
          inlines = first_block.content
        else
          -- fallback to stringified parsing
    local text = pandoc.utils.stringify(item)
          inlines = { pandoc.Str(text) }
        end

        -- find positions of em-dash separators (common separator used in the list format)
        local sep_idxs = {}
        for j, inl in ipairs(inlines) do
          if inl.t == 'Str' then
            local s = inl.text
            -- Accept em-dash, en-dash, hyphen, or pipe as separators.
            -- Using a pipe (`|`) is convenient to type and unlikely to appear in descriptions.
            if s == '—' or s == '–' or s == '-' or s:find('|') then
              table.insert(sep_idxs, j)
            end
          end
        end

        -- Helper to slice inlines
        local function slice(tbl, a, b)
          local out = {}
          for k = a, b do
            if tbl[k] then table.insert(out, tbl[k]) end
          end
          return out
        end

        local title_inlines = {}
        local desc_inlines = {}
        local tag_inlines = {}
        local url = ''

        if #inlines > 0 and inlines[1].t == 'Link' then
          -- item begins with a Link inline
          local link = inlines[1]
          title_inlines = link.content
          if link.target then url = link.target end
          if #sep_idxs >= 1 then
            -- description starts after first sep; use LAST separator as desc/tag split
            local sep1 = sep_idxs[1]
            local sep2 = sep_idxs[#sep_idxs]
            if sep2 and sep2 > sep1 then
              desc_inlines = slice(inlines, sep1+1, sep2-1)
              tag_inlines = slice(inlines, sep2+1, #inlines)
            else
              desc_inlines = slice(inlines, sep1+1, #inlines)
            end
          else
            -- no separators; remaining inlines after link are the description
            desc_inlines = slice(inlines, 2, #inlines)
          end
        else
          -- item does not start with a Link; accumulate title until first separator
          if #sep_idxs >= 1 then
            local sep1 = sep_idxs[1]
            local sep2 = sep_idxs[#sep_idxs]
            title_inlines = slice(inlines, 1, sep1-1)
            if sep2 and sep2 > sep1 then
              desc_inlines = slice(inlines, sep1+1, sep2-1)
              tag_inlines = slice(inlines, sep2+1, #inlines)
            else
              desc_inlines = slice(inlines, sep1+1, #inlines)
            end
          else
            -- nothing to split; all inlines are title/description
            title_inlines = inlines
          end
        end

        local title = pandoc.utils.stringify(title_inlines)
        local desc = pandoc.utils.stringify(desc_inlines)
        local tag = pandoc.utils.stringify(tag_inlines)

        local title_inlines = {}
        if url and url ~= '' then
          table.insert(title_inlines, pandoc.Link(pandoc.Inlines{pandoc.Str(title)}, url))
        else
          table.insert(title_inlines, pandoc.Str(title))
        end
        local title_para = pandoc.Para(title_inlines)
        local title_div = pandoc.Div({title_para}, pandoc.Attr('', {'project-grid-title'}, {}))

        local sep_div = pandoc.Div({}, pandoc.Attr('', {'project-grid-separator'}, {}))
        local desc_div = pandoc.Div({pandoc.Para({pandoc.Str(desc)})}, pandoc.Attr('', {'project-grid-description'}, {}))

        local tag_divs = {}
        if tag ~= '' then
          local sep2 = pandoc.Div({}, pandoc.Attr('', {'project-grid-separator'}, {}))
          local tag_div = pandoc.Div({pandoc.Para({pandoc.Str(tag)})}, pandoc.Attr('', {'project-grid-tag'}, {}))
          table.insert(tag_divs, sep2)
          table.insert(tag_divs, tag_div)
        end

        local children = {title_div, sep_div, desc_div}
        for _, v in ipairs(tag_divs) do table.insert(children, v) end

        local card_div = pandoc.Div(children, pandoc.Attr('', {'project-grid-card'}, {}))
        table.insert(cards, card_div)
      end

  -- mark this Div with both the projects-grid class (for existing styling)
  -- and a bookmarks-grid class so we can target bookmark indexes separately in CSS
  -- Insert a small page-scoped style so the title block width matches the bookmarks grid.
  -- This style is emitted only on pages that use the bookmarks_grid filter.
  local css = [[
<style>
/* Constrain the title block on bookmark index pages to match the bookmarks grid width */
body:not(.homepage) #title-block-header {
  max-width: 880px;
  margin-left: auto;
  margin-right: auto;
}
</style>
]]
  table.insert(new_blocks, pandoc.RawBlock('html', css))
  table.insert(new_blocks, pandoc.Div(cards, pandoc.Attr('', {'projects-grid','bookmarks-grid'}, {})))
    else
      table.insert(new_blocks, blk)
    end
  end

  doc.blocks = new_blocks
  return doc
end
