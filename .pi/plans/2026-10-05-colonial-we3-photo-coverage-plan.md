# Broader contextual photo coverage

**Bead:** colonial-we3 · **Date:** 2026-10-05 · **Branch:** main
**Baseline:** 2695702f6e1d09f6c76ca858edd93aecf37a49c8

## Goal and boundary
Append 35 useful views as IDs 39–73, retaining all 38 existing records/assets, seven exact paragraphs, facts, design and native interactions. No count cap: selection follows visual content and room connections. No dependencies, push or deployment. Unrelated `.beads.gate.lock` stays untouched.

## Source inventory and decisions
`tests/fixtures/photo-coverage.json` inventories every one of 77 listing JPGs plus all five updated owner files. Each record includes source hash/dimensions, section, visual match or addition, and selection/omission reason. It also freezes the canonical JSON digest of the original 38 manifest records. Source names are local identifiers, not Zillow positions; this task claims no new live carousel match.

Reviewed all 38 current images and all supplied sources using fresh contact sheets `/tmp/colonial-we3-{source,current}-*.jpg` and full owner images. All 34 selected listing sources are adequate 1440px-wide originals. Updated `basement2.jpeg` is 3768×2554. Original files remain untouched; retain watermarks, no cropping or upscaling.

Owner clarified this session:
- Only updated owner basement images at `/Users/hays/Desktop/owner photos`; exclude listing 62–65 regardless of alternative angles.
- Updated basement1, laundry and hot tub already match existing 30, 20 and 6. Do not duplicate/reprocess them. Add basement2 as 73. Owner concept plan matches existing 31; do not add another concept.
- Source 43 connects garage/mudroom hallway to kitchen/great room; closed door is pantry, exterior door goes to back porch, powder-room door barely visible. Caption uses confirmed connection. Source 49 uses neutral bench/coat-rack description; no unconfirmed destination.
- Other omissions: 32 repeats frontal approach (30/31 selected); 36 is covered hot tub (existing open tub plus wider 35 selected); 47 repeats porch axis (44, dining corner and reverse end selected); 54 is older laundry; 75 repeats ridge-facing aerial (74/76 selected).

Additions by paragraph (source basenames):
1. 30, 31, 43, 49: approach, entry detail, service circulation.
2. 34, 37, 38, 39, 40, 41, 58: great-room/kitchen relationships and upper windows.
3. 35, 44, 45, 46, 48, 71: deck, porch/daybed/dining and firepit approach.
4. 52, 53, 56, 57, 59, 60: primary bath, upper landing, bedroom and loft connections.
5. 66, 69, 72, basement2: garden/landscape and actual unfinished basement.
6. 74, 76: wider wooded landscape; no claim that a specific park or landmark is pictured.
7. 33, 67, 68, 70, 73, 77: exterior sides, paths/steps, rear porch and wooded setting.

## Minimal implementation and checks
1. Add inventory-backed regression checking every source decision, exact new IDs/captions/placements, both galleries, metadata and old-record freeze. Update count-sensitive tests to 73 (67 homepage inline figures). Observe expected RED before site changes.
2. Generate quality-78 WebP, max 1440/720px (1600/720px for owner basement; foliage-heavy IDs 62, 63, 65, 66, 67, 68 and 72 use 1200/720px to retain quality while meeting the existing 500KB budget), with existing ImageMagick pipeline. Append manifest provenance and static figures to both pages; update counts/search metadata and exact 151-file publication allowlist. Interleave additions after matching existing views per inventory; preserve original figure relative order.
3. Expanded catalog dots exceed fixed width. Reuse existing viewer scaling formula for catalog dots, using actual contained photo width; remove obsolete <=360px gap patch. Keep native interactions and scroll-step duration unchanged. Existing gallery fit fixture is regression; extend sequence test to visit every frame forward/reverse and verify bounded per-photo scroll length.
4. Run `npm test`, `python3 tests/test_listing.py`, `python3 test_design.py`, `python3 test_marketing_plans.py`, `git diff --check`. Verify hashes of local sources and reproduce every new derivative. Check all eleven existing browser fixtures, desktop/mobile appearance, 320px dots, real viewer navigation/focus, fallbacks and print geometry. Record measured sequence lengths, not guesses. Print geometry is not PDF pagination certification.
5. Update PRODUCT.md, DESIGN.md and surface count/coverage descriptions. Run Impeccable detector once, retain pinned design. Obtain bounded peer diff review, resolve findings, commit only task files, record evidence in Bead, direct-closeout and handoff.

## Evidence
Focused verification completed before final candidate gate:
- RED: `python3 tests/test_listing.py Listing.test_complete_source_inventory_and_expanded_coverage` failed because galleries ended at38 instead of73. GREEN: Python15 tests and Node12 tests pass.
- Existing500KB budget rejected seven full foliage derivatives (519–618KB). Trial quality68 still left worst source at554KB; retain quality78 and use1200px full size instead (371–429KB). No budget relaxation. All70 final derivatives reproduced byte-for-byte; all82 source hashes verified; original38 manifest records and76 image files unchanged. New derivatives total12,371,490 bytes.
- Browser `gallery-viewer` initially reproduced catalog overflow at320/390/820/1280px. Scaling fix passed all69 checks, with all73 dots retained. Removed obsolete one-breakpoint gap patch.
- Eleven fixtures passed: gallery-viewer, hero-layout, media-layout, buyer-quality, narrative-scroll (910 assertions, every frame forward/reverse on desktop/mobile), listing-fallbacks, buyer-audit, property-details, buyer-typography, buyer-harden and print-layout. First long scroll fixture wait used wrong wrapper argument position and timed out at5s; page finished and result was read using the correct timeout position. This was not a product failure.
- Actual320px controls: all35 additions decoded with matching source/alt/caption/title on both pages; Next73→1 and Previous1→73 wrap, Escape restores photo39 opener. Tab→Previous and Shift+Tab→Close verified on homepage viewer. Catalog has73 entries, no overflow; final dot row223px.
- At1440×1000, seven sequence counts are7/13/13/14/7/4/8 and section heights4196/7196/7196/7696/4196/2696/4696px. Existing500px photo steps retained; mobile retains422px steps at844px height. Total journey is intentionally longer; direct gallery and normal native scrolling remain available. No scroll interception or new timing.
- Print geometry PASS: homepage one visible photo out of67 source figures in enhanced desktop/mobile and no-script cases; gallery73/73. No new PDF pagination claim.
- Desktop visual proof `/Users/hays/.betterwright/artifacts/85b42e1702877c85/pi-evidence-1791229081852-105b97.png`; mobile `pi-evidence-1791229139722-5c759d.png`; print `pi-evidence-1791229055550-39c9ae.png` in same directory.
- Peer review `findings: []` validated at `.pi/reviews/colonial-we3/findings.json` (subscription GPT, repository read-only). Parent inspected subsequent evidence-only updates. Impeccable detector ran once: eight existing/pinned warnings/advisories (Arial, palette, frozen home-theater copy, summary spacing/leading); no redesign authorized.
- Read-only `agnt doctor --json` after tool-argument errors: no failures; generic missing pytest/check-pi-config warning does not apply to documented unittest/Node project commands. No environment/config changes.

Final candidate gate: run full static matrix and all eleven browser fixtures after staging; record final result/commit in colonial-we3. No push/deployment.
