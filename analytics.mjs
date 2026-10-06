import { ORIGIN, TTL, IDLE, pageURL, sourceFor, validState, nextVisit, outbound, activeMillis, sanitizeEvent } from './analytics-core.mjs';

const TOKEN = 'phc_sw6mykKHJ2N4ifnbdGEqnhvUSUYVdFPczjk3L2u8ez5X';
const COOKIE = 'colonial_analytics';
const OPT_OUT = 'colonial_analytics_opt_out';

// Module caching plus this guard also protects against duplicate script injection.
if (!window.__colonialAnalyticsStarted) {
  window.__colonialAnalyticsStarted = true;
  start().catch(() => {
    const status = document.querySelector('#analytics-status');
    if (status) status.textContent = 'PostHog analytics is unavailable. Browsing and contact links still work.';
  });
}

async function start() {
  const button = document.querySelector('#analytics-opt-out');
  const status = document.querySelector('#analytics-status');
  let sdk, stopped = false, state, sent = 0;
  const transport = new AbortController();
  const setStatus = text => { if (status) status.textContent = text; };
  const erase = () => { document.cookie = `${COOKIE}=; Max-Age=0; Path=/; SameSite=Lax; Secure`; };
  const blocked = () => {
    if (stopped || navigator.globalPrivacyControl === true || navigator.doNotTrack === '1') return true;
    try { return localStorage.getItem(OPT_OUT) === '1'; } catch { return true; }
  };
  function stop() {
    stopped = true;
    transport.abort(); // Also prevents queued SDK retries from sending after opt-out.
    sdk?.set_config({ capture_heatmaps: false });
    sdk?.heatmaps?.getAndClearBuffer();
    try { erase(); } catch { /* Cookie access can itself be denied. */ }
  }
  button?.addEventListener('click', () => {
    stop();
    try {
      localStorage.setItem(OPT_OUT, '1');
      setStatus('PostHog analytics is off for this browser. Existing server records are not deleted.');
    } catch {
      setStatus('Analytics is off on this page. Your browser could not save this choice; enable Global Privacy Control to keep opting out.');
    }
    button.disabled = true;
  });
  addEventListener('storage', event => { if (event.key === OPT_OUT && event.newValue === '1') { stop(); setStatus('PostHog analytics is off for this browser.'); } });
  if (new URLSearchParams(location.search).get('analytics') === 'off') {
    stop();
    try { localStorage.setItem(OPT_OUT, '1'); } catch { /* Current page still stops. */ }
  }
  // Check GPC before reading the preference or any analytics cookie, or loading SDK.
  if (blocked()) { setStatus('PostHog analytics is off for this browser.'); return; }
  if (location.origin !== ORIGIN || !pageURL(location.href) || window.top !== window || !navigator.locks || !/^phc_[\w-]+$/.test(TOKEN)) {
    setStatus('PostHog analytics is not running on this page.'); return;
  }
  function readState() {
    const value = document.cookie.split('; ').find(part => part.startsWith(COOKIE + '='))?.slice(COOKIE.length + 1);
    try { return value ? JSON.parse(decodeURIComponent(value)) : null; } catch { return null; }
  }
  function writeState(value) {
    const encoded = encodeURIComponent(JSON.stringify(value));
    document.cookie = `${COOKIE}=${encoded}; Expires=${new Date(value.born + TTL).toUTCString()}; Path=/; SameSite=Lax; Secure`;
    if (readState()?.id !== value.id) throw new Error('Analytics cookie unavailable');
  }
  const update = async initial => navigator.locks.request(COOKIE, () => {
    if (blocked()) return false;
    const now = Date.now();
    const previous = readState();
    const next = nextVisit(previous, now, initial ? sourceFor(location.href, document.referrer) : { source: 'direct', campaign: 'none' });
    const changed = state && state.visit !== next.visit;
    if (changed) { flush(); sdk?.heatmaps?.getAndClearBuffer(); }
    writeState(next);
    state = next;
    if (!initial && changed) capture('$pageview');
    return true;
  });

  // No network SDK loader, remote configuration, replay bundle or arbitrary site apps.
  sdk = (await import('./vendor/posthog-1.438.1.mjs')).default;
  if (blocked() || !await update(true)) return;
  sdk.init(TOKEN, {
    api_host: 'https://us.i.posthog.com', ui_host: 'https://us.posthog.com',
    persistence: 'memory', disable_persistence: true, cross_subdomain_cookie: false,
    bootstrap: { distinctID: state.id, isIdentifiedID: false, sessionID: state.visit },
    person_profiles: 'never', cookieless_mode: 'never',
    autocapture: false, capture_pageview: false, capture_pageleave: false,
    capture_heatmaps: { flush_interval_milliseconds: 60000 }, rageclick: false,
    capture_dead_clicks: false, capture_performance: false, capture_exceptions: false,
    disable_session_recording: true, disable_surveys: true, disable_conversations: true,
    disable_product_tours: true, disable_web_experiments: true, opt_in_site_apps: false,
    advanced_disable_flags: true, advanced_disable_toolbar_metrics: true,
    disable_external_dependency_loading: true, disableDeviceModel: true,
    internal_or_test_user_hostname: null, save_campaign_params: false, save_referrer: false,
    mask_all_text: true, mask_all_element_attributes: true, disable_capture_url_hashes: true,
    get_current_url: () => pageURL(location.href),
    api_transport: 'fetch', disable_beacon: true, request_batching: false, disable_compression: true,
    fetch_options: { signal: transport.signal, credentials: 'omit', referrerPolicy: 'no-referrer', keepalive: true },
    before_send: event => {
      try {
        if (blocked()) { stop(); return null; }
        const current = readState(), now = Date.now();
        if (!validState(current, now) || now - current.last >= IDLE || sent >= 400) return null;
        const clean = sanitizeEvent(event, current, location.href, now);
        if (!clean) return null;
        clean.properties.token = TOKEN;
        sent++;
        return clean;
      } catch { stop(); return null; }
    },
  });
  setStatus('PostHog analytics is on. You can turn it off for this browser.');
  const capture = (name, props = {}) => {
    if (!blocked()) sdk.capture(name, props);
  };
  capture('$pageview');

  // One delegated listener; never preventDefault, submit, or delay navigation.
  document.addEventListener('click', event => {
    const link = event.target.closest?.('a[href]');
    if (!link || !event.isTrusted) return;
    const destination = outbound(link.href, location.href);
    if (!destination) return;
    const placement = link.closest('.contact-panel') ? 'contact' : link.closest('header') ? 'header' : link.closest('footer') ? 'footer' : 'content';
    // Web Lock grants are asynchronous, including keyboard activation after idle.
    update(false).then(ready => { if (ready) capture('outbound_click', { destination, placement }); }).catch(stop);
  });

  const photo = document.querySelector('#photo-viewer');
  const image = document.querySelector('#viewer-image');
  const details = document.querySelector('#property-details');
  const gallery = document.querySelector('#all-photos');
  const sections = [...document.querySelectorAll('.story-copy')];
  const visibility = new Map();
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) visibility.set(entry.target, entry.intersectionRatio);
    changeSubject();
  }, { threshold: [0, .5, 1] });
  sections.forEach(section => observer.observe(section));
  const fallback = document.querySelector('#details');
  if (fallback) observer.observe(fallback);
  let subject = null, elapsed = 0, lastTick = performance.now(), activity = lastTick;
  let wasVisible = document.visibilityState === 'visible' && document.hasFocus();
  let lastWrite = 0, lastPhoto = null, detailsOpen = false, galleryOpen = false;
  const visible = () => document.visibilityState === 'visible' && document.hasFocus();
  function measure() {
    const now = performance.now();
    if (subject) elapsed += activeMillis(lastTick, now, activity, wasVisible);
    lastTick = now;
    wasVisible = visible();
  }
  function flush() {
    measure();
    if (subject && elapsed >= 1000) capture('engagement', { ...subject, active_ms: Math.min(1800000, Math.round(elapsed)) });
    elapsed = 0;
  }
  function changeSubject() {
    measure();
    let next = null;
    if (photo?.open) {
      const match = new URL(image.src).pathname.match(/\/assets\/listing\/(\d{2})\.webp$/);
      const id = match ? Number(match[1]) : null;
      if (id && id !== lastPhoto) capture('photo_open', { photo: id });
      lastPhoto = id;
      if (id && image.complete && image.naturalWidth && image.style.visibility !== 'hidden') next = { subject: 'photo', photo: id };
    } else {
      lastPhoto = null;
      if (details?.open) next = { subject: 'details' };
      else if (gallery?.open) next = { subject: 'gallery' };
      else {
        const section = sections.findIndex(node => visibility.get(node) >= .5);
        if (section >= 0) next = { subject: 'story', section: section + 1 };
        else if (visibility.get(fallback) >= .5) next = { subject: 'details' };
      }
    }
    if (details?.open && !detailsOpen) capture('details_open');
    if (gallery?.open && !galleryOpen) capture('gallery_open');
    detailsOpen = Boolean(details?.open); galleryOpen = Boolean(gallery?.open);
    if (JSON.stringify(next) !== JSON.stringify(subject)) { flush(); subject = next; }
  }
  const mutation = new MutationObserver(changeSubject);
  [photo, details, gallery].filter(Boolean).forEach(dialog => mutation.observe(dialog, { attributes: true, attributeFilter: ['open'] }));
  if (image) {
    mutation.observe(image, { attributes: true, attributeFilter: ['src', 'style'] });
    image.addEventListener('load', changeSubject);
    image.addEventListener('error', changeSubject);
  }
  function interact(event) {
    if (!event.isTrusted || !visible()) return;
    measure();
    activity = performance.now();
    if (Date.now() - lastWrite >= 1000) {
      lastWrite = Date.now();
      update(false).catch(stop);
    }
  }
  ['pointerdown', 'keydown', 'scroll', 'touchstart'].forEach(name => document.addEventListener(name, interact, { passive: true, capture: true }));
  document.addEventListener('visibilitychange', () => { flush(); if (visible()) activity = performance.now(); });
  addEventListener('blur', flush);
  addEventListener('focus', () => { measure(); activity = performance.now(); update(false).catch(stop); });
  addEventListener('pagehide', () => { flush(); capture('$pageleave'); });
  addEventListener('pageshow', event => { if (event.persisted) { measure(); activity = performance.now(); update(false).catch(stop); } });
  const timer = setInterval(() => {
    if (blocked()) { stop(); clearInterval(timer); observer.disconnect(); mutation.disconnect(); return; }
    measure();
    if (performance.now() - activity >= 30000 && elapsed) flush();
  }, 1000); // Local timing only: no heartbeat requests.
  changeSubject();
}
