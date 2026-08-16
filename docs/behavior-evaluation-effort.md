# Behavioral evaluation transfer effort

Started: 2026-07-28T08:36:17Z

## Current baseline — 2026-08-16

The current payload and version 2 behavioral contract were evaluated through
explicit and implicit selection paths.

| Runtime | Discovery or install evidence | Behavioral result | Status |
|---|---|---|---|
| Codex CLI 0.133.0 | Exact payload copied into each fixture's `.agents/skills/python-project-workflow` directory | Implicit greenfield and explicit mature-preservation cases passed deterministic grading, 2/2 | `workflow_verified` |
| Hermes Agent 0.19.0 | Exact payload copied temporarily into `~/.hermes/skills/python-project-workflow`; `hermes skills list` showed it enabled | Not established: provider returned HTTP 429 for implicit selection, and explicit `--skills python-project-workflow` did not resolve the skill listed by the client | `install_verified` |

The temporary Hermes payload was removed after the run. Hermes was 1,661
upstream commits behind at evaluation time, so the preload discrepancy may be a
client-version limitation. No behavioral claim is made from this run.

Codex results:

| Case | Selection | Duration | Input | Cached input | Output | Result |
|---|---|---:|---:|---:|---:|---|
| Greenfield scaffold | Implicit | 102.450 s | 236,452 | 190,976 | 4,114 | Pass |
| Mature preservation | Explicit | 39.535 s | 73,581 | 64,384 | 1,581 | Pass |
| **Total** | — | **141.985 s** | **310,033** | **255,360** | **5,695** | **2/2 pass** |

The Codex client logged a model-catalog decoding warning involving an unknown
reasoning level, but both executions completed and their structured outputs and
fixture states passed the deterministic grader.

## Historical baseline — 2026-07-28

> These results apply to the payload tested with Codex
> CLI 0.133.0 on 2026-07-28. The `8f96b25` `SKILL.md` refactor created a new
> evidence baseline, so these results no longer establish current
> `workflow_verified` status. Preserve them as historical transfer evidence
> as a comparison point.

## Scope

Prospective transfer of the isolated-fixture, structured-output,
retained-artifact, and deterministic-grading pattern to
`python-project-workflow`.

## Cases

1. Greenfield: create a coherent minimal Python project with one version
   contract, `src/` layout, tests, and CI.
2. Mature preservation: inspect an existing Poetry/Black project and report
   its conventions without replacing its toolchain.

## Ledger

| Phase | Started (UTC) | Ended (UTC) | Reused | Adapted | Defects |
|---|---|---|---|---|---|
| Orientation and case selection | 2026-07-28T08:36:17Z | 2026-07-28T08:37:00Z | Pattern-transfer note, existing skill contracts | Selected project-specific positive and preservation cases | Local checkout name differed from repository name |
| Harness implementation | 2026-07-28T08:37:00Z | 2026-07-28T08:38:40Z | Python runner structure, JSON schema, isolated git fixtures, retained artifacts | Greenfield file-state grading and mature-tool preservation grading | None |
| Deterministic validation | 2026-07-28T08:38:40Z | 2026-07-28T08:39:00Z | Runner and grader self-test pattern | Executable-bit requirement for repository Ruff policy | Initial Ruff run found EXE001; executable modes fixed |
| Live evaluation | 2026-07-28T08:39:35Z | 2026-07-28T08:43:03Z | One preserved sample per case, structured output, retained transcripts | Workspace-write greenfield task plus inspection-only mature task | None; both first samples passed |

## Result

Both first-sample Codex CLI 0.133.0 cases passed deterministic grading.

| Case | Duration | Input | Cached input | Output | Result |
|---|---:|---:|---:|---:|---|
| Greenfield scaffold | 165.569 s | 351,563 | 302,080 | 6,581 | Pass |
| Mature preservation | 41.668 s | 78,259 | 48,000 | 1,455 | Pass |
| **Total** | **207.237 s** | **429,822** | **350,080** | **8,036** | **2/2 pass** |

## Transfer Assessment

- Reused unchanged: isolated git fixtures, copied runtime payload, structured
  final output, retained artifacts, deterministic grader, model-free CI
  self-tests, and one-sample preservation.
- Adapted: workspace-write greenfield grading, inspection-only mature grading,
  expected scaffold file checks, and explicit preservation of Poetry, Black,
  and tox.
- Observed implementation defect: executable script modes were required by the
  repository's Ruff policy.
- Unrelated latest-Ruff findings in pre-existing scripts were not folded into
  this transfer.

The measured wall-clock interval from ledger start to completed live run was
6 minutes 46 seconds. This includes orientation, implementation, deterministic
validation, and model execution in the existing prepared workspace; it does not
include earlier research performed before the ledger began.
