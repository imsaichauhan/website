// Dark mode toggle implementation
// Manages theme switching with localStorage persistence and system preference detection

(function() {
  'use strict';

  const STORAGE_KEY = 'theme-preference';
  const THEME_LIGHT = 'light';
  const THEME_DARK = 'dark';

  // Get system preference (currently disabled - defaulting to light mode)
  function getSystemPreference() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return THEME_DARK;
    }
    return THEME_LIGHT;
  }

  // Get saved preference or default to light mode
  function getThemePreference() {
    const saved = localStorage.getItem(STORAGE_KEY);
    // Default to light mode for first-time visitors (dark mode not production-ready yet)
    return saved || THEME_LIGHT;
  }

  // Apply theme to document
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    updateToggleButton(theme);
  }

  // Update toggle button text to show current mode
  function updateToggleButton(theme) {
    // Update all toggle buttons on the page
    const toggles = document.querySelectorAll('.dark-mode-toggle');
    
    toggles.forEach(toggle => {
      const lightSpan = toggle.querySelector('.mode-light');
      const darkSpan = toggle.querySelector('.mode-dark');
      
      if (!lightSpan || !darkSpan) return;
      
      // Check if this is the experimental toggle (has different text format)
      const isExperimentalToggle = toggle.classList.contains('experimental-toggle');

      if (isExperimentalToggle) {
        // For Colophon page experimental toggle - don't change text, let CSS handle visibility
        // The HTML has the correct text in each span, CSS shows/hides based on theme
        return;
      } else {
        // For footer toggle (if it exists) - use compact format
        if (theme === THEME_DARK) {
          lightSpan.textContent = 'Light';
          darkSpan.textContent = '[Dark]';
        } else {
          lightSpan.textContent = '[Light]';
          darkSpan.textContent = 'Dark';
        }
      }
    });
  }

  // Toggle theme
  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || THEME_LIGHT;
    const newTheme = currentTheme === THEME_LIGHT ? THEME_DARK : THEME_LIGHT;
    
    localStorage.setItem(STORAGE_KEY, newTheme);
    applyTheme(newTheme);
  }

  // Initialize theme immediately (before page renders)
  const initialTheme = getThemePreference();
  applyTheme(initialTheme);

  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initToggle);
  } else {
    initToggle();
  }

  function initToggle() {
    // Select all dark mode toggle buttons (handles multiple buttons on same page)
    const toggles = document.querySelectorAll('.dark-mode-toggle');
    toggles.forEach(toggle => {
      toggle.addEventListener('click', toggleTheme);
    });

    // Make sure any toggles that were not present when the script first applied
    // the theme are updated now that the DOM is ready. Without this, pages
    // that include the script in the head (before the footer) will show the
    // wrong toggle text until the user interacts.
    updateToggleButton(document.documentElement.getAttribute('data-theme') || THEME_LIGHT);

    // Observe dynamic DOM changes and update any toggles that are added later.
    // This covers client-side navigation (Quarto's SPA-style page swaps)
    // where new content (including the home toggle) may be injected without
    // firing a full page load event.
    try {
      const observer = new MutationObserver((mutations) => {
        let addedToggle = false;
        for (const m of mutations) {
          for (const node of m.addedNodes) {
            if (node.nodeType !== 1) continue;
            if (node.matches && node.matches('.dark-mode-toggle')) {
              addedToggle = true;
              break;
            }
            if (node.querySelector && node.querySelector('.dark-mode-toggle')) {
              addedToggle = true;
              break;
            }
          }
          if (addedToggle) break;
        }
        if (addedToggle) {
          updateToggleButton(document.documentElement.getAttribute('data-theme') || THEME_LIGHT);
          // Re-wire click handlers for any new toggles
          const newToggles = document.querySelectorAll('.dark-mode-toggle');
          newToggles.forEach(t => {
            if (!t._darkModeBound) {
              t.addEventListener('click', toggleTheme);
              t._darkModeBound = true;
            }
          });
        }
      });

      observer.observe(document.documentElement || document.body, { childList: true, subtree: true });
    } catch (e) {
      // If MutationObserver isn't available for some reason, it's non-fatal.
      // The initial DOMContentLoaded update still covers standard page loads.
    }

    // Listen for system preference changes (currently disabled)
    // Since dark mode is not production-ready, we don't auto-switch based on system preferences
    /*
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        // Only apply system preference if user hasn't manually set a preference
        if (!localStorage.getItem(STORAGE_KEY)) {
          applyTheme(e.matches ? THEME_DARK : THEME_LIGHT);
        }
      });
    }
    */
  }
})();
