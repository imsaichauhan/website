// Minimal, collapsible TOC with scroll tracking and dynamic hiding
(function() {
    'use strict';
    
    function initTOC() {
        const toc = document.querySelector('nav#TOC');
        if (!toc) return;
        
        const tocTitle = toc.querySelector('h2#toc-title');
        const tocList = toc.querySelector('ul');
        
        if (!tocTitle || !tocList) return;
        
        // Start collapsed
        let isExpanded = false;
        tocList.style.display = 'none';
        tocList.style.transition = 'none';
        
        // Add minimal +/− indicator
        const indicator = document.createElement('span');
        indicator.className = 'toc-indicator';
        indicator.textContent = '+';
        indicator.style.fontSize = '0.7rem';
        indicator.style.color = '#999';
        indicator.style.marginLeft = '0.35rem';
        indicator.style.fontWeight = '300';
        tocTitle.appendChild(indicator);
        
        // Make title clickable
        tocTitle.style.cursor = 'pointer';
        tocTitle.style.userSelect = 'none';
        
        // Toggle expand/collapse on title click
        tocTitle.addEventListener('click', function(e) {
            e.stopPropagation();
            isExpanded = !isExpanded;
            tocList.style.display = isExpanded ? 'block' : 'none';
            indicator.textContent = isExpanded ? '−' : '+';
        });
        
        // Track current section on scroll
        const sections = Array.from(document.querySelectorAll('h2[id]'));
        const tocLinks = Array.from(toc.querySelectorAll('a'));
        
        function updateActiveSection() {
            // Always update, regardless of expanded state
            let currentSection = null;
            const viewportMiddle = window.innerHeight / 2;
            
            // Check ALL sections and find the LAST one whose top has crossed the viewport middle
            sections.forEach(section => {
                const rect = section.getBoundingClientRect();
                
                // If section heading has crossed the viewport middle (is at or above it)
                if (rect.top <= viewportMiddle) {
                    currentSection = section.getAttribute('id');
                }
            });
            
            // If no section has crossed yet, use the first section
            if (!currentSection && sections.length > 0) {
                currentSection = sections[0].getAttribute('id');
            }
            
            // Update active link styling
            tocLinks.forEach(link => {
                link.classList.remove('active');
                const href = link.getAttribute('href');
                if (href && currentSection && href === '#' + currentSection) {
                    link.classList.add('active');
                }
            });
        }
        
        // Throttled scroll handler for performance
        let scrollTimeout;
        let ticking = false;
        
        window.addEventListener('scroll', function() {
            if (!ticking) {
                window.requestAnimationFrame(function() {
                    updateActiveSection();
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
        
        // Smooth scroll to section with proper positioning
        tocLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    // Position section just below header
                    const headerHeight = 80;
                    const elementPosition = targetElement.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerHeight;
                    
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                    
                    // Update active state immediately
                    setTimeout(updateActiveSection, 100);
                }
            });
        });
        
        // Hide TOC when sidenotes overlap
        function checkCollisions() {
            const sidenotes = document.querySelectorAll('.sidenote');
            if (sidenotes.length === 0) {
                toc.style.opacity = '1';
                toc.style.pointerEvents = 'auto';
                return;
            }
            
            const tocRect = toc.getBoundingClientRect();
            let hasCollision = false;
            
            sidenotes.forEach(sidenote => {
                const sidenoteRect = sidenote.getBoundingClientRect();
                
                // Check vertical overlap with some margin
                const tocTop = tocRect.top - 20;
                const tocBottom = tocRect.bottom + 20;
                const sidenoteTop = sidenoteRect.top;
                const sidenoteBottom = sidenoteRect.bottom;
                
                if (!(sidenoteBottom < tocTop || sidenoteTop > tocBottom)) {
                    hasCollision = true;
                }
            });
            
            // Smoothly fade out/in
            if (hasCollision) {
                toc.style.opacity = '0';
                toc.style.pointerEvents = 'none';
            } else {
                toc.style.opacity = '1';
                toc.style.pointerEvents = 'auto';
            }
        }
        
        // Check for collisions on scroll
        let collisionTimeout;
        window.addEventListener('scroll', function() {
            if (collisionTimeout) {
                clearTimeout(collisionTimeout);
            }
            collisionTimeout = setTimeout(checkCollisions, 50);
        }, { passive: true });
        
        // Initial checks after page load
        setTimeout(function() {
            updateActiveSection();
            checkCollisions();
        }, 100);
        
        // Also update immediately
        updateActiveSection();
        
        // Recheck on window resize
        window.addEventListener('resize', function() {
            setTimeout(checkCollisions, 100);
        });
        
        console.log('TOC initialized: ' + sections.length + ' sections tracked');
    }
    
    // Run on DOM load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTOC);
    } else {
        initTOC();
    }
})();
