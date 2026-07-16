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

The orientation checklist directs agents to inspect project configuration,
version-control state, and recent tooling changes. These checks should use
metadata-oriented commands and targeted reads without printing suspected secret
contents. If credentials may already be tracked or present in Git history, the
skill directs the agent to stop, alert the user, redact output, and recommend
revocation or rotation. The primary security concern is correctness of generated
project files and CI templates while avoiding disclosure during inspection.

Last reviewed: 2026-07-16.
