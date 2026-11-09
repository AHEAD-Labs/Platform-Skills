# Contributing

Platform-Skills is a **public** repository. Content and comments must be suitable for public view. Audit findings stay in the internal Skills Auditor repository. Full detail is in [docs/OPERATIONS.md](docs/OPERATIONS.md).

## Submitting or updating a Skill (citizen / FDE)
1. **Export the Skill from Glean as a ZIP.** Do not unzip or edit it. `SKILL.md` must sit at the archive root, and its `name:` must equal the file name (`<skill-id>.zip`).
2. **Branch from `main`.** Use `submit/<skill-id>` for a new Skill, or `update/<skill-id>` for an approved one.
3. **Add the ZIP at `skills/shared/<skill-id>.zip`** (or `skills/glean/` / `skills/claude/` if it is platform-specific). Nothing else is accepted: loose `SKILL.md` folders, ZIPs elsewhere and symlinks all fail CI.
4. **Check it locally:** `python3 -I tools/skillpkg.py validate skills/shared/<skill-id>.zip --skill-id <skill-id>`
5. **Open a pull request** using the template and tick New Skill (full audit) or Update (delta audit).
6. **Expect `skill-policy-gate` to show POLICY BLOCK** until a trusted Skills Auditor result exists. That is the control working, not a broken build. `unit-tests` should be green.

## Review and merge
- **Another teammate reviews the exact change.** The author never approves or merges their own PR. Code owners are listed in `.github/CODEOWNERS` (real owners added by #7).
- Merge only after approval and green required checks. The merged state on `main` is the approved version.
- **Publishing is separate.** Glean import from `main` is a manual admin step after merge (see OPERATIONS).

## Tooling, CI and docs changes
Run `python3 -I -m unittest discover -s tests` before pushing, and write a failing test first for any behavior change. Changes to `.github/`, `tools/` or `skills/baseline-hashes.json` alter the trust controls, so they need code-owner review.

Do not commit credentials, tokens, API keys, client data, or Auditor reports.
