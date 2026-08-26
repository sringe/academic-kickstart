// Language toggle backed by the Google Website Translator widget.
//
// Two deliberate choices:
//
// 1. Google's script is loaded ONLY after the visitor asks for a translation.
//    Embedding it on every page would ship third-party JavaScript, and send the
//    page content to Google, for every visitor including those who never use it.
//
// 2. The state lives in Google's own `googtrans` cookie and the page reloads,
//    rather than us driving the widget's internal <select>. The cookie is the
//    documented interface and survives navigation, so the choice sticks as the
//    visitor moves around the site.
//
// The widget is a deprecated Google product: it still serves, but if it ever
// stops, this degrades to a button that does nothing rather than a broken page,
// and browsers' own built-in page translation remains available regardless.

(function () {
  'use strict';

  // Config comes from data attributes on the button, set from the [translate]
  // block in params.toml -- no inline script and no globals. Read inside run(),
  // not at load time, so it does not depend on the bundle executing after the
  // navbar markup.
  var COOKIE = 'googtrans';
  var TARGET = 'ko';
  var SOURCE = 'en';
  var LABEL_TARGET = '한국어';
  var LABEL_ORIGINAL = 'EN';

  function readCookie(name) {
    var m = document.cookie.match('(?:^|; )' + name + '=([^;]*)');
    return m ? decodeURIComponent(m[1]) : '';
  }

  function writeCookie(name, value) {
    // Set on the exact host and, where there is one, the registrable domain, so
    // the widget finds it on both example.com and www.example.com.
    var base = name + '=' + value + '; path=/; SameSite=Lax';
    document.cookie = base;
    var host = location.hostname;
    var parts = host.split('.');
    if (parts.length > 2) {
      document.cookie = base + '; domain=.' + parts.slice(-2).join('.');
    } else if (parts.length === 2) {
      document.cookie = base + '; domain=.' + host;
    }
  }

  function clearCookie(name) {
    var expire = '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
    document.cookie = name + expire;
    var parts = location.hostname.split('.');
    if (parts.length >= 2) {
      document.cookie = name + expire + '; domain=.' + parts.slice(-2).join('.');
    }
  }

  function translated() {
    return readCookie(COOKIE).indexOf('/' + TARGET) > 0;
  }

  function loadWidget() {
    if (document.getElementById('google-translate-script')) return;

    var host = document.createElement('div');
    host.id = 'google_translate_element';
    host.setAttribute('aria-hidden', 'true');
    document.body.appendChild(host);

    window.googleTranslateElementInit = function () {
      try {
        /* global google */
        new google.translate.TranslateElement(
          { pageLanguage: SOURCE, autoDisplay: false },
          'google_translate_element');
      } catch (e) { /* widget withdrawn or blocked */ }
    };

    var s = document.createElement('script');
    s.id = 'google-translate-script';
    s.src = 'https://translate.google.com/translate_a/element.js'
          + '?cb=googleTranslateElementInit';
    s.async = true;
    s.onerror = function () { document.body.classList.remove('is-translating'); };
    document.body.appendChild(s);
  }

  function paint(btn) {
    var on = translated();
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.classList.toggle('is-active', on);
    var label = btn.querySelector('.js-translate-label');
    if (label) {
      label.textContent = on ? LABEL_ORIGINAL : LABEL_TARGET;
    }
    btn.title = on
      ? 'Show the original English'
      : 'Translate this page (Google Translate)';
  }

  function run() {
    var btn = document.querySelector('.js-translate-toggle');
    if (btn && btn.dataset) {
      TARGET = btn.dataset.target || TARGET;
      SOURCE = btn.dataset.source || SOURCE;
      LABEL_TARGET = btn.dataset.labelTarget || LABEL_TARGET;
      LABEL_ORIGINAL = btn.dataset.labelOriginal || LABEL_ORIGINAL;
    }

    // Restore a previous choice on later page loads.
    if (translated()) {
      document.body.classList.add('is-translating');
      loadWidget();
    }
    if (!btn) return;
    paint(btn);

    btn.addEventListener('click', function (e) {
      e.preventDefault();
      if (translated()) {
        clearCookie(COOKIE);
      } else {
        writeCookie(COOKIE, '/' + SOURCE + '/' + TARGET);
      }
      location.reload();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
