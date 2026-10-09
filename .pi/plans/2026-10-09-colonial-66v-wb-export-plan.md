# Approved warmth export implementation plan

Issue: colonial-66v. Date:2026-10-09. Branch:main. Base:19ae8ba.

## Goal and approved boundary

Owner accepted B loft/great/kitchen, remaining interiors and revised upstairs bath; owner accepts clipping appearance on37winter/36fall. Owner requests moving forward with settings without another extensive transition review. Apply locally to existing seasonal exports, not originals/gallery, captions, runtime or manifest mapping. Deployment is desired next but needs target-bound approval after exports/checks. No paid generation or physical rerender.

## Smallest approach

- Add `scripts/seasons/export_wb.py` and `tests/test_export_wb.py`. Reuse `photo_wb.reference_rgb` and `warmth_gains`, existing ImageMagick, existing large quality80/small quality78 recipes. No dependencies.
- Read frozen accepted `B-reviewed`, `kitchen-B-reviewed` and latest `interiors-B` recipes/PNGs. Validate hashes before changes. Explicitly allow only37-06 and36-03 clipping holds as owner-reviewed; all other held/null/unchanged-source photos stay unchanged for their whole sequence. Basement and photos without approved references unchanged.
- Preserve complete pre-WB seasonal tree and original/gallery hashes privately at `.pi/artifacts/colonial-66v-photo-wb/export/source/`; persist immutable input recipes/PNG references and hashes. Repeated execution uses this snapshot, never corrected delivery files as inputs; fail on unexpected input/output drift.
- At3/6/9 use exact reviewed PNG pixels as lossless working masters. At other generated keys fit three reference patch medians to target log R/B interpolated across0/3/6/9/12 on manifest's equal-duration knot timeline. At0 target original photographic reference (not camera Kelvin); manifest original keys remain untouched. Photo38 has only original0 and3/6/9, so revised doorway-wall winter target needs no mixed-reference interpolation.
- Preserve generated scene/crop/dimensions; no masks, independent tint, spatial changes or model rerender. Retain corrected PNG working files privately and encode quality80 large; resize corrected large to exact original-small dimensions, quality78. Make candidates privately and verify complete batch before replacing task-owned local files.
- Record per-frame before/after hashes, recipe hashes, reference, gains/target, clipping/encoding metrics, dimensions and source mapping. Produce private before/after review from frozen inputs. Historical preview recipes remain immutable; their original source hashes describe pre-WB files, recoverable from snapshot.

## Verification

RED/GREEN unit tests: timeline interpolation with nonuniform numeric knots and wrap, exact anchors, invalid phases/values, approved held exceptions and fail-closed transfers, manifest scope/original exclusions. Real export verifies anchors from approved PNGs, expected changed-file set, all unrelated seasonal files and146 listing derivatives unchanged, both tier dimensions, finite metadata, no manifest change and idempotent regeneration. Inspect representative bathroom/loft/porch before/after; no exhaustive449-transition certification.

Commands: `python3 tests/test_export_wb.py`; `python3 tests/test_photo_wb.py`; `python3 scripts/seasons/export_wb.py` (private preparation); `python3 scripts/seasons/export_wb.py --apply` (local seasonal replacement); `node scripts/build-seasons-small.mjs --check`; `npm test`; `python3 tests/test_listing.py`; `python3 tests/test_walkthrough_tools.py`; `python3 test_design.py`; `python3 test_marketing_plans.py`; both git diff checks.

Commit only exporter/tests/plan and bounded seasonal large/small outputs. Record checkpoint in Bead. Do not claim full asset QA/closeout while basement content repair/unreliable porch corrections remain unresolved. Identify deployment target and exact source/scope before durable approval request.
