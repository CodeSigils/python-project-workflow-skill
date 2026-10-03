#!/usr/bin/env python3
"""Check local release versions, git tags, and the published release."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LOCAL_VERSION_SOURCES: dict[str, Path] = {
    "CITATION.cff": ROOT / "CITATION.cff",
}


def normalize_version(version: str) -> str:
    return version.removeprefix("v")


def version_key(version: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", normalize_version(version))
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


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


def get_latest_release() -> tuple[str | None, str | None]:
    """Return the newest published GitHub release tag and an optional error."""
    try:
        result = subprocess.run(
            ["gh", "release", "list", "--limit", "1", "--json", "tagName"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return None, str(exc)
    if result.returncode != 0:
        return None, result.stderr.strip() or f"gh exited {result.returncode}"
    try:
        entries = json.loads(result.stdout or "[]")
    except json.JSONDecodeError as exc:
        return None, f"could not parse gh output: {exc}"
    if not entries:
        return None, None
    return entries[0].get("tagName"), None


def validate_release(
    latest_tag: str | None,
    latest_release: str | None,
    release_error: str | None,
) -> list[str]:
    """Return errors when the latest tag has no matching published release."""
    if release_error:
        return [f"Could not query GitHub releases: {release_error}"]
    if latest_tag is None:
        return []
    if latest_release is None:
        return [f"GitHub has no published release, but tag {latest_tag} exists"]
    if normalize_version(latest_release) != normalize_version(latest_tag):
        return [
            f"Latest GitHub release is {latest_release}, "
            f"but the latest tag is {latest_tag}"
        ]
    return []


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

    local_values = {value for source, value in comparable.items() if source != "latest tag"}
    if len(local_values) > 1:
        rendered = ", ".join(
            f"{source}={version}" for source, version in comparable.items()
        )
        errors.append(f"Local version drift: {rendered}")
    elif latest_tag and local_values:
        local = next(iter(local_values))
        local_key = version_key(local)
        tag_key = version_key(latest_tag)
        if local_key is None or tag_key is None:
            errors.append(f"Versions must use X.Y.Z: local={local}, latest tag={latest_tag}")
        elif local_key < tag_key:
            errors.append(f"Local version {local} is behind latest tag {latest_tag}")
        elif local_key > tag_key:
            notes.append(f"RELEASE PENDING: local version {local} is ahead of {latest_tag}")

    return errors, notes


def run_self_tests() -> int:
    """Cover aligned, drifted, and no-tag states."""
    aligned = {source: "0.1.0" for source in LOCAL_VERSION_SOURCES}

    errors, notes = validate_versions(aligned, "v0.1.0", None)
    assert errors == [] and notes == []

    errors, _ = validate_versions(aligned, "v0.2.0", None)
    assert any("behind latest tag" in error for error in errors)

    ahead = {source: "0.2.0" for source in LOCAL_VERSION_SOURCES}
    errors, notes = validate_versions(ahead, "v0.1.0", None)
    assert errors == [] and notes == [
        "RELEASE PENDING: local version 0.2.0 is ahead of v0.1.0"
    ]

    errors, notes = validate_versions(aligned, None, None)
    assert errors == [] and notes == ["SKIP: no v-prefixed git tags found"]

    errors, notes = validate_versions(aligned, None, "not a git repository")
    assert errors == [] and notes == [
        "SKIP: could not query git tags: not a git repository"
    ]

    assert validate_release("v0.2.0", "v0.2.0", None) == []
    assert validate_release("v0.2.0", "0.2.0", None) == []
    assert validate_release(None, None, None) == []
    assert validate_release("v0.2.0", None, None) == [
        "GitHub has no published release, but tag v0.2.0 exists"
    ]
    assert validate_release("v0.2.0", "v0.1.0", None) == [
        "Latest GitHub release is v0.1.0, but the latest tag is v0.2.0"
    ]
    assert validate_release("v0.2.0", None, "gh is not installed") == [
        "Could not query GitHub releases: gh is not installed"
    ]

    print("PASS: check-version-consistency.py self-tests")
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-github-release",
        action="store_true",
        help="also require a published GitHub release for the latest tag",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_tests()

    local_versions = {
        "CITATION.cff": read_citation_version(LOCAL_VERSION_SOURCES["CITATION.cff"]),
    }
    latest_tag, tag_error = get_latest_tag()

    for source, version in local_versions.items():
        print(f"{source} version: {version or 'unreadable'}")
    print(f"Latest tag: {latest_tag or 'none'}")

    errors, notes = validate_versions(local_versions, latest_tag, tag_error)

    if args.require_github_release:
        latest_release, release_error = get_latest_release()
        print(f"Latest GitHub release: {latest_release or 'none'}")
        errors.extend(validate_release(latest_tag, latest_release, release_error))

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
