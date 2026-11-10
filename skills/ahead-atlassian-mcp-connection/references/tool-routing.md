# Tool Routing: Jira & Confluence in Glean (AHEAD)

Load this file when choosing which Atlassian tool to call, or when helping someone design a Glean agent that uses Jira or Confluence.

## AHEAD tool inventory (observed in a live Glean session, 2026-11-10)

| Family (as shown in Glean) | Site | Tools | Identity | Use for |
|---|---|---|---|---|
| **Indexed search/read** | `ahead-etech` Jira and Confluence | Glean search, document read | User's synced source permissions | Finding and summarizing issues, pages, comments |
| **Jira Actions** | `ahead-etech` | Run JQL | Per-user OAuth | All lists, filters, counts, dashboard data |
| **Jira Extension Actions** | `ahead-etech` | Get issue, Get issue edit metadata, Get transitions, Get fields, Get create metadata (issue type fields), Get issue types, Get project, Get all projects, List boards, List issue comments, Get attachment, Find users, Get current user, JQL autocomplete suggestions. **Writes (approval card):** Edit issue, Transition issue, Add comment, Update comment, Assign issue, Add watcher, Create issue, Create project | Per-user OAuth; attributed to the user | All single-issue reads and all Jira writes |
| **Confluence Actions** | `ahead-etech` | Search content (title match only), Get page by ID, Get pages, Get child pages, Get spaces, Get blog posts, Get current user. **Writes:** Create/Update page, Create/Update blog post, Add content label, Create space | Per-user OAuth | eTech Engineering Confluence reads by ID and writes |
| **Confluence Tools** | `ahd-foundry` (AHEAD Foundry) | Same read set. **Writes:** Create/Update page, Create/Update blog post, Add content label, Create inline comment, Create space | Per-user OAuth | Foundry Confluence pages. Live tools only; not in the Glean index |
| **Atlassian MCP (Service Account)** | Rovo MCP via a service-account API key | Atlassian's hosted MCP tools | Shared service account; actions show under its name | Agents deliberately built and approved to act as a shared identity. **Agent-only:** not available in chat |

Tool display names can change when admins update tool sets. Always use the tools actually loaded in the session, matched to the intents below. Never invent a tool name.

## Decision rules

1. **Known key or URL, read only** → Jira Extension Actions **Get issue**, or Confluence **Get page by ID** for the page's site. Don't run JQL for one ticket.
2. **Topic question** ("what do we know about X") → Glean search over indexed content first. Confluence **Search content** matches titles only, so use it to find a page by title, not by body text.
3. **List, filter, count, or dashboard data** → Jira Actions **Run JQL**. Keep the JQL tight (project, status, assignee, date range). Page with `next_page_token` (see below).
4. **Any Jira write** (edit fields, comment, transition, assign, watcher, create issue) → Jira Extension Actions.
5. **Any Confluence write** → Confluence Actions (`ahead-etech`) or Confluence Tools (`ahd-foundry`), matching the page's site.
6. **Both a Jira Actions family and Atlassian MCP service-credential tools are loaded in an agent** → use the Jira Actions families, unless the agent's instructions explicitly say to act as the service account.
7. **Create project / Create space** → don't. These are admin-level actions; route to a Service Desk ticket.
8. **Tools aren't loaded at all** (Glean writes out the JQL or the steps instead of acting) → reasoning mode or agent configuration. See `failure-diagnosis.md` causes 1a and 4.

## JQL pagination

Run JQL returns one page per call. On 2026-11-10, a query with 154 matches returned 50 issues on the first page, plus a `nextPageToken` and a CSV download link. Each response has:

- `totalCount`: all matching issues.
- `fetchedIssuesCount`: issues on this page.
- `nextPageToken`: present while more pages remain. Pass it as `next_page_token`.
- `csvFile.downloadLink`: CSV of the results.

Rules:

- Page until `nextPageToken` is absent, up to 10 pages per request.
- If you stop early, report "[fetched] of [total]" and give the CSV link.
- Static workflow agent steps don't page automatically. Use adaptive or plan-and-execute agents for full sets.

## Why Jira Actions over the service credential

- Jira Actions families run as the user, so permissions and the audit trail match what the user can do in Jira.
- The service credential acts as a shared account. Every action shows up under its name, and its access is whatever was granted to that account.
- Field example: an agent querying Jira to update a dashboard picked the Atlassian MCP service-credential tools first. It only worked after the user added the Jira Actions tools and told it to use them.

## Agent-builder guidance

- Attach **Jira Actions: Run JQL** for queries and only the **Jira Extension Actions** you need for updates (Agent Builder → Tools → By connector).
- In the agent instructions, say: "Use Jira Actions Run JQL to query issues and Jira Extension Actions to update them. Do not use Atlassian MCP service-credential tools."
- Don't attach the Atlassian service credential unless the agent must act as a shared, non-human identity and an admin has approved it.
- Every user who runs the agent must connect their own Jira account. Run agent stays disabled until every listed action is connected.
- Comments and descriptions use Atlassian Document Format (ADF).
- Transitions can only set fields on the transition screen. Use Edit issue for other fields after the transition.

## Sources

- Live Glean session tool inventory and Run JQL response, 2026-11-10
- [Jira tools](https://docs.glean.com/tools/connector/jira) · [Jira tools setup](https://docs.glean.com/administration/tools/setup-tools/jira-tools-setup) · [Jira tools: Extension or legacy?](https://docs.glean.com/administration/tools/managing-tools/jira-extension-tools-adf)
- [Search Jira with JQL](https://docs.glean.com/tools/connector/jira/search-jql) · [Confluence tools](https://docs.glean.com/tools/connector/confluence/confluence-index)
- [Set up Atlassian service credential](https://docs.glean.com/administration/agent-identity/atlassian)
- Isha Mehta, field example (Teams, 2026-10-30)
