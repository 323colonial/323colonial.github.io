# Walkthrough seam and lighting diagnosis · colonial-vby

8 October 2026. **Three confirmed rendering defects corrected; photographic fidelity remains unproven.** Changes affect the generator and its tests. The new full bake is a private review bundle, not a replacement of `assets/walkthrough/` and not a deployment.

## Diagnosis and smallest fixes

| Symptom | Evidence / cause | Change |
| --- | --- | --- |
| Dark wedge at south ceiling / kitchen-loft join | At the existing `p46_west` camera, pixel (337,279) in a 1100×733 render hits the back of exterior `siding`. The drawn ceiling ends at measured y=26.883 ft, short of the wall face at y=26.91. Direct Cycles and WebGL both show the wedge; it is not merely UV padding or compression. | Extend only the great-room south ceiling endpoint from drawn `D−0.5` to `D−0.25`, overlapping the wall. Same slope, winding, material and room dimensions. Regression now hits the front of `ceiling`. |
| Bright pools around kitchen/loft recessed fixtures | Recessed apertures had omnidirectional point sources 1.09 ft below them, illuminating the ceiling directly. Original kitchen/loft photos show recessed apertures, not suspended bare bulbs. | Preserve the four-value light tuples; record recessed indices/radii in `Builder.downlights`. Build these as downward disk area lights, 0.02 ft below their visible apertures. Keep powers and owner-specified daylight/soft-white color rules; other lamps remain point lights. |
| Cyan bath walls and floor | Encoder balanced the mean of all interior irradiance, including colored bounce, rather than a neutral reference. Baseline channel multipliers were R=0.83467, G=1.01286, B=1.24777. | Remove scene-average white balance. Preserve channel ratios, scalar exposure, Sea Salt paint and source textures. No material recoloring to conceal illuminant error. |

The light fingerprint now includes recessed indices/radii. Source-byte hashing still invalidates old bakes. No new dependency or scene JSON schema was introduced.

### Lines deliberately retained

Not every loft line is an opening. Baseline source-space rays either side of the right-wall line hit paint faces at y=19.228 and y=19.240 ft: a small modeled step from adjoining plan-wall runs. It also appears in the uncompressed direct Cycles render. This establishes a geometric contribution, not that every visible line has one cause. Do not flatten the approximate plan or change atlas padding/compression globally on that evidence. Other wall steps, fan shadows and the existing 461 sampled back-face hits remain; this is not an all-seams certification.

## Reference comparison and calibration limits

Local originals were hash-checked against `assets/listing/manifest.json`. `references.json` in the evidence bundle records exact paths, SHA-256 values and available source URLs:

- Kitchen 15: `Downloads/redfin-colonial-2026-10-06/redfin-18.jpg`.
- Loft 21/22: same directory, `redfin-28.jpg` / `redfin-29.jpg`.
- Bath 55/56: `Downloads/listing info/pics/52.jpg` / `53.jpg`.

The illustrated comparisons use photos 15, 21 and 55. No source pixels, watermarks, dimensions, finishes, provenance records or approved geometry assumptions changed. No download was needed.

![Original photographs beside baseline and revised WebGL renders](../.pi/artifacts/colonial-vby/reference-comparison.jpg)

- **Kitchen:** artificial blue-white ceiling halos diminish; apertures remain visible. The photo has a softer, more neutral ceiling and much richer appliance/material detail. The revised render is still warmer and simplified.
- **Loft:** recessed pools diminish; the fan's shadow remains. Removing global white balance makes warm-fixture rooms warmer, **not a closer overall color match** to the photographed loft. Do not call this full color calibration.
- **Bath:** cyan cast diminishes without changing Sea Salt. The photographed wall is grey-green; the model still reads greener/lighter in places. The neutral floor provides a useful qualitative check distinct from paint hue. Mirror, photo patches and geometry remain imperfect.
- **Exposure:** retain the existing scalar target rather than fitting brightness to unregistered photographs. Interior gain changes from 1.185 to 1.175 (about −0.012 stops); exterior remains about 0.630. Viewer exposure stays 1.0. Cycles previews use the existing AgX/+1.6 interior settings, so they are diagnostics, not identical WebGL color output.

Before/after **render cameras are identical**. Cameras are only approximate matches to the photographs; there is no verified tour pose, neutral-card capture, measured illuminance or physical paint calibration. Further color matching needs those constraints, not arbitrary per-room material edits. The [great-room pilot's no-go](great-room-pilot.md) for photorealistic expansion/publication remains in force.

## Verification

- Blender 5.2.2 / M3 Max Metal: five 4096px pages, 256 samples, 77° sky rotation, full bake/denoise/encode/export in 312.3 seconds.
- Real-bake checker: finite, nonnegative, nonempty maps; current fingerprint accepted; geometry/light mutations rejected; restored inputs accepted. Recessed sources verified as downward disks of the recorded diameter.
- Fresh shell export: 52,533 rays, zero escapes, 461 back-face hits, unchanged counts. The targeted seam ray catches a defect that the coarse shell sampling missed.
- Maximum encoded lit-texel clipped-channel fraction is **0.770%**, versus baseline maximum 0.526%. This increase is disclosed, not treated as a fidelity pass; images were inspected for broad clipping. Lowering every room's exposure to hide sparse clipping is not justified by the unregistered photos.
- Fixed WebGL views inspected: great room, kitchen join, kitchen, bath, loft and front exterior. Mean absolute channel differences from baseline: 7.687, 10.192, 13.169, 12.934, 13.644 and 0.462 /255 respectively. These quantify change, not photographic accuracy.
- Targeted tests were observed failing for the seam, recessed-source metadata and encoder channel ratios, then passing after fixes. Existing projection/calibration tests remain intact. Python signature regression covers the new light metadata.
- Existing browser fixture against the new private bundle: all ten assertions PASS. This covers loading, movement/teleport, note freeze/cancel, invalid room inputs, simulated persisted pagehide and missing-texture fallback, not physical-device or native BFCache certification.

## Evidence and reproduction

Private bundle: `.pi/artifacts/colonial-vby/`. It retains `diagnose.py`, baseline ray/aperture records and red/green logs under `diagnosis/`, `inputs.json`, `references.json`, `compare-refs.sh`, `reference-comparison.jpg`, `visual-metrics.json`, `proofs/`, `review.md`, build/check logs, `work/house.blend`, raw/denoised/encoded maps, and the isolated `site/` browser bundle. Image links require these local artifacts; this tracked report remains readable without them.

```sh
W="$PWD/.pi/artifacts/colonial-vby/work"
blender -b --python-exit-code 1 -P scripts/walkthrough/build.py -- \
  --work "$W" --size 4096 --samples 256 --bake --encode --export --save
blender -b --python-exit-code 1 -P tests/verify_walkthrough_lighting.py -- \
  --work "$W" --size 4096 --samples 256
node --test tests/*.test.mjs
python3 tests/test_walkthrough_tools.py
blender -b --python-exit-code 1 -P tests/test_walkthrough_blender.py
```

`work/textures`, `sky.hdr` and `sky_tonemapped.jpg` reuse the retained `colonial-14d-lighting.Ltif4W/work/` inputs through local symlinks. That original source bundle must remain available. Verified signature: `541ba37b3c1e7e2e92728ec7b8c734e340c24be783397121c9bd50fcb752f2a6`.

Serve the repository locally and open `/.pi/artifacts/colonial-vby/compare.html` for six fixed-camera pairs. The copied `site/scripts/walkthrough/publish.sh` assembled only this isolated bundle; the repository-root publication script was not run. `site/tests/walkthrough-browser.html` is the unchanged regression fixture pointed at that bundle.

No public asset replacement, push, deployment, reconstruction expansion, new geometry calibration, artwork-rights clearance or claim of photorealism. Remaining visual limitations are recorded above rather than silently marked fixed.
