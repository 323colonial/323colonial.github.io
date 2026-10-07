# Inline listing contact — design and implementation plan

Issue: colonial-57q (user-approved implementation extension, 2026-10-07)
Branch: main

## Goal and boundary
Replace header's Zillow/public-listing link and See in person disclosure with always-visible realtor identity, approved brokerage phone, and Questions & tours link on index.html and gallery.html. Retain existing house colors, typography, address, narrative, photos, facts, print handout and analytics privacy. No forms, embeds, dependencies, new phone, backend, deployment or push.

## Design
Desktop: address left; compact contact block right. Agent/brokerage identity above two underlined native links. Mobile: same contact block below address, left aligned, wrapping naturally without hiding contacts. Preserve 44px link targets. Call is explicitly brokerage/office, not Liz's direct mobile. Questions & tours goes to exact supplied Dandridge property URL in same tab; accessible name discloses Dandridge destination. No fabricated modal deep link. Remove obsolete disclosure CSS/JS and duplicate gallery agent text. Keep print-only phone.

## Implementation and evidence
1. Update existing Python contact contract first and observe expected failure. Baseline: node --test tests/*.test.mjs, python3 tests/test_listing.py, python3 test_design.py, python3 test_marketing_plans.py all passed.
2. Edit two headers and shared listing.css; remove disclosure dismissal JS; update affected browser fixtures and design/product docs. Keep analytics event schema unchanged: new external link uses existing other-external category and header placement.
3. Check existing local server identity, then run contact/layout/fallback/typography/hardening/print fixtures plus all affected browser checks. Inspect desktop/mobile on both pages, keyboard focus, no-JS and enlarged text. One batched review, one correction/confirmation pass maximum.
4. Run Impeccable detector once, classify unrelated findings without redesign. Run all existing Node/Python tests and diff checks. Commit only owned paths after staged review. No unrelated files staged. Record results and remaining research gaps in Bead. Successful research-wide closeout requires acknowledging those gaps; do not silently mark missing external evidence complete.

## Acceptance
- No contact popout or duplicate public-listing action on either page.
- Named agent/brokerage, approved office phone and Dandridge questions/tours remain visible at all tested widths.
- Native links work without JavaScript; keyboard targets visible, readable and at least 44px tall; no horizontal overflow.
- Sticky header/facts and print handout remain usable; approved content/assets unchanged.
- Tests/docs describe current design, not retired disclosure.

Concurrent state at start: only unrelated untracked .beads.gate.lock and .claude/. Other session had committed its prior work; do not alter it.

## Owner refinement

Owner requested tighter, more vertical contact presentation during review. Agent and brokerage now occupy separate lines above stacked links; contact capped at 240px, desktop padding reduced to 8px vertically, 44px native targets retained. No destination or scope change.

Owner then requested even, tighter line spacing. All four contact lines now use 24px rows; native links meet WCAG 2.2 minimum 24px targets rather than earlier self-imposed 44px. Other controls retain 44px.

## Final owner direction

Keep contact below address on small screens, but compress identity to 13px/1.35 and place number-only office phone | Questions & tours in one wrapping row with 24px link targets. Use clean https://search.soldvawv.com/search/detail/270760671 without query parameters. Reduce title link minimum to32px, header padding to8px, desktop minimum86px. Facts vertical padding10px desktop/8px mobile, mobile row gap6px, native facts links minimum24px. Preserve font sizes, content and print. Latest direction supersedes earlier vertical-link/side-by-side-header proposals.

## Final compact facts and visibility refinements

Owner approved price above Property details; separate View all photos, Coming Soon, then Expected on market lines at every width. Four facts stack in middle column on narrow screens, with aligned numbers and wrapping flex for enlarged text. All supporting summary text/actions13px regular; mobile values16px and price25px. Both links mahogany. Remove old180px action-width cap. Date groups naturally without forced no-wrap overflow. Equal gutters retained (40px desktop,20px mobile,12px at≤360px).

Facts use native sticky top+bottom to remain visible at viewport bottom on tall heroes and dock beneath masthead when scrolling, verified forward/reverse. Short-height static fallback retained. Analytics notice padding4px and privacy target24px; no tracking changes. Print explicitly restores horizontal facts to avoid inherited mobile stacking. All listing facts remain printed; status is in detail grid rather than duplicated below print price.
