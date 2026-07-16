# Lint, Format, Typing, and Testing Commands

This reference provides command recipes for the modern Python toolchain ([uv](https://docs.astral.sh/uv/), [ruff](https://docs.astral.sh/ruff/), [mypy](https://mypy.readthedocs.io/), [pytest](https://docs.pytest.org/)) and guidance on
adopting strictness incrementally.

## Default Commands (Greenfield or when no project-native commands exist)

Assuming you have `uv` installed and a `pyproject.toml` with the modern baseline.

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

If `uv` is unavailable, create and activate a virtual environment using the
platform-appropriate activation command, then install the project and its dev
extra explicitly:

```bash
python -m venv .venv
# Activate .venv for the current shell, then run:
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

If the project does not define a `dev` extra, install its project-native
development requirements instead. The Ruff, mypy, pytest, and build commands
above remain unchanged.

## Cross-Platform Testing Considerations

When testing cross-platform compatibility:

- Use `nox` or `tox` with matrices covering different Python versions and operating systems
- GitHub Actions example:
  `strategy.matrix: {os: [ubuntu-latest, windows-latest, macos-latest], python-version: [\"3.10\", \"3.11\", \"3.12\", \"3.13\", \"3.14\"]}`
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

### Ruff

- Start with `select = ["E", "F", "I", "UP", "B", "SIM"]` for greenfield projects.
- In legacy projects, begin with the existing rule set or the smallest subset that catches defects without flooding the diff.
- Use `--fix` only after reviewing what will be changed; avoid `--unsafe-fixes` unless the user accepts the risk.

### MyPy

```toml
[tool.mypy]
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = false
```

Then incrementally: enable `check_untyped_defs` → `disallow_untyped_defs` → `disallow_incomplete_defs` → strict flags.
Use `# type: ignore` sparingly, always with a comment.

### Testing

- Aim for high coverage but do not sacrifice test quality for percentage.
- For legacy code with no tests, write **characterization tests** first (run against representative inputs, capture output, assert against it) — tools: `syrupy` (new projects), `pytest-regressions` (existing).

## Existing-Project Caveats

- Do not reformat an entire codebase in the same commit as logic changes.
- Lockfile updates belong in separate commits.
- If the project uses a different toolchain (flake8, black, pylint), improve within it unless migration is explicitly requested.

## Verifying Tool Alignment

Ensure `requires-python` aligns with tool targets: `[tool.ruff].target-version`,
`[tool.mypy].python_version`, and `pyrightconfig.json` `pythonVersion`. For a
supported range, these should normally target its minimum version; targeting a
newer version can miss syntax incompatibilities. Mismatches cause false
positives or negatives.

## Special Cases

- **Jupyter notebooks**: use `nbqa ruff check notebook.ipynb`. Keep core logic in `.py` files.
- **Cython**: MyPy may need config to understand `.pyx` files; invoke build system before type checking.
- **Generated files**: exclude from lint/format/type checking via `.ruffignore` or tool config. Document ownership.

## When to Suggest the Modern Baseline

Recommend `uv` + `ruff` + `mypy` + `pytest` + PEP 621 + `src/` layout when:
- The project has no established tooling.
- The user explicitly asks for modernization.
- The existing toolchain is fragmented or stale.

Otherwise, improve within the existing toolchain unless the user requests migration.
