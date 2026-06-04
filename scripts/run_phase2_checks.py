#!/usr/bin/env python3
"""Phase 2 structural, fixture, and installed-mirror readiness checks.

This script does not judge LLM eval output. It verifies that controlled eval
assets are coherent enough for with-skill vs baseline runs, and that the local
Hermes runtime mirror matches the source skill when requested.
"""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
from json import JSONDecodeError
from pathlib import Path
from typing import Any

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
}
REQUIRED_EVALS = {
    "greenfield-setup",
    "existing-file-review",
    "incremental-typing-testing",
    "existing-project-preservation",
    "non-python-doc-only",
    "generic-python-question",
}
PYTEST_FIXTURES = {
    "evals/fixtures/existing-buggy",
    "evals/fixtures/existing-preserve",
}
LIVE_STATUS_DOCS = {
    "README.md",
    "plan.md",
    "todos.md",
}


def rel(path: Path) -> str:
    """Return a repository-relative path when possible for readable errors."""
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


def read_json_checked(path: Path) -> dict[str, Any]:
    text = read_text_checked(path)
    try:
        data = json.loads(text)
    except JSONDecodeError as exc:
        fail(
            f"invalid JSON in {rel(path)} at line {exc.lineno}, column {exc.colno}: {exc.msg}",
            hint="Fix evals/evals.json syntax before running Phase 2 checks again.",
        )
    if not isinstance(data, dict):
        fail(f"{rel(path)} top-level JSON value must be an object")
    return data


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
            hint="Keep live status in README.md, plan.md, and todos.md; use git history for completed-change records.",
        )
    for name in LIVE_STATUS_DOCS:
        path = ROOT / name
        if path.exists() and "IMPLEMENTATION_SUMMARY.md" in read_text_checked(path):
            fail(
                f"stale IMPLEMENTATION_SUMMARY.md reference remains in {name}",
                hint="Remove the reference and keep current status in README.md, plan.md, and todos.md.",
            )


def require_list(item: dict[str, Any], key: str, name: str) -> list[str]:
    value = item.get(key)
    if not isinstance(value, list):
        fail(f"eval {name!r} field {key!r} must be a list of strings")
    bad_values = [v for v in value if not isinstance(v, str) or not v]
    if bad_values:
        fail(f"eval {name!r} field {key!r} contains non-string or empty values: {bad_values!r}")
    return value


def check_evals() -> list[dict[str, Any]]:
    data = read_json_checked(ROOT / "evals" / "evals.json")
    if data.get("schema_version") != 1:
        fail("evals/evals.json schema_version must be 1")
    evals = data.get("evals")
    if not isinstance(evals, list) or len(evals) < len(REQUIRED_EVALS):
        fail(f"evals/evals.json must contain at least {len(REQUIRED_EVALS)} evals")

    names: set[str] = set()
    ref_names = {p.name for p in REF_DIR.glob("*.md")}
    for index, item in enumerate(evals):
        if not isinstance(item, dict):
            fail(f"evals/evals.json entry #{index + 1} must be an object")
        name = item.get("name")
        if not isinstance(name, str) or not name:
            fail(f"eval entry #{index + 1} is missing a non-empty string name")
        if name in names:
            fail(f"duplicate eval name: {name}")
        names.add(name)
        fixture_value = item.get("fixture")
        if not isinstance(fixture_value, str) or not fixture_value:
            fail(f"eval {name!r} is missing a non-empty string fixture path")
        fixture = ROOT / fixture_value
        if not fixture.exists():
            fail(f"fixture missing for eval {name!r}: {rel(fixture)}")
        if not isinstance(item.get("prompt"), str) or not item["prompt"].strip():
            fail(f"eval {name!r} is missing a non-empty prompt")
        if not isinstance(item.get("should_trigger"), bool):
            fail(f"eval {name!r} is missing boolean should_trigger")
        expected_refs = require_list(item, "expected_references", name)
        must_include = require_list(item, "must_include", name)
        require_list(item, "must_not_include", name)
        if item["should_trigger"] and not expected_refs:
            fail(f"triggering eval must name expected references: {name}")
        if item["should_trigger"] and not must_include:
            fail(f"triggering eval must define must_include terms: {name}")
        unknown_refs = sorted(set(expected_refs) - ref_names)
        if unknown_refs:
            fail(f"eval {name!r} references missing runtime files: {unknown_refs}")
    missing_names = REQUIRED_EVALS - names
    if missing_names:
        fail(f"missing required evals: {sorted(missing_names)}")
    return evals


def check_fixture_python_files(evals: list[dict[str, Any]]) -> None:
    fixture_dirs = sorted({ROOT / item["fixture"] for item in evals})
    for fixture in fixture_dirs:
        for py_file in fixture.rglob("*.py"):
            if any(part in {"__pycache__", "build", "dist"} or part.endswith(".egg-info") for part in py_file.parts):
                continue
            try:
                py_compile.compile(str(py_file), doraise=True)
            except py_compile.PyCompileError as exc:
                fail(f"fixture Python file does not compile: {rel(py_file)}: {exc.msg}")


def run_pytest_smoke() -> None:
    for fixture in sorted(PYTEST_FIXTURES):
        fixture_path = ROOT / fixture
        if not fixture_path.exists():
            fail(f"pytest fixture directory is missing: {fixture}")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q"],
                cwd=fixture_path,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=60,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            output = exc.stdout or ""
            if output:
                print(output, file=sys.stderr)
            fail(f"pytest smoke timed out after 60s for {fixture}")
        except OSError as exc:
            fail(f"could not run pytest smoke for {fixture}: {exc}")
        if result.returncode != 0:
            print(result.stdout, file=sys.stderr)
            fail(f"pytest smoke failed for {fixture} with exit code {result.returncode}")
        if " no tests ran" in result.stdout or "0 passed" in result.stdout:
            print(result.stdout, file=sys.stderr)
            fail(f"pytest smoke discovered zero tests for {fixture}")


def sync_installed_mirror() -> None:
    try:
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-installed", action="store_true", help="copy source skill files into the local Hermes mirror before checking")
    parser.add_argument("--skip-installed", action="store_true", help="skip local Hermes mirror verification for portable source-only checks")
    args = parser.parse_args()

    check_skill()
    check_references()
    check_status_sources()
    evals = check_evals()
    check_fixture_python_files(evals)
    run_pytest_smoke()
    if args.sync_installed:
        sync_installed_mirror()
    if not args.skip_installed:
        check_installed_mirror()
    mirror_scope = "source files only" if args.skip_installed else "source files and installed skill mirror"
    print(f"OK: Phase 2 assets, fixture smoke checks, and {mirror_scope} are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
