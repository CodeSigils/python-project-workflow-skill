# Python Best Practices Skill Agent Instructions

**Last verified:** 2026-06-05

This repository is the source checkout for the `python-best-practices` Hermes skill. It builds and evaluates the skill
source under `skill/`; the installed Hermes mirror is only a local runtime copy used for testing.

## Current Status

Phase 2 controlled eval assets, fixtures, structural checks, source-guidance review, benchmark runner, Codex non-trigger
rerun evidence, portable mature-automation JSON eval coverage, expanded Codex 9-eval benchmark evidence, mature-repo
dogfood evidence, runtime mature-repo preservation guidance, and benchmark-hardening guidance exist. Phase 2 user
qualitative approval was recorded on 2026-06-05. Phase 3 description optimization is complete; the 20-query trigger eval
set at `evals/trigger-description-evals.json` records the selected frontmatter description and
`evals/trigger-description-optimization-2026-06-05.md` records the decision. Phase 4 handoff is complete as of
2026-06-05: MIT license applied, readiness gates verified, mirror synced, handoff doc at `HANDOFF.md`. Distribution uses
the GitHub tap model documented in `SHIPPING.md`. Official hub contribution remains optional, requiring explicit
approval.

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
- Treat `~/.hermes/skills/software-development/python-best-practices` as a runtime mirror, not the canonical source.
- Repository-only assets (`README.md`, `plan.md`, `todos.md`, `research/`, `references/`, `evals/`, `tests/`,
  `.github/`, workspace outputs, and local session state) must not be described as installed runtime payload.
- Do not publish, package, install elsewhere, sync to another Hermes profile, push, tag, or release without explicit
  user approval for that side effect.
- After changing source skill files, sync the mirror with `python3 scripts/run_phase2_checks.py --sync-installed`, then
  rerun the check.

## Phase and User-Shipping Guard — BLOCKING

- Phase 2 completion required benchmark evidence plus explicit user qualitative approval; that approval was recorded on
  2026-06-05.
- Phase 3 optimizes trigger description only after behavior is stable. Before user approval, keep
  `evals/trigger-description-evals.json` marked as `draft-for-user-review`; after optimization, keep it marked
  `optimization-complete` with `selected_description` recorded.
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
8. Installed mirror under `~/.hermes/skills/software-development/python-best-practices` when runtime payload changes.

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

## Phase Closure Boundaries

Phase 2 means controlled eval assets and qualitative with-skill vs baseline review. `scripts/run_phase2_checks.py`
verifies structural readiness and fixture smoke tests; it does not judge LLM qualitative output. Phase 2 is closed as of
2026-06-05, Phase 3 trigger-description optimization is complete as of 2026-06-05, and Phase 4 handoff is complete as of
2026-06-05. Do not claim packaging, hub contribution, or cross-profile sync without explicit user authorization.

## Files to Know

- `skill/SKILL.md`: runtime router and operating contract.
- `skill/references/`: runtime reference files loaded by agents.
- `evals/evals.json`: controlled Phase 2 eval prompts and expectations, including the portable mature-automation case.
- `evals/trigger-description-evals.json`: Phase 3 trigger/near-miss eval set and selected frontmatter description.
- `evals/trigger-description-optimization-2026-06-05.md`: Phase 3 description optimization decision report.
- `evals/fixtures/`: disposable fixture projects for controlled evals.
- `LICENSE`: MIT license for the repository.
- `HANDOFF.md`: Phase 4 user handoff with verification evidence, shipping boundary, and known limits.
- `SHIPPING.md`: research-grounded shipping strategy, boundary, and update flow.

## Testing

Before reporting Phase 3 or shipping-readiness work complete, run:

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
