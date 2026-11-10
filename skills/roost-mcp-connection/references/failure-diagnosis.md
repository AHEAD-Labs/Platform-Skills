# Roost Failure Diagnosis — one likely cause, not a list

## Why this file exists

Historically, when a Roost connector call failed, the assistant's response listed four or five possible causes (login, permissions, indexing, configuration, network) with no indication of which one actually applied. Users had to read the whole list and guess, so they either retried blindly or opened a Service Desk ticket instead of fixing the real problem.

This file replaces that pattern with a decision order: evaluate the connector's actual error signal, stop at the first matching cause, and report only that one cause plus a concrete next step. See `SKILL.md` Instructions step 6 for when to use this file.

## Rule

Never present three or more candidate causes in a user-facing failure response. State the single most likely cause first, name the fix, and offer a second cause only as an explicit fallback ("if that doesn't resolve it, it's probably [X]") if the first fix doesn't apply. The catalog below is a decision aid for the assistant — do not read it aloud to the user as a menu of possibilities.

## Decision order

Evaluate signals in this order and stop at the first match.

### 1. Expired session or login

**Signal:** connector returns 401/403 with a token/session-expiry indicator, an explicit "re-authenticate," "session expired," or "sign in again" message, or an OAuth refresh failure.

**Root cause:** the user's Roost session or login has expired — not a permissions or setup problem.

**Response pattern:**
> Your Roost session has expired. Re-authenticate [via the connector's auth action/link, using whatever the connector/platform actually exposes] and I'll pick back up once you're signed in again.

Do not retry the call automatically after surfacing this message. Wait for the user to confirm they've re-authenticated, then retry once. Do not also mention permissions, indexing, or setup in this response — those are not the cause when this signal matches.

### 2. First-time setup not completed

**Signal:** connector reports Roost is not connected, not installed, not authorized for this user, or there is no workspace/organization mapping — i.e., an onboarding/connection-state error rather than an expired-credential error. This is also the default assumption the first time a Roost operation is attempted in a session with no prior successful Roost call and no clearer signal.

**Root cause:** a first-time setup step was skipped (connector authorization, workspace linking, or default destination space configuration), not that credentials expired or access was denied.

**Response pattern:**
> Roost isn't connected for your account yet — [name the specific missing step the connector returned, e.g., "the Roost MCP hasn't been authorized" or "no destination space is configured"]. Complete that step and let me know; I'll retry right after.

Distinguish this from cause 1: setup-not-done errors reference connection/installation/mapping state, not token or session lifecycle. Distinguish from cause 3: this is about the connector/account never being linked at all, not about a specific space's access grant.

### 3. Permission sync lag

**Signal:** the account is clearly authenticated (no auth error), but a specific space or page returns access-denied, "insufficient permissions," or "not a member of this space."

**Root cause:** most often the user was recently granted access to that space and the grant hasn't synced yet, or they need to request access to that specific resource. This is not a login problem.

**Response pattern:**
> You're signed in, but Roost says you don't have access to [named space/page] yet. If you were just added to that space, permission sync can lag briefly — try again shortly, or [request access from the owner, naming them only if the connector returned an owner].

Always name the specific space/page. Never imply the user's whole Roost account is broken when the signal is scoped to one resource.

### 4. Content not indexed, or source site excluded

**Signal:** a search/lookup for a page the user believes exists returns zero results or "not found," especially when the user supplied a specific title or topic (not a URL/ID) and there is no access-denied signal.

**Root cause:** the page may not be indexed yet, or that Roost space/site may be excluded from indexing — not that the user lacks access.

**Response pattern:**
> I couldn't find that page through search. It may not be indexed yet, or that Roost space could be excluded from indexing. If you have the direct URL or item ID, share it and I'll try reading it directly instead of searching.

Offer the direct-read fallback whenever the user might have the exact link — this is usually faster than waiting on indexing.

### 5. Everything else (fallback)

**Signal:** timeout, 5xx, malformed response, or an error shape that doesn't match any of the above.

**Root cause:** connector/service error — do not force this into one of the four named causes above when the signal doesn't support it.

**Response pattern:**
> The Roost connector call failed ([error type, only if useful to the user]). I can retry, or you can [manual fallback — e.g., open the page directly in Roost].

## Response pattern summary

One named cause → one concrete next step → (optional) one fallback cause only if the first fix doesn't apply. Never an unordered list of three-plus possible causes with no stated likelihood.

## First-time setup checklist

Use this to recognize cause 2 quickly, and proactively where the platform supports a lightweight check:

- Roost MCP/connector not yet authorized for the user's account.
- Roost workspace/organization not yet linked to the user's Glean/Claude workspace.
- No default destination space configured, so publish requests fail with a space-resolution error rather than an obvious content error.

If the connector or platform exposes a health/connection check, use it before the first Roost operation in a session to confirm setup is complete rather than discovering the gap via a failed publish or read. If no such check exists, do not block on it — attempt the real operation and classify any resulting error through the decision order above.
