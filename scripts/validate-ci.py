#!/usr/bin/env python3
"""Validate CI routing contracts that keep checks deterministic and complete."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/ci.yml"
RELEASE_WORKFLOW = ROOT / ".github/workflows/release.yml"
SHA_PIN_RE = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
EXACT_VERSION_RE = re.compile(r"^[0-9]+(?:\.[0-9]+){2}$")
RUFF_INSTALL_COMMAND = "uv sync --locked"
RELEASE_CHECK_COMMAND = (
    "python3 scripts/check-version-consistency.py --require-github-release"
)
HYGIENE_CHECK_COMMAND = "python3 scripts/check-repo-hygiene.py"
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
    "uv run --locked ty check scripts .github/scripts",
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


CHECKOUT_USE_RE = re.compile(r"^\s*(?:-\s+)?uses:\s*actions/checkout@")


def persisted_checkout_steps(workflow: str) -> list[int]:
    """Return the 1-based line numbers of checkout steps that keep the token.

    A checkout leaves the job's ``GITHUB_TOKEN`` in the runner's ``.git/config``
    unless the step opts out, so the credential outlives the step that needed
    it and is readable by anything that runs later in the job. SECURITY.md
    promises that no workflow here persists credentials; this turns that promise
    into something a push can fail on.
    """
    lines = workflow.splitlines()
    persisted: list[int] = []
    for index, line in enumerate(lines):
        if not CHECKOUT_USE_RE.match(line):
            continue
        indent = len(line) - len(line.lstrip())
        block: list[str] = []
        for follower in lines[index + 1 :]:
            if not follower.strip():
                block.append(follower)
                continue
            follower_indent = len(follower) - len(follower.lstrip())
            starts_step = follower.lstrip().startswith("- ")
            if follower_indent < indent or (starts_step and follower_indent <= indent):
                break
            block.append(follower)
        # A commented-out setting is not a setting, so comments never satisfy it.
        settings = [entry for entry in block if not entry.lstrip().startswith("#")]
        if not any("persist-credentials: false" in entry for entry in settings):
            persisted.append(index + 1)
    return persisted


def no_persisted_credentials(workflow: str, label: str) -> list[str]:
    """Report every checkout in ``workflow`` that leaves credentials persisted."""
    return [
        f"{label}: checkout at line {line} must set 'persist-credentials: false'"
        for line in persisted_checkout_steps(workflow)
    ]


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


LOCKED_TOOLS = ("ruff", "ty")


def check_tool_pins(root: Path, errors: list[str]) -> None:
    """The lockfile, not a workflow string, must pin each enforced tool.

    Dependabot has no package ecosystem that reads a bare workflow variable,
    so a version kept in one is invisible to every update mechanism and only
    changes when a human edits the workflow. Both the linter and the type
    checker are enforced in CI, so both need a pin the `uv` ecosystem can
    raise; otherwise dropping one from the lockfile would silently leave CI
    running an unpinned version.
    """
    lock = root / "uv.lock"
    if not lock.is_file():
        errors.append("uv.lock: missing; every enforced tool must be pinned in the lockfile")
        return
    text = lock.read_text(encoding="utf-8")
    for tool in LOCKED_TOOLS:
        match = re.search(rf'(?m)^name = "{tool}"\nversion = "([^"]+)"', text)
        if match is None:
            errors.append(f"uv.lock: no {tool} entry pinning the {tool} version")
        elif not EXACT_VERSION_RE.fullmatch(match.group(1)):
            errors.append(f"uv.lock: {tool} version {match.group(1)!r} is not an exact three-part version")


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

    check_tool_pins(root, errors)

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

    hygiene = section_body(workflow, "repo-hygiene")
    if hygiene is None:
        errors.append("ci.yml: missing the repo-hygiene job")
    else:
        for line in (
            "if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'",
            "runs-on: ubuntu-latest",
            "pull-requests: read",
        ):
            if line not in hygiene:
                errors.append(f"ci.yml: repo-hygiene job missing {line!r}")
        if not has_run_command(hygiene, HYGIENE_CHECK_COMMAND):
            errors.append("ci.yml: repo-hygiene job missing its hygiene check")
        if "matrix:" in hygiene:
            errors.append("ci.yml: repo-hygiene job must not use a matrix")

    if active.count(HYGIENE_CHECK_COMMAND) != 1:
        errors.append("ci.yml: hygiene check must appear exactly once")

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

    errors.extend(no_persisted_credentials(workflow, "ci.yml"))

    return errors


def validate_release_workflow(workflow: str) -> list[str]:
    errors: list[str] = []
    if "permissions:\n  contents: read\n" not in workflow:
        errors.append("release.yml: workflow must default to contents: read")
    preflight = section_body(workflow, "verify-release-tag")
    release = section_body(workflow, "release")
    if preflight is None:
        errors.append("release.yml: missing read-only verify-release-tag job")
    else:
        for required in (
            "fetch-depth: 0",
            "persist-credentials: false",
            "--expected-tag \"$GITHUB_REF_NAME\"",
            'git merge-base --is-ancestor "${GITHUB_REF_NAME}^{}" origin/main',
        ):
            if required not in preflight:
                errors.append(f"release.yml: verify-release-tag missing {required!r}")
    if release is None:
        errors.append("release.yml: missing release job")
    else:
        for required in (
            "needs: verify-release-tag",
            "permissions:",
            "contents: write",
            "persist-credentials: false",
            'gh release create "$GITHUB_REF_NAME" --verify-tag --generate-notes',
        ):
            if required not in release:
                errors.append(f"release.yml: release job missing {required!r}")
    return errors


def main() -> int:
    errors = validate_workflow(WORKFLOW.read_text(encoding="utf-8"))
    errors.extend(validate_release_workflow(RELEASE_WORKFLOW.read_text(encoding="utf-8")))
    # ci.yml is already covered above; skip it so a violation is not reported twice.
    for path in sorted((ROOT / ".github/workflows").glob("*.y*ml")):
        if path == WORKFLOW:
            continue
        errors.extend(
            no_persisted_credentials(path.read_text(encoding="utf-8"), path.name)
        )
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("PASS: CI validation gates, routing, and action pins are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
