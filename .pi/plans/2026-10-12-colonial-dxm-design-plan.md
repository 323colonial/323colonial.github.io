# Visitor photo movement

Issue: colonial-dxm

## Scope and decision
Visitor route only. Use one clipped horizontal composition at every aspect ratio: main (two thirds width), auxiliary column (one third width; two stacked photos). User clarified strip semantics: [old main | aux | incoming main] slides left; reverse strip slides right. Portrait retains this left/right relationship instead of the old below-main arrangement.

Sequence: auxiliary down, auxiliary down, main left, auxiliary down, auxiliary down, main right; repeat. Incoming auxiliary enters above, old top becomes bottom, old bottom exits. IDs remain unique, including outgoing and incoming. Main selection stays in existing exterior pool.

One linear speed derives from mean travel over all six steps: (4 * auxiliary height + 2 * main width) / 6, divided by a 1000ms mean transition duration. Each duration is distance / shared speed. Preserve eight-second dwell between transitions; no new user options. On unusually tall screens vertical travel can exceed horizontal travel; equal speed and actual geometry govern durations.

## Implementation
- `visitor-display.js`: six-step sequence, decoded/prepared incoming frame, transform-only Web Animations, atomic settled composition. Existing pending cancellation rolls back in-flight movement; resize cancels stale geometry. Preserve pause, seasonal preparation, failure/retry, reduced motion/save-data, print, and visibility behavior.
- `listing.css`: visitor-only absolute slots and clipping, opposite-side state, incoming slots. Remove portrait-only stacked variant.
- `tests/visitor-display.test.mjs`: repeated sequence selection/uniqueness, full pool coverage, normalized timing.
- `tests/visitor-browser.spec.mjs`: update changed sequence expectations; inspect real transforms, equal velocities, repeated cycles, layout, in-flight interruption and lifecycle. Fast-forward only visitor animations in long coverage tests; inspect real timing separately.
- Update visitor paragraphs in `DESIGN.md`, `PRODUCT.md`, and `.impeccable/surfaces/index-html.md` to match experiment.

## Verification
1. Observe focused failing regression before implementation.
2. `node --test tests/visitor-display.test.mjs`
3. `npx playwright test tests/visitor-browser.spec.mjs`
4. `npm run test:buyer`
5. Local browser visual proof: desktop/portrait/mobile, left/right settled arrangements and reduced motion. No deployment or push.
6. Review diff; commit task-owned files; `agnt work direct-closeout colonial-dxm --outcome success --reason ...` then handoff.

## Motion budget and limits
Only three or four figures mounted; transform animation at one transition at a time. Existing seasonal opacity animations are unchanged. No new dependency, photo processing, public API or persistent state. Real iPad/Safari performance not certified by Chromium checks.
