# Kitchen warmth batch design-plan

**Issue:** colonial-66v (remains open)
**Date:** 2026-10-09
**Branch:** main
**Goal:** Private B previews for05/35/47/48 at fall3, winter6, spring9, preserving accepted loft/great-room previews and every delivered asset.

## Approach and scope
- `scripts/seasons/lighting_reference.py`: add `--kitchen`, two approximate kitchen-facing cameras, separate private `lighting/kitchen` output. Same physical materials, fixtures, daylight schedule, calibration and assertions. No geometry or fixture changes. One new ray-traced batch; subsequent look changes reuse components.
- `scripts/seasons/photo_wb.py`: add kitchen batch. Measure matched B/C model paint at same +2 AgX exposure. Scale C variation by saved loft/great-room global peak, then add B-minus-C differential. Never normalize kitchen independently to the old10%cap. Photo35 faces great room and uses saved approved great-room B shifts. Output only `photo-wb/kitchen-B/` with original/current/B columns.
- Three diffuse white-painted patches per photo, median within each then median across three; warmth-only axis, original-relative targets, unchanged tint axis before clipping. Do not sample granite, appliances, tile or reflections.
- Existing C/B recipes are historical hash-bound artifacts; do not overwrite/rerender them when source code changes. Verify their outputs and physical input record bindings before reuse. All originals/seasonal assets remain unchanged.
- Tests: `tests/test_photo_wb.py` shared-scale and mixed-view target routing; real renderer and processor assertions cover new paths, usable cameras, clipping, dimensions and hashes.

## Acceptance and verification
- [x] Two valid kitchen reference views, four anchors, matched unclipped B/C samples.
- [x] Twelve private PNGs plus three contact sheets and HTML; three patch locations inspected against originals and seasonal sources.
- [x] Kitchen uses saved global scale;35 uses great-room target. Prior accepted output hashes checked by processor and peer.
- [x] Focused tests and real processing pass; all36 browser images decoded and presentation checklist audited. Owner review remains pending; final candidate matrix below is required before commit.

```sh
python3 tests/test_photo_wb.py
python3 tests/test_lighting_reference.py
python3 tests/test_night_looks.py
python3 tests/test_timeline_looks.py
blender -b --python-exit-code 1 -P scripts/seasons/lighting_reference.py -- --kitchen
blender -b --python-exit-code 1 -P scripts/seasons/photo_wb.py -- --kitchen
npm test
python3 tests/test_listing.py
python3 tests/test_walkthrough_tools.py
python3 test_design.py
python3 test_marketing_plans.py
node scripts/build-seasons-small.mjs --check
git diff --check
```

Local task-owned commit after gates, Bead checkpoint, no closeout/handoff. No paid generation, installs, delivery replacement, deployment or push. Existing window/content defects and full transition QA remain separate gates.

## Preview checkpoint and evidence

- RED: new shared-scale test rejected unsupported `peak` argument; mixed-view test failed because kitchen routing absent. GREEN: all seven photo math tests and five lighting math tests pass. No new broad pre-change baseline this batch; prior committed batch gates retained, fresh full candidate gates required.
- Real kitchen renderer and cached photo processor pass. Two valid views provide437/1420 common unclipped paint samples. Physical fixtures remain2700K/5000K; no geometry/material revision.
- Kitchen B original-relative linear R/B shifts: fall+6.88%, winter+29.93%, spring+2.40%. Great-room35: +8.30%, +49.87%, +2.66%. These are diagnostic ratios, not perceived warmth percentages or measured Kelvin. Kitchen response is smaller, not independently normalized.
- Maximum newly clipped pixel fraction0.8358% (35winter), reference target tolerance passes. No independent tint correction, windows globally affected; source content/registration issues remain untouched. Small measured tint-axis differences do not establish calibrated absence of tint.
- Read-only peer `3cdced13-7aea-4d00-bf1a-29333c836fbf` reports no actionable math/provenance/regression findings; did not rerender or visually audit. Parent inspected all three season sheets, original/source patch overlay and both night model views.
- Private outputs: `.pi/artifacts/colonial-66v-photo-wb/kitchen-B/`; `recipe.json` binds inputs,16 model display PNGs and16 outputs. `before.json` captures1213 original/seasonal/prior-preview/area-reference files for final preservation check. `patch-audit.jpg` shows patch coordinates across original/fall/winter/spring. `proof-kitchen.png` retains browser proof; all36 images decoded, full-page method/batch evidence audited.
- Final staged-candidate command results and post-gate hash/dimension assertions are retained in `final-gates.log` and `verification.json` in that private folder. Only four tracked files belong to this commit; original assets, accepted B/C snapshots, runtime, geometry and unrelated untracked state are excluded.
- Review URL: http://127.0.0.1:8765/.pi/artifacts/colonial-66v-photo-wb/kitchen-B/kitchen.html
