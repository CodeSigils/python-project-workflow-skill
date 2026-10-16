#!/usr/bin/env python3
"""Regression tests for the skill-source validator."""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate.py"


def load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate", VALIDATOR)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_validator()

    # The real repository must pass both new structural checks.
    module.check_payload_links()
    module.check_payload_urls_registered()

    # URL comparison ignores fragments, trailing slashes, and trailing dots.
    if module.normalize_url("https://docs.astral.sh/ruff/#rules") != "https://docs.astral.sh/ruff":
        raise AssertionError("normalize_url kept a fragment")
    if module.normalize_url("https://docs.astral.sh/ruff/") != "https://docs.astral.sh/ruff":
        raise AssertionError("normalize_url kept a trailing slash")
    if module.normalize_url("https://docs.pytest.org.") != "https://docs.pytest.org":
        raise AssertionError("normalize_url kept trailing punctuation")

    registered = {module.normalize_url("https://docs.astral.sh/ruff/")}
    texts = {
        "skills/python-project-workflow/references/a.md": "See [Ruff](https://docs.astral.sh/ruff/).",
        "skills/python-project-workflow/references/b.md": "See https://example.invalid/tool.",
    }
    missing = module.unregistered_urls(texts, registered)
    if set(missing) != {"https://example.invalid/tool"}:
        raise AssertionError(f"unregistered_urls returned {missing!r}")
    if module.unregistered_urls({"x": "content https://docs.astral.sh/ruff/"}, registered):
        raise AssertionError("unregistered_urls flagged a registered URL")

    # Relative link extraction drops schemes, anchors, and titles.
    extracted = module.extract_relative_links(
        "[a](foo.md) [b](../bar.md#frag) [c](https://example.invalid) "
        "[d](#local) [e](baz.md \"title\")"
    )
    if extracted != ["foo.md", "../bar.md", "baz.md"]:
        raise AssertionError(f"extract_relative_links returned {extracted!r}")

    if module.extract_backtick_refs("load `references/drift-classes.md`") != [
        "references/drift-classes.md"
    ]:
        raise AssertionError("extract_backtick_refs missed a reference path")

    # A payload file with an unregistered URL must be rejected end-to-end.
    mutated = dict(texts)
    mutated["skills/python-project-workflow/SKILL.md"] = "See https://example.invalid/new."
    if not module.unregistered_urls(mutated, registered):
        raise AssertionError("validator accepted an unregistered payload URL")

    # The real decision log must pass, and malformed entries must be rejected.
    module.check_decisions()
    module.check_research()

    valid = (
        "# Decisions\n\n## Decision: Sample\n\n"
        "- ID: D99\n- Status: accepted\n- Decided: 2026-10-15\n"
        "- Sources: https://docs.astral.sh/uv/\n- Recheck: on the next major release\n"
    )

    def run_decisions(text: str) -> bool:
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
            handle.write(text)
            path = Path(handle.name)
        holder: Any = module
        original = holder.DECISIONS
        holder.DECISIONS = path
        try:
            module.check_decisions()
            return True
        except SystemExit:
            return False
        finally:
            holder.DECISIONS = original
            path.unlink()

    if not run_decisions(valid):
        raise AssertionError("check_decisions rejected a valid decision")
    for mutated, label in (
        (valid.replace("- ID: D99\n", ""), "a missing ID field"),
        (valid.replace("- Recheck: on the next major release\n", ""), "a missing Recheck field"),
        (valid.replace("Status: accepted", "Status: maybe"), "an unknown status"),
        (
            valid.replace("https://docs.astral.sh/uv/", "https://example.invalid/x"),
            "an unregistered source",
        ),
    ):
        if run_decisions(mutated):
            raise AssertionError(f"check_decisions accepted {label}")

    profiled = valid.replace(
        "- Recheck: on the next major release\n",
        "- Recheck: on the next major release\n"
        "- Context: sample context\n"
        "- Evidence appraisal: applicable official documentation\n"
        "- Outcome check: the sample remains valid\n"
        "- Evidence profile: primary\n",
    )
    if not run_decisions(profiled):
        raise AssertionError("check_decisions rejected a complete primary evidence profile")
    if run_decisions(profiled.replace("- Outcome check: the sample remains valid\n", "")):
        raise AssertionError("check_decisions accepted an incomplete evidence profile")

    # The checked-in research register must keep every D# linked to a dated,
    # source-backed R-### finding.
    research = module.RESEARCH_INDEX.read_text(encoding="utf-8")

    def run_research(text: str) -> bool:
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
            handle.write(text)
            path = Path(handle.name)
        holder: Any = module
        original = holder.RESEARCH_INDEX
        holder.RESEARCH_INDEX = path
        try:
            module.check_research()
            return True
        except SystemExit:
            return False
        finally:
            holder.RESEARCH_INDEX = original
            path.unlink()

    if not run_research(research):
        raise AssertionError("check_research rejected the checked-in register")
    if run_research(research.replace("| R-003 |", "| R-001 |", 1)):
        raise AssertionError("check_research accepted a duplicate research ID")
    if run_research(research.replace("| R-003 |", "| R-003 |", 1).replace("| D3 |", "| D99 |", 1)):
        raise AssertionError("check_research accepted an unknown decision ID")

    print("PASS: skill source validator rejects broken links and unregistered URLs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
