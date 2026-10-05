# Additional interior listing photos

**Bead:** colonial-8d9 · **Date:** 2026-10-05 · **Branch:** main

## Goal and boundary
Add five useful interior views to existing narratives and both galleries. Keep seven approved paragraphs, existing 33 IDs/captions/assets, layout, contact facts and behavior unchanged. Local commit only; no push/deploy. Existing untracked `.beads.gate.lock` is unrelated and stays untouched.

## Source review and selection
Reviewed all 79 images in supplied Zillow listing carousel and 77 owner-supplied JPGs at `/Users/hays/Downloads/listing info/pics`. Matched by content, not filename assumption. Existing local legacy interiors are older and mostly 665px wide; do not reuse them. Selected owner JPGs are 1440px wide, clean photo exports, with existing watermarks retained. No source modification, cropping, generated imagery or remote downloads.

| New stable ID | Owner source | Observed Zillow position | Placement | Caption/alt |
| --- | --- | --- | --- | --- |
| 34 | 55.jpg | 55/79 | Narrative 1, after 3 | Wood staircase and detailed trim in the entry. |
| 35 | 42.jpg | 42/79 | Narrative 2, after 5 | Kitchen island looking toward the dining area and great room. |
| 36 | 50.jpg | 50/79 | Narrative 4, after 7 | Main-level half bath with wood vanity and window. |
| 37 | 51.jpg | 51/79 | Narrative 4, after 18 | Main-floor primary bedroom looking toward the closet and adjoining bath. |
| 38 | 61.jpg | 61/79 | Narrative 4, after 23 | Upstairs full bath with tub and shower. |

New images append to galleries to preserve existing deep links and approved order. Existing context-specific bath/laundry links remain. Narrative order differs from gallery order intentionally. Originals and prior manifest entries remain unchanged. Each added manifest record retains input basename, SHA-256, dimensions, matched source URL, selection/processing details and derivative dimensions/hashes. Existing ImageMagick pipeline produces uncropped quality-78 WebP at 1440px and 720px, without upscaling.

## Implementation and checks
1. Extend existing Python contract with exact new gallery IDs, captions, narrative placements, responsive metadata, asset hashes and original-photo preservation. Update only count-bound expectations in existing Node/browser checks. Observe focused RED before implementation.
2. Add `assets/listing/34–38{,-small}.webp`, append manifest records, add matching static figures to `index.html` and `gallery.html`, update counts to 38 and publication allowlist to 81 files. No new JS/helper abstraction. Browser verification found 38 catalog dots span 264px inside a 244px thumbnail at 320px; one CSS declaration reduces catalog gaps to 1px only at 360px and below. Existing gallery fixture is the RED/GREEN regression.
3. Run `npm test`, `python3 tests/test_listing.py`, `python3 test_design.py`, `python3 test_marketing_plans.py`, `git diff --check`; inspect image dimensions/bytes. Run existing ten browser fixtures plus print-layout geometry and focused added-photo viewer checks at desktop/mobile widths, reduced motion and no-script coverage. Run Impeccable detector once; preserve pinned styles and out-of-scope findings.
4. Update product/design/surface count statements, review diff and obtain bounded code review. Record verification and source provenance in Bead, commit task-owned files, run direct-closeout only on success, then handoff.

## Evidence
Browser source-review proofs under `/Users/hays/.betterwright/artifacts/85b42e1702877c85/`: `pi-evidence-1791222730009-f2a13d.png` (listing), `pi-evidence-1791222934368-ddf5fd.png` (all 79), `pi-evidence-1791222966572-9e2a08.png` (five selections). Source review is not implementation verification. Local comparison sheets: `/tmp/colonial-8d9-current-photos.jpg`, `/tmp/colonial-8d9-local-photos.jpg`, `/tmp/colonial-8d9-supplied.jpg`.
