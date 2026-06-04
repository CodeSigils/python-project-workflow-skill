# Python Best Practices Skill Agent Instructions

**Last verified:** 2026-06-04

This repository is the source checkout for the `python-best-practices` Hermes skill. It builds and evaluates the skill
source under `skill/`; the installed Hermes mirror is only a local runtime copy used for testing.

## Current Status

Phase 2 controlled eval assets, fixtures, structural checks, source-guidance review, benchmark runner, Codex non-trigger
rerun evidence, mature-repo dogfood evidence, and runtime mature-repo preservation guidance exist. Phase 3 description
optimization and Phase 4 user shipping/publishing readiness remain future work unless the user explicitly authorizes
them.

## Orientation Contract — BLOCKING

At session start, agents MUST read this file plus `README.md`, `plan.md`, `todos.md`, and the relevant validation
scripts before making status, phase, shipping, or readiness claims. Scripts are machine truth; prose is a guide that
must be kept aligned with executable checks.

## Quick Start

Run the structural and fixture readiness gate:

```bash
python3 scripts/run_phase2_checks.py
```

Run fixture tests directly when editing eval fixtures:

```bash
python3 -m pytest tests -q
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

## Source, Mirror, and Shipping Policy — BLOCKING

- Edit `skill/SKILL.md` and `skill/references/*.md` first.
- Treat `skill/` as the canonical runtime payload and directory-as-boundary shipping artifact.
- Treat `/home/sand/.hermes/skills/software-development/python-best-practices` as a runtime mirror, not the canonical
  source.
- Repository-only assets (`README.md`, `plan.md`, `todos.md`, `research/`, `references/`, `evals/`, `tests/`,
  `.github/`, workspace outputs, and local session state) must not be described as installed runtime payload.
- Do not publish, package, install elsewhere, sync to another Hermes profile, push, tag, or release without explicit
  user approval for that side effect.
- After changing source skill files, sync the mirror with `python3 scripts/run_phase2_checks.py --sync-installed`, then
  rerun the check.

## Phase and User-Shipping Guard — BLOCKING

- Phase 2 completion requires benchmark evidence plus explicit user qualitative approval (`ship it`).
- Phase 3 optimizes trigger description only after behavior is stable.
- Phase 4 is the user-shipping and optional publishing phase. Before claiming shipped/readiness, verify the source
  skill, installed mirror, fresh-session trigger behavior, and packaging boundary.
- A local mirror passing checks is not the same thing as publishing, hub contribution, cross-profile sync, or user
  handoff.

## Drift and Stale Information Contract — BLOCKING

When behavior, commands, paths, validation policy, phase status, shipping boundary, install payload, or readiness claims
change, agents MUST update every affected source of truth in the same change. Check at least:

1. `AGENTS.md` — repo-local maintenance contract.
2. `README.md` — human-facing status and file inventory.
3. `plan.md` — phase roadmap, outputs, verification, and key decisions.
4. `todos.md` — active task state.
5. `skill/SKILL.md` and `skill/references/` — runtime behavior and payload.
6. `scripts/run_phase2_checks.py` and tests — machine-checkable guard coverage.
7. `evals/evals.json` and fixture files — behavior expectations.
8. Installed mirror under `/home/sand/.hermes/skills/software-development/python-best-practices` when runtime payload
   changes.

Agents MUST NOT leave stale transitional commands, old phase claims, unsupported shipping-readiness claims,
runtime/source boundary confusion, or unverified benchmark assertions in live docs.

Severity:

| Level    | Meaning                                                                                          | Agent behavior                 |
| :------- | :----------------------------------------------------------------------------------------------- | :----------------------------- |
| BLOCKING | false status, stale commands, broken checks, payload-boundary drift, or unauthorized side effect | fix before reporting complete  |
| WARNING  | incomplete context or ambiguous wording near touched files                                       | fix when touching nearby files |
| INFO     | historical notes explicitly marked as historical                                                 | preserve with context          |

## Generated State Guard — BLOCKING

Canonical docs must not contain generated session state, OpenCode/OpenMemory context blocks, auto-injected comments,
activity logs, or transient summaries. Keep scratch/session artifacts in ignored workspace locations, not in
`AGENTS.md`, `README.md`, `plan.md`, `todos.md`, or runtime skill files.

## Phase 2 Boundary

Phase 2 means controlled eval assets and qualitative with-skill vs baseline review. `scripts/run_phase2_checks.py`
verifies structural readiness and fixture smoke tests; it does not claim the qualitative eval review is complete.

## Files to Know

- `skill/SKILL.md`: runtime router and operating contract.
- `skill/references/`: runtime reference files loaded by agents.
- `evals/evals.json`: controlled Phase 2 eval prompts and expectations.
- `evals/fixtures/`: disposable fixture projects for controlled evals.
- `scripts/run_phase2_checks.py`: local readiness gate and exact mirror/repo guard checker.
- `README.md`, `plan.md`, `todos.md`: human-facing status and roadmap.

## Testing

Before reporting Phase 2 or shipping-readiness work complete, run:

```bash
python3 scripts/run_phase2_checks.py --sync-installed
python3 scripts/run_phase2_checks.py
python3 -m pytest tests -q
python3 -m compileall -q scripts evals/fixtures tests
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

For CI or portable source-only validation, use `python3 scripts/run_phase2_checks.py --skip-installed`; CI runners do
not have the local Hermes installed-skill mirror.

## Version Policy

- Update `skill/SKILL.md` metadata version only for behavior changes intended to ship in the runtime skill.
- Update `VERSIONS.md` when changing version recommendations in templates.
- Keep README, plan, and todos aligned whenever phase status changes.
