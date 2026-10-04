#!/usr/bin/env python3
"""Run isolated-fixture Hermes behavior cases for python-project-workflow."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
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
GRADER = ROOT / "scripts/grade-codex-regression.py"
PAYLOAD = ROOT / "skills/python-project-workflow"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def checked(command: list[str], cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout


def payload_digest(path: Path) -> str:
    digest = hashlib.sha256()
    entries = list(path.rglob("*"))
    files = sorted(item for item in entries if item.is_file())
    if not files or any(item.is_symlink() for item in entries):
        raise RuntimeError(f"invalid or empty skill payload: {path}")
    for item in files:
        relative = item.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(item.read_bytes())
    return digest.hexdigest()


def verify_installed_payload(hermes_home: Path) -> tuple[Path, str]:
    installed = hermes_home / "skills/python-project-workflow"
    source_digest = payload_digest(PAYLOAD)
    try:
        installed_digest = payload_digest(installed)
    except (OSError, RuntimeError) as exc:
        raise RuntimeError(
            f"Hermes must have the exact repository payload installed at {installed}"
        ) from exc
    if installed_digest != source_digest:
        raise RuntimeError(
            f"installed Hermes payload differs from repository payload at {installed}"
        )
    return installed, source_digest


def prepare_fixture(root: Path, case: dict[str, Any]) -> None:
    if root.exists():
        raise FileExistsError(root)
    root.mkdir(parents=True)
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
    checked(["git", "config", "user.name", "Hermes Eval"], root)
    checked(["git", "config", "user.email", "hermes-eval@example.invalid"], root)
    checked(["git", "config", "commit.gpgsign", "false"], root)
    checked(["git", "add", "."], root)
    checked(["git", "commit", "--allow-empty", "-m", "test: create workflow fixture"], root)


def command(case: dict[str, Any], model: str | None, provider: str | None) -> list[str]:
    value = ["hermes", "chat", "-Q", "--toolsets", "terminal", "--max-turns", "40"]
    if case["invocation"] == "explicit":
        value.extend(["--skills", "python-project-workflow"])
    if model:
        value.extend(["--model", model])
    if provider:
        value.extend(["--provider", provider])
    value.extend(["--query", case["prompt"]])
    return value


def extract_result(output: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    for index, character in enumerate(output):
        if character != "{":
            continue
        try:
            value, _ = decoder.raw_decode(output[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and {"skills_used", "classification", "changed_paths"} <= value.keys():
            return value
    raise ValueError("Hermes output did not contain the required JSON object")


def self_test() -> int:
    with tempfile.TemporaryDirectory() as directory:
        hermes_home = Path(directory) / "hermes"
        shutil.copytree(PAYLOAD, hermes_home / "skills/python-project-workflow")
        _, digest = verify_installed_payload(hermes_home)
        assert digest == payload_digest(PAYLOAD)
        installed_skill = hermes_home / "skills/python-project-workflow/SKILL.md"
        installed_skill.write_text(installed_skill.read_text(encoding="utf-8") + "\ndrift\n", encoding="utf-8")
        try:
            verify_installed_payload(hermes_home)
        except RuntimeError:
            pass
        else:
            raise AssertionError("drifted Hermes payload was accepted")
        cases = read_json(CASES)["cases"]
        for case in cases:
            fixture = Path(directory) / case["id"]
            prepare_fixture(fixture, case)
            built = command(case, None, None)
            assert ("--skills" in built) == (case["invocation"] == "explicit")
        sample = 'answer follows\n{"skills_used":["python-project-workflow"],"classification":"greenfield","changed_paths":[]}\n'
        assert extract_result(sample)["classification"] == "greenfield"
    print(f"validated Hermes runner fixtures for {len(cases)} cases")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-dir", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/hermes"))
    parser.add_argument("--model")
    parser.add_argument("--provider")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--hermes-home", type=Path)
    parser.add_argument("--retain-fixtures", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    hermes_home = (args.hermes_home or Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))).resolve()
    installed, installed_digest = verify_installed_payload(hermes_home)
    temporary: tempfile.TemporaryDirectory[str] | None = None
    if args.fixture_dir:
        fixtures = args.fixture_dir.resolve()
    elif args.retain_fixtures:
        fixtures = Path(tempfile.mkdtemp(prefix="python-workflow-hermes-")).resolve()
        print(f"retaining fixtures at {fixtures}")
    else:
        temporary = tempfile.TemporaryDirectory(prefix="python-workflow-hermes-")
        fixtures = Path(temporary.name).resolve()
    output = args.output_dir.resolve()
    fixtures.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "repository_commit": checked(["git", "rev-parse", "HEAD"], ROOT).strip(),
        "hermes_version": checked(["hermes", "--version"], ROOT).strip(),
        "requested_model": args.model,
        "requested_provider": args.provider,
        "installed_skill": str(installed),
        "payload_sha256": installed_digest,
        "cases": [],
    }
    for case in read_json(CASES)["cases"]:
        fixture = fixtures / case["id"]
        prepare_fixture(fixture, case)
        stdout_path = output / f"{case['id']}-stdout.log"
        stderr_path = output / f"{case['id']}-stderr.log"
        result_path = output / f"{case['id']}-result.json"
        started = monotonic()
        environment = os.environ.copy()
        try:
            result = subprocess.run(
                command(case, args.model, args.provider), cwd=fixture, capture_output=True,
                text=True, check=False, timeout=args.timeout, env=environment,
            )
            stdout_path.write_text(result.stdout, encoding="utf-8")
            stderr_path.write_text(result.stderr, encoding="utf-8")
            parsed = extract_result(result.stdout) if result.returncode == 0 else None
            if parsed is not None:
                result_path.write_text(json.dumps(parsed, indent=2) + "\n", encoding="utf-8")
            status = "completed" if result.returncode == 0 and parsed is not None else "failed"
        except (subprocess.TimeoutExpired, ValueError) as exc:
            stderr_path.write_text(str(exc) + "\n", encoding="utf-8")
            status = "failed"
        summary["cases"].append({
            "id": case["id"], "invocation": case["invocation"], "status": status,
            "duration_seconds": round(monotonic() - started, 3),
        })
    summary["ended_at"] = datetime.now(timezone.utc).isoformat()
    (output / "run-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if any(item["status"] != "completed" for item in summary["cases"]):
        if temporary:
            temporary.cleanup()
        return 1
    grade_code = subprocess.run(
        [sys.executable, str(GRADER), "--results-dir", str(output),
         "--fixtures-dir", str(fixtures), "--output", str(output / "grade.json")],
        cwd=ROOT, check=False,
    ).returncode
    if temporary:
        temporary.cleanup()
    return grade_code


if __name__ == "__main__":
    raise SystemExit(main())
