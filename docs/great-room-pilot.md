# Great-room reconstruction pilot · colonial-unq

Reviewed 8 October 2026. **Experiment complete; no-go for photorealistic expansion or publication of the current reconstruction.** Existing geometry and render tooling make a coherent 360 view feasible, but current camera registration, dimensional confidence and surface/detail fidelity do not establish a faithful photographic reconstruction. This is a negative fidelity result, not a claim that reconstruction is impossible.

## Reused work and scope

The walkthrough already exists: `scripts/walkthrough/`, `assets/walkthrough/house.glb`, the viewer, and the saved scene from the [lighting verification](walkthrough.md#full-lighting-verification--7-october-2026). No new engine, model, interaction, bake, download or deployment was needed. Existing whole-house/game functionality exceeds this pilot's original boundary; this review neither expands it nor grants publication approval.

This closeout adds review evidence only. Buyer pages, publication allowlist, model, materials and viewer remain unchanged. `colonial-vby` remains the separate join-seam/interior-lighting follow-up.

## Reference inventory

The [Zillow tour](https://www.zillow.com/homedetails/323-Colonial-Dr-Berkeley-Springs-WV-25411/22875195_zpid/?imxlb=t%2C12) and its approximate plan labels were recorded in colonial-unq. This review did not reopen the remote tour or recover original panoramas. `plan.json` preserves tour-derived polygons, not verified construction measurements. `plan_extract.py` documents their metre-to-foot conversion and the fitted upper-floor alignment; original SVGs and an exact panorama capture pose are not included in this evidence bundle.

Seven existing original photographs were read locally and their SHA-256 hashes checked against `assets/listing/manifest.json`; no enlarged screenshot or generated seasonal/finish image was used as architectural evidence. Exact paths, hashes and available source URLs are in `.pi/artifacts/colonial-unq-review/references.json`.

| Listing ID | Original source | Evidence used |
| --- | --- | --- |
| 02 | `Downloads/redfin-colonial-2026-10-06/redfin-02.jpg` | East gable, angular glazing, sliders, hearth, dining and sectional |
| 12 | Same directory, `redfin-09.jpg` | Loft-down spatial relationships; framing does not reveal all upper glazing |
| 13 | Same directory, `redfin-07.jpg` | Stone irregularity, stove, raised hearth and slider trim |
| 34 | `Downloads/listing info/pics/55.jpg` | Entry door, stair foot, turned balusters and decorative stair trim |
| 41 | Same directory, `33.jpg` | Exterior gable, chimney and deck; roof appearance, not interior ridge measurement |
| 45 | Same directory, `38.jpg` | North windows, dormer, stair and seating relationships |
| 46 | Same directory, `39.jpg` | Kitchen opening, loft edge, stair, fans and ceiling planes |

`PRODUCT.md`, `tests/fixtures/photo-coverage.json` and `tests/fixtures/redfin-refresh.json` retain the broader provenance. The marketing floor plans remain secondary connection diagrams, not a new calibration source. Model textures include generated oak, generic CC0 stone/sky, artist images and photo patches; recognizable materials are not exact surface capture. Artwork rights remain a publication gate.

## Scale and assumptions

Values below distinguish source observations from model parameters. Decimal places in code/polygons are not measurement accuracy.

| Quantity | Source / current value | Confidence and limitation |
| --- | --- | --- |
| Living-room plan label | 23 ft 7 in × 15 ft 11 in | Approximate Zillow label recorded in Bead; not a verified rectangle or survey |
| Dining / kitchen labels | 12 ft 3 in × 9 ft 11 in / 11 ft 6 in × 9 ft 11 in | Separate adjoining zones; do not add their dimensions blindly |
| Hinged-door scale | Owner says standard height; provisional slab 80 in / 2.032 m | Exact height unmeasured; excludes trim and sliding doors |
| Current door geometry | Typical openings 6.75 ft interior, 6.8 ft exterior; `parts.door` subtracts 0.05 ft for slab | Slabs about 80.4 / 81 in, not a verified exact 80-inch calibration; slider 6.8 ft is a separate assumption |
| Plan coordinates | `plan_extract.py`: metres ÷ 0.3048, translated frame; upper x fit 69.1 / 67.2 | Tour-derived approximate scale with fitted inter-floor alignment; not independently validated |
| Hand-built y calibration | 26.5 drawn ft → 27.4 plan ft, applied once | Compatibility fit, not a physical measurement; shell polygons are already in plan space |
| Main ceiling / loft floor | `house.H1 = 8.1`, `F2 = 9.1` ft | Inferred vertical geometry; photos support relationship, not exact values |
| Great-room eave / peak | `EAVE = 9.7`, `GPK = 22.95` ft | Inferred finished ceiling; exterior roof ridge is distinct |
| Roof slope | Drawn 12:12; y stretch makes final slope about 44.04°, not 45° | Modeling assumption; no perspective-rectified roof measurement in this review |
| Stair | `NR = 14`, loft level 9.1 ft | Model parameters, not independently counted/measured risers |
| Review camera | p02 eye `(17.5, 13.8, 4.6)` ft; x west, y south, z up | Existing hand-set photo approximation, **not a verified tour capture point** |

## Geometry and materials comparison

Fresh renders use the existing saved Blender scene. `house.py`, `build.py`, `planshell.py`, `furnish.py` and `plan.json` match the source snapshot retained with that scene. Camera values come directly from `build.py::VIEWS`; no camera fit or geometry edits were hidden in this review.

![Original photos beside approximate-camera renders](../.pi/artifacts/colonial-unq-review/photo-comparison.jpg)

| View | What agrees | What prevents a fidelity pass |
| --- | --- | --- |
| 02, east gable | Hearth between sliders; angular glazing above; dining right and seating left | Window framing/proportions and composition visibly differ. Stone pattern, stove, table and sectional are substitutes. Camera versus geometry error is not isolated. |
| 45, north/stair | Stair left; dormer above front windows; fireplace right | Perspective/subject size differs; stair detailing and seating silhouette are simplified. This is not an accurately registered photo match. |
| 46, kitchen/loft | Kitchen below loft, stair adjacent to entry, vaulted ceiling above | Loft/kitchen framing differs; strong fixture hotspots and simplified rail/trim obscure photographic comparison. |
| 12, loft-down | Reference establishes open-to-below relationship | Existing `p12_down` camera renders mostly a black obstruction. Retained as failed camera evidence, not a successful match; exact occluder was not diagnosed. |

`p02_great-geometry.png` removes opaque surface textures using a neutral rough material while preserving transparent/emissive surfaces and exterior cards. It is a geometry diagnostic, not a fully neutral relighting. `p02_great-material.png` uses the existing materials and rebuilt Cycles daylight/fixtures. Photo patches can still contain photographed shading; the current model does not fully satisfy the proposed de-lit-material approach.

**Matched-camera criterion remains unproven.** There is an approximate-camera geometry preview and material trial, not a calibrated matched-camera result. Together with the failed loft view, this is evidence for the Bead's allowed negative feasibility outcome; it must not be relabeled a fidelity pass.

## Full-sphere inspection

Rendered one 2048 × 1024 equirectangular panorama at the p02 position, facing east at the centre. All directions share one scene and viewpoint, not generated/stitched alternative architectures. `sphere-inspection.jpg` contains six 90° perspective crops sampled from that panorama, including the longitude wrap, zenith and nadir.

![Six directions sampled from the panorama](../.pi/artifacts/colonial-unq-review/sphere-inspection.jpg)

- **Longitude wrap:** west-facing crop crosses the image boundary. No obvious split geometry at this resolution. Mean absolute edge-column difference is 3.645/255 per RGB channel versus 1.848 in immediate neighboring columns; maximum 33. This diagnostic is not a seam or photorealism certification.
- **Ceiling/floor:** no broad missing cap or exposed void in inspected crops. A small dark wedge at the kitchen/loft underside join remains visible; geometry versus shading cause is not established here. Fixture hotspots remain.
- **Perspective/consistency:** rectilinear crops preserve recognizable spatial relationships; equirectangular stretching near poles is expected. Room accuracy is still unproven because capture pose and vertical dimensions are not calibrated.
- **Surface quality:** overly uniform flooring, proxy stone/furniture and stand-in woods remain readily distinguishable from source photographs. 2048px/48-sample review is not high-resolution delivery validation.
- Existing shipped shell diagnostics report 52,533 rays, zero escapes and 461 back-face hits. Fresh asset tests validate that record; it does not prove every surface/view is gap-free, and this review did not rerun the full shell-ray export.

## Reproduction and evidence

Private local bundle: `.pi/artifacts/colonial-unq-review/` (git-ignored; not included in buyer publication). Representative images above require that bundle. The tracked report remains useful without it, but someone on another checkout needs the private artifacts for exact visual replay.

```sh
# Read existing scene, render only into review bundle; no build, bake or publication.
blender -b --python-exit-code 1 -P .pi/artifacts/colonial-unq-review/render.py
```

- Input scene: `.pi/artifacts/colonial-14d-lighting.Ltif4W/work/house.blend`; SHA-256 `5e70e40fd29f9e4b5feb19e16e584583056f2eadd6ed65acac997dc99d904910`.
- Existing source textures/HDRI must remain at the paths referenced by that saved scene. All were present; none downloaded. `inputs.json` in the prior lighting bundle records their hashes.
- Blender 5.2.2 LTS, Metal, 48 samples, seed 323, denoising, AgX / Medium High Contrast, exposure +1.6. Existing world rotation/lights retained. This is a fresh direct render, not a rebake of shipped WebGL lightmaps.
- `render.py` checks image availability, render dimensions, finite/nonuniform pixels and output count. Those checks cannot establish photographic fidelity or reject every obstructed camera.
- `render-settings.json` records exact cameras and six output hashes; `render.log` records execution. `sphere-check.json` records reproducible FFmpeg `v360` crop commands and seam diagnostics. `references.json` identifies original-photo inputs.
- Fresh baseline: walkthrough Node tests 6/6, Python tools tests 6/6, Blender projection assertions pass. Existing browser fixture reports all 10 assertions PASS. These are implementation regressions, not photorealism tests.

## Decision and next measurements

**No-go for more photorealistic viewpoints now.** Keep the existing walkthrough as an approximate local prototype. Do not spend another whole-house rebuild or larger bake on a camera/geometry/material-fidelity problem. Technical ability to render 360 is demonstrated; faithful photorealism from current reconstruction is not.

Before revisiting expansion:

1. Record one identified tour capture point with plan coordinates, camera height, heading/FOV and uncropped reference directions; recover original capture assets only with download/use approval. Calibrate against several shared architectural landmarks, not raw pixel-height ratios.
2. Measure one hinged door slab, floor-to-loft height, finished eave/ridge heights, slider/window opening sizes and offsets, stair risers/treads and dormer recess. Resolve vertical dimensions before increasing detail.
3. Repair the obstructed loft camera and compare east, north and kitchen/loft views with fixed registered cameras; separate lens/pose error from geometry error.
4. Address seams/lighting in `colonial-vby`. If photographic fidelity is still desired afterward, make a new bounded decision on accurate furniture/trim, irregular hearth geometry, de-lit surface capture and exterior scenery rather than expanding automatically.

No site changes, public release, new remote imagery, artwork-rights clearance, exact tour-pose validation or physical measurements are claimed by this closeout.
