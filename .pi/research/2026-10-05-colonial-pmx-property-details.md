# Property details: hide repetition, preserve the source

colonial-pmx · 2026-10-05 · baseline `b6907fd454300539808a3b3c5b779173d92d2b1d`.

## Decision and authorization

**Remove the expanded closing grid from the normal enhanced screen journey. Preserve its static HTML and fallback access.** The final narrative/photos now lead directly to the dated footer; docking facts and their pop-out remain the normal details access point.

The ticket began as evaluation only. Initial recommendation to retain the visible grid over-weighted technical fallbacks. After the user asked specifically about visual design, the recommendation changed: preserve the information, not its repeated presentation. The user then explicitly authorized this Bead to remove visibility while preserving no-script, scraper, print and other fallback access. This supersedes the initial retain recommendation; no facts, captions, photographs or frozen paragraphs were authorized to change.

Recovery used only the two named Beads (`colonial-2ua`, `colonial-pmx`), referenced artifacts and current source. No prior transcript. No deployment or push.

## Duplicated versus unique content

All twelve rows occur identically in the closing grid and pop-out. No fact is unique to either presentation. `listing.js` clones `#details .detail-grid`; raw HTML's dialog holds only a heading and Close button.

| Fact | Exact grid/pop-out value | Elsewhere on homepage |
| --- | --- | --- |
| Asking price | $499,000 | Summary and metadata |
| Bedrooms | 2 | Summary and narrative |
| Bathrooms | 2 full · 1 half | Summary/prose abbreviate as 2.5; description metadata has explicit split |
| Finished area | 2,081 sq ft above-grade | Summary, with qualifier |
| Lot size | 2.90 acres, estimated | Summary/prose omit estimate qualifier |
| Year built | 2008 | Not in summary or narrative |
| Lower level | Unfinished walkout basement | Narrative describes walkout basement and future potential; grid explicitly states unfinished |
| HOA | None | Narrative says No HOA |
| Garage | Attached · 2 cars | Narrative gives capacity; photo 11 caption says attached |
| MLS number | WVMO2008198 | Not in summary or narrative |
| Listing status | Coming Soon | Summary |
| Expected on market | October 8, 2026 | Summary |

The dated listing footer is separate and stays visible. No rows should be deleted merely because related prose exists.

## Visual and access assessment

- **Visual ending:** the expanded specification grid repeated accessible information after a photo-led narrative. Removing it saves approximately 531px at desktop 1440px width and 683px at mobile 390px without deleting content. These baseline measurements are not conversion or user-research results.
- **Discoverability trade-off:** the underlined 44px-high Property details opener follows the hero and docks with facts; at desktop 1440×1100 it initially sits below the viewport. At heights ≤500px facts stop docking. Hiding the closing grid removes incidental discovery at the end and its closed-dialog heading from screen-reader browse order. User accepted the cleaner visual ending; no new opener or closing CTA was added.
- **Mobile:** baseline 390×844 dialog fits all facts in 681px height. At 320×568 text wraps and internal scrolling is needed; Close remains visible at the final row. No sampled horizontal overflow. Physical-device and real browser-zoom testing remain unverified.
- **Keyboard and semantics:** native named dialog, `aria-haspopup="dialog"`, semantic definition list, initial Close focus, Escape/Close return to opener. Baseline Tab from sole Close produced `activeElement=BODY`, then Shift+Tab returned Close; do not infer strict focus-loop certification or a background-focus defect from this alone. VoiceOver/NVDA speech was not tested.
- **Source/search:** all twelve facts remain in delivered HTML, without a fetch, script data store or `<noscript>` duplicate. Text scrapers can parse them. Rendered scrapers may honor CSS and need to open the visible pop-out. No indexing/ranking guarantee; no live crawler test or external submission. Existing canonical/search metadata remains unchanged.

## Smallest implementation and preserved contracts

`listing.js` adds `has-dialog` to the source section only after cloning and wiring the supported native dialog. One screen-only CSS rule hides `.details.has-dialog:not(:target)`.

- Disabled scripts, failure before details initialization, or unsupported `showModal`: readiness class is absent, so source grid stays visible.
- Print: hiding rule does not apply; full source grid remains printable and dialogs stay hidden.
- Direct `#details`: native `:target` makes the source grid visible and keeps the fragment useful, including modified-click navigation. Leaving that fragment hides repetition again. Ordinary enhanced opener clicks still open the dialog without changing the URL.
- Static HTML, all twelve values/qualifiers, seven frozen paragraphs, captions and image bytes remain unchanged. No dependency or new state manager.

`tests/property-details.html` adds hidden-layout, fragment restoration, static-fact, unsupported-dialog and failed-initialization checks. Three existing geometry fixtures now scroll to the dated footer rather than the intentionally hidden heading. `PRODUCT.md` and `DESIGN.md` record the revised contract.

## Verification record

Existing local server `http://127.0.0.1:8884/` reused; no processes or unrelated runtime files removed. Baseline source/served HTML SHA-256 matched: `e2aa2b7ac0099997be28cd05ab395f39abaee458a90913c0aa76856cd7a4d80d`.

- Baseline property-details fixture: 54 PASS across 1440×1000, 820×900, 390×844, 320×568 and 800×400 plus no-script fallback.
- Expanded fixture before implementation: 61 PASS, six expected failures (five viewports still showing the grid; fragment exit still showing it).
- After the readiness class and CSS rule: 67 PASS, zero failures.
- Browser evidence and final command matrix are recorded in colonial-pmx closeout notes. Browser coverage is not full accessibility or public-release certification.

No new independent fact verification, physical-device test, screen-reader speech, paginated print preview or live indexing check. Public-release gates from colonial-2ua remain unverified.

## Separate print defect: colonial-uow

User flagged photo/caption overlap during print-media inspection. **Details visibility passes; overall print layout fails.** No print-quality pass is claimed.

Clean baseline reproduction: load `/` at 1440×1100, wait for `.story.is-scrolling`, emulate print, inspect narrative photo 28. Anchor stays flex and 534.60px high; image becomes 900.30px high and extends 182.85px below caption top. Screen `.is-scrolling .media-record > a` retains `height:var(--photo-height)` while print resets only image height to auto.

Follow-up colonial-uow should restore shared print flow, add a failing geometry check across enhanced narrative figures, preserve screen sequencing and inspect pagination. No print-photo fix is included here.

## Private evaluation proof frames

Base `/Users/hays/.betterwright/artifacts/85b42e1702877c85/`; host files may expire. These are **baseline evaluation** frames, not final implementation proofs:

- `pi-evidence-1791170333880-ea555f.png`: all twelve dialog facts and keyboard focus.
- `pi-evidence-1791170352670-9821f4.png`: original expanded closing grid.
- `pi-evidence-1791170377134-f3988a.png`: narrow dialog, final rows, persistent Close.
- `pi-evidence-1791170400200-5e66d9.png`: printable details with unrelated photo overlap; not print-quality approval.
- `pi-evidence-1791170516903-f0c5df.png`: clean print-overlap reproduction.
