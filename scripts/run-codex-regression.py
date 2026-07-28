#!/usr/bin/env python3
"""Run isolated Codex behavior cases for python-project-workflow."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals/codex/cases.json"
SCHEMA = ROOT / "evals/codex/result.schema.json"
GRADER = ROOT / "scripts/grade-codex-regression.py"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def checked(command: list[str], cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout


def prepare_fixture(root: Path, case: dict[str, Any]) -> None:
    if root.exists():
        raise FileExistsError(root)
    (root / ".agents/skills").mkdir(parents=True)
    shutil.copytree(ROOT / "skills/python-project-workflow", root / ".agents/skills/python-project-workflow")
    if case["id"] == "mature-preservation":
        (root / "legacy_app").mkdir()
        (root / "tests").mkdir()
        (root / "legacy_app/__init__.py").write_text('"""Legacy app."""\n', encoding="utf-8")
        (root / "tests/test_app.py").write_text("def test_app():\n    assert True\n", encoding="utf-8")
        (root / "pyproject.toml").write_text(
            '[tool.poetry]\nname = "legacy-app"\nversion = "1.0.0"\n\n'
            '[tool.black]\nline-length = 88\n\n[tool.poetry.dependencies]\npython = "^3.10"\n',
            encoding="utf-8",
        )
        (root / "tox.ini").write_text("[tox]\nenvlist = py310\n", encoding="utf-8")
    checked(["git", "init", "-b", "main"], root)
    checked(["git", "config", "user.name", "Codex Eval"], root)
    checked(["git", "config", "user.email", "codex-eval@example.invalid"], root)
    checked(["git", "config", "commit.gpgsign", "false"], root)
    checked(["git", "add", "."], root)
    checked(["git", "commit", "-m", "test: create workflow fixture"], root)


def command(fixture: Path, prompt: str, result: Path, model: str | None) -> list[str]:
    value = ["codex", "exec", "--json", "--ephemeral", "--ignore-user-config", "--ignore-rules",
             "--sandbox", "workspace-write", "--cd", str(fixture), "--output-schema", str(SCHEMA),
             "--output-last-message", str(result)]
    if model:
        value.extend(["--model", model])
    value.append(prompt)
    return value


def usage(transcript: Path) -> dict[str, int] | None:
    for line in reversed(transcript.read_text(encoding="utf-8").splitlines()):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "turn.completed":
            return event.get("usage")
    return None


def self_test() -> int:
    with tempfile.TemporaryDirectory() as directory:
        for case in read_json(CASES)["cases"]:
            fixture = Path(directory) / case["id"]
            prepare_fixture(fixture, case)
            assert command(fixture, case["prompt"], Path(directory) / "result.json", None)[-1] == case["prompt"]
    read_json(SCHEMA)
    print("validated runner fixtures for 2 cases")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-dir", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/codex"))
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    fixtures = (args.fixture_dir or Path(tempfile.mkdtemp(prefix="python-workflow-codex-"))).resolve()
    output = args.output_dir.resolve()
    fixtures.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "repository_commit": checked(["git", "rev-parse", "HEAD"], ROOT).strip(),
        "codex_version": checked(["codex", "--version"], ROOT).strip(),
        "requested_model": args.model,
        "cases": [],
    }
    for case in read_json(CASES)["cases"]:
        fixture = fixtures / case["id"]
        prepare_fixture(fixture, case)
        transcript = output / f"{case['id']}-transcript.jsonl"
        stderr = output / f"{case['id']}-stderr.log"
        result_path = output / f"{case['id']}-result.json"
        started = monotonic()
        with transcript.open("w", encoding="utf-8") as out, stderr.open("w", encoding="utf-8") as err:
            result = subprocess.run(command(fixture, case["prompt"], result_path, args.model), stdout=out, stderr=err,
                                    text=True, check=False, timeout=args.timeout)
        summary["cases"].append({"id": case["id"], "status": "completed" if result.returncode == 0 else "failed",
                                 "duration_seconds": round(monotonic() - started, 3), "usage": usage(transcript)})
    summary["ended_at"] = datetime.now(timezone.utc).isoformat()
    (output / "run-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if any(item["status"] != "completed" for item in summary["cases"]):
        return 1
    return subprocess.run([sys.executable, str(GRADER), "--results-dir", str(output),
                           "--fixtures-dir", str(fixtures), "--output", str(output / "grade.json")],
                          cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
