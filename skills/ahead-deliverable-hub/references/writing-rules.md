# Writing rules

The hub is read by the client's senior architects and executives, often without the delivery team in
the room. These rules exist because each one has been raised by a client or a principal in review.
`scripts/check.py` catches the mechanical ones; the judgement ones are yours.

## Voice

- **Conclusion first.** Every section opens with the answer, then the reasoning, then the evidence.
  A heading can carry the conclusion ("Strong foundations; consistency drops across distributed
  workflows") rather than a label ("Controls").
- **Consultative and precise.** Write as a trusted adviser: measured, specific, confident where the
  evidence supports it and explicit where it does not.
- **Avoid casual, hype and filler phrasing**, for example: "the bottom line", "we landed on", "we're
  excited about", "game-changer", "best-in-class", "world-class", "cutting-edge", "seamless",
  "low-hanging fruit", "move the needle". Use the plain alternative:

  | Instead of | Write |
  |---|---|
  | The bottom line is... | Overall, ... / In summary, ... |
  | We landed on a federated model | The recommended direction is a federated model |
  | We're excited about the opportunity | The target architecture gives [client] ... |
  | Seamless integration | Integration through [named mechanism] |
  | Best-in-class observability | Observability that meets [stated requirement] |

- **Recommend, do not commit.** Where the next phase needs a separate agreement, write "we recommend",
  "the proposed sequence", never "we will deliver".

## Final-date voice for templates

Templates are written as the finished package, as of its final date. Placeholder guidance describes
what the finished section contains, not the work to produce it.

- Write: "How Phase 2 was conducted: the design workshops, deep dives and walkthroughs."
- Not: "Update this with what we did this week." / "So far we have..." / "In progress".

## Language and mechanics

- US English by default: organization, prioritize, standardize, color, behavior, center, catalog, modeling,
  program. Product names keep their own spelling. Use UK English only when the user asks for it (for example,
  a UK client); then set `"lang": "en-GB"` in the config so the page, plan dates and spelling check follow.
- The client's name exactly as the client writes it, every time (if the client writes "Acme", never write "ACME").
  Check the casing of their product and team names too.
- No em dashes. Use a comma, colon, period or parentheses. For ranges write "Weeks 1 to 2".
- Expand an acronym on first use on each tab, and add it to the glossary.
- Numbers: digits for 10 and above and for all measurements; words for one to nine in prose.
- Dates: "November 6, 2026" in prose; "Fri, Nov 6" in tables and plans (UK hubs: "6 November 2026", "Fri 6 Nov").

## People and confidentiality

- No delivery-team (AHEAD) names in client-facing content. Owners appear only on placeholders.
  Refer to roles ("the lead architect") if a role matters.
- Client people may be named where the client expects it (decision owners, session participants);
  default to roles in evidence tables unless the user says otherwise.
- Never mention how content was produced: no "transcript", "recording", "this conversation", AI or
  tooling references. Cite the session by name and date ("Identity deep dive, 3 Nov").
- Never bring content, wording, findings or diagrams from one client's hub into another's.

## Evidence discipline

- Every finding, score and register item traces to a named source: a session and date, a document,
  or a test. If it cannot be traced, it is an assumption and goes in the assumptions table.
- Say how you know. Distinguish what was **heard** (stated in a session), **observed** (seen in a
  document, repository or demo), **tested** (shown by a test the team ran) and **recommended**.
- Do not overclaim. Separate designed from deployed, requirement from implemented, partially proven
  from proven. A control that exists on paper is "designed", not "in place".
- Do not invent numbers, dates, owners or names. If a value is missing, leave the placeholder and ask.
- When new evidence changes existing content, summarize the proposed changes for the user and apply
  them once agreed, unless the user has asked you to apply them directly.
- Note conflicts between sources (two dates for the same milestone, two owners for one deliverable)
  and raise them; do not choose silently.

## Tables, lists and length

- Use a table when readers compare across rows; use prose for an argument; use a list for three or
  more parallel items.
- Keep table cells short. Put the reasoning in the section text, not in a cell.
- Section text: typically two to five short paragraphs. If a section needs more, add `####` sub-headings.
- Tag results consistently: `[ok] Proven`, `[warn] Partially proven`, `[bad] Not proven`,
  `[info] Open`, `[star] Decision point`.
