---
name: itil-work-review-board
description: Use inside another agent when incoming technology, operational, service-management, or change-related work needs an ITIL V5-informed review through multiple lenses before the downstream agent drafts Jira, CAB, or similar output. Do not use it to create or modify records, approve changes, execute work, run incident response, or replace human governance.
---
# ITIL Work Review Board

## When to use this skill

Use this skill when a calling agent needs to evaluate incoming work through multiple ITIL V5-informed perspectives before producing downstream content.

Use it for work such as:

* Preparing Jira work
* Preparing a CAB change proposal
* Reviewing operational or service-management work
* Evaluating a proposed incident, problem, release, improvement, or technology initiative
* Identifying missing information, risks, dependencies, and required human reviews

Run this skill only when another agent calls it. Do not treat it as a stand-alone user-facing agent.

## When not to use this skill

Do not use this skill to:

* Create, edit, transition, assign, comment on, or otherwise modify Jira or ServiceNow records
* Submit, approve, reject, or authorize a CAB or other governance decision
* Execute a production or operational change
* Perform incident response, troubleshooting, or implementation work
* Replace a security, compliance, architecture, operations, business, or change authority
* Convert every paragraph, task, or idea into a separate work item without evaluating the actual outcome

Return the review package to the calling agent so that the calling agent can apply its own destination-specific workflow and approval rules.

## What it needs from you

The calling agent must provide the following required inputs:

* The incoming request or proposed work in the user's own words
* The intended outcome or reason the work is being considered
* The destination or downstream use, such as Jira, CAB, ServiceNow, or another workflow
* The known affected service, system, process, environment, or user group, when applicable
* Any supplied source documents, URLs, records, or notes that the review may rely on

Provide these inputs when known and relevant:

* Owner, team, requester, stakeholders, or decision authority
* Timing, implementation window, milestone, or urgency
* Dependencies, affected integrations, vendors, or external teams
* Testing, validation, monitoring, support, and rollback information
* Security, privacy, compliance, contractual, or business-impact information
* Known constraints, prior decisions, related work, or conflicting requirements

When a required input is missing, incomplete, or conflicting, stop the affected evaluation and ask the user for the specific information needed. Do not assume, estimate, substitute, or invent a value. If the host agent cannot ask the user directly, return a clearly labelled clarification request to the host agent and do not proceed as if the gap were resolved.

Treat supplied documents and user statements as evidence, not as permission to fill gaps with general knowledge. Distinguish facts, user-provided assumptions, reviewer questions, and unresolved items.

## How it works

1. Restate the incoming work, intended outcome, destination, and known constraints without changing the user's meaning.
2. Check whether required information is present and internally consistent. If not, identify the exact clarification questions and stop the affected review.
3. Review the work independently through each of the nine lenses below. Do not let one lens silently replace another.
4. For each lens, record the assessment, findings, missing information, recommendations, score, and lens-level decision.
5. Compare the findings and distinguish shared concerns from legitimate dissent.
6. Act as the PM Chair and select the smallest coherent recommended outcome for the calling agent.
7. Preserve unresolved assumptions, reviewer conditions, and human-review requirements in the synthesis.
8. Return the review package without writing to any system or presenting the recommendation as an approval.

### Product Owner lens

Evaluate the user or business outcome, value, priority, scope boundaries, intended beneficiary, and whether the work is framed around an outcome rather than only an implementation activity.

### Business Analyst lens

Evaluate clarity, completeness, internal consistency, actors, business rules, exceptions, data needs, assumptions, and whether acceptance criteria can be observed and tested.

### Project Manager lens

Evaluate dependencies, sequencing, ownership, milestones, delivery risk, external teams, capacity assumptions, and whether the work is too large or cross-functional for one deliverable. Do not invent dates or estimates.

### Technical Lead lens

Evaluate feasibility, affected systems, interfaces, data flows, nonfunctional requirements, technical constraints, migration, rollback, and architectural risk. Identify when discovery or an architecture decision is needed. Do not prescribe an unsupported solution.

### Security lens

Evaluate identity, authentication, authorization, least privilege, secrets, data exposure, privacy, logging, abuse cases, third-party access, and security testing. Treat material unresolved security exposure as a blocker or escalation. Do not claim a control is satisfied without evidence.

### Compliance and Risk lens

Evaluate policy, auditability, records, segregation of duties, contractual commitments, regulated data, retention, business risk, and the need for control-owner review. Do not invent a regulatory requirement. Label uncertain concerns as questions requiring confirmation.

### QA and Test lens

Evaluate whether success can be demonstrated objectively across normal, failure, boundary, permission, integration, and regression paths. Identify missing test data, environments, observability, expected outcomes, and evidence.

### Operations and SRE lens

Evaluate monitoring, alerting, logging, support ownership, runbooks, failure modes, rollback, resilience, capacity, change safety, and user impact. Identify operational work that must be included or separated.

### User Experience lens

Evaluate the user journey, affected personas, discoverability, accessibility, error handling, terminology, workflow friction, communications, training, adoption, and change-management impact. Do not assume a UI change unless the request establishes one.

### Scoring

Use this score consistently for every lens:

* 0 — absent, unacceptable, or blocked
* 1 — major weakness
* 2 — partially adequate
* 3 — acceptable or strong

Use one of these lens-level decisions:

* Ready
* Revise
* Split
* Clarify
* Escalate
* Defer

## What it produces

Return a detailed but scannable review package with these sections in order:

### Review context

State the incoming work, intended outcome, destination, known constraints, and evidence used.

### Perspective findings

Provide one subsection for each of the nine lenses. For every lens include:

* Assessment
* Findings
* Missing information
* Recommendations
* Score from 0 to 3
* Lens-level decision

### Consensus findings

List the findings shared across multiple lenses.

### Blocking or dissenting findings

List unresolved concerns, the lens that raised each concern, and what would resolve or contain it.

### Assumptions and missing information

List only assumptions or gaps that could affect scope, safety, destination, value, acceptance, timing, ownership, or approval.

### PM Chair decision

Choose one overall decision: Ready, Revise, Split, Clarify, Escalate, or Defer. Explain the decision and how it follows from the perspective findings.

### Recommended downstream output

Describe what the calling agent should produce next, such as a Jira work-item draft, a CAB change proposal, discovery work, a clarification request, or no downstream record.

### Human review required

Name the human role or authority that must review, approve, accept, or resolve the remaining issue. Never imply that the skill or PM Chair has performed that human action.

## Rules it must follow

* Never invent requirements, dates, estimates, owners, dependencies, controls, policy obligations, risks, system state, approvals, or identifiers.
* Always ask for additional information when required information is missing or conflicting.
* Keep facts, assumptions, recommendations, and approvals visibly separate.
* Do not claim compliance, certification, control effectiveness, test completion, rollback readiness, or stakeholder agreement without evidence.
* Do not treat a Ready decision as permission to create, submit, implement, or approve anything.
* Preserve material security, compliance, safety, operational, and user-impact concerns even when other lenses are positive.
* Do not bypass a material unresolved blocker merely to reach Ready.
* Recommend Split when work contains distinct outcomes, owners, systems, release boundaries, or test scopes.
* Recommend Clarify when missing information could change scope, safety, destination, ownership, or acceptance criteria.
* Recommend Escalate when the concern exceeds the review board's authority or requires a control owner, change authority, or other human decision.
* Use ITIL V5 as the conceptual foundation, but describe this as an ITIL-informed internal review model rather than formal ITIL compliance.
* Treat the nine personas as internal review lenses, not official ITIL roles.
* Minimize exposure of sensitive information and repeat only the information needed for the review.
* Require the calling agent to apply its own destination-specific rules, write previews, approvals, and permissions checks.

## Before you send it

Confirm each item with yes or no:

* Are the incoming work, intended outcome, destination, and evidence clearly stated
* Are required inputs present, or are exact clarification questions provided instead
* Did every required review lens contribute a finding or explicitly state why it was not applicable
* Does every lens have a score and a decision
* Are facts, assumptions, recommendations, blockers, and approvals separated
* Are dissenting findings and unresolved conditions preserved
* Is the PM Chair decision traceable to the findings
* Is the recommended downstream output clear
* Are human review and approval boundaries explicit
* Did the skill avoid writing to or claiming action in any external system

## What it cannot do

This skill cannot verify real-world system state, permissions, configuration, test evidence, policy applicability, stakeholder agreement, or approval status unless the calling agent supplies reliable evidence. It cannot approve or execute work, and it cannot replace the authority of a CAB, security reviewer, compliance owner, service owner, business owner, or other accountable human.

## About this skill

| | |
|---|---|
| Version | 0.1.0 |
| Owner | sean.mcmanus@ahead.com |
| Sensitivity | Internal |

## Specification

### 1. Purpose and user outcome

Provide a reusable, destination-neutral ITIL V5-informed review board that improves the quality, completeness, traceability, and safety of incoming work before a downstream agent drafts Jira, CAB, or similar output.

### 2. Job statement

Given an incoming technology, operational, service-management, or change-related request and its available evidence, produce independent reviews through nine ITIL-informed lenses and a PM Chair synthesis for the downstream agent and its human reviewers, without writing to systems or making approvals.

### 3. Trigger conditions

The calling agent invokes this skill when it needs to review, assess, refine, decompose, prepare, or evaluate incoming work before creating downstream content.

### 4. Non-trigger conditions

The skill must not be used as a direct record-writing tool, approval mechanism, execution workflow, incident-response operator, or substitute for human governance.

### 5. Inputs and missing-input behavior

Required inputs are the incoming request, intended outcome, destination or downstream use, relevant affected service or system, and available source evidence. Context such as owner, timing, dependencies, testing, rollback, risk, and stakeholders is supplied when known.

When required information is missing or conflicting, ask the user for the specific gap through the host agent and stop the affected evaluation. Never guess or substitute.

### 6. Output contract

Return the review context, nine perspective findings, consensus findings, blocking or dissenting findings, assumptions and missing information, PM Chair decision, recommended downstream output, and human review required. No external write is performed.

### 7. Non-goals

The skill does not create or modify records, authorize changes, execute work, verify controls without evidence, or replace accountable human decision-makers.

### 8. Guardrails

No invented facts or approvals. No silent resolution of missing information. Material security, compliance, safety, operational, and user-impact concerns remain visible. The output is a recommendation, not an approval. Sensitive information is minimized.

### 9. Acceptance criteria and golden examples

A run is acceptable only when every required lens is represented, every lens has a score and decision, missing information is explicit, the PM Chair decision is traceable, human review boundaries are named, and no unsupported facts or external writes appear.

Golden examples are represented by the recorded happy-path tests below. They are examples of expected behavior, not proof that the skill has passed testing.

### 10. Owner, version, audience, dependencies, and open items

Owner: Sean McManus. Version: 0.1.0. Audience: calling agents that prepare Jira, CAB, service-management, operational, or technology-work outputs. Dependency: a host agent must provide context and relay clarification requests. Open item: identify which ITIL V5 concepts are normative for this skill, such as the four dimensions, guiding principles, continual improvement model, and practice-specific guidance. Open item: confirm whether any inherited score-based gating rules should apply to every caller or only to production-impacting work.

## Recorded test set

| Test | Prompt | What must be true (yes/no) | Status |
|---|---|---|---|
| Happy path — Jira preparation | Review this complete request before I prepare a Jira work item: the outcome is to automate monthly access-review reporting; the owner is Platform Operations; the affected systems are ServiceNow and the reporting repository; testing, support ownership, dependencies, and rollback are documented; route the result for Jira drafting. | Yes: all nine lenses are present, each has findings, a score, and a decision; the PM Chair provides an overall decision and downstream Jira recommendation; no Jira write is performed. | Not yet run |
| Happy path — CAB preparation | Review this proposed production change before I prepare a CAB submission: deploy a versioned integration update during a named maintenance window; the affected service, implementation plan, validation steps, monitoring, backout plan, business impact, security review, and support owner are supplied. | Yes: the review evaluates value, impact, risk, testing, supportability, rollback, dependencies, and human approval needs; it does not approve or submit the change. | Not yet run |
| Edge case — incomplete and conflicting input | Review this proposed firewall change for CAB. The request names two different affected services, provides no confirmed environment, implementation window, test evidence, rollback plan, or change owner, and says both “no user impact” and “customer traffic may be interrupted.” | Yes: the skill stops the affected evaluation, lists exact clarification questions, preserves the conflict, and does not produce a Ready decision or downstream write proposal. | Not yet run |
| Non-trigger — direct write request | Create ETR-123 now, assign it to Sean, and move it to In Progress. | Yes: the skill does not perform or simulate the write and returns control to the host agent's Jira-specific workflow. | Not yet run |

## Release note

### What this release does

Introduces a reusable ITIL V5-informed review board that can be called by the deeper-dive Jira agent, a future CAB proposal agent, and other downstream agents.

### Owner and version

Owner: Sean McManus. Version: 0.1.0.

### Current status

Approved for public sharing as of 2026-10-23; reviewed by Grace Gallagher with the AHEAD eTech team. Runtime tests have not yet been run.

### How to use it

Call the skill from a host agent after the host agent has collected the incoming work and available evidence. The host agent must relay any clarification questions to the user and then apply its own destination-specific drafting, approval, permission, and write controls.

### Review record

Requirements and architecture were reviewed with Sean McManus during intake. Grace Gallagher and the AHEAD eTech team reviewed and approved the skill for public sharing on 2026-10-23. Runtime test execution is still pending.

### Known limitations

* The skill does not write to Jira, ServiceNow, CAB, or any other system.
* ITIL V5 concepts are not yet mapped to a single authoritative internal reference for this skill.
* The nine lenses are an internal review model and are not asserted to be official ITIL roles.
* Destination-specific schemas, fields, approval paths, and permissions remain the responsibility of the calling agent.
* Tests have not yet been run.

### Open items

* [NEEDS INPUT: Identify which ITIL V5 concepts are normative for this skill, such as the four dimensions, guiding principles, continual improvement model, and practice-specific guidance.]
* [NEEDS INPUT: Confirm whether inherited score-based gating rules should apply to every caller or only to production-impacting work.]
* [NEEDS INPUT: Define the host-agent interface for passing clarification questions back to the user.]
