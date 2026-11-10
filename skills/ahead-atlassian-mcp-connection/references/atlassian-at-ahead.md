# Atlassian at AHEAD: Quick Reference

Background facts the diagnosis relies on, for both adapters. For status, audience, and owners, the [Glean Connector & MCP Integration Documentation](https://ahead-etech.atlassian.net/wiki/spaces/Glean/pages/2393112579) register is the source of truth. Re-check it for anything that changes.

## Atlassian sites

| Site | Products | In the Glean index | Live tools in Glean | Notes |
|---|---|---|---|---|
| `ahead-etech.atlassian.net` | eTech Engineering Jira and Confluence (Cloud) | Yes | Jira Actions, Jira Extension Actions, Confluence Actions | Scoped by the eTech Engineering-All Dept product access group |
| `ahd-foundry.atlassian.net` | AHEAD Foundry Confluence | No | Confluence Tools | Read and write live by page ID; Foundry Jira has no Glean tools |
| Any other site, Data Center, or Server | — | No | No | Use the New Connector Request Process |

In Claude, the Atlassian connection lists whatever sites the user's Atlassian account can access (via `getAccessibleAtlassianResources`).

## What's indexed (ahead-etech)

- Jira: projects, issues, comments, dashboards, filters; users, groups, and memberships.
- Confluence: pages (with hierarchy), blog posts, spaces and folders, footer comments, attachment metadata.

## What isn't indexed

- Restricted Jira projects or issues the Glean app can't access (issue security schemes), and redlisted projects.
- Restricted Confluence pages or spaces, unless the Glean app is granted access.
- Confluence inline comments, archived pages, and custom content types (databases, whiteboards, smart links).
- Very recent comment-only changes may be missing until the next full crawl.

## Read vs. write

- Glean indexing and read scope come from the connector and group sync.
- Writes (Glean Jira Extension Actions, Confluence tools, Claude Atlassian connector) are governed by per-user OAuth and Atlassian project or space permissions.

## First-time authorization in Glean

Glean → profile → Settings → Connectors:

- **Confluence:** Authorize → choose the instance → toggle → AHEAD email → Accept. Then Authorize → Accept again until it shows a green check.
- **Jira:** three Authorize → Accept steps (first, middle, last) until done.

"1 authorization needed" means setup isn't finished.

## Limits that cause partial results

- Glean Run JQL: one page per call (50 issues observed on 2026-11-10), with `totalCount`, `fetchedIssuesCount`, `nextPageToken`, and a CSV download link.
- Glean JQL documented limits: up to 500 results per search, a response cap of about 1 MB, and JQL up to 2,000 characters. Agent runs have a tool-call budget; static workflow steps don't page.
- Confluence Search content (Glean) matches page titles only.

## Sources

- [JIRA connector page](https://ahead-etech.atlassian.net/wiki/spaces/Glean/pages/1843888154) · [Never Index Categories & Exceptions](https://ahead-etech.atlassian.net/wiki/spaces/Glean/pages/1843691525) · [Glean Connector Configuration for Jira and Confluence](https://ahead-etech.atlassian.net/wiki/spaces/ETR/pages/2088108087)
- [Search Jira with JQL](https://docs.glean.com/tools/connector/jira/search-jql)
- Live Glean session tool inventory, 2026-11-10
