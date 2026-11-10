# Contributing

Platform-Skills is a **public** repository. Everything you commit, including comments and file names, must be suitable for public view. Do not commit credentials, tokens, API keys, client data or anything confidential.

The rule is one folder per skill: `skills/<id>/` with a `SKILL.md` at its root. `<id>` uses lowercase letters, digits and hyphens, and equals `name` in the frontmatter.

## Add or update a skill in 3 steps

1. **Put your skill in a folder.** Create or edit `skills/<id>/SKILL.md` and any files the skill needs next to it.
   - Required frontmatter: `name` and `description`.
   - Recommended frontmatter (a missing one is a warning, not a failure): `version`, `owner`, `team`, `ahead-platform`, `audience`, `publication-status`, `glean-link`, `claude-link`. The README shows a [complete example](README.md#skill-folder-at-a-glance).
   - `owner` is a team name or GitHub handle. This repository is public, so keep contact details out of the frontmatter.
   - Platform is a frontmatter field (`ahead-platform`), not a folder.
   - **Updating:** edit the same folder and bump `version`.
2. **Open a pull request into `main`.** Branch from `main`, for example `add/<id>` or `update/<id>`, and use the pull request template. Say what changed and why, and choose the origin: GitHub, Glean export or assisted.
3. **Fix what the checks flag, then get a review.** Checks run on every pull request. Once they pass, a human code owner other than the author reviews the exact change and approves it.

Git history is the version history. To see how a skill changed:

```sh
git log -- skills/<id>/
```

## Check your change before you push

From the repository root, with Python 3:

```sh
python3 -I -B tools/skillpkg.py ci --root .
```

An `ERROR` fails the check; fix it and run the command again. A `WARNING` does not fail it. The report also lists warnings for skills already in the repository, so look for lines that name your own folder, `skills/<id>/`; the line that starts `CI OK` or `FAIL` is the result. What each message means, and how to fix it, is in the README under [If a check fails](README.md#if-a-check-fails).

## Starting from a Glean export

1. Unzip the export into `skills/<id>/`, so that `SKILL.md` sits at the root of that folder and not inside a wrapper folder. If unzipping made an extra folder (`skills/<id>/<id>/SKILL.md`), move its contents up one level.
2. Make sure `name` in `SKILL.md` equals the folder name.
3. Do not commit the ZIP. It is an export format, not the format this repository stores.
4. Open the pull request as in step 2 above and choose **Glean export** as the origin.

## Without a GitHub account (assisted)

1. Send the skill folder, or the Glean export, to a Platform-Skills maintainer through your team's internal chat.
2. The maintainer places it in `skills/<id>/`, sets you as `owner` in the frontmatter (by team name or handle, as for any skill), and opens the pull request with the origin **assisted**.
3. You stay the owner of the skill. The maintainer is only the author of the pull request, so a different code owner must review and approve it.

To update the skill later, send the changed folder the same way, with the new `version`.

## Review and merge

- **A human code owner other than the author approves every merge.** Code owners are defined in [`.github/CODEOWNERS`](.github/CODEOWNERS). Admin access is not approval.
- Automated checks support the reviewer. They do not approve, and a green check does not replace the review.
- Merge only after approval and passing required checks. The merged state of `main` is the current version of each skill.
- The author never approves or merges their own pull request.
- Skills Auditor is paused and an Auditor result is not required. See [docs/AUDITOR-CONTRACT.md](docs/AUDITOR-CONTRACT.md) for the background.

## Publishing is separate

Merging changes this repository only. It does not publish a skill to Glean or Claude, and no sync with either platform is provided or verified here.

## Changes to tooling, CI and docs

Run the unit tests before pushing:

```sh
python3 -I -B -m unittest discover -s tests
```

Changes under `.github/` or `tools/` alter the checks themselves, so they need review from a code owner like any other change. See [docs/GOVERNANCE.md](docs/GOVERNANCE.md).
