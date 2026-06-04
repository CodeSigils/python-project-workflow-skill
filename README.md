# Python Best Practices Hermes Skill

Build a Hermes agent skill that helps LLM agents work on Python projects safely and idiomatically.

The current strategy is adaptive rather than encyclopedic: the skill should inspect a live repository first, preserve
coherent local conventions, then apply modern Python defaults only when they fit the project state.

Preferred greenfield baseline:

```text
uv + ruff + mypy + pytest + pyproject.toml/PEP 621 + src/ layout + Google-style docstrings
```

Those are defaults, not mandates. Existing projects may already use Poetry, Hatch, tox, nox, pixi, conda, Black, isort,
Flake8, Pylint, Pyright, unittest, or framework-specific workflows. The skill should discover those choices before
recommending change.

## Project Status

**Phase 2: Test & Iterate.** Phase 0 research was corrected and revalidated on 2026-06-04, Phase 1 skill draft is
complete, and controlled Phase 2 eval prompts, fixtures, structural validation, source-guidance qualitative review,
benchmark runner, and Codex non-trigger rerun evidence now exist. The main remaining Phase 2 work is user qualitative
review/feedback and the later mature-repo dogfood pass.

The current implementation includes:

- `skill/SKILL.md` (router and operating contract)
- `skill/references/project-orientation.md`
- `skill/references/pyproject-template.md`
- `skill/references/lint-format-typing-testing.md`
- `skill/references/review-checklist.md`

## Research Integration

When deeper web research would help, the skill may suggest installing or loading the **Scrapling** Hermes skill. If the
user does not want to install/load that skill, continue with another verified source when possible.

## Additional Documentation

- `VERSIONS.md` - Tracks the rationale behind version choices in templates and recommendations
- `CONTRIBUTING.md` - Local development loop, validation commands, and CI expectations
- `AGENTS.md` - Agent instructions for this skill source checkout
- `scripts/run_phase2_checks.py` - Phase 2 structural, fixture, repo-guard, and installed-mirror validation
- `scripts/run_benchmark.py` - Controlled eval benchmark runner with OpenCode and Codex backend support
- `tests/test_run_phase2_checks.py` - Regression tests for validation-script negative paths
- `tests/test_run_benchmark.py` - Regression tests for benchmark grading/output behavior
- `.github/workflows/ci.yml` - Portable source-only validation for GitHub Actions
- `evals/evals.json` - Controlled Phase 2 eval prompts
- `evals/phase2-qualitative-review-2026-06-04.md` - Source-guidance qualitative review and iteration notes
- `evals/transcript-benchmark-iteration-1-2026-06-04.md` - First transcript benchmark summary and findings
- `research/tooling-version-snapshot-2026-06-04.md` - Live GitHub/PyPI snapshot for Phase 0 revalidation
- `research/code-extraction/best-practices.md` - Code extraction and analysis best practices

The tightening has been applied (early-exit guard, eval assertion upgrades, collapsed Orientation Checklist,
promoted benchmark runner, Codex backend support, command-status/filesystem-change grading, fixture-symbol validation,
repo guard checks, and explicit user-shipping boundary guidance). The latest Codex non-trigger benchmark passed in both
configurations for all four non-trigger prompts:
`python-best-practices-workspace/codex-nontrigger-20260604-r2/benchmark.json`.

Shipping boundary: `skill/` is the runtime payload and source of truth. The installed Hermes mirror is a local testing
copy. Packaging, hub contribution, cross-profile sync, push, tag, or release remain explicit user-authorized side
effects, not routine validation steps.

See [`plan.md`](./plan.md) for the phased implementation plan. See [`vision.md`](./vision.md) for the long-term
direction. See [`todos.md`](./todos.md) for active task tracking. See
[`research/cross-ecosystem-skill-strategy.md`](./research/cross-ecosystem-skill-strategy.md) for the current strategy.
See [`references/`](./references/) for authoritative sources.

## Strategy Summary

The skill should operate as:

```text
ORIENT → CLASSIFY → LOAD FOCUSED REFERENCE → ADVISE/EDIT → VERIFY → REPORT
```

Core rules:

1. Inspect project files and repo-local agent instructions before advising.
2. Prefer project-native commands over generic commands.
3. Use the greenfield baseline only for new or incoherent projects.
4. Keep `SKILL.md` concise; move detailed guidance into scoped reference files.
5. Report verification evidence and skipped checks honestly.
6. Treat mature repositories as preservation-first targets, not migration targets.

## Layout

```text
python-best-practices-skill/
├── README.md          # Project overview (this file)
├── AGENTS.md          # Agent instructions for this source checkout
├── CONTRIBUTING.md    # Local development and validation workflow
├── .gitignore         # Generated cache/build artifact ignores
├── .github/workflows/ # Portable CI validation
├── plan.md            # Phased implementation plan
├── vision.md          # Long-term vision / deferred ideas
├── todos.md           # Current task tracking
├── VERSIONS.md        # Version choices rationale
├── scripts/           # Local validation and benchmark scripts
│   ├── run_benchmark.py
│   └── run_phase2_checks.py
├── tests/             # Regression tests for validation and benchmark scripts
│   ├── test_run_benchmark.py
│   └── test_run_phase2_checks.py
├── evals/             # Controlled Phase 2 eval prompts and fixtures
│   ├── evals.json
│   └── fixtures/
├── research/          # Evidence, comparisons, and design rationale
│   ├── README.md
│   ├── cross-ecosystem-agent-instructions.md
│   ├── cross-ecosystem-skill-strategy.md
│   ├── hermes-skill-patterns.md
│   ├── tooling-version-snapshot-2026-06-04.md
│   ├── requirements-txt-role.md
│   └── code-extraction/
│       └── best-practices.md  # Code extraction and analysis best practices
├── references/        # Authoritative source links and distilled planning references
│   ├── README.md      # Source index with URLs
│   └── research-evidence.md
└── skill/             # The skill implementation (Phase 1+)
    ├── SKILL.md       # Router and operating contract
    └── references/    # Focused runtime reference docs
        ├── project-orientation.md
        ├── pyproject-template.md
        ├── lint-format-typing-testing.md
        └── review-checklist.md
```
