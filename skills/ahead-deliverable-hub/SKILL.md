---
name: ahead-deliverable-hub
description: Builds AHEAD deliverable hubs, which are branded, self-contained HTML websites that hold an engagement's deliverables. Starts from one of two templates (the Phase 1 discovery template or the Phase 2 target design template) or builds a custom hub from the deliverables in an SOW, for any phase or engagement. Use it whenever an AHEAD consultant asks for a deliverable hub, a hub or website for an engagement or phase, a discovery hub, a target design or deliverable package, a readout site or an HTML deliverable, or a template the team can fill in parallel, even if they never say "hub". Also use it to fill, check or hand over an existing hub file.
version: 1.3.7
owner: ethan.cunningham@ahead.com
team: AI HIVE
approved-by: Michal Lubas (AHEAD distribution, via Teams, 2026-10-27); AHEAD eTech team / Enterprise GPT team, via Grace, following a review call (2026-10-28)
approved-date: 2026-10-28
ahead-platform: [Claude, Glean]
sensitivity: Internal
publication-status: Approved for enterprise-wide distribution (Claude and Glean)
---

# AHEAD deliverable hub

## Why a hub

A deliverable hub puts an engagement's whole package in one file instead of a folder of separate documents. For the client that means one place to open, read and share, with the conclusion first and the detail one click away. For the team it means one current version everyone builds in, so there is no "which file is latest" and nothing emailed around. Because the skill builds every hub, they all carry the same look and pass the same checks. Teams use it to hand a phase over, present straight from one file, trace each claim to its evidence, and give the next phase a running start. The hub is self-contained and opens offline in any modern browser, with no access requests.

This skill produces an AHEAD deliverable hub: one self-contained HTML file per engagement or phase. The file has:

- a tabbed layout in the AHEAD dark editorial style;
- embedded fonts and logo, so it works offline and with no links out;
- an "On this page" rail on each tab;
- marked, owner-tagged slots that the team fills in.

The same engine builds a filled deliverable (a discovery readout, say) or an empty template (a target design package the team fills over four weeks). The design, structure and writing rules come from AHEAD's first two hubs: a discovery hub that has been delivered, and a target design package that is still in progress. They are encoded here so a new hub starts at that standard instead of rediscovering it.

Scripts are in `scripts/`. Run them with `python3`, from any directory. Read the reference files only when the step needs them:

| File | Read it when |
|---|---|
| `references/phase-patterns.md` | Choosing tabs and the Overview story for a discovery, target design or other phase |
| `references/config-schema.md` | Writing or editing the config (tabs, sections, block types, keys) |
| `references/writing-rules.md` | Writing any content or placeholder guidance, and before handover |
| `references/collaboration.md` | Setting up team editing, the weekly cadence, the Teams message, the final checks |
| `references/changelog.md` | Checking which template versions are current, or updating a template when its source phase closes |

## Runtime and portability

This skill runs on both Claude and Glean. The scripts use only the Python standard library and the assets are text-encoded (the logo and fonts are embedded as text, not binary files), so it works on any surface that executes Python. Behavior is the same on either surface: build with the scripts and deliver the hub as a file, a download link where the surface uses one, or saved to the engagement folder where it does not. Grounding and delivery do not depend on a particular connector. If code execution is not available on the current surface, say so plainly and do not hand-write the hub, because the look and the QA guarantees depend on the scripts.

## Confidentiality comes first

Each client's materials and outputs belong to that engagement, and many order forms forbid reusing them for anyone else. So:

- Always start from a preset in `assets/presets/`. Never start from another client's hub or config.
- Never copy wording, findings, diagrams or names from one client's hub into another's.
- This skill contains no client content. Keep it that way if you improve it.

## Every hub looks the same

The point of the skill is that every AHEAD deliverable hub has the same look and feel, whoever builds it and for whichever client.

- **Always build with `scripts/build.py`, and fill content with `fill_slot.py` or the building blocks.** Never write a hub's HTML or CSS by hand. Never edit the bundled styles inside a hub, and never add inline styles, fonts or colors.
- **No client logos.** The header carries the AHEAD logo only. The client is named in the page title, the cover and the footer. Using a client's logo needs their permission, and it breaks the shared look.
- **If someone asks for a different look** (colors, fonts, a light theme, a logo), explain that the look is fixed so every hub stays consistent. Then offer the closest standard option, such as a different block or section.
- `check.py` verifies that the hub carries the skill's stamp and that its styles are unchanged.

## Step 1: Establish the inputs

Gather the following, from the user or from the files they point to (SOW, deliverables schedule, delivery plan, notes). Ask only for what is missing, and do not guess.

- **Client and engagement.** The client name exactly as the client writes it, and the engagement name.
- **Phase.** The phase name or number, and the hub's final date (readout or design gate).
- **Plan dates.** The start date, if the hub includes a plan.
- **Deliverables.** The contracted deliverables, with their exact names, IDs and acceptance criteria. This is usually the SOW.
- **People.** The team, and the owner of each deliverable. The principal consultant owns the Overview.
- **Mode.**
  - *Template:* placeholders for the team to fill.
  - *Filled:* you write the content from the evidence.
  - *Template now, filled later:* the usual pattern for discovery.
- **Audience.** Client-facing is the default. Internal-only hubs can relax the people rules.
- **Extras.** Anything beyond the standard tabs: extra sections, a register, a table, a diagram slot, a glossary, or material to load. Structure is free to change before the first build and costly to change once the team is editing, so ask once. Put it in the same short question as the way in when both are open, for example "Anything beyond the standard tabs you want included?" Skip the question if the user has already said what they want or asked you to just build. Offer standard blocks only (see `references/config-schema.md`); the look stays fixed. The question is about structure. Do not write content the user has not given you.
- **Language.** US English is the default. Use UK English only if the user asks (for example, for a UK client), and set `"lang": "en-GB"` in the config.

If the SOW and the schedule disagree (dates, owners, acceptance wording), list the conflicts for the user. Do not resolve them silently.

## Step 2: Choose the way in

There are two ways in. Either start from one of two ready-made templates, or build a custom hub from the SOW. People ask in different words, so match on meaning:

| Way in | Preset | When it fits | What people say | Shape |
|---|---|---|---|---|
| Discovery template (Phase 1) | `discovery` | Large enterprises already on an AI journey that need a fact base of what exists | "Phase 1 template", "discovery hub", "like our Phase 1 discovery hub", "current-state assessment" | Overview, Register, Estate, Maturity, Controls, Architecture Hypothesis, Validation, Handover, Evidence |
| Target design template (Phase 2) | `target-design` | Advising on a target architecture or platform design | "Phase 2 template", "target design package", "target platform design", "like our Phase 2 deliverable package" | Overview, Delivery Plan, one tab per design deliverable, Target Architecture, Next-Phase Blueprint |
| Custom hub from the SOW (base template) | `blank` | Anything else: assessments, pilots, roadmaps, adoption programs | "build a hub from this SOW", "custom website", "base template", "start from scratch" | Overview plus one tab per SOW deliverable, with sections from its acceptance criteria; add a plan, register, scorecard or tables as needed |

Where the templates come from, and how settled they are:

- **Discovery template 1.0: delivered.** It is the structure of a discovery hub AHEAD has delivered to a client.
- **Target design template 1.0: agreed baseline.** It is the structure agreed at the start of a target design phase that is still in progress. Sections may be added, merged or renamed when that phase closes, and the template will then move to a new version.
- Both source hubs were built by prompting, not with this skill. Every hub records the template and version it started from in its generator stamp, so later updates can be traced.

- **If the user names a way in, use it.** The names "base", "Phase 1" and "Phase 2" also work as preset names on the command line.
- **If they do not say, offer the two templates and the custom option in one short question before building.** Recommend the closest fit to the phase they describe. Do not pick silently, because the choice shapes every tab.
- **Say how settled the template is.** When you build from the target design template, tell the user it is the agreed baseline (1.0) and may be updated. The build prints a note as a reminder. Hubs already built from 1.0 keep working; the team can add or rename sections themselves.
- **Reuse the structure, not the content.** The discovery and target design templates carry the tab structure, section guidance, design and rules from AHEAD's earlier hubs. They contain no client content. Never copy wording, findings or diagrams from another client's hub to make a template "more like" the original.
- Read `references/phase-patterns.md` for how each template's Overview and tabs work.

Whichever template you start from, replace its deliverable tabs with the SOW's deliverables. Tab labels are the exact deliverable names, with no IDs. Copy the acceptance criteria verbatim, and map each one to the section that meets it.

## Step 3: Write the config and build

```bash
S=<skill dir>/scripts
python3 $S/build.py --preset target-design --dump-config config.json   # then edit config.json
python3 $S/build.py config.json --out "<Client> x AHEAD <Phase> Deliverable Package v1.html" \
        --guide "How to add content to the <Phase> hub.md"
```

- Keep `config.json` next to the output. It is the source for rebuilds while the file is still empty.
- Write owners as roles in the config and map them to people in `owners`. A change of person is then a one-line edit.
- Write placeholder `guide` text as a description of the finished section, as of the final date (see `writing-rules.md`). The guide is what each owner reads, so make it specific.
- If the build stops with a duplicate-key or clash message, rename the key. Use suffixes such as `-text`, `-table` and `-figure`.

## Step 4: Check it

1. Run `python3 $S/check.py <file> --client "<Client>"` and fix every error. Treat warnings as judgment calls (a UK spelling inside a product name is fine). The check covers:
   - structure and slot markers;
   - self-containment, internal links and register cross-references;
   - em dashes, casual phrasing and work-in-progress wording;
   - spelling (US English by default) and client-name casing;
   - delivery-team names in the content.
2. Look at the pages. If a file preview screenshot tool is available, present the file and capture the Overview, one deliverable tab and the plan. Otherwise ask the user to open it. Check that:
   - the header tabs fit and stay readable at about 1280 px and 1440 px;
   - nothing is clipped;
   - sections follow a sensible reading order.
3. Opening the file with `?check` on the end of its address shows the remaining placeholders by tab and by owner.

## Step 5: Deliver

Save the hub into the user's engagement folder and present it. Give the user these next steps:

- Upload the hub to SharePoint, and use check out and check in for editing.
- Share the contributor guide, or just the slot list, with the owners.
- Send a short Teams message. There is a template in `references/collaboration.md`; keep it in the sender's voice.

## Filling content into a hub

- **Work on the latest file, not a rebuild.** Once anyone else has edited the hub, never regenerate it from the config, because that discards their work. Run `fill_slot.py <file> --list --empty` to see the open slots. Then fill the ones you were asked to:

  ```bash
  python3 $S/fill_slot.py hub.html --key controls-standards-body --md standards.md --out "hub v6.html"
  python3 $S/fill_slot.py hub.html --key architecture-adrs-body --rows adrs.json --out "hub v6.html"
  python3 $S/fill_slot.py hub.html --key overview-cover-stats --values "18,42,6" --in-place
  python3 $S/fill_slot.py hub.html --key architecture-glance-body --image target.png --caption "..." --in-place
  ```

- **Structured slots are protected.** `--text`, `--md`, `--html-file` and `--image` refuse a slot that holds a table, register, heatmap, gantt or headline numbers, and change nothing. Use `--rows`, `--block` or `--values` for those. Use `--append` to add after them. Use `--force` only when the user asked to replace the whole block.
- **Fill only what you were asked to fill.** If the user supplies data for two sections, fill those two and leave the rest as placeholders, including the interpretation of that data. Offer derived content (averages, a summary of what the scores show) in your reply rather than writing it into the hub. Unrequested text in a client deliverable is hard for the owner to spot and easy to ship by accident.
- **Use evidence only.** Every finding cites a named session and date, a document, or a test. Mark what was heard, observed, tested or recommended. Do not invent numbers, owners or dates; leave the placeholder and ask instead.
- **Propose, then apply.** When new evidence (a session, a review) would change existing content, list the proposed changes first. Apply them once the user agrees, unless they asked you to go ahead directly.
- **Keep the register disciplined.** High priority is for the few items that shape the architecture. Merge duplicates. Use a small, consistent set of status values. To refresh a register, heatmap, gantt or table in a hand-edited file, write that one block as JSON (the same shape as in the config) and run `fill_slot.py hub.html --key <slot key> --block block.json --in-place`.
- **Write the Overview last.** Write it from the finished tabs, following the Overview story in `phase-patterns.md`.
- **Hand over cleanly.** Before handover, run `check.py --final --client "<Client>"`.

## Design rules that matter

These came from client and principal feedback on AHEAD's hubs. Each has a reason, so keep the reason in mind when a new situation comes up.

- **Header.** One slim bar, with the AHEAD logo and full deliverable names as tabs, and no dividers. Readers navigate by deliverable name, and clutter in the header competes with the content.
- **No section numbering.** Numbers look mechanical and break when sections move. The rail already shows the order.
- **Readable type everywhere.** Body text is about 16.5 px, placeholders are full size, and headings are restrained. Tiny text and oversized titles both read as unfinished.
- **Visible placeholders.** Use the dashed placeholder with an icon, guidance and owner, and shimmer blocks for numbers. Never use "n", "TBD" or "xx", because they look like typos to a client who sees a draft.
- **Nothing is hidden behind links.** Do not add "format" or "supporting materials" sections. Do not use present modes or progress trackers; the hub is the deliverable.
- **One authoritative architecture diagram,** on the architecture tab only. The Overview describes the direction in words and links there.
- **Overview content.** The cover has three or four outcome numbers. The executive summary covers conclusion, approach, insights, position and opportunity. After it come the recommended direction (text), the next steps (framed as a recommendation), the index and the glossary. There are no outcome cards that preview a deliverable's detail.
- **Decisions.** Each deliverable tab has its own decisions table. The forward-looking tab consolidates them, and the architecture tab holds the ADRs. Mark only true decision points (usually two) with a star.
- **Plan.** The key sits above the gantt. Remove plan-change history; the plan shows the plan.
- **Styling.** The bundled styles (`assets/hub.css`) are the only styles. Gradients run at 69 degrees and only brand colors are used. For reusable, org-wide or GTM material, the `ahead-branding` skill's Brand review route applies.

## Maintainer tools, not part of normal use

`scripts/selftest.py`, `evals/run_script_evals.py` and the `evals/` folder are for people maintaining this skill, not for producing a hub. When someone asks you to build, fill, check, hand over, demo or try out a hub, do not run selftest or the evals, do not read `evals/`, and do not report self-test output, evaluation results, version internals or a list of bugs. Just build, fill, check or demonstrate the hub itself. "Try it out" or "demo it" means build a sample hub from made-up details and show that, not run the skill's tests. Run the maintainer tools only when the user explicitly asks to test or maintain the skill itself. `check.py` is not a maintainer tool: it is the QA step for the hub you are delivering, so run it as Step 4 describes.

## Scripts

| Script | Purpose |
|---|---|
| `build.py CONFIG --out X.html [--guide G.md]` | Build a hub. `--preset NAME` builds a preset directly (`base`, `discovery` or `phase-1`, `target-design` or `phase-2`). `--dump-config` copies a preset. `--client`, `--date`, `--phase-number` and `--owners "Role=Name;..."` override the config. |
| `fill_slot.py FILE --list [--empty] [--owner N] [--tab K]` | List slots and whether each is filled. |
| `fill_slot.py FILE --key K (--md F \| --text S \| --html-file F \| --rows F \| --values CSV \| --image F \| --block F.json) (--out NEW \| --in-place) [--append \| --force]` | Fill one slot and leave everything else untouched. Plain content stops at a structured slot unless `--append` or `--force` is given. |
| `check.py FILE --client NAME [--final] [--internal-names "A,B"] [--allow-names "C"]` | QA: structure, links, self-containment, placeholders, house style. Exits 1 on errors. |
| `guide.py FILE --out G.md` | Regenerate the contributor guide from the file as it is now. |
| `selftest.py` | Maintainers: build every template and a custom hub in a temporary folder and confirm the checks still catch what they should. Run after changing presets, styles or scripts. |
| `evals/run_script_evals.py [--json]` | Maintainers: run the script-checkable evaluation assertions in `evals/evals.json` and print PASS or FAIL per assertion id. |

For questions about AHEAD AI tooling policy, or publishing this skill org-wide, direct the user to the AHEAD AI HIVE or their eTech contact.
