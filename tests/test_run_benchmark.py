from __future__ import annotations

import importlib.util
import json
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


def test_run_status_check_fails_nonzero_exit() -> None:
    expectations = run_benchmark.check_run_status(-1)

    assert failed_texts(expectations) == ["Agent run completed without command error or timeout"]
    assert "-1" in expectations[0]["evidence"]


def test_run_status_check_passes_clean_exit_without_extra_expectation() -> None:
    assert run_benchmark.check_run_status(0) == []
