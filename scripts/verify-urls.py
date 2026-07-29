#!/usr/bin/env python3
"""Verify reachable HTTP(S) URLs referenced by docs and skill files.

The URL list lives in docs/evidence-urls.json so the research evidence base has
one machine-readable source of truth. If the doc adds or removes URLs, update
that manifest instead of editing this script's code.

Usage:
  python3 scripts/verify-urls.py
  python3 scripts/verify-urls.py --self-test

Outputs a table of URL -> final status with drift annotations.
Exit code 0 = all URLs match documented expected state.
Exit code 1 = one or more URLs differs from the manifest.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "docs" / "evidence-urls.json"


@dataclass(frozen=True)
class UrlCheckResult:
    """Result of a single URL check."""

    status: int | str
    redirects: int
    content: str | None


def load_manifest(path: Path = MANIFEST_PATH) -> list[dict[str, Any]]:
    """Load URL entries from the evidence manifest."""
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"FAIL: could not read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"FAIL: invalid JSON in {path}: {exc}") from exc

    urls = manifest.get("urls")
    if not isinstance(urls, list):
        raise SystemExit(f"FAIL: {path} must contain a top-level 'urls' list")
    return urls


def validate_entry(entry: dict[str, Any]) -> None:
    """Validate one manifest entry before using it."""
    required = ("name", "url", "expected_statuses")
    missing = [key for key in required if key not in entry]
    if missing:
        raise ValueError(f"missing required field(s): {', '.join(missing)}")
    if not isinstance(entry["expected_statuses"], list) or not entry["expected_statuses"]:
        raise ValueError("expected_statuses must be a non-empty list")
    for status in entry["expected_statuses"]:
        if not isinstance(status, int):
            raise ValueError("expected_statuses must contain integers")
    if "monitor" in entry and not isinstance(entry["monitor"], bool):
        raise ValueError("monitor must be a boolean")
    required_text = entry.get("required_text", [])
    if not isinstance(required_text, list) or not all(isinstance(anchor, str) and anchor for anchor in required_text):
        raise ValueError("required_text must be a list of non-empty strings")


def check_required_text(body: str, required_text: list[str]) -> str:
    """Return a body-validation label without exposing response content."""
    if any(anchor not in body for anchor in required_text):
        return "MISSING_ANCHOR"
    return "ANCHORS_OK"


def check_url(
    url: str,
    content_type: str | None = None,
    required_text: list[str] | None = None,
) -> UrlCheckResult:
    """Return UrlCheckResult for one URL.

    Read response bodies only when JSON or semantic anchors need validation.
    """
    request = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "repo-architecture-skill-url-verify"},
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            status = response.status
            redirect_count = (
                len(response.headers.get("Location", "").split("\n")) if "Location" in response.headers else 0
            )

            if content_type == "json" or required_text:
                body = response.read().decode("utf-8")
            if content_type == "json":
                try:
                    json.loads(body)
                except (json.JSONDecodeError, ValueError):
                    return UrlCheckResult(status, redirect_count, "INVALID_JSON")
            if required_text:
                return UrlCheckResult(status, redirect_count, check_required_text(body, required_text))
            if content_type == "json":
                return UrlCheckResult(status, redirect_count, "VALID")
            return UrlCheckResult(status, redirect_count, None)

    except urllib.error.HTTPError as exc:
        return UrlCheckResult(exc.code, 0, f"HTTP {exc.code}")
    except urllib.error.URLError as exc:
        return UrlCheckResult("ERROR", 0, str(exc.reason))
    except TimeoutError:
        return UrlCheckResult("TIMEOUT", 0, "timeout")
    except ValueError as exc:
        return UrlCheckResult("ERROR", 0, f"invalid URL: {exc}")


def classify_status(status: int | str, expected_statuses: list[int]) -> str:
    """Return OK when status matches the manifest, else DRIFT."""
    if isinstance(status, int) and status in expected_statuses:
        return "OK"
    return "DRIFT"


def check_self_test() -> None:
    """Run internal self-tests for the validation logic."""
    # Test classify_status
    assert classify_status(200, [200]) == "OK"
    assert classify_status(404, [200]) == "DRIFT"
    assert classify_status("ERROR", [200]) == "DRIFT"
    assert classify_status(200, [200, 201]) == "OK"
    assert classify_status(201, [200, 201]) == "OK"
    print("  PASS  classify_status")
    assert check_required_text("alpha beta", ["alpha", "beta"]) == "ANCHORS_OK"
    assert check_required_text("alpha beta", ["gamma"]) == "MISSING_ANCHOR"
    print("  PASS  check_required_text")

    # Test validate_entry
    try:
        validate_entry({"name": "test", "url": "https://example.com", "expected_statuses": [200]})
        print("  PASS  validate_entry valid")
    except ValueError:
        assert False, "should not fail"

    try:
        validate_entry({"url": "https://example.com"})  # missing name
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry missing field")

    try:
        validate_entry({"name": "test", "url": "https://example.com", "expected_statuses": []})
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry empty statuses")

    try:
        validate_entry({"name": "test", "url": "https://example.com", "expected_statuses": ["200"]})
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry non-int status")

    for invalid in ({"monitor": "false"}, {"required_text": [""]}):
        try:
            validate_entry(
                {
                    "name": "test",
                    "url": "https://example.com",
                    "expected_statuses": [200],
                    **invalid,
                }
            )
            assert False, "should have failed"
        except ValueError:
            pass
    print("  PASS  validate_entry semantic fields")

    print("  PASS  verify-urls.py self-tests")


def main() -> int:
    if "--self-test" in sys.argv:
        check_self_test()
        return 0

    entries = load_manifest()

    print("=== Evidence URL Re-verification ===")
    print(f"{'Name':<30s} {'Status':<8s} {'Expected':<12s} {'Redirects':<9s} {'Content':<12s} {'Note':<10s}")
    print("-" * 90)

    drift_found = False
    for entry in sorted(entries, key=lambda item: item["name"].lower()):
        try:
            validate_entry(entry)
        except ValueError as exc:
            print(f"  {entry.get('name', '<unnamed>'):<30s} {'-':<8s} {'-':<12s} {'-':<9s} {'-':<12s} MANIFEST: {exc}")
            drift_found = True
            continue

        if entry.get("monitor", True) is False:
            print(f"  {entry['name']:<30s} {'—':<8s} {'immutable':<12s} {'—':<9s} {'—':<12s} SKIPPED")
            continue

        content_type = entry.get("content_type")
        result = check_url(entry["url"], content_type, entry.get("required_text"))
        expected = entry["expected_statuses"]
        note = classify_status(result.status, expected)
        if note == "DRIFT":
            drift_found = True

        # Content check trumps status check for JSON endpoints
        content_label = result.content or "—"
        if result.content in {"INVALID_JSON", "MISSING_ANCHOR"}:
            note = "BROKEN"
            drift_found = True

        expected_text = "/".join(str(code) for code in expected)
        marker = "  ← DRIFT" if note == "DRIFT" else ""
        marker = "  ← BROKEN" if note == "BROKEN" else marker
        print(
            f"  {entry['name']:<30s} {str(result.status):<8s} {expected_text:<12s} "
            f"{str(result.redirects):<9s} {content_label:<12s} {note:<10s}{marker}"
        )

    if drift_found:
        print("\nRESULT: Drift or broken content detected — one or more URLs differ from docs/evidence-urls.json.")
        print("Update the manifest and research doc together after investigating the changed URL state.")
        return 1

    print("\nRESULT: All URLs match documented expected state and content validates OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
