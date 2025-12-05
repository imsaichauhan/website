// nav-expand.js
// Navigation expand/collapse toggle for homepage

(function() {
  // Only run on homepage
  if (!document.body.classList.contains('home')) {
    return;
  }

  const navToggle = document.getElementById('nav-expand-toggle');
  const homeNavGrid = document.querySelector('.home-nav-grid');
  const toggleCollapsed = navToggle?.querySelector('.toggle-collapsed');
  const toggleExpanded = navToggle?.querySelector('.toggle-expanded');

  if (!navToggle || !homeNavGrid) {
    return;
  }

  // Check saved state in localStorage
  const savedNavState = localStorage.getItem('navExpanded');
  if (savedNavState === 'true') {
    expandNav();
  }

  // Toggle on click
  navToggle.addEventListener('click', () => {
    if (homeNavGrid.classList.contains('nav-expanded')) {
      collapseNav();
    } else {
      expandNav();
    }
  });

  function expandNav() {
    homeNavGrid.classList.add('nav-expanded');
    navToggle.classList.add('is-expanded');
    
    navToggle.setAttribute('aria-expanded', 'true');
    navToggle.setAttribute('title', 'Hide all pages');
    localStorage.setItem('navExpanded', 'true');
  }

  function collapseNav() {
    homeNavGrid.classList.remove('nav-expanded');
    navToggle.classList.remove('is-expanded');
    
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('title', 'Show all pages');
    localStorage.setItem('navExpanded', 'false');
  }
})();
