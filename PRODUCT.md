# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Prospective buyers are primary users. Realtors and the owner use the site as supporting audiences when answering questions, arranging showings, and reviewing sale-prep records.

## Product purpose

Present a conventional photo-led listing for weekend and second-home buyers: understand the house, explore 33 ordered photographs, and contact the listing brokerage. Preserve the forest/warm-paper identity; Redfin/Zillow-style clarity replaces the renovation scrapbook.

## Approved public brief · revised 4 October 2026

- `index.html`: listing overview, about the home, property details, photo preview and contact. `gallery.html`: complete 33-position gallery with accessible enlarged viewing. Primary navigation is **Home / Photos**, linking to these two pages from the same normal-flow position below the masthead, with the current page marked (colonial-bqj). No sticky changing images, scroll effects or autoplay.
- Preserve the **seven Replacement Listing Text paragraphs verbatim and in order**, from the owner-approved `Listing Feedback 323 Colonial Dr.docx` (colonial-5me). Copy is frozen in `tests/fixtures/approved-listing.json`, including the owner-reconfirmed **up to 7-gigabit** claim despite the contemporaneous MLS 5-gigabit wording.
- Match each passage with captioned inline property imagery at all viewport sizes. Hero is preferred position 1, listing ID 5/72. Gallery follows the DOCX preferred positions/captions, not “OTHER PHOTOS.”
- Slot 6 uses the owner-supplied actual salt-water hot-tub photograph embedded in the revised DOCX, without a placeholder warning. The superseded [Olympic Hot Tub source](https://olympichottub.com/wp-content/uploads/2023/10/Hot-Spring-Flair-wBluetooth-Music-Chehalis_1.jpg) remains at `assets/listing/hottub-placeholder-source.jpg`, unused and unchanged; original house simulation `images/deck-hottub-v3.png` also remains untouched.
- Owner-supplied laundry and basement images are actual photographs. Only position 31, the basement marketing plan, carries the short label **Conceptual basement plan — not existing finished space**. No expanded basement proposal or new basement page.
- Per the final user request, remove routine “Listing photograph”, “Owner photograph”, seasonal/source caveats and repeated snapshot warnings from buyer pages. Retain exact DOCX captions and only the essential basement concept label. One footer per page reads **Listing information as of October 3, 2026.**
- Prior-listing seasonal provenance remains in the manifest and Bright MLS watermarks remain in the pixels. Safe crop derivatives remove viewer chrome or specified distracting edges; originals stay untouched. Position 12's already-truncated windows cannot be restored by cropping and are not invented.

## Listing snapshot and contact

Verified against Redfin / Bright MLS on **October 3, 2026**, not a live feed:

| Fact | Value |
| --- | --- |
| Price | $499,000 USD |
| Bedrooms / baths | 2 bedrooms; 2 full baths and 1 half bath |
| Finished area | 2,081 sq ft above grade; 0 finished sq ft below grade |
| Land | 2.90 estimated acres, including additional parcels |
| Built / HOA | 2008 / none |
| Status | Coming Soon; expected on market October 8, 2026 |
| MLS | WVMO2008198 |

Primary CTA: **Contact listing brokerage**, `tel:3048857645`, displayed 304-885-7645. Listing agent: **Liz McDonald**, **Dandridge Realty Group LLC**. Phone is the brokerage office, not a direct Liz line or the separate Redfin tour-agent number.

Secondary destination: [public Redfin listing](https://www.redfin.com/WV/Berkeley-Springs/323-Colonial-Dr-25411/home/21971085). Never publish the email-specific MLS portal URL. Status must not automatically become Active on the expected date.

## Operating context and boundaries

Static HTML/CSS and small progressive-enhancement `gallery.js`; no framework, dependency or build/runtime service. Native image links work without JavaScript. Public `listing.css` is isolated from legacy `styles.css`.

This implementation is local-only: no push or deployment authorized. Before later publication, owner/brokerage should reconfirm price, status, measurements, advertised improvements and photography rights. The dated snapshot is not a promise of present availability.

Legacy `floorplans.html`, `brochure.html`, `sale-prep.html`, shared `styles.css`, and all prior images/assets remain byte-identical and unlinked from the buyer journey. Owner records retain their noindex metadata and original planning/purchasing caveats; URL-accessible does not mean private. Old main/upstairs drawings and old finish simulations are not buyer content.

## Brand commitments

Name is 323 Colonial. Forest/warm-paper palette, restrained identity, Georgia narrative and compact sans-serif facts remain pinned. Exact approved listing prose takes precedence over editorial rewriting. “Quilt & Stone” remains the historical owner finish record, not a buyer-navigation destination.

## Approved finish specification · 15 September 2026

Sherwin-Williams · 814 S Loudoun St, Winchester, VA 22601-4597.

| Surface | Colour | Product and sheen |
| --- | --- | --- |
| Hallway | SW 7008 Alabaster | Emerald Interior Matte |
| Primary bedroom | SW 9139 Debonair | Emerald Interior Matte |
| Upstairs bedroom and walk-in | SW 6206 Oyster Bay | Emerald Interior Matte |
| Both full baths | SW 6204 Sea Salt | Duration Home Satin |
| Front, back and garage doors | SW 6208 Pewter Green | Emerald Urethane Trim Enamel Satin |
| Deck floor | SW 3080 Traditional Mahogany | SuperDeck Exterior Waterborne Solid Color Deck Stain |

- Matte supersedes the earlier flat preference. Door enamel and satin sheen carry forward the earlier discussion; the latest list confirms the door colour only.
- Omit paint purchase quantities. Great-room and loft whites stay for sale; half bath remains as-is. Kitchen Alabaster and porch finish remain earlier scope, not additions to this purchase specification. Basement work remains separate.
- Owner reports mostly sound, faded deck coating with little peeling. Confirm product compatibility, cleaning, prep, primer and tint base with the Winchester store; no base or formula is verified here.
- [Traditional Mahogany SW 3080](https://www.sherwin-williams.com/homeowners/color/find-and-explore-colors/stain-colors/SW3080-traditional-mahogany) replaces Dark Walnut for the deck. The approximate CSS swatch references the [manufacturer’s screen swatch](https://sherwin.scene7.com/is/image/sw/db3080tradmahogany_s); verify physical chips in daylight.
- Existing walnut deck and porch simulations are earlier concepts, not exact Traditional Mahogany matches. Preserve assets and provenance; disclose that mismatch beside deck images rather than relabeling their pixels as newly recoloured.
- `brochure.html` holds the owner purchase specification; the buyer finish schedule was removed from the public journey by colonial-5bv. Historical sale-prep prices remain estimates, not current product quotes. The pre-publication completion and photography gate still applies.

## Evidence and regeneration

- Approved revised DOCX remains at `/Users/hays/Downloads/Listing Feedback 323 Colonial Dr.docx`, unchanged; not copied into the public site. Approved document, embedded media and legacy file SHA-256 hashes live in `tests/fixtures/approved-listing.json`.
- `assets/listing/manifest.json` maps all 33 positions to embedded source relationship targets, exact captions, crop rectangles/decisions and output hashes. Derivatives are WebP at maximum 1600px and 720px, quality 78, with no upscaling or new generative edits.
- Reproduce with installed ImageMagick: `python3 scripts/extract-listing.py '/path/to/Listing Feedback 323 Colonial Dr.docx'`. Extraction rejects a source that differs from the approved hashes. No extraction is required to serve the committed website.
- Legacy `images/photo-*.jpg`, simulation sources, `images/planned-colours.json`, old reference plans and `assets/plates/` remain untouched. Basement drawing/pricing history lives in a separate CAD project.
- Existing Impeccable mock/build artifacts describe the superseded monograph composition; they are not authority over this approved brief. `DESIGN.md` and `.impeccable/design.json` describe the current buyer listing; legacy styling remains separate.

## Verification

Run from repository root:

```sh
node --test tests/*.test.mjs
python3 tests/test_listing.py
python3 test_design.py
python3 test_marketing_plans.py
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `tests/hero-layout.html`, `tests/media-layout.html`, `tests/gallery-viewer.html`, `tests/table-contrast.html` and `tests/buyer-quality.html` through the local server. Each must report PASS. The buyer-quality fixture checks navigation labels, page destinations, current state, matching normal-flow placement, frozen copy/captions, focus contrast, disclosure names, 44px navigation targets and responsive image-slot hints across both buyer routes and breakpoint edges. Manually verify native Tab/Shift+Tab focus containment, Escape dismissal and return focus, mobile/desktop presentation, and no-JavaScript image links. The listing regression freezes exact copy/order, contact facts, local links/assets, source/derivative hashes and byte-identical legacy preservation.
