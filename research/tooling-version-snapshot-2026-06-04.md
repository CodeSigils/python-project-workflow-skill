# Python Tooling Snapshot — 2026-06-04

This file records the live checks used to revalidate Phase 0 tooling claims on 2026-06-04. It is evidence for planning
and reference updates; runtime guidance should still tell agents to inspect the target project first.

## Commands run

```bash
date -u +%F

python3 - <<'PY'
import json, urllib.request
repos=['astral-sh/uv','astral-sh/ruff','python/mypy','pytest-dev/pytest','PyCQA/isort']
for repo in repos:
    with urllib.request.urlopen(f'https://api.github.com/repos/{repo}', timeout=20) as r:
        data=json.load(r)
    print(f'{repo}\tstars={data.get("stargazers_count")}\tupdated={data.get("updated_at")}')
print('--- pypi versions ---')
for pkg in ['uv','ruff','mypy','pytest','setuptools']:
    with urllib.request.urlopen(f'https://pypi.org/pypi/{pkg}/json', timeout=20) as r:
        data=json.load(r)
    print(f'{pkg}\tlatest={data["info"].get("version")}')
PY
```

## Observed output

```text
2026-06-04
astral-sh/uv	stars=85953	updated=2026-06-04T06:15:56Z
astral-sh/ruff	stars=47800	updated=2026-06-04T06:14:30Z
python/mypy	stars=20457	updated=2026-06-04T02:12:39Z
pytest-dev/pytest	stars=13887	updated=2026-06-03T12:09:32Z
PyCQA/isort	stars=6944	updated=2026-06-04T01:09:46Z
--- pypi versions ---
uv	latest=0.11.19
ruff	latest=0.15.15
mypy	latest=2.1.0
pytest	latest=9.0.3
setuptools	latest=82.0.1
```

## Phase 0 implications

- The preferred greenfield baseline remains defensible: uv, Ruff, mypy, pytest, pyproject.toml/PEP 621, `src/` layout,
  and Google-style docstrings as a default for general-purpose Python.
- Star counts are useful popularity signals, not authority. Python claims should be grounded in PEPs, PyPA, and upstream
  tool documentation.
- Version numbers are intentionally not hard-pinned in the runtime skill. The skill should recommend current stable
  tooling while telling agents to verify compatibility with the target project's `requires-python`, CI matrix, and
  lockfiles.
- `setuptools>=61.0` remains the minimum setuptools floor when choosing setuptools as the PEP 621 backend; newer
  projects can also choose Hatchling, Flit, PDM, or another backend when appropriate.
- `ruff` can replace many Flake8/isort/Black workflows in greenfield projects, but established projects should not be
  migrated without user approval.
- `pytest` remains the default test runner for new general-purpose Python projects, but existing
  unittest/tox/nox/hatch/pixi/framework runners should be preserved when coherent.
