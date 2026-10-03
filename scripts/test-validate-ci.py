#!/usr/bin/env python3
"""Regression tests for CI policy validation."""

from __future__ import annotations

import importlib.util
import re
import tempfile
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate-ci.py"
WORKFLOW = ROOT / ".github/workflows/ci.yml"


def load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_ci", VALIDATOR)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_rejected(module: ModuleType, workflow: str, label: str) -> None:
    if not module.validate_workflow(workflow):
        raise AssertionError(f"CI validator accepted {label}")


def assert_lockfile_rejected(module: ModuleType, lock_text: str | None, label: str) -> None:
    """The linter pin must live in the lockfile, so mutate one and check."""
    with tempfile.TemporaryDirectory() as tmp:
        if lock_text is not None:
            (Path(tmp) / "uv.lock").write_text(lock_text, encoding="utf-8")
        errors: list[str] = []
        module.check_ruff_pin(Path(tmp), errors)
        if not errors:
            raise AssertionError(f"CI validator accepted {label}")


def main() -> int:
    module = load_validator()
    workflow = WORKFLOW.read_text(encoding="utf-8")
    errors = module.validate_workflow(workflow)
    if errors:
        raise AssertionError(f"current workflow failed validation: {errors}")

    for command in module.REQUIRED_VALIDATE_COMMANDS:
        assert_rejected(
            module,
            workflow.replace(f"run: {command}", f"# run: {command}", 1),
            f"commented critical command {command!r}",
        )

    assert_rejected(
        module,
        workflow.replace(
            "          fetch-depth: 0\n          persist-credentials: false\n",
            "          fetch-depth: 0\n        with:\n          persist-credentials: false\n",
            1,
        ),
        "a duplicated step mapping key",
    )
    assert_rejected(
        module,
        workflow.replace(
            "    runs-on: ubuntu-latest\n",
            "    runs-on: ubuntu-latest\n    runs-on: ubuntu-latest\n",
            1,
        ),
        "a duplicated job mapping key",
    )
    assert_rejected(
        module,
        workflow.replace("    branches: [main]", "    branches: [main]\n    paths: [\"scripts/**\"]", 1),
        "push path filter",
    )
    assert_rejected(
        module,
        workflow.replace(
            "  pull_request:\n    branches: [main]",
            "  pull_request:\n    branches: [main]\n    paths-ignore: [\"docs/**\"]",
            1,
        ),
        "pull request path filter",
    )
    lock = (ROOT / "uv.lock").read_text(encoding="utf-8")
    assert_lockfile_rejected(module, None, "a missing uv.lock")
    assert_lockfile_rejected(
        module,
        '[[package]]\nname = "unrelated"\nversion = "1.0.0"\n',
        "a lockfile with no ruff entry",
    )
    assert_lockfile_rejected(
        module,
        lock.replace('version = "0.16.9"', 'version = "0.16.9rc1"', 1),
        "a ruff version that is not an exact three-part release",
    )
    assert_rejected(
        module,
        workflow.replace(
            f"run: {module.RUFF_INSTALL_COMMAND}",
            "run: python -m pip install --upgrade pip",
            1,
        ),
        "unpinned latest pip installation",
    )
    assert_rejected(
        module,
        workflow.replace("actions/checkout@", "actions/checkout@v5 # ", 1),
        "mutable action tag",
    )
    assert_rejected(
        module,
        workflow.replace(
            "run: python3 scripts/validate.py",
            "run: python3 ./scripts/verify-urls.py\n\n      - run: python3 scripts/validate.py",
            1,
        ),
        "live URL check in validation matrix",
    )

    dropped_job = re.sub(
        r"(?ms)^  release-integrity:\n.*?(?=^  [A-Za-z0-9_-]+:\n|\Z)", "", workflow, count=1
    )
    assert dropped_job != workflow, "release-integrity job block not found"
    assert_rejected(module, dropped_job, "a workflow with no published-release check")

    assert_rejected(
        module,
        workflow.replace("          GH_TOKEN: ${{ github.token }}\n", "", 1),
        "a published-release check with no token",
    )

    assert_rejected(
        module,
        workflow.replace(
            "          # The tag comparison needs real history: a default shallow clone has\n"
            "          # no tags, and the version check would silently pass on nothing.\n"
            "          fetch-depth: 0\n",
            "",
            1,
        ),
        "a published-release check on a shallow clone",
    )

    print("PASS: CI policy validator rejects missing gates, drift, and mutable pins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
