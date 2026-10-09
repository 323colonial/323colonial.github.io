# Buyer audit implementation

Issue: colonial-bjr. Date: 2026-10-09. Branch: main.

## Scope and sequence

1. Adapt `listing.css`: retain Georgia narrative and Arial utility after browser metric comparison; no fonts fetched. Remove mobile price flex growth, tighten numeric alignment width without shrinking type. Existing `tests/hero-layout.html` supplies red regression (320x640 147.83px >131). Use dark mahogany instead of Pewter Green for masthead/secondary dark roles; retain house-color fields and mark stain values as approximations. Assess coarse targets within sticky-height budget. Tests: layout, typography, audit, harden.
2. Profile `listing.js` scroll/layout geometry and style work in browser. Add focused browser regression before minimum measured correction. Preserve preload conditions and all of `seasonal-hero.js`, timing, nested blending, resize/focus behavior. Tests: rendering fixture, narrative-scroll, resize-reading, seasonal-runtime, crossfade-pixels.
3. Update `PRODUCT.md`, `DESIGN.md`, `.impeccable/design.json`, `.impeccable/surfaces/index-html.md`: 65 current photos with stable IDs, 36-second shared year, masthead dial/short-screen dock, evaluated fonts, corrected house palette. Preserve dated history and exact buyer prose/assets.
4. Bounded desktop/mobile polish and audit, detector once on changed UI; keyboard, fallback, print geometry and complete relevant browser regression. Local atomic task-owned commit only. No push/deployment.

## Verification

`node --test tests/*.test.mjs`; `python3 tests/test_listing.py`; `python3 test_design.py`; `python3 test_marketing_plans.py`. Browser fixtures served at verified local root http://127.0.0.1:8765. Evidence recorded in Bead and this artifact.

## Baseline / ownership

Fresh Node baseline: 35 pass, one unrelated tooling test fails importing removed `.pi/skills/impeccable/scripts/detector/design-system.mjs` during concurrent 4.5.2 upgrade. Python listing 16 pass; design and marketing pass. Extensive dirty `.pi/skills/impeccable/` files, `.beads.gate.lock`, `.claude/`, `MEMORY.md` predate work; never stage/revert these. Closeout may be blocked by unrelated tracked changes. Use current launcher, not removed modules.

Font comparison at 320px with 2.4em numeric alignment: Arial facts 147.83px before price-growth fix; system-ui also 147.83px with wider price (121.70px vs114.23px), Verdana wraps action group and totals174.16px. With price growth disabled and 2.4em numeric alignment, Arial fits 116.88px. Georgia preserves existing narrative voice and readable 18–23px role without network cost. No claim of universal platform font equivalence.

## Implementation and focused results

Completed in requested order: adapt, render optimization, current documentation, bounded polish. Only `layoutStories` changes production JavaScript. Batched reset/base geometry/caption/final-stage phases keep the original eligibility thresholds and reading-point restoration. `updatePhotos`, prefetch, privacy runtime, `seasonal-hero.js`, buyer HTML, gallery runtime, original/generated assets and frozen fixtures remain unchanged. No dependency or font download.

- Narrow facts: 320×640 falls from 147.83px to 116.88px (existing ceiling 131px); all ten hero-layout viewports pass without shrinking text.
- Rendering fixture: seven active stories; write-to-geometry barriers fall 21→3 at desktop/mobile. Ten warm rebuild medians were 5.30→4.70ms desktop and 7.90→6.70ms mobile. Barriers are instrumented read-after-write opportunities, not measured reflow count; desktop Chromium timings are advisory, not physical-phone/FPS evidence.
- Coarse target assessment: temporary 44px contact/details/photos targets at 320px raised masthead 129.09→149.09px and facts 116.88→131.19px. Prototype removed; existing 24px compact links meet the AA minimum but retain a comfort tradeoff. Dialog buttons remain 44px.
- Browser PASS: hero-layout, rendering-layout, narrative-scroll, resize-reading (32 assertions), media-layout, buyer-audit, buyer-typography, buyer-quality, gallery-viewer, listing-fallbacks, property-details, buyer-harden, print-layout (four cases). Pixel checker passed all 24 captures: desktop/mobile × three aspect-ratio pairs × seasonal off/on × forward/reverse, six pixel probes each; scroll endpoints also asserted by the fixture.
- Seasonal runtime: initial 86 PASS/1 FAIL at visible-tab resume. Test now logs one sampled phase without changing tolerance or runtime. Two subsequent runs pass 87/87, final phase 3.459250→3.459250. Initial failure is not claimed fixed or conclusively explained; no full endurance claim.
- Privacy fixture initially counted two 10-second callbacks: notice dismissal and seasonal `giveUp` loading hold. Browser diagnostics established the collision. Fixture now omits only the seasonal script when constructing its iframe; all 47 privacy assertions pass, with exactly one notice timer. No buyer runtime changes or weakened assertions. Seasonal integration remains covered separately.
- Bounded visual review: index and gallery at 1440×1000/390×844, zero overflow, house-led palette, unchanged copy and photo-led composition. Native Tab→Previous, Shift+Tab→Close, ArrowRight→Photo 2 of 65, Escape→first opener with visible 3px mahogany focus. No additional polish correction needed.

## Scoped audit and review

Informal scoped audit **17/20**: accessibility 3, performance 3, responsive 3, single-theme consistency 4, integrity 4. No verified P0/P1 buyer defect. Fixed narrow facts and stale authority; remaining P3 is compact-link touch comfort. Physical-device performance remains unverified. Full repository readiness is not implied by this score.

Updated Impeccable launcher context ran once; detector ran once on index/gallery/CSS. Four warnings: Arial in both HTML files/CSS and gallery Greek Villa classified as cream. Contextual disposition: Arial utility retained by measured font comparison, Georgia handles narrative/display; Greek Villa is the named house color, not a generic cream mandate. No old Arial/Pewter pins used. Detector exit 2 is advisory, not a clean-detector claim.

Subscription peer behavioral review: `.pi/reviews/colonial-bjr/layout-review.json`, empty findings, schema validation PASS. Parent reviewed complete owned diff, unchanged prefetch/runtime boundaries, fixture instrumentation and documentation consistency. Docs reflect 65 stable-ID photos, 36-second shared year, masthead dial/short dock, evaluated font roles and provisional stain approximations; historical finish specification remains separate.

## Evidence pointers and limits

Private browser evidence directory (may expire): `/Users/hays/.betterwright/artifacts/85b42e1702877c85/`.

- Narrow red/green: `pi-evidence-1791574043675-63cd55.png`, `pi-evidence-1791574157943-8aedb5.png`.
- Render red/green: `pi-evidence-1791574238000-debb09.png`, `pi-evidence-1791574279117-a6aaaa.png`.
- Resize: `pi-evidence-1791574303250-0c4d25.png`.
- Pixel manifests/capture paths: `browser-output-1791574822274-d96298.json`; 24/24 passed `tests/check_crossfade_pixels.py`.
- Print: `pi-evidence-1791574965227-1d65e5.png`.
- Desktop/mobile/focus: `pi-evidence-1791575088042-6721b2.png`, `pi-evidence-1791575130977-591763.png`, `pi-evidence-1791575165912-8bf2df.png`.
- Final seasonal/privacy: `pi-evidence-1791575272145-1edd30.png`, `pi-evidence-1791575350676-526d9b.png`.

Browser checklists audited ready. Final staged Node/Python gate and commit/closeout outcome are recorded in the Bead after execution. Baseline tooling import failure and unrelated tracked Impeccable upgrade prevent claiming repository release readiness until reconciled by their owner. Read-only `agnt doctor --json` reports no failures, one verification-prerequisite warning (pytest/check-pi-config); no environment repairs attempted.

Not checked: physical touch devices, native browser zoom, screen-reader operation, PDF pagination, full seasonal endurance or production. No push or deployment. No unrelated upgrade/user file staged, reverted or deleted.
