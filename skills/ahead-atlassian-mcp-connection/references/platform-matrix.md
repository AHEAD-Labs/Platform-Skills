# Platform Matrix

## Shared contract

`SPEC.md` is the single contract for both adapters: the same triggers, non-goals, write gate, one-cause diagnosis rule, Service Desk routing, guardrail model, and output templates.

## Glean vs. Claude

| Capability | Glean adapter (root `SKILL.md`) | Claude adapter (`adapters/claude/SKILL.md`) | Parity requirement |
|---|---|---|---|
| Atlassian access | Glean index plus Glean tools: Jira Actions (Run JQL), Jira Extension Actions, Confluence Actions (`ahead-etech`), Confluence Tools (`ahd-foundry`) | Claude Enterprise Atlassian connection (Rovo MCP, OAuth 2.1) | Same intents route to equivalent tools |
| Site selection | Tool family names the site | `getAccessibleAtlassianResources` → cloudId | Never invent a site or cloudId |
| Structured query | Run JQL; `next_page_token`; CSV link | `searchJiraIssuesUsingJql`; next-page token | Page up to 10 pages or label partial (AC-7) |
| Jira write | Jira Extension Actions behind the Glean approval card | `editJiraIssue`, `transitionJiraIssue`, `addOrEditJiraIssueComment` after an explicit chat "yes" | Read → check → preview → confirm (AC-4) |
| Deferred tools | n/a | `discover` → `executeRead` / `executeWrite` | Don't declare a tool unsupported before discovery (AC-18) |
| Service identity | Atlassian MCP service credential, agent-only, restricted | Not used | Never a permissions workaround (AC-14) |
| Session/login causes | Fast mode, skipped Authorize steps, expired token, site approval | Connector not connected or off, stale token | One cause (AC-5) |
| Permission causes | Product access group sync / Edit Issue permission | User's Atlassian permission, disabled write group, IP or domain allowlist | Service Desk route (AC-6); no Glean-only causes in Claude (AC-19) |
| Index causes | Restricted or redlisted, archived, inline comments, title-only search, Foundry not indexed | Not applicable (live reads) | — |
| SSO | Service Desk → IAM | Service Desk → IAM | Same |
| Install | Glean Settings → Skills (org-wide catalog) | Claude organization skills upload | Same version 1.0.0 |

## Surface parity: Glean chat vs. Glean agent

| Capability | Glean chat | Glean agent | Parity requirement |
|---|---|---|---|
| Tool routing | Jira Actions families / Confluence tools | Same; tools must be attached | Same tool family (P-02) |
| Tool loading | Thinking mode only | Tools listed on the agent | Fast-mode cause is chat-only |
| Authorization | Connect prompt on first use | Run agent disabled until all actions are connected | Same diagnosis category |
| Paging | Adaptive paging | Static workflow steps don't page | Agent-only cause is labeled cause 4 |
| Service credential | Not available | Only if the agent is explicitly approved | Never a workaround |

## Design decision

A paired behavioral contract, not byte-for-byte parity. Glean and Claude reach the same Atlassian sites through different tool surfaces and fail in different ways. Each adapter has its own routing and diagnosis reference, while the user-visible contract stays the same.
