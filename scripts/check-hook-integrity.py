#!/usr/bin/env python3
"""Fail when a git hook loses a check stage or a tracked file leaks a redaction marker.

On 2026-10-04 a repair had to restore `===` banner strings in `.githooks/*`,
`.github/workflows/ci.yml`, `pyproject.toml`, and the shipped references after a
redaction pass rewrote them to a removal placeholder in place. The marker had been
present since the first commit, and nothing in the gate reported it: `ruff` and
`ty` only inspect `scripts/` and `.github/scripts/`, so they never opened a hook,
and `shellcheck` parses shell structure without reading `echo` payloads. The
damage stayed latent until an unrelated edit made CI fail.

Two checks close that gap, and they fail differently on purpose:

* `missing_stages` compares each hook against a manifest of the commands it must
  run, so dropping or renaming a gate is an error rather than a silent reduction
  in coverage. This is the general form of the corruption: the recovery commits
  edited the hook configuration they were repairing.
* `marker_findings` scans tracked text files for redaction placeholders, so a
  marker that escapes into shipped content is reported at the boundary it
  crossed.

Stage matching is whitespace-normalized. Reflowing a long command across lines is
a formatting change and stays green; deleting the command is not.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Placeholders that indicate a redaction pass rewrote content in place. Each is
# matched literally, so a hit is a real leak rather than a documentation mention.
REDACTION_MARKERS = ("***REMOVED***", "<<REMOVED>>", "<REDACTED>", "[REDACTED]")

# The commands each hook must run. This file is excluded from its own marker scan
# because it has to name the markers it searches for.
PRE_COMMIT_STAGES = (
    "uv run --locked ruff check scripts .github/scripts",
    "uv run --locked ty check scripts .github/scripts",
    "python3 .github/scripts/check-portability.py",
    "python3 scripts/validate.py",
    "python3 scripts/check-expiry.py",
    "python3 scripts/check-version-consistency.py",
    "python3 scripts/check-readme-tree.py",
    "python3 scripts/check-hook-integrity.py",
)

PRE_PUSH_STAGES = (
    "uv run --locked ruff check scripts .github/scripts",
    "uv run --locked ty check scripts .github/scripts",
    "shellcheck scripts/*.sh .githooks/*",
    "python3 scripts/validate-ci.py",
    "python3 scripts/test-validate-ci.py",
    "python3 scripts/validate.py",
    "python3 .github/scripts/check-portability.py",
    "python3 scripts/check-readme-tree.py",
    "python3 scripts/check-version-consistency.py",
    "python3 scripts/check-expiry.py",
    "python3 scripts/check-repo-hygiene.py --self-test",
    "python3 scripts/test-sync-payload.py",
    "bash scripts/sync-payload.sh --ci",
    "python3 scripts/run-codex-regression.py --self-test",
    "python3 scripts/run-hermes-regression.py --self-test",
    "python3 scripts/grade-codex-regression.py --self-test",
    "python3 scripts/check-hook-integrity.py",
    "python3 scripts/check-hook-integrity.py --self-test",
)

HOOKS: dict[str, tuple[str, ...]] = {
    ".githooks/pre-commit": PRE_COMMIT_STAGES,
    ".githooks/pre-push": PRE_PUSH_STAGES,
}


# --------------------------------------------------------------------------
# Pure checks. Each takes already-collected data so it can be self-tested.
# --------------------------------------------------------------------------


def normalize(text: str) -> str:
    """Collapse every whitespace run to one space so reflowed lines still match."""
    return " ".join(text.split())


def missing_stages(body: str, stages: tuple[str, ...]) -> list[str]:
    """Manifest stages the hook body no longer runs."""
    flat = normalize(body)
    return [stage for stage in stages if normalize(stage) not in flat]


def marker_findings(name: str, text: str) -> list[str]:
    """Redaction placeholders that must not survive into tracked content."""
    hits = sorted({marker for marker in REDACTION_MARKERS if marker in text})
    return [f"{name} contains redaction marker {marker}" for marker in hits]


# --------------------------------------------------------------------------
# Collection
# --------------------------------------------------------------------------


def tracked_text(root: Path) -> dict[str, str]:
    """Map every tracked UTF-8 file to its text. Binary files are out of scope.

    Paths come from the index, contents from the working tree, so the check sees
    unstaged edits too. That is the stricter reading for a pre-commit hook and
    matches CI, where the two are the same.
    """
    done = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode != 0:
        return {}
    texts: dict[str, str] = {}
    for entry in done.stdout.split("\0"):
        if not entry:
            continue
        try:
            texts[entry] = (root / entry).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
    return texts


def check_hooks(texts: dict[str, str]) -> list[str]:
    """Every hook must exist and still run its manifest."""
    errors: list[str] = []
    for hook, stages in HOOKS.items():
        body = texts.get(hook)
        if body is None:
            errors.append(f"{hook} is not a readable tracked file")
            continue
        errors.extend(f"{hook} no longer runs {stage}" for stage in missing_stages(body, stages))
    return errors


def check_markers(texts: dict[str, str], root: Path) -> list[str]:
    """No tracked file may carry a redaction placeholder, except this one."""
    this_file = Path(__file__).resolve()
    errors: list[str] = []
    for name, body in texts.items():
        if (root / name).resolve() == this_file:
            continue
        errors.extend(marker_findings(name, body))
    return errors


def run_self_tests() -> None:
    """Exercise each pure check with a known input and a known expectation."""
    stages = ("ruff check", "ty check")
    both = "uv run --locked ruff check scripts\nuv run --locked ty check scripts"
    assert missing_stages(both, stages) == []
    # Removing a stage is a coverage loss and must be reported, not tolerated.
    assert missing_stages("uv run --locked ruff check scripts", stages) == ["ty check"]
    # Reflowing a command across lines stays green; only deletion is a fault.
    assert missing_stages("uv run --locked   ruff\n  check scripts\nty check", stages) == []
    assert missing_stages("", stages) == ["ruff check", "ty check"]

    assert marker_findings("clean.md", "echo '=== pre-commit: ruff check ==='\n") == []
    # The observed incident: a redaction pass rewrote an `===` banner in place.
    assert marker_findings(".githooks/pre-commit", 'echo "***REMOVED***= banner ***REMOVED***="') == [
        ".githooks/pre-commit contains redaction marker ***REMOVED***"
    ]
    # Several hits of one marker in one file collapse to a single finding.
    assert len(marker_findings("dup.md", "***REMOVED*** a ***REMOVED*** b")) == 1
    assert len(marker_findings("multi.md", "<<REMOVED>> and [REDACTED]")) == 2
    # An empty file is clean: absence of content is not a leak.
    assert marker_findings("empty.md", "") == []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail when a git hook loses a check stage or a tracked file leaks a redaction marker."
    )
    parser.add_argument("--root", default=".", help="repository root to scan")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checks and exit")
    args = parser.parse_args()

    if args.self_test:
        run_self_tests()
        print("PASS: hook integrity self-tests")
        return 0

    root = Path(args.root).resolve()
    texts = tracked_text(root)
    if not texts:
        print("FAIL: no tracked files found; run this inside the repository", file=sys.stderr)
        return 1

    errors = check_hooks(texts) + check_markers(texts, root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        print(f"FAIL: {len(errors)} hook integrity error(s)", file=sys.stderr)
        return 1

    print(f"PASS: {len(HOOKS)} hook(s) intact and {len(texts) - 1} tracked file(s) free of markers")
    return 0


if __name__ == "__main__":
    sys.exit(main())