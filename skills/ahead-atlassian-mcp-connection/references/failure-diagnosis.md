# Atlassian Failure Diagnosis (Glean): one likely cause, not a list

Load this file before writing any reply about a failed, empty, partial, or non-executed Jira or Confluence request in Glean.

## Rule

Check the signals in the order below and stop at the first match. Reply with one named cause, one next step, and at most one fallback. Don't read this catalog to the user, and never list three or more possible causes.

If the fix needs an admin, say so in the first sentence, tell the user to raise a **Service Desk ticket** describing the specific fix, and say retrying won't help. Don't name individual admins.

## Decision order

### 1. Session or login

**1a. Tools never ran.** Glean wrote out the JQL or the steps instead of doing the action, and no Connect prompt appeared.
- Cause: connected-app actions load only in Thinking mode. Fast mode, and Adaptive mode when it stays on the fast path, never load them.
- Reply: "Glean didn't run the Jira action because chat is in Fast mode. Switch the reasoning mode to Thinking and run the request again."

**1b. Never authorized / skipped setup.** The tool reports it isn't connected, a Connect prompt appears, or Settings → Connectors shows "authorization needed."
- Cause: the first-time authorization wasn't finished. Jira has several Authorize → Accept steps; Confluence needs a second Authorize after the first.
- Reply: "Jira (or Confluence) isn't fully authorized for your account yet. In Glean, go to Settings → Connectors, open Jira, and complete every Authorize → Accept step until it shows a green check. Pick the ahead-etech instance (or ahd-foundry for Foundry Confluence). Then I'll retry."

**1c. Expired or rejected token.** An auth or token error, repeated reconnect prompts, or "session expired."
- Reply: "Your Jira connection expired. Click Connect when prompted, or go to Settings → Connectors → Jira → ⋯ → Disconnect, then reconnect. Then start a new chat and try again."
- Fallback only if that fails: clear the browser cache. If it still fails, raise a Service Desk ticket.

**1d. Everyone sees authorization errors on Connect.**
- Cause: the Atlassian site hasn't approved Glean's app. Admin-only.
- Reply: "This needs an Atlassian site admin to approve Glean's Jira app, so reconnecting won't fix it. Raise a Service Desk ticket saying Jira authorization fails for all users in Glean."

### 2. Permissions or data visibility (admin needed)

**Signal:** the user can read the issue in Glean, but edit, comment, transition, or assign fails or is denied, even though the same action works in Jira directly. Also: Get issue edit metadata doesn't return the field, or Get transitions doesn't return the target status.
- Cause: the user's Jira permissions in Glean sync from the Atlassian product access group configured for Glean (eTech Engineering-All Dept). Either the user isn't in that group correctly, or the sync is behind. A missing Edit Issue project permission produces the same symptom. Write-back is governed separately from read and index access.
- Reply: "You can read this issue in Glean, but Glean can't edit or comment for you because your Jira access hasn't synced to Glean. This needs an admin, so retrying won't fix it. Raise a Service Desk ticket asking to confirm you're in the Glean product access group (eTech Engineering-All Dept) and have Edit Issue permission on [project]."
- Fallback: none. Don't suggest the service credential as a workaround.

**Signal:** a restricted project or page is denied or missing, and the user doesn't have access in Jira or Confluence either.
- Reply: "You don't have access to [project/space] in Jira (or Confluence) itself, so Glean can't show it. Request access from the project or space owner."

### 3. Indexed vs. live data, and completeness

**3a. Incomplete pagination.** Run JQL returns `fetchedIssuesCount` lower than `totalCount`, a `nextPageToken` remains, or the connector says pagination is incomplete.
- Cause: one call returns one page (50 issues observed), and the result set is bigger.
- Action: page with `next_page_token` up to 10 pages. If you still stop short, reply: "These results are incomplete: [fetched] of [total] issues. Full results: [CSV link]. Or I can narrow the search (last 30 days, open only, one project)."
- Don't present partial results as the full answer.

**3b. Not found in search, but the user believes it exists.**
- Pick the one cause the evidence supports:
  - the project is restricted or redlisted from Glean;
  - the page is archived;
  - the content is an inline Confluence comment (not indexed);
  - it's a recent comment-only change not yet crawled;
  - it's a custom Confluence type (database or whiteboard);
  - it's a Foundry (`ahd-foundry`) page, which isn't indexed and needs live Confluence Tools;
  - a Confluence Search content call missed because it matches titles only.
- Reply: "I couldn't find that through search. [One cause.] If you have the issue key or page URL, share it and I'll read it directly."
- If a direct live read also returns nothing and the user has access in Atlassian, treat it as cause 2.

### 4. Works in chat, fails in an agent

**Signal:** the same request works in chat but the agent fails, uses the wrong tool, or Run agent is disabled.

| Cause | Fix |
|---|---|
| Wrong tool family: the agent used Atlassian MCP service-credential tools | Add Jira Actions Run JQL and the needed Jira Extension Actions, and name them in the instructions |
| Jira tools missing in Agent Builder | Raise a Service Desk ticket to enable them for agents |
| Run agent disabled | Click Connect for each listed action on the launch screen |
| Partial data only in the agent | Static workflow steps don't page. Switch to adaptive or plan-and-execute, or narrow the JQL |
| Tight instructions or guardrails | Loosen the agent's source or tool restrictions |

### 5. Connector not set up at AHEAD

**Signal:** any Atlassian site other than `ahead-etech` (Jira and Confluence) or `ahd-foundry` (Confluence, live tools only), Jira/Confluence Data Center or Server, a client's Atlassian instance, or Foundry *Jira* (no Glean Jira tools for `ahd-foundry`).
- Reply: "Glean at AHEAD isn't connected to [site/product], so I can't reach it here. If there's a business need, submit a request through the New Connector Request Process."
- Reference: [New Connector Request Process](https://ahead-etech.atlassian.net/wiki/spaces/Glean/pages/1844281357)

### 6. SSO

**Signal:** the user can't sign in to Atlassian at all, SSO or Okta fails during the Authorize step, or an identity error appears before Jira.
- Reply: "This is a sign-in problem with your AHEAD identity, not a Glean or Jira permission. Raise a Service Desk ticket for Identity and Access Management."

### 7. Anything else

Timeouts, 5xx errors, or an error that doesn't match a cause above: "The Jira (or Confluence) call failed ([error, only if useful]). I can retry once, or you can make the change directly in Jira." If it keeps happening, try the Glean Support Assistant first, then raise a Service Desk ticket. Don't force the error into causes 1–6.

## Escalation routes

| Need | Route |
|---|---|
| Self-help | Glean Support Assistant agent |
| Access, provisioning, group membership, permission sync, tool enablement, connector or agent configuration | Service Desk ticket (triaged to the Atlassian admin or Glean Core Team) |
| SSO / identity | Service Desk ticket for Identity and Access Management |
| New Atlassian source or scope | New Connector Request Process |

For current owners, link the [Glean Connector & MCP Integration Documentation](https://ahead-etech.atlassian.net/wiki/spaces/Glean/pages/2393112579) register instead of naming a person.

## Sources

- [Incident & Escalation SOP](https://ahead-etech.atlassian.net/wiki/spaces/Glean/pages/1881735169) · [JIRA connector page](https://ahead-etech.atlassian.net/wiki/spaces/Glean/pages/1843888154) · [Never Index Categories & Exceptions](https://ahead-etech.atlassian.net/wiki/spaces/Glean/pages/1843691525)
- [Troubleshooting tools authentication](https://docs.glean.com/troubleshooting/tools-authentication) · [Search Jira with JQL](https://docs.glean.com/tools/connector/jira/search-jql)
- Live Glean session: Run JQL paging fields and Confluence title-only search behavior, 2026-11-10
- Isha Mehta / Grace Gallagher connector skills discussion, 2026-10-27
