# Python Project Workflow

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![agentskills.io](https://img.shields.io/badge/agentskills.io-v1-blue)](https://agentskills.io/specification)

Set up, inspect, preserve, and verify Python projects. This skill covers
greenfield bootstrap, tooling configuration, CI, packaging, mature-repo
preservation, and project-native verification.

It is not a Python code-review rule set. For code-review findings, use a
dedicated review skill such as `py-review-skill`.

## Install

Install the runtime payload by copying or symlinking
`skills/python-project-workflow/` into your agent's skills directory.

Generic agentskills.io-compatible layout:

```bash
cp -r skills/python-project-workflow <your-skills-dir>/
```

Codex CLI:

```bash
cp -r skills/python-project-workflow ~/.codex/skills/
```

Claude Code:

```bash
cp -r skills/python-project-workflow .claude/skills/
```

Hermes Agent:

```yaml
skills:
  external_dirs:
    - /path/to/python-project-workflow/skills/python-project-workflow
```

## What It Does

When loaded, the skill adapts to the target project:

- **Greenfield projects**: scaffold `pyproject.toml` (PEP 621), `src/` layout,
  uv, Ruff, mypy, pytest, and Google-style docstrings.
- **Existing projects**: discover the project's own tooling and work within its
  conventions. No forced migration.
- **Mature repositories**: preservation-first workflow; find the native gate,
  respect conventions, avoid broad defaults, and report before editing.
- **CI/verification**: project-native gates, cross-platform tool patterns, and
  ad-hoc verification when no gate exists.
- **Packaging**: build, publish, entry points, and lockfile policy.

## Verify

```bash
python3 scripts/validate.py
python3 scripts/verify-urls.py
python3 -m ruff check scripts
```

## Layout

```text
python-project-workflow/
├── LICENSE
├── CITATION.cff
├── SECURITY.md
├── README.md
├── .gitignore
├── .gitattributes
├── .github/workflows/
│   └── ci.yml
├── scripts/
│   ├── validate.py
│   └── verify-urls.py
└── skills/
    └── python-project-workflow/
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

Shipping boundary: `skills/python-project-workflow/` is the runtime payload and
source of truth. Everything else is repository-only development infrastructure.

## References

| Reference | Purpose |
| :--- | :--- |
| `project-orientation.md` | Inspection checklist: discover project tooling and conventions |
| `pyproject-template.md` | Modern baseline template with PEP 621 metadata |
| `lint-format-typing-testing.md` | Practical uv/Ruff/mypy/pytest commands and cross-platform tool guidance |
| `core-footguns.md` | Common Python pitfalls with examples and patterns |
| `safe-editing.md` | Safe edit workflow for backslash-heavy content |
| `mature-repo-preservation.md` | Preservation-first workflow for established repos |
| `eval-benchmark-hardening.md` | Benchmark and eval hardening guidance |

## License

MIT — see [LICENSE](LICENSE).
