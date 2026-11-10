# Config schema

A hub is one JSON config. `scripts/build.py` turns it into one self-contained HTML file.
Start from a preset (`--dump-config`) rather than writing a config from scratch.

Contents
1. Top-level fields and tokens
2. Tabs: three forms
3. Sections
4. Block types (with examples)
5. Keys, owners and content
6. Inline formatting

## 1. Top-level fields and tokens

```json
{
 "client": "Acme",                       // exactly as the client writes it
 "engagement": "Data Platform",
 "phase_number": 2,                      // gives {phase}="Phase 2", {next_phase}="Phase 3", {p}=2, {np}=3
 "phase": "Phase 2",                     // optional override, e.g. "Discovery" or "Assessment"
 "next_phase": "Phase 3",                // optional override
 "date": "6 November 2026",              // the final date the hub is written as of
 "start_date": "2026-10-12",             // ISO date of week 1, used by the gantt; omit for week numbers only
 "package": "{phase} Deliverable Package",
 "owners": {"Principal Consultant": "Full Name", "Lead Architect": "Full Name"},
 "default_owner": "Owner to confirm",
 "lang": "en-US",                        // default; "en-GB" only when the user asks for UK English
 "template": {"name": "target-design", "version": "1.0", "status": "agreed baseline"},  // set by the preset; keep it
 "tabs": [ ... ]
}
```

Tokens usable in any string: `{client} {engagement} {phase} {next_phase} {prev_phase} {p} {np} {date} {start} {package}`.

`template` comes from the preset and records where the hub started. It goes into the hub's generator
stamp, so anyone can later tell which template version a hub was built from. Leave it in the config.

Owners: write role names in the config (`"owner": "Lead Architect"`) and map them to people in
`owners`. The placeholder shows the mapped name with initials. Unmapped roles show the role.

## 2. Tabs: three forms

Every tab has `key` (short, lowercase, used in links: `#controls`) and `label` (the full deliverable
name shown in the header). Optional: `id` (shown as a chip in the index), `title`, `question` (the
line under the title in the index), `owner` (default owner for its slots), `index: false` to leave it
out of the Overview index, `accent` (hex color for its index row).

**a. Cover tab** (the Overview): `cover` replaces the hero.

```json
{"key": "overview", "label": "Overview", "index": false, "owner": "Principal Consultant",
 "cover": {"eyebrow": "{package} · {date}", "title": "{client} {engagement}: {phase} Target Architecture",
           "lede": "One sentence on what the package gives the client.",
           "stats": {"key": "overview-cover-stats", "items": [{"label": "Architecture decisions", "sub": "Recorded and agreed as ADRs", "value": "18"}]}},
 "sections": [ ... ]}
```

Stats without `value` render as shimmer placeholders. Use three (or four) outcome numbers.

**b. Deliverable shorthand**: expands to hero, Key conclusions, one section per element, Decisions
and open items, and Acceptance criteria coverage.

```json
{"key": "operating", "label": "Operating Model",
 "deliverable": {
   "id": "D2.5", "title": "Operating Model", "owner": "Operating Model Lead",
   "question": "Who owns, decides, supports and escalates what across the platform?",
   "sections": [
     ["rights", "Decision rights", "Who decides what, and where."],
     {"key": "raci", "title": "Ownership and RACI", "guide": "One row per area.", "columns": ["Area", "R", "A", "C", "I"]},
     {"key": "flow", "title": "Escalation flow", "kind": "diagram", "guide": "The escalation flow, with a caption."},
     {"key": "cadence", "title": "Governance cadence", "content": "Already-written **Markdown** fills the slot."}
   ],
   "criteria": [["Decision rights", ["rights"]], ["RACI or equivalent responsibility matrix", ["raci"]]],
   "summary": true, "decisions": true
 }}
```

Section entries are `[key, title, guide]` or a dict with `key`, `title`, `guide` and optionally
`columns` (makes a table slot), `rows`, `kind: "diagram"` (figure slot), `src`/`svg`/`caption`,
`content`, `owner`, `eyebrow`, `intro`, extra `blocks`. Set `"decisions": false` where a consolidated
table already exists. `sections_before` / `sections_after` add explicit sections around the expansion.

**c. Explicit tab**: `hero` plus `sections`.

```json
{"key": "maturity", "label": "Maturity Assessment", "question": "How mature each platform is.",
 "hero": {"eyebrow": "Maturity", "title": "Design and implementation maturity", "lede": "..."},
 "sections": [ ... ]}
```

`hero` takes `chip` (an ID pill) or `eyebrow`, plus `title` and `lede`.

## 3. Sections

```json
{"id": "patterns", "eyebrow": "Optional small label", "title": "Cross-estate patterns", "intro": "Optional one-line intro.", "blocks": [ ... ]}
```

The section's DOM id is `<tabkey>-<id>`; the left rail lists every section `title` on the tab.

## 4. Block types

| type | Use | Key fields |
|---|---|---|
| `slot` | Editable text (placeholder until filled) | `key`, `guide`, `owner`, `kind` (text/diagram), `content` |
| `table` | Editable table (with `key`) or static table (no key) | `columns`, `rows`, `guide`, `strong_first`, `editable` |
| `figure` | Diagram or image, embedded | `src` (image path) or `svg` (inline SVG), `caption`, `alt`, `guide` |
| `stats` | Headline numbers | `items` [{label, sub, value}] |
| `cards` | 2 or 3 column cards, each with a slot | `cols`, `items` [{title, eyebrow, key, guide, owner, content, accent}] |
| `lead` | Emphasized card with a slot and an optional note | `eyebrow`, `title`, `key`, `guide`, `note` (inline Markdown, can link to a tab) |
| `index` | Clickable list of tabs (ID chip, title, question) | `tabs` (optional explicit order) |
| `glossary` | Term and definition list | `terms` [[term, definition]], `guide` |
| `register` | Searchable, filterable register | `items` or `items_file` (CSV/XLSX), `facets`, `orders` |
| `heatmap` | Score grid with legend and cell notes | `rows`, `columns`, `scores` (null = not assessed), `scale` {min, max, labels}, `notes` {"Row|Column": "why"} |
| `gantt` | Plan chart with key above it | `weeks` {start, count, after} or [[label, date]], `rows`, `milestones` |
| `details` | Collapsible panel around other blocks | `summary`, `blocks`, `open` |
| `text` | Fixed prose (not a slot) | `content` |
| `callout` | Fixed highlighted line | `content` |
| `acceptance` | Criteria coverage table (the shorthand adds it) | `criteria` [[criterion, [section ids]]] |

Register item fields: `id` (required), `kind` (hypothesis, decision, experiment, risk, assumption,
question, finding, requirement), `title`, `statement`, `priority` (High/Medium/Low), `status`, `area`,
`owner`, `evidence` (string or list), `implication`, `outcome`, `next`, `confidence`. From a CSV/XLSX,
headers such as "Type", "Description", "Architecture component", "Source" and "Next step" are mapped
automatically; the header row is found by its "ID" column.

Gantt rows: `{"id": "D2.2", "title": "Governance and Control Kit", "date": "Wed 28 Oct", "due": 3,
"tasks": [{"id": "T-04", "title": "Map controls to enforcement points", "from": 1, "to": 2, "decision": 2}]}`.
`decision` puts a star in that week; use it only for real decision points. Milestones:
`{"id": "CP-02", "title": "Design gate", "date": "Fri 6 Nov", "week": 4}`.

## 5. Keys, owners and content

- Every `key` must be unique across the hub and must not equal a section id (`<tab>-<id>`). Use
  suffixes: `-text`, `-table`, `-figure`, `-stats`, `-grid`, `-list`.
- Keys are how contributors find their slot (`SLOT: controls-standards-body`) and how
  `fill_slot.py` targets it, so do not rename keys once the team is using the file.
- A block with `content` (or `rows`, `scores`, `items`, `terms`, `value`) renders filled; without it,
  it renders a placeholder showing the `guide` and the owner.
- `guide` text is written as the description of the finished section (see writing-rules.md).

## 6. Inline formatting

Within `content`, `guide`, table cells and notes:

- `**bold**`, `*italic*`, `` `code` ``
- `[label](#tabkey)` or `[label](#section-or-slot-id)` for links inside the hub
- `[[H012]]` links to register item H012 and opens it
- A cell or line starting `[ok] `, `[warn] `, `[bad] `, `[info] ` or `[star] ` becomes a status tag
- Block content: blank-line paragraphs, `- ` bullets, `1. ` numbered lists, `#### ` sub-headings,
  `> ` callouts. A string starting with `<` is treated as raw HTML.
