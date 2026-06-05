#!/usr/bin/env python3
"""Structural, fixture, trigger-eval, and installed-mirror readiness checks.

This script does not judge LLM eval output. It verifies that controlled eval
assets are coherent enough for with-skill vs baseline runs, Phase 3 trigger
query assets are coherent enough for description optimization, and the local
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
from typing import Any, cast

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
REQUIRED_EVALS = {
    "greenfield-setup",
    "existing-file-review",
    "incremental-typing-testing",
    "existing-project-preservation",
    "non-python-doc-only",
    "generic-python-question",
    "typo-in-docstring",
    "shell-script-question",
    "mature-automation-repo-preservation",
}
REQUIRED_TRIGGER_EVAL_COUNT = 20
REQUIRED_TRIGGER_EVAL_TRUE_COUNT = 10
REQUIRED_TRIGGER_EVAL_FALSE_COUNT = 10
PYTEST_FIXTURES = {
    "evals/fixtures/existing-buggy",
    "evals/fixtures/existing-preserve",
    "evals/fixtures/mature-automation-repo",
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


def contains_markdown_phrase(text: str, phrase: str) -> bool:
    """Return whether phrase appears, allowing Markdown formatter line wrapping."""
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
            hint="Keep live status in README.md, plan.md, and todos.md; use git history for completed-change records.",
        )
    for name in LIVE_STATUS_DOCS:
        path = ROOT / name
        if path.exists() and "IMPLEMENTATION_SUMMARY.md" in read_text_checked(path):
            fail(
                f"stale IMPLEMENTATION_SUMMARY.md reference remains in {name}",
                hint="Remove the reference and keep current status in README.md, plan.md, and todos.md.",
            )


def check_agent_contract() -> None:
    """Verify repo-local agent guards stay present and free of generated state."""
    agents_path = ROOT / "AGENTS.md"
    text = read_text_checked(agents_path)
    required_phrases = [
        "**Last verified:**",
        "## Orientation Contract — BLOCKING",
        "## Source, Mirror, and Shipping Policy — BLOCKING",
        "## Phase and User-Shipping Guard — BLOCKING",
        "## Drift and Stale Information Contract — BLOCKING",
        "## Generated State Guard — BLOCKING",
        "skill/` as the canonical runtime payload",
        "Do not publish, package, install elsewhere, sync to another Hermes profile, push, tag, or release",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            fail(
                f"AGENTS.md is missing required repo guard phrase: {phrase}",
                hint="Restore the source/mirror/shipping, drift, orientation, and generated-state guards before continuing.",
            )
    forbidden_markers = [
        "<!-- open-mem-context -->",
        "<!-- omo-context -->",
        "CONTEXT COMPACTION",
        "Generated agent session state",
    ]
    for marker in forbidden_markers:
        if marker in text:
            fail(
                f"AGENTS.md contains generated/session-state marker: {marker}",
                hint="Remove transient agent state from canonical docs; keep it in ignored workspace/session files.",
            )


def check_shipping_phase() -> None:
    """Verify the user-shipping phase and runtime boundary are documented."""
    plan = read_text_checked(ROOT / "plan.md")
    required_plan_phrases = [
        "### Phase 4 — Polish, Ship & Publish",
        "`skill/` is the directory-as-boundary runtime payload",
        "Produce a concise user handoff",
        "confirmation that repository-only files are absent from the runtime payload",
    ]
    for phrase in required_plan_phrases:
        if not contains_markdown_phrase(plan, phrase):
            fail(
                f"plan.md is missing required shipping-phase phrase: {phrase}",
                hint="Keep Phase 4 as an explicit user-shipping/publishing phase with runtime-boundary verification.",
            )
    readme = read_text_checked(ROOT / "README.md")
    if not contains_markdown_phrase(readme, "Shipping boundary: `skill/` is the runtime payload and source of truth"):
        fail(
            "README.md is missing the shipping boundary summary",
            hint="README.md must tell humans that skill/ is the runtime payload and the installed mirror is only a test copy.",
        )


def check_live_docs_fresh() -> None:
    """Warn about [ ] items in plan.md and todos.md that may be stale.

    Parses pending task entries from the live status docs, then checks
    whether recent commit messages (last 20) mention the same topic.
    A [ ] item whose keywords appear in recent commits is flagged as
    potentially stale — the author may have completed it without updating
    the doc.

    This is a non-fatal warning because some [ ] items are legitimately
    pending even when keywords overlap.
    """
    keywords_by_doc: dict[str, list[str]] = {}
    for name in LIVE_STATUS_DOCS:
        path = ROOT / name
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        keywords = []
        for line in lines:
            stripped = line.strip()
            # Match [ ] checklist items, not [x] done ones
            if stripped.startswith("- [ ] ") or stripped.startswith("* [ ] "):
                text = stripped[6:] if stripped.startswith("- [ ] ") else stripped[6:]
                if len(text) > 5:
                    keywords.append(text)
        if keywords:
            keywords_by_doc[name] = keywords

    if not keywords_by_doc:
        return

    # Fetch recent commit subjects
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--max-count=20"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return  # skip check if git is not available
    if result.returncode != 0:
        return

    commits = result.stdout.lower()

    for doc, items in keywords_by_doc.items():
        for item in items:
            significant_words = [
                w.lower().strip(",:;.()\"'")
                for w in item.split()
                if len(w) > 5 and w.lower() not in {"without", "should", "after", "before", "their"}
            ]
            if not significant_words:
                continue
            match_count = sum(1 for w in significant_words if w in commits)
            if match_count >= 2:
                print(
                    f"WARNING: {doc} has [ ] item that may be stale: \"{item}\"",
                    file=sys.stderr,
                )
                print(
                    "  Keywords from this item appear in recent commits.",
                    file=sys.stderr,
                )


def require_list(item: dict[str, Any], key: str, name: str) -> list[str]:
    value = item.get(key)
    if not isinstance(value, list):
        fail(f"eval {name!r} field {key!r} must be a list of strings")
    bad_values = [v for v in value if not isinstance(v, str) or not v]
    if bad_values:
        fail(f"eval {name!r} field {key!r} contains non-string or empty values: {bad_values!r}")
    return value


def require_any_groups(item: dict[str, Any], name: str) -> list[dict[str, Any]]:
    value = item.get("must_include_any", [])
    if not isinstance(value, list):
        fail(f"eval {name!r} field 'must_include_any' must be a list of objects")
    for index, group in enumerate(value, start=1):
        if not isinstance(group, dict):
            fail(f"eval {name!r} must_include_any group #{index} must be an object")
        group_name = group.get("name")
        if not isinstance(group_name, str) or not group_name:
            fail(f"eval {name!r} must_include_any group #{index} needs a non-empty string name")
        terms_value = group.get("terms")
        if not isinstance(terms_value, list) or not terms_value:
            fail(f"eval {name!r} must_include_any group {group_name!r} needs a non-empty terms list")
        terms = terms_value
        bad_terms = [term for term in terms if not isinstance(term, str) or not term]
        if bad_terms:
            fail(f"eval {name!r} must_include_any group {group_name!r} has invalid terms: {bad_terms!r}")
    return value


def check_evals() -> list[dict[str, Any]]:
    data = read_json_checked(ROOT / "evals" / "evals.json")
    if data.get("schema_version") != 1:
        fail("evals/evals.json schema_version must be 1")
    evals = data.get("evals")
    if not isinstance(evals, list):
        fail("evals/evals.json field 'evals' must be a list")

    names: set[str] = set()
    ref_names = {p.name for p in REF_DIR.glob("*.md")}
    for index, item in enumerate(evals):
        if not isinstance(item, dict):
            fail(f"evals/evals.json entry #{index + 1} must be an object")
        name = item.get("name")
        if not isinstance(name, str) or not name:
            fail(f"eval entry #{index + 1} is missing a non-empty string name")
        assert isinstance(name, str)
        eval_name = name
        if eval_name in names:
            fail(f"duplicate eval name: {eval_name}")
        names.add(eval_name)
        fixture_value = item.get("fixture")
        if not isinstance(fixture_value, str) or not fixture_value:
            fail(f"eval {name!r} is missing a non-empty string fixture path")
        fixture = ROOT / fixture_value
        if not fixture.exists():
            fail(f"fixture missing for eval {name!r}: {rel(fixture)}")
        if not isinstance(item.get("prompt"), str) or not item["prompt"].strip():
            fail(f"eval {name!r} is missing a non-empty prompt")
        prompt = item["prompt"]
        prompt_symbols = [symbol for symbol in re.findall(r"`([^`]+)`", prompt) if symbol]
        if prompt_symbols:
            fixture_text = "\n".join(
                path.read_text(encoding="utf-8", errors="ignore")
                for path in fixture.rglob("*")
                if path.is_file() and path.suffix in {".py", ".md", ".txt", ".toml", ".cfg"}
            )
            missing_symbols = [symbol for symbol in prompt_symbols if symbol not in fixture_text]
            if missing_symbols:
                fail(
                    f"eval {name!r} prompt references fixture symbol(s) not found: {missing_symbols}",
                    hint="Update the prompt or fixture so evals do not ask agents to edit nonexistent targets.",
                )
        if not isinstance(item.get("should_trigger"), bool):
            fail(f"eval {name!r} is missing boolean should_trigger")
        expected_refs = require_list(item, "expected_references", name)
        must_include = require_list(item, "must_include", name)
        require_any_groups(item, name)
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


def check_phase3_trigger_eval_set() -> None:
    """Validate the Phase 3 trigger-description eval query set."""
    path = ROOT / "evals" / "trigger-description-evals.json"
    data = read_json_checked(path)
    if data.get("schema_version") != 1:
        fail("evals/trigger-description-evals.json schema_version must be 1")
    if data.get("status") != "draft-for-user-review":
        fail(
            "evals/trigger-description-evals.json status must be draft-for-user-review",
            hint="Keep the Phase 3 eval set marked as a user-review draft until the user approves it.",
        )
    evals = data.get("evals")
    if not isinstance(evals, list):
        fail("evals/trigger-description-evals.json field 'evals' must be a list")
    trigger_evals = cast(list[dict[str, Any]], evals)
    if len(trigger_evals) != REQUIRED_TRIGGER_EVAL_COUNT:
        fail(
            f"Phase 3 trigger eval set must contain {REQUIRED_TRIGGER_EVAL_COUNT} queries; found {len(trigger_evals)}",
            hint="Keep the Phase 3 review set at 20 queries so trigger and near-miss coverage stays balanced.",
        )
    ids: set[str] = set()
    trigger_count = 0
    non_trigger_count = 0
    required_string_fields = ["id", "query", "category", "rationale", "expected_boundary"]
    for index, item in enumerate(trigger_evals, start=1):
        if not isinstance(item, dict):
            fail(f"trigger-description eval entry #{index} must be an object")
        for field in required_string_fields:
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                fail(f"trigger-description eval entry #{index} field {field!r} must be a non-empty string")
        eval_id = item["id"]
        if eval_id in ids:
            fail(f"duplicate trigger-description eval id: {eval_id}")
        ids.add(eval_id)
        should_trigger = item.get("should_trigger")
        if not isinstance(should_trigger, bool):
            fail(f"trigger-description eval {eval_id!r} is missing boolean should_trigger")
        if should_trigger:
            trigger_count += 1
        else:
            non_trigger_count += 1
    if trigger_count != REQUIRED_TRIGGER_EVAL_TRUE_COUNT or non_trigger_count != REQUIRED_TRIGGER_EVAL_FALSE_COUNT:
        fail(
            "Phase 3 trigger eval set must contain "
            f"{REQUIRED_TRIGGER_EVAL_TRUE_COUNT} trigger and {REQUIRED_TRIGGER_EVAL_FALSE_COUNT} non-trigger queries; "
            f"found {trigger_count} trigger and {non_trigger_count} non-trigger",
            hint="Keep Phase 3 description optimization balanced between should-trigger and should-not-trigger prompts.",
        )


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-installed", action="store_true", help="copy source skill files into the local Hermes mirror before checking")
    parser.add_argument("--skip-installed", action="store_true", help="skip local Hermes mirror verification for portable source-only checks")
    args = parser.parse_args()

    check_skill()
    check_references()
    check_status_sources()
    check_agent_contract()
    check_shipping_phase()
    check_live_docs_fresh()
    evals = check_evals()
    check_phase3_trigger_eval_set()
    check_fixture_python_files(evals)
    run_pytest_smoke()
    if args.sync_installed:
        sync_installed_mirror()
    if not args.skip_installed:
        check_installed_mirror()
    mirror_scope = "source files only" if args.skip_installed else "source files and installed skill mirror"
    print(f"OK: Phase 2/3 assets, fixture smoke checks, and {mirror_scope} are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
