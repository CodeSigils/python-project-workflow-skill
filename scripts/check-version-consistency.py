#!/usr/bin/env python3
"""Check local release versions and git tags for consistency."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

LOCAL_VERSION_SOURCES: dict[str, Path] = {
    "SKILL.md": ROOT / "skills" / "python-project-workflow" / "SKILL.md",
    "CITATION.cff": ROOT / "CITATION.cff",
}


def normalize_version(version: str) -> str:
    return version.removeprefix("v")


def read_skill_version(path: Path) -> str | None:
    """Extract metadata version from SKILL.md frontmatter."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None
    frontmatter = content.split("---", 2)
    if len(frontmatter) < 3:
        return None
    match = re.search(r'(?m)^version:\s*["\']?([^"\'#\s]+)', frontmatter[1])
    return match.group(1) if match else None


def read_citation_version(path: Path) -> str | None:
    """Extract the version field from CITATION.cff."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r'(?m)^version:\s*["\']?([^"\'#\s]+)', content)
    return match.group(1) if match else None


def get_latest_tag() -> tuple[str | None, str | None]:
    """Return the latest v-prefixed tag and an optional query error."""
    try:
        result = subprocess.run(
            ["git", "tag", "--list", "v*", "--sort=-version:refname"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return None, str(exc)
    if result.returncode != 0:
        return None, result.stderr.strip() or f"git exited {result.returncode}"
    tags = result.stdout.splitlines()
    return (tags[0], None) if tags else (None, None)


def validate_versions(
    local_versions: dict[str, str | None],
    latest_tag: str | None,
    tag_error: str | None,
) -> tuple[list[str], list[str]]:
    """Validate version consistency and return errors plus informational notes."""
    errors: list[str] = []
    notes: list[str] = []
    comparable: dict[str, str] = {}

    for source in LOCAL_VERSION_SOURCES:
        version = local_versions.get(source)
        if not version:
            errors.append(f"Could not extract version from {source}")
        else:
            comparable[source] = normalize_version(version)

    if tag_error:
        notes.append(f"SKIP: could not query git tags: {tag_error}")
    elif latest_tag:
        comparable["latest tag"] = normalize_version(latest_tag)
    else:
        notes.append("SKIP: no v-prefixed git tags found")

    if comparable and len(set(comparable.values())) > 1:
        rendered = ", ".join(
            f"{source}={version}" for source, version in comparable.items()
        )
        errors.append(f"Version drift: {rendered}")

    return errors, notes


def run_self_tests() -> int:
    """Cover aligned, drifted, and no-tag states."""
    aligned = {source: "0.1.0" for source in LOCAL_VERSION_SOURCES}

    errors, notes = validate_versions(aligned, "v0.1.0", None)
    assert errors == [] and notes == []

    drifted = {**aligned, "CITATION.cff": "0.2.0"}
    errors, _ = validate_versions(drifted, "v0.1.0", None)
    assert any(error.startswith("Version drift:") for error in errors)

    errors, notes = validate_versions(aligned, None, None)
    assert errors == [] and notes == ["SKIP: no v-prefixed git tags found"]

    errors, notes = validate_versions(aligned, None, "not a git repository")
    assert errors == [] and notes == [
        "SKIP: could not query git tags: not a git repository"
    ]

    print("PASS: check-version-consistency.py self-tests")
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_tests()

    local_versions = {
        "SKILL.md": read_skill_version(LOCAL_VERSION_SOURCES["SKILL.md"]),
        "CITATION.cff": read_citation_version(LOCAL_VERSION_SOURCES["CITATION.cff"]),
    }
    latest_tag, tag_error = get_latest_tag()

    for source, version in local_versions.items():
        print(f"{source} version: {version or 'unreadable'}")
    print(f"Latest tag: {latest_tag or 'none'}")

    errors, notes = validate_versions(local_versions, latest_tag, tag_error)
    for note in notes:
        print(note)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("OK: all available version sources are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
