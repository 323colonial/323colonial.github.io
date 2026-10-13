# Authorized watermark conversion

**Issue:** colonial-6nu
**Design:** docs/watermark-removal-research.md
**Date:** 2026-10-13
**Branch:** main

## Goal and boundary
Remove owner-authorized MLS marks from active photographs with existing local LaMa MPS, preserving clean assets, framing, captions, IDs and runtime behavior. No installs, uploads, nanobanana, push, deployment or colonial-tyl investigation. Small corner artifacts accepted; residual marks and outside-mask generation are not.

## Inventory and implementation
- HTML catalog: 65 stable IDs; listing manifest retains 73 historical records. Listing consumers: index.html, gallery.html, gallery.js, listing.js, visitor-display.js, seasonal-hero.js (original aliases), no-JS/print/reduced-motion/save-data fallbacks. Keep markup/runtime unchanged.
- assets/seasons-next/frames.json: 54 photos, 405 non-original full-size frames and matching smalls. Preserve manifest/timing and original aliases.
- scripts/publish-files.txt and tests/seo.test.mjs enumerate 130 listing images, 810 seasonal images, small OG GIF. assets/email also contains full email GIF; inspect both frame geometry/timing and rebuild from current cleaned hero frames.
- Preserve all active source bytes, manifests and GIFs under ignored .pi/artifacts/colonial-6nu/ before any replacement; retain lossless outputs/masks/reports there. Do not touch Downloads exports.
- Individually inspect 470 active masters (65 listing +405 seasonal); record clean/masked classification and exact half-open mask bounds in docs/watermark-conversion.json. Contact sheets are private review evidence, not replacements.
- Use existing .pi/research/colonial-meb-lama/{venv,big-lama.pt,requirements-lock.txt,checkpoint-provenance.json,validate30.py}. Full-image inference, padding removal only, binary composite. Fail closed on checkpoint/source mismatch; explicit MPS with CPU fallback disabled.
- scripts/remove-watermarks.py: bounded conversion driven by reviewed inventory; self-check exact mask/dimension/source/output invariants. ImageMagick WebP delivery and affected small tiers. Reuse established 720w dimensions and seasonal quality78 recipe; no clean-image rewrite.
- assets/listing/manifest.json: watermark_removal record with previous_derivatives; current derivative hashes updated, historical source fields unchanged. tests/test_listing.py recovers historical baseline before watermark layer then Redfin. New coverage/integrity tests join existing buyer gate.
- PRODUCT.md / DESIGN.md: explicit owner exception, current-source precedence, retained source and synthetic-detail limits. docs/watermark-removal-research.md stays historical research; new conversion report references it.

## Verification
- Fail-first provenance tests, then complete classified coverage/hashes and unchanged clean/pruned files.
- Every processed master: source copy byte equality; mask binary and exact reviewed bounds; unchanged dimensions; exact decoded outside-mask equality in saved PNG. Delivery codec changes reported separately.
- Review every marked output corner and clean input, reduced tiers and GIF frames; sample seasonal blends, annotation preservation.
- python3 tests/test_listing.py; python3 tests/test_build_listing.py; node --test tests/seasonal-assets.test.mjs; npm run test:buyer; git diff --check.
- Local browser normal/mobile/visitor/gallery and seasonal/fallback fixture evidence. Physical iPad not available; no hardware certification.
- Review owned diff; record evidence in Bead; local atomic commit; agnt work direct-closeout colonial-6nu --outcome success --reason ...; handoff_bead. Stop on incomplete coverage or failed gates.
