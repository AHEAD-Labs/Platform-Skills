#!/usr/bin/env python3
"""Rebuild data/estimate_products.csv from a new export of the
'AHEAD Services Product Estimates Report' (CSV).

Usage: python3 scripts/refresh_data.py "<export>.csv"
Writes: data/estimate_products.csv, data/snapshot.json. Prints what was added/removed.
"""
import csv, io, json, re, sys, os
from collections import Counter
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(DATA, "estimate_products.csv")
SNAP = os.path.join(DATA, "snapshot.json")
REQ = ["Estimate Product Name", "Product: Item Code / Manufacturer SKU", "Product: Item Description",
       "Active", "Product: Item State", "Level 1 Service"]
COLS = ["P_Name", "T_Name", "SKU", "Level", "Item_Name", "OEM", "Pillar", "L1_Dept", "L2_Practice",
        "L3_SubPractice", "Category", "Subcategory", "Description", "Service_Brief_Link", "Flags"]

def read_export(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return list(csv.DictReader(io.StringIO(raw.decode(enc))))
        except UnicodeDecodeError:
            continue
    raise SystemExit("Cannot decode file")

def norm(v):
    return re.sub(r"\s+", " ", (v or "").replace("\xa0", " ")).strip()

def level_of(name):
    m = re.search(r"SL([123])-", name)
    return f"SL{m.group(1)}" if m else "UNKNOWN"

def main(path):
    rows = read_export(path)
    missing = [c for c in REQ if c not in rows[0]]
    if missing:
        raise SystemExit(f"Export is missing columns: {missing}")
    sku_count = Counter(r["Product: Item Code / Manufacturer SKU"].strip() for r in rows)
    out, dropped = [], 0
    for r in rows:
        name = norm(r["Estimate Product Name"])
        if r["Active"].strip() not in ("1", "True", "true") or r["Product: Item State"].strip() != "Orderable":
            dropped += 1
            continue
        lvl = level_of(name)
        flags = []
        if lvl == "UNKNOWN": flags.append("level-unclear")
        if (r["Level 1 Service"].strip() in ("1", "True")) != (lvl == "SL1"): flags.append("level-flag-mismatch")
        if sku_count[r["Product: Item Code / Manufacturer SKU"].strip()] > 1: flags.append("shared-sku")
        if re.search(r"\(\d of \d\)", name): flags.append("multi-part:" + re.search(r"\((\d of \d)\)", name).group(1))
        if re.search(r"\bCHS\b", name): flags.append("CHS-variant")
        desc = norm(r["Product: Item Description"])
        if not desc: flags.append("no-description")
        if "?" in name: flags.append("name-has-?")  # export turns an en dash into '?'; search Salesforce on the text before it
        out.append({
            "P_Name": name, "T_Name": "T:" + name[2:] if name.startswith("P:") else "",
            "SKU": r["Product: Item Code / Manufacturer SKU"].strip(), "Level": lvl,
            "Item_Name": r.get("Product: Item Name", "").strip(), "OEM": r.get("Product: Service OEM", "").strip(),
            "Pillar": r.get("Product: Pillar", "").strip(), "L1_Dept": r.get("Product: L1 - Department", "").strip(),
            "L2_Practice": r.get("Product: L2 - Practice", "").strip(),
            "L3_SubPractice": r.get("Product: L3 - Sub-Practice", "").strip(),
            "Category": r.get("Product: Category", "").strip(), "Subcategory": r.get("Product: Sub-category", "").strip(),
            "Description": desc, "Service_Brief_Link": r.get("Product: Service Brief Link", "").strip(),
            "Flags": ";".join(flags)})
    old = set()
    if os.path.exists(OUT):
        old = {r["P_Name"] for r in csv.DictReader(open(OUT, encoding="utf-8"))}
    os.makedirs(DATA, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(out)
    m = re.search(r"(\d{4}-\d{2}-\d{2})-(\d{2})-(\d{2})-(\d{2})", os.path.basename(path))
    date = m.group(1) if m else datetime.now().strftime("%Y-%m-%d")
    snap = {"source": "AHEAD Services Product Estimates Report (Salesforce)", "source_file": os.path.basename(path),
            "snapshot_date": date, "rows": len(out), "by_level": dict(Counter(r["Level"] for r in out))}
    json.dump(snap, open(SNAP, "w"), indent=1)
    new = {r["P_Name"] for r in out}
    print(f"Wrote {len(out)} rows (dropped {dropped} inactive/not Orderable). Snapshot {date}. Levels: {snap['by_level']}")
    if old:
        print(f"Added {len(new-old)}, removed {len(old-new)}")
        for n in sorted(new - old)[:40]: print("  + ", n)
        for n in sorted(old - new)[:40]: print("  - ", n)

if __name__ == "__main__":
    if len(sys.argv) != 2: raise SystemExit(__doc__)
    main(sys.argv[1])
