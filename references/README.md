# Reference Sources Index

Authoritative sources that inform the Python best practices skill.

Star counts were rechecked on 2026-06-04 using the GitHub API. Treat them as popularity signals only; operational
guidance should prefer PEPs, PyPA specifications, and upstream tool documentation.

## Tools (Modern Stack)

| Tool       | GitHub                                                    | Stars checked 2026-06-04 | Role                                                                      |
| :--------- | :-------------------------------------------------------- | -----------------------: | :------------------------------------------------------------------------ |
| **uv**     | [astral-sh/uv](https://github.com/astral-sh/uv)           |                   85,953 | Package/project manager, virtualenv, lockfile, tool runner                |
| **ruff**   | [astral-sh/ruff](https://github.com/astral-sh/ruff)       |                   47,800 | Linter, import sorter, formatter                                          |
| **mypy**   | [python/mypy](https://github.com/python/mypy)             |                   20,457 | Static type checker                                                       |
| **pytest** | [pytest-dev/pytest](https://github.com/pytest-dev/pytest) |                   13,887 | Testing framework                                                         |
| **isort**  | [PyCQA/isort](https://github.com/PyCQA/isort)             |                    6,944 | Existing-project import sorter; Ruff `I` rules are the greenfield default |

## Style, Packaging, and Tool Documentation

| Resource                             | URL                                                                      | Use in this project                                                                    |
| :----------------------------------- | :----------------------------------------------------------------------- | :------------------------------------------------------------------------------------- |
| PEP 8                                | https://peps.python.org/pep-0008/                                        | Official Python style guide                                                            |
| PEP 257                              | https://peps.python.org/pep-0257/                                        | Docstring conventions                                                                  |
| PEP 484                              | https://peps.python.org/pep-0484/                                        | Type hints                                                                             |
| PEP 518                              | https://peps.python.org/pep-0518/                                        | `[build-system]` in `pyproject.toml`                                                   |
| PEP 621                              | https://peps.python.org/pep-0621/                                        | `[project]` metadata in `pyproject.toml`                                               |
| PEP 660                              | https://peps.python.org/pep-0660/                                        | Editable installs for pyproject-based builds                                           |
| Python Packaging User Guide          | https://packaging.python.org/                                            | Operational PyPA packaging guidance                                                    |
| PyPA specifications                  | https://packaging.python.org/en/latest/specifications/                   | Current packaging specs; prefer these over historical PEP text for operational details |
| PyPA packaging tutorial              | https://packaging.python.org/en/latest/tutorials/packaging-projects/     | Baseline project/package structure                                                     |
| PyPA Sample Project                  | https://github.com/pypa/sampleproject                                    | Concrete reference project structure                                                   |
| uv docs                              | https://docs.astral.sh/uv/                                               | Modern project/dependency/tool execution workflows                                     |
| Ruff docs                            | https://docs.astral.sh/ruff/                                             | Lint, import-sort, and format behavior                                                 |
| mypy docs                            | https://mypy.readthedocs.io/                                             | Static typing and incremental adoption                                                 |
| pytest good practices                | https://docs.pytest.org/en/stable/explanation/goodpractices.html         | Test layout and import-mode guidance                                                   |
| Google Python Style Guide            | https://google.github.io/styleguide/pyguide.html                         | General-purpose docstring/style default, with local-convention caveats                 |
| Hitchhiker's Guide to Python         | https://docs.python-guide.org/                                           | Long-running community best-practices reference                                        |
| GitHub Python.gitignore              | https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore | Primary maintained checklist for Python ignore patterns                                |
| gitignore.org/Toptal Python template | https://www.toptal.com/developers/gitignore/api/python                   | Secondary generated checklist for Python ignore patterns                               |

## Distilled defaults

1. Inspect the target repository first: `pyproject.toml`, legacy config files, lockfiles, CI, Makefile/justfile,
   nox/tox/hatch/pixi/poetry, tests, source layout, and repo-local agent instructions.
2. For greenfield or incoherent projects, prefer
   `uv + ruff + mypy + pytest + pyproject.toml/PEP 621 + src/ layout + Google-style docstrings`.
3. For coherent existing projects, preserve local tools and improve within them unless the user explicitly asks for
   modernization.
4. Treat `requires-python`, tool target versions, dependency floors, and CI matrices as one compatibility contract.
5. Use Ruff for greenfield lint/import-sort/format, but do not enable maximal rule sets or unsafe fixes without staged
   adoption.
6. Use mypy for type checking, with strict settings for greenfield/library code and incremental adoption for legacy
   code.
7. Use pytest as the default for new projects, but preserve existing unittest/tox/nox/hatch/pixi/framework runners when
   coherent.
8. Prefer PyPA specifications and upstream docs over popularity, blog posts, or public agent-rule examples.
9. Review `.gitignore` against maintained Python templates, but preserve project-specific rules and avoid wholesale
   replacement.
