# Security Policy

## Reporting a Vulnerability

Report security issues privately through the
[GitHub Security Advisory](https://github.com/CodeSigils/python-project-workflow-skill/security/advisories/new)
rather than opening a public issue. Do not include exploit details, credentials,
or other sensitive values in public reports.

Use private reporting for any credible security vulnerability, including:

- instructions or templates that could generate insecure project
  configurations, expose secrets, or cause destructive repository changes;
- unsafe credential, commit-metadata, `.gitignore`, or tracked-file guidance;
- compromised or misleading shipped skill payloads; and
- supply-chain or privilege risks in repository scripts, dependencies, or CI
  workflows.

Ordinary documentation defects, feature requests, and behavior bugs without a
credible security impact may be opened as public GitHub issues. When uncertain,
report privately.

## Repository Security Scope

Repository security covers maintainer infrastructure outside the shipped
payload: GitHub Actions, validation and synchronization scripts, release
metadata, and the canonical-to-payload mirror process. These components must
preserve the declared shipping boundary, avoid exposing credentials, and prevent
unreviewed content from entering the runtime payload.

CI validates payload structure, regular-file-only canonical and runtime entries,
canonical-reference parity, portable instructions, security directives, and the
absence of known unsafe probes. A
passing validator is evidence for these defined checks, not a claim that the
repository or generated projects are free of vulnerabilities.

## Shipped Skill Trust Guarantees

The shipped payload is a single `SKILL.md` and eight reference files with no
runtime scripts, no config files, and no dependencies. Shipped instructions
are checked for agent-specific references by CI.

The orientation checklist directs agents to inspect project configuration,
version-control state, and recent tooling changes. These checks should use
metadata-oriented commands and targeted reads without printing suspected secret
contents. If credentials may already be tracked or present in Git history, the
skill directs the agent to stop, alert the user, redact output, and recommend
revocation or rotation. The primary security concern is correctness of generated
project files and CI templates while avoiding disclosure during inspection.

Always-on safety rules live in
[`skills/python-project-workflow/SKILL.md`](skills/python-project-workflow/SKILL.md).
Detailed executable guidance is maintained canonically in
[`references/security-and-gitignore.md`](references/security-and-gitignore.md)
and shipped as its verified mirror under the skill payload. `SECURITY.md`
summarizes the trust boundary; it does not replace those runtime instructions.

## Skill Trust Checklist

- [x] Secret-related checks emit filenames, locations, counts, or status—not secret values.
- [x] Recent-history guidance does not print raw commit bodies.
- [x] The workflow checks effective `.gitignore` behavior separately from tracked sensitive files.
- [x] `.gitignore` recommendations preserve existing security rules and sanitized examples.
- [x] Agents redact sensitive values from reports and generated examples, and do not claim a repository is secret-free
  from heuristic or filename checks.
- [x] The shipped payload contains no destructive reset, forced-push, or secret-file dumping commands.

Last reviewed: 2026-07-17.
