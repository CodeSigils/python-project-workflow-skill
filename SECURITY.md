# Security Policy

Report security issues privately through the
[GitHub Security Advisory](https://github.com/CodeSigils/python-project-workflow-skill/security/advisories/new)
rather than opening a public issue.

Security concerns in this repository include scaffolding instructions that could
generate insecure project configurations or expose secrets, or supply-chain
risks in CI scripts and workflows. Do not include exploit details in public
reports.

Issues that do not involve the CI pipeline or credential material can be opened
as public GitHub issues. Report CI-related vulnerabilities through the advisory
link above.

The shipped payload is a single `SKILL.md` and seven reference files with no
runtime scripts, no config files, and no dependencies. Shipped instructions
are checked for agent-specific references by CI.

The orientation checklist directs agents to inspect structured configuration
files (pyproject.toml, .gitignore, CI YAML) through the agent's native reading
capability — it does not use content-extraction shell commands (`cat`,
`git log`, `grep`) that could expose credentials. The primary security concern
is correctness of generated project files and CI templates, not runtime
scanning of repository content.

Last reviewed: 2026-07-15.
