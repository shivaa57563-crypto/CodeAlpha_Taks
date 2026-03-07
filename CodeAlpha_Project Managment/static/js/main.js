/**
 * Project Management Tool - Front-end JavaScript
 * Simple helpers: flash auto-hide, form checks, etc.
 */

(function () {
  'use strict';

  // Auto-hide flash messages after 5 seconds so the page doesn't look cluttered
  var flashEl = document.querySelector('.flash-messages');
  if (flashEl) {
    setTimeout(function () {
      flashEl.style.opacity = '0';
      flashEl.style.transition = 'opacity 0.3s ease';
      setTimeout(function () {
        flashEl.remove();
      }, 300);
    }, 5000);
  }

  // Optional: confirm before leaving a page with unsaved form (can be added per form if needed)
  // Example: window.addEventListener('beforeunload', function(e) { ... });
})();
