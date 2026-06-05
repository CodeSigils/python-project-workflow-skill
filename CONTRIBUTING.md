# Contributing

This repository is the source checkout for the `python-best-practices` Hermes skill. The canonical runtime source lives
under `skill/`; the installed Hermes copy is only a local mirror for testing.

## Local development loop

1. Edit source files first:
   - `skill/SKILL.md`
   - `skill/references/*.md`
   - `scripts/run_phase2_checks.py`
   - `tests/*.py`
   - planning/research docs when behavior, phase status, or trigger-eval status changes

2. If you changed runtime skill files, sync the local Hermes mirror:

   ```bash
   python3 scripts/run_phase2_checks.py --sync-installed
   ```

3. Run the local validation gate:

   ```bash
   python3 scripts/run_phase2_checks.py
   python3 -m pytest tests -q
   python3 -m compileall -q scripts evals/fixtures tests
   python3 -m ruff check scripts tests
   ```

4. For portable checks that should not depend on a local Hermes installation, use:

   ```bash
   python3 scripts/run_phase2_checks.py --skip-installed
   ```

## Validation script test hooks

`scripts/run_phase2_checks.py` normally validates this repository and the local installed mirror at
`~/.hermes/skills/software-development/python-best-practices`. Regression tests override those paths with environment
variables:

- `PBP_SKILL_ROOT` — alternate repository root to validate
- `PBP_SKILL_INSTALLED` — alternate installed mirror path

These hooks are intended for tests and local diagnostics. Do not use them to hide stale source files or skip the normal
source checkout validation path.

## CI expectations

The GitHub Actions workflow uses source-only validation because CI runners do not have the developer's local Hermes
skill mirror. The CI gate should stay portable:

```bash
python3 scripts/run_phase2_checks.py --skip-installed
python3 -m pytest tests -q
python3 -m compileall -q scripts evals/fixtures tests
python3 -m ruff check scripts tests
```

## Status updates

Keep live status in these files:

- `README.md` — human-facing current state and next step
- `plan.md` — phase plan and decision summary
- `todos.md` — active task checklist
- `AGENTS.md` — repo-local maintenance contract and phase/shipping guards

When Phase 3 trigger-description work changes, also keep `evals/trigger-description-evals.json` and the validation
script aligned. Do not mark that eval set beyond `draft-for-user-review` until the user approves the prompts.

Do not add one-off implementation summaries as live status documents. Keep live status in `README.md`, `plan.md`, and
`todos.md`; use git history for completed-change records. `scripts/run_phase2_checks.py` enforces that removed summary
files and references to them do not return.
