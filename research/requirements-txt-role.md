# The Role of requirements.txt in Python Projects

## Overview

`requirements.txt` is a legacy format for specifying Python package dependencies. While modern Python projects
increasingly use `pyproject.toml` (PEP 621) and lockfiles like `uv.lock` or `poetry.lock`, understanding
`requirements.txt` remains important for maintaining existing projects and interfacing with tools that still expect it.

## Best Practices

### 1. When to Use requirements.txt

- **Maintaining compatibility** with older tools or CI systems that expect `requirements.txt`
- **Providing a simple, human-readable list** of pinned dependencies for quick setup
- **Working with platforms** (like Heroku) that historically expected `requirements.txt`
- **Creating environment exports** for reproducibility (though lockfiles are preferred)

### 2. How to Generate requirements.txt

- From `pyproject.toml`: Use tools like `poetry export` or `pip-compile` (from `pip-tools`)
- From a lockfile: `uv pip compile requirements.in -o requirements.txt` or similar
- **Never** generate by hand for complex projects; use a tool that resolves dependencies

### 3. Relationship with Other Files

- `pyproject.toml`: Source of truth for metadata and dependencies (PEP 621)
- `requirements.in`: Input file for `pip-compile` containing direct dependencies (not transitive)
- `requirements.txt`: Output of dependency resolution, containing pinned versions of all transitive dependencies
- `uv.lock` / `poetry.lock` / `Pipfile.lock`: Lockfiles that provide reproducible environments (preferred over
  `requirements.txt`)

### 4. Pitfalls to Avoid

- **Committing both `requirements.txt` and a lockfile** without a clear strategy (can cause confusion)
- **Using `requirements.txt` for development dependencies** without separating them (consider `requirements-dev.txt` or
  extras)
- **Not updating `requirements.txt` when dependencies change** (leads to drift)
- **Pinning overly strictly** (e.g., pinning transitive dependencies that don't need pinning)
- **Mixing formats** (e.g., specifying VCS dependencies in `requirements.txt` without proper syntax)

### 5. Modern Recommendation

For new projects, prefer:

- `pyproject.toml` for declaring dependencies (with version ranges)
- A lockfile (`uv.lock`, `poetry.lock`, etc.) for reproducible builds
- Only generate `requirements.txt` if explicitly needed for legacy tooling

## Integration with Hermes Skill

The Python Best Practices skill should:

1. Inspect for existing `requirements.txt` files and understand their purpose in the project
2. If present, verify that they are consistent with `pyproject.toml` or lockfiles
3. Recommend generating `requirements.txt` from lockfiles if needed for compatibility
4. Suggest moving to `pyproject.toml` + lockfile as the source of truth for new or modernizing projects
5. Note that the skill's verification commands (e.g., `uv sync`) work with lockfiles, not `requirements.txt`

## References

- Pip documentation on requirements.txt: https://pip.pypa.io/en/stable/reference/requirements-file-format/
- Pip-tools documentation: https://github.com/jazzband/pip-tools
- UV documentation on dependency management: https://docs.astral.sh/uv/
- PEPs: PEP 621 (pyproject.toml), PEP 517 (build system), PEP 518 (pyproject.toml build-system section)

Last updated: 2026-06-03
