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

`pre-commit` runs the fast validators: Ruff (when it is on `PATH`),
cross-agent portability, skill structure, freshness markers, version
consistency, and the README tree. `pre-push` mirrors the `validate` job in
`.github/workflows/ci.yml`, so a push that passes locally has already run
what CI would run.

The pre-push hook is the real gate on this repository. Branch protection
runs with `enforce_admins: false`, which means an administrator push to
`main` bypasses every required status check; GitHub reports those checks as
"expected" at push time, because the push that would trigger them has not
landed yet. No branch-protection setting changes that, so the hook enforces
locally and CI remains the backstop. `--no-verify` skips it, at the cost of
leaving CI as the only gate.

Both hooks are linted. CI runs `shellcheck scripts/*.sh .githooks/*` and
`validate-ci.py` requires that command, so the lint cannot be dropped
silently. Anything added to `.githooks/` is therefore expected to be shell;
if a non-shell hook is ever added deliberately, change the convention and
the command together.

For releases, follow `docs/release-checklist.md`.
