---
name: python-project-workflow
description: Set up, inspect, preserve, and verify Python projects across greenfield bootstrap, tooling configuration, CI, packaging, mature-repo preservation, and project-native verification. Use for Python project workflow tasks, not for pure code review; use py-review-skill or another dedicated review skill for review findings.
---

# Python Project Workflow

Use for setting up, inspecting, preserving, and verifying Python projects:
greenfield bootstrap, tooling configuration, CI, packaging, mature-repo preservation,
and project-native verification.

Do not use this as a Python code-review rule set. If the task is pure code
review, prefer `py-review-skill` or another dedicated review skill.

Framework-specific project conventions are out of scope. For Django, FastAPI,
Flask, and similar frameworks, use a dedicated framework skill or preserve the
project's established framework workflow; do not present this generic baseline
as framework-complete guidance.

## Scope

If this skill was loaded but the user request is a non-trigger, answer **directly** from general knowledge and nothing
more:

- Do NOT load references, mention the skill, or describe your trigger-classification reasoning.
- Do NOT explain why the request did or did not match a trigger — provide only the answer.
- Do NOT use phrases like "this is a non-trigger", "the skill says", "per the trigger guidance", or "exit immediately".
- Do NOT inspect, review, or reference the repository, its files, or its configuration.
- Do NOT propose verification commands, tooling changes, or a verification plan.
- **No preamble, no reasoning chain, no trigger assessment text.** Produce the answer as if the skill were never loaded.

The user should not be able to tell this skill was present in your configuration.

## Agent Process Pitfalls

- **Load before editing.** If you are about to edit or create a `.py` file and have not loaded this skill,
  stop and load it first. This skill's verification commands and orientation should inform your
  edits, not validate them after the fact. A retroactive load is better than no load, but loading first is the
  expected workflow.
- **Qualify by code role.** The "must load" rule above applies primarily to Python *product* repos (packages with
  pyproject.toml, test suites, CI toolchains). For Python *support code* in a non-Python repo — scripts, checkers,
  automation helpers with no packaging metadata, no tests, no type toolchain — evaluate cost vs benefit before
  loading the full skill suite. In those cases, project-native gates (the repo's own pre-commit hook, AGENTS.md
  Python policy) often provide the right level of guidance without the 80% overhead of the full skill suite.
  See "Project Type Classification" below.
- **Do NOT load for standalone CI scripts in non-Python repos.** A short Python script in `scripts/` or
  `.github/scripts/` in a repo whose primary content is markdown, YAML, shell, or YAML workflows — with no
  pyproject.toml, no test suite, no type toolchain — is textbook support code. Loading the full skill suite
  in that scenario adds 80% overhead (orientation checklist, version-contract audit, lint-format-typing-testing
  review) for 0% benefit. The script is already correct for its purpose. Use project-native gates instead
  (`shellcheck`, `npx awesome-lint`, the repo's own `verify.sh`, or whatever the repo already has). If the
  pre-load assessment says "support code," trust it without further overhead.
- **After loading, run the Orientation Checklist.** Use the checklist below to understand the repo's Python
  version contract, tooling, and layout before changing anything.

## Project Type Classification

On load, classify the project to load only relevant guidance:

| Signal | Classification | Load |
|--------|---------------|------|
| Empty/new directory, or an explicit request for a new scaffold, with no established source or tooling conventions | Greenfield | `pyproject-template.md`, then Orientation Checklist below |
| pyproject.toml or setup.py present, coherent tooling | Existing | Orientation Checklist below, then tool-specific guidance |
| Python only in scripts/, no packaging metadata, governance scripts | Automation / mature | `mature-repo-preservation.md`, skip packaging refs |
| Eval/benchmark runners present | Automation with benchmarks | Also load `eval-benchmark-hardening.md` |

**Support-code heuristic:** if all Python files are under `scripts/`, there are zero `.py` files in the repo root besides `__init__.py` stubs, and there is no `src/` layout, assume support code. The skill's `mature-repo-preservation.md` reference covers this case.

Apply the Existing and Automation rows before inferring Greenfield. Missing packaging metadata or a tests directory does
not make a repository greenfield when it already contains meaningful source, scripts, documentation, or project history.
Only classify such a repository as Greenfield when the user explicitly requests a new scaffold.

When in doubt, load only `mature-repo-preservation.md` — the smallest reference. You can always load more later.

## Orientation Checklist

Before giving advice, inspect the repository to understand its current state
and conventions. This checklist covers metadata, layout, configuration, CI,
and documentation.

### Python Project Metadata

- `pyproject.toml`:
  - `[project].name`, `version`, `description`, `authors`
  - `[project].requires-python`
  - `[project].dependencies`, `optional-dependencies`
  - `[build-system]` (build backend)
  - Tool sections: `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]`, `[tool.hatch]`
- `setup.py` / `setup.cfg` (if present)
- `requirements*.txt`, `uv.lock`, `poetry.lock`, `Pipfile`
- `.pre-commit-config.yaml`

### Source and Test Layout

- Source layout: `src/<package>/` (recommended), flat `<package>/`, or namespace packages
- Test layout: `tests/` or `test/`; presence of `conftest.py`, fixtures
- CLI entry points: `scripts/`, `cli/`, or `console_scripts` in metadata

### Configuration Files

- Ruff: `ruff.toml`, `.ruff.toml`, or `pyproject.toml` under `[tool.ruff]`
- MyPy: `mypy.ini`, `.mypy.ini`, or `pyproject.toml` under `[tool.mypy]`
- Pytest: `pytest.ini`, `tox.ini`, `noxfile.py`, or `pyproject.toml` under `[tool.pytest.ini_options]`
- Formatting: `pyproject.toml` under `[tool.black]` or project-native formatter config
- Type checking stubs: `py.typed` marker

### CI and Workflow

- `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, etc.
- Look for steps running: `uv sync`, `pip install`, `tox`, `nox`, `pytest`, `ruff`, `mypy`, `build`, `publish`
- Cross-platform indicators: CI matrix across OS, `setup-python` version spec, `.gitattributes` line endings

### Agent and Developer Documentation

- `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/*` # portability: allow-platform-ref, `.continue/rules/*`, `.github/copilot-instructions.md`
- `README.md`, `CONTRIBUTING.md`, `DEVELOPMENT.md`
- Documentation directories: `docs/`, `doc/`, `documentation/`

### Version Control State (Actionable)

- `.gitignore`: inspect existing project-specific rules before suggesting changes. Preserve local and security-related
  rules; make targeted additions instead of replacing the file wholesale. Preserve a sanitized `!.env.example` when
  used. Never commit credentials, access tokens, private keys, or populated secret files.
- `.gitignore` does not protect files that Git already tracks. Before claiming a sensitive path is protected, check
  tracked-file state without printing file contents. If a suspected secret is tracked or may have entered Git history,
  stop, alert the user, avoid exposing the value in output, and recommend revocation or rotation; removing or ignoring
  the file does not erase historical exposure.
- Never include credentials, access tokens, private keys, sensitive values, or secret-bearing URLs in commit subjects
  or bodies. Describe the issue generically and redact sensitive identifiers from version-control metadata.
- Do not automatically ignore or commit lockfiles such as `uv.lock`; decide from the target project's application vs
  library policy.
- Inspect recent tooling/configuration commits through bounded metadata or counts. Do not print raw commit bodies. If
  suspected secret-bearing metadata is encountered, stop and report only its existence or location.
- For `.gitignore`, secret-file, tracked-sensitive-file, credential-exposure, or commit-metadata work, load
  `references/security-and-gitignore.md` before advising or editing. It owns executable checks and detailed pattern
  guidance; the safety rules above always apply.

### Python Version Contract (Critical)

Always determine the project's declared and tested Python version range:

1. **Declared range**:
   - `pyproject.toml`: `[project].requires-python`
   - `setup.py`: `python_requires=` argument
   - `setup.cfg`: `[options].python_requires`
   - `tox.ini`: `envlist` or `basepython`
   - CI workflows: `strategy.matrix.python-version` or equivalent
   - `uv.lock` / `poetry.lock` may implicitly reflect tested versions

2. **Effective range** (what CI actually tests):
   - CI matrix: check all tested Python minor versions
   - If no CI, assume only the developer's local version is tested

3. **Tool configuration alignment**:
   - Ruff: `[tool.ruff].target-version` (e.g., `py311`)
   - MyPy: `[tool.mypy].python_version` (e.g., `python_version = 3.10`)
   - Pyright: `pyrightconfig.json` `pythonVersion`
   - For a project that supports a range of Python versions, target the minimum
     supported version. A newer target can allow syntax that fails on the
     declared minimum. Use a newer target only when configuration explicitly
     scopes it to code that does not support the project-wide minimum.

4. **Risk indicators**:
   - Code uses syntax newer than declared minimum (e.g., `match`/`case` in 3.8 project)
   - Dependency updates drop older Python support without version bump
   - README claims broader support than tested in CI
   - Tool configs target a different version than `requires-python`

## Resolution Chain

When references don't cover the exact scenario, escalate in order:

1. **Project-native gates first** — check Makefile, CI workflow scripts, project-specific commands
2. **Skill references** — consult the relevant reference per the Project Type Classification above
3. **Official tool docs** — search tool documentation via web (ruff docs, mypy docs, pytest docs, uv docs)
4. **Ask the user** — request clarification or additional context

## Task Classification Table

Classify the task so the skill loads only what is useful:

| Task                                              | Load reference                                                                                                                             |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| New project setup                                 | `pyproject-template.md`, then Orientation Checklist below |
| Existing project orientation                      | Orientation Checklist above |
| Mature repository / automation repo review        | `mature-repo-preservation.md`; if eval/benchmark runners are involved, also load `eval-benchmark-hardening.md` |
| **Study/notes repo with custom verification**     | `mature-repo-preservation.md`                                                                                                      |
| Type-hinting                                      | `lint-format-typing-testing.md` |
| Test work                                         | `lint-format-typing-testing.md` |
| Packaging/release                                 | `pyproject-template.md` |
| CI / verification setup                           | `lint-format-typing-testing.md` |
| `.gitignore` / secret-safe Git workflow            | `security-and-gitignore.md` |
| CLI development                                   | `pyproject-template.md` for entry points |
| Migration from existing code                      | Orientation Checklist above |
| General Python tooling (lint, format, type, test) | `lint-format-typing-testing.md` |

## Modern Baseline Defaults

For greenfield or incoherent projects, the preferred baseline is:

```text
uv + ruff + mypy + pytest + pyproject.toml/PEP 621 + src/ layout + Google-style docstrings
```

But present this as a default, not a mandate. Always explain the trade-offs and verify compatibility with the project's
declared Python version range.

### For Applications

- If you control the deployment environment (e.g., internal tool, web service), consider `requires-python = ">=3.12"` to
  use the latest features.
- If deploying to older LTS systems (e.g., Ubuntu 22.04 with Python 3.10), use `>=3.10`.

### For Libraries

- Aim for broad compatibility: `>=3.10` is the current default when no ecosystem constraint says otherwise.
- For new projects, do not select Python 3.8: it reached end-of-life in October 2024 and no longer receives security
  fixes. Use `>=3.10` or a newer floor that fits the deployment environment.
- For an existing project that still declares Python 3.8, preserve the current contract unless the user authorizes a
  compatibility-breaking change. Warn that 3.8 is unsupported upstream, identify the constraint keeping it in scope,
  and recommend a tested migration plan. Do not silently raise `requires-python` or remove 3.8 from CI.
- Review this floor as Python 3.10 approaches end-of-life in October 2026.

## Core Python Footguns

The compact awareness reference covers late-bound closures, identity versus equality, float comparisons, mutation while
iterating, wildcard imports, redundant `IOError`/`OSError` handling, shared automation configuration, and related
pitfalls. See `references/core-footguns.md`; use a dedicated review skill for a full code-review rule set.

### Backslash-heavy Content: Safe Edit Workflow

Editing files with dense backslash patterns (sed/grep/shell regex) is a recurring corruption site
because editing interfaces, language strings, shells, and target parsers may interpret escapes differently.
See `references/safe-editing.md` for the safe workflow and focused byte-level diagnostic.

## Verification Commands

Prefer project-native commands if present. Otherwise suggest the baseline.

### Cross-Platform Tool Preference

When writing or reviewing verification commands:
- Prefer `rg` (ripgrep) over `grep` when installed — it respects `.gitignore`,
  is faster, and has consistent flags across platforms.
- Use POSIX-safe tools (`od -A x -t x1z`) over Linux-specific ones (`xxd`).
- For file-searching patterns, prefer Python (`pathlib.rglob`, `os.walk`)
  or `rg` over `find | grep` where possible — fewer escaping pitfalls.
- Prefer project-native commands (Makefile scripts, CI workflow commands)
  over ad-hoc shell one-liners.
- **Check freshness.** If a reference file uses point-in-time version numbers,
  verify them against current official documentation before relying on them.

**Ad-hoc verification when no canonical gate is available:** If a changed file has no project-native test/lint/build command, or the session verifier asks for fresh evidence, create a focused temporary verifier under `/tmp` with an OS-safe `py-workflow-verify-` filename prefix (`mktemp /tmp/py-workflow-verify-XXXXXX.sh` for shell or `tempfile.NamedTemporaryFile(prefix="py-workflow-verify-", dir="/tmp", delete=False)` for Python). The verifier should run the smallest meaningful checks for the changed behavior, assert expected outputs, and remove itself afterward when possible. Report this explicitly as "ad-hoc verification", not suite green or full repository validation.

Freshness pitfall: ad-hoc verification is scoped to the files and behavior it checked. If you edit another file afterward — even a comment/docstring/usage example in a sibling script — the previous ad-hoc evidence is stale for that new changed path. Create a new focused `/tmp/py-workflow-verify-*` verifier for the newly edited behavior before reporting completion. For rewritten validators, mock external dependencies where possible so you can prove both pass and fail paths deterministically instead of relying only on live network state.

For ordinary Python projects:

```bash
# Synchronize the virtual environment and install the default dev dependency group
uv sync

# Check code style and linting (Ruff)
uv run ruff check .

# Check formatting (Ruff formatter)
uv run ruff format --check .

# Type checking (MyPy)
uv run mypy .

# Run tests (pytest)
uv run pytest

# Build the package (if packaging metadata was touched)
uv build
```

## Reporting

When the skill triggered (you loaded references and gave workflow guidance), structure the final response to include:

- classification of the Python task,
- files changed or reviewed,
- verification commands and results,
- remaining risks or skipped checks,
- concise next step.

Redact credentials, tokens, private keys, connection strings, sensitive URLs, and secret values from reports, command
output excerpts, generated documentation, and examples. Report existence or location only. Do not claim a repository is
secret-free from filename checks or absence of a regex match.

When the skill did **not** trigger, skip this Reporting section entirely. End with a direct answer to the user's
question without workflow scaffolding.

## Preserve Local Conventions

Unless the user explicitly asks for modernization, preserve coherent local conventions. Do not invent success. Report
actual command output and triage failures.

For mature repositories, especially governance or automation repos, first decide whether Python is the product or
support code. If Python appears only in scripts, generators, checkers, or tests and no packaging metadata exists, do
**not** force the greenfield baseline. Load `references/mature-repo-preservation.md`, use project-native gates first,
and keep any `pyproject.toml`/uv/Ruff/MyPy/src-layout suggestions as optional modernization unless the user authorizes
that work.

When a mature repository has canonical source plus installed/runtime/generated mirrors, treat source/runtime drift as a
blocking review finding. Edit canonical source first, sync mirrors with the project-provided command, and run both
source-only and mirror-aware gates before claiming the runtime behavior changed.

When resuming an interrupted Python implementation or review, treat compaction summaries and prior assistant claims as
leads, not truth. Reconstruct state from machine facts first: inspect git status/log/diff, reread the repository's
active agent/context files, check changed paths, and rerun the relevant project gates before continuing, committing, or
claiming completion. If the interruption left staged or uncommitted changes, classify them before editing so you do not
overwrite valid partial work or preserve stale transitional state.

For Python automation repositories with eval or benchmark runners, load `references/eval-benchmark-hardening.md` before
reviewing or changing runner behavior. In particular, preserve effective backend/model metadata in machine-readable
artifacts when fallback paths are possible, and keep eval assertion alternatives diagnostic rather than broadly true of
any reasonable answer.
