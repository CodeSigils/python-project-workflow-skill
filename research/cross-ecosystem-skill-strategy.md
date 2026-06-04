# Cross-Ecosystem Skill Strategy for Python Best Practices

Last checked: 2026-06-03

## Question

What are the strongest agent-skill / agent-instruction ecosystems doing well, and how should this project use those
patterns to build a high-quality `python-best-practices` Hermes skill?

## Executive recommendation

Build this skill as an adaptive workflow, not a Python encyclopedia.

The best ecosystems converge on the same design: small, scoped, concrete, repo-aware, verifiable instructions outperform
large generic style guides. For this project, that means:

1. `skill/SKILL.md` should be a concise router and operating contract.
2. Detailed Python knowledge should live in scoped reference files loaded only when relevant.
3. The first action should always be project inspection before applying defaults.
4. The skill should preserve coherent local conventions and use the modern baseline only for greenfield or incoherent
   projects.
5. Every recommendation should name verification commands or explain why verification is unavailable.

The default greenfield stack remains sound:

```text
uv + ruff + mypy + pytest + pyproject.toml/PEP 621 + src/ layout + Google-style docstrings
```

But the skill should present this as a preferred default, not a universal mandate.

## Sources checked

### Agent instruction and skill ecosystems

| Ecosystem                   | Source URL                                                                                                                         | Key mechanism                                                           |
| :-------------------------- | :--------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------- |
| Claude Code memory          | https://code.claude.com/docs/en/memory                                                                                             | Scoped `CLAUDE.md` project/user/team guidance.                          |
| Claude Code skills          | https://code.claude.com/docs/en/skills                                                                                             | `SKILL.md` plus supporting files and scripts.                           |
| Cursor rules                | https://cursor.com/docs/rules                                                                                                      | `.cursor/rules` with always-on, model-selected, glob, and manual rules. |
| Windsurf / Devin memories   | https://docs.devin.ai/desktop/cascade/memories                                                                                     | Global/workspace/AGENTS rules with triggers.                            |
| Continue rules              | https://docs.continue.dev/customize/deep-dives/rules                                                                               | Versionable reusable rule files.                                        |
| GitHub Copilot instructions | https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions | Repository and path-scoped custom instructions.                         |
| AGENTS.md convention        | https://agents.md/                                                                                                                 | Repo-local instruction files for coding agents.                         |
| OpenAI Codex AGENTS guide   | https://developers.openai.com/codex/guides/agents-md                                                                               | Nested `AGENTS.md` instruction discovery and override order.            |

### Python-specific authoritative sources

| Topic                     | Source URL                                                           | Use in this project                               |
| :------------------------ | :------------------------------------------------------------------- | :------------------------------------------------ |
| Packaging tutorial        | https://packaging.python.org/en/latest/tutorials/packaging-projects/ | Baseline project/package structure.               |
| PyPA sample project       | https://github.com/pypa/sampleproject                                | Concrete structure example.                       |
| PyPA specs index          | https://packaging.python.org/en/latest/specifications/               | Current canonical packaging specs.                |
| uv overview               | https://docs.astral.sh/uv/                                           | Modern package/project manager default.           |
| uv projects               | https://docs.astral.sh/uv/concepts/projects/                         | Project workflow and lockfile model.              |
| Ruff overview             | https://docs.astral.sh/ruff/                                         | Modern lint/import-sort/format default.           |
| Ruff configuration        | https://docs.astral.sh/ruff/configuration/                           | Config guidance and rule-selection caution.       |
| Ruff formatter            | https://docs.astral.sh/ruff/formatter/                               | Black-compatible formatter rationale.             |
| mypy getting started      | https://mypy.readthedocs.io/en/stable/getting_started.html           | Why annotations are required for useful checking. |
| mypy existing code        | https://mypy.readthedocs.io/en/stable/existing_code.html             | Incremental typing strategy.                      |
| pytest good practices     | https://docs.pytest.org/en/stable/explanation/goodpractices.html     | `src/` layout and import-mode guidance.           |
| Google Python Style Guide | https://google.github.io/styleguide/pyguide.html                     | Docstring/style baseline, with caveats.           |
| PEP 8                     | https://peps.python.org/pep-0008/                                    | General style source.                             |
| PEP 518                   | https://peps.python.org/pep-0518/                                    | `[build-system]` source.                          |
| PEP 621                   | https://peps.python.org/pep-0621/                                    | `[project]` metadata source.                      |
| PEP 660                   | https://peps.python.org/pep-0660/                                    | Editable installs for pyproject-based builds.     |

### Public instruction examples sampled

| Example                              | URL                                                                                            | Why it matters                                                             |
| :----------------------------------- | :--------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------- |
| SQLFluff root `AGENTS.md`            | https://github.com/sqlfluff/sqlfluff/blob/main/AGENTS.md                                       | Strong active Python example with architecture, commands, and conventions. |
| SQLFluff nested source instructions  | https://github.com/sqlfluff/sqlfluff/blob/main/src/sqlfluff/AGENTS.md                          | Directory-scoped source guidance.                                          |
| SQLFluff nested test instructions    | https://github.com/sqlfluff/sqlfluff/blob/main/test/AGENTS.md                                  | Directory-scoped test guidance.                                            |
| OpenAI Guardrails Python `AGENTS.md` | https://github.com/openai/openai-guardrails-python/blob/main/AGENTS.md                         | Python style/review checklist example.                                     |
| RMG-Py Copilot instructions          | https://github.com/ReactionMechanismGenerator/RMG-Py/blob/main/.github/copilot-instructions.md | Scientific/tool-heavy Python instructions with domain context.             |
| Beets Copilot instructions           | https://github.com/beetbox/beets/blob/master/.github/copilot-instructions.md                   | Mixed example: useful review heuristics, but persona-heavy.                |
| niworkflows `CLAUDE.md`              | https://github.com/nipreps/niworkflows/blob/master/CLAUDE.md                                   | Scientific Python setup/testing prerequisites.                             |
| PgSTAC `CLAUDE.md`                   | https://github.com/stac-utils/pgstac/blob/main/CLAUDE.md                                       | Generated-file and migration boundaries.                                   |
| tmuxp Cursor pytest rule             | https://github.com/tmux-python/tmuxp/blob/master/.cursor/rules/tmuxp-pytest.mdc                | Focused glob-scoped test guidance.                                         |
| pygeohash Cursor testing rule        | https://github.com/wdm0006/pygeohash/blob/master/.cursor/rules/testing.mdc                     | Concrete commands, but quality caveats.                                    |
| pygeohash pytest standards rule      | https://github.com/wdm0006/pygeohash/blob/master/.cursor/rules/pytest_standards.mdc            | Example of public rule quality variance.                                   |
| unxt Copilot instructions            | https://github.com/GalacticDynamics/unxt/blob/main/.github/copilot-instructions.md             | Small scientific repo with architecture and version context.               |

## Cross-ecosystem patterns to borrow

### 1. Scope and layering are the main quality multiplier

Strong systems avoid one always-on mega-prompt. They use project, path, team, user, or manual scopes:

- Claude Code has project and local memory files.
- Cursor supports always-on, model-selected, glob, and manual rules.
- Windsurf / Devin supports global, workspace, AGENTS, system, and trigger-scoped rules.
- GitHub Copilot supports repository and path-scoped instruction files.
- Codex discovers nested `AGENTS.md` files from repo root to current directory.

Implication for this skill:

- Keep `SKILL.md` short and route to references.
- Split Python guidance by task surface.
- Tell agents to inspect repo-local instruction files before applying generic advice.

Recommended runtime shape:

```text
skill/
├── SKILL.md
└── references/
    ├── project-orientation.md
    ├── pyproject-template.md
    ├── lint-format.md
    ├── typing.md
    ├── testing.md
    ├── packaging.md
    ├── errors-and-logging.md
    ├── cli.md
    ├── migration-existing-code.md
    └── review-checklist.md
```

### 2. Concrete commands beat abstract principles

The strongest instruction files tell agents how to verify work:

- setup command,
- lint command,
- format command,
- type-check command,
- focused test command,
- full test command,
- build/package command,
- generated-file/no-edit zones.

Implication for this skill:

- Always prefer project-native commands discovered from config, README, Makefile, CI, tox, nox, hatch, pixi, uv, poetry,
  or pre-commit.
- Use default commands only when the project lacks conventions.

Default greenfield verification path:

```bash
uv sync
uv run ruff format --check .
uv run ruff check .
uv run mypy .
uv run pytest
uv build
```

Do not require `uv build` unless packaging metadata or distributable package behavior was touched.

### 3. Project inspection must precede recommendations

A Python best-practices skill can easily become harmful if it blindly migrates established projects.

The skill should inspect:

```text
pyproject.toml
setup.py
setup.cfg
requirements*.txt
uv.lock
poetry.lock
Pipfile
tox.ini
noxfile.py
pytest.ini
mypy.ini
ruff.toml
.pre-commit-config.yaml
Makefile
.github/workflows/*.yml
AGENTS.md
CLAUDE.md
.cursor/rules/*
.github/copilot-instructions.md
.github/instructions/*.instructions.md
.continue/rules/*
```

Then classify the project:

| Project state                      | Skill behavior                                                            |
| :--------------------------------- | :------------------------------------------------------------------------ |
| Greenfield                         | Recommend the modern baseline.                                            |
| Coherent existing toolchain        | Preserve local conventions and improve within them.                       |
| Fragmented/stale toolchain         | Recommend modernization only with trade-offs and user approval.           |
| Scientific/HPC/conda-heavy project | Respect conda/pixi/mamba or domain-specific workflow.                     |
| Framework project                  | Defer Django/FastAPI/scientific specifics to future references/subskills. |
| Legacy untyped project             | Adopt typing incrementally; do not force full strictness immediately.     |

### 4. Good public examples teach the project mental model

SQLFluff, RMG-Py, niworkflows, PgSTAC, and unxt are useful because they explain the repo’s architecture, generated
files, fixtures, domain constraints, or workflows. They do not only say "write clean code."

Implication for this skill:

- The skill should help agents create or improve repo-local Python instructions that include project context, not just
  universal style rules.
- It should encourage this pattern for Python repositories:

```text
AGENTS.md / CLAUDE.md
├── What this project is
├── Source layout and main packages
├── Setup command
├── Lint/format/type/test commands
├── Targeted test examples
├── Dependency/change policy
├── Generated files and no-edit zones
├── Domain-specific constraints
└── Final reporting expectations
```

### 5. Public examples are uneven; validate claims before borrowing

The search found strong examples, but also copied boilerplate, persona-heavy instructions, and at least one questionable
pytest claim. Public `.cursor/rules` examples are plentiful but inconsistent. Continue rule examples were relatively
scarce in sampled public Python repos.

Implication for this skill:

- Treat public examples as pattern evidence, not authority.
- Ground Python claims in PyPA, Python PEPs, uv, Ruff, mypy, pytest, and style-guide docs.
- Use examples to shape structure, not to copy technical claims uncritically.

## Python-specific conclusions

### uv

Use uv as the default for new projects because it unifies project management, virtual environments, lockfiles, Python
installation, tool execution, building, and publishing.

Caveats:

- Existing projects may be committed to pip, Poetry, Hatch, tox, nox, conda, pixi, or enterprise workflows.
- Libraries may commit lockfiles for development reproducibility, but consumers are not bound to that lockfile.
- uv is the workflow frontend; PyPA/PEP specs remain the standards layer.

### Ruff

Use Ruff as the default for linting, import sorting, and formatting.

Caveats:

- Do not enable all rules by default.
- Ruff’s default rules are conservative; strictness should be staged.
- Preserve Black/isort/Flake8/Pylint if a project already standardizes on them unless modernization is requested.

### mypy

Use static typing as the default expectation for new code, especially public APIs.

Caveats:

- `strict = true` is good for greenfield/library code but too blunt for many legacy, framework-heavy, or script-heavy
  projects.
- Existing projects need incremental typing: module-by-module adoption, targeted ignores, pinned mypy version, and stub
  package handling.
- Detect Pyright/Pylance config before imposing mypy.

### pytest

Use pytest as the default test runner. Prefer `tests/` outside package code and `src/` layout for distributable
packages.

Caveats:

- Some projects use unittest, tox, nox, hatch, pixi, framework-specific runners, or Makefile wrappers.
- Avoid ad hoc `PYTHONPATH` hacks unless project docs require them.
- Prefer project-managed execution such as `uv run pytest`, `tox`, `nox`, `pixi run`, or `make test`.

### pyproject.toml and packaging

Use `pyproject.toml` with `[build-system]` and PEP 621 `[project]` metadata as the default for package metadata and tool
configuration.

Caveats:

- PEP pages are historical records; use current PyPA specs for operational details.
- Do not mandate one build backend for all projects.
- Do not reorganize an existing package into `src/` layout without user approval.

### Docstrings and style

Google-style docstrings are a reasonable general default for this project.

Caveats:

- NumPy/Sphinx/reST styles are common in scientific and library ecosystems.
- Google’s Pylint and import guidance is stricter than many open-source projects and should not override local style by
  default.

## Recommended `SKILL.md` operating contract

The first draft should make these rules explicit:

1. Inspect before advising.
2. Prefer repo conventions over generic defaults.
3. Use the modern baseline for greenfield or incoherent projects.
4. Keep changes minimal and reversible.
5. Ask before changing package managers, dependency policy, source layout, or generated-file boundaries.
6. Load only the relevant reference file for the task.
7. Verify with project-native commands.
8. Report commands run, results, files changed, skipped checks, and remaining risks.

## Recommended reference files for Phase 1

Do not try to write every possible reference file at once. Start with the smallest set that makes the skill useful and
testable:

1. `skill/SKILL.md`
2. `skill/references/project-orientation.md`
3. `skill/references/pyproject-template.md`
4. `skill/references/lint-format-typing-testing.md`
5. `skill/references/review-checklist.md`

Then add focused files only after evals show the skill needs them:

- `packaging.md`
- `errors-and-logging.md`
- `cli.md`
- `migration-existing-code.md`
- `scientific-python.md`
- `web-frameworks.md`

## Proposed task routing table

| User task               | Load references                                                                    | Default behavior                                                            |
| :---------------------- | :--------------------------------------------------------------------------------- | :-------------------------------------------------------------------------- |
| New Python project      | `project-orientation.md`, `pyproject-template.md`, `lint-format-typing-testing.md` | Recommend modern baseline.                                                  |
| Existing project review | `project-orientation.md`, `review-checklist.md`                                    | Preserve local conventions; report risks.                                   |
| Add tests               | `project-orientation.md`, `lint-format-typing-testing.md`                          | Use pytest unless project has another runner.                               |
| Add type hints          | `project-orientation.md`, `lint-format-typing-testing.md`                          | Type public APIs; use incremental typing for legacy code.                   |
| Packaging change        | `project-orientation.md`, `pyproject-template.md`                                  | Use PEP 621/PyPA guidance; avoid backend dogmatism.                         |
| Lint/format cleanup     | `project-orientation.md`, `lint-format-typing-testing.md`                          | Use project-native formatter/linter first.                                  |
| Python PR/code review   | `project-orientation.md`, `review-checklist.md`                                    | Check correctness, typing, tests, dependencies, security, and verification. |

## Risks to avoid

1. Mega-prompt skill that repeats every Python rule inline.
2. Blind migration to uv/Ruff/mypy when the repo already has a coherent stack.
3. Enabling maximal Ruff/mypy strictness without a staged adoption plan.
4. Overfitting to Google style where NumPy/Sphinx/project style is established.
5. Treating public agent rule examples as authoritative Python guidance.
6. Hiding failures behind broad ignores such as global `ignore_missing_imports = true`.
7. Using `PYTHONPATH` hacks instead of proper editable/project-managed installs.
8. Changing lockfiles, generated files, migrations, or vendored code without understanding their source of truth.

## Best next step

Write the Phase 1 skill draft, but keep it intentionally small:

```text
SKILL.md = workflow/router/verification contract
references/ = scoped Python details and templates
```

A good first implementation slice is:

1. Create `skill/SKILL.md` with the operating contract and task routing table.
2. Create `skill/references/project-orientation.md` with the inspection checklist.
3. Create `skill/references/pyproject-template.md` with one modern baseline template plus caveats.
4. Create `skill/references/lint-format-typing-testing.md` with practical uv/Ruff/mypy/pytest commands and staged
   strictness.
5. Create `skill/references/review-checklist.md` for review tasks.
6. Then run Phase 2 evals before expanding references further.

This keeps the skill reviewable and lets evals tell us what detail is actually missing.

## Research method note

Scrapling support was considered as an optional future web-research aid. This pass did not require stealth or
JavaScript-heavy scraping: official docs and public raw files were accessible through browser/search/HTTP-style tooling.
For future deeper sampling of public rule files, agents should suggest installing or loading the Scrapling Hermes skill
when it is not already available, or use Sourcegraph-style search to crawl candidate repositories and fetch raw
instruction files systematically.
