// Opt-in visitor display. Catalog IDs name originals, never seasonal frames or sizes.
(() => {
  if (new URLSearchParams(location.search).get('display') !== 'visitor') return;
  const EXTERIORS = [1, 3, 28, 39, 41, 64];
  const SMALL = [1, 4, 3, 17, 28, 50, 39, 51, 41, 52, 64, 53];
  function nextPhoto(current, pane) {
    const pool = pane === 0 ? EXTERIORS : SMALL;
    const start = pool.indexOf(current[pane]);
    for (let step = 1; step <= pool.length; step++) {
      const id = pool[(start + step) % pool.length];
      if (!current.includes(id)) return id;
    }
  }

  const hero = document.querySelector('.hero-photo');
  const toggle = document.querySelector('#hero-motion');
  if (!hero || !toggle) return;
  hero.querySelector('a').inert = true;
  document.body.classList.add('visitor-requested');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const print = matchMedia('print');
  const connection = navigator.connection;
  const panes = document.createElement('div');
  panes.className = 'visitor-panes';
  let current = [1, 4, 39], pane = 0;
  let ready = false, paused = false, busy = false, away = false, printing = false;
  let timer, generation = 0, seasonalHeld = false;
  const pending = new Set();
  const still = () => reduced.matches || connection?.saveData;
  const available = () => {
    const box = hero.getBoundingClientRect();
    return !away && !printing && !print.matches && !document.hidden
      && !document.querySelector('dialog[open]') && box.bottom > document.querySelector('.masthead').offsetHeight && box.top < innerHeight;
  };
  function controls() {
    if (window.seasonalClock) { window.seasonalClock.refresh(); return; }
    toggle.querySelector('.motion-action').textContent = paused ? 'Resume' : 'Pause';
    toggle.setAttribute('aria-description', 'Exterior and porch photographs. One pane changes every eight seconds.');
    toggle.hidden = Boolean(still() || print.matches || printing || document.querySelector('dialog[open]'));
  }
  function cancel() {
    clearTimeout(timer);
    timer = null;
    generation++;
    for (const abort of pending) abort();
    busy = false;
  }
  function size() {
    const height = ['.masthead', '.listing-summary', '.analytics-notice'].reduce((sum, selector) =>
      sum + (document.querySelector(selector)?.getBoundingClientRect().height || 0), 0);
    hero.style.setProperty('--visitor-chrome', `${height}px`);
  }
  function load(id) {
    // Clone authored metadata, not provenance; generator changes flow through the catalog.
    const source = document.querySelector(`#all-photos #photo-${id}`);
    if (!source) return Promise.reject(new Error('Photo absent from current catalog'));
    const figure = source.cloneNode(true), link = figure.querySelector('a');
    const oldImage = link.querySelector('img'), image = new Image();
    figure.removeAttribute('id');
    figure.querySelector('.photo-number')?.remove();
    const url = link.getAttribute('href');
    const frame = document.createElement('div');
    frame.className = 'visitor-image';
    link.replaceWith(frame);
    image.alt = oldImage.alt;
    image.width = oldImage.width;
    image.height = oldImage.height;
    image.decoding = 'async';
    frame.append(image);
    return new Promise((resolve, reject) => {
      let settled = false;
      const finish = ok => {
        if (settled) return;
        settled = true;
        clearTimeout(timeout);
        pending.delete(abort);
        if (ok) resolve(figure);
        else { image.removeAttribute('src'); reject(new Error('Photo unavailable')); }
      };
      const abort = () => finish(false);
      const timeout = setTimeout(abort, 10000);
      pending.add(abort);
      image.src = url;
      image.decode().then(() => finish(true), abort);
    });
  }
  async function change() {
    timer = null;
    if (!available() || paused || seasonalHeld || (ready && still()) || busy) return;
    busy = true;
    const token = generation;
    const next = ready ? nextPhoto(current, pane) : null;
    try {
      const figures = await Promise.all((ready ? [next] : current).map(load));
      if (token !== generation || !available() || paused || seasonalHeld) return;
      if (ready && window.seasonalClock) {
        const controller = new AbortController(), abort = () => controller.abort();
        pending.add(abort);
        try { await window.seasonalClock.prepare(figures[0], controller.signal); }
        finally { pending.delete(abort); }
        if (token !== generation || !available() || paused || seasonalHeld) return;
      }
      if (!ready) {
        panes.append(...figures);
        hero.append(panes);
        document.body.classList.add('visitor-mode');
        ready = true;
        size();
      } else {
        // Atomic decoded cut: no duplicate identity even across outgoing/incoming pixels.
        panes.children[pane].replaceWith(figures[0]);
        current[pane] = next;
        pane = (pane + 1) % 3;
      }
    } catch {
      if (token === generation) { cancel(); paused = true; }
    } finally {
      if (token === generation) busy = false;
      sync();
    }
  }
  function schedule() {
    if (!available() || paused || seasonalHeld || (ready && still())) { cancel(); return; }
    if (busy || timer) return;
    if (!ready) change();
    else timer = setTimeout(change, 8000);
  }
  function sync() {
    schedule();
    controls();
  }
  // Seasonal runtime owns the dial; this adapter shares pause/lifecycle without a second seasonal clock.
  window.visitorDisplay = {
    get paused() { return paused; },
    get ready() { return ready; },
    get active() { return !away && !printing && !still(); },
    resume() { paused = false; },
    hold(value) { seasonalHeld = value; schedule(); },
  };
  toggle.addEventListener('click', () => {
    if (window.seasonalClock) return;
    paused = !paused; sync();
  });
  hero.addEventListener('focusin', () => { paused = true; sync(); });
  document.addEventListener('visibilitychange', sync);
  new MutationObserver(sync).observe(document.body, {subtree: true, attributes: true, attributeFilter: ['open']});
  const observer = new ResizeObserver(() => { size(); sync(); });
  for (const selector of ['.masthead', '.listing-summary', '.analytics-notice']) {
    const element = document.querySelector(selector);
    if (element) observer.observe(element);
  }
  addEventListener('scroll', sync, {passive: true});
  addEventListener('resize', () => { size(); sync(); });
  addEventListener('pagehide', () => { away = true; sync(); });
  addEventListener('pageshow', () => { away = false; sync(); });
  addEventListener('beforeprint', () => { printing = true; sync(); });
  addEventListener('afterprint', () => { printing = false; sync(); });
  reduced.addEventListener('change', sync);
  print.addEventListener('change', sync);
  connection?.addEventListener?.('change', sync);
  sync();
})();
