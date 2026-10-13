# iPad seasonal halt investigation · colonial-tyl

## Result

**Reported iPad halt remains unreproduced; root cause unknown.** Owner confirmed the device was unavailable for this investigation. Local Chromium tests reproduce intentional stops and recovery, not the reported hardware incident. No runtime, asset, timing, accessibility, dependency, publication or deployment change is included.

Investigated on 13 October 2026 against source revision `d9d7ea9ef0f119aa6e6beeac2549ebbd002c1e03`, after closed colonial-6nu. That work replaced imagery without changing seasonal/visitor runtime. Its Bead recorded an intermittent fixture phase/initialization failure followed by a passing recheck; this investigation's fresh baseline passed without retry. Neither result establishes an iPad cause.

### Missing incident facts

All remain unknown: iPad model, iPadOS/browser version, exact URL and served release, normal versus `?display=visitor` mode, elapsed time before halt, network/cache conditions, screen-lock/background/navigation events, visible Pause/Resume label, whether the seasonal dial and photo identities also stopped, and whether Resume recovered. Do not assume current local source matches the page seen on the iPad. `PRODUCT.md` records publication gaps; this work did not inspect or deploy the live site.

## Stop classification from current source

| Visible state | Current mechanism | Expected next action |
| --- | --- | --- |
| Pause label, frozen dial briefly | Missing required frame holds shared boundary for up to 10 seconds; `seasonal-hero.js` `sync`, `hold`, `giveUp` | Frame readiness resumes motion; exhausted retries/hold becomes a stall. |
| Resume plus “Seasonal photos did not load. Resume to retry.” in description/title | Shared seasonal stall: failed load/decode, or unresolved request/decode; two retries after initial failure | Resume abandons pending load/decode identities and retries. A completed required pair or removal of blocking participant can also lift stall; `online` retries. |
| Resume without seasonal failure description | User pause, restored normal-mode session preference, reduced motion turned off, or visitor load/prepare failure | Explicit Resume. Visitor failures do not currently expose a distinct reason in the seasonal description. |
| Pause label while no seasonal image participates | Offscreen/hidden story photos are not live participants | Return to a participating photo. No layers or running clock when none participate. |
| Hidden tab, open dialog, print | Lifecycle gates freeze clock and suppress new scheduled seasonal loads; existing requests may settle | Return/close/leave print. These are not stored user pauses. |
| Static originals, no seasonal control | Reduced motion, save-data at startup, unsupported Web Animations, missing manifest in normal mode, or no JavaScript | Expected fallback. A missing visitor manifest instead keeps original-photo rotation and its pause control. |
| Visitor triptych stops changing identity | Shared seasonal hold/pause, visitor pause/failure, offscreen hero, lifecycle cancellation, or an unfinished slide | Identify whether seasons/dial still advance before attributing cause. |

Normal-mode preference uses `sessionStorage.colonial_seasons_paused`; it remembers pause, not phase. Visitor mode ignores that preference. A visitor `focusin` on the hero also explicitly pauses, though visitor panes are intentionally inert/noninteractive.

The current manifest has 18 two-second segments (36-second year); absent `hold_seconds` uses the runtime's 10-second default. Visitor identity changes dwell eight seconds, then load/decode the incoming original and prepare its seasonal pair before sliding. Original load and seasonal preparation each have a 10-second bound: these are separate stages, not a single end-to-end 10-second budget.

### Relevant boundaries

- `seasonal-hero.js`: `load`/`decode` track pending identities; `schedule` bounds requests and decoded windows; `sync` is the shared readiness/lifecycle barrier; `boundary` advances one segment and drops stale carry after ≥100ms lateness; `retry` detaches unresolved work. Visibility and `pageshow` invoke `sync`.
- `visitor-display.js`: `change` catches load/prepare/movement failure and pauses; `cancel` invalidates pending work and rolls back movement; `schedule` waits a fresh interval after lifecycle cancellation. `slide` awaits all `Animation.finished` promises without a separate deadline. That last point is an investigation seam, not evidence that Safari leaves them unsettled.
- `tests/seasonal-runtime.test.mjs`, `tests/seasonal-runtime.html`, `tests/visitor-display.test.mjs`, `tests/visitor-browser.spec.mjs`: existing unit, injected-failure, lifecycle and browser coverage. `tests/buyer-browser.spec.mjs` runs the HTML fixture; `playwright.config.mjs` selects Chromium.
- `PRODUCT.md`, `DESIGN.md` define timing/fallback contracts. `PRODUCT.md` and `docs/buyer-accessibility.md` record physical iPad/Safari, OS backgrounding and device-memory coverage gaps.

No fix is warranted by an unobserved promise or generic suspicion of memory pressure. Do not add a periodic reload, auto-Resume, second clock, unbounded prefetch, or longer timeout without reproducing the relevant failure and separately bounding implementation.

## Fresh fixture evidence

Environment: Darwin arm64, Node v24.21.0, installed Playwright 1.64.0, local HTTP server bound to `127.0.0.1:18765`. No installs or external photo processing. Exact logs live under `.pi/artifacts/colonial-tyl/`.

```sh
node --test tests/seasonal-runtime.test.mjs tests/visitor-display.test.mjs
npx playwright test tests/visitor-browser.spec.mjs tests/buyer-browser.spec.mjs --grep 'seasonal-runtime|visitor|rotation|incoming|pending|failed|initial|reduced|seasonal|pause|movement|in-flight|unsupported|real-time|expanded'
```

- `node.log`: **8/8 PASS**, including replacing unresolved decode without double-releasing network slots, ignoring late decode results, visible-frame priority and 600 deterministic visitor transitions.
- `browser-baseline.log`: **40/40 PASS in 2.8 minutes**, first run: seasonal HTML fixture plus all 39 visitor tests.
- HTML fixture: 7.2-second synthetic year; both photo-pair runs sampled all 18 segments and wrap, 541 samples each, zero stopped samples/dial misses. Real-image scroll covered 53/53 seasonal photos at 76 stops. Injected hanging request, unresolved decode and rejected decode produced bounded stalls; Resume recovered. Late abandoned decode did not replace recovered layers; failed decode tried three times without retry storm.
- Visitor suite: 99-transition pool coverage, three viewport geometries, pending original/seasonal failure and timeout, explicit pause, hidden/dialog/print/page-exit cancellation, rollback, missing manifest and reduced-motion/save-data fallbacks passed.
- Most visitor tests install virtual timers, while Web Animations use real document timeline time. This is useful deterministic logic coverage, not hours of wall-clock playback. The HTML fixture shortens timings and replaces browser media/network behavior in selected cases. Synthetic visibility/page events do not replicate iPadOS suspension or process eviction.

### Unmodified real-time playback sample

In the persistent desktop browser (Chrome/153.0.0.0 user agent, macOS, 864×749 CSS viewport), opened `http://127.0.0.1:18765/` and `http://127.0.0.1:18765/?display=visitor`. No virtual clock, injected failure, scrolling or lifecycle event. Both tabs reported `document.hidden=false` throughout sampling; tab selection here did not simulate real backgrounding.

Read existing clock/DOM state once per second for 180 seconds per mode, starting at 08:13:14.523Z and 08:13:19.747Z respectively. Each produced 181 samples, all 18 segments, five phase wraps, Pause throughout, and zero sampled holds/stalls/non-running states. Normal mode had at most two seasonal image layers; visitor mode had at most eight, including incoming panes, and 39 distinct sampled DOM identity lists (including transitional four-pane lists, **not** 39 completed transitions). These counts are not decoded-memory or heap measurements; visitor photo-ID keys can collide with narrative records in the existing `decoded` diagnostic map.

Saved sampler source, raw rows and summaries: `.pi/artifacts/colonial-tyl/soak.json` (browser evidence wrapper, data under `result`). Assert-based extraction checked sample count, duration, segment coverage, wraps and running state. Initial extraction treated the host's text trust wrapper as plain JSON and failed before validation; corrected wrapper parsing passed. Proof images: `normal-proof.png`, `visitor-proof.png`; checklist: `browser-evidence.json`. Screenshots corroborate rendered states, not continuous playback. One-second sampling can miss short holds; three minutes cannot exclude longer intermittent failures. Local fast/cache-assisted delivery is not the incident network.

## Ranked next tests, not diagnosed causes

Ranking is by investigation value and fit to existing mechanisms, not measured probability.

1. **A bounded load/decode stop mistaken for an unexplained halt.** Known reproducible mechanism, especially when visitor mode reaches a new photo. At the incident, capture label, accessible description, `seasonalClock.state()`, failed/pending request URLs and timings, plus `visitorDisplay.paused`. Seasonal `stalled=true` distinguishes the shared barrier; visitor `paused=true` with seasonal `stalled=false` points to visitor failure or explicit pause, not uniquely to network failure.
2. **Lifecycle or preference stop.** Correlate visibility, pagehide/pageshow, lock/unlock, print/dialog, reduced-motion state and exact viewport position. Existing synthetic recovery passes. A real foreground page that remains stopped after gates clear needs its own Safari reproduction, not a generic “background tabs pause” explanation.
3. **Browser clock/animation stall or device resource pressure.** If label stays Pause, gates are clear and no load failure exists, compare two clock snapshots and displayed layers. `running=true` with phase pinned at segment end suggests a timer/timeline problem; advancing phase with frozen image suggests rendering/bitmap behavior. Only visitor identities frozen, especially with `.visitor-panes[data-slide]`, warrants inspecting pending `Animation.finished`. No evidence here establishes a Safari bug, leak, memory limit, or accumulating retained bitmaps.

## Smallest next action on the actual iPad

1. Record missing device facts and exact URL/release before testing. Start with the reported mode and original conditions; do not change several settings at once.
2. Keep page foreground for the reported interval; if unknown, start with 15 minutes and record the limit. Record foreground/lock/network transitions and time to halt. Repeat the other mode only as a separate comparison.
3. At halt, capture the visible image, dial and Pause/Resume control **before touching Resume**. Note whether identity rotation, seasonal dissolve, or both stopped. With Safari remote inspection available, save this read-only snapshot twice several seconds apart, plus console/network errors:

   ```js
   ({
     url: location.href,
     time: performance.now(),
     timeline: document.timeline.currentTime,
     visibility: document.visibilityState,
     reduced: matchMedia('(prefers-reduced-motion: reduce)').matches,
     print: matchMedia('print').matches,
     saveData: navigator.connection?.saveData,
     dialog: Boolean(document.querySelector('dialog[open]')),
     clock: window.seasonalClock?.state(),
     visitor: window.visitorDisplay && {
       ready: visitorDisplay.ready,
       paused: visitorDisplay.paused,
       active: visitorDisplay.active
     },
     label: document.querySelector('#hero-motion')?.textContent.trim(),
     description: document.querySelector('#hero-motion')?.getAttribute('aria-description'),
     slide: document.querySelector('.visitor-panes')?.dataset.slide,
     hero: document.querySelector('.hero-photo')?.getBoundingClientRect().toJSON()
   })
   ```

4. Tap Resume once if offered; record recovery, latency and any new failed request. If label says Pause, record that first: first tap pauses intentionally and is not a retry. Record results of subsequent explicit Resume separately. Avoid reload until pre-recovery evidence is saved.
5. Open a separately bounded implementation Bead only when evidence identifies the failing path. Keep shared clock, bounded decode/load, original-photo fallback and accessibility behavior intact.

**Coverage limit:** local short-duration Chromium and injected faults cannot clear an intermittent iPad Safari incident. Device evidence remains required; investigation completion is not bug resolution or showing-readiness certification.
