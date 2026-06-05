from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

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
    "mature-repo-preservation.md",
    "eval-benchmark-hardening.md",
]
REQUIRED_EVALS = [
    "greenfield-setup",
    "existing-file-review",
    "incremental-typing-testing",
    "existing-project-preservation",
    "non-python-doc-only",
    "generic-python-question",
    "typo-in-docstring",
    "shell-script-question",
    "mature-automation-repo-preservation",
]


def make_minimal_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "skill" / "references").mkdir(parents=True)
    for fixture_name in ["sample", "existing-buggy", "existing-preserve", "mature-automation-repo"]:
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

    # Triggering evals (first 4) need should_trigger=True + expected_references + must_include
    # Non-trigger evals (last 4) need should_trigger=False, empty refs/includes
    trigger_names = {
        "greenfield-setup",
        "existing-file-review",
        "incremental-typing-testing",
        "existing-project-preservation",
        "mature-automation-repo-preservation",
    }
    evals = []
    for name in REQUIRED_EVALS:
        if name in trigger_names:
            evals.append({
                "name": name,
                "fixture": "evals/fixtures/sample",
                "prompt": f"Prompt for {name}",
                "should_trigger": True,
                "expected_references": ["project-orientation.md"],
                "must_include": ["inspect"],
                "must_not_include": [],
            })
        else:
            evals.append({
                "name": name,
                "fixture": "evals/fixtures/sample",
                "prompt": f"Prompt for {name}",
                "should_trigger": False,
                "expected_references": [],
                "must_include": [],
                "must_not_include": ["python-best-practices"],
            })
    (repo / "evals" / "evals.json").write_text(json.dumps({"schema_version": 1, "evals": evals}), encoding="utf-8")
    trigger_description_evals = [
        {
            "id": f"trigger-{index}",
            "query": f"Python project query {index}",
            "should_trigger": index <= 10,
            "category": "trigger" if index <= 10 else "near-miss",
            "rationale": "Minimal trigger-description eval for checker tests.",
            "expected_boundary": "Minimal expected boundary.",
        }
        for index in range(1, 21)
    ]
    (repo / "evals" / "trigger-description-evals.json").write_text(
        json.dumps({"schema_version": 1, "status": "draft-for-user-review", "evals": trigger_description_evals}),
        encoding="utf-8",
    )
    (repo / "AGENTS.md").write_text(
        "\n".join([
            "# Agent contract",
            "**Last verified:** 2026-06-04",
            "## Orientation Contract — BLOCKING",
            "## Source, Mirror, and Shipping Policy — BLOCKING",
            "Treat `skill/` as the canonical runtime payload.",
            "Do not publish, package, install elsewhere, sync to another Hermes profile, push, tag, or release.",
            "## Phase and User-Shipping Guard — BLOCKING",
            "## Drift and Stale Information Contract — BLOCKING",
            "## Generated State Guard — BLOCKING",
        ]),
        encoding="utf-8",
    )
    (repo / "README.md").write_text(
        "Shipping boundary: `skill/` is the runtime payload and source of truth.\n",
        encoding="utf-8",
    )
    (repo / "plan.md").write_text(
        "\n".join([
            "### Phase 4 — Polish, Ship & Publish",
            "`skill/` is the directory-as-boundary runtime payload.",
            "Produce a concise user handoff.",
            "confirmation that repository-only files are absent from the runtime payload.",
        ]),
        encoding="utf-8",
    )
    (repo / "todos.md").write_text("# TODOs\n", encoding="utf-8")
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


def test_missing_trigger_description_eval_set_reports_hint(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "evals" / "trigger-description-evals.json").unlink()

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 1
    assert "required file is missing: evals/trigger-description-evals.json" in result.stderr


def test_imbalanced_trigger_description_eval_set_reports_hint(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    data = json.loads((repo / "evals" / "trigger-description-evals.json").read_text(encoding="utf-8"))
    data["evals"][10]["should_trigger"] = True
    (repo / "evals" / "trigger-description-evals.json").write_text(json.dumps(data), encoding="utf-8")

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 1
    assert "must contain 10 trigger and 10 non-trigger queries" in result.stderr
    assert "balanced between should-trigger and should-not-trigger" in result.stderr


def test_optimization_complete_trigger_eval_set_requires_selected_description(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    data = json.loads((repo / "evals" / "trigger-description-evals.json").read_text(encoding="utf-8"))
    data["status"] = "optimization-complete"
    (repo / "evals" / "trigger-description-evals.json").write_text(json.dumps(data), encoding="utf-8")

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 1
    assert "optimization-complete trigger eval set must record selected_description" in result.stderr


def test_optimization_complete_trigger_eval_set_passes_with_selected_description(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    data = json.loads((repo / "evals" / "trigger-description-evals.json").read_text(encoding="utf-8"))
    data["status"] = "optimization-complete"
    data["selected_description"] = "Use for Python project code and tooling work after inspecting repo conventions."
    (repo / "evals" / "trigger-description-evals.json").write_text(json.dumps(data), encoding="utf-8")

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 0


def test_unknown_trigger_description_eval_status_reports_allowed_values(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    data = json.loads((repo / "evals" / "trigger-description-evals.json").read_text(encoding="utf-8"))
    data["status"] = "ready"
    (repo / "evals" / "trigger-description-evals.json").write_text(json.dumps(data), encoding="utf-8")

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 1
    assert "status must be one of" in result.stderr
    assert "draft-for-user-review" in result.stderr
    assert "optimization-complete" in result.stderr


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


def test_eval_prompt_referencing_missing_fixture_symbol_reports_hint(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    data = json.loads((repo / "evals" / "evals.json").read_text(encoding="utf-8"))
    data["evals"][0]["prompt"] = "Please fix `missing_symbol` in this fixture."
    (repo / "evals" / "evals.json").write_text(json.dumps(data), encoding="utf-8")

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 1
    assert "prompt references fixture symbol(s) not found" in result.stderr
    assert "missing_symbol" in result.stderr
    assert "HINT: Update the prompt or fixture" in result.stderr


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda item: item.update({"must_include_any": "not-a-list"}), "field 'must_include_any' must be a list"),
        (
            lambda item: item.update({"must_include_any": [{"terms": ["inspect"]}]}),
            "must_include_any group #1 needs a non-empty string name",
        ),
        (
            lambda item: item.update({"must_include_any": [{"name": "orientation", "terms": [""]}]}),
            "must_include_any group 'orientation' has invalid terms",
        ),
    ],
)
def test_invalid_must_include_any_schema_reports_actionable_error(tmp_path: Path, mutation, expected: str) -> None:
    repo = make_minimal_repo(tmp_path)
    data = json.loads((repo / "evals" / "evals.json").read_text(encoding="utf-8"))
    mutation(data["evals"][0])
    (repo / "evals" / "evals.json").write_text(json.dumps(data), encoding="utf-8")

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 1
    assert expected in result.stderr


def test_removed_implementation_summary_reports_live_status_hint(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "IMPLEMENTATION_SUMMARY.md").write_text("stale status snapshot", encoding="utf-8")

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 1
    assert "IMPLEMENTATION_SUMMARY.md should not exist" in result.stderr
    assert "Keep live status in README.md, plan.md, and todos.md" in result.stderr


def test_installed_mirror_mismatch_reports_sync_hint(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    mirror = repo / ".installed-skill-mirror"
    shutil.copytree(repo / "skill", mirror)
    (mirror / "references" / "review-checklist.md").write_text("stale mirror", encoding="utf-8")

    result = run_checker(repo)

    assert result.returncode == 1
    assert "installed mirror reference differs: review-checklist.md" in result.stderr
    assert "HINT: Run python3 scripts/run_phase2_checks.py --sync-installed" in result.stderr


def test_installed_mirror_extra_file_reports_sync_hint(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    mirror = repo / ".installed-skill-mirror"
    shutil.copytree(repo / "skill", mirror)
    (mirror / "references" / "stale-runtime-only.md").write_text("not in source skill/", encoding="utf-8")

    result = run_checker(repo)

    assert result.returncode == 1
    assert "installed mirror has file(s) outside source runtime payload" in result.stderr
    assert "references/stale-runtime-only.md" in result.stderr
    assert "replace the mirror with the canonical skill/ payload" in result.stderr


def test_sync_installed_replaces_extra_mirror_files(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    mirror = repo / ".installed-skill-mirror"
    shutil.copytree(repo / "skill", mirror)
    stale_file = mirror / "references" / "stale-runtime-only.md"
    stale_file.write_text("not in source skill/", encoding="utf-8")

    result = run_checker(repo, "--sync-installed")

    assert result.returncode == 0
    assert not stale_file.exists()


def test_sync_installed_copies_mature_repo_reference(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    mirror = repo / ".installed-skill-mirror"

    result = run_checker(repo, "--sync-installed")

    assert result.returncode == 0
    assert (mirror / "references" / "mature-repo-preservation.md").exists()


def test_missing_mature_repo_eval_reports_required_eval(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    data = json.loads((repo / "evals" / "evals.json").read_text(encoding="utf-8"))
    data["evals"] = [item for item in data["evals"] if item["name"] != "mature-automation-repo-preservation"]
    (repo / "evals" / "evals.json").write_text(json.dumps(data), encoding="utf-8")

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 1
    assert "missing required evals" in result.stderr
    assert "mature-automation-repo-preservation" in result.stderr


def test_missing_agent_shipping_guard_reports_hint(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
    (repo / "AGENTS.md").write_text(
        agents.replace("## Source, Mirror, and Shipping Policy — BLOCKING", "## Source Policy"),
        encoding="utf-8",
    )

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 1
    assert "AGENTS.md is missing required repo guard phrase" in result.stderr
    assert "Restore the source/mirror/shipping" in result.stderr


def test_generated_agent_state_marker_reports_hint(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    with (repo / "AGENTS.md").open("a", encoding="utf-8") as file:
        file.write("\n<!-- open-mem-context -->\n")

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 1
    assert "AGENTS.md contains generated/session-state marker" in result.stderr
    assert "Remove transient agent state" in result.stderr


def test_missing_phase4_shipping_boundary_reports_hint(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "plan.md").write_text("### Phase 4 — Polish & Publish\n", encoding="utf-8")

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 1
    assert "plan.md is missing required shipping-phase phrase" in result.stderr
    assert "explicit user-shipping/publishing phase" in result.stderr


def test_shipping_boundary_check_accepts_markdown_wrapped_phrase(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "plan.md").write_text(
        "\n".join([
            "### Phase 4 — Polish, Ship & Publish",
            "`skill/` is the directory-as-boundary runtime payload.",
            "Produce a concise user handoff.",
            "confirmation that repository-only files are absent from the runtime",
            "payload.",
        ]),
        encoding="utf-8",
    )

    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 0
