# Python Best Practices Skill Agent Instructions

This repository is the source checkout for the `python-best-practices` Hermes skill. It builds and evaluates the skill
source under `skill/`; the installed Hermes mirror is only a local runtime copy used for testing.

## Quick Start

Run the structural and fixture readiness gate:

```bash
python3 scripts/run_phase2_checks.py
```

Run fixture tests directly when editing eval fixtures:

```bash
(
  cd evals/fixtures/existing-buggy && python3 -m pytest -q
)
(
  cd evals/fixtures/existing-preserve && python3 -m pytest -q
)
```

Sync the runtime mirror after changing `skill/`:

```bash
python3 scripts/run_phase2_checks.py --sync-installed
```

## Source and Mirror Policy

- Edit `skill/SKILL.md` and `skill/references/*.md` first.
- Treat `/home/sand/.hermes/skills/software-development/python-best-practices` as a runtime mirror, not the canonical
  source.
- Do not publish, package, or install elsewhere without explicit user approval.
- After changing source skill files, sync the mirror with `python3 scripts/run_phase2_checks.py --sync-installed`, then
  rerun the check.

## Phase 2 Boundary

Phase 2 means controlled eval assets and qualitative with-skill vs baseline review. `scripts/run_phase2_checks.py`
verifies structural readiness and fixture smoke tests; it does not claim the qualitative eval review is complete.

## Files to Know

- `skill/SKILL.md`: runtime router and operating contract.
- `skill/references/`: runtime reference files loaded by agents.
- `evals/evals.json`: controlled Phase 2 eval prompts and expectations.
- `evals/fixtures/`: disposable fixture projects for controlled evals.
- `scripts/run_phase2_checks.py`: local readiness gate and mirror checker.
- `README.md`, `plan.md`, `todos.md`: human-facing status and roadmap.

## Testing

Before reporting Phase 2 work complete, run:

```bash
python3 scripts/run_phase2_checks.py --sync-installed
python3 scripts/run_phase2_checks.py
python3 -m compileall -q scripts evals/fixtures
(
  cd evals/fixtures/existing-buggy && python3 -m pytest -q
)
(
  cd evals/fixtures/existing-preserve && python3 -m pytest -q
)
```

If `ruff` is available, also smoke-check the fixtures:

```bash
uvx ruff check evals/fixtures/existing-preserve
uvx ruff check evals/fixtures/existing-buggy || true
```

The buggy fixture is intentionally lint-dirty; its pytest suite should still collect and pass so agents can run tests
while reviewing the deliberately sloppy code.

## Version Policy

- Update `skill/SKILL.md` metadata version only for behavior changes intended to ship in the runtime skill.
- Update `VERSIONS.md` when changing version recommendations in templates.
- Keep README, plan, and todos aligned whenever phase status changes.
