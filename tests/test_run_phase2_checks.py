from __future__ import annotations

import json
import os
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


def test_minimal_repo_passes(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    result = run_checker(repo, "--skip-installed")
    msg = f"stdout={result.stdout!r} stderr={result.stderr!r}"
    assert result.returncode == 0, msg


def test_missing_skill_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "skill" / "SKILL.md").unlink()
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1


def test_missing_reference_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "skill" / "references" / "project-orientation.md").unlink()
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1


def test_empty_evals_json_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "evals" / "evals.json").write_text("{}", encoding="utf-8")
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1


def test_missing_trigger_eval_set_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "evals" / "trigger-description-evals.json").unlink()
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1


def test_bad_trigger_eval_count_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    items = [
        {
            "id": f"t{i}",
            "query": "Test",
            "should_trigger": i <= 5,
            "category": "test",
            "rationale": "Test",
            "expected_boundary": "Test",
        }
        for i in range(1, 12)
    ]
    (repo / "evals" / "trigger-description-evals.json").write_text(
        json.dumps({"schema_version": 1, "status": "draft-for-user-review", "evals": items}),
        encoding="utf-8",
    )
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1
    assert "must contain 20" in result.stderr


def test_missing_contract_section_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "AGENTS.md").write_text("# Minimal\n", encoding="utf-8")
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1


def test_gentle_forbidden_marker_fails(tmp_path: Path) -> None:
    """AGENTS.md with generated session markers must fail."""
    repo = make_minimal_repo(tmp_path)
    text = (repo / "AGENTS.md").read_text(encoding="utf-8")
    (repo / "AGENTS.md").write_text(
        text + "\n<!-- open-mem-context -->\n",
        encoding="utf-8",
    )
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1


def test_missing_shipping_phrases_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "plan.md").write_text("Minimal plan.\n", encoding="utf-8")
    result = run_checker(repo, "--skip-installed")

    assert result.returncode == 1
    assert "plan.md is missing required shipping-phase phrase" in result.stderr


def test_missing_shipping_boundary_in_readme_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "README.md").write_text("No boundary mentioned.\n", encoding="utf-8")
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1
    assert "README.md is missing the shipping boundary summary" in result.stderr


def test_imp_summary_file_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "IMPLEMENTATION_SUMMARY.md").write_text("Should not exist.\n", encoding="utf-8")
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1
    assert "IMPLEMENTATION_SUMMARY.md should not exist" in result.stderr


def test_imp_summary_in_readme_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    readme = (repo / "README.md").read_text(encoding="utf-8")
    (repo / "README.md").write_text(
        readme + "\nSee IMPLEMENTATION_SUMMARY.md for details.\n",
        encoding="utf-8",
    )
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1
    assert "stale IMPLEMENTATION_SUMMARY.md reference remains in README.md" in result.stderr


def test_non_compiling_fixture_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    (repo / "evals" / "fixtures" / "sample" / "bad.py").write_text(
        "def broken(\n    pass\n",
        encoding="utf-8",
    )
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1
    assert "fixture Python file does not compile" in result.stderr


def test_bad_trigger_eval_imbalance_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    items = [
        {
            "id": f"t{i}",
            "query": "Test",
            "should_trigger": True,
            "category": "trigger",
            "rationale": "Test",
            "expected_boundary": "Test",
        }
        for i in range(1, 21)
    ]
    (repo / "evals" / "trigger-description-evals.json").write_text(
        json.dumps({"schema_version": 1, "status": "draft-for-user-review", "evals": items}),
        encoding="utf-8",
    )
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1
    assert "must contain 10 trigger and 10 non-trigger" in result.stderr


def test_missing_must_include_for_trigger_evals_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    evals_path = repo / "evals" / "evals.json"
    data = json.loads(evals_path.read_text(encoding="utf-8"))
    for item in data["evals"]:
        if item["should_trigger"]:
            item["must_include"] = []
    evals_path.write_text(json.dumps(data), encoding="utf-8")
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1
    assert "must_include" in result.stderr


def test_missing_expected_refs_for_trigger_evals_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    evals_path = repo / "evals" / "evals.json"
    data = json.loads(evals_path.read_text(encoding="utf-8"))
    for item in data["evals"]:
        if item["should_trigger"]:
            item["expected_references"] = []
    evals_path.write_text(json.dumps(data), encoding="utf-8")
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1
    assert "triggering eval must name expected references" in result.stderr


def test_unknown_reference_in_evals_fails(tmp_path: Path) -> None:
    repo = make_minimal_repo(tmp_path)
    evals_path = repo / "evals" / "evals.json"
    data = json.loads(evals_path.read_text(encoding="utf-8"))
    for item in data["evals"]:
        if item["should_trigger"]:
            item["expected_references"] = ["non-existent.md"]
    evals_path.write_text(json.dumps(data), encoding="utf-8")
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 1
    assert "references missing runtime files" in result.stderr


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


def test_markdown_format_check_skips_gracefully(tmp_path: Path) -> None:
    """The markdown format check should pass gracefully regardless of formatter availability."""
    repo = make_minimal_repo(tmp_path)
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 0


def test_commit_author_guard_warns_on_bot_author(tmp_path: Path) -> None:
    """The author guard should warn when a recent commit has bot-like authorship."""
    repo = make_minimal_repo(tmp_path)

    # Initialize a git repo with a bot-authored commit.
    # Only stage test.txt so the markdown formatter check doesn't see
    # unformatted repo scaffolding files.
    subprocess.run(["git", "init"], cwd=repo, check=True, timeout=10,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "bot@dependabot.com"], cwd=repo, check=True, timeout=10,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.name", "dependabot[bot]"], cwd=repo, check=True, timeout=10,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    (repo / "test.txt").write_text("test\n", encoding="utf-8")
    subprocess.run(["git", "add", "test.txt"], cwd=repo, check=True, timeout=10,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["git", "commit", "-m", "bot commit"], cwd=repo, check=True, timeout=10,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 0
    assert "WARNING:" in result.stderr
    assert "dependabot" in result.stderr.lower()
    assert "author" in result.stderr.lower()


def test_commit_author_guard_skips_when_no_git(tmp_path: Path) -> None:
    """The author guard should pass gracefully when not in a git repo."""
    repo = make_minimal_repo(tmp_path)
    result = run_checker(repo, "--skip-installed")
    assert result.returncode == 0
