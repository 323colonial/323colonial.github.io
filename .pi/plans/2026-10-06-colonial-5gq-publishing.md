# Main-push publishing

Bead: colonial-5gq. Branch: main.

## Evidence and boundary

GitHub API reports Pages `build_type: legacy`, source `gh-pages:/`, deployed release `f28077320e024564d1d18fcca2d22c464b75ef33`. Remote main is `e3310e8f314b5f1c2d25d216e9bdd3afa97186fa`. No repository workflow exists; only GitHub's dynamic Pages workflow. The previous buyer-only release moved publishing away from main. Environment `github-pages` already permits main and gh-pages; Actions are enabled.

Outcome: every main push starts CI; successful checks publish only `scripts/publish-files.txt` to existing GitHub Pages URL. Use official Pages artifact/deploy actions, no branch-writing token or extra secret. Serialize deployments without cancelling an active release; GitHub may coalesce pending runs during rapid pushes. Failed checks leave previous site intact.

## Implementation and checks

1. Add failing Node tests for exact, byte-identical allowlist staging and rejection of unsafe/missing/symlink inputs and existing output directories.
2. Add minimal Node staging script; build into a fresh runner-temp directory, never repository root. Add SHA-pinned GitHub Actions workflow for unfiltered main pushes and main-only manual reruns, npm tests, artifact upload and Pages deployment with job-scoped permissions.
3. Document activation, artifact exclusion, run monitoring and rollback in docs/publishing.md; update current PRODUCT publishing contract.
4. Run `npm test`, Python regression commands, workflow lint, and an actual temporary artifact inventory/content comparison. Commit only task files.
5. Request bounded approval before production activation: switch Pages to Actions and push exact committed candidate to origin/main with remote-state checks. No force, branch deletion or gh-pages modification. Verify successful Actions deployment and live bytes; otherwise retain explicit blocker/limits in Bead.

No UI, content, analytics, hosting domain, runtime dependency or allowlist changes. Existing untracked `.beads.gate.lock` stays untouched.
