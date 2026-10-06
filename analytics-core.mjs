// Policy shared by the browser adapter and offline regression checks.
export const ORIGIN = 'https://323colonial.github.io';
export const TTL = 90 * 86400000;
export const IDLE = 30 * 60000;
const channels = ['direct', 'google', 'bing', 'zillow', 'facebook', 'instagram', 'email', 'brokerage', 'other-referral'];
const campaigns = ['none', 'listing', 'open-house'];
const events = ['$pageview', '$pageleave', '$$heatmap', 'photo_open', 'details_open', 'gallery_open', 'outbound_click', 'engagement'];
const uuid = /^[\da-f]{8}-[\da-f]{4}-[47][\da-f]{3}-[89ab][\da-f]{3}-[\da-f]{12}$/;
const day = time => new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(time);
const validSource = s => s && channels.includes(s.source) && campaigns.includes(s.campaign);

export function pageURL(value) {
  try {
    const url = new URL(value, ORIGIN);
    if (url.origin !== ORIGIN || !['/', '/index.html', '/gallery.html'].includes(url.pathname)) return null;
    return ORIGIN + (url.pathname === '/index.html' ? '/' : url.pathname);
  } catch { return null; }
}

export function sourceFor(href, referrer) {
  let source = 'direct', campaign = 'none';
  try {
    const url = new URL(href, ORIGIN);
    const supplied = url.searchParams.get('utm_source');
    if (channels.includes(supplied)) source = supplied;
    else if (referrer) {
      const ref = new URL(referrer);
      if (ref.origin !== ORIGIN) {
        source = ['google', 'bing', 'zillow', 'facebook', 'instagram'].find(name =>
          ref.hostname === `${name}.com` || ref.hostname.endsWith(`.${name}.com`)) || 'other-referral';
      }
    }
    if (campaigns.includes(url.searchParams.get('utm_campaign'))) campaign = url.searchParams.get('utm_campaign');
  } catch { /* Malformed or unavailable referrer is direct/unknown. */ }
  return { source, campaign };
}

export function validState(s, now) {
  return Boolean(s && uuid.test(s.id) && uuid.test(s.visit) && uuid.test(s.firstVisit) &&
    Number.isSafeInteger(s.born) && s.born > 0 && s.born <= now && now - s.born < TTL &&
    Number.isSafeInteger(s.last) && s.last >= s.born && s.last <= now &&
    validSource(s.acquisition) && validSource(s.current));
}

export function nextVisit(previous, now, source) {
  source = validSource(source) ? { source: source.source, campaign: source.campaign } : { source: 'direct', campaign: 'none' };
  const valid = validState(previous, now);
  const fresh = !valid || now - previous.last >= IDLE;
  // UUIDv7 timestamp prefix lets PostHog's session reports recognize visit start.
  const hex = now.toString(16).padStart(12, '0');
  const visit = fresh ? `${hex.slice(0, 8)}-${hex.slice(8)}-7${crypto.randomUUID().slice(15)}` : previous.visit;
  return {
    id: valid ? previous.id : crypto.randomUUID(), born: valid ? previous.born : now,
    visit, firstVisit: valid ? previous.firstVisit : visit, last: now,
    acquisition: valid ? { source: previous.acquisition.source, campaign: previous.acquisition.campaign } : source,
    current: fresh ? source : { source: previous.current.source, campaign: previous.current.campaign },
  };
}

export function outbound(href, base) {
  try {
    const url = new URL(href, base);
    if (url.protocol === 'tel:') return url.pathname === '+13048851547' ? 'brokerage-phone' : 'other-phone';
    if (url.protocol === 'mailto:') return url.pathname === 'liz@dandridgerealtygroup.com' ? 'agent-email' : 'other-email';
    if (!['http:', 'https:'].includes(url.protocol) || url.origin === new URL(base).origin) return null;
    return url.hostname === 'zillow.com' || url.hostname.endsWith('.zillow.com') ? 'zillow' : 'other-external';
  } catch { return null; }
}

export function activeMillis(start, end, lastActivity, visible) {
  return visible ? Math.max(0, Math.min(end, lastActivity + 30000) - start) : 0;
}

export function sanitizeEvent(event, state, href, now) {
  const url = pageURL(href);
  if (!url || !events.includes(event?.event) || !validState(state, now)) return null;
  const input = event.properties || {};
  const properties = {
    distinct_id: state.id, $session_id: state.visit, visit_id: state.visit,
    $current_url: url, $pathname: new URL(url).pathname,
    $process_person_profile: false, $is_identified: false,
    $geoip_disable: true, // Only the coarse-only hosted transformation may enrich location.
    source: state.current.source, campaign: state.current.campaign,
    acquisition_source: state.acquisition.source, acquisition_campaign: state.acquisition.campaign,
    returning_browser: state.visit !== state.firstVisit,
    later_day_return: state.visit !== state.firstVisit && day(now) !== day(state.born),
    device: ['Desktop', 'Mobile', 'Tablet'].includes(input.$device_type) ? input.$device_type : 'unknown',
  };
  if (event.event === '$$heatmap') {
    const data = {};
    let remaining = 100;
    for (const [raw, points] of Object.entries(input.$heatmap_data || {})) {
      const path = pageURL(raw);
      if (!path || !Array.isArray(points)) continue;
      for (const point of points) {
        if (!remaining || !point || !['click', 'mousemove'].includes(point.type) ||
          !Number.isFinite(point.x) || !Number.isFinite(point.y) ||
          point.x < 0 || point.x > 20000 || point.y < 0 || point.y > 500000) continue;
        (data[path] ||= []).push({ x: Math.round(point.x), y: Math.round(point.y), target_fixed: point.target_fixed === true, type: point.type });
        remaining--;
      }
    }
    if (remaining === 100) return null;
    properties.$heatmap_data = data;
  }
  for (const key of ['$viewport_width', '$viewport_height', '$screen_width', '$screen_height']) {
    if (Number.isFinite(input[key]) && input[key] > 0 && input[key] <= 20000) properties[key] = Math.round(input[key]);
  }
  if (Number.isInteger(input.photo) && input.photo >= 1 && input.photo <= 73) properties.photo = input.photo;
  if (Number.isInteger(input.section) && input.section >= 1 && input.section <= 7) properties.section = input.section;
  if (['photo', 'details', 'gallery', 'story'].includes(input.subject)) properties.subject = input.subject;
  if (Number.isInteger(input.active_ms) && input.active_ms >= 1000 && input.active_ms <= 1800000) properties.active_ms = input.active_ms;
  if (['brokerage-phone', 'agent-email', 'other-phone', 'other-email', 'zillow', 'other-external'].includes(input.destination)) properties.destination = input.destination;
  if (['header', 'contact', 'content', 'footer'].includes(input.placement)) properties.placement = input.placement;
  return { event: event.event, timestamp: event.timestamp, properties };
}
