# Lint, Format, Typing, and Testing Commands

This reference provides command recipes for the modern Python toolchain (uv, ruff, mypy, pytest) and guidance on
adopting strictness incrementally.

## Default Commands (Greenfield or when no project-native commands exist)

Assuming you have `uv` installed and a `pyproject.toml` with the modern baseline:

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

## Cross-Platform Testing Considerations

When testing cross-platform compatibility:

- Use `nox` or `tox` with matrices covering different Python versions and operating systems
- GitHub Actions example:
  `strategy.matrix: {os: [ubuntu-latest, windows-latest, macos-latest], python-version: [\"3.9\", \"3.10\", \"3.11\", \"3.12\"]}`
- Test console scripts/installation on all target platforms
- Consider using `cibuildwheel` for building wheels across platforms
- Test path handling with `pathlib` to avoid platform-specific issues
- Be aware of filesystem case sensitivity differences (case-sensitive on Linux/macOS, case-insensitive on Windows by
  default)

## Using Project-Native Commands

Always prefer commands discovered from the project's configuration:

- Check `Makefile`, `justfile`, `taskfile.sh`, or `scripts/` for common tasks.
- Look at CI workflows (`.github/workflows/*.yml`) for the exact commands used in testing.
- If the project has `noxfile.py` or `tox.ini`, consider using `nox` or `tox` as they may encapsulate complex matrix
  testing.
- If the project uses `hatch`, `pixi`, or `poetry`, use their respective commands (`hatch run test`, `pixi run test`,
  `poetry run pytest`).

Example: If the project's CI uses `nox -s test-3.11`, prefer that over `uv run pytest` unless you have a reason to
bypass the project's test matrix.

## Staged Adoption of Strictness (for existing projects)

Do not enable all strictness flags at once in a large existing codebase. Instead, adopt them incrementally.

### Ruff

- Start with a safe, useful subset such as `select = ["E", "F", "I", "UP", "B", "SIM"]` for greenfield projects.
- In legacy projects, begin with the project's existing rule set or the smallest subset that catches real defects
  without flooding the diff.
- Add stricter categories in separate changes after the team has reviewed the signal/noise ratio.
- Use `--fix` for auto-fixable rules only after reviewing what will be changed; avoid `--unsafe-fixes` unless the user
  explicitly accepts the risk.

### MyPy

Begin with:

```toml
[tool.mypy]
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = false
```

Then, over time:

1. Enable `check_untyped_defs` to get warnings for untyped function bodies.
2. Enable `disallow_untyped_defs` to require type hints on function definitions.
3. Enable `disallow_incomplete_defs` and `check_untyped_defs` for class attributes.
4. Finally, consider `disallow_untyped_decorators` and `no_implicit_optional`.

Use `# type: ignore` comments sparingly and only with a ticket or comment explaining why.

### Testing

- Aim for high test coverage but do not sacrifice test quality for percentage.
- Use coverage tools to identify untested critical paths, but remember that 100% coverage is not the goal.
- Property-based testing (e.g., with `hypothesis`) can be valuable for complex logic.

### Characterization Tests (Approval Tests)

When refactoring legacy code that has no existing tests, write **characterization tests** first to lock in existing
behavior before making changes:

1. Run the code against representative inputs and capture the output.
2. Write a test that asserts the captured output (an "approval test" or "golden file" test).
3. Refactor the code, then confirm the test still passes.
4. If the refactoring is correct but changes behavior, update the golden file.

Tools: `pytest-regressions` (data file approval), `syrupy` (snapshot testing), `pytest-approvaltests` (text-based
approval). For new projects, `syrupy` is the lightest option; for existing projects, start with inline assertions or
`pytest-regressions`.

This technique prevents accidental behavior changes during refactoring and builds a test safety net gradually.

## Existing-Project Caveats

- Do not reformat an entire codebase on a whim; it creates noisy history and obscures real changes. If reformatting is
  needed, do it in a separate commit with a clear message, and avoid mixing it with logic changes.
- When enabling stricter linting or type checking, expect to fix real issues or add `# type: ignore` comments with
  justification.
- Lockfiles (`uv.lock`, `poetry.lock`) should be updated in a separate commit from logic changes unless the dependency
  update is the purpose of the change.
- If the project uses a different toolchain (e.g., `flake8`, `black`, `pylint`), consider whether switching to the
  modern baseline adds enough value to justify the disruption. Sometimes it's better to improve within the existing
  toolchain.

## Verifying Tool Alignment

Ensure that the Python version targeted by your tools matches the project's declared `requires-python`:

- Check Ruff: `[tool.ruff].target-version` should be within or equal to `requires-python`.
- Check MyPy: `[tool.mypy].python_version` should be within or equal to `requires-python`.
- If using `pyright`, check `pyrightconfig.json` for `pythonVersion`.

Mismatches can lead to false positives (e.g., MyPy complaining about syntax that is actually supported) or false
negatives (missing errors because the tool is configured for an older version).

## Special Cases

### Jupyter Notebooks

- Use `nbqa` to run Ruff, MyPy, etc., on notebooks: `nbqa ruff check notebook.ipynb`.
- Consider separating logic from notebooks: put the core logic in `.py` files and keep notebooks for exploration and
  reporting.

### Mixed Python/Cython Projects

- MyPy may need configuration to understand `.pyx` files or to ignore them.
- Ensure the build system (e.g., `setuptools` with `Cython` or `scikit-build`) is invoked before type checking if
  needed.

### Generated Files

- Explicitly exclude generated files from linting, formatting, and type checking if they are not meant to be edited. Use
  `.ruffignore`, `.mypyignore`, or configure the tool to skip certain paths.
- Clearly document which files are generated and who owns them.

## When to Suggest the Modern Baseline

Recommend the modern baseline (`uv`, `ruff`, `mypy`, `pytest`, `pyproject.toml/PEP 621`, `src/` layout) when:

- The project has no established tooling for linting, formatting, typing, or testing.
- The user explicitly asks for a new project setup or modernization.
- The existing toolchain is fragmented (multiple, conflicting tools) or stale (unmaintained, missing critical features).
- The project is incoherent (e.g., some parts use `flake8`, others `pylint`; some tests use `unittest`, others `pytest`
  without consolidation).

Otherwise, improve within the existing toolchain unless the user requests migration.
