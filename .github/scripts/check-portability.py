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
    ("Hermes config path", re.compile(r"~/\\.hermes(?:/|\b)", re.IGNORECASE)),
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


def main() -> int:
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