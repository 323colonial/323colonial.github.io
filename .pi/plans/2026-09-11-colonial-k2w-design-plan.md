# Buyer rewrite design-plan

Bead: colonial-k2w. Approved implementation; retain Mountain House Monograph visual system.

## Boundary
Three public destinations: `index.html` (The house), `gallery.html`, `floorplans.html`; shared Request a showing mailto action. Rewrite for finished house under explicit pre-publication upgrade-completion gate. No push or deployment. Keep two bedrooms, two full baths, one half bath; basement remains unfinished. No invented appliance details.

## Implementation
1. Add failing public sitemap/copy/image-label checks in `tests/site-structure.test.mjs`; update only tests whose old planning journey is superseded.
2. Shorten home into house/rooms/outdoor narrative, reuse approved simulated assets with attached `Digitally simulated image` labels. Move full photo journey to gallery. Preserve prior-listing provenance and approximate render/staging disclosure.
3. Remove owner-record links from public pages. Preserve `brochure.html` and `sale-prep.html` at existing URLs with owner-only navigation and noindex metadata (not access control). Keep their decisions, estimates, tables and limitations intact.
4. Retain floor-plan sheets and limits; rewrite introduction/lower-level description for buyers without claiming basement completion. Update product/design/surface content rules to match approved publication gate.
5. Verify tests, all public links/assets, desktop/mobile layout, keyboard navigation and showing hrefs. Review diff; commit only task files; record evidence and close through direct-closeout.

## Verification
- `node --test tests/site-structure.test.mjs`
- `python3 test_design.py`
- `python3 test_marketing_plans.py`
- Local HTTP server + browser at 1376x768 and 390x844; public navigation, captions, plan anchors/full-size links, overflow, focus and showing mailto.
- Mechanical detector once over changed HTML/CSS; peer review before commit.

## Verification evidence
- Baseline: 15 Node tests plus both Python checks passed before edits.
- RED: new sitemap, finished-copy, disclosure, owner-separation and missing-gallery assertions failed before implementation; test-only false positives for legacy CSS class names and the real room-photo asset were corrected.
- GREEN: 16 Node tests plus both Python checks pass. Five-page local link/asset/anchor/unique-ID check passes. Owner main/footer content is byte-identical to pre-rewrite HEAD.
- Browser: hero fixture passes 10 widths; media fixture passes 5 routes × 3 widths; owner-table fixture passes 2 routes × 3 widths, minimum contrast 11.75:1. Desktop 1376×768 and mobile 390×844 captures of all public pages inspected; captions, navigation and showing controls remain usable. Full-size plan hrefs and image assets verified; no email sent.
- Read-only peer review: `openai-codex/gpt-6-astra`, invocation `4742bebc-caed-4e62-8cf6-8dcd2960e670`, no findings.
- Private evidence: `~/.pi/runtime/167c520629483ea9015528eb7327f7b1db9656ff62d59414312e4d5ad2e793df/colonial-k2w-evidence/` contains six public-page captures, RED log, detector/doctor reports and peer review output. No runtime evidence added to Git.
- Detector ran once in degraded regex mode (HTML parser modules absent); all reported colour advisories refer to unchanged CSS. Browser computed-style/hit/contrast checks provide separate evidence, not a claim of a clean detector scan.
- Browser batch API schema/name mismatches and one navigation timeout occurred; read-only doctor found no failures, only generic unused prerequisite warnings. No config/dependency changes; continued with named locators and project browser fixtures.

## Publication constraint
Copy assumes advertised improvements are complete. Owner/realtor must confirm each advertised upgrade before publication and provide authorized fresh listing photography; Bright MLS prior-listing images remain identified. No claim that this session verified physical completion. Owner records remain URL-accessible, not private or authenticated.
