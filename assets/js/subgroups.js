// Research subgroup cards: expand one at a time.
//
// The detail panels are in the markup and open by default, so a visitor without
// JavaScript sees all of the content rather than three headings that do
// nothing. This collapses them on load and wires up the toggles.

(function () {
  'use strict';

  function run() {
    var wrap = document.querySelector('.js-subgroups');
    if (!wrap) return;

    var cards = Array.prototype.slice.call(
      wrap.querySelectorAll('.subgroup-card'));
    if (!cards.length) return;

    wrap.classList.add('is-enhanced');   // lets CSS collapse the panels

    // The open/closed height is entirely a CSS matter (a 0fr/1fr grid track),
    // so this only has to move a class and keep aria in step.
    function setOpen(card, open) {
      var btn = card.querySelector('.js-subgroup-toggle');
      card.classList.toggle('is-open', open);
      if (btn) btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }

    cards.forEach(function (card) {
      var btn = card.querySelector('.js-subgroup-toggle');
      if (!btn) return;
      setOpen(card, false);
      btn.addEventListener('click', function () {
        var willOpen = !card.classList.contains('is-open');
        cards.forEach(function (c) { setOpen(c, false); });   // one at a time
        if (willOpen) setOpen(card, true);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
