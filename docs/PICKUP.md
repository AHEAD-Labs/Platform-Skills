# Pick up where Akbar left off

For the engineer or reviewer continuing Platform-Skills during or after the 2026-10-19 → 10-31 PTO. Read this first. It links to the deeper docs rather than repeating them.

## 1. Orientation (about 30 minutes)
1. [README](../README.md): what the repo is, and the two-repo model (Skills Auditor audits, Platform-Skills holds the approved source).
2. [OPERATIONS](OPERATIONS.md): submit, update, audit, approve, project, Glean release, rollback.
3. [GOVERNANCE](GOVERNANCE.md): who can approve, the trust boundaries, and the required branch protection.
4. [AUDITOR-CONTRACT](AUDITOR-CONTRACT.md): the Auditor interface and why it is not in CI yet.
5. Run the checks yourself:
   ```
   git clone https://github.com/AHEAD-Labs/Platform-Skills && cd Platform-Skills
   python3 -I -m unittest discover -s tests       # 48 tests, OK
   git worktree add --detach ../ps-main origin/main
   python3 -I tools/skillpkg.py plan --trusted-root ../ps-main
   python3 -I tools/skillpkg.py ci   --trusted-root ../ps-main   # CI OK: {}  (exit 0)
   ```

## 2. State snapshot (verified 2026-10-19; re-check with the commands shown)
| Item | State | Re-check |
| --- | --- | --- |
| Tooling, CI, docs | On `main` via #4 (`1f793b0`). Merged by its author without independent review | `git log --oneline -3 origin/main` |
| #7 Priority 1 (ratify #4, ruleset, CODEOWNERS) | Open, assigned to Joe and Grace | `gh pr view 7` |
| #5 Seed ZIP baselines | Draft. Gate shows the expected POLICY BLOCK | `gh pr checks 5` |
| #6 Auditor integration proposal | Draft | `gh pr view 6` |
| Branch protection on `main` | **None** (0 rules) | `gh api repos/AHEAD-Labs/Platform-Skills/rules/branches/main --jq length` |
| Skills Auditor v1 | Skills-Marketplace **#114 open, not merged** (head `45dd7a7`). Report schema `skills-auditor-report-v1` is compatible | `gh pr view 114 -R AHEAD-Labs/Skills-Marketplace` |
| Approved Platform Skills / Glean imports from this repo | **None yet** | `ls provenance projections/glean 2>/dev/null` |

## 3. Documentation gap audit (2026-10-19)
"Fixed here" means fixed in the PR that adds this file. "After #7" means it touches a file that #7 also edits, so it is left for a follow-up to avoid merge conflicts.

| # | Where | Gap | Status |
| --- | --- | --- | --- |
| G1 | README "Next execution sequence", "Initial Landing Set" | Said the seed ZIPs were staged in `skills/shared/` on `main`; they are only in draft #5 | Fixed here |
| G2 | README "What this is not", "What does not belong", diagram | Said candidates are audited *before* reaching the repo; in practice they are submitted by PR here and CI blocks them until audited | Fixed here |
| G3 | README "Glean pilot status", validation matrix | Missing the 2026-10-13 findings (ZIP-URL import failed, sync is one-way, manual Skills do not convert); ZIP-vs-folder was shown as fully open although the projection is built | Fixed here |
| G4 | README "Version history" | `git log` path did not match the layout | Fixed here |
| G5 | CONTRIBUTING | Described a pre-pipeline flow: no ZIP-only rule, no CI commands, no POLICY BLOCK expectation | Fixed here |
| G6 | skills/README | Suggested Skill *directories* are allowed (the gate rejects loose `SKILL.md`); `glean/` described as "published" | Fixed here |
| G7 | PR template | Required "was audited" before the PR, although the audit runs on the PR | Fixed here |
| G8 | AUDITOR-CONTRACT | Said the Auditor branch was local only; it is now Skills-Marketplace #114 | Fixed here |
| G9 | OPERATIONS | Gaps: no Python prerequisite, no way to fetch the approved baseline for a delta audit, no statement that a Skill PR cannot currently go green, no location for `approval.json` | Fixed here |
| G10 | PTO handoff, GOVERNANCE | Should link this file and the D2 decision | After #7 |
| G11 | Repo root | No `SECURITY.md` for a public repo | Deliverable D12 |
| G12 | Glean release steps | Written from meeting findings and never exercised; no admin-UI specifics | Deliverable D6 |

## 4. Deliverables to pick up (priority order)
| ID | Deliverable | Proposed owner | Depends on | Done when |
| --- | --- | --- | --- | --- |
| **D1** | Merge #7: independent review of #4, `main` ruleset, CODEOWNERS | Joe or Grace | none | #7 merged by a non-author; `rules/branches/main` lists PR, approval, checks and force-push rules; `gh api repos/AHEAD-Labs/Platform-Skills/codeowners/errors --jq '.errors|length'` → 0 |
| **D2** | **Decide the interim audit path.** Until D7, `skill-policy-gate` blocks *every* Skill PR, so no Skill can be approved through the normal route | Joe and Grace, with the Auditor owner | D1 | Written decision in GOVERNANCE.md. Either (a) no Skill merges until D7, or (b) a recorded admin bypass with the REVIEW_READY report hash and Auditor SHA in the PR, report kept internal |
| **D3** | Merge Skills Auditor #114 and nominate a pinned SHA | Auditor owner (Akbar on return, or a delegate) | none | Merged on Skills-Marketplace `main`; SHA recorded in AUDITOR-CONTRACT.md |
| D4 | Decide #5 (seed ZIPs as unapproved baselines vs. keeping them off `main`) | Joe or Grace | D1 | #5 merged, closed, or split (baseline file first) |
| D5 | First Skill end to end: fix REVISE findings in Glean, re-export, full audit → REVIEW_READY, project, merge | Owning FDE + reviewer | D2, D3 | `provenance/<id>.json` and `projections/glean/<id>/` on `main` via a reviewed PR |
| D6 | First Glean folder import from `main`, then rewrite the OPERATIONS "Glean release" section from what was actually observed | Grace / Isha (Glean admins) | D5 | Observed import recorded in provenance `glean`; legacy copy handled; runbook updated |
| D7 | Implement #6: internal runner, GitHub App, required `skills-auditor/result` status | Auditor owner + org admin | D3 | Status appears on a Platform-Skills PR and is required on `main` |
| D8 | `provenance.source_zip` records the path as passed (an absolute path leaks a local directory and differs between machines). Store it repo-relative; test first | Any engineer | none | New test; `project` with an absolute path writes `skills/shared/<id>.zip` |
| D9 | Pin Python in CI (`actions/setup-python` by SHA); today it uses the runner's system `python3` | Any engineer | D1 (workflow change needs code-owner review) | Workflow pins a version; both jobs green |
| D10 | Require `version:` in `SKILL.md` and a version bump on delta updates (e.g. `outlook-event-creation` has none, so provenance records an empty version) | Any engineer + Enterprise GPT for the rule | none | Tests for missing version and unchanged version on update |
| D11 | Release tag per approval (`<id>/v<version>` on the merge commit) linking the Glean version to the git commit | Joe or Grace | D5 | Tag scheme documented in OPERATIONS; first tag pushed |
| D12 | `SECURITY.md` plus private vulnerability reporting for this public repo | An admin | none | Setting enabled; file says how to report |
| D13 | Glean Skills API adapter ([cookbook](https://developers.glean.com/cookbook/skill-publishing-pipeline)), behind a manual-approval environment. Not alongside GitHub import on production Skills | Enterprise GPT, with admin sign-off | D6 | Design PR approved before any credential is created |
| D14 | Claude distribution (stage two) | Enterprise GPT | D6 | Separate proposal |

## 5. Decisions already made (do not reopen without the owners)
- The ZIP exported from Glean is the canonical source. The Glean folder is generated, never hand-edited.
- New Skill → full audit; update to an approved Skill → delta audit against the version on `main`.
- Approval = an independent GitHub review and merge on protected `main`. JSON approval records are unauthenticated claims. Admin rights are not Skill approval.
- The CI gate trusts only the base branch and trusted Auditor output. It fails closed. No audit result is ever fabricated.
- Glean publication is manual and admin-controlled; GitHub is the only writer for imported Skills.
- The repo is intentionally public. Audit findings stay in the internal Auditor repo.
- Reviewers and code owners are Joe (`@JoeVaderRules`) and Grace (`@babiryegrace20`), pending confirmation in #7. Meredith is an admin for visibility only, not a reviewer.

## 6. Resume block for a fresh Claude Code session
Paste this into a new session started in a clone of this repo.
```
## Session Handoff: Platform-Skills pickup

**Objective**: Keep the Glean-first Platform Skills pipeline (ZIP → PR → deterministic gate + Skills Auditor → independent review → main → manual Glean import) moving during Akbar's PTO.

**Status**: Tooling is on main (#4, 1f793b0, unreviewed). #7 (review + branch protection + CODEOWNERS) is open for Joe/Grace. #5 and #6 are drafts. No Skill is approved or imported yet.

**Done**:
- tools/skillpkg.py: validate/plan/project/verify/ci; 48 tests in tests/
- .github/workflows/validate.yml: unit-tests + skill-policy-gate (pull_request, read-only, base-branch tool)
- docs/: OPERATIONS, GOVERNANCE, AUDITOR-CONTRACT, PICKUP, PTO-HANDOFF-2026-10-19

**In progress / next action**:
- Check whether #7 has merged (`gh pr view 7`). If it has, take deliverable D2 in docs/PICKUP.md; otherwise remind Joe/Grace that D1 comes first.

**Key decisions (do not re-litigate)**:
- See docs/PICKUP.md section 5.

**Open questions**:
- D2 interim audit path; D4 seed baselines; D7 runner location and App ownership.

**To resume**: Resolve the open questions above with Joe and Grace first, then proceed in the deliverable order in docs/PICKUP.md section 4. Never modify the Skills-Marketplace repo from here, never merge your own PR, never fabricate an audit.
```
