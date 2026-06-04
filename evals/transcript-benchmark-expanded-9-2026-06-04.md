# Transcript Benchmark — Expanded 9-Eval Codex Run (2026-06-04)

## Scope

This report records the first expanded 9-eval benchmark run after adding the portable
`mature-automation-repo-preservation` controlled eval.

Raw local outputs are intentionally kept in the ignored workspace:

- `python-best-practices-workspace/codex-expanded-9-20260604/benchmark.json`
- `python-best-practices-workspace/codex-expanded-9-20260604/eval-*/{with_skill,without_skill}/outputs/response.md`
- `python-best-practices-workspace/codex-expanded-9-20260604/eval-*/{with_skill,without_skill}/grading.json`

## Execution

Command:

```bash
python3 scripts/run_benchmark.py --backend codex --iteration-label codex-expanded-9-20260604
```

Environment notes:

- Backend: Codex CLI via `scripts/run_benchmark.py --backend codex`
- Model: default Codex model from the runner, `gpt-5.5`
- Configurations: `with_skill` and `without_skill`
- Run count: 9 evals × 2 configurations = 18 runs
- Command status: all 18 runs exited with status `0`

## Quantitative summary

The grader is substring/assertion based and intentionally simple. Analyst review is still required for semantic passes
that miss an exact expected phrase.

| Eval                                |   With skill |   Baseline | Notes                                                                   |
| :---------------------------------- | -----------: | ---------: | :---------------------------------------------------------------------- |
| greenfield-setup                    | 10/10 (100%) | 8/10 (80%) | Baseline omitted `uv` and the literal word `verification`.              |
| existing-file-review                |    5/7 (71%) |  5/7 (71%) | Both omitted exact `resource` and `wildcard` terms.                     |
| incremental-typing-testing          |    7/9 (78%) |  7/9 (78%) | Both missed exact expected wording around existing tests/inspection.    |
| existing-project-preservation       |   9/9 (100%) | 9/9 (100%) | Both preserved existing project conventions.                            |
| non-python-doc-only                 |   7/7 (100%) | 7/7 (100%) | Non-trigger behavior stayed clean.                                      |
| generic-python-question             |   4/4 (100%) | 4/4 (100%) | Non-trigger behavior stayed clean.                                      |
| typo-in-docstring                   |   7/7 (100%) | 7/7 (100%) | Non-trigger behavior stayed clean.                                      |
| shell-script-question               |   6/6 (100%) | 6/6 (100%) | Non-trigger behavior stayed clean.                                      |
| mature-automation-repo-preservation |   9/10 (90%) | 9/10 (90%) | Both preserved the native gate; exact `optional modernization` missing. |

Aggregate pass rates from `benchmark.json`:

- With skill mean: 0.9325
- Baseline mean: 0.9102
- Delta: +0.0223

Aggregate timing:

- With skill mean: 36.9783 seconds
- Baseline mean: 22.0411 seconds
- Delta: +14.9372 seconds

## Analyst review

### Non-trigger regression check

The expanded run did not reproduce the earlier high-signal non-trigger failure. All four non-trigger cases scored 100%
for both `with_skill` and `without_skill`, with no prohibited skill/trigger machinery in the captured responses.

This supports the earlier non-trigger guidance fix.

### Mature automation case

The new mature automation eval produced the desired preservation-first behavior in both configurations:

- identified the repository as a mature automation/support-code repo;
- named inspected project files, including `AGENTS.md`;
- preserved the native gate: `bash scripts/check-consistency.sh` and `python3 -m pytest tests -q`;
- avoided `uv`, `src/`, package conversion, and native-gate replacement.

The one failed assertion in each configuration is an exact-phrase miss: responses did not contain
`optional modernization`. Semantically, both responses treated modernization as non-required and limited recommendations
to safe incremental improvements. This is not a skill-behavior blocker, but the assertion wording is brittle.

### Remaining benchmark weaknesses

The skill does not consistently outperform baseline on broad best-practice keyword assertions. Several failures are
exact wording misses rather than obvious bad advice, and several baseline responses are already strong.

This means the current benchmark is now useful as a regression suite, especially for non-trigger and mature-repo
preservation behavior, but it is still weak as a measurement of skill-specific lift.

## Recommendation

Do one more narrow eval-quality iteration before asking for Phase 2 qualitative shipping approval:

1. Replace brittle exact-phrase assertions such as `optional modernization`, `resource`, and `wildcard` with checks that
   better reflect the intended behavior, or document them as known false-negative-prone terms.
2. Add a small number of skill-specific assertions that are harder for the baseline to satisfy accidentally, especially
   around preservation-first behavior and scoped recommendations.
3. Rerun only the affected evals after assertion changes, then run the full suite only if those targeted checks change.

No broad skill rewrite is recommended from this run. The important behavior risks tested here — non-trigger leakage and
mature-repo migration pressure — look controlled.
