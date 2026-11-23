#!/usr/bin/env python3
"""Shared fixtures and subprocess helpers for the behavioral regression runners.

The Codex and Hermes runners each build the same isolated fixture, shell out to a
checked subprocess, and grade with the same script. The pieces that were copied
verbatim live here so a fix reaches every runner; only the agent-specific setup
stays in each runner. This module carries helpers only and is never run directly.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GRADER = ROOT / "scripts/grade-codex-regression.py"
CASES = ROOT / "evals/codex/cases.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def checked(command: list[str], cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout


def write_mature_preservation_fixture(root: Path) -> None:
    """Write the legacy Poetry/tox tree the mature-preservation case inspects."""
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


def write_pep621_partial_inspect_fixture(root: Path) -> None:
    """Write a partial PEP 621 project with a requires-python/tool-target mismatch."""
    (root / "src" / "sample_pkg").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "src" / "sample_pkg" / "__init__.py").write_text('__version__ = "0.1.0"\n', encoding="utf-8")
    (root / "tests" / "test_basic.py").write_text("def test_basic():\n    assert True\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        "[build-system]\n"
        'requires = ["setuptools>=77.0.3", "wheel"]\n'
        'build-backend = "setuptools.build_meta"\n\n'
        "[project]\n"
        'name = "sample-pkg"\n'
        'version = "0.1.0"\n'
        'requires-python = ">=3.11"\n'
        "# description/readme intentionally missing for partial PEP 621 inspection\n\n"
        "[tool.ruff]\n"
        'target-version = "py310"\n\n'
        "[tool.mypy]\n"
        'python_version = "3.10"\n',
        encoding="utf-8",
    )
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / "ci.yml").write_text(
        "name: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
        "    strategy:\n      matrix:\n        python-version: ['3.10', '3.11']\n"
        "    steps:\n      - uses: actions/checkout@v4\n",
        encoding="utf-8",
    )


def write_pep621_legacy_setupcfg_fixture(root: Path) -> None:
    """Write a legacy setuptools/setup.cfg project without PEP 621 [project] metadata."""
    (root / "legacy_pkg").mkdir()
    (root / "tests").mkdir()
    (root / "legacy_pkg" / "__init__.py").write_text("__version__ = '0.1.0'\n", encoding="utf-8")
    (root / "tests" / "test_basic.py").write_text("def test_basic():\n    assert True\n", encoding="utf-8")
    (root / "setup.cfg").write_text(
        "[metadata]\n"
        "name = legacy-pkg\n"
        "version = 0.1.0\n"
        "description = Legacy package\n\n"
        "[options]\n"
        "packages = find:\n"
        "python_requires = >=3.9\n",
        encoding="utf-8",
    )
    (root / "setup.py").write_text("from setuptools import setup\n\nsetup()\n", encoding="utf-8")


def init_fixture_repo(root: Path, author: str, email: str, *, allow_empty: bool) -> None:
    """Create a committed git repository the agent under test can inspect."""
    checked(["git", "init", "-b", "main"], root)
    checked(["git", "config", "user.name", author], root)
    checked(["git", "config", "user.email", email], root)
    checked(["git", "config", "commit.gpgsign", "false"], root)
    checked(["git", "add", "."], root)
    commit = ["git", "commit"]
    if allow_empty:
        commit.append("--allow-empty")
    checked([*commit, "-m", "test: create workflow fixture"], root)


def run_grader(output: Path, fixtures: Path) -> int:
    return subprocess.run(
        [
            sys.executable,
            str(GRADER),
            "--results-dir",
            str(output),
            "--fixtures-dir",
            str(fixtures),
            "--output",
            str(output / "grade.json"),
        ],
        cwd=ROOT,
        check=False,
    ).returncode
