# Buyer website hardening — colonial-0bc

5 October 2026. Baseline `5febb9b` (closed colonial-ko5). Recovery used only `bd show colonial-ko5`, `bd show colonial-0bc` and their referenced artifacts/current source. No previous transcript. Impeccable context setup ran once; harden and craft-floor references followed. Prior `2026-10-05-colonial-hdy-audit.md` confirms its print findings were already repaired; no duplicate print work.

## Demonstrated defects and scoped repair

1. **Long tokens overflow both routes.** At 1440, 390 and 320px, 100+ character tokens in captions, narrative and contact text increased document/element scroll width. Shared `body { overflow-wrap: anywhere }` allows emergency wrapping without truncation or hiding content.
2. **200% text clips controls.** Doubling computed text sizes at 390/320px overflowed contact summaries and dialogs; the homepage date also forced its grid column wider. Remove summary/date `nowrap`, let the identity shrink, and wrap dialog bars/control rows. No font-size reductions. [Before](colonial-0bc-evidence/text-before.png), [after](colonial-0bc-evidence/text-200-percent.png) are actual captures, different routes sharing the same header rules. Contact content remains scrollable inside its viewport-bounded panel.
3. **Slow navigation mismatches photograph and caption.** A local image response delayed three seconds left the exterior pixels visible below the newly selected great-room caption. DOM confirmed `currentSrc` still selected photo 1 while `src` requested photo 2, with no loading status. Shared `showPhoto` now announces “Loading photo…” through the existing `role=status` element and hides old image pixels until `load`. Real errors retain the existing full-size recovery text, navigation and Close. [Before](colonial-0bc-evidence/slow-before.png), [after](colonial-0bc-evidence/slow-after.png). The delayed request subsequently decoded and restored the correct visible photo.

Production diff: `listing.css` and `gallery.js` only. No HTML, listing fact, caption, asset, palette, native scrolling, dependency, API, hosting or persistent-state changes. `DESIGN.md` records the behavior; `PRODUCT.md` names the new fixture. No push/deployment.

## Regression and coverage

`tests/buyer-harden.html` uses the existing dependency-free iframe fixture pattern. **RED: 20 expected failures / 44 passes. GREEN: 64/64.** It tests both routes at 1440×1000, 390×844, 320×640 and 720×500; long Unicode tokens, expanded RTL text, empty/single-character text, 200% per-element text sizes at mobile widths, contact/dialog overflow, real unique HTTP 404 image requests, pending visibility/status, recovery URL, ten rapid Next actions, final image/caption position, and Close focus restoration. No synthetic error event substitutes for the real 404 check. Fixture mutations never change shipped copy.

| Dimension | Assessment |
| --- | --- |
| Desktop/mobile | Inspected both actual routes at 1440×1000 and 390×1000. Composition, uncropped imagery and contact access preserved. Dates may wrap naturally. |
| Enlargement | 200% text-only enlargement at 390/320; 720×500 reflow proxy for 1440×1000 at 200% page zoom. Native browser zoom itself remains unverified. |
| Long/empty text | Long tokens repaired; empty, single-character, accented Latin, CJK, emoji and expanded Arabic text fit. This is stress testing, not authorization to edit approved listing copy. |
| RTL/i18n | RTL text islands tested. Product remains an English US property listing, not a localized app. Full RTL chrome, locale switching, currency/date conversion and translated copy are not applicable; no localization machinery added. |
| Missing/slow/offline | Actual 3-second delayed image and real 404 tested. Browser context offline mode caused a fresh image request to fail visibly; loaded page retained contact details and working disclosure after Escape. [Offline capture](colonial-0bc-evidence/offline.png). Reconnect is necessary before a network recovery link can succeed. Offline mode was restored afterward. Cold offline navigation is not supported; no cache/service worker/storage was added. |
| Loading/concurrency | Existing status reused. Old pixels cannot accompany new captions while pending. Rapid navigation settles on last selected photo; no unnecessary disabling of navigation or custom request manager. |
| Keyboard/focus | Both routes: native Enter opens; Tab reaches Previous; Shift+Tab returns Close; ArrowLeft wraps to 33; Escape restores photo opener. Homepage second Escape dismisses catalog. Contact Enter/Escape closes and restores summary. |
| Screen-reader resilience | Existing named native dialogs, semantic captions, image alt text, position live region and status semantics retained. Loading is exposed through `role=status`. Actual VoiceOver/NVDA announcements unverified. |
| High contrast | Chromium forced-colors emulation inspected: focused Close outline, labeled navigation and full-size link visible. Dots are decorative; accessible position remains text. [Capture](colonial-0bc-evidence/forced-colors.png). Not a Windows hardware/assistive-technology certification. |
| Fallbacks | Existing no-script, reduced-motion, unsupported-dialog and failed-initialization browser fixtures remain final gates. No polyfill or new fallback framework needed. |
| Input/forms | No user-data entry or network-submit forms. Only native `method=dialog` close forms; validation, injection sanitization, duplicate submission, permissions, auth, rate limits and API 4xx/5xx UI are not applicable. |
| Empty/large datasets | Fixed authored 33-photo catalog. No fetched datasets, search, pagination, zero-result flow or 1,000-item use case. Empty text tested; speculative empty-catalog architecture skipped. |
| Performance | Existing responsive images, lazy loading, nearby preload, system fonts and passive/rAF scrolling preserved. No new request, timer, listener lifecycle, dependency or benchmark claim. Cold-network/low-end CPU performance remains unprofiled. |

## Verification record and final gate

Focused regression and shell checks before final staging:

- `tests/buyer-harden.html`: 64 PASS, zero failures.
- `node --test tests/*.test.mjs`: 12/12 PASS.
- `python3 tests/test_listing.py`: 11/11 PASS, including frozen copy/assets.
- `python3 test_design.py` and `python3 test_marketing_plans.py`: PASS.
- Manual detector on changed CSS/JS/fixture: only existing owner-pinned Arial warning (exit 2); not a defect.
- Independent read-only routed `openai-codex/gpt-6-astra` review: no findings. `.pi/reviews/colonial-0bc/review.json` validates with `agnt review validate`.

After staging, rerun the shell commands and all eleven browser fixtures: hero-layout, media-layout, buyer-quality, listing-fallbacks, buyer-audit, property-details, buyer-typography, gallery-viewer, narrative-scroll, buyer-harden and print-layout. Print fixture requires print-media emulation after Ready. Final gate results, candidate commit and closeout are recorded in **Bead colonial-0bc**; this report does not substitute earlier focused results for the final gate.

Bounded Impeccable inspection/fix/confirmation completed; no open-ended polish loop. Optional next polish is a separately scoped native Safari/Firefox/real-zoom/screen-reader pass, not a redesign. No additional demonstrated defect deferred. Local task verification does not establish publication readiness, live hosting behavior, fresh PDF pagination or physical print certification.

## Tooling and provenance

An occupied latency-test port initially served an unrelated existing local server. Its ordinary missing response was not used as slow-response evidence. Restarted only the new helper on an OS-assigned loopback port; did not stop unrelated servers. Temporary helper `/tmp/colonial-0bc-server.py` subclasses Python's SimpleHTTPRequestHandler, delays `/__harden__/slow.webp` by three seconds, then serves existing photo 2. No browser sleeps or response interception.

Two rejected subagent calls mixed route-derived and explicit mode/access fields and did not launch workers. Ran read-only `agnt doctor --json`: zero failures, generic unrelated missing pytest/check-pi-config prerequisites warning. Route-only review then succeeded. No environment, shell startup or home-managed config changed. Existing unrelated `.beads.gate.lock` remains untouched.

Six committed PNGs are unaltered captures. Normal desktop/mobile captures remain private under BetterWright artifact root `85b42e1702877c85`, basenames `proof-1791178688957-da2cd5.png`, `proof-1791178689017-ff273d.png`, `proof-1791178689190-91c953.png`, `proof-1791178689244-316fcb.png`; they may expire. Durable source, runnable fixture and defect/fix captures remain the handoff record.
