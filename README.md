# 323 Colonial

A photo-led website for a house in Berkeley Springs, West Virginia, built to help prospective buyers understand the property before arranging a visit. It pairs an owner-approved narrative with photographs, property details, and direct links to the listing brokerage.

**[Visit the website](https://323colonial.github.io/) · [Browse the photo gallery](https://323colonial.github.io/gallery.html)**

This repository contains the website, its image-authoring tools, and an experimental 3D reconstruction. The public website is deliberately smaller than the repository: two pages and their supporting assets. Research, source records, tests, and the walkthrough stay outside the website’s publication bundle.

This README describes the current source, which may be ahead of the deployed site. Listing information is a dated snapshot, not a live MLS feed; consult the brokerage for current availability and details.

## The idea

A listing gallery shows what a house looks like. This project connects those photographs to a reading experience: seven passages introduce the house, its rooms, outdoor spaces, and setting, while the accompanying images show the relevant views.

The visual design borrows from the house’s colors: dark mahogany, Debonair blue, Sea Salt, Accessible Beige, and Greek Villa. Georgia carries the narrative; Arial keeps facts and controls compact. These are system fonts, so the site needs no font downloads. The screen colors suggest the finishes rather than promise physical paint matches.

The implementation uses static HTML, CSS, and JavaScript without a frontend framework. JavaScript adds motion and in-page viewers; the underlying text, photographs, and ordinary links remain useful without it.

## What visitors can explore

### A three-photo opening view

The default homepage opens with one large photograph beside two smaller photographs. The large pane shows house exteriors and an owner-selected hot-tub view. The smaller panes draw from outdoor, aerial, porch, and deck photographs.

After an eight-second pause, the composition changes through sliding transitions. The smaller pair moves downward; periodic changes to the main image move the pair to the opposite side. This opening display is the one part of the site that changes photographs automatically. The narrative below advances with the reader’s scroll.

The masthead’s **Pause/Resume animation** control governs both the photo rotation and seasonal effects. Reduced-motion and data-saving preferences keep the opening composition still. Without JavaScript, the page retains its original single-photo opening. The `?variant=singlehero` option also selects that earlier layout.

The three-photo preview crops images to fill its panes. The gallery and enlarged viewer preserve the photographs’ full framing.

### A narrative, not an endless carousel

Scrolling through the seven passages brings their associated photographs into view. Where the screen has enough room, the images crossfade as the reader scrolls forward or backward. The page does not intercept scrolling or force a reading pace.

On small or short screens, or with reduced motion enabled, the site can show ordinary inline photographs instead. The property-details link opens a native browser dialog when JavaScript is available and reaches the same information within the page otherwise.

### The complete photo collection

The current catalog contains **65 images**. Visitors can open the catalog from the homepage or use the separate gallery page. The enlarged viewer provides captions, previous and next controls, keyboard navigation, and links to full-size images.

Photo identifiers remain stable even when a photograph leaves the catalog. Gaps in filenames and numbered links are intentional; the visible viewer count still runs from 1 to 65.

One image is a **conceptual basement plan, not existing finished space**. The site preserves that distinction in its caption and accessible description.

### Contact and print

The header keeps the listing agent and brokerage visible, with a telephone link and a **Questions & tours** link to the brokerage’s public listing. The website does not collect inquiries itself or promise an instant tour booking.

The homepage also has a print layout intended as a one-page property handout. It keeps the original opening photograph, introductory paragraph, property facts, contact information, and listing date. The gallery provides the fuller printable photo collection.

## Seasonal imagery

The homepage can show the house and its setting through a simulated year. Selected photographs dissolve through prepared seasonal and lighting variations, all following a shared 36-second cycle. The small seasonal dial in the masthead follows that same cycle and doubles as the pause control.

These variations are generated or edited interpretations of listing photographs—not a record of photographs taken throughout a year. The browser displays prepared WebP files; it does not call an image-generation service.

Only visible photographs need active seasonal layers. Motion pauses when the page is hidden, a dialog is open, or no seasonal photograph is in view. The runtime coordinates image loading so visible photographs stay on the same seasonal phase. The non-seasonal listing images remain the gallery images and the fallback for reduced motion, data saving, printing, and unavailable enhancement.

The current seasonal set lives in [`assets/seasons-next/`](assets/seasons-next/). Its [`frames.json`](assets/seasons-next/frames.json) records the photographs, frame positions, and timing. Each generated frame has a large version and a smaller version for narrower displays. The older `assets/seasons/` set remains in the repository but is not part of the publication allowlist.

## How content and images are maintained

The site separates approved copy, image records, and generated photo markup.

| Part | Source of truth |
| --- | --- |
| Narrative and page structure | [`index.html`](index.html), with approved prose checked against [`tests/fixtures/approved-listing.json`](tests/fixtures/approved-listing.json) |
| Photo captions, stable IDs, derivative metadata, and source history | [`assets/listing/manifest.json`](assets/listing/manifest.json) |
| Photo selection and narrative placement | [`scripts/build-listing.py`](scripts/build-listing.py) |
| Layout, colors, and responsive behavior | [`listing.css`](listing.css), with rationale in [`DESIGN.md`](DESIGN.md) |
| Seasonal frame selection and timing | [`assets/seasons-next/frames.json`](assets/seasons-next/frames.json) |

The site preserves the seven approved narrative paragraphs verbatim. A copy change needs an updated approval record, not merely an HTML edit. Price or status changes also need a review of the visible facts, page titles, sharing metadata, and dated footer. None updates automatically from a listing service.

For photo changes, edit the manifest and, when needed, the placement lists. Then regenerate the marked photo regions:

```sh
python3 scripts/build-listing.py
```

The generator updates photo markup in `index.html` and `gallery.html`; it leaves the surrounding prose and page structure alone. To check for stale markup without writing files:

```sh
python3 scripts/build-listing.py --check
```

Keep existing photo IDs when replacing images, and preserve the conceptual-plan disclosure. Older extraction scripts reproduce historical inputs and should not overwrite current derivatives.

### Image processing and provenance

The repository keeps records of source images, edits, dimensions, and hashes. Current listing images include owner-authorized watermark removal. Reconstructed corner texture is synthetic detail, not recovered photographic evidence. The [conversion record](docs/watermark-conversion.md) explains the scope and accepted limits; the [margin review](assets/listing/margin-review.md) records separate trims of solid outer borders.

In runtime documentation, “original” means the current non-seasonal listing image. It does not necessarily mean an untouched camera file or the archived pre-edit source.

Seasonal authoring lives under [`scripts/seasons/`](scripts/seasons/). The tools include image-generation requests, alignment, lighting adjustments, and export recipes. They run during asset preparation, not in the visitor’s browser. Some recipes need private working files, so a fresh checkout alone cannot reproduce every asset. See [authoring tools](docs/authoring-tools.md) before running them; generation requests can upload reference images and use a paid API.

After an approved large seasonal frame changes, regenerate the small versions with the ImageMagick-based tool:

```sh
node scripts/build-seasons-small.mjs
node scripts/build-seasons-small.mjs --check
```

The build regenerates all small seasonal frames. The check validates inventory and dimensions, not visual quality or whether matching-size files contain the latest pixels. Review and commit each changed large/small pair together.

## Analytics and privacy

The website uses PostHog to measure visits, photo and property-detail interest, estimated engagement, contact-link clicks, and interaction heatmaps. It also includes a separate Cloudflare Web Analytics integration.

The PostHog implementation limits collection in several ways:

- A random first-party identifier represents a **browser, not a verified person**. Its cookie expires 90 days after creation rather than renewing indefinitely.
- Global Privacy Control, Do Not Track, and a saved opt-out prevent PostHog collection. Local previews and unsupported routes are excluded.
- General automatic event capture, session replay, and person profiles are disabled. Heatmaps contain pointer coordinates, not video recordings or form contents.
- The event sanitizer excludes raw query strings, raw referrers, contact addresses, and page text. Source and campaign labels come from a fixed set.
- The documented account configuration adds approximate country, region, and city while discarding client IP from stored analytics. Providers still receive IP addresses when handling network requests; this is not a promise of anonymous transport or no provider logs.

The **Privacy and opt-out** disclosure remains available near the footer. Its button stops future PostHog collection in that browser and clears the site’s analytics identifier; it does not erase records already delivered to the service. Cloudflare analytics remains separate.

The page can hide the brief notice below the header after ten seconds in a visible tab. A separate 30-day cookie remembers that dismissal. Dismissing the notice does not grant consent or change tracking preferences.

The site’s disclosure states that PostHog processes events in its US Cloud and retains them for a rolling year. It also commits the owner to stopping collection and deleting analytics after the sale. These are operating commitments, not actions this repository performs automatically. Counts should be read as browsers, visits, and clicks—not people, inquiries, or completed tours.

See [Buyer analytics](docs/analytics.md) for the event definitions, privacy controls, reporting caveats, and account-verification history.

## Building and publishing

There is no frontend compilation step. The HTML, CSS, scripts, and delivery images are already present. “Building” the website for publication means assembling an isolated directory containing only approved public files.

[`scripts/publish-files.txt`](scripts/publish-files.txt) is the exact publication allowlist. [`scripts/build-pages.mjs`](scripts/build-pages.mjs) checks those paths and copies them into a new output directory:

```sh
# Run from the repository root. The output must not already exist.
node scripts/build-pages.mjs /tmp/colonial-site-candidate
```

The parent directory must exist. The script rejects an existing output directory so stale or unintended files cannot remain in the bundle. It stages files locally; it does not deploy them.

The [GitHub Actions workflow](.github/workflows/publish.yml) is configured to validate pushes to `main` and pull requests. Once GitHub Pages uses the Actions source, successful non-pull-request runs on `main` stage and deploy the allowlisted bundle. Validation covers the buyer-facing Node and Python checks plus Chromium browser tests. A failed check blocks that release.

Source code alone does not establish which revision is live or whether that Pages setting has been activated. See [Publishing](docs/publishing.md) for activation, prerequisites, checks, deployment verification, and recovery.

**Do not publish the repository root.** The allowlist excludes authoring records, tests, source manifests, experimental pages, and private local files from the website artifact. That boundary does not make tracked repository files or Git history private.

## The experimental 3D walkthrough

Alongside the listing site, this repository contains a first-person walkthrough built with Three.js and a Blender-generated model. It supports walking, mouse-look, stairs, collision, running, jumping, and crouching.

The reconstruction combines:

- An approximate building shell derived from vector floor plans from the listing’s 3D tour.
- Hand-built geometry for stairs, roof elements, kitchen fittings, furniture, and outdoor structures.
- Photo crops applied to selected surfaces, such as cabinetry and wall art.
- Baked lighting, lightmaps, and runtime reflections.

It is an experiment in reconstructing a recognizable house from plans and photographs, not a survey or a validated photorealistic model. The garage, basement, and closets are closed. Geometry and camera alignment still limit fidelity, and physical-device GPU performance remains unverified.

**The walkthrough is not linked from the buyer pages or included in the publication allowlist.** Some artwork uses copyrighted images whose rights must be resolved before public release. Publishing the walkthrough also requires an owner decision; its presence in this repository is not release approval.

The [walkthrough guide](docs/walkthrough.md) covers local inspection, controls, Blender export, lighting, and model limitations. The [great-room pilot review](docs/great-room-pilot.md) explains why further photorealistic expansion remains on hold. The [authoring-tools guide](docs/authoring-tools.md) distinguishes small offline checks from generation requests and full-scene bakes.

## Repository guide

| Path | What it contains |
| --- | --- |
| [`index.html`](index.html), [`gallery.html`](gallery.html) | The two buyer-facing pages |
| [`listing.css`](listing.css) | Shared styling, responsive layouts, and print rules |
| [`listing.js`](listing.js), [`gallery.js`](gallery.js) | Narrative enhancement, dialogs, photo viewing, and notice behavior |
| [`visitor-display.js`](visitor-display.js) | The rotating three-photo opening composition |
| [`seasonal-hero.js`](seasonal-hero.js) | Shared seasonal animation for the opening display and narrative |
| [`analytics.mjs`](analytics.mjs), [`analytics-core.mjs`](analytics-core.mjs) | Analytics initialization, privacy gates, event policy, and sanitization |
| [`assets/listing/`](assets/listing/), [`assets/seasons-next/`](assets/seasons-next/) | Listing images, seasonal frames, and their source records or manifests |
| [`scripts/`](scripts/) | Content generation, image processing, staging, and experimental authoring tools |
| [`walkthrough/`](walkthrough/), [`assets/walkthrough/`](assets/walkthrough/) | The unpublished 3D viewer and its prepared assets |
| [`vendor/`](vendor/) | Pinned third-party browser libraries and their licenses |
| [`tests/`](tests/) | Content, behavior, privacy, rendering, and publication checks |
| [`docs/`](docs/) | Focused technical guides and review records |

For the project’s intent and constraints, start with [PRODUCT.md](PRODUCT.md). For the visual system and interaction rules, read [DESIGN.md](DESIGN.md). Both include historical decisions; later revisions may supersede earlier descriptions. The [accessibility review](docs/buyer-accessibility.md) records checks and remaining limits rather than claiming universal device coverage.
