#!/usr/bin/env python3
"""Report repository hygiene drift and fail on actionable review debt.

A review session that has to remember to run `git status`, close stale pull
requests, and delete merged branches will eventually forget one of them. The
failure mode is not a dirty tree; it is a new pull request opened against a
branch that was already superseded, which stacks work and makes the real diff
hard to read.

Stacked pull requests, neglected pull requests, and stale branches are errors.
Local state and inaccessible remote metadata remain notes. The workflow writes
the result to the GitHub Actions job summary.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

DEFAULT_BRANCH = "main"
UNREVIEWED_PULL_GRACE_DAYS = 3
STALE_PULL_DAYS = 14
STALE_BRANCH_DAYS = 30


def run(args: list[str]) -> tuple[int, str, str]:
    """Return (returncode, stdout, stderr) for a command, tolerating absence."""
    try:
        done = subprocess.run(args, capture_output=True, text=True, check=False)
    except OSError as error:
        return 1, "", str(error)
    return done.returncode, done.stdout, done.stderr


# --------------------------------------------------------------------------
# Pure checks. Each takes already-collected data so it can be self-tested.
# --------------------------------------------------------------------------


def stacked_pulls(pulls: list[dict], default_branch: str) -> list[str]:
    """Open pull requests whose base is not the default branch.

    The shape is `gh pr list --json number,headRefName,baseRefName`: the ref
    names are flat keys, not nested objects. Reading them as nested silently
    yields an empty string, which then reads as a stacked pull request.
    """
    findings: list[str] = []
    for pull in pulls:
        base = pull.get("baseRefName") or ""
        if base != default_branch:
            head = pull.get("headRefName") or ""
            findings.append(
                f"pull request #{pull.get('number')} ({head}) is based on "
                f"{base!r} instead of {default_branch!r}"
            )
    return findings


def unmerged_branches(names: list[str], merged: set[str], default_branch: str) -> list[str]:
    """Branches that exist but carry no commit the default branch has."""
    return [
        f"branch {name!r} has no commit reachable from {default_branch}"
        for name in sorted(set(names) - merged)
        if name != default_branch
    ]


def orphaned_branches(names: list[str], with_pull: set[str], default_branch: str) -> list[str]:
    """Branches with neither a merged commit nor an open pull request."""
    return [
        f"branch {name!r} is neither merged nor has an open pull request"
        for name in sorted(set(names) - with_pull - {default_branch})
    ]


def age_days(value: str, now: datetime) -> int | None:
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return max(0, (now - timestamp.astimezone(timezone.utc)).days)


def neglected_pulls(pulls: list[dict], now: datetime) -> list[str]:
    findings: list[str] = []
    for pull in pulls:
        number = pull.get("number")
        created_days = age_days(str(pull.get("createdAt") or ""), now)
        updated_days = age_days(str(pull.get("updatedAt") or ""), now)
        if created_days is None or updated_days is None:
            findings.append(f"pull request #{number} has an unreadable GitHub timestamp")
            continue
        reviews = pull.get("reviews") or []
        if not reviews and created_days >= UNREVIEWED_PULL_GRACE_DAYS:
            findings.append(
                f"pull request #{number} has no review after {created_days} day(s)"
            )
        if updated_days >= STALE_PULL_DAYS:
            findings.append(
                f"pull request #{number} has not been updated for {updated_days} day(s)"
            )
    return findings


def stale_branches(
    branch_dates: dict[str, str], with_pull: set[str], now: datetime
) -> list[str]:
    findings: list[str] = []
    for name, updated_at in sorted(branch_dates.items()):
        if name == DEFAULT_BRANCH or name in with_pull:
            continue
        days = age_days(updated_at, now)
        if days is None:
            findings.append(f"branch {name!r} has an unreadable commit timestamp")
        elif days >= STALE_BRANCH_DAYS:
            findings.append(f"branch {name!r} has no pull request and is {days} day(s) old")
    return findings


# --------------------------------------------------------------------------
# Collection
# --------------------------------------------------------------------------


def local_state(root: str) -> tuple[list[str], list[str]]:
    """Collect local notes: dirty tree, stashes, unmerged branches, loose tags."""
    notes: list[str] = []
    code, out, _ = run(["git", "-C", root, "status", "--porcelain"])
    if code == 0 and out.strip():
        notes.append(f"worktree has {len(out.strip().splitlines())} uncommitted change(s)")
    code, out, _ = run(["git", "-C", root, "stash", "list"])
    if code == 0 and out.strip():
        notes.append(f"{len(out.strip().splitlines())} stash entry(ies) held")
    code, out, _ = run(["git", "-C", root, "branch", "--format=%(refname:short)"])
    names = [line.strip() for line in out.splitlines() if line.strip()] if code == 0 else []
    code, out, _ = run(
        ["git", "-C", root, "branch", "--merged", DEFAULT_BRANCH, "--format=%(refname:short)"]
    )
    merged = {line.strip() for line in out.splitlines()} if code == 0 else {DEFAULT_BRANCH}
    notes.extend(unmerged_branches(names, merged, DEFAULT_BRANCH))
    return names, notes


def remote_pulls(repo: str) -> tuple[list[dict], list[str]]:
    """Fetch open pull requests. Returns (pulls, notes); notes explain a skip."""
    code, out, err = run(
        [
            "gh", "pr", "list", "--repo", repo, "--state", "open",
            "--limit", "50", "--json",
            "number,headRefName,baseRefName,createdAt,updatedAt,reviews",
        ]
    )
    if code != 0:
        return [], [f"pull request query unavailable, stacking not checked: {err.strip() or out.strip()}"]
    try:
        return json.loads(out), []
    except json.JSONDecodeError as error:
        return [], [f"pull request query returned invalid JSON: {error}"]


def remote_branches(repo: str) -> tuple[dict[str, str], list[str]]:
    code, out, err = run(
        ["gh", "api", f"repos/{repo}/branches", "--paginate", "--jq", ".[].name"]
    )
    if code != 0:
        return {}, [f"branch query unavailable: {err.strip() or out.strip()}"]
    names = [line.strip() for line in out.splitlines() if line.strip()]
    dates: dict[str, str] = {}
    notes: list[str] = []
    for name in names:
        code, timestamp, err = run(
            ["gh", "api", f"repos/{repo}/commits/{name}", "--jq", ".commit.committer.date"]
        )
        if code != 0:
            notes.append(f"could not read the latest commit for branch {name!r}: {err.strip()}")
            continue
        dates[name] = timestamp.strip()
    return dates, notes


def detect_repo(root: str) -> str:
    """Read owner/name from the origin remote so no repository is hardcoded."""
    code, out, _ = run(["git", "-C", root, "remote", "get-url", "origin"])
    if code != 0:
        return "unknown/unknown"
    url = out.strip()
    if url.startswith("git@") and ":" in url:
        return url.split(":", 1)[1].removesuffix(".git")
    if "github.com/" in url:
        return url.split("github.com/", 1)[1].removesuffix(".git")
    return "unknown/unknown"


def collect(repo: str, root: str) -> tuple[list[str], list[str]]:
    """Gather every error and note. Errors are the conditions that must not ship."""
    errors: list[str] = []
    notes: list[str] = []

    names, local_notes = local_state(root)
    notes.extend(local_notes)

    pulls, pull_notes = remote_pulls(repo)
    notes.extend(pull_notes)
    errors.extend(stacked_pulls(pulls, DEFAULT_BRANCH))
    errors.extend(neglected_pulls(pulls, datetime.now(timezone.utc)))

    if not pull_notes:
        remote, branch_notes = remote_branches(repo)
        notes.extend(branch_notes)
        pull_branches = {str(p.get("headRefName") or "") for p in pulls}
        notes.extend(orphaned_branches(list(remote), pull_branches, DEFAULT_BRANCH))
        errors.extend(stale_branches(remote, pull_branches, datetime.now(timezone.utc)))
    return errors, notes


def write_summary(lines: list[str]) -> None:
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary:
        return
    with open(summary, "a", encoding="utf-8") as file:
        file.write("## Repository hygiene\n\n")
        file.write("\n".join(f"- {line}" for line in lines))
        file.write("\n")


def run_self_tests() -> None:
    """Exercise each pure check with a known input and a known expectation."""
    assert stacked_pulls([], DEFAULT_BRANCH) == []
    assert stacked_pulls(
        [{"number": 8, "headRefName": "dependabot/x", "baseRefName": "main"}], DEFAULT_BRANCH
    ) == []
    assert stacked_pulls(
        [{"number": 9, "headRefName": "feature", "baseRefName": "feature"}], DEFAULT_BRANCH
    ) == ["pull request #9 (feature) is based on 'feature' instead of 'main'"]
    # A missing ref name is itself a fault, so it must not read as "main".
    assert stacked_pulls([{"number": 10}], DEFAULT_BRANCH) == [
        "pull request #10 () is based on '' instead of 'main'"
    ]

    assert unmerged_branches(["main"], {"main"}, DEFAULT_BRANCH) == []
    assert unmerged_branches(["main", "old"], {"main"}, DEFAULT_BRANCH) == [
        "branch 'old' has no commit reachable from main"
    ]
    assert unmerged_branches(["main", "landed"], {"main", "landed"}, DEFAULT_BRANCH) == []

    assert orphaned_branches(["main"], set(), DEFAULT_BRANCH) == []
    assert orphaned_branches(["main", "stale"], set(), DEFAULT_BRANCH) == [
        "branch 'stale' is neither merged nor has an open pull request"
    ]
    assert orphaned_branches(["main", "stale"], {"stale"}, DEFAULT_BRANCH) == []

    now = datetime(2026, 10, 4, tzinfo=timezone.utc)
    assert neglected_pulls(
        [{"number": 1, "createdAt": "2026-10-01T00:00:00Z", "updatedAt": "2026-10-04T00:00:00Z", "reviews": []}], now
    ) == ["pull request #1 has no review after 3 day(s)"]
    assert neglected_pulls(
        [{"number": 2, "createdAt": "2026-09-01T00:00:00Z", "updatedAt": "2026-09-01T00:00:00Z", "reviews": [{"state": "APPROVED"}]}], now
    ) == ["pull request #2 has not been updated for 33 day(s)"]
    assert stale_branches(
        {"main": "2026-01-01T00:00:00Z", "old": "2026-09-01T00:00:00Z"}, set(), now
    ) == ["branch 'old' has no pull request and is 33 day(s) old"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report repository hygiene drift and fail on stacked pull requests."
    )
    parser.add_argument("--repo", default="", help="owner/name, for pull request and branch queries")
    parser.add_argument("--root", default=".", help="repository root for local git queries")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checks and exit")
    args = parser.parse_args()

    if args.self_test:
        run_self_tests()
        print("PASS: repo hygiene self-tests")
        return 0

    repo = args.repo or detect_repo(args.root)
    errors, notes = collect(repo, args.root)
    print(f"REPOSITORY: {repo}")

    for note in notes:
        print(f"NOTE: {note}")
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        print(f"FAIL: {len(errors)} repository hygiene error(s)", file=sys.stderr)
        write_summary([f"FAIL: {error}" for error in errors] + notes)
        return 1
    write_summary(["PASS: no stacked or neglected pull requests"] + notes)
    print("PASS: no stacked pull requests; hygiene notes above, if any")
    return 0


if __name__ == "__main__":
    sys.exit(main())
