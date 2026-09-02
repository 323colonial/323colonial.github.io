---
name: 323 Colonial
description: A warm, domestic property record grounded in wooded photography and material evidence.
colors:
  forest-ink: "#26302a"
  canopy-green: "#2c3e33"
  woodland-link: "#cfe0d4"
  warm-paper: "#f7f5f1"
  card-white: "#ffffff"
  sage-rule: "#b9c9bd"
  fieldstone-border: "#c8c3b8"
  caption-moss: "#4c5a50"
  soft-sage-band: "#e7ede8"
  weathered-note: "#5c564c"
  quiet-stone-text: "#7a736a"
  alabaster: "#edeae1"
  quilt-blue: "#7a8b94"
  sea-glass: "#cbd5cc"
  fieldstone-grey: "#b0a99c"
  pewter-green: "#5b675c"
  walnut-stain: "#4a3428"
typography:
  display:
    fontFamily: "Georgia, serif"
    fontSize: "44px"
    fontWeight: 400
    lineHeight: "normal"
    letterSpacing: "1px"
  headline:
    fontFamily: "Georgia, serif"
    fontSize: "30px"
    fontWeight: 400
    lineHeight: "normal"
    letterSpacing: "0.5px"
  title:
    fontFamily: "Georgia, serif"
    fontSize: "22px"
    fontWeight: 400
    lineHeight: "normal"
    letterSpacing: "normal"
  body:
    fontFamily: "Georgia, serif"
    fontSize: "15.5px"
    fontWeight: 400
    lineHeight: 1.65
    letterSpacing: "normal"
  label:
    fontFamily: "system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "normal"
rounded:
  none: "0px"
spacing:
  fine: "6px"
  compact: "8px"
  text-gap: "10px"
  inset: "14px"
  grid-gap: "18px"
  section-gutter: "40px"
  home-gutter: "48px"
  hero-rise: "70px"
components:
  masthead:
    backgroundColor: "{colors.canopy-green}"
    textColor: "{colors.card-white}"
    typography: "{typography.headline}"
    rounded: "{rounded.none}"
    padding: "34px 40px 26px"
  section-navigation:
    backgroundColor: "{colors.canopy-green}"
    textColor: "{colors.woodland-link}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "10px 48px"
  section-heading:
    textColor: "{colors.forest-ink}"
    typography: "{typography.title}"
    rounded: "{rounded.none}"
    padding: "0 0 8px"
  image-card:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.caption-moss}"
    rounded: "{rounded.none}"
    padding: "0"
  palette-swatch:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.forest-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "0"
  table-header:
    backgroundColor: "{colors.soft-sage-band}"
    textColor: "{colors.forest-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.none}"
    padding: "7px 14px"
  information-band:
    backgroundColor: "{colors.soft-sage-band}"
    textColor: "{colors.forest-ink}"
    rounded: "{rounded.none}"
    padding: "6px 0 22px"
---

# Design System: 323 Colonial

## Overview

**Creative North Star: "The Woodland Survey"**

323 Colonial should feel like a carefully assembled house book made at the property: warm, domestic, and quietly aspirational, but always grounded in photographs, measurements, material choices, and owner decisions. Woodland greens, warm paper, fieldstone neutrals, oak-brown imagery, and an editorial serif make the site inviting without turning it into a sales fantasy.

The interface stays restrained so the house remains the subject. Photography establishes atmosphere; square-edged records, captions, swatches, and tables establish trust. Reject glossy luxury-listing hype: polish should come from proportion, legibility, and evidence rather than inflated claims or ornamental effects.

**Key Characteristics:**
- Property photography leads; interface color supports it.
- Georgia serif carries place and domestic warmth; system sans-serif carries facts and metadata.
- Warm paper, evergreen fields, sage rules, and fieldstone borders create quiet continuity.
- Square corners, hairline borders, and no shadows keep records direct.
- Dense planning information remains calm through consistent gutters, measures, and alignment.

## Colors

Palette takes its character from canopy shade, fieldstone, oak, warm interior paint, and the muted Quilt & Stone room colors.

### Primary
- **Canopy Green** (#2c3e33): Dark evergreen field for mastheads and navigation; it anchors the site without competing with photography.
- **Forest Ink** (#26302a): Near-black green for body copy and headings; it softens contrast against warm paper while remaining authoritative.

### Secondary
- **Woodland Link** (#cfe0d4): Pale green reserved for links and secondary text on dark evergreen surfaces.
- **Soft Sage Band** (#e7ede8): Light green-grey used for table headers and information bands where tonal grouping is clearer than elevation.

### Tertiary
- **Alabaster** (#edeae1): Warm interior white represented in the documented paint palette.
- **Quilt Blue** (#7a8b94): Muted blue-grey tied to the main bedroom and regional textile reference.
- **Sea Glass** (#cbd5cc): Pale green-grey tied to the main bath.
- **Fieldstone Grey** (#b0a99c): Warm stone neutral tied to bedroom-wing rooms.
- **Pewter Green** (#5b675c): Deep exterior green tied to doors and garage doors.
- **Walnut Stain** (#4a3428): Dark brown tied to deck and porch floors.

These property colors are evidence and content, not a general-purpose rainbow for interface accents.

### Neutral
- **Warm Paper** (#f7f5f1): Default page canvas.
- **Card White** (#ffffff): Image cards, plan sheets, swatches, and table bodies.
- **Sage Rule** (#b9c9bd): Section dividers and broad tonal boundaries.
- **Fieldstone Border** (#c8c3b8): Card, swatch, and table outlines.
- **Caption Moss** (#4c5a50): Image-caption and secondary card text.
- **Weathered Note** (#5c564c): Explanatory notes and caveats.
- **Quiet Stone Text** (#7a736a): Footer copy and lowest-emphasis metadata.

### Named Rules

**The House Before UI Rule.** Use interface greens and neutrals to frame photography; never recolor the interface with every room paint.

**The Evidence Palette Rule.** Paint colors identify actual material decisions. Do not use them decoratively where readers could mistake color for project status or meaning.

## Typography

**Display Font:** Georgia (with generic serif fallback)

**Body Font:** Georgia (with generic serif fallback)

**Label Font:** System UI (with generic sans-serif fallback)

**Character:** Georgia gives the property record a familiar bookish warmth. System sans-serif makes navigation, captions, tables, quantities, and caveats scan like practical annotations rather than promotional copy.

### Hierarchy
- **Display** (400, 44px, normal line height, 1px tracking): Home hero title only.
- **Headline** (400, 30px, normal line height, 0.5px tracking): Secondary-page mastheads.
- **Title** (400, 22px on the home page; 19px on dense secondary pages): Section headings with a sage hairline beneath.
- **Body** (400, 15–15.5px, 1.6–1.65 line height): Narrative explanation, held to roughly 820–840px.
- **Label** (400–600, 11–14px): Navigation, captions, notes, swatches, table data, and footer metadata. Bold is reserved for names, decisions, and table headers.

### Named Rules

**The Serif Speaks, Sans Certifies Rule.** Use serif for the house narrative and section hierarchy; use sans-serif for navigation, labels, quantities, status, and evidence notes.

**The Quiet Weight Rule.** Hierarchy comes primarily from size, family, spacing, and rules. Avoid heavy display weights.

## Layout

Pages use a left-anchored editorial layout rather than a centered application shell. Home content keeps 48px side gutters; secondary records use 40px. Narrative measures stop near 820–840px, headings near 1000–1100px, and media grids may extend to 1400–1500px.

Photo grids use intrinsic responsive filling: 340px minimum cards with 18px gaps on the home page, and 310px minimum cards with 16px gaps on secondary pages. Cards collapse to one column on narrow viewports without a breakpoint-specific redesign. Navigation wraps into additional rows; the 48px content gutter and 44px hero title remain fixed at the observed 390px viewport.

Section rhythm is generous above and tight below: home headings use 42px top spacing and 8px bottom spacing; secondary headings use 34px above and 6px below. Hero imagery spans the full viewport width and is cropped with `object-fit: cover`; room imagery uses a 3:2 frame, while product imagery uses 16:9.

## Elevation & Depth

System is flat, tonal, and border-defined. It uses no shadows. Depth comes from full-width evergreen fields, warm-paper background, white records, pale sage bands, image contrast, and single-pixel rules.

### Named Rules

**The No Shadow Rule.** Separate surfaces with tone, whitespace, and a one-pixel fieldstone border; do not lift cards above the page.

**The One Plane Rule.** Cards and tables belong to the document plane. Hover effects must not make static evidence appear draggable or interactive.

## Shapes

Form language is rectangular and architectural. Cards, swatches, tables, headers, and plan sheets use square corners (0px radius) and crisp one-pixel borders. Photographs are clipped to consistent rectangles rather than decorative masks. Broad horizontal rules echo plan sheets and field notes.

**The Square Record Rule.** Keep informational surfaces square. Rounded containers would soften the documentary character and imply an application UI that does not exist here.

## Components

Components feel tactile and welcoming through photography, paper tones, and close-set captions—not through shadows, pills, or exaggerated state effects.

### Mastheads
- **Shape:** Full-width, square, dark evergreen field.
- **Typography:** White Georgia headline with system-sans metadata beneath.
- **Spacing:** 34px top, 40px sides, 26px bottom on secondary pages.
- **Links:** Pale woodland green; underline on hover.

### Navigation
- **Style:** Dark evergreen strip with compact pale-green system-sans links.
- **Spacing:** 10px vertical and 48px horizontal; links keep 22px separation and wrap naturally on narrow screens.
- **State:** Hover adds an underline without changing layout or color hierarchy.

### Section Headings
- **Style:** Regular-weight Georgia with a one-pixel sage rule below.
- **Behavior:** More space above than below; width follows the page's reading measure rather than spanning every media grid.

### Photo Cards
- **Corner Style:** Square.
- **Background:** White.
- **Border:** One-pixel fieldstone outline.
- **Media:** 3:2 crop for rooms and house views; 16:9 for product references.
- **Caption:** Compact system sans-serif, usually 12.5px, with 9px vertical and 12–13px horizontal inset.

### Palette Swatches
- **Style:** Fixed-width white record with a 64px color field above concise system-sans identification.
- **Border:** Same one-pixel fieldstone outline as photo cards.
- **Typography:** Paint name leads in semibold; code and room assignment follow at smaller size.

### Tables
- **Style:** White, collapsed-border records using compact system-sans text.
- **Header:** Pale sage fill with semibold labels.
- **Cells:** One-pixel fieldstone borders and 7px by 14px padding; numeric columns align right and do not wrap where totals must compare.

### Information Bands
- **Style:** Pale sage full-width band bounded by sage rules.
- **Purpose:** Group one major supporting topic without introducing a raised card or a second visual hierarchy.

No button, input, chip, dialog, or form-field pattern exists in the current site. Do not infer one from unrelated application conventions.

## Do's and Don'ts

### Do:
- **Do** let property photography provide visual drama while interface surfaces stay restrained.
- **Do** preserve the serif narrative and system-sans evidence split.
- **Do** keep captions visibly attached to their image, swatch, plan, or table.
- **Do** use warm paper, white records, evergreen fields, and one-pixel stone or sage boundaries consistently.
- **Do** label visualisations and planning material clearly wherever imagery could be mistaken for completed work.

### Don't:
- **Don't** introduce glossy luxury-listing styling, inflated promotional effects, or visual claims unsupported by the property record.
- **Don't** round cards, add floating shadows, or turn static evidence into app-like tiles.
- **Don't** use the Quilt & Stone room colors as arbitrary interface accents.
- **Don't** replace real house imagery with generic real-estate stock photography.
- **Don't** invent controls or component variants until a real interaction requires them.
