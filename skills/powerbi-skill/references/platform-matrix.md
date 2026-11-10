# Platform Matrix — powerbi-skill v3

One contract, two surfaces. The skill is instructions plus references, so parity is high; the differences are in how the connector and identity are wired.

| Concern | Glean (chat + agents) | Claude (Claude.ai project, Claude Code, Cowork) |
|---|---|---|
| Capability type | Glean Skill, auto-triggered by description; referenceable inside agents | Skill loaded into the project/session |
| Connector | Power BI MCP enabled per user; if deferred, search "Power BI" to load the tools | Power BI MCP configured for the workspace/session |
| Identity → RLS | Connector passes the user's identity to Power BI; Power BI applies RLS | Same, based on the configured connection identity |
| Role hint availability | Requesting user's profile/title is available to the runtime; usable as a soft routing hint | May be absent — fall back to question cues only |
| Trigger control | Description-based auto-trigger; must be allowed to engage in context | Project instructions or explicit invocation |
| Feedback capture (OI-3) | Best fit: an agent step or action writing to a OneDrive/SharePoint spreadsheet | No equivalent; gap reports go to the owner manually |
| Artifact building | Downstream Glean capability, not this skill | Downstream Claude capability, not this skill |

**Intentional differences**

- Role-aware routing is pilot behavior and only applies where the runtime actually knows the role. Absence of a role must never change the correctness of an answer, only its default model pick.
- Feedback capture will land on Glean first because that is where the action surface exists.

**Parity tests:** run E-1 and E-2 from `evals/evals.json` with identical inputs on both surfaces and compare the number, the model chosen, and the scope line.
