# Phase 2 Mature-Repo Dogfood: ai-project-governance

**Date:** 2026-06-04 **Target:** `/home/sand/projects/ai-project-governance` **Mode:** read-only review; no target files
edited **Purpose:** Test whether `python-best-practices` preserves a mature repository's existing conventions instead of
forcing the greenfield baseline.

## Classification

- Python task type: existing mature-repo review
- Skill behavior under test: ORIENT → CLASSIFY → LOAD FOCUSED REFERENCE → ADVISE/EDIT → VERIFY → REPORT
- Target project classification: coherent existing toolchain, not greenfield
- Modernization authorization: not authorized
- Target side effects: none

## Target repo state observed

`git status --short --branch` in the target reported:

```text
## main...origin/main [ahead 3]
 M README.md
 M scripts/check-consistency.sh
 M scripts/check_current_claims.py
 M tests/test_repository_consistency_checker.py
?? tests/test_amendment_checks.py
```

This means the dogfood ran against a dirty worktree with pre-existing local changes. The review therefore treated the
target as read-only and did not modify, stage, commit, install, sync, push, publish, or release anything in that
repository.

## Detected stack and conventions

Machine observations:

- No `pyproject.toml`, `setup.py`, `setup.cfg`, `tox.ini`, `noxfile.py`, `requirements*.txt`, `uv.lock`, or
  `poetry.lock` were present at the target root.
- Python exists as repository automation, not as a packaged Python application/library:
  - `project-governance-init/generate.py`
  - `scripts/check_current_claims.py`
  - `scripts/check_docs.py`
  - `scripts/generate-research-index.py`
  - `scripts/governance-ledger.py`
  - `scripts/ledgerctl.py`
  - `scripts/ledgerlib.py`
  - `tests/*.py`
- The authoritative project gate is `bash scripts/check-consistency.sh`, not a generic Python-only command.
- The test suite is run directly with `python3 -m pytest tests -q`.
- The repository has a strong `AGENTS.md` lifecycle contract requiring orientation, classification, evidence grounding,
  machine-truth verification, and side-effect boundaries.
- `.gitignore` already covers common Python generated artifacts (`__pycache__/`, `*.py[cod]`, `.pytest_cache/`,
  `.mypy_cache/`, `.ruff_cache/`, `.tox/`, `.venv/`, `venv/`) plus Hermes/OpenCode/OpenMem/session scratch state.

## Verification evidence from target

Commands run in `/home/sand/projects/ai-project-governance`:

```bash
bash scripts/check-consistency.sh
python3 -m pytest tests -q
python3 -m compileall -q project-governance-init scripts tests
```

Observed results:

```text
bash scripts/check-consistency.sh
=> PASS  All checks passed.
```

The checker emitted expected WARN-level governance audit notes:

```text
WARN  plan-vs-research-audit.md: 0 ❌ gaps, 3 ⚠️ warnings — review before material governance changes.
WARN: AMD-006: ledger says evidence_quality='operational' but table says 'N/A (verification mechanism)'
WARN: AMD-013: ledger says evidence_quality='operational' but table says 'N/A (structural reorganization)'
WARN: AMD-017: ledger says evidence_quality='operational' but table says 'N/A (schema standardization)'
WARN: AMD-004: amendment file signals 'design-innovation' but ledger says evidence_quality='well-backed'
WARN: AMD-005: amendment file signals 'design-innovation' but ledger says evidence_quality='well-backed'
WARN: AMD-007: amendment file signals 'design-innovation' but ledger says evidence_quality='well-backed'
WARN: AMD-010: amendment file signals 'design-innovation' but ledger says evidence_quality='well-backed'
WARN: AMD-012: amendment file signals 'operational' but ledger says evidence_quality='well-backed'
WARN: AMD-014: amendment file signals 'design-innovation' but ledger says evidence_quality='partially-backed'
WARN: AMD-023: amendment file signals 'design-innovation' but ledger says evidence_quality='well-backed'
WARN: AMD-026: amendment file signals 'design-innovation' but ledger says evidence_quality='partially-backed'
```

These warnings did not fail the target gate.

```text
python3 -m pytest tests -q
=> 161 passed in 10.69s

python3 -m compileall -q project-governance-init scripts tests
=> exit 0
```

## Python best-practice assessment

The skill behaved correctly for a mature repo:

1. It did not recommend forcing `uv`, `src/`, `pyproject.toml`, Ruff, or strict MyPy onto a coherent governance
   repository.
2. It discovered and used the project-native verification gate first.
3. It treated Python as implementation/support automation inside a governance project, not as evidence that the repo
   must become a packaged Python distribution.
4. It preserved the target repository's side-effect boundary while its worktree was dirty.
5. It surfaced Python-specific observations only as incremental suggestions.

## Safe improvement candidates

These are optional, not blockers:

1. Document the Python interpreter expectation explicitly.
   - Current scripts use Python 3.11+ features such as `tomllib` and modern type syntax.
   - If this repo remains intentionally non-packaged, a short developer note may be enough.
   - A `pyproject.toml` should not be added just for aesthetics unless the project wants centralized test/tool config.

2. Consider a minimal lint/type smoke layer only if it supports existing gates.
   - The current standard-library-first scripts and `pytest` suite are already strong.
   - Ruff or MyPy adoption would be a modernization task and should be explicitly authorized, staged, and aligned with
     the governance lifecycle.

3. Keep WARN-level governance audit items visible.
   - The target checker already does this well.
   - The warnings are governance-quality feedback, not Python correctness failures.

4. Avoid package-manager migration until there is a concrete need.
   - No dependency or packaging metadata was observed.
   - Adding uv/lockfile/package metadata without a real distribution or dependency-management problem would be
     over-engineering.

## Dogfood conclusion

Pass. The `python-best-practices` workflow handled this mature repository as preservation-first. It found the native
contract and gates, avoided greenfield migration pressure, ran real verification, and produced bounded Python
recommendations without editing the target.

## Follow-up for python-best-practices skill

This dogfood supports marking the planned mature-repo review item complete, while keeping Phase 2 open until the user
gives qualitative approval (`ship it`). Phase 3 trigger-description optimization and Phase 4 handoff/publishing remain
future work.
