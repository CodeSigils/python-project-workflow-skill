#!/usr/bin/env python3
"""Validate CI routing contracts that keep push and PR checks deterministic."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/ci.yml"


def job_body(workflow: str, name: str) -> str | None:
    match = re.search(
        rf"(?ms)^  {re.escape(name)}:\n(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
        workflow,
    )
    return match.group("body") if match else None


def main() -> int:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    errors: list[str] = []

    validate = job_body(workflow, "validate")
    external = job_body(workflow, "verify-urls")
    if validate is None:
        errors.append("ci.yml: missing validate job")
    else:
        if "python3 scripts/verify-urls.py" in validate:
            errors.append(
                "ci.yml: live URL checks must not run in the validation matrix"
            )
        if "python3 scripts/validate-ci.py" not in validate:
            errors.append("ci.yml: validation matrix must run the CI policy check")
        if 'python-version: ["3.10", "3.13"]' not in validate:
            errors.append(
                "ci.yml: Python matrix must test the advertised 3.10 lower bound and 3.13 upper bound"
            )

    if external is None:
        errors.append("ci.yml: missing verify-urls job")
    else:
        required = (
            "if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'",
            "runs-on: ubuntu-latest",
            "run: python3 scripts/verify-urls.py",
        )
        for line in required:
            if line not in external:
                errors.append(f"ci.yml: verify-urls job missing {line!r}")
        if "matrix:" in external:
            errors.append("ci.yml: verify-urls job must not use a matrix")

    if workflow.count("run: python3 scripts/verify-urls.py") != 1:
        errors.append("ci.yml: URL verifier must appear exactly once")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("PASS: live URL verification is isolated from push and pull-request CI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
