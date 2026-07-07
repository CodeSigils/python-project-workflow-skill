# Shipping Strategy

**Evidence basis:**
[ai-project-governance packaging-strategies research](https://github.com/CodeSigils/ai-project-governance/blob/main/research/packaging-strategies.md)
(14 ecosystem sources surveyed) and
[Hermes skills system documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills).

## Research Grounding

The packaging-strategies research examined 6 battle-tested projects (cookiecutter, uv, just, biome, ast-grep) and 8
ecosystem packaging patterns (npm, pre-commit, GitHub Actions, Go modules, Rust crates, Python src-layout, Hermes
skills). The universal finding across all of them:

> A manifest file at the root defines the entry point. Everything else in the repo is invisible to the consumer. No
> ecosystem uses a combined glob-allowlist plus exclusion-list approach for packaging — the boundary is always defined
> by a single manifest or a directory boundary.

Hermes skills follow the same pattern: the skill directory (`SKILL.md` + optional references, templates, scripts) IS the
artifact. Files not referenced by `SKILL.md` are invisible at runtime.

## Shipping Boundary

| What ships to the user            | What stays in the repo                          |
| :-------------------------------- | :---------------------------------------------- |
| `skill/SKILL.md`                  | `README.md`, `vision.md` |
| `skill/references/*.md`           | `CONTRIBUTING.md`, `SHIPPING.md`   |
| (anything else `skill/` contains) | `HANDOFF.md`, `VERSIONS.md`, `LICENSE`          |
|                                   | `research/`, `references/`, `evals/`, `tests/`  |
|                                   | `scripts/`, `.github/`, workspace output        |

The canonical source is `skill/` in this repository. The installed Hermes mirror at
`~/.hermes/skills/software-development/python-best-practices` is a local testing copy, not a distribution target.

## Distribution Model: GitHub-Backed Skill Entry

This skill uses a **GitHub-backed skill entry.** The GitHub repo IS the distribution channel — there is no separate
runtime package to maintain. Hermes resolves the public skill identifier to the `skill/` payload in this repository at
install and update time.

### How users install

```bash
# Public install identifier:
hermes skills install skills-sh/CodeSigils/python-best-practices-skill/skill

# Preview before installing:
hermes skills inspect skills-sh/CodeSigils/python-best-practices-skill/skill
```

Single-command install is the simplest path. The `skill/` directory in this repo IS the skill payload behind the public
identifier.

### Update workflow

```bash
# Local development:
cd ~/projects/python-best-practices-skill
# ... edit skill/SKILL.md or skill/references/ ...
python3 scripts/run_phase2_checks.py --sync-installed  # copy to local mirror for testing
python3 scripts/run_phase2_checks.py                    # verify all gates pass
git add -A && git commit -m "..."                        # commit changes
git push origin main                                     # publish to GitHub

# Consumer updates (run by anyone who installed the skill):
hermes skills check              # see if upstream has changes
hermes skills update             # reinstall with latest from GitHub
```

### Sync strategy

| Event                | User action                                                                    |
| :------------------- | :----------------------------------------------------------------------------- |
| First install        | `hermes skills install skills-sh/CodeSigils/python-best-practices-skill/skill` |
| New references added | `git push` → `hermes skills update`                                            |
| Bug fix to SKILL.md  | `git push` → `hermes skills update`                                            |
| Check for updates    | `hermes skills check`                                                          |
| Uninstall            | `hermes skills uninstall python-best-practices`                                |

There is no dual-maintenance problem: GitHub is the single source of truth, and the public skill entry points back to
this repository.

## Development Workflow (Maintainers)

While developing, use the local installed mirror for rapid iteration:

```bash
cd ~/projects/python-best-practices-skill
python3 scripts/run_phase2_checks.py --sync-installed   # sync skill/ to mirror
python3 scripts/run_phase2_checks.py                     # verify all gates pass
python3 -m pytest tests -q                                # run regression tests
```

This is the same loop documented in `CONTRIBUTING.md`. The `--sync-installed` command copies the `skill/` directory to
`~/.hermes/skills/software-development/python-best-practices` so the installed skill reflects your latest edits without
a hub round-trip.

Once changes are ready, commit, push, and consumers run `hermes skills update`.

## Relationship to the Hermes Hub

The current install path uses the public `skills-sh/...` identifier for this GitHub-backed skill. There is no separate
package file to build for GitHub-based distribution.

If the skill is ever contributed to the **official Hermes optional skills catalog** (requiring a Hermes core PR), the
install command would change to:

```bash
hermes skills install official/owner/python-best-practices
```

That path would add an additional synchronization point (the Hermes release cycle) but would make the skill discoverable
in `hermes skills browse --source official`. This remains an optional future step.

For now, the GitHub-backed public skill entry has zero package-build overhead, one source of truth, and a simple update
chain.
