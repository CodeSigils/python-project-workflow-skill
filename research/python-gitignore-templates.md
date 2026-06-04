# Python .gitignore Template Research

Research checked on 2026-06-04. Use this as evidence for the `python-best-practices` skill's version-control hygiene
guidance.

## Sources checked

| Source                                    | URL                                                                      | Observed behavior                                                        | Use in the skill                                                                              |
| :---------------------------------------- | :----------------------------------------------------------------------- | :----------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------- |
| GitHub `github/gitignore` Python template | https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore | Plain-text maintained Python template. Observed 220 lines on 2026-06-04. | Primary checklist for Python ignore patterns.                                                 |
| GitHub web view                           | https://github.com/github/gitignore/blob/main/Python.gitignore           | HTML view of the same maintained template.                               | Human-review link. Prefer the raw URL for automated checks.                                   |
| gitignore.org / Toptal generator          | https://www.toptal.com/developers/gitignore/api/python                   | Plain-text generated Python template. Observed 176 lines on 2026-06-04.  | Secondary comparison source, especially when combining templates.                             |
| gitignore.org Python page                 | https://gitignore.org/Python                                             | HTML page rather than a raw template.                                    | Mention only as the discoverability entry point; do not treat as the machine-readable source. |

## Evidence summary

The official GitHub template and the gitignore.org/Toptal generator overlap on the core Python artifact categories:

- bytecode and optimized files (`__pycache__/`, `*.py[cod]` or GitHub's newer `*.py[codz]`),
- build and distribution outputs (`build/`, `dist/`, `*.egg-info/`, wheels, eggs),
- test and coverage artifacts (`.pytest_cache/`, `.coverage`, `htmlcov/`),
- virtual environments (`.venv/`, `venv/`, `ENV/`, etc.),
- tool caches (`.tox/`, `.nox/`, `.mypy_cache/`, `.ruff_cache/`, `.pytype/`, `.pyre/`),
- local environment files such as `.env`.

The templates are not identical. On 2026-06-04, the GitHub template included `*.py[codz]` and `uv.lock` commentary,
while the Toptal template used `*.py[cod]` and did not mention `uv.lock`. This is a good example of why the skill should
use maintained templates as checklists rather than hard-coding one copied template forever.

## Recommended skill behavior

1. Inspect the target project's existing `.gitignore` before recommending changes.
2. Compare it against the official GitHub Python template first.
3. Use the gitignore.org/Toptal generated Python template as a secondary comparison source.
4. Preserve project-specific ignores, including editor, operating-system, generated-docs, local-database, or deployment
   artifacts.
5. Recommend targeted additions for missing Python-generated artifacts instead of replacing the whole file.
6. Do not automatically ignore lockfiles. For example, GitHub's Python template documents that `uv.lock` may be ignored
   for libraries but generally should be committed for applications. The right choice depends on the target project's
   packaging and deployment policy.
7. Do not remove existing ignore rules unless they are clearly obsolete and the user asked for cleanup.

## Runtime checklist

When reviewing a Python repository, the skill should check whether `.gitignore` covers these common buckets:

- bytecode: `__pycache__/`, `*.py[codz]`, `*$py.class`,
- build/distribution: `build/`, `dist/`, `*.egg-info/`, `*.egg`, `wheels/`,
- test/coverage: `.pytest_cache/`, `.coverage`, `.coverage.*`, `coverage.xml`, `htmlcov/`,
- type/lint/tool caches: `.mypy_cache/`, `.ruff_cache/`, `.pytype/`, `.pyre/`, `.tox/`, `.nox/`, `.hypothesis/`,
- virtual environments: `.venv/`, `venv/`, `env/`, `ENV/`,
- local configuration/secrets: `.env`, `.env.*` when the project does not intentionally version environment examples.

These are review prompts, not a universal mandatory template. Repo-local conventions and deployment policy remain
authoritative.
