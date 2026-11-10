# Skills Auditor integration (PAUSED)

> **Status: paused.** Skills Auditor is not part of the approval path. A pull request does not need an Auditor result to merge. Approval is review by a human code owner who is not the author (see [GOVERNANCE.md](GOVERNANCE.md)). The notes below describe the design as it stood when the integration was being planned. They are kept for reference only and do not describe how this repository works today.

Platform-Skills never fabricates or self-certifies an audit. When this was written, the CI gate returned **POLICY BLOCK (exit 2)** for every new or changed Skill ZIP, because no trusted Auditor result could reach it yet.

## Verified Auditor interface (inspected read-only, 2026-10-19)
- Repository: `AHEAD-Labs/Skills-Marketplace` (**internal**). Branch `feat/skills-auditor-deterministic-core`, commit `db4d148`. That branch was **local only, not pushed**, so nothing can be pinned yet.
- CLI: `python3 scripts/skills_auditor.py full <pkg> --json r.json --md r.md` / `delta <candidate> --baseline <approved> ...`. Exit codes: 0 REVIEW_READY, 1 REVISE, 2 BLOCK, 3 usage error. Deterministic, no LLM key.
- Report: `schema_version: skills-auditor-report-v1`, `tool: skills-auditor`, `skill_id`, `mode`, `result`, `candidate.package_sha256`, `rule_set_version`, `policy_fingerprint`, `approval: not_approved`. `tools/skillpkg.py` checks exactly these fields.
- A local run against the six seed ZIPs returned **REVISE** for all six. Findings are kept internal. None of the seeds is REVIEW_READY.
- Reusable workflow `.github/workflows/skills-auditor.yml` (`workflow_call`) needs a GitHub App id plus private key with `contents:read` on the Auditor repo.

## Why the reusable workflow cannot simply be called from here
1. GitHub only lets a **public** repository call reusable workflows that are stored in **public** repositories. Platform-Skills is public and the Auditor is internal.
2. Holding the App private key as a secret in this public repo would expose it to anyone with write access who edits a workflow in a same-repo PR.

## Recommended integration (needs owner decisions; PR B)
Have the **trusted side run the audit and report a status back**:
1. Workflow in the internal Auditor repo (or an internal runner repo), triggered by `workflow_dispatch` or a schedule, given a Platform-Skills PR number and head SHA.
2. It checks out Platform-Skills at that SHA. No token is needed because the repo is public. It runs `skillpkg.py plan --trusted-root <main checkout>` to choose full or delta per ZIP, and runs the pinned Auditor.
3. It posts a commit status `skills-auditor/result` (success only when every ZIP is REVIEW_READY) on the Platform-Skills commit, using a GitHub App with `statuses:write` on Platform-Skills only. The full report stays in the internal repo's artifacts.
4. Branch protection on `main` requires `skills-auditor/result`, restricted to that App as the source.
5. Optional: the internal job publishes a REVIEW_READY report, which `skillpkg.py ci --auditor-reports DIR` verifies (hash, mode, result).

Decisions needed: Auditor owner (push and merge `db4d148`, nominate a release SHA), an org admin (create the App), and the Platform-Skills admins (required status check).
