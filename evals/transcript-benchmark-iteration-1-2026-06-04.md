# Transcript Benchmark — Iteration 1 (2026-06-04)

## Scope

This report records the first transcript-based with-skill vs baseline benchmark for the `python-best-practices` Hermes
skill.

The benchmark used the six controlled prompts that were in `evals/evals.json` at the time of the iteration-1 run and
generated one `with_skill` and one `without_skill` transcript per prompt. The current `evals/evals.json` has since
expanded beyond this historical run.

## Execution notes

- Primary attempt: `delegate_task` with `gpt-5.5`.
- Blocker: delegation hit HTTP 429 usage-limit errors after the first partial batch.
- Fallback used for complete run: `opencode run --model opencode/big-pickle`.
- Inputs were reset from `evals/fixtures/` before the complete fallback run.
- Raw local transcripts and grading files are in the ignored workspace:
  - `python-best-practices-workspace/iteration-1/benchmark.json`
  - `python-best-practices-workspace/iteration-1/benchmark.md`
  - `python-best-practices-workspace/iteration-1/review.html`
  - `python-best-practices-workspace/iteration-1/eval-*/{with_skill,without_skill}/outputs/response.md`

The ignored workspace preserves raw evidence locally without committing model-generated transcript noise into the source
repository.

## Quantitative summary

The current grader is assertion-oriented and intentionally simple. It checks expected inclusions/exclusions with limited
synonym handling, so analyst review is still required for borderline cases.

| Eval                          |   With skill |     Baseline | Delta |
| ----------------------------- | -----------: | -----------: | ----: |
| greenfield-setup              | 10/10 (100%) | 10/10 (100%) |   +0% |
| existing-file-review          |   7/7 (100%) |   7/7 (100%) |   +0% |
| incremental-typing-testing    |   9/9 (100%) |   9/9 (100%) |   +0% |
| existing-project-preservation |   9/9 (100%) |   9/9 (100%) |   +0% |
| non-python-doc-only           |    2/3 (67%) |   3/3 (100%) |  -33% |
| generic-python-question       |   2/2 (100%) |   2/2 (100%) |   +0% |

Mean pass rate:

- With skill: 92.6%
- Baseline: 98.1%
- Delta: -5.6 percentage points

## Findings

### Finding 1 — Non-trigger responses still expose skill machinery

Severity: high for skill quality, not a repository blocker.

In the `non-python-doc-only` and `generic-python-question` with-skill runs, the response correctly recognized the prompt
as a non-trigger, but still mentioned the skill or trigger decision in the final answer. After a targeted rerun with
strengthened guidance, the generic Python question improved, but the docs-only prompt still exposed skill/trigger
machinery.

This violates the intended user experience for non-trigger prompts: if the skill is loaded accidentally, it should
silently step aside and answer normally.

Change applied in this session:

- `skill/SKILL.md` now says that if the skill is loaded for a non-trigger request, the answer should be normal and
  should not mention the skill, trigger checks, repository inspection, or verification commands.

Remaining concern:

- A targeted rerun improved but did not fully eliminate meta-language. The skill may need an even more prominent
  non-trigger rule near the response style section, or the benchmark harness may need a less artificial with-skill
  prompt that does not repeatedly say “skill under test.”

### Finding 2 — The baseline can already satisfy many fixture expectations

The current fixture assertions are mostly best-practice keywords that a competent baseline model can hit without the
skill. That makes the benchmark weak for measuring skill-specific improvement.

Recommended next improvement:

- Add expectations that test skill-specific discipline, especially:
  - preserves existing toolchains without migration pressure;
  - avoids source-layout/package-manager churn in coherent projects;
  - silently no-ops for non-trigger prompts;
  - names concrete project files inspected;
  - keeps recommendations scoped to the user's requested change.

### Finding 3 — The transcript harness is still local and ad hoc

The complete run used a local ignored script in `python-best-practices-workspace/run_opencode_iteration.py`, not a
committed reusable eval runner.

Recommended next improvement:

- Promote the harness into `scripts/` once its model/provider assumptions are settled.
- Add an explicit completeness check for degenerate outputs such as “waiting for context-gathering completion.”
- Keep raw transcripts in the ignored workspace, but commit concise summary reports under `evals/`.

## Next recommendation

The next best step is to strengthen the non-trigger guidance and benchmark assertions, then rerun only the non-trigger
prompts before running the full suite again.
