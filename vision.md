# Vision: Python Best Practices Hermes Skill

## North Star

A Hermes skill that acts as an on-demand Python project advisor: given a Python task or repository, it inspects the live
project state, identifies the local conventions, selects focused guidance, recommends or applies safe improvements, and
reports verification evidence.

The skill should be useful for both:

- greenfield Python projects that need a modern baseline, and
- mature Python repositories where preserving established conventions is more important than applying generic defaults.

## What Success Looks Like

### Greenfield project

A user drops into a chat:

```text
I'm starting a new Python CLI project. Set me up.
```

The skill responds by:

- creating a `src/` layout when a distributable package makes sense,
- generating `pyproject.toml` with PEP 621 metadata,
- configuring uv-compatible workflows,
- adding Ruff, mypy, and pytest configuration,
- creating a minimal package and tests scaffold,
- explaining what was created and why,
- running or recommending the relevant verification commands.

### Existing mature project

A user asks:

```text
Review this Python repository and tell me what to improve.
```

The skill responds by:

- inspecting package/config/test/CI files first,
- reading repo-local agent instructions such as `AGENTS.md`, `CLAUDE.md`, Cursor rules, or Copilot instructions,
- preserving coherent local conventions,
- identifying safe Python best-practice gaps,
- avoiding broad package-manager, layout, or strictness migrations unless requested,
- reporting project-native commands and skipped checks.

## Dogfood Strategy

`/home/sand/projects/ai-project-governance` is a valuable mature-repo dogfood target, but not the first eval target.

Use it after controlled Phase 2 evals to test whether the skill can survive a complex governance-heavy Python
repository:

- respect mature `AGENTS.md` instructions,
- discover `bash scripts/check-consistency.sh` as the canonical gate,
- avoid forcing greenfield defaults,
- produce a review/advice report before edits,
- require explicit authorization for broad changes.

## Longer-term Aspirations (deferred)

These are not part of the current Phase 2 stabilization and shipping path. Revisit after evals show real need:

1. **Auto-migration**: take a legacy Python project and suggest a staged upgrade path for typing, Ruff, packaging, or
   test structure.
2. **Per-framework variants**: Django, Flask, FastAPI, and Typer guidance separated into branch references or subskills.
3. **Scientific Python variants**: NumPy/SciPy, notebooks, conda/pixi/mamba, JAX/PyTorch, and data-heavy testing
   patterns.
4. **Python version strategy**: guidance on Python 3.9 vs 3.10 vs 3.11 vs 3.12+ syntax and compatibility.
5. **Security scanning**: integrate bandit, pip-audit, safety, dependency review, or secret scanning guidance.
6. **CI template generation**: generate `.github/workflows/ci.yml` with Ruff, mypy, pytest, and build checks.
7. **Docker best practices**: Python Dockerfile optimization, slim images, multi-stage builds, and uv cache layers.
8. **Cross-platform considerations**: explicit guidance on pathlib usage, line endings, executable permissions, and
   virtual environment activation differences across Windows/macOS/Linux.
9. **Version maintenance strategy**: establish process for reviewing and updating version recommendations in templates
   to prevent stale information.
10. **Code extraction and analysis**: integrate AST-based code analysis for suggesting refactorings, identifying
    anti-patterns, and extracting metadata for project understanding.
11. **Published as an official Hermes skill**: installable via `hermes skills install`.

## Brand (future revisit)

Codename "Pyractices" — placeholder. Revisit naming when publishing.

## Anti-vision (explicitly out of scope)

- Not a linter, formatter, type checker, or test runner itself — it configures and invokes existing tools.
- Not a beginner Python course.
- Not a mandate to use uv, Ruff, mypy, pytest, `src/` layout, or Google docstrings in every repository.
- Not a framework-specific guide by default; framework variants belong in focused references or separate skills.
- Not an auto-migration tool unless the user explicitly asks for migration planning or implementation.
