# Governance: review, approval and branch protection

**Approval authority** is a reviewed and merged pull request on protected `main`, approved by someone other than the author. Admin access alone does not approve any Skill. JSON approval records are unauthenticated claims, kept only as provenance.

## Trust boundaries (reviewed 2026-10-19)
| Contributor attempt | Result | Control |
| --- | --- | --- |
| Edit `skills/baseline-hashes.json` to authorize their ZIP | Ignored in that PR; still POLICY BLOCK | Gate reads the baseline from the base revision (tested) |
| Commit a forged passing audit report | Ignored | Gate accepts audit reports only via `--auditor-reports` from a trusted run, never committed files (tested) |
| Forge approval JSON | No effect on CI. `project` treats it as an unauthenticated claim | PR review and branch protection |
| Edit `tools/skillpkg.py` to pass | Ignored once the tool is on `main` | Gate runs the base branch's tool (bootstrap PR excepted) |
| Edit `.github/workflows/validate.yml` | **Possible** | CODEOWNERS on `.github/**` plus required review. **Admin action needed** |
| Tamper with a projection or provenance | Fails (exit 1) | `verify` compares every file against the ZIP (tested) |
| Project an unapproved seed ZIP | Fails | Gate rejects projections of baseline ZIPs (tested) |
| Hide a ZIP as `.ZIP`, outside `skills/`, or by renaming it (PK magic bytes) | Fails (exit 1) | Whole-tree scan; packages are allowed only at `skills/{claude,glean,shared}/<id>.zip` (tested; found by security review 2026-10-19) |
| Commit a loose `SKILL.md` folder that Glean could import | Fails | `SKILL.md` is allowed only under `projections/glean/<id>/` (tested) |
| Commit symlinks to redirect reads or writes | Fails | Symlinks are rejected anywhere in the tree, and `project` refuses symlinked outputs (tested) |
| New or changed ZIP with no trusted Auditor result | POLICY BLOCK (exit 2) | No bypass in code (tested) |

## Required repository settings (applied by Joe or Grace; not yet applied)

Reviewers and code owners: **Joe and Grace**. Meredith has admin access for visibility only. She is **not** a code owner or a PR reviewer.
Checked 2026-10-19: `main` has **no branch protection**, and `.github/CODEOWNERS` is a placeholder. Apply a ruleset on `main`:
- Require a pull request. Require at least 1 approval, dismiss stale approvals on push, and require approval of the most recent push by someone other than the pusher.
- Require code owner review once CODEOWNERS holds real handles.
- Require status checks `unit-tests` and `skill-policy-gate` (and `skills-auditor/result` once it exists). Require branches to be up to date.
- Block force pushes and branch deletion. Do not grant a bypass list (or keep it emergency-only and logged).
- Do not enable auto-merge.

CODEOWNERS is set in `.github/CODEOWNERS` (Joe `@JoeVaderRules`, Grace `@babiryegrace20`). Narrower path rules (`.github/`, `tools/`, `skills/baseline-hashes.json`) can be added later if the team grows.
