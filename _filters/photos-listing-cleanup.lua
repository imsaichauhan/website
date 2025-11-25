-- Pandoc Lua filter: remove Quarto-injected collection meta nodes
-- This filter removes Spans/Divs (and raw HTML) that have classes
-- `collection-meta` or `collection-count-mobile` so the generator's
-- raw HTML is preserved in the final output.

local pandoc = pandoc

local function has_class(classes, name)
  if not classes then return false end
  for _, c in ipairs(classes) do
    if c == name then return true end
  end
  return false
end

function Span(el)
  if el.classes and (has_class(el.classes, 'collection-meta') or has_class(el.classes, 'collection-count-mobile')) then
    return {}
  end
  return nil
end

function Div(el)
  if el.classes and (has_class(el.classes, 'collection-meta') or has_class(el.classes, 'collection-count-mobile')) then
    return {}
  end
  return nil
end

function RawInline(el)
  if el.format == 'html' then
    local t = el.text or ''
    if t:match('collection%-meta') or t:match('collection%-count%-mobile') then
      return {}
    end
  end
  return nil
end

function RawBlock(el)
  if el.format == 'html' then
    local t = el.text or ''
    if t:match('collection%-meta') or t:match('collection%-count%-mobile') then
      return {}
    end
  end
  return nil
end

-- End of filter
