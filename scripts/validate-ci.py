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
RELEASE_CHECK_COMMAND = (
    "python3 scripts/check-version-consistency.py --require-github-release"
)
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


BLOCK_SCALAR_SUFFIXES = ("|", ">", "|-", ">-", "|+", ">+")
KEY_RE = re.compile(r"([A-Za-z0-9_-]+):(.*)$")


def duplicate_keys(workflow: str) -> list[str]:
    """Report mapping keys that repeat inside the same block.

    GitHub refuses to load a workflow file whose mapping repeats a key, and
    the failure is total and indirect: every run on the branch is marked
    failed with "This run likely failed because of a workflow file issue" and
    no step executes, so nothing names the offending line. A YAML loader does
    not help either, because it accepts a repeated key and keeps the last
    value silently. That is how a duplicated `with:` reached this repository's
    main branch and stayed there unnoticed for a session.

    Blocks are identified by their enclosing key path, and a list item
    contributes its index so sibling steps never collide. Keys inside a
    block scalar are not keys at all, so they are skipped.
    """
    errors: list[str] = []
    stack: list[tuple[int, str]] = []
    counters: dict[int, int] = {}
    seen: dict[tuple[str, ...], int] = {}
    block_indent = -1
    for number, raw in enumerate(workflow.splitlines(), start=1):
        if block_indent >= 0:
            if raw.strip() and (len(raw) - len(raw.lstrip())) > block_indent:
                continue
            block_indent = -1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        body = raw.lstrip()
        item = body.startswith("- ")
        if item:
            body = body[2:]
        match = KEY_RE.match(body)
        if match is None:
            continue
        key, value = match.group(1), match.group(2).strip()
        while stack and stack[-1][0] >= indent:
            stack.pop()
        path = tuple(entry[1] for entry in stack)
        if item:
            counters[indent] = counters.get(indent, 0) + 1
            # A sentinel one column in from the dash keeps the item scope
            # alive for the keys that follow it without being popped by them.
            scope = f"[{counters[indent]}]"
            path = path + (scope,)
            stack.append((indent + 1, scope))
        full = path + (key,)
        first = seen.get(full)
        if first is None:
            seen[full] = number
        else:
            errors.append(
                f"ci.yml: duplicate key {key!r} at line {number}, "
                f"already set at line {first}"
            )
        if value in BLOCK_SCALAR_SUFFIXES:
            block_indent = indent
        elif not value:
            stack.append((indent, key))
    return errors


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

    errors.extend(duplicate_keys(workflow))

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

    published = section_body(active, "release-integrity")
    if published is None:
        errors.append("ci.yml: missing release-integrity job")
    else:
        # The release procedure is otherwise unverified: nothing else in this
        # repository consults GitHub Releases, so a tag can stand unpublished
        # until someone reads the checklist by hand.
        for line in (
            "if: github.event_name == 'schedule'"
            " || github.event_name == 'workflow_dispatch'",
            "runs-on: ubuntu-latest",
            "fetch-depth: 0",
            "GH_TOKEN: ${{ github.token }}",
        ):
            if line not in published:
                errors.append(f"ci.yml: release-integrity job missing {line!r}")
        if not has_run_command(published, RELEASE_CHECK_COMMAND):
            errors.append(
                "ci.yml: release-integrity job missing its published-release check"
            )
        if "matrix:" in published:
            errors.append("ci.yml: release-integrity job must not use a matrix")

    if active.count(RELEASE_CHECK_COMMAND) != 1:
        errors.append("ci.yml: published-release check must appear exactly once")

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
