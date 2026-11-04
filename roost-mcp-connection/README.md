# Roost MCP Connection package

Claude adapter of AHEAD's `roost-mcp-connection` skill. It lets a user say "send this to Roost," discover relevant Roost pages, ask whether a page is verified/current, and pin a page in the current response — without naming the Roost MCP explicitly.

## Package state

Draft / pilot-ready design, version 0.2.0, ported from the Glean `roost-mcp-connection` package (same spec). Not represented as production-ready until the Roost MCP contract is confirmed for this Claude workspace and the shared evaluation set has a runtime pass.

## How to install in Claude

1. Download this folder (`SKILL.md`, `SPEC.md`, `references/`) as a skill package.
2. In Claude, add it as a skill (Settings → Capabilities/Skills → add skill, or the equivalent upload flow for your Claude surface) and upload the folder or a zip of it.
3. Confirm your Claude workspace has a connected Roost MCP. If it does not, the skill will correctly report that Roost access could not be completed rather than fabricating results — see **Limitations** in `SKILL.md`.
4. Once installed, just talk naturally: "send this to Roost," "is the Roost onboarding page current?", "pin the Roost page about X."

## Included files

- `SKILL.md` — Claude-adapted instructions: Spec Summary, When to Use, Inputs, Instructions, Output Format, Quality Checklist, Limitations, Change Log.
- `SPEC.md` — source-of-truth contract, workflow, safety gates, acceptance criteria, and open items for this adapter.
- `references/roost-mcp-contract.md` — fields that must be validated against the live Roost MCP connector before production use.
- `references/topic-pin-rules.example.yaml` — example schema for approved topic-to-page pin rules.
- `references/failure-diagnosis.md` — decision order for diagnosing a Roost failure to one likely cause (expired session/login, first-time setup, permission sync lag, not-indexed/excluded content) instead of a hedged list of possibilities.

## Important limitation

The available AHEAD references document Roost publishing, listing accessible content, reading existing items, and publishing updates, but do not publish the production MCP server/tool schema for Claude specifically. The skill therefore uses semantic connector matching and refuses to invent tool names or fields. Complete `references/roost-mcp-contract.md` against your Claude + Roost MCP environment, and run the shared evaluation set, before treating this as production-ready.

## Suggested rollout

1. Confirm the Roost MCP is connected and reachable in your Claude workspace.
2. Validate the connector contract with the Roost owner and your Claude/Glean admin.
3. Pilot with read-only discovery/verification first.
4. Enable publish/update only after destination, visibility, classification, and confirmation behavior pass review.
5. Add approved topic-to-page pin rules with owners and review dates.
