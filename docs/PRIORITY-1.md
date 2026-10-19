# Priority 1: ratify #4 and protect `main`

**Who:** Joe or Grace. **Not** Akbar, the author of #4. (Meredith is an admin for visibility only, not a reviewer.)
**Why first:** #4 (`1f793b0`) was merged by its author without independent review, and `main` has no branch protection. Every later control (the policy gate, CODEOWNERS, approval of Skills) depends on these two gaps being closed.

Approving and merging PR #7 records that an independent reviewer has checked #4. If you find a problem, request changes on #7 and open a revert PR for `1f793b0` instead.

## 1. Review the merged #4 content (about 20 minutes)
Diff: https://github.com/AHEAD-Labs/Platform-Skills/commit/1f793b06aaa3ea346ba8fb5ead962c4fb3c408fd
```
git clone https://github.com/AHEAD-Labs/Platform-Skills && cd Platform-Skills
python3 -I -m unittest discover -s tests          # expect: Ran 48 tests ... OK
python3 -I tools/skillpkg.py ci                    # expect: CI OK: {}
```
Check:
- [ ] `.github/workflows/validate.yml`: `pull_request` trigger (not `pull_request_target`), `permissions: contents: read`, no secrets, actions pinned by SHA, nothing published or written back.
- [ ] `tools/skillpkg.py`: no network access, no execution of archive contents, audit reports accepted only from `--auditor-reports` (never from committed files), baselines read only from `--trusted-root`.
- [ ] Docs are accurate and safe for a **public** repo (no secrets, no internal audit findings, no client data).
- [ ] Nothing claims a Skill is approved or published to Glean.

## 2. Protect `main` (admin; Settings → Rules → Rulesets → New branch ruleset, target `main`)
- [ ] Require a pull request before merging, with **1 approval**.
- [ ] Dismiss stale approvals when new commits are pushed.
- [ ] Require approval of the most recent push (so the author can't approve their own change).
- [ ] Require status checks `unit-tests` and `skill-policy-gate`, and require branches to be up to date.
- [ ] Block force pushes and block deletion.
- [ ] Bypass list empty (or emergency-only, with a reason recorded in the PR).
- [ ] Auto-merge not enabled.
- [ ] Verify by running `gh api repos/AHEAD-Labs/Platform-Skills/rules/branches/main`; it should list the rules above.

## 3. CODEOWNERS (admin)
- [ ] Confirm `.github/CODEOWNERS` (added in this PR) lists the right accounts: `@JoeVaderRules` (Joe) and `@babiryegrace20` (Grace). Fix it here if not.
- [ ] After merging, turn on "Require review from Code Owners" in the ruleset.

## 4. Then, in order
1. PR #5: the decision on seed baselines.
2. PR #6: Auditor integration decisions.
