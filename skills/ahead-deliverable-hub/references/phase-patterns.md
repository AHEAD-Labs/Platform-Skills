# Phase patterns

How to shape a hub for each kind of phase. The engine is the same for all of them; what changes is
the tab set, the Overview story and where decisions live. Start from the closest preset, then
replace its deliverable tabs with the ones in the SOW.

Contents
1. Principles that apply to every phase
2. Discovery template, Phase 1 (preset `discovery`)
3. Target design template, Phase 2 (preset `target-design`)
4. Any other phase: the base template (preset `blank`)
5. Deriving tabs and sections from a SOW

---

## 1. Principles that apply to every phase

- **One tab per contracted deliverable, named exactly as the SOW names it.** Tab labels use the full
  English name ("Governance and Control Kit"), never the ID ("D2.2"). The ID appears as a chip on the
  tab's hero and in the Overview index. Readers navigate by name; reviewers check against the SOW.
- **Overview first, then the plan (if there is one), then the deliverables in reading order.** Put the
  tab that brings everything together (the target architecture, the roadmap, the recommendation) just
  before the forward-looking tab (the next-phase blueprint), because it depends on the tabs before it.
- **The Overview tells the story without giving away the detail.** It answers: what did we conclude,
  how did we get there, where are we now, what do we recommend next. It links to the tabs for the
  substance. It never carries the architecture diagram or a deliverable's detailed content.
- **Everything lives in the hub.** No "format" or "supporting materials" sections, no links to decks,
  spreadsheets or SharePoint. If a table matters, it is a table in the hub. The reason: the hub is the
  deliverable, and a reader on a plane or in a board pack must not hit a dead link.
- **A template reads as the final package, not as work in progress.** Guides are written as of the
  final date ("How Phase 2 was conducted", not "What we are doing this week"). Nothing tracks progress;
  the only progress signal is the `?check` view, which lists remaining placeholders.
- **Every slot has one owner.** Owners are tagged on the placeholder so each person can find their
  sections; the tags disappear as content replaces the placeholders, so no names reach the client.
- **Decisions sit with the deliverable that made them, then roll up.** Each deliverable tab ends with a
  "Decisions and open items" table; the forward-looking tab consolidates them; architecture decisions
  are also recorded as ADRs on the architecture tab. There is no separate decisions tab.
- **Mark only real decision points.** In the plan, a star means the client is asked to decide something
  (typically two: the draft review and the final review). Starring every workshop dilutes the signal.

## 2. Discovery template, Phase 1 (preset `discovery`)

Status: **template 1.0, delivered.** The structure of a discovery hub AHEAD has delivered.

Purpose: present what the phase found, with the evidence, and hand a clear scope to the next phase.
A discovery hub is usually *filled* by the end of the phase (findings, register, scores), so it is
often built in two passes: a template with owners at the start, then content filled from the evidence.

| Tab | What it holds | Notes |
|---|---|---|
| Overview | Headline finding (a conclusion, not a description), architecture and next-phase implications, what the phase established, evidence streams, contents index, deliverables-to-tab map, key terms | Headline numbers: sessions held, platforms assessed, hypotheses tested, decisions recorded |
| Hypothesis and Decision Register | Interactive register: hypotheses, decisions, experiments, with priority, status, area, evidence, implication, next step | Generated from config items or a CSV/XLSX export of the team's register |
| Current-State Estate | What the estate tells us, platforms table, user and project context, how it is used, evidence limitations | Current state only. No direction here |
| Maturity Assessment | What the scores show, heatmap (platform by dimension), patterns and actions, rubric | Confirm the rubric with the team before scoring |
| Control Assessment | Posture in brief, control heatmap, evidence behind each domain score, open questions that affect the next phase | |
| Architecture Hypothesis | Requirements, current-state diagram, logical hypothesis diagram, direction views, common platform contract, open questions | Label the hypothesis as a hypothesis |
| Feasibility Validation | What was proved and what was not, results table with Proven / Partially proven / Not proven tags, cross-cutting findings, notation, test detail, ranked next spikes | |
| Phase N to Phase N+1 | Next-phase scope, position per capability (Reuse / Select / Standardize), decisions the next phase must take | |
| Evidence Base | How evidence was gathered, sessions held, materials reviewed, assumptions | Participants by role |

Register discipline (this is where discovery hubs earn trust):
- Every item cites its evidence: a named session and date, a document, or a test. Hearsay is labelled.
- Priorities are balanced. High is for the handful of items that shape the architecture (roughly one in
  five); if everything is High, nothing is.
- Merge duplicates rather than keeping near-identical rows; keep the surviving ID and note the merge.
- Status values are few and consistent (Open, Validated, Agreed, Deferred to Phase N, Closed).
- Cross-reference items from anywhere in the hub with `[[H012]]`; the link opens the item.

## 3. Target design template, Phase 2 (preset `target-design`)

Status: **template 1.0, agreed baseline.** The structure was agreed at the start of a target design
phase that is still in progress. Expect structural updates when that phase closes (see `changelog.md`).

Purpose: hand over the final design package at the design gate. Built at the *start* of the phase as a
fixed template with every section the acceptance criteria require, each tagged with an owner, so the
team fills it week by week rather than assembling it at the end.

| Tab | What it holds |
|---|---|
| Overview | Cover with three headline numbers; executive summary (overall conclusion, our approach, key insights, current position, the opportunity for the client); recommended direction (text only, links to the architecture tab); recommended next steps (presented as a recommendation if the next phase needs a separate agreement); deliverable index; glossary |
| Phase Delivery Plan | Gantt (key above the chart), key sessions and reviews with the two decision points, engagement cadence |
| One tab per design deliverable | Hero with ID chip and the deliverable's question; Key conclusions; one section per required element; Decisions and open items; Acceptance criteria coverage table linking each criterion to its section |
| Target Architecture | Opens with the single authoritative target architecture diagram; detailed views must be consistent with it; ADR table; evolution from baseline; open decisions |
| Next-Phase Build Blueprint | Prioritized work packages, acceptance and readiness criteria, sequencing, team and sprint sizing, commercial options, consolidated decisions and open items, design gate outcome |

Rules specific to target design:
- **One architecture diagram, shown once, on the Target Architecture tab.** The Overview describes the
  direction in words and links to it. The reader meets the architecture where it is explained, and
  there is one version of the truth to keep consistent.
- **Headline numbers are outcomes**, such as ADRs recorded, decisions agreed, workflows validated.
  Avoid counting work packages or effort; those belong to the blueprint.
- **Distinguish designed from deployed.** Control, observability and onboarding tabs each state what is
  design or requirement only, and what is already deployed, tested or certified.
- **The next phase is a recommendation**, not a commitment, unless it is already contracted.

## 4. Any other phase: the base template (preset `blank`)

Assessments, strategy and roadmap work, pilots, build phases and handovers all fit the same frame:

1. Overview: conclusion, approach, insights, position, recommendation, index, glossary.
2. Plan (optional): only if the plan is itself a deliverable or the client asked to see it.
3. One tab per contracted deliverable, using the `deliverable` shorthand.
4. Free-form tabs (explicit sections and blocks) for content that is not a deliverable but the reader
   needs, such as a scorecard heatmap, a register, an evidence base.
5. The integrating tab, then the forward-looking tab, last.

Useful mappings:
- Readiness or maturity assessment: heatmap block for the scorecard, register block for findings,
  table for the use-case shortlist, roadmap as a gantt.
- Strategy or roadmap: options table with [ok]/[warn]/[bad] tags, a gantt for the roadmap, decisions table.
- Build or pilot phase: plan tab, one tab per increment or work package, validation results table,
  runbook and handover tab.

## 5. Deriving tabs and sections from a SOW

1. List the contracted deliverables with their exact names and IDs. Each becomes a tab (except the plan,
   which can be a tab if contracted).
2. For each deliverable, copy the acceptance criteria verbatim into `criteria`. Create one section per
   distinct element the criteria require, in the order a reader needs them; map each criterion to the
   section(s) that answer it. A criterion with no section is a gap, so either add a section or raise it.
3. Write the deliverable's question: the one sentence the tab answers ("Who owns, decides, supports
   and escalates what across the platform?"). It is the tab's lede and its line in the index.
4. Assign an owner per deliverable (and per section where it differs). The principal consultant owns the
   Overview; the engagement lead usually owns the plan and glossary.
5. Note anything in the SOW that conflicts (dates, owners, acceptance wording) and tell the user rather
   than resolving it silently.
