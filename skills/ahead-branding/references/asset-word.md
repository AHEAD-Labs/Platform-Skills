# Asset Rules — Word Documents, Proposals, Reports, Whitepapers

Triggered by: Word doc, document, proposal, SOW, statement of work, MSA exhibit, solution brief, service brief, report, whitepaper, ebook, one-pager, letter, memo, runbook, assessment, account plan.

## Start here

| Deliverable | Template |
|---|---|
| **Default for any Word document** — formal client deliverable (SOW, proposal, assessment), report, whitepaper, general document | **THE Word Template Final** (`.dotx`, Archie Word Templates folder) |
| Letter or short correspondence on company stationery | **THE Word Template Final**, until Brand publishes a 2026 letterhead. The 2023 Letterhead is retired |
| Service Brief | Hand off to the `ahead-service-brief-generator` skill — it owns the OA-approved template. Do not rebuild it |
| Project or team communication | **Communication Template** |

Paths are in `brand-registry.md` §4. Generate a real `.docx` on the template. Never hand back a styling checklist and ask the user to reformat a blank document.

**If THE Word Template Final can't be read from SharePoint:** no Word template is bundled. Say the SharePoint templates couldn't be accessed and give the reconnect step (In Glean, go to **Settings → Connectors** and authorize SharePoint access.). Build on 2026 styles (Aptos, 2026 palette), labeled "template not applied", only if the user says to continue.

**Retrieving the default template:** look for `THE Word Template Final.dotx` in the Word Templates folder in Archie (Official-Intranet-Files › ARCHIE Files › Marketing › Presentations and Visuals › Templates › Word Templates). Do not report that "the relevant Word template could not be found" because the 2023 Formal Word Template is unavailable; that file is no longer the default. Use the 2023 Formal Word Template only when the user names it. If `THE Word Template Final.dotx` itself cannot be retrieved, say so, build the closest compliant `.docx`, and label it "template not applied."
## Typography

**Aptos only** — Word is a Microsoft Office deliverable, and the 2026 Style Guide names Aptos as the sole Office typeface. Use Aptos for headings, body, tables, captions, headers, and footers. Verdana only as a backup if Aptos is unavailable. Do not introduce Parabolica (Marketing-owned), Poppins, PT Serif, Calibri, or Tenorite (Tenorite is the stale 2024 face and fails validation). If `THE Word Template Final.dotx` defines its own font, keep the template's font and say so in the brand report.

Heading hierarchy: H1 → H2 → H3, used in order, no skipping. Body 11pt, charcoal `#2A2A2A` or black. Do not mix more than two font families; in practice, use one. An isolated italic line is not a header.

## Color

- At least one primary palette color appears in the document — typically headings in Navy `#123A61` with AHEAD Blue `#009FDC` rules, callouts, or table header fills. Primaries: `#0C243B`, `#123A61`, `#009FDC`, `#0B52ED`, `#33CC99`, `#FC794D`.
- Table header rows: Navy fill with white Aptos. Banded rows: Ice Blue `#E8F1FC` (`#EBF0F2` is stale 2024).
- No Brand Team-only accent colors; no purple. The 2024 colors are stale.
- Text contrast at least 4.5:1.
- Keep body text high-contrast and readable; do not set long passages in a brand color.

## Logo, header, footer

- Logo comes from the template header. If you must place it manually, use the navy logo on white or light backgrounds, top-left, clearspace ≥ the height of the "E".
- Footer for formal client deliverables: `Confidential to AHEAD and [Client Short Name] — Page X of Y`.
- Footer for internal documents: `Confidential - Proprietary to AHEAD`.
- Keep the template's front matter, legal notice, and revision-history blocks. Do not delete them to save space.

## Structure conventions

- Lead with the outcome. Executive summary first, detail after.
- Use tables for anything that is genuinely row-and-column shaped — scope, assumptions, deliverables, RACI, pricing lines.
- Mark unknowns explicitly as `[NEEDS INPUT: ...]` rather than inventing a value. Keep internal notes out of client-facing output; put open questions in a sidecar list for the author, not in the deliverable body.
- Whitepapers and ebooks are visual documents: they are subject to the **maximum three brand element treatments** rule and the approved photography rules.

## Reusable versus one-off

A proposal for one client is a one-off — generate it and move on. A solution brief, service brief, enablement doc, or anything destined for a shared library is **Evergreen**: flag Brand Team review in a chat note (brand@ahead.com). Do not add a review block to the document.

## Before you hand it over

Run `python3 scripts/validate_brand.py <doc>.docx --mode standard` (or `--mode evergreen`). Fix every finding.
