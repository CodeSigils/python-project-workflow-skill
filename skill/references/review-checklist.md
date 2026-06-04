# Python Review Checklist

A practical checklist for reviewing Python code and projects. Focus on correctness, safety, and maintainability.

## Correctness & Safety

- [ ] No bare `except:` clauses — catch specific exceptions.
- [ ] No mutable default arguments (e.g., `def foo(items=[]):`).
- [ ] No late-binding closure bugs in loops; capture loop variables intentionally.
- [ ] Empty inputs are handled before division, indexing, `min`/`max`, or aggregation assumptions.
- [ ] Resources (files, sockets, etc.) are properly closed, preferably with context managers (`with`).
- [ ] No `import *` — explicit imports are preferred.
- [ ] No `eval()` or `exec()` unless absolutely necessary and input is trusted.
- [ ] No `pickle.load()` of untrusted data.
- [ ] No hardcoded secrets (passwords, API keys) — use environment variables or a secrets manager.
- [ ] No SQL injection vulnerabilities — use parameterized queries.
- [ ] No command injection vulnerabilities — use `subprocess` with `args` list and avoid `shell=True`.
- [ ] Path traversal checks: validate user input before joining with base directories.
- [ ] Use `secrets` module for generating random tokens/passwords, not `random`.
- [ ] Timeouts on network calls and external processes.
- [ ] Check for integer overflow in performance-critical code (though rare in Python).
- [ ] Use `os.path` or `pathlib` for path manipulation, not string concatenation.

## Typing & Static Analysis

- [ ] Public functions and classes have type hints.
- [ ] No `Any` in public signatures without justification.
- [ ] Complex return types use `TypedDict`, `NamedTuple`, or dataclasses for clarity.
- [ ] Type hints are accurate and up-to-date with the code.
- [ ] No `# type: ignore` comments without a ticket or explanation.
- [ ] Consider enabling `disallow_untyped_defs` gradually in existing projects.
- [ ] MyPy configuration is present and aligned with the project's Python version.
- [ ] Consider using `pyright` or `pyre` in addition to MyPy for faster feedback.

## Testing

- [ ] Tests are present for critical paths and bug fixes.
- [ ] Test names are descriptive and follow a convention (e.g., `test_<unit>_<scenario>`).
- [ ] Tests are independent and do not rely on external state unless using fixtures.
- [ ] Use `pytest` fixtures for setup/teardown instead of repetitive code.
- [ ] Mock external dependencies (network, database, etc.) in unit tests.
- [ ] Integration tests cover critical user journeys.
- [ ] Property-based testing (e.g., with `hypothesis`) is considered for complex logic.
- [ ] Tests run quickly in CI; slow tests are marked appropriately.
- [ ] Test coverage is measured, but 100% is not the goal — focus on critical paths.
- [ ] No flaky tests; if present, they are quarantined or fixed.
- [ ] Test output is readable and actionable on failure.

## Dependencies & Security

- [ ] Dependencies are up-to-date and vetted for known vulnerabilities (use `pip-audit`, `safety`, or `dependabot`).
- [ ] No unnecessary dependencies; each dependency justifies its cost.
- [ ] Dependency licenses are compatible with the project's intended use.
- [ ] Lockfile policy is explicit and appropriate for the project type: usually committed for applications, more nuanced
      for reusable libraries.
- [ ] Vulnerability scanning is part of CI (if the project is public or handles sensitive data).
- [ ] Consider using `pip-audit` or `safety` in CI to detect vulnerable dependencies.
- [ ] Avoid pinned dependencies with known vulnerabilities — update to a safe version.

## Documentation & Conventions

- [ ] Public functions and classes have docstrings (Google, NumPy, or Sphinx style).
- [ ] Docstrings are kept up-to-date with signature changes.
- [ ] README includes installation, usage, and contribution instructions.
- [ ] CONTRIBUTING.md or DEVELOPMENT.md exists for contributors.
- [ ] Code follows a consistent style (PEP 8, with project-specific exceptions documented).
- [ ] Linting (e.g., Ruff) is run in CI and failures block merging.
- [ ] Formatting (e.g., Ruff formatter) is applied consistently.
- [ ] Import sections are grouped and sorted (standard library, third-party, local).
- [ ] No commented-out code or large blocks of dead code.
- [ ] Version control history is meaningful (atomic commits, good messages).
- [ ] Changelog is maintained (e.g., using `towncrier` or `keepachangelog`).

## Python-Version Compatibility (Critical)

- [ ] The project declares a `requires-python` range in `pyproject.toml` or `setup.py`.
- [ ] The declared range is realistic and tested in CI.
- [ ] Code does not use syntax newer than the declared minimum (e.g., no `match`/`case` in a 3.8 project).
- [ ] Tool configurations (Ruff `target-version`, MyPy `python_version`) align with `requires-python`.
- [ ] CI tests all supported minor versions in the declared range (or at least the extremes).
- [ ] Dependencies support the declared Python floor (check their `requires-python`).
- [ ] README and documentation match the declared `requires-python`.
- [ ] If using backports (e.g., `typing_extensions`), they are used only when needed for older Python support.
- [ ] No accidental use of stdlib modules that were added in newer Python versions (e.g., `tomllib` in 3.11+, `zoneinfo`
      in 3.9+).
- [ ] Consider adding a `tox` or `nox` configuration to test multiple Python versions if missing.

## Project Maintenance

- [ ] Issue tracker is used and triaged regularly.
- [ ] Pull requests are reviewed before merging.
- [ ] Releases are tagged and documented.
- [ ] The project has a CONTRIBUTING.md guide.
- [ ] Consider adding a `CODE_OF_CONDUCT.md`.
- [ ] Security policy (SECURITY.md) is present if the project is public.
- [ ] Dependabot or similar is enabled for automatic dependency updates.
- [ ] CI/CD pipeline is present and green on the default branch.
- [ ] Release process is automated or well-documented.
- [ ] Consider adding a `RELEASING.md` for maintainers.

## How to Use This Checklist

- Use it as a guide during code reviews, not as a rigid pass/fail gate.
- Focus on the items that are most relevant to the change or project state.
- For existing projects, prioritize fixing safety and correctness issues over style.
- When in doubt, ask: "Does this change make the project safer, more correct, or more maintainable?"
- Track recurring issues and consider adding project-specific rules to your linter or CI.
