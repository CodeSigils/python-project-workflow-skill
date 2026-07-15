# Python Project Workflow

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/CodeSigils/python-project-workflow-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/CodeSigils/python-project-workflow-skill/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![agentskills.io](https://img.shields.io/badge/agentskills.io-v1-blue)](https://agentskills.io/specification)

**Python Project Workflow** — guides an AI agent through Python project setup,
tooling, CI, packaging, and preservation.

This skill handles greenfield scaffolds (src layout, PEP 621, uv/Ruff/mypy/pytest),
existing-project orientation, mature-repo preservation, CI configuration, packaging,
and project hygiene — `.gitignore` presets, `__pycache__`/coverage/venv artifact
handling, and preserving local ignore rules.

It does **not** review Python code. Pair it with
[`py-review-skill`](https://github.com/CodeSigils/py-review-skill) for that.

The shipped payload is portable — no agent-specific commands or paths — so it
works with Hermes, Claude Code, Codex, Gemini CLI, OpenCode, and any
agentskills.io client.

---

## What It Does in Practice

Suppose you ask your agent:

> Create a Python 3.10+ command-line project named `invoice-checker`. Use a
> `src/` layout, add tests and GitHub Actions, and leave it ready to build.

The workflow guides the agent to:

1. classify the directory as a greenfield Python project;
2. establish one consistent Python-version contract across packaging, tools,
   and CI;
3. create PEP 621 project metadata, the package and CLI entry point, tests,
   Ruff, mypy, and pytest configuration;
4. add an appropriate GitHub Actions matrix and lockfile policy;
5. run the relevant lint, format, type, test, and build gates; and
6. report exactly what was created, what passed, and any remaining decisions.

A typical result looks like:

```text
invoice-checker/
├── pyproject.toml
├── uv.lock
├── src/invoice_checker/
│   ├── __init__.py
│   └── cli.py
├── tests/
│   └── test_cli.py
└── .github/workflows/ci.yml
```

For an established project, the behavior is deliberately different: the skill
first discovers the existing package manager, layout, version floor, formatter,
test runner, and native CI gate. It works within those conventions instead of
replacing Poetry with uv, Black with Ruff, or tox with a new workflow merely to
match the greenfield defaults.

After implementation, use
[`py-review-skill`](https://github.com/CodeSigils/py-review-skill) for the
complementary code-review pass. The workflow skill answers “how should this
project be structured and verified?”; the review skill answers “what is wrong or
risky in this Python code?”

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

The repository is not currently indexed in the Hermes hub, so no hub-install
command is advertised. Clone plus `external_dirs` is the verified Hermes path
until registration.

*Other agents: see sections below for their native setup commands.*
</details>

<details>
<summary><b>Claude Code</b></summary>

```bash
cp -r skills/python-project-workflow ~/.claude/skills/
```
</details>

<details>
<summary><b>Codex</b></summary>

```bash
cp -r skills/python-project-workflow ~/.agents/skills/
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

The current runtime surface is entirely cross-agent compatible. Platform setup
commands remain in this repository README; shipped skill files and references
use portable paths and client-neutral operations.

---

## Verify

```bash
python3 .github/scripts/check-portability.py
python3 scripts/validate-ci.py
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
│   ├── validate-ci.py
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
