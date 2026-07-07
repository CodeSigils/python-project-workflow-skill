---
name: python-best-practices
description: "Use for changing or reviewing Python project code, packaging, typing, tests, CI, or tooling; inspect first, not concept-only Q&A."
version: 1.2.7
author: CodeSigils
license: MIT
tier: powerful
ref:
  - references/project-orientation.md
  - references/pyproject-template.md
  - references/lint-format-typing-testing.md
  - references/review-checklist.md
  - references/mature-repo-preservation.md
  - references/eval-benchmark-hardening.md
metadata:
  hermes:
    tags: [python, best-practices, code-quality, tooling, verification]
    related_skills: [codebase-inspection, requesting-code-review, shell-scripting]
---

# Python Best Practices Skill

Use for changing or reviewing Python project code, packaging, typing, tests, CI, or tooling; inspect first, not
concept-only Q&A.

## When to Use This Skill

Trigger on Python implementation, refactor, review, packaging, setup, testing, typing, and tooling work. Do not trigger
on general Python concept questions, pure documentation changes, or non-Python tooling unless the user asks to apply the
answer to project code or change Python workflow/conventions.

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

- **Load before editing.** If you are about to edit, create, or review a `.py` file and have not loaded this skill,
  stop and load it first. This skill's review checklist, verification commands, and orientation should inform your
  edits, not validate them after the fact. A retroactive load is better than no load, but loading first is the
  expected workflow.
- **Qualify by code role.** The "must load" rule above applies primarily to Python *product* repos (packages with
  pyproject.toml, test suites, CI toolchains). For Python *support code* in a non-Python repo — scripts, checkers,
  automation helpers with no packaging metadata, no tests, no type toolchain — evaluate cost vs benefit before
  loading the full skill suite. In those cases, project-native gates (the repo's own pre-commit hook, AGENTS.md
  Python policy) often provide the right level of guidance without the 80% overhead of the full skill suite.
  See "Pre-Load Assessment" below.
- **Do NOT load for standalone CI scripts in non-Python repos.** A 150-line Python script in `scripts/` or
  `.github/scripts/` in a repo whose primary content is markdown, YAML, shell, or YAML workflows — with no
  pyproject.toml, no test suite, no type toolchain — is textbook support code. Loading the full skill suite
  in that scenario adds 80% overhead (orientation checklist, version-contract audit, lint-format-typing-testing
  review) for 0% benefit. The script is already correct for its purpose. Use project-native gates instead
  (`shellcheck`, `npx awesome-lint`, the repo's own `verify.sh`, or whatever the repo already has). If the
  pre-load assessment says "support code," trust it without further overhead.
- **After loading, run the Orientation Checklist.** Read `project-orientation.md` to understand the repo's Python
  version contract, tooling, and layout before changing anything.

## Pre-Load Assessment

Before loading the full skill suite (references, review checklist, etc.), answer these questions
to decide whether the effort is worth the overhead:

| Question | Yes means | No means |
|---|---|---|
| Does the repo have a `pyproject.toml` or `setup.py` with packaging metadata? | Full skill — load `project-orientation.md` then `review-checklist.md` | Skip packaging references. Consider `mature-repo-preservation.md` instead. |
| Are there tests under `tests/` or `test/`? | Load `lint-format-typing-testing.md` pytest section | Skip test references. |
| Is there a `ruff.toml`, `.mypy.ini`, or type-checking config? | Load tool-specific references as needed | Skip tooling references. The repo uses project-native gates. |
| Is Python the *product* or *support code*? | Full skill suite is appropriate | Project-native gates (AGENTS.md Python policy, pre-commit hook) likely suffice. Cross-check the core review-checklist items manually instead of loading all references. |
| Does the project have versioned releases or packaging lifecycle? | Load `pyproject-template.md` and `lint-format-typing-testing.md` packaging section | Skip — not relevant for automation-only scripts. |

**Support-code heuristic:** if all Python files are under `scripts/`, there are zero `.py` files in the repo root besides `__init__.py` stubs, and there is no `src/` layout, assume support code. The skill's `mature-repo-preservation.md` reference covers this case.

When in doubt, load only `mature-repo-preservation.md` and `review-checklist.md` — the two smallest references. You can always load more later.

## Orientation Checklist

Load and read `project-orientation.md` to orient yourself in the repository. It covers metadata inspection, source/test
layout, configuration files, CI workflows, and agent documentation.

### Version Control State (Actionable)

- `.gitignore`: inspect existing project-specific rules before suggesting changes. Compare against the
  [official GitHub Python template](https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore) and
  [Toptal Python template](https://www.toptal.com/developers/gitignore/api/python). Check common artifacts:
  `__pycache__/`, `*.py[codz]`, `*.egg-info/`, `build/`, `dist/`, `.coverage`, `.coverage.*`, `coverage.xml`,
  `htmlcov/`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.tox/`, `.nox/`, `.hypothesis/`, `.pytype/`, `.pyre/`,
  `.venv/`, `venv/`, `.env`, and `.env.*`. Preserve local ignores and recommend targeted additions instead of replacing
  wholesale. Do not automatically ignore or commit lockfiles such as `uv.lock`; decide from the target project's
  application vs library policy.
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

| Task                                              | Load reference                                                                                                                             |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| New project setup                                 | `pyproject-template.md`, then `project-orientation.md`                                                                                     |
| Existing project review                           | `review-checklist.md`, then task-specific files                                                                                            |
| Mature repository / automation repo review        | `mature-repo-preservation.md`, then `review-checklist.md`; if eval/benchmark runners are involved, also load `eval-benchmark-hardening.md` |
| **Study/notes repo with custom verification**     | `mature-repo-preservation.md`                                                                                                      |
| Type-hinting                                      | `lint-format-typing-testing.md` (`mypy.md` is deferred)                                                                                    |
| Test work                                         | `lint-format-typing-testing.md` (`pytest.md` is deferred)                                                                                  |
| Packaging/release                                 | `pyproject-template.md` and `lint-format-typing-testing.md` (`packaging.md` deferred)                                                      |
| Error handling/logging                            | `review-checklist.md` (`errors-and-logging.md` is deferred)                                                                                |
| CLI development                                   | `pyproject-template.md` for entry points; for guidance on migrating CLI scripts from bash to Python (thin wrapper pattern, recognition criteria, reference sweep), see `shell-scripting` skill's "When to Migrate from Bash to Python" section |                                                               |
| Migration from existing code                      | `project-orientation.md`; migration-specific reference is deferred                                                                         |
| General Python tooling (lint, format, type, test) | `lint-format-typing-testing.md` |
| Dependency update (check versions, read changelogs, clean up stale CI workarounds) | `review-checklist.md` (dependency section) |

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
- **`IOError` *is* `OSError` since Python 3.3.** Catching both `except (IOError, OSError)` is redundant — `IOError` was merged into `OSError` in PEP 3151. Catching `OSError` alone covers both. This is a common pattern in code written against Python 2 or early 3.x that was never cleaned up. When reviewing, flag the redundancy as a style issue.
- **Guard-condition ordering: classify before allow-list.** When filtering items that need both a STRUCTURAL classification (what IS this thing?) and an ALLOW-LIST check (is it one of the known exceptions?), apply the structural check first, then the allow-list. The reverse order silently accepts items that match the allow-list even when the structural gate should have rejected them. Concrete example: processing `*-by:` attribution trailers where `Co-authored-by:` must be caught but `Closes:` (a standard git trailer that happens to look structurally similar) should be left alone:

  ```python
  # WRONG — allow-list check before structural classification
  if key in ALLOWED_TRAILERS:
      continue              # ← prematurely accepts "co-authored-by" because it IS in
                            #   the list, when it should have been caught by the -by rule
  if not key.endswith("-by"):
      continue
  violations.append(trailer)

  # RIGHT — structural classification first, then allow-list
  if not key.endswith("-by"):
      continue              # ← skip anything that isn't a -by trailer at all
  if key in ALLOWED_TRAILERS:
      continue              # ← now this is safe — we know it IS a -by trailer
  violations.append(trailer)
  ```

  The one-line mnemonic: **"What is it?" before "Is it allowed?"** Without this order, the allow-list doubles as a silent bypass for everything the structural filter was meant to catch.
- **Shared config duplication across sibling scripts.** When two or more Python scripts in the same project define the same hardcoded paths, file lists, or configuration values, each copy is a drift surface. Worse, the same list may have different names in each file (`MISSING_FILES` vs `KEY_FILES`), concealing the duplication from casual inspection. Fix by extracting shared values to a `_paths.py` or `_config.py` module imported by all scripts. Run a cross-file trace (`grep -rn` each value across the repo) before concluding that a single-file review is complete — see P17 in durable-patterns.md and Step 0 in requesting-code-review.
- **Review sibling scripts after editing.** If you changed one Python script, also review its immediate siblings in the same directory — especially scripts that share constants, are called via `subprocess.run`, or implement complementary functions. A `ROOT = Path(".")` or `SCRIPT_DIR` defined independently in two sibling scripts is a drift surface that a single-file review misses. The user will notice if you only reviewed the file you edited and not the ones it depends on or mirrors.

### Backslash-heavy Content: Safe Edit Workflow

Editing files with dense backslash patterns (e.g. sed BRE capture groups `\(...\)`, grep ERE, or shell regex) is a
recurring corruption site. Three independent layers each interpret backslashes differently:

| Layer | `\(` becomes | Mechanism |
|-------|-------------|-----------|
| `patch` tool `old_string`/`new_string` | `\\(` (doubled) | Tool applies its own escape pass — each `\(` becomes `\\(` |
| Python regular string `"\\([^}]*\\)"` | `\([^}]*\)` (correct) | `\\\\` -> `\\`, `\(` -> `(` — works but fragile under editing |
| Python raw string `r"\([^}]*\)"` | `\([^}]*\)` (correct) | Raw = literal — BUT `r"\\([^}]*\\)"` produces `\\(` (double), visually identical |

**The core problem:** there is no single reliable escape-free path through `patch` or Python strings for backslash-heavy content. Each layer interprets backslashes differently. Here is the resolution:

#### Safe workflow (ranked by reliability)

**1. First resort: `write_file` with raw `terminal("cat")` input**

Use `execute_code` with `terminal("cat")` to read raw bytes, then `write_file` — zero escaping layers:

```python
from hermes_tools import terminal, write_file

# Read raw file (no escaping, no format wrapping)
r = terminal(["cat", "/path/to/file"])
content = r["output"]

# Python string replacement — backslashes in your replacement text are literal
content = content.replace(
    'old_backslash_pattern',   # literal bytes from the file
    'new_backslash_pattern'    # literal bytes you want
)

# Write — write_file accepts raw content with no escaping
write_file("/path/to/file", content)
```

Use raw strings `r'...'` so Python doesn't process the backslashes. Verify the result with `xxd` (see Diagnostic below).

**2. Second resort: `sed -i` in single quotes**

Bash single quotes preserve backslashes literally — zero unexpected escaping:

```bash
# Replace `\(` with `\(` (correct BRE capture group)
sed -i 's/\(/\(/g' file
```

**3. Third resort: Python byte-level (binary mode)**

When the edit is too complex for `sed` but `write_file` from `terminal("cat")` has issues, use binary I/O with explicit hex escapes to avoid any ambiguity:

```python3 << 'PYEOF'
data = open('file', 'rb').read()
# Explicit hex escapes — no backslash-counting needed
data = data.replace(b"\x5c\x28", b"\x5c\x29")  # \( and \)
# Or use byte concatenation for extreme cases:
open_paren = b"\x5c\x28"  # \(
close_paren = b"\x5c\x29"  # \)
data = data.replace(b"old_pattern", open_paren + b"[^}]*" + close_paren)
open('file', 'wb').write(data)
PYEOF
```

*Note: `b"\x5c\x28"` is a Python bytes literal — `\x5c` is the hex value 0x5c (backslash), `\x28` is 0x28 (open paren). No backslash escaping confusion.*

**4. Diagnostic: verify bytes before and after every backslash edit**

```bash
# Before editing
sed -n '<LINE_NUM>p' <file> | xxd | grep '5c'

# After editing — confirm single not doubled:
#   5c 28 = \( (correct, one backslash + paren)
#   5c 5c 28 = two backslashes + paren (doubled)
sed -n '<LINE_NUM>p' <file> | xxd | grep '5c'
```

## Verification Commands

Prefer project-native commands if present. Otherwise suggest the baseline.

**Hermes runtime/plugin edits:** If the edited Python lives under `~/.hermes/hermes-agent/` rather than a normal product checkout, do not stop at gateway restart or manual behavior inspection. Run syntax/lint checks against the changed runtime files, a relevant pytest subset, and a focused import/behavior probe from the Hermes runtime venv.

**Ad-hoc verification when no canonical gate is available:** If a changed file has no project-native test/lint/build command, or the session verifier asks for fresh evidence, create a focused temporary verifier under `/tmp` with an OS-safe `hermes-verify-` filename prefix (`mktemp /tmp/hermes-verify-XXXXXX.sh` for shell or `tempfile.NamedTemporaryFile(prefix="hermes-verify-", dir="/tmp", delete=False)` for Python). The verifier should run the smallest meaningful checks for the changed behavior, assert expected outputs, and remove itself afterward when possible. Report this explicitly as "ad-hoc verification", not suite green or full repository validation.

Freshness pitfall: ad-hoc verification is scoped to the files and behavior it checked. If you edit another file afterward — even a comment/docstring/usage example in a sibling script — the previous ad-hoc evidence is stale for that new changed path. Create a new focused `/tmp/hermes-verify-*` verifier for the newly edited behavior before reporting completion. For rewritten validators, mock external dependencies where possible so you can prove both pass and fail paths deterministically instead of relying only on live network state.

For ordinary Python projects:

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

When the skill triggered (you loaded references and gave workflow guidance), structure the final response to include:

- classification of the Python task,
- files changed or reviewed,
- verification commands and results,
- remaining risks or skipped checks,
- concise next step.

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