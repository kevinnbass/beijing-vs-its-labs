#!/usr/bin/env python3
"""Build A13 (the sixteen governments left open by idea 39): check, count, write the table file and the note.

Round 4 form (Nov 23, 2026); the round-1 form is in round1/build.py.
Run: python3 -I build.py          (from anywhere; everything is written beside this file; no web request is made)
Reads   rows.txt             one block per government (see its header)
        note_template.txt    the note's text with {{PLACEHOLDERS}}
        request_log.txt      every web search, page save and Archive call of round 1 (counted here)
        sources.tsv          every address given to the project's fetcher in round 1
        pages_for_browser.tsv, pages_left_off.tsv   the list for the owner's browser and what left it (counted here)
        archive/             the Internet Archive lists and answers of round 1
        ../../tables/provinces_31.tsv   the session's table of all 31 governments (counted here; each row here must agree with it)
        ../A12_tenders_and_provinces/idea39_provincial_targets/search_log.txt   the earlier builder's searches
Writes  quotes.tsv, archive_strings.tsv, near_percent.txt, absent_check.txt, transcription_check.txt, table.tsv, counts.tsv, extra_refs.tsv,
        unreached_note_base.txt, then unreached_note.md and unreached_note.html through scripts/cn_doc_build.py
Stops before writing the note if any string is not found where it should be, or a control fails.
"""
import html, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path('.')
PROJ = ROOT / 'research' / 'cn_chip_policy_20261120'
PRIMARY = ROOT / 'research' / 'primary'
A12LOG = HERE.parent / 'A12_tenders_and_provinces' / 'idea39_provincial_targets' / 'search_log.txt'
P31 = PROJ / 'tables' / 'provinces_31.tsv'
sys.path.insert(0, str(ROOT / 'scripts'))
import cn_srclib as L   # noqa: E402  (the project's own normaliser: squash(), has(), page())

SIXTEEN = {'Zhejiang': '浙江', 'Chongqing': '重庆', 'Anhui': '安徽', 'Shaanxi': '陕西', 'Shanxi': '山西', 'Jiangxi': '江西', 'Guangxi': '广西', 'Qinghai': '青海',
           'Hainan': '海南', 'Xinjiang': '新疆', 'Tibet': '西藏', 'Guangdong': '广东', 'Jilin': '吉林', 'Heilongjiang': '黑龙江', 'Ningxia': '宁夏', 'Yunnan': '云南'}
RESULTS = ['share', 'reward', 'other', 'earlier', 'account', 'notfound', 'extra']
TO31 = {'share': 'share', 'reward': 'plan_no_share', 'other': 'plan_no_share', 'earlier': 'plan_no_share', 'extra': 'plan_no_share',
        'account': 'account_only', 'notfound': 'not_reached'}          # this note's result -> the session table's result
EXPECT = {'share': ['Guangdong'], 'reward': ['Shanxi', 'Ningxia'],
          'other': ['Anhui', 'Jilin', 'Guangxi', 'Jiangxi', 'Qinghai', 'Chongqing', 'Zhejiang', 'Shaanxi', 'Hainan'],
          'earlier': ['Heilongjiang', 'Yunnan'], 'account': ['Tibet'], 'notfound': ['Xinjiang'], 'extra': ['Gansu', 'Hunan']}   # what the template's prose names
BASIS = {'official': 'Saved official page', 'wayback': 'Saved Archive capture of the official page', 'copy': 'Saved copy on another site',
         'account': 'A press account saved from another site', 'capture': 'Archive capture kept in this folder: read, not saved',
         'hand': "Saved official page, saved by hand in the owner's browser"}
DAMAGED = {'man-cn-o39-qinghai-green-compute-2024', 'man-cn-o39-qinghai-compute-15fyp-2026', 'man-cn-o39-hunan-green-compute-plan-2025'}   # PDF text layer damaged: never quoted
NEAR_EXPECT = {'cn-o39b-guangdong-yuesuan-2024': 2, 'cn-o39b-shanxi-measures-2024-jincheng': 1, 'cn-o39-guangxi-digital-plan-2024-wayback': 1,
               'cn-o39-qinghai-green-compute-2024-wayback': 1, 'cn-o39-hunan-green-compute-plan-2025-wayback': 1}     # the places read; the template describes exactly these
GROUP_SEARCHES = {'11', '12', '13'}
WORDS = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen']
HOME = re.compile(r'国产|自主可控|安全可控|安全可靠|自主化|信创')
QUOTE = re.compile(r'"([^"]+)"')
HANDNOTE = "Saved by hand in the owner's browser as a PDF; its text layer is damaged and is not quoted: the words cited from it were read from the page images and typed into transcription.txt beside the saved copy"
REFS = {   # id: (kind, label). Ids that the argument's own references file already holds keep the core's label and are not written to extra_refs.tsv.
    'cn-o39b-broker-table-202410': ('PUB', 'A report on AI computing by a server maker (Inspur) and a state research institute (the China Academy of Information and Communications Technology), with a table of national and provincial computing plans. No date was read in the saved copy'),
    'cn-o39-ningxia-ai-measures-2023': ('DOC', "General Office of the Ningxia Hui Autonomous Region People's Government, measures to promote artificial intelligence (宁政办规发〔2023〕8号), Aug 13, 2023 (read by the first note)"),
    'cn-o39b-ningxia-hub-plan-2024-yinchuan-news': ('ACCT', "Ningxia's implementation plan for its computing hub, 2025 to 2027, as reported by Ningxia Daily on the Yinchuan city government's site, Dec 18, 2024. A newspaper's account, not the plan's text"),
    'cn-o39b-anhui-digital-infra-2023-sd-copy': ('DOC', "Anhui Data Resources Bureau and five other bodies, three-year plan for digital infrastructure, 2023 to 2025, Dec 11, 2023. A copy on the Shandong big data bureau's site"),
    'cn-o39b-anhui-compute-plan-2023-jswx': ('ACCT', "Anhui's plan for intelligent computing infrastructure, 2023 to 2025, as described on the Jiangsu cyberspace office's site on Dec 8, 2023, which credits state radio's news site and the provincial planner. An account, not the plan's text"),
    'cn-o39b-jilin-digital-plan-2023': ('DOC', "General Office of the Jilin Provincial People's Government, plan for the digital economy, 2023 to 2025 (吉政办发〔2023〕34号), written Dec 1, 2023"),
    'cn-o39-jilin-ai-opinion-2025': ('DOC', "Jilin Provincial People's Government, opinions on artificial intelligence, Sept 12, 2025 (read by the first note)"),
    'cn-o39-guangxi-digital-plan-2024-wayback': ('DOC', "Guangxi Big Data Development Bureau, three-year plan to promote the digital economy, 2024 to 2026 (桂数发〔2024〕17号), Jul 9, 2024. Internet Archive capture of the bureau's page"),
    'cn-o39b-guangxi-ai-plus-2026-tzxm': ('DOC', "General Office of the Guangxi Zhuang Autonomous Region People's Government, three-year AI Plus plan, 2026 to 2028 (桂政办发〔2025〕61号), Dec 27, 2025. A copy on a state investment-approval site"),
    'cn-o39-jiangxi-industry-compute-2026-wayback': ('DOC', "Jiangxi Department of Industry and Information Technology, three-year plan for computing services and data in industry, 2026 to 2028, Apr 30, 2026. Internet Archive capture of the department's page"),
    'cn-o39-qinghai-compute-15fyp-2026-wayback': ('DOC', "Qinghai Provincial People's Government, plan for the green computing industry in the fifteenth five-year period (青政〔2026〕57号), Aug 25, 2026. Internet Archive capture of the provincial government's page"),
    'cn-o39-qinghai-green-compute-2024-wayback': ('DOC', "General Office of the Qinghai Provincial People's Government, plan for a green computing base (青政办〔2024〕7号), Feb 5, 2024. Internet Archive capture of the provincial government's page"),
    'man-cn-o39-qinghai-compute-15fyp-2026': ('DOC', "Qinghai Provincial People's Government, plan for the green computing industry in the fifteenth five-year period, Aug 25, 2026. " + HANDNOTE),
    'cn-o39b-chongqing-sina-article': ('ACCT', "Chongqing's three-year plan for computing, 2024 to 2026, as described in an article on the Sina portal, Nov 8, 2024. A portal article, not a newspaper's, and not the plan's text"),
    'cn-le16-shaanxi-digital-measures-2024-mofcom': ('DOC', "Shaanxi Provincial Party Committee and Provincial People's Government, measures for the digital economy. A copy on the commerce ministry's e-commerce service site"),
    'cn-le16-hainan-ai-plus-2026-smartcity': ('DOC', "General Office of the Hainan Provincial People's Government, AI Plus action plan, 2026 to 2028 (琼府办〔2026〕6号). A copy on the policy site smartcity.team"),
    'cn-o39-heilongjiang-ai-plus-2026': ('DOC', "Heilongjiang Provincial People's Government, AI Plus implementation plan, written Feb 14, 2026 (read by the first note)"),
    'cn-o39-yunnan-digital-channel-2026': ('DOC', "General Office of the Yunnan Provincial People's Government, plan for a digital information corridor and the digital industry, May 15, 2026. A copy on another provincial body's site (read by the first note)"),
    'cn-o39b-tibet-compute-plan-2024-wxb': ('ACCT', "Tibet's action plan for computing, 2024 to 2026, as reported by the trade newspaper People's Posts and Telecommunications News on the regional cyberspace office's site, Jun 27, 2024. A newspaper's account, not the plan's text"),
    'cn-le16-xinjiang-plan-2024-indicators': ('DOC', "Xinjiang Uygur Autonomous Region, the region's plan for economic and social development for 2024, on the regional government's site (saved by agent L16)"),
    'cn-le16-xinjiang-drc-cppcc-197-reply-202510': ('DOC', "Xinjiang Development and Reform Commission, reply to a proposal on computing, posted Sept 5, 2025, on the commission's site (saved by agent L16)"),
    'man-cn-o39-gansu-ai-plus-2026': ('DOC', "Gansu Provincial People's Government, AI Plus action plan (甘政发〔2026〕1号), Jan 6, 2026. Saved by hand in the owner's browser as a PDF; its text layer is sound"),
    'cn-o39-hunan-green-compute-plan-2025-wayback': ('DOC', "Hunan Department of Industry and Information Technology, plan for the green intelligent computing industry, 2025 to 2030 (湘工信信软〔2025〕53号), Feb 23, 2025. Internet Archive capture of the department's page"),
    'man-cn-o39-hunan-green-compute-plan-2025': ('DOC', 'Hunan Department of Industry and Information Technology, plan for the green intelligent computing industry, 2025 to 2030, Feb 23, 2025. ' + HANDNOTE),
}


def stop(msg):
    print('STOP:', msg); sys.exit(1)


def single(sid):
    """One form of a page for counting places: the HTML body without tags, or else text.txt."""
    d = PRIMARY / sid; t = ''
    for b in d.glob('body*'):
        if b.suffix.lower() in ('.html', '.htm'):
            raw = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', b.read_text(encoding='utf-8', errors='replace'))
            t += ' ' + html.unescape(re.sub(r'(?s)<[^>]+>', ' ', raw))
    if not t.strip() and (d / 'text.txt').exists(): t = (d / 'text.txt').read_text(encoding='utf-8', errors='replace')
    return re.sub(r'\s+', '', t)


def num(n, cap=False):
    w = WORDS[n] if 0 <= n < len(WORDS) else str(n)
    return w.capitalize() if cap else w


def read_rows():
    rows, cur = [], None
    for ln in (HERE / 'rows.txt').read_text(encoding='utf-8').splitlines():
        if ln.startswith('#'): continue
        if not ln.strip():
            if cur: rows.append(cur); cur = None
            continue
        k, _, v = ln.partition(':'); k = k.strip(); v = v.strip()
        if cur is None: cur = {'check': [], 'absent': [], 'capture': [], 'capabsent': []}
        if k in ('check', 'absent', 'capture', 'capabsent'): cur[k].append([x.strip() for x in v.split('|')])
        else: cur[k] = v
    if cur: rows.append(cur)
    return rows


def core_ref_ids():
    ids = set()
    for f in (PROJ / 'argument' / 'argument_refs.tsv', PROJ / 'argument' / 'argument_refs_more.tsv'):
        if f.exists(): ids |= {l.split('\t')[0] for l in f.read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')}
    return ids


def has_strict(words, sid):
    """For a hand-saved PDF with a damaged text layer: the words must stand in our typed reading, never in the PDF's text."""
    if sid in DAMAGED:
        f = PRIMARY / sid / 'transcription.txt'
        return f.exists() and len(L.squash(words)) >= 6 and L.squash(words) in L.squash(f.read_text(encoding='utf-8'))
    return L.has(words, sid)


def archive_state():
    out = {}
    for lst in sorted((HERE / 'archive').glob('list*.tsv')):
        for ln in lst.read_text(encoding='utf-8').splitlines():
            if not ln.strip() or ln.startswith('#'): continue
            key = ln.split('\t')[0]; av = HERE / 'archive' / f'{key}.avail.json'
            if not (av.exists() and av.stat().st_size > 2): out[key] = ('waiting', ''); continue
            j = json.loads(av.read_text(encoding='utf-8', errors='replace'))
            if 'withdrawn' in j: out[key] = ('withdrawn', ''); continue
            snap = (j.get('archived_snapshots') or {}).get('closest') or {}
            out[key] = ('capture', snap.get('timestamp', '')) if snap.get('available') and str(snap.get('status')) == '200' else ('none', '')
    return out


def main():
    rows = read_rows()
    main_rows = [r for r in rows if r.get('table') != '2']
    if sorted(r['gov'] for r in main_rows) != sorted(SIXTEEN): stop('rows.txt does not hold exactly the sixteen governments, one block each')
    by = {k: [r['gov'] for r in rows if r['result'] == k] for k in RESULTS}
    if by != EXPECT: stop(f'the template names the governments of each result group; rows.txt now gives {by}: reword the template, then change EXPECT')

    # ---- the session's table of all 31: counts, and agreement row by row
    t31 = [l.rstrip('\n').split('\t') for l in P31.read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    res31 = {r[0]: r[1] for r in t31[1:]}
    if len(res31) != 31: stop(f'{P31} does not hold 31 governments')
    for r in rows:
        if res31.get(r['gov']) != TO31[r['result']]: stop(f"{r['gov']}: this note says {r['result']}, the session's table says {res31.get(r['gov'])}")
    c31 = {k: sum(1 for v in res31.values() if v == k) for k in ('share', 'plan_no_share', 'account_only', 'not_reached')}

    # ---- searches named for each government (round 1 here; the earlier builder's)
    logl = [l.split(' @@ ') for l in (HERE / 'request_log.txt').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    a12 = [l.split(' @@ ') for l in A12LOG.read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')] if A12LOG.exists() else []
    fill = {}
    for g, zh in SIXTEEN.items():
        s = sum(1 for f in logl if f[1] == 'search' and f[0] not in GROUP_SEARCHES and zh in f[3])
        e = sum(1 for f in a12 if len(f) >= 3 and not f[1].startswith('page reading') and zh in f[2])
        fill[f'S_{g}'] = num(s); fill[f'S_{g}_cap'] = num(s, True); fill[f'E_{g}'] = num(e); fill[f'T_{g}'] = num(s + e)
    l16 = [l.split('\t') for l in (PROJ / 'loose_ends' / 'L16_provinces' / 'searches.tsv').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    l16 = [f for f in l16 if len(f) >= 3 and f[1] == 'search' and 'not run' not in ' '.join(f[2:])]      # agent L16's searches that ran (one of its lines lacks a tab, so the whole line is tested)
    for g in ('Xinjiang', 'Shaanxi', 'Hainan'): fill[f'L16_{g}'] = num(sum(1 for f in l16 if SIXTEEN[g] in f[2]))
    fill['L16_Xinjiang_site'] = num(sum(1 for f in l16 if '[xinjiang.gov.cn]' in f[2]))
    arch = archive_state()
    MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    for k, v in arch.items():
        if v[0] == 'capture': fill[f'CAPDATE_{k}'] = f'{MON[int(v[1][4:6]) - 1]} {int(v[1][6:8])}, {v[1][:4]}'

    def filled(s):
        return re.sub(r'\{\{([A-Za-z0-9_\-]+)\}\}', lambda m: str(fill[m.group(1)]) if m.group(1) in fill else m.group(0), s)

    # ---- every string against the saved pages
    quotes, bad, core = [], [], core_ref_ids()
    for r in rows:
        for k in ('doc', 'words', 'english', 'limits', 'official', 'plain'): r[k] = filled(r.get(k, ''))
        if '{{' in ' '.join(r[k] for k in ('doc', 'words', 'english', 'limits', 'official', 'plain')): stop(f"{r['gov']}: a placeholder was not filled")
        if '"' in r['plain']: stop(f"{r['gov']}: words of an Archive capture must stand without quotation marks")
        if r['result'] not in RESULTS or r['basis'] not in BASIS: stop(f"{r['gov']}: unknown result or basis")
        ids = r.get('ids', '').split()
        for i in ids:
            if i not in REFS and i not in core: stop(f"{r['gov']}: {i} has no reference label")
            if not (PRIMARY / i).is_dir(): stop(f"{r['gov']}: {i} has no saved copy")
        if r.get('share'):
            if r['result'] != 'share': stop(f"{r['gov']}: a share is typed but the result is not share")
            quotes.append((ids[0], r['share']))
        elif r['result'] == 'share': stop(f"{r['gov']}: result share without the page's words")
        for k in ('doc', 'words', 'english', 'limits', 'official'):
            for q in QUOTE.findall(r[k]):
                hit = [i for i in ids if i not in DAMAGED and L.has(q, i)]      # a quotation never rests on a damaged PDF
                if not hit: bad.append(f"{r['gov']}: NOT FOUND in a sound saved copy among {', '.join(ids) or 'no id'}: {q}")
                else: quotes.append((hit[0], q))
        for c in r['check']:
            if len(c) != 2 or c[0] not in ids: stop(f"{r['gov']}: bad check line {c}")
            quotes.append((c[0], c[1]))
    quotes = list(dict.fromkeys(quotes))
    for sid, q in quotes:
        if not has_strict(q, sid): bad.append(f'NOT FOUND in {sid}: {q}')
    if L.has('力争到2025年底，新增国产化算力占比达到90%', 'cn-o39b-guangdong-yuesuan-2024'): bad.append('control: a planted false string was found')
    if has_strict('3 算力设施 数据中心标准机架规模 万架 4 16 预期性', 'man-cn-o39-qinghai-compute-15fyp-2026'): bad.append('control: a planted false table row was found in a transcription')
    if bad: print('\n'.join(sorted(set(bad)))); stop(f'{len(set(bad))} string(s) not found')
    (HERE / 'quotes.tsv').write_text('# saved id <TAB> exact words of the page. Written by build.py from rows.txt; check with scripts/cn_has.py.\n'
                                     '# For the hand-saved PDFs with a damaged text layer the words are those of transcription.txt (our reading of the page images).\n' +
                                     ''.join(f'{sid}\t{q}\n' for sid, q in quotes), encoding='utf-8')
    n_dam = sum(1 for sid, _ in quotes if sid in DAMAGED)

    # ---- our typed readings of the damaged PDFs' page images, against the saved captures of the same pages (sound text)
    PAIR = {'man-cn-o39-qinghai-green-compute-2024': 'cn-o39-qinghai-green-compute-2024-wayback', 'man-cn-o39-qinghai-compute-15fyp-2026': 'cn-o39-qinghai-compute-15fyp-2026-wayback',
            'man-cn-o39-hunan-green-compute-plan-2025': 'cn-o39-hunan-green-compute-plan-2025-wayback'}
    tr_lines, tr_tot, tr_same, tr_cell, tr_image = ['# typed line of transcription.txt @@ how it stands in the saved capture of the same page. Written by build.py.'], 0, 0, 0, 0
    for man, wb in PAIR.items():
        pg = L.page(wb)
        for ln in (PRIMARY / man / 'transcription.txt').read_text(encoding='utf-8').splitlines():
            if not ln.startswith('[page '): continue
            txt = ln.split('] ', 1)[1]; tr_tot += 1
            if L.squash(txt) in pg: tr_same += 1; how = 'word for word'
            elif ' ' in txt and L.squash(txt.split(' ', 1)[1]) in pg: tr_cell += 1; how = 'word for word once the repeated category cell is set aside'
            else: tr_image += 1; how = 'NOT in the capture text (a table or box that is an image there too): rests on the page image alone'
            tr_lines.append(f'{man} @@ {txt} @@ {how}')
    (HERE / 'transcription_check.txt').write_text('\n'.join(tr_lines) + '\n', encoding='utf-8')
    if L.squash('推动算力中心部署自主可控、安全可控的算力设备') in L.page('cn-o39-qinghai-compute-15fyp-2026-wayback'): stop('control: a misreading (安全可控 for 安全可靠) was found in the capture')
    if (tr_tot, tr_same, tr_cell, tr_image) != (56, 40, 5, 11): stop(f'the template describes 56 typed lines: 40 the same, 5 once a cell is set aside, 11 images; now {(tr_tot, tr_same, tr_cell, tr_image)}: read transcription_check.txt and reword')
    fill.update({'TR_TOT': tr_tot, 'TR_SAME': tr_same + tr_cell, 'TR_CELL': num(tr_cell), 'TR_IMAGE': tr_image})

    # ---- strings from the Archive capture kept in archive/ (read, not saved)
    cap_text, cap_q = {}, []
    def cap(key):
        if key not in cap_text: cap_text[key] = L.squash((HERE / 'archive' / f'{key}.txt').read_text(encoding='utf-8'))
        return cap_text[key]
    for r in rows:
        if r['basis'] == 'capture' and not r['capture']: stop(f"{r['gov']}: a row that rests on a capture needs capture checks")
        for c in r['capture']:
            if L.squash(c[1]) not in cap(c[0]): stop(f"{r['gov']}: NOT FOUND in the capture {c[0]}: {c[1]}")
            cap_q.append((c[0], c[1]))
        if r['plain'] and not any(L.squash(r['plain'].split(':', 1)[1]) in cap(c[0]) for c in r['capture']): stop(f"{r['gov']}: the words shown are not in its capture")
    if L.squash('逐步提升算力基础设施使用自主可控设备比例达到70%') in cap('o39b-jiangxi-measures-2025-jdz'): stop('control: a planted false string was found in a capture')
    (HERE / 'archive_strings.tsv').write_text('# capture key (archive/<key>.txt) <TAB> exact words. Written by build.py; each was found in the capture.\n' + ''.join(f'{k}\t{q}\n' for k, q in cap_q), encoding='utf-8')

    # ---- words that are not in a page, each with a control word that is
    ab, n_ab = ['# page @@ control word (count) @@ words counted at zero. Written by build.py.'], 0
    for r in rows:
        for kind, text_of in (('absent', L.page), ('capabsent', cap)):
            for a in r[kind]:
                sid, control, words = a[0], a[1], [w.strip() for w in a[2].split(',')]
                if sid in DAMAGED: stop(f'{sid}: no word count is made on a damaged text layer')
                p = text_of(sid); c = p.count(L.squash(control))
                if c < 1: stop(f'{sid}: the control word {control} is not in the page, so a zero proves nothing')
                for w in words:
                    if p.count(L.squash(w)): stop(f"{r['gov']}: {w} IS in {sid}; the row says it is not")
                ab.append(('capture ' if kind == 'capabsent' else '') + f'{sid} @@ {control} ({c}) @@ ' + ', '.join(f'{w} (0)' for w in words)); n_ab += 1
    if L.page('cn-o39b-guangdong-yuesuan-2024').count(L.squash('国产')) < 1: stop('control: the absent-word count cannot see a word that is there')
    (HERE / 'absent_check.txt').write_text('\n'.join(ab) + '\n', encoding='utf-8')

    # ---- home-made words near a percent sign, in the pages read in this pass or saved since (not the first note's pages, not the damaged PDFs)
    scan = list(dict.fromkeys(i for r in rows for i in r.get('ids', '').split()
                              if (i.startswith(('cn-o39b-', 'cn-le16-', 'cn-le25-')) or i.endswith('-wayback')) and i != 'cn-o39b-broker-table-202410'))
    near, got = ['# saved id @@ the place. Written by build.py; every line was read.'], {}
    for sid in scan:
        t = single(sid); seen = []
        for m in re.finditer('[%％]', t):
            seg = t[max(0, m.start() - 60):m.end() + 60]
            if 'http' in seg or '%e' in seg.lower(): continue
            if HOME.search(seg) and not any(abs(m.start() - s) < 60 for s in seen):
                seen.append(m.start()); near.append(f'{sid} @@ {t[max(0, m.start() - 60):m.end() + 30]}')
        if seen: got[sid] = len(seen)
    (HERE / 'near_percent.txt').write_text('\n'.join(near) + '\n', encoding='utf-8')
    if got != NEAR_EXPECT: stop(f'near_percent.txt no longer holds the places the template describes ({got}): read it, reword the template, then change NEAR_EXPECT')

    # ---- counts
    logl = [f for f in logl if f[1] != 'withdrawn']
    kinds = [f[1] for f in logl]
    n_search, n_save, n_arch = kinds.count('search'), kinds.count('save'), kinds.count('Archive')
    if n_search + n_save + n_arch != len(logl): stop('request_log.txt has a line of an unknown kind')
    def tsv_rows(name):
        return [l.split('\t') for l in (HERE / name).read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')][1:]
    br, left = tsv_rows('pages_for_browser.tsv'), tsv_rows('pages_left_off.tsv')
    if any(len(b) != 6 for b in br): stop('pages_for_browser.tsv: a line does not have six fields')
    tried = {l.split('\t')[0] for l in (PROJ / 'hand_tried_20261123.tsv').read_text(encoding='utf-8').splitlines()[2:] if l.strip()}
    for b in br:
        if re.search(r'bloomberg|theinformation|scmp\.com', b[2], re.I): stop('pages_for_browser.tsv lists a page of an outlet that must not be listed')
    n_acct = len({i for r in rows for i in r.get('ids', '').split() if REFS.get(i, ('',))[0] == 'ACCT'})
    st = [v[0] for v in arch.values()]
    gov_form = [f[0] for f in logl if f[1] == 'search' and f[2] == 'gov.cn' and '算力基础设施 OR 智能算力 OR 算力产业' in f[3]]     # one form of words, limited to government sites
    if '72' not in gov_form or '63' not in gov_form: stop('the control named in the template (request 72, Jilin) or the Xinjiang search (63) is not of the common form')
    for g in ('Shaanxi', 'Hainan', 'Guangxi', 'Jilin', 'Heilongjiang', 'Yunnan'):
        if fill[f'S_{g}'] != 'two': stop(f'the template says two round-1 searches for {g}; the log says {fill[f"S_{g}"]}')
    n_read = len(by['reward']) + len(by['other']) + len(by['earlier'])
    fill.update({'N_GOVFORM': num(len(gov_form)), 'GOVFORM_REQS': ', '.join(gov_form), 'N_READ': num(n_read), 'N_other': num(len(by['other'])),
                 'N_ARCH_WD_cap': num(st.count('withdrawn'), True), 'N_LEFT_cap': num(len(left), True)})
    fill.update({'N31_share': num(c31['share']), 'N31_share_cap': num(c31['share'], True), 'N31_plan': c31['plan_no_share'], 'N31_account': num(c31['account_only']),
                 'N31_notfound': num(c31['not_reached']), 'N_other_cap': num(len(by['other']), True), 'U_other': ', '.join(by['other']),
                 'N_REQ': len(logl), 'N_SEARCH': n_search, 'N_SAVE': n_save, 'N_ARCH': n_arch, 'N_ARCH_NONE': num(st.count('none')), 'N_ARCH_CAP': num(st.count('capture')),
                 'N_ARCH_WD': num(st.count('withdrawn')), 'N_BROWSER': num(len(br)), 'N_LEFT': num(len(left)), 'N_TRIED': len(tried),
                 'N_NEAR': num(sum(got.values())), 'N_NEAR_PAGES': num(len(got)), 'N_SCAN': len(scan), 'N_ABSENT': num(n_ab), 'N_ACCT_cap': num(n_acct, True)})
    (HERE / 'counts.tsv').write_text('# Written by build.py.\nwhat\tcount\twhich\n' + ''.join(f'result {k}\t{len(v)}\t{", ".join(v)}\n' for k, v in by.items()) +
                                     ''.join(f'all 31, session table: {k}\t{v}\t\n' for k, v in c31.items()) +
                                     f'round-1 requests: web searches\t{n_search}\t\nround-1 requests: page saves\t{n_save}\t\nround-1 requests: Archive calls\t{n_arch}\t' +
                                     '; '.join(f'{k} {v[0]}' for k, v in arch.items()) + f'\nround-1 requests: all\t{len(logl)}\t\nround-4 requests\t0\t\n'
                                     f'pages_for_browser.tsv lines\t{len(br)}\t{", ".join(b[0] for b in br)}\npages_left_off.tsv lines\t{len(left)}\t\n'
                                     f'pages scanned for a home-made word near a percent sign\t{len(scan)}\t{"; ".join(f"{k} {v}" for k, v in got.items())}\n', encoding='utf-8')

    # ---- the tables: for the note (three columns) and as data
    trow, trow2, tsv = [], [], ['table\tgovernment\tresult\tdocument, issuing bodies and date\tshare in the page\'s own words\tother words of the page\tour English and limits\twhat the row rests on\tofficial address\tsaved ids']
    for r in rows:
        ids = r.get('ids', '').split()
        share = f'The page says: "{r["share"]}"' if r.get('share') else ''
        said = ' '.join(x for x in (share, r['words'], r['plain']) if x)
        if r['result'] != 'share':
            said += ('. ' if r['plain'] and not r['words'] else ' ') + {'account': 'No share in either account.', 'notfound': 'No share in the two pages cited.'}.get(r['result'], 'No share in the page read.')
        m = re.match(r'(https?://\S+)\s*(.*)', r['official'])
        if m and r['basis'] == 'wayback': off = 'Official address: given in table.tsv.'
        elif m and r['basis'] in ('official', 'hand'): off = 'Official address: in the references, with the saved copy.'
        elif m: off = ('Official address: given in table.tsv ' + ('' if 'http' in m.group(2) else m.group(2))).strip() + '.'
        else: off = f'Official address: {r["official"][0].lower() + r["official"][1:]}'
        col3 = ' '.join(x for x in (r['english'], r['limits'], f'**{BASIS[r["basis"]]}.**', off, ' '.join(f'[{i}]' for i in ids if f'[{i}]' not in r['limits'])) if x)
        line = f"| {r['gov']} | {r['doc']} {said} | {col3} |"
        if line.count('|') != 4: stop(f"{r['gov']}: a bar inside a cell")
        if re.search(r'https?://', line): stop(f"{r['gov']}: an address inside a table cell; it cannot wrap there")
        tgt = trow2 if r.get('table') == '2' else trow
        tgt.append(line); tgt.extend(f'!! {c[0]} | {c[1]}' for c in r['check'])
        tsv.append('\t'.join([r.get('table', '1'), r['gov'], r['result'], r['doc'], r.get('share') or {'account': 'no share in either account', 'notfound': 'no computing plan found; no share in the pages cited'}.get(r['result'], 'no share in the page read'), ' '.join(x for x in (r['words'], r['plain']) if x),
                              ' '.join(x for x in (r['english'], r['limits']) if x), BASIS[r['basis']], r['official'], ' '.join(ids)]))
    (HERE / 'table.tsv').write_text('\n'.join(tsv) + '\n', encoding='utf-8')
    fill['TABLE'] = '\n'.join(trow); fill['TABLE2'] = '\n'.join(trow2)
    fill['CHECK_LINE'] = (f'Saved pages: {len(quotes)} strings checked, {len(quotes)} found, 0 not found ({n_dam} of them against our typed reading of page images); two planted false strings were rejected. '
                          f'Words not in a page: {n_ab} checks, each with a control word found. Archive capture kept here: {len(cap_q)} strings checked, all found; a planted false string was rejected. '
                          f'Home-made words near a percent sign: {sum(got.values())} places in {len(got)} of {len(scan)} pages scanned, each read. All 31, from the session\'s table: '
                          f'{c31["share"]} share, {c31["plan_no_share"]} plan read without a share, {c31["account_only"]} account only, {c31["not_reached"]} no plan found.')
    cited = list(dict.fromkeys(i for r in rows for i in r.get('ids', '').split()))
    (HERE / 'extra_refs.tsv').write_text('# id <TAB> kind <TAB> label <TAB> address (empty = the address in the saved copy\'s record). Written by build.py. Ids the argument\'s references file holds keep its label and are not here.\n' +
                                         ''.join(f'{i}\t{REFS[i][0]}\t{REFS[i][1]}\t{json.loads((PRIMARY / i / "meta.json").read_text()).get("url", "") if i.startswith("man-") else ""}\n'
                                                 for i in cited if i not in core), encoding='utf-8')
    note = filled((HERE / 'note_template.txt').read_text(encoding='utf-8'))
    leftover = re.findall(r'\{\{[^}]+\}\}', note)
    if leftover: stop(f'placeholders not filled: {sorted(set(leftover))}')
    (HERE / 'unreached_note_base.txt').write_text(note, encoding='utf-8')
    print(fill['CHECK_LINE'])
    p = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts' / 'cn_has.py'), str(HERE / 'quotes.tsv')], capture_output=True, text=True)
    print('cn_has.py:', (p.stdout.strip().splitlines() or ['(no output)'])[-1], '| exit', p.returncode)
    if p.returncode != 0: print(p.stdout[-1500:]); stop('cn_has.py failed')
    p = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts' / 'cn_doc_build.py'), str(HERE / 'unreached_note_base.txt'), '--refs', str(HERE / 'extra_refs.tsv'),
                        '--title', 'Sixteen Provincial Plans', '--eyebrow', 'China chip policy: idea 39, second pass'], capture_output=True, text=True)
    print(p.stdout.strip()[-2500:]); print(p.stderr.strip()[-1200:])
    if p.returncode != 0: stop('cn_doc_build.py did not write the note')


main()
