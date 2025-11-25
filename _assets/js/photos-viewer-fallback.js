// Lightweight fallback for the photo viewer: if the "originals" image fails to load
// (not copied into _site), swap to the thumbnails folder for the same filename.
// This file assumes pages define `slug`, `images` and `currentIndex` (the generator does).
(function(){
  // Feature flag: set `window.enablePhotoThumbnailFallback = true` in a page
  // or global script to allow swapping to thumbnails when originals fail.
  // Default: false (do not swap automatically).
  try{
    if(typeof window !== 'undefined' && typeof window.enablePhotoThumbnailFallback === 'undefined'){
      window.enablePhotoThumbnailFallback = false;
    }
  }catch(e){}

  function trySwapToThumbnail(img){
    try{
      if(!img) return;
      // Prefer to use a filename from the page's images/currentIndex if available (some pages keep those in closure)
      var fname = null;
      try{
        if(typeof currentIndex !== 'undefined' && Array.isArray(images) && images[currentIndex]){
          fname = images[currentIndex].file || null;
        }
      }catch(e){}
      // Fallback: derive filename from src path last segment
      if(!fname){
        try{ var parts = (img.src || '').split('/'); fname = parts[parts.length-1] || null; }catch(e){}
      }
      if(!fname) return;
      // Derive slug from page path if not available as a global variable
      var theSlug = '';
      try{
        if(typeof slug !== 'undefined' && slug) theSlug = slug;
        else {
          var m = window.location.pathname.match(/\/photos\/([^\/]+)/);
          theSlug = (m && m[1]) ? m[1] : '';
        }
      }catch(e){}
      // Build thumbnail path (avoid double slashes)
      var base = '/_assets/images/photos/' + (theSlug ? theSlug + '/' : '');
      var thumb = base + 'thumbnails/' + fname;
      if(img.src !== thumb){
        img.src = thumb;
      }
    }catch(e){ console.error('photos-viewer-fallback error', e); }
  }

  function install(){
    var img = document.getElementById('viewer-image');
    if(!img) return;
    // If the error event fires, attempt swap only when the feature flag is enabled.
    img.addEventListener('error', function(){
      try{
        if(window.enablePhotoThumbnailFallback){
          trySwapToThumbnail(img);
        } else {
          // Leave the src unchanged so the browser can show its broken-image UI or alt text.
          console.warn('photo viewer: original image failed to load and thumbnail fallback is disabled. Image src=', img.src);
        }
      }catch(e){ console.error('photos-viewer-fallback error', e); }
    });
    // Also guard against zero-sized images (sometimes naturalWidth is 0 briefly):
    // if after a short delay image has not loaded, attempt the swap only when enabled.
    img.addEventListener('load', function(){ /* no-op: successful load */ });
    var observer = new MutationObserver(function(){
      try{
        if(window.enablePhotoThumbnailFallback && img && img.src && img.naturalWidth === 0){
          setTimeout(function(){ if(img && img.naturalWidth === 0) trySwapToThumbnail(img); }, 350);
        }
      }catch(e){}
    });
    observer.observe(document.documentElement || document.body, { attributes:false, childList:true, subtree:true });
  }

  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install);
  else install();
})();

// --- Viewer sizing helper: make viewer images larger in layout (1.5x) while
// constraining to the viewport so captions remain visible and flow beneath.
(function(){
  // Viewer scale: 1 means show at natural pixel size; larger than 1 upscales images.
  // Set to 1 to avoid automatic upscaling.
  var SCALE = 1;
  function capWidthByViewport(w){
    try{
      // Mirror the CSS constraints exactly: max-width: calc(98.4vw - 0.96rem)
      // CSS uses 98.4vw (0.984) and subtracts 0.96rem; replicate that here so
      // the JS cap and CSS max-width agree.
      var rem = parseFloat(getComputedStyle(document.documentElement).fontSize) || 16;
      var cap = Math.max(0, Math.round(window.innerWidth * 0.984 - (0.96 * rem)));
      return Math.min(w, cap || w);
    }catch(e){ return w; }
  }

  function sizeViewerImage(img){
    try{
      if(!img) return;
      var natW = img.naturalWidth || img.width || img.clientWidth;
      if(!natW) return;
      var target = Math.round(natW * SCALE);
      var finalW = capWidthByViewport(target);
      // Apply layout width so caption moves beneath the image
  // Apply the computed width while allowing the CSS max-width/max-height
  // rules to still apply if necessary (so the aspect ratio is preserved
  // and the CSS max-height can constrain the image on very tall images).
  img.style.width = finalW + 'px';
  img.style.height = 'auto';
  // Clear any inline max-width so the stylesheet's max-width takes effect.
  img.style.maxWidth = '';
      // Ensure container can size to content
      var c = img.closest('.viewer-image-container');
      if(c) { c.style.width = 'auto'; c.style.height = 'auto'; }
    }catch(e){ console.error('photos-viewer-size error', e); }
  }

  function installSizer(){
    var img = document.getElementById('viewer-image');
    if(!img) return;
    var onLoad = function(){ sizeViewerImage(img); };
    img.addEventListener('load', onLoad);
    // If already loaded, size immediately
    if(img.complete && img.naturalWidth){ sizeViewerImage(img); }
    // Recompute on resize (debounced)
    var to;
    window.addEventListener('resize', function(){ clearTimeout(to); to = setTimeout(function(){ sizeViewerImage(img); }, 120); });
  }

  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', installSizer);
  else installSizer();
})();
