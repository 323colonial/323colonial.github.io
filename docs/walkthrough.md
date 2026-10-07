# 3D walkthrough

`walkthrough/index.html` is a first-person walk through an approximate 3D model of the house: WASD and mouse-look, run, jump, crouch, stairs and wall collision. It is a static page (three.js, vendored under `vendor/three-0.186.1/`) and reads everything from `assets/walkthrough/`.

It is **not** in `scripts/publish-files.txt` and nothing links to it yet. Publishing it means adding `walkthrough/`, `assets/walkthrough/` and `vendor/three-0.186.1/` to the allowlist and linking to `walkthrough/` from a buyer page; both are owner decisions.

## What the model is built from

- **Shell**: `planshell.py` generates walls, floors, flat ceilings, doors and windows from `plan.json`, the measured vector floor plans of the listing's Zillow 3D tour (`plan_extract.py` converts the tour's SVGs). Every wall is a closed slab with a finish on both faces.
- **Hand-built, in `house.py` / `furnish.py`**: stair, roof and dormers, kitchen, bath fixtures, porch, deck, furniture. These are drawn in "drawn feet" and scaled once in y onto the measured plan (`calibrate`, a single straight scale); use `yinv()` to place something at a measured y.
- **Photo patches**: flat things that should look like the real house (kitchen cabinet fronts, range, backsplash, island faces, bath wainscot, wall art) are squared-up crops of the listing photographs, one per surface. The recipes, with the pixel corners picked by eye, are in `prepare.sh`.
- **Everything else**: CC0 materials and the sky from [Poly Haven](https://polyhaven.com); a generated strip-oak floor (`oakfloor.py`). The trees are cards cut from the sky photograph, so the woods are a stand-in.
- **Artwork**: three pieces use the artists' own published images (Greg Dunn's *Neurogenesis I* and *Maki-e Neurons*, and a cerulean-warbler painting), from links the owner supplied. They are the artists' copyright; settle that before the page goes public.
- Finishes follow the owner's list (Sherwin-Williams Greek Villa, Debonair, Sea Salt, Accessible Beige, Pewter Green; mahogany deck stain); furniture follows the staged listing photographs.
- The garage, basement and closets are closed.
- Whole-photo projection (`project.py`, key **P** in the page) is kept but off by default: it smears wherever geometry and photograph disagree.

## Reviewing in the page

Run `python3 scripts/walkthrough/serve.py` and open `/walkthrough/`. **K** freezes the view and asks for a note; the note, position, heading and a screenshot are appended to `.walkthrough-notes/` (git-ignored). **F** flies through walls.

## Rebuilding

Needs Blender 5.x (tested with 5.2.2), ImageMagick 7, Python 3, curl and uv. The preparation step downloads textures/artwork and uses uv to obtain Python 3.12, NumPy and Pillow; it requires network access and separate download approval when run by an agent. Serving the committed assets needs only Python 3.

```sh
W=/some/scratch/dir
scripts/walkthrough/prepare.sh $W                 # download CC0 textures, cut photo textures
blender -b -P scripts/walkthrough/build.py -- --work $W --size 4096 --samples 256 --bake --encode --export
scripts/walkthrough/publish.sh $W                 # write assets/walkthrough/
```

- `house.py` is the building, `furnish.py` the furniture, `parts.py` windows/doors/rails/cabinets, `hb.py` the mesh and lightmap-atlas builder. Dimensions are in feet: x = west of the east wall, y = south of the front wall, z = up from the main floor.
- `build.py --preview --views p02_great,p46_west` renders reference stills from listing-photo viewpoints without baking, which is the quick way to check a geometry change.
- `build.py` lowers its own priority (`nice` 10), prefers a Metal GPU and leaves four CPU cores free. Non-Metal systems fall back to Blender's CPU configuration. Prior development reported about five minutes for a 4096 px bake on an M3 Max; this review did not remeasure it.
- **Work unbaked, bake last.** `build.py --export` alone takes about a second: it writes the geometry, collision data and shell check, marks the scene `baked: false`, and the page then shows it under plain even light. Use that loop for geometry and placement. `--bake --size 2048 --samples 64` is a one-minute draft bake; the full bake is only needed before showing the result.
- Every export runs a shell check: rays cast from inside each room must not leave the house except through glass or an open slider. The count is in `scene.json` (`checks`) and `tests/walkthrough.test.mjs` fails on any escape.
- In the page, **K** shows and copies your position in plan feet, **F** flies through walls.
- Lighting is baked in Cycles (sky plus ceiling fixtures), denoised (`denoise.py`) and stored as lightmaps. The viewer adds environment/planar reflections; unbaked previews use simple realtime lights. Geometry, materials, lights, sky, source or bake-setting changes invalidate the bake. Run a full `--bake --encode --export` with matching size/sample/sun settings; partial `--pages` bakes cannot authorize a new encoded bundle.
- `publish.sh` assembles a local bundle in a temporary sibling directory before swapping it in. Missing inputs/conversion failures leave the previous bundle untouched. Successful replacements retain the old bundle under `assets/.walkthrough-previous.*/walkthrough` for manual recovery; backups are git-ignored and never automatically pruned. Stop the preview server during replacement: this local tool is not a concurrent deployment service.
- Unbaked bundles need no lightmap files. Required textures must finish loading before the viewer starts or captures its reflection probe; failures show the fallback panel. Photo atlases are exported only when `--project` runs in that invocation, never rediscovered from stale output.
- `scene.json` carries materials, wall collision segments, walkable floors and a terrain height grid. The page exposes them as `window.colonial` for local inspection.

## Verification and review limits

```sh
node --test tests/*.test.mjs
python3 tests/test_walkthrough_tools.py
blender -b --python-exit-code 1 -P tests/test_walkthrough_blender.py
# With serve.py running, open /tests/walkthrough-browser.html; expect PASS.
```

Bead `colonial-14d` records initial code review. Regressions cover stale bake/projection reuse, failed bundle conversion, fresh unbaked publication, local note validation/numbering, single plan calibration, texture failure, walking/teleport, frozen note entry, short-screen controls and persisted-page handling. Browser fixture simulates persisted `pagehide`; it is not real back/forward-cache certification. Note writes require same-origin localhost requests, with a 4 MiB body cap; this is a local developer server, not a public service.

Current geometry remains approximate, not a validated photorealistic reconstruction. Mobile-device GPU budgets and photographic fidelity comparisons remain unverified. Keep measured shell data separate from hand-drawn geometry; improve camera/geometry alignment before expanding photo projection. Profile actual slow rooms before adding spatial indexes or a new engine. Artwork rights and owner publication approval remain release gates; buyer pages and their publication allowlist are unchanged.

### Full lighting verification · 7 October 2026

Reopened `colonial-14d` to run the real pipeline, not only fingerprint unit tests. Original HDRI and every source texture were available locally; no downloads or replacement of shipped assets were needed.

- **PASS:** Blender 5.2.2 / M3 Max Metal, 4096px, 256 samples, 77° sky rotation; all five pages baked, denoised, encoded, exported and assembled into an isolated browser bundle. Build completed in 328.7 seconds, including five 48-sample reference previews.
- **PASS:** raw, denoised and encoded maps have expected dimensions and finite, nonnegative values. Every page is lit/nonempty. At most 0.526% of lit texels per page have an encoded channel at 1.0; this is a measured statistic, not a photorealism threshold.
- **PASS:** real geometry/light mutations change the fingerprint and make the exporter emit `baked:false`; restoring matching inputs restores `baked:true`. Run `blender -b --python-exit-code 1 -P tests/verify_walkthrough_lighting.py -- --work WORK --size 4096 --samples 256` against a completed bake. It writes trial exports only to a temporary directory.
- **PASS, bounded visual regression:** inspected matched WebGL views of great room, kitchen, bath, loft and exterior, with fixed camera/resolution/fire time. Mean absolute RGB-channel differences from shipped bake were respectively 0.165, 0.192, 0.176, 0.310 and 0.107 on a 0–255 scale. Window/roof/porch shadows, exposure and bath mirror remained consistent. This compares two modeled renders, not either render against the real house.
- **Existing issues remain:** thin wall/ceiling join lines, strong fixture hotspots and cool bath cast; tracked in `colonial-vby`. Shell check remains 52,533 rays, zero escapes and 461 back-face hits. No claim that every room/direction is artifact-free.

Local evidence bundle: `.pi/artifacts/colonial-14d-lighting.Ltif4W/` (git-ignored). `inputs.json` records input hashes and source revision; `build.log`, `publish.log`, `verify.log`, `work/preview/`, `proofs/` and `compare.html` preserve results. The verified bake signature is `9fe8937b0954c6c19f93c2d57e15fe85102d53548bd9b2df18cf33fce04b7f6f`. Existing `assets/walkthrough/`, viewer and vendor bytes stayed unchanged.
