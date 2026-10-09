# Remaining interior warmth batches design-plan

**Issue:** colonial-66v (open)
**Date:** 2026-10-09
**Branch:** main
**Goal:** Review all remaining seasonal interiors by room with approved B appearance, keeping prior accepted previews and delivered assets unchanged.

## Scope and approach

User requests proceeding through entire interior photo set. Continue existing fall3/winter6/spring9 anchor-review workflow; other mapped phases remain a later interpolation/QA step, not silently certified.

- New previews: primary bedroom18/37, guest bedroom23/60, powder36, upstairs bath38, hall49, mudroom54, remaining great-room/entry34/42/44/45/46, loft58/61 (15photos,45PNGs).
- Already accepted: loft21/22/57/59, great-room02/12/13/14, kitchen05/35/47/48 (12photos,36PNGs). Link immutable reviewed snapshots, never overwrite them.
- Basement30/73: current anchors visible in index/review but held, no fabricated model targets. Existing model has no usable basement interiors/lighting;73 also needs approved content/paving repair. No paid generation.
- Unchanged original/gallery interiors7/15/19/20/24/55/56 remain original-only. No new variants. Porches/decks are outdoor-light groups, excluded from interior WB batch; factual plan31 untouched.

## Smallest implementation

1. `scripts/seasons/lighting_reference.py`: separate `--interiors` output, two valid approximate camera poses per new modeled room (primary,guest,powder,upper-bath,hall,mudroom). Retain current fixtures/materials/calibration and white paint/ceiling ray selection. Colored walls are bounce surfaces, never neutral reference samples. Cached components support future adjustments without ray tracing.
2. `scripts/seasons/photo_wb.py`: reuse kitchen matched B/C path for new groups and saved global C scaling, existing accepted B room targets for remaining great-room/loft views. Fixed three white ceiling/paint patch coordinates per photo; same median/axis/luminance rules. Separate `interiors-B/` outputs; no masks or independent tint edits. Preserve all accepted C/B/kitchen files and physical references.
3. Complete interior index links accepted groups, new room pages, basement held page and original/gallery-only items. Show scope and remaining intermediate-frame gate. No runtime UI changes or new dependencies.
4. `tests/test_photo_wb.py`: exact remaining group/target coverage, three patches per view, unchanged-room reuse and global scale behavior. Existing renderer/processor assertions plus artifact checks prove camera coverage, unclipped samples, outputs/dimensions/provenance.

## Verification and acceptance

- RED/GREEN focused tests before implementation.
- Inspect originals, source patch overlays, model views and all season contact sheets; hold unsupported or clipped reference cases rather than silently skipping.
- Preserve original/seasonal/accepted-preview hashes from `.pi/artifacts/colonial-66v-photo-wb/interiors-B/before.json`.
- Verify all recipe input/output/component hashes, dimensions and accepted-target equality. Browser evidence establishes presentation only, owner acceptance remains separate.
- Stage only two scripts, `tests/test_photo_wb.py`, `tests/test_lighting_reference.py` and this plan. Full final gates before local commit; Bead checkpoint without closeout/handoff.

```sh
python3 tests/test_photo_wb.py
python3 tests/test_lighting_reference.py
python3 tests/test_night_looks.py
python3 tests/test_timeline_looks.py
blender -b --python-exit-code 1 -P scripts/seasons/lighting_reference.py -- --interiors
blender -b --python-exit-code 1 -P scripts/seasons/photo_wb.py -- --interiors
npm test
python3 tests/test_listing.py
python3 tests/test_walkthrough_tools.py
python3 test_design.py
python3 test_marketing_plans.py
node scripts/build-seasons-small.mjs --check
git diff --check
git diff --cached --check
```

No delivered edits, publication, push, installation, or independent tint correction. Basement holds, unreviewed intermediate frames, registration and transition QA remain explicit. Original colors are photographic references, not measured physical CCT; rough simulations guide relative room response only.

## Owner-approved porch addition

Owner explicitly adds screened porch04/17/50/51/52/53. They propose white daybed views to peg other views through stable wood: “basically wood-balancing.” Use04/50 as white-daybed anchors (three diffuse frame patches each); measure original-relative warmth change on three shaded cedar-ceiling patches after fitting daybed whites. Transfer median change from both anchor views to three cedar patches in17/51/52/53. Never force wood neutral or copy absolute wood RGB between views. Record transfer disagreement; sunspots, lamps, chains and reflections excluded from samples. All18 new porch anchors are provisional owner-review candidates.

Include two porch cameras in isolated `--interiors` reference output, with three small neutral diffuse virtual cards per position. Cards are camera-visible but do not cast shadows or participate in other diffuse rays; they sample illumination without replacing cedar or its bounce. Select only probe rays for porch targets. Preserve actual2700K porch lamps; use4.5-recessed equivalent total distributed across existing three model positions as an explicitly approximate3–5 count proxy (owner previously estimated4–5 back-deck fixtures, exact porch count not surveyed). Interior fixture assignments unchanged. Roof, screens and approximate wood bounce retained; tree shade/weather/screen transmission uncertain.

Coverage becomes21 new photos/63 comparisons plus12 previously accepted photos. Index exposes porch separately, basement holds and original-only interiors. Test white-anchor ordering, transfer of relative warmth despite different wood colors, finite input validation and complete porch membership. No porch intermediate frames adjusted yet.

## Implementation and review checkpoint

- Output `.pi/artifacts/colonial-66v-photo-wb/interiors-B/index.html` links9 groups, accepted snapshots, basement holds and7 original/gallery-only interiors.63PNG comparisons include48 unaccepted candidates and15 explicit HOLDs, not63 approved corrections.
-12porch comparisons (17/51/52/53, all three seasons) remain unchanged source after transfer rejection. Daybed anchor wood deltas disagree by0.274/0.807/0.306 logR/B across fall/winter/spring; spring even disagrees in sign. Median must not conceal this. A conservative0.2-spread/opposite-sign guard rejects transfer; this is a provisional review gate, not measured color tolerance. Rejected daybed anchors also block transfer.
- Photo-reference channels below.002 or at/above.98 linear are held before fitting. Zero is valid sampled image data but not valid color-ratio evidence; it gives HOLD/identity/null target rather than aborting the batch or dividing by zero. Photo51 original ceiling blue median~.00061 caused unstable4xblue gain in the rejected draft. Latest held comparison has no WB correction.
- Three interior fitted candidates are held:37winter (~2.19%new clipping),36fall (~2.16%),38winter (~4.62% and visibly excessive modeled warmth). These remain visible as diagnostics, not approved outputs. Other48candidates also require owner acceptance.
- White-patch overlays inspected across originals and seasonal sources; ceiling strips used for Sea Salt bathrooms, avoiding colored walls/mirrors. Removed candidate patches touching fans, vents, railing or door trim before final generation. Room/season contact sheets inspected for color; this is not full-resolution feature/registration/transition certification.
- Physical reference `.pi/artifacts/colonial-66v-lighting/interiors/`:14views,56anchor results,89EXRs including calibration. Original interior fixture assignments unchanged; only porch3sources use the disclosed4.5-fixture-equivalent proxy. Six virtual cards preserve wood bounce by disabling their shadow/diffuse/glossy visibility.
- Renderer zero-daylight metric originally divided0/0 (guest-bedroom60night): now color ratios are `null`, with RED/GREEN test. No light has no defined chromaticity.
- Fixed +2 sampling exposure rejected every upper-bath view at old.025 per-channel floor because valid warm blue was~.006. New interior batch uses.005; old C/B/kitchen behavior keeps.025. All views must still have20 common unclipped samples and two usable views per room.
- Porch day/night dynamic range cannot fit the old display-sampling range: daytime cards clipped, nighttime blue near black. Neutral-probe mean is brightness-normalized to scene-linearY.1 before the same B/C transform/AgX; both treatments share each recorded gain. Physical components, photo exposure and original-relative daybed anchoring unchanged. This color-only approximation is less directly comparable to indoor fixed-radiance measurements and remains provisional, not calibrated photometry.
- A NumPy float32 probe gain initially failed JSON serialization; helper now returns native float. No delivered image was affected by any failed private run.
- Peer3431da70 findings (anchor disagreement, near-black51, missing explicit holds) verified and addressed. Follow-up8bc61b90 found rejected-anchor propagation and zero-channel handling gaps; both addressed with failing tests then green. Focused photo math14 and lighting math6 pass; full final candidate matrix required before commit.
- Read-only doctor: no failures; generic missing pytest/check-pi-config warning only. No installs or home-config edits.
- Final command output, candidate diff, input/output/component/dimension/preservation assertions and browser proof live in this private output folder as `final-gates.log`, `candidate.diff`, `verification.json`, and `proof-*.png`. Preservation baseline covers1302files. No new broad pre-edit baseline; prior committed gates retained, fresh full candidate gate required.

**Still open:** owner appearance review, porch wood-bridge disagreement, clipped/overwarm candidates, basement30reference/73content repair, other mapped annual phases, full-size window/color and registration/transition QA. No delivery/publish authority inferred.
