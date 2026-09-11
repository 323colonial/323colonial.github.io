# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Prospective buyers are primary users. Realtors and the owner use the site as supporting audiences when answering questions, arranging showings, and reviewing sale-prep records.

## Product purpose

Present 323 Colonial clearly enough for a prospective buyer to understand the house, explore its rooms and outdoor living, and request a showing. Three public destinations—The house, Gallery and Floor plans—describe the finished house. Owner colour decisions and budgets remain separate from the buyer journey.

## Positioning

Site ties property claims to house photography, verified facts, approved owner improvements or reference plans. Buyer copy describes approved improvements as complete under a strict pre-publication confirmation gate; simulated images remain explicitly identified.

## Operating context

Static site uses GitHub Pages. This rewrite is local, not authorization to push or publish. Before publication, the owner/realtor must confirm every advertised improvement is complete and provide authorized fresh listing photography. Until then, retained Bright MLS prior-listing images are identified as such and may show earlier finishes.

## Capabilities and constraints

- Keep site as static HTML and CSS with no build step.
- Public navigation: The house (`index.html`), Gallery (`gallery.html`), Floor plans (`floorplans.html`), plus Request a showing via `realtor@stevenhay.com`.
- Public AI-edited imagery carries the exact attached label **Digitally simulated image**. Colours and staging are approximate.
- Do not publish finished-house copy until advertised upgrades are confirmed complete. The basement remains unfinished; preserve two bedrooms, two full baths and one half bath.
- Owner records remain at `brochure.html` and `sale-prep.html`, unlinked from public pages, with owner navigation and `noindex, nofollow`. They are URL-accessible, not private or authenticated.
- Describe budget figures as estimates, not quotes.
- Preserve verified house facts and owner decisions.
- Treat basement drawings as pricing information, not construction or permit documents.

## Brand commitments

Name is 323 Colonial. Voice is specific, factual, and restrained. Avoid listing hype. "Quilt & Stone" names confirmed colour scheme. Existing greens, warm white, stone grey, oak, and fieldstone come from house and its setting, but visual implementation belongs in DESIGN.md rather than this record.

## Evidence on hand

- `images/photo-*.jpg`: prior-listing photographs. MLS watermark remains, so public listing needs new photography.
- Other property imagery in `images/`: AI visualisations based on house photographs. Public captions identify digital simulation; owner records retain their planned-work status and original caveats.
- `images/plan-A-4.png` and `images/plan-A-5.png`: rough main-floor and second-floor plans derived from sketch and photographs, not field measurements.
- `sale-prep.html`: owner decisions and budgeting ranges for paint, faucets, cabinet hardware, and landscaping.
- Basement drawing set and pricing history exist in separate CAD project and convey with house.

## Product principles

- Let prospective buyers see the actual house and reach a showing request quickly.
- Separate photographic evidence from digital simulation, and keep physical completion verification at the publication gate.
- Make every material claim traceable to house evidence or an approved owner decision; never invent appliance brands, models or installation dates.
- Keep owner planning and pricing records outside public navigation.
- Keep source plain enough to review without a framework or build tool.
