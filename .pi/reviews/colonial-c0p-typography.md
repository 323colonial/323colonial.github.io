# Colonial-c0p — buyer typography implementation

## Decision and scope

Recovered only colonial-yec, colonial-c0p and their referenced evaluation/context artifacts; no prior transcript. Retain Georgia/Arial, 400/700 weights, prose size/leading, exact copy/facts/captions, photography and the intentional homepage/gallery showing-control distinction. No HTML, JavaScript, assets, dependencies, push or deployment changes.

`listing.css` raises status, expected date, above-grade qualifier, details labels and concept disclosure from 12px to 13px. Removes redundant mobile overrides. Counters/footer stay 12px. Only the gallery introduction paragraph gains `max-width: 60ch`; heading and gallery widths stay unchanged. DESIGN.md and affected sidecar metadata match these changes; unrelated historic sidecar drift is not repaired.

## Enlargement boundary — NOT VERIFIED

Actual text-only enlargement and browser default-font preferences are unavailable through the exposed browser tool surface. No settings/profile edits or substitute synthetic probes were used to claim support. Browser zoom was separately attempted via native `ControlOrMeta+Equal`, followed by reset `ControlOrMeta+Digit0`. At 1440×1000, before and after both reported innerWidth 1440, devicePixelRatio 1, visualViewport.scale 1: shortcut did not change zoom. Therefore actual browser zoom, default-font preferences and 200% text-only enlargement remain NOT VERIFIED, not PASS.

The earlier doubled-computed-font overflow remains synthetic evidence only, not a confirmed WCAG failure. Conditional header repair was not justified: masthead and listing.js remain byte-identical. Viewport resizing tests below are not zoom tests. Real-browser enlargement remains a manual follow-up when a browser with those controls is available; if it confirms clipping, reproduce before changing header reflow.

## Measure and fit evidence

At 1440×1000, gallery Georgia paragraph remains 18px/29.7px:

| Trial | Rendered width | Trimmed line character counts |
| --- | ---: | --- |
| Existing | 760px | 95 / 60 |
| 60ch (retained) | 662.87px | 84 / 71 |
| 65ch | 718.11px | 84 / 71 |
| 70ch | 760px (parent cap) | 95 / 60 |

Measured character-by-character DOM Range line grouping with frozen paragraph text. CSS ch is zero-glyph width, not average prose character width: retained 60ch improves the longest line but does not claim a 60–70-character line. Two-line density and original copy remain intact.

| Homepage viewport | Header (unchanged) | Facts before → after |
| --- | ---: | ---: |
| 320×480 | 88px | 177.4 → 180.5px |
| 390×844 | 88px | 160.0 → 161.6px |
| 844×390 | 102px | 140.8 → 142.4px |
| 1440×1000 | 102px | 140.8 → 142.4px |

Both pages pass focused showing-control bounds, brokerage hit-target access, essential computed sizes, subordinate counters/footer, measured header offset and horizontal overflow checks at all four sizes. Homepage additionally passes measured facts offset, docking/static short-screen behavior, qualifier fit and details-dialog wrapping. Gallery concept disclosure wraps without horizontal overflow. Header/facts combined heights remain correctly measured by existing ResizeObserver logic.

## TDD and polish

- RED: `tests/buyer-typography.html` in local browser failed all eight essential-size cases and desktop gallery measure (95/60). Other checks passed. Screenshot `pi-observation-1791166000691-2dd82c.png`.
- GREEN: same fixture after minimal CSS change passes all 69 assertions, including rendered gallery counts 84/71. Screenshot `proof-1791166041268-95ab90.png`.
- Initial shell verification: `node --test tests/*.test.mjs` 7/7; `python3 tests/test_listing.py` 11/11; `python3 test_design.py` PASS; `python3 test_marketing_plans.py` PASS.
- Bounded Impeccable polish: inspected desktop and mobile facts/contact, details, concept viewer and gallery introduction. Hierarchy and quiet photo-led composition preserved; no additional visual changes justified. Primary prose untouched. Essential notes remain regular Arial; contrast colors unchanged.
- Native keyboard checks: details Escape restores Property details; contact Tab reaches brokerage and Shift+Tab restores summary; contact Escape restores summary. Viewer Tab reaches Previous, Shift+Tab returns Close; arrows advance/reverse. Viewer Escape returns to photo 31, catalog Escape to View all 33 photos. Single-control details dialog may tab to browser chrome; Shift+Tab returns Close without activating background links.
- Desktop 1440×1000 and homepage 390×844 exercised details/contact/catalog/viewer. Gallery 320×480 contact and conceptual viewer also exercised; Escape restores photo 31. No outbound calls or inquiries sent.
- Mechanical scan once: `node .pi/skills/impeccable/scripts/detect.mjs --json listing.css`, exit 2, exactly one `overused-font` warning at line 63 for Arial. Intentional exception: PRODUCT.md explicitly pins Arial for facts, not a reason to replace fonts.
- Independent routed GPT review: no findings; `.pi/reviews/colonial-c0p-review.json`. Delegated reference `runtime:delegated-results/febc58db-5acf-4980-9ee2-17477c785e46/child-0.json`.

Final staged-candidate shell and all nine browser fixture results, commit and closeout are recorded in colonial-c0p notes after execution. This document records implementation evidence, not a deployment claim.

## Local screenshot evidence

Base: `/Users/hays/.betterwright/artifacts/85b42e1702877c85/`.

- Focused geometry/type results: `proof-1791166041268-95ab90.png`.
- Mobile contact and facts: `pi-observation-1791166134467-d9f257.png`.
- Mobile conceptual viewer: `pi-observation-1791166176210-a03e3b.png`.
- Desktop conceptual viewer: `pi-observation-1791166276598-56a430.png`.
- Desktop facts and restored catalog focus: `proof-1791166291552-52df96.png`.
- Gallery desktop final measure: `proof-1791166314906-3da829.png`.
- Gallery 320px contact access: `proof-1791166314953-dd0d90.png`.

Tool notes: two controls.batch schema errors occurred before action execution; switched to known locators. Read-only `agnt doctor --json` found no failures, only generic missing pytest/check-pi-config warnings; this project's documented Python checks use stdlib and pass. No environment repairs attempted. Existing port-8883 server and pre-existing untracked `.beads.gate.lock` remain untouched.
