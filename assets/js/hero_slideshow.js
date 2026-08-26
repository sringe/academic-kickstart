// Hero side panel: crossfade between the research images.
//
// The markup ships every slide stacked in the panel with the first marked
// active, so with JavaScript off (or before this runs) the panel still shows a
// picture rather than an empty frame.
//
// Pauses while the tab is hidden, on hover, and entirely for visitors who have
// asked for reduced motion — for whom a picture that changes by itself is
// exactly the thing they turned off.

(function () {
  'use strict';

  function setup(panel) {
    var slides = panel.querySelectorAll('.hero-slide');
    var dots = panel.querySelectorAll('.hero-slide-dot');
    if (slides.length < 2) return;

    var interval = parseInt(panel.getAttribute('data-interval'), 10) || 6000;
    var index = 0;
    var timer = null;
    var paused = false;

    function show(next) {
      index = (next + slides.length) % slides.length;
      Array.prototype.forEach.call(slides, function (s, i) {
        var on = i === index;
        s.classList.toggle('is-active', on);
        if (on) { s.removeAttribute('aria-hidden'); }
        else { s.setAttribute('aria-hidden', 'true'); }
      });
      Array.prototype.forEach.call(dots, function (d, i) {
        d.classList.toggle('is-active', i === index);
        d.setAttribute('aria-selected', i === index ? 'true' : 'false');
      });
    }

    function tick() {
      if (!paused && !document.hidden) show(index + 1);
    }

    function start() {
      if (timer === null) timer = window.setInterval(tick, interval);
    }

    function stop() {
      if (timer !== null) { window.clearInterval(timer); timer = null; }
    }

    Array.prototype.forEach.call(dots, function (d, i) {
      d.addEventListener('click', function () {
        show(i);
        stop(); start();          // restart the clock from this slide
      });
    });

    panel.addEventListener('mouseenter', function () { paused = true; });
    panel.addEventListener('mouseleave', function () { paused = false; });
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) stop(); else start();
    });

    start();
  }

  function run() {
    var reduce = window.matchMedia
      && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) return;
    Array.prototype.forEach.call(
      document.querySelectorAll('.js-hero-slideshow'), setup);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
