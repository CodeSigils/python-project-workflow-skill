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
