#!/usr/bin/env python3
"""Source and installed-mirror readiness checks for the python-best-practices skill.

Validates:
- skill/SKILL.md structure and required sections
- skill/references/ completeness and size
- README.md shipping boundary phrasing
- No stale IMPLEMENTATION_SUMMARY.md
- Git commit authorship hygiene
- Markdown formatting (when formatter is available)
- Installed mirror sync (when requested)
"""

from __future__ import annotations

import argparse
import filecmp
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("PBP_SKILL_ROOT", DEFAULT_ROOT)).resolve()
SKILL = ROOT / "skill" / "SKILL.md"
REF_DIR = ROOT / "skill" / "references"
DEFAULT_INSTALLED = Path.home() / ".hermes" / "skills" / "software-development" / "python-best-practices"
INSTALLED = Path(os.environ.get("PBP_SKILL_INSTALLED", DEFAULT_INSTALLED)).resolve()
REQUIRED_REFS = {
    "project-orientation.md",
    "pyproject-template.md",
    "lint-format-typing-testing.md",
    "review-checklist.md",
    "mature-repo-preservation.md",
    "eval-benchmark-hardening.md",
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


def contains_markdown_phrase(text: str, phrase: str) -> bool:
    return " ".join(phrase.split()) in " ".join(text.split())


def check_skill() -> None:
    text = read_text_checked(SKILL)
    if not text.startswith("---\n"):
        fail("skill/SKILL.md does not start with YAML frontmatter")
    if "\n---\n" not in text[4:]:
        fail("skill/SKILL.md frontmatter is not closed")
    for section in [
        "## When to Use This Skill",
        "## Orientation Checklist",
        "## Task Classification Table",
        "## Verification Commands",
        "## Preserve Local Conventions",
    ]:
        if section not in text:
            fail(f"missing section in skill/SKILL.md: {section}")
    if re.search(r"^\|\|", text, re.MULTILINE):
        fail("skill/SKILL.md table still has accidental double-pipe rows")
    for missing_ref in ["packaging.md", "errors-and-logging.md", "cli.md", "migration-existing-code.md"]:
        if f"`{missing_ref}` (deferred)" in text:
            fail(
                f"task table routes directly to deferred reference without fallback: {missing_ref}",
                hint="Point the row at an existing fallback reference, then label the richer reference as deferred.",
            )


def check_references() -> None:
    if not REF_DIR.exists():
        fail(f"runtime reference directory is missing: {rel(REF_DIR)}")
    found = {p.name for p in REF_DIR.glob("*.md")}
    missing = REQUIRED_REFS - found
    if missing:
        fail(
            f"missing reference files: {sorted(missing)}",
            hint="Create the missing files under skill/references/ or update REQUIRED_REFS if the source set changed.",
        )
    for name in REQUIRED_REFS:
        path = REF_DIR / name
        size = path.stat().st_size
        if size < 500:
            fail(f"reference file looks too small: {rel(path)} ({size} bytes)")


def check_status_sources() -> None:
    removed_summary = ROOT / "IMPLEMENTATION_SUMMARY.md"
    if removed_summary.exists():
        fail(
            "IMPLEMENTATION_SUMMARY.md should not exist",
            hint="Keep status in README.md; use git history for completed-change records.",
        )


def check_shipping_phase() -> None:
    """Verify README.md documents the runtime shipping boundary."""
    readme = read_text_checked(ROOT / "README.md")
    if not contains_markdown_phrase(readme, "Shipping boundary: `skill/` is the runtime payload and source of truth"):
        fail(
            "README.md is missing the shipping boundary summary",
            hint="README.md must tell humans that skill/ is the runtime payload and the installed mirror is only a test copy.",
        )


def sync_installed_mirror() -> None:
    try:
        if INSTALLED.exists():
            shutil.rmtree(INSTALLED)
        INSTALLED.mkdir(parents=True, exist_ok=True)
        (INSTALLED / "references").mkdir(exist_ok=True)
        shutil.copy2(SKILL, INSTALLED / "SKILL.md")
        for name in REQUIRED_REFS:
            shutil.copy2(REF_DIR / name, INSTALLED / "references" / name)
    except OSError as exc:
        fail(f"could not sync installed mirror at {INSTALLED}: {exc}")


def check_installed_mirror() -> None:
    if not INSTALLED.exists():
        fail(
            f"installed mirror missing: {INSTALLED}",
            hint="Run python3 scripts/run_phase2_checks.py --sync-installed to create it, or use --skip-installed for source-only checks.",
        )
    installed_skill = INSTALLED / "SKILL.md"
    if not installed_skill.exists():
        fail(
            f"installed mirror missing SKILL.md: {installed_skill}",
            hint="Run python3 scripts/run_phase2_checks.py --sync-installed.",
        )
    if not filecmp.cmp(SKILL, installed_skill, shallow=False):
        fail(
            "installed SKILL.md differs from source skill/SKILL.md",
            hint="Run python3 scripts/run_phase2_checks.py --sync-installed, then rerun the check.",
        )
    allowed_files = {Path("SKILL.md")} | {Path("references") / name for name in REQUIRED_REFS}
    actual_files = {path.relative_to(INSTALLED) for path in INSTALLED.rglob("*") if path.is_file()}
    extra_files = sorted(actual_files - allowed_files)
    if extra_files:
        fail(
            f"installed mirror has file(s) outside source runtime payload: {[str(path) for path in extra_files]}",
            hint="Run python3 scripts/run_phase2_checks.py --sync-installed to replace the mirror with the canonical skill/ payload.",
        )
    for name in REQUIRED_REFS:
        src = REF_DIR / name
        dst = INSTALLED / "references" / name
        if not dst.exists():
            fail(
                f"installed mirror missing reference: {name}",
                hint="Run python3 scripts/run_phase2_checks.py --sync-installed.",
            )
        if not filecmp.cmp(src, dst, shallow=False):
            fail(
                f"installed mirror reference differs: {name}",
                hint="Run python3 scripts/run_phase2_checks.py --sync-installed, then rerun the check.",
            )


def check_markdown_format() -> None:
    """Verify tracked .md files pass the markdown formatter if available."""
    formatter = (
        Path.home()
        / ".hermes"
        / "skills"
        / "markdown-formatter"
        / "src"
        / "index.js"
    )
    if not formatter.exists():
        print("WARNING: markdown formatter not found, skipping format check")
        return

    for exe in ("node", "oxfmt"):
        try:
            subprocess.run(
                ["which", exe],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=10,
            )
        except (subprocess.SubprocessError, OSError):
            print(f"WARNING: {exe} not available, skipping markdown format check")
            return

    try:
        result = subprocess.run(
            ["git", "ls-files", "*.md"],
            cwd=ROOT,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=10, check=True,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        print(f"WARNING: could not list tracked .md files: {exc}")
        return

    md_files = [f for f in result.stdout.splitlines() if f.strip()]
    if not md_files:
        return

    try:
        verify = subprocess.run(
            ["node", str(formatter), "--verify", "--all", *md_files],
            cwd=ROOT,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=60,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        print(f"WARNING: markdown formatter check failed to run: {exc}")
        return

    if verify.returncode != 0:
        print(verify.stdout, file=sys.stderr)
        fail(
            "tracked .md files are not formatted",
            hint="Run the markdown formatter: node <skill>/markdown-formatter/src/index.js --fix --guard <files>",
        )


BOT_AUTHOR_PATTERNS = [
    "dependabot",
    "renovate",
    "[bot]",
    "bot@",
    "agn",
    "automation",
    "auto-merge",
]


def check_commit_authors() -> None:
    """Warn if recent commits have bot/agent-like authorship (non-fatal)."""
    try:
        result = subprocess.run(
            ["git", "log", "--max-count=10",
             "--format=%H|%an|%ae|%cn|%ce"],
            cwd=ROOT,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=10, check=False,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        print(f"WARNING: could not check git authors: {exc}")
        return

    if result.returncode != 0 or not result.stdout.strip():
        return

    for line in result.stdout.strip().splitlines():
        parts = line.split("|", maxsplit=4)
        if len(parts) != 5:
            continue
        sha, aname, aemail, cname, cemail = parts

        fields = [
            ("author", aname, aemail),
            ("committer", cname, cemail),
        ]
        for role, name, email in fields:
            combined = f"{name} <{email}>".lower()
            for pattern in BOT_AUTHOR_PATTERNS:
                if pattern in combined:
                    print(
                        f"WARNING: commit {sha[:8]} has {role} matching "
                        f"bot pattern {pattern!r}: {name} <{email}>",
                        file=sys.stderr,
                    )

        if f"{aname} <{aemail}>".lower() != f"{cname} <{cemail}>".lower():
            print(
                f"NOTE: commit {sha[:8]} author differs from committer "
                f"(author: {aname} <{aemail}> vs committer: {cname} <{cemail}>)",
                file=sys.stderr,
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-installed", action="store_true", help="copy source skill files into the local Hermes mirror before checking")
    parser.add_argument("--skip-installed", action="store_true", help="skip local Hermes mirror verification for portable source-only checks")
    args = parser.parse_args()

    check_skill()
    check_references()
    check_status_sources()
    check_shipping_phase()
    check_commit_authors()
    check_markdown_format()
    if args.sync_installed:
        sync_installed_mirror()
    if not args.skip_installed:
        check_installed_mirror()
    mirror_scope = "source files only" if args.skip_installed else "source files and installed skill mirror"
    print(f"OK: skill source checks and {mirror_scope} are valid")
    return 0


if __name__ == "__main__":
    main()
