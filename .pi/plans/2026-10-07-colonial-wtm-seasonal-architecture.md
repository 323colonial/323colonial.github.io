# colonial-wtm: synchronized seasonal hero and narrative architecture

## Decision and scope

Evaluation reconciled with delivered implementation on 8 October 2026. This document replaces the earlier draft; Git history retains its estimates and alternatives. The owner requested completion of this evaluation. It records the architecture and already-recorded owner decisions, not a new asset-quality acceptance, performance certification or deployment approval.

Use one shared annual clock for the hero and scroll-sequenced narrative photographs, sparse per-photo keys, and two seasonal image layers above each untouched original. Keep the native scroll controller, static-site progressive enhancement, original-photo galleries and existing analytics semantics. No framework, backend or new dependency.

Authoritative implementation references:

- `seasonal-hero.js`: clock, frame scheduler, two-layer compositing, readiness and lifecycle.
- `assets/seasons-next/frames.json`: delivered timing and per-photo keys.
- `PRODUCT.md` and `DESIGN.md`: current buyer behavior and design constraints.
- `colonial-gz0`, closed at `fd16042`: implementation and integration ownership.
- `colonial-rp8`, closed at `a01f4a2`: catalog pruning, separate from this evaluation.
- `colonial-y9y`, closed at `c4d3ee2`: outer scroll-compositing correction. The original evaluation incorrectly treated that inherited blend as exact.
- `colonial-66v`: asset production, provenance, registration and final asset acceptance. Closing this evaluation does not close its remaining defects or QA gaps.

`graphify-out/graph.json` is absent. References above were checked against source. This closeout changes documentation and ticket state only: no runtime, gallery, original image, analytics, allowlist, push or deployment changes.

## Settled changes from the original brief

| Earlier proposal | Owner decision / delivered contract |
| --- | --- |
| Approximately 24 generated frames per changing photo | Sparse 18/12/9/6/5/4-key sequences, plus original-only photos; exact map in `frames.json` |
| 60-second proposal, then 24-second draft | 36-second year, 18 consecutive 2-second segments |
| Four manual season buttons and blend status | One footer Pause/Resume animation button; no manual season buttons or season label |
| Preserve all 73 catalog entries | 65 retained stable IDs after separately approved pruning; no renumbering |
| Producer/consumer contract still awaiting implementation | Producer `3503fd9`, small-tier export and consumer integration `fd16042` share the delivered contract below |
| Future private integration ticket | `colonial-gz0` already delivered; do not reopen implementation here |

The producer/consumer integration is evidence of a working contract, not retrospective proof that every original staged approval gate or visual-quality criterion was satisfied. The pilot records the actual owner reviews in `.pi/plans/2026-10-07-colonial-66v-pilot.md`.

## Shared timing

The coordinate grid has 12 seasonal steps. Knots are:

```text
0, 1, 2, 3, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 11, 12
```

The last 12 is the wrap endpoint, equivalent to 0. Every adjacent knot pair takes 2 seconds, so the year takes 36 seconds. Initial coordinate is 0. Anchors are late summer 0, fall 3, winter 6 and spring 9. Their elapsed times are 0, 6, 16 and 28 seconds: they are **not** equal quarters of elapsed time.

For segment `i`, elapsed time `t` and duration `D[i]`, the grid coordinate is:

```text
q = knots[i] + (knots[i + 1] - knots[i]) * t / D[i]
normalized phase = q / 12
```

A sparse photo dissolves between its own neighboring keys, using distance along this grid including wrap. Its fade rate therefore changes at half-step boundaries, in sync with every other photo. The previous uniform `elapsed / 2s` step formula was wrong for half steps.

There are no intentional holds. Readiness, user pause and lifecycle suspension can extend wall-clock time. Finite Web Animations share one `document.timeline` start time per segment. JavaScript handles boundaries, not every animation frame. Pause freezes the current blend; Resume continues from it, without claiming a single named season.

## Rendering and scroll composition

The untouched original `<img>` stays first inside its original-photo link, in flow and opaque. It defines geometry, responsive sizing and fallback. The runtime appends an absolute `.season-stack` containing:

1. Next seasonal key underneath at full opacity.
2. Current key above it, fading out linearly.

Ordinary source-over yields `(1-s)A + sB` with full coverage. Giving both layers complementary partial opacity would expose the background and is not used. A visible new stack joins over the original with a 600 ms fade; an offscreen join needs no visible fade. Removing the stack restores the original.

Seasonal composition and photo-identity composition are separate. `listing.js` controls native scroll progress, figure visibility, captions and interaction. Following `colonial-y9y`, complementary link opacities use `plus-lighter` inside an isolated transparent photo group; the seasonal stack remains source-over inside each isolated link. Unequal contain-fit edges fade to the surrounding section color. Existing focus behavior, final-photo viewing step and caption ownership remain intact.

Each seasonal export must match its original derivative's exact dimensions at the same tier. This is a contract, not a claim that all exports currently conform: photo 02's large keys 03, 06 and 09 remain 1280×852 against original 1280×851 at this evaluation closeout. Repair and regression belong to `colonial-66v`.

## Readiness and bounded scheduling

Participants are viewport-intersecting, non-hidden photos with loaded originals, either the hero or inside an enabled `.story.is-scrolling`. Inline fallback stories and original galleries do not participate.

- At a boundary, participating photos advance together only when required frames are decoded. Existing stacks retain the held shared phase; an unready entrant shows its original, never a wrong seasonal frame or blank box.
- A ready entrant may join an already-running segment at the shared start time. An unready entrant joins when its required pair becomes available; a boundary can hold everyone while waiting.
- Readiness waits default to 10 seconds. Load/decode failures receive at most two automatic retries. Exhaustion or timeout stalls motion and exposes Resume with an accessible loading-failure description. Gallery access and scrolling remain usable.
- Resume and the `online` event reset failed loads; Resume also abandons hung loading requests so they cannot occupy slots indefinitely (`194567a`). Late abandoned arrivals must not attach. A missing/invalid JSON response leaves originals and hidden controls.
- Frame requests prioritize visible photos and upcoming time boundaries, then nearby photos in scroll direction. No whole year is fetched just because a photo exists.
- Throughput samples use Resource Timing, excluding cache/revalidation-only and tiny-body samples. Default temporal reach is one segment; measured rates below 0.5 Mbps stop speculative reach, below 4 Mbps retain one, and faster links allow two. Spatial lookahead is one photo farther than temporal reach when prefetch is enabled. Concurrent load limit is 2 on links below 1.5 Mbps, 4 at or above 4 Mbps, otherwise 3.
- Small tier is selected at viewport widths up to 800px, measured throughput below 1.5 Mbps, or when the original selected its small source. Selection is evaluated on loads, not a promise of immediate replacement of already-ready frames after resize.
- The decoded window targets the current pair plus next key for visible photos and the nearest lookahead photo. Farther prefetch can retain compressed image resources. Removing references lets the browser reclaim decoded bitmaps; it does not prove actual GPU or process-memory residency.

## Lifecycle, accessibility and originals

| State/event | Contract / implementation behavior |
| --- | --- |
| No seasonal photo visible | Logical clock rests; seasonal stacks removed from departed photos |
| Hidden tab, print or any open dialog | Clock freezes; scheduler starts no new requests (already-started transfers may settle) |
| Return from tab/dialog | Resume held phase when ready unless user-paused; no elapsed wall-time catch-up |
| Reduced motion | Originals; remove stacks immediately; disabling preference later does not autoplay |
| No JavaScript or save-data at initialization | Originals; no seasonal enhancement requests |
| Print | Original images and exact captions; seasonal stacks hidden |
| Ordinary fresh navigation | Start phase 0; retain only paused preference in `sessionStorage` |
| bfcache/pageshow | Reconcile retained clock/visibility; no cross-tab or cross-visitor synchronization |
| Resize / sequencing fallback | Re-evaluate participation; inline stories show originals; subsequent loads choose applicable tier |
| Failed manifest fetch/JSON parse | Originals remain; controls stay hidden |

Pause/Resume retains the existing accessible footer control. Seasonal image layers have empty alt text, ignore pointer interaction and introduce no focus target. Animated links describe themselves as seasonal concepts opening originals. Storage failure degrades to an in-page preference, not a broken page.

Both catalog forms, `gallery.html`, viewer entry from any photo, adjacent previews and full-size/direct links use unchanged `assets/listing/` originals. Neither gallery loads seasonal buffers or joins the clock. No new seasonal analytics events.

## Delivered asset/runtime contract

Owner: `colonial-wtm` records the contract; `colonial-66v` produces and checks exports; the closed `colonial-gz0` consumes them. Runtime deliberately does not carry private QA/provenance records.

- Stable ID: original catalog position, also used in `data-position` and `gallery.html#photo-N`.
- Manifest: `assets/seasons-next/frames.json`, version 1, `steps: 12`, the knot array above, `seconds_per_segment: 2`, `tiers: ["large", "small"]`, and `photos` keyed by ID.
- Photo entry: ordered `keys` on the knot grid, with `original` listing keys served from unchanged listing derivatives. Example: photo 55 is `{"keys":[0],"original":[0]}` and is skipped by enhancement. Actual animated entries, including photo 73's sparse exceptions, come from the manifest rather than a fixed count inferred from room type.
- Generated paths: `NN/KK.webp` for large, `NN/KK-small.webp` for small, relative to the manifest. Half-step 4.5 is `04h.webp` / `04h-small.webp`. There is no `-large` suffix.
- Originals: `assets/listing/NN.webp` / `NN-small.webp`; not copied into the seasonal tree. Do not rebalance gallery originals.
- Dimensions/crop: exact corresponding original derivative dimensions, no invented field of view. Small tier is 720w; large tier retains per-photo original size. WebP exports use existing ImageMagick tooling; no new format or dependency.
- Byte counts, source hashes, model/prompts, registration and review dispositions belong to asset QA records and private working files, not the delivery manifest. Scripts reside in `scripts/seasons/`; small export builder is `scripts/build-seasons-small.mjs`. Private working masters remain under `.pi/artifacts/seasons-pilot/`.
- Manifest membership and successful decoding do not certify property fidelity. Unapproved/failed assets require explicit repair, hold or owner disposition under `colonial-66v`; this evaluation does not silently waive them.

Treatments for all historical 73 IDs are explicit below. Runtime encodes animated/original-only keys and omits other treatments instead of adding unused metadata fields.

| Treatment | IDs |
| --- | --- |
| Animated hero/narrative (53) | 1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 16, 17, 18, 21, 22, 23, 25, 26, 27, 28, 29, 30, 34, 35, 36, 37, 38, 39, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 57, 58, 59, 60, 61, 64, 65, 66, 67, 73 |
| Original-only / seasonally invariant (3) | 7, 55, 56; only 55 needs an explicit one-key manifest entry |
| Gallery/context-link-only photographs (8) | 8, 9, 15, 19, 20, 24, 32, 33 |
| Non-photo (1) | 31, conceptual basement plan; unchanged factual disclosure |
| Pruned from buyer catalog (8) | 40, 62, 63, 68, 69, 70, 71, 72; owned by `colonial-rp8` |

## Budgets, measured exports and limits

Measured at evaluation closeout, before photo-02 repair:

| Measure | Value |
| --- | --- |
| Manifest entries | 54: 53 changing + original-only 55 |
| Key-count distribution | 7×18, 14×12, 1×9, 10×6, 2×5, 19×4, 1×1 |
| Generated exports | 405 large + 405 small |
| Large bytes / largest frame | 104,536,390 / 530,288 |
| Small bytes / largest frame | 30,121,046 / 138,142 |
| Combined generated bytes | 134,657,436 (134.66 MB decimal); excludes originals and manifest |

These are asset totals, not bytes transferred in a normal visit. A full read's transfer depends on dwell, direction, cache, tier and readiness. One worst-size small frame every 2 seconds costs about 0.55 Mbps; large about 2.12 Mbps. Two simultaneously changing photos can double those rates. Sparse keys lower demand, not necessarily enough to avoid slow-network holds.

The original **proposed, unaccepted performance targets** were: 120 KB small (150 KB hero), 350 KB large (420 KB hero), 300 MB seasonal tree, 9 live decoded frames and 4 seasonal image layers under a two-photo viewport assumption; fast-4G holds ≤100 ms, boundary work <8 ms and scroll p95 within 10% of baseline. Actual exports fit the tree target but exceed some per-frame proposals. No claim that every cap passed or that this closeout approves deviations. Asset byte/quality trade-offs belong to `colonial-66v`; runtime performance certification requires measured target-device evidence before relying on these goals as release gates.

For planning, 9 RGBA frames at 720×479 consume about 12.4 MB; at 1280×852, 39.3 MB; at 1600×1046, 60.3 MB, before surfaces and browser overhead. At two simultaneous photos, two seasonal layers each gives four layers, plus possible stack join animations. These are scenario estimates, not universal limits for unusually tall viewports or proof of hardware memory use.

Verification profiles proposed: 390px DPR-3 phones with 3–4 GB RAM on 1.6/9 Mbps links, and 1440×900 DPR-2 desktop. Real-device memory, GPU, transfer-per-dwell and p95 timings have not been rerun/certified by this evaluation.

## Alternatives retained

- **All-frame CSS animation stacks:** rejected; original 12-frame hero held roughly 52 MB of decoded pixels before surfaces, multiplied across narrative photos. Separate independent clocks and unbounded eager fetching are wrong here.
- **Video:** shared exact boundary readiness and multiple mobile decoders complicate synchronization. Earlier local ffmpeg comparison of the old 12-frame/24-second hero found 4.1 MB WebP stills versus 5.4–10.1 MB video at 1280px. This is historical evidence for that sequence, not a fresh benchmark of the new set.
- **Canvas/WebGL:** no demonstrated gain worth reimplementing responsive image layout, links and print/fallback behavior.
- **Animated image / CSS-only loop:** lacks the shared decode barrier and controllable phase required here.
- **Contact-sheet sprite:** decodes/loads the whole year before use; does not solve mobile memory.

Sparse stills with browser dissolves remain the smallest complete design for the accepted requirements. The discarded batch-price and generation-count estimates are in Git history; they are not current billing authority.

## Touchpoints and ownership

`seasonal-hero.js`, `index.html`, `.season-stack` rules in `listing.css`, `scripts/build-seasons-small.mjs`, `scripts/publish-files.txt` and `tests/seo.test.mjs` were integrated by `colonial-gz0`. `listing.js` remains the identity/geometry controller; `gallery.js` remains the original viewer. `colonial-y9y` later corrected the identity blend. Current product/design docs record these outcomes.

The allowlist now includes the manifest and 810 seasonal derivatives. That describes a local staged artifact, not authorization to publish it. This evaluation does not deploy, push, change public disclosure, certify asset suitability or treat existing allowlist membership as approval. No circular dependency: evaluation can close with an explicit asset contract while `colonial-66v` resolves asset QA.

## Runnable verification and closeout evidence

Static/application regression baseline and final gate for this documentation-only closeout:

```sh
npm test
python3 tests/test_listing.py
python3 test_design.py
python3 test_marketing_plans.py
git diff --check
```

Baseline: Node 34/34, listing Python 16/16, design and marketing checks passed. Final results are recorded in the Bead closeout. Independently checked manifest inventory, file sizes, treatment coverage and exact photo-02 mismatch. No new executable logic is introduced by this document.

For runtime acceptance, use the existing local fixtures rather than creating another harness:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/tests/seasonal-runtime.html` and require its reported PASS (about two minutes). Its shortened-year fixtures cover shared phase across every segment/wrap, pause, failure/recovery, viewport-only stacks, source request reuse, original galleries and motion/print/save-data fallbacks. Read phase and computed opacities; screenshots can finish/reset animations and cannot establish temporal correctness alone.

`tests/crossfade-pixels.html` with `tests/check_crossfade_pixels.py` independently checks compositing pixels, both scroll directions, unequal aspect ratios and nested seasonal blends. Exact capture/probe commands are in `PRODUCT.md`. Other runnable fixtures there cover narrative geometry, original viewer links/previews, focus, print, responsive layouts and fallback behavior.

Remaining empirical matrix for runtime/device certification: delayed/corrupt/hung frame entry, rapid scroll both directions, live reduced-motion toggles, tab/dialog suspension, fresh/back/bfcache navigation, all adjacent key blends including wrap, transfer/memory/layer counts, scroll p95 and boundary work on the device/network profiles above. Existing implementation tests and closed follow-ups supply prior evidence, not a fresh rerun of every case in this documentation ticket.

**Closeout boundary:** architecture evaluation delivered and reconciled; no claim that asset QA, all device budgets, publication or every superseded original requirement passed unchanged. `colonial-66v` retains asset defects/acceptance; any future deployment remains a separate approved action.
