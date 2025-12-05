// Convert footnotes to sidenotes/margin notes (Works in Progress style)
(function() {
    'use strict';
    
    console.log('Footnotes script loaded!');
    
    function createSidenotes() {
        console.log('Creating sidenotes...');
        
        // Don't create sidenotes on mobile - let footnotes show at bottom
        const isMobile = window.matchMedia('(max-width: 768px)').matches;
        if (isMobile) {
            console.log('Mobile detected - skipping sidenote creation');
            return;
        }
        
        // Disable Quarto's tippy.js tooltips for footnotes
        if (window.tippy) {
            window.tippy.setDefaultProps({ trigger: 'manual' });
        }
        
        // Get all footnote references
        const footnoteRefs = document.querySelectorAll('a.footnote-ref');
        console.log('Found ' + footnoteRefs.length + ' footnote references');
        
        if (footnoteRefs.length === 0) {
            console.log('No footnote references found');
            return;
        }
        
        // Process each footnote reference
        footnoteRefs.forEach((ref, index) => {
            console.log('Processing footnote ' + (index + 1));
            
            // Disable any tippy instance on this element
            if (ref._tippy) {
                ref._tippy.destroy();
            }
            
            // Remove Quarto's data attributes that trigger tooltips
            ref.removeAttribute('data-tippy-content');
            ref.removeAttribute('title');
            
            // Get the footnote ID (e.g., "fn1")
            const footnoteId = ref.getAttribute('href').substring(1);
            
            // Extract the footnote number from the superscript
            const footnoteNumber = ref.textContent.trim();
            
            // Find the corresponding footnote content
            const footnoteElement = document.getElementById(footnoteId);
            
            if (!footnoteElement) {
                console.log('Footnote element not found for ' + footnoteId);
                return;
            }
            
            // Clone the element to get clean text
            const clone = footnoteElement.cloneNode(true);
            
            // Remove the back reference link
            const backLink = clone.querySelector('.footnote-back');
            if (backLink) {
                backLink.remove();
            }
            
            // Get the footnote text
            const footnoteText = clone.innerHTML.trim();
            
            // Find the paragraph containing this footnote reference
            const paragraph = ref.closest('p');
            if (!paragraph) {
                console.log('No paragraph found for footnote ' + footnoteNumber);
                return;
            }
            
            // Ensure the paragraph has relative positioning
            if (getComputedStyle(paragraph).position === 'static') {
                paragraph.style.position = 'relative';
            }
            
            // Create a sidenote element
            const sidenote = document.createElement('div');
            sidenote.className = 'sidenote';
            sidenote.setAttribute('data-footnote-number', footnoteNumber);
            
            // Structure: horizontal line (::before), then number + content below
            sidenote.innerHTML = `
                <div class="sidenote-content">
                    <span class="sidenote-number">${footnoteNumber}</span>
                    ${footnoteText}
                </div>
            `;
            
            // Calculate the vertical offset of the ref within its paragraph
            const paragraphRect = paragraph.getBoundingClientRect();
            const refRect = ref.getBoundingClientRect();
            const offsetTop = refRect.top - paragraphRect.top;
            
            // Apply styles directly as well as via class (for maximum specificity)
            // On tablet/narrow screens show sidenotes inline, on desktop use margin
            const isTablet = window.matchMedia('(min-width: 769px) and (max-width: 900px)').matches;
            if (isTablet) {
                // Let CSS handle stacking; ensure the element is relative/100% width
                sidenote.style.position = 'relative';
                sidenote.style.left = '0';
                sidenote.style.top = 'auto';
                sidenote.style.width = '100%';
                sidenote.style.display = 'block';
            } else {
                // On wider screens use absolute positioning, but ensure multiple
                // sidenotes in the same paragraph don't overlap by checking
                // existing sidenotes and adjusting the `top` if needed.
                sidenote.style.position = 'absolute';
                sidenote.style.left = 'calc(100% + 2rem)';

                // Default desired top based on the ref offset
                let desiredTop = offsetTop;

                // If there are existing sidenotes in this paragraph, ensure we
                // place the new one below the last one to avoid overlap.
                const existingSidenotes = paragraph.querySelectorAll('.sidenote');
                if (existingSidenotes.length > 0) {
                    const last = existingSidenotes[existingSidenotes.length - 1];
                    // If the last sidenote has an explicit top, compute its bottom
                    const lastTopStr = last.style.top || window.getComputedStyle(last).top;
                    const parsedLastTop = parseFloat(lastTopStr) || 0;
                    const lastHeight = last.getBoundingClientRect().height || 0;
                    const lastBottom = parsedLastTop + lastHeight;
                    // Add a small gap (8px)
                    desiredTop = Math.max(desiredTop, lastBottom + 8);
                }

                sidenote.style.top = desiredTop + 'px';
                sidenote.style.width = '260px';
                sidenote.style.display = 'block';
            }
            
            console.log('Appending sidenote to paragraph at offset ' + offsetTop);
            
            // Append the sidenote to the paragraph
            paragraph.appendChild(sidenote);
        });
        
        console.log('Sidenotes creation complete');
    }
    
    // Run on DOM load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createSidenotes);
    } else {
        createSidenotes();
    }
    
    // Also run after page fully loaded (in case of async scripts)
    window.addEventListener('load', function() {
        // Destroy any tippy tooltips on footnotes that Quarto may have created
        document.querySelectorAll('a.footnote-ref').forEach(ref => {
            if (ref._tippy) {
                ref._tippy.destroy();
            }
        });
    });
})();
