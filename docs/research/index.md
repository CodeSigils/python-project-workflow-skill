# Research record

**Append-only.** Consult this register, [`../decisions.md`](../decisions.md),
and [`../evidence-urls.json`](../evidence-urls.json) before researching a
covered maintainer concern. Reuse a current, applicable result; otherwise
research primary guidance, add a dated finding, then record any durable
decision it enables.

| ID | Concern | Status | Last Verified | Enables |
| --- | --- | --- | --- | --- |
| R-001 | Whether CI should install uv with its official pinned action | Complete | 2026-10-15 | D1 |
| R-002 | How CI should pin Actions and handle checkout credentials | Complete | 2026-10-15 | D2 |
| R-003 | Whether this repository needs a standalone research-first consultation path | Complete | 2026-10-15 | D3 |
| R-004 | How to prevent scheduled hygiene failures from unreviewed Dependabot pull requests | Complete | 2026-11-04 | D4 |

## R-001 — CI installs uv with its official pinned action

The official uv GitHub Actions guide recommends `astral-sh/setup-uv`, supports
combining it with `actions/setup-python`, and documents caching. The action
repository documents its supported inputs. This applies to the repository's
CI setup, not to a generated Python project.

Sources: https://docs.astral.sh/uv/guides/integration/github/,
https://github.com/astral-sh/setup-uv

## R-002 — Pin Actions and do not persist checkout credentials

GitHub's security hardening guidance recommends pinning third-party Actions to
full commit SHAs. It supports the repository's narrower CI policy: least
privilege job permissions and `persist-credentials: false` on every checkout.

Sources: https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions

## R-003 — Standalone research-first consultation

Evidence-based software engineering frames a decision as a question followed
by relevant, critically appraised evidence and an outcome check. GOV.UK's
assurance guidance makes the evidence-to-decision link explicit; AWS ADR
guidance keeps decision context and consequences reviewable. These are
applicable to durable maintainer decisions, while the repository's lightweight
records deliberately do not claim a universal evidence score or a full trade
study for routine choices.

Sources: https://ebse.webspace.durham.ac.uk/,
https://www.gov.uk/government/publications/evidence-led-assurance-for-the-software-development-lifecycle,
https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html

## R-004 — Scheduled hygiene and unreviewed Dependabot pull requests

Two consecutive Monday runs failed only in the repository-hygiene job because
Dependabot pull requests #26 and #27 had no review past the three-day grace and
#26 had not been updated for fourteen days. GitHub documents that scheduled
runs can be delayed under load (the 09:17 UTC cron started between 14:34 and
19:31 UTC) but delay did not cause these failures. Auto-merge waits for all
required checks and must be enabled at repository level. Dependabot-triggered
workflows get a read-only `GITHUB_TOKEN` by default and require explicit
`permissions` to write. Dependabot rebases on its weekly schedule or on
conflict, not immediately when merely behind, so `strict` required checks can
leave a queued pull request waiting. The hygiene gate therefore must not count
auto-merge-queued work as review debt. A separate 2026-09-21 URL-verification
failure remains a one-off with no retained log; diagnostics are a separate
concern.

Sources: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows,
https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/automatically-merging-a-pull-request,
https://docs.github.com/en/code-security/dependabot/working-with-dependabot/automating-dependabot-with-github-actions,
https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-on-actions,
https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference
