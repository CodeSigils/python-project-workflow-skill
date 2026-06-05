# Plan: Python Best Practices Hermes Skill

## Overview

Build a Hermes agent skill (`python-best-practices`) that helps LLM agents work on Python projects safely,
idiomatically, and with evidence-backed tooling choices.

The skill is not a Python encyclopedia. It is an adaptive workflow:

```text
ORIENT → CLASSIFY → LOAD FOCUSED REFERENCE → ADVISE/EDIT → VERIFY → REPORT
```

The preferred greenfield baseline is:

```text
uv + ruff + mypy + pytest + pyproject.toml/PEP 621 + src/ layout + Google-style docstrings
```

Those are defaults, not mandates. For existing projects, the skill must inspect live configuration and preserve coherent
local conventions unless the user explicitly asks for modernization.

Current strategy source of truth:
[`research/cross-ecosystem-skill-strategy.md`](./research/cross-ecosystem-skill-strategy.md).

## Phases

### Phase 0 — Planning & Research (complete; revalidated 2026-06-04)

**Goal:** Authoritative evidence base and implementation strategy before writing skill code.

**2026-06-04 correction pass:** Phase 0 was repeated to remove stale source names, revalidate live tool/version claims,
and propagate the research recommendations into planning, source references, and runtime reference files.

**Actions:**

- [x] Create project skeleton
- [x] Document optional Scrapling web-research support only as a suggestion to install/load the skill
- [x] Check HQ skill index — no existing Python best practices skill
- [x] Research top Python best practices sources
- [x] Research cross-ecosystem agent instruction patterns
  - `research/cross-ecosystem-agent-instructions.md`
  - `research/cross-ecosystem-skill-strategy.md`
  - `research/hermes-skill-patterns.md`
- [x] Research code extraction best practices
  - `research/code-extraction/best-practices.md`
- [x] Research the role of requirements.txt in Python projects and how it interacts with pyproject.toml and lockfiles
- [x] Research Python `.gitignore` template sources and targeted ignore-rule guidance
- [x] Decide the skill strategy: adaptive router + focused references, not mega-prompt
- [x] Compile distilled planning references under `references/` and `skill/references/`:
  - `references/README.md` — source index with URLs and revalidated GitHub popularity signals
  - `references/research-evidence.md` — distilled planning evidence
  - `research/tooling-version-snapshot-2026-06-04.md` — live GitHub/PyPI snapshot for Phase 0 revalidation
  - `research/python-gitignore-templates.md` — maintained Python `.gitignore` template comparison
  - `skill/references/project-orientation.md` — project structure and inspection reference
  - `skill/references/pyproject-template.md` — PEP 621 template and backend caveats
  - `skill/references/lint-format-typing-testing.md` — Ruff, mypy, pytest, and tooling commands
- [x] User review of Phase 0 output

**Input:** Seed research and public ecosystem examples. **Output:** `plan.md`, `vision.md`, `todos.md`,
`references/*.md`, `research/*.md`. **Verification:** User approves Phase 0 strategy before Phase 1 begins.

---

### Phase 1 — Skill Draft (complete)

**Goal:** Write a small, reviewable skill draft that routes agents to the right focused guidance.

**Do not** start with a giant `SKILL.md` that repeats every Python rule. The cross-ecosystem research shows that strong
agent-instruction systems use scoped, concrete, repo-aware guidance with progressive disclosure.

**Top-level `skill/SKILL.md` responsibilities:**

1. Trigger on Python implementation, refactor, review, packaging, setup, testing, typing, and tooling work.
2. Require project inspection before advice.
3. Classify the project state and task type.
4. Route to the relevant reference file.
5. State the greenfield baseline and caveats.
6. List core Python footguns.
7. Require verification evidence before reporting complete.
8. Preserve local conventions unless modernization is requested.

**First reference set:**

1. `skill/references/project-orientation.md`
   - inspect config files, lock files, CI, Makefile, test runners, and repo-local agent instructions
2. `skill/references/pyproject-template.md`
   - modern PEP 621 baseline template, build-backend caveats, `src/` layout guidance
3. `skill/references/lint-format-typing-testing.md`
   - uv/Ruff/mypy/pytest command recipes, staged strictness, existing-project caveats
4. `skill/references/review-checklist.md`
   - practical Python review checklist for correctness, typing, tests, dependencies, error handling, and verification
5. `skill/references/mature-repo-preservation.md`
   - preservation-first guidance for mature automation repositories
6. `skill/references/eval-benchmark-hardening.md`
   - benchmark/eval runner metadata, fallback attribution, assertion-quality, and TDD hardening guidance

**Reference files intentionally deferred until evals prove they are needed:**

- `packaging.md`
- `errors-and-logging.md`
- `cli.md`
- `migration-existing-code.md`
- `scientific-python.md`
- `web-frameworks.md`

**Output:** `skill/SKILL.md` and focused files under `skill/references/`. **Verification:** Markdown
formatting/structure checks; manual review of trigger scope and reference routing.

---

### Phase 2 — Test & Iterate (complete; qualitative approval recorded 2026-06-05)

**Current status:** controlled eval prompts, fixtures, structural readiness checks, a source-guidance qualitative
review, a first transcript benchmark, benchmark-runner guards, Codex non-trigger rerun evidence, a portable
mature-automation JSON eval, mature-repo dogfood evidence, an expanded Codex 9-eval benchmark run, and a targeted
assertion-quality iteration exist. The expanded run shows the earlier non-trigger leakage is controlled and the mature
automation case preserves the native gate. The targeted pass narrowed brittle exact-phrase checks into named synonym
groups so evals grade behavior rather than one-word wording choices. Follow-up hardening records effective fallback
backend/model metadata for timed-out OpenCode runs and tightens the incremental typing/testing assertion group. A
post-polish Codex rerun of the affected incremental typing/testing eval passed 9/9 assertions in both `with_skill` and
`without_skill` configurations. User qualitative approval to close Phase 2 was recorded on 2026-06-05 after reviewing
the recommendation to move into Phase 3.

**Goal:** Validate that the skill improves agent behavior on realistic Python tasks without overfitting or causing
unsafe migrations.

**Controlled eval prompts:**

1. Greenfield setup: "I'm starting a new Python CLI project. Set me up with the right structure, config, and tooling."
2. Existing-file review: "Review this Python file and tell me what's wrong with it." Use a deliberately sloppy file.
3. Incremental typing/testing: "I need to add type hints and a test suite to this module. Walk me through it."
4. Existing-project preservation: give the agent a small existing Python project with established tooling and verify it
   preserves local conventions.
5. Mature automation repository preservation: review a fixture where Python supports governance scripts/tests and verify
   the response preserves the native shell gate instead of converting the repo into a packaged Python project.

**High-complexity dogfood target:**

Completed against `/home/sand/projects/ai-project-governance` after controlled evals established baseline behavior.
Evidence is recorded in `evals/mature-repo-dogfood-ai-project-governance-2026-06-04.md`.

Purpose:

- Test whether the skill respects a mature `AGENTS.md` contract and project-specific lifecycle.
- Verify it discovers project-native gates such as `bash scripts/check-consistency.sh`.
- Verify it avoids forcing greenfield `uv` / `src/` / strict-mypy migration onto an established governance repository.
- Produce a review/advice report first; do not make broad edits without explicit authorization.

**Prompt pattern used:**

```text
Use the python-best-practices skill to review /home/sand/projects/ai-project-governance as an existing mature Python
repository. Inspect repo conventions first. Do not migrate package managers, rewrite layout, or change governance docs.
Produce a report: detected stack, project-native commands, Python best-practice gaps, verification commands, and safe next
improvements.
```

**Eval setup:**

- [x] Create `evals/evals.json` with controlled prompts, including a portable mature-automation preservation fixture.
- [x] Add fixture smoke checks in `scripts/run_phase2_checks.py`.
- [x] Add validation-script regression tests for actionable negative-path errors.
- [x] Add portable GitHub Actions source-validation workflow.
- [x] Add human-facing `CONTRIBUTING.md` local development loop.
- [x] Produce source-guidance qualitative review for user review.
- [x] Run transcript-based with-skill vs baseline using the `skill-creator`/fallback transcript pattern.
- [x] Launch or produce transcript benchmark results for user review.
- [x] Strengthen non-trigger behavior and benchmark assertions.
- [x] Rerun affected non-trigger prompts successfully with Codex backend.
- [x] Add portable mature-automation fixture coverage to `evals/evals.json` and `scripts/run_phase2_checks.py`.
- [x] Rerun the expanded 9-eval benchmark suite after adding the mature-automation case.
- [x] Narrow brittle exact-phrase eval assertions surfaced by the expanded Codex run.
- [x] Add ai-project-governance as a mature-repo dogfood report after the controlled cases establish baseline behavior.

**Iteration loop:** fix based on feedback, rerun, repeat. Iteration 1 results are recorded in
`evals/transcript-benchmark-iteration-1-2026-06-04.md`; expanded 9-eval Codex results are summarized in
`evals/transcript-benchmark-expanded-9-2026-06-04.md`; targeted assertion-quality evidence is recorded in ignored
workspace benchmark outputs under `python-best-practices-workspace/codex-assertion-quality-*` and
`python-best-practices-workspace/codex-polish-incremental-20260605/benchmark.json`; mature-repo dogfood is recorded in
`evals/mature-repo-dogfood-ai-project-governance-2026-06-04.md`; raw local transcripts live in the ignored
`python-best-practices-workspace/` directory.

**Output:** Iterated skill revisions, benchmark results, and dogfood findings. **Verification:** User qualitative
approval recorded on 2026-06-05 after benchmark and dogfood review; Phase 3 is now the active phase.

---

### Phase 3 — Description Optimization (current)

**Current status:** the initial 20-query trigger/near-miss eval set exists at `evals/trigger-description-evals.json` and
is marked `draft-for-user-review`. It contains 10 should-trigger prompts and 10 should-not-trigger near misses.

**Goal:** Maximize triggering accuracy after the skill behavior is stable.

- [x] Generate 20 trigger eval queries: mix of should-trigger and should-not-trigger prompts.
- [x] Include near misses: generic Python questions, framework-specific requests, non-Python tooling, and docs-only
      requests.
- [ ] User reviews eval set.
- [ ] Select or implement the description-optimization workflow/tooling for this repo.
- [ ] Run up to 5 description-optimization iterations once the workflow is chosen.
- [ ] Apply the selected description to `skill/SKILL.md` frontmatter.

**Output:** Optimized frontmatter `description:`. **Verification:** Trigger rate on held-out test set, target >80%
without obvious over-triggering.

---

### Phase 4 — Polish, Ship & Publish

**Goal:** Ship a user-ready local skill, with optional packaging or hub publishing only after explicit approval.

Shipping model:

- `skill/` is the directory-as-boundary runtime payload: everything inside it is eligible to ship; repository-only
  assets such as `README.md`, `plan.md`, `todos.md`, `research/`, `references/`, `evals/`, `tests/`, `.github/`, and
  workspace outputs stay in the source checkout.
- The local installed Hermes mirror at `~/.hermes/skills/software-development/python-best-practices` is a test/runtime
  mirror, not source of truth. Sync only from `skill/` with `scripts/run_phase2_checks.py --sync-installed`.
- Packaging/publishing uses an explicit human-authorized side-effect boundary: do not package, publish, contribute to
  the hub, push tags, or sync to other Hermes profiles from routine validation.

Tasks:

1. Refresh source-vs-mirror drift with `python3 scripts/run_phase2_checks.py --sync-installed` and rerun the check.
2. Verify source-only CI parity with `python3 scripts/run_phase2_checks.py --skip-installed`.
3. Verify the installed skill is discoverable (`hermes skills list | grep python-best-practices`) and loads in a fresh
   session.
4. Run at least one fresh-session trigger check and one should-not-trigger near miss after Phase 3 description tuning.
5. Produce a concise user handoff: what the skill does, install/runtime boundary, verification evidence, known limits,
   and exact next command for the user.
6. Optional, only after explicit approval: package with `package_skill.py` or contribute to Hermes skill hub.

**Output:** User-ready local skill handoff, or an explicitly approved package/publish artifact. **Verification:** Full
local gate, source-only gate, installed mirror sync check, fresh-session trigger/near-miss evidence, and confirmation
that repository-only files are absent from the runtime payload.

---

## Key Decisions

| #   | Decision                                                      | Rationale                                                                                                                        | Evidence                                                                     |
| :-- | :------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------- |
| 1   | Adaptive workflow, not encyclopedia                           | Strong agent ecosystems use scoped, concrete, verifiable instructions                                                            | `research/cross-ecosystem-skill-strategy.md`                                 |
| 2   | Inspect before advising                                       | Existing Python projects vary by package manager, runner, layout, and CI                                                         | Cursor/Claude/Codex/Copilot patterns; Python tooling docs                    |
| 3   | `SKILL.md` as router / operating contract                     | Progressive disclosure keeps the always-loaded prompt small                                                                      | Claude Skills, Cursor rules, Codex `AGENTS.md` layering                      |
| 4   | uv as greenfield package/project manager default              | Unified project, dependency, environment, build, and tool execution model                                                        | Astral uv docs                                                               |
| 5   | Ruff as greenfield lint/import-sort/format tool               | Fast modern replacement for many lint/format tools                                                                               | Astral Ruff docs                                                             |
| 6   | mypy for typing, with staged strictness                       | Static typing catches issues, but legacy projects need incremental rollout                                                       | mypy getting-started and existing-code docs                                  |
| 7   | pytest as default test runner                                 | Widely used and well-documented; pairs well with `src/` layout                                                                   | pytest good practices                                                        |
| 8   | PEP 621 / pyproject-centered config                           | Standard package metadata and tool config location                                                                               | PyPA packaging guide, PEP 518, PEP 621, current PyPA specs                   |
| 9   | Google-style docstrings as default, not mandate               | Useful general default; NumPy/Sphinx styles remain valid in some projects                                                        | Google Python Style Guide, ecosystem caveats in strategy report              |
| 10  | ai-project-governance as later mature dogfood                 | High-signal stress test but too complex for the first eval                                                                       | Strategy recommendation from 2026-06-03 session                              |
| 11  | `.gitignore` guidance uses maintained templates as checklists | GitHub and gitignore.org/Toptal templates are useful baselines, but repo-specific ignores and lockfile policy must be preserved. | `research/python-gitignore-templates.md`                                     |
| 12  | `skill/` is the user-shipping boundary                        | Industry packaging research favors simple directory/manifest boundaries over sprawling allowlist plus exclusion policy.          | `/home/sand/projects/ai-project-governance/research/packaging-strategies.md` |

## Deferred Decisions

See [`vision.md`](./vision.md) for full vision doc.

- Framework-specific guidance (Django, FastAPI, Flask) — separate references or skills after core evals
- Scientific Python / conda / pixi / notebook guidance — separate reference after evidence of need
- Security scanning (bandit, pip-audit, safety) — later candidate
- CI template generation — later candidate
- Docker best practices — later candidate
- Auto-migration of legacy projects — aspiration, not Phase 1 behavior
