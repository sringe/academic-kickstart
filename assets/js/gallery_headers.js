// Gallery album headings: split "8/2026: Group picture" into a date chip and a
// title, so the month reads as a label rather than as part of the sentence.
//
// Done in JavaScript because the headings are hand-written in
// content/gallery/gallery.md as plain "<h2 class="headline"><span>…</span></h2>"
// and CSS cannot address part of a text node. Without JS the heading still
// renders correctly, just as one run of text.

(function () {
  'use strict';

  // "8/2026: …", "10/2025: …" — a month/year prefix followed by a colon.
  var DATE_PREFIX = /^\s*(\d{1,2}\s*\/\s*\d{4})\s*:\s*([\s\S]+)$/;

  function run() {
    var spans = document.querySelectorAll('h2.headline > span');
    Array.prototype.forEach.call(spans, function (span) {
      // Only touch plain-text headings; leave anything with markup alone.
      if (span.children.length) return;

      var m = DATE_PREFIX.exec(span.textContent);
      if (!m) return;

      var chip = document.createElement('span');
      chip.className = 'headline-date';
      chip.textContent = m[1].replace(/\s+/g, '');

      var title = document.createElement('span');
      title.className = 'headline-text';
      title.textContent = m[2].trim();

      span.textContent = '';
      span.appendChild(chip);
      span.appendChild(title);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
