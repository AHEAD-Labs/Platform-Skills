#!/usr/bin/env python3
"""Build report rows in canonical column order.

Usage: format_report_row.py run.json
run.json: {"run": {...run-level fields...}, "items": [{...item fields...}]}
Prints JSON: {"header": [...], "rows": [[...], ...]} (rows ready for an Excel range write).
"""
import json, sys, uuid
from datetime import datetime
from zoneinfo import ZoneInfo

HEADER = ["Run ID", "Run Date/Time (CT)", "Requested By", "Mode", "Input Type", "Input Name",
          "Scope Summary", "Item #", "AHEAD Solution (Unity)", "SKU", "Unity Item Name",
          "Unity Item State", "Level", "Estimate Product (P:)", "Estimate Template (T:)",
          "P Active", "T Active", "Practice (L3)", "Multi-practice", "Why It Fits", "Flags",
          "Confidence", "Data Freshness"]
RUN = ["requested_by", "mode", "input_type", "input_name", "scope_summary"]
ITEM = ["solution", "sku", "item_name", "item_state", "level", "estimate_product",
        "estimate_template", "p_active", "t_active", "practice", "multi_practice",
        "why", "flags", "confidence", "freshness"]

def clean(v, limit=500):
    s = "" if v is None else str(v).replace("\t", " ").replace("\r", " ").replace("\n", " ").strip()
    return s[:limit]

def build(data):
    run = data["run"]
    rid = run.get("run_id") or uuid.uuid4().hex[:8]
    now = "'" + datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d %H:%M")  # leading apostrophe keeps Excel from converting to a serial number
    items = data.get("items") or [{}]
    rows = []
    for i, it in enumerate(items):
        n = it.get("item_no", 0 if not data.get("items") else i + 1)
        row = [rid, now] + [clean(run.get(k), 300 if k == "scope_summary" else 200) for k in RUN]
        row += [n] + [clean(it.get(k)) for k in ITEM]
        if not data.get("items"):
            row[HEADER.index("Why It Fits")] = "No active match"
        rows.append(row)
    return {"header": HEADER, "rows": rows}

if __name__ == "__main__":
    print(json.dumps(build(json.load(open(sys.argv[1]))), indent=1))
