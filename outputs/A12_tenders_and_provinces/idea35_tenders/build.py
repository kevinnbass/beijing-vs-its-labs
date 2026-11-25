#!/usr/bin/env python3
"""Build idea 35 (a sample of purchase notices): check, count, write the table file and the note.
Round 4: buyers are labelled only by what their names say (no "public" or "state"); later records of agent L17 are
quoted in the template; L17's count of Wuhan University notices is recounted here from L17's own tables.

Run: python3 -I build.py          (from anywhere; everything is written beside this file)
Reads   notices.txt         one line per notice (see its header)
        note_template.txt   the note's text with {{PLACEHOLDERS}}
        refs_manual.tsv     references that are not notices (held sources, the Jilin page, the trade-press page)
Writes  quotes.tsv          every string taken from a page (saved id, tab, exact words)
        notices.tsv         the table as a data file: date, buyer, kind of body, kind of notice, class, hardware words,
                            amount, address, saved id
        counts.tsv          notices by year and class, counted here
        extra_refs.tsv      references for scripts/cn_doc_build.py
        tenders_note_base.txt, then tenders_note.md and tenders_note.html through scripts/cn_doc_build.py
Stops before writing the note if scripts/cn_has.py does not find every string in its saved copy.
"""
import json, subprocess, sys
from collections import Counter, OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path('.')
PRIMARY = ROOT / 'research' / 'primary'
CLASSES = OrderedDict([('N', 'names Nvidia hardware'), ('H', 'names home-made accelerator hardware'), ('S', 'names no accelerator by maker or model')])


def load():
    rows = []
    for k, ln in enumerate((HERE / 'notices.txt').read_text(encoding='utf-8').splitlines(), 1):
        if not ln.strip() or ln.startswith('#'): continue
        f = [x.strip() for x in ln.split(' @@ ')]
        if len(f) != 13: sys.exit(f'notices.txt line {k}: {len(f)} fields, 13 wanted')
        r = dict(zip(('id', 'year', 'date_q', 'date_en', 'buyer', 'body', 'kind', 'cls', 'hw', 'hw_note', 'amt_q', 'amt_en', 'remark'), f))
        if r['cls'] not in CLASSES: sys.exit(f'line {k}: class {r["cls"]}')
        if r['year'] not in ('2024', '2025', '2026'): sys.exit(f'line {k}: year {r["year"]}')
        r['hw'] = [h.strip() for h in r['hw'].split(';;')]
        m = PRIMARY / r['id'] / 'meta.json'
        if not m.exists(): sys.exit(f'line {k}: no saved copy {r["id"]}')
        meta = json.loads(m.read_text())
        if meta.get('status') != 200: sys.exit(f'line {k}: {r["id"]} was not saved with status 200')
        r['url'] = meta['url']
        rows.append(r)
    ids = [r['id'] for r in rows]
    if len(ids) != len(set(ids)): sys.exit('an id stands twice in notices.txt')
    return rows


def main():
    rows = load()
    # 1. every string taken from a page, checked against its saved copy
    q = ['# saved id <TAB> exact words. Written by build.py from notices.txt; checked by scripts/cn_has.py.']
    for r in rows:
        for s in [r['date_q']] + r['hw'] + [r['amt_q']]:
            if s != '-': q.append(f'{r["id"]}\t{s}')
    (HERE / 'quotes.tsv').write_text('\n'.join(q) + '\n', encoding='utf-8')
    p = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts/cn_has.py'), str(HERE / 'quotes.tsv')], capture_output=True, text=True)
    print(p.stdout.strip())
    if p.returncode != 0: sys.exit('STOPPED: a string was not found in its saved copy; nothing else written')
    has_line = p.stdout.strip().splitlines()[-1]

    # 2. the table as a data file
    out = ['date_on_page\tyear\tbuyer\tkind_of_body\tkind_of_notice\tclass\thardware_words\tour_note\tamount\taddress\tsaved_id']
    for r in rows:
        out.append('\t'.join([r['date_en'], r['year'], r['buyer'], r['body'], r['kind'], r['cls'], ' / '.join(r['hw']), r['hw_note'], r['amt_en'], r['url'], r['id']]))
    (HERE / 'notices.tsv').write_text('\n'.join(out) + '\n', encoding='utf-8')

    # 3. counts
    c = Counter((r['year'], r['cls']) for r in rows)
    years = ['2024', '2025', '2026']
    lines = ['year\t' + '\t'.join(CLASSES) + '\tall']
    for y in years: lines.append(y + '\t' + '\t'.join(str(c[(y, k)]) for k in CLASSES) + '\t' + str(sum(c[(y, k)] for k in CLASSES)))
    tot = {k: sum(c[(y, k)] for y in years) for k in CLASSES}
    lines.append('all\t' + '\t'.join(str(tot[k]) for k in CLASSES) + '\t' + str(len(rows)))
    (HERE / 'counts.tsv').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))

    # 2b. account for every page tried for this idea (from ../sources.tsv)
    tried, saved, failed = [], [], []
    for ln in (HERE.parent / 'sources.tsv').read_text(encoding='utf-8').splitlines():
        if not ln.startswith('cn-o35-'): continue
        sid = ln.split('\t')[0]; tried.append(sid)
        try: st = json.loads((PRIMARY / sid / 'meta.json').read_text()).get('status')
        except Exception: st = None
        (saved if st == 200 else failed).append((sid, st))
    left = OrderedDict()
    for ln in (HERE / 'left_out.txt').read_text(encoding='utf-8').splitlines():
        if not ln.strip() or ln.startswith('#'): continue
        sid, cat, why = [x.strip() for x in ln.split(' @@ ')]
        left[sid] = (cat, why)
    in_table = {r['id'] for r in rows}; saved_ids = {s for s, _ in saved}
    if in_table & set(left): sys.exit('a page is both in the tables and in left_out.txt')
    if in_table | set(left) != saved_ids: sys.exit(f'tables + left_out.txt do not equal the pages saved: {sorted((in_table | set(left)) ^ saved_ids)}')
    cats = Counter(c for c, _ in left.values())
    # the H20 by name: none of the saved pages of this idea, and the control page has it
    import html as _h, re as _re
    def _text(sid):
        d = PRIMARY / sid; t = (d / 'text.txt').read_text(encoding='utf-8', errors='replace') if (d / 'text.txt').exists() else ''
        for b in d.glob('body*'):
            if b.suffix == '.html':
                raw = _re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', b.read_text(encoding='utf-8', errors='replace'))
                t += ' ' + _h.unescape(_re.sub(r'(?s)<[^>]+>', ' ', raw))
        return t
    h20 = _re.compile(r'(?<![A-Za-z0-9])H20(?![0-9])')
    with_h20 = [s for s, _ in saved if h20.search(_text(s))]
    if with_h20 or not h20.search(_text('cn-tolerate-bit')): sys.exit(f'H20 scan: {with_h20} / control {bool(h20.search(_text("cn-tolerate-bit")))}')
    print(f'H20 by name: 0 of {len(saved)} saved pages of this idea; found in the control page cn-tolerate-bit')
    def n(pred): return sum(1 for r in rows if pred(r))
    N = [r for r in rows if r['cls'] == 'N']; H = [r for r in rows if r['cls'] == 'H']; S = [r for r in rows if r['cls'] == 'S']
    central = [r for r in rows if r['id'].startswith('cn-o35-ccgp-')]
    award = lambda r: r['kind'].startswith(('award', 'result'))
    fill = {
        'N_ALL': len(rows), 'N_N': len(N), 'N_H': len(H), 'N_S': len(S), 'N_NH': len(N) + len(H),
        'N_WHU_N': n(lambda r: r['cls'] == 'N' and r['buyer'].startswith('Wuhan University')),
        'N_BUYERS': len({r['buyer'].split(',')[0] for r in rows}),
        'N_BUYERS_N': len({r['buyer'].split(',')[0] for r in N}),
        'N_CENTRAL': len(central), 'N_CENTRAL_AWARD': n(lambda r: r in central and award(r)),
        'N_AWARD': n(award), 'N_OTHERKIND': n(lambda r: not award(r)),
        'N_CENTRAL_AWARD_S': n(lambda r: r in central and award(r) and r['cls'] == 'S'),
        'N_CENTRAL_AWARD_H': n(lambda r: r in central and award(r) and r['cls'] == 'H'),
        'N_CENTRAL_AWARD_N': n(lambda r: r in central and award(r) and r['cls'] == 'N'),
        'N_UNIV': n(lambda r: 'university' in r['body'] or 'college' in r['body']),
        'N_INST': n(lambda r: 'institute' in r['body']), 'N_GOV': n(lambda r: 'agency' in r['body']),
        'HAS_LINE': has_line,
        'N_TRIED': len(tried), 'N_SAVED': len(saved), 'N_FAILED': len(failed), 'N_LEFT': len(left), 'N_SEARCHES': sum(1 for l in (HERE / 'search_log.txt').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')),
        'L_NOTAI': cats['not-ai'], 'L_BEFORE': cats['before-2024'], 'L_NOACC': cats['no-accelerator'], 'L_NOCONTENT': cats['no-content'], 'L_ELSE': cats['used-elsewhere'],
        'N_404': sum(1 for _, s in failed if s == 404), 'N_NOCONN': sum(1 for _, s in failed if s != 404),
    }
    if fill['N_UNIV'] + fill['N_INST'] + fill['N_GOV'] != len(rows): sys.exit('kinds of body do not add up')
    import re as _re2
    sl = [l.split(' @@ ')[2] for l in (HERE / 'search_log.txt').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    nv_rx = _re2.compile(r'英伟达|NVIDIA|H100|H200|H20|A100|A800|L40S|4090|5090', _re2.I)
    fill['N_S_NV'] = sum(1 for x in sl if nv_rx.search(x)); fill['N_S_HM'] = len(sl) - fill['N_S_NV']
    if any(nv_rx.search(x) and _re2.search(r'昇腾|寒武纪|海光|Atlas|国产', x) for x in sl): sys.exit('a search names both kinds: count it by hand')
    # L17's count of Wuhan University result notices (Sept 1, 2025 to Nov 23, 2026), recounted from L17's own tables by
    # L17's rule (an Nvidia brand word in the notice's hardware words); each counted notice's saved page must hold the word too
    L17 = ROOT / 'research/cn_chip_policy_20261120/loose_ends/L17_tenders'
    sys.path.insert(0, str(ROOT / 'scripts')); import cn_srclib as L
    wr = []
    for f in ('whu_notices.tsv', 'whu_notices_early.tsv'):
        wr += [l.rstrip('\n').split('\t') for l in (L17 / f).read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    win = [r for r in wr if '2025-09-01' <= r[1] <= '2026-11-23']
    brand = _re2.compile(r'NVIDIA|Nvidia|nvidia|NVDIA|NVidia|英伟达')
    nvw = [r for r in win if brand.search(r[4])]
    bad = [r[0] for r in nvw if not _re2.search(r'nvidia|nvdia|英伟达', L.page(r[0]))]
    if bad: sys.exit(f'WHU recount: no Nvidia word in the saved page of {bad}')
    if (len(win), len(nvw)) != (72, 23): sys.exit(f'WHU recount: {len(win)} and {len(nvw)}, not 72 and 23 as L17 wrote: read and change the note')
    print(f'WHU recount (L17 tables): {len(win)} result notices dated 2025-09-01 to 2026-11-23; {len(nvw)} name Nvidia in the notice; each of the {len(nvw)} saved pages holds the word')
    fill['N_WHU_L17'] = len(win); fill['N_WHU_L17_NV'] = len(nvw)
    # round 5: the core's table of purchase records, counted here (each row must have the header's number of cells)
    pr = [l.rstrip('\n').split('\t') for l in (ROOT / 'research/cn_chip_policy_20261120/tables/procurement_records.tsv').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    if any(len(x) != len(pr[0]) for x in pr[1:]): sys.exit('procurement_records.tsv: a row without the header\'s number of cells')
    fill['N_PROC'] = len(pr) - 1
    if fill['N_PROC'] != 51: sys.exit(f'procurement_records.tsv now has {fill["N_PROC"]} rows, not 51: read the new rows and change the later records')
    print(f'core table of purchase records: {fill["N_PROC"]} rows')
    for y in years:
        for k in CLASSES: fill[f'C_{y}_{k}'] = c[(y, k)]
        fill[f'C_{y}_ALL'] = sum(c[(y, k)] for k in CLASSES)

    def cap(s): return s[:1].upper() + s[1:]

    def checks(r):
        o = []
        if not r['date_q'].startswith(('SUSTech', '（2025）')): o.append(f'!! {r["id"]} | {r["date_q"]}')
        if r['amt_q'] != '-': o.append(f'!! {r["id"]} | {r["amt_q"]}')
        return o

    def table(rs):
        o = ['| Date on the page; buyer; kind of notice | Hardware, in the notice\'s own words | What it is; amount; source |']
        for r in rs:
            hw = '; '.join(f'"{h}"' for h in r['hw'])
            amt = '' if r['amt_en'] == '-' else ' ' + cap(r['amt_en']) + '.'
            rem = '' if r['remark'] == '-' else ' ' + cap(r['remark']) + '.'
            o.append(f'| {cap(r["date_en"])}. {r["buyer"]} ({r["body"]}). {cap(r["kind"])} | {hw} | {cap(r["hw_note"])}.{amt}{rem} [{r["id"]}] |')
            o.extend(checks(r))
        return '\n'.join(o)

    fill['TABLE_N'] = table(N)
    fill['TABLE_H'] = table(H)
    fill['TABLE_S'] = table(S)
    # each cell carries its own label: at phone width the page hides the header row and stacks the cells
    ct = ['| Year | Names Nvidia hardware | Names home-made accelerator hardware | Names no accelerator | All |']
    for y in years: ct.append(f'| {y} | Nvidia: {c[(y, "N")]} | Home-made: {c[(y, "H")]} | No accelerator: {c[(y, "S")]} | All: {fill[f"C_{y}_ALL"]} |')
    ct.append(f'| All three years | Nvidia: {len(N)} | Home-made: {len(H)} | No accelerator: {len(S)} | All: {len(rows)} |')
    fill['TABLE_COUNT'] = '\n'.join(ct)

    t = (HERE / 'note_template.txt').read_text(encoding='utf-8')
    for k, v in fill.items(): t = t.replace('{{' + k + '}}', str(v))
    if '{{' in t: sys.exit('note_template.txt: a placeholder was not filled: ' + t[t.index('{{'):t.index('{{') + 40])
    (HERE / 'tenders_note_base.txt').write_text(t, encoding='utf-8')

    # 4. references: one line per notice, plus the hand-written ones
    refs = ['# id <TAB> kind <TAB> label <TAB> address (empty = the address in the saved copy\'s record). Written by build.py.']
    for r in rows:
        refs.append(f'{r["id"]}\tNOTICE\t{r["buyer"]}: {r["kind"]}, {r["date_en"]}. A purchase notice on the buyer\'s own site or on a government purchasing site\t')
    refs += [ln for ln in (HERE / 'refs_manual.tsv').read_text(encoding='utf-8').splitlines() if ln.strip() and not ln.startswith('#')]
    (HERE / 'extra_refs.tsv').write_text('\n'.join(refs) + '\n', encoding='utf-8')

    p = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts/cn_doc_build.py'), str(HERE / 'tenders_note_base.txt'), '--refs', str(HERE / 'extra_refs.tsv'),
                        '--title', 'Purchase Notices Sample', '--eyebrow', 'China chip policy: idea 35, purchase notices'], capture_output=True, text=True)
    print(p.stdout.strip()); print(p.stderr.strip())
    sys.exit(p.returncode)


if __name__ == '__main__':
    main()
