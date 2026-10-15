#!/usr/bin/env python3
"""Run isolated Codex behavior cases for python-project-workflow."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import Any

from regression_support import (
    CASES,
    checked,
    init_fixture_repo,
    read_json,
    run_grader,
    write_mature_preservation_fixture,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "evals/codex/result.schema.json"


def prepare_fixture(root: Path, case: dict[str, Any]) -> None:
    if root.exists():
        raise FileExistsError(root)
    (root / ".agents/skills").mkdir(parents=True)
    shutil.copytree(ROOT / "skills/python-project-workflow", root / ".agents/skills/python-project-workflow")
    if case["id"] == "mature-preservation":
        write_mature_preservation_fixture(root)
    init_fixture_repo(root, "Codex Eval", "codex-eval@example.invalid", allow_empty=False)


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
    parser.add_argument("--retain-fixtures", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    temporary: tempfile.TemporaryDirectory[str] | None = None
    if args.fixture_dir:
        fixtures = args.fixture_dir.resolve()
    elif args.retain_fixtures:
        fixtures = Path(tempfile.mkdtemp(prefix="python-workflow-codex-")).resolve()
        print(f"retaining fixtures at {fixtures}")
    else:
        temporary = tempfile.TemporaryDirectory(prefix="python-workflow-codex-")
        fixtures = Path(temporary.name).resolve()
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
        if temporary:
            temporary.cleanup()
        return 1
    grade_code = run_grader(output, fixtures)
    if temporary:
        temporary.cleanup()
    return grade_code


if __name__ == "__main__":
    raise SystemExit(main())
