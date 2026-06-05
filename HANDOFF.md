# Phase 4 Handoff: Python Best Practices Hermes Skill

Handoff date: 2026-06-05
Source commit: 56dc60d

## What the Skill Does

The `python-best-practices` Hermes skill helps LLM agents work on Python projects
safely, idiomatically, and with evidence-backed tooling choices. It is an adaptive
workflow (ORIENT -> CLASSIFY -> LOAD FOCUSED REFERENCE -> ADVISE/EDIT -> VERIFY ->
REPORT), not a Python encyclopedia.

Trigger description (optimized in Phase 3):
> Use for changing or reviewing Python project code, packaging, typing, tests, CI,
> or tooling; inspect first, not concept-only Q&A.

## Install / Runtime Boundary

| Area                | Path                                                                              |
| :------------------ | :-------------------------------------------------------------------------------- |
| Canonical source    | `skill/` directory in this repository                                             |
| Installed mirror    | `~/.hermes/skills/software-development/python-best-practices`                     |
| Sync command        | `python3 scripts/run_phase2_checks.py --sync-installed`                           |
| Source-only check   | `python3 scripts/run_phase2_checks.py --skip-installed`                           |

The repository checkout also contains `evals/`, `tests/`, `research/`, `references/`,
`scripts/`, workspace output, and documentation — these are repository-only assets,
not runtime payload.

## Verification Evidence

All checks pass as of handoff:

- `scripts/run_phase2_checks.py --sync-installed`: PASS
- `scripts/run_phase2_checks.py` (full gate): PASS
- `scripts/run_phase2_checks.py --skip-installed`: PASS
- `python3 -m pytest tests -q`: 37 passed
- All fixture test suites (existing-buggy, existing-preserve, mature-automation-repo): PASS
- `python3 -m compileall -q scripts evals/fixtures tests`: PASS
- `uvx ruff check scripts tests`: PASS
- `diff -qr skill ~/.hermes/skills/software-development/python-best-practices`: no drift
- Phase 3 trigger eval set: 20 prompts (10 should-trigger, 10 should-not-trigger), status: optimization-complete
- Phase 3 decision report: `evals/trigger-description-optimization-2026-06-05.md`
- Benchmark evidence: `python-best-practices-workspace/` (Codex 9-eval expanded, polish incremental)
- Dogfood evidence: `evals/mature-repo-dogfood-ai-project-governance-2026-06-04.md`
- `hermes skills list | grep python-best-practices`: found, local, enabled
- `skill_view python-best-practices`: version 1.2.5, correct description, all references linked

## Fresh-Session Trigger Verification

The installed mirror is synced. The skill is discoverable and enabled in the current
Hermes profile. To verify trigger behavior in a truly fresh session:

1. Start a new Hermes session with `hermes new`
2. Send a Python prompt that should trigger (e.g., "review this Python file")
3. Verify the skill loads and references are available
4. Send a near-miss prompt (e.g., "what is a Python list comprehension")
5. Verify the skill does not trigger and you get a plain answer

Trigger eval set at `evals/trigger-description-evals.json` has 20 pre-written prompts
for systematic testing.

## Known Limits

- Evaluated with Codex backend (OpenCode CLI). Other backends may trigger differently.
- Framework-specific guidance (Django, FastAPI, Flask) is deferred.
- Scientific Python / conda / pixi guidance is deferred.
- Security scanning (bandit, pip-audit) is deferred.
- No automated migration tooling for legacy projects.

## Next Command

```bash
# To verify everything is working in a fresh session:
hermes new
# Then test with:
#   "Review main.py for typing issues"  (should trigger)
#   "What is a decorator in Python?"     (should not trigger)
```

## License

MIT — see `LICENSE` in the repository root.
