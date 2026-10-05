# Listing-only route pruning

Bead: colonial-yec. Scope: local implementation, no redesign, push or deployment.
Recovery: colonial-cec and colonial-yec plus `.pi/reviews/colonial-cec-font-evaluation.md`; no prior transcript recovered.

## Route inventory and decisions (before deletion)

| Route/file | Decision | Rationale |
| --- | --- | --- |
| `/`, `index.html` | Keep unchanged | Approved property narrative, all facts, gallery/details dialogs and brokerage contact. |
| `gallery.html` | Keep unchanged | Ordered 33-photo gallery and direct-link/no-JavaScript fallback. |
| `brochure.html` | Remove | Unlinked owner paint/purchase record and simulations, not current listing content. Finish specification remains in PRODUCT.md; full record recoverable in Git. |
| `sale-prep.html` | Remove | Unlinked historical owner budget/unfinished-work estimates with obsolete email CTA. Not buyer listing evidence. |
| `floorplans.html` | Remove | Unlinked superseded sketch-based main/upstairs plans and obsolete email CTA. Current buyer brief excludes these plans; conceptual basement image remains in buyer gallery with disclosure. Original drawings preserved. |
| `styles.css` | Remove | Only three removed root HTML pages load it. Buyer pages use listing.css. No runtime import in retained scripts/CSS. |
| `tests/table-contrast.html` | Remove | Exercises only removed owner tables, not buyer UI. |
| Other `tests/*.html` | Keep | Developer regression fixtures, not product routes; narrow media-layout route loop to buyer pages. |
| `.impeccable/**/*.html` | Keep | Historical design/tool artifacts, not buyer routes; no artifact cleanup authorized. |

No standalone legal pages, sitemap, robots.txt, redirect config or application router exists. Essential dated listing/footer and conceptual-plan disclosures stay unchanged. No redirects: neither listing nor gallery replaces owner budgets, paint purchases or old main/upstairs drawings. Local server should return 404 for removed routes; no claim about a deployed host.

## Boundary and recovery

Delete exactly `brochure.html`, `floorplans.html`, `sale-prep.html`, `styles.css`, `tests/table-contrast.html` from the tracked tree. Recovery source: `c74ac19d8bdbc179592fe369e98960a6e5790653`; `git show <SHA>:<path>` retrieves each original. No branches, untracked data or remote state deleted. Pre-existing `.beads.gate.lock` stays untouched.

Keep all images, assets, provenance manifests, asset generators and their regression checks. Historical names in immutable provenance and prior reports are records, not active links; do not rewrite history to conceal removal. Existing approved-listing fixture stays unchanged; explicitly assert absence for its four retired source files while checking all remaining hashes.

## Implementation and checks

1. Add failing exact root-route/retired-file checks; retire legacy page assertions while preserving asset provenance and durable finish-spec checks.
2. Remove five named files. Point design checks at actual listing.css components and buyer pages; narrow media-layout coverage. Update PRODUCT.md and DESIGN.md's live scope/verification statements only.
3. Run `node --test tests/*.test.mjs`, `python3 tests/test_listing.py`, `python3 test_design.py`, `python3 test_marketing_plans.py`, and `git diff --check`.
4. Run retained browser regression fixtures on local server; smoke desktop/mobile listing, details, gallery/viewer, showing disclosure and native fallback links. Verify removed routes return 404. No phone call or external inquiry submission.
5. Review task-owned diff, commit, record evidence in this artifact/Bead, direct-closeout then hand off.

Buyer HTML/CSS/JS and all image assets must remain byte-identical. No build step exists (static site; npm script runs tests).

## Verification results

- RED: `node --test tests/site-structure.test.mjs` failed with the three obsolete HTML files in the root inventory. GREEN: same command passed after deletion (4 tests).
- Shell matrix: Node 7/7; Python listing 11/11; design check PASS; marketing-plan pixel/hash checks PASS. `git diff --check` and cached diff check passed. Final staged-candidate gate is recorded in the Bead closeout.
- Byte-preservation check: `git diff HEAD --exit-code -- index.html gallery.html listing.css listing.js gallery.js assets images tests/fixtures/approved-listing.json` passed.
- All eight retained browser fixtures reported PASS, with no FAIL lines: hero-layout, media-layout, gallery-viewer, buyer-quality, narrative-scroll, listing-fallbacks, buyer-audit, property-details. Full initial output: `/Users/hays/.betterwright/artifacts/85b42e1702877c85/browser-output-1791165362060-c42b2f.json`.
- Existing local server `http://127.0.0.1:8883` served retained pages. Each of the five deleted paths returned HTTP 404. No sitemap/redirect entries or buyer links required removal; buyer local-link test passed.
- Desktop 1440×1000: hero, 12-fact details dialog, close-return focus, correct brokerage telephone/public listing hrefs, all-33 catalog and enlarged photo verified. Mobile 390×844 gallery: 33 photos, document width 390, Next advances to photo 2, showing panel accessible. Native Tab reached Previous, Shift+Tab returned Close, Escape closed viewer and restored original photo opener. No external contact action submitted.
- Browser evidence checklist `colonial-yec retained buyer flows` audited, all five requirements proven. Proofs under `/Users/hays/.betterwright/artifacts/85b42e1702877c85/`: home `pi-evidence-1791165157607-de92cd.png`; details `pi-evidence-1791165236259-abc6b7.png`; contact `pi-evidence-1791165253918-e65134.png`; catalog/viewer `pi-evidence-1791165293351-854416.png`; mobile `pi-evidence-1791165327763-59f5df.png`.
- Routed independent read-only review: openai-codex/gpt-6-astra, no findings; validated `.pi/reviews/colonial-yec-review.json`. Delegation: `runtime:delegated-results/76e4f7b4-6788-4fd0-95ae-3164974d4a6e/child-0.json`. Parent scope/docs review passed; afterward restored two existing durable finish-spec assertions and corrected historical-styling wording, focused Node check passed.
- Limits: static local verification only, no deployment certification or live inquiry. No retained production UI changed, so no visual redesign/detector pass was needed. Browser harness rejected two malformed batch requests before execution; native locators completed smoke checks after inspecting mismatched names. Read-only `agnt doctor --json` found no failures, only generic missing pytest/check-pi-config prerequisites not used by this project's documented matrix. No config changed; existing server and `.beads.gate.lock` left untouched.
