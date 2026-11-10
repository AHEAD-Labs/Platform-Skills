# Governance: review, approval and repository settings

**Approval is human code-owner review.** A change is approved when a human code owner, who is not the author, reviews and approves the pull request, and it is merged into `main`. Admin access alone does not approve any skill. Skills Auditor is paused, and an Auditor result is not required for a merge (see [AUDITOR-CONTRACT.md](AUDITOR-CONTRACT.md)).

## How a change is approved

1. A skill is a folder, `skills/<id>/`, with a `SKILL.md` at its root. Every change to it, new or update, arrives as a pull request.
2. Automated checks run on the pull request. They support the reviewer and never approve.
3. A human code owner other than the author reviews the exact change and approves. For an assisted submission, the maintainer who opens the pull request is its author, so a different code owner approves.
4. The pull request merges. Git history is the version history.

Code owners are defined in [`.github/CODEOWNERS`](../.github/CODEOWNERS). They must be real, verified GitHub users or teams; never add guessed handles.

## What the automated checks guard

CI runs the copy of the checking tool that is on `main`, against the pull request's files. A pull request therefore cannot change the rules that judge it. The table lists what each control is for. For the exact behaviour, read `tools/` and `tests/`.

| Contributor attempt | Intended result | Control |
| --- | --- | --- |
| Edit the checking tool so a change passes | The edit is ignored for that pull request | CI runs the base-branch copy of the tool |
| Hide a file with a path that escapes the tree (traversal, absolute path, case-only duplicate) | Fails | Whole-tree scan with path safety |
| Commit a symlink to redirect reads or writes | Fails | Symlinks are rejected anywhere in the tree |
| Commit a file type that is not on the allowed list, or a file over the size limit | Fails | File-type allowlist and size limits |
| Commit a skill folder without `SKILL.md` at its root, or whose `name` differs from the folder name | Fails | Skill folder check |
| Weaken the checks by editing `.github/workflows/` | Possible: a workflow can be edited in the same pull request | Code-owner review of every change, enforced by the ruleset below |
| Approve or merge your own change | Blocked only when the repository settings below are applied | Ruleset on `main` |

## Required repository settings

Admins apply these in GitHub, outside the files in this repository, so this document cannot tell you whether they are on. Check them with the commands at the end of this section.

**Ruleset on `main`:**

- Require a pull request before merging, with at least 1 approval.
- Dismiss stale approvals when new commits are pushed.
- Require approval of the most recent push by someone other than the person who pushed it.
- Require review from code owners.
- Require the status checks defined in `.github/workflows/validate.yml`, and require branches to be up to date.
- Block force pushes and branch deletion.
- Leave the bypass list empty, or restrict it to emergencies and record the reason in the pull request.
- Do not enable auto-merge.

**Actions settings:**

- Default workflow permissions: read only.
- Do not allow GitHub Actions to create or approve pull requests. Approval must come from a human.

**Check the settings:**

```sh
gh api repos/AHEAD-Labs/Platform-Skills/rules/branches/main
gh api repos/AHEAD-Labs/Platform-Skills/actions/permissions/workflow
```

An empty list from the first command means `main` has no enforced rules. In the second, `default_workflow_permissions` should be `read` and `can_approve_pull_request_reviews` should be `false`.
