# PTO handoff (Akbar, out 2026-10-19 to 10-31)

Platform-Skills is intentionally **public**. Anything committed here must be suitable for public view.

## State at handoff
| Item | Where | Status |
| --- | --- | --- |
| A. Tooling, tests, read-only CI, docs | PR A (`release/skill-pipeline-tools`) | Open, awaiting independent review |
| B. Skills Auditor integration + CODEOWNERS/branch protection | PR B (`proposal/auditor-integration`, draft) | Needs Auditor-owner and admin decisions |
| C. Six seed ZIP exports + baseline hashes | PR C (`pilot/seed-baseline`, draft) | Blocked by design until baseline is admin-approved or Skills are audited |
| Old branch `glean-platform-skills-pilot` | origin `5e83f4d` (ZIP staging) | Superseded by A + C. Do not merge it directly. |

Nothing was merged to `main`: there is no independent reviewer for my own PRs, and the author does not approve their own PR.

PR links and the remote CI run are listed at the end of this file.

## IMPLEMENTED AND TESTED (48 unit tests, `python3 -I -m unittest discover -s tests`)
- `tools/skillpkg.py` (stdlib only, no tokens or LLM key) provides validate, plan, project, verify and ci.
- ZIP safety: traversal, absolute and backslash paths, symlink and special entries, duplicate paths (case-insensitive), encrypted entries, file-type allowlist, size and entry limits, root `SKILL.md` whose `name` matches the id.
- Full vs delta: a Skill already approved on `main` (has `provenance/<id>.json`) requires a delta audit, otherwise a full audit. Mismatched reports are rejected.
- Real Auditor report schema (`skills-auditor-report-v1`): requires `REVIEW_READY`, the exact package sha256, and the matching mode.
- Deterministic, idempotent projection and provenance. Edited, extra or missing files are rejected. Projecting a seed baseline is rejected.
- Trust boundaries (see GOVERNANCE.md): the gate ignores PR edits to baselines, audit and approval JSON, and the tool itself. Hidden ZIPs, loose `SKILL.md` folders and symlinks fail.
- Seed ZIPs verified byte-identical: `sha256sum` matches the hashes in PR C.

## IMPLEMENTED, REMOTE RESULT RECORDED BELOW
- `.github/workflows/validate.yml` has jobs `unit-tests` and `skill-policy-gate`. Trigger is `pull_request`, permissions `contents: read`, no secrets, pinned checkout.

## PROPOSED / NOT IMPLEMENTED
- Auditor in CI (AUDITOR-CONTRACT.md). It must run on the internal side and post the status `skills-auditor/result`.
- Glean Skills API adapter. Automated Glean import.

## BLOCKED ON APPROVAL OR VENDOR
- **Auditor owner:** push and merge Skills-Marketplace `db4d148` (local only at handoff) and nominate a pinned SHA.
- **Org admin:** GitHub App for the status-posting design.
- **Admins (Joe, Grace or Meredith):** branch protection ruleset and CODEOWNERS with verified handles (GOVERNANCE.md).
- **Seed Skills:** a local Auditor run returned REVISE for all six. The FDE or owner must fix and re-export before any can be approved.
- **Glean (vendor):** ZIP-URL import fails. Still open: refresh cadence, tenant behaviour, roadmap, and the migration path for manual org Skills.

## Responsibilities
- **Domain team / FDE:** Skill content, functional tests, fixing REVISE findings, re-exporting.
- **Enterprise GPT reviewers:** audit review and independent PR approval. Never the author.
- **Admins:** settings, baseline-hash changes, workflow and tool changes.
- **Glean admins (Grace/Isha):** manual import from `main`, legacy-copy deactivation, recording the observed deployment state.

Admin rights are not Skill approval. Technical ownership after PTO is **proposed** to Joe (with Grace for Glean distribution) and **not yet accepted**. Escalation: Meredith (Enterprise GPT governance).

## Next actions for Joe and Grace
1. Review and merge PR A (any reviewer other than Akbar). Check that `unit-tests` and `skill-policy-gate` are green on it.
2. Apply the `main` ruleset and CODEOWNERS (GOVERNANCE.md). Require `unit-tests` and `skill-policy-gate`.
3. Decide PR C: merge `skills/baseline-hashes.json` alone first, after admin review (seeds are allowed as unapproved). After that the ZIPs pass as baseline. Or keep the seeds off `main` until they are audited.
4. With the Auditor owner, choose the PR B design and create the App.
5. Pick one Skill, fix its REVISE findings, run the full audit to REVIEW_READY, project it, merge, then run a manual Glean folder import from `main` and record the result (OPERATIONS.md).
