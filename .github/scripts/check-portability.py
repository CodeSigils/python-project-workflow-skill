#!/usr/bin/env python3
"""Check for agent-specific references in portable skill files.

Ensures python-project-workflow's runtime surface remains cross-agent
compatible. Scans both SKILL.md and references/*.md under skills/.

"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SKILLS_DIR = Path("skills")

FORBIDDEN_PATTERNS = (
    ("Hermes tool name", re.compile(r"\bskill_(?:view|manage)\b", re.IGNORECASE)),
    ("Hermes config path", re.compile(r"~/\.hermes(?:/|\b)", re.IGNORECASE)),
    (
        "Hermes CLI command",
        re.compile(
            r"\bhermes\s+(?:skills?|config|tools?|setup|help|doctor|gateway|run|serve|cron)\b",
            re.IGNORECASE,
        ),
    ),
    ("Hermes Python import", re.compile(r"from hermes_tools\b", re.IGNORECASE)),
    ("Claude Code agent reference", re.compile(r"\bClaude\(\)", re.IGNORECASE)),
    ("Gemini CLI command", re.compile(r"\bgemini\s+skills?\b", re.IGNORECASE)),
    ("Codex CLI command", re.compile(r"\bcodex\s+run\b", re.IGNORECASE)),
    (
        "Platform-specific path",
        re.compile(r"\.(?:claude|cursor|codex|opencode|gemini)/"),
    ),
)


def scan_file(path: Path) -> list[tuple[Path, int, str, str]]:
    violations: list[tuple[Path, int, str, str]] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    # File-level exemption: if any of the first 3 lines contains the exemption
    # marker, skip the entire file. This allows educational documents about
    # portability to reference platform-specific patterns.
    for i in range(min(3, len(lines))):
        if "# portability: allow-platform-ref" in lines[i]:
            return violations
    for line_no, line in enumerate(lines, start=1):
        if "# portability: allow-platform-ref" in line:
            continue
        for label, pattern in FORBIDDEN_PATTERNS:
            if pattern.search(line):
                violations.append((path, line_no, label, line.rstrip()))
    return violations


def run_self_tests() -> int:
    """Run internal self-tests for the validation logic."""
    test_cases = [
        ("skill_view(name)", True, "Hermes tool name"),
        ("SKILL_VIEW(name)", True, "Hermes tool name case insensitive"),
        ("from hermes_tools import foo", True, "Hermes Python import"),
        ("from HERMES_TOOLS import foo", True, "Hermes Python import case insensitive"),
        ("~/.hermes/config", True, "Hermes config path"),
        ("~/.hermes/", True, "Hermes config path with slash"),
        ("hermes skills install", True, "Hermes CLI command"),
        ("hermes config set", True, "Hermes CLI command"),
        ("Claude()", True, "Claude Code agent reference"),
        ("gemini skills", True, "Gemini CLI command"),
        ("codex run", True, "Codex CLI command"),
        (".claude/config", True, "Platform-specific path"),
        (".cursor/config", True, "Platform-specific path"),
        ("normal text", False, "Normal text"),
        ("skill_manage(action='create')", True, "Hermes tool name"),
    ]

    for text, should_match, label in test_cases:
        for pattern_label, pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                if not should_match:
                    print(f"FAIL: {label} matched unexpectedly: {text!r}")
                    return 1
                break
        else:
            if should_match:
                print(f"FAIL: {label} should have matched: {text!r}")
                return 1

    print("PASS: check-portability.py self-tests")
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Check for agent-specific references in portable skill files."
    )
    parser.add_argument("--self-test", action="store_true", help="Run internal self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_tests()

    violations: list[tuple[Path, int, str, str]] = []
    for path in sorted(SKILLS_DIR.rglob("*.md")):
        try:
            violations.extend(scan_file(path))
        except OSError as exc:
            print(f"FAIL: could not read {path}: {exc}", file=sys.stderr)
            return 1

    if violations:
        print("FAIL: agent-specific references found in skills/ — will break non-Hermes agents:")
        for path, line_no, label, line in violations:
            print(f"  {path}:{line_no}: {label}: {line}")
        return 1

    print("PASS: no agent-specific references in skills/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
