// Handle broken links gracefully by detecting 404s and providing visual feedback
(function(){
  'use strict';

  // Check if a link is internal (points to the same domain)
  function isInternalLink(href){
    if(!href) return false;
    // Ignore anchors, mailto, tel
    if(href.indexOf('#') === 0) return false;
    if(href.indexOf('mailto:') === 0) return false;
    if(href.indexOf('tel:') === 0) return false;
    
    // Check if it's a relative URL or same hostname
    try{
      var url = new URL(href, window.location.href);
      return url.hostname === window.location.hostname;
    }catch(e){
      // If it starts with / or doesn't have protocol, treat as internal
      return href.indexOf('/') === 0 || href.indexOf('./') === 0 || href.indexOf('../') === 0;
    }
  }

  // Check if an internal link is broken (404)
  function checkInternalLink(anchor){
    var href = anchor.getAttribute('href');
    if(!href || !isInternalLink(href)) return;

    // Don't check links that have already been checked
    if(anchor.hasAttribute('data-link-checked')) return;
    anchor.setAttribute('data-link-checked', 'true');

    // DISABLED: Automatic link checking causes issues with Quarto preview
    // The fetch requests trigger re-renders which cause temp file conflicts
    // Manual checking can be enabled by uncommenting the code below
    
    /*
    // Use fetch with HEAD to check if the link exists (lighter than GET)
    fetch(href, { method: 'HEAD' })
      .then(function(response){
        if(!response.ok && response.status === 404){
          markAsBroken(anchor, 'internal');
        }
      })
      .catch(function(){
        // Network error or other issue, mark as potentially broken
        markAsBroken(anchor, 'internal-error');
      });
    */
  }

  // Check if an external link is broken
  function checkExternalLink(anchor){
    var href = anchor.getAttribute('href');
    if(!href || isInternalLink(href)) return;

    // Don't check external links automatically (could cause CORS issues)
    // Instead, we'll add error handling when the link is clicked
    anchor.addEventListener('click', function(e){
      // Let the link open normally, but track if it fails
      setTimeout(function(){
        // Check if the window is still focused (link opened successfully)
        // This is a heuristic and not foolproof
      }, 100);
    });
  }

  // Mark a link as broken with visual feedback
  function markAsBroken(anchor, type){
    anchor.classList.add('broken-link');
    anchor.setAttribute('data-link-status', type);
    
    // Add a visual indicator
    var indicator = document.createElement('span');
    indicator.className = 'broken-link-indicator';
    indicator.setAttribute('aria-label', 'This link may be broken');
    indicator.innerHTML = ' <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>';
    
    // Insert after the link text
    if(anchor.nextSibling){
      anchor.parentNode.insertBefore(indicator, anchor.nextSibling);
    }else{
      anchor.parentNode.appendChild(indicator);
    }

    // Add a title tooltip
    var originalTitle = anchor.getAttribute('title') || '';
    var warningMessage = type === 'internal' 
      ? 'Warning: This page may not exist (404)' 
      : 'Warning: This link may be broken';
    anchor.setAttribute('title', originalTitle ? originalTitle + ' - ' + warningMessage : warningMessage);
  }

  // Handle image loading errors
  function handleBrokenImages(){
    var images = document.querySelectorAll('img:not([data-image-checked])');
    images.forEach(function(img){
      img.setAttribute('data-image-checked', 'true');
      
      img.addEventListener('error', function(){
        // Add a class to style broken images
        img.classList.add('broken-image');
        
        // Optionally replace with a placeholder
        var placeholder = document.createElement('div');
        placeholder.className = 'broken-image-placeholder';
        placeholder.innerHTML = '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg><span>Image not found</span>';
        placeholder.style.cssText = 'display:flex;flex-direction:column;align-items:center;justify-content:center;background:#f5f5f5;color:#999;padding:2rem;text-align:center;min-height:200px;border:1px dashed #ccc;';
        
        // Optional: Replace the image with the placeholder
        // Uncomment the next line to enable this behavior
        // img.parentNode.replaceChild(placeholder, img);
      });
    });
  }

  // Main function to check all links on the page
  function checkAllLinks(){
    // Automatic link checking is DISABLED to prevent issues with Quarto preview
    // Only handle broken images
    handleBrokenImages();
  }

  // Run on page load
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', checkAllLinks);
  }else{
    checkAllLinks();
  }
})();
