#!/usr/bin/env python3
"""Find candidate estimate products in data/estimate_products.csv.

Usage:
  find_products.py "wireless site survey" ["cyber recovery" ...] [--top 15] [--oem Dell] [--practice Network]
                   [--level SL2|SL1|SL3] [--json] [--no-adjacent]
Each quoted query is one work item. Output per work item: candidate rows ranked by keyword relevance
over Item_Name, P_Name, Description, OEM, sub-practice and category. This is a RETRIEVER:
the caller must read the Description of each candidate and judge fit, and may rerun with other words.
ADJACENT: when a work item hits a cross-practice topic in data/adjacency_groups.json (e.g. Purview, Cyber Recovery),
every active row of that topic in ANY practice is also listed under "Also consider" (not ranked, not filtered by
--oem/--practice/--level). Use --no-adjacent to turn this off.
"""
import csv, json, math, os, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
SYN = {  # query word -> extra words searched
    "wifi": ["wireless", "wlan"], "wlan": ["wireless"], "wi-fi": ["wireless"],
    "survey": ["survey", "heatmap", "site"], "cyber": ["cyber"],
    "recovery": ["recovery", "crr", "ire", "vault", "isolated", "clean", "room"],
    "ransomware": ["ransomware", "recovery", "crr", "ire", "vault"],
    "vault": ["vault", "ire", "isolated", "crr"], "backup": ["backup", "data", "protection", "dprot"],
    "firewall": ["firewall", "ngfw"], "sdwan": ["sd-wan", "sdwan"], "k8s": ["kubernetes"],
    "m365": ["microsoft", "365", "m365"], "o365": ["microsoft", "365"], "aws": ["aws", "amazon"],
    "gcp": ["gcp", "google"], "vmware": ["vmware", "vcf", "broadcom"], "snow": ["servicenow"],
}
STOP = set("a an and are as at be by for from in into is it of on or the to with we our their this that will include includes including client need needs want project scope".split())

def stem(w):
    for s in ("ing", "ed", "es", "s"):
        if len(w) > len(s) + 3 and w.endswith(s): return w[: -len(s)]
    return w

def toks(text):
    return [stem(t) for t in re.findall(r"[a-z0-9][a-z0-9\-\+]*", text.lower()) if t not in STOP]

def load():
    rows = list(csv.DictReader(open(os.path.join(DATA, "estimate_products.csv"), encoding="utf-8")))
    for r in rows:
        r["_name"] = Counter(toks(" ".join([r["Item_Name"], r["P_Name"], r["SKU"]])))
        r["_body"] = Counter(toks(" ".join([r["Description"], r["OEM"], r["L3_SubPractice"], r["Category"], r["Subcategory"]])))
    df = Counter()
    for r in rows:
        for t in set(r["_name"]) | set(r["_body"]): df[t] += 1
    return rows, df

def search(rows, df, query, top, oem=None, practice=None, level=None):
    n = len(rows)
    q = []
    for w in re.findall(r"[a-z0-9][a-z0-9\-\+]*", query.lower()):
        if w in STOP: continue
        q.append((stem(w), 1.0))
        for x in SYN.get(w, []):
            if stem(x) != stem(w): q.append((stem(x), 0.5))
    qd = {}
    for t, wt in q: qd[t] = max(qd.get(t, 0), wt)
    scored = []
    for r in rows:
        if oem and oem.lower() not in r["OEM"].lower(): continue
        if practice and practice.lower() not in (r["L2_Practice"] + r["L3_SubPractice"] + r["Pillar"] + r["L1_Dept"]).lower(): continue
        if level and r["Level"] != level: continue
        s, hit = 0.0, []
        for t, wt in qd.items():
            idf = math.log(1 + n / (1 + df.get(t, 0)))
            if t in r["_name"]: s += 2.0 * wt * idf; hit.append(t)
            elif t in r["_body"]: s += 1.0 * wt * idf; hit.append(t)
        if s > 0: scored.append((s, hit, r))
    scored.sort(key=lambda x: (-x[0], {"SL2": 0, "SL1": 1, "SL3": 2}.get(x[2]["Level"], 3)))
    return scored[:top]

def load_groups():
    path = os.path.join(DATA, "adjacency_groups.json")
    return json.load(open(path, encoding="utf-8"))["groups"] if os.path.exists(path) else []

def adjacent(rows, groups, query, hits):
    """Return [(group, [rows])] for groups triggered by the query text or by the top candidates."""
    q = query.lower()
    out, seen = [], set()
    for g in groups:
        trig = re.compile(g["trigger"], re.I)
        mem = re.compile(g["members"], re.I)
        fields = g.get("member_fields", ["P_Name", "SKU", "Item_Name"])
        is_member = lambda r: bool(mem.search(" ".join(r[f] for f in fields)))
        if not (trig.search(q) or any(is_member(r) for _, _, r in hits[:3])): continue
        have = {r["P_Name"] for _, _, r in hits}
        extra = [r for r in rows if is_member(r) and r["P_Name"] not in have and r["P_Name"] not in seen]
        seen.update(r["P_Name"] for r in extra)
        extra.sort(key=lambda r: ({"SL2": 0, "SL1": 1, "SL3": 2}.get(r["Level"], 3), r["L1_Dept"], r["P_Name"]))
        if extra: out.append((g, extra))
    return out

def main(argv):
    top, oem, practice, level, as_json, queries, use_adj = 15, None, None, None, False, [], True
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--top": top = int(argv[i + 1]); i += 2
        elif a == "--oem": oem = argv[i + 1]; i += 2
        elif a == "--practice": practice = argv[i + 1]; i += 2
        elif a == "--level": level = argv[i + 1]; i += 2
        elif a == "--json": as_json = True; i += 1
        elif a == "--no-adjacent": use_adj = False; i += 1
        else: queries.append(a); i += 1
    if not queries: raise SystemExit(__doc__)
    rows, df = load()
    snap = json.load(open(os.path.join(DATA, "snapshot.json")))
    groups = load_groups() if use_adj else []
    out = {"snapshot": snap, "results": {}, "adjacent": {}}
    clean = lambda r: {k: v for k, v in r.items() if not k.startswith("_")}
    for q in queries:
        hits = search(rows, df, q, top, oem, practice, level)
        out["results"][q] = [{"score": round(s, 1), "matched": h, **clean(r)} for s, h, r in hits]
        out["adjacent"][q] = [{"group": g["id"], "label": g["label"], "products": [clean(r) for r in extra]}
                              for g, extra in adjacent(rows, groups, q, search(rows, df, q, 3))]
    if as_json: print(json.dumps(out, indent=1)); return
    print(f"Snapshot {snap['snapshot_date']} - {snap['rows']} active Orderable products\n")
    for q, res in out["results"].items():
        print(f"## {q}  ({len(res)} candidates)")
        for lvl in ("SL2", "SL1", "SL3"):
            for r in [x for x in res if x["Level"] == lvl]:
                fl = f" [{r['Flags']}]" if r["Flags"] else ""
                print(f"- {r['Level']} | {r['P_Name']} | {r['SKU']} | {r['T_Name']} | {r['OEM']} / {r['L3_SubPractice']}{fl}")
                print(f"    {r['Description'] or '(no description)'}")
        for ad in out["adjacent"].get(q, []):
            print(f"  ### ALSO CONSIDER (adjacent, cross-practice): {ad['label']} - {len(ad['products'])} more")
            for r in ad["products"]:
                d = (r["Description"] or "(no description)")
                print(f"  - {r['Level']} | {r['P_Name']} | {r['SKU']} | {r['T_Name']} | {r['L1_Dept']} / {r['L3_SubPractice']}")
                print(f"      {d[:200]}")
        print()

if __name__ == "__main__":
    main(sys.argv[1:])
