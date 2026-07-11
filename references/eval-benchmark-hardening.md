# Eval and Benchmark Hardening for Python Automation Repos

Use this reference when reviewing or modifying Python scripts that run agent evals, benchmarks, fixtures, or quality
gates.

## Durable lesson

Benchmark prose, stderr, and human-readable summaries are not enough. If a run can use fallbacks, retries, skipped
paths, or generated assertions, record the effective behavior in machine-readable output so later review does not
require log archaeology.

## Metadata pattern

When a benchmark runner has configured and fallback execution paths, store both configured and effective values:

- `backend`: the user/configured backend requested for the run.
- `model`: the user/configured model requested for the run.
- `effective_backend`: the backend that actually produced the result, or the fallback that failed last.
- `effective_model`: the model that actually produced the result, or the fallback model that failed last.
- `fallback_reason`: a compact reason that preserves the full fallback path, for example:
  - `opencode_timeout` when the primary OpenCode run timed out and Codex produced the answer.
  - `opencode_timeout_codex_timeout` when OpenCode timed out and the Codex fallback also timed out.

Keep this metadata in every durable run artifact that reviewers will inspect, such as per-sample timing files and
aggregate benchmark JSON.

## Eval assertion quality

Broad string assertions can produce false confidence. Prefer diagnostic assertion groups that are flexible about wording
but specific to the intended behavior.

Good pattern:

```json
{
  "name": "incremental typing/testing rollout",
  "terms": [
    "add tests before changing behavior",
    "start with current tests",
    "stage mypy adoption",
    "then add annotations",
    "small typing/testing steps"
  ]
}
```

Avoid alternatives that are true of almost any answer, such as `small steps`, `then update`, or
`approach it in this order`.

## TDD workflow for runner/eval changes

1. Add or tighten the test first.
2. Run the focused test and confirm it fails for the intended reason.
3. Change the runner/eval fixture minimally.
4. Rerun the focused test.
5. Rerun the project-native full gates.
6. If benchmark output schema changes, update validation checks and negative-path tests so malformed assertion groups
   produce actionable errors.

## Review checklist

- Do machine-readable artifacts identify which backend/model actually produced or failed the response?
- Does a fallback timeout reason preserve the full path rather than naming only the final backend?
- Are assertion alternatives behavior-specific rather than generic planning phrases?
- Are malformed eval schemas rejected with actionable messages?
- Are source/runtime mirrors synchronized only through project-approved commands when runtime payload changed?
