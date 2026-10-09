# Seasonal instrument — design and implementation

Issue: colonial-ykx. Date: 2026-10-09. Branch: main. Local only.

## Goal / direction
A small house-clock-like instrument makes the shared photographic year legible and motion control reachable throughout reading. Keep the incumbent palette/composition. Greek Villa strokes on Pewter Green, four authored SVG seasonal marks and one balanced hand; a plain Pause/Resume label completes one native button. No new images, dependencies, telemetry, timers, persistent state or gallery changes.

## Boundary and smallest implementation
Move existing #hero-motion from footer into masthead. Desktop sits beside contact block; mobile uses a reserved right column beside address/contact, not an overlay. At <=500px height keep existing scrolling header/facts fallbacks and use a 44px bottom dock with page-end and focus clearance. Native dialogs remain in top layer; control hides while modal open. Reduced motion, save-data, no-JS, failed manifest and print keep originals/hidden device.

Hand rotation uses KN/N phase, DUR[seg] and exact shared startedAt with one finite Web Animation. No independent year or rAF. Controls reconciliation cancels hand animation when frozen and paints held phase. Quarter transitions update accessible description (summer toward fall, etc.), not per-frame announcements. Existing action name and stalled recovery remain, with visible Pause/Resume and hidden “animation” qualifier.

## Sequence / files
1. Extend tests/seasonal-runtime.html before implementation: persistent control structure, sampled computed hand rotation vs shared phase, every segment and wrap, delayed/hung/failed loads, pause and lifecycle. Observe expected RED.
2. Change index.html, listing.css, seasonal-hero.js only for device; run same fixture GREEN. Existing callers: CSS #hero-motion and fixture text/description checks; no export/config changes.
3. Browser desktop/mobile actual page, keyboard Space/Enter, contact/focus separation, viewer, short viewport, reduced motion and print. Run Node, listing Python, design/marketing checks; relevant browser geometry fixtures. Run Impeccable detector once. Scoped independent review.
4. Update current PRODUCT.md/DESIGN.md seasonal control statements, record evidence and limitations in Bead, signed local task commit, direct-closeout; no push/deploy. Leave unrelated .beads.gate.lock, .claude/, MEMORY.md untouched.

## Commands / acceptance
npm test; python3 tests/test_listing.py; python3 test_design.py; python3 test_marketing_plans.py; git diff --check.
Serve existing http://127.0.0.1:8765/; runtime fixture must report PASS. Hand and images must agree across nonuniform knot segments and annual wrap, all frozen states and resumed state. One >=44px native control, useful non-color seasonal indication, visible focus, no content/contact obstruction. No asset bytes changed.

## Verification record
Implementation: existing button moved, 52px dial in 64px-wide native target; zero block padding keeps desktop masthead exactly 86px. Hand uses shared finite segment Web Animation. Source changes limited to index.html, listing.css, seasonal-hero.js; Python contact assertion narrowed from whole header to actual contact group. PRODUCT.md/DESIGN.md updated. Gallery/photos/config/exports unchanged.

RED: missing masthead dial and phase display observed in runtime fixture before UI changes. Focused GREEN: 86 runtime assertions passed before final masthead/description/idle assertions; 2,050 uninterrupted running samples with zero hand misses, all 18 segments/quarter samples/wrap, held/stalled/pause/lifecycle/fallback cases, all 53 real seasonal photos over 76 scroll stops. Final run results and candidate hashes belong in .pi/artifacts/colonial-ykx/verification.json and Bead closeout.

Scoped peer 41e6636f-9b13-4bc4-95ec-e3730b2ac61d identified short-screen stacking: elementFromPoint confirmed photo intercepted dock. Added z-index20 and executable dock hit-target/footer-clearance regression; browser confirmed repair. Layout fixture exposed late 3.5px desktop masthead growth from button padding; isolated padding-zero experiment repaired docking at 1080/900, then adopted and protected with 86px assertion. Device remains >=44px.

Baseline exception: unchanged HEAD snapshots under .pi/artifacts/colonial-ykx/baseline reproduce tests/hero-layout.html 320×640 failure, “mobile facts bar exceeds 130px budget plus rounding tolerance,” from existing open-house facts content. Do not expand this task into facts redesign or claim full release readiness. Final layout comparison must retain only that identical baseline failure. Impeccable detector ran once: existing facts padding/leading, pinned Arial and frozen “home theater” copy warnings; no new device finding. No skill update or unrelated drift repair.

Desktop/mobile narrative, native Tab/Enter/Space, Pause/Resume, modal hide/Escape, 740×390 dock/end-content, live reduced motion and print visually checked. Evidence copied under .pi/artifacts/colonial-ykx/. No physical touch device, screen-reader speech, Safari/Firefox, native PDF pagination or hardware performance certification. Browser fixture tests computed transforms and opacity; screenshot evidence is visual only because captures may finish animations. Separate fixture tab avoids capture interference. Browser wrapper timeout diagnosed; read-only agnt doctor showed no core failures, existing missing pytest/check-pi-config warnings only. No config changes.

Local task regression and release readiness are separate: task checks must pass; existing 320px facts-budget failure is explicitly not a passing full release gate. No push/deployment authority.
