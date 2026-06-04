# Python Best Practices Hermes Skill

Build a Hermes skill that helps agents work on Python projects safely and idiomatically.

The skill is adaptive rather than encyclopedic: inspect the live repository first, preserve coherent local conventions,
then apply modern Python defaults only when they fit the project state.

Preferred greenfield baseline:

```text
uv + ruff + mypy + pytest + pyproject.toml/PEP 621 + src/ layout + Google-style docstrings
```

Those are defaults, not mandates. Existing projects may already use Poetry, Hatch, tox, nox, pixi, conda, Black, isort,
Flake8, Pylint, Pyright, unittest, or framework-specific workflows. The skill should discover those choices before
recommending change.

## Status at a glance

| Area                                  | Current state                                                                                                                 |
| :------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------- |
| Active phase                          | Phase 2 — Test & Iterate                                                                                                      |
| Runtime skill source                  | `skill/`                                                                                                                      |
| Installed mirror                      | `/home/sand/.hermes/skills/software-development/python-best-practices`                                                        |
| Runtime skill version                 | `1.2.2` in `skill/SKILL.md`                                                                                                   |
| Latest local gate                     | `python3 scripts/run_phase2_checks.py` passes for source plus installed mirror                                                |
| Latest non-trigger benchmark evidence | `python-best-practices-workspace/codex-nontrigger-20260604-r2/benchmark.json`                                                 |
| Latest dogfood evidence               | `evals/mature-repo-dogfood-ai-project-governance-2026-06-04.md`                                                               |
| Not yet complete                      | Expanded 9-eval benchmark rerun, Phase 2 user qualitative approval, Phase 3 trigger-description optimization, Phase 4 handoff |

Phase 0 research was corrected and revalidated on 2026-06-04, Phase 1 skill drafting is complete, and Phase 2 controlled
eval assets now exist. The latest Codex non-trigger rerun has 8 runs and a 1.0 mean pass rate for both `with_skill` and
`without_skill`; it validates that near-miss prompts can be answered without exposing skill machinery.

Phase 2 is still open until the expanded 9-eval suite is rerun and the user gives qualitative approval after reviewing
benchmark and dogfood evidence. A passing local mirror is not a package, hub contribution, release, push, or user
handoff.

## Runtime payload

Shipping boundary: `skill/` is the runtime payload and source of truth. The installed Hermes mirror is only a local
testing copy. Packaging, hub contribution, cross-profile sync, push, tag, or release remain explicit user-authorized
side effects, not routine validation steps.

Only `skill/` is the runtime payload and source of truth for the skill that can be installed or shipped.

Runtime files:

- `skill/SKILL.md` — router and operating contract
- `skill/references/project-orientation.md`
- `skill/references/pyproject-template.md`
- `skill/references/lint-format-typing-testing.md`
- `skill/references/review-checklist.md`
- `skill/references/mature-repo-preservation.md`

Repository-only files such as `README.md`, `plan.md`, `todos.md`, `research/`, `references/`, `evals/`, `tests/`,
`.github/`, and `python-best-practices-workspace/` are development, evaluation, or evidence assets. Do not describe them
as installed runtime payload.

## Quick validation

Run the source-only gate for CI-style validation:

```bash
python3 scripts/run_phase2_checks.py --skip-installed
```

Run the local source-plus-installed-mirror gate:

```bash
python3 scripts/run_phase2_checks.py
```

After changing `skill/`, sync the installed mirror and rerun the gate:

```bash
python3 scripts/run_phase2_checks.py --sync-installed
python3 scripts/run_phase2_checks.py
```

Run the regression suite:

```bash
python3 -m pytest tests -q
python3 -m compileall -q scripts evals/fixtures tests
```

Preview the Codex non-trigger benchmark rerun without spending model calls:

```bash
python3 scripts/run_benchmark.py --dry-run --trigger-filter non-trigger --backend codex --iteration-label review-dry-run
```

## Strategy summary

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
7. For non-trigger prompts, answer directly without exposing skill or trigger-classification machinery.

## Research integration

When deeper web research would help, the skill may suggest installing or loading the **Scrapling** Hermes skill. If the
user does not want to install/load that skill, continue with another verified source when possible.

## Development assets

- `AGENTS.md` — repo-local maintenance contract and source/mirror/shipping guards
- `plan.md` — phase roadmap, verification gates, and key decisions
- `todos.md` — active task tracking
- `VERSIONS.md` — version-choice rationale for templates and recommendations
- `CONTRIBUTING.md` — local development loop and CI expectations
- `scripts/run_phase2_checks.py` — structural, fixture, repo-guard, and exact installed-mirror validation
- `scripts/run_benchmark.py` — controlled eval benchmark runner with OpenCode and Codex backend support
- `tests/test_run_phase2_checks.py` — validation-script regression tests
- `tests/test_run_benchmark.py` — benchmark grading/output regression tests
- `.github/workflows/ci.yml` — portable source-only validation for GitHub Actions
- `evals/evals.json` — 9 controlled Phase 2 eval prompts, including the portable mature-automation preservation fixture
- `evals/phase2-qualitative-review-2026-06-04.md` — source-guidance qualitative review and iteration notes
- `evals/transcript-benchmark-iteration-1-2026-06-04.md` — first transcript benchmark summary and findings
- `evals/mature-repo-dogfood-ai-project-governance-2026-06-04.md` — preservation-first mature-repo dogfood report
- `research/tooling-version-snapshot-2026-06-04.md` — live GitHub/PyPI snapshot for Phase 0 revalidation
- `research/code-extraction/best-practices.md` — code extraction and analysis best practices
- `references/README.md` — authoritative source index
- `references/research-evidence.md` — distilled planning evidence

See [`plan.md`](./plan.md) for the phased implementation plan. See [`vision.md`](./vision.md) for deferred ideas. See
[`research/cross-ecosystem-skill-strategy.md`](./research/cross-ecosystem-skill-strategy.md) for the current strategy.

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
│   ├── evals.json     # 9 controlled eval prompts
│   └── fixtures/
├── research/          # Evidence, comparisons, and design rationale
│   ├── README.md
│   ├── cross-ecosystem-agent-instructions.md
│   ├── cross-ecosystem-skill-strategy.md
│   ├── hermes-skill-patterns.md
│   ├── tooling-version-snapshot-2026-06-04.md
│   ├── python-gitignore-templates.md
│   ├── requirements-txt-role.md
│   └── code-extraction/
│       └── best-practices.md  # Code extraction and analysis best practices
├── references/        # Authoritative source links and distilled planning references
│   ├── README.md
│   └── research-evidence.md
└── skill/             # Runtime skill payload
    ├── SKILL.md
    └── references/
        ├── project-orientation.md
        ├── pyproject-template.md
        ├── lint-format-typing-testing.md
        ├── review-checklist.md
        └── mature-repo-preservation.md
```
