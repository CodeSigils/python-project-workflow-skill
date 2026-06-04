from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase2_checks.py"

REQUIRED_SECTIONS = [
    "## When to Use This Skill",
    "## Orientation Checklist",
    "## Task Classification Table",
    "## Verification Commands",
    "## Preserve Local Conventions",
]
REQUIRED_REFS = [
    "project-orientation.md",
    "pyproject-template.md",
    "lint-format-typing-testing.md",
    "review-checklist.md",
]
REQUIRED_EVALS = [
    "greenfield-setup",
    "existing-file-review",
    "incremental-typing-testing",
    "existing-project-preservation",
    "non-python-doc-only",
    "generic-python-question",
]


def make_minimal_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "skill" / "references").mkdir(parents=True)
    for fixture_name in ["sample", "existing-buggy", "existing-preserve"]:
        (repo / "evals" / "fixtures" / fixture_name / "tests").mkdir(parents=True)
        (repo / "evals" / "fixtures" / fixture_name / "tests" / "test_sample.py").write_text(
            "def test_sample():\n    assert True\n",
            encoding="utf-8",
        )

    skill_text = "---\nname: python-best-practices\n---\n\n" + "\n".join(REQUIRED_SECTIONS)
    (repo / "skill" / "SKILL.md").write_text(skill_text, encoding="utf-8")

    reference_body = "# Reference\n\n" + ("Detailed guidance for validation tests.\n" * 30)
    for name in REQUIRED_REFS:
        (repo / "skill" / "references" / name).write_text(reference_body, encoding="utf-8")

    evals = [
        {
            "name": name,
            "fixture": "evals/fixtures/sample",
            "prompt": f"Prompt for {name}",
            "should_trigger": True,
            "expected_references": ["project-orientation.md"],
            "must_include": ["inspect"],
            "must_not_include": [],
        }
        for name in REQUIRED_EVALS
    ]
    (repo / "evals" / "evals.json").write_text(json.dumps({"schema_version": 1, "evals": evals}), encoding="utf-8")
    return repo


def run_checker(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PBP_SKILL_ROOT"] = str(repo)
    env["PBP_SKILL_INSTALLED"] = str(repo / ".installed-skill-mirror")
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )


def test_source_only_check_can_run_against_temp_repo(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 0
    assert "source files only are valid" in result.stdout


def test_invalid_evals_json_reports_line_column_and_hint(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "evals" / "evals.json").write_text('{"schema_version": 1, "evals": [}', encoding="utf-8")

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 1
    assert "invalid JSON in evals/evals.json" in result.stderr
    assert "line 1" in result.stderr
    assert "HINT: Fix evals/evals.json syntax" in result.stderr


def test_missing_reference_reports_recovery_hint(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "skill" / "references" / "review-checklist.md").unlink()

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 1
    assert "missing reference files" in result.stderr
    assert "review-checklist.md" in result.stderr
    assert "HINT: Create the missing files under skill/references/" in result.stderr


def test_installed_mirror_mismatch_reports_sync_hint(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    mirror = repo / ".installed-skill-mirror"
    shutil.copytree(repo / "skill", mirror)
    (mirror / "references" / "review-checklist.md").write_text("stale mirror", encoding="utf-8")

    result = run_checker(repo)

    assert result.returncode == 1
    assert "installed mirror reference differs: review-checklist.md" in result.stderr
    assert "HINT: Run python3 scripts/run_phase2_checks.py --sync-installed" in result.stderr
