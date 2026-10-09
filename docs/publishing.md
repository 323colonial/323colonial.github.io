# Publishing

`.github/workflows/publish.yml` publishes the buyer website at https://323colonial.github.io/ from `main` using GitHub Actions.

Every push to `main` starts the workflow, without path filters. A manual **Run workflow** on `main` can retry a failed release. Other branches do not deploy. Successful `npm ci` and `npm test` are required before publication; a failed build leaves the previous site live.

The workflow stages only `scripts/publish-files.txt` into a new temporary directory using `scripts/build-pages.mjs`, then uploads and deploys that directory with official GitHub Pages actions. It never publishes the checkout or writes `gh-pages`. Source documents, provenance, tests, tooling, hidden files and credentials stay outside the artifact. This does not make Git history private.

Deployments are serialized without cancelling an active release. GitHub concurrency may replace a pending run with a newer push; under rapid pushes the newest successful revision wins, not necessarily every intermediate revision.

## One-time activation

Implementation alone does not change the live Pages settings. After approving production activation:

1. Set repository **Settings → Pages → Build and deployment → Source** to **GitHub Actions** (API `build_type: workflow`). Do not select repository-root branch publishing.
2. Ensure Actions are enabled and the `github-pages` environment permits `main`. No required reviewer should block automatic deployment if unattended main-push publishing is desired.
3. Push the workflow and staging code to `main`. Monitor **Actions → Publish website**, including its deployment URL.

No custom secrets or personal access token are needed. Build has read-only repository access; only the deployment job receives `pages: write` and `id-token: write`. Actions are pinned to commit SHAs. Existing domain and HTTPS settings are unchanged.

Before this change, Pages used `gh-pages:/` with GitHub's automatic branch builder. Manual allowlist releases updated `gh-pages`, but pushes to `main` could not publish. At investigation time the live release was `f28077320e024564d1d18fcca2d22c464b75ef33`; the environment already permitted `main` and `gh-pages`.

## Checks and recovery

From repository root, with Node 24:

```sh
npm ci
npm test
# OUTPUT must not exist; its parent directory must exist.
node scripts/build-pages.mjs /tmp/colonial-site-candidate
# Optional local workflow lint:
nix shell nixpkgs#actionlint --command actionlint .github/workflows/publish.yml
```

The Impeccable test uses `.pi/skills/impeccable/scripts/impeccable detect`, not the retired Node scripts. The upgrade bundles a macOS ARM64 engine; other platforms, including Linux CI, download the engine pinned in `scripts/VERSION` from GitHub Releases on first use and verify its SHA-256 sidecar. They need network access and a writable cache. Run `.pi/skills/impeccable/scripts/impeccable engine-probe` to provision/check it before tests, or supply a trusted preinstalled engine through `IMPECCABLE_BIN`. A failed download or checksum blocks tests and publication; it is not skipped.

The publishing test checks exact inventory and byte identity against the allowlist, stale-output rejection, traversal, duplicates, missing files, directories and symlinks. Existing SEO tests check the list against all buyer-page assets. Adding a public asset requires updating both the allowlist and its expected inventory test. Browser fixtures remain separate manual checks, not CI browser certification.

After deployment, verify the workflow SHA and live file bytes; spot-check excluded paths return 404. If CI fails, inspect the failing step, fix it and push to `main`, or rerun after resolving a transient failure. Do not bypass a failed check by uploading the checkout.

For content rollback, revert the bad change and push the revert through the same checks, subject to normal push/deployment approval. To roll back this CI migration, disable **Publish website** and restore Pages source to **Deploy from a branch → gh-pages → /** after approval. The untouched `gh-pages` branch preserves the pre-migration release; do not force-push or delete it.
