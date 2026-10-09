# Publishing

`.github/workflows/publish.yml` publishes the buyer website at https://323colonial.github.io/ from `main` using GitHub Actions.

Every push to `main` and every pull request starts validation, without path filters. A manual **Run workflow** on `main` can retry a failed release. Only non-PR runs on `main` stage and deploy. Successful `npm ci`, Chromium provisioning and `npm run test:buyer` are required before publication; a failed check leaves the previous site live.

The workflow stages only `scripts/publish-files.txt` into a new temporary directory using `scripts/build-pages.mjs`, then uploads and deploys that directory with official GitHub Pages actions. It never publishes the checkout or writes `gh-pages`. Source documents, provenance, tests, tooling, hidden files and credentials stay outside the artifact. This does not make Git history private.

Deployments are serialized without cancelling an active release. Pull requests have separate concurrency groups, so they cannot replace pending main releases. GitHub concurrency may replace a pending main run with a newer push; under rapid pushes the newest successful revision wins, not necessarily every intermediate revision.

## One-time activation

Implementation alone does not change the live Pages settings. After approving production activation:

1. Set repository **Settings → Pages → Build and deployment → Source** to **GitHub Actions** (API `build_type: workflow`). Do not select repository-root branch publishing.
2. Ensure Actions are enabled and the `github-pages` environment permits `main`. No required reviewer should block automatic deployment if unattended main-push publishing is desired.
3. Push the workflow and staging code to `main`. Monitor **Actions → Publish website**, including its deployment URL.

No custom secrets or personal access token are needed. Build has read-only repository access; only the deployment job receives `pages: write` and `id-token: write`. Actions are pinned to commit SHAs. Existing domain and HTTPS settings are unchanged.

Before this change, Pages used `gh-pages:/` with GitHub's automatic branch builder. Manual allowlist releases updated `gh-pages`, but pushes to `main` could not publish. At investigation time the live release was `f28077320e024564d1d18fcca2d22c464b75ef33`; the environment already permitted `main` and `gh-pages`.

## Checks and recovery

From repository root, with Node 24 and Python 3:

```sh
npm ci
npx playwright install chromium
npm run test:buyer
# Separate full Node tooling suite, including walkthrough and design detector:
npm run test:tooling
# OUTPUT must not exist; its parent directory must exist.
node scripts/build-pages.mjs /tmp/colonial-site-candidate
# Optional local workflow lint:
nix shell nixpkgs#actionlint --command actionlint .github/workflows/publish.yml
```

`npm test` aliases the buyer suite. Its explicit Node list covers content/SEO, analytics privacy, seasonal scheduling/recovery/assets and publication isolation; Python runs `tests/test_listing.py`, `test_design.py` and `tests/test_build_listing.py` (including the offline photo generator's read-only drift check). `npm run test:browser` runs the existing rendering, gallery, resize-reading and seasonal fixtures in Chromium. Each fixture must finish with a PASS title, passing results and no uncaught page errors; missing completion fails after 170 seconds, with a 180-second per-test ceiling and no retries. Results print to the log and attach under ignored `test-results/`. The workflow has a 15-minute build ceiling.

Playwright is a development-only dependency pinned to `1.64.0` in the lockfile; it pins the Chromium revision. CI provisions only Chromium using `npx playwright install --with-deps chromium`. Provisioning requires network access; failures block release. Fixtures then run serially on a runner-owned `http://127.0.0.1:18765` server with fresh browser contexts, blocked service workers and all nonlocal requests aborted, including analytics. An occupied port fails rather than reusing an unknown server. Neither browser dependencies nor fixtures enter the publication allowlist. This is Chromium regression coverage, not Firefox/WebKit, physical-device, production/CDN, field-performance or print-pagination certification; other browser fixtures remain manual.

In the Nix development shell, `node_modules` links are managed by Nix. Update dependencies with `npm install --package-lock-only --ignore-scripts`, then re-enter `nix develop`; do not run ordinary install/ci over those links. Install Chromium inside that shell separately. `npm ci` above is for ordinary checkouts and CI.

The separate `test:tooling` suite explicitly runs `.pi/skills/impeccable/scripts/impeccable engine-probe` before the full Node glob. This includes unpublished walkthrough checks and the Impeccable detector; neither blocks buyer release. The detector uses `.pi/skills/impeccable/scripts/impeccable detect`, not retired Node scripts. macOS ARM64 has a bundled engine; other platforms download the version pinned in `.pi/skills/impeccable/scripts/VERSION` from GitHub Releases and verify its SHA-256 sidecar. They need network access and a writable cache, or a trusted preinstalled engine through `IMPECCABLE_BIN`. Failed provisioning/checks fail the tooling suite; nothing is silently skipped. Authoring Python/Blender pipelines remain separate from these Node suites; see [private authoring checks](authoring-tools.md).

The publishing test checks exact inventory and byte identity against the allowlist, stale-output rejection, traversal, duplicates, missing files, directories and symlinks. Existing SEO tests check the list against all buyer-page assets. Adding a public asset requires updating both the allowlist and its expected inventory test. The four selected browser fixtures are required in CI; broader manual checks remain as described above.

### Replacing seasonal frames

`node scripts/build-seasons-small.mjs --check` is a read-only structural gate: inventory, timing-table membership and tier dimensions. Matching dimensions do **not** prove fresh pixels. No stale shipped pair was established by this review.

For an approved large-frame replacement, run `node scripts/build-seasons-small.mjs` before structural validation. Default builds now regenerate every small frame from its current large source using the existing ImageMagick recipe; `--force` remains accepted but is unnecessary. This deliberately trades incremental build speed for freshness without adding a fingerprint file. Review/commit each changed large+small pair together; originals, captions and manifests are not regenerated. ImageMagick is required for authoring, not for the read-only buyer gate.

For the reviewed warmth-export workflow, keep using `scripts/seasons/export_wb.py`: preparation makes paired large/small candidates and hashes both in its private report; `--apply` installs the approved prepared pairs and verifies installed hashes; `--check` verifies the prepared/installed batch. Do not replace only one tier or bypass its frozen-input/recipe checks. No new asset pipeline or public provenance format is introduced.

After deployment, verify the workflow SHA and live file bytes; spot-check excluded paths return 404. If CI fails, inspect the failing step, fix it and push to `main`, or rerun after resolving a transient failure. Do not bypass a failed check by uploading the checkout.

For content rollback, revert the bad change and push the revert through the same checks, subject to normal push/deployment approval. To roll back this CI migration, disable **Publish website** and restore Pages source to **Deploy from a branch → gh-pages → /** after approval. The untouched `gh-pages` branch preserves the pre-migration release; do not force-push or delete it.
