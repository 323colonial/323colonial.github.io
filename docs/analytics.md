# Buyer analytics

Bead: `colonial-zoc.2`. Implementation is local; account configuration, ingested event verification and deployment are not yet complete.

## Browser contract

`analytics.mjs` gates PostHog before loading its SDK or reading its analytics cookie. GPC, DNT, saved opt-out, non-production origins, unsupported routes, embedded pages, missing Web Locks and refused preference storage prevent collection. `?analytics=off` saves the owner's browser exclusion before initialization. Opt-out remains usable even when the SDK is blocked. Cloudflare Web Analytics is unchanged and separate.

The public ingestion token is embedded in the browser module from ignored `.posthog.token`; the original file is never a publication asset. Never put a personal PostHog API key here.

`colonial_analytics` is a host-only Secure/SameSite=Lax cookie containing random browser/visit IDs, creation/activity timestamps, and enumerated source/campaign labels. It expires **90 days from creation**, never from last use. Missing, invalid or expired state starts fresh, without recovering old identity. Web Locks serialize cross-tab state changes. SDK persistence is memory-only: no second SDK browser ID can survive expiry. Browser identity is not a human identity.

Visits split after **30 minutes without foreground interaction**. Reloads, navigation and concurrent tabs reuse the visit ID. A foreground return after that gap starts another visit, even on an already-open page. Native UUIDv7-shaped visit IDs populate both `visit_id` and `$session_id`; SDK internal session state is not reporting authority. Count distinct visit IDs, not pageviews, to avoid reload inflation. Later-day returns compare current and first-acquisition dates in America/New_York and require a different visit.

Sources: direct, Google, Bing, Zillow, Facebook, Instagram, email, brokerage, other-referral. Only exact lower-case enumerated `utm_source` values and campaigns `listing` / `open-house` survive; everything else is discarded. Original acquisition and current-visit attribution remain separate. No raw referrers, query strings, fragments, ad IDs, contact addresses or DOM text are sent. Unknown/direct is explicit, not inferred from timezone.

## Events

All events carry sanitized canonical page URL/path, browser/visit IDs, current/acquisition source and campaign, coarse device category, returning-browser/later-day booleans, `$process_person_profile:false`, `$is_identified:false`, and `$geoip_disable:true`. Approved viewport/screen dimensions support heatmaps. No identify/alias/person enrichment, general autocapture, replay, remote flags/config, surveys, errors, web vitals, ad integrations or external scripts.

| Event | Additional properties / definition |
| --- | --- |
| `$pageview` | Initial page and later visit on open tab. Not a unique visit count. |
| `$pageleave` | Best-effort page exit. Not proof that the buyer abandoned an inquiry. |
| `photo_open` | `photo`: stable manifest position 1–73, matching existing `data-position`. Includes viewer arrow navigation. Manifest descriptive `id` values are not unique; positions are frozen by listing tests. |
| `details_open`, `gallery_open` | Successful native dialog opening. |
| `engagement` | `subject`: photo/details/gallery/story; photo or section 1–7; `active_ms`. Requires visible focused tab, loaded visible enlarged image or qualifying visible section. Stops after 30 seconds without interaction. Emits on subject change, hidden/blur, idle and exit, only for at least one second. Estimates attention, not exact reading. |
| `outbound_click` | Destination category: brokerage-phone, agent-email, Zillow, other-phone/email/external; placement: header/contact/content/footer. No full destination URL. One delegated trusted-click handler; navigation is never prevented. Capture is best-effort, especially immediate document departure. |
| `$$heatmap` | SDK batches every 60 seconds; sanitized URL-keyed coordinates only, at most 100 valid points per batch. `/index.html` normalizes to `/`, so only two URLs enter reporting. No arbitrary text or geographic coordinates. |

At most 400 accepted events per page instance; no network heartbeat. SDK fetch uses omitted credentials/no-referrer, with an abort signal that also blocks retries after opt-out. Previously delivered records are not erased by opting out.

## Coarse geography: account installation required

Install `scripts/posthog-coarse-geoip.hog` as a free custom transformation in **project 647943**. Disable the full GeoIP transformation, including legacy instances. Keep project-specific **discard client IP** enabled. No filters on the coarse transformation. It intentionally ignores `$geoip_disable` (which prevents built-in full enrichment) and adds only country, first region/state and approximate city to events. It does not add person setters or log IP/lookup data. Unknown lookup remains unknown; no country exclusion or geographic service.

Failure behavior: disabled/erroring custom transformation adds nothing. It cannot leak geographic coordinates because it never copies them into an event. Project IP discard is a separate ingestion control after transformations. This concerns stored analytics properties, not transport/security logs or internal queues. Owner attests IP discard enabled and DPA signed; actual project checks remain pending. Verify saved product/model-development opt-out before first event.

Mechanism verified against PostHog source commit `94dffaa4bfba0ab610c6ee03e447a58bedfbd299`: `nodejs/src/cdp/templates/_transformations/geoip/geoip.template.ts` honors `$geoip_disable`; `nodejs/src/cdp/hog-transformations/transformation-functions.ts` exposes `geoipLookup`. [Custom transformation documentation](https://posthog.com/docs/cdp/transformations/customizing-transformations) explains immutable event/copy/return semantics. Compiler and tenant behavior require account-side tests; local static code is not live evidence.

Before activation, authorize a bounded isolated synthetic check, exercise successful/missing/invalid lookup and disabled/erroring transformation, and inspect complete stored event JSON for IP/coordinates/person setters. Keep synthetic event names outside production report selections. Do not use real visitors as test data.

## Private owner dashboard recipe

Use free Trends and available Paths/SQL; no public sharing or paid lifecycle/group features. Always label counts as browsers, visits or clicks—not people, leads or completed calls.

1. **Traffic:** `$pageview` unique browsers by `source`, `device`, `$geoip_country_name`, `$geoip_subdivision_1_name`, `$geoip_city_name`; direct/unknown included. Separate acquisition-source report.
2. **Visits/returns:** count distinct `visit_id` over approved events; distinct browser IDs where `returning_browser=true`; separate `later_day_return=true`. Use selected weeks and US/Eastern timezone. Do not add pageview counts to infer repeat visits.
3. **Interest:** `photo_open` counts/unique browsers by `photo`; details/gallery opens; sum `engagement.active_ms` by subject/photo/section. Timing is a lower-bound estimate, not precise reading duration.
4. **Outbound intent:** `outbound_click` total and unique browsers by destination/placement. Clicking-browser rate = unique clicking browsers divided by unique browsers across approved events for the same period. Direct-to-contact is valid; do not require a photo/details funnel first.
5. **Observed paths:** use `$pageview`, photo/details/gallery opens and outbound events, not heatmap batches or engagement heartbeat-like paths. Paths show observed events only, not confirmed conversion or precise intent.

Approximate small city groups can still be identifying; they are not anonymous populations or individual dossiers. Owner accepts rolling one-year event retention on free plan and is responsible for stopping collection and deleting analytics after sale. No indefinite archive promised. Keep 1M/month analytics billing limit, no card/trial/paid toolbar; other product limits are separate. In-app heatmaps use two canonical URLs within free three-URL allowance.

## Verification and publication

- `npm test`: policy and runtime checks, including cross-page/day expiry, asynchronous Web Lock idle-click regression, hidden/idle timing, storage/SDK refusal and opt-out/GPC.
- `tests/analytics-browser.html`: real pinned SDK, local synthetic origin, intercepted fetch only. Exercises payload and heatmap sanitization plus trusted click and opt-out. **Never publish this fixture.**
- Existing Python and all ten PRODUCT browser regressions pass locally. Desktop/mobile privacy controls fit at 1440/390px with 44px button targets.
- Vendored SDK: `posthog-js@1.438.1`, npm `dist/module.no-external.js`, unchanged; SHA-256 `9399ae49eb33dd94d90cc71663770cae625b6aafca5b0d4491f0e70d602c8262`. MIT license retained. Upgrades require rerunning SDK payload/heatmap checks.
- `scripts/publish-files.txt` now lists exactly 155 buyer assets. Publish only this list, not repository root. Account/compiler/ingestion/dashboard/live URL verification remains separate from local checks.

Read-only GitHub inspection on 2026-10-06 found public `323colonial/323colonial.github.io`, legacy Pages source `main:/`, remote HEAD `658e4dccb716522b2529f13de76d21e701c0c7d6`. Its tree contains repository tooling/docs alongside buyer files. Do not push the development tree as a release. Choose and approve an isolated allowlist-only publication target; do not remove remote repository files or rewrite history as incidental cleanup.
