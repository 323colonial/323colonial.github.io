# Night appearance comparison plan

**Issue:** colonial-66v — remains in progress
**Date:** 2026-10-08
**Branch:** main
**Design:** Owner approved shared photographic adaptation; compare nighttime options before extending all18timeline positions.

## Smallest approved step

Reuse existing winter linear EXR components for21/22/57/59. No new geometry, lighting renders, photo generation or delivered image edits. Physical soft-white sources remain2700K and daylight exceptions5000K. Generate baseline and three display-only treatments mapping a2700K reference white toward3000/3250/3500K-like chromaticities. These labels denote appearance targets, not measured perceived Kelvin, replacement bulbs or camera-WB slider values.

Use a shared Bradford chromatic-adaptation matrix per option in linear RGB, before the existing fixed AgX/+4 display transform. A reference white has equal luminance before/after; do not auto-expose or independently white-balance each view. Wood bounce and colored surfaces remain in the image. This is a rough photographic presentation experiment, not a simulation of human vision. No exact pixel target derives from owner's3250K observation.

## Scope / files

- Add `scripts/seasons/night_looks.py`: small offline Blender image-processing script; reads existing components and source record, writes only `.pi/artifacts/colonial-66v-lighting/night-looks/`.
- Add `tests/test_night_looks.py`: standard-library checks for identity, white mapping, luminance, monotonic warmth and linearity.
- Reuse `scripts/seasons/lighting_reference.py:cct_rgb`; do not modify physical model, generators, callers, manifest, exports or originals. No dependencies/installs.
- Private outputs:16PNGs,comparisonHTML,recipe/input/output hashes,verification record. Same row cameras, same column treatment. Directly compare model appearance, not independently graded photos.

## Steps / acceptance

1. Observe focused tests RED, then implement shared matrix and image processing.
2. Validate existing source hashes, finite pixels and input immutability; retain matrix and exact input/output hashes. Baseline must reproduce existing winter display images.
3. Inspect all four options across four views and verify browser images/labels. Present owner choice; no preference selection on owner's behalf.
4. Verify/stage/commit owned script/tests/plan. Preserve checkpoint in Bead, without closing overallQA.

```sh
python3 tests/test_night_looks.py
python3 tests/test_lighting_reference.py
blender -b --python-exit-code 1 -P scripts/seasons/night_looks.py
npm test
git diff --check
```

## Deferred

Owner chooses night warmth first. Then model all18unique timeline positions, identify coolest predicted cast instead of assumingOct1, anchor near daylight neutrality and construct smooth shared adaptation. Photo57's independent pink correction, any actual photo grading, whole-set expansion and remaining assetQA stay separate. No paid generation,push or deployment.

## Preview checkpoint

Private comparison: `.pi/artifacts/colonial-66v-lighting/night-looks/review.html`, with `recipe.json`,16PNG previews and `build.log`. Columns: physical baseline,A subtle3000K-like,B medium3250K-like,C stronger3500K-like. B remains a suggested starting point, NOT an owner selection. All four rows show progressively cooler appearance while retaining warm wood bounce.

Four new standard-library tests pass after observed missing-module RED: identity,reference-white mapping/luminance,ordered cooling with colored paint retained,and linearity/invalid input. Existing four lighting tests also pass. Blender processing reproduces all four baseline display images pixel-for-pixel; all source hashes unchanged;16finite previews with zero negative-channel fraction. New script does not modify physical source settings or source-record files.

Browser shows all16images and explanatory labels; checklist proven and audited. First navigation displayed10images and six failed image reads. Files independently decoded correctly; local HTTP log contained only first10requests. Retrying only missing image reads once loaded all16. Root cause not established; no renderer or server configuration changed. Proof retained as `review-proof.png`.

Final candidate gates recorded under `night-looks/final-gates.log` after staging; no new broad baseline run for this isolated offline addition. No exhaustive18-point modeling or real-photo correction performed. Overall colonial-66v remains open; wait for owner warmth choice before next preview stage.
