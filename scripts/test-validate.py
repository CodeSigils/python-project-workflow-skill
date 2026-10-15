#!/usr/bin/env python3
"""Regression tests for the skill-source validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

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

    print("PASS: skill source validator rejects broken links and unregistered URLs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
