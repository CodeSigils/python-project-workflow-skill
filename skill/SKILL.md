---
name: python-best-practices
description: "An adaptive workflow for working on Python projects. Inspect first, then advise."
version: 1.0.2
author: CodeSigils
license: MIT
tier: powerful
metadata:
  hermes:
    tags: [python, best-practices, code-quality, tooling, verification]
    related_skills: [codebase-inspection, requesting-code-review]
---

# Python Best Practices Skill

An adaptive workflow for working on Python projects. Inspect first, then advise.

## When to Use This Skill

Trigger on Python implementation, refactor, review, packaging, setup, testing, typing, and tooling work. Do not trigger
on general Python concept questions, pure documentation changes, or non-Python tooling unless the user asks to apply the
answer to project code or change Python workflow/conventions.

## Orientation Checklist

Before giving advice, inspect the repository to understand its current state and conventions.

### Python Project Metadata

- `pyproject.toml`:
  - `[project].name`, `version`, `description`, `authors`
  - `[project].requires-python` (declared Python compatibility)
  - `[project].dependencies`, `optional-dependencies`
  - `[build-system]` (build backend)
  - Tool-specific sections: `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]`, `[tool.hatch]`, etc.
- `setup.py` / `setup.cfg` (if present)
- `requirements*.txt`, `uv.lock`, `poetry.lock`, `Pipfile` (lockfiles)
- `tox.ini`, `noxfile.py` (test automation)
- `.pre-commit-config.yaml`

### Source and Test Layout

- Source layout:
  - `src/<package>/` (recommended)
  - Flat `<package>/` at project root
  - Namespace packages
- Test layout:
  - `tests/` (recommended)
  - `test/` (less common)
  - Presence of `conftest.py`, fixtures
- Scripts and CLI entry points: `scripts/`, `cli/`, or console_scripts in metadata

### Configuration Files

- Ruff: `ruff.toml`, `.ruff.toml`, `pyproject.toml` under `[tool.ruff]`
- MyPy: `mypy.ini`, `.mypy.ini`, `pyproject.toml` under `[tool.mypy]`
- Pytest: `pytest.ini`, `tox.ini`, `noxfile.py`, `pyproject.toml` under `[tool.pytest.ini_options]`
- Formatting: `pyproject.toml` under `[tool.black]` or project-native formatter config
- Import sorting: `isort.cfg`, `.isort.cfg`, `pyproject.toml` under `[tool.isort]`
- Type checking stubs: `py.typed` marker

### CI and Workflow

- `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, etc.
- Look for steps that run: `uv sync`, `pip install -e .[test]`, `tox`, `nox`, `pytest`, `ruff`, `mypy`, `build`,
  `publish`

### Agent and Developer Documentation

- `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/*`, `.continue/rules/*`, `.github/copilot-instructions.md`, `CONVENTIONS.md`,
  `.aider*`
- `README.md`, `CONTRIBUTING.md`, `DEVELOPMENT.md`
- Documentation directories: `docs/`, `doc/`, `documentation/`
- **Web Research (Optional)**: When current package/tool facts matter, use verified sources. If deeper web research
  would help, suggest installing or loading the Scrapling Hermes skill. If the user does not want to install/load that
  skill, continue with another verified source when possible.

### Version Control State

- `.gitignore`:
  - Inspect existing project-specific rules before suggesting changes.
  - Compare against the official GitHub Python template first:
    <https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore>.
  - Use the gitignore.org/Toptal generated Python template as a secondary checklist:
    <https://www.toptal.com/developers/gitignore/api/python>.
  - Check common Python-generated artifacts: `__pycache__/`, `*.py[codz]`, `*.egg-info/`, `build/`, `dist/`,
    `.coverage`, `.coverage.*`, `coverage.xml`, `htmlcov/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.tox/`,
    `.nox/`, `.hypothesis/`, `.pytype/`, `.pyre/`, `.venv/`, `venv/`, `.env`, and `.env.*`.
  - Preserve local ignores and recommend targeted additions instead of replacing the file wholesale.
  - Do not automatically ignore or commit lockfiles such as `uv.lock`; decide from the target project's application vs
    library policy.
- Recent commits that affect tooling or configuration

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
   - These should be within or equal to the declared `requires-python` range

4. **Risk indicators**:
   - Code uses syntax newer than declared minimum (e.g., `match`/`case` in 3.8 project)
   - Dependency updates drop older Python support without version bump
   - README claims broader support than tested in CI
   - Tool configs target a different version than `requires-python`

## Task Classification Table

Classify the task so the skill loads only what is useful:

| Task                                              | Load reference                                                                        |
| ------------------------------------------------- | ------------------------------------------------------------------------------------- |
| New project setup                                 | `pyproject-template.md`, then `project-orientation.md`                                |
| Existing project review                           | `review-checklist.md`, then task-specific files                                       |
| Type-hinting                                      | `lint-format-typing-testing.md` (`mypy.md` is deferred)                               |
| Test work                                         | `lint-format-typing-testing.md` (`pytest.md` is deferred)                             |
| Packaging/release                                 | `pyproject-template.md` and `lint-format-typing-testing.md` (`packaging.md` deferred) |
| Error handling/logging                            | `review-checklist.md` (`errors-and-logging.md` is deferred)                           |
| CLI development                                   | `pyproject-template.md` for entry points; CLI-specific reference is deferred          |
| Migration from existing code                      | `project-orientation.md`; migration-specific reference is deferred                    |
| General Python tooling (lint, format, type, test) | `lint-format-typing-testing.md`                                                       |

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
- Only go lower than 3.10 if you have a specific need to support older systems (for example enterprise, distro-bound, or
  plugin ecosystems).
- Avoid `>=3.8` unless absolutely necessary; Python 3.8 reached end-of-life in September 2024.
- Review this floor as Python 3.10 approaches end-of-life in October 2026.

## Core Python Footguns

Watch out for these common sources of bugs or confusion:

- Mutable default arguments: `def foo(items=[]):` -> use `None` and create a new list inside.
- Late binding closures in loops: capture loop variables with `functools.partial` or default arguments.
- Misunderstanding `__init__` vs `__new__`.
- Assuming `==` works for all types (especially floats).
- Not closing resources (files, sockets, etc.) -> use context managers (`with`).
- Confusion between `is` and `==` for mutable types.
- Modifying a list while iterating over it -> iterate over a copy or use list comprehensions.
- Importing `*` from modules -> pollutes namespace and makes dependencies unclear.
- Not handling exceptions properly -> bare `except:` or swallowing exceptions.
- Assuming dictionaries are ordered (before Python 3.7, they were not guaranteed to be).
- Using `+` for string concatenation in loops -> use `str.join()` or `io.StringIO`.
- Threading issues: GIL, race conditions, deadlocks.
- Multiprocessing: pickling issues, shared state.

## Verification Commands

Prefer project-native commands if present. Otherwise suggest the baseline:

```bash
# Synchronize the virtual environment and install dependencies (including dev)
python -m uv sync

# Check code style and linting (Ruff)
python -m ruff check .

# Check formatting (Ruff formatter)
python -m ruff format --check .

# Type checking (MyPy)
python -m mypy .

# Run tests (pytest)
python -m pytest

# Build the package (if packaging metadata was touched)
python -m build
```

## Reporting

The final response should include:

- classification of the Python task,
- files changed or reviewed,
- verification commands and results,
- remaining risks or skipped checks,
- concise next step.

## Preserve Local Conventions

Unless the user explicitly asks for modernization, preserve coherent local conventions. Do not invent success. Report
actual command output and triage failures.
