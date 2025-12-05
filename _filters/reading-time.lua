-- Filter to inject reading-time into the document body after title block
-- This runs after Pandoc processes the document structure

local reading_time_content = nil

function Meta(meta)
  -- Capture reading-time from metadata
  if meta['reading-time'] then
    reading_time_content = pandoc.utils.stringify(meta['reading-time'])
  end
  return meta
end

function Pandoc(doc)
  -- If we have reading time, inject it after the title block (minimal style, no icon)
  if reading_time_content then
    local reading_time_div = pandoc.RawBlock('html', 
      '<div class="quarto-title-meta"><div class="reading-time">' .. reading_time_content .. '</div></div>')
    
    -- Insert at the beginning of the document body (after title block is generated)
    table.insert(doc.blocks, 1, reading_time_div)
  end
  
  return doc
end

return {
  { Meta = Meta },
  { Pandoc = Pandoc }
}
