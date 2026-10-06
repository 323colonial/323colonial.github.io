# PostHog implementation plan

**Issue:** colonial-zoc.2
**Design:** colonial-zoc.1 final SETUP HANDOFF
**Date:** 2026-10-06
**Branch:** main

**Goal:** Implement approved buyer analytics without altering listing content or native navigation.

**Boundary:** Browser persistence and third-party event ingestion. Public token comes from ignored `.posthog.token`; never publish that file. Pinned self-hosted PostHog JS 1.438.1 avoids a third-party script CDN and unpinned SDK updates. SDK uses memory only; one first-party cookie owns absolute 90-day browser lifetime and shared 30-minute visits. Native Web Locks serialize cross-tab visit creation; no locks/storage means no collection. SDK session persistence cannot enforce approved absolute lifetime/source-minimization alone. No geographic gate, proxy, fingerprinting, replay, person profiles, general autocapture, or opt-in UI.

## Implementation

1. Add `tests/analytics.test.mjs`, observe RED, then implement pure policy/state/payload functions in `analytics-core.mjs`.
2. Add `analytics.mjs` integration: GPC/exclusion/opt-out before SDK or analytics cookie, shared visits, bounded sanitized heatmaps, active-visible engagement and one delegated outbound listener. SDK source inspection confirms heatmaps use `capture('$$heatmap', {$heatmap_data: ...})`, passing through `before_send` in selected version.
3. Add native privacy disclosure/opt-out on both buyer pages, preserve dated footer and Cloudflare. Deliberately extend publication allowlist for modules and pinned SDK/license. Token embedded only as public project configuration; original token file remains ignored.
4. Verify Node/Python suite and PRODUCT browser fixtures plus deterministic offline analytics integration. Record schema/report recipe and account/live checks separately.

## Verification

```sh
node --test tests/analytics.test.mjs
npm test
python3 tests/test_listing.py
python3 test_design.py
python3 test_marketing_plans.py
python3 -m http.server 8765 --bind 127.0.0.1
```

Run PRODUCT browser fixtures and analytics fixture through loopback, with no live PostHog events. Verify no raw URLs/queries/text enter payloads, absolute expiry and distinct visit identity, idle/hidden exclusion, click de-duplication, blocked SDK/storage, opt-out/GPC and heatmap path/point bounds. Live ingestion/report correctness requires separately authorized synthetic events and account configuration; local tests do not prove them. Server coarse-location filtering remains a recorded technical gate, not permission to reopen settled owner policy. User requests getting site running; no remote publication until target, bounded release scope and privacy configuration are verified and applicable approval recorded.
