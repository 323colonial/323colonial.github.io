# Loft lighting reference design-plan

**Issue:** colonial-66v (still open; exhaustive asset QA remains pending)
**Date:** 2026-10-08
**Branch:** main
**Goal:** Rough bottom-up seasonal lighting reference for nearby views 21/22/57/59, separate from any photographic warmth adjustment.

## Boundary and audit

No delivered assets, manifest, viewer, publish list, dependencies or original model sources change. Add one offline Blender script plus small standard-library tests; results stay in `.pi/artifacts/colonial-66v-lighting/`. No downloads, paid generation, installation or deployment. Existing `scripts/walkthrough/build.py` can build geometry without bake/export/save; retained local textures/HDRI exist under `.pi/artifacts/colonial-vby/work/`. Blender 5.2.2 is installed. No graphify graph exists.

Inspected `docs/walkthrough.md`, `docs/walkthrough-lighting.md`, house/build/furnish source and seasonal solar helpers. Geometry axes: X west, Y south, Z up, feet converted to metres. Loft has six recessed sources, one fan, north dormer and open sightline to east great-room glass. Existing 21/22 cameras are approximate; 57/59 need explicit approximate poses checked against originals. Geometry has known imperfections; not a photographic reconstruction.

Current fixture powers are relative, source RGB arbitrary, glass tinted and ignored by diffuse/shadow rays, sky arbitrary HDRI. Photo-textured surfaces contain baked illumination. These cannot be treated as physical inputs. Private reference replaces source powers/colors, neutral glass transmission, sky and major bounce materials; retains shell, windows, rails, furniture and porch occlusion. Emits no new walkthrough bundle.

## Inputs / assumptions

- Actual lamps mostly 2700K; physical upper bound 3000K. Kitchen four 600lm directional 5000K tracks; powder/primary bath 5000K. Other baths remain warm. General bulbs 600lm, recessed 700lm, sink 1400lm. Bedroom fans 4 bulbs; loft/great-room fans bracket 3–4. Chandelier bracket 6–10 bulbs. Unverified peripheral fixture geometry/counts must be disclosed.
- Neutral window-film transmission .85, range .80–.90. This is film-only, not measured whole-window transmission; do not silently compound it across duplicate panes.
- Common paint Greek Villa, bedroom Debonair/Accessible Beige, bathrooms Sea Salt. Existing linear colors are rough photographic guesses; preserve hue families, use explicit rough reflectances, not claimed measured spectral values. Remove photo-texture illumination from major bounce surfaces in reference only.
- Original Oct 1, 10:00 local; seasonal 3/6/9 use existing schedule (Oct 28 17:45 / Jan 15 19:12 / Apr 15 07:45), Berkeley Springs, America/New_York. Reuse existing solar function and order-of-magnitude illuminance table without invoking generation.
- Uniform diffuse sky plus directional sun; no measured weather/forest horizon. Bracket daylight and sun attenuation, explicitly approximate tree canopy. Night has no sun/moon, sky .001 lux. Mix radiance in linear RGB, never average Kelvin.
- Fixed daylight-reference RGB/WB, AgX transform and exposure across views/seasons. Source CCTs are approximated Planckian chromaticities, not LED spectra; 683lm/W photopic RGB bookkeeping is not electrical watts. Verify Blender radiometric convention with a neutral diffuse plane before trusting source ratios.

## Tasks

1. Tests first for source color normalization, compass coordinates, seasonal sun/night and linear combination. Add `tests/test_lighting_reference.py`; observe expected failure, then implement `scripts/seasons/lighting_reference.py`.
2. Build private scene via existing builder, audit actual source positions and material settings. Disable uncalibrated emissive surfaces and foliage photo cards. Add physical flux/aim assumptions and approximate 57/59 cameras. Verify neutral-card light calibration, finite renders, glazing participation and unchanged shipped hashes.
3. Render 4 views × 4 anchors, plus lamp-only/daylight-only components where needed. Record linear painted-surface statistics separately from display RGB. Use shared scenario bounds, not individually tuned photos. Inspect contact sheets and actual camera coverage before drawing conclusions.
4. Record commands, inputs/source hashes, source inventory, assumptions, results and limitations in private report and Bead. Owner chooses whether to scale reference or trial artistic cooling; no regrading authorized here. Commit only owned script/tests/plan once verified. Do not close colonial-66v while overall QA remains pending.

## Acceptance / verification

- [x] 21/22/57/59 approximate views visually checked, not asserted registered.
- [x] Source/color/solar checks pass; reference-plane renderer units documented (not real-house calibration).
- [x] Four seasonal anchors and lamp/daylight contribution evidence retained in linear space.
- [x] Physical uncertainty separate from optional artistic cooling; no delivered files changed.

```sh
python3 tests/test_lighting_reference.py
blender -b --python-exit-code 1 -P scripts/seasons/lighting_reference.py -- --check
blender -b --python-exit-code 1 -P scripts/seasons/lighting_reference.py -- --render
node --test tests/*.test.mjs
python3 tests/test_walkthrough_tools.py
git diff --check
```

Plan saved here; execution authorized by owner. Existing asset-QA ledger remains independent of this pilot.

## Pilot checkpoint

Evidence: `.pi/artifacts/colonial-66v-lighting/{report.md,inputs.json,results.json,render.log,review.html,physical-contact.jpg}`. Browser review page shows 20 loaded images (4 originals plus 16 model anchor views), all rows/columns visible; proof copied to `review-proof.png`. Original/listing and walkthrough source/assets unchanged.

Under baseline assumptions, ceiling lamp contributions for views21/22/57/59 are respectively31/37/10/8% on Oct1,76/80/49/44% in fall,~100% in winter,37/45/9/8% in spring. Different visible surfaces have different window access despite nearby cameras. Winter scene-linear ceiling R/G is2.887/2.867/2.831/2.611: no uniquely pink57 predicted. Fall east-facing surfaces retain more sky, not more warmth. These values are not photo pixel ratios or calibrated lux; no automatic grade should be derived from them.

Peer review found spot cone clipping, lattice-alpha loss, missing plan.json provenance and overstated uncertainty coverage. Fixed first three; explicitly narrowed sensitivity claims. Point, spot, area and one-crossing glazing checks pass against analytical neutral-plane expectations (all errors <0.03%, test tolerance5%). Four offline math tests pass; missing-module and missing-spot-helper RED failures were observed before implementation. Latest 24 component renders/16 previews pass finite/nonempty checks. Shared AgX/D65/+4 display is intentionally not neutralized to photographed originals.

Count alternatives (fan3–4, chandelier6–10), film endpoints and reflectance ranges were NOT rendered. Script uses disclosed3-bulb loft/great-room fan and8-bulb chandelier assumptions; global lamp/daylight multipliers are sensitivity examples, not exhaustive bounds. Back porch model has3 cans versus owner4–5; peripheral bath geometry/counts also approximate. No claim of full-house physical verification. Materials use rough diffuse proxies, with Sea Salt approximate semi-gloss retained; camera registration, surveyed canopy and measured photometry remain absent.

Focused checks passed: offline4 tests, Node36 tests, walkthrough tools6 tests, Blender transport calibration and full pilot render. Final candidate matrix additionally uses existing listing/design/marketing/season-dimension gates; results recorded in Bead/private final-gates.log after staging. No broad pre-implementation baseline rerun for this independent offline addition; no pre-existing failure claimed.

Next: owner reviews pilot and chooses a coordinated private warmth/tint experiment or expansion. No photo regrading, paid generation, public exports, push or deployment performed. Overall colonial-66v remains in progress: owner asset review, technical QA and73 repair are still open.
