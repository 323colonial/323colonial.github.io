# Buyer analytics

Bead: `colonial-zoc.2`. Published on 2026-10-06 under approval `colonial-61i`; private dashboard accepted from owner-supplied saved definitions and execution results. Account evidence is owner-assisted, not a direct authenticated agent inspection. Publication and verification details below.

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

### Timed notice dismissal (colonial-6ma)

The notice is informational, not a consent prompt. Shared `listing.js` dismisses it after **10 uninterrupted seconds in a visible tab**, as requested by the owner. Returning from a hidden tab starts a fresh interval. Focusing or hovering the notice cancels dismissal for that page, including during animation. The native **Privacy and opt-out** disclosure before the dated footer remains available without a timeout or JavaScript. Dismissal never enables tracking, opts in, opts out, or changes GPC/DNT handling.

While the notice is onscreen, a **240ms fade-and-height collapse** reclaims the entire notice slot (32px desktop, about 53px at 390px width with default text). No blank spacer remains. Offscreen notices collapse immediately with scroll compensation to preserve reading position; reduced motion and unavailable Web Animations also skip animation. Wheel, touch-scroll or keyboard input during an active animation cancels it. No manual close button or extra dependency is needed.

`colonial_notice_dismissed=1` is a separate, host-only presentation cookie: **30 days from dismissal**, `Path=/`, `SameSite=Lax`, and `Secure` on HTTPS. Root path covers both buyer pages; there is no Domain attribute, identifier or analytics payload. Repeat visits do not renew it. Missing/expired flags show the notice again. Denied cookie reads leave it visible; failed writes restore it after animation. Without JavaScript the notice and disclosure remain visible. This change preserves the existing analytics policy; it is not a legal determination that notice-only analytics is sufficient in every jurisdiction.

The header’s Questions & tours link goes to the public Dandridge listing and uses existing `other-external` / `header` categories. This measures outbound intent, not an inquiry or confirmed tour.

At most 400 accepted events per page instance; no network heartbeat. SDK fetch uses omitted credentials/no-referrer, with an abort signal that also blocks retries after opt-out. Previously delivered records are not erased by opting out.

## Coarse geography: account configuration

The owner confirms `scripts/posthog-coarse-geoip.hog` is enabled as a free custom transformation in **project 647943**, full GeoIP is disabled, and project-specific **discard client IP** is enabled. Preserve these settings. No filters on the coarse transformation. It intentionally ignores `$geoip_disable` (which prevents built-in full enrichment) and adds only country, first region/state and approximate city to events. It does not add person setters or log IP/lookup data. Unknown lookup remains unknown; no country exclusion or geographic service.

Failure behavior: disabled/erroring custom transformation adds nothing. It cannot leak geographic coordinates because it never copies them into an event. Project IP discard is a separate ingestion control after transformations. This concerns stored analytics properties, not transport/security logs or internal queues. Owner attests DPA signed and saved product/model-development opt-out. A successful tenant preview and one stored synthetic event were inspected through owner-supplied screenshots: five coarse fields, no non-null raw IP, geographic coordinates or person setters. This does not establish provider transport/log retention.

Mechanism verified against PostHog source commit `94dffaa4bfba0ab610c6ee03e447a58bedfbd299`: `nodejs/src/cdp/templates/_transformations/geoip/geoip.template.ts` honors `$geoip_disable`; `nodejs/src/cdp/hog-transformations/transformation-functions.ts` exposes `geoipLookup`. [Custom transformation documentation](https://posthog.com/docs/cdp/transformations/customizing-transformations) explains immutable event/copy/return semantics. The tenant preview successfully executed `geoipLookup` despite an editor diagnostic saying it was unimplemented; runtime success supersedes that diagnostic.

One authorized synthetic event, `colonial_zoc2_geo_test`, was ingested and its expanded stored non-null properties inspected. Missing/invalid lookup and disabled/erroring transformation were not exercised in the tenant; failure behavior above is based on the transformation's explicit field allowlist and independent IP-discard setting, not live fault-injection evidence. Do not disable privacy controls on the live project to test them. Keep any future authorized synthetic event names outside production report selections; do not use real visitors as test data.

## Private owner dashboard recipe

Use free Trends and available Paths/SQL; no public sharing or paid lifecycle/group features. Always label counts as browsers, visits or clicks—not people, leads or completed calls.

1. **Traffic:** `$pageview` unique browsers by `source`, `device`, `$geoip_country_name`, `$geoip_subdivision_1_name`, `$geoip_city_name`; direct/unknown included. Separate acquisition-source report.
2. **Visits/returns:** count distinct `visit_id` over approved events; distinct browser IDs where `returning_browser=true`; separate `later_day_return=true`. Use selected weeks and US/Eastern timezone. Do not add pageview counts to infer repeat visits.
3. **Interest:** `photo_open` counts/unique browsers by `photo`; details/gallery opens; sum `engagement.active_ms` by subject/photo/section. Timing is a lower-bound estimate, not precise reading duration.
4. **Outbound intent:** `outbound_click` total and unique browsers by destination/placement. Clicking-browser rate = unique clicking browsers divided by unique browsers across approved events for the same period. Direct-to-contact is valid; do not require a photo/details funnel first.
5. **Observed paths:** use `$pageview`, photo/details/gallery opens and outbound events, not heatmap batches or engagement heartbeat-like paths. Paths show observed events only, not confirmed conversion or precise intent.

Approximate small city groups can still be identifying; they are not anonymous populations or individual dossiers. Owner accepts rolling one-year event retention on free plan and is responsible for stopping collection and deleting analytics after sale. No indefinite archive promised. Keep 1M/month analytics billing limit, no card/trial/paid toolbar; other product limits are separate. In-app heatmaps use two canonical URLs within free three-URL allowance.

## Accepted private dashboard

US Cloud project **647943**, dashboard **2178189**, **323 Colonial --- buyer activity**; account-relative path `/dashboard/2178189`. Owner confirms public sharing **OFF**. On 2026-10-06 the owner supplied all saved SQL/Paths definitions and relayed successful execution of all 11 insights, including the four updated segment/Paths queries. The agent reviewed those definitions against `analytics-core.mjs`; it did not run authenticated account queries itself.

| Insight ID | Report |
| --- | --- |
| `6cuo5m5Amtbi` | Daily distinct browsers and distinct `visit_id` values |
| `8BC5drfKQNIK` | Returning & Later-Day: distinct returning/later-day **browsers**, not visit totals |
| `dbiBoaww90My` | Distinct outbound clickers / all distinct browsers; zero denominator produces null |
| `vQQAIQhfrbY1` | Photo-open totals by photo |
| `SkdROn8X3CDr` | Active seconds for `engagement`, `subject = 'photo'`, photo 1–73 only |
| `zMJK7Of2Q_rd` | Separate opens and active-seconds columns by event/subject category |
| `CGJPShQKJxWX` | Current × acquisition source; browsers, returning/later-day browsers, photo/details/gallery openers and outbound clickers |
| `GejcqX1IaHty` | Same browser/return/exploration measures by device |
| `1z6qPf0JCzO_` | Browsers and returning/later-day browsers by country, state and approximate city |
| `fuaidnt9JpFb` | Click totals and distinct clickers by destination × placement |
| `BNPoQAx9` | Native Paths: pageviews/custom events, five steps, at most 50 edges |

SQL uses a rolling 28-day window and explicit event selections, excluding `^colonial_zoc2_`. Daily SQL buckets explicitly use `America/New_York`; the owner-reported project timezone is US/Eastern for native Paths. The first day may be partial. A visit spanning midnight appears on both active days; daily/grouped distinct counts must not be summed into period-wide unique counts. Source/geography groups can overlap. Exploration columns count independently: they are not a required or ordered conversion funnel.

Paths excludes `engagement`, `$pageleave`, `colonial_zoc2_geo_test` and `$$heatmap` by exact name. The ineffective `properties.event` filter was removed. This covers the only synthetic event sent for this task; add any future test-event names before use rather than assuming wildcard coverage. `filterTestAccounts` is false; this is explicit event exclusion, not a global test-account filter.

Photo reports executed successfully but had no matching rows. Opens/engagement returned gallery-open count 1, story 11.2 seconds and gallery 173.9 seconds; these are dated observations, not fixed expected totals. Gallery opens and gallery attention occupy separate categories. Earlier AI-memory flags describing query failures or a blank tile are stale. No title-capitalization change is required for acceptance.

## Verification and publication

- `npm test`: policy and runtime checks, including cross-page/day expiry, asynchronous Web Lock idle-click regression, hidden/idle timing, storage/SDK refusal and opt-out/GPC.
- Serve locally and open `tests/privacy-notice.html`: both buyer pages at desktop/mobile widths, controlled 10-second timer, collapse geometry, 30-day flag/no renewal, missing/blocked storage, focus/hover, hidden tabs, animation cancellation, reduced motion, no-JS and persistent opt-out. Cookie/clock boundaries are deterministic doubles; verify native cookie expiry and real elapsed animation separately in the browser. Never publish this fixture.
- `tests/analytics-browser.html`: real pinned SDK, local synthetic origin, intercepted fetch only. Exercises payload and heatmap sanitization plus trusted click and opt-out. **Never publish this fixture.**
- Existing Python and all ten PRODUCT browser regressions pass locally. Desktop/mobile privacy controls fit at 1440/390px with 44px button targets.
- Vendored SDK: `posthog-js@1.438.1`, npm `dist/module.no-external.js`, unchanged; SHA-256 `9399ae49eb33dd94d90cc71663770cae625b6aafca5b0d4491f0e70d602c8262`. MIT license retained. Upgrades require rerunning SDK payload/heatmap checks.
- `scripts/publish-files.txt` lists exactly 155 buyer assets. Publish only this list, not repository root. These developer docs and tests are not publication assets.

Approval `colonial-61i` authorized one isolated publication from source `7fc464721ad02c7d107b0ed36f075c21dadce216`. Release `3ae1738eb61a30cd29fd43035a0c4116cedb84d8` contains only those 155 files, on `323colonial/323colonial.github.io` branch `gh-pages`; Pages source was changed to `gh-pages:/`. Remote `main` and history were left unchanged. The build completed and all 155 live paths returned HTTP 200 with bytes matching the source; sorted path/content-SHA256 aggregate: `2f77b25e55cfe0b775d4d33be5557be6135726d39c8c1501211ca9190a79ea8d`. All three modules had JavaScript MIME types; sampled tooling/private-source paths returned 404. Repository history remains public: Pages exclusion is not repository-history deletion.

Recorded live checks covered photo/details/gallery dialogs, Escape, the 73-photo gallery, mobile overflow, image decode and saved analytics opt-out. Evidence combines offline real-SDK payload tests, independent stored synthetic ingestion and exact deployed bytes; it is not a captured production SDK-to-stored-event journey. No additional live test events were sent after the single coarse-GeoIP check. Future publication or privacy-control changes require their own applicable authority; this closeout does not authorize another deployment.
