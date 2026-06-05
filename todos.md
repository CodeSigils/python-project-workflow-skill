# TODOs

## Phase 0 — Planning & Research (complete; revalidated 2026-06-04)

- [x] Create project skeleton (README, plan, vision, todos, refs)
- [x] Document optional Scrapling web-research support only as a suggestion to install/load the skill
- [x] Search HQ skill index for existing Python skill (none found)
- [x] Research authoritative Python best practices sources
- [x] Create research/ folder with cross-ecosystem agent-instruction comparison
- [x] Create cross-ecosystem skill strategy synthesis
- [x] Update project docs to reflect adaptive workflow strategy
- [x] Create `references/README.md` with source URLs and revalidated popularity signals
- [x] Create `references/research-evidence.md` with distilled evidence and caveats
- [x] Create `research/tooling-version-snapshot-2026-06-04.md` with live GitHub/PyPI checks
- [x] Reference: PyPA/PEP 621 project structure and packaging caveats
- [x] Reference: Ruff config presets, staged rules, and unsafe-fix caveats
- [x] Reference: mypy config boilerplate with incremental adoption strategy
- [x] Reference: pytest patterns, `src/` layout, and import-mode caveats
- [x] Reference: modern pyproject.toml / PEP 621 template
- [x] Get project reviewed by user

## Phase 1 — Skill Draft (complete)

- [x] Create `skill/SKILL.md` as a concise router / operating contract
- [x] Add `skill/references/project-orientation.md`
- [x] Add `skill/references/pyproject-template.md`
- [x] Add `skill/references/lint-format-typing-testing.md`
- [x] Add `skill/references/review-checklist.md`
- [x] Verify Markdown formatting and reference routing
- [x] User review of skill draft

## Phase 2 — Test & Iterate

- [x] Create eval test prompts for greenfield setup, existing-file review, incremental typing/testing, and
      existing-project preservation
- [x] Create `evals/evals.json` and fixture smoke validation in `scripts/run_phase2_checks.py`
- [x] Add portable mature-automation preservation eval and fixture smoke coverage
- [x] Rerun expanded 9-eval benchmark suite after adding the mature-automation case
- [x] Narrow brittle exact-phrase eval assertions surfaced by the expanded Codex run
- [x] Add validation-script regression tests for actionable error output
- [x] Add portable GitHub Actions source-validation workflow
- [x] Add `CONTRIBUTING.md` with the local development loop
- [x] Run source-guidance qualitative review and document iteration notes
- [x] Run transcript-based with/without skill comparison using the `skill-creator`/fallback transcript pattern
- [x] Create or export transcript benchmark results so the human can review test cases
- [x] Strengthen non-trigger behavior and benchmark assertions
- [x] Rerun affected non-trigger prompts successfully with Codex backend
- [x] Dogfood on `/home/sand/projects/ai-project-governance` as a mature-repo review target
- [ ] Iterate based on feedback

## Phase 3 — Description Optimization

- [ ] Generate trigger eval set (20 queries, mix of should-trigger and should-not-trigger)
- [ ] Include near misses so the skill does not over-trigger on generic Python or non-Python work
- [ ] Select or implement the description-optimization workflow/tooling for this repo
- [ ] Run the chosen optimization workflow and apply the selected description to frontmatter

## Phase 4 — Polish, Ship & Publish

- [ ] Treat `skill/` as the directory-as-boundary runtime payload
- [x] Maintain local installed mirror for runtime testing
- [ ] Run source-only and installed-mirror readiness gates
- [ ] Verify in a fresh session with one trigger and one near-miss prompt
- [ ] Produce user handoff with verification evidence and known limits
- [ ] Optional after explicit approval: package as .skill file
- [ ] Optional after explicit approval: contribute to Hermes skill hub
