#!/usr/bin/env python3
"""Generate a lightweight skills catalog (CSV + Markdown) from skills/*/SKILL.md frontmatter.

Stdlib only. Read-only on the repo; output goes to --out (default /tmp) and is never committed.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

COLUMNS = ["id", "name", "description", "version", "owner", "team", "platforms",
           "publication-status", "audience", "source path", "glean-link", "claude-link"]
# catalog column -> SKILL.md frontmatter key (id and source path come from the folder)
FRONTMATTER_KEYS = {"name": "name", "description": "description", "version": "version",
                    "owner": "owner", "team": "team", "platforms": "ahead-platform",
                    "publication-status": "publication-status", "audience": "audience",
                    "glean-link": "glean-link", "claude-link": "claude-link"}
MAX_READ_BYTES = 256 * 1024
MD_DESCRIPTION_MAX = 200

KEY_RE = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_.-]*)\s*:(?:\s+(.*))?$")
BLOCK_SCALAR_RE = re.compile(r"^[>|][+-]?$")


SQ_RE = re.compile(r"^'((?:[^']|'')*)'\s*(?:#.*)?$")
DQ_RE = re.compile(r'^"((?:[^"\\]|\\.)*)"\s*(?:#.*)?$')


def _unquote(value):
    value = value.strip()
    m = SQ_RE.match(value)
    if m:
        return m.group(1).replace("''", "'")
    m = DQ_RE.match(value)
    if m:
        return re.sub(r'\\(["\\])', r"\1", m.group(1))
    return re.sub(r"\s+#.*$", "", value).strip()


def _split_inline_list(value):
    inner = value.strip()[1:-1].strip()
    return [_unquote(p) for p in inner.split(",")] if inner else []


def parse_frontmatter(text):
    """Return the top-level frontmatter keys of a SKILL.md as {key: str | list[str]}.

    Supports plain/quoted scalars, inline and block lists, and folded/literal block scalars.
    Returns {} when there is no complete frontmatter block.
    """
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return {}
    block = lines[1:end]
    result = {}
    i = 0
    while i < len(block):
        line = block[i]
        i += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = KEY_RE.match(line)
        if not m:
            continue
        key, raw = m.group(1), (m.group(2) or "").strip()
        if BLOCK_SCALAR_RE.match(raw):
            body = []
            while i < len(block) and (not block[i].strip() or block[i][0] in " \t"):
                body.append(block[i])
                i += 1
            stripped = [b.strip() for b in body]
            if raw.startswith(">"):
                result[key] = " ".join(s for s in stripped if s)
            else:
                result[key] = "\n".join(stripped).strip("\n")
        elif raw == "":
            items = []
            while i < len(block) and re.match(r"^\s*-(\s|$)", block[i]):
                items.append(_unquote(re.sub(r"^\s*-\s*", "", block[i])))
                i += 1
            result[key] = items if items else ""
        else:
            while (i < len(block) and block[i][:1] in (" ", "\t") and block[i].strip()
                   and not block[i].lstrip().startswith("#")):
                raw += " " + block[i].strip()
                i += 1
            result[key] = _split_inline_list(raw) if raw.startswith("[") else _unquote(raw)
    return result


def _clean(value):
    if isinstance(value, list):
        value = ", ".join(v for v in value if v)
    return " ".join(str(value).split())


def missing_fields(row):
    """Catalog columns that are blank for this row (id and source path are always set)."""
    return [c for c in COLUMNS if c not in ("id", "source path") and not row[c]]


def _read_head(path):
    with open(path, "rb") as f:
        return f.read(MAX_READ_BYTES).decode("utf-8", errors="replace")


def collect(skills_dir, root=None):
    """Return (rows, warnings) for every skills/<id>/SKILL.md, sorted by id.

    Values come only from frontmatter; absent fields stay blank (links are never invented).
    Symlinked skill folders and SKILL.md files are skipped and reported in warnings.
    """
    skills_dir = Path(skills_dir)
    root = Path(root) if root else skills_dir.parent
    rows, warnings = [], []
    for entry in sorted(skills_dir.iterdir(), key=lambda p: p.name):
        skill_md = entry / "SKILL.md"
        if entry.is_symlink():
            if skill_md.exists():
                warnings.append(f"skipped {entry.name}: skill folder is a symlink")
            continue
        if not entry.is_dir() or not (skill_md.is_symlink() or skill_md.is_file()):
            continue
        if skill_md.is_symlink():
            warnings.append(f"skipped {entry.name}: SKILL.md is a symlink")
            continue
        fm = parse_frontmatter(_read_head(skill_md))
        row = {"id": entry.name, "source path": entry.relative_to(root).as_posix() + "/"}
        for column, key in FRONTMATTER_KEYS.items():
            row[column] = _clean(fm.get(key, ""))
        rows.append(row)
    return rows, warnings


def _csv_safe(value):
    """Neutralise spreadsheet formulas: the CSV is opened in Excel and descriptions come from PRs."""
    value = str(value)
    return "'" + value if value[:1] in ("=", "+", "-", "@", "\t", "\r") else value


def write_csv(path, columns, rows):
    # utf-8-sig: Excel only reads non-ASCII text (em dashes etc.) correctly when a BOM is present.
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([_csv_safe(row.get(c, "")) for c in columns])


def _md_cell(value, limit=None):
    text = " ".join(str(value).split())
    if limit and len(text) > limit:
        text = text[:limit - 1].rstrip() + "\u2026"
    return text.replace("|", "\\|")


def _md_table(columns, rows, limits=None):
    limits = limits or {}
    lines = ["| " + " | ".join(columns) + " |", "|" + " --- |" * len(columns)]
    for row in rows:
        cells = [_md_cell(row.get(c, ""), limits.get(c)) for c in columns]
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def published_not_in_github(rows, path):
    """Read a published-skills CSV and return (columns, rows not matching any catalog skill).

    The list needs an `id` or `name` column (header case ignored); it is matched, case- and
    whitespace-insensitively, against each catalog skill's folder id and frontmatter name.
    """
    known = {v.strip().lower() for r in rows for v in (r["id"], r["name"]) if v.strip()}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        key = next((c for want in ("id", "name") for c in columns if c.strip().lower() == want), None)
        if key is None:
            raise ValueError("published list needs an 'id' or 'name' column; found: "
                             + (", ".join(columns) or "no header"))
        missing = [{c: r.get(c) or "" for c in columns} for r in reader
                   if any(isinstance(v, str) and v.strip() for v in r.values())
                   and (r.get(key) or "").strip().lower() not in known]
    return columns, missing


def render_markdown(rows, published=None):
    n = len(rows)
    lines = ["# Skills catalog", "",
             f"{n} skill{'s' if n != 1 else ''}, generated from `skills/*/SKILL.md` frontmatter. "
             f"Descriptions are shortened here; the CSV has the full text.", ""]
    lines += _md_table(COLUMNS, rows, {"description": MD_DESCRIPTION_MAX})
    if published is not None:
        columns, missing = published
        lines += ["", "## Published but not in GitHub", ""]
        lines += _md_table(columns, missing) if missing else ["None: every skill in the published list is in GitHub."]
    return "\n".join(lines) + "\n"


def write_outputs(out_dir, rows, published=None):
    """Write catalog.csv and catalog.md (plus published-not-in-github.csv when given) to out_dir."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = [out / "catalog.csv", out / "catalog.md"]
    write_csv(paths[0], COLUMNS, rows)
    paths[1].write_text(render_markdown(rows, published), encoding="utf-8")
    if published is not None:
        paths.append(out / "published-not-in-github.csv")
        write_csv(paths[2], published[0], published[1])
    return paths


EMAIL_RE = re.compile(r"[\w.+-]+@([\w-]+(?:\.[\w-]+)+)")


def non_ahead_emails(owner):
    """Email addresses in an owner field whose domain is not ahead.com (possible personal emails)."""
    found = []
    for m in EMAIL_RE.finditer(owner):
        domain = m.group(1).lower()
        if domain != "ahead.com" and not domain.endswith(".ahead.com"):
            found.append(m.group(0))
    return found


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate a skills catalog (CSV + Markdown) from skills/*/SKILL.md frontmatter. "
                    "Output is a local artifact: never commit it.")
    parser.add_argument("--skills-dir", default=str(Path(__file__).resolve().parent.parent / "skills"),
                        help="folder holding <id>/SKILL.md (default: this repo's skills/)")
    parser.add_argument("--out", default="/tmp", help="folder for the output files (default: /tmp)")
    parser.add_argument("--published-list", metavar="CSV",
                        help="CSV of published skills (needs an id or name column); adds a "
                             "'published but not in GitHub' sheet")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    skills_dir = Path(args.skills_dir).resolve()
    if not skills_dir.is_dir():
        print(f"error: {skills_dir} is not a folder", file=sys.stderr)
        return 2
    root = skills_dir.parent
    out = Path(args.out).resolve()
    if out == root or root in out.parents:
        print(f"error: --out {out} is inside the repo ({root}); the catalog is a local artifact "
              f"and must not be committed. Choose a folder outside the tree.", file=sys.stderr)
        return 2
    rows, warnings = collect(skills_dir, root)
    published = None
    if args.published_list:
        try:
            published = published_not_in_github(rows, args.published_list)
        except (OSError, ValueError) as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
    paths = write_outputs(out, rows, published)

    print(f"Skills: {len(rows)}")
    print("Missing fields per skill:")
    for row in rows:
        missing = missing_fields(row)
        print(f"  {row['id']}: " + ("missing " + ", ".join(missing) if missing else "complete"))
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  {w}")
    flagged = [(r["id"], non_ahead_emails(r["owner"])) for r in rows if non_ahead_emails(r["owner"])]
    if flagged:
        print("Owner fields with non-AHEAD emails (possible personal email):")
        for sid, emails in flagged:
            print(f"  {sid}: {', '.join(emails)}")
    if published is not None:
        print(f"Published but not in GitHub: {len(published[1])}")
    print("Wrote:")
    for p in paths:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
