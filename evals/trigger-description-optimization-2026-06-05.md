# Phase 3 Trigger Description Optimization — 2026-06-05

## Status

Phase 3 trigger-description optimization is complete after user approval of the 20-query trigger/near-miss eval set.

## Selected description

```text
Use for changing or reviewing Python project code, packaging, typing, tests, CI, or tooling; inspect first, not concept-only Q&A.
```

## Candidate review

| Candidate | Description                                                                                                                                                      | Decision                                                                                                                                               |
| :-------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Current   | An adaptive workflow for working on Python projects. Inspect first, then advise.                                                                                 | Rejected: too generic; weakly names the actual trigger surface.                                                                                        |
| A         | Use for Python project implementation, refactor, review, packaging, testing, typing, and tooling; inspect repo conventions first.                                | Rejected: good trigger coverage, but does not explicitly protect concept-only near misses.                                                             |
| B         | Python project code and tooling work: inspect repo conventions, preserve existing workflows, then guide implementation, review, packaging, typing, tests, or CI. | Rejected: strong preservation wording, but slightly less direct about excluding concept-only questions.                                                |
| Selected  | Use for changing or reviewing Python project code, packaging, typing, tests, CI, or tooling; inspect first, not concept-only Q&A.                                | Selected: names project-code/tooling work, includes packaging/typing/tests/CI, keeps inspect-first behavior, and explicitly excludes concept-only Q&A. |

## Eval boundary reviewed

The approved eval set contains 20 prompts:

- 10 should-trigger Python project-work prompts.
- 10 should-not-trigger near misses covering general Python concepts, docs-only edits, bash/git/JSON/frontend tooling,
  Hermes usage, FastAPI concept explanation, and decorator explanation.

The selected description is intentionally narrower than “Python best practices” so generic Python explanations and tiny
text/documentation edits do not attract the runtime skill.

## Files updated

- `skill/SKILL.md` frontmatter `description:` updated.
- `skill/SKILL.md` version bumped from `1.2.4` to `1.2.5` because trigger behavior changed.
- `evals/trigger-description-evals.json` marked `optimization-complete` and records `selected_description`.
- Live project docs updated to keep phase/status claims aligned.
