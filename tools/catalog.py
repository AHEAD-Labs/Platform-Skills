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
NO_AUDIENCE = "No audience set"
# Recommended (warning-only) frontmatter fields, as catalog columns; name and description are required, not listed here.
RECOMMENDED = ["version", "owner", "team", "platforms", "publication-status", "audience", "glean-link", "claude-link"]
MISSING_MARK = "MISSING"
NOT_SET = "(not set)"
POSSIBLE_COLUMNS = ["published entry", "skill id", "skill name", "why"]
POSSIBLE_WHY = "same after ignoring case, hyphens, underscores and spaces"
SEPARATORS_RE = re.compile(r"[\s_-]+")
AUDIENCE_COLUMNS = ["id", "description", "version", "platforms", "publication-status", "source path"]
AUDIENCE_SPLIT_RE = re.compile(r"[;,]")

KEY_RE = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_.-]*)\s*:(?:\s+(.*))?$")
BLOCK_SCALAR_RE = re.compile(r"^[>|][+-]?$")


COMMENT_RE = re.compile(r"\s#")  # a YAML comment starts at whitespace followed by '#'
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
    m = COMMENT_RE.search(value)
    return (value[:m.start()] if m else value).strip()


def _split_inline_list(value):
    """Split `[a, "b, c", 'd']` on commas outside quotes, in one linear pass."""
    inner = value.strip()[1:-1]
    if not inner.strip():
        return []
    pieces, begin, quote, at_item_start, i = [], 0, None, True, 0
    while i < len(inner):
        c = inner[i]
        if quote:
            if quote == '"' and c == "\\":
                i += 1  # skip the escaped character
            elif c == quote:
                if quote == "'" and inner[i + 1:i + 2] == "'":
                    i += 1  # '' is an escaped single quote
                else:
                    quote = None
        elif c == ",":
            pieces.append(inner[begin:i])
            begin, at_item_start = i + 1, True
        elif c not in " \t":
            if at_item_start and c in "\"'":
                quote = c
            at_item_start = False
        i += 1
    pieces.append(inner[begin:])
    if not pieces[-1].strip():
        pieces.pop()  # trailing comma
    return [_unquote(p) for p in pieces]


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


def _norm(value):
    return SEPARATORS_RE.sub("", value.lower())


def compare_published(rows, path):
    """Compare a published-skills CSV with the catalog, in both directions.

    The list needs an `id` or `name` column (header case ignored). Each entry is matched,
    ignoring case and surrounding whitespace, against each skill's folder id and frontmatter
    name. Returns a dict:
      columns         the list's own columns
      published_only  list entries with no matching folder (rows keep the list's columns)
      github_only     catalog rows whose id and name are not on the list
      possible        near-misses, listed apart: an entry that differs from a folder id or name
                      only by case-insensitive hyphens, underscores or spaces. They are never
                      treated as matches, and are left out of published_only and github_only.
    """
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames or []
            key = next((c for want in ("id", "name") for c in columns if c.strip().lower() == want), None)
            if key is None:
                raise ValueError("published list needs an 'id' or 'name' column; found: "
                                 + (", ".join(columns) or "no header"))
            entries = [{c: r.get(c) or "" for c in columns} for r in reader
                       if any(isinstance(v, str) and v.strip() for v in r.values())]
    except csv.Error as e:
        raise ValueError(f"published list is not readable as CSV: {e}") from e
    listed = {e[key].strip().lower() for e in entries if e[key].strip()}
    known = {v.strip().lower() for r in rows for v in (r["id"], r["name"]) if v.strip()}
    by_norm = {}
    for r in rows:
        for v in (r["id"], r["name"]):
            if v.strip():
                by_norm.setdefault(_norm(v), {})[r["id"]] = r
    published_only, possible = [], []
    for e in entries:
        text = e[key].strip()
        if text.lower() in known:
            continue
        near = by_norm.get(_norm(text), {}) if _norm(text) else {}
        if near:
            possible += [{"published entry": text, "skill id": r["id"], "skill name": r["name"],
                          "why": POSSIBLE_WHY} for r in near.values()]
        else:
            published_only.append(e)
    near_ids = {p["skill id"] for p in possible}
    github_only = [r for r in rows if r["id"] not in near_ids
                   and r["id"].strip().lower() not in listed and r["name"].strip().lower() not in listed]
    return {"columns": columns, "published_only": published_only,
            "github_only": github_only, "possible": possible}


def render_markdown(rows, gap=None):
    n = len(rows)
    lines = ["# Skills catalog", "",
             f"{n} skill{'s' if n != 1 else ''}, generated from `skills/*/SKILL.md` frontmatter. "
             f"Descriptions are shortened here; the CSV has the full text.", ""]
    lines += _md_table(COLUMNS, rows, {"description": MD_DESCRIPTION_MAX})
    if gap is not None:
        lines += ["", "## Published but not in GitHub", ""]
        lines += (_md_table(gap["columns"], gap["published_only"]) if gap["published_only"]
                  else ["None: every skill on the published list is in GitHub."])
        lines += ["", "## In GitHub but not on the published list", ""]
        lines += (_md_table(COLUMNS, gap["github_only"], {"description": MD_DESCRIPTION_MAX})
                  if gap["github_only"] else ["None: every skill in GitHub is on the published list."])
        lines += ["", "## Possible matches, check by hand", ""]
        lines += (["Not counted as matches in either list above.", ""] + _md_table(POSSIBLE_COLUMNS, gap["possible"])
                  if gap["possible"] else ["None: no near-misses."])
    return "\n".join(lines) + "\n"


def _audiences(row):
    """The audience values a skill declares, in order, de-duplicated ignoring case. Never inferred."""
    seen, names = set(), []
    for part in AUDIENCE_SPLIT_RE.split(row["audience"]):
        part = part.strip()
        if part and part.lower() not in seen:
            seen.add(part.lower())
            names.append(part)
    return names


def group_by_audience(rows):
    """[(heading, rows)] with one group per audience (case-insensitive, sorted) and, last, the
    skills that declare none. A skill appears under every audience it declares."""
    groups, blank = {}, []
    for row in rows:
        names = _audiences(row)
        if not names:
            blank.append(row)
        for name in names:
            groups.setdefault(name.lower(), (name, []))[1].append(row)
    result = [groups[key] for key in sorted(groups)]
    if blank:
        result.append((NO_AUDIENCE, blank))
    return result


def audience_summary(rows):
    return [f"{heading} {len(group)}" for heading, group in group_by_audience(rows)]


def render_audience_markdown(rows):
    n = len(rows)
    lines = ["# Skills by audience", "",
             f"{n} skill{'s' if n != 1 else ''}. A skill is listed under each audience it declares in its "
             f"frontmatter; skills that declare none are under \"{NO_AUDIENCE}\". Audience is never inferred.", ""]
    for heading, group in group_by_audience(rows):
        lines += [f"## {heading} ({len(group)})", ""]
        lines += _md_table(AUDIENCE_COLUMNS, group, {"description": MD_DESCRIPTION_MAX})
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def fill_in_table(rows):
    """(columns, rows) for the owners' fill-in sheet: one row per skill id, one column per recommended
    field that at least one skill is missing. A cell says MISSING or is empty. Ids and field names only."""
    columns = [c for c in RECOMMENDED if any(not r[c] for r in rows)]
    table = [{"id": r["id"], **{c: MISSING_MARK if not r[c] else "" for c in columns}} for r in rows]
    return ["id"] + columns, table


def status_counts(rows):
    """[(publication-status value, skills)] by count then value, with skills lacking one last."""
    counts = {}
    for r in rows:
        value = r["publication-status"] or NOT_SET
        counts[value] = counts.get(value, 0) + 1
    return sorted(counts.items(), key=lambda kv: (kv[0] == NOT_SET, -kv[1], kv[0]))


def write_outputs(out_dir, rows, gap=None, fill_in=False):
    """Write catalog.csv, catalog.md and catalog-by-audience.md to out_dir, plus the three
    gap-report CSVs (published-not-in-github, github-not-published, possible-matches) when a
    gap report is given, plus fill-in.csv and publication-status-values.csv when fill_in is set."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = [out / "catalog.csv", out / "catalog.md", out / "catalog-by-audience.md"]
    write_csv(paths[0], COLUMNS, rows)
    paths[1].write_text(render_markdown(rows, gap), encoding="utf-8")
    paths[2].write_text(render_audience_markdown(rows), encoding="utf-8")
    if gap is not None:
        for name, columns, data in (("published-not-in-github.csv", gap["columns"], gap["published_only"]),
                                    ("github-not-published.csv", COLUMNS, gap["github_only"]),
                                    ("possible-matches.csv", POSSIBLE_COLUMNS, gap["possible"])):
            paths.append(out / name)
            write_csv(paths[-1], columns, data)
    if fill_in:
        columns, table = fill_in_table(rows)
        paths.append(out / "fill-in.csv")
        write_csv(paths[-1], columns, table)
        paths.append(out / "publication-status-values.csv")
        write_csv(paths[-1], ["publication-status", "skills"],
                  [{"publication-status": v, "skills": str(n)} for v, n in status_counts(rows)])
    return paths


EMAIL_SPLIT_RE = re.compile(r"[^\w.+@-]+")
EMAIL_TOKEN_RE = re.compile(r"[\w.+-]+@([\w-]+(?:\.[\w-]+)+)")


def _email_parts(owner):
    """(email, domain) pairs found in an owner field. Tokenised first, then each token is
    fully matched, so a long hostile value cannot trigger quadratic regex backtracking."""
    parts = []
    for token in EMAIL_SPLIT_RE.split(owner):
        m = EMAIL_TOKEN_RE.fullmatch(token.rstrip("."))
        if m:
            parts.append((m.group(0), m.group(1).lower()))
    return parts


def owner_emails(owner):
    """Email addresses in an owner field."""
    return [email for email, _ in _email_parts(owner)]


def non_ahead_emails(owner):
    """Email addresses in an owner field whose domain is not ahead.com (possible personal emails)."""
    return [email for email, domain in _email_parts(owner)
            if domain != "ahead.com" and not domain.endswith(".ahead.com")]


def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate a skills catalog from skills/*/SKILL.md frontmatter. Writes catalog.csv, "
                    "catalog.md and catalog-by-audience.md to --out. Output is a local artifact: never commit it.",
        epilog="Audience view: each skill is listed under every value of its frontmatter `audience` "
               "(a list, or text split on commas or semicolons; matched ignoring case). Skills with no "
               "audience go under \"No audience set\". Audience is never inferred from the description.")
    parser.add_argument("--skills-dir", default=str(Path(__file__).resolve().parent.parent / "skills"),
                        help="folder holding <id>/SKILL.md (default: this repo's skills/)")
    parser.add_argument("--out", default="/tmp", help="folder for the output files (default: /tmp)")
    parser.add_argument("--published-list", metavar="CSV",
                        help="CSV of skills published elsewhere. Needs a header row with an id or name "
                             "column (any case); other columns are kept as they are. Matched, ignoring case, "
                             "against each skill's folder id and frontmatter name. Writes a gap report in both "
                             "directions (published but not in GitHub; in GitHub but not on the list) plus "
                             "possible matches to check by hand (same after ignoring hyphens, underscores and "
                             "spaces; never counted as matches)")
    parser.add_argument("--fill-in", action="store_true",
                        help="also write fill-in.csv (one row per skill id, a column per recommended field that "
                             "any skill is missing, cells say MISSING; ids and field names only) and "
                             "publication-status-values.csv (each distinct publication-status value with its "
                             "skill count)")
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
    gap = None
    if args.published_list:
        try:
            gap = compare_published(rows, args.published_list)
        except (OSError, ValueError) as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
    paths = write_outputs(out, rows, gap, fill_in=args.fill_in)

    print(f"Skills: {len(rows)}")
    print("Missing fields per skill:")
    for row in rows:
        missing = missing_fields(row)
        print(f"  {row['id']}: " + ("missing " + ", ".join(missing) if missing else "complete"))
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  {w}")
    # Skill ids only: owner values (names, emails) are personal data and are never printed.
    with_email = [r["id"] for r in rows if owner_emails(r["owner"])]
    if with_email:
        print("Owner fields containing an email address (skill ids only): " + ", ".join(with_email))
    personal = [r["id"] for r in rows if non_ahead_emails(r["owner"])]
    if personal:
        print("Owner fields with a non-AHEAD address (possible personal email; skill ids only): "
              + ", ".join(personal))
    print("Audience view: " + (", ".join(audience_summary(rows)) or "no skills"))
    if rows and not any(_audiences(r) for r in rows):
        print(f'All {len(rows)} skills are under "{NO_AUDIENCE}": none declares an audience.')
    if args.fill_in:
        columns, table = fill_in_table(rows)
        needing = sum(1 for t in table if any(t[c] for c in columns[1:]))
        print(f"Fill-in sheet: {needing} of {len(rows)} skills need at least one recommended field (fill-in.csv)")
        print("publication-status values: " + ", ".join(f"{v} {n}" for v, n in status_counts(rows)))
    if gap is not None:
        print(f"Published but not in GitHub: {len(gap['published_only'])}")
        print(f"In GitHub but not on the published list: {len(gap['github_only'])}")
        print(f"Possible matches (check by hand): {len(gap['possible'])}")
    print("Wrote:")
    for p in paths:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
