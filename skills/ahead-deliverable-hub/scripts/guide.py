#!/usr/bin/env python3
"""Write the contributor guide (Markdown) for a hub, reading the slots from the HTML itself,
so it stays accurate after people have edited the file.

  python3 guide.py hub.html --out "How to add content.md"
"""
import argparse, html as H, pathlib, re

SLOT_RE = re.compile(r'SLOT: (\S+)\s*\n\s*Section: (.*?)\s*\n\s*Owner: (.*?)\s*\n', re.S)
TAB_RE = re.compile(r'<!-- #+ TAB: (\S+) #+ -->')


def slots(html):
    """Return [(tab, key, label, owner, filled)] in document order."""
    tabs = [(m.start(), m.group(1)) for m in TAB_RE.finditer(html)]
    out = []
    for m in SLOT_RE.finditer(html):
        key, label, owner = m.group(1), m.group(2).strip(), m.group(3).strip()
        tab = next((t for pos, t in reversed(tabs) if pos < m.start()), '')
        end = html.find(f'<!-- END SLOT: {key} -->', m.end())
        body = html[m.end():end if end > 0 else m.end()]
        # The instruction comment (rest of the SLOT header) can quote '<span class="skel">'; only the markup after it counts.
        body = body.split('-->', 1)[-1]
        filled = '<div class="ph" ' not in body and '<span class="skel"' not in body
        out.append((tab, key, label, owner, filled))
    return out


def tab_labels(html):
    return {k: H.unescape(v) for k, v in re.findall(r'data-tab="([^"]+)"><span class="tl">(.*?)</span>', html)}


SNIPPETS = r'''
## Building blocks

Paste these inside your slot in place of the placeholder. Styling is already in the file.

Paragraph and sub-heading

```html
<h4>Sub-heading</h4>
<p>Your text. Use <b>bold</b> for the few words that matter most.</p>
```

Bulleted or numbered list

```html
<ul><li>First point</li><li>Second point</li></ul>
<ol><li>First step</li><li>Second step</li></ol>
```

Callout (one key point you want the reader to notice)

```html
<div class="callout">The one thing the reader must take away.</div>
```

Two columns

```html
<div class="two"><div><h4>Left</h4><p>...</p></div><div><h4>Right</h4><p>...</p></div></div>
```

Table row (inside a table slot: add rows, then delete the row with class="ph-row")

```html
<tr><td>ID-01</td><td>Text</td><td>Text</td></tr>
```

Status tags

```html
<span class="tag t-ok">Agreed</span> <span class="tag t-warn">Partially proven</span>
<span class="tag t-bad">Not proven</span> <span class="tag t-info">Open</span> <span class="tag t-star">Decision point</span>
```

Figure (the image must be embedded, not linked; ask Claude to embed it, or use fill_slot.py --image)

```html
<figure><img src="data:image/png;base64,..." alt="What the diagram shows"><figcaption>Caption</figcaption></figure>
```

Link to another tab or section inside the hub

```html
<a href="#architecture" onclick="return goAnchor('architecture')">Target Architecture</a>
```
'''

RULES = '''
## House style

- Write for the client's senior readers: conclusion first, then the reasoning and evidence.
- Consultative and precise. Avoid casual or hype phrasing ("bottom line", "landed on", "excited about", "game-changer", "best-in-class").
- US English (organization, prioritize, program), unless the hub is set to UK English. The client's name exactly as they write it, no em dashes.
- Everything lives in the hub: no links to SharePoint, attachments or "see the deck".
- No delivery-team names in the content. Owners appear only on placeholders, which disappear as you fill them.
- Write as of the hub's final date. Avoid "so far", "this week", "to date" or "in progress".
- Distinguish what was heard, what was observed, what was tested and what is a recommendation.
'''


def make_guide(html):
    title = H.unescape((re.search(r'<title>(.*?)</title>', html) or [None, 'Engagement hub'])[1])
    labels = tab_labels(html)
    ss = slots(html)
    owners = {}
    for tab, key, label, owner, filled in ss:
        owners.setdefault(owner, []).append((tab, key, label, filled))
    todo = sum(1 for s in ss if not s[4])
    name = re.sub(r'\s*(hub)\s*$', '', title, flags=re.I)
    md = [f'# How to add content to the {name} hub', '',
          f'The hub is one HTML file. Every section that needs content is a marked slot with an owner. '
          f'There are {len(ss)} slots; {todo} still show a placeholder.', '',
          '## Steps', '',
          '1. In SharePoint, select the file and choose **Check out**, so nobody else edits it at the same time.',
          '2. Download it and open it in a text editor (VS Code, Notepad++ or similar).',
          '3. Search for `SLOT:` followed by the slot key listed below. Each slot comment names its section and owner.',
          '4. Replace the whole `<div class="ph">...</div>` inside the slot with your content. Keep the `SLOT` and `END SLOT` comments.',
          '5. Open the file in a browser to check it. Add `?check` to the end of the address to see the placeholders still to fill.',
          '6. Upload it back to the same place in SharePoint (same file name) and choose **Check in**, with a one-line comment on what you changed.',
          '', 'Update your sections at least once a week rather than at the end.', '']
    md.append('## Slots by owner\n')
    for owner in sorted(owners):
        items = owners[owner]
        left = sum(1 for x in items if not x[3])
        md.append(f'### {owner} ({left} to fill of {len(items)})\n')
        cur = None
        for tab, key, label, filled in items:
            if tab != cur:
                md.append(f'\n**{labels.get(tab, tab)}**\n')
                cur = tab
            md.append(f'- {"[x]" if filled else "[ ]"} {label} (`{key}`)')
        md.append('')
    md.append(SNIPPETS)
    md.append(RULES)
    return '\n'.join(md) + '\n'


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('html')
    ap.add_argument('--out')
    a = ap.parse_args()
    text = make_guide(pathlib.Path(a.html).read_text(encoding='utf-8'))
    if a.out:
        pathlib.Path(a.out).write_text(text, encoding='utf-8')
        print('guide written to', a.out)
    else:
        print(text)
