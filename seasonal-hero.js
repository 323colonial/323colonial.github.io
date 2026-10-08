// One shared seasonal clock for the hero and the scroll-sequenced narrative photos.
// Each original <img> stays first in its link and is never altered. Seasonal frames
// sit in a two-layer stack above it, so every fallback is "remove the stack".
(() => {
  const manifestUrl = document.currentScript?.dataset.manifest;
  const toggle = document.querySelector('#hero-motion');
  if (!manifestUrl || !toggle || !Element.prototype.animate || navigator.connection?.saveData) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const print = matchMedia('print');
  const narrow = matchMedia('(max-width: 800px)');
  const STORE = 'colonial_seasons_paused';
  const DESCRIPTION = 'Animated seasonal concept. Opens the original property photograph.';
  const RETRIES = 2;

  let M, KN, DUR, N, S, base, HOLD, FADE;
  let photos = [];                 // seasonal photos in page order
  let seg = 0, offset = 0;         // logical clock: timing-table segment and ms into it
  let startedAt = null;            // document.timeline time the segment began; null while frozen
  let timer = 0, carry = null;
  let paused = false, stalled = false, shown = false, begun = false;
  let holdSince = null, holdTimer = 0;
  let direction = 1, lastY = scrollY, rate = 0, inflight = 0;
  try { paused = sessionStorage.getItem(STORE) === '1'; } catch { /* Storage denied: start playing. */ }

  const now = () => document.timeline.currentTime ?? performance.now();
  const dialogOpen = () => Boolean(document.querySelector('dialog[open]'));
  const still = () => reduced.matches || print.matches;
  const have = (p, keys) => keys.every(key => p.frames.get(key)?.state === 'ready');
  const participating = p => p.near && !p.figure.hidden && p.original.complete && p.original.naturalWidth > 0
    && (p.hero || Boolean(p.figure.closest('.story.is-scrolling')));

  // The dissolve a photo is in during timing segment i, and its upper-layer opacity at
  // each end. Phase is linear in time inside a segment, so sparse photos stay exact.
  function pair(p, i) {
    const keys = p.keys, at = KN[i];
    if (keys.length === 1) return {a: keys[0], b: keys[0], from: 1, to: 1};
    let n = keys.length - 1;
    while (n > 0 && keys[n] > at) n--;
    if (keys[n] > at) n = keys.length - 1; // Before its first key a photo is still in the wrap.
    const a = keys[n], b = keys[(n + 1) % keys.length], span = ((b - a + N) % N) || N;
    const from = 1 - ((at - a + N) % N) / span;
    return {a, b, from, to: Math.max(0, from - (KN[i + 1] - at) / span)};
  }
  // Frozen exactly on one of its keys, a photo needs that single frame.
  function needs(p, i, ms, running) {
    const {a, b, from} = pair(p, i);
    return a !== b && (running || ms > 0 || from < 1) ? [a, b] : [a];
  }
  function elapsed() {
    return startedAt == null ? offset : Math.min(DUR[seg], Math.max(0, now() - startedAt));
  }
  const phase = () => KN[seg] + (KN[seg + 1] - KN[seg]) * elapsed() / DUR[seg];

  // --- Frames -------------------------------------------------------------------
  // Slow links get the small tier and a smaller window; see reach().
  function small(p) {
    return M.tiers.includes('small') && (narrow.matches || (rate > 0 && rate < 1.5) || /-small\.webp$/.test(p.original.currentSrc));
  }
  function source(p, key) {
    if (p.own.has(key)) {
      // Keys served by the untouched original reuse its own derivatives.
      const set = (p.original.getAttribute('srcset') || p.original.getAttribute('src')).split(',').map(c => c.trim().split(/\s+/)[0]);
      return new URL(small(p) ? set[0] : set.at(-1), document.baseURI).href;
    }
    const name = String(Math.floor(key)).padStart(2, '0') + (key % 1 ? 'h' : '');
    return `${base}${String(p.position).padStart(2, '0')}/${name}${small(p) ? '-small' : ''}.webp`;
  }
  function measure(url) {
    const t = performance.getEntriesByName(url).pop();
    // Cache hits report no transfer and say nothing about the link.
    // Small bodies arrive in one burst and measure latency, not throughput.
    if (!t?.transferSize || t.encodedBodySize < 10000) return;
    const sample = t.encodedBodySize * 8 / Math.max(1, t.responseEnd - t.responseStart) / 1000; // Mbps
    rate = rate ? rate * .7 + sample * .3 : sample;
  }
  // How far the fetch window blooms past what the barrier needs: 0 stops prefetching.
  const reach = () => !rate ? 1 : rate < .5 ? 0 : rate < 4 ? 1 : 2;
  const limit = () => rate && rate < 1.5 ? 2 : rate >= 4 ? 4 : 3;

  function load(p, f, keep) {
    f.keep = keep;
    if (f.state === 'ready' || f.state === 'loading' || (f.state === 'cached' && !keep)) return;
    if (f.state === 'error' && (f.tries > RETRIES || performance.now() < f.retryAt)) return;
    if (inflight >= limit()) return;
    const img = new Image(), url = source(p, f.key);
    img.alt = '';
    img.decoding = 'async';
    f.state = 'loading'; f.img = img;
    inflight++;
    img.src = url;
    img.decode().then(() => true, () => false).then(ok => {
      if (f.img !== img) return; // Abandoned: a late arrival must not attach.
      inflight--;
      measure(url);
      if (ok) {
        f.tries = 0;
        // Frames outside a photo's three-frame window only warm the HTTP cache.
        if (f.keep) f.state = 'ready'; else { f.state = 'cached'; f.img = null; }
      } else {
        const wait = HOLD * (f.tries ? .3 : .1);
        f.state = 'error'; f.img = null; f.tries++;
        f.retryAt = performance.now() + wait;
        setTimeout(sync, wait + 10);
      }
      sync();
    });
  }

  // Priority blooms outward on two axes, time first: what the clock reaches next for
  // visible photos, then for the nearest photo in the scroll direction, then the
  // following segment, then photos further away. Never a whole year for its own sake.
  function schedule() {
    // Nothing new is requested while the tab is hidden, printing or under a dialog.
    if (document.hidden || dialogOpen() || still()) return;
    const live = photos.filter(participating), wanted = new Map(), order = [];
    const frozen = paused || stalled;
    const want = (p, keys, keep) => keys.forEach(key => {
      let f = p.frames.get(key);
      if (!f) p.frames.set(key, f = {key, state: 'idle', img: null, tries: 0});
      if (!wanted.has(f)) order.push([p, f]);
      wanted.set(f, wanted.get(f) || keep);
    });
    const at = (p, s) => frozen ? needs(p, seg, offset, false)
      : s === 0 ? [...needs(p, (seg + 1) % S, 0, true), ...needs(p, seg, offset, true)]
      : needs(p, (seg + 1 + s) % S, 0, true);
    if (live.length) {
      const index = live.map(p => photos.indexOf(p));
      const edge = direction > 0 ? Math.max(...index) : Math.min(...index);
      const eligible = p => p && (p.hero || p.figure.closest('.story.is-scrolling'));
      const far = reach();
      for (let ring = 0; ring <= far; ring++) {
        for (let s = 0; s <= (frozen ? 0 : ring); s++) for (let d = 0; d <= ring; d++) {
          if (Math.max(s, d) !== ring) continue;
          const targets = d === 0 ? live : [photos[edge + direction * d]].filter(eligible);
          // Decoded frames stay bounded: the current pair plus the next key, per photo.
          targets.forEach(p => want(p, at(p, s), s === 0 && d <= 1));
        }
      }
    }
    for (const p of photos) for (const f of p.frames.values()) {
      if (wanted.get(f) || f.img?.isConnected) continue;
      if (f.state === 'loading' && !wanted.has(f)) { inflight--; f.img.src = ''; f.img = null; f.state = 'idle'; }
      else if (f.state === 'ready') { f.img = null; f.state = 'cached'; }
    }
    order.forEach(([p, f]) => load(p, f, wanted.get(f)));
  }

  // --- Rendering ----------------------------------------------------------------
  // Lower layer is the next key at full opacity; the upper is the current key fading
  // out. Source-over on an opaque layer is the exact linear dissolve, with full coverage.
  function paint(p) {
    const {a, b, from, to} = pair(p, seg);
    const upper = p.frames.get(a).img, next = p.frames.get(b);
    const lower = a !== b && next?.state === 'ready' ? next.img : null;
    // A new frame only ever enters beneath an opaque one, so a late paint cannot blank.
    // The spent upper layer goes first so the frame on screen is never moved.
    [...p.stack.children].forEach(layer => {
      layer.getAnimations().forEach(animation => animation.cancel());
      layer.style.removeProperty('opacity');
      if (layer !== lower && layer !== upper) layer.remove();
    });
    if (lower && lower.parentNode !== p.stack) p.stack.prepend(lower);
    if (p.stack.lastElementChild !== upper) p.stack.append(upper);
    if (a === b) return;
    if (startedAt == null) { upper.style.opacity = from + (to - from) * offset / DUR[seg]; return; }
    // Sync comes from every photo sharing this one start time, not from correcting drift.
    upper.animate({opacity: [from, to]}, {duration: DUR[seg], fill: 'both'}).startTime = startedAt;
  }
  function seen(p) {
    const box = p.link.getBoundingClientRect();
    return box.bottom > 0 && box.top < innerHeight && parseFloat(p.figure.style.getPropertyValue('--photo-opacity') || 1) > .05;
  }
  function show(p) {
    if (!p.stack) {
      p.stack = document.createElement('span');
      p.stack.className = 'season-stack';
      p.link.append(p.stack);
      p.link.setAttribute('aria-description', DESCRIPTION);
      // Photos already on screen fade in above their original; others join unseen.
      if (seen(p)) p.stack.animate({opacity: [0, 1]}, FADE);
      shown = true;
    }
    paint(p);
  }
  function leave(p) {
    p.stack?.remove();
    p.stack = null;
  }

  // --- Clock --------------------------------------------------------------------
  function freeze() {
    if (startedAt == null) return;
    offset = elapsed();
    startedAt = null;
    clearTimeout(timer);
    photos.forEach(p => { if (p.stack) paint(p); });
  }
  function boundary() {
    const end = startedAt + DUR[seg], late = now() - end;
    if (late < 0) { timer = setTimeout(boundary, 1 - late); return; }
    seg = (seg + 1) % S; offset = 0; startedAt = null;
    // An on-time boundary continues from the ideal instant, so the year does not stretch.
    carry = late < 100 ? end : null;
    sync();
  }
  function hold(on) {
    if (!on) { holdSince = null; clearTimeout(holdTimer); return; }
    if (holdSince != null) return;
    holdSince = performance.now();
    holdTimer = setTimeout(giveUp, HOLD);
  }
  function giveUp() {
    hold(false);
    stalled = true;
    sync();
  }
  const failed = (p, keys) => keys.some(key => { const f = p.frames.get(key); return f?.state === 'error' && f.tries > RETRIES; });

  function sync() {
    if (!M) return;
    if (reduced.matches) { freeze(); hold(false); photos.forEach(leave); controls(); return; }
    const live = photos.filter(participating);
    photos.forEach(p => { if (p.stack && !live.includes(p)) leave(p); });
    // The stuck photo scrolling away, or its frame arriving, lifts a stall.
    if (stalled && live.every(p => have(p, needs(p, seg, offset, true)))) stalled = false;
    const want = !paused && !stalled && !document.hidden && !print.matches && !dialogOpen() && live.length > 0;
    const blocked = live.filter(p => !have(p, needs(p, seg, offset, true)));
    if (want && startedAt != null) {
      // Running: a late arrival joins the dissolve in progress at the shared start time.
      live.forEach(p => { if (!p.stack && !blocked.includes(p)) show(p); });
    } else if (want && !blocked.length) {
      hold(false);
      startedAt = (offset === 0 && carry != null ? carry : now()) - offset;
      live.forEach(show);
      timer = setTimeout(boundary, DUR[seg] - offset);
    } else {
      freeze();
      const waiting = want ? blocked : [];
      if (waiting.some(p => failed(p, needs(p, seg, offset, true)))) { carry = null; giveUp(); return; }
      hold(waiting.length > 0);
      // Everyone holds together. A photo without the held frame shows its original.
      live.forEach(p => {
        if (have(p, needs(p, seg, offset, false))) show(p); else leave(p);
      });
    }
    carry = null;
    schedule();
    controls();
  }

  // --- Controls -----------------------------------------------------------------
  // One understated footer control. Its name is its state; a stall turns it into Resume.
  function controls() {
    toggle.hidden = !(shown || stalled) || still();
    const text = paused || stalled ? 'Resume animation' : 'Pause animation';
    if (toggle.textContent !== text) toggle.textContent = text;
    if (stalled) toggle.setAttribute('aria-description', 'Seasonal photos did not load.');
    else toggle.removeAttribute('aria-description');
  }
  function retry() {
    stalled = false;
    photos.forEach(p => p.frames.forEach(f => { if (f.state === 'error') { f.state = 'idle'; f.tries = 0; } }));
  }
  function remember() {
    // Only the paused preference survives a visit to the gallery; phase never does.
    try { paused ? sessionStorage.setItem(STORE, '1') : sessionStorage.removeItem(STORE); } catch { /* Preference lasts this page only. */ }
  }
  toggle.addEventListener('click', () => {
    if (stalled) retry();
    else { paused = !paused; remember(); }
    sync();
  });
  async function begin() {
    begun = true;
    let manifest;
    try {
      const response = await fetch(manifestUrl);
      if (!response.ok) return;
      manifest = await response.json();
    } catch { return; } // No manifest: originals remain and the controls stay hidden.
    ({knots: KN, steps: N} = manifest);
    DUR = manifest.durations.map(seconds => seconds * 1000);
    S = DUR.length;
    HOLD = (manifest.hold_seconds ?? 10) * 1000;
    FADE = manifest.fade_ms ?? 600;
    base = new URL('.', new URL(manifestUrl, document.baseURI)).href;
    document.querySelectorAll('.hero-photo figure, .story-photos figure').forEach(figure => {
      const position = Number(figure.dataset.position), entry = manifest.photos[position];
      const link = figure.querySelector('a'), original = link?.querySelector('img');
      if (!entry || !original) return;
      const own = new Set(entry.original || []);
      // Off-table keys would break the shared boundaries; all-original photos need nothing.
      if (entry.keys.some(key => !KN.includes(key)) || entry.keys.every(key => own.has(key))) return;
      photos.push({figure, link, original, position, own, keys: entry.keys, hero: Boolean(figure.closest('.hero-photo')),
        frames: new Map(), stack: null, near: false});
    });
    if (!photos.length) return;
    M = manifest;
    // The page already holds about 150 image entries; throughput needs the seasonal ones too.
    performance.setResourceTimingBufferSize?.(600);
    // Join a little before a photo reaches the viewport so it arrives at the shared phase.
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => { photos.find(p => p.link === entry.target).near = entry.isIntersecting; });
      sync();
    }, {root: document, rootMargin: '25% 0px'});
    photos.forEach(p => {
      observer.observe(p.link);
      if (!p.original.complete) p.original.addEventListener('load', sync, {once: true});
    });
    const watch = new MutationObserver(sync);
    document.querySelectorAll('dialog').forEach(dialog => watch.observe(dialog, {attributes: true, attributeFilter: ['open']}));
    // Stories fall back to inline originals on short or reduced layouts.
    document.querySelectorAll('.story').forEach(story => watch.observe(story, {attributes: true, attributeFilter: ['class']}));
    addEventListener('scroll', () => {
      if (scrollY !== lastY) direction = scrollY > lastY ? 1 : -1;
      lastY = scrollY;
    }, {passive: true});
    document.addEventListener('visibilitychange', sync);
    addEventListener('pageshow', sync);
    addEventListener('online', () => { if (stalled) retry(); sync(); });
    print.addEventListener('change', sync);
    // Clock state for fixtures; seek freezes the year at a point.
    window.seasonalClock = {
      state: () => ({segment: seg, elapsed: elapsed(), phase: phase(), running: startedAt != null, paused, stalled,
        holding: holdSince != null, rate, reach: reach(), joined: photos.filter(p => p.stack).map(p => p.position),
        decoded: Object.fromEntries(photos.map(p => [p.position, [...p.frames.values()].filter(f => f.img && f.state === 'ready').length]))}),
      seek(segment, ms = 0) {
        freeze(); hold(false);
        paused = true; stalled = false; seg = segment; offset = ms;
        sync();
      },
    };
    sync();
  }

  reduced.addEventListener('change', () => {
    // Turning the preference off never restarts motion by itself.
    if (!reduced.matches) { paused = true; shown = true; }
    if (begun) sync(); else if (!still()) begin();
  });
  print.addEventListener('change', () => { if (!begun && !still()) begin(); });
  if (!still()) begin();
})();
