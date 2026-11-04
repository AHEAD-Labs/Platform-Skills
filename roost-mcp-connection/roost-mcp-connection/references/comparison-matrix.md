# Requirements Traceability Matrix

| Requirement | Implementation | Evidence/test | Status |
|---|---|---|---|
| Easier “send this to Roost” invocation | Invocation rules and publish flow in `SKILL.md` | `publish-natural-language` | Designed |
| Surface relevant Roost pages | Dedicated `Roost pages` response section | `discover-roost-pages` | Designed |
| Call out verified/current/ready state | Explicit verification model and allowed labels | `verification-without-freshness` and `verification-success` | Designed |
| Pin pages for searches | Response-level pin plus approved rule schema | `pin-response-only` | Designed |
| Avoid false native-search claim | Non-goal and response wording | `native-search-non-trigger` | Designed |
| Respect permissions and classification | Space access, visibility, refusal, and confirmation guardrails | `unsafe-external-share` | Designed |
| Do not invent MCP schema | Contract sheet and semantic tool matching | Static review / contract validation | Open |
| Never ask the user which Roost tool to use | Tool-ambiguity wording in `SKILL.md` / `SPEC.md` trigger contract | `tool-ambiguity-not-clarifying-question` | Designed |
| Diagnose failures to one likely cause, not a list | Failure-diagnosis decision order in `SKILL.md` step 6 / `references/failure-diagnosis.md` | `expired-session-reauth`, `first-time-setup-not-done`, `permission-sync-lag`, `content-not-indexed-or-excluded`, `single-cause-not-multi-cause-failure` | Designed |
| Production readiness | Validator, runtime evals, approvals | Release checklist | Open |
