# Authorized local watermark conversion — colonial-6nu

## Decision and scope

Owner confirmed removal rights and accepted small LaMa corner reconstruction artifacts in colonial-meb, then authorized this implementation. This is owner confirmation, not independent license review. No nanobanana, seasonal regeneration, photo upload, paid processing, dependency installation, push or deployment. LaMa reconstructs covered texture; it does not recover hidden property detail.

Inventory comes from the current `gallery.html` catalog, `assets/seasons-next/frames.json`, page/runtime consumers and `scripts/publish-files.txt`, not from the owner's editable Downloads exports. Those exports were not touched.

| Active masters | Marked, converted | Clean, unchanged |
| --- | ---: | ---: |
| 65 listing photographs/concept image | 57 | 8 |
| 405 non-original seasonal frames | 369 | 36 |
| Total | 426 | 44 |

Clean listing IDs: 5, 6, 7, 20, 25, 30, 31, 73. Clean seasonal frames: photo5 keys3/6/9, all18 photo6 frames, all8 photo25 frames, all3 photo30 frames, all4 photo73 frames. Photo5 key0 was marked and converted. Original seasonal aliases use listing images; no duplicate conversion. Pruned IDs and retired `assets/seasons/` remain untouched.

Replaced 426 full-size WebPs and their 426 small tiers. Rebuilt both existing email GIFs from cleaned hero frames; only the 300×199 GIF is published/used by Open Graph. The 480×318 email version remains outside the publish allowlist. Both retain 120 frames, 200ms per frame, 24-second duration, infinite looping and full framing. Runtime's separate 36-second seasonal timing, manifest, URLs, markup, captions, IDs, viewer targets, visitor mode and no-JS/print/reduced-motion/save-data fallbacks did not change.

## Method and provenance

`docs/watermark-conversion.json` is the complete per-image ledger: source/output hashes, dimensions, half-open mask bounds `[x0,y0,x1,y1]`, mask/master hashes, clean classifications, small tiers, device, encoding error and GIF source mapping. Listing manifest `watermark_removal` takes precedence over Redfin, edited and original historical fields; `previous_derivatives` preserves every prior derivative record. Existing historical fixtures still verify those recovered records, rather than accepting rewritten history.

- Existing `simple-lama-inpainting==0.1.2`, explicit `mps:0`, `PYTORCH_ENABLE_MPS_FALLBACK=0`. CPU handles I/O, masks, compositing and encoding, not inference fallback.
- Checkpoint `big-lama.pt`: SHA256 `7ba7aa7ac37a4d41fdbbeba3a2af7ead18058552997e3a3cd1a3b2210c9e6b4c`; existing runtime/lock/checkpoint provenance under `.pi/research/colonial-meb-lama/`. Research, source URL and license limitations: `docs/watermark-removal-research.md`.
- Full image inference; remove only model padding; composite binary-mask pixels onto original RGB image. Saved lossless PNG dimensions and decoded pixels outside every mask are exactly unchanged.
- Full-size delivery uses ImageMagick WebP quality80 for Redfin listing replacements, otherwise78; small tiers use existing dimensions at quality78, resized from cleaned lossless masters. No master resizing/cropping. The existing general seasonal builder remains available but was not run across clean images.
- **Lossy WebP is not pixel-identical outside masks.** Against the lossless masters, per-image outside-mask mean absolute channel error ranges from 0.630 to 3.552 on an 8-bit scale; worst single-channel difference is47. Those are codec differences, not LaMa editing outside masks.
- GIFs use twelve cleaned integer hero anchors, ten ordinary linear blends per segment, ImageMagick resizing and FFmpeg global palettes (128/96 colors, Bayer scale3). No model used in preview generation. Final sizes: 5,661,330 /1,885,497 bytes, below previous 5,735,599 /1,934,663 bytes.

All active source WebPs, smalls, original manifests and original GIFs were byte-copied and made read-only before replacement at `.pi/artifacts/colonial-6nu/originals/`, retaining repository-relative paths. Lossless outputs and masks live under `masters/` and `masks/` with the same paths and `.png` extensions. `stage/` holds exact installed outputs. These directories are private/ignored and excluded by the publication allowlist; do not delete them during routine cleanup.

Git recovery source before this task: `a26b35cddd9a01abce6dbdaf69e9a62412fd0997`. Original tracked assets remain recoverable there even if private evidence is lost. Restore only explicitly selected task files in a separately approved rollback; do not reset unrelated work.

## Review and checks

Private evidence root: `.pi/artifacts/colonial-6nu/`.

- `active-paths.json`, `reviewed-inputs.json`, `corners-00.png` through `corners-11.png`: individual native-scale source-corner review, including clean classification. `clean-and-annotation.png` shows clean full frames and annotated aerial32.
- `after-00.png` through `after-07.png`: every full-size and reduced delivery corner reviewed. Three rectangular edge artifacts were corrected with expanded individual masks on listing23, listing36 and seasonal22/09; `repair.py`, `before-mask-repair/` and `repaired-corners.png` retain that review and exact execution. Final JSON and mask files supersede those three earlier contact-sheet cells. No visible MLS text or block remains in reviewed final corners. Mild blur, invented seams and varying snow texture remain within owner's accepted corner-artifact threshold.
- Listing32's 120×42 mask avoids its boundary disclaimer; concept31 remains byte-identical. Exact outside-mask master equality also protects every other annotation.
- `gif-all-corners.png`: all240 decoded GIF frame corners reviewed; no residual marks. New global palettes avoid the first staged GIF attempt's size increase; that earlier output is retained privately, not delivered.
- Both staging scripts explicitly reject optimized Python (`-O` / `PYTHONOPTIMIZE`) before imports or side effects, so integrity assertions cannot silently disappear. Both verification suites require exactly the two expected GIF records; empty/partial/duplicate preview coverage fails. Hash-matched executed script snapshots are retained as private `executed-remove-watermarks.py` and `executed-build-watermark-previews.py`; tracked versions add the post-review optimization guard without changing image processing.
- `scripts/remove-watermarks.py` fails closed on existing stage, source/checkpoint mismatch, invalid masks or integrity failures. It stages, never installs. It requires the recorded pre-conversion inputs; do not feed already-cleaned deliveries back into it. For reproduction, prepare a separate checkout of the recovery commit, preserved input manifest/runtime and final reviewed masks; do not overwrite the live private evidence directory.
- `scripts/build-watermark-previews.py` stages previews from verified cleaned masters; refuses an existing output set. `tests/test_watermark_masters.py` independently verifies saved masks, master equality, delivery hashes/dimensions and GIF timing using the existing venv. CI's dependency-free `tests/test_listing.py` checks complete active coverage, current/clean hashes, historical provenance and GIF output hashes.

Commands:

```sh
.pi/research/colonial-meb-lama/venv/bin/python tests/test_watermark_masters.py
python3 tests/test_listing.py
python3 tests/test_build_listing.py
node --test tests/seasonal-assets.test.mjs
npm run test:buyer
git diff --check
```

Focused listing and seasonal asset checks passed after installation. Full buyer/browser closeout evidence is recorded in colonial-6nu and private `buyer-gate.log` / browser proof artifacts. No physical iPad/Safari, prolonged device playback, OS backgrounding or production deployment verification; unrelated halt investigation remains colonial-tyl.
