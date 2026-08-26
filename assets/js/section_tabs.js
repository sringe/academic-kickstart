// Homepage section tabs.
//
// The homepage used to be one long scroll in which the news list was penned
// into a 280px box with its own scrollbar — a scrolling region inside a
// scrolling page. Instead the blocks marked `data-home-tab="…"` in the widget
// templates become tabs directly under the hero, and one is shown at a time.
//
// Notes:
//  * Several blocks can share a tab name (Welcome owns both the message and the
//    journal covers); they are grouped by name, in first-appearance order.
//  * When a whole <section> belongs to one tab, the section is hidden rather
//    than its inner div, so its padding and background go with it.
//  * The choice is mirrored in the URL fragment, so a tab can be linked to and
//    survives a reload.

(function () {
  'use strict';

  var ATTR = 'data-home-tab';

  function slug(s) {
    return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  }

  function build() {
    var panels = Array.prototype.slice.call(document.querySelectorAll('[' + ATTR + ']'));
    if (panels.length < 2) return null;

    var order = [];
    var groups = {};
    panels.forEach(function (el) {
      var name = el.getAttribute(ATTR);
      if (!name) return;
      if (!groups[name]) { groups[name] = []; order.push(name); }
      groups[name].push(el);
    });
    if (order.length < 2) return null;

    // Decide what to hide for each panel: its section, or just the panel.
    var targets = {};
    order.forEach(function (name) {
      targets[name] = groups[name].map(function (el) {
        var section = el.closest('section.home-section');
        if (!section) return el;
        var inSection = section.querySelectorAll('[' + ATTR + ']');
        var allSame = true;
        Array.prototype.forEach.call(inSection, function (p) {
          if (p.getAttribute(ATTR) !== name) allSame = false;
        });
        return allSame ? section : el;
      });
    });

    return { order: order, targets: targets };
  }

  function run() {
    var model = build();
    if (!model) return;

    var bar = document.createElement('nav');
    bar.className = 'home-tabs';
    bar.setAttribute('aria-label', 'Sections');
    var list = document.createElement('div');
    list.className = 'home-tabs-inner container';
    bar.appendChild(list);

    var buttons = {};
    model.order.forEach(function (name) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'home-tab';
      b.textContent = name;
      b.setAttribute('data-tab', name);
      b.setAttribute('aria-selected', 'false');
      b.addEventListener('click', function () { select(name, true); });
      list.appendChild(b);
      buttons[name] = b;
    });

    function select(name, fromClick) {
      if (!model.targets[name]) return;
      model.order.forEach(function (other) {
        var on = other === name;
        buttons[other].classList.toggle('is-active', on);
        buttons[other].setAttribute('aria-selected', on ? 'true' : 'false');
        model.targets[other].forEach(function (el) {
          el.hidden = !on;
          // `hidden` is easily beaten by a display rule from the theme.
          el.style.display = on ? '' : 'none';
        });
      });
      if (fromClick) {
        if (history.replaceState) {
          history.replaceState(null, '', '#' + slug(name));
        }
        bar.scrollIntoView({ block: 'start', behavior: 'smooth' });
      }
    }

    // Place the bar directly after the hero, else before the first panel.
    var hero = document.querySelector('section.home-section.wg-hero-card');
    var firstSection = model.targets[model.order[0]][0];
    var anchor = hero || (firstSection.closest('section.home-section') || firstSection);
    anchor.parentNode.insertBefore(bar, anchor.nextSibling);

    // Honour a fragment such as #simulations on load.
    var want = model.order[0];
    var frag = (location.hash || '').replace('#', '');
    model.order.forEach(function (n) { if (slug(n) === frag) want = n; });
    select(want, false);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
