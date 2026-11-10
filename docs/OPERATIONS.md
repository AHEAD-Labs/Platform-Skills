# Maintainer notes

For code owners and maintainers. Contributors should start with [CONTRIBUTING.md](../CONTRIBUTING.md). Approval rules and required repository settings are in [GOVERNANCE.md](GOVERNANCE.md).

## The flow

Pull request → automated checks → review by a human code owner who is not the author → merge into `main`. Skills Auditor is paused and its result is not part of this flow.

## Running the checks locally

From the repository root, with Python 3, on the branch under review:

```sh
python3 -I -B tools/skillpkg.py ci --root .
```

It exits 1 if any `ERROR` is printed and 0 otherwise. Warnings never fail it. The README lists every message under [If a check fails](../README.md#if-a-check-fails). The warning that a skill's `version` was not increased only appears on the pull request check, because it compares with `main`; check the version bump by eye when you review.

## Reviewing a pull request

Read the whole diff of the skill folder, including reference and data files, not only `SKILL.md`.

- `skills/<id>/SKILL.md` exists, `<id>` is lowercase letters, digits and hyphens, and `name` equals `<id>`.
- `owner` is a team name or GitHub handle, not contact details.
- For an update, `version` is bumped.
- The origin in the pull request template is filled in.
- Nothing in the folder is a credential, token, API key or client data, and the content is appropriate for a **public** repository.
- No ZIP or other export artifact is committed.
- You are not the author of the change.

## Opening a pull request for a contributor without GitHub (assisted)

1. Receive the skill folder, or the Glean export, from the contributor.
2. If it is an export, unzip it so that `SKILL.md` is at the root of the folder.
3. Create the branch and add the folder:

   ```sh
   git switch -c add/<id> origin/main
   # copy the folder to skills/<id>/, then set the contributor as `owner` in SKILL.md
   git add skills/<id>
   git commit
   ```

4. Open the pull request and choose the origin **assisted**.
5. Ask a different code owner to review it. You are the author, so you cannot approve it.

## Rolling back

Open a pull request that reverts the merge commit, review it like any other change, and merge it:

```sh
git revert <commit>        # add -m 1 if the commit is a merge commit
```

To look at an older version without changing anything:

```sh
git log -- skills/<id>/
git show <commit>:skills/<id>/SKILL.md
```

## Removing a skill

Delete its folder in a pull request. Review and merge it like any other change.

## Publishing is outside this repository

Merging changes this repository only. Nothing here publishes a skill to Glean or Claude, and no sync with either platform is provided or verified.
