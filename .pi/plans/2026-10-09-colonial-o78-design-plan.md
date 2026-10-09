# Remaining audit findings implementation plan

Issue: colonial-o78. Branch: main. Design: included Bead scope. Date: 2026-10-09.

## Boundaries
Preserve completed findings 1–7 and exact buyer behavior. No new dependencies, runtime rendering, asset changes, provenance publication, API generation, downloads, full-scene bakes, push or deployment. Unrelated untracked files untouched.

## 8: Offline photo authoring
Current manifest contains captions/current dimensions for all photos; repeated static figures in hero, seven stories and two catalogs warrant one authoring path. Add scripts/build-listing.py with explicit stable placement lists, fixed figure variants, explicit comment-delimited replacement ranges and --check. Bootstrap marker locations with HTMLParser; reject missing, reversed or overlapping boundaries. Keep all non-figure bytes, prose and page shells untouched. Use manifest whitelist fields only, escape text, validate paths/positions/dimensions. Independent approved-listing and other fixtures remain unchanged. Tests compare generated figures to existing HTML before replacement, test idempotence, changed metadata propagation, escaping and invalid inputs. Add check to buyer Python gate and document authoring command.

## 9a: Pilot paths
Correct ROOT by one level; OUT defaults to ignored .pi/artifacts/seasons, optional explicit private scratch environment path. Separate source directory HERE from OUT. Fix hero_half.py, hero_relight.py and tween.py align executable references. Reject scratch paths outside ignored artifacts when inside repository and reject tag traversal before writes/API calls. Import and sun CLI remain offline/no-write. Test with network/subprocess guards and temporary scratch.

## 9b: One concurrency owner
Remove align.measure's inner eight-thread pool; existing frame-level callers own parallelism. No scheduling abstraction or worker options. Preserve ordered patches, affine fit, fewer-than-12 rejection and residual measurement. Regression checks run concurrent measures with deterministic subprocess double; actual bounded existing-input comparison runs two frames concurrently, same machine/input, before and after. Record time, peak live ImageMagick children, fit JSON and pixel hashes; no buyer performance claim.

## 9c: Blender allocation
Keep page_imgs dictionary keys for every non-fx page, values None without --bake; allocate real targets only when --bake is requested. Existing encode/export iterate keys and keep signatures/stale checks. Real Blender regression checks export metadata/UV/geometry/material identity; tiny synthetic 64px one-page bake/encode verifies active BAKE nodes and finite pixels. Full scene export-only run uses fresh scratch with synthetic local HDRI/textures if necessary, never overwrites existing bakes. Measure process peak RSS before/after under same conditions; fingerprints intentionally invalidate on source changes.

## Verification and closeout
Regression-first tests per finding. Baseline once, then focused checks and final npm run test:buyer, npm run test:tooling, tests/test_export_wb.py, test_marketing_plans.py, tests/test_walkthrough_tools.py, tests/test_walkthrough_blender.py and added authoring tests. Independent routed repository review, resolve findings, task-owned atomic commit, full numbered disposition/evidence in Bead, direct-closeout and handoff.

Initial baseline Node/Python/design pass; browser launch blocked by installed Playwright 1.63.0 vs lockfile 1.64.0. Re-enter project nix develop rather than change dependencies or download browser. Installed Chromium cache includes build1248. agnt doctor reports no failures, unrelated generic verification prerequisites warning.
