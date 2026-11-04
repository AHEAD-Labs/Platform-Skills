# Platform Matrix

| Capability | Glean | Claude | Parity requirement |
|---|---|---|---|
| Natural-language Roost invocation | Skill trigger recognizes “send this to Roost” and related phrases | Same if Roost MCP is connected | No user-facing MCP terminology required |
| Roost discovery/read | Use connected Roost MCP plus normal Glean retrieval | Use connected Roost MCP plus conversation context | Same labels and evidence rules |
| Native search result injection | Not assumed; response-level surfacing is the MVP | Not applicable unless platform supports it | Never claim native ranking/index changes without evidence |
| Verification | Live read plus access and freshness/version evidence | Same | Same allowed labels |
| Response pin | Dedicated response section | Dedicated response section | Do not claim persistence without action success |
| Persistent pin | `[NEEDS INPUT: Glean action contract]` | `[NEEDS INPUT: Claude action contract]` | Optional feature |
| Publish/update | Semantic Roost MCP write operation; confirm destination/visibility | Same | Same safety gates |
| Tool names/schemas | Must be validated from live export/configuration | Must be validated from live export/configuration | Never hard-code guessed names |
| Tool/MCP-action ambiguity | Resolved silently via semantic matching; never asked as a clarifying question | Same | Same non-goal wording |
| Failure diagnosis | One named cause (session/login, setup, permission sync, not-indexed/excluded) via `references/failure-diagnosis.md` decision order | Same | Same signal categories and messaging rules |
| Evaluation | Glean runtime trace and response assertions | Claude runtime trace and response assertions | Same golden prompts where possible |

## Design decision

Use a paired behavioral contract, not assumed byte-for-byte platform parity. Glean is the primary target because the user’s problem is invocation and surfacing in Glean; Claude parity is retained because the Roost MCP documentation describes both supported AI tools.
