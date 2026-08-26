// Live citation counts.
//
// Publication pages render a count from data/pubmeta.json at build time, which
// goes stale as soon as the site is deployed. This refreshes those numbers in
// the visitor's browser from OpenAlex, so the site never has to be rebuilt to
// stay current.
//
// OpenAlex is used rather than Google Scholar because Scholar sends no CORS
// header and blocks automated traffic, so a browser can never read it. OpenAlex
// allows cross-origin requests and takes up to 50 DOIs per call, so a page of
// 50 publications costs exactly one request. No API key, no rate limit worth
// worrying about (100k/day). scripts/sync_publications.py writes the build-time
// fallback from the same source, so the number never jumps on load.
//
// Deliberately no `mailto` parameter: that would publish an email address in a
// static asset. Only the server-side script identifies itself.

(function () {
  'use strict';

  var API = 'https://api.openalex.org/works';
  var BATCH = 50;                  // OpenAlex OR-filter limit
  var CACHE_KEY = 'ringelab.citations.v1';
  var CACHE_TTL = 6 * 60 * 60 * 1000;   // 6 hours

  function readCache() {
    try {
      var raw = window.localStorage.getItem(CACHE_KEY);
      if (!raw) return null;
      var c = JSON.parse(raw);
      if (!c || typeof c.at !== 'number' || Date.now() - c.at > CACHE_TTL) return null;
      return c.counts || null;
    } catch (e) {
      return null;   // private mode, blocked storage, corrupt value
    }
  }

  function writeCache(counts) {
    try {
      window.localStorage.setItem(CACHE_KEY,
        JSON.stringify({ at: Date.now(), counts: counts }));
    } catch (e) { /* storage unavailable or full; not worth reporting */ }
  }

  function normDoi(doi) {
    return String(doi || '')
      .replace(/^https?:\/\/(dx\.)?doi\.org\//i, '')
      .trim()
      .toLowerCase();
  }

  function paint(nodes, counts) {
    nodes.forEach(function (el) {
      var n = counts[normDoi(el.getAttribute('data-doi'))];
      if (typeof n !== 'number') return;      // unknown DOI: leave the fallback
      var value = el.querySelector('.js-citation-value');
      if (value) value.textContent = String(n);
      if (n > 0) {
        el.removeAttribute('hidden');
      } else {
        el.setAttribute('hidden', '');
      }
    });
  }

  function fetchBatch(dois) {
    var url = API
      + '?filter=doi:' + dois.map(encodeURIComponent).join('|')
      + '&select=doi,cited_by_count&per-page=' + BATCH;
    return fetch(url, { headers: { Accept: 'application/json' } })
      .then(function (r) {
        if (!r.ok) throw new Error('OpenAlex responded ' + r.status);
        return r.json();
      })
      .then(function (data) {
        var out = {};
        (data.results || []).forEach(function (w) {
          out[normDoi(w.doi)] = w.cited_by_count || 0;
        });
        return out;
      });
  }

  function run() {
    var nodes = Array.prototype.slice.call(
      document.querySelectorAll('.js-citation-count[data-doi]'));
    if (!nodes.length || typeof window.fetch !== 'function') return;

    var dois = [];
    nodes.forEach(function (el) {
      var d = normDoi(el.getAttribute('data-doi'));
      if (d && dois.indexOf(d) === -1) dois.push(d);
    });
    if (!dois.length) return;

    var cached = readCache();
    if (cached && dois.every(function (d) { return d in cached; })) {
      paint(nodes, cached);
      return;
    }

    var batches = [];
    for (var i = 0; i < dois.length; i += BATCH) {
      batches.push(fetchBatch(dois.slice(i, i + BATCH)));
    }

    Promise.all(batches).then(function (results) {
      var counts = {};
      results.forEach(function (r) {
        Object.keys(r).forEach(function (k) { counts[k] = r[k]; });
      });
      if (!Object.keys(counts).length) return;
      paint(nodes, counts);
      writeCache(counts);
    }).catch(function () {
      // Offline, blocked, or OpenAlex down: the build-time numbers stand.
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
