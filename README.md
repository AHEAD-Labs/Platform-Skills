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

```text
skills/
└── example-skill/          <- the folder name is the skill's id
    ├── SKILL.md            <- required, at the top of the folder
    └── references/         <- optional: any extra files the skill needs
        └── notes.md
```

`SKILL.md` starts with a short block of frontmatter:

```markdown
---
# Required
name: example-skill                  # same as the folder name
description: One or two sentences on what the skill does and when to use it.

# Recommended (leaving one out is a warning, not a failure)
version: 1.0.0                       # bump it on every update
owner: your-github-handle            # a GitHub handle or a role; no contact details
team: Your Team
ahead-platform: [Claude, Glean]      # which platform(s) the skill is for
audience: Who the skill is for
publication-status: Draft
# glean-link:                        # add once the skill is published in Glean
# claude-link:                       # add once the skill is published in Claude
---

# Example skill

The instructions the assistant follows go here, in plain Markdown.
```

Only `name` and `description` are required.

## Package philosophy

- **The folder is the format.** A skill is a folder `skills/<id>/` with a `SKILL.md` at its root. That folder is what this repository stores and what reviewers read.
- **A ZIP is only an export.** Some tools, such as Glean, can export a skill as a ZIP. If you start from one, unzip it into the skill's folder and commit the folder, never the ZIP.
- **Platform is a frontmatter field.** `ahead-platform` says whether a skill is for Claude, Glean or both. It is never a folder, so every skill sits directly under `skills/`.
- **Git history is the version history.** Bump `version` on every update; git records each change, who reviewed it and why.

## Starting from a Glean export

1. Unzip the export into `skills/<id>/`, so that `SKILL.md` is at the root of that folder and not inside a wrapper folder.
2. Make sure `name` in `SKILL.md` matches the folder name.
3. Open the pull request and choose **Glean export** as the origin. It gets the same checks and review as any other change.

## No GitHub account?

Send the skill folder (or the Glean export) to a Platform-Skills maintainer through your team's internal chat. The maintainer places it in `skills/<id>/`, sets you as `owner` in the frontmatter, and opens the pull request with the origin **assisted**. You remain the owner of the skill. Because the maintainer authors that pull request, a different code owner must review and approve it.

## Who reviews

The rule: every merge into `main` needs approval from a **human code owner who is not the author of the change**. Code owners are defined in [`.github/CODEOWNERS`](.github/CODEOWNERS). Automated checks help the reviewer; they do not approve anything, and having admin access is not approval either. The repository settings that enforce this rule are described in [docs/GOVERNANCE.md](docs/GOVERNANCE.md).

## What the automated checks do

They run on every pull request. They scan the repository for unsafe paths, symlinks, file types that are not allowed and files that are too large, and they read each skill folder's `SKILL.md`.

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

## Repository layout

```text
skills/<id>/SKILL.md   one folder per skill (plus any files the skill needs)
standards/             pointers to skill-writing standards
docs/                  governance and maintainer notes
tools/  tests/         the checking tool that CI runs, and its tests
.github/               CI workflow, pull request template, code owners
CONTRIBUTING.md        how to propose and review a change
```

| Doc | Contents |
| --- | --- |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to add, update and review a skill |
| [docs/GOVERNANCE.md](docs/GOVERNANCE.md) | Approval authority and required repository settings |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Notes for maintainers: assisted submissions, rollback |

Skills Auditor, an earlier audit step, is **paused** and not required for a merge; see [docs/AUDITOR-CONTRACT.md](docs/AUDITOR-CONTRACT.md).
