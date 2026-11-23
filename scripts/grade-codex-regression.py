#!/usr/bin/env python3
"""Grade python-project-workflow Codex behavior results."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path, PurePath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals/codex/cases.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def path_matches(value: object, expected: str) -> bool:
    if not isinstance(value, str):
        return False
    parts = PurePath(value).parts
    expected_parts = PurePath(expected).parts
    return parts[-len(expected_parts) :] == expected_parts


def contains_any(value: object, terms: list[str]) -> bool:
    text = str(value).lower()
    return any(term.lower() in text for term in terms)


def actual_changes(fixture: Path) -> set[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=fixture,
        capture_output=True,
        text=True,
        check=True,
    )
    changes: set[str] = set()
    for line in result.stdout.splitlines():
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changes.add(path)
    return changes


def executable_errors(case: dict[str, Any], fixture: Path) -> list[str]:
    if not case.get("import_check"):
        return []
    errors: list[str] = []
    compile_result = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "src", "tests"],
        cwd=fixture,
        capture_output=True,
        text=True,
        check=False,
    )
    if compile_result.returncode:
        errors.append(f"{case['id']}: generated Python does not compile")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(fixture / "src")
    import_result = subprocess.run(
        [sys.executable, "-c", case["import_check"]],
        cwd=fixture,
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )
    if import_result.returncode:
        errors.append(f"{case['id']}: generated CLI entry point is not importable")
    return errors


def script_entry_errors(case: dict[str, Any], fixture: Path) -> list[str]:
    required = case.get("required_scripts", {})
    if not required:
        return []
    try:
        pyproject = (fixture / "pyproject.toml").read_text(encoding="utf-8")
    except OSError:
        return []
    section = re.search(r"(?ms)^\[project\.scripts\]\s*(.*?)(?=^\[|\Z)", pyproject)
    body = section.group(1) if section else ""
    errors: list[str] = []
    for name, target in required.items():
        pattern = rf"(?m)^\s*{re.escape(name)}\s*=\s*[\"']{re.escape(target)}[\"']\s*$"
        if not re.search(pattern, body):
            errors.append(f"{case['id']}: missing project script {name} = {target}")
    return errors


def case_fixture_error(case_id: str, fixture: Path) -> list[str]:
    expected: dict[str, tuple[list[str], list[str]]] = {
        "pep621-partial-inspect": (
            ["pyproject.toml", ".github/workflows/ci.yml", "src/sample_pkg/__init__.py"],
            ["setup.cfg", "setup.py"],
        ),
        "pep621-legacy-setupcfg": (
            ["setup.cfg", "setup.py", "legacy_pkg/__init__.py"],
            [],
        ),
    }
    required, forbidden = expected.get(case_id, ([], []))
    errors: list[str] = []
    for relative in required:
        if not (fixture / relative).exists():
            errors.append(f"{case_id}: fixture missing {relative}")
    for relative in forbidden:
        if (fixture / relative).exists():
            errors.append(f"{case_id}: fixture unexpectedly contains {relative}")
    if case_id == "pep621-partial-inspect":
        pyproject = (fixture / "pyproject.toml").read_text(encoding="utf-8") if (fixture / "pyproject.toml").exists() else ""
        if 'requires-python = ">=3.11"' not in pyproject or 'target-version = "py310"' not in pyproject:
            errors.append(f"{case_id}: fixture missing PEP 621/contract mismatch markers")
        if "[project]" not in pyproject or 'description' in pyproject:
            # description intentionally missing; only enforce [project] presence and missing description marker
            pass
        if 'description = ' in pyproject or "readme =" in pyproject:
            errors.append(f"{case_id}: fixture should omit description/readme for partial case")
    if case_id == "pep621-legacy-setupcfg":
        setup_cfg = (fixture / "setup.cfg").read_text(encoding="utf-8") if (fixture / "setup.cfg").exists() else ""
        pyproject = (fixture / "pyproject.toml").read_text(encoding="utf-8") if (fixture / "pyproject.toml").exists() else ""
        if "[metadata]" not in setup_cfg or "name = legacy-pkg" not in setup_cfg:
            errors.append(f"{case_id}: fixture missing setup.cfg metadata markers")
        if "[project]" in pyproject:
            errors.append(f"{case_id}: legacy fixture must not include PEP 621 [project] table")
    return errors


def grade_case(case: dict[str, Any], result: dict[str, Any], fixture: Path) -> list[str]:
    errors: list[str] = []
    if "python-project-workflow" not in result.get("skills_used", []):
        errors.append(f"{case['id']}: skill not recorded")
    if not contains_any(result.get("classification", ""), case["classification_terms"]):
        errors.append(f"{case['id']}: incorrect project classification")
    changed = result.get("changed_paths", [])
    observed = actual_changes(fixture)
    for expected in case["expected_paths"]:
        if not (fixture / expected).is_file():
            errors.append(f"{case['id']}: missing {expected}")
        if not any(path_matches(item, expected) for item in changed):
            errors.append(f"{case['id']}: {expected} not recorded as changed")
        if expected not in observed:
            errors.append(f"{case['id']}: {expected} absent from actual git changes")
    if case.get("inspect_only") or case["id"] in {
        "mature-preservation",
        "pep621-partial-inspect",
        "pep621-legacy-setupcfg",
    }:
        if changed or observed:
            errors.append(f"{case['id']}: fixture was modified")
    for relative, terms in case.get("required_text", {}).items():
        try:
            content = (fixture / relative).read_text(encoding="utf-8")
        except OSError:
            continue
        for term in terms:
            if term not in content:
                errors.append(f"{case['id']}: {relative} missing required content {term!r}")
    errors.extend(executable_errors(case, fixture))
    errors.extend(script_entry_errors(case, fixture))
    errors.extend(case_fixture_error(case["id"], fixture))
    tools = " ".join(result.get("preserved_tools", [])).lower()
    for tool in case.get("preserved_tools", []):
        if tool not in tools:
            errors.append(f"{case['id']}: did not preserve {tool}")
    if not contains_any(result.get("summary", ""), case["summary_terms"]):
        errors.append(f"{case['id']}: summary lacks expected evidence")
    return errors


def grade_results(results_dir: Path, fixtures_dir: Path) -> dict[str, Any]:
    graded = []
    for case in read_json(CASES)["cases"]:
        try:
            result = read_json(results_dir / f"{case['id']}-result.json")
            errors = grade_case(case, result, fixtures_dir / case["id"])
        except (OSError, ValueError, TypeError) as exc:
            errors = [f"{case['id']}: unreadable result: {exc}"]
        graded.append({"id": case["id"], "passed": not errors, "errors": errors})
    return {"passed": all(item["passed"] for item in graded), "case_count": len(graded), "cases": graded}


def self_test() -> int:
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        results = base / "results"
        fixtures = base / "fixtures"
        results.mkdir()
        for case in read_json(CASES)["cases"]:
            fixture = fixtures / case["id"]
            fixture.mkdir(parents=True)
            subprocess.run(["git", "init", "-b", "main"], cwd=fixture, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Grader Self Test"], cwd=fixture, check=True)
            subprocess.run(["git", "config", "user.email", "grader@example.invalid"], cwd=fixture, check=True)
            subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=fixture, check=True)
            if case["id"] == "mature-preservation":

                (fixture / "legacy_app").mkdir()

                (fixture / "tests").mkdir()

                (fixture / "legacy_app/__init__.py").write_text('"""Legacy app."""\n', encoding="utf-8")

                (fixture / "tests/test_app.py").write_text("def test_app():\n    assert True\n", encoding="utf-8")

                (fixture / "pyproject.toml").write_text('[tool.poetry]\nname = "legacy-app"\nversion = "1.0.0"\n\n[tool.black]\nline-length = 88\n\n[tool.poetry.dependencies]\npython = "^3.10"\n', encoding="utf-8")

                (fixture / "tox.ini").write_text("[tox]\nenvlist = py310\n", encoding="utf-8")

            elif case["id"] == "pep621-partial-inspect":

                (fixture / "src" / "sample_pkg").mkdir(parents=True)

                (fixture / "tests").mkdir()

                (fixture / ".github" / "workflows").mkdir(parents=True)

                (fixture / "src" / "sample_pkg" / "__init__.py").write_text('__version__ = "0.1.0"\n', encoding="utf-8")

                (fixture / "tests" / "test_basic.py").write_text("def test_basic():\n    assert True\n", encoding="utf-8")

                (fixture / "pyproject.toml").write_text('[build-system]\nrequires = ["setuptools>=77.0.3", "wheel"]\nbuild-backend = "setuptools.build_meta"\n\n[project]\nname = "sample-pkg"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n\n[tool.ruff]\ntarget-version = "py310"\n\n[tool.mypy]\npython_version = "3.10"\n', encoding="utf-8")

                (fixture / ".github" / "workflows" / "ci.yml").write_text("name: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    strategy:\n      matrix:\n        python-version: ['3.10', '3.11']\n    steps:\n      - uses: actions/checkout@v4\n", encoding="utf-8")

            elif case["id"] == "pep621-legacy-setupcfg":

                (fixture / "legacy_pkg").mkdir()

                (fixture / "tests").mkdir()

                (fixture / "legacy_pkg" / "__init__.py").write_text("__version__ = '0.1.0'\n", encoding="utf-8")

                (fixture / "tests" / "test_basic.py").write_text("def test_basic():\n    assert True\n", encoding="utf-8")

                (fixture / "setup.cfg").write_text("[metadata]\nname = legacy-pkg\nversion = 0.1.0\ndescription = Legacy package\n\n[options]\npackages = find:\npython_requires = >=3.9\n", encoding="utf-8")

                (fixture / "setup.py").write_text("from setuptools import setup\n\nsetup()\n", encoding="utf-8")

            if case["expected_paths"]:

                subprocess.run(["git", "commit", "--allow-empty", "-m", "baseline"], cwd=fixture, check=True, capture_output=True)

                for relative in case["expected_paths"]:

                    path = fixture / relative

                    path.parent.mkdir(parents=True, exist_ok=True)

                    content = "fixture\n"

                    if relative == "pyproject.toml":

                        content = '[project]\nname = "invoice-checker"\n\n[project.scripts]\ninvoice-checker = "invoice_checker.cli:main"\n'

                    elif relative.endswith("cli.py"):

                        content = "def main():\n    return 0\n"

                    elif relative.endswith(".py"):

                        content = "# valid Python fixture\n"

                    path.write_text(content, encoding="utf-8")

            else:

                subprocess.run(["git", "add", "."], cwd=fixture, check=True, capture_output=True)

                subprocess.run(["git", "commit", "-m", "baseline"], cwd=fixture, check=True, capture_output=True)
            result = {
                "skills_used": ["python-project-workflow"],
                "classification": case["classification_terms"][0],
                "changed_paths": [f"/tmp/fixture/{item}" for item in case["expected_paths"]],
                "preserved_tools": case.get("preserved_tools", []),
                "summary": " ".join(case["summary_terms"]),
                "limitations": [],
            }
            (results / f"{case['id']}-result.json").write_text(json.dumps(result), encoding="utf-8")
        assert grade_results(results, fixtures)["passed"]
        mature = fixtures / "mature-preservation" / "unexpected.txt"
        mature.write_text("unexpected\n", encoding="utf-8")
        assert not grade_results(results, fixtures)["passed"]
        bad_partial = fixtures / "pep621-partial-inspect" / "pyproject.toml"
        bad_partial.write_text(bad_partial.read_text(encoding="utf-8") + 'description = "added"\nreadme = "README.md"\n', encoding="utf-8")
        results_bad = base / "results-bad"
        results_bad.mkdir()
        for case in read_json(CASES)["cases"]:
            src = json.loads((results / f"{case['id']}-result.json").read_text(encoding="utf-8"))
            if case["id"] == "pep621-partial-inspect":
                src["summary"] = "looks fine"
            (results_bad / f"{case['id']}-result.json").write_text(json.dumps(src), encoding="utf-8")
        assert not grade_results(results_bad, fixtures)["passed"]
    print(f"validated grader against {len(read_json(CASES)['cases'])} cases")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path)
    parser.add_argument("--fixtures-dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.results_dir or not args.fixtures_dir:
        parser.error("--results-dir and --fixtures-dir are required")
    grade = grade_results(args.results_dir, args.fixtures_dir)
    rendered = json.dumps(grade, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if grade["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
