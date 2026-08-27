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

    // A section holding panels for two different tabs (the pages widget owns
    // both Welcome and News) is never hidden itself -- only the panels inside
    // it are -- so when neither is on, its own padding is left behind as an
    // empty 42px strip under the tab bar. Collect those shells so select() can
    // collapse them. Sections that are targets in their own right are left
    // out: they are already shown and hidden directly.
    var shells = [];
    order.forEach(function (name) {
      targets[name].forEach(function (el) {
        if (el.tagName === 'SECTION') return;
        var sec = el.closest('section.home-section');
        if (sec && shells.indexOf(sec) === -1) shells.push(sec);
      });
    });

    return { order: order, targets: targets, shells: shells };
  }

  function run() {
    var model = build();
    if (!model) return;

    // Lets the stylesheet drop the now-duplicated panel headings, tighten the
    // spacing and enable scroll snapping -- but only when the tabs exist. The
    // class goes on <html> too because scroll-snap-type has to sit on the
    // scrolling element itself.
    document.body.classList.add('has-home-tabs');
    document.documentElement.classList.add('has-home-tabs');

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

    // A lazily-loaded image inside a display:none panel is never fetched, and
    // stays unfetched when the panel is shown. Nudge them when a panel opens.
    function wake(el) {
      var imgs = el.querySelectorAll('img[loading="lazy"]');
      Array.prototype.forEach.call(imgs, function (img) {
        img.setAttribute('loading', 'eager');
        if (!img.complete || img.naturalWidth === 0) {
          var src = img.getAttribute('src');
          if (src) img.setAttribute('src', src);
        }
      });
    }

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
          if (on) wake(el);
        });
      });
      model.shells.forEach(function (sec) {
        var on = false;
        Array.prototype.forEach.call(sec.querySelectorAll('[' + ATTR + ']'), function (p) {
          if (p.style.display !== 'none') on = true;
        });
        sec.hidden = !on;
        sec.style.display = on ? '' : 'none';
      });

      if (fromClick) {
        if (history.replaceState) {
          history.replaceState(null, '', '#' + slug(name));
        }
        bar.scrollIntoView({ block: 'start', behavior: 'smooth' });
      }
    }

    // The bar goes above the first panel -- i.e. directly under the navbar --
    // so it is on screen whatever is open. It used to sit under the hero, but
    // once a panel opened the hero was above the bar and out of reach: the
    // panel is a scroll container with `overscroll-behavior: contain`, so
    // scrolling up in it does not chain to the page. The hero is now a panel
    // of its own instead (data-home-tab="Group" in the hero_card widget).
    var firstSection = model.targets[model.order[0]][0];
    var anchor = firstSection.closest('section.home-section') || firstSection;
    anchor.parentNode.insertBefore(bar, anchor);

    // Publish the height of the fixed navbar plus the tab bar, so the panel
    // below can be told to fill exactly the rest of the window and the snap
    // points can clear the navbar. Measured rather than hard-coded: both change
    // between breakpoints.
    function measure() {
      var nav = document.querySelector('#navbar-main');
      var navH = nav ? Math.round(nav.getBoundingClientRect().height) : 0;
      var barH = Math.round(bar.getBoundingClientRect().height);
      var root = document.documentElement.style;
      root.setProperty('--navbar-h', navH + 'px');
      root.setProperty('--home-tabs-offset', (navH + barH) + 'px');
    }
    measure();
    window.addEventListener('resize', measure);

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
