# Narrative crossfade compositing

**Bead:** colonial-y9y
**Date:** 2026-10-08
**Branch:** main

## Goal and boundary

Remove the background pulse during scroll-linked crossfades without changing native scrolling, photo identity, aspect ratios, captions, focus, seasonal timing, or fallbacks. Owner approved implementation and one local task-owned commit; no push/deployment. Existing unrelated untracked `.claude/`, `MEMORY.md`, and `.beads.gate.lock` stay untouched.

## Approach and scope

Use `mix-blend-mode: plus-lighter` on scroll-photo links inside an isolated transparent `.story-photos` group, subject to real browser pixel verification. Complementary premultiplied colors/alpha add to one where images overlap; non-overlapping contain-fit edges blend to the section background. Keep seasonal source-over stacks isolated inside each link. Retain normal rendering outside enhanced sequences and in print.

- `listing.css`: shared compositing boundary and link blend mode only.
- `tests/crossfade-pixels.html`: real homepage/listing.js with deterministic solid-color images; seek forward/reverse, same/mismatched aspect ratios, desktop/mobile, and frozen seasonal midpoints (the actual runtime uses inline opacity while paused). Export independent expected screen-pixel probes.
- `tests/check_crossfade_pixels.py`: check captured browser PNG against exported probes using existing ImageMagick; no new dependency.
- Existing narrative and seasonal fixtures: verify actual runtime, accessibility, geometry and fallbacks.
- `DESIGN.md` / `PRODUCT.md`: record compositing and repeatable verification.

## Sequence and acceptance

1. Add pixel fixture/checker; capture current homepage rendering and observe midpoint assertion failure.
2. Apply CSS correction. Prove midpoint weights, endpoints, quarter blends, transparent letterboxes, reverse scroll and nested seasonal layers in desktop/mobile captures.
3. Assess easing after correction. Keep existing direct linear mapping unless concrete residual evidence justifies changing its approved behavior; no timed catch-up.
4. Run Node/Python regressions and relevant browser fixtures; document baseline failures separately. Review diff, commit only task files, and direct-closeout Bead.

## Verification

```sh
node --test tests/*.test.mjs
python3 tests/test_listing.py
python3 test_design.py
python3 test_marketing_plans.py
python3 tests/check_crossfade_pixels.py SCREENSHOT.png PROBES.json
```

Local browser fixtures: `tests/crossfade-pixels.html`, `tests/narrative-scroll.html`, `tests/seasonal-runtime.html`, `tests/resize-reading.html`, `tests/media-layout.html`, `tests/listing-fallbacks.html`, and `tests/print-layout.html` (print-media phase). Pixel capture uses the browser tool, not canvas reimplementation of CSS. Existing seasonal suite previously produced one tab-resume assertion failure; investigate/isolate rather than silently treating the suite as passing. Physical-device/Safari rendering is outside available Chromium evidence.

## Focused evidence and decision

- RED: five overlapping midpoint probes differ from independent 50/50 swatches; background probe passes. Captures and probe JSON: `.pi/artifacts/colonial-y9y/red.*`.
- GREEN: same fixture passes after two CSS declarations plus explanatory comment. Desktop/mobile endpoint, quarter, midpoint, reverse, mixed-aspect and nested-season cases pass; private captures/probes in `.pi/artifacts/colonial-y9y/`.
- Test calibration: capture color management transforms literal RGB values, so compare against opaque reference swatches within the same capture. Capture tool finishes paused WAAPI animations; use runtime-equivalent frozen inline opacity for pixel cases. Moved bottom probe horizontally clear of mobile position dots, retaining the same contain-fit region.
- Easing decision: retain existing linear scroll mapping. This fix removes measured background contamination without altering native input response, caption switching or reading-position fractions. No evidence justifies broadening this bugfix into new timing behavior.
- Subscription-backed read-only peer review: PASS, no significant findings in CSS/compositing or pixel checker. Result persisted at `runtime:delegated-results/858079ac-a8e1-4c1f-ad1e-74382b7f41f6/child-0.json`.
- Baseline shell matrix: 34 Node tests, 16 listing Python tests, design and marketing checks all pass.
