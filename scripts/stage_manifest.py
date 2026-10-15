#!/usr/bin/env python3
"""Single source of truth for the repository's verification stage lists.

The same checks are declared in five places: the CI `validate` job, a newly
split CI `lint` job, the CI policy validator, both git hooks, and the README.
The two Python consumers import these tuples instead of restating them, so the
validators cannot drift from each other and a stage is added or renamed in one
edit. The YAML, POSIX-shell, and prose copies must stay literal -- GitHub, the
shell, and a rendered document each need the command text itself -- and
`validate-ci.py` and `check-hook-integrity.py` fail when a literal copy loses a
stage declared here.

This module carries data only; it has no `main` and is never run directly.
"""

from __future__ import annotations

# Every interpreter-dependent check the CI `validate` job must run, in the
# order the workflow lists them. Each runs under the advertised Python matrix.
REQUIRED_VALIDATE_COMMANDS: tuple[str, ...] = (
    "python3 .github/scripts/check-portability.py",
    "python3 .github/scripts/check-portability.py --self-test",
    "python3 scripts/check-version-consistency.py",
    "python3 scripts/check-readme-tree.py",
    "python3 scripts/check-expiry.py",
    "python3 scripts/validate-ci.py",
    "python3 scripts/check-hook-integrity.py",
    "python3 scripts/check-hook-integrity.py --self-test",
    "python3 scripts/validate.py",
    "python3 scripts/test-validate-ci.py",
    "python3 scripts/test-validate.py",
    "python3 scripts/test-sync-payload.py",
    "python3 scripts/run-codex-regression.py --self-test",
    "python3 scripts/run-hermes-regression.py --self-test",
    "python3 scripts/grade-codex-regression.py --self-test",
    "bash scripts/sync-payload.sh --ci",
)

# The toolchain checks the CI `lint` job runs once, not once per matrix leg:
# Ruff, ty, and shellcheck read source text and do not depend on the
# interpreter under test, so running them per Python version is wasted work.
LINT_JOB_COMMANDS: tuple[str, ...] = (
    "uv run --locked ruff check scripts .github/scripts",
    "uv run --locked ty check scripts .github/scripts",
    "shellcheck scripts/*.sh .githooks/*",
)

# The commands each git hook must keep running. `check-hook-integrity.py` fails
# when a hook loses one, so a truncated hook cannot quietly reduce coverage.
PRE_COMMIT_STAGES: tuple[str, ...] = (
    "uv run --locked ruff check scripts .github/scripts",
    "uv run --locked ty check scripts .github/scripts",
    "python3 .github/scripts/check-portability.py",
    "python3 scripts/validate.py",
    "python3 scripts/check-expiry.py",
    "python3 scripts/check-version-consistency.py",
    "python3 scripts/check-readme-tree.py",
    "python3 scripts/check-hook-integrity.py",
)

PRE_PUSH_STAGES: tuple[str, ...] = (
    "uv run --locked ruff check scripts .github/scripts",
    "uv run --locked ty check scripts .github/scripts",
    "shellcheck scripts/*.sh .githooks/*",
    "python3 scripts/validate-ci.py",
    "python3 scripts/test-validate-ci.py",
    "python3 scripts/validate.py",
    "python3 scripts/test-validate.py",
    "python3 .github/scripts/check-portability.py",
    "python3 .github/scripts/check-portability.py --self-test",
    "python3 scripts/check-readme-tree.py",
    "python3 scripts/check-version-consistency.py",
    "python3 scripts/check-expiry.py",
    "python3 scripts/verify-urls.py --self-test",
    "python3 scripts/check-repo-hygiene.py --self-test",
    "python3 scripts/test-sync-payload.py",
    "bash scripts/sync-payload.sh --ci",
    "python3 scripts/run-codex-regression.py --self-test",
    "python3 scripts/run-hermes-regression.py --self-test",
    "python3 scripts/grade-codex-regression.py --self-test",
    "python3 scripts/check-hook-integrity.py",
    "python3 scripts/check-hook-integrity.py --self-test",
)
