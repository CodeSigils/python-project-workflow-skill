# Hermes Skill Design Patterns Borrowed from Other Ecosystems

This document converts the cross-ecosystem research into concrete design rules
for the future `python-best-practices` Hermes skill.

## Recommended skill shape

```text
skill/
├── SKILL.md
└── references/
    ├── project-orientation.md
    ├── pyproject-template.md
    ├── ruff.md
    ├── mypy.md
    ├── pytest.md
    ├── packaging.md
    ├── errors-and-logging.md
    └── review-checklist.md
```

## Top-level SKILL.md responsibilities

Keep `SKILL.md` short enough that the agent can load it often. It should do only
five things:

1. Trigger on Python implementation, refactor, review, packaging, test, or setup
   work.
2. Inspect live project state before recommending tools.
3. Select the right reference file for the task.
4. Apply core Python footgun checks.
5. Require verification evidence before reporting complete.

Everything else belongs in linked reference files.

## Proposed workflow

```text
ORIENT → CLASSIFY → ADVISE/EDIT → VERIFY → REPORT
```

### ORIENT

Inspect files before advising:

- `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements*.txt`, `uv.lock`,
  `poetry.lock`, `Pipfile`, `tox.ini`, `noxfile.py`, `pytest.ini`, `mypy.ini`,
  `ruff.toml`, `.pre-commit-config.yaml`, `.github/workflows/*.yml`.
- Source layout: `src/<package>/`, flat package, namespace packages, scripts.
- Test layout: `tests/`, `conftest.py`, fixtures, integration markers.
- Supported Python version from metadata and CI.

### CLASSIFY

Classify the task so the skill loads only what is useful:

| Task | Load reference |
| :--- | :------------- |
| New project setup | `pyproject-template.md`, `ruff.md`, `mypy.md`, `pytest.md` |
| Existing project review | `review-checklist.md`, then task-specific files |
| Type-hinting | `mypy.md` |
| Test work | `pytest.md` |
| Packaging/release | `packaging.md` |
| Error handling/logging | `errors-and-logging.md` |

### ADVISE/EDIT

Use the repo's existing stack if it is already coherent. Recommend the modern
baseline when:

- the project has no established tooling,
- the user asks for a new project setup,
- the existing stack is fragmented or stale and the user asks for modernization.

Default modern baseline:

```text
uv + ruff + mypy + pytest + pyproject.toml/PEP 621 + src/ layout
```

### VERIFY

Prefer project-native commands if present. Otherwise suggest the baseline:

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest
uv build
```

For existing projects, do not invent success. Report actual command output and
triage failures.

### REPORT

The final response should include:

- classification of the Python task,
- files changed or reviewed,
- verification commands and results,
- remaining risks or skipped checks,
- concise next step.

## Anti-patterns to avoid in the Hermes skill

1. Mega-prompt SKILL.md that repeats every Python rule inline.
2. Dogmatic migration to uv/ruff/mypy when the repo has a working established
   stack and the user did not request modernization.
3. Advice without commands.
4. Config snippets without explaining supported Python versions.
5. Telling agents to use `mypy --strict` without a gradual adoption strategy for
   existing untyped codebases.
6. Treating generated files, vendored files, lock files, and migrations the same
   as source code.
7. Overloading one skill with Django/FastAPI/scientific/release-engineering
   details that should become focused subskills or references later.

## Concrete first-draft requirements

The first `skill/SKILL.md` draft should include these mandatory sections:

1. When to use this skill.
2. Orientation checklist.
3. Task classification table.
4. Modern baseline defaults.
5. Verification commands.
6. Python footguns.
7. Progressive-disclosure reference list.
8. Reporting format.

## Best next implementation step

Write `skill/SKILL.md` using this file as the design contract, then add the first
three reference files:

1. `skill/references/pyproject-template.md`,
2. `skill/references/ruff-mypy-pytest.md`,
3. `skill/references/review-checklist.md`.
