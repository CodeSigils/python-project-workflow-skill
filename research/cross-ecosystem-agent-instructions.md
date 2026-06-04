# Cross-Ecosystem Agent Instruction Research

Last checked: 2026-06-03

Question: what do the strongest skill/rule/instruction ecosystems do well when they guide agents on Python best
practices, and what should this Hermes skill borrow?

## Sources checked

| Ecosystem                 | Source URL                                                                                                      | Relevant mechanism                                                         |
| :------------------------ | :-------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------- |
| Claude Code               | https://docs.anthropic.com/en/docs/claude-code/memory                                                           | `CLAUDE.md` memory files for project/user/team guidance.                   |
| Cursor                    | https://docs.cursor.com/context/rules                                                                           | Project rules and context-specific instructions.                           |
| Windsurf                  | https://docs.windsurf.com/windsurf/cascade/memories                                                             | Memories/rules that steer Cascade with reusable context.                   |
| Continue                  | https://docs.continue.dev/customize/deep-dives/rules                                                            | Rule files for coding standards and reusable agent behavior.               |
| GitHub Copilot            | https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot | Repository custom instructions and path-scoped guidance.                   |
| Aider                     | https://aider.chat/docs/usage/conventions.html                                                                  | Repository conventions, lint/test commands, and edit workflow assumptions. |
| AGENTS.md convention      | https://agents.md/                                                                                              | Repo-local instruction files for coding agents.                            |
| OpenAI Codex repo example | https://raw.githubusercontent.com/openai/codex/main/AGENTS.md                                                   | Concrete AGENTS.md with project-specific commands and conventions.         |

Network note: the URLs above were checked with HTTP requests on 2026-06-03. This research pass used direct HTTP checks
plus ecosystem documentation. In reusable guidance, deeper scraping needs should be framed as a suggestion to install or
load the Scrapling Hermes skill, not as a dependency or capability that is already present.

## Repeating patterns across strong ecosystems

### 1. Repo-local instructions beat global style advice

The strongest systems prioritize files checked into the repository: `CLAUDE.md`, `.cursor/rules`,
`.github/copilot-instructions.md`, Continue rules, `AGENTS.md`, and Aider conventions. This keeps guidance close to the
code and lets the instruction file describe actual commands, layout, and trade-offs.

Implication for this skill: it should not pretend one Python style fits every repo. It should first inspect existing
project files (`pyproject.toml`, `uv.lock`, `ruff.toml`, `mypy.ini`, `pytest.ini`, `tox.ini`, `noxfile.py`, CI
workflows) and adapt recommendations to live project conventions.

### 2. Commands are first-class guidance

Good instruction files tell agents exactly how to verify work. They name commands like lint, format, type-check, tests,
focused tests, docs build, or package build. For Python, that means the skill should provide command recipes such as:

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest
uv build
```

When a project uses different tools, the skill should preserve local commands instead of replacing them prematurely.

### 3. Rules are scoped and layered

Cursor, Continue, Copilot, and AGENTS.md-style ecosystems all support either path-scoped or repo-scoped guidance. The
strongest examples do not put frontend, backend, packaging, tests, and deployment instructions into one undifferentiated
wall of text.

Implication: the Hermes skill should use progressive disclosure:

- `SKILL.md`: short workflow and decision tree.
- `skill/references/tooling.md`: uv/ruff/mypy/pytest commands.
- `skill/references/typing.md`: strict typing strategy.
- `skill/references/testing.md`: pytest patterns.
- `skill/references/packaging.md`: `pyproject.toml`, src layout, build metadata.
- `skill/references/review-checklist.md`: agent code-review checklist.

### 4. Good guidance includes do/don't rules, not just ideals

Strong rules encode concrete footguns:

- do not commit secrets,
- do not invent commands that are not in the repo,
- do not run broad destructive formatters without understanding scope,
- do not ignore failing tests,
- do not change generated/lock files casually,
- do not over-engineer abstractions for small modules.

For Python, the skill should include comparable footguns:

- avoid mutable default arguments,
- avoid bare `except`,
- avoid wildcard imports,
- avoid runtime import cycles,
- avoid silent `# type: ignore` without a reason,
- avoid tests that pass only because they hit local state/network,
- avoid package imports that work only because the current directory is on `sys.path`.

### 5. Strong ecosystems distinguish canonical rules from personal memory

Claude Code and similar systems distinguish project memory from user/personal memory. Repository instructions should be
safe to share. Personal preferences, local paths, API keys, and one-off state do not belong in canonical project rules.

Implication: the Python skill should tell agents to keep durable project rules in repo files and keep local
preferences/secrets out. If a config snippet contains a secret, redact it as `[REDACTED]`.

### 6. Examples and templates matter

Good instruction ecosystems provide examples rather than abstract principles alone. A Python best-practices skill should
include small copyable templates for:

- `pyproject.toml` with PEP 621 metadata,
- ruff lint/format config,
- mypy strict config with realistic exclusions,
- pytest config and fixture layout,
- CLI entry point wiring,
- exception/logging patterns,
- packaging/build commands.

### 7. Verification is part of the instruction, not an afterthought

The best agent instructions describe what "done" means. For this skill, done should normally mean:

1. formatting is clean,
2. linting is clean,
3. type checking is clean or failures are explicitly triaged,
4. tests pass, preferably focused tests first then broader suite,
5. packaging/build checks pass when packaging was touched,
6. docs/examples are updated when behavior changes.

## Ecosystem-specific observations

### Claude Code / CLAUDE.md

Strengths:

- simple, repo-local file name,
- supports persistent project memory,
- encourages documenting commands and project-specific practices.

Borrow:

- a "project orientation first" step for Python repositories,
- clear separation between checked-in project guidance and personal notes.

Avoid:

- letting a single memory file grow into an unstructured mega-prompt.

### Cursor rules

Strengths:

- scoped rules fit different directories and file types,
- useful for coding standards that apply only to part of a repo.

Borrow:

- path/scope thinking: packaging guidance differs from test guidance, library code differs from CLI code.

Avoid:

- highly fragmented rules that require an agent to load many small files before doing simple work.

### Windsurf memories

Strengths:

- reusable memory can capture stable project conventions,
- useful for iterative work across sessions.

Borrow:

- durable conventions: supported Python versions, preferred tool commands, framework choices, test tiers.

Avoid:

- storing temporary task status as durable best-practice guidance.

### Continue rules

Strengths:

- rule files are explicit and versionable,
- good fit for team-wide coding standards.

Borrow:

- rule files should be actionable and narrowly scoped.

Avoid:

- vague rules such as "write clean code" without commands or examples.

### GitHub Copilot custom instructions

Strengths:

- repository-level instructions meet agents where developers already work,
- can encode project conventions for many users.

Borrow:

- include tool commands and conventions in repo docs; the Python skill can help generate or review these instructions.

Avoid:

- assuming Copilot-specific instruction formats are portable to every agent.

### Aider conventions

Strengths:

- strong emphasis on repository commands and edit/test cycles,
- practical for terminal-based agents.

Borrow:

- run project-native tests after edits,
- prefer small focused changes that are easy to review.

Avoid:

- treating broad code rewrites as default when a targeted edit is safer.

### AGENTS.md / Codex-style examples

Strengths:

- explicit repo-local contract for coding agents,
- can include commands, architecture notes, and safe operating boundaries.

Borrow:

- for Python repos, encourage an `AGENTS.md` section listing:
  - setup command,
  - lint command,
  - type command,
  - test command,
  - packaging/build command,
  - generated files and no-edit zones,
  - minimum Python version.

Avoid:

- mixing project contract, personal memory, and stale session notes.

## What this means for the Hermes Python skill

The Hermes skill should be an expert workflow, not an encyclopedia. It should:

1. inspect before advising,
2. preserve local conventions unless clearly obsolete,
3. recommend the modern baseline (`uv`, `ruff`, `mypy`, `pytest`, PEP 621, `src/` layout) when starting new work,
4. provide copyable config templates,
5. include verification gates,
6. include anti-patterns and escalation rules,
7. keep the top-level skill concise and push deep content into references.

## Open follow-up research

- Find high-quality public `.cursor/rules` and `CLAUDE.md` examples from active Python repositories.
- Compare Python-specific Copilot instruction examples from real projects.
- Evaluate whether framework-specific subskills are better than one giant Python skill for Django, FastAPI, scientific
  Python, and packaging/release work.
