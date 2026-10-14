# Contributing

Thanks for improving Python Project Workflow. Only
`skills/python-project-workflow/` ships to users; repository docs, fixtures,
scripts, CI, and root `references/` are maintainer infrastructure.

## Make a focused change

1. Read `skills/python-project-workflow/SKILL.md` and the relevant canonical
   file under `references/`.
2. Edit `SKILL.md` in place. Edit reference content only in root `references/`,
   then run `bash scripts/sync-payload.sh` to refresh the shipped mirror.
3. Keep frontmatter limited to `name` and `description`, keep the payload
   client-neutral, and preserve progressive disclosure.
4. Do not include credentials, private repository content, raw commit bodies,
   or secret-bearing URLs in fixtures, logs, commits, or reports.

## Validate

Install the toolchain first with `uv sync --locked`. Ruff is pinned in
`uv.lock` rather than in a workflow variable, so local and CI runs lint with
the same version; Dependabot updates that pin.

Run the complete command list in the README's **Verify** section. The live
Codex and Hermes runners are intentionally optional because they require local
client access and may consume a subscription. Their `--self-test` modes are
deterministic and remain part of normal validation.

Live runners delete temporary fixtures by default; pass `--retain-fixtures`
only when debugging. The Hermes runner also refuses to start unless the payload
under the active `HERMES_HOME` exactly matches this repository, preventing stale
installations from producing runtime evidence.

When a change materially affects `SKILL.md`, an evaluation prompt, fixture,
schema, or grader, reset affected runtime claims to `candidate`. Promote a
runtime only with evidence that meets `docs/portability-contract.md`; a working
documentation link or structurally valid payload is not runtime verification.

## Pull requests

Explain the user-visible behavior, list validation performed, and identify any
runtime evidence that was reset, added, or intentionally left unverified. Keep
generated evaluation artifacts out of Git; record only redacted summaries in
maintainer documentation.

## Local hooks

This repository ships two POSIX shell hooks in `.githooks/`. Activate them
once per clone:

```sh
git config core.hooksPath .githooks
```

`pre-commit` runs the fast validators: hook integrity, Ruff (when it is on
`PATH`), cross-agent portability, skill structure, freshness markers, version
consistency, and the README tree. `pre-push` runs the complete local source
validation gate before a direct push to `main`; it deliberately exits without
running for feature branches and tags.

GitHub branch protection is the authoritative gate: `main` requires its CI
checks and does not allow administrator bypass. The repository has one solo
maintainer, so it deliberately requires zero approvals; pull requests remain
the normal change record and CI is the independent validation. The local hook
is faster feedback only. `--no-verify` skips it, leaving GitHub CI as the
remaining gate.

Both hooks are linted. CI runs `shellcheck scripts/*.sh .githooks/*` and
`validate-ci.py` requires that command, so the lint cannot be dropped
silently. Anything added to `.githooks/` is therefore expected to be shell;
if a non-shell hook is ever added deliberately, change the convention and
the command together.

Shell lint cannot see content damage inside a hook. A redaction pass once
rewrote `===` banner strings in `.githooks/*`, `ci.yml`, and the shipped
references to a removal placeholder, and every gate stayed green because
Ruff and `ty` only read `scripts/` and `.github/scripts/`.
`scripts/check-hook-integrity.py` closes that gap: it fails when a hook no
longer runs a command recorded in its manifest, and when a tracked file
carries a redaction placeholder. Stage matching is whitespace-normalized, so
reflowing a command is fine while deleting one is not. When you add, remove,
or rename a stage in either hook, update the manifest in the same change; the
command is required in CI by `validate-ci.py`, so CI enforces the same
manifest the hooks do.

For releases, follow `docs/release-checklist.md`.

## Automation decisions

- GitHub branch protection, not local hooks, requires CI checks and prevents
  direct pushes to `main`, including administrator bypass. The repository has
  a solo maintainer, so the approval requirement remains zero; stale-review
  dismissal is retained for any future collaborator review.
- Only an annotated `vX.Y.Z` tag whose target is reachable from `main` and
  whose version matches `CITATION.cff` can create a release. The release job
  receives `contents: write` only after a read-only preflight passes.
- Dependabot groups minor and patch GitHub Action updates weekly. Major action
  upgrades stay deliberately manual and must receive the same review as a
  migration.
- The scheduled hygiene job treats an unreviewed pull request older than three
  days and any open pull request older than fourteen days as failures. A remote
  branch without an open pull request becomes stale after thirty days.
