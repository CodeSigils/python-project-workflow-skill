# Phase 2 Qualitative Review — 2026-06-04

## Scope

This is a source-guidance qualitative review, not a benchmark of captured model transcripts. It inspects the skill,
runtime references, controlled eval prompts, and fixtures to judge whether the skill should improve agent behavior
versus a generic baseline.

Validation run during review:

```bash
python3 scripts/run_phase2_checks.py --skip-installed
python3 -m pytest tests -q
```

Result: source-only Phase 2 checks passed and 5 regression tests passed.

## Overall recommendation

Ship with minor follow-up iterations before broader release.

The skill is likely to improve behavior on the high-value triggered evals: greenfield setup, existing-file review,
incremental typing/testing, and existing-project preservation. The main residual risk is over-triggering on generic
Python questions or docs-only tasks, plus a few missing review checklist details.

## Per-eval findings

### greenfield-setup

Baseline risk: medium. A generic agent may scaffold a plausible project but skip inspection, omit version-contract
alignment, or give config without verification.

With-skill expected improvement: high. The skill routes new projects to `pyproject-template.md` and
`project-orientation.md`, names the modern baseline, and requires verification evidence.

Iteration applied: added a CLI greenfield minimum to `pyproject-template.md` covering package layout, console-script
entry point, thin CLI design, and CLI smoke tests.

### existing-file-review

Baseline risk: medium. A generic agent will likely catch mutable defaults and unclosed files but may miss wildcard
imports, late-binding closures, division-by-zero, or verification.

With-skill expected improvement: medium-high. The review checklist and core footguns reinforce correctness, resource
handling, explicit imports, tests, and verification.

Iteration applied: added review checklist items for late-binding closures and empty-input aggregation/division risks.

### incremental-typing-testing

Baseline risk: medium-high. A generic agent may recommend strict MyPy all at once, ignore existing tests, or focus on
annotations without characterization tests.

With-skill expected improvement: high. `lint-format-typing-testing.md` emphasizes project-native commands, staged MyPy
adoption, pytest, existing tests, and verification.

Remaining recommendation: add a future short “bug-fix typing/testing workflow” recipe if real eval transcripts show
agents still skip characterization tests.

### existing-project-preservation

Baseline risk: high. A generic agent may push uv, Ruff, strict MyPy, or `src/` layout onto a coherent existing
toolchain.

With-skill expected improvement: high. The skill repeatedly says to inspect first and preserve coherent local
conventions.

Iterations applied:

- Softened lockfile guidance in `review-checklist.md` from mandatory lockfile presence to explicit
  application-vs-library policy.
- Added explicit project-orientation warning not to force greenfield conventions onto coherent existing projects.

### non-python-doc-only

Baseline risk: low-medium. A generic agent may over-discuss Python tooling for a docs-only task.

With-skill expected improvement: low but useful. The skill now more explicitly says docs-only changes should not trigger
unless they change Python workflow/conventions.

Iteration applied: clarified non-trigger language in `skill/SKILL.md`.

### generic-python-question

Baseline risk: low. A generic agent usually answers correctly; the risk is unnecessary repo inspection or tooling
advice.

With-skill expected improvement: only if the skill does not trigger.

Iteration applied: added explicit non-trigger language for general Python concept questions unless the user asks to
apply the concept to project code.

## Remaining recommendations

1. Run a transcript-based with-skill vs baseline benchmark for the six controlled prompts.
2. If transcript review shows weak CLI scaffolds, promote the CLI greenfield subsection into a dedicated `cli.md`
   reference.
3. If transcript review shows weak typing/testing changes, add a concise characterization-test workflow to
   `lint-format-typing-testing.md`.
4. Add the mature `/home/sand/projects/ai-project-governance` dogfood eval only after controlled transcript review.
