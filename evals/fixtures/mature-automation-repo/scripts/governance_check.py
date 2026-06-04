from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_ledger(path: Path) -> dict[str, Any]:
    """Load a simple governance ledger used by the consistency checker."""
    return json.loads(path.read_text(encoding="utf-8"))


def count_findings(ledger: dict[str, Any]) -> int:
    """Return the number of governance findings in the ledger."""
    findings = ledger.get("findings", [])
    if not isinstance(findings, list):
        raise TypeError("ledger findings must be a list")
    return len(findings)
