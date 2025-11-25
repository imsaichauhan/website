// Save as: _assets/js/auto-hide-header.js

(function() {
  let lastScrollTop = 0;
  let scrollThreshold = 100; // Minimum scroll before hiding (in pixels)
  let header = null;
  
  function init() {
    // Find the header - adjust selector based on your header structure
    header = document.querySelector('.navbar-container') || 
             document.querySelector('header') || 
             document.querySelector('nav');
    
    if (!header) return;
    
    // Add transition for smooth animation - don't change position/layout
    header.style.transition = 'transform 0.3s ease-in-out';
    
    window.addEventListener('scroll', handleScroll, { passive: true });
  }
  
  function handleScroll() {
    const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
    
    // At the top of page - always show header
    if (currentScroll <= scrollThreshold) {
      header.style.transform = 'translateY(0)';
      lastScrollTop = currentScroll;
      return;
    }
    
    // Scrolling down - hide header
    if (currentScroll > lastScrollTop && currentScroll > scrollThreshold) {
      header.style.transform = 'translateY(-100%)';
    } 
    // Scrolling up - show header
    else if (currentScroll < lastScrollTop) {
      header.style.transform = 'translateY(0)';
    }
    
    lastScrollTop = currentScroll;
  }
  
  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();