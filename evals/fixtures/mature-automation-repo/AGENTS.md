# Mature Automation Repo Agent Contract

This fixture represents a mature governance/automation repository. Python is used for scripts and tests, not as a
packaged application.

## Required workflow

1. Read this file before recommending changes.
2. Preserve the existing repository contract and shell-first validation gate.
3. Do not migrate to uv, Ruff, MyPy, or a src/ layout unless explicitly requested.
4. Prefer the project-native gate:

```bash
bash scripts/check-consistency.sh
python3 -m pytest tests -q
```
