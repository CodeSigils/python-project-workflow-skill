#!/usr/bin/env python3
"""Verify reachable HTTP(S) URLs referenced by docs and skill files."""

from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
URL_RE = re.compile(r"https?://[^\s)>]+")
SEARCH_ROOTS = [
    ROOT / "README.md",
    ROOT / "SECURITY.md",
    ROOT / "CITATION.cff",
    ROOT / "skills",
]


def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for root in SEARCH_ROOTS:
        if root.is_file():
            files.append(root)
        elif root.exists():
            files.extend(sorted(root.glob("**/*.md")))
    return files


def iter_urls() -> list[tuple[Path, str]]:
    pairs: list[tuple[Path, str]] = []
    for path in iter_markdown_files():
        text = path.read_text(encoding="utf-8")
        for match in URL_RE.finditer(text):
            pairs.append((path, match.group(0).rstrip(".,;")))
    return pairs


def request_url(url: str, method: str) -> str | None:
    request = urllib.request.Request(
        url,
        method=method,
        headers={"User-Agent": "python-project-workflow-url-check"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if 200 <= response.status < 400:
                return None
            return f"HTTP {response.status}"
    except urllib.error.HTTPError as exc:
        if method == "HEAD" and exc.code == 405:
            return request_url(url, "GET")
        return f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001 - report URL check failure
        return str(exc)


def main() -> int:
    failures: list[str] = []
    seen: set[str] = set()
    for path, url in iter_urls():
        if url in seen:
            continue
        seen.add(url)
        failure = request_url(url, "HEAD")
        if failure:
            failures.append(f"{path.relative_to(ROOT)}: {url}: {failure}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print(f"verified {len(seen)} URLs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
