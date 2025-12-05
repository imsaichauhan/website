// Move reading time inline with date in title block header
document.addEventListener('DOMContentLoaded', function() {
    const titleBlock = document.getElementById('title-block-header');
    if (!titleBlock) return;
    
    // Find the reading time div that was injected by the Lua filter
    const readingTimeMeta = document.querySelector('.quarto-title-meta');
    const dateElement = titleBlock.querySelector('.date');
    
    if (readingTimeMeta && dateElement) {
        // Get the reading time text
        const readingTimeDiv = readingTimeMeta.querySelector('.reading-time');
        if (readingTimeDiv) {
            const readingTimeText = readingTimeDiv.textContent.trim();
            
            // Create a separator and reading time span
            const separator = document.createElement('span');
            separator.className = 'meta-separator';
            separator.textContent = ' · ';
            
            const readingTimeSpan = document.createElement('span');
            readingTimeSpan.className = 'reading-time-inline';
            readingTimeSpan.textContent = readingTimeText;
            
            // Append to date element (making them inline)
            dateElement.appendChild(separator);
            dateElement.appendChild(readingTimeSpan);
            
            // Remove the original quarto-title-meta div
            readingTimeMeta.remove();
        }
    }
});
