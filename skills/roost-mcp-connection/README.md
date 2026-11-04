# Roost MCP Connection package

AHEAD's `roost-mcp-connection` skill for Glean and Claude. It lets a user say "send this to Roost," discover relevant Roost pages, ask whether a page is verified/current, and pin a page in the current response — without naming the Roost MCP explicitly, on either platform.

## Package state

Draft / pilot-ready design, version 0.3.0. One shared `SPEC.md` and one `SKILL.md` cover both the Glean and Claude platform adapters (see `references/platform-matrix.md` for where behavior is identical vs. platform-specific). Not represented as production-ready until the Roost MCP contract is confirmed for each target workspace and the shared evaluation set has a runtime pass on both platforms.

## How to install

### In Glean

1. Download this folder (`SKILL.md`, `SPEC.md`, `references/`) as a skill package.
2. In Glean, go to Settings → Skills → add skill, and upload the folder or a zip of it.
3. Confirm your Glean workspace has the Roost MCP connector enabled under Settings → Connectors. If it does not, the skill will correctly report that Roost access could not be completed rather than fabricating results — see **Limitations** in `SKILL.md`.
4. Once installed, just talk naturally: "send this to Roost," "is the Roost onboarding page current?", "pin the Roost page about X."

### In Claude

1. Download this same folder as a skill package.
2. In Claude, add it as a skill (Settings → Capabilities/Skills → add skill, or the equivalent upload flow for your Claude surface) and upload the folder or a zip of it.
3. Confirm your Claude workspace has a connected Roost MCP. If it does not, the skill will correctly report that Roost access could not be completed rather than fabricating results.
4. Use the same natural-language phrasing as above — no platform-specific wording is required.

## Included files

- `SKILL.md` — cross-platform instructions: Spec Summary, When to Use, Inputs, Instructions, Output Format, Quality Checklist, Limitations, Change Log.
- `SPEC.md` — source-of-truth contract, workflow, safety gates, acceptance criteria, and open items shared by both platform adapters.
- `references/platform-matrix.md` — capability-by-capability comparison of Glean vs. Claude behavior.
- `references/comparison-matrix.md` — requirements traceability matrix.
- `references/roost-mcp-contract.md` — fields that must be validated against the live Roost MCP connector before production use, for each platform.
- `references/topic-pin-rules.example.yaml` — example schema for approved topic-to-page pin rules.
- `references/failure-diagnosis.md` — decision order for diagnosing a Roost failure to one likely cause (expired session/login, first-time setup, permission sync lag, not-indexed/excluded content) instead of a hedged list of possibilities.

## Important limitation

The available AHEAD references document Roost publishing, listing accessible content, reading existing items, and publishing updates, but do not publish the production MCP server/tool schema for either platform. The skill therefore uses semantic connector matching and refuses to invent tool names or fields. Complete `references/roost-mcp-contract.md` against your Glean and/or Claude + Roost MCP environment, and run the shared evaluation set on each platform, before treating this as production-ready.

## Suggested rollout

1. Confirm the Roost MCP is connected and reachable in each target workspace (Glean and/or Claude).
2. Validate the connector contract with the Roost owner and your Glean/Claude admin.
3. Pilot with read-only discovery/verification first.
4. Enable publish/update only after destination, visibility, classification, and confirmation behavior pass review.
5. Add approved topic-to-page pin rules with owners and review dates.
