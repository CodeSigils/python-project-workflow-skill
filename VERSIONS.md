# Version Choices Rationale

This document explains the rationale behind version choices in templates and recommendations. Last revalidated:
2026-06-04.

## Policy

The runtime skill should avoid hard-pinning tool versions in generic templates. Instead, it should:

1. inspect the target project's `requires-python`, lockfiles, and CI matrix;
2. choose tool versions compatible with that support policy;
3. prefer current stable releases for greenfield projects;
4. preserve existing pins in coherent projects unless the task is dependency modernization;
5. document any version floor that is required by a standard or feature.

## setuptools>=61.0

`setuptools>=61.0` is the minimum setuptools floor used in the template because setuptools 61 introduced beta support
for PEP 621 project metadata in `pyproject.toml`. It is not a recommendation to pin every project to 61.x; use newer
compatible setuptools releases unless the target project has a reason not to.

Observed on PyPI during the 2026-06-04 revalidation: setuptools 82.0.1.

## Python Version Requirements

For libraries, `>=3.10` is the current default recommendation when no user or ecosystem constraint says otherwise. It
balances modern syntax and broad enough compatibility.

Lifecycle context:

- Python 3.8 reached end-of-life in September 2024.
- Python 3.9 reaches end-of-life in October 2025.
- Python 3.10 reaches end-of-life in October 2026.

For applications in controlled environments, `>=3.12` or newer can be reasonable when the deployment runtime supports
it. For enterprise, distro-bound, scientific, or plugin ecosystems, preserve the ecosystem's support floor unless
modernization is explicitly requested.

## Tool Snapshot from 2026-06-04

| Tool       | Latest observed PyPI version | Guidance                                                                          |
| :--------- | :--------------------------- | :-------------------------------------------------------------------------------- |
| uv         | 0.11.19                      | Greenfield project/dependency/environment/tool runner default.                    |
| Ruff       | 0.15.15                      | Greenfield lint/import-sort/format default. Stage rule selection.                 |
| mypy       | 2.1.0                        | Greenfield/library type checker default; adopt incrementally for legacy projects. |
| pytest     | 9.0.3                        | Greenfield test-runner default; preserve coherent existing runners.               |
| setuptools | 82.0.1                       | One valid build backend; `>=61.0` is the PEP 621 feature floor.                   |

See `research/tooling-version-snapshot-2026-06-04.md` for command output.

## Maintenance Notes

- Recheck tool versions quarterly when editing templates.
- Recheck Python EOL status at least annually or when changing `requires-python` guidance.
- Do not update runtime templates merely to chase the latest version number; update when compatibility, defaults, or
  recommended behavior changes.
