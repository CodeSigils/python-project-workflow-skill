# Mature Repository Preservation

Use this reference when reviewing an established repository that contains Python but is not clearly a greenfield Python
package.

## Core lesson

A repository can contain meaningful Python automation without needing to become a packaged Python project. Do not treat
the presence of `*.py` or `tests/*.py` as automatic justification for adding `pyproject.toml`, `src/`, `uv`, Ruff, MyPy,
or packaging metadata.

## Inspection pattern

1. Check worktree safety first:
   - `git status --short --branch`
   - If dirty, preserve existing changes. Do not edit, stage, commit, or run destructive generators unless the user
     explicitly includes those files in scope.
2. Identify whether Python is the product or supporting automation:
   - Packaging signals: `pyproject.toml`, `setup.py`, `setup.cfg`, package source tree, distribution docs.
   - Automation signals: `scripts/*.py`, generator tools, repository checkers, tests for repo-maintenance scripts.
3. Read project-local agent or governance files before advising:
   - `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, README, repo-specific check scripts.
4. Prefer project-native gates before generic Python gates:
   - custom consistency scripts, Make targets, tox/nox, CI workflow commands, then pytest/compileall when appropriate.
5. Report optional modernization separately from blockers.

## Preservation-first guidance

Good recommendations:

- "The native gate is `bash scripts/check-consistency.sh`; keep using it as the commit gate."
- "Python here appears to support repository automation, so adding packaging metadata is optional, not required."
- "If you want centralized tool config later, introduce it as an explicit modernization task."
- "Given the dirty worktree, I reviewed read-only and did not modify target files."

Avoid:

- Replacing a coherent governance/checker workflow with the greenfield baseline.
- Adding `pyproject.toml` just for aesthetics.
- Recommending lockfile or package-manager migration without a dependency-management problem.
- Treating WARN-level project-native governance findings as Python correctness failures.

## Verification examples

For mature automation repos, useful safe gates often look like:

```bash
bash scripts/check-consistency.sh
python3 -m pytest tests -q
python3 -m compileall -q scripts tests
```

Adjust paths to the live repository. Always report the actual results and any WARN-level findings separately from
failures.
