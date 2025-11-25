// Make external links open in a new tab and add security rel attributes.
// Runs on DOMContentLoaded so it applies to static and inlined content.
(function(){
  function isExternalLink(href){
    if(!href) return false;
    // Ignore anchors and mailto/tel
    if(href.indexOf('#') === 0) return false;
    if(href.indexOf('mailto:') === 0) return false;
    if(href.indexOf('tel:') === 0) return false;
    // Absolute URLs with protocol
    try{
      var url = new URL(href, window.location.href);
      return url.hostname !== window.location.hostname;
    }catch(e){
      return false;
    }
  }

  function apply(){
    var anchors = document.querySelectorAll('a[href]');
    anchors.forEach(function(a){
      // Do not override explicit target set by author
      if(a.hasAttribute('target')) return;
      var href = a.getAttribute('href');
      if(isExternalLink(href)){
        a.setAttribute('target', '_blank');
        // Add noopener noreferrer for security
        var rel = (a.getAttribute('rel') || '').split(/\s+/).filter(Boolean);
        if(rel.indexOf('noopener') === -1) rel.push('noopener');
        if(rel.indexOf('noreferrer') === -1) rel.push('noreferrer');
        a.setAttribute('rel', rel.join(' '));
      }
    });
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', apply);
  } else {
    apply();
  }
})();
