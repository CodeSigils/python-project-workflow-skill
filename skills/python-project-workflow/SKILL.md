---
name: python-project-workflow
description: Set up, inspect, preserve, and verify Python project workflows, including greenfield scaffolding, packaging, dependency and tool configuration, CI, compatibility contracts, mature automation repositories, and project-native validation. Use when the task affects repository-wide Python structure or workflow. Do not use for pure code review, isolated support-script edits in otherwise non-Python repositories, or framework-specific implementation unless the request also changes project tooling or workflow.
---

# Python Project Workflow

Apply a preservation-first workflow to Python project setup, tooling, CI,
packaging, compatibility, and repository-wide verification.

Framework-specific project conventions are out of scope. For Django, FastAPI,
Flask, and similar frameworks, use dedicated framework guidance or preserve the
project's established workflow. Do not present this generic baseline as
framework-complete guidance.

## Workflow

1. Inspect repository instructions, version-control state, and project-native
   configuration before recommending or making changes.
2. Classify the repository and the requested operation.
3. Load only the references relevant to that classification.
4. Preserve coherent local conventions unless the user explicitly requests
   modernization.
5. Verify with project-native gates and report actual results.

## Repository Classification

Apply Existing and Automation before considering Greenfield. Missing packaging
metadata or tests does not make a repository greenfield when meaningful source,
scripts, documentation, or history already exist.

| Signal | Classification | Guidance |
| --- | --- | --- |
| Empty directory or explicit new-scaffold request | Greenfield | Load `references/pyproject-template.md` |
| Packaging metadata and coherent tooling | Existing project | Orient first, then load task-specific guidance |
| Python used for repository checkers or governance | Mature automation | Load `references/mature-repo-preservation.md` |
| Eval or benchmark runners | Automation with benchmarks | Also load `references/eval-benchmark-hardening.md` |

For isolated support scripts that fall outside this skill's trigger, use
repository-native instructions and focused checks. Do not infer correctness
from classification alone.

## Operation Modes

- **Inspect or advise:** use read-only discovery. Do not install dependencies,
  synchronize environments, generate files, or edit configuration.
- **Implement:** make only changes authorized by the user and preserve unrelated
  worktree changes.
- **Verify:** run already-available project-native gates first. Treat setup or
  dependency installation as a separate step when it is required.
- **Bootstrap:** create or replace project structure only for an explicit
  greenfield or modernization request.

## Orientation Checklist

Inspect only what is relevant to the task:

- Active repository instructions such as `AGENTS.md`, `CONTRIBUTING.md`, and
  framework-specific guidance.
- `git status --short --branch`, relevant diffs, and recent bounded history.
- Packaging metadata: `pyproject.toml`, `setup.py`, `setup.cfg`, build backend,
  dependencies, and lockfiles.
- Source, test, namespace-package, and CLI entry-point layout.
- Tool configuration for Ruff, MyPy, Pyright, pytest, tox, nox, pre-commit,
  Hatch, Poetry, Pixi, or project-specific scripts.
- CI workflows, supported operating systems, and Python-version matrices.
- README and developer documentation claims that form part of the workflow
  contract.

When resuming interrupted work, treat summaries and prior claims as leads.
Reconstruct state from repository facts before editing, committing, or claiming
completion.

## Python Version Contract

Determine and align:

1. The declared range in packaging metadata.
2. The effective range exercised by CI or deployment.
3. Tool targets such as Ruff's `target-version`, MyPy's `python_version`, and
   Pyright's `pythonVersion`.
4. Syntax and dependency compatibility with the minimum supported version.

Target the project-wide minimum unless configuration intentionally scopes a
newer target. Preserve an existing compatibility contract unless the user
authorizes a breaking change. Do not silently raise `requires-python` or remove
older versions from CI.

For a new compatibility recommendation, verify current interpreter lifecycle,
platform defaults, dependency support, and packaging guidance from official
sources. Do not encode point-in-time lifecycle claims as durable policy.

## Reference Routing

Load references progressively:

| Task | Reference |
| --- | --- |
| Greenfield setup, packaging, release, or CLI entry points | `references/pyproject-template.md` |
| Linting, formatting, typing, tests, or CI commands | `references/lint-format-typing-testing.md` |
| Mature repositories and automation | `references/mature-repo-preservation.md` |
| Eval or benchmark runners | `references/eval-benchmark-hardening.md` |
| `.gitignore`, secrets, credentials, or Git-history exposure | `references/security-and-gitignore.md` |
| Canonical/runtime payload or installed-copy drift | `references/drift-classes.md` |
| Escape-heavy shell, regex, or generated text | `references/safe-editing.md` |
| Compact correctness awareness outside pure review | `references/core-footguns.md` |

Use project-native gates first, then relevant skill references, then current
official tool documentation. Ask the user when a material choice remains.

## Preserve Local Conventions

For existing repositories:

- Do not impose `uv`, `src/`, Ruff, MyPy, pytest, PEP 621, or a new package
  layout when coherent alternatives already exist.
- Keep modernization separate from required fixes.
- Do not reformat unrelated code or combine broad mechanical changes with logic
  changes.
- Decide lockfile policy from the repository's application or library contract;
  do not automatically ignore, regenerate, or commit lockfiles.
- Treat project-native warnings according to their documented severity.

For greenfield or explicitly incoherent projects, a reasonable starting point
is `uv`, Ruff, MyPy, pytest, PEP 621, and a `src/` layout. Present this as a
negotiable baseline and verify compatibility with the intended deployment and
dependency ecosystem.

When canonical source has runtime, generated, or installed mirrors, edit the
canonical source first. Synchronize mirrors only through project-provided
commands, then run both source-only and mirror-aware gates.

## Sensitive-Evidence Safety

- Inspect existing `.gitignore` behavior before changing it. Preserve
  project-specific and security-related rules, including a sanitized
  `!.env.example` when used.
- Never commit credentials, access tokens, private keys, or populated secret files.
- `.gitignore` does not protect files that Git already tracks. Check tracked
  state without printing suspected secret contents.
- If sensitive material is tracked or may have entered history, stop, alert the
  user, and recommend revocation or rotation. Removing or ignoring a file does
  not erase historical exposure.
- Never include credentials, access tokens, private keys, sensitive values, or secret-bearing URLs in commit subjects or bodies.
- Inspect Git metadata with bounded, redacted queries. Do not print raw commit bodies.
- Report existence or location only. Redact secret values, sensitive URLs,
  connection strings, and identifying fragments from output and examples.
- Do not claim a repository is secret-free from filename checks or the absence
  of a regex match.
- Load `references/security-and-gitignore.md` before advising or editing around
  ignore rules, credentials, tracked sensitive files, or history exposure.

## Verification

Prefer commands already defined by CI, Make, tox, nox, task runners, or
repository scripts. Load `references/lint-format-typing-testing.md` only when
generic tool commands are needed.

Before running a command, distinguish:

- Read-only checks that inspect existing state.
- Environment setup such as `uv sync`, virtual-environment creation, or package
  installation.
- Generators or fixers that can modify source, configuration, or lockfiles.

Run setup and mutating verification only when authorized and necessary. Do not
claim a full suite is green when only a focused check ran.

When no canonical gate covers changed behavior, create a focused temporary
verifier under `/tmp` only when it adds meaningful evidence. Name it with a
`py-workflow-verify-` prefix, exercise the smallest relevant pass and fail
paths, remove it afterward when practical, and report it as ad-hoc
verification.

Re-run verification when later edits can affect the behavior or contract
already checked. Match documentation-only changes with documentation checks;
do not create a new behavioral harness solely because an unrelated comment or
example changed.

For escape-heavy edits, load `references/safe-editing.md` and use a focused
byte-level diagnostic where relevant.

## Reporting

Report:

- Repository and operation classification.
- Files changed or reviewed.
- Verification commands and observed results.
- Skipped checks and remaining risks.
- A concise next step when work remains.

Do not invent success or hide failures behind unrelated passing checks.
