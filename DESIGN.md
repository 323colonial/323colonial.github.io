---
name: "323 Colonial"
description: "House-color property narrative with full-width photography, docking facts and native-scroll photo sequences."
colors:
  greek-villa: "#f0ece2"
  pewter-green: "#5e6259"
  debonair: "#90a0a6"
  sea-salt: "#cdd2ca"
  accessible-beige: "#d1c7b8"
  mahogany: "#593a32"
  cedar: "#8b523c"
  stone: "#969187"
  ink: "#252d29"
  print-paper: "#ffffff"
  print-ink: "#000000"
  muted: "#50564f"
  image-field: "transparent"
  viewer-backdrop: "rgb(25 31 27 / 90%)"
typography:
  property-mark:
    fontFamily: "Georgia, Times New Roman, serif"
    fontSize: "clamp(24px, 2.5vw, 34px)"
    fontWeight: 400
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  property-mark-mobile:
    fontFamily: "Georgia, Times New Roman, serif"
    fontSize: "25px"
    fontWeight: 400
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  property-mark-small:
    fontFamily: "Georgia, Times New Roman, serif"
    fontSize: "22px"
    fontWeight: 400
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  headline:
    fontFamily: "Georgia, Times New Roman, serif"
    fontSize: "clamp(28px, 2.5vw, 36px)"
    fontWeight: 400
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Georgia, Times New Roman, serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.65
  narrative:
    fontFamily: "Georgia, Times New Roman, serif"
    fontSize: "clamp(18px, 1.48vw, 23px)"
    fontWeight: 400
    lineHeight: 1.65
  location:
    fontFamily: "Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
  header-detail:
    fontFamily: "Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.35
  control:
    fontFamily: "Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 700
    lineHeight: 1.5
  summary-link:
    fontFamily: "Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.35
  supporting:
    fontFamily: "Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.6
  caption:
    fontFamily: "Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
  viewer-caption:
    fontFamily: "Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
  metadata:
    fontFamily: "Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.5
  footer:
    fontFamily: "Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.6
  status:
    fontFamily: "Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.35
  detail:
    fontFamily: "Arial, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
  quick-facts:
    fontFamily: "Arial, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.45
  quick-facts-mobile:
    fontFamily: "Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.35
  fact-value:
    fontFamily: "Arial, sans-serif"
    fontSize: "20px"
    fontWeight: 400
    lineHeight: 1.45
  fact-value-compact:
    fontFamily: "Arial, sans-serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.45
  fact-value-mobile:
    fontFamily: "Arial, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.35
  price:
    fontFamily: "Arial, sans-serif"
    fontSize: "30px"
    fontWeight: 700
    lineHeight: 1.2
  price-mobile:
    fontFamily: "Arial, sans-serif"
    fontSize: "25px"
    fontWeight: 700
    lineHeight: 1.2
  viewer-title:
    fontFamily: "Arial, sans-serif"
    fontSize: "16px"
    fontWeight: 700
    lineHeight: 1.4
  viewer-control:
    fontFamily: "Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.4
components:
  button-primary:
    backgroundColor: "{colors.mahogany}"
    textColor: "{colors.greek-villa}"
    typography: "{typography.control}"
    padding: "10px 18px"
  button-primary-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.greek-villa}"
  inline-contact:
    textColor: "{colors.greek-villa}"
    typography: "{typography.header-detail}"
  gallery-link:
    textColor: "{colors.mahogany}"
    typography: "{typography.summary-link}"
  docking-facts:
    backgroundColor: "{colors.greek-villa}"
    textColor: "{colors.ink}"
    padding: "10px 40px"
  narrative-photo-field:
    backgroundColor: "{colors.image-field}"
  scroll-cue:
    textColor: "{colors.ink}"
    typography: "{typography.metadata}"
  photo-note:
    textColor: "{colors.muted}"
    typography: "{typography.caption}"
  photo-dialog:
    backgroundColor: "{colors.greek-villa}"
    textColor: "{colors.ink}"
    padding: "20px 24px"
    width: "min(1100px, calc(100% - 32px))"
---

# Design System: 323 Colonial

## Overview

**Creative North Star: "House-color property narrative"**

House colors frame real property photography and uninterrupted Georgia prose. Persistent address/contact access and compact Arial facts support a quiet, photo-led walk through the home. The owner-pinned composition is implemented in `index.html` and `gallery.html`, not a conventional listing mosaic.

**Key Characteristics:**
- Full-width photographs and alternating, heading-free narrative.
- House-color fields, square controls and fine rules; no shadows.
- Native scrolling with fit-aware inline fallbacks.

Source: `listing.css`, `listing.js` and `gallery.js`; surface contract: `.impeccable/surfaces/index-html.md`. Supplied desktop/mobile finish-review captures in `.impeccable/review/` confirm the composition. This document governs buyer pages, not historical Impeccable comps. Legacy owner/planning pages and their `styles.css` were removed by colonial-yec; buyer styling is unchanged.

## Colors

### Primary
Pewter Green anchors the persistent masthead. Mahogany carries buttons, status, action links, selection and focus; Greek Villa provides their light counterpart.

### Secondary
Sea Salt, Debonair and Accessible Beige are broad narrative fields. The seven fields run Sea Salt, Greek Villa, Accessible Beige, Debonair, Greek Villa, Debonair, Accessible Beige.

### Neutral
Greek Villa is the page, facts and dialog field; Accessible Beige also backs enlarged images. Ink is primary text, muted green-grey is metadata, stone makes fine separators, and cedar marks the facts bar's lower edge. Contain-fit narrative image slots stay transparent so letterboxing matches each surrounding section, including during crossfades; the dark translucent viewer backdrop separates modal focus.

**The House Palette Rule.** These are screen approximations of the owner's colors, not physical paint-match specifications. CSS aliases resolve forest to Pewter Green, paper to Greek Villa, paper-strong to Accessible Beige and rule to stone.

## Typography

Georgia with Times New Roman/serif fallback carries address, section headings and prose; Arial/sans-serif carries facts, captions and controls. No font downloads. Frontmatter records literal source roles, including responsive variants, rather than inventing a new scale.

Narrative is regular-weight fluid type, bounded to 65ch and reset to body size on mobile. Only Property details and the gallery introduction have section headings; the seven narrative passages have none. Price uses tabular numerals. Narrative scroll sequences use decorative position dots with numeric text retained for screen readers; the enlarged viewer shows “Photo N of 65.” Catalog thumbnails carry no visible position strip. Status, expected date, above-grade qualifier, details labels and the essential concept note use 13px at every width; captions also use 13px. Footer and mobile locality stay subordinate at 12px; facts labels, summary links, status and date use 13px Arial. The gallery introduction paragraph alone is capped at 60ch; its heading and gallery grid retain their widths. Prose size and leading remain unchanged.

## Layout

- **Persistent header:** CSS `position: sticky; top: 0`, not fixed positioning. Desktop minimum height 86px, padding 8px 40px; address/locality left, narrow vertical contact stack right on both pages. At 800px and below, contact sits below the address with 8px 20px header padding and 4px row gap; the address link uses a 32px minimum height. At both width ≤800px and height ≤500px, the header scrolls normally to preserve reading space. Script measures actual header and facts heights for sticky offsets and anchor clearance; window resize and height-observer notifications share one animation-frame layout.
- **Hero and facts:** full-width image-only seasonal hero at the original intrinsic aspect ratio. The hero and the sequenced narrative photographs share one 36-second year: 18 knots, 2 seconds apart, each photo dissolving between its own frames. The original image stays first in its link, untouched; a `.season-stack` after it holds two layers, the next frame opaque below and the current frame fading out above, so the dissolve is exact with no additive blending and it composes inside the narrative's scroll opacity. No hero labels or controls; its caption appears only in print. One understated, underlined footer Pause/Resume animation button retains the 44px target and is the only seasonal control. Originals remain the initial/static images and every gallery, catalog and viewer target; reduced motion, save-data, no JavaScript, failed loading and print retain them. Only photographs inside the viewport with non-zero scroll opacity carry seasonal layers or animations, at most three decoded frames each. Pause when nothing seasonal is in view, when hidden, printing or under a dialog. No new dependency; no seasonal layer in galleries or dialogs. Facts retain their normal-flow slot after the hero. Native sticky top and bottom insets keep the bar visible at the viewport bottom while a tall hero fills the screen, then let it travel upward and dock beneath the header. No positioning JavaScript. At viewport heights of 500px or less, facts remain in normal flow and anchor clearance reserves only the persistent header, or 24px when the compact header also scrolls normally. This preserves reading space at high zoom and in landscape, including without JavaScript. No duplicate address block. Desktop facts use a flex row with 10px vertical padding; mobile keeps price/details, vertically stacked facts, and photos/status/date in three columns, with 8px vertical padding and 8px column gaps. The flex row can wrap at enlarged text sizes. Supporting type is unified at 13px; listing content stays unchanged.
- **Narrative:** full-width fields with 56px 40px padding, 64px column gap, 45% text / 55% photos after gaps; even rows reverse sides. No 1200px cap here. Unenhanced photos stack with 28px gaps. At 800px and below, padding is 40px 20px and each paragraph precedes its photos.
- **Details:** the enhanced screen journey ends with narrative/photos and the dated footer, without a repeated closing grid (colonial-pmx). Static source retains the normal-flow section for no-script/failed initialization, unsupported dialogs, print and direct `#details` navigation: 72px 40px padding; three-column definition list with 32px gaps and ruled cells. At 800px and below, padding becomes 48px 20px and the list has two columns with 20px gaps.
- **Gallery and footer:** centered container capped at 1200px, 32px side gutters; gutters become 16px at 700px. Gallery starts at three columns with 40px row / 24px column gaps, drops to two at 1000px and one at 700px (32px gaps). Dialog width is capped at 1100px with 16px viewport margins; mobile padding is 16px.

Responsive max-width boundaries: **1100px** compacts facts; **1000px** changes gallery columns; **800px** stacks header contact, facts, narrative and details layouts; **700px** changes gallery, container and viewer layout; **360px** tightens header/facts gutters and stacks the facts annotation. Agent and both contact links remain visible at every width.

**The Native Scroll Rule.** Native scroll position directly controls reversible crossfades between captioned photographs; scrolling is never captured. On desktop the whole narrative stage sticks below header and facts plus 24px; on mobile only the photo sequence sticks, with 16px clearance after the paragraph. Steps are `max(240px, half the viewport height)`: hold for the first half, blend for the second. The final photo receives a full pinned step after its blend completes. The tallest caption reserves a stable frame; at most two photos blend. Only the images blend; the dominant photo owns the readable, unblended caption, highlighted dot, interaction and accessibility state. A focused photo stays fully visible until focus leaves, then scroll state resumes.

Only nearby sequences (within one viewport below the visible area and not entirely above it) preload their next photograph; distant sequences retain native lazy loading. The closed viewer image also uses native lazy loading; opening it selects the requested full-size image.

Reduced motion, less than 300px available height, or desktop copy taller than the available space disables sequencing for that section. All its photographs then remain inline. No JavaScript also leaves inline photos and working gallery links. Narrative photo changes have no timed transitions, autoplay or parallax; only the owner-approved seasonal dissolve of the photograph in view runs on a clock.

**Print handout (colonial-5dm).** Homepage prints one page on US Letter or A4 portrait at 100% scale, with 0.5in margins and browser headers/footers disabled. Black text on white paper retains Georgia/Arial: 26pt address, 22pt price, 11pt opening paragraph and fact values, 9pt captions/labels. The original uncropped hero and exact caption sit beside the unchanged first paragraph; all twelve facts follow. A print-only footer supplies existing agent/brokerage contact and the public site URL above the unchanged snapshot date. Other narrative paragraphs/photos stay in source and on screen but do not print. No supplemental page, duplicated photo catalog, navigation, sticky positioning or dialog controls. `gallery.html` remains the complete printable photo catalog. `tests/print-layout.html` checks selected-content geometry and fallback modes; actual browser PDF pagination must also be checked on both paper sizes.

## Elevation & Depth

No shadows or blur. Tonal fields and 1px rules provide separation. The header layers above docking facts (z-index 20 / 10). Native dialogs use the browser top layer and the recorded translucent backdrop, and scroll within viewport-height limits. Long text can break within words when necessary; contact labels, dates and dialog control rows wrap rather than overflowing at enlarged text sizes.

## Shapes

Square controls and image frames, without rounded cards or decorative clipping. Hero and inline photos retain natural proportions; sequenced and enlarged images use contain-fit. Source watermarks remain pixels, not new UI decoration. Confirmed solid outer photo margins are trimmed per `assets/listing/margin-review.md`; ambiguous edge pixels and photographic content remain intact.

## Components

- **Address/contact header (colonial-57q):** address is the home link; locality stays visible. Both pages show Liz McDonald and Dandridge Realty Group LLC on single-spaced lines above one row of native links: (304) 885-1547 | Questions & tours. The separator is decorative; the phone accessible name identifies the Dandridge office. Phone remains the approved general brokerage number; the second link opens the clean public Dandridge property listing URL, without query parameters, in the same tab. No popout, email action, external integration or custom contact JavaScript.
- **Actions:** mahogany buttons with paper text, 1px border and 44px minimum height. Hover switches to ink and underlines. Header contacts use underlined 13px Arial native links with 24px minimum height (WCAG 2.2 minimum target size); name and brokerage use 13px/1.35 type. Property details and all-photos links also retain 24px minimum targets; other buttons retain 44px. Text links use underlines; both Property details and all-photos actions use mahogany. The date/action group has no arbitrary width cap. All summary links/status/date use regular 13px/1.35 Arial. Date stays together when it fits and can wrap at enlarged text sizes; narrow fact values use a shared right-aligned number width.
- **Contact placement:** right-aligned compact identity block on desktop, with 13px/1.35 type and no extra row gaps. Phone and tours share a wrapping flex row with an 8px gap around the separator. At 800px and below, contact aligns left below the address. Both links stay in the page, wrapping as needed rather than hiding behind a disclosure.
- **Focus:** 3px mahogany outline with 4px offset; paper outline in the masthead, with zero offset on compact contact links to avoid covering adjacent text. Each page starts with a focus-revealed skip link.
- **Docking facts:** plain-text price above the compact underlined Property details link; at every width, the all-photos action sits above a separate listing-status line (Active) and a single-spaced open-house line while one is scheduled. Four facts stack in the mobile middle column; cedar lower rule. The Property details link opens a native details dialog populated from the closing definition grid; Close or Escape returns focus to that link. Only after dialog initialization succeeds does a readiness class hide the source section on screen; `:target` preserves direct `#details` access. Without enhancement the link reaches the visible original section, which also remains available in print. No sticky contact band at the end.
- **Photo position indicators (colonial-19k, revising colonial-ms9):** narrative scroll sequences retain one decorative dot per local photo, left to right, over the bottom of the contained image—not its letterbox padding. Greek Villa fills the current dot; Pewter Green fills the others, with fine contrasting outlines. No backing strip, clickable dot targets or added animation; screen-reader slide counters remain. Dots do not intercept image links and do not print. Catalogs show captions without repeated 73-dot strips: a static grid has no single current photo, and those tiny marks add clutter rather than useful scroll position. Accessible photo labels and existing hidden catalog numbering remain. On both pages, the enlarged viewer instead shows its existing “Photo N of 65” heading with polite live updates, providing exact sequential position without counting dots.
- **Narrative photo sequence:** exact caption beneath each visible image, with position dots only when enhancement fits. No scroll instructions. Contextual prose links open photos 15, 19, 24, 31 and 32; separate laundry link opens 20. Interior views 34–38 join paragraphs 1, 2 and 4; expanded views 39–73 join all seven sections, including the updated owner basement reverse view. Galleries append additions without renumbering the original 38.
- **Photo catalog/viewer:** View all 65 photos opens a native catalog dialog. Thumbnails and contextual links open the shared enlarged viewer with caption, Previous / Next, adjacent previews, full-size link and Close. Arrows navigate with wraparound; Escape dismisses and focus returns to the opener. Concept images are omitted from tiny adjacent previews. Pending loads expose a polite loading status and hide the previous image so new captions never describe stale pixels. Failed loads expose recovery text; navigation and Close remain available. Without enhancement, `gallery.html` preserves ordered thumbnail links to full-size assets.
- **Concept note:** only photo 31 carries “Conceptual basement plan — not existing finished space.” Its accessible links disclose that distinction while preserving visible link wording. Routine source/seasonal labels are absent; photo 6 is the actual hot tub.
- **Property details/footer:** the full definition grid lives in the pop-out on enhanced screens; its static source remains visible only for fallback, direct-fragment and print access. One dated listing footer per page. No invented cards, inputs, tags or navigation primitives.
- **Analytics privacy (colonial-zoc.2):** a non-sticky 13px Arial notice with 4px vertical padding and a 24px privacy-link target follows the header, linking to a native disclosure before the dated footer. Disclosure copy is 14px Arial, bounded to 75ch; existing mahogany button turns off PostHog and exposes an accessible status. No consent modal or opt-in. Colonial-6ma dismisses the notice after 10 visible-tab seconds, using a 240ms fade/collapse while onscreen (no spacer), immediate scroll-compensated removal when offscreen, and no animation for reduced motion. Focus/hover cancels dismissal; no-JS or blocked storage preserves the notice. A separate 30-day host-only flag remembers dismissal without renewal; the permanent disclosure is labeled Privacy and opt-out. Notice and disclosure do not print; tracking, listing copy, photo assets, dialogs and Cloudflare remain unchanged.

## Do's and Don'ts

- Do preserve the seven approved paragraphs, exact captions, watermarks and conceptual-plan disclosure.
- Do keep contact access, visible keyboard focus and ordinary links available.
- Do use the existing system fonts, static assets and dependency-free enhancement.
- Do keep buyer styling and retained historical image assets intact when pruning unrelated routes.
- Don't replace the approved composition with a mosaic, story headings, Home / Photos navbar or closing contact band.
- Don't crop property evidence with cover-fit or present the conceptual plan as existing finished space.
- Don't intercept scrolling, add timed autoplay outside the seasonal dissolves or parallax, or remove reduced-motion and short-screen fallbacks.
