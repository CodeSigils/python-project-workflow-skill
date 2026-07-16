#!/usr/bin/env python3
"""Regression tests for read-only payload drift detection."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = Path("skills/python-project-workflow/references/core-footguns.md")
ORPHAN = Path("skills/python-project-workflow/references/orphan.md")


def run_sync(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "scripts/sync-payload.sh", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="python-project-workflow-sync-") as tmp:
        fixture = Path(tmp) / "repo"
        shutil.copytree(
            ROOT,
            fixture,
            ignore=shutil.ignore_patterns(".git", ".ruff_cache", "__pycache__"),
        )

        target = fixture / REFERENCE
        target.write_text(
            target.read_text(encoding="utf-8") + "\nintentional drift\n",
            encoding="utf-8",
        )
        orphan = fixture / ORPHAN
        orphan.write_text("orphan\n", encoding="utf-8")
        before = target.read_bytes()

        check = run_sync(fixture, "--ci")
        if check.returncode == 0:
            raise AssertionError(f"--ci accepted payload drift:\n{check.stdout}")
        if target.read_bytes() != before:
            raise AssertionError("--ci modified a drifted payload file")
        if not orphan.exists():
            raise AssertionError("--ci removed an orphaned payload file")
        if "DRIFTED: references/core-footguns.md" not in check.stdout:
            raise AssertionError(f"--ci did not report content drift:\n{check.stdout}")
        if "ORPHANED: references/orphan.md" not in check.stdout:
            raise AssertionError(f"--ci did not report the orphan:\n{check.stdout}")

        sync = run_sync(fixture)
        if sync.returncode != 0:
            raise AssertionError(f"normal sync failed:\n{sync.stdout}")
        source = fixture / "references/core-footguns.md"
        if target.read_bytes() != source.read_bytes():
            raise AssertionError("normal sync did not repair payload drift")
        if orphan.exists():
            raise AssertionError("normal sync did not remove the orphan")

        final_check = run_sync(fixture, "--ci")
        if final_check.returncode != 0:
            raise AssertionError(f"repaired payload failed --ci:\n{final_check.stdout}")

        target.chmod(0o755)
        mode_check = run_sync(fixture, "--ci")
        if mode_check.returncode == 0:
            raise AssertionError("--ci accepted payload permission drift")
        if not target.stat().st_mode & 0o111:
            raise AssertionError("--ci modified drifted payload permissions")
        if "DRIFTED: references/core-footguns.md" not in mode_check.stdout:
            raise AssertionError(
                f"--ci did not report permission drift:\n{mode_check.stdout}"
            )

        mode_sync = run_sync(fixture)
        if mode_sync.returncode != 0:
            raise AssertionError(f"normal sync failed to repair mode:\n{mode_sync.stdout}")
        if target.stat().st_mode & 0o111:
            raise AssertionError("normal sync did not repair payload permissions")

    print("PASS: payload CI mode detects content, orphan, and permission drift")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
