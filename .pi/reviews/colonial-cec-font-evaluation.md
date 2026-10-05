---
target: colonial-cec buyer font evaluation
total_score: 22
max_score: 28
na_heuristics: 5,7
untested_heuristics: 3,9
p0_count: 0
p1_count: 0
bead: colonial-cec
assessment_scope: buyer typography only
target_identity: "file:/Users/hays/Projects/323-colonial-website/index.html"
target_fingerprint: "sha256:e45d7ccdfa82559f97228acf0b08c4a65673f71625a58cb297c2ebd12ac7966b"
target_path: /Users/hays/Projects/323-colonial-website/index.html
timestamp: 2026-10-05T01-45-59Z
slug: index-html
---
Method: dual-agent (A: 0ac6ffd8-376a-441f-94bf-13f175eb781b · B: 107de78c-a9f9-478c-9991-dc6ce8c1fe02)

# Buyer font evaluation — colonial-cec

## Scope and verdict

Evaluated `index.html`, `gallery.html`, and shared buyer contact, details, catalog and photo-viewer typography in `listing.css`. User explicitly excluded unrelated pages planned for pruning; their findings do not contribute to this assessment. This is an evaluation, not authorization to change the UI or fonts.

Source revision: `fe31e67e324f171501389f662747ed31153c5861`. Recovery used `bd show colonial-93v`, `bd show colonial-cec` and referenced artifacts; no prior transcript or historical critique was recovered. Impeccable context ran once for `index.html`; critique and typeset guidance informed independent assessments. Assessments ran serially to avoid shared browser-state conflicts; A completed before detector findings entered synthesis.

**Keep Georgia + Arial.** Pairing fits the quiet, photo-led house presentation. Main opportunity: improve resilience and secondary-text readability, not replace fonts. `PRODUCT.md` Brand commitments pins both families; `DESIGN.md` Typography describes their roles. Familiarity is not itself a defect. A claim that Georgia feels old-fashioned would be taste, not observed evidence.

## Font inventory

Both buyer pages load `listing.css` (`index.html:5`, `gallery.html:8`). Georgia falls back to Times New Roman/serif; Arial falls back to sans-serif. Used weights are regular 400 and bold 700. No font downloads, `@font-face`, variable-font axes, light-weight requests or font preloads are needed by this implementation.

| Role | Current styling | Source |
| --- | --- | --- |
| Address | Georgia 24–34px; mobile 25px, smallest 22px; 1.15 leading | `listing.css:44,147,188` |
| Narrative | Georgia 18–23px, mobile 18px; 1.65 leading | `listing.css:85–86,164` |
| Section headings | Georgia 28–36px; 1.15 leading | `listing.css:37–38` |
| Price | Arial bold 30px, mobile 25px; 1.2 leading | `listing.css:64,154` |
| Fact values / labels | Arial 20px / 15px; compact values 18px; mobile 16px / 12px; 1.45 leading | `listing.css:69–72,138,156–158` |
| Captions / concept note | Arial 13px / 12px; viewer caption 14px; 1.5 leading | `listing.css:60–62,124` |
| Details labels / values | Arial 12px / 16px; 1.5 leading | `listing.css:106–107` |
| Controls | Arial bold 14px; selected mobile controls 12px; 1.5 leading | `listing.css:29,160,184` |
| Homepage showing disclosure | Arial regular 13px at all widths; 1.6 leading | `listing.css:50` |
| Gallery showing disclosure | Arial bold 14px desktop, 12px mobile | `listing.css:29,49,150` |
| Contact panel / dialog title | Arial 14px / bold 16px; 1.6 / 1.4 leading | `listing.css:52,121` |
| Status, dates, counters, footer | Arial 12px; leading 1.5–1.65 by role | `listing.css:68,75,101,108` |
| Location / public listing | Arial 13px; location 12px mobile | `listing.css:46–47,148` |
| Supplemental laundry link | Arial regular 14px; 1.6 leading | `listing.css:88` |
| Viewer full-size link / error | Arial 14px, full-size link 12px mobile; 1.4 / 1.5 leading | `listing.css:125,129,184` |

Address tracking is −.025em; section headings −.02em; prose normal. Price resets tracking to normal. Price and counters request tabular numerals (`listing.css:64–65,102`). Scale is role-driven, not a mathematical modular scale. Adjacent 12/13/14px support roles rely on placement and weight, not size alone. No new abstraction is needed to evaluate or refine them.

The homepage's quiet 13px showing disclosure versus gallery's bolder control is intentional under colonial-93v. Do not normalize it as an accidental inconsistency. Section spacing, not paragraph indentation, separates the seven approved narrative passages; adding headings or rewriting them would violate scope.

## What works

- **Readable primary prose:** at 1440×1000, narrative renders Georgia 21.312/35.165px in 583.2px columns. Across seven paragraphs, non-final lines measured 51–63 characters. At 390×844, first paragraph renders 18/29.7px in 350px, 14 lines of 31–46 characters. Shorter mobile measure is preferable to reducing readable type to force the rubric's desktop 45–75-character target.
- **Clear hierarchy and fit:** Georgia carries address and sustained narrative; Arial separates factual comparison and actions. Bold price stands apart without bolding the prose. The photograph-led composition and house-color fields supply specificity; novelty fonts would not improve the evidence. Heading-free narrative is approved, not missing hierarchy to repair.
- **Low font-delivery risk:** source has no external font imports; homepage exposed zero FontFace entries and zero matching font-resource requests. There is no webfont blocking/swap stage. `listing.js:91` waits for `document.fonts.ready` before remeasuring; header/facts ResizeObserver and resize handling support fit. Installed font identity and fallback metrics remain unverified. No downloaded fonts does not mean zero whole-page layout shift.
- **Contrast:** sampled source-color ratios were narrative 5.23:1–11.98:1, masthead 5.29:1 and muted metadata on paper 6.39:1. These exceed 4.5:1 for sampled ordinary-text pairs; they are not a full accessibility certification.

## Priority findings

### 1. P2 — enlarged text can push showing control offscreen

**Observed stress result:** at 320×480, a temporary DOM-only doubling of computed font sizes produced 419px document width. Disclosure right edge reached 355.92px; screenshot shows clipped “See in person.” Sticky header grew to 283.78px. Contact panel subsequently settled within the viewport and remained vertically scrollable.

**Boundary:** flex masthead plus non-wrapping disclosure (`listing.css:42,49`). This is a synthetic enlargement probe, not actual browser zoom and not a demonstrated WCAG failure.

**Why it matters:** text enlargement intended to improve reading can reduce access to showing information and consume most of a short screen.

**Recommendation:** first reproduce using actual browser text-only enlargement/default-font settings. Then, if confirmed, permit header reflow at insufficient available width rather than shrinking fonts or clipping controls. Preserve contact access and measured sticky offsets. Suggested command: `/impeccable adapt`.

### 2. P2 — important secondary facts receive small type

**Observed sizing, inferred reading cost:** status, expected date, “above grade,” details labels and the conceptual-plan disclosure are 12px. Mobile facts compress qualifier and value into one line (`listing.css:62,68–75,106,156–161`). Ordinary captions are 13px. Normal screenshots remain readable; user difficulty was not measured.

**Why it matters:** these qualifiers affect interpretation of the property, not merely decoration. Low-vision and distracted readers may need extra effort or enlargement. Small text alone is not a WCAG violation.

**Recommendation:** trial 13–14px for important qualifiers and disclosures before enlarging every metadata role. Evaluate wrapping and sticky facts/header height together; keep counters/footer subordinate. Retain Georgia/Arial, approved facts, concept distinction and exact copy. Suggested command: `/impeccable typeset`.

## Minor observations

- **P3 — gallery introduction measure:** `.gallery-intro p` occupies 760px at desktop, Georgia 18/29.7px; first line measured 95 characters, second 60 (`gallery.html:20`, `listing.css:110`). Optional paragraph-only width reduction toward roughly 60–70ch, checked by rendered character counts. This is only two lines, so low priority; no copy rewrite needed.
- Font declarations use pixels. They do not establish support for browser default-font preferences. Check preferences separately rather than treating responsive viewport resizing as proof of text scaling.
- Address/headline tightening is modest and visually coherent in sampled sizes; no evidence supports altering tracking or adding an actual light weight. Two families have distinct jobs; neither should be removed merely to reduce the family count.

## Browser verification

| Check | Result |
| --- | --- |
| Homepage at 1440×1000 and 390×844 | No document horizontal overflow; hierarchy and narrative reading inspected |
| Homepage at 1280×800 | Address 32px; narrative 18.944/31.258px, width 511.2px; captions 13/19.5px |
| Homepage at 320×480 | Narrative 18/29.7px; page width 320px; facts static; zero sticky narrative sequences |
| Contact at 320×480 | Arial 14/22.4px; panel x16–304, y87–369; call/public-listing text fits |
| Details at 320×480 | Title 16px, labels 12px, values 16px; 12 facts; client/scroll widths 276/276, heights 446/762; vertical scrolling |
| Photo viewer at 320×480 | Title 16px, caption/buttons 14px, full-size link 12px; widths 276/276; controls visible |
| Gallery at 320×480 | Introduction 18/29.7px, heading 28px, captions 13px; page width 320px |
| Text spacing | Temporary 1.5 line-height, .12em letter-spacing, .16em word-spacing and 2em paragraph spacing; sampled viewer/details/contact had no measured horizontal overflow; vertical scrolling increased |
| Synthetic doubled text | Header overflow, as documented in priority finding 1; not actual browser zoom |

Viewport metadata does not prohibit zoom (`index.html:2`, `gallery.html:5`). Focus styling exists (`listing.css:26–28`) but this evaluation did not freshly audit the full keyboard flow. Standard 400/700 weights avoid requests for unavailable light variants; actual installed faces, fallback-font substitution, missing font environments, localization expansion, OS text scaling, actual zoom, screen readers and whole-page CLS remain unverified. Browsers were resized desktop sessions, not physical phones. Contrast calculations and sampled spacing probes do not establish full WCAG conformance.

Reduced-motion fallback is source-backed (`listing.js`); short-height fallback was observed. No translation or replacement copy was introduced to stress frozen listing text.

## Typography-scoped critique summary

| # | Heuristic | Score | Evidence / limit |
| --- | --- | --- | --- |
| 1 | Visibility of status | 3/4 | Status/date visible, but 12px |
| 2 | Match with real world | 4/4 | Familiar address, price and units; clear reading order |
| 3 | User control and freedom | Untested | Actual zoom and full keyboard exit flow not assessed |
| 4 | Consistency and standards | 3/4 | Shared family roles; intentional header-control difference |
| 5 | Error prevention | n/a | Input/error-prevention flows outside typography scope |
| 6 | Recognition rather than recall | 3/4 | Facts paired with labels; small qualifiers |
| 7 | Flexibility and efficiency | n/a | Marketing typography; accelerators outside scope |
| 8 | Aesthetic/minimalist design | 3/4 | Restrained hierarchy; gallery measure excess |
| 9 | Error recovery | Untested | Error typography in source; error state not triggered |
| 10 | Help and documentation | 3/4 | Gallery instructions readable; long desktop line |
| | **Scored subset** | **22/28 — Good** | Untested/n/a excluded; not whole-site usability score |

**Cognitive load:** sampled typography supports one reading path, four grouped quick facts, visible labeled actions, and progressive disclosure. No typography-driven choice overload observed. No claim that all 33 photo choices must be reduced to four; visual catalog selection is a different task. Whole-homepage information architecture remains separate work.

**Emotional journey:** serif narrative and photography support a calm first impression; compact sans-serif facts provide reassurance. Small qualifiers and enlarged-header overflow are the typographic weak points. No broader emotional-journey redesign is proposed.

**Personas:** Jordan, first-time buyer, gets clear address → facts → narrative progression. Sam, low-vision reader, benefits from generous prose and sampled contrast but faces small qualifiers and enlargement risk. Casey, distracted mobile buyer, can scan numbers quickly while “sq ft above grade” takes closer attention. These are design implications, not user-study results.

## Mechanical scan reconciliation

Assessment B ran the bundled type detector once, exit 2. Command initially included legacy pages before the user narrowed scope. Retained buyer portion contains two `overused-font` warnings: one each for `index.html` and `gallery.html`, line 0, snippet `Primary font: arial`. Source role locations are given above. Rejected as replacement advice: Arial is explicitly pinned and has a distinct informational role. No unexplained buyer typography warning was retained.

Capture truncates during excluded legacy results; no exact overall count is claimed. Those findings and scores are excluded. No scan rerun was needed to recover the complete buyer records at the beginning of captured output. This detector did not identify the manually observed enlargement/measure issues; automated thresholds are not proof of reading quality.

Buyer browser overlays also flagged `cream-palette` and `theater-slop-phrase`. Pinned palette and literal approved “home theater” copy make these contextual false positives, not typography defects. Mutable-injection preflight succeeded; temporary overlays were inspected, then cleared by navigation. Overlay server on 8400 was stopped. Existing static server on 8883 was not started by this task and was left running. No persistent human-visible overlay is claimed.

Raw capture, local only: `/var/folders/rh/k2_zcjrj1vg6z_j_sr25qs580000gn/T/pi-bash-1619a4885574bd61.log`. Buyer warnings appear at the start; do not use excluded legacy totals for this assessment.

## Evidence index

Fresh screenshots, source revision above. Base directory: `/Users/hays/.betterwright/artifacts/85b42e1702877c85/`. Absolute local artifact paths are not deployed site URLs. Both agents audited their browser evidence checklists; parent independently inspected desktop/mobile narrative, gallery desktop, details, viewer and enlargement images.

| Surface | Screenshot filename |
| --- | --- |
| Desktop narrative/facts, 1440×1000 | `proof-1791163977839-fbb26e.png` |
| Mobile narrative/facts, 390×844 | `proof-1791163993616-69544d.png` |
| Gallery desktop | `pi-observation-1791164032728-67cd27.png` |
| Gallery mobile | `pi-observation-1791164025786-bff266.png` |
| Desktop, 1280×800 | `pi-evidence-1791164238805-42a14f.png` |
| Buyer detector overlay | `pi-evidence-1791164266966-00227f.png` |
| Contact, 320×480 | `pi-evidence-1791164280578-96d463.png` |
| Details, 320×480 | `pi-evidence-1791164293862-a77af7.png` |
| Viewer, 320×480 | `pi-evidence-1791164309106-47a77c.png` |
| Synthetic enlarged-text overflow | `pi-evidence-1791164353037-70fda8.png` |

Delegated result references: `runtime:delegated-results/0ac6ffd8-376a-441f-94bf-13f175eb781b/child-0.json` and `runtime:delegated-results/107de78c-a9f9-478c-9991-dc6ce8c1fe02/child-0.json`. Raw B result includes subsequently excluded legacy observations; this buyer-only synthesis supersedes their relevance.

## Follow-up boundary

Recommended, not implemented or newly authorized:

1. Reproduce actual text-enlargement behavior; minimally allow header reflow if confirmed. Verify 320/390px widths, short viewports, 200% text enlargement, browser zoom, disclosure bounds and contact access.
2. Trial 13–14px for essential qualifiers/disclosures with facts wrapping and sticky-height checks; preserve lower-value metadata hierarchy.
3. Optionally shorten only gallery introduction measure. Preserve wording.

Keep fonts, weights, prose size/leading, photography, exact approved copy, palette and no-download strategy. Do not add fonts, dependencies, a token abstraction or unrelated-page cleanup. Any future change should retain existing buyer regression tests, include a focused reproduction for the changed behavior, and end with a bounded `/impeccable polish` check. This evaluation makes no release/deployment claim.

Historical critique trend intentionally not recovered under the user's context boundary. No UI changes made.

Questions skipped: two priority findings; evaluation only, no implementation requested.
