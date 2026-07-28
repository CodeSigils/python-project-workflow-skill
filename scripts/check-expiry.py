#!/usr/bin/env python3
"""Warn about expired rule freshness markers."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPIRES_RE = re.compile(r"^\*\*Expires:\*\* (?P<date>\d{4}-\d{2}-\d{2})$", re.MULTILINE)


def main() -> int:
    today = date.today()
    expired: list[str] = []
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        for match in EXPIRES_RE.finditer(text):
            expiry = date.fromisoformat(match.group("date"))
            if expiry < today:
                expired.append(f"{path.relative_to(ROOT)}: expired {expiry.isoformat()}")

    if expired:
        print("Expired freshness markers:")
        for item in expired:
            print(f"- {item}")
        return 1
    else:
        print("no expired freshness markers")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
