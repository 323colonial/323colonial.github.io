---
name: 323 Colonial
description: Photo-led property listing with a restrained forest and warm-paper identity.
colors:
  forest: "#183828"
  ink: "#172c24"
  paper: "#f7f6eb"
  paper-strong: "#f3f0e6"
  rule: "#98a096"
  muted: "#536059"
  white: "#ffffff"
typography:
  display:
    fontFamily: "Georgia, Times New Roman, serif"
    fontSize: "clamp(32px, 3.2vw, 44px)"
    fontWeight: 400
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Georgia, Times New Roman, serif"
    fontSize: "18px"
    lineHeight: 1.65
  label:
    fontFamily: "Arial, sans-serif"
rounded:
  default: "0"
components:
  button-primary:
    backgroundColor: "{colors.forest}"
    textColor: "{colors.paper}"
    padding: "12px 20px"
  button-paper:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.forest}"
    padding: "12px 20px"
---

# Design System: 323 Colonial

## Overview

**Photo-led property listing** retains the forest/warm-paper identity while using familiar property-listing structure. Actual property photography, scannable facts and brokerage contact take priority over owner planning. The approved brief pins this conventional presentation; no new decorative identity or scroll choreography.

Buyer pages use `listing.css`. Legacy `floorplans.html`, `brochure.html` and `sale-prep.html` retain their original `styles.css` and Mountain House Monograph layout, unchanged and unlinked from buyer navigation. Historical Impeccable comps/build state/sidecar describe that earlier composition, not the current public layout; separate tool/sidecar maintenance is outside this task.

## Colors

Forest anchors masthead, contact band and primary controls. Warm paper is the page field; ink carries primary text. Muted green-grey carries photo numbers and essential labels; rule grey separates sections and facts. Strong paper supports the enlarged-image field.

Palette contrast on paper: ink 13.60:1, forest 11.83:1, muted 6.07:1. Use paper text on forest; do not substitute low-contrast grey for contact-band copy.

## Typography

Georgia gives headings and exact listing prose a restrained residential character. Arial makes facts, captions, navigation, price and controls easy to scan. Both use installed system fonts; no remote font requests.

Body is 18px with 1.65 line height; paragraph measure is bounded at 68ch. H1 scales from 32–44px; h2 from 28–36px; story headings are 28px, reducing to 25px on mobile. Captions are 14px and essential placeholder/concept labels 12px; compact mosaic captions use 12px. Price uses bold 32px sans-serif and tabular numbers.

## Layout

Content is capped at 1200px with 32px desktop gutters and 16px mobile gutters. The home mosaic uses a 2:1 grid: specified exterior on the left, great room and porch on the right. Address, price, key facts and dated status follow. Section navigation stays in normal document flow.

Story sections use equal text/photo columns, 56px apart; paired images share the photo column. At 700px and below, text and all matching captioned images stack in reading order. Supporting hero photos stay paired. Gallery uses three columns, two at 1000px, one at 700px. Images retain natural proportions; there is no CSS cover-cropping of watermarks or evidence.

Major sections separate by 64px desktop / 40px mobile. Story rows use 40px desktop / 32px mobile vertical padding. Contact is a two-column forest band, stacking on mobile. No sticky photographs, scroll effects, smooth-scroll animation or autoplay.

## Elevation & Depth

Flat surfaces, no shadows. Hairline rules and forest fields establish hierarchy. Native modal viewer uses a dark-green backdrop (`rgb(10 24 17 / 90%)`) solely to distinguish protected viewing focus from the inert page behind it.

## Shapes

Square image frames and controls, no rounded cards. Photographs are content, not background decoration. Aspect ratios stay intrinsic, including portrait-like source imagery and the conceptual drawing.

## Components

- **Navigation:** Overview / About the home / Property details / Photos / Contact. Sans-serif links wrap on narrow screens; Photos indicates the gallery’s current page.
- **Brokerage controls:** forest on paper or paper on forest, 44px minimum height, explicit brokerage wording. Hover darkens the field or adds an underline.
- **Focus:** visible 3px current-colour outline with 4px offset; each route begins with a keyboard-visible skip link.
- **Photo records:** image link and exact approved caption. Routine source notes are omitted; provenance stays in the asset manifest. Only placeholder/concept images carry short attached labels. Gallery numbers represent real sequence, not decoration. Placeholder photo is explicitly not this property; conceptual plan is explicitly not existing finished space.
- **Enlarged viewer:** native `<dialog>`, labeled title and caption, Previous / Next, Close, full-size fallback. Arrow keys navigate, Escape dismisses, focus returns to the opener. Image-load failure exposes recovery text. Images use contain-fit, never crop-fit.
- **No-JavaScript fallback:** gallery image links open the optimized full-size asset directly. No framework or runtime fetch is required.

## Do's and Don'ts

- **Do** preserve exact approved prose, caption order, image provenance and watermarks.
- **Do** distinguish listing facts, third-party placeholder imagery and conceptual drawings.
- **Do** show the listing date once in each footer and keep brokerage contact explicit.
- **Do** keep buyer styling isolated from legacy pages and assets.
- **Don't** present a placeholder, simulation or plan as evidence of existing property condition.
- **Don't** reintroduce owner paint planning or rough main/upstairs drawings into buyer navigation.
- **Don't** add animation, sticky changing images, autoplay, remote fonts or runtime dependencies.
