---
name: 323 Colonial
description: Buyer-first property monograph led by verified photography and plainly labeled planning records.
direction: Mountain House Monograph
colors:
  forest: "#183828"
  forest-ink: "#172c24"
  warm-paper: "#f7f6eb"
  strong-paper: "#f3f0e6"
  rule: "#98a096"
  muted: "#536059"
  white: "#ffffff"
typography:
  display: "Georgia, Times New Roman, serif"
  body: "Georgia, serif"
  label: "Arial, sans-serif"
shape: "Square corners, hairline rules, no shadows"
---

# Design System: 323 Colonial

## Direction

**Mountain House Monograph** presents 323 Colonial as a specific house with evidence, not a generic lifestyle concept. Prospective buyers see actual-property photography first, concise facts second, then planning records. Warm paper and forest ink give the site a restrained book-like character; square records and compact labels make claims easy to verify.

## Evidence hierarchy

1. **Current property:** prior-listing photography of actual 323 Colonial leads every route. Retain and disclose the Bright MLS watermark.
2. **Property facts:** dates, room relationships, materials, and current-condition notes follow photography.
3. **Planned work:** AI-edited imagery is secondary and always labeled **Planned-work visualisation**.
4. **Reference material:** floor and basement drawings are orientation, planning, and pricing aids only. State that they are not field-measured, construction, or permit documents.
5. **Estimates:** use budgeting ranges and preserve estimate-not-quote caveats.

Never use invented architecture as property evidence.

## Visual tokens

Tokens live in `styles.css`.

- **Forest `#183828`:** mastheads, showing bands, and high-emphasis controls.
- **Forest ink `#172c24`:** headings and body text.
- **Warm paper `#f7f6eb`:** page field.
- **Strong paper `#f3f0e6`:** summary and planning bands.
- **Rule `#98a096`:** dividers and record boundaries.
- **Muted `#536059`:** caveats, captions, and secondary metadata.
- **White `#ffffff`:** image and table records.

Interface stays flat: no gradients, shadows, rounded cards, or decorative color detached from property evidence.

## Typography

- **Display:** Georgia, then Times New Roman or generic serif. Use light visual weight, tight tracking, and compressed line-height for the property mark and large headings.
- **Body:** Georgia or generic serif for narrative and descriptive copy.
- **Labels:** Arial or generic sans-serif for navigation, facts, provenance, status, tables, and controls.
- **Dependency rule:** fonts use local system stacks; pages make no remote font request.

Serif tells the property story. Sans-serif certifies facts and status.

## Layout

### Home hero

At the approved 1376×768 viewport, the masthead is a narrow forest band. Hero below uses a 67/33 split:

- left: verified exterior photograph with provenance label;
- right: location, stacked `323 Colonial` title, short deck, three features, showing CTA, secondary planning link, real-room evidence, and reference-plan evidence.

At 980px and below, masthead wraps and hero becomes a vertical document. Photography remains first. At 390px, every section uses one readable column except paired evidence thumbnails.

### Editorial sections

Sections alternate warm-paper and forest fields. Headings align with short explanatory text; photography uses an asymmetrical ledger on desktop and single-column records on mobile. Planning links form a quiet bordered index rather than competing with showing actions.

### Planning routes

Planning pages share buyer masthead first and compact planning navigation second. Introductory current-property photography precedes plans, visualisations, or estimates. Tables reflow to viewport width on mobile rather than creating nested horizontal scrolling.

## Components

### Buyer masthead

- Property mark at left.
- Primary buyer navigation: The house, Rooms, Outdoors, Floor plans.
- Paper showing control at right.
- Mobile interactive targets are at least 44px high.

### Showing controls

`Request a showing` is the dominant action and uses `realtor@stevenhay.com`. Forest controls appear on paper; paper controls appear on forest. Square border, uppercase sans label, visible keyboard focus.

### Media records

Photography and visualisations use the same square-edged record frame but different status language. Captions stay attached to images. Planned-work status must be visible on the image and repeated in nearby copy when ambiguity remains.

### Plans

Plan sheets sit on white paper with a hairline border. Captions repeat `reference`, `not field-measured`, and intended planning/pricing use. Plans never lead a route ahead of current-property photography.

### Tables

Tables use white cells, pale green headers, one-pixel boundaries, and tabular numbers. Desktop preserves comparison alignment. Mobile uses fixed layout, wrapping labels, and compact cells without horizontal scrolling.

### Focus and motion

Every route starts with a keyboard-visible skip link to main content. Links and controls use a two-pixel `:focus-visible` outline with offset. Scroll-linked hero drift runs only when reduced motion is not requested; content and meaning never depend on motion.

## Content rules

### Do

- Lead with photographs of actual 323 Colonial.
- Name image provenance and current/planned/reference status.
- Keep buyer navigation and showing actions visually primary.
- Use factual room, material, and outdoor descriptions.
- Repeat limitations where plans or estimates could be mistaken for promises.

### Do not

- Present AI imagery as existing condition.
- Present rough drawings as measurements or construction documents.
- Promote planning records above current-property evidence.
- Use inflated luxury-listing language or unsupported claims.
- Add remote fonts, frameworks, or runtime dependencies.
