# colonial-66v: asset QA and repair record

## Current status

**Open: exhaustive asset QA remains a completion gate.** On 8 October 2026 the owner explicitly chose to go through the photos, recording exceptions, clarifications or repairs. Broad prior grid acceptance is not a waiver of unreviewed defects. No new generation, publication, push or deployment is authorized by this record.

Recovery sources: `bd show colonial-wtm`, `bd show colonial-66v`, their referenced pilot and architecture artifacts. No earlier transcript or unrelated memory was recovered. Existing untracked `.beads.gate.lock`, `.claude/` and `MEMORY.md` remain untouched.

The settled contract is [colonial-wtm's evaluation](2026-10-07-colonial-wtm-seasonal-architecture.md): 36-second year, sparse 18/12/9/6/5/4 keys on the nonuniform 12-step timeline; 65 retained catalog IDs. Its full 73-ID treatment table remains authoritative. Approximately 24 generated frames and a 24-second year are historical proposals, not current requirements. Runtime/catalog integration belongs to the previously closed follow-ups, not this asset repair.

## Photo02 dimension repair

- Defect: large keys `03`, `06`, `09` and their retained lossless masters were 1280×852; original is 1280×851. Existing small-tier checker warned but exited successfully. Exact historical generation command causing the extra row was not recovered.
- Repair: existing `.pi/artifacts/seasons-pilot/fin/02/KK.final.png` masters resized to **1280×851!**, metadata stripped, WebP quality 80 using existing ImageMagick recipe. No crop, generative edit or invented field of view. Lossless sources unchanged. These masters match the corresponding staged post PNGs; old review WebPs were byte-identical to delivered exports. The old encoding was not reproduced byte-for-byte, so this is a fresh encode, not a claimed lossless WebP edit.
- Corresponding three small exports refreshed from repaired large files to **720×479!**, strip, quality 78, matching `scripts/build-seasons-small.mjs`. Only six delivered image files changed.
- `scripts/build-seasons-small.mjs --check` now treats large dimension mismatches as errors, just like small-tier mismatches; generation skips invalid large inputs.
- `tests/seasonal-assets.test.mjs`: real-inventory test plus isolated wrong-size-large/valid-small fixture. RED: both failed for the known warning/success behavior. GREEN: both passed after repair/checker change. All 810 generated exports pass the existing checker. SHA256 before/after comparison confirms all 146 local listing derivatives unchanged, including retained and pruned originals.
- Browser inspected photo02's six 50% adjacent blends at 1280px: 0→3, 3→5, 5→6, 6→8, 8→9 and 9→0. No obvious doubled fixed edges/crop jumps in window trim, picture, hearth and furniture. Seasonal trees, sunlight and reflections overlap. This is **static midpoint inspection**, not numeric registration measurement, small-tier visual approval or repeated-cycle temporal certification.

Repair provenance, before/after hashes and exact commands: `.pi/artifacts/colonial-66v-closeout/repair.json`. Initial inventory: `before.json`. Tool version is recorded there. `qa-inventory.json` records all 450 current keys (405 generated) and 449 adjacent transitions, with hashes and unchecked gates explicitly pending; only photo02 large static midpoints have a fresh inspection disposition. Browser proofs copied as `02-0-3.png` through `02-9-0.png`, plus `02-dimensions.png`, avoiding browser rolling-quota loss.

### Refreshed measured inventory

| Tier | Frames | Bytes | Largest frame |
| --- | ---: | ---: | ---: |
| Large | 405 | 104,467,408 | 530,288 |
| Small | 405 | 30,119,880 | 138,142 |
| Combined | 810 | 134,587,288 | — |

Manifest unchanged: 54 entries, 53 changing plus original-only 55; 450 total mapped keys including originals. Architecture's earlier totals are explicitly pre-repair measurements. Tree remains below proposed 300 MB; some frames still exceed proposed 350 KB large / 120 KB small limits. Those were unaccepted proposals, not certified device/release budgets. No silent re-encoding of other assets to meet them.

## Sweep dispositions

| Item | Disposition and evidence |
| --- | --- |
| 25 missing keys 1/2/4 | Explicit prior as-is acceptance preserved; nine-key mapping unchanged. |
| 26 winter plant and other remaining differences | Explicit prior as-is acceptance preserved. |
| 28 top-edge sky at 1/2 | Explicit prior as-is acceptance preserved. |
| Hero plant/calendar and other differences | Explicit prior as-is acceptance preserved. |
| 33 winter lights | Removed from animation under separately owned catalog work; original gallery-only. |
| 46 first snow | Prior pilot records regenerated frame, 0.0px / 29 of 29 matches; not independently remeasured in this pass. |
| 39/41 thaw paving | Prior final pilot records recheck against originals with no invented paving; not a blanket all-frame approval. |
| Remaining exterior/porch thaw | New original/7/8 contact-sheet check for 04,06,10,11,17,27,29,43,50,51,52,53,64,65,66,67: no obvious added paving at 440px per tile. Original stone paths, driveway, terrace and wood deck remain recognizable. Contact-sheet scale does not establish full-resolution detail, registration, every window or transition fidelity. Photo66's foreground stump also exists in the full-size original. |
| Kitchen05 refrigerator reflection | Still open. Original/fall/winter/spring sheet shows similar bright vertical streaks despite exterior changes. No physical-accuracy or owner-acceptance claim; review with owner alongside related kitchen views. |
| Basement73 missing first snow | Owner now chooses **four seasonal anchors 0/3/6/9**, not five keys with 8. This is repair direction only; delivered manifest unchanged pending replacement/review. |
| Basement73 clutter and landing | **Held for repair/review.** Full-size original and fall comparison confirms generated fall removes bags/hose/vacuum/doormat and replaces original paved landing with leafy ground. Contact sheet also shows uncluttered winter/thaw/spring. Owner selected replacement of cluttered summer0 with a reviewed uncluttered variant, retaining 0/3/6/9 and preserving original paving in every generated frame. Do not remove gallery original or silently approve permanent-surface changes. No paid generation authorized yet. |

Thaw sheets: `.pi/artifacts/colonial-66v-closeout/thaw-1.jpg` through `thaw-4.jpg`. Each row is original, step7, step8; row groups respectively `04/06/10/11`, `17/27/29/43`, `50/51/52/53`, `64/65/66/67`. `05-sheet.jpg` is original/3/6/9; `73-sheet.jpg` is original/3/6/8/9. These are review evidence, not all-set approval.

## Remaining gate and next review

1. Owner-assisted room/view review, beginning with basement73 repair direction and kitchen05/35/47/48. Record item-specific accept/fix/hold; retain existing explicit exceptions above.
2. Before production repairs, settle exact generation scope and bounded authorization. Photo73 needs a clean summer key, restored paved landing across generated anchors, and removal of key8 only after reviewed replacement is ready. Update both tiers, manifest and allowlist together only within approved integration scope; do not orphan or delete private masters.
3. Establish numeric fixed-landmark tolerance/method and bathroom daylight reference explicitly. Prior pilot contains many edge-fit and overlay results, including uncertain low-match frames; these do not equal a complete final per-frame QA ledger. Never interpret low matches as automatic failure or pass.
4. Inspect every final frame at full size and display sizes; all windows/reflections/lighting and related views; every adjacent transition, midpoint, repeated cycles and wrap. Photo02's six static midpoints and thaw contact sheets are the exact fresh visual coverage so far, not exhaustive proof.
5. Preserve per-frame source/provenance/hash mapping and contact sheets. Existing generation logs/prompts and lossless masters remain in `seasons-pilot`; export hashes alone cannot reconstruct every frame's generative lineage. Complete coverage is still unverified.
6. Run final regressions, commit owned changes, then close only after these gates or explicit owner-recorded exceptions. Integration/runtime device performance and publication remain separate.

## Private preview and verification

Reuse of the prior review page, pointed at current delivered exports with manifest-derived original-key resolution:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/.pi/artifacts/colonial-66v-closeout/review.html?only=73` or `?only=05,35,47,48`. Snapshot manifest is embedded; refresh the copy when manifest changes. Original pilot page/assets remain untouched. Preview is a local QA artifact, not new production UI. All 450 preview key paths were checked to exist; inspect original keys as well as generated keys before relying on a review grid.

Commands for the bounded dimension repair:

```sh
node --test tests/seasonal-assets.test.mjs
node scripts/build-seasons-small.mjs --check
npm test
python3 tests/test_listing.py
python3 test_design.py
python3 test_marketing_plans.py
git diff --check
```

Focused regression and inventory checks passed. Full candidate results are recorded in the Bead after running. No full runtime/device matrix or unrelated Blender dependency installation. Two browser batch-schema errors prompted read-only `agnt doctor --json`: no core failures, generic missing pytest/check-pi-config warning; switched to documented direct locators, changed no home configuration.
