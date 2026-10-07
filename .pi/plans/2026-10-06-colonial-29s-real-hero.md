# Approved real-homepage seasonal hero

Bead colonial-29s. Local implementation only; keep open for owner visual review. No push, deployment or handoff.

Outcome: image-only uncropped hero, twelve approved scenes in a continuous 24-second loop. One footer pause/resume button; no scene labels, timing form or hero caption on screen. Print retains original photo and caption. Mock stays unchanged.

Smallest boundary: isolated seasonal-hero.js loaded only by index.html, scoped listing.css rules, existing hero link with explicit data-seasons paths, footer button. Copy eleven selected WebPs byte-for-byte to assets/seasons; reuse assets/listing/01.webp as summer and fallback. Original gallery/narrative/assets/analytics untouched. No dependency or persistent preferences.

1. Add failing tests/seasonal-hero.html regression using actual homepage and deterministic browser fallbacks; publication test requires explicit paths.
2. Decode generated layers only after original hero loads and when motion/data preferences allow. Enable all layers atomically after successful decoding; native opacity Web Animations, shared 24s phase and additive blending. Pause offscreen, hidden, in print and under dialogs; footer pause survives those lifecycle changes. Reduced motion restores original image. Failed decode leaves original and no button.
3. Extend exact publish allowlist, provenance and PRODUCT/DESIGN/surface contracts for this narrow exception. Record inherited strict v4 alignment failures without claiming registration certification.
4. Verify Node/Python regressions and browser fixtures, all adjacent fades/wrap, pause, fallback/error paths, original viewer, mobile/desktop and print. Independent scoped review. Commit task-owned changes locally; show localhost preview, leave Bead open.
