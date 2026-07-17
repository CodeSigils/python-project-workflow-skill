# Modern pyproject.toml Template (PEP 621)

This file provides a minimal, modern `pyproject.toml` using PEP 621 metadata. Adjust the values to fit your project.

> **Freshness:** Packaging metadata and Python EOL guidance were reviewed on 2026-07-17.
> Verify against official docs before using in production.
> See [ruff docs](https://docs.astral.sh/ruff/), [mypy docs](https://mypy.readthedocs.io/),
> [pytest docs](https://docs.pytest.org/), [uv docs](https://docs.astral.sh/uv/) for current versions.

## Minimal Template

```toml
[build-system]
# setuptools>=77.0.3 supports the PEP 639 license metadata used below
# If the project uses an older build backend (hatchling, flit_core, pdm-backend),
# keep its existing build-system config instead of migrating to setuptools.
# Check official documentation for latest compatible version
requires = ["setuptools>=77.0.3", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-package"
version = "0.1.0"
description = "A short description of your package."
readme = "README.md"
requires-python = ">=3.11"  # or >=3.12 for controlled applications; preserve ecosystem floors
authors = [
    {name = "Your Name", email = "you@example.com"}
]
# SPDX license expression and included license files (PEP 639)
license = "MIT"
license-files = ["LICENSE*"]
# Keywords for discoverability
keywords = ["python", "package"]
# Classifiers help users find your package on PyPI
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Operating System :: OS Independent",
]
# Runtime dependencies
dependencies = [
    # Example: "requests>=2.28.0",
]
# Local development dependencies (PEP 735); uv sync includes dev by default
[dependency-groups]
dev = [
    "pytest",
    "ruff",
    "mypy",
]
# For reusable templates, avoid stale generic pins. Pin in applications or lockfiles
# when reproducibility requires it, after checking Python compatibility.
# Entry points for console scripts (if applicable)
[project.scripts]
# your-cli = "your_package.__main__:main"
```

## CLI Greenfield Minimum

For a new CLI project: `src/your_package/__init__.py`, `__main__.py`, `tests/test_cli.py`.
Use `argparse` unless the user prefers Click or Typer. Add one CLI smoke test.

## Source Layout Recommendation

Use the `src/` layout to avoid accidental imports from the source tree and to isolate the package.

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

This tells setuptools to look for packages under the `src/` directory.

## Tool Configuration Examples

### Ruff

```toml
[tool.ruff]
target-version = "py311"  # Align with requires-python
line-length = 88

[tool.ruff.lint]
# Start with a useful, reviewable subset. Do not enable ALL by default.
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = []

[tool.ruff.format]
quote-style = "double"
```

### MyPy

```toml
[tool.mypy]
python_version = "3.11"  # Target the minimum version in requires-python
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
```

### Pytest

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = ["-ra", "-q"]
```

## Cross-Platform Considerations

When authoring cross-platform Python packages:

- Use `pathlib` instead of `os.path.join` for path manipulation
- Test console scripts on target platforms (Windows/macOS/Linux)
- Consider line endings in `.gitattributes` (`* text=auto`)
- Avoid platform-specific assumptions in setup.py/pyproject.toml
- Test installation and basic functionality on all supported platforms
- Use environment markers in dependencies when needed (`sys_platform == "win32"`)

## Version Recommendations

### For Applications

- If you control the deployment environment (e.g., internal tool, web service), consider `requires-python = ">=3.12"` to
  use the latest features.
- If deployment must use a distribution's system Python, set the floor to the oldest supported image you actually
  deploy. For example, Ubuntu 26.04 LTS currently defaults to Python 3.14; older supported images may require a lower
  floor.

### For Libraries

- Aim for broad compatibility without starting on a near-EOL interpreter: `>=3.11` is the current default when no
  ecosystem constraint says otherwise.
- For new projects, do not select Python 3.10 by default: it is in source-only security maintenance and reaches
  end-of-life in October 2026. Use `>=3.11` or a newer floor that fits the deployment environment.
- For existing projects that still declare 3.10, preserve the contract unless a compatibility-breaking migration is in
  scope. Document the constraint and plan a tested migration before changing `requires-python` or the CI matrix.
- For new projects, do not select Python 3.8: it reached end-of-life in October 2024 and no longer receives security
  fixes. Use `>=3.11` or a newer floor that fits the deployment environment.
- For existing projects that still declare 3.8, preserve the contract unless a compatibility-breaking migration is in
  scope. Document the legacy constraint, warn that 3.8 is unsupported upstream, and plan a tested migration before
  changing `requires-python` or the CI matrix.

### Dependency Floor

- When choosing a dependency version, check its `requires-python` to ensure it doesn't declare a higher floor than your
  project.
- Use `python -m pip index versions <package>` to inspect available releases and `uv tree` or `pipdeptree` to audit the
  resolved dependency graph.

## Notes

- The `requires-python` field is critical for telling installers (pip, uv) which Python versions are supported.
- Keep `requires-python`, tool configuration (`target-version`, `python_version`), and CI matrix in sync.
- For existing projects, do not change `requires-python` without understanding the impact on users.
- When in doubt, preserve the existing `requires-python`, align tooling to it, and flag unsupported Python versions for
  an explicit migration decision.
- **Version Maintenance**: Tool version recommendations in this template represent current best practices at time of
  writing. Check official documentation for latest compatible versions and update periodically.
