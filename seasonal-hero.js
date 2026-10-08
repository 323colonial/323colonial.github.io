// One shared seasonal clock for the hero and the scroll-sequenced narrative photos.
// Each original <img> stays first in its link and is never altered. Seasonal frames
// sit in a two-layer stack above it, so every fallback is "remove the stack".
(() => {
  const manifestUrl = document.currentScript?.dataset.manifest;
  const group = document.querySelector('#season-controls');
  if (!manifestUrl || !group || !Element.prototype.animate || navigator.connection?.saveData) return;
  const toggle = group.querySelector('#hero-motion');
  const status = group.querySelector('#season-status');
  const seasonButtons = [...group.querySelectorAll('[data-season]')];
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
  let landing = null;              // segment a season button is loading
  let holdSince = null, holdTimer = 0, noteTimer = 0;
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
    const frozen = paused || stalled || landing != null;
    const want = (p, keys, keep) => keys.forEach(key => {
      let f = p.frames.get(key);
      if (!f) p.frames.set(key, f = {key, state: 'idle', img: null, tries: 0});
      if (!wanted.has(f)) order.push([p, f]);
      wanted.set(f, wanted.get(f) || keep);
    });
    const at = (p, s) => landing != null ? needs(p, landing, 0, false)
      : frozen ? needs(p, seg, offset, false)
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
    p.settling = null;
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
    p.stack = p.settling = null;
  }
  // Season buttons: every photo dissolves straight to the anchor together.
  function settle(p) {
    const keys = needs(p, seg, 0, false), target = p.frames.get(keys[0]).img;
    if (!p.stack || keys.length > 1) { show(p); return; }
    const top = p.stack.lastElementChild;
    let animation;
    if (target === top) animation = top.animate({opacity: 1}, {duration: FADE, fill: 'forwards'});
    else if (target.parentNode === p.stack) animation = top.animate({opacity: 0}, {duration: FADE, fill: 'forwards'});
    else { p.stack.append(target); animation = target.animate({opacity: [0, 1]}, FADE); }
    p.settling = animation;
    animation.finished.then(() => { if (p.settling === animation) { paint(p); controls(); } }, () => {});
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
    if (!on) { holdSince = null; clearTimeout(holdTimer); clearTimeout(noteTimer); return; }
    if (holdSince != null) return;
    holdSince = performance.now();
    holdTimer = setTimeout(giveUp, HOLD);
    noteTimer = setTimeout(controls, Math.min(1500, HOLD / 2));
  }
  function giveUp() {
    hold(false);
    // A season that cannot load leaves the visitor paused where they were.
    if (landing != null) landing = null; else stalled = true;
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
    if (landing != null && live.every(p => have(p, needs(p, landing, 0, false)))) {
      hold(false);
      seg = landing; offset = 0; landing = null;
      live.forEach(settle);
    }
    const want = !paused && !stalled && landing == null && !document.hidden && !print.matches && !dialogOpen() && live.length > 0;
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
      const waiting = landing != null ? live.filter(p => !have(p, needs(p, landing, 0, false))) : want ? blocked : [];
      const keys = p => landing != null ? needs(p, landing, 0, false) : needs(p, seg, offset, true);
      if (waiting.some(p => failed(p, keys(p)))) { carry = null; giveUp(); return; }
      hold(waiting.length > 0);
      // Everyone holds together. A photo without the held frame shows its original.
      live.forEach(p => {
        if (p.settling) return;
        if (have(p, needs(p, seg, offset, false))) show(p); else leave(p);
      });
    }
    carry = null;
    schedule();
    controls();
  }

  // --- Controls -----------------------------------------------------------------
  function controls() {
    group.hidden = !(shown || stalled) || still();
    toggle.textContent = paused || stalled ? 'Resume animation' : 'Pause animation';
    const settling = landing != null || photos.some(p => p.settling);
    const anchors = Object.entries(M.anchors).map(([name, step]) => [step, name.replace(/-/g, ' ')]).sort((x, y) => x[0] - y[0]);
    const at = phase() % N, exact = anchors.find(([step]) => step === at);
    const before = anchors.findLast(([step]) => step <= at) || anchors.at(-1);
    const after = anchors[(anchors.indexOf(before) + 1) % anchors.length];
    seasonButtons.forEach(button => button.setAttribute('aria-pressed',
      String(paused && !settling && M.anchors[button.dataset.season] === at)));
    const text = stalled ? 'Seasonal photos did not load. Animation paused.'
      : settling ? 'Changing season.'
      : paused ? (exact ? `Paused at ${exact[1]}.` : `Paused between ${before[1]} and ${after[1]}.`)
      : holdSince != null && performance.now() - holdSince >= Math.min(1400, HOLD / 2 - 5) ? 'Loading seasonal photos.' : '';
    if (status.textContent !== text) status.textContent = text;
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
    else { paused = !paused; landing = null; remember(); }
    sync();
  });
  seasonButtons.forEach(button => button.addEventListener('click', () => {
    if (!M) return;
    const index = KN.indexOf(M.anchors[button.dataset.season]);
    if (index < 0) return;
    paused = true; stalled = false;
    remember();
    freeze();
    hold(false);
    landing = index;
    sync();
  }));

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
        frames: new Map(), stack: null, settling: null, near: false});
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
    // Read-only clock for fixtures; seek freezes the year at a point, as a season button does.
    window.seasonalClock = {
      state: () => ({segment: seg, elapsed: elapsed(), phase: phase(), running: startedAt != null, paused, stalled,
        holding: holdSince != null, rate, reach: reach(), joined: photos.filter(p => p.stack).map(p => p.position),
        decoded: Object.fromEntries(photos.map(p => [p.position, [...p.frames.values()].filter(f => f.img && f.state === 'ready').length]))}),
      seek(segment, ms = 0) {
        freeze(); hold(false);
        paused = true; stalled = false; landing = null; seg = segment; offset = ms;
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
