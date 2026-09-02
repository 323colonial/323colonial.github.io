# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Owner is primary user. Prospective realtors may receive site during sale preparation so they can understand house, planned work, likely listing presentation, and remaining decisions.

## Product purpose

Prepare and market 323 Colonial for sale. Site keeps house presentation, sale-prep choices, budget ranges, floor plans, and basement potential in one place. Success means owner and prospective realtors can decide what work matters before listing without mistaking plans for completed work.

## Positioning

Site ties its claims to this property's photographs, owner decisions, cost notes, and CAD-derived plans. It shows both current evidence and planned changes instead of presenting a generic real-estate brochure.

## Operating context

Static site is published through GitHub Pages and shared by URL. Owner uses it while sale-prep work is still underway. Prospective realtors may review it before listing. Public-listing photography comes after work is complete.

## Capabilities and constraints

- Keep site as static HTML and CSS with no build step.
- Preserve navigation among marketing, colour scheme, floor-plan, and sale-prep pages.
- Label every AI-edited image as a visualisation of planned work.
- Never imply unfinished work is complete.
- Describe budget figures as estimates, not quotes.
- Preserve verified house facts and owner decisions.
- Treat basement drawings as pricing information, not construction or permit documents.

## Brand commitments

Name is 323 Colonial. Voice is specific, factual, and restrained. Avoid listing hype. "Quilt & Stone" names confirmed colour scheme. Existing greens, warm white, stone grey, oak, and fieldstone come from house and its setting, but visual implementation belongs in DESIGN.md rather than this record.

## Evidence on hand

- `images/photo-*.jpg`: prior-listing photographs. MLS watermark remains, so public listing needs new photography.
- Other files in `images/`: AI visualisations based on house photographs. Captions must identify them as intent, not completed work.
- `images/plan-A-4.png` and `images/plan-A-5.png`: rough main-floor and second-floor plans derived from sketch and photographs, not field measurements.
- `sale-prep.html`: owner decisions and budgeting ranges for paint, faucets, cabinet hardware, and landscaping.
- Basement drawing set and pricing history exist in separate CAD project and convey with house.

## Product principles

- Separate present condition, planned work, and completed work.
- Make every material claim traceable to house evidence or an owner decision.
- Help owner and realtor compare sale impact against cost.
- Keep source plain enough to review without a framework or build tool.
