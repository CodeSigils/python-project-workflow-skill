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
works with Hermes, Claude Code, Codex, Gemini CLI, OpenCode. It is
agentskills.io-compatible.

---

## What It Does in Practice

Suppose you ask your agent:

> Create a Python 3.11+ command-line project named `invoice-checker`. Use a
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

## Python Frameworks

> **Framework projects (Django, FastAPI, Flask, etc.):** This skill does NOT
> support frameworks. It provides a solid generic Python foundation — uv, ruff,
> mypy, pytest, CI matrix, `.gitignore` — but framework-specific conventions are
> out of its scope. This is by design. For those, use a dedicated skill or add
> the framework's steps to the CI template it generates.

## Quick Start

Make the skill discoverable by your agent.

<details>
<summary><b>Hermes Agent</b></summary>

**Install directly from GitHub:**
```bash
hermes skills install CodeSigils/python-project-workflow-skill/skills/python-project-workflow
```

**For development, clone the repo and add its `skills/` directory to `external_dirs`:**
```yaml
skills:
  external_dirs:
    - /path/to/python-project-workflow/skills
```
Every commit is immediately reflected without reinstalling.

*Other agents: see sections below for their native setup commands.*
</details>

<details>
<summary><b>Claude Code</b></summary>

```bash
mkdir -p ~/.claude/skills
cp -r skills/python-project-workflow ~/.claude/skills/
```
</details>

<details>
<summary><b>Codex</b></summary>

```bash
mkdir -p ~/.agents/skills
cp -r skills/python-project-workflow ~/.agents/skills/
```
</details>

<details>
<summary><b>Gemini CLI / .agents/ path</b></summary>

```bash
mkdir -p .agents/skills
cp -r skills/python-project-workflow .agents/skills/
```
</details>

<details>
<summary><b>OpenCode</b></summary>

```bash
mkdir -p .opencode/skills
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

## Skill Payload — What Ships to the User

Only `skills/python-project-workflow/` is the runtime payload. Everything else
is development infrastructure — canonical reference sources, maintenance
scripts, CI, and repository documentation.

```text
skills/
└── python-project-workflow/
    ├── SKILL.md                          # Runtime workflow and orientation guidance
    └── references/
        ├── pyproject-template.md         # PEP 621 project and tooling baseline
        ├── lint-format-typing-testing.md # Lint, format, type, test, and CI guidance
        ├── core-footguns.md              # Common Python correctness pitfalls
        ├── safe-editing.md               # Safe editing of escape-heavy content
        ├── mature-repo-preservation.md   # Preservation-first existing-repo workflow
        ├── eval-benchmark-hardening.md   # Reliable evaluation and benchmark practices
        ├── drift-classes.md              # Payload and installed-copy drift handling
        └── security-and-gitignore.md     # Secret-safe ignore and Git procedures
```

The payload contains Markdown instructions only: one `SKILL.md` and eight
reference files. It includes no runtime scripts, configuration files, or
dependencies. Copy `skills/python-project-workflow/` to the agent's skill
directory, as described in Quick Start above.

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
python3 scripts/test-validate-ci.py
python3 scripts/verify-urls.py
python3 scripts/test-sync-payload.py
bash scripts/sync-payload.sh --ci
python3 -m ruff check scripts .github/scripts
```

---

## Repo Layout

```text
python-project-workflow/
├── README.md                            # Project overview, setup, usage, and verification
├── LICENSE                              # MIT license terms
├── CITATION.cff                         # Citation metadata for research and tooling
├── SECURITY.md                          # Vulnerability reporting policy and security scope
├── .gitignore                           # Local Python, editor, and agent-state exclusions
├── .gitattributes                       # Cross-platform text and line-ending policy
├── .github/
│   ├── workflows/ci.yml                 # Validation matrix and scheduled URL checks
│   └── scripts/check-portability.py      # Rejects agent-specific runtime references
├── references/                          # Canonical sources mirrored into the payload
│   ├── pyproject-template.md             # PEP 621 project and tool configuration baseline
│   ├── lint-format-typing-testing.md     # Tool commands and staged adoption guidance
│   ├── core-footguns.md                  # Common Python correctness pitfalls
│   ├── safe-editing.md                   # Safe handling of escape-heavy content
│   ├── mature-repo-preservation.md       # Preservation-first workflow for existing repos
│   ├── eval-benchmark-hardening.md       # Reliable benchmark and evaluation practices
│   ├── drift-classes.md                  # Payload and installed-copy drift handling
│   └── security-and-gitignore.md         # Secret-safe ignore and Git procedures
├── scripts/                             # Repository maintenance and validation tools
│   ├── payload-manifest.json             # Declares canonical files copied into the payload
│   ├── sync-payload.sh                   # Synchronizes or checks the runtime payload mirror
│   ├── check-version-consistency.py      # Validates version alignment across manifests and tags
│   ├── check-readme-tree.py              # Ensures README repo-layout tree matches tracked files
│   ├── test-validate-ci.py                # Regression tests for CI policy enforcement
│   ├── test-sync-payload.py              # Regression tests for payload drift behavior
│   ├── validate-ci.py                    # Enforces CI routing, required gates, toolchain policy, and action pins
│   ├── validate.py                       # Checks skill structure, metadata, and references
│   └── verify-urls.py                    # Checks documented external links on a schedule
└── skills/
    └── python-project-workflow/
        ├── SKILL.md                      # Runtime instructions and orientation checklist
        └── references/                   # Shipped mirrors of the canonical references
            └── *.md                      # Same eight guides listed under references/
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
| `security-and-gitignore.md` | Secret-safe `.gitignore`, tracked-file, scanner, and commit-metadata procedures |

The Orientation Checklist is now inlined in SKILL.md § Orientation Checklist.

## License

MIT — see [LICENSE](LICENSE).
