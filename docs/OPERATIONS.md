# Platform-Skills operations guide

Flow: export the ZIP from Glean → PR → deterministic validation → **Skills Auditor** (full or delta) → human review → merge to `main` (approved) → manual Glean import.
Items marked **works today** are in `tools/skillpkg.py` (Python 3 standard library, no tokens or LLM key) and covered by `tests/`.

## Layout
| Path | Purpose |
| --- | --- |
| `skills/shared/<id>.zip` | Canonical source package (as exported from Glean). Never edited by tools. |
| `skills/baseline-hashes.json` | Seed exports that may exist **unapproved** (exact sha256). Trusted only from `main`. |
| `projections/glean/<id>/` | Generated Glean-readable folder (`SKILL.md` at root). Never hand-edited. |
| `provenance/<id>.json` | ZIP hash, per-file hashes, audit summary, approval claim, Glean deployment state. Its presence on `main` marks `<id>` as approved, so the next change needs a **delta** audit. |

## Commands (works today)
```
python3 -I -m unittest discover -s tests                     # 48 tests
python3 -I tools/skillpkg.py validate skills/shared/<id>.zip --skill-id <id>
python3 -I tools/skillpkg.py plan --trusted-root <checkout-of-main>   # full vs delta per ZIP
python3 -I tools/skillpkg.py ci   --trusted-root <checkout-of-main> [--auditor-reports DIR]
```
`ci` exit codes: 0 OK; **1** invalid, unsafe or tampered; **2** POLICY BLOCK (no trusted REVIEW_READY audit). To make a checkout of main: `git worktree add --detach /tmp/ps-main origin/main`.

## New Skill (citizen/FDE)
1. Export the ZIP from Glean. Do not unzip or edit it. Its frontmatter `name:` must equal the file stem.
2. Branch `submit/<id>`, add `skills/shared/<id>.zip`, open a PR, and tick **New Skill (full audit)** in the template.
3. `unit-tests` should pass. `skill-policy-gate` will show **POLICY BLOCK** until a trusted Auditor result exists. That is expected, not a broken build.

## Update an existing Platform Skill
Replace the ZIP on `update/<id>`. Because `provenance/<id>.json` exists on `main`, `plan` reports `delta` with the approved ZIP as the baseline, and a full-mode report is rejected.

## Audit (until CI integration lands, see AUDITOR-CONTRACT.md)
An engineer with internal Auditor access runs it locally on the exact ZIP:
```
python3 -I <Skills-Marketplace>/scripts/skills_auditor.py full  skills/shared/<id>.zip --json /tmp/<id>.json --md /tmp/<id>.md
python3 -I <Skills-Marketplace>/scripts/skills_auditor.py delta skills/shared/<id>.zip --baseline <approved.zip> --json ... --md ...
```
Keep reports in the internal repo or ticket. **Do not commit audit findings to this public repo.** REVISE or BLOCK: the owning FDE fixes the Skill in Glean, re-exports it and pushes a new commit, and the audit is re-run. Never edit a report.

## Approve and project (after REVIEW_READY plus an independent reviewer)
```
python3 -I tools/skillpkg.py project skills/shared/<id>.zip --skill-id <id> --audit /tmp/<id>.json --approval approval.json
python3 -I tools/skillpkg.py verify  skills/shared/<id>.zip --skill-id <id>
```
`approval.json`: `{"skill_id","package_sha256","decision":"approved","author","approved_by","approved_at","pull_request"}`. It is stored as `approval_claim_unauthenticated`. The real approval is the GitHub review and merge. Commit `projections/glean/<id>/` and `provenance/<id>.json` in the same PR. Before committing, check that the Skill's `sensitivity` is suitable for a **public** repository.

## Glean release (manual, admin-controlled; not yet exercised end to end)
1. After merge, note the merge commit SHA.
2. In Glean admin, use GitHub import on the folder path `projections/glean/<id>/` on `main` (folder or `SKILL.md` path; ZIP URLs failed on 2026-10-13). Import is **one-way** (GitHub → Glean).
3. **Avoid duplicates:** existing manual org Skills are not converted automatically. Note the legacy Skill, confirm the imported copy works, then deactivate the legacy copy deliberately. Do not edit the imported Skill in Glean, because GitHub must be the only writer.
4. **Confirm source link and version:** the Glean Skill should show the GitHub source, and its `SKILL.md` `version:` should equal `provenance/<id>.json` `version`.
5. Record the observed state in a PR updating `provenance/<id>.json` → `glean`: `git_commit`, `source_url`, `deployment_state: "imported"`. Only record this once seen in Glean.

## Rollback
`git revert <merge-commit>` in a reviewed PR (it restores the ZIP, projection and provenance together), then the Glean admin re-imports or re-syncs and records the state. To fetch an old package: `git show <commit>:skills/shared/<id>.zip > old.zip`.

## Troubleshooting
| Message | Fix |
| --- | --- |
| `unsafe path` / `special file or symlink` / `duplicate` / `file type not allowed` / `too large` | Re-export a clean ZIP. Allowed types: md txt json py html css yaml yml csv png jpg, LICENSE*. |
| `SKILL.md must be at the archive root` | Export without a wrapper folder. |
| `does not match expected skill id` | Frontmatter `name:` must equal the ZIP file name. |
| `POLICY BLOCK ... no trusted Skills Auditor result` | Expected until audited. See the Audit section. |
| `requires a delta audit` / `requires a full audit` | Re-run the Auditor in the mode shown by `plan`. |
| `not REVIEW_READY` | Fix the findings and resubmit. |
| `projection ... differs` / `unexpected file` | Re-run `project`. Never hand-edit. |
| `baseline packages ... must not be projected` | Seed ZIPs are unapproved. Audit them first. |
| `unit-tests` red | Tooling bug. Run the unit tests locally. |

## Second adapter (not implemented)
Glean's Skills API publishing cookbook (https://developers.glean.com/cookbook/skill-publishing-pipeline) uploads packages directly. It is a separate adapter and **does not prove GitHub ZIP-URL import works**. Do not run both against production Skills. It would need a service credential, a protected manual-approval environment, and admin sign-off.
