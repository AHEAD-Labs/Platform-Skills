"""Self-test for the ahead-deliverable-hub skill. Run after any change to the presets, styles or scripts.

    python3 selftest.py            # prints PASS/FAIL per check, exits 1 if anything fails

It builds every template and a custom hub into a temporary folder, fills slots, and confirms that
check.py catches the things it should (edited styles, UK spelling, em dashes, team names, open
placeholders at handover). Nothing is written outside the temporary folder.
"""
import json, pathlib, re, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / 'assets'
PY = sys.executable
results = []


def run(*args):
    p = subprocess.run([PY, *map(str, args)], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def check(name, cond):
    results.append((name, bool(cond)))
    print(('PASS  ' if cond else 'FAIL  ') + name)


def main():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='hub-selftest-'))
    build, chk, fill, guide = HERE / 'build.py', HERE / 'check.py', HERE / 'fill_slot.py', HERE / 'guide.py'
    passed = lambda out: 'Result: PASS' in out

    # 1. every way in builds and passes
    for preset in ('phase-1', 'phase-2', 'base'):
        out_html = tmp / f'{preset}.html'
        rc, _ = run(build, '--preset', preset, '--client', 'Contoso', '--date', 'March 5, 2027', '--out', out_html)
        rc2, out = run(chk, out_html, '--client', 'Contoso')
        check(f'build and check: {preset}', rc == 0 and passed(out))
    html2 = (tmp / 'phase-2.html').read_text(encoding='utf-8')
    check('stamp records the template version', re.search(r'template=target-design [\d.]+ \(agreed baseline\)', html2))
    _, out = run(build, '--preset', 'phase-2', '--client', 'X', '--out', tmp / 'x.html')
    check('baseline note is printed', 'agreed baseline' in out)
    rc, out = run(build, '--preset', 'phase-9', '--out', tmp / 'y.html')
    check('unknown template is rejected', rc != 0 and 'unknown preset' in out)
    check('no client logo option in output', 'client_logo' not in html2)

    # 2. custom hub from SOW-style deliverables
    cfg = json.loads((ASSETS / 'presets' / 'blank.json').read_text(encoding='utf-8'))
    cfg.update(client='Contoso', engagement='Data Platform', phase='Assessment', date='March 5, 2027',
               owners={'Lead Architect': 'Jane Doe'})
    cfg['tabs'] = [cfg['tabs'][0], {'key': 'readiness', 'label': 'Readiness Scorecard', 'deliverable': {
        'id': 'D1', 'title': 'Readiness Scorecard', 'owner': 'Lead Architect',
        'question': 'How ready is each platform for production?',
        'sections': [['scores', 'Scores by platform', 'One row per platform.'],
                     {'key': 'gaps', 'title': 'Gaps', 'columns': ['Gap', 'Impact', 'Owner']}],
        'criteria': [['Scorecard covering all platforms', ['scores']], ['Prioritized gap list', ['gaps']]],
        'summary': True, 'decisions': True}}]
    (tmp / 'custom.json').write_text(json.dumps(cfg), encoding='utf-8')
    custom = tmp / 'custom.html'
    rc, _ = run(build, tmp / 'custom.json', '--out', custom)
    _, out = run(chk, custom, '--client', 'Contoso')
    check('custom hub from SOW deliverables', rc == 0 and passed(out))

    # 3. fill slots on the latest file
    _, listing = run(fill, custom, '--list', '--empty')
    key = (re.findall(r'readiness-[a-z-]+', listing) or ['readiness-summary-text'])[0]
    rc, _ = run(fill, custom, '--key', 'overview-cover-stats', '--values', '12,4,3', '--in-place')
    check('fill headline numbers', rc == 0)
    (tmp / 's.md').write_text('Platform A scored 3 of 5.', encoding='utf-8')
    rc, _ = run(fill, custom, '--key', key, '--md', tmp / 's.md', '--in-place')
    check(f'fill a section from Markdown ({key})', rc == 0 and 'Platform A scored 3 of 5.' in custom.read_text(encoding='utf-8'))
    _, out = run(chk, custom, '--client', 'Contoso')
    check('check still passes after filling', passed(out))
    _, out = run(chk, custom, '--client', 'Contoso', '--final')
    check('--final blocks handover while placeholders remain', 'Result: FAIL' in out)
    rc, _ = run(guide, custom, '--out', tmp / 'g.md')
    check('contributor guide is written', rc == 0 and (tmp / 'g.md').stat().st_size > 0)

    # 3b. a hub with every slot filled reaches handover (regression: filled headline numbers were still listed as open)
    _, listing = run(fill, custom, '--list')
    check('filled headline numbers are listed as filled', not re.search(r'TO FILL\s+\S+\s+overview-cover-stats', listing))
    full = tmp / 'full.html'; full.write_text(custom.read_text(encoding='utf-8'), encoding='utf-8')
    _, open_slots = run(fill, full, '--list', '--empty')
    last = ''
    for k in re.findall(r'^TO FILL\s+.*?\s([a-z0-9]+(?:-[a-z0-9]+)+)\s', open_slots, re.M):
        _, last = run(fill, full, '--key', k, '--text', 'Content added by the self-test.', '--force', '--in-place')
    _, out = run(chk, full, '--client', 'Contoso', '--final')
    check('--final passes once every slot is filled', 'Result: PASS' in out)
    check('placeholder count reaches zero once every slot is filled', '(0 placeholders left' in last)

    # 3c. structured slots are not overwritten by plain content (regression: --text replaced a filled register)
    gate = tmp / 'guard.html'
    rc, _ = run(build, '--preset', 'phase-1', '--client', 'Contoso', '--out', gate)
    (tmp / 'reg.json').write_text(json.dumps({'type': 'register', 'key': 'register-items-list', 'items': [
        {'id': 'H001', 'kind': 'hypothesis', 'title': 'Central identity', 'statement': 'One identity provider.',
         'priority': 'High', 'status': 'Open', 'area': 'Identity', 'evidence': 'Session 1', 'next': 'Test it'}]}), encoding='utf-8')
    run(fill, gate, '--key', 'register-items-list', '--block', tmp / 'reg.json', '--in-place')
    rc, out = run(fill, gate, '--key', 'register-items-list', '--text', 'oops', '--in-place')
    text = gate.read_text(encoding='utf-8')
    check('plain text does not replace a filled register', rc != 0 and 'H001' in text and 'oops' not in text)
    check('the refusal says nothing was changed and names the options', 'Nothing was changed' in out and '--force' in out)
    rc, _ = run(fill, gate, '--key', 'estate-platforms-table', '--text', 'oops', '--in-place')
    check('plain text does not replace an empty table slot', rc != 0 and '<tbody>' in gate.read_text(encoding='utf-8'))
    rc, _ = run(fill, gate, '--key', 'register-items-list', '--text', 'Note after the register.', '--append', '--in-place')
    text = gate.read_text(encoding='utf-8')
    check('--append adds after a register and keeps it', rc == 0 and 'H001' in text and 'Note after the register.' in text)
    rc, _ = run(fill, gate, '--key', 'register-items-list', '--text', 'Replaced on purpose.', '--force', '--in-place')
    check('--force replaces a register when asked', rc == 0 and 'Replaced on purpose.' in gate.read_text(encoding='utf-8'))
    prose = tmp / 'prose.html'
    run(build, '--preset', 'phase-1', '--client', 'Contoso', '--out', prose)
    run(fill, prose, '--key', 'overview-headline-text', '--text', 'First draft.', '--in-place')
    rc, _ = run(fill, prose, '--key', 'overview-headline-text', '--text', 'Second draft.', '--in-place')
    check('prose slots can still be rewritten without --force', rc == 0 and 'Second draft.' in prose.read_text(encoding='utf-8'))

    # 4. look and house-style guards
    base = (tmp / 'phase-1.html').read_text(encoding='utf-8')
    css = (ASSETS / 'hub.css').read_text(encoding='utf-8')
    cases = {
        'extra style block is rejected': base.replace('</head>', '<style>body{color:red}</style></head>', 1),
        'rules added inside the style block are rejected': base.replace('<style>', '<style>body{color:red}\n', 1),
        'edited built-in styles are rejected': base.replace(css, css.replace('#', '#f', 1), 1),
    }
    for name, text in cases.items():
        f = tmp / 'tamper.html'; f.write_text(text, encoding='utf-8')
        _, out = run(chk, f, '--client', 'Contoso')
        check(name, 'Result: FAIL' in out)
    (tmp / 'u.md').write_text('The organisation will prioritise the programme — Jane Doe agreed.', encoding='utf-8')
    c2 = tmp / 'c2.html'; c2.write_text(custom.read_text(encoding='utf-8'), encoding='utf-8')
    run(fill, c2, '--key', 'overview-approach', '--md', tmp / 'u.md', '--in-place')
    _, out = run(chk, c2, '--client', 'Contoso', '--internal-names', 'Jane Doe')
    check('UK spelling is flagged', re.search(r'organisation|prioritise|programme', out))
    check('em dash is flagged', re.search(r'dash', out, re.I))
    check('delivery-team name is flagged', 'Jane Doe' in out)
    _, out = run(chk, tmp / 'phase-1.html', '--client', 'contoso')
    check('client-name casing is checked', 'Contoso' in out)

    failed = [n for n, ok in results if not ok]
    print(f'\n{len(results) - len(failed)} of {len(results)} checks passed. Files in {tmp}')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
