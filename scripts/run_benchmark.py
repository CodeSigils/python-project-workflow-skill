#!/usr/bin/env python3
"""Benchmark runner for python-best-practices skill evals.

Runs each eval from evals/evals.json in two configurations (with_skill and
without_skill) against an LLM backend, captures responses and timing, and
writes a benchmark.json summary suitable for review.

Backends:
  opencode (default)   — invokes `opencode run --model <model> <prompt>`
  codex                — invokes `codex exec` in a read-only sandbox

Usage:
  # Default: OpenCode backend with the default model
  python3 scripts/run_benchmark.py

  # Codex backend with the default Codex model
  python3 scripts/run_benchmark.py --backend codex

  # Try OpenCode first, but fall back to Codex if an OpenCode run times out
  python3 scripts/run_benchmark.py --backend opencode --fallback-backend codex --timeout 60

  # Custom model
  python3 scripts/run_benchmark.py --model anthropic/claude-sonnet-4

  # Output to a specific directory
  python3 scripts/run_benchmark.py --output-dir results/iteration-2

  # Dry-run: show what would be run without executing
  python3 scripts/run_benchmark.py --dry-run

  # Run a single eval
  python3 scripts/run_benchmark.py --filter greenfield-setup

  # Show the non-trigger Codex rerun commands without executing them
  python3 scripts/run_benchmark.py --dry-run --trigger-filter non-trigger --backend codex
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
SKILL_FILE = ROOT / "skill" / "SKILL.md"
REF_DIR = ROOT / "skill" / "references"
EVALS_FILE = ROOT / "evals" / "evals.json"
DEFAULT_OUTPUT_DIR = ROOT / "python-best-practices-workspace"
RESPONSE_FILENAME = "response.md"
RAW_STDOUT_FILENAME = "raw-output.txt"
RAW_STDERR_FILENAME = "stderr.txt"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_opencode_output(text: str) -> str:
    """Strip opencode noise lines from raw stdout."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[open-mem]") or stripped.startswith("[opencode-notify]"):
            continue
        if stripped.startswith("> Sisyphus"):
            continue
        lines.append(line.rstrip())
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + "\n" if lines else ""


def prompt_for(eval_item: dict, idx: int, cfg: str, skill_file: Path, ref_dir: Path) -> str:
    """Build the prompt for a given eval+configuration.

    Structure matches what the iteration-1 grader expects.
    """
    prompt = eval_item["prompt"]
    should_trigger = bool(eval_item.get("should_trigger"))
    verification_instruction = (
        "- Include concise verification guidance when appropriate."
        if should_trigger
        else "- For non-trigger prompts, answer only the user's direct question; do not add tooling, inspection, or verification guidance unless explicitly requested."
    )
    inspect_instruction = (
        "- Inspect the target project directory if the prompt is project-specific."
        if should_trigger
        else "- Do not perform or describe repository inspection unless the user explicitly asks for a review."
    )

    base = textwrap.dedent(f"""\
    You are producing one transcript benchmark output for the python-best-practices skill project.

    User prompt:
    {prompt}

    Instructions:
    {inspect_instruction}
    - Do not modify files. Produce the final user-facing answer only.
    - Save nothing yourself; your stdout will be captured.
    {verification_instruction}
    """)

    if cfg == "with_skill":
        expected_refs = eval_item.get("expected_references", [])
        refs_text = ", ".join(expected_refs) if expected_refs else "none"
        return textwrap.dedent(f"""\
        {base}
        WITH-SKILL CONFIGURATION:
        Before answering, use this skill under test:
        {skill_file}

        Read any relevant references from:
        {ref_dir}

        Expected relevant references for this eval: {refs_text}
        Follow the skill's trigger/non-trigger guidance. If the skill says this prompt should
        not trigger, answer simply without forcing Python tooling advice.
        """)

    return textwrap.dedent(f"""\
    {base}
    BASELINE CONFIGURATION:
    Do not read {skill_file.parent}.
    Do not mention python-best-practices, Hermes skills, or the skill under test.
    Answer from general Python/project knowledge only.
    """)


def run_opencode(
    prompt: str,
    model: str,
    input_dir: Path,
    *,
    timeout: int = 300,
) -> tuple[str, str, str, int, float]:
    """Run a single opencode invocation.

    Returns (cleaned_output, raw_stdout, raw_stderr, returncode, duration_s).
    """
    start = time.time()
    proc = subprocess.run(
        ["opencode", "run", "--model", model, prompt],
        cwd=input_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    duration = time.time() - start
    raw_output = proc.stdout
    cleaned = clean_opencode_output(raw_output)
    if proc.returncode != 0 and not cleaned.strip():
        cleaned = f"RUN ERROR (exit {proc.returncode})\n\nSTDERR:\n{proc.stderr}\n"
    return cleaned, raw_output, proc.stderr, proc.returncode, duration


def run_codex(
    prompt: str,
    model: str,
    input_dir: Path,
    output_dir: Path,
    *,
    timeout: int = 300,
) -> tuple[str, str, str, int, float]:
    """Run a single Codex invocation.

    Codex writes progress metadata to stderr. --output-last-message gives us
    a cleaner final answer for grading while stdout/stderr are still archived.
    """
    output_last = output_dir / "codex.last-message.txt"
    start = time.time()
    proc = subprocess.run(
        [
            "codex",
            "--sandbox",
            "read-only",
            "-a",
            "never",
            "--model",
            model,
            "exec",
            "--skip-git-repo-check",
            "--output-last-message",
            str(output_last),
            "-",
        ],
        input=prompt,
        cwd=input_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    duration = time.time() - start
    raw_output = proc.stdout
    cleaned = raw_output
    if output_last.exists():
        cleaned = output_last.read_text(encoding="utf-8")
    if proc.returncode != 0 and not cleaned.strip():
        cleaned = f"RUN ERROR (exit {proc.returncode})\n\nSTDERR:\n{proc.stderr}\n"
    return cleaned, raw_output, proc.stderr, proc.returncode, duration


# ---------------------------------------------------------------------------
# Grader
# ---------------------------------------------------------------------------

def grade_output(
    response: str,
    assertions: dict,
) -> list[dict]:
    """Run assertion checks against the response.

    Supports exact substring requirements (must_include / must_not_include)
    plus synonym groups (must_include_any). The synonym groups keep evals
    focused on behavior instead of brittle one-word phrasing.

    Returns a list of expectation dicts matching the grading.json format.
    """
    must_include = assertions.get("must_include", [])
    must_include_any = assertions.get("must_include_any", [])
    must_not_include = assertions.get("must_not_include", [])
    expectations = []
    response_lower = response.lower()

    for term in must_include:
        passed = term.lower() in response_lower
        expectations.append({
            "text": f"Includes expected guidance: {term}",
            "passed": passed,
            "evidence": (
                f"Found: '{term}' appears in response."
                if passed
                else f"Missing: '{term}' not found in response."
            ),
        })

    for group in must_include_any:
        name = group.get("name", "one of expected alternatives")
        terms = group.get("terms", [])
        found_terms = [term for term in terms if term.lower() in response_lower]
        passed = bool(found_terms)
        expectations.append({
            "text": f"Includes expected guidance group: {name}",
            "passed": passed,
            "evidence": (
                f"Found alternative(s): {found_terms!r}."
                if passed
                else f"Missing all alternatives for {name!r}: {terms!r}."
            ),
        })

    for term in must_not_include:
        passed = term.lower() not in response_lower
        expectations.append({
            "text": f"Avoids prohibited guidance: {term}",
            "passed": passed,
            "evidence": (
                f"No prohibited guidance found for '{term}'."
                if passed
                else f"Found prohibited guidance: '{term}' appears in response."
            ),
        })

    return expectations


def compute_summary(expectations: list[dict]) -> dict:
    passed = sum(1 for e in expectations if e["passed"])
    total = len(expectations)
    return {
        "passed": passed,
        "failed": total - passed,
        "total": total,
        "pass_rate": round(passed / total, 4) if total else 1.0,
    }


def check_filesystem_changes(original: Path, working: Path) -> list[dict]:
    """Detect files created, deleted, or modified by the agent.

    Compares the original fixture directory against the working copy the agent
    ran in. Tool-generated artifacts are ignored. Returns expectation dicts
    only for unexpected changes; no changes means an empty list.
    """
    if not original.exists() or not working.exists():
        return []

    expectations: list[dict] = []
    excluded_names = {
        ".omo",
        ".open-mem",
        "opencode.raw.txt",
        "opencode.stderr.txt",
        RAW_STDOUT_FILENAME,
        RAW_STDERR_FILENAME,
    }

    def is_excluded(path: Path) -> bool:
        return any(part in excluded_names for part in path.parts)

    def add_failure(text: str, evidence: str) -> None:
        expectations.append({"text": text, "passed": False, "evidence": evidence})

    original_files = {
        path.relative_to(original)
        for path in original.rglob("*")
        if path.is_file() and not is_excluded(path.relative_to(original))
    }
    working_files = {
        path.relative_to(working)
        for path in working.rglob("*")
        if path.is_file() and not is_excluded(path.relative_to(working))
    }

    for rel_path in sorted(original_files - working_files):
        add_failure(
            f"Agent did not delete fixture file: {rel_path.as_posix()}",
            f"Fixture file missing from working directory: {rel_path.as_posix()}",
        )

    for rel_path in sorted(working_files - original_files):
        add_failure(
            f"Agent did not create unexpected file: {rel_path.as_posix()}",
            f"Unexpected file created in working directory: {rel_path.as_posix()}",
        )

    for rel_path in sorted(original_files & working_files):
        if not (original / rel_path).read_bytes() == (working / rel_path).read_bytes():
            add_failure(
                f"Agent did not modify fixture file: {rel_path.as_posix()}",
                f"File differs between fixture and working copy: {rel_path.as_posix()}",
            )

    return expectations


DEGENERATE_PATTERNS = [
    "waiting for context",
    "context-gathering",
    "i need to see",
    "let me examine",
    "let me look at",
    "let me check",
    "let me run",
    "i'll run",
    "i will run",
    "i should inspect",
    "before i answer",
    "i need to gather",
    "analyzing the",
    "let me first",
    "fetching context",
]


def check_degenerate_output(response: str) -> list[dict]:
    """Detect signs the agent got stuck in a meta-loop.

    Returns expectation dicts for patterns that indicate the model is
    describing its internal process instead of producing a final answer.
    Only flags patterns that appear BEFORE any substantive response.
    """
    if not response or len(response.strip()) < 50:
        return []

    expectations: list[dict] = []
    lines = response.splitlines()
    # Analyze first 20% of the response for degenerate patterns
    sample_lines = lines[:max(5, len(lines) // 5)]
    sample_text = "\n".join(sample_lines).lower()

    for pattern in DEGENERATE_PATTERNS:
        if pattern in sample_text:
            expectations.append({
                "text": f"Response does not start with degenerate meta-loop: \"{pattern}\"",
                "passed": False,
                "evidence": f"Pattern '{pattern}' found in first {len(sample_lines)} lines of response",
            })

    # Check for runs where the model just echoes the instruction
    if "WITH-SKILL CONFIGURATION" in response or "BASELINE CONFIGURATION" in response:
        expectations.append({
            "text": "Response does not echo the benchmark instruction verbatim",
            "passed": False,
            "evidence": "Response still contains benchmark configuration header text",
        })

    return expectations


def check_run_status(returncode: int) -> list[dict]:
    """Fail grading when the benchmarked command did not complete cleanly."""
    if returncode == 0:
        return []
    return [{
        "text": "Agent run completed without command error or timeout",
        "passed": False,
        "evidence": f"Benchmark command returned exit code {returncode}",
    }]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run python-best-practices skill benchmark evals.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR,
        help="Output directory for benchmark results (default: %(default)s)",
    )
    parser.add_argument(
        "--backend", choices=("opencode", "codex"), default=os.environ.get("PBP_EVAL_BACKEND", "opencode"),
        help="Agent backend to run (default: %(default)s, or PBP_EVAL_BACKEND env var)",
    )
    parser.add_argument(
        "--model", default=os.environ.get("PBP_EVAL_MODEL"),
        help="Model identifier for the selected backend (or PBP_EVAL_MODEL env var)",
    )
    parser.add_argument(
        "--fallback-backend", choices=("none", "codex"), default=os.environ.get("PBP_EVAL_FALLBACK_BACKEND", "none"),
        help="Fallback backend to use when an OpenCode run times out (default: %(default)s)",
    )
    parser.add_argument(
        "--fallback-model", default=os.environ.get("PBP_EVAL_FALLBACK_MODEL", "gpt-5.5"),
        help="Model identifier for the fallback backend (default: %(default)s, or PBP_EVAL_FALLBACK_MODEL env var)",
    )
    parser.add_argument(
        "--delegate", action="store_true",
        help="Use Hermes delegate_task backend instead of the selected CLI backend",
    )
    parser.add_argument(
        "--provider", default=None,
        help="Provider name for hermes backend (e.g. openrouter, anthropic)",
    )
    parser.add_argument(
        "--filter", default=None,
        help="Run only evals whose name contains this substring",
    )
    parser.add_argument(
        "--trigger-filter", choices=("all", "trigger", "non-trigger"), default="all",
        help="Run all evals, only triggering evals, or only non-triggering evals (default: %(default)s)",
    )
    parser.add_argument(
        "--timeout", type=int, default=300,
        help="Timeout in seconds per eval run (default: %(default)s)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be run without executing",
    )
    parser.add_argument(
        "--iteration-label", default=None,
        help="Label for this benchmark iteration (default: auto-increment)",
    )
    return parser.parse_args(argv)


def build_output_dir(base: Path, label: str | None) -> Path:
    """Determine the output directory, auto-incrementing if needed."""
    if label:
        return base / label
    if not base.exists():
        return base / "iteration-1"
    existing = sorted(
        (d for d in base.iterdir() if d.name.startswith("iteration-") and d.is_dir()),
        reverse=True,
    )
    if existing:
        last_num = max(
            int(d.name.split("-")[1]) for d in existing if d.name.split("-")[1].isdigit()
        )
        next_num = last_num + 1
    else:
        next_num = 1
    return base / f"iteration-{next_num}"


def main() -> int:
    args = parse_args()
    if args.model is None:
        args.model = "gpt-5.5" if args.backend == "codex" else "opencode/big-pickle"
    if args.fallback_backend != "none" and args.backend != "opencode":
        print("ERROR: --fallback-backend is only supported when --backend opencode", file=sys.stderr)
        return 1

    if not SKILL_FILE.exists():
        print(f"ERROR: skill file not found: {SKILL_FILE}", file=sys.stderr)
        return 1
    if not EVALS_FILE.exists():
        print(f"ERROR: evals file not found: {EVALS_FILE}", file=sys.stderr)
        return 1

    evals_data = json.loads(EVALS_FILE.read_text(encoding="utf-8"))
    evals = evals_data.get("evals", [])
    if not evals:
        print("ERROR: no evals found in evals.json", file=sys.stderr)
        return 1

    if args.trigger_filter == "trigger":
        evals = [e for e in evals if e.get("should_trigger") is True]
    elif args.trigger_filter == "non-trigger":
        evals = [e for e in evals if e.get("should_trigger") is False]

    if args.filter:
        evals = [e for e in evals if args.filter.lower() in e["name"].lower()]
        if not evals:
            print(f"ERROR: no evals match filter: {args.filter}", file=sys.stderr)
            return 1
    if not evals:
        print(f"ERROR: no evals match trigger filter: {args.trigger_filter}", file=sys.stderr)
        return 1

    output_dir = build_output_dir(args.output_dir, args.iteration_label)
    if args.dry_run:
        print(f"[dry-run] Would output to: {output_dir}")
        print(f"[dry-run] Model: {args.model}")
        print(f"[dry-run] Backend: {'hermes delegate' if args.delegate else args.backend}")
        if args.fallback_backend != "none":
            print(f"[dry-run] Fallback: {args.fallback_backend} ({args.fallback_model}) on OpenCode timeout")
        print(f"[dry-run] Evals to run: {[e['name'] for e in evals]}")
        print("[dry-run] Configurations: with_skill, without_skill")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    runs_data = []
    aggregate_timestamps: dict[str, list[float]] = {"with_skill": [], "without_skill": []}
    aggregate_pass_rates: dict[str, list[float]] = {"with_skill": [], "without_skill": []}

    for idx, eval_item in enumerate(evals):
        name = eval_item["name"]
        fixture = Path(str(eval_item.get("fixture", "")))
        fixture_abs = ROOT / fixture if not fixture.is_absolute() else fixture
        assertions = {
            "must_include": eval_item.get("must_include", []),
            "must_include_any": eval_item.get("must_include_any", []),
            "must_not_include": eval_item.get("must_not_include", []),
        }

        for cfg in ("with_skill", "without_skill"):
            edir = output_dir / f"eval-{idx}-{name}" / cfg

            # Prepare input directory: use the fixture directory
            input_dir = edir / "input"
            output_dir_cfg = edir / "outputs"

            if edir.exists():
                shutil.rmtree(edir)
            input_dir.mkdir(parents=True, exist_ok=True)
            output_dir_cfg.mkdir(parents=True, exist_ok=True)

            # Copy fixture contents into input dir
            if fixture_abs.exists():
                for item in fixture_abs.iterdir():
                    dest = input_dir / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest)

            # Build prompt
            prompt_text = prompt_for(
                eval_item, idx, cfg, SKILL_FILE, REF_DIR,
            )

            # Run
            print(f"Running {name} {cfg} ...", end=" ", flush=True)
            backend = "hermes" if args.delegate else args.backend
            effective_backend = backend
            effective_model = args.model
            fallback_reason = None

            if args.delegate:
                # Hermes delegate_task backend — not fully implemented in this version
                print("SKIP (hermes delegate backend needs hermes_python_client)")
                cleaned = "HERMES DELEGATE BACKEND NOT IMPLEMENTED"
                raw_output = cleaned
                raw_stderr = ""
                returncode = -1
                duration = 0.0
            else:
                try:
                    if args.backend == "codex":
                        cleaned, raw_output, raw_stderr, returncode, duration = run_codex(
                            prompt_text, args.model, input_dir, output_dir_cfg, timeout=args.timeout,
                        )
                    else:
                        cleaned, raw_output, raw_stderr, returncode, duration = run_opencode(
                            prompt_text, args.model, input_dir, timeout=args.timeout,
                        )
                    print(f"exit={returncode} duration={duration:.1f}s")
                except subprocess.TimeoutExpired:
                    if args.backend == "opencode" and args.fallback_backend == "codex":
                        print(f"TIMEOUT ({args.timeout}s); falling back to codex ...", end=" ", flush=True)
                        effective_backend = "codex"
                        effective_model = args.fallback_model
                        try:
                            cleaned, raw_output, raw_stderr, returncode, fallback_duration = run_codex(
                                prompt_text, args.fallback_model, input_dir, output_dir_cfg, timeout=args.timeout,
                            )
                            raw_stderr = (
                                f"OpenCode timed out after {args.timeout}s; "
                                f"fallback_backend=codex fallback_model={args.fallback_model}\n\n"
                                f"{raw_stderr}"
                            )
                            duration = float(args.timeout) + fallback_duration
                            fallback_reason = "opencode_timeout"
                            print(f"exit={returncode} duration={duration:.1f}s")
                        except subprocess.TimeoutExpired:
                            print(f"FALLBACK TIMEOUT ({args.timeout}s)")
                            cleaned = f"TIMEOUT after {args.timeout}s; codex fallback also timed out after {args.timeout}s"
                            raw_output = cleaned
                            raw_stderr = ""
                            returncode = -1
                            duration = float(args.timeout * 2)
                            fallback_reason = "codex_timeout"
                    else:
                        print(f"TIMEOUT ({args.timeout}s)")
                        cleaned = f"TIMEOUT after {args.timeout}s"
                        raw_output = cleaned
                        raw_stderr = ""
                        returncode = -1
                        duration = float(args.timeout)
                        fallback_reason = f"{args.backend}_timeout"

            # Write outputs
            response_file = output_dir_cfg / RESPONSE_FILENAME
            raw_file = output_dir_cfg / RAW_STDOUT_FILENAME
            err_file = output_dir_cfg / RAW_STDERR_FILENAME
            timing_file = edir / "timing.json"

            response_file.write_text(cleaned, encoding="utf-8")
            raw_file.write_text(raw_output, encoding="utf-8")
            err_file.write_text(raw_stderr, encoding="utf-8")
            timing_file.write_text(json.dumps({
                "backend": backend,
                "effective_backend": effective_backend,
                "model": args.model,
                "effective_model": effective_model,
                "fallback_reason": fallback_reason,
                "returncode": returncode,
                "duration_seconds": round(duration, 3),
                "stdout_bytes": len(raw_output.encode()),
                "stderr_bytes": len(raw_stderr.encode()),
                "tokens": None,
            }, indent=2), encoding="utf-8")

            # Grade: text assertions + filesystem + degenerate checks
            expectations = grade_output(cleaned, assertions)
            fs_expectations = check_filesystem_changes(fixture_abs, input_dir)
            degenerate_expectations = check_degenerate_output(cleaned)
            status_expectations = check_run_status(returncode)
            all_expectations = expectations + status_expectations + fs_expectations + degenerate_expectations
            summary = compute_summary(all_expectations)
            grading_file = edir / "grading.json"
            grading_file.write_text(json.dumps({
                "eval_id": idx,
                "eval_name": name,
                "configuration": cfg,
                "expectations": all_expectations,
                "summary": summary,
                "grader_note": (
                    "Substring checks with narrow synonym handling; analyst pass should review "
                    "false positives/negatives. Command-status, filesystem-change, "
                    "and degenerate-output checks are also included."
                ),
            }, indent=2), encoding="utf-8")

            aggregate_timestamps[cfg].append(duration)
            aggregate_pass_rates[cfg].append(summary["pass_rate"])

            runs_data.append({
                "eval_id": idx,
                "eval_name": name,
                "configuration": cfg,
                "run_number": 1,
                "result": {
                    "pass_rate": summary["pass_rate"],
                    "passed": summary["passed"],
                    "failed": summary["failed"],
                    "total": summary["total"],
                    "time_seconds": round(duration, 3),
                    "backend": backend,
                    "effective_backend": effective_backend,
                    "model": args.model,
                    "effective_model": effective_model,
                    "fallback_reason": fallback_reason,
                    "tokens": None,
                    "errors": 0 if returncode == 0 else 1,
                },
            })

    # Write benchmark.json summary
    def stats(vals: list[float]) -> dict:
        if not vals:
            return {"mean": 0, "stddev": 0, "min": 0, "max": 0}
        mean = sum(vals) / len(vals)
        variance = sum((x - mean) ** 2 for x in vals) / len(vals)
        return {
            "mean": round(mean, 4),
            "stddev": round(variance ** 0.5, 4),
            "min": round(min(vals), 4) if vals else 0,
            "max": round(max(vals), 4) if vals else 0,
        }

    with_skill_times = aggregate_timestamps["with_skill"]
    without_skill_times = aggregate_timestamps["without_skill"]
    with_skill_rates = aggregate_pass_rates["with_skill"]
    without_skill_rates = aggregate_pass_rates["without_skill"]

    bench = {
        "metadata": {
            "skill_name": "python-best-practices",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "backend": "hermes" if args.delegate else args.backend,
            "model": args.model,
            "fallback_backend": None if args.fallback_backend == "none" else args.fallback_backend,
            "fallback_model": None if args.fallback_backend == "none" else args.fallback_model,
            "note": f"Generated by scripts/run_benchmark.py (backend: {'hermes' if args.delegate else args.backend})",
        },
        "runs": runs_data,
        "run_summary": {
            "with_skill": {
                "pass_rate": stats(with_skill_rates),
                "time_seconds": stats(with_skill_times),
                "tokens": {"mean": None, "stddev": None, "min": None, "max": None},
            },
            "without_skill": {
                "pass_rate": stats(without_skill_rates),
                "time_seconds": stats(without_skill_times),
                "tokens": {"mean": None, "stddev": None, "min": None, "max": None},
            },
            "delta": {
                "pass_rate": round(
                    (stats(with_skill_rates)["mean"] - stats(without_skill_rates)["mean"]), 4
                ) if with_skill_rates and without_skill_rates else 0,
                "time_seconds": round(
                    (stats(with_skill_times)["mean"] - stats(without_skill_times)["mean"]), 4
                ) if with_skill_times and without_skill_times else 0,
                "tokens": None,
            },
        },
    }

    bench_file = output_dir / "benchmark.json"
    bench_file.write_text(json.dumps(bench, indent=2), encoding="utf-8")
    print(f"\nBenchmark written to: {bench_file}")
    print(f"Output directory: {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
