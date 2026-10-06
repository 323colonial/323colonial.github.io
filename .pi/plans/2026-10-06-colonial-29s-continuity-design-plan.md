# Seasonal continuity correction design-plan

Issue: colonial-29s (keep open for owner review; no handoff)
Date: 2026-10-06
Branch: main (existing private trial; no public-site changes)

## Approved outcome
Owner approved revising ALL generated scenes, including three previously accepted anchors, to fix grass/snow, sunlight/shadows/speculars and indoor/outdoor lighting continuity. Original summer JPEG remains byte-identical. Existing twelve-scene v3 and four-scene v2 trials remain available as historical comparisons. Twelve scenes and five-second continuous loop remain unchanged. User separately asked how to obtain Luma API access; no purchase/video generation authorized here.

## Implementation boundary
Only .impeccable/mocks/seasons assets/viewer/checks and ignored .pi/artifacts/seasons/v4 scripts/raw/evidence. No public pages, original listing assets, dependency, deployment, account credential or home-config changes. Reuse Gemini image-edit requests, native affine registration and ImageMagick finishing. Keep old v2/v3 files untouched. Save new eleven edited scenes and exact prompt/schedule/hash/registration provenance in v4.

## Shared art direction
This is an art-directed seasonal cycle, not a claim to astronomical accuracy from an unknown camera compass bearing. Summer fixes baseline camera/materials/daylight. Autumn sun lowers toward camera-right, shadows lengthen/soften. Sunset fades to diffuse winter twilight: NO hard solar highlights. Dawn returns through diffuse sky, then low camera-left spring sun rises toward summer baseline. Broad sky reflections remain broad and subdued in twilight; sun accents follow direct-light strength, not independent white flashes. Preserve red grill enamel, no invented chrome.

Use one schedule for all requests, with current target + previous/next target + fixed master + full contact sheet as refs. Explicit ground fractions aim to reduce both plateaus and abrupt winter/spring jumps: winter ~85% snow, thaw ~60%, early growth ~30%, spring ~5% shaded residual, late spring0%; exposed grass progresses dormant straw/olive -> muted green -> fresh green -> lush late spring. These are target fractions, NOT measurements or guarantees. Preserve terrain, patch locations, consistent branch structure and moderate seasonal texture changes. Autumn first-frost must visibly thin leaves before bare first-snow.

After registration, enforce one stable window-light source and brightness envelope with existing glass polygons; preserve mullions/reflections, no full-image overlays. Keep exterior fixtures localized. Prefer source-generated physically coherent grill/shadow treatment; inspect specific crops before accepting, never claim physical rendering correctness from prompts.

## Steps and checks
1. Preserve v3 viewer as twelve-before.html. Add regression expecting v4 sources plus immutable original summer; observe RED before changing main viewer.
2. Generate eleven scoped continuity revisions with common schedule, same geometry master, target and neighboring references. Bounded2-request parallelism, no blind retries. Keep prompt/raw hashes. Inspect a contact sheet before finishing.
3. Register all11 via existing .pi/artifacts/seasons/v2/align. Finish masked practical-light progression and watermark; save v4 provenance and independent NCC diagnostics. Do not weaken2px/.4 thresholds; explicitly disclose low-confidence changed-glass regions.
4. Inspect all12 frames and adjacent midpoints plus lawn, grill, window/light and shadow strips. Compare against v3. Correct one bounded batch if necessary.
5. Point private viewer to v4, retain historical links, remove stale approved-target labels. Tests retain all12 fades/wrap, original source, pause, reduced motion, mobile layout and privacy.
6. Run node --test tests/*.test.mjs; python3 tests/test_listing.py; python3 test_design.py; python3 test_marketing_plans.py; browser check.html normal/reduced; git diff --check. Hash-check original summer and historicalassets. Commit only task-owned files; record evidence and remaining limits in Bead. Keep open until owner sees result.

## Luma research
Verified official https://lumalabs.ai/learning-hub/dream-machine-credit-system: Dream Machine subscriptions/credits and API credits are separate/nontransferable. https://platform.lumalabs.ai/ redirects to Luma auth; current https://docs.agents.lumalabs.ai/ specifies LUMA_AGENTS_API_KEY. Account not accessed, no key created/read, no billing changes, no generation. Do not assume owner trial credits are API credits. Multi-keyframe API capability does not establish availability in trial web UI.
