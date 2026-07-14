# Python Project Workflow

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/CodeSigils/python-project-workflow-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/CodeSigils/python-project-workflow-skill/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![agentskills.io](https://img.shields.io/badge/agentskills.io-v1-blue)](https://agentskills.io/specification)

Portable Python project workflow skill for agentskills.io-compatible agents.

This repo ships an adaptive skill that handles greenfield bootstrap, tooling
configuration, CI setup, packaging, mature-repo preservation, and cross-platform
verification. No agent-specific commands or paths — compatible with Hermes,
Claude Code, Codex CLI, Gemini CLI, OpenCode, and any agentskills.io client.

- **Greenfield projects** — scaffold `pyproject.toml` (PEP 621), `src/` layout,
  uv, Ruff, mypy, pytest, and Google-style docstrings
- **Existing projects** — discover the project's own tooling, work within its
  conventions. No forced migration.
- **Mature repositories** — preservation-first workflow; find the native gate,
  respect conventions, avoid broad defaults, and report before editing
- **CI/verification** — project-native gates, cross-platform tool patterns,
  ad-hoc verification when no gate exists
- **Packaging** — build, publish, entry points, lockfile policy

It is not a Python code-review rule set. For code-review findings, use a
dedicated review skill such as `py-review-skill`.

---

## Quick Start

Make the skill discoverable by your agent.

<details>
<summary><b>Hermes Agent</b></summary>

**Recommended for development — clone the repo and add to `external_dirs`:**
```yaml
skills:
  external_dirs:
    - /path/to/python-project-workflow/skills
```
Every commit is immediately reflected without reinstalling.

**For end users — install from hub:**
```bash
hermes skills install CodeSigils/python-project-workflow-skill
```

*Other agents: see sections below for their native setup commands.*
</details>

<details>
<summary><b>Claude Code</b></summary>

```bash
cp -r skills/python-project-workflow ~/.claude/skills/
```
</details>

<details>
<summary><b>Codex CLI</b></summary>

```bash
cp -r skills/python-project-workflow ~/.codex/skills/
```
</details>

<details>
<summary><b>Gemini CLI / .agents/ path</b></summary>

```bash
cp -r skills/python-project-workflow .agents/skills/
```
</details>

<details>
<summary><b>OpenCode</b></summary>

```bash
cp -r skills/python-project-workflow .opencode/skills/
```
</details>

For agents that support external skill directories, point the config at
`skills/python-project-workflow/` for live-updating access.

---

## How to Use

1. **Load `python-project-workflow`** when working with a Python project.
2. **The skill classifies your project** — greenfield, existing, mature, or
   automation — and loads the relevant reference file automatically.
3. **Review the orientation checklist** (in SKILL.md § Orientation Checklist) to understand
   the project's Python version contract, tooling, and layout before editing.
4. **Use the task classification table** in SKILL.md to load the right
   reference for your task.

All references are self-contained. No external setup, config files, or
environment variables required.

---

## Portability

Each shipped file in `skills/` is checked by CI for agent-specific references
(`skill_view`, `hermes skills`, `from hermes_tools`, platform adapter paths,
etc.). If a commit adds a platform-specific command, CI fails before it reaches
the runtime.

The current surface is entirely cross-agent compatible — zero platform
references in any shipped skill file or reference.

---

## Verify

```bash
python3 .github/scripts/check-portability.py
python3 scripts/validate.py
python3 scripts/verify-urls.py
python3 scripts/test-sync-payload.py
bash scripts/sync-payload.sh --ci
python3 -m ruff check scripts
```

---

## Layout

```text
python-project-workflow/
├── LICENSE
├── CITATION.cff
├── SECURITY.md
├── README.md
├── .gitignore
├── .gitattributes
├── .github/
│   ├── workflows/ci.yml
│   └── scripts/check-portability.py
├── scripts/
│   ├── payload-manifest.json
│   ├── sync-payload.sh
│   ├── test-sync-payload.py
│   ├── validate.py
│   └── verify-urls.py
└── skills/
    └── python-project-workflow/
        ├── SKILL.md                         # orientation inlined
        └── references/
            ├── pyproject-template.md
            ├── lint-format-typing-testing.md
            ├── core-footguns.md
            ├── safe-editing.md
            ├── mature-repo-preservation.md
            ├── eval-benchmark-hardening.md
            └── drift-classes.md
```

Shipping boundary: `skills/python-project-workflow/` is the runtime payload.
Its `SKILL.md` is authored in place, while root `references/` is the canonical
source for mirrored payload references. `scripts/payload-manifest.json` declares
what is mirrored, and `scripts/sync-payload.sh --ci` verifies the boundary without
modifying it. Everything else is repository-only development infrastructure.

## References

| Reference | Purpose |
| :--- | :--- |
| `pyproject-template.md` | Modern baseline template with PEP 621 metadata |
| `lint-format-typing-testing.md` | Practical uv/Ruff/mypy/pytest commands and cross-platform tool guidance |
| `core-footguns.md` | Common Python pitfalls with examples and patterns |
| `safe-editing.md` | Safe edit workflow for backslash-heavy content |
| `mature-repo-preservation.md` | Preservation-first workflow for established repos |
| `eval-benchmark-hardening.md` | Benchmark and eval hardening guidance |
| `drift-classes.md` | Payload drift and installed-mirror staleness detection and remediation |

The Orientation Checklist is now inlined in SKILL.md § Orientation Checklist.

## License

MIT — see [LICENSE](LICENSE).
