# Approval Routing and the Brand Review Gate

Policy captured from Sam Mock, Director of Brand Marketing, in the 2026-09-14 requirements session. **Brand approvals for Evergreen artifacts go to brand@ahead.com** (updated November 2026).

## The decision

Ask one question: **will this asset be used again by someone other than the author?**

| Situation | Review | Behavior |
|---|---|---|
| Sales rep building a deck for tomorrow's client meeting; single-use, single-client | **Not required** | Generate it. Make it as good as the skill allows and get out of the way |
| One-off proposal, one-off customer readout, personal working doc | **Not required** | Generate it |
| Internal HTML tool or dashboard used only inside AHEAD | **Not required** | Generate it |
| Solution brief, service brief, enablement asset, campaign material — anything logged into the company record for others to pull from | **Required** | Generate it, add the review note in chat |
| Any department-wide, region-wide, or company-wide employee communication | **Required** | Generate it, add the review note in chat, route structure to Louise Thompson |
| Interactive/HTML content shared externally | **Required** | Generate it, add the review note in chat |
| Events, swag, or anything applying the logo to physical goods | **Required** | Brand Team approval before production |

Speed matters more than perfection for one-offs. Consistency matters more than speed for anything reusable.

## The review note (chat only)

Do **not** put a brand review block, status box, or approval placeholder in the deliverable. The file stays clean. The review requirement is stated once, in the chat response, as a note (see "What to say in your response" below).

## Save, publish, and share checkpoint

Claude and Glean both offer to save generated files to SharePoint. Treat that offer as a gate.

If the user asks to **save to SharePoint, publish, export to a shared library, or share externally** an Evergreen deliverable and has not said Brand Marketing reviewed it:

1. Stop before performing the action.
2. Ask exactly once: *"Before this goes into SharePoint — has Brand Marketing reviewed it? Reusable assets are supposed to get a brand check first (brand@ahead.com)."*
3. Whatever the answer, respect it and proceed. Do not add anything to the file.

Do not gate one-off assets this way. Do not ask twice.

## What to say in your response

For an Evergreen output, include this note verbatim in the chat response, not in the file:

> This is reusable content, so Brand Marketing needs to review it before it's treated as final. Please contact brand@ahead.com for brand approval of evergreen artifacts.

## Escalation and questions

| Question | Route to |
|---|---|
| **Brand approval of an Evergreen artifact** | **brand@ahead.com** |
| Brand permission, exceptions, new treatments, accent color use | Sam Mock — sam.mock@ahead.com |
| Design execution, template mechanics, asset production | Sarah Stiefelmayer — sarah.stiefelmayer@ahead.com |
| Internal communications structure and cadence | Louise Thompson |
| Skill behavior, guardrail additions, registry updates | Grace Gallagher — grace.gallagher@ahead.com |
| Org-wide publication of this skill | AHEAD eTech team |

## Good and bad example libraries

Brand Marketing is assembling curated sets of compliant and non-compliant examples so the skill has a labeled sample space to reason against.

`[NEEDS INPUT: SharePoint paths for the approved "good examples" and "bad examples" folders.]`

When those folders exist, add them to `brand-registry.md` and reference them here. Keep them in **separate, explicitly labeled folders** — a compliant-examples folder and a non-compliant-examples folder — so nothing in the non-compliant set is ever treated as a pattern to imitate. Never mix the two sets in one location.
