# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Prospective buyers are primary users. Realtors and the owner use the site as supporting audiences when answering property questions and arranging showings.

## Product purpose

Present a photo-led narrative for weekend and second-home buyers: understand the house through seven exact paragraphs and coordinated photographs, explore all 33 images, and contact the listing brokerage. The owner-directed layout uses house colors, a full-width hero, fixed address/contact header and docking listing facts.

## Approved public brief · revised 4 October 2026

- Current owner revision (colonial-aap) supersedes colonial-bqj layout: `index.html` has a full-width exterior hero, docking price/status/facts, seven heading-free alternating narrative/photo sections, then the dated footer. The closing Property Details grid remains in static source as a fallback, but is hidden on screen after its pop-out initializes (colonial-pmx). The persistent header reads **323 Colonial Dr**, with **Berkeley Springs, WV 25411** beneath; public listing and showing/call access live there. On the title page, agent and brokerage details appear only inside **See in person** (colonial-93v). Its borderless text disclosure sits beside the public listing link on desktop; mobile keeps the public link inside the disclosure. Gallery header is unchanged. No duplicate address block, About heading, story subheadings, Home / Photos navbar, closing contact band or A closer look section.
- Vertical native scrolling advances relevant captioned photographs through reversible, scroll-linked crossfades (colonial-dp6). Each sequence reserves a full scroll step for its final photo after the transition completes. No scroll interception, timed autoplay or parallax. Desktop paragraphs alternate sides. Mobile paragraphs precede their sticky photo sequence. Reduced motion or insufficient viewport height shows ordinary inline photographs instead. No-JavaScript links still work.
- **Property details** is the link in the docking facts heading (colonial-prb, revising colonial-4c4). It opens an in-page native dialog with all twelve existing property facts; **$499,000** is plain text. Escape or Close returns focus to the Property details link. The closing details section remains the static-source, no-JavaScript/failed-initialization, unsupported-dialog and print fallback; direct `#details` navigation reveals it in normal flow. Only successfully enhanced, non-targeted screen presentation hides it. Facts and price are unchanged.
- **View all 33 photos** opens a native gallery dialog; each thumbnail opens the shared enlarged viewer. `gallery.html` remains the ordered direct-link and no-JavaScript fallback. Contextual prose links open photos 15, 19, 24, 31 and 32; a separate laundry link opens 20. Hero plus narrative slides cover every other position. Photo 31 remains explicitly conceptual.
- Preserve the **seven Replacement Listing Text paragraphs verbatim and in order**, from the owner-approved `Listing Feedback 323 Colonial Dr.docx` (colonial-5me). Copy is frozen in `tests/fixtures/approved-listing.json`, including the owner-reconfirmed **up to 7-gigabit** claim despite the contemporaneous MLS 5-gigabit wording.
- Match each passage with captioned property imagery at all viewport sizes. Hero is preferred position 1, listing ID 5/72, shown full width without cropping. Narrative sequencing follows the paragraph subject; the gallery retains DOCX preferred position/caption order, not “OTHER PHOTOS.”
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

Static HTML/CSS and small progressive-enhancement `gallery.js` / `listing.js`; no framework, dependency or build/runtime service. Native image and gallery links work without JavaScript. `listing.js` measures the header/facts and enables sticky photo sequences only when content fits; it respects reduced motion and preserves focused photo links. At viewport heights of 500px or less, facts scroll normally while the contact header stays accessible. Only nearby sequences preload their next photo, and the closed viewer image is lazy-loaded. Both buyer pages share `listing.css`.

This implementation is local-only: no push or deployment authorized. On October 5, 2026, the owner reconfirmed listing facts, descriptions, square footage/acreage and permission to publish all photos, and accepted responsibility for keeping listing facts current. This is owner confirmation, not a new independent MLS verification; the dated October 3 footer remains unchanged. Reconfirm any subsequent changes before publication. Status never advances automatically.

The owner-selected origin is `https://323colonial.github.io/`, hosted on GitHub Pages. Homepage canonical is `/`; the independent gallery is `/gallery.html`. Both pages use address/locality search descriptions and Open Graph metadata with the existing uncropped exterior `assets/listing/01.webp` (1600×1060, image/webp). Price remains in the homepage title and matching share title; the owner must update both when price changes. New metadata excludes disputed internet speed. Sitemap, structured data and Twitter cards are deferred.

`scripts/publish-files.txt` defines the exact 71-file buyer-only publication allowlist. A future authorized deployment must stage only those files in a clean output directory—not publish the repository root. The list itself does not enforce public exclusion. GitHub Pages repository/source settings, final publish revision, live redirects/headers, crawler access, forbidden-file exclusion and retired-route 404/410 responses remain NOT VERIFIED. No redirect configuration or deployment workflow has been added. Local checks do not establish release readiness; see `.pi/plans/2026-10-05-colonial-2ua-seo-plan.md` and Bead colonial-2ua.

The site serves only `index.html` and `gallery.html` as product pages. Colonial-yec removes legacy `floorplans.html`, `brochure.html`, `sale-prep.html` and their unused `styles.css`; no equivalent replacement warrants redirects. Route decisions and Git recovery source are recorded in `.pi/plans/2026-10-05-colonial-yec-route-pruning-plan.md`. All prior images/assets remain byte-identical. Old main/upstairs drawings and finish simulations are not linked buyer content. Developer tests and historical design artifacts remain repository tooling, not product pages.

## Brand commitments

Name is 323 Colonial. Owner's website palette: Sherwin-Williams Greek Villa, Pewter Green, Debonair, Sea Salt and Accessible Beige, plus mahogany brown, stone and red cedar tones. Website values are screen approximations, not physical paint-match specifications or changes to the historical finish schedule below. Georgia narrative and Arial facts remain pinned. Exact approved listing prose takes precedence over editorial rewriting; contextual links wrap existing words without changing them. “Quilt & Stone” remains the historical owner finish record, not a buyer-navigation destination.

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
- [Traditional Mahogany SW 3080](https://www.sherwin-williams.com/homeowners/color/find-and-explore-colors/stain-colors/SW3080-traditional-mahogany) replaces Dark Walnut for the deck. The historical approximate CSS swatch referenced the [manufacturer’s screen swatch](https://sherwin.scene7.com/is/image/sw/db3080tradmahogany_s); verify physical chips in daylight.
- Existing walnut deck and porch simulations are earlier concepts, not exact Traditional Mahogany matches. Preserve assets and provenance; disclose that mismatch beside deck images rather than relabeling their pixels as newly recoloured.
- The table above preserves the owner purchase specification; removed owner pages remain recoverable in Git. The buyer finish schedule was removed from the public journey by colonial-5bv. Historical sale-prep prices remain estimates, not current product quotes. The pre-publication completion and photography gate still applies.

## Evidence and regeneration

- Approved revised DOCX remains at `/Users/hays/Downloads/Listing Feedback 323 Colonial Dr.docx`, unchanged; not copied into the public site. Approved document, embedded media and legacy file SHA-256 hashes live in `tests/fixtures/approved-listing.json`.
- `assets/listing/manifest.json` maps all 33 positions to original embedded sources, current owner-edited PNG hashes, exact captions and output hashes. Derivatives use WebP quality 78. Colonial-286 removes confirmed solid outer margins from 16 photographs without changing their existing scale; all other files remain unchanged. Bounds, conservative edge decisions and reproduction instructions live in `assets/listing/margin-review.md`.
- Reproduce reviewed trims with installed ImageMagick: `python3 scripts/trim-listing-margins.py '/path/to/edited-listing-photos' '/tmp/reproduced-margin-trims'`. The historical `extract-listing.py` reproduces pre-edit DOCX images, not the current edited/trimmed assets; do not use it to overwrite the current site. No extraction is required to serve the committed website.
- Legacy `images/photo-*.jpg`, simulation sources, `images/planned-colours.json`, old reference plans and `assets/plates/` remain untouched. Basement drawing/pricing history lives in a separate CAD project.
- Existing Impeccable mock/build artifacts describe the superseded monograph composition; they are not authority over this approved brief. `DESIGN.md` and `.impeccable/design.json` describe the current buyer listing; retired styling remains recoverable in Git.

## Verification

Run from repository root:

```sh
node --test tests/*.test.mjs
python3 tests/test_listing.py
python3 test_design.py
python3 test_marketing_plans.py
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `tests/hero-layout.html`, `tests/media-layout.html`, `tests/gallery-viewer.html`, `tests/buyer-quality.html`, `tests/narrative-scroll.html`, `tests/listing-fallbacks.html`, `tests/buyer-audit.html`, `tests/property-details.html` and `tests/buyer-typography.html` through the local server. Each must report PASS. Fixtures cover responsive geometry, alternating sides, sticky-content fit, docking facts, forward/reverse photo progression, gallery/plan dialogs, contact access, frozen copy/captions, focus contrast, responsive image slots and disabled-script/reduced-motion fallbacks. Manually verify native Tab/Shift+Tab behavior, Escape dismissal and return focus. The Python listing regression freezes exact copy/order, all-33 narrative coverage, contact facts, local links/assets, source/derivative hashes, accessible link naming, absence of retired routes and byte-identical legacy asset preservation. The Node route inventory check requires exactly the two buyer HTML pages at the site root.
