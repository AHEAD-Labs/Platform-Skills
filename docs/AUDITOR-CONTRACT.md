# Skills Auditor integration (NOT YET INTEGRATED)

Platform-Skills never fabricates or self-certifies an audit. Today the CI gate returns **POLICY BLOCK (exit 2)** for every new or changed Skill ZIP, because no trusted Auditor result can reach it yet.

## Verified Auditor interface (inspected read-only, 2026-10-19)
- Repository: `AHEAD-Labs/Skills-Marketplace` (**internal**). First inspected at local commit `db4d148`. Now pushed as **Skills-Marketplace #114** (`feat/skills-auditor-deterministic-core`, head `45dd7a7` on 2026-10-19), **open and not merged**. Pin a SHA only after #114 merges.
- Re-checked at `45dd7a7`: same CLI and exit codes, same `skills-auditor-report-v1` schema, rule set now `sa-rules-1.1.0`, plus an optional `--use-client-denylist` flag. `tools/skillpkg.py` does not depend on the rule-set version.
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

Decisions needed: Auditor owner (review and merge Skills-Marketplace #114, nominate a release SHA), an org admin (create the App), and the Platform-Skills admins (required status check).
