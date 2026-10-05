# Colonial-9t3 — buyer homepage SEO and findability

Assessment: 5 October 2026. Recommendations only; no site changes, publication, URL submissions, account connections or outbound contact.

## Verdict

**Good source foundations; public search readiness NOT VERIFIED.** No source-level indexing blocker found in the two buyer pages. Their static text, real links, descriptive image alternatives and responsive layout are useful foundations. Missing canonical, sitemap, social tags and structured data are not themselves indexing blockers.

Publication has two unresolved gates: identify and authorize the actual public deployment, and reconfirm the dated listing facts/rights. After those gates, prioritize consistent URL identity and search/share metadata. Optional schema and sitemap work comes later. No ranking, traffic, indexing, rich-result or exact-snippet promise is supported.

This is an SEO assessment, not another full Impeccable/a11y audit or an SEO-score calculation.

## Scope, authority and evidence boundary

- Beads recovered: only `colonial-7mz` and `colonial-9t3`, with their referenced artifacts. No prior transcript or unrelated work history recovered.
- Binding context: `PRODUCT.md`, `DESIGN.md`, `.impeccable/surfaces/index-html.md`. Preserve seven frozen paragraphs, exact captions, facts, house colors, Georgia/Arial, uncropped property evidence, conceptual-plan disclosure and accessible/native fallbacks.
- Source baseline: `a1b461d6410ccc43b3d831d6657c7144f1397bd5`. Homepage SHA-256: `e45d7ccdfa82559f97228acf0b08c4a65673f71625a58cb297c2ebd12ac7966b`; gallery: `9dd3de2bdeb111ff2312db703b6019fd99b6d55cf1c7475acac01ae3418a36bb`.
- Prior critique: `.impeccable/critique/2026-10-05T02-29-57Z__index-html.md`. Homepage fingerprint matches. Its catalog-numbering and mobile-scroll-pacing recommendations remain UX work, not new SEO defects here. No redesign, extra story headings or closing contact band recommended.
- **Deployment evidence:** PRODUCT explicitly calls implementation local-only. No tracked `CNAME`, robots/sitemap, recognized Netlify/Vercel configuration, `_headers`, `_redirects` or `.github` deployment workflow found in scoped inventory. `package.json` contains test tooling, not a deployment script. No owned public origin established. This does not prove no older public site exists elsewhere.
- **Local HTTP evidence:** existing `127.0.0.1:8883` server, untouched. GETs for both buyer pages returned 200, `text/html`, no `X-Robots-Tag`, and byte-for-byte source matches. `robots.txt`, `sitemap.xml`, `floorplans.html`, `brochure.html`, `sale-prep.html` returned 404 locally. None establishes production headers, redirects, crawling or indexing.
- **Fresh browser evidence:** desktop homepage 1440×1100; mobile homepage/contact/gallery 390×844. Browser evidence checklist audited ready. Mobile homepage document width equaled viewport width, 390px. No horizontal overflow in that sampled state. Address/locality, facts, gallery access, named brokerage and phone link visible. No call placed.
- **Unknown:** public host/domain ownership, DNS/TLS, deployment revision, production redirects/headers/cache/compression, crawler access, indexed URLs, backlinks, search volume/rankings, Search Console ownership/data, analytics and field Core Web Vitals. No account access established or used. Public Redfin destination was identified in source, not freshly checked for listing truth or link availability.

## Source inventory

| Surface | Observed evidence | Assessment |
| --- | --- | --- |
| Search titles | `index.html:3`: `323 Colonial Dr · Berkeley Springs, WV · $499,000`; `gallery.html:6`: `Photos · 323 Colonial Dr` | Distinct, meaningful titles. Homepage carries maintenance-sensitive price; gallery omits locality from title. Neither is a confirmed search defect. |
| Descriptions | `index.html:4`: mountain home, acreage, beds/baths, porch/deck; `gallery.html:7`: 33 ordered photographs/labeled concepts, address and Berkeley Springs, West Virginia | Unique summaries exist. Homepage description lacks address/locality and explicit listing context. Gallery wording can be made more precise: only one conceptual plan among 33 views. |
| Semantics/content | One address H1 per page; `lang=en`, viewport, main landmark, skip link, figures/captions; homepage seven static paragraphs and closing twelve-fact definition list | Meaningful HTML, not a JavaScript-only shell. Heading-free narrative is deliberate; no SEO justification for violating approved design. Dialog copies do not replace the source details. |
| Crawl links | `index.html:12–25`: ordinary `gallery.html`, `gallery.html#photo-N`, `#details`; gallery thumbnails link full-size WebP; home link on both pages | Linked buyer journey remains discoverable without click handlers. All local anchor destination files exist; frozen listing tests pass. Photo fragments are positions within one gallery page, not 33 separate indexable pages. |
| Indexing/identity | Both heads lack robots directives and canonical; no root robots/sitemap file | No HTML `noindex`/`nofollow` barrier. Explicit `index,follow` is unnecessary. Production headers/access still decisive [S1–S3]. |
| Images | Homepage 61 source `img` nodes = 27 hero/narrative + 33 closed catalog + 1 viewer; gallery 34 = 33 photos + viewer. All have nonempty alt and width/height. Native lazy loading on 60/61 and 33/34 respectively | Repeated UI nodes are not 61 unique images or evidence of 61 network transfers. Hero/first gallery image has high fetch priority, not lazy. Descriptive captions and context already strong [S7]. |
| Enhancement | `listing.js:10–35` hides/inerts inactive story figures and preloads nearby next images; `gallery.js:1–85` enhances real links into native dialogs | Do not assume Google scrolls sequences or opens dialogs. All 33 image sources are independently present in ordinary gallery HTML; retain that fallback [S8]. |
| Sharing/schema | No Open Graph, Twitter Card, JSON-LD or other structured-data markup found in either page | Optional metadata opportunity, not failure to be indexed. No current rich-result eligibility claim [S9–S13]. |
| Owner records | Only `index.html` and `gallery.html` remain root HTML; removed owner pages are not linked | Preserve removal and any separately retained noindex protections. Source assessment cannot certify protections on old deployed copies. |

## Prioritized recommendations

Priorities mean work order, not proven production incidents. **P1 gates** must be resolved before any publication; **P2 improvements/checks** are worthwhile after authorization; **P3 enhancements** are optional. Effort excludes waiting for owner/host access. Every change needs later implementation authorization.

### P1-G1 — Establish public target and safe publication boundary

**Evidence/location:** PRODUCT local-only boundary; deployment inventory and local HTTP checks above. Repository still contains historical assets, provenance, tests and private/tooling directories.

**Smallest next step:** owner identifies canonical HTTPS origin, hosting target and approved publish revision. Define a deployment allowlist for the two buyer pages, `listing.css`, both scripts and the exact required buyer images—not the whole repository or whole historical asset tree. Preserve originals locally. Keep `.git`, `.beads`, `.pi`, `.impeccable`, owner records, tests, manifests/review notes and unused simulations outside public output. If owner records must remain privately accessible, use authentication/access controls; **noindex is not privacy**.

For retired public routes with no replacement, verify genuine 404/410 responses rather than redirecting everything to the homepage or serving a 200 soft-404. If any legacy HTML remains intentionally accessible on another approved surface, preserve its noindex and allow compliant crawlers to read that directive; robots disallow alone is not a deindexing substitute [S2, S5]. Do not restore removed pages merely to add noindex.

**Benefit:** establishes eligibility/access evidence and prevents accidental exposure or owner-page search contamination. **Effort/dependencies:** small deployment audit, host/owner authorization required. **Verify later:** public GETs for both pages/assets; exact deployed source revision; TLS/redirect chain; robots and `X-Robots-Tag`; no login/challenge for intended public content; forbidden files absent; retired routes error correctly. Use already-authorized Search Console inspection only if available. This gate is unresolved, not a finding that production is blocked [S1].

### P1-G2 — Reconfirm facts and assign update responsibility

**Evidence/location:** `index.html:3,14–16,19–25,28–34,77`; both footers; PRODUCT snapshot as of October 3, 2026. Current source says $499,000, Coming Soon, expected October 8. No current confirmation obtained.

**Smallest next step:** owner/brokerage confirms price, actual status, measurements, improvements and photography rights before publication or any public Offer/listing markup. Name who maintains price/status across title, facts, footer, share tags and any future schema. Do not advance status automatically on October 8 or silently update metadata while leaving frozen visible facts inconsistent.

Known conflicts/qualifications: owner-reconfirmed **up to 7-gigabit** copy versus contemporaneous MLS **5-gigabit** wording; 2,081 sq ft is **above grade**, basement unfinished; 2.90 acres **estimated**, including additional parcels; photo 31 is a **conceptual plan**, not finished space. Phone is brokerage office, not Liz's direct number. Do not infer rental income, legal rental use, guest capacity, completed renovations, precise boundaries or coordinates. Omit disputed speed from new metadata/schema pending reconciliation; changing frozen prose requires separate approval.

**Benefit:** avoids stale search/share claims and misleading machine-readable facts [S5, S9]. **Effort/dependencies:** small editorial check; owner/brokerage response is gating. **Verify later:** timestamped approval against visible content and all metadata; exact-copy tests remain green. No revised price/status or public listing-markup template supplied by this assessment.

### P2-1 — Choose one homepage URL; keep gallery independently canonical

**Evidence/location:** missing canonical in both heads; internal home links use `index.html`. Public `/` versus `/index.html`, host aliases and preview domains remain unknown—not confirmed duplicates.

**Smallest future change:** after G1, choose preferred homepage route and host, add absolute self-referential canonical to each buyer page, and align internal home links. If deployment exposes duplicate homepage routes/hosts, use host-supported permanent redirects where appropriate. Keep `gallery.html` self-canonical: it is a useful separate image destination, not an alias for the homepage. Never use Redfin, localhost or a guessed domain as canonical. Do not use noindex or robots blocking to solve ordinary duplicate URL selection [S3].

**Benefit:** consistent URL identity across search, shares and links; possible signal consolidation, not guaranteed ranking gain. **Effort/dependencies:** small, chosen origin/routing required. **Verify:** public URL/redirect matrix, one canonical per head, canonical targets return 200 and remain indexable; compare Google-selected canonical only with authorized Search Console access.

### P2-2 — Improve search snippets and sharing without rewriting narrative

**Evidence/location:** titles/descriptions and absent share tags in both heads. Homepage description could describe many homes; gallery title lacks locality. Current price-bearing title creates update burden.

**Smallest future change:** owner-approved metadata-only revision. Include address/locality in homepage description, keep a short factual property summary, and add Berkeley Springs/WV to gallery title if useful. Describe gallery as 33 views including a labeled conceptual basement plan rather than implying several concepts. Consider a price-free homepage title if no reliable update owner exists; retain address and locality. Only add current sale/status wording after G2. Do not keyword-stuff or alter seven paragraphs/captions.

Add Open Graph `og:title`, `og:type=website`, `og:url`, `og:image`, description and image alt/dimensions using approved absolute public URLs [S13]. Preferred image: real exterior position 1, not the conceptual basement, retired simulation or unused hot-tub placeholder. Reuse approved uncropped asset if intended clients support it; create a derivative only if compatibility testing requires it, preserving property evidence and originals. Twitter-specific cards are optional, contingent on actual target-channel needs, not a dependency to add now.

**Benefit:** clearer address-query relevance and more intentional shared previews; actual selection remains controlled by search engines/social clients. No universal title/description character-limit pass/fail or promised CTR gain [S5–S7]. **Effort/dependencies:** small; G1/G2 and metadata/photo approval. **Verify:** inspect raw heads for consistency and absolute URLs; fetch share image with correct MIME/dimensions; later test real previews only with separately authorized public URL submission/sharing. No preview debugger submission performed here.

### P2-3 — Validate image discovery and real mobile performance before optimizing

**Evidence/location:** gallery retains all 33 linked `img src` entries and exact captions; sequence visibility depends on JS/scroll. `listing.css:20–41,145–190`, image sizes/srcsets in both pages, `listing.js:10–89`.

**Smallest next step:** preserve gallery as crawlable HTML; do not replace links with button-only/modal-only content. On authorized public target inspect rendered HTML for representative hero, later gallery photo and conceptual image URLs; verify image fetches and crawler permissions. Native lazy loading is supported, but homepage hidden slides/closed catalog alone are not proof of image indexing [S7–S8]. Keep photo 31's explicit alt/caption disclosure. Numeric filenames offer weaker descriptive clues, but mass-renaming stable manifest-backed images is low-value churn relative to existing rich captions/alt text. No rename recommended.

Measure cold-load mobile behavior and scroll/dialog interactions before compressing further or rewriting sequencing. Existing strengths: WebP, responsive `srcset`/`sizes`, dimensions, deferred small scripts, local system fonts, native lazy loading, fit-aware reduced-motion/short-screen fallback. Do not lazy-load hero or strip accessibility to chase scores.

**Benefit:** verifies actual image accessibility and identifies real loading bottlenecks without speculative redesign. **Effort/dependencies:** small measurement pass, public/staging target and representative devices/network. **Verify:** cold mobile lab runs, LCP candidate, image requests, layout shifts and interaction traces. Field targets are p75 LCP ≤2.5s, INP ≤200ms, CLS ≤0.1, segmented mobile/desktop [S14]; local timings are not field Core Web Vitals. Small site may lack enough field data. No full accessibility, no-JS, reduced-motion or slow-network browser matrix rerun here; prior source fallbacks retained, not newly certified.

### P3-1 — Optional small sitemap and legitimate referral discovery

**Evidence/location:** two internally linked buyer pages; no sitemap. New site's external links and search demand unknown.

**Smallest future change:** optional static two-entry XML sitemap of approved canonical buyer URLs after G1, especially if launch has few inbound links. No plugin, generator service or 33 fragment entries needed. An image extension for approved gallery image URLs is optional if image discovery evidence warrants it. Only truthful content-change dates; exclude retired routes, private records and tooling. `robots.txt` can advertise sitemap and state deliberate policy, but its absence is not a blocker [S4, S7].

Address/local intent is already strong: street/city/state/ZIP in persistent header; MLS in details; frozen prose covers mountain home, acreage, Cacapon, D.C./Baltimore access. Likely useful query themes include exact address/MLS and Berkeley Springs mountain/second-home searches; these are intent hypotheses, not researched keyword volumes or ranking claims. Prefer accurate owner/brokerage-approved listing/referral links over new keyword landing pages or city stuffing. Existing outbound Redfin link is not evidence of an inbound link.

**Do not create a Google Business Profile for the house.** For-sale properties are explicitly ineligible; a qualifying brokerage office is a different entity and is not this property's address [S12]. No account creation, directory submission, profile edit or brokerage outreach authorized here.

**Benefit:** supplemental discovery and consistent references. **Effort/dependencies:** small sitemap; referral coordination depends on brokerage permission. **Verify:** XML URLs match live canonicals and 200 responses; inspect approved incoming links if later arranged. Search Console submission is a separate authorized action, not part of this report.

### P3-2 — Optional semantic schema, not a real-estate rich-result promise

**Evidence/location:** no schema in either head. Google's supported search-feature gallery lists no dedicated for-sale `RealEstateListing` rich result [S10]. Schema vocabulary support is not Google feature eligibility.

**Recommendation now:** defer implementation/public listing markup pending G1/G2. After reconfirmation, the smallest semantic option is `WebPage` describing a `SingleFamilyResidence` with a `PostalAddress` and representative actual-house image. `RealEstateListing` describes the listing web page and is in Schema.org's “new” area; it is optional vocabulary, not an SEO requirement [S11]. Do not force Product, VacationRental, LocalBusiness or review/rating markup to chase unrelated features. A weekend-home audience does not turn a for-sale house into a bookable vacation rental; Google's rental feature also has separate onboarding/eligibility requirements [S15].

If later authorized: distinguish page, physical residence and brokerage; include only verified visible facts and use stable IDs on confirmed origin. Represent two bedrooms, two full baths and one partial bath separately. Schema `numberOfBathroomsTotal` is integer **3**, not displayed marketing shorthand **2.5**. Do not confuse bedrooms with total rooms. If including area, preserve the above-grade meaning and proper units (`FTK` for square feet); omit a structured measurement rather than misstate its scope. Do not convert estimated acreage into surveyed area. Exclude conceptual photo 31 from images representing existing finished property. No invented coordinates, offer availability enum, reviews, ratings or amenities. Offer/price/status remains gated on reconfirmation and update responsibility [S9, S11].

**Benefit:** explicit entity semantics for compatible consumers; no guaranteed rich results or rankings. **Effort/dependencies:** small-to-medium semantic/content validation; G1/G2. **Verify later:** JSON parsing, Schema.org vocabulary/range validation, and field-by-field comparison with approved visible content. A Google Rich Results Test reporting no supported item does not prove valid residence schema is invalid, nor does a valid schema test prove a Google enhancement. External validator submissions require separate authorization.

## Loading evidence, not a benchmark

Uncompressed disk sizes: homepage **52,753 B**, gallery **28,422 B**, CSS **12,845 B**, gallery JS **3,670 B**, listing JS **5,737 B**. Hero full **321,188 B**; small **102,304 B**. All 33 full WebPs total **5,352,970 B**; all 33 small variants total **1,980,454 B**. These are asset inventory totals, not initial page weight.

A desktop load followed by mobile resize selected the already-loaded full hero and recorded CSS, both scripts, hero, photo 11 full and photo 3 small requests. Warm resize cannot assess fresh mobile image selection. No measured LCP/INP/CLS, Lighthouse score, mobile network throughput, compression or production cache claim. Keep source optimization strengths; measure before adding formats, CDN, bundling or further compression. Existing scroll code's layout work is a profiling target, not a demonstrated performance failure.

## Verification and review

Executed this session:

- `node --test tests/*.test.mjs` — **PASS, 7 tests**; includes root-route inventory and tooling/design checks.
- `python3 tests/test_listing.py` — **PASS, 11 tests**; frozen content, links and image/provenance checks.
- HTMLParser inventory — both pages one H1, all source images with nonempty alt/dimensions, no missing local anchor destination files; metadata inventory confirmed omissions above.
- Loopback GET/source-byte comparison and retired-route status checks — **PASS for stated local observations only**.
- Browser `colonial-9t3-local-findability` — **4/4 proof items, audited ready**. Screenshots below.
- Two independent cold, self-contained peer reasoning checks, same routed model (`openai-codex/gpt-6-astra`), no repository/history access. Peers did not independently browse or verify sources. Accepted cautions: discovery ≠ indexing; publish allowlist must include exact dependencies; assign ongoing fact-maintenance owner; retain measurement qualifiers; omit disputed speed/conceptual imagery from property markup.
- Primary external guidance located with `agnt web-search`, then fetched and checked for relevant content. All cited source URLs returned 200. Schema.org RealEstateListing initially returned gzip bytes through text helper; `curl --compressed -fsSL` recovered readable primary HTML. No tooling/config repair.

Peer results: `runtime:delegated-results/b24830e6-7f7e-48c9-ba85-2961f7ee086d/child-0.json`, `runtime:delegated-results/08eb612f-8d73-4377-8068-069dbcce58c7/child-1.json`. These are private runtime references, not required to understand this report.

Report-only verification does not establish release readiness. Full product regression/browser matrix, actual zoom, screen-reader behavior, live SERPs, public crawl, current listing verification and account analytics remain **NOT VERIFIED**. No source or frozen fixture changes recommended as already approved.

### Local screenshot register

Private host base: `/Users/hays/.betterwright/artifacts/85b42e1702877c85/`. Captures are not portable and may expire under host quota; written observations above are durable.

| Evidence | File |
| --- | --- |
| Desktop identity and full exterior hero | `pi-evidence-1791167623625-2c977d.png` |
| Mobile identity, facts and gallery access | `pi-evidence-1791167646996-7f43f2.png` |
| Mobile named brokerage and call link | `pi-evidence-1791167711637-3dc0b2.png` |
| Mobile direct gallery with titled/captioned imagery | `pi-evidence-1791167749549-52d8de.png` |

## Verified primary guidance

Retrieved 5 October 2026. Citations support general recommendations, not claims about this site's public presence.

- **S1:** Google [technical requirements](https://developers.google.com/search/docs/essentials/technical): public crawler access, successful HTTP response, indexable content.
- **S2:** Google [robots meta and X-Robots-Tag](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag): default permissions, crawl access needed to read directives, non-HTML header control.
- **S3:** Google [canonical URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls): optional signals, absolute/self canonical, consistency and noindex distinction.
- **S4:** Google [sitemap overview](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview): small linked sites versus new/low-link/media-rich discovery needs.
- **S5:** Google [title links](https://developers.google.com/search/docs/appearance/title-link): distinct descriptive titles; automated selection and device-dependent truncation.
- **S6:** Google [snippets](https://developers.google.com/search/docs/appearance/snippet): query-dependent page text/meta selection, useful unique descriptions.
- **S7:** Google [image SEO](https://developers.google.com/search/docs/appearance/google-images): real img src, supported WebP, captions/alt/context, responsive images, light filename signals and preferred-image metadata.
- **S8:** Google [lazy-loaded content](https://developers.google.com/search/docs/crawling-indexing/javascript/lazy-loading): native lazy loading, no bot interaction assumption, rendered-HTML inspection.
- **S9:** Google [structured-data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies): accurate, current, relevant, visible content and crawlable images.
- **S10:** Google [supported structured-data search gallery](https://developers.google.com/search/docs/appearance/structured-data/search-gallery): feature eligibility is separate from general schema validity.
- **S11:** Schema.org [RealEstateListing](https://schema.org/RealEstateListing) and [SingleFamilyResidence](https://schema.org/SingleFamilyResidence): page versus residence semantics, new-area status, full/partial bath and area properties.
- **S12:** Google [Business Profile eligibility](https://support.google.com/business/answer/13763036?hl=en): for-sale/rental properties excluded; sales/leasing offices distinguished.
- **S13:** [Open Graph protocol](https://ogp.me/): core title/type/image/URL metadata and image alt/dimensions.
- **S14:** Google web.dev [Web Vitals](https://web.dev/articles/vitals): field thresholds, p75 and lab/field distinction.
- **S15:** Google [VacationRental structured data](https://developers.google.com/search/docs/appearance/structured-data/vacation-rental): rental-specific feature and onboarding limits.

## Handoff

Assessment complete when report/scope checks pass and artifact is committed. Next implementation, if requested: resolve G1/G2 first; select a bounded metadata/canonical/share change; preserve all approved copy, captions and image provenance; verify locally and on separately authorized deployment. No implementation Bead, deployment or external submission is created implicitly by these recommendations.
