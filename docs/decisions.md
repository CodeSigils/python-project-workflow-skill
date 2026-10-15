# Decisions

Durable records of non-obvious maintainer choices that would otherwise be
re-researched. Each entry states its status, the date it was decided, the
external sources behind it, and the trigger that should send a maintainer back
to re-check it. Every source URL must be registered in
[`evidence-urls.json`](evidence-urls.json), which `scripts/verify-urls.py` checks
against its expected status and content.

Keep entries short and honest: record the decision and its evidence, not a
tutorial. When a decision changes, flip its `Status` or add a superseding entry
rather than rewriting history; git history remains the full change record.
`scripts/validate.py` rejects an entry with a missing field, an unknown status, or
a source that is not registered.

## Decision: CI installs uv with the official pinned action

- Status: accepted
- Decided: 2026-10-15
- Sources: https://docs.astral.sh/uv/guides/integration/github/, https://github.com/astral-sh/setup-uv
- Recheck: a new major release of uv or of `astral-sh/setup-uv`, or a Dependabot bump of the action pin

Rationale: The official integration guide and the action's own README both
recommend `astral-sh/setup-uv`, and the guide calls pinning a specific uv version
a best practice. `actions/checkout` must run before `setup-uv` when the job reads
the repository, and combining `actions/setup-python` with `setup-uv` is
explicitly supported and faster because the runner image caches the interpreter.
The toolchain checks (Ruff, ty, shellcheck) do not depend on the Python version
under test, so they run once in a dedicated `lint` job instead of on every matrix
leg. Caching is enabled explicitly (`enable-cache: true`) and the action pin is
the full 40-character commit SHA shown in the action's README.

## Decision: Pin GitHub Actions and never persist checkout credentials

- Status: accepted
- Decided: 2026-10-15
- Sources: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions
- Recheck: a change to GitHub's hardening guidance, or when a new workflow or action is added

Rationale: GitHub's security-hardening guidance recommends pinning third-party
actions to a full-length commit SHA, the only reference that cannot be moved,
because a tag can be reassigned to a different commit. Every checkout sets
`persist-credentials: false` so the token is not written into the local Git
config, each job keeps the smallest permissions it needs (`contents: read` by
default), and CI never stores a personal access token. `scripts/validate-ci.py`
enforces the action pins and the credential rule.
