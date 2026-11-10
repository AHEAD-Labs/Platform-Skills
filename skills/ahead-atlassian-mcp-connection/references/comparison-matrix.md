# Requirements Traceability Matrix

| Requirement (source) | Implementation | Acceptance criterion | Eval case | Status |
|---|---|---|---|---|
| Route to the right tool without the user naming it (initiative brief) | Both adapters, steps 1–2; routing references | AC-1, AC-2, AC-3, AC-18 | 1, 2, C-1 | Implemented |
| Agents use Jira Actions, not service-credential tools (Isha Mehta, 2026-10-30) | Field rule; agent-builder guidance | AC-2, AC-16 | 2, P-02 | Implemented |
| Search works but edit/comment fails from group sync (Isha Mehta, 2026-10-27) | Glean diagnosis cause 2; edit-metadata and transition check | AC-5, AC-6 | 3, P-01 | Implemented |
| "Pagination incomplete" (Isha Mehta, 2026-10-27) | Bounded paging (Glean step 3, Claude step 3); Partial template | AC-7, AC-17 | G-01 | Implemented; paging verified live 2026-11-10 |
| One cause instead of four or five (initiative brief) | Decision orders, first match wins | AC-5, AC-17 | 3, A-01, C-2 | Implemented |
| Admin fixes go to a Service Desk ticket (owner decision, 2026-11-10) | All admin replies | AC-6 | 3, C-2, G-02 | Implemented |
| Session/login (framework group 1) | Glean 1a–1d; Claude 1a–1b | AC-8 | E-02 | Implemented |
| Indexed vs. live and excluded (framework group 3) | Glean 3b; `references/atlassian-at-ahead.md` | AC-5, AC-17 | A-01 | Implemented |
| Works in chat, fails in agent (framework group 4) | Glean cause 4 | AC-16 | P-02 | Implemented |
| Connector not set up (framework group 5) | Glean cause 5; Claude cause 5 | AC-9 | E-03 | Implemented |
| SSO (framework group 6) | Service Desk → IAM in both | AC-10 | E-04 | Implemented |
| Claude Enterprise Atlassian connection (owner, 2026-11-10) | Claude adapter | AC-18, AC-19 | C-1, C-2, C-3, P-01 | Implemented |
| Register is the source of truth | Step 7 / references | AC-12 | 1, S-01 | Implemented |
| Write safety | Write gate; guardrail model | AC-4, AC-14 | 1, G-02, C-3 | Implemented |
| Prompt-injection resistance | Untrusted retrieved content | AC-13 | S-01 | Implemented |
| Non-trigger precision | Trigger contract | AC-11 | 4 | Implemented |
| Package and distribution integrity | `scripts/validate_package.py`, `scripts/build_distributions.py` | AC-15, AC-20 | R-01, A-02 | Passing locally (2026-11-10) |
| Org-wide release | eTech org-wide review | — | — | Approved 2026-11-10; runtime evals open |

## Design decisions

1. **Glean Skill, not Agent.** The value is routing and diagnosis inside existing chats and agents.
2. **Jira Actions families by default in Glean.** User-attributed, permission-faithful writes. The service credential is a restricted, agent-only exception.
3. **Service Desk, not names.** Every admin-only fix routes to a Service Desk ticket, so the skill doesn't go stale.
4. **Paired adapters.** Claude reads Atlassian live through Rovo MCP, so Glean-only causes are excluded there.
