# Research Folder

This folder records research for the `python-best-practices` Hermes skill. It is separate from the distilled planning
references:

- `research/` captures evidence, comparisons, snapshots, and design rationale.
- `references/` holds distilled planning guidance and source indexes.
- `skill/` holds the canonical runtime Hermes skill payload and focused runtime references.

## Files

| File                                     | Purpose                                                                                                                              |
| :--------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| `cross-ecosystem-agent-instructions.md`  | Comparison of how strong agent-instruction ecosystems structure Python and repo best-practice guidance.                              |
| `cross-ecosystem-skill-strategy.md`      | 2026-06-03 synthesis of agent-instruction ecosystems, public examples, Python-source caveats, and the recommended skill strategy.    |
| `hermes-skill-patterns.md`               | Design implications for converting research into a Hermes skill.                                                                     |
| `requirements-txt-role.md`               | Evidence on when `requirements.txt` is still useful alongside `pyproject.toml` and lockfiles.                                        |
| `python-gitignore-templates.md`          | Evidence for reviewing Python `.gitignore` files against GitHub's maintained template and gitignore.org/Toptal's generated template. |
| `tooling-version-snapshot-2026-06-04.md` | Live GitHub/PyPI snapshot used to revalidate Phase 0 tooling claims.                                                                 |
| `code-extraction/best-practices.md`      | Best practices for extracting, analyzing, and working with code in Python applications.                                              |

## Current conclusion

The best ecosystems do not try to encode every best practice in one giant prompt. They combine:

1. a short repo-local entry point,
2. explicit commands for build/test/lint/type-check,
3. project-specific conventions,
4. safety and escalation rules,
5. progressive disclosure into focused rule/reference files.

That maps well to a Hermes skill: keep `SKILL.md` concise as a router and operating contract, then link to focused
reference files for project orientation, pyproject templates, lint/format/type/test workflows, and review checklists.

The mature-repo dogfood strategy used `/home/sand/projects/ai-project-governance` after controlled evals as a
preservation-first review target rather than as the first test case. The report is recorded in
`evals/mature-repo-dogfood-ai-project-governance-2026-06-04.md`.
