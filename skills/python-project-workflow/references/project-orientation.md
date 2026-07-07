# Project Orientation

Before giving advice, inspect the repository to understand its current state and conventions.

## Inspection Checklist

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
- **Cross-platform indicators**:
  - CI matrix including multiple operating systems (windows-latest, ubuntu-latest, macos-latest)
  - Use of `actions/setup-python` with proper version specification
  - Handling of line endings in `.gitattributes`
  - Platform-specific dependency handling
  - Testing on target deployment platforms

### Agent and Developer Documentation

- `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/*`, `.continue/rules/*`, `.github/copilot-instructions.md`, `CONVENTIONS.md`,
  `.aider*`
- `README.md`, `CONTRIBUTING.md`, `DEVELOPMENT.md`
- Documentation directories: `docs/`, `doc/`, `documentation/`

### Version Control State

- `.gitignore`:
  - Inspect existing project-specific rules before suggesting changes.
  - Compare against the official GitHub Python template first:
    <https://github.com/github/gitignore/blob/main/Python.gitignore>.
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

## Decision: Apply Baseline or Preserve?

After inspection, classify the project using the table in SKILL.md (§ Project Type Classification):

- **Greenfield** (no pyproject.toml, no setup.py, no tests): Load `pyproject-template.md` and set up the modern baseline.
- **Existing / coherent toolchain**: Preserve local conventions; suggest incremental improvements within them.
- **Automation / mature** (Python only in scripts/, no packaging metadata): Load `mature-repo-preservation.md` — do not force greenfield defaults.
- **Fragmented or stale toolchain**: Recommend modernization only with explicit user approval and a migration plan.
- **Specialized domains** (scientific, embedded, enterprise): Respect domain-specific constraints (e.g., conda/pixi/mamba, older Python LTS).

Do not force `src/` layout, uv, Ruff, strict MyPy, or another greenfield convention onto a coherent existing project.
Recommend those as optional migrations only when the user asks for modernization or the inspection shows clear toolchain
fragmentation.
