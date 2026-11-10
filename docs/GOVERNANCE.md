# Governance: review, approval and repository settings

**Approval is human code-owner review.** A change is approved when a human code owner, who is not the author, reviews and approves the pull request, and it is merged into `main`. Admin access alone does not approve any skill. Skills Auditor is paused, and an Auditor result is not required for a merge (see [AUDITOR-CONTRACT.md](AUDITOR-CONTRACT.md)).

## How a change is approved

1. A skill is a folder, `skills/<id>/`, with a `SKILL.md` at its root. Every change to it, new or update, arrives as a pull request.
2. Automated checks run on the pull request. They support the reviewer and never approve.
3. A human code owner other than the author reviews the exact change and approves. For an assisted submission, the maintainer who opens the pull request is its author, so a different code owner approves.
4. The pull request merges. Git history is the version history.

Code owners are defined in [`.github/CODEOWNERS`](../.github/CODEOWNERS). They must be real, verified GitHub users or teams; never add guessed handles.

## What the automated checks guard

CI runs the copy of the checking tool that is on `main`, against the pull request's files. A pull request therefore cannot change the rules that judge it. The table says where each check runs: across the **whole repository** (everything except `.git`), or in **each skill folder** (every folder directly under `skills/`). For the exact behaviour, read `tools/` and `tests/`.

| Contributor attempt | Intended result | Where it is checked |
| --- | --- | --- |
| Edit the checking tool so a change passes | The edit is ignored for that pull request, because CI runs the copy of the tool that is on `main` | CI |
| Use an unsafe file or folder name (backslash, control character or drive letter) | Fails | Whole repository |
| Commit a symbolic link | Fails | Whole repository |
| Commit a ZIP file, whether or not it is named `.zip` | Fails | Whole repository |
| Put a `SKILL.md` anywhere other than `skills/<id>/SKILL.md`, or leave a loose file directly in `skills/` | Fails | Whole repository |
| Use a folder name that is not a valid skill id, leave out `SKILL.md` or the required frontmatter, or give `name` a value that differs from the folder name | Fails | Each skill folder |
| Commit a file type that is not allowed, a file over the size limit, a skill folder over the size or file-count limit, or two names that differ only in upper/lower case | Fails | Each skill folder |
| Change a skill without raising its `version` | Warning only | Each skill folder, on pull requests only (it compares with `main`) |
| Weaken the checks by editing `.github/workflows/` | Possible: a workflow can be edited in the same pull request | Not a check. Needs code-owner review, which the ruleset below requires once applied |
| Approve or merge your own change | Blocked only when the repository settings below are applied | Not a check. The ruleset on `main` |

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
