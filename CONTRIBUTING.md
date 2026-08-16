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

Run the complete command list in the README's **Verify** section. The live
Codex and Hermes runners are intentionally optional because they require local
client access and may consume a subscription. Their `--self-test` modes are
deterministic and remain part of normal validation.

Live runners delete temporary fixtures by default; pass `--retain-fixtures`
only when debugging. The Hermes runner also refuses to start unless the enabled
`~/.hermes/skills/python-project-workflow` payload exactly matches this
repository, preventing stale installations from producing runtime evidence.

When a change materially affects `SKILL.md`, an evaluation prompt, fixture,
schema, or grader, reset affected runtime claims to `candidate`. Promote a
runtime only with evidence that meets `docs/portability-contract.md`; a working
documentation link or structurally valid payload is not runtime verification.

## Pull requests

Explain the user-visible behavior, list validation performed, and identify any
runtime evidence that was reset, added, or intentionally left unverified. Keep
generated evaluation artifacts out of Git; record only redacted summaries in
maintainer documentation.

For releases, follow `docs/release-checklist.md`.
