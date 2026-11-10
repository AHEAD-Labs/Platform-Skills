# Proposal: Skills Auditor status check (draft, needs decisions)

Status: **not active.** See `internal-auditor-runner.yml.example` and `../AUDITOR-CONTRACT.md`.

| Decision | Owner | Notes |
| --- | --- | --- |
| Push, review and merge Auditor `db4d148`; nominate the pinned SHA | Skills Auditor owner | The branch was local-only on 2026-10-19 |
| Create GitHub App with `statuses:write` on Platform-Skills only | Org admin | Private key stored only in the internal repo |
| Where the runner lives (Skills-Marketplace or a separate internal repo) | Enterprise GPT | |
| Trigger: manual dispatch by a reviewer vs. scheduled poll of open PRs | Enterprise GPT | Manual is simpler and keeps a human in the loop |
| Require `skills-auditor/result` (source: that App) on `main` | Platform-Skills admins | Add to the ruleset in GOVERNANCE.md |
| Whether seed baselines need audit before they may live on `main` | Admins + Security | See PR C |

Once active, a reviewer dispatches the run with the PR head SHA, reads the internal report, and approves the PR only when `skills-auditor/result` is success and the content review is done. REVIEW_READY is never approval.
