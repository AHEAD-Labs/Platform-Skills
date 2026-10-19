# Platform-Skills

**Skills Auditor is where we audit. Platform-Skills is where the approved version lives.**

Platform-Skills is the proposed maintained source for Skills that earn AHEAD Platform Skill status, with their version history. The current pilot is **Glean-first**; Claude distribution is stage two.

**Picking this up?** Start at [docs/PICKUP.md](docs/PICKUP.md): orientation, state snapshot, gap audit and prioritized deliverables.

Status labels used below: **CONFIRMED** (demonstrated), **TESTING** (in progress), **OPEN** (unresolved or unproven), **BLOCKED** (cannot proceed until something else is resolved).

## What this is, and what it is not

Platform-Skills **is**:

- the proposed single home of each approved Platform Skill, so a Skill is maintained once rather than edited separately on each platform
- the version history of those Skills: every change is a pull request with a reviewer
- the pilot workspace for validating how Glean (and later Claude) consume Skills from this repository

Platform-Skills **is not**:

- the audit engine. That is [Skills Auditor](#relationship-to-skills-auditor), a separate internal repository (formerly Skills Marketplace). Candidates are *submitted* here by pull request, and CI blocks them until a trusted Auditor result exists.
- a broad, company-wide intake channel
- a proven automated publishing path. GitHub-to-Glean sync is still being validated (see [Validation matrix](#validation-matrix)).
- a place for credentials, runtime infrastructure, or operational state

## Operating model

| Role | Owns |
| --- | --- |
| Domain teams / aligned FDEs | Skill business logic and ongoing maintenance |
| Enterprise GPT | Standards, qualification and auditing, promotion rules, shared distribution architecture |

- **New Skill: full audit.**
- **Update to an existing Platform Skill: delta/regression audit.**
- **Human approval is required before promotion.** Automated checks support the reviewer; they do not replace them.

## Relationship to Skills Auditor

| Repository | Role |
| --- | --- |
| Skills Auditor | Audit of a new or updated Skill before it is promoted |
| Platform-Skills (this repo) | Maintained source for approved Platform Skills and their version history |

```mermaid
flowchart TD
    A["Candidate / updated Skill ZIP<br/>(PR to Platform-Skills)"] --> V["Deterministic gate<br/>tools/skillpkg.py"]
    V --> B["Skills Auditor<br/>Full or delta audit"]
    B -->|Independent human review + merge| C["Platform-Skills main<br/>Approved source"]
    C -->|publish / sync<br/>pilot validating| D["Glean"]
    C -.->|stage two| E["Claude"]
```

## Package philosophy

- Users work with portable Skill **packages**, not repository internals. They should not need to hand-edit files in this repo.
- Glean exports Skills as **ZIP packages**.
- The six seed ZIP exports are **untouched baseline exports**, staged on the pilot pull request (not yet on `main`; see the [PTO handoff](docs/PTO-HANDOFF-2026-10-19.md)). They must remain byte-for-byte unchanged.
- **Implemented:** the ZIP stays canonical, and `tools/skillpkg.py` deterministically generates the Glean-readable folder (`projections/glean/<id>/`) plus provenance once a Skill is audited and approved. Glean's acceptance of that folder from `main` is still to be confirmed.

## Pipeline and operations

| Doc | Contents |
| --- | --- |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Submit, update, audit, approve, project, Glean release, rollback, troubleshooting |
| [docs/GOVERNANCE.md](docs/GOVERNANCE.md) | Approval authority, trust boundaries, required branch protection |
| [docs/AUDITOR-CONTRACT.md](docs/AUDITOR-CONTRACT.md) | Skills Auditor interface and integration status (**not yet integrated**) |
| [docs/PTO-HANDOFF-2026-10-19.md](docs/PTO-HANDOFF-2026-10-19.md) | Current state, open PRs, next actions |

CI (`validate-skills`) runs unit tests and a policy gate on every PR, with a read-only token and no secrets. Any new or changed Skill ZIP is **blocked** until a trusted Skills Auditor result exists. That block is intentional.

## Glean pilot status

| Finding | Status |
| --- | --- |
| Direct GitHub Skill import was previously demonstrated | CONFIRMED |
| Nested Skill reference files were discovered successfully | CONFIRMED |
| Private-repository import failure. Strongly suggests an authorization issue; root cause not proven | OPEN |
| Scheduled GitHub sync. Prior result is inconclusive, not a failure of the architecture | OPEN |
| GitHub import is one-way (GitHub → Glean) and accepts Skill folder / `SKILL.md` paths (2026-10-13) | CONFIRMED |
| Importing a ZIP file URL from GitHub failed with a directory parsing error (2026-10-13) | CONFIRMED (fails) |
| Existing manual org Skills do not become Git-backed automatically; a controlled migration/deactivation is needed | CONFIRMED |
| Refresh cadence, tenant behavior, vendor roadmap | OPEN |

### Why the previous sync experiment is inconclusive

- It used a throwaway Skill.
- It ran on an experiment branch, not the intended canonical `main` path.
- Repository visibility changed during the experiment.
- The Glean-side Skill was also interacted with and modified.

A clean GitHub-only-writer test is still required.

## Validation matrix

| Area | Status | Notes |
| --- | --- | --- |
| Existing Shared Skill vs newly uploaded package: coexistence / deduplication | TESTING | Using the six baseline exports |
| Canonical Git representation: ZIP vs expanded Skill directory | IMPLEMENTED, NOT CONFIRMED IN GLEAN | ZIP is canonical; `tools/skillpkg.py` generates `projections/glean/<id>/`. Needs a first folder import from `main` (PICKUP D6) |
| GitHub update propagation | OPEN | |
| Refresh / scheduled-sync behavior | OPEN | Needs the clean test below |
| Private-repository authorization | OPEN | Hypothesis only; not proven |
| Organization-wide publication / migration behavior | OPEN | |

## Next execution sequence

See [docs/PICKUP.md §4](docs/PICKUP.md#4-deliverables-to-pick-up-priority-order) for the maintained, owner-assigned list. In short:

1. Independent review of the merged tooling and branch protection on `main` (#7).
2. Decide the interim audit path while the Auditor is not in CI.
3. Decide whether the six seed exports land on `main` as unapproved baselines (draft #5).
4. Take one real Skill end to end: audit to REVIEW_READY, project, merge.
5. Run a clean folder import from `main` with **GitHub as the sole writer** (no edits in Glean), then record what was observed.
6. Take the unresolved product/platform questions to Glean.

## What belongs here

- Skill packages (ZIPs) under [`skills/`](skills/README.md): approved ones, and candidates on open PRs
- Generated Glean folders and provenance for approved Skills (`projections/glean/`, `provenance/`)
- Short pointers to the Skill standard, under [`standards/`](standards/README.md)
- Contribution and review guidance ([CONTRIBUTING.md](CONTRIBUTING.md))

## What does not belong here

- Credentials, API keys, tokens, or other secrets
- Unapproved Skills on `main`, except seed exports explicitly listed in a trusted `skills/baseline-hashes.json`
- Skills Auditor reports or findings (they stay in the internal Auditor repository)
- Skills Auditor evaluation logic or AI judging
- Deployment, sync, or notification infrastructure
- Client data or other confidential material

## How a skill moves

1. **Candidate**: a new or updated Skill is drafted by the owning domain team / FDE.
2. **Audited**: Skills Auditor runs a full audit (new Skill) or a delta/regression audit (update).
3. **Approved**: a human approves, and it is merged into this repository. The merged state is the approved version.
4. **Maintained**: later changes, including UAT feedback, come in as pull requests here.
5. **Published**: the approved version reaches Glean and/or Claude. Publishing is separate from merging, and the mechanism (manual vs GitHub sync) is under validation.

## Initial Landing Set

The first population of this repository is the set of Skills launched through the initial Enterprise GPT Skills rollout on September 28, 2026:

- `story-writing-for-presentations`
- `outlook-event-creation`
- `ahead-meeting-prep-and-notes`
- `ahead-weekly-recap`
- `ahead-skill-package-builder`
- `ahead-daily-digest`

These were launched in Glean and were also announced as available to users with Claude access.

The six Glean org-wide export ZIPs are staged on draft PR #5 as unapproved baseline artifacts; they are not on `main` yet. Staging them does **not** mean they are approved Platform Skills or that anything has been published.

- Each landed Skill should preserve its version history and provenance.
- Once an artifact is reviewed and merged, `main` is the approved source for that Skill.
- Availability in Glean or Claude is separate from the repository source of truth.
- Updates based on UAT or user feedback come back through a new branch and pull request, not through silent changes to deployed copies.

### Landing workflow

```mermaid
flowchart TD
    A["Existing launched skill"] --> B["Approved artifact supplied"]
    B --> C["Platform-Skills branch"]
    C --> D["Pull request"]
    D --> E["Peer review"]
    E --> F["Merge to main"]
    F --> G["Platform-Skills is the canonical<br/>approved repository version"]
    G --> H["Publish / sync to Glean and/or Claude<br/>(mechanism under validation)"]
```

## Version history

Git is the version history. Each approved change is a merged pull request, so the diff, the reviewer, and the reasoning stay attached to the change. To see what changed in a Skill, read its history:

```sh
git log --follow -- skills/shared/<skill-id>.zip     # the source package
git log -- provenance/<skill-id>.json                # approvals, audit summary, Glean state
```

## Why human review is the approval gate

A Skill shapes what Claude and Glean do for AHEAD employees. Automated checks catch structure and consistency problems, but a teammate has to confirm the Skill is correct and appropriate. Merging a pull request in this repository is that confirmation, which is why the author never approves their own change.

## How UAT feedback becomes a change

UAT feedback is never applied as an undocumented edit directly on a platform. It follows the same path as any other change:

```mermaid
flowchart LR
    A["UAT feedback"] --> B["Update approved source"]
    B --> C["Pull request"]
    C --> D["Peer review"]
    D --> E["Merge"]
    E --> F["New approved version"]
    F --> G["Publish / sync"]
```

If a platform copy has been edited directly, bring that change back here as a pull request so the repository stays the source of truth.

## Repository layout

```text
README.md            this file
CONTRIBUTING.md      how to propose and review a change
skills/              Skills (claude/, glean/, shared/ for source ZIPs)
projections/glean/   generated Glean-readable folders (approved Skills only)
provenance/          per-Skill hash, audit and deployment record
tools/skillpkg.py    validation, projection and CI gate (stdlib Python)
tests/               unit tests (python3 -I -m unittest discover -s tests)
docs/                operations, governance, Auditor contract, handoff
standards/           pointers to the Skill standard
.github/             CODEOWNERS, pull request template, validate-skills workflow
```

See [CONTRIBUTING.md](CONTRIBUTING.md) to propose a change.
