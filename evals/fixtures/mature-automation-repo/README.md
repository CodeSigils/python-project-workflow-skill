# Mature Automation Repo Fixture

This fixture is intentionally not a Python package. It models a governance repository whose Python code supports
repository checks.

Use the native validation command:

```bash
bash scripts/check-consistency.sh
```

The repository has no `pyproject.toml`, no lockfile, and no package build backend on purpose.
