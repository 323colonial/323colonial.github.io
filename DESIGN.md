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
  muted: "#50564f"
  image-field: "rgb(240 236 226 / 25%)"
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
    lineHeight: 1.6
  control:
    fontFamily: "Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 700
    lineHeight: 1.5
  control-mobile:
    fontFamily: "Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 700
    lineHeight: 1.5
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
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.65
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
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.45
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
    lineHeight: 1.45
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
  showing-disclosure:
    textColor: "{colors.greek-villa}"
    typography: "{typography.control}"
    padding: "12px 16px"
  gallery-link:
    textColor: "{colors.mahogany}"
    typography: "{typography.control}"
  contact-panel:
    backgroundColor: "{colors.greek-villa}"
    textColor: "{colors.ink}"
    typography: "{typography.supporting}"
    padding: "24px"
    width: "min(380px, calc(100vw - 32px))"
  docking-facts:
    backgroundColor: "{colors.greek-villa}"
    textColor: "{colors.ink}"
    padding: "18px 40px"
  narrative-photo-field:
    backgroundColor: "{colors.image-field}"
  scroll-cue:
    textColor: "{colors.ink}"
    typography: "{typography.metadata}"
  photo-note:
    textColor: "{colors.muted}"
    typography: "{typography.metadata}"
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

Source: `listing.css`, `listing.js` and `gallery.js`; surface contract: `.impeccable/surfaces/index-html.md`. Supplied desktop/mobile finish-review captures in `.impeccable/review/` confirm the composition. This document governs buyer pages, not legacy `styles.css` or historical Impeccable comps.

## Colors

### Primary
Pewter Green anchors the persistent masthead. Mahogany carries buttons, status, action links, selection and focus; Greek Villa provides their light counterpart.

### Secondary
Sea Salt, Debonair and Accessible Beige are broad narrative fields. The seven fields run Sea Salt, Greek Villa, Accessible Beige, Debonair, Greek Villa, Debonair, Accessible Beige.

### Neutral
Greek Villa is the page, facts and dialog field; Accessible Beige also backs enlarged images. Ink is primary text, muted green-grey is metadata, stone makes fine separators, and cedar marks the facts bar's lower edge. Translucent Greek Villa fills contain-fit narrative image slots; the dark translucent viewer backdrop separates modal focus.

**The House Palette Rule.** These are screen approximations of the owner's colors, not physical paint-match specifications. CSS aliases resolve forest to Pewter Green, paper to Greek Villa, paper-strong to Accessible Beige and rule to stone.

## Typography

Georgia with Times New Roman/serif fallback carries address, section headings and prose; Arial/sans-serif carries facts, captions and controls. No font downloads. Frontmatter records literal source roles, including responsive variants, rather than inventing a new scale.

Narrative is regular-weight fluid type, bounded to 65ch and reset to body size on mobile. Only Property details and the gallery introduction have section headings; the seven narrative passages have none. Price and counters use tabular numerals. Metadata bottoms out at 12px, including mobile facts annotations and dates; there are no 10px or 11px text roles. Captions remain distinct from the smaller essential concept note.

## Layout

- **Persistent header:** CSS `position: sticky; top: 0`, not fixed positioning. Desktop minimum height 102px, padding 18px 40px; address/locality left, agent/public listing/showing disclosure right. Script measures actual header and facts heights for sticky offsets and anchor clearance.
- **Hero and facts:** one full-width exterior at intrinsic aspect ratio, caption below. Facts begin after it in normal flow, then dock beneath the header. At viewport heights of 500px or less, facts remain in normal flow and anchor clearance reserves only the persistent header. This preserves reading space at high zoom and in landscape, including without JavaScript. No duplicate address block. Desktop facts use a flex row; mobile uses two columns with facts spanning a second row.
- **Narrative:** full-width fields with 56px 40px padding, 64px column gap, 45% text / 55% photos after gaps; even rows reverse sides. No 1200px cap here. Unenhanced photos stack with 28px gaps. At 800px and below, padding is 40px 20px and each paragraph precedes its photos.
- **Details:** normal-flow closing section, 72px 40px padding; three-column definition list with 32px gaps and ruled cells. At 800px and below, padding becomes 48px 20px and the list has two columns with 20px gaps.
- **Gallery and footer:** centered container capped at 1200px, 32px side gutters; gutters become 16px at 700px. Gallery starts at three columns with 40px row / 24px column gaps, drops to two at 1000px and one at 700px (32px gaps). Dialog width is capped at 1100px with 16px viewport margins; mobile padding is 16px.

Responsive max-width boundaries: **1100px** hides the header agent and compacts facts; **1000px** changes gallery columns and limits summary action width; **800px** switches header, facts, narrative and details layouts (header minimum 88px); **700px** changes gallery, container and viewer layout; **360px** tightens header gutters and stacks the facts annotation. Hidden header information remains available through the showing disclosure.

**The Native Scroll Rule.** Native scroll position directly controls reversible crossfades between captioned photographs; scrolling is never captured. On desktop the whole narrative stage sticks below header and facts plus 24px; on mobile only the photo sequence sticks, with 16px clearance after the paragraph. Steps are `max(240px, half the viewport height)`: hold for the first half, blend for the second. The final photo receives a full pinned step after its blend completes. The tallest caption reserves a stable frame; at most two photos blend. Only the images blend; the dominant photo owns the readable, unblended caption, counter, interaction and accessibility state. A focused photo stays fully visible until focus leaves, then scroll state resumes.

Only nearby sequences (within one viewport below the visible area and not entirely above it) preload their next photograph; distant sequences retain native lazy loading. The closed viewer image also uses native lazy loading; opening it selects the requested full-size image.

Reduced motion, less than 300px available height, or desktop copy taller than the available space disables sequencing for that section. All its photographs then remain inline. No JavaScript also leaves inline photos and working gallery links. Print removes sticky positioning and exposes every narrative photo. There are no timed transitions, autoplay or parallax.

## Elevation & Depth

No shadows or blur. Tonal fields and 1px rules provide separation. The header layers above docking facts (z-index 20 / 10); its bordered contact panel opens below it. Native dialogs use the browser top layer and the recorded translucent backdrop. The contact panel and dialogs scroll within viewport-height limits.

## Shapes

Square controls and image frames, without rounded cards or decorative clipping. Hero and inline photos retain natural proportions; sequenced and enlarged images use contain-fit. Source watermarks remain pixels, not new UI decoration. Confirmed solid outer photo margins are trimmed per `assets/listing/margin-review.md`; ambiguous edge pixels and photographic content remain intact.

## Components

- **Address/contact header:** address is the home link; locality stays visible. Native See in person disclosure contains agent, brokerage call and public listing links. Escape closes it and restores summary focus when no dialog is open; outside clicks close it.
- **Actions:** mahogany buttons with paper text, 1px border and 44px minimum height. Hover switches to ink and underlines. Showing disclosure has a paper outline; text links use underlines, with mahogany assigned to the gallery action. Mobile disclosure/gallery action type uses the compact control role.
- **Focus:** 3px mahogany outline with 4px offset; paper outline in the masthead, mahogany again inside its paper contact panel. Each page starts with a focus-revealed skip link.
- **Docking facts:** underlined Property details link in the heading with plain-text price, status, four facts, all-photos action and expected date; cedar lower rule. The Property details link opens a native details dialog populated from the closing definition grid; Close or Escape returns focus to that link. Without enhancement the link reaches the original closing details section, which also remains available in print. No sticky contact band at the end.
- **Narrative photo sequence:** exact caption beneath each visible image, then a stone-ruled, right-aligned current/total counter when enhancement fits. No scroll instructions. Contextual prose links open photos 15, 19, 24, 31 and 32; separate laundry link opens 20.
- **Photo catalog/viewer:** View all 33 photos opens a native catalog dialog. Thumbnails and contextual links open the shared enlarged viewer with caption, Previous / Next, adjacent previews, full-size link and Close. Arrows navigate with wraparound; Escape dismisses and focus returns to the opener. Concept images are omitted from tiny adjacent previews. Failed loads expose recovery text. Without enhancement, `gallery.html` preserves ordered thumbnail links to full-size assets.
- **Concept note:** only photo 31 carries “Conceptual basement plan — not existing finished space.” Its accessible links disclose that distinction while preserving visible link wording. Routine source/seasonal labels are absent; photo 6 is the actual hot tub.
- **Property details/footer:** compact definition grid followed by one dated listing footer per page. No invented cards, inputs, tags or navigation primitives.

## Do's and Don'ts

- Do preserve the seven approved paragraphs, exact captions, watermarks and conceptual-plan disclosure.
- Do keep contact access, visible keyboard focus and ordinary links available.
- Do use the existing system fonts, static assets and dependency-free enhancement.
- Do keep buyer styling isolated from unchanged legacy pages and assets.
- Don't replace the approved composition with a mosaic, story headings, Home / Photos navbar or closing contact band.
- Don't crop property evidence with cover-fit or present the conceptual plan as existing finished space.
- Don't intercept scrolling, add timed autoplay or parallax, or remove reduced-motion and short-screen fallbacks.
