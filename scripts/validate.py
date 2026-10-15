#!/usr/bin/env python3
"""Validate the python-project-workflow skill source."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "python-project-workflow"
SKILL = SKILL_DIR / "SKILL.md"
REF_DIR = SKILL_DIR / "references"
EVIDENCE_MANIFEST = ROOT / "docs" / "evidence-urls.json"
DECISIONS = ROOT / "docs" / "decisions.md"
REQUIRED_REFS = {
    "pyproject-template.md",
    "lint-format-typing-testing.md",
    "core-footguns.md",
    "safe-editing.md",
    "mature-repo-preservation.md",
    "eval-benchmark-hardening.md",
    "drift-classes.md",
    "security-and-gitignore.md",
}
REQUIRED_SECTIONS = {
    "## Workflow",
    "## Operation Modes",
    "## Orientation Checklist",
    "## Reference Routing",
    "## Sensitive-Evidence Safety",
    "## Verification",
    "## Preserve Local Conventions",
}
UV_COMMANDS = (
    "uv sync",
    "uv run ruff check .",
    "uv run ruff format --check .",
    "uv run mypy .",
    "uv run pytest",
    "uv build",
)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def fail(message: str, *, hint: str | None = None) -> NoReturn:
    print(f"FAIL: {message}", file=sys.stderr)
    if hint:
        print(f"HINT: {hint}", file=sys.stderr)
    raise SystemExit(1)


def read_text_checked(path: Path) -> str:
    if path.is_symlink():
        fail(f"required file must not be a symlink: {rel(path)}")
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail(f"required file is missing: {rel(path)}")
    except UnicodeDecodeError as exc:
        fail(f"required file is not valid UTF-8: {rel(path)}: {exc}")
    except OSError as exc:
        fail(f"could not read required file {rel(path)}: {exc}")
    raise AssertionError("unreachable")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        fail("SKILL.md does not start with YAML frontmatter")
    try:
        _, raw, body = text.split("---\n", 2)
    except ValueError:
        fail("SKILL.md frontmatter is not closed")

    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            fail(f"malformed frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')

    ALLOWED_FIELDS = {"name", "description"}
    extra = set(data) - ALLOWED_FIELDS
    if extra:
        fail(f"unsupported frontmatter fields: {sorted(extra)}")
    if data.get("name") != "python-project-workflow":
        fail("frontmatter name must be python-project-workflow")
    if len(data.get("description", "").split()) < 18:
        fail("frontmatter description is too short to trigger reliably")
    return data, body


def contains_markdown_phrase(text: str, phrase: str) -> bool:
    return " ".join(phrase.split()) in " ".join(text.split())


def check_skill() -> None:
    text = read_text_checked(SKILL)
    _, body = parse_frontmatter(text)

    for section in sorted(REQUIRED_SECTIONS):
        if section not in body:
            fail(f"missing section in {rel(SKILL)}: {section}")

    if re.search(r"^\|\|", body, re.MULTILINE):
        fail(f"{rel(SKILL)} table still has accidental double-pipe rows")

    # Portability hazard check: body must not contain Hermes-specific paths/tools
    forbidden = [
        ".hermes",
        "hermes-verify",
    ]
    for needle in forbidden:
        if needle in body:
            fail(f"{rel(SKILL)} body contains non-portable runtime marker: {needle}")

    unsafe_probe_patterns = {
        "unredacted commit body output": re.compile(
            r"git\s+log[^\n]*(?:--format\s*=\s*[\"']?%B|--pretty\s*=\s*[\"']?%B)"
            r"[^\n]*(?:\|\s*(?:head|tail|sed|cat|tee|less|more)\b|$)"
        ),
        "secret file content output": re.compile(r"\bcat\s+(?:\.env(?:\.[^\s]+)?|[^\s]*credential[^\s]*)"),
        "destructive git reset": re.compile(r"\bgit\s+reset\s+--hard\b"),
        "forced git push": re.compile(r"\bgit\s+push\b[^\n]*(?:--force|-f\b)"),
    }
    runtime_files = [(SKILL, body)]
    runtime_files.extend(
        (path, read_text_checked(path)) for path in sorted(REF_DIR.glob("*.md"))
    )
    for path, runtime_text in runtime_files:
        for label, pattern in unsafe_probe_patterns.items():
            if pattern.search(runtime_text):
                fail(f"{rel(path)} contains unsafe security probe: {label}")

    security_directives = [
        "Never commit credentials, access tokens, private keys, or populated secret files.",
        "`!.env.example`",
        "`.gitignore` does not protect files that Git already tracks.",
        "recommend revocation or rotation",
        "Never include credentials, access tokens, private keys, sensitive values, or secret-bearing URLs in commit subjects or bodies.",
        "Do not print raw commit bodies.",
        "Report existence or location only.",
        "`references/security-and-gitignore.md`",
    ]
    for directive in security_directives:
        if not contains_markdown_phrase(body, directive):
            fail(f"{rel(SKILL)} missing .gitignore security directive: {directive}")

    if not contains_markdown_phrase(body, "Framework-specific project conventions are out of scope."):
        fail(f"{rel(SKILL)} missing framework scope boundary")

    workflow_directives = [
        "Do not use for pure code review, isolated support-script edits",
        "Do not infer correctness from classification alone.",
        "Do not install dependencies, synchronize environments, generate files, or edit configuration.",
        "Run setup and mutating verification only when authorized and necessary.",
        "Do not encode point-in-time lifecycle claims as durable policy.",
    ]
    frontmatter, _ = parse_frontmatter(text)
    combined = f"{frontmatter['description']}\n{body}"
    for directive in workflow_directives:
        if not contains_markdown_phrase(combined, directive):
            fail(f"{rel(SKILL)} missing workflow boundary: {directive}")

    for missing_ref in ["packaging.md", "errors-and-logging.md", "cli.md", "migration-existing-code.md"]:
        if f"`{missing_ref}` (deferred)" in body:
            fail(
                f"task table routes directly to deferred reference without fallback: {missing_ref}",
                hint="Point the row at an existing fallback reference, then label the richer reference as deferred.",
            )

    if len(text.splitlines()) > 500:
        fail(f"{rel(SKILL)} exceeds 500-line runtime budget")


def check_references() -> None:
    if not REF_DIR.exists():
        fail(f"runtime reference directory is missing: {rel(REF_DIR)}")
    found = {path.name for path in REF_DIR.glob("*.md")}
    missing = REQUIRED_REFS - found
    extra = found - REQUIRED_REFS
    if missing:
        fail(f"missing reference files: {sorted(missing)}")
    if extra:
        fail(f"unexpected reference files: {sorted(extra)}")
    for name in REQUIRED_REFS:
        path = REF_DIR / name
        size = path.stat().st_size
        if size < 500:
            fail(f"reference file looks too small: {rel(path)} ({size} bytes)")
        if len(read_text_checked(path).splitlines()) > 250:
            fail(f"reference file exceeds 250-line budget: {rel(path)}")

    pyproject = read_text_checked(REF_DIR / "pyproject-template.md")
    for obsolete in ('license = {text = "MIT"}', '"License :: OSI Approved :: MIT License"'):
        if obsolete in pyproject:
            fail(f"pyproject template contains deprecated license metadata: {obsolete}")
    for required in (
        'license = "MIT"',
        'license-files = ["LICENSE*"]',
        "setuptools>=77.0.3",
        "[dependency-groups]",
        'requires-python = ">=3.11"',
        'target-version = "py311"',
        'python_version = "3.11"',
    ):
        if required not in pyproject:
            fail(f"pyproject template missing current packaging metadata: {required}")
    for dated_claim in (
        "Ubuntu 26.04",
        "reaches end-of-life",
        "is the current default",
    ):
        if dated_claim in pyproject:
            fail(f"pyproject template contains point-in-time policy: {dated_claim}")
    if "[project.optional-dependencies]\ndev = [" in pyproject:
        fail("pyproject template must declare local dev tools as a dependency group")

    tooling = read_text_checked(REF_DIR / "lint-format-typing-testing.md")
    for command in UV_COMMANDS:
        if command not in tooling:
            fail(f"tooling reference missing uv-managed command: {command}")
    if "python -m uv" in tooling:
        fail("tooling reference must invoke the uv executable directly")
    if "nbqa ruff check" in tooling:
        fail("tooling reference must use Ruff's native notebook support")

    drift = read_text_checked(REF_DIR / "drift-classes.md")
    if "Edit source (root `SKILL.md`" in drift:
        fail("drift guide points to nonexistent root SKILL.md")
    if "Its `SKILL.md` is authored in place" not in drift:
        fail("drift guide does not describe mixed payload ownership")
    if "flags payload symlinks and orphans" not in drift:
        fail("drift guide does not describe regular-file payload enforcement")

    safe_editing = read_text_checked(REF_DIR / "safe-editing.md")
    for platform_marker in ('terminal("cat")', "write_file", "sed -i 's/"):
        if platform_marker in safe_editing:
            fail(f"safe-editing guide contains obsolete recipe: {platform_marker}")

    security = read_text_checked(REF_DIR / "security-and-gitignore.md")
    required_security_procedures = (
        "git check-ignore --no-index",
        "tracked_sensitive_env_files",
        "capture only its exit status",
        "do not prove a repository is secret-free",
        "History rewriting requires separate authorization",
    )
    for procedure in required_security_procedures:
        if not contains_markdown_phrase(security, procedure):
            fail(f"security reference missing required procedure: {procedure}")


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
BACKTICK_REF_RE = re.compile(r"`(references/[A-Za-z0-9._/-]+\.md)`")
EXTERNAL_URL_RE = re.compile(r"https?://[^\s)>\]`'\"]+")


def normalize_url(url: str) -> str:
    """Compare URLs without fragment, trailing slash, or trailing punctuation."""
    cleaned = url.strip().strip("<>").rstrip(".,;:'\"")
    return cleaned.split("#", 1)[0].rstrip("/")


def unregistered_urls(texts: dict[str, str], registered: set[str]) -> dict[str, str]:
    """Return ``{url: source-label}`` for payload URLs absent from the registry."""
    missing: dict[str, str] = {}
    for label, text in texts.items():
        for raw in EXTERNAL_URL_RE.findall(text):
            normalized = normalize_url(raw)
            if normalized not in registered:
                missing.setdefault(normalized, label)
    return missing


def extract_relative_links(text: str) -> list[str]:
    """Relative markdown link targets, without schemes, anchors, or titles."""
    targets: list[str] = []
    for raw in LINK_RE.findall(text):
        target = raw.strip().split()[0] if raw.strip() else ""
        target = target.split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:", "/")):
            continue
        targets.append(target)
    return targets


def extract_backtick_refs(text: str) -> list[str]:
    """Inline ``references/*.md`` paths named in backticks."""
    return BACKTICK_REF_RE.findall(text)


def load_registered_urls() -> set[str]:
    raw = read_text_checked(EVIDENCE_MANIFEST)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"evidence manifest is not valid JSON: {rel(EVIDENCE_MANIFEST)}: {exc}")
    urls = data.get("urls") if isinstance(data, dict) else None
    if not isinstance(urls, list) or not urls:
        fail(f"evidence manifest has no urls list: {rel(EVIDENCE_MANIFEST)}")
    registered: set[str] = set()
    for entry in urls:
        url = entry.get("url") if isinstance(entry, dict) else None
        if not isinstance(url, str) or not url:
            fail(f"evidence manifest entry without a url: {rel(EVIDENCE_MANIFEST)}")
        registered.add(normalize_url(url))
    return registered


def payload_texts() -> dict[str, str]:
    texts = {rel(SKILL): read_text_checked(SKILL)}
    for path in sorted(REF_DIR.glob("*.md")):
        texts[rel(path)] = read_text_checked(path)
    return texts


def check_payload_links() -> None:
    for label, text in payload_texts().items():
        base = (ROOT / label).parent
        for target in extract_relative_links(text):
            if not (base / target).is_file():
                fail(
                    f"{label} has a broken relative link: {target}",
                    hint="Fix the path or add the missing payload file.",
                )
        for refname in extract_backtick_refs(text):
            if not (SKILL_DIR / refname).is_file():
                fail(f"{label} points at a missing reference: `{refname}`")


def check_payload_urls_registered() -> None:
    registered = load_registered_urls()
    missing = unregistered_urls(payload_texts(), registered)
    if missing:
        listed = ", ".join(f"{url} ({label})" for url, label in sorted(missing.items()))
        fail(
            f"payload cites external URLs absent from {rel(EVIDENCE_MANIFEST)}: {listed}",
            hint="Register each tool doc in the manifest, then run scripts/verify-urls.py.",
        )


DECISION_HEADING_RE = re.compile(r"(?m)^## Decision: (?P<title>.+)$")
DECISION_FIELDS = ("Status", "Decided", "Sources", "Recheck")
DECISION_STATUSES = {"proposed", "accepted", "deprecated", "superseded", "rejected"}


def check_decisions() -> None:
    """Each durable decision must be complete and cite registered sources."""
    text = read_text_checked(DECISIONS)
    matches = list(DECISION_HEADING_RE.finditer(text))
    if not matches:
        fail(f"{rel(DECISIONS)} has no '## Decision:' entries")

    registered = load_registered_urls()
    for index, match in enumerate(matches):
        title = match.group("title").strip()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.end():end]
        label = f"{rel(DECISIONS)} decision {title!r}"

        fields: dict[str, str] = {}
        for line in block.splitlines():
            field = re.match(
                r"^- (?P<key>Status|Decided|Sources|Recheck):\s*(?P<value>.+?)\s*$", line
            )
            if field:
                fields[field.group("key")] = field.group("value")

        for key in DECISION_FIELDS:
            if not fields.get(key):
                fail(f"{label} is missing a non-empty '{key}:' field")
        if fields["Status"] not in DECISION_STATUSES:
            fail(f"{label} has an unknown status: {fields['Status']}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields["Decided"]):
            fail(f"{label} 'Decided' must be YYYY-MM-DD: {fields['Decided']}")

        sources = EXTERNAL_URL_RE.findall(fields["Sources"])
        if not sources:
            fail(f"{label} cites no source URL in 'Sources:'")
        for raw in sources:
            if normalize_url(raw) not in registered:
                fail(
                    f"{label} cites a source absent from {rel(EVIDENCE_MANIFEST)}: {raw}",
                    hint="Register the source in the evidence manifest, then run scripts/verify-urls.py.",
                )


def check_readme() -> None:
    readme = read_text_checked(ROOT / "README.md")
    required = [
        "agentskills.io-compatible",
        "structurally portable",
        "skills/python-project-workflow/",
        "reference-routing table",
        "Shipping boundary: `skills/python-project-workflow/` is the runtime payload",
        "hermes skills install CodeSigils/python-project-workflow-skill/skills/python-project-workflow",
        "installation verified with Hermes Agent 0.20.1",
    ]
    for phrase in required:
        if not contains_markdown_phrase(readme, phrase):
            fail(f"README.md missing required phrase: {phrase}")
    if "Hermes Skill" in readme:
        fail("README.md should not frame the project as Hermes-only")
    if "task classification table" in readme.lower():
        fail("README.md references the removed task classification table")
    if "entirely cross-agent compatible" in readme.lower():
        fail("README.md overstates runtime compatibility")
    for runtime in (" Code", "Gemini CLI", "OpenCode"):
        if not re.search(
            rf"<summary><b>{re.escape(runtime)}(?: / \.agents/ path)?</b></summary>.*?"
            r"installation and workflow behavior have not\s+been independently verified",
            readme,
            re.DOTALL,
        ):
            fail(f"README.md must bound unverified {runtime} claims")

    contributing = read_text_checked(ROOT / "CONTRIBUTING.md")
    if not contains_markdown_phrase(
        contributing, "payload under the active `HERMES_HOME` exactly matches"
    ):
        fail("CONTRIBUTING.md must describe profile-aware Hermes payload verification")


def check_evidence_docs() -> None:
    portability = read_text_checked(ROOT / "docs" / "portability-contract.md")
    for phrase in (
        "That material change started a new evidence baseline",
        "| OpenAI Codex CLI | 0.133.0 | `workflow_verified`",
        "| Hermes Agent     | 0.20.1  | `install_verified`",
        "|  Code      | —       | `candidate`",
        "| Gemini CLI       | —       | `candidate`",
        "| OpenCode         | —       | `candidate`",
        "does not by itself promote a runtime beyond `candidate`",
        "provider HTTP 429",
    ):
        if not contains_markdown_phrase(portability, phrase):
            fail(f"portability contract missing current evidence boundary: {phrase}")

    evaluation = read_text_checked(ROOT / "docs" / "behavior-evaluation-effort.md")
    for phrase in (
        "## Current baseline — behavioral contract version 3",
        "## Historical baseline — 2026-07-28",
        "historical transfer evidence",
    ):
        if not contains_markdown_phrase(evaluation, phrase):
            fail(f"behavior evaluation missing historical boundary: {phrase}")


def check_security() -> None:
    security = read_text_checked(ROOT / "SECURITY.md")
    required = [
        "## Skill Trust Checklist",
        "does not print raw commit bodies",
        "effective `.gitignore` behavior",
        "tracked sensitive files",
        "redact sensitive values from reports",
        "regular-file-only canonical and runtime entries",
    ]
    for phrase in required:
        if not contains_markdown_phrase(security, phrase):
            fail(f"SECURITY.md missing trust contract: {phrase}")


def check_status_sources() -> None:
    removed_summary = ROOT / "IMPLEMENTATION_SUMMARY.md"
    if removed_summary.exists():
        fail("IMPLEMENTATION_SUMMARY.md should not exist")
    old_skill = ROOT / "skill"
    if old_skill.exists():
        fail("old runtime directory still exists: skill/")


def main() -> int:
    check_skill()
    check_references()
    check_payload_links()
    check_payload_urls_registered()
    check_decisions()
    check_readme()
    check_evidence_docs()
    check_security()
    check_status_sources()
    print("OK: portable skill source checks are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
