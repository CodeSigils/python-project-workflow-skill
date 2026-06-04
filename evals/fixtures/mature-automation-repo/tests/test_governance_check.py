from __future__ import annotations

from pathlib import Path

from scripts.governance_check import count_findings, load_ledger


def test_count_findings_from_ledger(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    ledger.write_text('{"findings": [{"id": "F-001"}, {"id": "F-002"}]}', encoding="utf-8")

    assert count_findings(load_ledger(ledger)) == 2
