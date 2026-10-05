# Buyer-site SEO implementation

**Bead:** colonial-2ua
**Date:** 2026-10-05
**Branch / baseline:** main / 3acb3feb5fd5c1dd320c4daac367ef142476b55b
**Scope:** local implementation, not publication.

## Decisions and gates

Owner confirmed https://323colonial.github.io/ on GitHub Pages in this session. Use `/` for homepage and `/gallery.html` for independent gallery. On 2026-10-05 owner reconfirmed listing facts (including $499,000, Coming Soon, expected October 8), descriptions, square footage/acreage and permission to publish all photos; owner maintains listing facts. This is owner confirmation, not fresh independent MLS/brokerage verification. Retain dated October 3 footer and all frozen prose/captions. Do not add disputed internet speed to metadata.

Outcome: consistent canonical/search/share identity. Boundaries: two HTML heads, their home links, and a reviewed future-publication file list. Smallest change: static tags, existing real exterior image, no runtime code/dependencies. Keep price-bearing homepage title because a maintainer is now named. Gallery metadata describes 33 views including one conceptual basement plan. No visible prose changes.

`scripts/publish-files.txt` will enumerate exactly 71 buyer files: index.html, gallery.html, listing.css, gallery.js, listing.js and full/small WebPs for positions 01–33. No directory globs, source images, historical assets, manifest, owner records, tests, scripts, docs, .git, .beads, .pi or .impeccable in public output. This list is not a deployed privacy control. Any future build must stage ONLY these paths in a clean output directory, not publish the repository root.

No hosting settings or workflow changes. GitHub Pages target repository/source configuration and final publish revision remain unverified/unapproved for release. Do not invent `_redirects`, JavaScript redirects or a meta refresh. Canonicalize `/index.html` to `/` via head tags; actual host-supported redirect behavior must be checked separately. Retired routes need genuine 404/410, not homepage catch-all.

P3: defer sitemap (two linked pages; unnecessary for this bounded change), structured data (not needed for indexability; adds maintenance), Twitter cards (no target-channel need). No new robots directive required. No ranking or rich-result promises.

## Implementation and checks

1. Add focused Node tests using installed htmlparser2/css-select for single absolute canonicals, exact approved metadata/share-image facts, home-link consistency, complete allowlist and preserved body. Observe RED before HTML changes.
2. Add static tags and root home links. Add explicit allowlist; adapt Python local-link resolver for root URL semantics, retaining all existing checks.
3. Run `node --test tests/*.test.mjs`, `python3 tests/test_listing.py`, `python3 test_design.py`, `python3 test_marketing_plans.py`, `git diff --check`. Confirm exterior WebP dimensions/type against actual bytes and existing manifest.
4. Run existing nine browser fixtures, mobile/desktop visual and native keyboard checks. Record one cold mobile local load (fresh origin) and scroll/dialog observations; not field Core Web Vitals or production-network performance. No speculative optimization.
5. Review task diff, commit task-owned changes, preserve results and deferred publication gates in Bead. Leave unrelated .beads.gate.lock and existing port-8883 server alone.

## Public verification boundary

NOT VERIFIED without separate authorization: live page/image responses, redirects/TLS/canonical matrix, crawler headers/access, forbidden-file exclusion, retired-route responses, deployed revision, public mobile network behavior and actual social previews. Owner must approve exact publish candidate and buyer-only artifact before any deployment. No push, deploy, account connection, validator/URL submission or sharing.
