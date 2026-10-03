#!/usr/bin/env python3
"""Validate CI routing contracts that keep checks deterministic and complete."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/ci.yml"
SHA_PIN_RE = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
EXACT_VERSION_RE = re.compile(r"^[0-9]+(?:\.[0-9]+){2}$")
RUFF_INSTALL_COMMAND = "uv sync --locked"
REQUIRED_VALIDATE_COMMANDS = (
    "python3 .github/scripts/check-portability.py",
    "python3 scripts/check-version-consistency.py",
    "python3 scripts/check-readme-tree.py",
    "python3 scripts/validate-ci.py",
    "python3 scripts/validate.py",
    "python3 scripts/test-validate-ci.py",
    "python3 scripts/test-sync-payload.py",
    "python3 scripts/run-codex-regression.py --self-test",
    "python3 scripts/run-hermes-regression.py --self-test",
    "python3 scripts/grade-codex-regression.py --self-test",
    "bash scripts/sync-payload.sh --ci",
    "uv run --locked ruff check scripts .github/scripts",
    "shellcheck scripts/*.sh .githooks/*",
)


def section_body(workflow: str, name: str) -> str | None:
    match = re.search(
        rf"(?ms)^  {re.escape(name)}:\n(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
        workflow,
    )
    return match.group("body") if match else None


def active_workflow_lines(workflow: str) -> str:
    """Remove comment-only lines before applying policy checks."""
    return "\n".join(
        line for line in workflow.splitlines() if not line.lstrip().startswith("#")
    )


def has_run_command(body: str, command: str) -> bool:
    return bool(
        re.search(
            rf"(?m)^\s*run:\s*{re.escape(command)}\s*(?:#.*)?$",
            body,
        )
    )


def check_ruff_pin(root: Path, errors: list[str]) -> None:
    """The lockfile, not a workflow string, must pin the linter.

    Dependabot has no package ecosystem that reads a bare workflow variable,
    so a version kept in one is invisible to every update mechanism and only
    changes when a human edits the workflow.
    """
    lock = root / "uv.lock"
    if not lock.is_file():
        errors.append("uv.lock: missing; Ruff must be pinned in the lockfile")
        return
    match = re.search(r'(?m)^name = "ruff"\nversion = "([^"]+)"', lock.read_text(encoding="utf-8"))
    if match is None:
        errors.append("uv.lock: no ruff entry pinning the linter version")
    elif not EXACT_VERSION_RE.fullmatch(match.group(1)):
        errors.append(f"uv.lock: ruff version {match.group(1)!r} is not an exact three-part version")


def validate_workflow(workflow: str, root: Path = ROOT) -> list[str]:
    active = active_workflow_lines(workflow)
    errors: list[str] = []

    push = section_body(active, "push")
    pull_request = section_body(active, "pull_request")
    if push is None:
        errors.append("ci.yml: missing push event")
    elif re.search(r"(?m)^\s*paths(?:-ignore)?:", push):
        errors.append("ci.yml: push must not use path filters")
    if pull_request is None:
        errors.append("ci.yml: missing pull_request event")
    elif re.search(r"(?m)^\s*paths(?:-ignore)?:", pull_request):
        errors.append("ci.yml: pull_request must not use path filters")

    check_ruff_pin(root, errors)

    validate = section_body(active, "validate")
    external = section_body(active, "verify-urls")
    if validate is None:
        errors.append("ci.yml: missing validate job")
    else:
        if "verify-urls.py" in validate:
            errors.append(
                "ci.yml: live URL checks must not run in the validation matrix"
            )
        for command in REQUIRED_VALIDATE_COMMANDS:
            if not has_run_command(validate, command):
                errors.append(
                    f"ci.yml: validation matrix missing run command {command!r}"
                )
        if not has_run_command(validate, RUFF_INSTALL_COMMAND):
            errors.append(
                "ci.yml: validation matrix must install dependencies from the lockfile"
            )
        if re.search(r"\bpip\s+install\s+--upgrade\s+pip\b", validate):
            errors.append(
                "ci.yml: validation matrix must not install an unpinned latest pip"
            )
        if 'python-version: ["3.10", "3.14"]' not in validate:
            errors.append(
                "ci.yml: Python matrix must test the advertised 3.10 lower bound and 3.14 stable boundary"
            )

    if external is None:
        errors.append("ci.yml: missing verify-urls job")
    else:
        required = (
            "if: github.event_name == 'schedule'"
            " || github.event_name == 'workflow_dispatch'"
            " || github.event_name == 'pull_request'",
            "runs-on: ubuntu-latest",
        )
        for line in required:
            if line not in external:
                errors.append(f"ci.yml: verify-urls job missing {line!r}")
        if not has_run_command(external, "python3 scripts/verify-urls.py"):
            errors.append("ci.yml: verify-urls job missing its URL verifier command")
        if "matrix:" in external:
            errors.append("ci.yml: verify-urls job must not use a matrix")

    if active.count("scripts/verify-urls.py") != 1:
        errors.append("ci.yml: URL verifier must appear exactly once")


    uses = re.findall(r"(?m)^\s*(?:-\s+)?uses:\s*([^#\s]+)", active)
    if not uses:
        errors.append("ci.yml: workflow must declare its external actions explicitly")
    for reference in uses:
        if reference.startswith("./"):
            continue
        if not SHA_PIN_RE.fullmatch(reference):
            errors.append(
                f"ci.yml: action reference must use a full commit SHA: {reference}"
            )

    return errors


def main() -> int:
    errors = validate_workflow(WORKFLOW.read_text(encoding="utf-8"))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("PASS: CI validation gates, routing, and action pins are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
