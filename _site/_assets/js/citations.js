// Make citations clickable and scroll to references
(function() {
    'use strict';
    
    function makeCitationsClickable() {
        const citations = document.querySelectorAll('.citation[data-cites]');
        
        citations.forEach(citation => {
            const citeId = citation.getAttribute('data-cites');
            if (!citeId) return;
            
            // Make citation clickable
            citation.style.cursor = 'pointer';
            
            citation.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Try to find the reference by id
                let targetElement = document.getElementById('ref-' + citeId);
                
                // If not found, try without the 'ref-' prefix
                if (!targetElement) {
                    targetElement = document.getElementById(citeId);
                }
                
                // Scroll to the reference
                if (targetElement) {
                    // Update URL hash to trigger :target CSS
                    window.location.hash = targetElement.id;
                    
                    targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            });
        });
        
        console.log('Made ' + citations.length + ' citations clickable');
    }
    
    // Run on DOM load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', makeCitationsClickable);
    } else {
        makeCitationsClickable();
    }
})();
