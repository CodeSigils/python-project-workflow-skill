# Security-Safe `.gitignore` and Git Workflow

Load this reference for `.gitignore`, secret-file, tracked-sensitive-file,
credential-exposure, or commit-metadata work. It supplements the always-loaded
safety contract in `SKILL.md`; it is not a general application-security audit.

## Preserve Before Editing

- Inspect existing rules and add only what the project needs. Never replace the
  file wholesale or remove security-related and project-specific entries.
- Compare Python artifact coverage with the
  [GitHub Python template](https://github.com/github/gitignore/blob/main/Python.gitignore)
  when useful. Common candidates include `__pycache__/`, `*.py[codz]`,
  `*.egg-info/`, `build/`, `dist/`, coverage outputs, `.pytest_cache/`,
  `.ruff_cache/`, `.mypy_cache/`, `.tox/`, `.nox/`, `.venv/`, and `venv/`.
- Ignore populated `.env` variants while preserving a sanitized
  `!.env.example` when the project uses one.
- Avoid broad `*.key` or `*.pem` rules until checking for intentional public
  certificates or test fixtures.
- Decide lockfile policy from the project's application-versus-library role.

## Verify Effective Ignore and Tracked State

When Git is available, check matcher behavior and tracked filenames without
printing contents:

```bash
for candidate in .env .env.local .env.production; do
  git check-ignore --no-index "$candidate" >/dev/null 2>&1 \
    || printf 'NOT_IGNORED: %s\n' "$candidate"
done

tracked_env_count=$(git ls-files -- .env '.env.*' \
  | awk '!/\.example$/{count++} END{print count+0}')
printf 'tracked_sensitive_env_files=%s\n' "$tracked_env_count"
```

Ignoring a path does not untrack it or remove it from history. If a suspected
secret is tracked or may have been shared in Git history, stop lower-priority
work, reveal neither content nor value, alert the user, and recommend revocation
or rotation. History rewriting requires separate authorization and coordination.

## Scanner and Commit-Metadata Safety

Filename checks and regex absence do not prove a repository is secret-free.
Use a project-native secret scanner only when the repository already defines
one. Use its documented quiet or redacted mode, or capture only its exit status
when output may contain matches. Do not install or configure a scanner during
ordinary project workflow setup.

Inspect recent tooling or configuration commits through bounded metadata or
counts. Do not print raw commit bodies. Never place credentials, tokens, private
keys, sensitive values, or secret-bearing URLs in commit subjects or bodies.
Report suspected exposure by existence or location only.

## Reporting Checklist

- Redact sensitive values from reports, command excerpts, generated docs, and examples.
- Distinguish ignored state from tracked state.
- Describe heuristic checks as limited evidence, not a clean-security verdict.
- Preserve sanitized examples, intentional fixtures, and public certificates.
- State skipped scanner or history checks rather than inventing success.
