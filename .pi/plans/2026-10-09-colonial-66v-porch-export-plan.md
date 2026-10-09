# Approved porch WB export plan

Issue: colonial-66v. Date:2026-10-09. Branch:main. Base:2f33c5895bbf0e69031081b15ebd7051f68091dc.

Owner approved porch-matched previews after requesting consistency across all six porch views. Scope is44 generated frames /88 large-small WebPs for17/51/52/53. Original phase0, gallery/listing, approved04/50, previous129 warmth-corrected frames, manifest, runtime, captions and other assets remain unchanged. No masks, independent tint, geometry edits, Blender or paid generation. New production publication requires separate exact approval.

## Implementation

Private reproducible processor/checks and evidence at `.pi/artifacts/colonial-66v-photo-wb/porch-export/`; accepted source is sibling `porch-matched/recipe.json` and12 PNG anchors. Reuse existing `export_wb` IO/dimensions/interpolation helpers and `photo_wb.warmth_gains`. Do not weaken automatic wood-transfer guards or rerun historical exporter against newly changed delivery.

1. Freeze accepted recipe/anchors plus44 large/44 small source files and hashes before any local replacements. Verify accepted preview against its recipe. Persist owner acceptance and base SHA.
2. Copy exact accepted PNG masters at3/6/9. Other generated keys interpolate manual log-R/B correction deltas across0/3/6/9/12 using elapsed shared-clock knots, zero correction at original summer/wrap. Preserve whole-image mean linear luminance with same warmth-only helper as previews. Never fit disputed wood targets or stack corrections.
3. Produce private16-bit PNG masters, quality80 large WebPs; resize large to unchanged small dimensions, quality78. Record gain, clipping, dimensions, hashes and encoding error. Stop on unreviewed clipping beyond max(2%,approved anchor maximum)+0.5%, pixel/dimension/scope drift or input changes.
4. Verify complete candidate scope before local replacements; allow only frozen-old or exact-candidate current bytes for idempotent application. Never initialize missing snapshot during apply/check. Verify every unaffected input remains identical. Repeated preparation must reproduce output hashes. Apply only88 explicit files and verify installed state.
5. Inspect all44 corrected frames by per-photo timeline sheets and representative full-size intermediate/before-after views. No claim of exhaustive inherited449-transition/fidelity QA. Record limits and Bead checkpoint; commit only88 images and this plan.

## Verification

Private assert-based check first fails for missing report, then proves exact44/88 scope, original-key exclusion,6/9/3 anchor byte equivalence, frozen sources, target gains, output hashes/dimensions, encoding and all unaffected public inputs. Exercise fail-closed missing/stale/tampered report in isolated copies or read-only validation; no unsafe live test mutations.

Commands: `python3 .pi/artifacts/colonial-66v-photo-wb/porch-export/export.py`; sibling `check.py`; exporter `--apply` and `--check`; `python3 tests/test_export_wb.py`; `python3 tests/test_photo_wb.py`; `node scripts/build-seasons-small.mjs --check`; `npm test`; `python3 tests/test_listing.py`; `python3 tests/test_walkthrough_tools.py`; `python3 test_design.py`; `python3 test_marketing_plans.py`; `git diff --check`; `git diff --cached --check`; `node scripts/build-pages.mjs <new-private-output-dir>`.

After local commit, approval must bind exact source SHA, origin/main URL and expected remote SHA,88-file buyer delta, ordinary single push triggering existing Pages deployment, evidence, rollback via separately approved forward commit and stop-on-drift. Verify successful workflow and live files after approved push. Broader Bead remains open for unrelated photo73 repair and inherited QA.
