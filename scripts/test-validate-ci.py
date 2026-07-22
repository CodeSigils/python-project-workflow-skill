#!/usr/bin/env python3
"""Regression tests for CI policy validation."""

from __future__ import annotations

import importlib.util
import re
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
        workflow.replace('- ".gitignore"', '# - ".gitignore"'),
        "commented .gitignore shared path filter",
    )
    assert_rejected(
        module,
        workflow.replace("paths: &ci_paths", "paths:", 1),
        "missing shared path anchor",
    )
    assert_rejected(
        module,
        workflow.replace("paths: *ci_paths", "paths:", 1),
        "pull request not reusing shared path anchor",
    )
    assert_rejected(
        module,
        re.sub(
            r'RUFF_VERSION: "[^"]+"',
            'RUFF_VERSION: "latest"',
            workflow,
            count=1,
        ),
        "unpinned Ruff version variable",
    )
    assert_rejected(
        module,
        workflow.replace('"ruff==$RUFF_VERSION"', "ruff==9.9.9", 1),
        "literal Ruff version in install command",
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

    print("PASS: CI policy validator rejects missing gates, drift, and mutable pins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
