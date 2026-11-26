#!/usr/bin/env python3
"""Build idea 39 (provincial targets for home-made computing hardware, and local vouchers): check, count, write the
table files and the note. Round 4 (Nov 23, 2026): all 31 governments, six groups, the local vouchers.

Run: python3 -I build.py          (from anywhere; everything is written beside this file)
Reads   provinces.txt       one line per document read (see its header; made by round4/make_rows.py)
        vouchers.txt        one line per local voucher rule that favours home-made computing (see its header; since round 9)
        ../../../tables/local_vouchers_classes.tsv, local_vouchers.tsv, local_vouchers_more.tsv   the core's voucher tables, through
                            scripts/cn_voucher_classes.py (imported; its compute() must equal the published table of classes)
        ../../../tables/provincial_ict_plans.tsv   the core's class search of the plans of the kind that holds Zhejiang's share
        absent.txt          words that must not stand in a page, each with a control word that must
        note_template.txt   the note's text with {{PLACEHOLDERS}}
        ../../../tables/provinces_31.tsv   the core's table of the 31 governments: the groups here must agree with it
        ../archive/         the two Internet Archive captures as first kept (build.py checks the saved bytes are the same)
        ../sources.tsv      every address tried for saving in round 1
Writes  quotes.tsv            every string taken from a saved page (saved id, tab, exact words); checked by scripts/cn_has.py
        archive_strings.tsv   strings from captures kept only in ../archive/ (none since round 2)
        near_percent.txt      for each document that sets no share: every place where a home-made word stands within
                              60 characters of a percent sign (each read by a person)
        provinces.tsv, vouchers.tsv, counts.tsv, extra_refs.tsv
        provinces_note_base.txt, then provinces_note.md and provinces_note.html through scripts/cn_doc_build.py
Stops before writing the note if any string is not found where it should be, a control fails, a count changes from
what the note's words assume, or the groups disagree with the core's table.
Three hand-saved PDFs have damaged text layers (DAMAGED): a string checked in one of them must stand in its
transcription.txt (a reading of the page images), not only in the text layer.
"""
import html, json, re, subprocess, sys
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path('.')
PROJ = ROOT / 'research' / 'cn_chip_policy_20261120'
PRIMARY = ROOT / 'research' / 'primary'
ARCH = HERE.parent / 'archive'
sys.path.insert(0, str(ROOT / 'scripts'))
import cn_srclib as L   # noqa: E402  (the project's own normaliser: squash(), page(), has())

ALL_UNITS = ['Beijing', 'Tianjin', 'Hebei', 'Shanxi', 'Inner Mongolia', 'Liaoning', 'Jilin', 'Heilongjiang', 'Shanghai', 'Jiangsu', 'Zhejiang', 'Anhui',
             'Fujian', 'Jiangxi', 'Shandong', 'Henan', 'Hubei', 'Hunan', 'Guangdong', 'Guangxi', 'Hainan', 'Chongqing', 'Sichuan', 'Guizhou', 'Yunnan',
             'Tibet', 'Shaanxi', 'Gansu', 'Qinghai', 'Ningxia', 'Xinjiang']
GROUPS = ('share', 'none', 'account', 'notfound', 'other', 'also')
CORE_RESULT = {'share': 'share', 'plan_no_share': 'none', 'account_only': 'account', 'not_reached': 'notfound'}
EXPECT = {'share': 9, 'none': 20, 'account': 1, 'notfound': 1}          # the note's words assume these (8 and 21 until core edit 8, Nov 25, 2026: Zhejiang's sector plan)
EXTRA_QUOTES = [('cn-o39-hebei-opinion-2024-sjz', '新增算力基础软硬件设施自主可控比例60%以上'),
                ('cn-o39-hebei-opinion-2024-sjz', '河北省人民政府办公厅 2024年5月8日')]
BASIS = {'official': 'Saved official page', 'hand': 'Saved by hand from an official page', 'capture': 'Saved Archive capture',
         'copy': 'Saved copy on another site', 'archive': 'Read, not saved', 'news': "A newspaper's account"}
RANK = ['official', 'hand', 'capture', 'copy', 'archive', 'news']
KEPT = {'cn-o39-nmg-plan-pdf-wayback': 'o39-nmg-plan-pdf', 'cn-o39-henan-plan-2024-wayback': 'o39-henan-plan-2024'}   # saved id -> my kept capture in ../archive/
DAMAGED = {'man-cn-o39-qinghai-compute-15fyp-2026', 'man-cn-o39-qinghai-green-compute-2024', 'man-cn-o39-hunan-green-compute-plan-2025'}
N_NEAR_READ = 11      # places in near_percent.txt read by a person in round 4 (12:40 UTC); none sets a share of home-made hardware
WORDS = ['none', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen']
VSHORT = {'Hangzhou city': 'Hangzhou', 'Zhejiang province': 'Zhejiang', 'Wenzhou city': 'Wenzhou', 'Binjiang district of Hangzhou': 'Binjiang',
          'Beijing E-Town (a development zone, not the city)': 'E-Town', 'Longhua district of Shenzhen': 'Longhua', 'Shanxi province': 'Shanxi',
          'Shenzhen city': 'Shenzhen', 'Wuhan city': 'Wuhan', 'Qingdao city': 'Qingdao', 'Shanghai city': 'Shanghai', 'Qiaokou district of Wuhan': 'Qiaokou',
          'Hongshan district of Wuhan': 'Hongshan', 'Shandong province': 'Shandong', 'Hunan province': 'Hunan', 'Sichuan province': 'Sichuan',
          'Wuhu city': 'Wuhu', 'Suzhou city': 'Suzhou', 'Tianjin city': 'Tianjin',   # round 5: names in vcount_as_stands.py's output
          'Xiamen city': 'Xiamen', 'Xinjiang Uygur Autonomous Region': 'Xinjiang',   # core edit 8: names in tables/local_vouchers_classes.tsv
          'Chengdu city': 'Chengdu', 'Hubei province': 'Hubei', 'Longwan district and Wenzhou Bay New Area (Wenzhou)': 'Longwan and Wenzhou Bay New Area',
          'Ningbo city': 'Ningbo', 'Huangyan district (Taizhou)': 'Huangyan',
          'Changsha Economic and Technological Development Zone': 'Changsha Economic and Technological Development Zone'}   # round 9: the 7 and the 4
VHOME = re.compile(r'国产|自主|信创')      # round 9: the classifier's home-made words (cn_voucher_classes.py), for a voucher row that pays for home-made computing only
HOME = re.compile(r'国产|自主可控|安全可控|安全可靠|自主化')
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
CITE = re.compile(r'\[((?:cn|ms|man)-[A-Za-z0-9-]+)\]')
# labels for ids cited only in remarks, notes or checks, when the core's reference lists do not hold them
MORE_LABELS = {
    'cn-o39-hebei-opinion-2024-xiongan': ("DOC", "Hebei. Opinions on the layout of computing and the AI industry, General Office of the Hebei Provincial People's Government, May 8, 2024: a copy on the Xiong'an New Area's site"),
    'cn-o39-hebei-opinion-2024-sjz': ("DOC", "Hebei. The same opinions: a copy on a city data bureau's site"),
    'man-cn-o39-qinghai-compute-15fyp-2026': ("DOC", "Qinghai. Plan for the green computing industry in the 15th five-year period, Qinghai Provincial People's Government, Aug 25, 2026: a PDF of the government's page saved by hand. Its text layer is damaged; read only from the page images, through a transcription kept with the saved copy"),
    'cn-ga04-sz-suzhou-aiplus-2026-jiedu': ("DOC", "Suzhou city. The city government's reading of its measures for an AI+ city, 2026 edition"),
    'cn-ga04-sz-suzhou-aiplus-2025-5hao': ("DOC", "Suzhou city. Measures for building its pilot zone for AI+ innovation and development at a high level, 苏府规字〔2025〕5号, Feb 13, 2025"),
    'cn-factions-etwon-vouchers': ("DOC", "Beijing E-Town (a development zone, not the city). Policies to build an AI-native industry, 京技管发〔2024〕10号, Mar 28, 2024; repealed by 京技管发〔2024〕29号 of Nov 26, 2024"),
    'cn-cnpress-binjiang-rental-reply-20260720': ("DOC", "Binjiang district of Hangzhou (Hangzhou High-tech Zone): a district bureau's reply, published Jul 20, 2026, describing its rule of May 2025"),
    'cn-policy-computing-network-1779': ("DOC", "National. Opinions on the national integrated computing network, December 2023"),
    # core edit 8
    'cn-ga31-cndocs-1': ("DOC", "Xinjiang Uygur Autonomous Region. Measures to speed the high-quality development of profit-oriented services, 2026 to 2028, General Office of the regional government, 新政办发〔2026〕22号: the copy in the government's gazette list"),
    'cn-ga31-unsaved-sc-338hao-fgw-wayback': ("DOC", "Sichuan province. Notice issuing the measures for building the computing network (trial), 川发改数据〔2026〕338号, written Aug 11 and published Aug 13, 2026: the provincial development and reform commission's own page, as the Internet Archive captured it"),
}


def page_text(sid, single=False):
    """Every saved form of a page as one string (single=True: one form only, the HTML body or else text.txt, for counting)."""
    d = PRIMARY / sid; txt = (d / 'text.txt').read_text(encoding='utf-8', errors='replace') if (d / 'text.txt').exists() else ''
    bodies = ''
    for b in d.glob('body*'):
        if b.suffix.lower() in ('.html', '.htm'):
            raw = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', b.read_text(encoding='utf-8', errors='replace'))
            bodies += ' ' + html.unescape(re.sub(r'(?s)<[^>]+>', ' ', raw))
    t = (bodies or txt) if single else txt + ' ' + bodies
    return re.sub(r'\s+', '', t)


def transcription(sid):
    f = PRIMARY / sid / 'transcription.txt'
    return L.squash(f.read_text(encoding='utf-8')) if f.exists() else ''


def split_checks(field, own):
    """';;'-separated strings; an item '[other-id] words' is checked in that other saved copy."""
    out = []
    for c in ([] if field == '-' else [w.strip() for w in field.split(';;')]):
        m = re.match(r'^\[((?:cn|ms|man)-[A-Za-z0-9-]+)\]\s+(.+)$', c)
        out.append((m.group(1), m.group(2)) if m else (own, c))
    return out


def cap_date(ts):
    return f'{MONTHS[int(ts[4:6]) - 1]} {int(ts[6:8])}, {ts[:4]}'


def load():
    rows = []
    for k, ln in enumerate((HERE / 'provinces.txt').read_text(encoding='utf-8').splitlines(), 1):
        if not ln.strip() or ln.startswith('#'): continue
        if '"' in ln: sys.exit(f'provinces.txt line {k}: a straight double quote')
        f = [x.strip() for x in ln.split(' @@ ')]
        if len(f) != 11: sys.exit(f'provinces.txt line {k}: {len(f)} fields, 11 wanted')
        r = dict(zip(('unit', 'group', 'doc', 'src', 'words', 'en', 'remark', 'checks', 'basis', 'where', 'label'), f))
        if r['unit'] not in ALL_UNITS: sys.exit(f'line {k}: unit {r["unit"]}')
        if r['group'] not in GROUPS: sys.exit(f'line {k}: group {r["group"]}')
        if (r['label'] != '-') != (r['group'] == 'share'): sys.exit(f'line {k}: a label is wanted for rows of the share group and for no other row')
        if r['basis'] not in BASIS: sys.exit(f'line {k}: basis {r["basis"]}')
        r['words'] = [] if r['words'] == '-' else [w.strip() for w in r['words'].split(';;')]
        r['checks'] = split_checks(r['checks'], r['src'])
        r['arch'] = r['src'].startswith('archive:')
        if (r['basis'] == 'archive') != r['arch']: sys.exit(f'line {k}: basis and source disagree on the Archive')
        if r['src'] in DAMAGED and r['words']: sys.exit(f'line {k}: words quoted from a damaged PDF {r["src"]}: quote the capture or the transcription, not the text layer')
        if r['arch']:
            r['key'] = r['src'].split(':', 1)[1]; m = json.loads((ARCH / f'{r["key"]}.meta.json').read_text())
            if m.get('exit') != 0: sys.exit(f'line {k}: the capture was not fetched cleanly')
            r['url'] = m['url']; r['capture'] = m['capture']; r['sha'] = m['sha256']; r['cap_date'] = cap_date(m['capture_timestamp'])
            r['host'] = re.sub(r'^https?://([^/]+)/.*$', r'\1', m['url'])
        else:
            m = PRIMARY / r['src'] / 'meta.json'
            if not m.exists(): sys.exit(f'line {k}: no saved copy {r["src"]}')
            meta = json.loads(m.read_text())
            ok = meta.get('status') == 200 or (r['basis'] == 'hand' and meta.get('status') == 'hand-saved' and r['src'].startswith('man-'))
            if not ok: sys.exit(f'line {k}: {r["src"]} was not saved with status 200 (or by hand, for basis hand)')
            if (r['basis'] == 'hand') != r['src'].startswith('man-'): sys.exit(f'line {k}: basis hand and the id do not agree')
            r['url'] = meta['url']
            if (r['basis'] == 'capture') != r['src'].endswith('-wayback'): sys.exit(f'line {k}: basis capture and the id do not agree')
            if r['basis'] == 'capture':
                ts = str(meta.get('capture_timestamp') or '')
                if len(ts) < 8 or 'web.archive.org' not in str(meta.get('route')): sys.exit(f'line {k}: no capture record')
                if '{CAP}' not in r['where']: sys.exit(f'line {k}: no {{CAP}} in the where field')
                r['cap_date'] = cap_date(ts); r['where'] = r['where'].replace('{CAP}', r['cap_date'])
                if r['src'] in KEPT:
                    kept = ARCH / f'{KEPT[r["src"]]}.meta.json'
                    if json.loads(kept.read_text())['sha256'] != meta.get('sha256'): sys.exit(f'line {k}: the saved capture is not the bytes kept in ../archive/')
        rows.append(r)
    return rows


def load_vouchers():
    out = []
    for k, ln in enumerate((HERE / 'vouchers.txt').read_text(encoding='utf-8').splitlines(), 1):
        if not ln.strip() or ln.startswith('#'): continue
        if '"' in ln: sys.exit(f'vouchers.txt line {k}: a straight double quote')
        f = [x.strip() for x in ln.split(' @@ ')]
        if len(f) != 13: sys.exit(f'vouchers.txt line {k}: {len(f)} fields, 13 wanted')      # 11 until round 9; the two rates in words added
        v = dict(zip(('place', 'level', 'date', 'home', 'other', 'home_en', 'other_en', 'src', 'words', 'checks', 'basis', 'where', 'note'), f))
        v['home'], v['other'] = int(v['home']), int(v['other'])
        if v['basis'] not in ('official', 'copy', 'capture'): sys.exit(f'vouchers.txt line {k}: basis {v["basis"]}')      # core edit 8: capture = an Internet Archive capture of the official file (Xiamen)
        meta = json.loads((PRIMARY / v['src'] / 'meta.json').read_text())
        if meta.get('status') != 200: sys.exit(f'vouchers.txt line {k}: {v["src"]} not saved with status 200')
        v['words'] = [w.strip() for w in v['words'].split(';;')]
        v['checks'] = split_checks(v['checks'], v['src'])
        # each rate stands in the rate words (spaces inside a number and its sign ignored: "25 ％"); a rule that pays for
        # home-made computing only (other 0, round 5) must name home-made computing in its rate words instead
        ws = [w.replace(' ', '') for w in v['words']]
        if not any(f'{v["home"]}%' in w or f'{v["home"]}％' in w for w in ws): sys.exit(f'vouchers.txt line {k}: {v["home"]}% is not in the rate words')
        if v['other'] == 0:
            if not any(VHOME.search(w) for w in ws): sys.exit(f'vouchers.txt line {k}: other 0, and the rate words do not name home-made computing')
        elif not any(f'{v["other"]}%' in w or f'{v["other"]}％' in w for w in ws): sys.exit(f'vouchers.txt line {k}: {v["other"]}% is not in the rate words')
        out.append(v)
    return out


def main():
    rows = load()
    docs = [r for r in rows if not r['arch']]
    vouchers = load_vouchers()

    # 0. the groups agree with the core's table of the 31 governments
    core = {}
    lines = [l for l in (PROJ / 'tables' / 'provinces_31.tsv').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    head = lines[0].split('\t')
    for l in lines[1:]:
        c = dict(zip(head, l.split('\t'))); core[c['government']] = c
    if set(core) != set(ALL_UNITS): sys.exit(f'provinces_31.tsv: not the 31 governments: {sorted(set(core) ^ set(ALL_UNITS))}')
    unit_group = {}
    for u in ALL_UNITS:
        gs = {r['group'] for r in rows if r['unit'] == u}
        g = next((x for x in ('share', 'none', 'account', 'notfound') if x in gs), None)
        if g is None: sys.exit(f'{u}: no row of the groups share, none, account or notfound')
        if g != CORE_RESULT[core[u]['result']]: sys.exit(f'{u}: group {g} here, {core[u]["result"]} in tables/provinces_31.tsv')
        unit_group[u] = g
    by = {g: [u for u in ALL_UNITS if unit_group[u] == g] for g in EXPECT}
    for g, n in EXPECT.items():
        if len(by[g]) != n: sys.exit(f'{g}: {len(by[g])} governments, the note assumes {n}: change the note')
    print('groups agree with tables/provinces_31.tsv: ' + '; '.join(f'{g} {len(v)}' for g, v in by.items()))

    # 1. strings from saved pages, through the project's checker; strings in a damaged PDF must stand in its transcription
    q = ['# saved id <TAB> exact words. Written by build.py from provinces.txt and vouchers.txt; checked by scripts/cn_has.py.']
    pairs = []
    for r in docs:
        pairs += [(r['src'], s) for s in r['words']] + r['checks']
    for v in vouchers:
        pairs += [(v['src'], s) for s in v['words']] + v['checks']
    pairs += EXTRA_QUOTES
    nd = 0
    for sid, s in pairs:
        if sid in DAMAGED:
            nd += 1
            if L.squash(s) not in transcription(sid): sys.exit(f'STOPPED: not in the transcription of the damaged PDF {sid}: {s}')
    for sid in DAMAGED:
        if L.squash('国产算力芯片使用占比达到100%') in transcription(sid): sys.exit('STOPPED: the planted false string was found in a transcription')
    q += [f'{a}\t{b}' for a, b in pairs]
    (HERE / 'quotes.tsv').write_text('\n'.join(q) + '\n', encoding='utf-8')
    p = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts/cn_has.py'), str(HERE / 'quotes.tsv')], capture_output=True, text=True)
    print(p.stdout.strip())
    if p.returncode != 0: sys.exit('STOPPED: a string was not found in its saved copy')
    has_line = p.stdout.strip().splitlines()[-1]
    dam_line = f'{nd} strings checked in damaged PDFs, each found in the reading of the page images (transcription.txt); a planted false string was not'
    print(dam_line)

    # 2. strings from captures kept only in ../archive/ (none since round 2)
    a = ['# archive key <TAB> exact words. Written by build.py; checked against ../archive/<key>.txt. Since round 2 no row rests on an unsaved capture.']
    for r in rows:
        if not r['arch']: continue
        body = L.squash((ARCH / f'{r["key"]}.txt').read_text(encoding='utf-8'))
        for s in r['words'] + [c for _, c in r['checks']]:
            a.append(f'{r["key"]}\t{s}')
            if L.squash(s) not in body: sys.exit(f'STOPPED: not found in the Archive capture {r["key"]}: {s}')
    (HERE / 'archive_strings.tsv').write_text('\n'.join(a) + '\n', encoding='utf-8')

    # 3. absent words, each with a control
    absent = OrderedDict()
    for ln in (HERE / 'absent.txt').read_text(encoding='utf-8').splitlines():
        if not ln.strip() or ln.startswith('#'): continue
        sid, words, ctl = [x.strip() for x in ln.split(' @@ ')]
        t = page_text(sid); words = [w.strip() for w in words.split(';;')]
        for w in words:
            if t.count(w): sys.exit(f'STOPPED: {w} stands in {sid} ({t.count(w)} places)')
        if not t.count(ctl): sys.exit(f'STOPPED: the control word {ctl} is not in {sid}')
        absent[sid] = (words, ctl, t.count(ctl))
        print(f'absent in {sid}: {", ".join(words)} (0 places each); control {ctl} found {t.count(ctl)} times')

    # 4. documents that set no share: list every home-made word that stands near a percent sign, for a person to read
    near = ['# For each document that sets no share (groups none, also, account, notfound): every place where 国产, 自主可控, 安全可控,',
            '# 安全可靠 or 自主化 stands within 60 characters of a percent sign. Written by build.py. Each place was read by a person;',
            '# none sets a share of home-made hardware (round 4 reading, after the list: see the end of this file).']
    n_near = 0
    for r in docs:
        if r['group'] not in ('none', 'also', 'account', 'notfound'): continue
        t = page_text(r['src'], single=True)
        hits = []
        for m in HOME.finditer(t):
            seg = t[max(0, m.start() - 60):m.end() + 60]
            if '%' in seg or '％' in seg: hits.append(seg)
        near.append(f'\n== {r["unit"]} | {r["src"]} | home-made words: {len(HOME.findall(t))}; percent signs: {t.count("%") + t.count("％")}; near each other: {len(hits)}')
        near += ['   …' + h + '…' for h in hits]; n_near += len(hits)
    reading = (HERE / 'near_percent_reading.txt')
    if reading.exists(): near += ['', '# ---- the reading ----'] + reading.read_text(encoding='utf-8').splitlines()
    (HERE / 'near_percent.txt').write_text('\n'.join(near) + '\n', encoding='utf-8')
    if n_near != N_NEAR_READ: sys.exit(f'near_percent.txt now holds {n_near} places, not the {N_NEAR_READ} that were read: read them and change the note')

    # 5. counts by group, and kinds of document for the governments without a share (from the core's table)
    kinds = {}
    for u in by['none']: kinds.setdefault(core[u]['kind_of_document'], []).append(u)
    n_comp = len(kinds.get('computing', []))
    (HERE / 'counts.tsv').write_text('group\tgovernments\tnames\n' + '\n'.join(f'{g}\t{len(by[g])}\t{", ".join(by[g])}' for g in EXPECT) + '\nall\t31\t\n'
                                     + '\n'.join(f'none, document read: {k}\t{len(v)}\t{", ".join(v)}' for k, v in sorted(kinds.items())) + '\n', encoding='utf-8')
    for g in EXPECT: print(f'{g}: {len(by[g])}: {", ".join(by[g])}')
    print('no share, by the kind of document read (core table): ' + '; '.join(f'{k} {len(v)}' for k, v in sorted(kinds.items())))

    # 6. the table as a data file
    out = ['unit\tgroup\tdocument_issuers_date\tpage_words\tour_english\tremark\tbinding_or_expected\trests_on\twhere_the_page_stands\taddress\tsaved_id']
    for r in rows:
        ref = f'read, not saved; Archive capture {r["capture"]} sha256 {r["sha"]}' if r['arch'] else r['src']
        out.append('\t'.join([r['unit'], r['group'], r['doc'], ' / '.join(r['words']), r['en'] if r['en'] != '-' else '', r['remark'] if r['remark'] != '-' else '',
                              r['label'] if r['label'] != '-' else '', BASIS[r['basis']], r['where'], r['url'], ref]))
    (HERE / 'provinces.tsv').write_text('\n'.join(out) + '\n', encoding='utf-8')

    # 7. vouchers (round 9): the count and the classes are the core's, computed by scripts/cn_voucher_classes.py (imported, so it runs
    # once), whose result must equal the published table tables/local_vouchers_classes.tsv row by row. vouchers.txt holds the rules that
    # favour home-made computing (the 7 that pay more and the 4 that pay for home-made only), which must equal the core's counted rows of
    # those two classes with their rates; the other counted rules (no higher rate for home-made computing) are listed from the core's table.
    import cn_voucher_classes as VC
    R = VC.compute()
    def _tab(name):
        ls = [x for x in (PROJ / 'tables' / name).read_text(encoding='utf-8').split('\n') if x and not x.startswith('#')]
        return [dict(zip(ls[0].split('\t'), x.split('\t'))) for x in ls[1:]]
    ctab = _tab('local_vouchers_classes.tsv')
    if [[c[k] for k in ('row_id', 'government', 'class', 'reason', 'deciding_words', 'saved_id')] for c in ctab] != [list(r) for r in R['out']]:
        sys.exit('tables/local_vouchers_classes.tsv differs from what scripts/cn_voucher_classes.py computes now: the core table is stale; stop')
    _vr = {f'A{i}': r for i, r in enumerate(_tab('local_vouchers.tsv'), 1)}; _vr.update({f'B{i}': r for i, r in enumerate(_tab('local_vouchers_more.tsv'), 1)})
    _pc = lambda s: (lambda m: int(m.group(1)) if m else None)(re.search(r'(\d+)\s*[%％]', s))      # noqa: E731
    _cl = {VC.MORE: 'tiered', VC.ONLY: 'home-made only'}
    vcnt = [c for c in ctab if c['class'] != VC.NOT]
    core_rows = {}
    for c in vcnt:
        if c['class'] not in _cl: continue
        r = _vr[c['row_id']]; h = _pc(r['rate_home']); o = 0 if r['rate_other'].startswith('none') else (_pc(r['rate_other']) or h)
        if c['government'] in core_rows: sys.exit(f'two counted rules for {c["government"]} in tables/local_vouchers_classes.tsv')
        core_rows[c['government']] = (_cl[c['class']], h, o)
    if len({v['place'] for v in vouchers}) != len(vouchers): sys.exit('vouchers.txt: a government twice')
    if any(v['other'] > v['home'] for v in vouchers): sys.exit('vouchers.txt: a rule pays more for other computing: change the note')
    tiered = [v for v in vouchers if v['home'] > v['other'] > 0]; only = [v for v in vouchers if v['other'] == 0]
    if len(tiered) + len(only) != len(vouchers): sys.exit('vouchers.txt: a row that favours no kind of computing: such rules are listed from the core table')
    mine = {VSHORT[v['place']]: ('tiered' if v in tiered else 'home-made only', v['home'], v['other']) for v in vouchers}
    def vdiff(a, b): return sorted(set(a.items()) ^ set(b.items()))
    if vdiff(core_rows, mine): sys.exit(f'vouchers.txt differs from the core\'s counted rules that favour home-made computing: {vdiff(core_rows, mine)}')
    bad = dict(mine); k0 = next(iter(bad)); bad[k0] = (bad[k0][0], bad[k0][1] + 1, bad[k0][2])          # control: one rate changed must be seen
    if not vdiff(core_rows, bad): sys.exit('vouchers control: a changed rate was not seen')
    third = [c for c in vcnt if c['class'] in (VC.ONE, VC.TWO)]
    one = sorted((c for c in vcnt if c['class'] == VC.ONE), key=lambda c: c['government'])
    two = [c for c in vcnt if c['class'] == VC.TWO]
    if len(vcnt) != len(R['counted']) or len(third) != R['third'] or (len(tiered), len(only), len(one), len(two)) != (R['n'][VC.MORE], R['n'][VC.ONLY], R['n'][VC.ONE], R['n'][VC.TWO]):
        sys.exit('the counts from the core table and from cn_voucher_classes.py differ')
    if R['line'] != f'{len(vcnt)} / {len(tiered)} / {len(only)} / {len(third)}': sys.exit(f'the classifier\'s line {R["line"]} is not the count of the table')
    if [c['government'] for c in two] != ['Hangzhou']: sys.exit(f'the note words the rule of two rates by an unnamed type as Hangzhou\'s plan: {[c["government"] for c in two]}')
    not_by = sorted(((v, k[1]) for k, v in R['by'].items() if k[0] == VC.NOT), key=lambda x: -x[0])
    if sum(v for v, _ in not_by) != R['not_counted']: sys.exit('the reasons of the rows not counted do not add up')
    print(f'vouchers: the core\'s table of classes equals cn_voucher_classes.py\'s result ({len(R["out"])} rows); voucher classes {R["line"]}; '
          f'vouchers.txt equals its {len(tiered)} + {len(only)} rules that favour home-made computing, rates included; control (one rate changed) reported')
    (HERE / 'vouchers.tsv').write_text('place\tlevel\tdate\thome_made_pct\tother_pct\thome_made_rate\tother_rate\tclass\trests_on\tnote\tsaved_id\taddress\n' + '\n'.join(
        '\t'.join([v['place'], v['level'], v['date'], str(v['home']), str(v['other']), v['home_en'], v['other_en'], 'pays more for home-made and still pays for other computing' if v in tiered else 'pays for home-made computing only', v['where'], v['note'] if v['note'] != '-' else '', v['src'],
                   json.loads((PRIMARY / v['src'] / 'meta.json').read_text())['url']]) for v in vouchers) + '\n', encoding='utf-8')
    print(f'vouchers: {len(vcnt)} counted; {len(tiered)} pay more for home-made computing ({", ".join(v["place"] for v in tiered)}); {len(only)} pay for home-made computing only ({", ".join(v["place"] for v in only)}); '
          f'{len(third)} state no higher rate ({len(one)} one rate, {len(two)} two rates by a type it does not name: {two[0]["government"]}); {R["not_counted"]} read and not counted')
    # round 10: the second fact about the same rules, scripts/cn_voucher_other.py: how many counted rules also give home-made computing
    # something by ANOTHER provision (the class is decided by the counted payment alone). The script is run (its controls must behave)
    # and its printed line must equal the line made here from its own functions; the note words the kinds as the script names them.
    import cn_voucher_other as VO
    po = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts/cn_voucher_other.py')], capture_output=True, text=True)
    if po.returncode != 0: sys.exit('cn_voucher_other.py failed: ' + (po.stderr or po.stdout)[-400:])
    _vcls, _vcnt = VO.classes(); _vrows = VO.read_tsv(VO.TABLE)
    if VO.problems(_vrows, _vcls, _vcnt): sys.exit('cn_voucher_other.py: rows refused')
    _vt = VO.tally(_vrows, _vcnt); _vn = VO.tally(_vrows, _vcnt, skip=VO.NARROW)
    if VO.line(_vt, _vcnt, 'voucher other provisions') not in po.stdout: sys.exit('cn_voucher_other.py: its printed line is not the line made here')
    (_n3, _r3, _p3, _a3), (_nm, _rm, _pm, _am), (_no, _ro, _po, _ao) = _vt
    if (len(_r3), len(_rm), len(_ro)) != (len(third), len(tiered), len(only)): sys.exit('cn_voucher_other.py: its groups are not the classes counted here')
    if _am or _ao: sys.exit('a rule that pays more, or pays for home-made only, now has another provision: change the note')
    if _p3['USE2'] or [_vcnt[k]['government'] for k in _p3['PREFER']] != ['Beijing city']: sys.exit('other provisions: USE2 or PREFER is not as the note words it')
    if sorted((_vcnt[k]['government'], kd) for k, kd in VO.NARROW) != [('Beijing city', 'PREFER'), ('Hebei District (Tianjin)', 'ADAPT')]: sys.exit('other provisions: the narrow way is not as the note words it')
    _vid = {}
    for r_ in _vrows: _vid.setdefault((r_['row_id'], r_['kind']), r_['saved_id'])
    def _vlist(kd): return ', '.join(f'{_vcnt[k]["government"]} [{_vid[(k, kd)]}]' for k in _p3[kd])
    print(f'other provisions (cn_voucher_other.py, controls behave): of the {len(_r3)} with no higher rate, {len(_a3)} (BUILD {len(_p3["BUILD"])}, ADAPT {len(_p3["ADAPT"])}, PREFER {len(_p3["PREFER"])}); narrow {len(_vn[0][3])}; of the {len(tiered)} and the {len(only)}: 0')
    # the plans of the kind that holds Zhejiang's share, searched as a class (core table): groups counted, and no share in any text read
    ict = _tab('provincial_ict_plans.tsv')
    if {r['unit'] for r in ict} != set(ALL_UNITS) - {'Zhejiang'}: sys.exit('provincial_ict_plans.tsv: not the 30 other units')
    if not all(re.match(r'^(15th: )?(none|not known)', r['home_made_share_number_in_its_own_words_or_none']) for r in ict): sys.exit('provincial_ict_plans.tsv: a plan read sets a home-made share: read it and change the note')
    icg = {g: sum(1 for r in ict if r['group'] == g) for g in ('the plan for 2026 to 2030 read in full', 'the plan for 2026 to 2030 read as a consultation draft', 'only the plan for 2021 to 2025 read', 'no plan text found')}
    if sum(icg.values()) != len(ict): sys.exit('provincial_ict_plans.tsv: a group the note does not name')
    print('plans of Zhejiang\'s kind (core table): ' + '; '.join(f'{g} {n}' for g, n in icg.items()) + '; no text read sets a home-made share')

    # 8. the note
    def cell_mid(r):
        doc = r['doc'].rstrip('.')
        if not r['words']: return f'{doc}. No words on home-made hardware are quoted'
        return f'{doc}. The page says: ' + '; '.join(f'"{w}"' for w in r['words'])

    def cell_last(r):
        s = f'**{BASIS[r["basis"]]}** ({r["where"]}). '
        if r['en'] != '-': s += f'({r["en"]}). '
        if r['remark'] != '-': s += r['remark'] + '. '
        s += f'[{r["src"]}]'
        return s.replace('. .', '.')

    def hidden(r):
        return [f'!! {sid} | {c}' for sid, c in r['checks']]

    def table(groups, with_label=False):
        # with_label: a second column that says whether the page marks the share as binding or indicative.
        # Each label cell is worded to be read alone: the phone view hides the header row and stacks the cells.
        head = ('| Government | Binding or indicative? | Document, issuing bodies and date; the page\'s own words | What the row rests on; our English; limits; source |' if with_label
                else '| Government | Document, issuing bodies and date; the page\'s own words | What the row rests on; our English; limits; source |')
        o = [head]
        for r in rows:
            if r['group'] not in groups: continue
            lab = f' {r["label"]} |' if with_label else ''
            o.append(f'| {r["unit"]} |{lab} {cell_mid(r)} | {cell_last(r)} |')
            o += hidden(r)
        return '\n'.join(o)

    def vtable(vs):
        o = ['| Local government and the rule\'s date | Home-made computing | Other computing | The rule\'s words; what the row rests on; source |']
        for v in vs:
            note = '' if v['note'] == '-' else v['note'] + '. '
            hom = v['home_en'][:1].upper() + v['home_en'][1:]; oth = v['other_en'][:1].upper() + v['other_en'][1:]
            o.append(f'| {v["place"]}, {v["date"]} | {hom} | {oth} | ' + '; '.join(f'"{w}"' for w in v['words'])
                     + f'. **{BASIS[v["basis"]]}** ({v["where"]}). {note}[{v["src"]}] |')
            o += [f'!! {sid} | {c}' for sid, c in v['checks']]
        return '\n'.join(o)

    # binding or indicative: count the two label words in every page of the share group (the checker's own normalised text)
    share = [r for r in docs if r['group'] == 'share']
    cnt = {r['src']: (L.page(r['src']).count('约束性'), L.page(r['src']).count('预期性')) for r in share}
    js = cnt['cn-factions-jiangsu-plan']
    if js[0] != 1 or js[1] < 1: sys.exit(f'label scan: the control failed (Jiangsu: 约束性 {js[0]}, 预期性 {js[1]})')
    # core edit 8: Zhejiang's sector plan has a table of indicators too: 17 lines 预期性, 1 约束性 (its energy-efficiency line), none of them for home-made computing; its share stands outside the table
    zj = cnt['cn-ga31-cndocs-52']; zp = L.page('cn-ga31-cndocs-52'); zi = zp.find('约束性')
    if zj != (1, 17) or 'pue' not in zp[max(0, zi - 40):zi] or re.search('国产|自主', zp[max(0, zi - 40):zi]): sys.exit(f'label scan: Zhejiang\'s plan is not as read (约束性 {zj[0]}, 预期性 {zj[1]})')
    za, zb = zp.find('序号指标名称'), zp.rfind('预期性')
    if not (0 < za < zb) or re.search('国产|自主可控', zp[za:zb + 3]): sys.exit('label scan: Zhejiang\'s table of indicators is not as read')
    stray = {k: v for k, v in cnt.items() if k not in ('cn-factions-jiangsu-plan', 'cn-ga31-cndocs-52') and v != (0, 0)}
    if stray: sys.exit(f'label scan: a label word stands in another page: {stray}; read it and change the label')
    print(f'label scan: {len(cnt)} pages; 约束性 (binding) stands {sum(v[0] for v in cnt.values())} times, 预期性 (indicative) {sum(v[1] for v in cnt.values())} times, all in the tables of indicators of Jiangsu\'s and Zhejiang\'s plans; 0 and 0 in the other {len(cnt) - 2}')
    # Sichuan: the plan's table of main targets holds no home-made row (control: it holds the intelligent-computing row)
    sc = page_text('cn-factions-sichuan50', single=True); i = sc.find('四川省算力基础设施发展主要目标'); j = sc.find('扫一扫', i)
    if i < 0 or j < 0 or '智能算力占比' not in sc[i:j] or '国产' in sc[i:j] or '自主' in sc[i:j]: sys.exit('Sichuan: the table of main targets is not as read')

    best = {u: min((r['basis'] for r in share if r['unit'] == u), key=RANK.index) for u in by['share']}
    by_basis = {k: [u for u in by['share'] if best[u] == k] for k in RANK}
    print('the nine rest on: ' + '; '.join(f'{BASIS[k]}: {len(v)} ({", ".join(v)})' for k, v in by_basis.items() if v))
    doc_basis = {k: sum(1 for r in docs if r['basis'] == k) for k in RANK}
    fill = {'TABLE_SHARE': table(('share',), True), 'TABLE_NONE': table(('none',)), 'TABLE_EDGE': table(('account', 'notfound')),
            'TABLE_OTHER': table(('other',)), 'TABLE_ALSO': table(('also',)),
            'TABLE_V_TIER': vtable(tiered), 'TABLE_V_ONLY': vtable(only),
            'LIST_V_ONE': '; '.join(f'{c["government"]} [{c["saved_id"]}]' for c in one),
            'N_V_THIRD': len(third), 'N_V_TWO': len(two), 'N_V_NOT': R['not_counted'], 'N_V_ROWS': len(R['out']), 'N_V_OWN': len(R['own']), 'N_V_ELSE': len(R['elsewhere']),
            'V_NOT_BY': '; '.join(f'{n} {w}' for n, w in not_by), 'N_V_OTHERNAME': len(R['other_name']),
            'N_VO_ANY': len(_a3), 'N_VO_BUILD': len(_p3['BUILD']), 'N_VO_ADAPT': len(_p3['ADAPT']), 'N_VO_PREFER': len(_p3['PREFER']), 'N_VO_NARROW': len(_vn[0][3]),
            'U_VO_BUILD': _vlist('BUILD'), 'U_VO_ADAPT': _vlist('ADAPT'), 'U_VO_PREFER': _vlist('PREFER'),
            **{f'N_ICT{i}': n for i, n in enumerate(icg.values(), 1)},
            'N_SHARE': len(by['share']), 'N_NONE': len(by['none']), 'U_SHARE': ', '.join(by['share']), 'U_NONE': ', '.join(by['none']),
            'N_NONE_COMP': n_comp, 'N_NONE_OTHERKIND': len(by['none']) - n_comp, 'U_NONE_COMP': ', '.join(kinds.get('computing', [])),
            'U_NONE_OTHERKIND': ', '.join(u for u in by['none'] if u not in kinds.get('computing', [])),
            'N_DOCS': len(docs), 'N_DOCS_NONE': sum(1 for r in docs if r['group'] == 'none'), 'N_DOCS_ALSO': sum(1 for r in docs if r['group'] == 'also'),
            'N_DOCS_SCANNED': sum(1 for r in docs if r['group'] in ('none', 'also', 'account', 'notfound')),
            'N_NEAR': n_near, 'HAS_LINE': has_line, 'DAM_LINE': dam_line,
            'N_LABEL_PAGES': len(cnt), 'N_LABEL_OTHERS': len(cnt) - 2, 'N_JS_EXPECTED': js[1], 'N_ZJ_EXPECTED': zj[1],
            'N_V': len(vcnt), 'N_V_TIER': len(tiered), 'N_V_ONE': len(one), 'U_V_TIER': ', '.join(v['place'] for v in tiered),
            'N_V_ONLY': len(only), 'U_V_ONLY': ', '.join(v['place'] for v in only),
            **{f'N8_{k.upper()}': len(v) for k, v in by_basis.items()}, **{f'W8_{k.upper()}': WORDS[len(v)] for k, v in by_basis.items()},
            **{f'U8_{k.upper()}': ', '.join(v) for k, v in by_basis.items()}, **{f'ND_{k.upper()}': v for k, v in doc_basis.items()},
            'ABSENT_NATIONAL': absent['cn-policy-computing-network-1779'][2]}
    t = (HERE / 'note_template.txt').read_text(encoding='utf-8')
    for k, v in fill.items(): t = t.replace('{{' + k + '}}', str(v))
    if '{{' in t: sys.exit('note_template.txt: a placeholder was not filled: ' + t[t.index('{{'):t.index('{{') + 40])
    (HERE / 'provinces_note_base.txt').write_text(t, encoding='utf-8')

    # 9. references for every saved id the note names that the core's reference lists do not hold
    have = set()
    for f in (PROJ / 'argument/argument_refs.tsv', PROJ / 'argument/argument_refs_more.tsv'):
        have |= {ln.split('\t')[0] for ln in f.read_text(encoding='utf-8').splitlines() if ln.strip() and not ln.startswith('#')}
    named = set(CITE.findall(t)) | {ln[2:].split('|', 1)[0].strip() for ln in t.splitlines() if ln.startswith('!!')}
    lab = {}
    for r in docs:
        kind = 'ACCT' if r['basis'] == 'news' else 'DOC'
        x = f'{r["unit"]}. {r["doc"]}'.rstrip('.')
        if r['basis'] == 'capture': x += f'. Internet Archive capture of {r["cap_date"]}'
        if r['basis'] == 'hand': x += '. A PDF of the official page saved by hand in a browser'
        lab.setdefault(r['src'], (kind, x))
    for v in vouchers:
        lab.setdefault(v['src'], ('DOC', f'{v["place"]}. Local computing-voucher rule, {v["date"]}' + ({'official': '', 'copy': '; a copy on another site', 'capture': '; an Internet Archive capture of the official file'}[v['basis']])))
    # round 9: the counted rules listed from the core table, labelled from the core's cells (document and issuing body)
    for c in one:
        r = _vr[c['row_id']]
        # round 10: a copy that is an Internet Archive capture says so (readers took "another copy" for a third party's)
        _m = json.loads((PRIMARY / c['saved_id'] / 'meta.json').read_text()); _cap = 'web.archive.org' in str(_m.get('route', '')) + str(_m.get('url', '')) or c['saved_id'].endswith('-wayback')
        lab.setdefault(c['saved_id'], ('DOC', f'{c["government"]}. {r["document"]}; {r["body"]}' + ('' if c['row_id'] in R['own'] else ('; read in an Internet Archive capture' if _cap else '; read in another copy than the issuer\'s own page'))))
    lab.update({k: v for k, v in MORE_LABELS.items() if k not in lab})
    refs = ['# id <TAB> kind <TAB> label <TAB> address (empty = the address in the saved copy\'s record). Written by build.py.']
    missing = []
    for sid in sorted(named - have):
        if sid not in lab: missing.append(sid); continue
        refs.append(f'{sid}\t{lab[sid][0]}\t{lab[sid][1]}\t')
    if missing: sys.exit(f'no reference label for: {missing}')
    (HERE / 'extra_refs.tsv').write_text('\n'.join(refs) + '\n', encoding='utf-8')

    p = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts/cn_doc_build.py'), str(HERE / 'provinces_note_base.txt'), '--refs', str(HERE / 'extra_refs.tsv'),
                        '--title', 'Provincial Chip Targets', '--eyebrow', 'China chip policy: provincial targets'], capture_output=True, text=True)
    print(p.stdout.strip()); print(p.stderr.strip())
    sys.exit(p.returncode)


if __name__ == '__main__':
    main()
