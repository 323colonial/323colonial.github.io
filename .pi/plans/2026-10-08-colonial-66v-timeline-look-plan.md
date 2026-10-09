# Full loft timeline appearance plan

**Issue:** colonial-66v, still open
**Date:**2026-10-08
**Branch:**main
**Goal:**18unique modeled timeline points for21/22/57/59, with B primary and C alternate; no photo edits.

Owner deferred pink-table investigation. Material remains approximate and unchanged; table is not used as white reference. This limits absolute fidelity but does not block a rough shared-lighting study.

## Scope / smallest implementation

1. Extend `scripts/seasons/lighting_reference.py` with a private `--timeline` run under `.pi/artifacts/colonial-66v-lighting/timeline/`. Existing4anchor command stays available. Use manifest's18unique knots (12 repeats0), existing seasonal dates/times, original Oct1 override. Interpolate canopy guesses between existing anchor values and sun-color guesses by solar elevation, preserving existing lit anchors. No fixture/material/model changes. Reuse two lamp-only components per view; render18daylight components per view.
2. Add `scripts/seasons/timeline_looks.py`, reusing existing linear-RGB/Bradford helpers. Use equal-view average of normalized ceiling RGB divided by known ceiling reflectance as approximate common illuminant proxy. Exclude table/furniture. Rank coolest by highest blue/red, not inferred measured Kelvin. Map that phase's proxy near D65; retain material cream through reflectance, not pure-white every wall.
3. Keep exact approved B/C night matrices at key6. Blend positive Bradford cone gains geometrically between coolest correction and each night treatment, with warmth weight from log(red/blue) relative to those phase endpoints. No arithmetic Kelvin averaging, per-view WB, auto-exposure or asset corrections. Smoothstep between each equal2second timeline segment, including last-to-first wrap; save sampled curve and knot matrices. Static model previews show knots, not full motion certification.
4. Write private B/C review pages and input/output hashes. Preserve previous physical/night records. New source version makes old source-fingerprint checks intentionally stale until their physical source run is regenerated; old proof remains historical, not silently refreshed.

## Files and checks

- Modify:`scripts/seasons/lighting_reference.py`, `tests/test_lighting_reference.py`.
- Add:`scripts/seasons/timeline_looks.py`, `tests/test_timeline_looks.py`.
- Reuse without modification:`night_looks.py`, walkthrough geometry/materials, listing/seasons assets.

Tests first:18knots and unique filenames, original date, below-horizon zero sun, anchor preservation; coolest ranking, shared gains, exact night/D65 endpoints, cyclic smoothstep continuity. Render finite/nonempty checks and source hashes; verify72physical views and144B/Cviews. Inspect chronological contact sheets and browser output. Record limitations/Bead checkpoint, stage owned paths, run final gates and commit locally. No closeout while fullassetQA unresolved.

```sh
python3 tests/test_lighting_reference.py
python3 tests/test_night_looks.py
python3 tests/test_timeline_looks.py
blender -b --python-exit-code 1 -P scripts/seasons/lighting_reference.py -- --timeline
blender -b --python-exit-code 1 -P scripts/seasons/timeline_looks.py
npm test
python3 tests/test_listing.py
python3 test_design.py
python3 test_marketing_plans.py
node scripts/build-seasons-small.mjs --check
git diff --check
```

No paid generation, dependencies, installs, photo grades, pushes, deployments or changes to73. Full motion, calibrated photometry and material accuracy remain outside this reference pilot.

## Implementation checkpoint

The first complete18-point run ranks phase11 (July10,09:15local) coolest by the declared ceiling-proxy B/R criterion:0.38969, versus phase1=0.38729 and Oct1/phase0=0.37839. Treat these as a near-tie within model/material/weather uncertainty—not a precise physical winner. Phase11 supplies near-D65 endpoint. Exact B/C correction matrices remain at phase6; different views retain local mixed-light differences under a common matrix. No table/material edits.

Private evidence root:`.pi/artifacts/colonial-66v-lighting/timeline/`. Physical `results.json` holds72view/phase metrics,80lamp/daylight components plus calibration EXRs; `looks/` holds144B/CJPEG knot previews,8lossless night endpoint PNGs,B/Coverview sheets,review pages and recipe. `looks/B.html` is primary review,`C.html` alternate. Daytime highlights remain bright under unchanged diagnostic exposure; these are not target photo exposures or calibrated visual matches.

Tests cover5physical math/schedule checks,4existing night appearance checks,and4timeline reference/curve/component-integrity checks. RED observed for missing TIMELINE,missing timeline module and missing component verifier before GREEN. Real Blender run caught output-directory variable shadowing; renamed shader node variable. Font-dependent montage failed with missing fontconfig; read-only agnt doctor showed no core failures (generic pytest/check-pi-config warning). Replaced montage with font-free image appends; no environment/config changes or installs.

Read-only peer review found no math/color-space defect within disclosed limits, but found component-to-metric provenance and auxiliary-output hashing gaps. Physical generator now fingerprints EXRs when rendered; appearance pass rejects changed components before use. Winter PNGs,overviews andHTML also receive recorded hashes. Component mutation rejection has a focused regression. Hash-bound pipeline and final candidate gates must pass before commit; final logs/evidence live beside outputs.

The curve is C1 cyclic in positive cone gains over18equal2second segments. Displayed previews are static knots; sampled numerical continuity is not full-motion proof. Pink table remains deferred by owner; its appearance is not accepted as accurate or used for white-reference fitting. Photo57 actual tint,73repair and overallassetQA remain open. No direct-closeout/handoff.
