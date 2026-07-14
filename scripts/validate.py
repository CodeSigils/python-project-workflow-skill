#!/usr/bin/env python3
"""Validate the python-project-workflow skill source."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "python-project-workflow"
SKILL = SKILL_DIR / "SKILL.md"
REF_DIR = SKILL_DIR / "references"
REQUIRED_REFS = {
    "pyproject-template.md",
    "lint-format-typing-testing.md",
    "core-footguns.md",
    "safe-editing.md",
    "mature-repo-preservation.md",
    "eval-benchmark-hardening.md",
    "drift-classes.md",
}
REQUIRED_SECTIONS = {
    "## Scope",
    "## Orientation Checklist",
    "## Task Classification Table",
    "## Verification Commands",
    "## Preserve Local Conventions",
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def fail(message: str, *, hint: str | None = None) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    if hint:
        print(f"HINT: {hint}", file=sys.stderr)
    raise SystemExit(1)


def read_text_checked(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail(f"required file is missing: {rel(path)}")
    except UnicodeDecodeError as exc:
        fail(f"required file is not valid UTF-8: {rel(path)}: {exc}")
    except OSError as exc:
        fail(f"could not read required file {rel(path)}: {exc}")
    raise AssertionError("unreachable")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        fail("SKILL.md does not start with YAML frontmatter")
    try:
        _, raw, body = text.split("---\n", 2)
    except ValueError:
        fail("SKILL.md frontmatter is not closed")

    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            fail(f"malformed frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')

    ALLOWED_FIELDS = {
        "name", "description", "version", "author", "license",
        "tier", "ref", "compatibility", "metadata",
    }
    extra = set(data) - ALLOWED_FIELDS
    if extra:
        fail(f"unsupported frontmatter fields: {sorted(extra)}")
    if data.get("name") != "python-project-workflow":
        fail("frontmatter name must be python-project-workflow")
    if len(data.get("description", "").split()) < 18:
        fail("frontmatter description is too short to trigger reliably")
    return data, body


def contains_markdown_phrase(text: str, phrase: str) -> bool:
    return " ".join(phrase.split()) in " ".join(text.split())


def check_skill() -> None:
    text = read_text_checked(SKILL)
    _, body = parse_frontmatter(text)

    for section in sorted(REQUIRED_SECTIONS):
        if section not in body:
            fail(f"missing section in {rel(SKILL)}: {section}")

    if re.search(r"^\|\|", body, re.MULTILINE):
        fail(f"{rel(SKILL)} table still has accidental double-pipe rows")

    # Portability hazard check: body must not contain Hermes-specific paths/tools
    forbidden = [
        ".hermes",
        "hermes-verify",
    ]
    for needle in forbidden:
        if needle in body:
            fail(f"{rel(SKILL)} body contains non-portable runtime marker: {needle}")

    for missing_ref in ["packaging.md", "errors-and-logging.md", "cli.md", "migration-existing-code.md"]:
        if f"`{missing_ref}` (deferred)" in body:
            fail(
                f"task table routes directly to deferred reference without fallback: {missing_ref}",
                hint="Point the row at an existing fallback reference, then label the richer reference as deferred.",
            )

    if len(text.splitlines()) > 500:
        fail(f"{rel(SKILL)} exceeds 500-line runtime budget")


def check_references() -> None:
    if not REF_DIR.exists():
        fail(f"runtime reference directory is missing: {rel(REF_DIR)}")
    found = {path.name for path in REF_DIR.glob("*.md")}
    missing = REQUIRED_REFS - found
    extra = found - REQUIRED_REFS
    if missing:
        fail(f"missing reference files: {sorted(missing)}")
    if extra:
        fail(f"unexpected reference files: {sorted(extra)}")
    for name in REQUIRED_REFS:
        path = REF_DIR / name
        size = path.stat().st_size
        if size < 500:
            fail(f"reference file looks too small: {rel(path)} ({size} bytes)")
        if len(read_text_checked(path).splitlines()) > 250:
            fail(f"reference file exceeds 250-line budget: {rel(path)}")


def check_readme() -> None:
    readme = read_text_checked(ROOT / "README.md")
    required = [
        "agentskills.io-compatible",
        "skills/python-project-workflow/",
        "Shipping boundary: `skills/python-project-workflow/` is the runtime payload",
    ]
    for phrase in required:
        if not contains_markdown_phrase(readme, phrase):
            fail(f"README.md missing required phrase: {phrase}")
    if "Hermes Skill" in readme:
        fail("README.md should not frame the project as Hermes-only")


def check_status_sources() -> None:
    removed_summary = ROOT / "IMPLEMENTATION_SUMMARY.md"
    if removed_summary.exists():
        fail("IMPLEMENTATION_SUMMARY.md should not exist")
    old_skill = ROOT / "skill"
    if old_skill.exists():
        fail("old runtime directory still exists: skill/")


def main() -> int:
    check_skill()
    check_references()
    check_readme()
    check_status_sources()
    print("OK: portable skill source checks are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
