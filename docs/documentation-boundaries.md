# Documentation Boundaries

This map assigns one primary owner to each maintained documentation concern.
It prevents parallel sources of truth while preserving audience-appropriate
navigation.

| Concern | Canonical source | Derived or supporting surfaces | Drift control | Recheck trigger |
| --- | --- | --- | --- | --- |
| Shipped workflow and reference routing | `skills/python-project-workflow/` | Root `references/` supplies mirrored reference content | `scripts/validate.py`; `scripts/sync-payload.sh --ci` | Any runtime payload or reference change |
| Mirrored runtime references | Root `references/` | `skills/python-project-workflow/references/` | `scripts/payload-manifest.json`; `scripts/sync-payload.sh --ci` | Add, remove, rename, or edit a reference |
| Client runtime-support status | `docs/portability-contract.md` | README installation links; behavioral-evidence ledger | Evidence-boundary review in `AGENTS.md`; `scripts/validate.py` | Runtime, fixture, prompt, grader, or payload-contract change |
| Behavioral execution evidence | `docs/behavior-evaluation-effort.md` | Runtime-support matrix | Deterministic regression suite and recorded run artifacts | New deterministic or live evaluation run |
| Maintainer verification commands | `scripts/stage_manifest.py` | CI workflow, Git hooks, README Verify block | `scripts/validate-ci.py`; `scripts/check-hook-integrity.py` | Add, remove, or rename a verification stage |
| Repository orientation and file roles | README Repo Layout | Tracked and unignored worktree files | `scripts/check-readme-tree.py` | Tracked-file or role-boundary change |
| Security reporting and trust boundary | `SECURITY.md` and `references/security-and-gitignore.md` | Shipped security reference | `scripts/validate.py`; portability and CI-policy checks | Payload safety, CI permission, or sensitive-evidence procedure change |
| Durable maintainer decisions and external evidence | `docs/decisions.md`, `docs/research/index.md`, and `docs/evidence-urls.json` | Canonical references when a decision changes runtime guidance | `scripts/validate.py`; scheduled URL verification | New durable decision or source recheck |

Use this map when a documentation change crosses audiences or artifacts. Edit the
canonical source first, update only the listed derived surfaces, and run the
named control rather than copying a rule into an additional document.
