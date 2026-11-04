# Roost MCP Contract Validation Sheet

Complete this file from the live Glean/Claude connector configuration or approved export. Do not replace unknowns with guesses.

## Required bindings

- Server/connector identifier: `[NEEDS INPUT]`
- Authentication model and scope: `[NEEDS INPUT]`
- Read/list/search operation: `[NEEDS INPUT]`
- Read operation input schema: `[NEEDS INPUT]`
- Read operation output schema: `[NEEDS INPUT]`
- Publish/create operation: `[NEEDS INPUT]`
- Update/version operation: `[NEEDS INPUT]`
- Space listing/selection operation: `[NEEDS INPUT]`
- Health/validation operation: `[NEEDS INPUT]`
- Persistent pin/bookmark operation: `[NEEDS INPUT or NOT SUPPORTED]`

## Fields to verify

| Field | Required for | Verified? | Notes |
|---|---|---:|---|
| Direct page URL | Discovery/publish result | No | Must be returned, not inferred when possible |
| Page/item ID | Read/update/pin | No |  |
| Space ID/name | Publish/access | No |  |
| Access result | Verification | No | Current-user scoped |
| Last-updated timestamp | Freshness | No | Define timezone/semantics |
| Version identifier | Freshness/update | No |  |
| Health/validation status | Ready label | No |  |
| External-sharing state | Publish safety | No |  |
| Returned status/error | All writes | No |  |

## Production gate

Do not change package state from draft/pilot until every required binding is filled, permissions are approved, the topic pin configuration is reviewed, and the runtime eval set passes in a representative environment.
