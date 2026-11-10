# Platform-Skills: the reviewed, shared home for AHEAD skills

Platform-Skills holds AHEAD-managed **skills** as plain folders in git. A skill is a folder of instructions (plus any files it needs) that teaches an AI assistant, such as Claude or Glean, how to do one job well. The rule here is that someone other than the author reviews every change, and git keeps each skill's version history.

- **Belongs here:** skill folders, and guidance on writing and reviewing them.
- **Does not belong here:** credentials, tokens, client data, or anything you would not put on a public web page. This repository is public.

## Add or update a skill in 3 steps

1. **Make a folder** `skills/<id>/` with a `SKILL.md` at the top of it. `<id>` uses lowercase letters, digits and hyphens, and matches `name` inside the file. To update a skill, edit its folder and bump `version`.
2. **Open a pull request** into `main` and fill in the template.
3. **A reviewer who isn't you approves it.** The rule: every merge needs approval from a human code owner other than the author. Then it merges.

**If a check fails,** the message says what to fix. Fix it, push again, and the checks re-run. ([More](#if-a-check-fails))

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
owner: your-github-handle            # a team name or GitHub handle
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

1. Unzip the export into `skills/<id>/`, so that `SKILL.md` is at the root of that folder and not inside a wrapper folder. If unzipping made an extra folder (`skills/<id>/<id>/SKILL.md`), move its contents up one level.
2. Make sure `name` in `SKILL.md` matches the folder name.
3. Open the pull request and choose **Glean export** as the origin. It gets the same checks and review as any other change.

## No GitHub account?

Send the skill folder (or the Glean export) to a Platform-Skills maintainer through your team's internal chat. The maintainer places it in `skills/<id>/`, sets you as `owner` in the frontmatter (by team name or handle, as for any skill), and opens the pull request with the origin **assisted**. You remain the owner of the skill. Because the maintainer authors that pull request, a different code owner must review and approve it.

## Who reviews

The rule: every merge into `main` needs approval from a **human code owner who is not the author of the change**. Code owners are defined in [`.github/CODEOWNERS`](.github/CODEOWNERS). Automated checks help the reviewer; they do not approve anything, and having admin access is not approval either. The repository settings that administrators apply to enforce this rule are described in [docs/GOVERNANCE.md](docs/GOVERNANCE.md).

## What the automated checks do

They run on every pull request, and you can run the same check yourself (see below).

- **Across the whole repository** (everything except `.git`): unsafe file and folder names, symbolic links, ZIP files (by name or by content), a `SKILL.md` anywhere other than `skills/<id>/SKILL.md`, and loose files directly in `skills/`.
- **In each skill folder** (every folder directly under `skills/`): the folder name is a valid id; `SKILL.md` is at the top of the folder with valid frontmatter, and its `name` equals the folder name; only allowed file types; limits on file size, total size and number of files; no two names that differ only in upper/lower case.
- **Warnings** never fail the check: missing recommended frontmatter fields, an `owner` that is an email address, and, on pull requests only, a changed skill whose `version` did not change.

## If a check fails

Run the check on your own computer before you push, from the repository root:

```sh
python3 -I -B tools/skillpkg.py ci --root .
```

It needs Python 3 and nothing else to install. Each problem is printed as an `ERROR` or a `WARNING`, followed by a line that says how to fix it. For example:

```text
Skill check: scanned 1 file; 1 skill folder: my-skill.
ERROR skills/my-skill/SKILL.md:2: frontmatter name does not match the folder name (name: other-name, folder: my-skill)
  How to fix: Make them identical: rename the folder to skills/<name>/, or change the name: line to the folder name.
WARNING skills/my-skill/SKILL.md:1: recommended frontmatter fields are missing (version, owner, team, ahead-platform, audience, publication-status, glean-link, claude-link)
  How to fix: Add them when you can. This is a warning; the check still passes.
FAIL: 1 error, 1 warning. Each problem above says how to fix it.
```

- An **ERROR** fails the check. Fix it, commit, and push again; the checks re-run on the pull request.
- A **WARNING** does not fail the check. Fix it when you can.
- The report also lists warnings for skills that are already in the repository, so a good new skill can still print several. Errors come first, and the line that starts `CI OK` or `FAIL` is the result. Look for lines that name your own folder, `skills/<id>/`.
- On a pull request the same messages appear in the check's log and summary. The warning that a skill's version was not increased appears only there, because it compares your skill with what is on `main`; the local command above cannot show it.

<details>
<summary>Every message, and how to fix it</summary>

### Errors found anywhere in the repository

| Message | How to fix |
| --- | --- |
| `ZIP files are not accepted in this repository` | `Unzip it into its own folder skills/<id>/ so that SKILL.md is at the top of that folder, then delete the ZIP. ZIP is an export format, not the repository format.` |
| `symbolic links (shortcuts) are not allowed in this repository` | `Replace the link with a copy of the real file, or delete it.` |
| `unsafe file or folder name (backslash, control character or drive letter)` | `Rename it using only letters, digits, hyphens, underscores and dots, so that it works on Windows, macOS and Linux.` |
| `files directly in skills/ are not part of any skill` | `Move it into a skill folder skills/<id>/, or out of skills/. Only skills/README.md may sit directly in skills/.` |
| `SKILL.md is only allowed directly inside a skill folder, at skills/<id>/SKILL.md` | `Move the skill so that this file is at skills/<id>/SKILL.md: one folder per skill, directly under skills/, with no folder in between.` |
| `no skills/ folder found, so nothing was checked` | `Run the check from the repository root, or pass --root with the repository path.` |

### Errors found in a skill folder

| Message | How to fix |
| --- | --- |
| `folder name is not a valid skill id` | `Use 2 to 64 characters: lowercase letters, digits and hyphens, starting with a letter or digit (for example my-skill). Rename the folder and the name: field together.` |
| `skill folder has no SKILL.md at its top level` | `Each folder directly under skills/ is one skill and needs skills/<id>/SKILL.md. If unzipping an export added an extra folder level (skills/<id>/<id>/SKILL.md), move those files up one level.` |
| `the file must be named SKILL.md, in capital letters` | `Rename the file to SKILL.md.` |
| `two paths in this skill differ only in upper/lower case` | `Rename or remove one of them; they collide on Windows and macOS.` |
| `file type is not allowed in a skill folder` | `Allowed: .css .csv .html .jpg .js .json .md .png .py .txt .yaml .yml and LICENSE files. Remove the file or convert it to an allowed type.` |
| `file is larger than the 5 MB per-file limit` | `Make the file smaller or remove it. Keep large data outside the repository and link to it from SKILL.md.` |
| `skill folder is larger than the 25 MB total limit` | `Remove or shrink files. Keep large data outside the repository and link to it from SKILL.md.` |
| `skill folder has more than 200 files` | `Remove files the skill does not need, or combine small files.` |
| `SKILL.md is not valid UTF-8 text` | `Save SKILL.md with UTF-8 encoding.` |
| `SKILL.md does not start with a frontmatter block` | `Make the first line of SKILL.md exactly ---, then add name: and description: lines, then a line with only ---.` |
| `SKILL.md frontmatter block is not closed` | `Add a line with only --- after the last frontmatter field.` |
| `frontmatter field appears more than once` | `Keep one line for the field and delete the others.` |
| `required frontmatter field is missing or empty` | `Add it to the frontmatter. name: must equal the folder name; description: says what the skill does and when to use it.` |
| `frontmatter name does not match the folder name` | `Make them identical: rename the folder to skills/<name>/, or change the name: line to the folder name.` |

### Warnings (the check still passes)

| Message | How to fix |
| --- | --- |
| `recommended frontmatter fields are missing` | `Add them when you can. This is a warning; the check still passes.` |
| `owner contains an email address, and this repository is public` | `Consider a team name or GitHub handle instead. This is a warning; the check still passes.` |
| `skill files changed but version was not increased` | `Increase version: in SKILL.md (for example 1.0.0 to 1.0.1); git history is the version history. This is a warning; the check still passes.` |

</details>

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
