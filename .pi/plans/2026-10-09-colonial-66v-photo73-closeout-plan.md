# Photo73 repair and colonial-66v closeout

**Issue:** colonial-66v
**Branch:** main
**Goal:** install owner-approved four-anchor photo73 repair, verify bounded change, close asset work with explicit review exceptions.

## Accepted scope

Owner approved private `.pi/artifacts/colonial-66v-photo73-repair/review.jpg` and four PNG masters after requesting doorway clutter removal. Summer removes bags/hose/shop-vac/tools/mat; seasonal frames restore the paved landing. Interior storage/furniture and original/gallery photos remain untouched. Pixels outside repair masks match their respective sources exactly. Reconstructed ground beneath clutter is not measured ground truth.

Use `assets/seasons-next/73/{00,03,06,09}.webp` and matching small files. Existing recipe: large WebP quality80, small quality78 resized from large to original-small dimensions. Change only photo73 in `frames.json` to keys0/3/6/9, original=[]; untouched gallery73 remains fallback. Update `scripts/publish-files.txt` accordingly. Archive then retire tracked08/08-small from seasonal export directory (strict inventory rejects unused files); recoverable from e046fb0a0545e9cbf390c9683fc5c9c4bdb62c4c and private backup. Preserve every private master.

## Verification and closeout

- Add focused manifest/generated-summer/publication regression in `tests/seasonal-assets.test.mjs`; observe RED before installation, GREEN after.
- Check approved master hashes, exact8 output dimensions, encoding RMSE, all original hashes and all non73 seasonal hashes unchanged; allowlisted build exactly matches source. Preserve private provenance/export report.
- Run Node suite, Python listing/export-WB/photo-WB/walkthrough tools, design/marketing checks, full seasonal dimension/inventory check and both diff checks. No runtime changes or new dependencies.
- Refresh QA continuity: kitchen/revised bathroom/porch appearance accepted, delivery verified; exhaustive frame/transition review explicitly skipped by owner for these repairs, not falsely certified. Previous detailed QA inventory remains historical. Basement30 unchanged; no further basement grading requested.
- Commit only task-owned change; direct-closeout after final gates. No new push/deployment authority. User requested close after this repair, not another full-set review.
- After66v closes, create successor for small always-visible mono/two-color mechanical seasonal-clock indicator integrated with accessible Pause/Resume; handoff to implement. Preserve reduced-motion, keyboard/focus, screen-reader and shared-clock behavior.
