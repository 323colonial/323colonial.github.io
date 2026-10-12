# Buyer accessibility follow-up · colonial-d5x

## Scope and decisions

Local Chromium evidence, 12 October 2026. No new publication authority, dependency, listing copy, photograph, caption, contact fact, seasonal timing or visitor behavior change.

### Fonts and palette are choices, not pins

Owner prefers house colors, not mandatory cream dominance or Arial. Accessible Beige is used in one bedroom; Greek Villa is distinct. Current seven narrative fields use Sea Salt once, Greek Villa twice, Accessible Beige twice and Debonair twice. Counts describe section assignment, not screen-area percentages; photography and variable section heights change visible proportions.

The prior measured comparison (`.pi/plans/2026-10-09-colonial-bjr-design-plan.md`) found Arial's narrow price width 114.23px versus system-ui's 121.70px; Verdana wrapped the action group and increased facts height to 174.16px before the layout correction. Retain Arial utilities for compact metrics and no download; retain Georgia's readable narrative/utility contrast. These results are platform-specific, not universal font superiority.

Compared with the current Greek Villa base, white would increase text contrast but make the shell brighter and less connected to the house colors. A Sea Salt base would reduce ink contrast from 11.98:1 to 9.20:1 while reducing separation from the first narrative field. Both remain viable; neither solves a reproduced defect. Current narrative ink contrast ranges 5.23:1 (Debonair) to 11.98:1 (Greek Villa); beige is 8.46:1. Retain distribution in this corrective pass, not because bedroom paint establishes a hierarchy or the detector grants an exemption. No wholesale redesign authorized.

### Targets: real padding, not invisible text interception

WCAG 2.2 SC 2.5.8 AA minimum is 24×24 CSS px, with exceptions. SC 2.5.5's 44×44 target is enhanced AAA guidance, not a blanket AA requirement. Existing phone/tours/details/photos targets at normal text are respectively 88.91/103.33/90.33/105.28px wide.

A centered expansion from 24 to 44px adds 10px above and below. Range geometry finds intersections with brokerage text above phone/tours, price above Property details, and Active below photos. Such a target would steal text interaction and imply activation where no link is drawn. Enlarged text also wraps the contact links into neighboring rows. No overlapping pseudo-elements shipped.

Real minimum-height comparison in current Chromium (header / facts height, CSS px):

| Viewport / input | Shipped layout | All four links at least 44px |
| --- | --- | --- |
| 1440×1000, fine pointer | 86 / 85 | 95.09 / 105 |
| 390×844, coarse | 129.09 / 103.38 | 149.09 / 103.38 |
| 320×740, coarse | 129.09 / 103.38 | 149.09 / 103.38 |
| 320×256, coarse | 129.09 / 103.38 | 149.09 / 103.38 |
| 844×390, coarse | 86 / 85 | 95.09 / 105 |
| 320×740, coarse, 200% text | 368.66 / 303.75 | 386.47 / 303.75 |

Safe improvement: facts links now have real 44px minima on coarse pointers, width ≤800px, height ≥501px. At 320/390px normal text, the middle facts column already reserves enough height. Keep 24px contact, desktop and short-screen minima to preserve compact chrome; enlarged text can naturally make targets taller. Retained compact links have a comfort tradeoff, not a minimum-size violation. Tests sample target corners/centers, verify full focused-target visibility and no horizontal overflow, and synthesize touch opening/closing of details. This is not a physical touch-device test.

### Enlarged text correction

At 320×740 with 200% text, keyboard focus left the photos link extending to y≈758, below the viewport. Header/facts together used about 664px before the new coarse padding. Root cause: height-only media queries retained sticky chrome on a tall viewport despite enlarged content.

`listing.js` reuses measured heights to set `reading-space-limited` when header + facts exceed viewport height minus 160px. CSS then releases both bars into normal flow and uses 24px top anchor clearance. Existing observer/resize paths recalculate it; expanding the viewport restores sticky behavior. No extra geometry phase, observer, focus interception or scrolling animation. Without JavaScript, existing short-screen CSS and normal native scrolling remain; content-fit detection needs enhancement.

## Documentation provenance

- Footer: commit `8253e57b4a26f1a566b332958b04b54128597019` explicitly changes status to Active and footer to October 8, 2026, with listing regressions updated. PRODUCT already records the owner-stated Active change and subsequent October 8 feed recheck. Correct the two stale October 3-footer statements; do not revert newer markup.
- Share image: owner approval recorded in colonial-wjn's portable Beads record; commit `58d045f39886bbd7a41a5251e2a294cb30cbfca9` updates both pages and SEO tests to the published 300×199 GIF. Correct stale WebP documentation. Messaging clients need not animate it.
- No current listing re-verification, new status change, push or deployment is implied.

## Repeatable gate and limits

Run `npm run test:buyer`. New `tests/buyer-accessibility.spec.mjs` uses the installed Playwright/Chromium stack:

- Real Tab/Shift+Tab/Enter/Escape navigation, skip-link destination, visible header focus, modal initial focus, dismissal and return, nested catalog/viewer restoration.
- Chromium accessibility-tree landmarks, background isolation and polite updated photo count; role/name checks, language, image alt presence and single h1.
- Six target scenarios above, measured 44px proposal, coarse-pointer detection and synthesized tap; 200% text with sticky recovery after resize.
- Actual solid-field text contrast. These checks do not audit every pixel, image overlay, semantic nuance or WCAG criterion.

Buyer browser gate also now includes existing buyer-audit, buyer-harden, buyer-typography, property-details and listing-fallbacks fixtures, including reflow, real image failure/loading announcements, 200% text, no-script and reduced-motion cases. Existing seasonal/visitor suites cover pause, save-data, lifecycle and motion fallbacks. CDP/ARIA checks prove exposed semantics, not spoken announcements.

Focused red/green: enlarged-text target visibility failed before the content-fit fix; coarse facts target test failed with `Expected: >= 44; Received: 24` before padding. Initial skip-link test incorrectly demanded focus on nonfocusable `main`; corrected to verify next Tab enters main. Dialog tests wait for native asynchronous close events before starting the next interaction.

Not tested: VoiceOver/NVDA/JAWS speech, physical iPad/Safari, native browser zoom/pinch zoom, all browser engines, production CWV or device memory. 320px reflow and scripted 200% text are not native zoom certification. No full WCAG-conformance claim. Full-suite, visual-review and detector results are recorded in colonial-d5x at closeout.
