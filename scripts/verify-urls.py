#!/usr/bin/env python3
"""Verify reachable HTTP(S) URLs referenced by docs and skill files.

The URL list lives in docs/evidence-urls.json so the evidence base has one
machine-readable source of truth. If a doc adds or removes URLs, update that
manifest instead of editing this script's code.

Usage:
  python3 scripts/verify-urls.py
  python3 scripts/verify-urls.py --self-test

Prints one line per URL and exits 0 when every URL matches the manifest.
Exit code 1 when a URL's status differs from the manifest or a required text
anchor is missing.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "docs" / "evidence-urls.json"
RETRYABLE_HTTP_STATUSES = frozenset({429, 500, 502, 503, 504})
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1


@dataclass(frozen=True)
class UrlCheckResult:
    """Result of a single URL check."""

    status: int | str
    content: str | None
    attempts: int


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
        # This validates a parsed manifest document, not a function
        # signature, so ValueError is the accurate class; TRY004 assumes
        # an API contract and wants TypeError here.
        if not isinstance(status, int):
            raise ValueError("expected_statuses must contain integers")  # noqa: TRY004
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


def check_url_once(
    url: str,
    required_text: list[str] | None = None,
) -> UrlCheckResult:
    """Fetch one URL once, reading its body only when anchors are required."""
    request = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "python-project-workflow-url-verify"},
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            status = response.status
            if required_text:
                body = response.read().decode("utf-8")
                return UrlCheckResult(status, check_required_text(body, required_text), 1)
            return UrlCheckResult(status, None, 1)

    except urllib.error.HTTPError as exc:
        return UrlCheckResult(exc.code, f"HTTP {exc.code}", 1)
    except urllib.error.URLError as exc:
        return UrlCheckResult("ERROR", str(exc.reason), 1)
    except TimeoutError:
        return UrlCheckResult("TIMEOUT", "timeout", 1)
    except ValueError as exc:
        return UrlCheckResult("ERROR", f"invalid URL: {exc}", 1)


def is_retryable(status: int | str) -> bool:
    """Return whether a result is a transient availability failure, not content drift."""
    return status in {"ERROR", "TIMEOUT"} or (
        isinstance(status, int) and status in RETRYABLE_HTTP_STATUSES
    )


def check_url(url: str, required_text: list[str] | None = None) -> UrlCheckResult:
    """Return a checked URL after bounded retries for transient host failures."""
    result = check_url_once(url, required_text)
    for attempt in range(2, MAX_ATTEMPTS + 1):
        if not is_retryable(result.status):
            return result
        time.sleep(RETRY_DELAY_SECONDS)
        retried = check_url_once(url, required_text)
        result = UrlCheckResult(retried.status, retried.content, attempt)
    return result


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
    assert is_retryable(503)
    assert is_retryable("TIMEOUT")
    assert not is_retryable(404)
    assert not is_retryable(200)
    print("  PASS  is_retryable")
    with (
        patch.object(
            sys.modules[__name__],
            "check_url_once",
            side_effect=[
                UrlCheckResult(503, "HTTP 503", 1),
                UrlCheckResult(200, "ANCHORS_OK", 1),
            ],
        ),
        patch.object(time, "sleep") as sleep,
    ):
        recovered = check_url("https://example.invalid", ["anchor"])
    assert recovered == UrlCheckResult(200, "ANCHORS_OK", 2)
    sleep.assert_called_once_with(RETRY_DELAY_SECONDS)

    with (
        patch.object(
            sys.modules[__name__],
            "check_url_once",
            return_value=UrlCheckResult(404, "HTTP 404", 1),
        ),
        patch.object(time, "sleep") as sleep,
    ):
        definite = check_url("https://example.invalid")
    assert definite == UrlCheckResult(404, "HTTP 404", 1)
    sleep.assert_not_called()
    print("  PASS  check_url retry behavior")
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
    print(f"{'Name':<30s} {'Status':<8s} {'Expected':<12s} {'Content':<12s} {'Note':<10s}")
    print("-" * 84)

    drift_found = False
    for entry in sorted(entries, key=lambda item: item["name"].lower()):
        try:
            validate_entry(entry)
        except ValueError as exc:
            print(f"  {entry.get('name', '<unnamed>'):<30s} {'-':<8s} {'-':<12s} {'-':<12s} MANIFEST: {exc}")
            drift_found = True
            continue

        if entry.get("monitor", True) is False:
            print(f"  {entry['name']:<30s} {'—':<8s} {'unmonitored':<12s} {'—':<12s} SKIPPED")
            continue

        result = check_url(entry["url"], entry.get("required_text"))
        expected = entry["expected_statuses"]
        note = classify_status(result.status, expected)
        if note == "DRIFT":
            drift_found = True

        content_label = result.content or "—"
        if result.content == "MISSING_ANCHOR":
            note = "BROKEN"
            drift_found = True

        expected_text = "/".join(str(code) for code in expected)
        marker = "  ← DRIFT" if note == "DRIFT" else ""
        marker = "  ← BROKEN" if note == "BROKEN" else marker
        status_label = f"{result.status} ({result.attempts}x)"
        print(
            f"  {entry['name']:<30s} {status_label:<8s} {expected_text:<12s} "
            f"{content_label:<12s} {note:<10s}{marker}"
        )

    if drift_found:
        print("\nRESULT: Drift or broken content detected — one or more URLs differ from docs/evidence-urls.json.")
        print("Update the manifest after investigating the changed URL state.")
        return 1

    print("\nRESULT: All URLs match documented expected state and content validates OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
