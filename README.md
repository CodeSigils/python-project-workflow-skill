# Python Best Practices — Hermes Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Hermes Skill](https://img.shields.io/badge/hermes-skill-purple)](https://hermes-agent.nousresearch.com/docs)

Adaptive guidance for Python projects: inspect the repo, preserve local conventions, apply modern defaults where they fit.

The skill is a structured workflow — **orient, classify, load focused reference, advise/edit, verify, report** — not a Python encyclopedia. It helps agents make safe, evidence-backed decisions about tooling, linting, typing, testing, packaging, and code review.

## Install

```bash
hermes skills install skills-sh/CodeSigils/python-best-practices-skill/skill
```

To update later:

```bash
hermes skills check
hermes skills update
```

## What it does

When loaded, the skill adapts to the target project:

- **Greenfield projects** — sets up `pyproject.toml` (PEP 621), `src/` layout, uv, Ruff, mypy, pytest, and Google-style docstrings.
- **Existing projects** — discovers the project's own tooling (Poetry, Hatch, tox, nox, unittest, etc.) and works within its conventions. No forced migration.
- **Mature repositories** — preservation-first: find the native gate, respect `AGENTS.md`, avoid broad defaults, produce a review report before editing.
- **Code review** — checks typing, packaging, CI, test structure, security posture, and common Python pitfalls with a structured checklist.

The trigger description is deliberately scoped:

> Use for changing or reviewing Python project code, packaging, typing, tests, CI, or tooling; inspect first, not concept-only Q&A.

Python concept questions ("what is a decorator") answer directly without loading the skill suite.

## Verify

```bash
# Source-only check (portable, no local Hermes install needed):
python3 scripts/run_phase2_checks.py --skip-installed

# Full gate with installed mirror:
python3 scripts/run_phase2_checks.py --sync-installed
python3 scripts/run_phase2_checks.py
```

## Layout

```text
python-best-practices-skill/
├── LICENSE            # MIT license
├── CITATION.cff       # Software citation metadata (CFF v1.2.0)
├── SECURITY.md        # Security policy and vulnerability reporting
├── README.md          # Project overview (this file)
├── .gitignore
├── .gitattributes
├── .github/workflows/ # CI validation
├── scripts/           # Local validation script
│   └── run_phase2_checks.py
└── skill/             # Runtime skill payload
    ├── SKILL.md
    └── references/
        ├── project-orientation.md
        ├── pyproject-template.md
        ├── lint-format-typing-testing.md
        ├── review-checklist.md
        ├── mature-repo-preservation.md
        └── eval-benchmark-hardening.md
```

Shipping boundary: `skill/` is the runtime payload and source of truth. Everything else is repository-only development infrastructure.

## References

The skill loads scoped reference files at runtime rather than embedding all guidance in the router:

| Reference | Purpose |
| :--- | :--- |
| `project-orientation.md` | Inspection checklist — discover project tooling and conventions |
| `pyproject-template.md` | Modern baseline template with PEP 621 metadata |
| `lint-format-typing-testing.md` | Practical uv/Ruff/mypy/pytest commands and staged adoption |
| `review-checklist.md` | Structured code-review checklist |
| `mature-repo-preservation.md` | Preservation-first workflow for established repos |
| `eval-benchmark-hardening.md` | Benchmark and eval hardening guidance |

## License

MIT — see [LICENSE](LICENSE).
