import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

// Exercise private runtime functions without adding a shipped testing interface.
// Only image/network and animation APIs are doubled; browser fixtures cover real DOM/clock behavior.
function runtime() {
  const requests = [], animations = [];
  let constructions = 0;
  const hand = {
    style: {}, getAnimations: () => animations,
    animate() {
      constructions++;
      const animation = { startTime: null, cancel() { animations.splice(animations.indexOf(this), 1); } };
      animations.push(animation);
      return animation;
    },
  };
  const action = { textContent: '' }, attributes = new Map();
  const toggle = {
    querySelector: name => name === '.season-hand' ? hand : action,
    getAttribute: name => attributes.get(name), setAttribute: (name, value) => attributes.set(name, value),
  };
  const document = { currentScript: { dataset: { manifest: 'frames.json' } }, hidden: false,
    querySelector: name => name === '#hero-motion' ? toggle : null,
    timeline: { currentTime: 100 }, baseURI: 'http://localhost/' };
  const context = vm.createContext({ document, navigator: {}, Element: { prototype: { animate() {} } },
    matchMedia: () => ({ matches: false }), scrollY: 0, sessionStorage: { getItem() {} }, URL,
    performance: { now: () => 100, getEntriesByName: () => [] }, setTimeout() {}, clearTimeout() {},
    Image: class { decode() { return Promise.resolve(); } set src(value) { this.url = value; requests.push(this); } },
  });
  const source = readFileSync('seasonal-hero.js', 'utf8');
  const marker = "  toggle.addEventListener('click', () => {";
  assert.ok(source.includes(marker));
  vm.runInContext(source.replace(marker, `
    M = {}; KN = [0, 1, 2, 3]; DUR = [1000, 1000, 1000]; N = S = 3; HOLD = 1000; base = 'http://localhost/';
    sync = () => {};
    globalThis.runtime = { schedule, decode, retry, giveUp, controls,
      setup(value) { photos = value; rate = 1; },
      clock(s, start, ms = 0) { seg = s; startedAt = start; offset = ms; shown = true; },
      state: () => ({inflight, stalled}),
    };
    return;
  ` + marker), context);
  return { ...context.runtime, requests, hand, toggle, document, constructions: () => constructions };
}
const photo = position => ({ position, near: true, hero: true, own: new Set(), keys: [0, 1, 2], frames: new Map(),
  figure: { hidden: false }, original: { complete: true, naturalWidth: 1280, currentSrc: '' } });
const flush = async () => { await Promise.resolve(); await Promise.resolve(); };

test('two slots serve every participating current pair before any speculative frame', async t => {
  const r = runtime(), first = photo(1), second = photo(2);
  r.setup([first, second]);
  r.schedule();
  const urls = () => r.requests.map(img => img.url.replace('http://localhost/', ''));
  t.diagnostic(`first two slots: ${urls().join(', ')}`);
  for (const img of [...r.requests]) img.onload();
  await flush();
  const ready = [0, 1].filter(key => first.frames.get(key)?.state === 'ready').length;
  t.diagnostic(`required hero frames ready after first two completions: ${ready}/2`);
  assert.equal(ready, 2);
  assert.deepEqual(urls(), ['01/00.webp', '01/01.webp']);
  r.schedule();
  assert.deepEqual(urls(), ['01/00.webp', '01/01.webp', '02/00.webp', '02/01.webp']);
  assert.equal(r.state().inflight, 2);
  for (const img of r.requests.slice(2)) img.onload();
  await flush();
  r.schedule();
  assert.deepEqual(urls().slice(4), ['01/02.webp', '02/02.webp'], 'lookahead retained after current readiness');
});

test('Resume replaces unresolved decode without releasing its network slot twice; late result ignored', async () => {
  const r = runtime(), p = photo(1);
  r.setup([p]);
  r.schedule();
  const old = r.requests[0];
  let finishOld;
  old.decode = () => new Promise(resolve => { finishOld = resolve; });
  old.onload();
  const f = [...p.frames.values()].find(frame => frame.img === old);
  assert.equal(f.state, 'decoding');
  assert.equal(r.state().inflight, 1);
  r.giveUp();
  assert.equal(r.state().stalled, true);
  r.retry();
  assert.equal(f.state, 'idle');
  assert.equal(f.img, null);
  assert.equal(r.state().inflight, 0, 'only the other, still-loading frame released its slot');
  r.schedule();
  const fresh = f.img;
  assert.notEqual(fresh, old);
  assert.equal(r.state().inflight, 2);
  fresh.onload();
  await flush();
  assert.equal(f.state, 'ready');
  finishOld();
  await flush();
  assert.equal(f.img, fresh);
  assert.equal(f.state, 'ready');
  assert.equal(r.state().inflight, 1);
});

test('dial keeps unchanged animation and updates segment, shared start, frozen phase and visibility', t => {
  const r = runtime();
  r.clock(0, 50);
  for (let i = 0; i < 20; i++) r.controls();
  t.diagnostic(`20 unchanged syncs: ${r.constructions()} dial constructions`);
  assert.equal(r.constructions(), 1);
  assert.equal(r.hand.getAnimations()[0].startTime, 50);
  r.clock(1, 50); r.controls();
  assert.equal(r.constructions(), 2);
  r.clock(1, 75); r.controls();
  assert.equal(r.constructions(), 3);
  assert.equal(r.hand.getAnimations()[0].startTime, 75);
  r.clock(1, null, 500); r.controls();
  assert.equal(r.hand.getAnimations().length, 0);
  assert.equal(r.hand.style.transform, 'rotate(180deg)');
  r.clock(1, 75); r.controls();
  r.document.querySelector = name => name === '#hero-motion' ? r.toggle : {};
  r.controls();
  assert.equal(r.toggle.hidden, true);
  assert.equal(r.hand.getAnimations().length, 0);
  assert.equal(r.constructions(), 4);
});

test('listing owns its narrative helpers; gallery carries neither helper', () => {
  const listing = readFileSync('listing.js', 'utf8'), gallery = readFileSync('gallery.js', 'utf8');
  for (const name of ['createPhotoDots', 'photoInset']) {
    assert.match(listing, new RegExp(`function ${name}\\(`));
    assert.doesNotMatch(gallery, new RegExp(`\\b${name}\\b`));
  }
});
