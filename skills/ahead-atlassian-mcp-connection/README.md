# Atlassian MCP Connection package

AHEAD's `atlassian-mcp-connection` skill for **Glean and Claude**. It sends Jira and Confluence requests to the right tool without the user naming one. When a request fails, it gives one likely cause and one next step, and points admin-only fixes to a Service Desk ticket. Part of the Glean Connector & MCP Skills initiative, Phase 1.

## Release state

- **Version:** 1.0.0
- **Owner:** Grace Gallagher, grace.gallagher@ahead.com
- **Team:** Solutions Engineering
- **Platforms:** Glean (Glean Skill) and Claude (Claude skill), paired under one `SPEC.md`
- **Sensitivity:** Internal
- **Publication status:** Approved for the org-wide Glean Skills Catalogue and org-wide Claude install
- **Approval:** AHEAD eTech team, org-wide skill review (Grace Gallagher), 2026-11-10. A separate Glean admin review was waived by the owner (solution agreed with Isha Mehta in a sync call).
- **Outstanding (non-blocking):** the 18 runtime evaluation cases are `not_run`, so `--release-gate` reports that evidence is still required. Approval isn't runtime evidence.

## Distributions

Built by `python3 scripts/build_distributions.py` into `dist/`:

| File | Install where | Contents |
|---|---|---|
| `atlassian-mcp-connection-glean-1.0.0.zip` | Glean org skill | Glean `SKILL.md` at root, `SPEC.md`, `README.md`, Glean and shared references, `evals/evals.json` |
| `atlassian-mcp-connection-claude-1.0.0.zip` | Claude organization skill | Claude `SKILL.md` at root (Claude frontmatter with governance under `metadata`), `SPEC.md`, `README.md`, Claude and shared references, `evals/evals.json` |
| `atlassian-mcp-connection-source-1.0.0.zip` | Maintainers | Full source package, including adapters and scripts |

## Install

**Glean (org-wide):**

1. Admin → Skills (or Settings → Skills) → Add skill.
2. Upload `atlassian-mcp-connection-glean-1.0.0.zip`, and set visibility to the whole organization.
3. Confirm the catalog description matches the `SKILL.md` frontmatter.
4. Users need the Jira and Confluence connectors authorized (Settings → Connectors).

**Claude (org-wide):**

1. As a Claude organization owner, go to Admin settings → Capabilities → Skills.
2. Upload `atlassian-mcp-connection-claude-1.0.0.zip` and provision it to the organization.
3. Individual installs: Settings → Capabilities → Skills → Upload skill. For Claude Code, unzip into `~/.claude/skills/atlassian-mcp-connection/`.
4. Users need the Atlassian connector connected (Settings → Connectors).

## Verification

```bash
python3 scripts/validate_package.py                # structural check
python3 scripts/validate_package.py --install-gate # install readiness
python3 scripts/validate_package.py --release-gate # fails until runtime evidence is recorded
python3 scripts/build_distributions.py             # builds and validates the three zips
```

## Running the evaluations

1. Open a clean Glean or Claude session with only this skill loaded, using synthetic fixtures.
2. Paste each case prompt exactly and judge each assertion pass or fail.
3. Save the transcript to a durable location, then record the result:

```bash
python3 scripts/record_eval_run.py --case 1 --assertion 1-1 --result pass \
  --runtime Glean --run-by you@ahead.com \
  --evidence "Glean run 2026-11-12; transcript <evidence location> lines 12-40"
```

## Rollback

Unpublish the skill in Glean or remove it from Claude organization skills, then reinstall the prior distribution zip.
