# Portability Contract

**Status:** normative maintainer contract

**Scope:** packaging, adapter, validation, and compatibility claims for this
repository. This file is maintainer documentation and is not part of the
shipped skill payload.

## Canonical payload

`skills/python-project-workflow/` is the sole runtime source and installable
artifact. It contains:

- `SKILL.md` — the primary methodology and task routing
- `references/` — 8 detailed reference files shipped as part of the payload

Adapters may point at the skill directory or add required metadata, but must
not copy its methodology. The canonical payload remains free of
agent-specific commands, installation paths, manifest fields, and
compatibility claims as enforced by `.github/scripts/check-portability.py`.

The `scripts/payload-manifest.json` and `scripts/sync-payload.sh` together
manage the canonical-to-payload mirror process. The manifest declares which
files ship; the sync script copies them. This exists because references/ are
shipped alongside SKILL.md rather than kept as separate maintainer-only docs.

## Evidence levels

Use these claims consistently:

| Claim             | Required evidence                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------------- |
| Payload portable  | Canonical files parse under the declared format, pass the portability CI gate, and have no known platform-only runtime dependency |
| Install verified  | A named runtime and version discovers or installs the exact payload through a recorded procedure  |
| Workflow verified | That runtime completes representative positive and negative tasks against the behavioral contract |

Evidence at one level does not establish the next.

## Runtime states

Use `candidate`, `install_verified`, `workflow_verified`, `limited`, or
`unsupported`. Record the runtime version, date, installation path, explicit and
implicit selection, scenarios, evidence or grading criteria, and limitations.

A vendor documentation page can establish a documented discovery path, but it
does not by itself promote a runtime beyond `candidate`. `install_verified`
requires a maintainer-observed installation or discovery of this exact payload;
`workflow_verified` additionally requires passing behavioral cases.

Do not extrapolate a result to untested runtimes or later versions. A material
change to `SKILL.md`, the behavioral contract, prompt, or grader starts a new
evidence baseline.

## Current status

The canonical payload passes:
- Deterministic format, frontmatter, section, and reference validation (`validate.py`)
- Portability marker check (`check-portability.py`, including `references/` scope)
- Evaluation fixture and schema integrity

Behavioral contract version 3 added Git-state verification, executable CLI
checks, and exact Hermes payload hashing. That material change started a new
evidence baseline; deterministic validation alone establishes only payload
portability.

| Runtime          | Version | Status      | Current evidence boundary |
| ---------------- | ------- | ----------- | ------------------------- |
| OpenAI Codex CLI | 0.133.0 | `workflow_verified` | Contract v3 implicit greenfield and explicit mature-preservation cases passed 2/2 on 2026-08-16 with Git-state and executable CLI grading |
| Hermes Agent     | 0.20.1  | `install_verified` | Exact payload appeared enabled in `hermes skills list`; behavioral run remained blocked by provider HTTP 429 and explicit preload resolution |
| Claude Code      | —       | `candidate` | Documented discovery path only; installation and workflow unverified |
| Gemini CLI       | —       | `candidate` | Documented discovery path only; installation and workflow unverified |
| OpenCode         | —       | `candidate` | Documented discovery path only; installation and workflow unverified |

Current and historical behavioral evidence, including client diagnostics and
limitations, is recorded in `docs/behavior-evaluation-effort.md`.

## Adding runtime evidence

1. Select one runtime as an active target.
2. Record its exact version and discovery or installation path.
3. Test explicit and implicit selection with positive and negative scenarios.
4. Preserve reproducible or raw evidence without exposing sensitive values.
5. Grade against `evals/codex/cases.json`; the directory name is retained for
   compatibility, but the behavioral contract is client-neutral.
6. Record limitations and the narrowest supported state.

Keep model evaluation non-blocking. Reuse this contract and fixture vocabulary
before creating a runtime-specific runner. Extract a generic harness only after
two concrete uses share the same lifecycle and grading needs.

## Portability markers

`check-portability.py` supports file-level exemption markers for educational
content. A file whose first 3 lines contain `# portability: allow-platform-ref`
is excluded from the scan. This allows reference documents about portability
itself to reference platform-specific patterns without triggering the CI gate.

Use this marker sparingly. Prefer generic CLI examples when possible.

## Non-goals

This contract does not promise identical outputs across models, installers, or
agent products. It does not require a matrix covering every agent, and it does
not make hosted model evaluation a blocking check for ordinary changes.

The goal is a portable source of truth with explicit, evidence-bounded runtime
support — not universal behavioral equivalence.
