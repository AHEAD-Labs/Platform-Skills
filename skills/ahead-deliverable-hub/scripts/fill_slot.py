#!/usr/bin/env python3
"""Fill or list slots in an existing hub HTML file without touching anything else.
Use this on the team's latest file instead of rebuilding, so their edits are kept.

List slots
  python3 fill_slot.py hub.html --list [--owner "Name"] [--tab controls] [--empty]

Fill a slot (write a new version with --out, or use --in-place)
  python3 fill_slot.py hub.html --key controls-standards-body --md content.md --out "hub v5.html"
  python3 fill_slot.py hub.html --key controls-standards-body --text "Paragraph one.\n\n- point" --in-place
  python3 fill_slot.py hub.html --key controls-decisions-table --rows rows.json --in-place   (JSON list of lists, or .csv)
  python3 fill_slot.py hub.html --key overview-cover-stats --values "14,32,6" --in-place
  python3 fill_slot.py hub.html --key architecture-glance-body --image target.png --caption "..." --in-place
  python3 fill_slot.py hub.html --key register-items-list --block register.json --in-place   (any block type, rendered by build.py)
Add --append to keep existing content and add the new content after it.
Plain-content options (--text, --md, --html-file, --image) refuse a slot that holds a table, register, heatmap, gantt or
headline numbers, and change nothing. Use --rows, --block or --values for those, --append to add after them, or --force to replace them.
"""
import argparse, base64, csv, json, mimetypes, pathlib, re, sys
from hublib import md, mdi, e
from guide import slots, tab_labels


def locate(html, key):
    m = re.search(r'<div class="slot" id="%s"[^>]*>' % re.escape(key), html)
    end = html.find(f'<!-- END SLOT: {key} -->')
    if not m or end < 0:
        raise SystemExit(f'Slot "{key}" not found, or its END SLOT marker is missing. Run with --list to see slot keys.')
    close = html.rfind('</div>', m.end(), end)
    if close < 0:
        raise SystemExit(f'Slot "{key}" has no closing </div> before its END SLOT marker.')
    return m.end(), close


STRUCTURED = ('<table', 'class="rg', 'class="stats"', 'class="g-', 'class="hm')


def is_structured(inner):
    """True if the slot holds a table, register, heatmap, gantt or headline numbers (not plain prose)."""
    visible = re.sub(r'<!--[\s\S]*?-->', '', inner)
    return any(m in visible for m in STRUCTURED)


def strip_placeholder(inner):
    inner = re.sub(r'\s*<div class="ph"[\s\S]*?</div></div>', '', inner, count=1)
    return inner.strip('\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('html')
    ap.add_argument('--list', action='store_true'); ap.add_argument('--owner'); ap.add_argument('--tab'); ap.add_argument('--empty', action='store_true')
    ap.add_argument('--key')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--md', help='Markdown file ("-" for stdin)'); g.add_argument('--html-file', help='HTML fragment file')
    g.add_argument('--text', help='Markdown string'); g.add_argument('--rows', help='JSON list of rows, or CSV with a header row')
    g.add_argument('--values', help='comma-separated values for a headline-numbers slot'); g.add_argument('--image', help='image file to embed')
    g.add_argument('--block', help='JSON file with one block (register, heatmap, table, glossary, gantt...) rendered by the build engine')
    ap.add_argument('--client', help='client name for {client} tokens in --block content')
    ap.add_argument('--caption'); ap.add_argument('--alt')
    ap.add_argument('--append', action='store_true')
    ap.add_argument('--force', action='store_true', help='allow --text/--md/--html-file/--image to replace a table, register, heatmap, gantt or headline numbers')
    ap.add_argument('--out'); ap.add_argument('--in-place', action='store_true')
    a = ap.parse_args()
    path = pathlib.Path(a.html)
    html = path.read_text(encoding='utf-8')

    if a.list:
        labels = tab_labels(html)
        for tab, key, label, owner, filled in slots(html):
            if a.owner and a.owner.lower() not in owner.lower():
                continue
            if a.tab and a.tab != tab:
                continue
            if a.empty and filled:
                continue
            print(f'{"filled " if filled else "TO FILL"}  {labels.get(tab, tab):<34} {key:<40} {owner:<24} {label}')
        return

    if not a.key:
        ap.error('--key is required (or use --list)')
    if not (a.out or a.in_place):
        ap.error('choose --out NEW_FILE (recommended: a new version) or --in-place')
    s, c = locate(html, a.key)
    inner = html[s:c]

    if a.block:
        from build import Hub
        bp = pathlib.Path(a.block)
        blk = json.loads(bp.read_text(encoding='utf-8'))
        blk['key'] = a.key
        hub = Hub({'client': a.client or 'Client', 'tabs': [{'key': 'x', 'label': 'x', 'sections': []}]}, bp.parent)
        hub.keys.discard(a.key)
        out_html = hub.block(blk, hub.tabs[0], {'id': 'x', 'title': ''})
        m = re.search(r'<div class="slot" id="%s"[^>]*>\n?' % re.escape(a.key), out_html)
        endm = out_html.rfind('\n</div>\n<!-- END SLOT')
        inner = '\n' + (out_html[m.end():endm] if m and endm > 0 else out_html) + '\n'
    elif a.rows:
        p = pathlib.Path(a.rows)
        if p.suffix.lower() == '.csv':
            with open(p, newline='', encoding='utf-8-sig') as f:
                rows = list(csv.reader(f))[1:]
        else:
            rows = json.loads(p.read_text(encoding='utf-8'))
        trs = ''.join('<tr>' + ''.join(f'<td>{mdi(x)}</td>' for x in r) + '</tr>\n' for r in rows)
        if '</tbody>' not in inner:
            raise SystemExit(f'Slot "{a.key}" is not a table slot.')
        inner = re.sub(r'\s*<tr class="ph-row">[\s\S]*?</tr>\n?', '\n', inner, count=1)
        inner = inner.replace('</tbody>', trs + '</tbody>', 1)
    elif a.values:
        vals = [v.strip() for v in a.values.split(',')]
        n = len(re.findall(r'<span class="skel"[^>]*></span>', inner))
        if n == 0:
            raise SystemExit(f'Slot "{a.key}" has no number placeholders left.')
        it = iter(vals)
        inner = re.sub(r'<span class="skel"[^>]*></span>', lambda m: e(next(it, '')) or m.group(0), inner)
    else:
        if a.image:
            p = pathlib.Path(a.image)
            mime = mimetypes.guess_type(str(p))[0] or 'image/png'
            uri = f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()
            new = (f'<figure><img src="{uri}" alt="{e(a.alt or a.caption or "")}">'
                   + (f'<figcaption>{mdi(a.caption)}</figcaption>' if a.caption else '') + '</figure>')
        elif a.md:
            new = md(sys.stdin.read() if a.md == '-' else pathlib.Path(a.md).read_text(encoding='utf-8'))
        elif a.html_file:
            new = pathlib.Path(a.html_file).read_text(encoding='utf-8')
        elif a.text is not None:
            new = md(a.text.replace('\\n', '\n'))
        else:
            ap.error('give content: --md, --html-file, --text, --rows, --values or --image')
        if is_structured(inner) and not (a.append or a.force):
            raise SystemExit(f'Slot "{a.key}" holds structured content (a table, register, heatmap, gantt or headline numbers). '
                             'Nothing was changed. Use --rows, --block or --values for it, add --append to keep it and add content after it, '
                             'or add --force to replace it.')
        kept = strip_placeholder(inner)
        inner = '\n' + ((kept + '\n') if (a.append and kept.strip()) else '') + new + '\n'
    out = html[:s] + inner + html[c:]
    dest = path if a.in_place else pathlib.Path(a.out)
    dest.write_text(out, encoding='utf-8')
    visible = re.sub(r'<!--[\s\S]*?-->', '', out)
    left = visible.count('<div class="ph" ') + visible.count('<span class="skel"')
    print(f'filled {a.key} -> {dest}  ({left} placeholders left in the file)')


if __name__ == '__main__':
    main()
