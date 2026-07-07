# Python Project Workflow — Hermes Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Hermes Skill](https://img.shields.io/badge/hermes-skill-purple)](https://hermes-agent.nousresearch.com/docs)

Set up, inspect, and verify Python projects. Greenfield bootstrap, tooling configuration, CI packaging, mature-repo preservation — not code review.

For Python code review rules, install [nathan-gage/python-skills](https://github.com/nathan-gage/python-skills) (70 rules, impact levels, code examples).

## Install

```bash
hermes skills install skills-sh/CodeSigils/python-project-workflow-skill/skill
```

To update later:

```bash
hermes skills check
hermes skills update
```

## What it does

When loaded, the skill adapts to the target project:

- **Greenfield projects** — scaffold `pyproject.toml` (PEP 621), `src/` layout, uv, Ruff, mypy, pytest, and Google-style docstrings.
- **Existing projects** — discovers the project's own tooling and works within its conventions. No forced migration.
- **Mature repositories** — preservation-first: find the native gate, respect conventions, avoid broad defaults, produce a review report before editing.
- **CI/verification** — project-native gates, cross-platform tool patterns, ad-hoc verification when no gate exists.
- **Packaging** — build, publish, entry points, lockfile policy.

## Companion: nathan-gage/python-skills

For code review rules (70 rules across 8 categories with impact levels), install:

```bash
git clone https://github.com/nathan-gage/python-skills ~/.hermes/skills/python-skills
```

Both skills coexist. nathan-gage handles code review. This skill handles project workflow.

## Verify

```bash
# Source-only check (portable, no local Hermes install needed):
python3 scripts/validate.py --skip-installed

# Full gate with installed mirror:
python3 scripts/validate.py --sync-installed
python3 scripts/validate.py
```

## Layout

```text
python-project-workflow-skill/
├── LICENSE            # MIT license
├── CITATION.cff       # Software citation metadata (CFF v1.2.0)
├── SECURITY.md        # Security policy and vulnerability reporting
├── README.md          # Project overview (this file)
├── .gitignore
├── .gitattributes
├── .github/workflows/
│   └── ci.yml
├── scripts/           # Local validation script
│   └── validate.py
└── skill/             # Runtime skill payload
    ├── SKILL.md
    └── references/
        ├── project-orientation.md
        ├── pyproject-template.md
        ├── lint-format-typing-testing.md
        ├── core-footguns.md
        ├── safe-editing.md
        ├── mature-repo-preservation.md
        └── eval-benchmark-hardening.md
```

Shipping boundary: `skill/` is the runtime payload and source of truth. Everything else is repository-only development infrastructure.

## References

| Reference | Purpose |
| :--- | :--- |
| `project-orientation.md` | Inspection checklist — discover project tooling and conventions |
| `pyproject-template.md` | Modern baseline template with PEP 621 metadata |
| `lint-format-typing-testing.md` | Practical uv/Ruff/mypy/pytest commands and cross-platform tool guidance |
| `core-footguns.md` | Common Python pitfalls with examples and patterns |
| `safe-editing.md` | Safe edit workflow for backslash-heavy content |
| `mature-repo-preservation.md` | Preservation-first workflow for established repos |
| `eval-benchmark-hardening.md` | Benchmark and eval hardening guidance |

## License

MIT — see [LICENSE](LICENSE).
