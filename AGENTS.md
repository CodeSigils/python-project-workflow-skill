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

`docs/decisions.md` records non-obvious maintainer choices with their sources and
recheck triggers. Before researching a setup, pinning, or policy question from
scratch, read it; the answer is often already recorded, so there is no need to
re-derive it. When you make a durable choice others would otherwise re-research,
add an entry with its `Status`, `Decided` date, `Sources` (registered in
`docs/evidence-urls.json`), and a `Recheck` trigger. `scripts/validate.py` rejects
an incomplete entry or one that cites an unregistered source.

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
