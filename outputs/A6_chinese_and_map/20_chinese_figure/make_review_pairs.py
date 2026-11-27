"""Write pairs_for_review.tsv: every English line of the figure beside its Chinese line, for a second reader.

Run: python3 -I make_review_pairs.py      (after make_inputs.py and cn_figure_build.py)
Round 4: the pairs come from the files and the two built pages themselves, so the list cannot drift from what is shown.
  records  zh_lines.txt (each record's Chinese T, S, label and date label beside the core's English, which
           make_inputs.py has checked against the core's present data) and the core's data (Q with my Z; E with Q)
  page     the visible text of the core's built page (../../../figure/beijing_vs_labs.html, read only) beside the
           visible text of beijing_vs_labs_zh.html, element by element, for every kind of element listed in KINDS.
           The script stops if a kind has a different number of elements on the two pages.
  pop-up   the labels of the pop-up, listed by hand and checked to stand in the two templates.
Lines that exist only on the Chinese page are listed with an empty English cell.
Round 14 (Nov 26, 2026): a record mark inside an element is written " [record mark N] ", apart from the words (GRAB).
Round 4 mirror: include the displayed one-rate value and the three saved-source lines added by the core.
"""
import re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

F = Path(__file__).resolve().parent
EN = F / 'english_originals'
CORE_PAGE = F.parents[2] / 'figure' / 'beijing_vs_labs.html'
ZH_PAGE = F / 'beijing_vs_labs_zh.html'
CJK = re.compile(r'[一-鿿]')
rows = []
review = {}
RECORD_REVIEW = {
    'man-cn-factions-wsj-ding': 'Record 11. The Journal cites unnamed people, dates the Huawei briefing to summer 2025 and gives no date for the warning. The strip preserves the English quote.',
    'cn-acts-reuters-customs-20260114': 'Record 21. Reuters cites three unnamed people for the customs account, and two of them plus a third unnamed source for the instructions to companies. Compare the English quotes.',
}
NOTE_REVIEW = {
    1: 'Argument point 18 and B17-P18. Later ministry census and AFP question in the reporter’s own words.',
    2: 'Argument points 4 and 18. AI-chip warnings, the forum exception and the eight-week count.',
    3: 'Argument point 4. The warning breakdown moved into the preceding note.',
    4: 'Argument answer, third limit. Nvidia filings first, then Reuters and unnamed sourcing.',
    6: 'Three readings of Beijing’s intent. The closing sentence describes the direction of the acts drawn here.',
    7: 'Compare the Tencent licence-table value and the two attributed per-buyer ceilings. The August quotation is from Reuters’s relay of the Financial Times report.',
}

# ---------- records ----------
core, cur = {}, None
core_lines = (EN / 'figure_data.txt').read_text(encoding='utf-8').splitlines()
for ln in core_lines:
    if ln.startswith('@ '):
        _, lane, kind, d, dl, sid = ln.split(); cur = core[(lane, sid)] = dict(dl=dl, n=len(core) + 1)
    elif cur is not None and ln[:2] in ('T ', 'S ', 'Q ', 'E ', 'C ', 'A '): cur[ln[0]] = ln[2:].strip()
zh, cur = {}, None
for ln in (F / 'zh_lines.txt').read_text(encoding='utf-8').splitlines():
    if ln.startswith('@ '):
        _, lane, sid = ln.split(); cur = zh[(lane, sid)] = {}
    elif cur is not None and ln.strip() and not ln.startswith(('#', '!')):
        k, _, v = ln.partition(' '); cur[k] = v.strip()
assert set(core) == set(zh), set(core) ^ set(zh)
for key, c in core.items():
    z = zh[key]; tag = f'record, block {c["n"]} of the data [{key[0]} {key[1]}]'
    assert z['ET'] == c['T'] and z['ES'] == c['S'], f'run make_inputs.py first: {key}'
    if c['dl'] != '-': rows.append((tag + ' date label', c['dl'].replace('_', ' '), z['D']))
    rows.append((tag + ' T', c['T'], z['T'])); rows.append((tag + ' S', c['S'], z['S']))
    assert z.get('EA') == c.get('A') and ('A' in c) == ('A' in z), f'run make_inputs.py first: {key}'
    if 'A' in c: rows.append((tag + ' second source', c['A'].split(' | ', 1)[1], z['A']))
    if 'C' in c:
        assert z['EC'] == c['C'].split(' ', 3)[3], f'run make_inputs.py first: {key}'
        label_tag = tag + ' C (label on the strip)'
        rows.append((label_tag, z['EC'], z['C']))
        if key[1] in RECORD_REVIEW:
            review[tag + ' T'] = review[label_tag] = RECORD_REVIEW[key[1]]
    if 'Z' in z: rows.append((tag + ' Q (source, English) and Z (my Chinese)', c['Q'], z['Z']))
    else: rows.append((tag + ' E (the core\'s English, not shown) and Q (source, Chinese, shown)', c.get('E', ''), c['Q']))
n_rec = len(rows)

# ---------- the two built pages, element by element ----------
KINDS = [  # name, CSS selector, what to take ('text' or an attribute)
    ('page title', 'title', 'text'), ('line above the headline', '.eyebrow', 'text'), ('headline', 'h1', 'text'), ('deck', '.deck', 'text'),
    ('key', '.key li span', 'text'), ('panel title', '.card h2', 'text'), ('panel subtitle', '.card .sub', 'text'), ('hint', '.hint', 'text'),
    ('strip: title', 'svg title', 'text'), ('strip: description', 'svg desc', 'text'), ('strip: row, who', 'svg .who', 'text'), ('strip: row, what', 'svg .what', 'text'),
    ('strip: tick', 'svg .tick', 'text'), ('strip: note', 'svg .eranote', 'text'), ('strip: flag', 'svg .flagt', 'text'),
    ('H200 bars: label', '.bar-lab', 'text'), ('H200 bars: value', '.bar-track b', 'text'), ('H200 bars: note', '.bar-note', 'text'),
    ('share: label', '.sh-lab', 'text'), ('share: key', '.sh-keys span', 'text'), ('share: caption', '.sh-cap', 'text'),
    ('revenue: sentence', '.revcard .big', 'text'), ('revenue: chart read aloud', '.rev', 'aria-label'), ('revenue: bar', '.rv', 'title'), ('revenue: month', '.rv span', 'text'), ('revenue: note', '.revwrap .fine', 'text'),
    ('31 governments: bar read aloud', '.pv-bar', 'aria-label'), ('31 governments: key', '.pv-keys span', 'text'), ('31 governments: row', 'table.pv tr', 'text'),
    ('line on paper: row', '.pp', 'text'), ('line on paper: other policies', '.paper > .fine', 'text'),
    ('vouchers: key', '.vkey span', 'text'), ('vouchers: group', '.vgrp h3', 'text'), ('vouchers: sub-group', '.vgrp h4', 'text'), ('vouchers: row', '.vr:not(.axis) .vlab', 'text'), ('vouchers: row note', '.vr:not(.axis) .vnote', 'text'), ('vouchers: row read aloud', '.vr:not(.axis) .vt', 'aria-label'),
    ('vouchers: one-rate label', '.vn.side', 'text'), ('vouchers: note', '.vf', 'text'),
    # round 9 (Nov 25, 2026): the compact list of one-rate rules and its lettered notes, drawn since voucher round 5, were not in this
    # sheet. Its explanation and headings pair by position; the rules and the notes pair by the saved copy each rule links (below),
    # because the two builders order the list and assign the letters each in its own way.
    ('vouchers: one-rate list, explanation', '.vexpl', 'text'), ('vouchers: one-rate list, heading', '.vmh', 'text'),
    ('inside Beijing: column', '.bcol h4', 'text'), ('inside Beijing: body', '.bcol li > span:first-child', 'text'), ('inside Beijing: note', '.row.b .card:nth-child(2) > .fine', 'text'),
    ('records: column', '.lcol h3', 'text'), ('note', '.notes li', 'text'), ('strip: scroll area read aloud', '.scroll', 'aria-label'),
]
# round 14 (Nov 26, 2026): a record mark inside an element (a.p, the circled record number, as beside each H200 bar label) is
# written as " [record mark N] ", never run into the words before it: a reader took the bar label's "by July" and its mark 31
# for "by July 31". GRAB_PLAIN is the old reading, kept only for the control below.
GRAB = """(kinds) => kinds.map(([name, sel, what]) => [...document.querySelectorAll(sel)].map(el => {
  if (what !== 'text') return (el.getAttribute(what) || '').replace(/\\s+/g, ' ').trim();
  const c = el.cloneNode(true); c.querySelectorAll('a.p[data-n]').forEach(a => a.replaceWith(' [record mark ' + a.dataset.n + '] '));
  return (c.textContent || '').replace(/\\s+/g, ' ').trim(); }))"""
GRAB_PLAIN = """(sel) => [...document.querySelectorAll(sel)].map(el => (el.textContent || '').replace(/\\s+/g, ' ').trim())"""
GRAB_VM = """() => [[...document.querySelectorAll('.vm')].map(vm => {
    const a = vm.querySelector('.vml .srcn'), f = vm.querySelector('.vml .vfl'), t = vm.querySelector('.vmt'), l = vm.querySelector('.vml');
    const rate = vm.querySelector('.vmp').textContent.trim();
    return {href: a ? a.getAttribute('href') : '', letter: f ? f.textContent.trim() : '', aria: t ? (t.getAttribute('aria-label') || '') : '',
            lab: l ? l.textContent.replace(/\\s+/g, ' ').trim() + ' | ' + rate : '', place: l && l.firstChild ? l.firstChild.textContent.trim() : ''}; }),
  [...document.querySelectorAll('.vfoot p')].map(p => { const b = p.querySelector('b');
    return {letter: b ? b.textContent.trim() : '', text: p.textContent.replace(/\\s+/g, ' ').trim()}; })]"""
vm, plain = [], []
with sync_playwright() as p:
    br = p.chromium.launch(); got = []
    for page in (CORE_PAGE, ZH_PAGE):
        pg = br.new_context(viewport={'width': 1280, 'height': 900}).new_page(); pg.goto(page.as_uri()); pg.wait_for_timeout(400)
        got.append(pg.evaluate(GRAB, [list(k) for k in KINDS]))
        vm.append(pg.evaluate(GRAB_VM))
        plain.append(pg.evaluate(GRAB_PLAIN, '.bar-lab'))
    br.close()
# round 14: no record number runs into a bar label's words, on either page; control: the old reading of the same labels does run
# them together ("by July 31"), so the check can fail
_bars = [got[i][[k[0] for k in KINDS].index('H200 bars: label')] for i in (0, 1)]
for labs, old in zip(_bars, plain):
    assert len(labs) == len(old) and all(re.search(r'\[record mark \d+\]$', x) for x, y in zip(labs, old) if x != y), 'a bar label\'s record mark is not set apart'
assert any(re.search(r'July \d+$', y) for y in plain[0]) and not any(re.search(r'July \d+$', x) for x in _bars[0]), 'control: the old reading did not join a mark to "July", or the new one still does'
n_marks = sum(len(re.findall(r'\[record mark \d+\]', x)) for page in got for kind in page for x in kind)
for (name, sel, what), a, b in zip(KINDS, *got):
    a, b = [x for x in a if x], [x for x in b if x]
    assert a and len(a) == len(b), f'{name} ({sel}): {len(a)} on the core page, {len(b)} on the Chinese page'
    for i, (x, y) in enumerate(zip(a, b), 1):
        if x != y or CJK.search(y):
            tag = f'page: {name}' + (f' {i}' if len(a) > 1 else '')
            rows.append((tag, x, y))
            if name == 'note' and i in NOTE_REVIEW:
                review[tag] = NOTE_REVIEW[i]
# round 9: the one-rate rules, paired by the address of the saved copy each links; the lettered notes, by the rules they are attached to
(en_r, en_n), (zh_r, zh_n) = vm
pair_ok = lambda er, zr: bool(er) and len({r['href'] for r in er}) == len(er) == len(zr) and {r['href'] for r in er} == {r['href'] for r in zr}
assert pair_ok(en_r, zh_r), f'one-rate rules: {len(en_r)} on the core page, {len(zh_r)} on the Chinese page, or their linked copies differ'
_bad = [dict(r) for r in zh_r]; _bad[0]['href'] += '#control'
assert not pair_ok(en_r, _bad), 'control failed: a rule linking another copy was not caught'
ke, kz = {r['href']: r for r in en_r}, {r['href']: r for r in zh_r}
for i, r in enumerate(en_r, 1):
    z = kz[r['href']]
    rows.append((f'page: vouchers: one-rate rule {i} (paired by its linked copy)', r['lab'], z['lab']))
    rows.append((f'page: vouchers: one-rate rule {i} read aloud', r['aria'], z['aria']))
letters = {}
for h, r in ke.items():
    if r['letter'] or kz[h]['letter']: letters.setdefault(r['letter'], set()).add(kz[h]['letter'])
assert all(len(v) == 1 and '' not in v for v in letters.values()) and '' not in letters and len({next(iter(v)) for v in letters.values()}) == len(letters), f'lettered notes do not pair one to one: {letters}'
ne, nz = {n['letter']: n['text'] for n in en_n}, {n['letter']: n['text'] for n in zh_n}
assert set(ne) == set(letters) and set(nz) == {next(iter(v)) for v in letters.values()}, f'a lettered note is attached to no one-rate rule: {sorted(ne)} {sorted(nz)} {letters}'
starts = lambda note, le, places: any(note.startswith(f'{le} {pl}') for pl in places)      # a note opens with its letter and its rule's place
for le in sorted(ne):
    lz = next(iter(letters[le]))
    pe = {ke[h]['place'] for h in ke if ke[h]['letter'] == le}; pz = {kz[h]['place'] for h in kz if kz[h]['letter'] == lz}
    assert starts(ne[le], le, pe) and starts(nz[lz], lz, pz), f'note {le} / {lz} does not open with its rule\'s place: {ne[le][:40]} | {nz[lz][:40]} | {pe} {pz}'
    rows.append((f'page: vouchers: lettered note {le} (Chinese page: {lz})', ne[le], nz[lz]))
_le = sorted(ne)[:2]
assert len(_le) == 2 and not starts(ne[_le[0]], _le[0], {ke[h]['place'] for h in ke if ke[h]['letter'] == _le[1]}), 'control failed: a note paired with another rule\'s place passed'
n_page = len(rows) - n_rec

# Saved wording added for the current source attributions. Chinese originals are presented verbatim.
checks = (
    ('cn-ga31-cnpress2ap3-23', '发布机构： 安徽宿州高新技术产业开发区管委会', '发布机构： 安徽宿州高新技术产业开发区管委会'),
    ('cn-ga31-msspostsp2-38', '全国网络安全标准化技术委员会秘书处', '全国网络安全标准化技术委员会秘书处'),
    ('cn-tolerate-ftaug26', 'according to two people with knowledge of the matter.', '据两名知情人士透露。'),
)
zh_checks = set((F / 'figure_data.txt').read_text(encoding='utf-8').splitlines())
for sid, exact, rendered in checks:
    line = f'! {sid} | {exact}'
    assert line in core_lines and line in zh_checks, f'source check is missing: {sid}'
    rows.append((f'checked source passage [{sid}]', exact, rendered))

# ---------- Chinese page only, and the pop-up ----------
zt, et = (F / 'template.html').read_text(encoding='utf-8'), (EN / 'template.html.copy').read_text(encoding='utf-8')
m = re.search(r'<p class="draft">(.*?)</p>', zt, re.S); assert m
rows.append(('page (Chinese page only): draft note under the key', '', re.sub(r'<[^>]+>', '', m.group(1))))
assert "'In our English: '" in et and "'本页中文译文：'" in zt and "'英文原文：“'" in zt and "'原文：“'" in zt, 'the pop-up labels changed: update this row'
rows.append(('pop-up labels. Core page: its English for a Chinese source, no quote marks. Chinese page: my Chinese for an English source, no quote marks, then the source\'s own words in quote marks; a Chinese source shows its own words only',
             'In our English: ', '本页中文译文： (then 英文原文：“...”); a Chinese source: 原文：“...”'))
zb, eb = (F / 'cn_figure_build.py').read_text(encoding='utf-8'), (EN / 'cn_figure_build.py').read_text(encoding='utf-8')
for u, v in (('On the record', '有公开记录'), ('Press report, unnamed sources', '媒体报道，未具名消息人士'), ('aria-label="record ', 'aria-label="第')):
    assert u in eb and v in zb, (u, v)
    rows.append(('pop-up and marks: fixed words', u, v))

with open(F / 'pairs_for_review.tsv', 'w', encoding='utf-8') as fh:
    fh.write('where\tEnglish (the core figure)\tChinese\tnative review (core batch 17)\n')
    for where, english, chinese in rows:
        fields = where, english, chinese, review.get(where, '')
        fh.write('\t'.join(field.replace('\t', ' ').replace('\n', ' ') for field in fields) + '\n')
print(f'{len(review)} changed pairs flagged for native review')
print(f'{len(rows)} pairs written to {F / "pairs_for_review.tsv"}: {n_rec} from the records, {n_page} from the two pages ({len(KINDS)} kinds of element, equal counts on both), {len(rows) - n_rec - n_page} others; record marks set apart as [record mark N]: {n_marks} on the two pages')
