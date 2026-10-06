import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import test from 'node:test';

const file = new URL('../analytics-core.mjs', import.meta.url);
const policy = existsSync(file) ? await import(file.href) : {};
const origin = 'https://323colonial.github.io';
const now = Date.parse('2026-10-06T15:00:00Z');
const source = { source: 'zillow', campaign: 'listing' };
const core = () => { assert.equal(typeof policy.nextVisit, 'function', 'analytics policy missing'); return policy; };

test('reload, cross-page and later visits keep only absolute-lifetime browser linkage', () => {
  const { nextVisit, TTL, IDLE } = core();
  const first = nextVisit(null, now, source);
  const reload = nextVisit(first, now + 1000, { source: 'direct', campaign: 'none' });
  assert.equal(reload.id, first.id);
  assert.equal(reload.visit, first.visit);
  assert.deepEqual(reload.current, source);
  const later = nextVisit(reload, now + IDLE + 1000, { source: 'direct', campaign: 'none' });
  assert.equal(later.id, first.id);
  assert.notEqual(later.visit, first.visit);
  assert.deepEqual(later.acquisition, source);
  assert.equal(later.current.source, 'direct');
  const nextDay = nextVisit(later, now + 86400000, source);
  assert.equal(nextDay.id, first.id);
  assert.notEqual(nextDay.visit, first.visit);
  const expired = nextVisit(nextDay, now + TTL, { source: 'direct', campaign: 'none' });
  assert.notEqual(expired.id, first.id);
  assert.equal(expired.born, now + TTL);
  assert.equal(expired.acquisition.source, 'direct');
  assert.equal(expired.firstVisit, expired.visit);
});

test('untrusted stored state fails closed and never restores unknown fields', () => {
  const { nextVisit, validState } = core();
  for (const s of [null, {}, { born: now + 1 }, { id: 'someone@example.com', born: now }]) {
    assert.equal(validState(s, now), false);
  }
  const good = nextVisit(null, now, source);
  assert.equal(validState(good, now), true);
  assert.equal(validState({ ...good, current: { source: 'secret', campaign: 'none' } }, now), false);
  const clean = nextVisit({ ...good, email: 'secret@example.com', current: { ...good.current, email: 'secret@example.com' } }, now + 1, source);
  assert.doesNotMatch(JSON.stringify(clean), /secret@example.com/);
});

test('sources and outbound destinations never preserve personal URLs or click IDs', () => {
  const { sourceFor, outbound } = core();
  assert.deepEqual(sourceFor(origin + '/?utm_source=zillow&utm_campaign=listing&email=secret&gclid=x', ''), source);
  assert.deepEqual(sourceFor(origin + '/?utm_source=secret@example.com&utm_campaign=recipient-123', ''), { source: 'direct', campaign: 'none' });
  assert.equal(sourceFor(origin, 'https://www.google.com/search?q=private').source, 'google');
  assert.equal(sourceFor(origin, origin + '/gallery.html').source, 'direct');
  assert.equal(sourceFor(origin, 'https://private-user.example/secret').source, 'other-referral');
  assert.equal(outbound('tel:+13048851547', origin), 'brokerage-phone');
  assert.equal(outbound('mailto:liz@dandridgerealtygroup.com?body=secret', origin), 'agent-email');
  assert.equal(outbound('https://www.zillow.com/secret?recipient=x', origin), 'zillow');
  assert.equal(outbound('https://other.example/private', origin), 'other-external');
  assert.equal(outbound('/gallery.html', origin), null);
  assert.equal(outbound('javascript:alert(1)', origin), null);
});

test('event allowlist discards SDK enrichment, profile setters, URLs and arbitrary text', () => {
  const { nextVisit, sanitizeEvent } = core();
  const state = nextVisit(null, now, source);
  const event = sanitizeEvent({ event: '$pageview', timestamp: new Date(now), $set: { email: 'private' }, properties: {
    $current_url: origin + '/?private=1', $referrer: 'private', $ip: '1.2.3.4', $geoip_latitude: 40,
    $device_type: 'Desktop', $browser: 'Chrome', text: 'private', token: 'public',
  } }, state, origin + '/?secret=1', now);
  assert.equal(event.properties.distinct_id, state.id);
  assert.equal(event.properties.$current_url, origin + '/');
  assert.equal(event.properties.$process_person_profile, false);
  assert.equal(event.properties.$geoip_disable, true, 'built-in full GeoIP must be disabled on every event');
  assert.equal(event.properties.returning_browser, false);
  assert.equal(event.properties.device, 'Desktop');
  assert.equal('token' in event.properties, false);
  assert.equal('$set' in event, false);
  assert.doesNotMatch(JSON.stringify(event), /private|1\.2\.3\.4|Chrome|geoip_latitude/);
  assert.equal(sanitizeEvent({ event: '$identify', properties: {} }, state, origin, now), null);
  const later = nextVisit(state, now + 86400000, source);
  const returned = sanitizeEvent({ event: '$pageview', properties: {} }, later, origin, now + 86400000);
  assert.equal(returned.properties.returning_browser, true);
  assert.equal(returned.properties.later_day_return, true);
});

test('heatmap batches bound paths, points and exact coordinate fields', () => {
  const { nextVisit, sanitizeEvent } = core();
  const state = nextVisit(null, now, source);
  const point = { x: 40, y: 80, target_fixed: true, type: 'click', text: 'private' };
  const event = sanitizeEvent({ event: '$$heatmap', properties: { $heatmap_data: {
    [origin + '/?email=secret']: Array(120).fill(point),
    [origin + '/gallery.html#secret']: [point],
    [origin + '/not-approved']: [point],
    'https://evil.example/': [point],
  } } }, state, origin, now);
  const data = event.properties.$heatmap_data;
  assert.ok(Object.keys(data).every(k => [origin + '/', origin + '/gallery.html'].includes(k)));
  assert.equal(Object.values(data).flat().length, 100);
  assert.deepEqual(data[origin + '/'][0], { x: 40, y: 80, target_fixed: true, type: 'click' });
  assert.doesNotMatch(JSON.stringify(event), /secret|private|evil|not-approved/);
  assert.equal(sanitizeEvent({ event: '$pageview', properties: {} }, state, origin + '/tests/test.html', now), null);
});

test('attention excludes hidden, unfocused, idle and pre-resume time', () => {
  const { activeMillis } = core();
  assert.equal(activeMillis(0, 10000, 0, true), 10000);
  assert.equal(activeMillis(0, 60000, 0, true), 30000);
  assert.equal(activeMillis(40000, 60000, 0, true), 0);
  assert.equal(activeMillis(0, 10000, 0, false), 0);
  assert.equal(activeMillis(20000, 19000, 20000, true), 0);
});

test('buyer pages contain native notice/opt-out and only gated analytics module', () => {
  for (const name of ['index.html', 'gallery.html']) {
    const html = readFileSync(name, 'utf8');
    assert.match(html, /id="analytics-privacy"/);
    assert.match(html, /id="analytics-opt-out"/);
    assert.match(html, /type="module" src="analytics\.mjs"/);
    assert.doesNotMatch(html, /src="[^"]*posthog/);
  }
});
