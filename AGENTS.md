# Repository agent guidance

`skills/python-project-workflow/` is the only runtime payload. Keep agent- and
maintainer-specific procedures in this repository infrastructure, not in the
shipped skill, unless they are portable across supported clients.

## Read first

Before changing this repository, read this file, then the root `README.md`,
`CONTRIBUTING.md`, and `SECURITY.md`. Read the relevant workflow, script, or
canonical file under `references/` before editing it; do not rely on a past
session summary when the repository or GitHub settings can provide the fact.

## Decisions

Before researching a setup, pinning, policy, or other durable maintainer
concern, consult `docs/decisions.md`, then search `docs/evidence-urls.json` by
`domain_tag`, then read `docs/research/index.md`. Reuse a current, applicable
finding; otherwise research official guidance first, append a dated finding,
then record the resulting durable decision. Each decision has a stable `D#` ID,
links to registered sources and a recheck trigger, and is enabled by an `R-###`
finding. `scripts/validate.py` rejects incomplete, unregistered, duplicated, or
unlinked records.

## CI and Git policy

GitHub repository settings are the operational source of truth for branch
protection, required checks, collaborator access, and security features. Before
changing CI, hooks, release automation, or their documentation, inspect the
live settings and keep the documentation aligned with them.

A previous audit found documentation claiming stale-review dismissal was enabled
when the live protection rule had it disabled. Do not copy policy values from
older docs or session summaries. For the current solo-maintainer model, zero
required approvals is intentional; if review requirements are introduced, set
the matching live protection options and document them in the same change.

Use SSH for maintainer Git transport when it is configured. Do not add an SSH
private key to Actions for this public repository. GitHub Actions uses its
ephemeral `github.token` only where GitHub API access is required, with the
smallest job-level permissions; never add a personal access token to CI.
