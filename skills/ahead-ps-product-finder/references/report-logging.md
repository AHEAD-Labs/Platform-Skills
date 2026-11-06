# Report logging

Target workbook: Services Finder Skill Report.xlsx (Scope Central > Scope Central Library > How-To's & Guides > Reports)
URL: https://thinkaheadit.sharepoint.com/:x:/r/sites/ScopeCentral/Shared%20Documents/Scope%20Central%20Library/How-To%27s%20%26%20Guides/Reports/Services%20Finder%20Skill%20Report.xlsx?d=w2bac66734571461ab1f3551806fba22b&csf=1&web=1&e=1e6gJK

`glean_document_reader` returns only the sheet name for this file (no cells), so use the Microsoft Graph Excel tools. Run `help(<sdk_name>)` on each before first use.

## Columns (A..W, in this order; produced by `scripts/format_report_row.py`)
Run ID | Run Date/Time (CT) | Requested By | Mode (Scope/Audit) | Input Type (Transcript/Description/Attachment) | Input Name | Scope Summary | Item # | AHEAD Solution (Unity) | SKU | Unity Item Name | Unity Item State | Level (SL1/SL2/SL3) | Estimate Product (P:) | Estimate Template (T:) | P Active | T Active | Practice (L3) | Multi-practice | Why It Fits | Flags | Confidence | Data Freshness

One row per recommended P: product (SL2 and SL1 variants shown to the user; not Custom unless recommended). A run with no match logs one row with Item # = 0 and `No active match` in Why It Fits.

## Steps
The write tool also requires `internal_tool_cta` (e.g. "Add 4 rows"). `values` must match the address dimensions exactly. All Graph tools require `_user_goal` (the user's request verbatim), `internal_preview_markdown` (the rows as a markdown table for writes) and `internal_preview_description_brief`.
1. Resolve the file once: `microsoft_onedrive_extension_tools__one_drive_get_drive_item_by_sharing_url(sharing_url=<URL above>, select_fields=["id","name"])` -> `drive_id`, `item_id`. Reuse them: drive_id `b!9opxsSkETU2zR54H3jSuFDL1cloJfDtErObIE6wH9Iwl0TynooUITLS1TWSdmafC`, item_id `01FS4I3J3TM2WCW4KFDJDLD42VDADPXIRL`, worksheet `Sheet1` (verified 2026-10-18). Re-resolve if a call fails.
2. Find the last used row: `excel_get_range(worksheet_id="Sheet1", address="A1:A5000")` and take the last non-empty cell. Empty column A = no header yet.
3. Run `python3 scripts/format_report_row.py run.json` to get `header` and `rows`. If the sheet is empty, write header + rows together starting at A1. Otherwise write only `rows` starting at last+1, range `A{n}:W{n+len(rows)-1}`.
4. Re-read column A immediately before writing (another run may have appended). Write with `request_microsoft_excel_extension_tools__excel_update_range`, one range for the whole run; issue it alone (needs user approval) and wait. Use `excel_add_table_row` only if a table object exists.
5. Re-read the written range to confirm, then tell the user the row range written.

## Rules
- Append only. Never call clear_range, insert_range, delete, or overwrite any existing cell.
- Do not log verbatim transcripts, personal data, or prices. Scope Summary max 300 characters.
- If the write fails or is declined, print the rows as a tab-separated block for pasting and say plainly that the log was not written.
