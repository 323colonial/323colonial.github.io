# Buyer website technical audit — colonial-hdy

Date: 5 October 2026. Audited revision: `5fe8997789c6b785a94b47393894a7e0144ff074`.
Implementation follow-up: **colonial-vw9 — Implement confirmed Impeccable audit recommendations** (created before audit closeout).

## Implementation integrity verdict

**PASS for product-specific coherence; not release certification.** The implementation follows the owner-pinned house palette, Georgia/Arial typography, exact seven-paragraph narrative, native scrolling, factual imagery and labeled conceptual plan. No redesign is warranted. Three confirmed P2 findings remain: two gallery-print defects and one print-test synchronization defect. No P0, P1 or P3 findings confirmed in this scope.

Audit only: no buyer HTML, CSS, JavaScript, imagery, facts, captions, dependencies or publication settings changed. No push or deployment. Recovery used only `bd show colonial-5dm`, `bd show colonial-hdy` and current referenced source/constraints; no prior transcript recovered.

## Audit health score

| Dimension | Score / 4 | Evidence and limit |
| --- | ---: | --- |
| Accessibility | 3 | Named native controls/dialogs, visible focus, contrast and fallback checks pass; screen-reader and cross-engine certification not performed. |
| Performance | 3 | Small dependency-free enhancement, responsive WebP, lazy loading and nearby preload; no controlled cold-network/mobile CPU benchmark. |
| Responsive design | 3 | Desktop/mobile and short-screen checks pass; gallery paged-media behavior fails. |
| Theming | 4 | Consistent documented house tokens and deliberate print palette; scored against approved single-theme contract, not an invented dark-mode requirement. |
| Implementation integrity | 3 | Frozen content and product-specific system hold; print test reports false geometry failures and misses actual pagination defects. |
| **Total** | **16/20** | **Good — address weak dimensions.** |

Scores describe inspected scope, not proof of full WCAG AA compliance. Lack of a required dark theme is not a defect. Accessibility/performance ceilings reflect unverified conditions rather than invented findings.

## Executive summary

- **F1 / P2:** Gallery prints the screen-only skip link repeatedly, obscuring photo content and sometimes captions.
- **F2 / P2:** Gallery allows photos and captions to land on different pages; Letter also produced a footer-only final page.
- **F3 / P2:** Print fixture measures responsive images before post-resize decoding settles, producing repeatable false proportion failures.
- Homepage handout remains one clean page on Letter and A4 portrait. Desktop/mobile buyer experience, exact copy, native dialogs and scroll/fallback behavior remain intact in tested Chromium.
- Implement F1–F3 through **colonial-vw9**. Do not change approved visual direction or copy in response to detector taste warnings.

## Confirmed findings

### F1 — [P2] Gallery prints a repeated skip-link overlay

- **Location:** `gallery.html:22`; shared `.skip-link` at `listing.css:33–34`; print exclusion scoped only to `.listing-page` at `listing.css:216–217`.
- **Category:** Responsive design / implementation integrity, paged media.
- **Impact:** “Skip to content” is meaningless on paper and covers property evidence. In the A4 PDF it overlays photographs near the bottom of pages 2 and 3. In Letter page 6 it collides with photo 33's caption.
- **Reproduce:** Open `gallery.html` in Chromium 153, decode catalog images, print portrait at 100%, 0.5in margins, browser headers/footers off. Inspect Letter and A4 PDFs. This does not require focusing the skip link.
- **Evidence:** [Actual A4 pages 2–3](colonial-hdy-audit-evidence/gallery-a4-pages-2-3.png), left/right panels. PDF artifact names and settings are below. Extracted Letter text contains repeated `Skip to content`, including `Skip three / Nearly to content` where it crosses the last caption.
- **Root cause:** The fixed-position screen skip link survives gallery print. The homepage-only print hide rule does not match gallery's unclassed body. Screen off-canvas positioning is not a reliable print exclusion.
- **Standard:** Existing print requirement to hide screen navigation and avoid overlap. No separate WCAG conformance claim from this paper-only observation.
- **Smallest recommendation:** Hide the existing skip link for both buyer pages in print only; retain the keyboard-visible screen link unchanged. Add an assertion that gallery print also excludes it.
- **Suggested command:** `/impeccable adapt`.

### F2 — [P2] Gallery pagination separates photographs from captions

- **Location:** `.gallery-grid` at `listing.css:116,146,179`; print break protection at `listing.css:207` applies to `.story figure`, not gallery figures. Example markup: photo 3 at `gallery.html:33`.
- **Impact:** Printed captions become ambiguous or detached from their image. A4 photo 3 appears at the bottom of page 2, but its “Tucked into 2.9 wooded acres…” caption starts page 3. Photo 5's caption similarly follows on the next page. Letter has a seventh page containing only the dated footer.
- **Reproduce:** Same settings as F1; inspect A4 pages 2–3 and Letter page 7. This is actual pagination, not continuous print-media geometry.
- **Evidence:** [A4 split caption](colonial-hdy-audit-evidence/gallery-a4-pages-2-3.png). Left panel ends with photo 3; right panel begins with its detached caption. `pdfinfo`: gallery Letter 7 pages, gallery A4 19 pages.
- **Root cause:** Gallery figures have no print-specific fragmentation protection. Screen breakpoints also apply to print: Letter's 720px printable width selects two columns, while A4's approximately 698px width selects one. That explains much of the count difference; printing the full catalog is intentional, but detached captions are not.
- **Category / standard:** Responsive design / print photo-caption association and figure integrity. No arbitrary one-page limit should be applied to the 33-photo catalog.
- **Smallest recommendation:** Keep each gallery image, exact caption and concept note together using native print fragmentation rules; verify their behavior in actual PDFs. If grid fragmentation prevents this, use the smallest print-only layout adjustment. Keep all 33 photos and their proportions. Avoid a footer-only extra sheet where practical. Do not impose a new gallery page-count target or crop images to save paper.
- **Suggested command:** `/impeccable adapt`.

### F3 — [P2] Print fixture races responsive image decoding

- **Location:** `tests/print-layout.html:25–31` decodes before changing media/width; `:45–47` changes widths then waits only two animation frames; `:66` compares rendered and intrinsic proportions.
- **Category:** Implementation integrity / verification reliability.
- **Impact:** False failures misdirect work toward correct images and undermine the regression gate. The fixture also cannot detect F1–F2 through its continuous geometry checks alone.
- **Reproduce:** Open the fixture in screen media, wait for `Ready`, then emulate print. In this session, both initial and isolated runs reported the gallery case FAIL for photos **19, 20, 24, 31 and 32: uncropped proportions**. All three homepage cases passed.
- **Evidence:** On the same gallery iframe, with print media still active, await `decode()` on the selected `.gallery-grid img` images and repeat the same ratio/object-fit comparison: **zero failures**. No site CSS, markup or image was changed. Actual decoded gallery PDFs do not establish an image-proportion defect; they expose the separate pagination defects above.
- **Root cause / confidence:** High confidence that the fixture samples unsettled responsive-image geometry: its decode wait precedes the media/width change that can select new `srcset` candidates, and waiting for those candidates clears every measured mismatch. Do not “fix” image dimensions or weaken the tolerance to silence it.
- **Smallest recommendation:** Wait for selected images to decode after print/width changes, then settle layout before asserting. Keep all existing content and geometry assertions; retain actual PDF checks for pagination, which this fixture explicitly does not model.
- **Standard:** Deterministic regression evidence, not a WCAG violation.
- **Suggested command:** `/impeccable harden`.

## Verification performed

### Source and shell checks

Loaded Impeccable skill, its audit playbook, and `context.mjs --target index.html` once. Read current `PRODUCT.md`, `DESIGN.md`, surface brief, buyer markup and complete `listing.css`, `listing.js`, `gallery.js`.

| Command | Result |
| --- | --- |
| `node --test tests/*.test.mjs` | 12/12 PASS |
| `python3 tests/test_listing.py` | 11/11 PASS |
| `python3 test_design.py` | PASS: buyer styles wired across 2 pages |
| `python3 test_marketing_plans.py` | PASS: preserved plan invariants |
| `node .pi/skills/impeccable/scripts/detect.mjs --json index.html gallery.html listing.css listing.js gallery.js` | Exit 2; 8 findings, context-reviewed below; no confirmed product defect from detector |

### Browser fixtures

Served current repository at `http://127.0.0.1:8765/`. Browser: Chromium 153 on macOS, persistent browser profile. Nine screen fixtures launched in separate tabs; failed fixture then rerun in isolation without source changes.

| Fixture | Result |
| --- | --- |
| `tests/hero-layout.html` | 9 PASS |
| `tests/media-layout.html` | 6 PASS |
| `tests/buyer-quality.html` | 16 PASS (output has 18 lines including heading/blank line) |
| `tests/listing-fallbacks.html` | 12 PASS |
| `tests/buyer-audit.html` | Initial 38 PASS / 1 FAIL; isolated rerun 39 PASS; see unverified risks |
| `tests/property-details.html` | 67 PASS |
| `tests/buyer-typography.html` | 69 PASS |
| `tests/gallery-viewer.html` | 51 PASS |
| `tests/narrative-scroll.html` | 214 PASS |
| `tests/print-layout.html` | Both runs: 3 homepage cases PASS, gallery case FAIL as F3; after decode, manual equivalent ratio comparison has zero failures |

Do not describe the initial matrix or print fixture as wholly green. No fixes were made during this audit.

### Screen, keyboard and fallback observations

- Visually inspected homepage at 1440×1100 and 390×844, gallery at 1440×1000 and 390×844. Hero remains uncropped; gallery shifts three columns to one; caption separation and typography readable. Homepage prose measured 21.312px / 35.1648px on desktop, 18px / 1.65 on mobile.
- Existing quality fixtures additionally cover widths 320, 390, 700, 701, 1000, 1001, 1264 and 1440. Short-screen checks include 320×256, 844×390 and 1440×500; facts scroll away while contact remains reachable.
- Mobile contact panel shows agent, brokerage, phone and public listing link without horizontal overflow. Gallery at 390px has a 358px column and no visible standalone targets under 44px. Inline prose links retain native text-link semantics; they are not automatically WCAG AA failures for being shorter than 44px.
- Native details dialog focuses Close details; Escape restores Property details. Tab/Shift+Tab exercised. A single-button dialog can hand Tab to browser chrome; no demonstrated background-page activation or keyboard trap.
- Nested catalog/viewer: Tab reaches Previous → full-size link → Next; Shift+Tab reverses; ArrowLeft wraps photo 1 to 33. First Escape closes viewer and returns catalog photo opener; second closes catalog and restores View all 33 photos. Existing viewer fixture covers all positions/captions, modified clicks and synthetic image-error recovery.
- No-script/reduced-motion homepage fixtures preserve all narrative images, contact access and ordinary gallery links. Property-details fixture covers unsupported dialog and failed listing initialization. Additional 390px script-disabled gallery iframe showed all 33 figures, original full-image href, working native contact disclosure, no generated viewer previews and no horizontal overflow.
- Native scroll fixture verifies reversible crossfades, final-photo hold, reduced/short fallback, captions and focused-photo preservation. One initial screenshot taken immediately after programmatic scrolling showed a not-yet-decoded photo; subsequent loaded image and its two crossfade opacities were verified. Not classified as a persistent blank-image defect.
- Applied WCAG text-spacing values in the browser only: line height 1.5, paragraph margin 2em, letter spacing .12em, word spacing .16em. Both routes at 1440, 390 and 320px retained document width and contained contact panels. This is a bounded spacing check, not real browser zoom or a complete accessibility certification.

### Contrast and performance

Calculated WCAG luminance ratios from actual CSS colors: paper/pewter **5.29:1**; paper/mahogany **8.57:1**; ink/debonair **5.23:1**; muted/paper **6.39:1**; ink/sea-salt **9.20:1**. Tested text combinations exceed AA 4.5:1; not all meet AAA 7:1. Focus contrast is separately covered by buyer-quality fixtures.

Shared scripts total **9,473 bytes** uncompressed; CSS **15,520 bytes**. No frontend runtime dependency or downloaded font. Hero uses `fetchpriority="high"`; images declare intrinsic dimensions, responsive slots and WebP derivatives. Nearby next-photo preload is deliberate, not a defect. A closed-viewer probe showed `loading="lazy"`, empty `currentSrc`, `naturalWidth=0`, no `/01-small.webp` resource request.

`listing.js` uses passive scroll plus requestAnimationFrame and no autoplay or scroll interception. Its read/write loops and resize measurements are potential profiling targets, not confirmed performance failures. No CPU trace, cold-network LCP/CLS budget or mobile-device frame-rate claim made.

### Actual print pagination

Fresh PDFs generated from initialized current pages after relevant images decoded:

```js
// Homepage: viewport 1440×1100; hero decoded.
await page.pdf({
  path, format, scale: 1, displayHeaderFooter: false,
  printBackground: true, preferCSSPageSize: true
});
// format: 'Letter' or 'A4'. Homepage named @page supplies 0.5in margins.
// Gallery: same options plus explicit 0.5in margins on all four sides;
// all 33 .gallery-grid images decoded before printing.
```

| Page | Letter portrait | A4 portrait |
| --- | --- | --- |
| Homepage | 1 page, 612×792pt | 1 page, 595.92×842.88pt |
| Gallery | 7 pages, last page footer only | 19 pages, detached captions confirmed |

`pdfinfo`, `pdftotext -layout` and full-page `pdftoppm` renders inspected. Homepage has complete hero/caption, unchanged opening paragraph, twelve facts, existing contact, public URL and date. No blank/extra page, clipping or overlap observed. Gallery intentionally prints all photos rather than the one-page homepage selection, but F1–F2 need repair.

Owner reported Firefox defaulted to landscape. **No CSS or metadata forces landscape.** `listing.css:199` declares `@page listing-sheet { size: auto; margin: .5in; }`; orientation remains a browser/user choice. Retained Firefox print settings are a plausible explanation, not verified here. Current contract specifies portrait; no orientation change was requested. Firefox print pagination remains unverified.

## Detector findings: intentional choices and false positives

Eight emitted records reduce to these five categories:

| Detector category | Context verdict |
| --- | --- |
| Cramped summary padding | False positive: rendered screen summary has 18px 40px padding; print removes its border. No text touches the claimed bottom boundary. |
| Tight leading, “0.16x” | False positive against rendered body/narrative: desktop narrative is 21.312/35.1648px (1.65). Compact title/price leading is deliberate. No observed .16 line-height. |
| Overused Arial (three records) | Owner-pinned facts/control font, paired with Georgia; changing it violates brief. |
| Cream/beige gallery palette | Owner's Greek Villa/house-color palette, not accidental generic theme. |
| “home theater” (two records) | Literal room use in frozen approved prose/captions, not invented promotional rhetoric. |

No detector-driven palette/font/copy edits recommended. Literal translucent photo/backdrop colors and black/white print colors are documented exceptions, not an uncontrolled theme system. Owner-approved header differences between homepage and gallery are intentional.

## Patterns and positive findings

Main gap is **paged-media coverage**, not broad UI inconsistency: homepage has dedicated print rules; gallery inherits screen navigation and grid fragmentation. Continuous geometry assertions alone cannot prove paginated photo/caption integrity. Responsive-image assertions also need to await the final selected source.

Maintain these strengths:

- Frozen owner copy/captions, exact facts and image hashes; conceptual plan remains clearly distinguished from existing finished space.
- Native HTML controls, working link fallbacks, semantic headings/landmarks, named images/dialogs, visible keyboard focus and contact access.
- Fit-aware sequencing and reduced-motion inline alternatives instead of scroll interception or indiscriminate animation suppression.
- Small static delivery, responsive image sizes and conservative preloading; no need for a framework, font service or new dependency.
- Useful one-page homepage print selection without deleting screen narrative/photos.

## Unverified risks and exclusions

1. Initial parallel `buyer-audit` run failed **“closed viewer does not request initial image”** (`tests/buyer-audit.html:28–29`). Isolated unchanged rerun passed all 39 checks; independent closed-viewer probe made no small-image request. Shared-cache/concurrent-fixture sensitivity is plausible but not proven. Preserve this observation; reproduce before changing product code or adding a separate defect.
2. Safari, Firefox rendering/printing, screen-reader announcements, forced colors, actual browser 200%/400% zoom, text-only enlargement, physical printers and low-end/mobile CPU/network behavior were not certified. CSS viewport and spacing tests are not substitutes for all of these.
3. Image-error regression dispatches synthetic events; no real production network-outage test performed. Source provides recovery text/full-size link, but that is not proof of every network failure mode.
4. Local test server is not deployed hosting. CDN/cache headers, live URL behavior, crawler access, forbidden-file exclusion, publication allowlist enforcement and physical printing remain outside this audit. No release-readiness claim.
5. No new MLS verification or copy rewrite. Dated snapshot and owner-approved internet-speed wording preserved.

## Recommended actions

Tracked in **colonial-vw9**, blocked on this audit until closeout:

1. **[P2] `/impeccable adapt`** — F1/F2: gallery-only print repair; preserve screen skip-link accessibility and all 33 image/caption/concept groups. Verify actual Letter/A4 portrait PDFs and unchanged one-page homepage.
2. **[P2] `/impeccable harden`** — F3: stabilize post-media/resize image decode in existing print fixture without loosening assertions. Extend gallery print navigation checks; keep real pagination verification.
3. **`/impeccable audit`** — rerun affected evidence and unchanged screen/CLI gates; distinguish test failures from product failures.
4. **`/impeccable polish`** — final bounded visual check of repaired print output only; no redesign or frozen-copy edits.

You can ask me to run these one at a time, all at once, or in any order you prefer. Re-run `/impeccable audit` after fixes to measure improvement.

## Evidence references

Durable defect image: [gallery A4 pages 2–3](colonial-hdy-audit-evidence/gallery-a4-pages-2-3.png), joined from full-page PDF renders without altering their contents. SHA-256: `8275dcd6c38434222895446d7ef1d0120098c103c6f1d01d17c573e1ce6fa5cd`.

Private artifacts may expire. The reproducible settings, observations and defect image above remain the durable record.

PDFs copied to `/tmp/colonial-hdy-proof/` (also generated under `/Users/hays/.betterwright/artifacts/85b42e1702877c85/`):

| Filename | SHA-256 |
| --- | --- |
| `colonial-hdy-home-Letter-1791174649443-0d5098.pdf` | `0b53d2c19e6d0ea563fd52c752a6d1f550202cffdc69c687666b9fcaf04d3701` |
| `colonial-hdy-home-A4-1791174649776-f21002.pdf` | `0ef635603ac57cd121e2a152657dcac0bd0ffbd3e272537f818fc49fff1f3e4b` |
| `colonial-hdy-gallery-Letter-1791174645644-889638.pdf` | `b5399b5e3a3258073e4114bb2e8d198064642e0fae2d2a6ab14424406d5f41fb` |
| `colonial-hdy-gallery-A4-1791174648563-97d8cb.pdf` | `06a517f31bc3254c67eb78d7b9d457ad061913f4308cf753757d92432457bff2` |

Private screenshot basenames under the same BetterWright directory:

- Homepage desktop: `pi-evidence-1791174435795-93d73d.png`.
- Homepage mobile contact: `pi-evidence-1791174537374-975ddb.png`.
- Gallery desktop/mobile: `pi-evidence-1791174560273-9305ad.png`, `pi-evidence-1791174578663-339415.png`.
- Both actual homepage PDF renders: `pi-evidence-1791174847671-69fb34.png`.
- Diagnostic sheet of observed fixture/keyboard results, not a product screenshot: `pi-evidence-1791174929313-7b1560.png`.
- Browser checklist `colonial-hdy-audit`: 10/10 inspection requirements evidenced and audited. This marks audit coverage, not absence of defects.

Tooling note: two malformed controls-batch requests made no page mutation; switched to supported Playwright calls after read-only `agnt doctor --json`. Doctor had no failures, with unrelated missing pytest/check-pi-config prerequisites; no environment repair attempted. A broad PDF-preparation selector initially included generated preview images with no src, causing decode rejection; scoped to catalog images. Neither is a buyer-site finding.
