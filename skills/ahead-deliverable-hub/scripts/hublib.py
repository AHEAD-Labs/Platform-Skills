"""Shared helpers for the AHEAD deliverable hub scripts: escaping, a small Markdown converter,
token substitution and the slot markup that every editable section uses."""
import html as _html
import re

def e(s):
    return _html.escape('' if s is None else str(s), quote=True)

# ------------------------------------------------------------------ tokens
TOKEN_RE = re.compile(r'\{(client|engagement|phase|next_phase|prev_phase|p|np|date|start|package)\}')

def make_tokens(cfg):
    p = cfg.get('phase_number')
    phase = cfg.get('phase') or (f'Phase {p}' if p else 'This phase')
    nxt = cfg.get('next_phase') or (f'Phase {p + 1}' if isinstance(p, int) else 'The next phase')
    prv = cfg.get('prev_phase') or (f'Phase {p - 1}' if isinstance(p, int) and p > 1 else 'The previous phase')
    t = {
        'client': cfg.get('client', 'Client'),
        'engagement': cfg.get('engagement', ''),
        'phase': phase,
        'next_phase': nxt,
        'prev_phase': prv,
        'p': str(p) if p is not None else '',
        'np': str(p + 1) if isinstance(p, int) else '',
        'date': cfg.get('date', ''),
        'start': cfg.get('start_date', ''),
    }
    t['package'] = cfg.get('package') or f"{phase} Deliverable Package"
    t['package'] = TOKEN_RE.sub(lambda m: t.get(m.group(1), m.group(0)), t['package'])
    return t

def subst(obj, tokens):
    """Replace {client}, {phase}, {next_phase}, {date} ... everywhere in a config tree."""
    if isinstance(obj, str):
        return TOKEN_RE.sub(lambda m: tokens.get(m.group(1), m.group(0)), obj)
    if isinstance(obj, list):
        return [subst(x, tokens) for x in obj]
    if isinstance(obj, dict):
        return {k: subst(v, tokens) for k, v in obj.items()}
    return obj

# ------------------------------------------------------------------ markdown
TAG_RE = re.compile(r'^\[(ok|warn|bad|info|star)\]\s+(.*)$', re.S)

def tag(kind, text):
    return f'<span class="tag t-{kind}">{text}</span>'

def mdi(s):
    """Inline Markdown: **bold**, *italic*, `code`, [text](#anchor), [[ITEM-ID]] register links,
    and a leading [ok]/[warn]/[bad]/[info]/[star] status tag. Raw HTML is passed through."""
    if s is None:
        return ''
    s = str(s)
    if s.lstrip().startswith('<'):
        return s
    m = TAG_RE.match(s.strip())
    if m:
        return tag(m.group(1), mdi(m.group(2)))
    out = e(s)
    out = re.sub(r'`([^`]+)`', r'<code>\1</code>', out)
    out = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', out)
    out = re.sub(r'(?<![*\w])\*([^*\n]+)\*(?!\*)', r'<i>\1</i>', out)
    out = re.sub(r'\[\[([A-Za-z0-9_.\-]+)\]\]',
                 lambda m: f'<a class="xref" href="#ri-{m.group(1)}" onclick="return goItem(\'{m.group(1)}\')">{m.group(1)}</a>', out)
    def link(m):
        text, href = m.group(1), _html.unescape(m.group(2))
        if href.startswith('#'):
            k = href[1:]
            return f'<a href="#{e(k)}" onclick="return goAnchor(\'{e(k)}\')">{text}</a>'
        return f'<a href="{e(href)}" target="_blank" rel="noopener">{text}</a>'
    out = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', link, out)
    return out

def md(s):
    """Block Markdown: paragraphs, #### headings, - bullets, 1. numbered lists, > callouts.
    A string that starts with '<' is treated as raw HTML and returned unchanged."""
    if s is None:
        return ''
    if isinstance(s, list):
        s = '\n\n'.join(str(x) for x in s)
    s = str(s).strip('\n')
    if s.lstrip().startswith('<'):
        return s
    out, para, lst, ltype, quote = [], [], [], None, []
    def flush_para():
        if para:
            out.append('<p>' + mdi(' '.join(para)) + '</p>')
            para.clear()
    def flush_list():
        nonlocal ltype
        if lst:
            out.append(f'<{ltype}>' + ''.join(f'<li>{mdi(x)}</li>' for x in lst) + f'</{ltype}>')
            lst.clear()
        ltype = None
    def flush_quote():
        if quote:
            out.append('<div class="callout">' + mdi(' '.join(quote)) + '</div>')
            quote.clear()
    for raw in s.split('\n'):
        line = raw.rstrip()
        st = line.strip()
        if not st:
            flush_para(); flush_list(); flush_quote(); continue
        mh = re.match(r'^#{2,4}\s+(.*)$', st)
        mb = re.match(r'^[-*]\s+(.*)$', st)
        mn = re.match(r'^\d+[.)]\s+(.*)$', st)
        mq = re.match(r'^>\s?(.*)$', st)
        if mh:
            flush_para(); flush_list(); flush_quote(); out.append(f'<h4>{mdi(mh.group(1))}</h4>')
        elif mb or mn:
            flush_para(); flush_quote()
            want = 'ul' if mb else 'ol'
            if ltype and ltype != want:
                flush_list()
            ltype = want
            lst.append((mb or mn).group(1))
        elif mq:
            flush_para(); flush_list(); quote.append(mq.group(1))
        elif lst and raw.startswith(('  ', '\t')):
            lst[-1] += ' ' + st
        else:
            flush_list(); flush_quote(); para.append(st)
    flush_para(); flush_list(); flush_quote()
    return '\n'.join(out)

# ------------------------------------------------------------------ owners and placeholders
def initials(name):
    words = [w for w in re.split(r'\s+', str(name).strip()) if w and w[0].isalnum()]
    return (''.join(w[0] for w in words[:2]) or '?').upper()

ICONS = {
    'text': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>',
    'diagram': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="8.5" y="16" width="7" height="5" rx="1.5"/><path d="M6.5 8v3h11V8M12 11v5"/></svg>',
    'table': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 10h18M9 10v10"/></svg>',
    'data': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="5" height="5" rx="1"/><rect x="10" y="3" width="5" height="5" rx="1"/><rect x="17" y="3" width="4" height="5" rx="1"/><rect x="3" y="10" width="5" height="5" rx="1"/><rect x="10" y="10" width="5" height="5" rx="1"/><rect x="3" y="17" width="5" height="4" rx="1"/></svg>',
}

def ph(guide, owner, kind='text'):
    ico = ICONS.get(kind, ICONS['text'])
    return (f'<div class="ph" data-kind="{e(kind)}" data-owner="{e(owner)}"><span class="ph-ico" aria-hidden="true">{ico}</span>'
            f'<div class="ph-main"><p class="ph-g">{mdi(guide)}</p>'
            f'<span class="ph-o"><span class="av">{e(initials(owner))}</span>{e(owner)}</span></div></div>')

def slot_open(key, label, owner, how):
    return (f'\n<!-- ================================================================\n'
            f'     SLOT: {key}\n     Section: {label}\n     Owner: {owner}\n     {how}\n'
            f'     ================================================================ -->\n'
            f'<div class="slot" id="{e(key)}" data-owner="{e(owner)}" data-label="{e(label)}">\n')

def slot_close(key):
    return f'\n</div>\n<!-- END SLOT: {key} -->\n'

HOW_TEXT = 'Replace the placeholder <div class="ph">...</div> below with your content.'
HOW_TABLE = 'Add one <tr> per entry, then delete the placeholder row (class="ph-row").'
HOW_STATS = 'Replace each <span class="skel"></span> with the number; adjust the labels if needed.'
HOW_DATA = 'Fill with: fill_slot.py FILE --key <this key> --block block.json (a register or heatmap block), or rebuild while the file is unedited.'
