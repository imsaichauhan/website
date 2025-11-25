// Disable figure reference tooltips and style as regular links
(function() {
    'use strict';
    
    function disableFigureTooltips() {
        // Find all figure reference links (links that point to figures)
        const figureRefs = document.querySelectorAll('a[href^="#fig-"]');
        
        figureRefs.forEach(ref => {
            // Disable tippy tooltips on figure references
            if (ref._tippy) {
                ref._tippy.destroy();
            }
        });
        
        // Also disable tooltips globally for figure references if tippy is loaded
        if (window.tippy) {
            window.tippy.setDefaultProps({
                // Disable tooltips for elements matching figure reference selector
                onShow(instance) {
                    if (instance.reference.matches('a[href^="#fig-"]')) {
                        return false;
                    }
                }
            });
        }
        
        console.log('Disabled tooltips for ' + figureRefs.length + ' figure references');
    }
    
    // Run on DOM load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', disableFigureTooltips);
    } else {
        disableFigureTooltips();
    }
    
    // Also run after a slight delay to catch any tooltips initialized later
    setTimeout(disableFigureTooltips, 500);
})();
