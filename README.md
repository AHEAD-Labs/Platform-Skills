# Platform-Skills: the reviewed, shared home for AHEAD skills

Platform-Skills holds AHEAD-managed **skills** as plain folders in git. A skill is a folder of instructions (plus any files it needs) that teaches an AI assistant, such as Claude or Glean, how to do one job well. Each skill here has an owner, a reviewer and a version history.

- **Belongs here:** skill folders, and guidance on writing and reviewing them.
- **Does not belong here:** credentials, tokens, client data, or anything you would not put on a public web page. This repository is public.

## Add or update a skill in 3 steps

1. **Make a folder** `skills/<id>/` with a `SKILL.md` at the top of it. `<id>` uses lowercase letters, digits and hyphens, and matches `name` inside the file. To update a skill, edit its folder and bump `version`.
2. **Open a pull request** into `main` and fill in the template.
3. **A reviewer who isn't you approves it.** The rule: every merge needs approval from a human code owner other than the author. Then it merges.

**If a check fails,** the message says what to fix. Fix it, push again, and the checks re-run.

**No GitHub account?** Send the folder to a Platform-Skills maintainer through your team's internal chat. The maintainer opens the pull request for you, and you stay the skill's `owner`. ([Details](#no-github-account))

Not sure what a skill folder looks like? See [Skill folder at a glance](#skill-folder-at-a-glance).

## Skill folder at a glance

```markdown
---
name: my-skill-id
description: One or two sentences on what the skill does and when to use it.
version: 1.0.0
owner: your-github-handle
---
```

`name` and `description` are required. `version`, `owner`, `team`, `ahead-platform`, `audience`, `publication-status`, `glean-link` and `claude-link` are recommended; leaving one out is a warning, not a failure.

## Starting from a Glean export

Unzip the export into `skills/<id>/` so that `SKILL.md` is at the root of that folder (not inside an extra wrapper folder). Do not commit the ZIP itself: a ZIP is an export format, not the format this repository stores. Choose **Glean export** as the origin in the pull request. It goes through the same checks and review as any other change.

## No GitHub account?

Send the skill folder (or the Glean export) to a Platform-Skills maintainer through your team's internal chat. The maintainer places it in `skills/<id>/`, sets you as `owner` in the frontmatter, and opens the pull request with the origin **assisted**. You remain the owner of the skill. Because the maintainer authors that pull request, a different code owner must review and approve it.

## Who reviews

The rule: every merge into `main` needs approval from a **human code owner who is not the author of the change**. Code owners are defined in [`.github/CODEOWNERS`](.github/CODEOWNERS). Automated checks help the reviewer; they do not approve anything, and having admin access is not approval either. The repository settings that enforce this rule are described in [docs/GOVERNANCE.md](docs/GOVERNANCE.md).

## What the automated checks do

They run on every pull request, using the copy of the checking tool that is on `main`, so a pull request cannot change the rules that judge it. They scan the whole tree for unsafe paths, symlinks, file types outside the allowed list and files over the size limits, and they read each skill folder's `SKILL.md`. A failed check is meant to say what is wrong and how to fix it.

## What belongs here, and what does not

Belongs here:

- skill folders under [`skills/`](skills/README.md)
- short pointers to writing standards under [`standards/`](standards/README.md)
- contribution, review and governance guidance

Does not belong here:

- credentials, API keys, tokens or other secrets
- client data or other confidential material
- runtime infrastructure, deployment or sync tooling

## Publishing to Glean or Claude

Merging a pull request adds or updates a skill **in this repository**. It does not publish the skill to Glean or Claude, and nothing here syncs with either platform or has been verified to. The optional `glean-link` and `claude-link` frontmatter fields are pointers that a skill's owner maintains by hand.

## Skills Auditor (paused)

Skills Auditor was an earlier audit step for this repository. It is **paused**: an Auditor result is not required for a pull request to merge, and approval is the human code-owner review described above. The old integration notes are kept for reference in [docs/AUDITOR-CONTRACT.md](docs/AUDITOR-CONTRACT.md).

## Repository layout

```text
skills/<id>/SKILL.md   one folder per skill (plus any files the skill needs)
standards/             pointers to skill-writing standards
docs/                  governance, operations and background
tools/  tests/         the checking tool that CI runs, and its tests
.github/               CI workflow, pull request template, code owners
CONTRIBUTING.md        how to propose and review a change
```

| Doc | Contents |
| --- | --- |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to add, update and review a skill |
| [docs/GOVERNANCE.md](docs/GOVERNANCE.md) | Approval authority, trust boundaries, required repository settings |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Notes for maintainers: assisted submissions, rollback |
| [docs/AUDITOR-CONTRACT.md](docs/AUDITOR-CONTRACT.md) | Skills Auditor integration notes (**paused**) |
| [docs/PTO-HANDOFF-2026-10-19.md](docs/PTO-HANDOFF-2026-10-19.md) | Handoff note from 2026-10-19 (**historical**) |
