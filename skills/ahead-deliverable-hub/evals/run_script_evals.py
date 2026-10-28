#!/usr/bin/env python3
"""Run the script-checkable evaluation assertions for ahead-deliverable-hub.

    python3 evals/run_script_evals.py            # prints PASS/FAIL per assertion id, exits 1 on any failure
    python3 evals/run_script_evals.py --json     # same results as JSON, for recording in evals.json

Standard library only. Builds hubs from the presets in a temporary folder and uses synthetic data
(client names "Acme Corp" and "Beta Bank" are placeholders). Nothing is written outside that folder.
Model-behavior cases (way-in question, SOW conflict, non-trigger, cross-client refusal, fixed-look
explanation) cannot be run by a script; they stay not_run until a person runs them in Claude.
"""
import json, pathlib, re, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / 'scripts'
PY = sys.executable
results = {}


def run(*args):
    p = subprocess.run([PY, *map(str, args)], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def record(aid, ok, note):
    results[aid] = {'passed': bool(ok), 'note': note}
    print(('PASS  ' if ok else 'FAIL  ') + f'{aid}  {note}')


def slot_states(html):
    _, out = run(S / 'fill_slot.py', html, '--list')
    states = {}
    for line in out.splitlines():
        m = re.search(r'\s([a-z0-9]+(?:-[a-z0-9]+)+)\s', line)
        if m:
            states[m.group(1)] = line.split()[0] == 'filled'
    return states


def empty_keys(html):
    return [k for k, filled in slot_states(html).items() if not filled]


def main():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='hub-evals-'))
    skill_version = re.search(r"VERSION = '([^']+)'", (S / 'build.py').read_text(encoding='utf-8')).group(1)

    # HP-1: target design hub, fill three slots, nothing else changes
    t = tmp / 'hp1.html'
    rc, _ = run(S / 'build.py', '--preset', 'target-design', '--client', 'Acme Corp', '--out', t)
    stamp = re.search(r'ahead-deliverable-hub ([0-9.]+); look=', t.read_text(encoding='utf-8'))
    record('HP1-1', rc == 0 and stamp and stamp.group(1) == skill_version, f'build exit {rc}; stamp version {stamp and stamp.group(1)}')
    before = slot_states(t)
    (tmp / 'c.md').write_text('The target platform is ready for the design gate.\n', encoding='utf-8')
    run(S / 'fill_slot.py', t, '--key', 'overview-conclusion-text', '--md', tmp / 'c.md', '--in-place')
    run(S / 'fill_slot.py', t, '--key', 'overview-cover-stats', '--values', '18,42,6', '--in-place')
    run(S / 'fill_slot.py', t, '--key', 'overview-approach', '--text', 'We held six working sessions.', '--in-place')
    after = slot_states(t)
    changed = sorted(k for k in before if before[k] != after.get(k))
    record('HP1-2', changed == ['overview-approach', 'overview-conclusion-text', 'overview-cover-stats'], f'slots changed: {changed}')
    rc1, _ = run(S / 'check.py', t, '--client', 'Acme Corp')
    rc2, _ = run(S / 'check.py', t, '--client', 'Acme Corp', '--final')
    record('HP1-3', rc1 == 0 and rc2 == 1, f'check exit {rc1} (want 0); --final exit {rc2} (want 1 while placeholders remain)')

    # HP-2: discovery hub, structured fills, then handover
    d = tmp / 'hp2.html'
    run(S / 'build.py', '--preset', 'discovery', '--client', 'Beta Bank', '--out', d)
    (tmp / 'reg.json').write_text(json.dumps({'type': 'register', 'key': 'register-items-list', 'items': [
        {'id': 'H001', 'kind': 'hypothesis', 'title': 'Central identity', 'statement': 'One identity provider.',
         'priority': 'High', 'status': 'Open', 'area': 'Identity', 'evidence': 'Session 1', 'next': 'Test it'}]}), encoding='utf-8')
    rc, _ = run(S / 'fill_slot.py', d, '--key', 'register-items-list', '--block', tmp / 'reg.json', '--in-place')
    record('HP2-1', rc == 0 and 'H001' in d.read_text(encoding='utf-8') and slot_states(d).get('register-items-list') is True, f'register fill exit {rc}')
    (tmp / 'est.json').write_text(json.dumps([['Platform A', 'Hosts agents', '400 users', 'Platform team', 'Session 1']]), encoding='utf-8')
    rc, _ = run(S / 'fill_slot.py', d, '--key', 'estate-platforms-table', '--rows', tmp / 'est.json', '--in-place')
    record('HP2-2', rc == 0 and 'Platform A' in d.read_text(encoding='utf-8'), f'table rows fill exit {rc}')
    run(S / 'fill_slot.py', d, '--key', 'overview-cover-stats', '--values', '46,12,3,5', '--in-place')
    for k in empty_keys(d):
        run(S / 'fill_slot.py', d, '--key', k, '--text', 'Content added by the eval.', '--force', '--in-place')
    rc, _ = run(S / 'check.py', d, '--client', 'Beta Bank', '--final')
    record('HP2-3', rc == 0 and not empty_keys(d), f'--final exit {rc} (want 0); empty slots left: {len(empty_keys(d))}')

    # EC-2: bad input fails closed
    e = tmp / 'ec.html'
    run(S / 'build.py', '--preset', 'target-design', '--client', 'Acme Corp', '--out', e)
    snap = e.read_text(encoding='utf-8')
    rc, _ = run(S / 'fill_slot.py', e, '--key', 'no-such-key', '--text', 'x', '--in-place')
    record('EC2-1', rc != 0 and e.read_text(encoding='utf-8') == snap, f'unknown key exit {rc}; file unchanged')
    rc, _ = run(S / 'fill_slot.py', e, '--key', 'architecture-glance-body', '--image', tmp / 'missing.png', '--in-place')
    record('EC2-2', rc != 0 and e.read_text(encoding='utf-8') == snap, f'missing image exit {rc}; file unchanged')

    # SEC-1: structured content is not silently replaced; filled headline numbers count as filled
    g = tmp / 'sec.html'
    run(S / 'build.py', '--preset', 'discovery', '--client', 'Beta Bank', '--out', g)
    run(S / 'fill_slot.py', g, '--key', 'register-items-list', '--block', tmp / 'reg.json', '--in-place')
    rc, out = run(S / 'fill_slot.py', g, '--key', 'register-items-list', '--text', 'oops', '--in-place')
    txt = g.read_text(encoding='utf-8')
    record('SEC1-1', rc != 0 and 'H001' in txt and 'oops' not in txt and 'Nothing was changed' in out, f'--text on register exit {rc}; register kept')
    rc, _ = run(S / 'fill_slot.py', g, '--key', 'estate-platforms-table', '--text', 'oops', '--in-place')
    record('SEC1-2', rc != 0 and '<tbody>' in g.read_text(encoding='utf-8'), f'--text on table slot exit {rc}; table kept')
    rc_a, _ = run(S / 'fill_slot.py', g, '--key', 'register-items-list', '--text', 'After the register.', '--append', '--in-place')
    kept = 'H001' in g.read_text(encoding='utf-8') and 'After the register.' in g.read_text(encoding='utf-8')
    rc_f, _ = run(S / 'fill_slot.py', g, '--key', 'register-items-list', '--text', 'Replaced.', '--force', '--in-place')
    record('SEC1-3', rc_a == 0 and kept and rc_f == 0 and 'Replaced.' in g.read_text(encoding='utf-8'), f'--append exit {rc_a} keeps register; --force exit {rc_f} replaces it')
    run(S / 'fill_slot.py', g, '--key', 'overview-cover-stats', '--values', '1,2,3,4', '--in-place')
    record('SEC1-4', slot_states(g).get('overview-cover-stats') is True, 'filled headline numbers are listed as filled')

    # GR-3: the fixed look and house style are enforced by the scripts
    base = tmp / 'hp2.html'
    css_tamper = tmp / 'tamper.html'
    css_tamper.write_text(base.read_text(encoding='utf-8').replace('</head>', '<style>body{color:red}</style></head>', 1), encoding='utf-8')
    rc, _ = run(S / 'check.py', css_tamper, '--client', 'Beta Bank')
    record('GR3-1', rc == 1, f'added style block: check exit {rc} (want 1)')
    rc, _ = run(S / 'build.py', '--preset', 'target-design', '--client', 'Acme Corp', '--logo', 'x.png', '--out', tmp / 'l.html')
    record('GR3-2', rc != 0, f'--logo option exit {rc} (want nonzero: no client logo option exists)')
    style = tmp / 'style.html'
    run(S / 'build.py', '--preset', 'target-design', '--client', 'Acme Corp', '--out', style)
    run(S / 'fill_slot.py', style, '--key', 'overview-conclusion-text', '--text', 'The programme is organised — Jane Doe agreed.', '--in-place')
    rc, out = run(S / 'check.py', style, '--client', 'Acme Corp', '--internal-names', 'Jane Doe')
    record('GR3-3', rc == 1 and 'Em dash' in out and 'Jane Doe' in out and re.search(r'programme|organised', out), f'em dash, UK spelling and team name flagged; exit {rc}')

    # ART-1: self-contained, repeatable output
    a = tmp / 'a1.html'; b = tmp / 'a2.html'
    for f in (a, b):
        run(S / 'build.py', '--preset', 'target-design', '--client', 'Acme Corp', '--out', f)
    ta = a.read_text(encoding='utf-8')
    ext = re.findall(r'(?:src|href)="https?://', ta)
    record('ART1-1', not ext, f'external src/href references: {len(ext)}')
    sa = re.search(r'ahead-deliverable-hub [^"<]*', ta).group(0)
    sb = re.search(r'ahead-deliverable-hub [^"<]*', b.read_text(encoding='utf-8')).group(0)
    record('ART1-2', sa == sb, f'stamp: {sa}')
    ok = True
    for preset, client in (('discovery', 'Beta Bank'), ('target-design', 'Acme Corp'), ('base', 'Contoso')):
        f = tmp / f'preset-{preset}.html'
        rc1, _ = run(S / 'build.py', '--preset', preset, '--client', client, '--out', f)
        rc2, _ = run(S / 'check.py', f, '--client', client)
        ok = ok and rc1 == 0 and rc2 == 0
    record('ART1-3', ok, 'every preset builds and passes check.py')

    # RES-1: package integrity
    skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    spec = (ROOT / 'SPEC.md').read_text(encoding='utf-8')
    refs = sorted(set(re.findall(r'(?<![A-Za-z0-9_/-])(?:references|assets|scripts|evals)/[A-Za-z0-9_./-]*[A-Za-z0-9_]\.[a-z]+', skill + spec)))
    missing = [r for r in refs if not (ROOT / r).is_file()]
    record('RES1-1', not missing, f'{len(refs)} referenced files checked; missing: {missing}')
    fm = dict(re.findall(r'^([a-z-]+):\s*(.+)$', skill.split('---')[1], re.M))
    need = ['name', 'description', 'version', 'owner', 'team', 'approved-by', 'approved-date', 'ahead-platform', 'sensitivity', 'publication-status']
    gaps = [k for k in need if not fm.get(k, '').strip()]
    record('RES1-2', not gaps, f'frontmatter fields missing: {gaps}')
    spec_v = re.search(r'^- \*\*Version:\*\* ([0-9.]+)', spec, re.M)
    log_v = re.search(r'^- \*\*([0-9.]+)\.?\*\*', (ROOT / 'references' / 'changelog.md').read_text(encoding='utf-8'), re.M)
    same = {fm.get('version'), skill_version, spec_v and spec_v.group(1), log_v and log_v.group(1).rstrip('.')}
    record('RES1-3', len(same) == 1, f'versions (frontmatter, build.py, SPEC, changelog): {sorted(map(str, same))}')
    rc, out = run(S / 'selftest.py')
    record('RES1-4', rc == 0, out.strip().splitlines()[-1].split('. Files')[0])

    failed = [k for k, v in results.items() if not v['passed']]
    print(f'\n{len(results) - len(failed)} of {len(results)} script assertions passed.')
    if '--json' in sys.argv:
        print(json.dumps(results, indent=1))
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
