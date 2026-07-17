#!/usr/bin/env python3
"""Check that the README repo-layout tree matches tracked files."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

TREE_SECTION_RE = re.compile(
    r"^## Repo Layout\n+```text\n(?P<tree>.*?)\n```",
    re.MULTILINE | re.DOTALL,
)

# Tree entry: optional indent (groups of 4 chars: '│   ' or '    '), a branch
# marker '├── ' or '└── ', the entry name, and an optional '# comment'.
TREE_ENTRY_RE = re.compile(
    r"^(?P<indent>(?:[│ ]   )*)(?P<branch>[├└]──[─ ])(?P<name>[^#\n]+?)(?:\s*#.*)?$"
)


def get_tracked_files() -> set[str]:
    """Return the set of all tracked file paths, relative to repo root."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            check=True,
            cwd=ROOT,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: could not list git files: {exc}", file=sys.stderr)
        sys.exit(1)
    return {line for line in result.stdout.splitlines() if line}


def parse_tree_paths(tree_text: str) -> set[str]:
    """Parse the ASCII tree and return the set of file paths declared.

    Each indent level is exactly 4 characters ('│   ' or '    ').
    Directory entries end with '/'; file entries are collected.
    """
    paths: set[str] = set()
    dir_stack: list[str] = []

    for line in tree_text.splitlines():
        m = TREE_ENTRY_RE.match(line)
        if not m:
            continue

        raw_indent = m.group("indent")
        name = m.group("name").strip()

        # One indent level is 4 chars — count them
        depth = len(raw_indent) // 4

        # Trim directory stack to current depth
        while len(dir_stack) > depth:
            dir_stack.pop()

        if name.endswith("/"):
            # Directory entry
            dir_name = name.rstrip("/")
            if len(dir_stack) <= depth:
                dir_stack.append(dir_name)
            else:
                dir_stack[depth] = dir_name
                dir_stack = dir_stack[: depth + 1]
        else:
            # File entry — skip wildcards like *.md
            if "*" in name:
                # Generate matching files from the filesystem
                dir_path = "/".join(dir_stack) + ("/" if dir_stack else "")
                match_path = ROOT / dir_path
                if match_path.exists():
                    for f in sorted(match_path.glob(name)):
                        rel = f.relative_to(ROOT).as_posix()
                        paths.add(rel)
                continue
            full_path = "/".join(dir_stack) + ("/" if dir_stack else "") + name
            paths.add(full_path)

    return paths


def main() -> int:
    if not README.exists():
        print("FAIL: README.md not found", file=sys.stderr)
        return 1

    readme_text = README.read_text(encoding="utf-8")

    m = TREE_SECTION_RE.search(readme_text)
    if not m:
        print("FAIL: could not find ## Repo Layout section with ```text tree in README", file=sys.stderr)
        return 1

    tracked = get_tracked_files()
    declared = parse_tree_paths(m.group("tree"))

    stale = declared - tracked
    omitted = tracked - declared

    if stale:
        for f in sorted(stale):
            print(f"STALE: {f}  (in README tree but not tracked)")
    if omitted:
        for f in sorted(omitted):
            print(f"OMITTED: {f}  (tracked but not in README tree)")

    if stale or omitted:
        print()
        print("FAIL: README repo-layout tree does not match tracked files", file=sys.stderr)
        return 1

    print("PASS: README repo-layout tree matches tracked files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
