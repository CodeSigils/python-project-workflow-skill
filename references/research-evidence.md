# Python Best Practices — Research Evidence

Research revalidated on 2026-06-04. This distilled evidence supports the skill strategy, but it is not a substitute for
inspecting each target repository.

Primary evidence files:

- `research/cross-ecosystem-skill-strategy.md`
- `research/cross-ecosystem-agent-instructions.md`
- `research/hermes-skill-patterns.md`
- `research/requirements-txt-role.md`
- `research/python-gitignore-templates.md`
- `research/tooling-version-snapshot-2026-06-04.md`
- `research/code-extraction/best-practices.md`

## Modern Tooling Stack

| Layer                         | Preferred greenfield default                             | Existing-project caveat                                                                             | Evidence source                                         |
| :---------------------------- | :------------------------------------------------------- | :-------------------------------------------------------------------------------------------------- | :------------------------------------------------------ |
| Project/dependency management | uv                                                       | Preserve Poetry, Hatch, tox, nox, pixi, conda, pip-tools, or enterprise workflows when coherent.    | Astral uv docs, PyPA specs                              |
| Lint/import-sort/format       | Ruff                                                     | Preserve Black/isort/Flake8/Pylint when already standardized unless modernization is requested.     | Astral Ruff docs                                        |
| Type checking                 | mypy                                                     | Adopt incrementally for legacy/framework-heavy/script-heavy projects; detect Pyright/Pylance first. | mypy docs                                               |
| Testing                       | pytest                                                   | Preserve unittest, tox, nox, hatch, pixi, or framework runners when coherent.                       | pytest docs                                             |
| Packaging metadata            | `pyproject.toml` with PEP 621                            | Do not migrate layouts or build backends without understanding distribution/user impact.            | PyPA specs, PEP 518, PEP 621, PEP 660                   |
| Source layout                 | `src/` layout for packages                               | Do not reorganize established packages without explicit approval.                                   | PyPA tutorial, pytest good practices                    |
| Version-control hygiene       | `.gitignore` checked against maintained Python templates | Preserve repo-specific ignores; recommend targeted additions rather than replacing the file.        | GitHub Python.gitignore, gitignore.org/Toptal generator |
| Docstrings                    | Google style for general-purpose Python                  | NumPy/Sphinx/reST styles remain valid in scientific and library projects.                           | Google Python Style Guide, ecosystem caveats            |

## Key Observations

1. Strong agent-instruction ecosystems favor small, scoped, repo-aware instructions with progressive disclosure. That
   supports `SKILL.md` as a router plus focused references, not a mega-prompt.
2. The skill's first action must be repository inspection. Blindly applying uv/Ruff/mypy/pytest defaults can damage
   established projects.
3. Modern Python packaging is `pyproject.toml`-centered, but historical PEPs are not the whole operational source of
   truth. Use current PyPA specifications and packaging guide pages for implementation details.
4. Ruff is the greenfield lint/import-sort/format default because it covers much of the Flake8/isort/Black surface area,
   but strict rule selection should be staged.
5. uv is the greenfield workflow default because it unifies project management, dependency resolution, environments,
   lockfiles, Python installs, and tool execution. Existing package-manager commitments still win by default.
6. mypy catches useful classes of errors, but strict mode is a destination for many existing projects, not the first
   step.
7. pytest remains the general-purpose testing default. The skill should still prefer project-native wrappers discovered
   from CI, Makefile, nox, tox, hatch, pixi, poetry, or framework docs.
8. `requirements.txt` is no longer the preferred source of package metadata for new packages, but it remains useful for
   deployment constraints, pip-only environments, and interoperability. See `research/requirements-txt-role.md`.
9. Version recommendations should be verified periodically, not hard-coded as stale facts. The 2026-06-04 snapshot
   observed uv 0.11.19, Ruff 0.15.15, mypy 2.1.0, pytest 9.0.3, and setuptools 82.0.1 on PyPI.
10. Python `.gitignore` review should use maintained templates as checklists, not wholesale replacements. Prefer the
    official GitHub Python template as the primary source and gitignore.org/Toptal as a secondary comparison source.

## Authority Ranking

```text
1. Current PyPA specifications and Python documentation
2. PEPs for accepted language/packaging rationale and historical context
3. Tool upstream documentation: uv, Ruff, mypy, pytest, setuptools/build backend docs
4. Repo-local project files and CI for target-project truth
5. High-quality public agent-instruction examples for structure, not technical authority
6. Popularity signals such as GitHub stars
```

## Default pyproject shape

Use this only for greenfield projects or when the user asks for modernization. Existing projects should inherit their
current build backend, package manager, layout, and test runner unless there is a clear reason to change.

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-package"
version = "0.1.0"
description = "A short description of your package."
readme = "README.md"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest",
    "ruff",
    "mypy",
]

[tool.ruff]
target-version = "py310"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-ra"]
```

The exact `requires-python`, tool target versions, dependency pins, and CI matrix must be chosen from the target
project's support policy.
