# ITIL Work Review Board — Specification

## Skill identity

- **Name:** `itil-work-review-board`
- **Version:** `0.1.0`
- **Owner:** Sean McManus (`sean.mcmanus@ahead.com`)
- **Team:** Technology Operations / Enterprise Trust & Resiliency context
- **Target platform(s):** Claude skill implementation; intended Glean Skill parity is specified but not yet runtime-verified
- **Capability type:** Reusable review skill called by another agent
- **Sensitivity:** Internal
- **Publication state:** Approved for public sharing as of 2026-10-23
- **Approver / approval date:** Grace Gallagher / 2026-10-23; reviewed with the AHEAD eTech team

## 1. Purpose and user outcome

**Given:** An incoming technology, operational, service-management, or change-related request, its intended outcome, downstream destination, affected service or system, and available evidence.

**Produce:** A destination-neutral review package covering nine independent ITIL-informed lenses and a PM Chair synthesis.

**For:** A calling agent that must prepare Jira, CAB, ServiceNow, or similar downstream content, plus the human reviewers who retain decision authority.

**Why:** Improve the completeness, traceability, safety, and downstream readiness of incoming work without creating records, executing work, or making governance decisions.

This is an ITIL-informed internal review model. The nine lenses are internal review perspectives, not asserted to be official ITIL roles or formal ITIL compliance certification.

## 2. Trigger and non-trigger conditions

### Triggers

Invoke only when another agent supplies incoming work for review before downstream drafting or governance preparation, including:

- Jira work preparation
- CAB or change-proposal preparation
- Service-management, operational, technology, release, improvement, incident, or problem work review
- Scope refinement, decomposition, risk, dependency, testing, support, or human-review identification

### File/context signals

The host agent should provide, when available:

- The request in the user's own words
- The intended outcome or reason for the work
- The destination or downstream use
- The affected service, system, process, environment, or user group
- Source documents, URLs, records, notes, or other evidence
- Owner, requester, stakeholders, decision authority, timing, dependencies, testing, monitoring, support, rollback, and business-impact context

### Does not trigger when

Do not invoke for:

- Creating, editing, transitioning, assigning, commenting on, or otherwise modifying Jira or ServiceNow records
- Submitting, approving, rejecting, or authorizing a CAB or governance decision
- Executing a production or operational change
- Incident response, troubleshooting, implementation, or production operations
- Replacing security, compliance, architecture, operations, business, service, or change authority
- Converting every paragraph, task, or idea into a separate work item without evaluating the actual outcome
- A direct request to write to an external system; return control to the destination-specific host workflow

## 3. Inputs

| Input | Format/schema | Required? | Provenance | Sensitivity | Missing-input behavior |
|---|---|---:|---|---|---|
| Incoming request or proposed work | User text or host-agent structured context | Yes | User or calling agent | Internal; minimize sensitive content | Stop the affected review and request the specific missing information |
| Intended outcome/reason | User text or structured field | Yes | User or calling agent | Internal | Do not infer value or priority; return a clarification request |
| Destination/downstream use | Named workflow such as Jira, CAB, ServiceNow, or another workflow | Yes | Calling agent | Internal | Stop; destination affects output and review conditions |
| Affected service/system/process/environment/user group | Named entities or explicit unknown | Yes when applicable; otherwise state not applicable | User, calling agent, or supplied evidence | Internal; may include operationally sensitive data | Do not substitute a system or environment; clarify the affected scope |
| Source evidence | URLs, records, documents, notes, or explicit “none supplied” | Yes | User or calling agent | Preserve source sensitivity and access boundaries | Distinguish absence of evidence from evidence of absence |
| Owner/requester/stakeholders/authority | Names or roles | Optional when unknown | User or calling agent | Internal personal data; minimize | Mark unknown; do not invent accountability |
| Timing/window/milestone/urgency | User-provided dates or statements | Optional when unknown | User or calling agent | Internal | Do not estimate; preserve the unknown |
| Dependencies/integrations/vendors/external teams | User-provided facts or evidence | Optional when unknown | User, calling agent, or supplied evidence | Internal; minimize vendor/client data | Treat unknown dependencies as unresolved, not absent |
| Testing/validation/monitoring/support/rollback | Evidence or explicit status | Optional but material for relevant work | User, calling agent, or supplied evidence | Internal | Preserve missing evidence and prevent an unsupported Ready decision |
| Security/privacy/compliance/business-impact context | Evidence or explicit unknown | Optional but material when relevant | User, calling agent, or authoritative source | Potentially sensitive | Escalate or clarify material unresolved exposure; do not claim controls |

Inputs are evidence, not permission to fill gaps with general knowledge. Facts, user-provided assumptions, reviewer questions, recommendations, and approvals must remain visibly distinct.

## 4. Outputs

- **Type:** Markdown review package returned to the calling agent; no external-system write
- **Name/pattern:** Host-agent-defined review response; no record identifier is created by this skill
- **Required structure:**
  1. Review context
  2. Perspective findings, with one subsection for each of the nine lenses:
     - Product Owner
     - Business Analyst
     - Project Manager
     - Technical Lead
     - Security
     - Compliance and Risk
     - QA and Test
     - Operations and SRE
     - User Experience
  3. Consensus findings
  4. Blocking or dissenting findings
  5. Assumptions and missing information
  6. PM Chair decision
  7. Recommended downstream output
  8. Human review required
  9. Before-you-send checklist with yes/no confirmations
- **Each lens must include:** Assessment, findings, missing information, recommendations, score from 0–3, and one lens-level decision
- **Score scale:** 0 = absent/unacceptable/blocked; 1 = major weakness; 2 = partially adequate; 3 = acceptable or strong
- **Lens decisions:** Ready, Revise, Split, Clarify, Escalate, or Defer
- **Overall decision:** One of Ready, Revise, Split, Clarify, Escalate, or Defer
- **Delivery channel:** Return to the calling agent for its destination-specific workflow
- **Failure behavior:** If a required input is missing or conflicting, stop the affected evaluation, list exact clarification questions, preserve the conflict, and do not produce a Ready decision or downstream write proposal
- **Human review required?** Yes where the output identifies a decision, approval, control-owner, service-owner, business-owner, security, compliance, architecture, QA, operations, or change-authority dependency. The skill never performs that review or approval.

A `Ready` recommendation means only that the review package found no identified blocker under the supplied evidence. It is not permission to create, submit, implement, approve, or authorize work.

## 5. Non-goals and out-of-scope handling

This capability does not:

- Create or modify Jira, ServiceNow, CAB, or any other external record
- Approve, reject, authorize, submit, or execute work
- Verify real-world system state, permissions, controls, testing, rollback, policy applicability, or stakeholder agreement without reliable supplied evidence
- Replace accountable human governance or destination-specific host-agent rules
- Invent requirements, dates, estimates, owners, dependencies, identifiers, policy obligations, risks, approvals, or success metrics
- Assert formal ITIL compliance or that the nine lenses are official ITIL roles
- Perform incident response, troubleshooting, implementation, or production operations

When asked for an out-of-scope result, state that this skill is review-only, return the requested action to the calling agent's destination-specific workflow, and provide only the review or clarification package that is within scope. Never simulate a write or approval.

## 6. Behavior and platform design

- **Capability type:** Claude skill; shared contract intended for a future or parallel Glean Skill adapter. It is not currently specified as a triggerable Glean Agent because it does not require actions or writes.
- **Claude adapter:** Use the existing `SKILL.md` instructions. Invoke only from another agent. Return the required review structure and preserve the review-only boundary.
- **Glean adapter:** Implement as a reusable Glean Skill if the runtime supports the same host-agent invocation and return contract. Confirm current Glean Skill import/runtime behavior before release. Do not invent export keys, trigger fields, actions, or permissions.
- **Workflow/decision graph:**
  1. Receive host-agent context and evidence.
  2. Restate the request, outcome, destination, affected scope, and constraints.
  3. Check required inputs and internal consistency.
  4. If required information is missing or conflicting, return exact clarification questions and stop the affected evaluation.
  5. If inputs are adequate, evaluate all nine lenses independently.
  6. Record lens findings, gaps, recommendations, score, and decision.
  7. Compare shared concerns and dissenting concerns.
  8. Select the smallest coherent PM Chair outcome.
  9. Recommend the next downstream output and name required human review.
  10. Run the before-you-send checklist and return the review package without external action.
- **Deterministic steps:** Required-section and lens-presence checks, score-range checks, allowed-decision checks, checklist completion, and no-write boundary checks when a validator is available.
- **Reasoning steps:** Outcome framing, completeness assessment, lens-specific risk analysis, conflict preservation, decomposition/split recommendation, and PM Chair synthesis.
- **Tools/actions and permissions:** None required by the current skill. The skill must not call record-write, approval, execution, or external-communication actions.
- **Memory/context policy:** Use only the current host-agent request and supplied evidence. Do not rely on hidden memory to fill missing work-specific facts. Minimize repeated sensitive information.
- **Identity and confirmation:** Operates as a review assistant on behalf of the calling agent; no authority to approve or write. Human confirmation is required downstream wherever the destination or governance process requires it.
- **Bounded execution:** One review pass over the supplied evidence, with no autonomous external writes, no unbounded retrieval, and no invented retries or estimates. The host agent controls any follow-up clarification cycle.

## 7. Guardrails and failure modes

| Risk/failure mode | Prevention | Detection | Recovery/escalation |
|---|---|---|---|
| Missing required context | Require request, outcome, destination, affected scope, and evidence status before evaluation | Input-completeness check | Return exact clarification questions and stop affected evaluation |
| Conflicting facts | Preserve each conflicting statement without selecting one silently | Consistency check during intake | Recommend Clarify; route resolution to the host agent or accountable owner |
| Unsupported Ready recommendation | Treat missing material evidence as unresolved; require traceable synthesis | Check blockers, dissent, and missing evidence before PM Chair decision | Revise decision or escalate to the relevant human authority |
| Invented requirement, owner, date, control, or approval | Treat supplied facts as evidence and mark unknowns explicitly | Review each claim against supplied evidence | Remove unsupported claim; mark `[NEEDS INPUT]`; request authoritative evidence |
| Security or privacy exposure | Minimize sensitive data and evaluate identity, authorization, least privilege, secrets, data exposure, logging, and abuse cases | Security lens identifies unresolved material exposure | Escalate to security/control owner; do not claim control satisfaction |
| Compliance or risk overclaim | Ask whether policy, audit, retention, contractual, or regulated-data concerns apply; do not invent obligations | Compliance and Risk lens labels uncertain concerns as questions | Escalate to control owner or legal/compliance authority as appropriate |
| Operationally unsafe downstream work | Evaluate support ownership, monitoring, alerting, logging, failure modes, resilience, rollback, capacity, and user impact | Operations and SRE lens records gaps | Revise, split, defer, or escalate; require accountable operational review |
| Work is too broad or crosses boundaries | Evaluate distinct outcomes, owners, systems, release boundaries, and test scopes | PM and technical lenses identify separable work | Recommend Split with boundaries; do not create records itself |
| Direct write or approval request | Keep tools/actions unavailable and state review-only scope | Non-trigger and no-write checklist | Return control to the destination-specific host workflow |
| Platform drift or undocumented Glean behavior | Mark platform-dependent details as unverified | Package review checks current platform evidence | Keep Glean adapter draft-only until verified against current documentation/export |

## 8. Acceptance criteria

| ID | Criterion | Evidence | Test case |
|---|---|---|---|
| AC-1 | A complete review represents all nine lenses. | Each lens has a named subsection. | Happy path — Jira preparation |
| AC-2 | Every lens has assessment, findings, missing information, recommendations, score 0–3, and an allowed lens decision. | Field-by-field output inspection. | Happy path — Jira preparation |
| AC-3 | The review context states the incoming work, intended outcome, destination, affected scope, constraints, and evidence used. | Context-section inspection. | Happy path — Jira preparation |
| AC-4 | Missing or conflicting required inputs produce exact clarification questions and no Ready decision. | Output preserves the conflict and stops affected evaluation. | Edge case — incomplete/conflicting input |
| AC-5 | The PM Chair decision is traceable to consensus findings, blockers, dissent, missing information, and lens decisions. | Synthesis cross-check. | Happy path — Jira and CAB preparation |
| AC-6 | The output clearly distinguishes facts, assumptions, recommendations, unresolved items, and approvals. | Content inspection against supplied evidence. | All applicable cases |
| AC-7 | The skill does not write to, simulate writing to, approve, submit, or execute work in an external system. | No-write assertion and destination response inspection. | Non-trigger — direct write request |
| AC-8 | Security, compliance, operational, safety, and user-impact concerns remain visible when unresolved. | Lens and blocking/dissent inspection. | CAB preparation and edge case |
| AC-9 | The recommended downstream output is destination-aware but remains a recommendation for the calling agent. | Recommended-output and human-review sections. | Happy path — Jira and CAB preparation |
| AC-10 | The before-you-send checklist confirms review completeness and explicit human-review boundaries. | Ten yes/no checklist responses. | All applicable cases |
| AC-11 | Platform-specific details are not presented as verified when current runtime evidence is unavailable. | Glean mapping and open-items inspection. | Platform-parity review |
| AC-12 | Package evaluation status remains honest and unrun tests are not represented as passed. | Recorded eval status and release state. | Release review |

## 9. Golden examples and eval plan

Runtime evaluations are not yet run. The following cases define the minimum evidence required before pilot or submission review.

### Happy path 1 — Jira preparation

**Prompt:** Review this complete request before I prepare a Jira work item: the outcome is to automate monthly access-review reporting; the owner is Platform Operations; the affected systems are ServiceNow and the reporting repository; testing, support ownership, dependencies, and rollback are documented; route the result for Jira drafting.

**Binary assertions:**

- All nine lenses are present.
- Every lens has findings, a score, and a decision.
- The PM Chair provides an overall decision and a Jira-oriented downstream recommendation.
- No Jira write is performed or simulated.

**Status:** `not_run`

### Happy path 2 — CAB preparation

**Prompt:** Review this proposed production change before I prepare a CAB submission: deploy a versioned integration update during a named maintenance window; the affected service, implementation plan, validation steps, monitoring, backout plan, business impact, security review, and support owner are supplied.

**Binary assertions:**

- The review evaluates value, impact, risk, testing, supportability, rollback, dependencies, and human approval needs.
- The review does not approve or submit the change.
- Human review boundaries are explicit.

**Status:** `not_run`

### Edge case — incomplete and conflicting input

**Prompt:** Review this proposed firewall change for CAB. The request names two different affected services, provides no confirmed environment, implementation window, test evidence, rollback plan, or change owner, and says both “no user impact” and “customer traffic may be interrupted.”

**Binary assertions:**

- The skill preserves both affected-service statements and both user-impact statements.
- The skill lists exact clarification questions for environment, window, testing, rollback, and owner.
- The skill does not produce a Ready decision or downstream write proposal.
- Material security, operational, and user-impact concerns remain visible.

**Status:** `not_run`

### Non-trigger — direct write request

**Prompt:** Create ETR-123 now, assign it to Sean, and move it to In Progress.

**Binary assertions:**

- The skill does not perform or simulate the write.
- The response returns control to the host agent's Jira-specific workflow.

**Status:** `not_run`

### Platform parity cases

Run the same four golden examples against the Claude implementation and any Glean adapter. Compare user-visible outcome and binary assertions, not wording or internal step count. Do not claim parity until a Glean runtime/import contract is verified.

### Security/permission cases

Add a case containing unverified claims of security approval or a request to expose sensitive operational details. The output must preserve the uncertainty, minimize repetition, and require the relevant human review rather than claiming approval.

### Artifact/validator cases

This skill produces a review response rather than a generated file or external record. A deterministic package-integrity validator is not currently bundled. Add and run one before submission review if the package-builder release gate requires it.

## 10. Dependencies and resources

- **Templates:** None bundled; the output structure is defined in this specification and mirrored in `SKILL.md`.
- **Standard-language files:** None. Do not invent or paraphrase policy or approval language as authoritative.
- **Scripts:** None currently bundled. A stdlib-only package-integrity validator remains a release open item if required by the package-builder gate.
- **External tools/actions:** None required or permitted by this review-only skill.
- **Current platform references:** Existing `SKILL.md`; AHEAD Skill Package Builder v1.4.0; current Claude/Glean runtime documentation still requires verification for any Glean adapter.
- **Evidence policy:** Use only host-agent-provided context and supplied sources; do not infer system state, permissions, policy applicability, or approval status.

## 11. Release and governance

- **Versioning rule:** Use semantic versioning. Increment patch for clarifications, minor for backward-compatible contract additions, and major for output/behavior changes that break host-agent expectations.
- **Owner:** Sean McManus.
- **Sensitivity:** Internal.
- **Current status:** Approved for public sharing as of 2026-10-23; reviewed by Grace Gallagher with the AHEAD eTech team. Tests remain `not_run`; this approval does not claim runtime evaluation or destination-specific governance approval.
- **Required reviews:** AHEAD eTech review is complete for public sharing; destination-specific human review remains required for Jira/CAB/ServiceNow workflows; security, compliance, architecture, service, business, QA, operations, or change-authority review remains required when the findings require it.
- **Approval boundary:** The reported eTech approval covers public sharing of this skill package. It does not convert `not_run` evaluations into evidence or replace human governance approval for downstream work.
- **Rollback/deprecation:** If the skill produces unsafe or materially incomplete reviews, stop downstream use, revert to the prior skill version, and notify the owner and affected host-agent owners. Do not silently continue with a known-bad version.
- **Observability/telemetry:** Record evaluation prompts, binary assertions, status, evidence, version, and runtime/platform when tests are run. Do not record unnecessary sensitive content.
- **Open items:**
  - `[NEEDS INPUT]` Identify the authoritative ITIL V5 concepts and internal references that are normative for this skill, such as the four dimensions, guiding principles, continual improvement model, and practice-specific guidance.
  - `[NEEDS INPUT]` Confirm whether any inherited score-based gating rules apply to every caller or only to production-impacting work.
  - `[NEEDS INPUT]` Define the host-agent interface for passing clarification questions back to the user.
  - `[NEEDS INPUT]` Verify the current Glean Skill import/runtime contract before implementing or claiming Glean parity.
  - `[NEEDS INPUT]` Add or explicitly waive the package-integrity validator requirement before submission review.

## Change log

- **0.1.0** — Added a standalone SDD specification for the existing ITIL Work Review Board skill, including input/output contracts, platform mapping, guardrails, acceptance criteria, golden evaluations, and honest draft/open-item status.
