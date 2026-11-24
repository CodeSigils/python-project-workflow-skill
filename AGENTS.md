# Repository agent guidance

`skills/python-project-workflow/` is the only runtime payload. Keep agent- and
maintainer-specific procedures in this repository infrastructure, not in the
shipped skill, unless they are portable across supported clients.

## Read first

Before changing this repository, read this file, then the root `README.md`,
`CONTRIBUTING.md`, and `SECURITY.md`. Read the relevant workflow, script, or
canonical file under `references/` before editing it; do not rely on a past
session summary when the repository or GitHub settings can provide the fact.

## Decisions and evidence

Before researching a setup, pinning, policy, or other durable maintainer concern, consult `docs/decisions.md`, then search `docs/evidence-urls.json` by `domain_tag`, then read `docs/research/index.md`. Reuse a current, applicable finding; otherwise research official guidance first, append a dated finding, then record the resulting durable decision. `scripts/validate.py` enforces record completeness/registration/linkage. Keep this workflow in docs/decisions+research; do not duplicate it in runtime skill files.

## Verification and CI policy

The authoritative local verification command list is in [README.md `## For Maintainers / Contributors` → `### Verify`](README.md#verify). Hooks, CI workflows, and `scripts/stage_manifest.py` enforce automated gates; do not maintain divergent command copies in docs. When a command or gate changes, update the owning implementation and the README Verify section in the same change.

When a change materially affects `SKILL.md`, reference routing, eval cases/fixtures/prompts/graders, or runtime/evidence claims, run a docs-drift and evidence-boundary review before closeout: update `README.md`, `docs/portability-contract.md`, `docs/behavior-evaluation-effort.md`, and any affected diagrams/authoritative-detail links for stale accuracy; do not preserve stale `workflow_verified`/baseline claims after a contract change without new recorded evidence. If validators encode doc/evidence boundaries, update them in the same change.

GitHub repository settings are the operational source of truth for branch protection, required checks, collaborator access, and security features. Before changing CI, hooks, release automation, or their documentation, inspect live settings and keep documentation aligned. For sensitive-evidence handling, follow the runtime canonical procedure in `references/security-and-gitignore.md` (mirrored in the shipped payload) and the repository trust boundary in `SECURITY.md`; do not restate secret-handling rules in multiple maintainer docs.

A previous audit found documentation claiming stale-review dismissal was enabled
when the live protection rule had it disabled. Do not copy policy values from
older docs or session summaries. For the current solo-maintainer model, zero
required approvals is intentional; if review requirements are introduced, set
the matching live protection options and document them in the same change.

Use SSH for maintainer Git transport when it is configured. Do not add an SSH
private key to Actions for this public repository. GitHub Actions uses its
ephemeral `github.token` only where GitHub API access is required, with the
smallest job-level permissions; never add a personal access token to CI.

## Post-delivery hygiene

After an authorized merge or confirmed remote PR acceptance, reconcile local VCS
state safely using primary Git/GitHub behavior: refresh remote-tracking state
(`git fetch --prune`), identify the actual default branch and configured
upstream (do not assume names), fast-forward the local default branch only when
the working tree is clean and the update is unambiguous, and remove the local
topic branch only when it is confirmed merged or its tip is an ancestor of the
updated default branch. If local state prevents a safe sync, preserve it and
report the blocker instead of guessing. Host automatic branch deletion does not
reconcile local clones.
