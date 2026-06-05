from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_benchmark.py"

spec = importlib.util.spec_from_file_location("run_benchmark", SCRIPT)
assert spec is not None
run_benchmark = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_benchmark)


def failed_texts(expectations: list[dict]) -> list[str]:
    return [item["text"] for item in expectations if not item["passed"]]


def test_filesystem_change_check_detects_nested_modification(tmp_path: Path) -> None:
    original = tmp_path / "original"
    working = tmp_path / "working"
    (original / "pkg").mkdir(parents=True)
    (working / "pkg").mkdir(parents=True)
    (original / "pkg" / "core.py").write_text("VALUE = 1\n", encoding="utf-8")
    (working / "pkg" / "core.py").write_text("VALUE = 2\n", encoding="utf-8")

    expectations = run_benchmark.check_filesystem_changes(original, working)

    assert failed_texts(expectations) == ["Agent did not modify fixture file: pkg/core.py"]


def test_filesystem_change_check_detects_nested_deletion(tmp_path: Path) -> None:
    original = tmp_path / "original"
    working = tmp_path / "working"
    (original / "pkg").mkdir(parents=True)
    (working / "pkg").mkdir(parents=True)
    (original / "pkg" / "core.py").write_text("VALUE = 1\n", encoding="utf-8")

    expectations = run_benchmark.check_filesystem_changes(original, working)

    assert failed_texts(expectations) == ["Agent did not delete fixture file: pkg/core.py"]


def test_filesystem_change_check_detects_nested_creation(tmp_path: Path) -> None:
    original = tmp_path / "original"
    working = tmp_path / "working"
    (original / "pkg").mkdir(parents=True)
    (working / "pkg").mkdir(parents=True)
    (working / "pkg" / "new.py").write_text("VALUE = 1\n", encoding="utf-8")

    expectations = run_benchmark.check_filesystem_changes(original, working)

    assert failed_texts(expectations) == ["Agent did not create unexpected file: pkg/new.py"]


def test_filesystem_change_check_ignores_tool_artifacts(tmp_path: Path) -> None:
    original = tmp_path / "original"
    working = tmp_path / "working"
    original.mkdir()
    working.mkdir()
    (working / ".open-mem").mkdir()
    (working / ".open-mem" / "memory.db").write_text("generated", encoding="utf-8")
    (working / ".omo").mkdir()
    (working / ".omo" / "context.json").write_text("generated", encoding="utf-8")
    (working / "raw-output.txt").write_text("stdout", encoding="utf-8")
    (working / "stderr.txt").write_text("stderr", encoding="utf-8")

    expectations = run_benchmark.check_filesystem_changes(original, working)

    assert expectations == []


def test_build_output_dir_handles_missing_base_directory(tmp_path: Path) -> None:
    base = tmp_path / "missing-workspace"

    output_dir = run_benchmark.build_output_dir(base, None)

    assert output_dir == base / "iteration-1"


def test_benchmark_output_names_are_backend_neutral() -> None:
    assert run_benchmark.RESPONSE_FILENAME == "response.md"
    assert run_benchmark.RAW_STDOUT_FILENAME == "raw-output.txt"
    assert run_benchmark.RAW_STDERR_FILENAME == "stderr.txt"


def test_benchmark_writes_real_stderr_byte_count(tmp_path: Path, monkeypatch) -> None:
    skill_file = tmp_path / "skill" / "SKILL.md"
    ref_dir = tmp_path / "skill" / "references"
    evals_file = tmp_path / "evals.json"
    output_dir = tmp_path / "workspace"
    skill_file.parent.mkdir()
    ref_dir.mkdir()
    skill_file.write_text("---\nname: test\n---\n", encoding="utf-8")
    evals_file.write_text(
        json.dumps({"evals": [{"name": "sample", "prompt": "Hi", "should_trigger": False}]}),
        encoding="utf-8",
    )

    def fake_run_opencode(prompt, model, input_dir, *, timeout=300):
        return "answer\n", "raw stdout", "stderr text", 0, 1.25

    monkeypatch.setattr(run_benchmark, "SKILL_FILE", skill_file)
    monkeypatch.setattr(run_benchmark, "REF_DIR", ref_dir)
    monkeypatch.setattr(run_benchmark, "EVALS_FILE", evals_file)
    monkeypatch.setattr(run_benchmark, "run_opencode", fake_run_opencode)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_benchmark.py",
            "--output-dir",
            str(output_dir),
            "--iteration-label",
            "stderr-test",
            "--filter",
            "sample",
        ],
    )

    assert run_benchmark.main() == 0

    timing = json.loads((output_dir / "stderr-test" / "eval-0-sample" / "with_skill" / "timing.json").read_text())
    assert timing["stderr_bytes"] == len("stderr text".encode())


def test_benchmark_reused_iteration_label_clears_stale_input_files(tmp_path: Path, monkeypatch) -> None:
    skill_file = tmp_path / "skill" / "SKILL.md"
    ref_dir = tmp_path / "skill" / "references"
    evals_file = tmp_path / "evals.json"
    output_dir = tmp_path / "workspace"
    stale_input_file = output_dir / "reuse" / "eval-0-sample" / "with_skill" / "input" / "stale.py"
    skill_file.parent.mkdir()
    ref_dir.mkdir()
    stale_input_file.parent.mkdir(parents=True)
    skill_file.write_text("---\nname: test\n---\n", encoding="utf-8")
    stale_input_file.write_text("STALE = True\n", encoding="utf-8")
    evals_file.write_text(
        json.dumps({"evals": [{"name": "sample", "prompt": "Hi", "should_trigger": False}]}),
        encoding="utf-8",
    )

    def fake_run_opencode(prompt, model, input_dir, *, timeout=300):
        assert not (input_dir / "stale.py").exists()
        return "answer\n", "raw stdout", "", 0, 1.25

    monkeypatch.setattr(run_benchmark, "SKILL_FILE", skill_file)
    monkeypatch.setattr(run_benchmark, "REF_DIR", ref_dir)
    monkeypatch.setattr(run_benchmark, "EVALS_FILE", evals_file)
    monkeypatch.setattr(run_benchmark, "run_opencode", fake_run_opencode)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_benchmark.py",
            "--output-dir",
            str(output_dir),
            "--iteration-label",
            "reuse",
            "--filter",
            "sample",
        ],
    )

    assert run_benchmark.main() == 0
    assert not stale_input_file.exists()


def test_opencode_timeout_can_fall_back_to_codex(tmp_path: Path, monkeypatch) -> None:
    skill_file = tmp_path / "skill" / "SKILL.md"
    ref_dir = tmp_path / "skill" / "references"
    evals_file = tmp_path / "evals.json"
    output_dir = tmp_path / "workspace"
    skill_file.parent.mkdir()
    ref_dir.mkdir()
    skill_file.write_text("---\nname: test\n---\n", encoding="utf-8")
    evals_file.write_text(
        json.dumps({"evals": [{"name": "sample", "prompt": "Hi", "should_trigger": False}]}),
        encoding="utf-8",
    )

    def fake_run_opencode(prompt, model, input_dir, *, timeout=300):
        raise subprocess.TimeoutExpired(cmd="opencode", timeout=timeout)

    def fake_run_codex(prompt, model, input_dir, output_dir_cfg, *, timeout=300):
        assert model == "fallback-model"
        return "fallback answer\n", "raw fallback", "codex stderr", 0, 2.5

    monkeypatch.setattr(run_benchmark, "SKILL_FILE", skill_file)
    monkeypatch.setattr(run_benchmark, "REF_DIR", ref_dir)
    monkeypatch.setattr(run_benchmark, "EVALS_FILE", evals_file)
    monkeypatch.setattr(run_benchmark, "run_opencode", fake_run_opencode)
    monkeypatch.setattr(run_benchmark, "run_codex", fake_run_codex)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_benchmark.py",
            "--backend",
            "opencode",
            "--fallback-backend",
            "codex",
            "--fallback-model",
            "fallback-model",
            "--timeout",
            "7",
            "--output-dir",
            str(output_dir),
            "--iteration-label",
            "fallback",
            "--filter",
            "sample",
        ],
    )

    assert run_benchmark.main() == 0

    run_dir = output_dir / "fallback" / "eval-0-sample" / "with_skill"
    assert (run_dir / "outputs" / "response.md").read_text() == "fallback answer\n"
    timing = json.loads((run_dir / "timing.json").read_text())
    assert timing["duration_seconds"] == 9.5
    assert timing["backend"] == "opencode"
    assert timing["effective_backend"] == "codex"
    assert timing["model"] == "opencode/big-pickle"
    assert timing["effective_model"] == "fallback-model"
    assert timing["fallback_reason"] == "opencode_timeout"
    stderr = (run_dir / "outputs" / "stderr.txt").read_text()
    assert "OpenCode timed out after 7s" in stderr
    assert "fallback_backend=codex fallback_model=fallback-model" in stderr
    benchmark = json.loads((output_dir / "fallback" / "benchmark.json").read_text())
    assert benchmark["metadata"]["backend"] == "opencode"
    assert benchmark["metadata"]["model"] == "opencode/big-pickle"
    assert benchmark["metadata"]["fallback_backend"] == "codex"
    assert benchmark["metadata"]["fallback_model"] == "fallback-model"
    assert benchmark["runs"][0]["result"]["effective_backend"] == "codex"
    assert benchmark["runs"][0]["result"]["effective_model"] == "fallback-model"
    assert benchmark["runs"][0]["result"]["fallback_reason"] == "opencode_timeout"


def test_opencode_timeout_and_codex_fallback_timeout_are_recorded(tmp_path: Path, monkeypatch) -> None:
    skill_file = tmp_path / "skill" / "SKILL.md"
    ref_dir = tmp_path / "skill" / "references"
    evals_file = tmp_path / "evals.json"
    output_dir = tmp_path / "workspace"
    skill_file.parent.mkdir()
    ref_dir.mkdir()
    skill_file.write_text("---\nname: test\n---\n", encoding="utf-8")
    evals_file.write_text(
        json.dumps({"evals": [{"name": "sample", "prompt": "Hi", "should_trigger": False}]}),
        encoding="utf-8",
    )

    def fake_run_opencode(prompt, model, input_dir, *, timeout=300):
        raise subprocess.TimeoutExpired(cmd="opencode", timeout=timeout)

    def fake_run_codex(prompt, model, input_dir, output_dir_cfg, *, timeout=300):
        raise subprocess.TimeoutExpired(cmd="codex", timeout=timeout)

    monkeypatch.setattr(run_benchmark, "SKILL_FILE", skill_file)
    monkeypatch.setattr(run_benchmark, "REF_DIR", ref_dir)
    monkeypatch.setattr(run_benchmark, "EVALS_FILE", evals_file)
    monkeypatch.setattr(run_benchmark, "run_opencode", fake_run_opencode)
    monkeypatch.setattr(run_benchmark, "run_codex", fake_run_codex)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_benchmark.py",
            "--backend",
            "opencode",
            "--fallback-backend",
            "codex",
            "--fallback-model",
            "fallback-model",
            "--timeout",
            "7",
            "--output-dir",
            str(output_dir),
            "--iteration-label",
            "fallback-timeout",
            "--filter",
            "sample",
        ],
    )

    assert run_benchmark.main() == 0

    run_dir = output_dir / "fallback-timeout" / "eval-0-sample" / "with_skill"
    assert (run_dir / "outputs" / "response.md").read_text() == (
        "TIMEOUT after 7s; codex fallback also timed out after 7s"
    )
    timing = json.loads((run_dir / "timing.json").read_text())
    assert timing["duration_seconds"] == 14.0
    assert timing["backend"] == "opencode"
    assert timing["effective_backend"] == "codex"
    assert timing["model"] == "opencode/big-pickle"
    assert timing["effective_model"] == "fallback-model"
    assert timing["fallback_reason"] == "opencode_timeout_codex_timeout"
    benchmark = json.loads((output_dir / "fallback-timeout" / "benchmark.json").read_text())
    assert benchmark["runs"][0]["result"]["errors"] == 1
    assert benchmark["runs"][0]["result"]["effective_backend"] == "codex"
    assert benchmark["runs"][0]["result"]["effective_model"] == "fallback-model"
    assert benchmark["runs"][0]["result"]["fallback_reason"] == "opencode_timeout_codex_timeout"


def test_fallback_backend_requires_opencode_backend(tmp_path: Path, monkeypatch) -> None:
    skill_file = tmp_path / "skill" / "SKILL.md"
    skill_file.parent.mkdir()
    skill_file.write_text("---\nname: test\n---\n", encoding="utf-8")
    monkeypatch.setattr(run_benchmark, "SKILL_FILE", skill_file)
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_benchmark.py", "--backend", "codex", "--fallback-backend", "codex"],
    )

    assert run_benchmark.main() == 1


def test_run_status_check_fails_nonzero_exit() -> None:
    expectations = run_benchmark.check_run_status(-1)

    assert failed_texts(expectations) == ["Agent run completed without command error or timeout"]
    assert "-1" in expectations[0]["evidence"]


def test_run_status_check_passes_clean_exit_without_extra_expectation() -> None:
    assert run_benchmark.check_run_status(0) == []


def test_grade_output_supports_include_any_groups() -> None:
    expectations = run_benchmark.grade_output(
        "Use a context manager with open() so file handles are closed.\n",
        {
            "must_include": [],
            "must_include_any": [
                {
                    "name": "file resource handling issue",
                    "terms": ["resource", "context manager", "with open"],
                }
            ],
            "must_not_include": [],
        },
    )

    assert expectations == [
        {
            "text": "Includes expected guidance group: file resource handling issue",
            "passed": True,
            "evidence": "Found alternative(s): ['context manager', 'with open'].",
        }
    ]


def test_grade_output_fails_include_any_group_when_all_terms_missing() -> None:
    expectations = run_benchmark.grade_output(
        "No relevant guidance here.\n",
        {
            "must_include": [],
            "must_include_any": [
                {
                    "name": "wildcard import issue",
                    "terms": ["wildcard", "import *"],
                }
            ],
            "must_not_include": [],
        },
    )

    assert failed_texts(expectations) == ["Includes expected guidance group: wildcard import issue"]
    assert "Missing all alternatives" in expectations[0]["evidence"]
