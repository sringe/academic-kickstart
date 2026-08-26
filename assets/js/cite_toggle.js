// Cite dialog: switch between BibTeX and the short "Nature-style" citation.
//
// The theme's own handler (assets/js/academic.js) loads cite.bib into the modal
// when a Cite button is clicked. This adds a two-way switch in the modal header:
// the short form comes from the button's data-citation attribute, which the
// template fills from layouts/partials/citation_nature.html, so both places
// agree on the format.
//
// The switch lives in the modal HEADER on purpose: the theme's Copy button
// copies everything inside .modal-body, so putting the switch there would copy
// the button labels along with the citation.

(function () {
  'use strict';

  var modal, codeEl, group, downloadBtn;
  var cache = { bibtex: '', nature: '', filename: '' };
  var mode = 'bibtex';

  function setMode(next) {
    if (!codeEl) return;
    // Remember whatever the theme loaded before we replace it.
    if (mode === 'bibtex' && codeEl.textContent.trim()) {
      cache.bibtex = codeEl.textContent;
    }
    mode = next;

    if (next === 'nature') {
      codeEl.textContent = cache.nature || '';
      codeEl.classList.remove('tex');
      if (downloadBtn) downloadBtn.style.display = 'none';
    } else {
      codeEl.classList.add('tex');
      if (downloadBtn) downloadBtn.style.display = '';
      if (cache.bibtex) {
        codeEl.textContent = cache.bibtex;
      } else if (cache.filename) {
        // Toggled away before the theme's load finished; fetch it ourselves.
        fetch(cache.filename)
          .then(function (r) { return r.ok ? r.text() : ''; })
          .then(function (t) {
            if (!t) return;
            cache.bibtex = t;
            if (mode === 'bibtex') codeEl.textContent = t;
          })
          .catch(function () { /* leave the pane as it is */ });
      }
    }

    Array.prototype.forEach.call(group.querySelectorAll('button'), function (b) {
      var on = b.getAttribute('data-cite-mode') === next;
      b.classList.toggle('active', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  function build() {
    modal = document.getElementById('modal');
    if (!modal) return false;
    codeEl = modal.querySelector('.modal-body code');
    downloadBtn = modal.querySelector('.js-download-cite');
    var header = modal.querySelector('.modal-header');
    if (!codeEl || !header || header.querySelector('.js-cite-format')) return true;

    group = document.createElement('div');
    group.className = 'btn-group btn-group-sm js-cite-format';
    group.setAttribute('role', 'group');
    group.setAttribute('aria-label', 'Citation format');
    [['bibtex', 'BibTeX'], ['nature', 'Citation']].forEach(function (pair) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'btn btn-outline-primary';
      b.setAttribute('data-cite-mode', pair[0]);
      b.textContent = pair[1];
      b.addEventListener('click', function () { setMode(pair[0]); });
      group.appendChild(b);
    });

    // Between the title and the close button.
    var close = header.querySelector('.close');
    if (close) header.insertBefore(group, close);
    else header.appendChild(group);
    return true;
  }

  function run() {
    if (!build()) return;

    Array.prototype.forEach.call(document.querySelectorAll('.js-cite-modal'),
      function (btn) {
        btn.addEventListener('click', function () {
          cache.nature = btn.getAttribute('data-citation') || '';
          cache.filename = btn.getAttribute('data-filename') || '';
          cache.bibtex = '';            // different paper, drop the old text
          mode = 'bibtex';
          // Hide the switch when there is no short citation to switch to.
          group.style.display = cache.nature ? '' : 'none';
          setMode('bibtex');
        });
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
