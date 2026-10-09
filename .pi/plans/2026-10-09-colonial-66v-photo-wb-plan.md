# Loft and great-room private white-balance batches

**Issue:** colonial-66v (open)
**Date:** 2026-10-09
**Branch:** main
**Goal:** Review 24 warmth-only seasonal candidates for loft21/22/57/59 and great-room02/12/13/14. Owner prefers C; originals and delivered assets unchanged.

## Smallest boundary

- Extend `scripts/seasons/lighting_reference.py` with `--areas`: existing four loft views plus existing great-room02/45 camera poses, four anchors only, separate private `areas/` output. Same house/fixture inputs. The p12_down pose was tried but rejected as effectively black/occluded; p45_north supplies the second ground-level reference. No model or material revisions. Existing timeline evidence remains historical and is not overwritten.
- Add `scripts/seasons/photo_wb.py` and `tests/test_photo_wb.py`. Reuse recorded C matrices at0/3/6/9 to display new area renders under same AgX and a common +2 reference-sampling exposure (two stops below earlier overbright diagnostic previews). Derive relative seasonal warmth from common unclipped ray-sampled ceiling/paint pixels, averaged equally per room group. C is one photographic treatment; room responses remain different. At least20 common samples per view and two usable views per room are required; rejected views are recorded.
- Owner requested three white-painted patches per photograph: use per-channel pixel median within each patch, then equal-weight per-channel median across three. Coordinates match across original and seasonal images. Owner rejected literal model strength after orange/clipped trial and selected subtle photo-led targets. Scale model shifts so the warmest room's winter target is10% higher linear R/B than its original; retain relative room/season variation. Target = original median-reference log(R/B) + scaled seasonal change. Apply one linear-RGB red/blue gain parameter, preserving G/sqrt(R*B) (no independent tint correction) and median-reference luminance before clipping. This is a declared photographic warm/cool axis, not measured CCT or a raw-camera Temperature control.
- Use current delivered seasonal images as exact before inputs; save full-size lossless candidate PNGs privately. This is a review trial, not final export from lossless masters. Originals remain source references only. No per-pixel exposure fitting, structural changes, generation, installs or deployment. Global correction also affects windows; inspect and hold where masking is needed rather than silently call it production-ready.
- Record source/output hashes, model samples, patch coordinates, gains, target/achieved warmth, clipping and residual tint diagnostics. Private review pages show original/current/candidate, with phase/photo labels and targets. No owner acceptance inferred.

## Verification

1. RED/GREEN math tests: warmth target, unchanged tint axis and sample luminance, identity, invalid input rejection.
2. Real Blender `--areas` run and photo batch; require finite renders, sufficient common unclipped painted samples,24 outputs at original dimensions, unchanged input hashes.
3. Inspect patch sheets and each season's before/after contact sheets; verify local review page images and disclosed limits in browser.
4. Stage owned paths only; inspect diff; final tests plus npm/listing/design/marketing/810tier gates. Local commit and Bead checkpoint; no closeout while overallQA/photo73 remain open.

## Checkpoint

Observed RED/GREEN for missing warmth helper, photo-led scaling and three-patch median. Initial implementation peer10497419 found no concrete math/colorspace/source-protection bug; later median addition has focused outlier/invalid-count tests. Real area model and photo pipeline execute successfully after rejecting an occluded p12 camera and overexposed reference samples. Read-only agnt doctor: no core failures; existing missingpytest/check-pi-config warnings. No installations/config changes.

Current private output contains24 full-resolution PNG trials, six season/area contact sheets, two HTML review pages and hash-bound recipe. Model samples common across anchors:21=1063,22=1133,57=1691,59=2327,02=1110,45=768. Scaled logR/B shifts (original/fall/winter/spring): loft0/.04025/.09509/.01628; great-room0/.01641/.09531/.00725. These are artistic preview settings, not calibrated room-temperature claims.

Three-patch crop sheet inspected. Largest channel-overflow footprint is about1.55% of pixels in59spring, principally bright regions; global correction also alters exterior color. These remain review trials, not delivery-ready grades. Photo57's strongest orange cast is reduced without independent tint fitting; owner acceptance remains pending. All delivered files and originals remain unchanged. Full-resolution/transition QA and potential masks remain open.

Approximate model materials/weather and display tone mapping limit target precision. Source photographs are already edited, so neither absolute model colors nor physical WB matrices are applied directly to them. Independent tint edits and masks require a visible need and separate review.
