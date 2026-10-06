import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';
import * as policy from '../analytics-core.mjs';

// Replace only module loading: DOM/storage and SDK transport are boundary doubles.
const original = readFileSync('analytics.mjs', 'utf8');
const source = original.slice(original.indexOf('\n') + 1).replace("import('./vendor/posthog-1.438.1.mjs')", 'loadSDK()');
const settle = async () => { for (let i = 0; i < 3; i++) await new Promise(setImmediate); };
function harness(options = {}) {
  let now = Date.parse('2026-10-06T15:00:00Z'), perf = 0, config, loads = 0, reads = 0;
  const jar = options.jar || { cookie: '' };
  const storage = options.storage || new Map();
  const handlers = new Map(), events = [], timers = [];
  const node = () => ({ textContent: '', disabled: false, addEventListener(type, fn) { this[type] = fn; } });
  const button = node(), status = node(), dialog = { open: false }, image = { src: policy.ORIGIN + '/assets/listing/01.webp', complete: true, naturalWidth: 1600, style: { visibility: 'visible' }, ...node() };
  let mutation;
  const doc = {
    visibilityState: 'visible', hasFocus: () => true, referrer: '',
    querySelector: s => ({ '#analytics-opt-out': button, '#analytics-status': status, '#photo-viewer': dialog, '#viewer-image': image })[s] || null,
    querySelectorAll: () => [],
    addEventListener: (name, fn) => { const list = handlers.get(name) || []; list.push(fn); handlers.set(name, list); },
    get cookie() { reads++; return jar.cookie; },
    set cookie(s) { if (!options.blockCookie) jar.cookie = s.includes('Max-Age=0') ? '' : s.split(';')[0]; },
  };
  const sdk = {
    init(token, c) { config = c; },
    set_config(c) { Object.assign(config || {}, c); },
    heatmaps: { getAndClearBuffer() {} },
    capture(event, properties) {
      const result = config.before_send({ event, properties: { $device_type: 'Desktop', ...properties }, timestamp: new Date(now) });
      if (result) events.push(result);
    },
  };
  const context = vm.createContext({ ...policy, URL, URLSearchParams, Date: class extends Date { static now() { return now; } },
    crypto, AbortController, console, performance: { now: () => perf }, document: doc,
    navigator: { globalPrivacyControl: options.gpc, locks: { request: (_name, fn) => new Promise(resolve => setImmediate(resolve)).then(fn) } },
    location: new URL(options.url || policy.ORIGIN + '/?utm_source=zillow&private=secret'),
    localStorage: {
      getItem(k) { if (options.blockStorage) throw Error('blocked'); return storage.get(k) || null; },
      setItem(k, v) { if (options.blockStorage) throw Error('blocked'); storage.set(k, v); },
    },
    addEventListener: doc.addEventListener,
    IntersectionObserver: class { observe() {} disconnect() {} },
    MutationObserver: class { constructor(fn) { mutation = fn; } observe() {} disconnect() {} },
    setInterval(fn) { timers.push(fn); return timers.length; }, clearInterval() {},
    loadSDK: async () => { loads++; if (options.blockSDK) throw Error('blocked SDK'); return { default: sdk }; },
  });
  context.window = context; context.top = context;
  vm.runInContext(source, context);
  return { jar, storage, events, status, button, doc, dialog, image, sdk, context,
    get config() { return config; }, get loads() { return loads; }, get reads() { return reads; },
    emit(name, event = {}) { for (const fn of handlers.get(name) || []) fn(event); },
    advance(ms) { now += ms; perf += ms; }, tick() { timers.forEach(fn => fn()); },
    mutate() { mutation(); }, duplicate() { vm.runInContext(`{ ${source} }`, context); },
  };
}

test('GPC, opted-out and development pages never load SDK or read analytics cookie', async () => {
  for (const options of [{ gpc: true }, { blockStorage: true }, { storage: new Map([['colonial_analytics_opt_out', '1']]) }, { url: 'http://localhost:8765/' }]) {
    const h = harness(options); await settle();
    assert.equal(h.loads, 0); assert.equal(h.reads, 0); assert.equal(h.events.length, 0);
  }
});

test('blocked SDK/cookie remains usable and honestly reports unavailable analytics', async () => {
  for (const options of [{ blockSDK: true }, { blockCookie: true }]) {
    const h = harness(options); await settle();
    assert.equal(h.events.length, 0);
    assert.match(h.status.textContent, /not running|unavailable/i);
    h.button.click();
    assert.equal(h.storage.get('colonial_analytics_opt_out'), '1');
  }
});

test('reload and navigation reuse visit, later day returns, expiry breaks linkage', async () => {
  const h = harness(); await settle();
  const first = h.events[0].properties;
  const second = harness({ jar: h.jar, url: policy.ORIGIN + '/gallery.html' }); await settle();
  assert.equal(second.events[0].properties.distinct_id, first.distinct_id);
  assert.equal(second.events[0].properties.visit_id, first.visit_id);
  h.advance(86400000); h.emit('focus'); await settle();
  assert.equal(h.events.filter(e => e.event === '$pageview').length, 2, 'later visit on an open tab gets a pageview');
  assert.equal(h.events.at(-1).properties.distinct_id, first.distinct_id);
  assert.equal(h.events.at(-1).properties.later_day_return, true);
  h.advance(policy.TTL); h.emit('focus'); await settle(); h.sdk.capture('$pageview', {});
  assert.notEqual(h.events.at(-1).properties.distinct_id, first.distinct_id);
  assert.equal(h.events.at(-1).properties.returning_browser, false);
});

test('one outbound listener survives duplicate injection and expired visit keyboard click', async () => {
  const h = harness(); await settle(); h.duplicate(); await settle();
  const link = { href: 'tel:+13048851547', closest: () => null };
  const click = { isTrusted: true, target: { closest: () => link } };
  h.emit('click', click); await settle();
  assert.equal(h.events.filter(e => e.event === 'outbound_click').length, 1);
  h.advance(policy.IDLE + 1);
  h.emit('keydown', { isTrusted: true }); h.emit('click', click); await settle();
  assert.equal(h.events.filter(e => e.event === 'outbound_click').length, 2);
});

test('photo attention excludes hidden and idle periods and stops on close', async () => {
  const h = harness(); await settle();
  h.dialog.open = true; h.mutate(); h.advance(10000);
  h.doc.visibilityState = 'hidden'; h.emit('visibilitychange');
  assert.equal(h.events.at(-1).properties.active_ms, 10000);
  const count = h.events.length;
  h.advance(60000); h.tick(); assert.equal(h.events.length, count);
  h.doc.visibilityState = 'visible'; h.emit('visibilitychange');
  h.advance(60000); h.tick(); assert.equal(h.events.at(-1).properties.active_ms, 30000);
  h.dialog.open = false; h.mutate(); const closed = h.events.length;
  h.advance(10000); h.tick(); assert.equal(h.events.length, closed);
});

test('opt-out aborts transport, clears ID and prevents subsequent events across tabs', async () => {
  const h = harness(); await settle();
  assert.equal(h.config.persistence, 'memory');
  assert.equal(h.config.advanced_disable_flags, true);
  assert.equal(h.config.fetch_options.credentials, 'omit');
  h.button.click(); const count = h.events.length;
  assert.equal(h.jar.cookie, ''); assert.equal(h.config.fetch_options.signal.aborted, true);
  h.sdk.capture('$pageview', {}); assert.equal(h.events.length, count);
  const other = harness({ storage: h.storage, jar: h.jar }); await settle();
  assert.equal(other.loads, 0); assert.equal(other.reads, 0);
});
