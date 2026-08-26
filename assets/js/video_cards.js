// Click-to-play video cards (homepage "Simulations" section).
//
// Each card renders only a poster image. The <video> element is created on the
// first click, so a visitor who never plays anything downloads none of the
// clips — they are several MB each, which would otherwise be a rude thing to
// push onto a phone on cellular data.
//
// Only one card plays at a time: starting one pauses the others.

(function () {
  'use strict';

  function build(card, src) {
    var video = document.createElement('video');
    video.className = 'video-card-player';
    video.src = src;
    video.controls = true;
    video.loop = true;
    video.playsInline = true;      // iOS: play inline instead of going fullscreen
    video.preload = 'auto';
    video.setAttribute('webkit-playsinline', '');
    return video;
  }

  function pauseOthers(except) {
    Array.prototype.forEach.call(document.querySelectorAll('.video-card-player'),
      function (v) { if (v !== except && !v.paused) v.pause(); });
  }

  function run() {
    var buttons = document.querySelectorAll('.js-video-play');
    if (!buttons.length) return;

    Array.prototype.forEach.call(buttons, function (btn) {
      btn.addEventListener('click', function () {
        var src = btn.getAttribute('data-video');
        if (!src) return;

        // Already swapped in: just toggle.
        var existing = btn.querySelector('.video-card-player');
        if (existing) {
          if (existing.paused) { pauseOthers(existing); existing.play(); }
          else { existing.pause(); }
          return;
        }

        var video = build(btn, src);
        btn.classList.add('is-playing');
        btn.appendChild(video);
        pauseOthers(video);

        var play = video.play();
        if (play && typeof play.catch === 'function') {
          // Autoplay policies can still refuse; the controls remain usable.
          play.catch(function () {});
        }
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
