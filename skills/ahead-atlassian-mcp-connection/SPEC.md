# SPEC — Atlassian MCP Connection

## Skill identity

- **Name:** atlassian-mcp-connection
- **Version:** 1.0.0
- **Owner:** Grace Gallagher (grace.gallagher@ahead.com)
- **Team:** Solutions Engineering
- **Target platform(s):** Glean (Glean Skill) and Claude (Claude skill). Paired package with one shared contract.
- **Sensitivity:** Internal
- **Publication state:** Approved, for the org-wide Skills Catalogue (Glean) and org-wide Claude install
- **Approver / approval date:** AHEAD eTech team, org-wide skill review (Grace Gallagher, eTech reviewer), 2026-11-10

### Review log

| Date | Reviewer | Scope | Outcome |
|---|---|---|---|
| 2026-10-30 | Isha Mehta and Grace Gallagher (sync call) | Solution approach: per-connector skill, shared framework, Jira Actions over the service credential | Agreed. The owner waived a separate Glean admin review of the package on 2026-11-10 on the basis of this agreement. |
| 2026-11-10 | Grace Gallagher (owner) | Platform verification: live Glean tool inventory, Run JQL paging, service-credential exposure | Verified in a live Glean session (see §6) |
| 2026-11-10 | AHEAD eTech team, org-wide skill review (Grace Gallagher) | Contract, Glean and Claude adapters, guardrails, references, validator, distributions | Approved for org-wide release at 1.0.0. Approval doesn't substitute for runtime evaluation evidence. |

**Governance note:** the owner and the eTech reviewer are the same person for this release. This is recorded for transparency.

## 1. Purpose and user outcome

**Given:** a natural-language Jira or Confluence request in Glean (chat or agent) or Claude, optionally with an issue key, page URL, or error.

**Produce:** a correctly routed tool call with a confirmed result; a labeled partial result; or a one-cause failure diagnosis with one next step, with admin-only fixes routed to a Service Desk ticket.

**For:** AHEAD Glean and Claude users, and Glean agent builders, working with AHEAD's Atlassian sites.

**Why:** Field tickets show four repeating Atlassian problems:

1. Users can search issues but can't edit or comment through Glean, even though they can in Jira directly, because of product access group sync.
2. "Pagination incomplete" cuts results short.
3. An agent used Atlassian MCP service-credential tools instead of Jira Actions, and worked only after the user added Jira Actions and told it to use them.
4. On failure, the assistant lists four or five causes instead of one.

**User outcomes:**

- Jira and Confluence requests reach the right tool the first time.
- Admin-only failures are named and routed to a Service Desk ticket.
- Partial results are labeled partial.
- Agent builders know which Jira tools to attach.

## 2. Trigger and non-trigger conditions

### Triggers

- Find, read, summarize, list, filter, or count Jira issues or Confluence pages.
- Edit, comment on, transition, assign, watch, or create Jira issues. Create or update Confluence pages.
- Atlassian failure reports in Glean or Claude.
- Questions about which Jira or Confluence tools a Glean agent should use.

### File/context signals

- `ahead-etech.atlassian.net` or `ahd-foundry.atlassian.net` URLs; an issue key confirmed as Jira by search or a tool result.
- A Jira, Confluence, or Atlassian connector error or partial result in the conversation.

### Does not trigger when

- The ticket lives in ServiceNow, Monday.com, GitHub Issues, or Zendesk.
- The request is for Atlassian, Glean, or Claude admin changes.
- The request is to change Glean indexing or connector scope.
- Asking which tool to use. That is never a valid clarifying question; only intent ambiguity is.

## 3. Inputs

| Input | Format/schema | Required? | Provenance | Sensitivity | Missing-input behavior |
|---|---|---:|---|---|---|
| User request | Natural language | Yes | Current message | User-provided | Ask one intent question |
| Issue key / page URL or ID | `ABC-123`, Atlassian URL, page ID | Writes: yes | User text, URL, tool result, or search | Internal | Resolve via search or JQL. Never guess or increment |
| Site | `ahead-etech` or `ahd-foundry`; Claude cloudId | Yes | URL, context, or `getAccessibleAtlassianResources` (Claude) | Internal | Default `ahead-etech`. Other sites go to diagnosis cause 5 |
| Change to make | Field values, comment, status | Writes only | User or conversation | Internal | Ask. Don't fill in values |
| Error or symptom | Tool error, empty or partial result, description | Troubleshoot only | Tool output or user | Internal | Run the failing call once or ask |
| Surface | Glean chat, Glean agent, or Claude | No | Context | Internal | Infer from the runtime |

## 4. Outputs

- **Type:** chat response; optional tool write after confirmation.
- **Name/pattern:** the `SKILL.md` Output Format templates (write preview, successful write, partial results, failure diagnosis, agent design guidance). The same templates are used on both platforms.
- **Required structure:**
  - Failure replies have exactly one cause line, one "Next step" line, and at most one fallback line.
  - Partial results give fetched and total counts, plus the CSV link in Glean.
- **Delivery channel:** Glean chat or agent response; Claude chat response.
- **Failure behavior:** never report success without a tool-returned result. Never report partial results as complete.
- **Human review required?** Yes, for every write. Glean shows an approval card; Claude requires an explicit chat confirmation plus its tool-permission prompt. Writes change shared Atlassian records attributed to the user.
- **Distribution artifacts:**
  - `dist/atlassian-mcp-connection-glean-1.0.0.zip`
  - `dist/atlassian-mcp-connection-claude-1.0.0.zip`
  - Both are built and validated by `scripts/build_distributions.py`.

## 5. Non-goals and out-of-scope handling

This capability does not:

- perform Atlassian, Glean, or Claude administration (groups, permission schemes, Rovo MCP domain or IP allowlists, connector enablement, Create project or space);
- change Glean indexing scope, redlisting, or connector configuration;
- use the Atlassian MCP service credential, or anyone else's credentials, to work around a user's missing permission;
- handle non-Atlassian ticket systems;
- replace a loaded Jira create/update skill's field-metadata and ADF rules;
- name individual admins, or quote owners or status from memory.

When asked for an out-of-scope result, it should say in one sentence that it can't do this, point to a Service Desk ticket (or the New Connector Request Process for new sources), and stop. It should not attempt a workaround.

## 6. Behavior and platform design

- **Capability type:** paired package. A Glean Skill (root `SKILL.md`) and a Claude skill (`adapters/claude/SKILL.md`) share this contract. In Glean it is a Skill, not an Agent: routing and diagnosis knowledge used inside any chat or agent, with no trigger form, schedule, or fixed step graph.
- **Glean adapter tools (allow-list), verified in a live Glean session on 2026-11-10:**
  - Glean search and document read (indexed `ahead-etech` Jira and Confluence).
  - **Jira Actions** (`ahead-etech`): Run JQL. Paging: one page per call (50 observed), with `totalCount`, `fetchedIssuesCount`, `nextPageToken`, and a CSV download link.
  - **Jira Extension Actions** (`ahead-etech`): Get issue, Get issue edit metadata, Get transitions, Get fields, Get create metadata, Get issue types, Get project, Get all projects, List boards, List issue comments, Get attachment, Find users, Get current user. Writes behind the approval card: Edit issue, Transition issue, Add comment, Update comment, Assign issue, Add watcher, Create issue. Create project is excluded by guardrail.
  - **Confluence Actions** (`ahead-etech`) and **Confluence Tools** (`ahd-foundry`): Search content (title-only), Get page by ID, Get pages, Get child pages, Get spaces, Get blog posts. Writes: Create/Update page and blog post, Add content label; Create inline comment on `ahd-foundry`. Create space is excluded by guardrail.
  - **Atlassian MCP (Service Account) credential:** agent-only. It isn't in the chat tool list (verified 2026-11-10) and is attached per agent in the agent's Tools tab. Field evidence (2026-10-30) shows it is attached to at least one AHEAD agent. Allowed only in agents deliberately built and approved for a shared identity.
- **Claude adapter tools:** Claude Enterprise's Atlassian connection (Atlassian Rovo MCP, OAuth 2.1, per-user permissions). Every call starts with `getAccessibleAtlassianResources` to get the cloudId. Primary tools: `getJiraIssue`, `searchJiraIssuesUsingJql`, `editJiraIssue`, `transitionJiraIssue`, `addOrEditJiraIssueComment`, `createJiraIssue`, `getConfluenceContent`, `createConfluenceContent`, `updateConfluenceContent`, `search`. Deferred tools are reached through `discover` → `executeRead` / `executeWrite`. Destructive and permission tools are excluded unless the user explicitly asks and confirms.
- **Workflow or decision graph (both platforms):**
  1. Classify intent.
  2. Resolve the site and target. Never guess.
  3. Route using the adapter's routing reference.
  4. For queries: page up to 10 pages, or label partial.
  5. For writes: read → check allowed fields or transitions → preview → user confirms → write → report returned fields.
  6. On failure, empty, or partial results: use the adapter's diagnosis reference → one cause → one next step → optional single fallback.
  7. Point owner and status questions to the register; admin fixes go to a Service Desk ticket.
- **Deterministic steps:** routing tables; diagnosis decision order (first match wins); paging bound; output templates; distribution build and validation.
- **Reasoning steps:** intent classification; matching a signal to a cause; drafting JQL.
- **Memory/context policy:** no persistent memory. Current conversation only.
- **Identity and confirmation:** per-user OAuth on both platforms. Glean approval card or Claude explicit confirmation before every write.
- **Bounded execution:** at most one retry, after a user-confirmed fix; at most 10 JQL pages per request.
- **Kill switch / rollback:** unpublish the skill in Glean skill settings or remove it from Claude organization skills. Roll back by reinstalling the prior distribution zip.

## 7. Guardrails and failure modes

### Guardrail model

| Category | Soft guardrail | Hard guardrail |
|---|---|---|
| **Trigger** | Adjacent request (e.g., ServiceNow ticket): confirm the system with search before routing. | Don't route non-Atlassian tickets to Atlassian tools. Don't act on admin requests. |
| **Content** | Label partial results with fetched and total counts and the CSV link or a paging offer. | Don't invent keys, IDs, cloudIds, field values, tool names, error codes, or owners. Don't name admins. |
| **Action** | Preview the change and wait for confirmation. | No write without confirmation. No credential workaround. No Create project or space, destructive, or permission-changing actions without explicit request and confirmation. |
| **Artifact** | If a template field can't be filled (no link returned), say which field is missing. | Never report success without a tool-returned result. Never list three or more causes. Distributions that fail validation are not shipped. |
| **Governance** | Record platform facts that may drift (tool display names, Rovo MCP versions) as non-blocking open items. | Don't claim runtime-tested status while evaluations are `not_run`. |

### Failure modes

| Risk/failure mode | Prevention | Detection | Recovery/escalation |
|---|---|---|---|
| Wrong tool family (service credential for user work) | Routing table and field rule | Tool trace shows the service credential for a user write | Switch to the Jira Actions families; add them to the agent |
| Multi-cause hedged reply | Decision order, first match wins | Reply has 3+ causes | Rewrite to one cause and one next step |
| Retry loop on an admin-only cause | Admin wording says retrying won't help | User retries | Service Desk ticket |
| Partial results presented as complete | Paging rule and Partial template | `fetchedIssuesCount` < `totalCount`, or a next-page token remains | Page up to the bound, or label partial with the CSV link |
| Unconfirmed write | Write gate | Write call without prior confirmation | Hard stop. Preview and request confirmation |
| Prompt injection in issue or page content | Retrieved content is untrusted | Retrieved text contains instructions | Ignore it and continue the user's task |
| Invented key or cloudId | Resolve via search or `getAccessibleAtlassianResources` | Value not in any tool result | Search or ask |

## 8. Acceptance criteria

| ID | Criterion | Evidence | Test case |
|---|---|---|---|
| AC-1 | Intent is classified before any tool call, and the user is never asked which tool or MCP to use. | Runtime trace and response | 1, 2, C-1 |
| AC-2 | In Glean, JQL uses Jira Actions Run JQL and Jira writes use Jira Extension Actions, not the Atlassian MCP service credential, unless the agent is explicitly approved for a service identity. | Tool trace | 1, 2, P-02 |
| AC-3 | Glean Confluence writes use Confluence Actions (`ahead-etech`) or Confluence Tools (`ahd-foundry`), matching the page's site. | Tool trace | 2 |
| AC-4 | Every write is preceded by a target read, a preview, and user confirmation. | Tool trace order | 1, G-02, C-1 |
| AC-5 | Every failure reply names exactly one cause, one next step, and at most one fallback. | Response | 3, E-02, E-03, A-01, C-2 |
| AC-6 | Admin-only causes say an admin is needed, point to a Service Desk ticket, say retrying won't help, and don't name individual admins. | Response | 3, C-2 |
| AC-7 | Query results are paged up to 10 pages; anything less than the total is labeled incomplete with fetched and total counts (and the CSV link in Glean). | Trace and response | G-01 |
| AC-8 | A Glean Fast-mode "steps instead of action" signal is diagnosed as reasoning mode, not permissions. | Response | E-02 |
| AC-9 | Atlassian sites other than `ahead-etech` and `ahd-foundry` (Confluence), or Data Center/Server, are diagnosed as not connected, with the New Connector Request Process. | Response | E-03 |
| AC-10 | Atlassian or Okta sign-in failure is routed to a Service Desk ticket for Identity and Access Management. | Response | E-04 |
| AC-11 | Non-Atlassian ticket requests don't invoke Atlassian tools. | Tool trace | 4 |
| AC-12 | No invented keys, IDs, cloudIds, tool names, error codes, or owners; owner questions point to the register. | Response and trace | 1, S-01, C-1 |
| AC-13 | Instructions embedded in retrieved Jira or Confluence content are ignored. | Tool trace | S-01 |
| AC-14 | No credential workaround, and no Create project/space or destructive action without explicit request and confirmation. | Response and trace | G-02 |
| AC-15 | `scripts/validate_package.py` passes its structural checks. | Validator output | R-01 |
| AC-16 | The same golden request yields the same tool family and diagnosis category in Glean chat and a Glean agent, and the same contract (one cause, write gate, templates) in Glean and Claude. | Paired traces | P-01, P-02 |
| AC-17 | Failure and partial-result replies conform to the Output Format templates. | Response vs. template | A-01, G-01 |
| AC-18 | In Claude, the cloudId comes from `getAccessibleAtlassianResources` or the site URL, and deferred tools are reached through `discover` instead of being declared unsupported. | Claude trace | C-1, C-3 |
| AC-19 | In Claude, the diagnosis uses Claude causes (connector connection, Rovo MCP domain or IP allowlist, Atlassian permissions) and never cites Glean-only causes (index lag, product access group sync, Fast mode). | Claude response | C-2 |
| AC-20 | `scripts/build_distributions.py` produces Glean and Claude zips with `SKILL.md` at the archive root, valid quoted frontmatter, descriptions within 1,000 characters (Glean) and 1,024 characters (Claude), and every referenced file present. | Build output | A-02 |

## 9. Golden examples and eval plan

- **Happy path 1:** Glean comment on a named Jira issue (1).
- **Happy path 2:** Glean agent JQL plus a Confluence page update (2).
- **Edge cases:** read OK but edit denied (3); Fast mode (E-02); non-AHEAD site (E-03); SSO (E-04).
- **Non-trigger:** ServiceNow request lookup (4).
- **Guardrail modes:** paging (G-01, soft); service-credential bypass request (G-02, hard).
- **Platform parity:** Glean vs. Claude contract (P-01); Glean chat vs. Glean agent (P-02).
- **Claude-specific:** Claude comment with cloudId resolution (C-1); IP allowlist block (C-2); deferred transition tool (C-3).
- **Security:** prompt injection in issue content (S-01).
- **Artifact and validator:** template conformance (A-01); distribution build (A-02); package integrity (R-01).

All cases are in `evals/evals.json`. Record runs with `scripts/record_eval_run.py`.

## 10. Dependencies and resources

- **Glean adapter:** root `SKILL.md`, `references/tool-routing.md`, `references/failure-diagnosis.md`.
- **Claude adapter:** `adapters/claude/SKILL.md`, `adapters/claude/references/claude-tool-routing.md`, `adapters/claude/references/claude-failure-diagnosis.md`.
- **Shared:** `references/atlassian-at-ahead.md`, `references/platform-matrix.md`, `references/comparison-matrix.md`, `evals/evals.json`.
- **Scripts:** `scripts/validate_package.py`, `scripts/record_eval_run.py`, `scripts/build_distributions.py`.
- **Current platform references:**
  - Glean docs: Jira tools, Jira tools setup, Jira Extension vs. legacy, Search Jira with JQL, Confluence tools, Atlassian service credential, Troubleshooting tools authentication.
  - Atlassian docs: Rovo MCP supported tools, getting started, control MCP server settings, OAuth consent and invalid-token knowledge-base articles.
  - AHEAD sources: Glean Connector & MCP Integration Documentation register, JIRA connector page, Never Index Categories & Exceptions, Glean Connector Configuration for Jira and Confluence, Incident & Escalation SOP, New Connector Request Process.

## 11. Release and governance

- **Versioning rule:** semantic versioning. Behavior changes bump minor; wording and reference fixes bump patch. Keep `SKILL.md`, `adapters/claude/SKILL.md`, `SPEC.md`, and `evals/evals.json` versions identical.
- **Owner:** Grace Gallagher, Solutions Engineering.
- **Sensitivity:** Internal.
- **Required reviews:** AHEAD eTech org-wide skill review, completed 2026-11-10. A separate Glean admin review was waived by the owner (see the review log).
- **Rollback/deprecation:** unpublish in Glean skill settings or remove from Claude organization skills, then reinstall the prior distribution. Deprecate if native routing makes the skill redundant.
- **Observability/telemetry:** Atlassian-category Service Desk ticket volume, compared before and after release.
- **Resolved 2026-11-10 (owner):**
  - The Jira tool set at AHEAD is Jira Actions (Run JQL) plus Jira Extension Actions (all issue-level reads and writes) on `ahead-etech`, verified in a live Glean session.
  - Confluence is available on `ahead-etech` (Confluence Actions) and `ahd-foundry` (Confluence Tools).
  - Glean's "pagination incomplete" behavior is Run JQL paging: one page per call, with `nextPageToken` and `fetchedIssuesCount` < `totalCount`. Handled by bounded paging and the Partial template.
  - The Atlassian MCP (Service Account) credential is enabled as an agent-attachable credential, absent from chat.
  - Replies point to a Service Desk ticket for admin-only fixes.
  - The separate Glean admin review was waived.
  - Claude Enterprise has the Atlassian connection; the Claude adapter was added.
- **Open 2026-11-10 (non-blocking):** execute the runtime evaluation cases in Glean and Claude and record dated per-assertion evidence, so that `--release-gate` passes.
- **Open 2026-11-10 (non-blocking):** list which Glean agents have the Atlassian service credential attached (Admin console → Agents). The Admin console wasn't inspected directly in this release.
- **Open 2026-11-10 (non-blocking):** record a baseline of Atlassian-category Service Desk tickets for the telemetry comparison.
