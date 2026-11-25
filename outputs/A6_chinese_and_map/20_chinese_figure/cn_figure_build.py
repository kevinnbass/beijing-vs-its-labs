"""Build the Chinese-language version of the figure "Beijing vs. its labs" (China chip-policy project, output idea 20).

Round 4: adapted from the core's builder as rebuilt on Nov 23, 2026 (scripts/cn_figure_build.py; an
unchanged copy is in english_originals/). Everything it writes is in this folder; the core's files are only read.

Run: python3 -I make_inputs.py                                           first: writes figure_data.txt and template.html
     python3 -I cn_figure_build.py                                       checks every quotation, writes the page
     python3 -I cn_figure_build.py --png     the same, then exports PNG images of it
Reads figure_data.txt and template.html (this folder) and, like the core's builder, the project's tables
(research/cn_chip_policy_20261120/tables/: house_licence_table.tsv, provinces_31.tsv, chip_evaluations.tsv,
state_media_items.tsv). Nothing is written unless:
  1. every "Q" and "!" line is found in its saved copy (research/primary/<id>), as in the core's builder;
  2. every pair of quote marks in a T or C line, and in the finished page, holds words that are part of a checked
     Q or ! line (so quote marks hold only a source's exact words, never my Chinese rendering of English);
  3. every record whose Q is English has a Z line (my Chinese rendering) and no record whose Q is Chinese has one;
  4. scripts/cn_has.py passes on quotes.tsv (written here from the Q and ! lines);
  5. the panels name the same saved ids, in the same order, and the same voucher rates as the core's builder.
Writes: beijing_vs_labs_zh.html, figure_events_zh.tsv, quotes.tsv and, with --png, beijing_vs_labs_zh_*.png.
The page is a build product: a rebuild replaces it. Numbers on the page come from the data file, the tables and this
script only. Before the page is called done: scripts/render_and_look.py (look at every screenshot).
Round 8 (core edit 7, Nov 25, 2026), as the core's builder now does: records are numbered by date, Beijing's rows first,
then the companies'; a block with an "N" line keeps the number given there (record 62, added after the English figure was
made public, so that no record changed its number). The template body types that number in its records note; the build
stops if the note does not name each fixed number.
"""
import ast, html, json, re, subprocess, sys
from collections import Counter
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

F = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[5]            # .
assert (ROOT / 'scripts' / 'cn_srclib.py').exists(), ROOT
sys.path.insert(0, str(ROOT / 'scripts'))
import cn_srclib as L   # noqa: E402

TB = ROOT / 'research/cn_chip_policy_20261120/tables'
LANES = {'BH': ('北京', '限制英伟达', 'away'), 'BL': ('北京', '放行英伟达', 'toward'),
         'CN': ('企业', '争取英伟达芯片', 'toward'), 'CH': ('企业', '转向国产芯片', 'away')}
ORDER = ['BH', 'BL', 'CN', 'CH']
OUT = 'beijing_vs_labs_zh'
esc = html.escape
CJK = re.compile(r'[一-鿿]')


def smart(s):
    return re.sub(r'"([^"]*)"', '“\\1”', s).replace("'", '’')


def fmt(d): return f'{d.year}年{d.month}月{d.day}日'


def url(sid):
    u = L.url_of(sid)
    assert u, f'no address to link for {sid}'
    return esc(u, quote=True)


def table(name):
    """Rows of a tab-separated table in the project's tables folder, as dicts (lines starting # are comments)."""
    lines = [l for l in (TB / name).read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    head = lines[0].split('\t')
    return [dict(zip(head, l.split('\t'))) for l in lines[1:]]


def load():
    evs, checks, cur = [], [], None
    for n, ln in enumerate((F / 'figure_data.txt').read_text(encoding='utf-8').splitlines(), 1):
        if not ln.strip() or ln.startswith('#'): continue
        if ln.startswith('@ '):
            _, lane, kind, d, dl, sid = ln.split()
            assert lane in LANES and kind in ('doc', 'rec', 'press'), (n, ln)
            cur = dict(lane=lane, kind=kind, date=date.fromisoformat(d), dl=None if dl == '-' else dl.replace('_', ' '), sid=sid, T='', S='', Q='', E='', U='', C='', Z='', rawT='', rawC='', N='')
            evs.append(cur)
        elif ln.startswith('! '):
            sid, q = ln[2:].split(' | ', 1); checks.append((sid.strip(), q.strip()))
        elif ln[:2] in ('T ', 'S ', 'Q ', 'E ', 'U ', 'C ', 'Z ', 'N '):
            if ln[0] in 'TC': cur['raw' + ln[0]] = ln[2:].strip()
            cur[ln[0]] = smart(ln[2:].strip()) if ln[0] in 'TSC' else ln[2:].strip()
        else: sys.exit(f'line {n} not understood: {ln[:60]}')
    return evs, checks


def within(seg, verified):
    """True when the quoted words are part of a checked quotation (spacing, case and quote style ignored)."""
    s = L.squash(seg)
    return bool(s) and any(s in v for v in verified)


def verify(evs, checks):
    bad = []
    for e in evs:
        if not (e['T'] and e['S'] and e['Q']): bad.append(f"incomplete block {e['sid']}")
        elif not L.has(e['Q'], e['sid']): bad.append(f"NOT FOUND in {e['sid']}: {e['Q'][:70]}")
        if CJK.search(e['Q']) and e['Z']: bad.append(f"Z line on a Chinese source {e['sid']}")
        if not CJK.search(e['Q']) and not e['Z']: bad.append(f"no Z line (Chinese rendering) for the English source {e['sid']}")
        if '"' in e['Z'] or '“' in e['Z']: bad.append(f"quote marks inside a Z line {e['sid']}")
        if '"' in e['S'] or '“' in e['S']: bad.append(f"quote marks inside an S line {e['sid']}")
    for sid, q in checks:
        if not L.has(q, sid): bad.append(f'NOT FOUND in {sid}: {q[:70]}')
    assert not L.has('this sentence was never written by anyone at all', evs[0]['sid']), 'the control quotation was found: the check cannot fail'
    # quote marks in a T or C line hold only words that are part of a checked quotation of the same saved id
    for e in evs:
        own = [L.squash(x['Q']) for x in evs if x['sid'] == e['sid']] + [L.squash(q) for sid, q in checks if sid == e['sid']]
        for raw in (e['rawT'], e['rawC']):
            assert raw.count('"') % 2 == 0, f"odd number of quote marks: {raw}"
            for seg in re.findall(r'"([^"]*)"', raw):
                if not within(seg, own): bad.append(f"quoted words not part of a checked quotation of {e['sid']}: {seg}")
    assert not within('这句话谁也没有写过', [L.squash(e['Q']) for e in evs]), 'the control for quoted words passed: the check cannot fail'
    return bad


def page_quotes_ok(page, evs, checks):
    """Every pair of curly quote marks in the page's visible text must hold words that are part of a checked quotation."""
    verified = [L.squash(e['Q']) for e in evs] + [L.squash(q) for _, q in checks]
    text = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', page)
    text = re.sub(r'(?s)<!--.*?-->', ' ', text)
    text = html.unescape(re.sub(r'(?s)<[^>]+>', ' ', text))
    assert text.count('“') == text.count('”'), 'unbalanced curly quote marks in the page text'
    segs = re.findall(r'“([^“”]*)”', text)
    return segs, [s for s in segs if not within(s, verified)]


def mirror_check():
    """The panels here must name the same saved ids, in the same order, as the core's builder, and the same voucher
    rows (rates and ids); the nine revenue figures must be the core's. Read from the two source files."""
    ID = re.compile(r"""['"]((?:cn|man|ms)-[a-z0-9-]+)['"]""")

    def funcs(p):
        src = p.read_text(encoding='utf-8'); tree = ast.parse(src)
        return {n.name: ast.get_source_segment(src, n) for n in tree.body if isinstance(n, ast.FunctionDef)}
    en, zh = funcs(F / 'english_originals' / 'cn_figure_build.py'), funcs(Path(__file__))
    for fn in ('bars', 'revenue', 'provinces', 'paper', 'vouchers', 'bodies', 'hfac', 'evaluations', 'state_media'):
        a, b = ID.findall(en[fn]), ID.findall(zh[fn])
        assert a == b, f'{fn}(): the saved ids are not the core\'s, in its order:\n core {a}\n here {b}'
    rate = re.compile(r", (\d+), (\d+), '((?:cn|man|ms)-[a-z0-9-]+)'")
    assert rate.findall(en['vouchers']) == rate.findall(zh['vouchers']) and len(rate.findall(zh['vouchers'])) == 19, 'the voucher rows are not the core\'s'
    num = re.compile(r"\('(\d{4}-\d\d-\d\d)', ([\d \-]+),")
    assert num.findall(en['revenue']) == num.findall(zh['revenue']) and len(num.findall(zh['revenue'])) == 9, 'the revenue figures are not the core\'s'
    for fn in ('hfac', 'evaluations', 'state_media'):          # the counting code itself: the same asserts
        a, b = re.findall(r'assert [^\n]+', en[fn]), re.findall(r'assert [^\n]+', zh[fn])
        assert [x.split(', ')[0] for x in a] == [x.split(', ')[0] for x in b], f'{fn}(): the asserts differ from the core\'s'


def number(evs):
    """Number the records by date, Beijing's rows first and then the companies', except a record with an "N" line, which
    keeps the number given there (core edit 7, Nov 25, 2026: a record added after the figure was made public takes the
    next free number, so no earlier record changes its number). Returns each side's records by date, fixed ones included,
    for the lists under the chart. Copied from the core's builder of edit 7 (english_originals/cn_figure_build.py)."""
    free = [e for e in evs if not e['N']]
    b = sorted([e for e in free if e['lane'][0] == 'B'], key=lambda e: e['date'])
    c = sorted([e for e in free if e['lane'][0] == 'C'], key=lambda e: e['date'])
    for i, e in enumerate(b + c, 1): e['n'] = i
    for e in evs:
        if e['N']: e['n'] = int(e['N'])
    assert sorted(e['n'] for e in evs) == list(range(1, len(evs) + 1)), 'the record numbers do not run from 1 to the number of records'
    assert all(e['n'] > len(free) for e in evs if e['N']), 'a fixed number falls among the numbers given by date'
    for e in evs:
        e['when'] = e['dl'] or fmt(e['date']); e['url'] = e['U'] or L.url_of(e['sid'])
        e['dir'] = LANES[e['lane']][2]; e['solid'] = e['kind'] != 'press'
    b = sorted([e for e in evs if e['lane'][0] == 'B'], key=lambda e: e['date'])
    c = sorted([e for e in evs if e['lane'][0] == 'C'], key=lambda e: e['date'])
    return b, c


# ---------- the dated strip (SVG) ----------
W, GL, GR = 1400, 216, 26
A, BK, C = date(2023, 1, 1), date(2025, 1, 1), date(2026, 12, 1)
FRAC, R, PITCH = 0.15, 10, 23


def X(d):
    x0, x1 = GL, W - GR
    if d < BK: return x0 + (d - A).days / (BK - A).days * FRAC * (x1 - x0)
    return x0 + FRAC * (x1 - x0) + (d - BK).days / (C - BK).days * (1 - FRAC) * (x1 - x0)


def strip(evs):
    top, y, out, lanes = 50, 50, [], {}
    for k in ORDER:
        placed = []
        for e in sorted([e for e in evs if e['lane'] == k], key=lambda e: e['date']):
            x, lv = X(e['date']), 0
            while any(l == lv and abs(x - px) < PITCH + 1 for px, l in placed): lv += 1   # PITCH + 1: rings 22.5 px wide never touch
            placed.append((x, lv)); e['x'], e['lv'] = x, lv
        h = (max(l for _, l in placed) + 1) * PITCH + 16
        lanes[k] = (y, h); y += h + (16 if k == 'BL' else 0)
    bottom = y
    H = bottom + 40
    xb = X(BK)
    out.append(f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="strip-t strip-d"><title id="strip-t">按日期排列的记录，2023年至2026年11月</title>'
               f'<desc id="strip-d">每个带编号的圆点是一条有日期的记录，逐条列在图的下方。共四行：北京限制英伟达，北京放行英伟达，企业争取英伟达芯片，企业转向国产芯片。</desc>')
    out.append(f'<rect class="era" x="{GL}" y="{top}" width="{xb - GL:.1f}" height="{bottom - top}"/>')
    ticks = [(date(2023, 1, 1), '2023年'), (date(2024, 1, 1), '2024年')] + [(date(y_, m, 1), (f'{y_}年{m}月' if m == 1 else f'{m}月')) for y_ in (2025, 2026) for m in (1, 4, 7, 10)]
    for d, lab in ticks:
        x = X(d); strong = d.month == 1
        out.append(f'<line class="grid{" yr" if strong else ""}" x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom + 6}"/><text class="tick{" yr" if strong else ""}" x="{x + 4:.1f}" y="{bottom + 22}">{lab}</text>')
    out.append(f'<text class="eranote" x="{GL + 6}" y="{bottom + 37}">2023年和2024年画得较窄</text>')
    # The third flag: Nvidia, Nov 17, 2026: "we are no longer shipping licensed Hopper Data Center products to China";
    # Reuters: "The Hopper family includes the H200" (both "!" lines). Why it stopped is not said here.
    for d, lab, anchor in ((date(2025, 7, 15), '2025年7月 · 美国重新批准H20对华销售', 'end'), (date(2025, 12, 8), '2025年12月8日 · 美国允许对华销售H200', 'start'), (date(2026, 11, 17), '2026年11月17日 · 英伟达停止H200发货', 'end')):
        x = X(d); dx = -7 if anchor == 'end' else 7
        out.append(f'<line class="flag" x1="{x:.1f}" y1="14" x2="{x:.1f}" y2="{bottom}"/><text class="flagt" x="{x + dx:.1f}" y="26" text-anchor="{anchor}">{esc(lab)}</text>')
    for k in ORDER:
        y0, h = lanes[k]; who, what, dr = LANES[k]
        out.append(f'<line class="lane" x1="0" y1="{y0 + h}" x2="{W}" y2="{y0 + h}"/>')
        cy = y0 + h / 2
        out.append(f'<text class="who" x="10" y="{cy - 4:.1f}">{who}</text><circle class="sw {dr}" cx="16" cy="{cy + 11:.1f}" r="5"/><text class="what" x="28" y="{cy + 15:.1f}">{what}</text>')
    y0, h = lanes['BL']
    out.append(f'<line class="band" x1="0" y1="{y0 + h + 8}" x2="{W}" y2="{y0 + h + 8}"/>')
    for e in sorted(evs, key=lambda e: e['n']):
        y0, h = lanes[e['lane']]
        cy = y0 + h - 8 - R - e['lv'] * PITCH
        out.append(f'<a href="#e{e["n"]}" class="pin {e["dir"]} {"solid" if e["solid"] else "hollow"}" data-n="{e["n"]}" data-tip="1" aria-label="{e["n"]}. {esc(e["when"])}：{esc(e["T"], quote=True)}">'
                   f'<circle cx="{e["x"]:.1f}" cy="{cy:.1f}" r="{R}"/><text x="{e["x"]:.1f}" y="{cy + 4:.1f}">{e["n"]}</text></a>')
        if e['C']:                                         # a short label beside the mark: "start|end dx dy words"
            anchor, dx, dy, words = e['C'].split(' ', 3)
            out.append(f'<text class="call" x="{e["x"] + float(dx):.1f}" y="{cy + float(dy):.1f}" text-anchor="{anchor}">{e["n"]} · {esc(words)}</text>')
    out.append('</svg>')
    return '\n'.join(out)


# ---------- panels ----------
def pin(e, tip=True):
    return f'<a href="#e{e["n"]}" class="p {e["dir"]} {"solid" if e["solid"] else "hollow"}" data-n="{e["n"]}"{" data-tip=1" if tip else ""} aria-label="第{e["n"]}条记录">{e["n"]}</a>'


def by(evs, sid, lane=None):
    m = [e for e in evs if e['sid'] == sid and (lane is None or e['lane'] == lane)]
    assert len(m) == 1, (sid, lane, len(m)); return m[0]


def hfac():
    """The House committee's table (by its summary, a BIS summary; status as of May 11, 2026): sums by exporter, status and
    location, made here from tables/house_licence_table.tsv, exactly as the core's builder makes them. The totals must
    equal the summary's own figures, which "!" lines check in the saved summary."""
    rows = [dict(exp=r['exporter'], con=r['consignee'], chips=int(r['chip_count'].replace(',', '')), status=r['status'], loc=r['location'])
            for r in table('house_licence_table.tsv')]

    def s(**k):
        sel = [r for r in rows if all(r[a] == b for a, b in k.items())]
        return sum(r['chips'] for r in sel), len(sel)
    t = dict(all=s(), appr=s(status='Approved, not shipped'), appr_nv=s(status='Approved, not shipped', exp='Nvidia'),
             appr_amd=s(status='Approved, not shipped', exp='AMD'), rwa=s(status='RWA'), rwa_nv=s(status='RWA', exp='Nvidia'),
             rwa_amd=s(status='RWA', exp='AMD'))
    abroad = [r for r in rows if r['loc'] != 'China']
    t['abroad'] = (sum(r['chips'] for r in abroad), len(abroad))
    t['abroad_places'] = sorted({r['loc'] for r in abroad})
    assert t['all'] == (3_444_160, 54) and t['appr'] == (879_868, 21), t          # the summary's own figures ("!" lines)
    assert t['appr_nv'][0] + t['appr_amd'][0] == t['appr'][0] and t['rwa_nv'][0] + t['rwa_amd'][0] == t['rwa'][0], t
    assert abroad and all(r['status'] == 'RWA' and r['exp'] == 'Nvidia' for r in abroad), 'an application abroad is not an Nvidia RWA'
    assert all(re.search(r'bytedance|byteplus|tiktok|alibaba', r['con'], re.I) for r in abroad), [r['con'] for r in abroad]
    assert 2 * t['rwa'][0] > t['all'][0], 'RWA is not more than half of the chips'
    return t


def bars(evs):
    h = hfac()
    f = lambda v: f'{v:,}'
    zh = {'Indonesia': '印度尼西亚', 'Malaysia': '马来西亚', 'Thailand': '泰国'}
    places = '、'.join(zh[p] for p in h['abroad_places'][:-1]) + '和' + zh[h['abroad_places'][-1]]
    rows = [  # label, value text, chips (for the width), class, note, events
        ('中国企业为2026年订购', '超过200万枚', 2_000_000, 'toward', '路透社，2025年12月31日', [by(evs, 'cn-labs-h200-two-million-202512-relay1-wayback')]),
        ('华盛顿已批准：以英伟达为出口商的申请', f(h['appr_nv'][0]) + '枚', h['appr_nv'][0], 'us',
         f'共{h["appr_nv"][1]}份申请，截至2026年5月11日均标为“Approved, not shipped”（已批准、未发货）。加上AMD的同类芯片'
         f'（{f(h["appr_amd"][0])}枚，{h["appr_amd"][1]}份申请），合计{f(h["appr"][0])}枚。表格“H200 License and Equivalent Application Status as of May 11, 2026”（截至2026年5月11日的H200许可及同类申请状态），'
         '由众议院外交事务委员会于2026年11月19日公布；各项合计为本页所算', []),   # touch-up 6b sync (Nov 24, 2026): the table by its title, as the English builder now names it
        ('华盛顿未予处理即退回：以英伟达为出口商的申请', f(h['rwa_nv'][0]) + '枚', h['rwa_nv'][0], 'us',
         f'共{h["rwa_nv"][1]}份申请，其中包括收货方在{places}的全部{h["abroad"][1]}份（{f(h["abroad"][0])}枚），收货方名称带有ByteDance、BytePlus、TikTok和Alibaba字样。'
         f'加上AMD的{h["rwa_amd"][1]}份，在表内{f(h["all"][0])}枚芯片中占{f(h["rwa"][0])}枚。表格没有说明原因。同一表格', []),
        ('北京方面有条件批准', '超过40万枚', 400_000, 'toward', '对象是字节跳动、阿里巴巴和腾讯。路透社，2026年1月28日', [by(evs, 'ms-bj-20260128-h200-nod-standard')]),
        ('到7月，北京方面考虑放行的总量', '不到20万枚', 200_000, 'toward', 'The Information，经路透社转述，2026年7月8日', [by(evs, 'cn-acts-reuters-ti-cap-20260708-relay1')]),
        ('已到报道点名的两家买方手中', '各约1万枚', 20_000, 'toward', '字节跳动和腾讯（英国《金融时报》，经路透社转述，2026年8月18日）；到11月已是数家企业（路透社，2026年11月5日）', [by(evs, 'cn-tolerate-reutersaug26-relay1-wayback')]),
        ('存放在香港，等待运往中国', '约60万枚', 600_000, 'away', '北京方面迟迟未批准大规模进口（原文：“withholds approval for large-scale imports”）。路透社，2026年11月5日', [by(evs, 'cn-clips-evidence-1')]),
    ]
    out = ['<div class="bars">']
    for lab, val, n, cls, note, es in rows:
        head, last = lab[:-3], lab[-3:]            # the last characters and the marks stay on one line
        lab_h = f'{esc(head)}<span class="nw">{esc(last)}{chr(160)}{"".join(pin(e) for e in es)}</span>' if es else esc(lab)
        out.append(f'<div class="bar-row"><div class="bar-lab">{lab_h}</div>'
                   f'<div class="bar-track"><i class="{cls}" style="--f:{n / 2_000_000:.4f}"></i><b>{esc(val)}</b></div>'
                   f'<div class="bar-note">{esc(note)}</div></div>')
    out.append('</div>')
    return '\n'.join(out), h


def share():
    rows = [('美国收紧出口管制之前', [('toward', 95, '英伟达约95%'), ('rest', 5, '')], '英伟达：约占中国先进芯片市场的95%。', '路透社，2026年5月14日'),
            ('2025年', [('toward', 55, '英伟达55%'), ('other', 4, ''), ('away', 41, '中国厂商41%')],
             '按AI加速卡出货量计：英伟达55%，AMD 4%，中国厂商41%。燧原科技的招股说明书依据IDC数据和自身销量，称英伟达约220万张，总量约400万张。',
             'IDC数据，据路透社报道，2026年4月1日；燧原科技招股说明书，2026年9月'),
            ('2026年1月至6月', [('toward', 34, '英伟达34%'), ('away', 28, '华为28%'), ('rest', 38, '其他38%')], '英伟达34%，华为28%。其余38%中，报道点名平头哥7%、寒武纪5%、昆仑芯4%、海光3%；剩下的19%（本页相减所得）没有细分。', 'IDC数据，据路透社报道，2026年10月13日')]
    out = ['<div class="share">']
    for lab, segs, cap, src in rows:
        out.append(f'<div class="sh-row"><div class="sh-lab">{esc(lab)}</div><div class="sh-bar" role="img" aria-label="{esc(cap, quote=True)}">' +
                   ''.join(f'<i class="{c}" style="flex:{w}"></i>' for c, w, _ in segs) + '</div>'
                   '<div class="sh-keys">' + ''.join(f'<span style="flex:{w}">{esc(t)}</span>' for _, w, t in segs) + '</div>'
                   f'<div class="sh-cap">{esc(cap)} <span class="srcn">{esc(src)}</span></div></div>')
    out.append('<div class="sh-cap">灰色是AMD（2025年为4%）。斜线部分是报道没有细分的部分。</div>')
    out.append('</div>')
    return '\n'.join(out)


def revenue():
    """Nvidia's revenue from direct customers headquartered in China and Hong Kong, by quarter, in millions of dollars.
    Every number is a cell of a filing's own table (checked by the "!" lines at the end of figure_data.txt); the two
    fourth quarters are a year's figure less its first nine months, computed here. The same figures as the core's."""
    q = [('2024-10-27', 8142, '', 'man-ms-sec-10q-2025-10'),
         ('2025-01-26', 25048 - 17230, '全年25,048减去前九个月的17,230', 'man-ms-sec-10k-fy2026'),
         ('2025-04-27', 9659, '', 'man-ms-sec-10q-2026-04'),
         ('2025-07-27', 3985, '', 'man-ms-sec-10q-2026-07'),
         ('2025-10-26', 2973, '', 'man-ms-sec-10q-2025-10'),
         ('2026-01-25', 19677 - 16617, '全年19,677减去前九个月的16,617', 'man-ms-sec-10k-fy2026'),
         ('2026-04-26', 4550, '', 'man-ms-sec-10q-2026-04'),
         ('2026-07-26', 7880, '', 'man-ms-sec-10q-2026-07'),
         ('2026-10-25', 11050, '', 'ms-p3-nvda-8k-20261117-pdf')]
    mx = max(v for _, v, _, _ in q)
    bn = lambda v: str((Decimal(v) / 1000).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
    said = '；'.join(f'{fmt(date.fromisoformat(d))}：{v:,}' for d, v, _, _ in q)
    out = [f'<div class="revwrap"><div class="rev" role="img" aria-label="按季度截止日列出，单位百万美元。{esc(said, quote=True)}">']
    for d, v, how, sid in q:
        dt = date.fromisoformat(d)
        tip = f'截至{fmt(dt)}的季度：{v:,}百万美元' + (f'（本页相减所得：{how}）' if how else '')
        out.append(f'<div class="rv" title="{esc(tip, quote=True)}"><b>{bn(v)}{"*" if how else ""}</b><i style="--h:{v / mx:.4f}"></i><span>{dt.month}月<em>{dt.year}</em></span></div>')
    out.append('</div>')
    docs = [('man-ms-sec-10q-2025-10', '截至2025年10月26日的季度'), ('man-ms-sec-10k-fy2026', '截至2026年1月25日的财年'), ('man-ms-sec-10q-2026-04', '截至2026年4月26日的季度'),
            ('man-ms-sec-10q-2026-07', '截至2026年7月26日的季度'), ('ms-p3-nvda-8k-20261117-pdf', '2026年11月17日提交的业绩文件')]
    out.append('<p class="fine">图中月份是季度截止的月份。* 本页相减所得：全年数字减去前九个月。英伟达的报告：' +
               '、'.join(f'<a href="{url(sid)}">{esc(lab)}</a>' for sid, lab in docs) + '。</p>')
    # Nvidia's own words on the latest quarter's licensed sales ("!" lines on cn-o38-nvda-q3fy27-call-transcript-pdf)
    out.append('<p class="fine">关于最近一个季度，英伟达说，获许可的Hopper数据中心产品第三季度对华销售额为24亿美元（原文：“Q3 sales of licensed Hopper Data Center products to China was $2.4 billion”），'
               '并说公司已不再向中国发运这类产品（原文：“we are no longer shipping licensed Hopper Data Center products to China”）'
               f'（<a href="{url("cn-o38-nvda-q3fy27-call-transcript-pdf")}">业绩电话会，2026年11月17日</a>）。它没有说明原因。</p></div>')
    return '\n'.join(out)


def provinces():
    """The 31 provincial-level governments by what their published plans were found to set: counted here from
    tables/provinces_31.tsv, as the core's builder counts them. The eight shares measure different things, so they are
    listed with what each counts, never drawn as one series. Each share's words are a "!" line."""
    pr = table('provinces_31.tsv')
    cnt = Counter(r['result'] for r in pr)
    assert len(pr) == 31 and sum(cnt.values()) == 31 and set(cnt) == {'share', 'plan_no_share', 'account_only', 'not_reached'}, cnt
    zh = {'Jiangsu': '江苏', 'Guangdong': '广东', 'Tianjin': '天津', 'Hebei': '河北', 'Shanghai': '上海', 'Sichuan': '四川', 'Inner Mongolia': '内蒙古', 'Shandong': '山东', 'Tibet': '西藏', 'Xinjiang': '新疆'}
    one = lambda k: [zh[r['government']] for r in pr if r['result'] == k]
    acc, nr = one('account_only'), one('not_reached')
    seg = [('away', cnt['share'], f'{cnt["share"]}个定了占比'), ('rest', cnt['plan_no_share'], f'{cnt["plan_no_share"]}个的规划已读，未定占比'),
           ('other', cnt['account_only'], f'{cnt["account_only"]}个的规划只见于有关报道（{"、".join(acc)}）'),
           ('none', cnt['not_reached'], f'{cnt["not_reached"]}个未能查到（{"、".join(nr)}）')]
    shares = [  # government, share as written, of what and by when, how it is worded or held, saved id
        ('Jiangsu', '70%以上', '新建算力中心的国产算力芯片使用占比，2030年（2025年为50%）', '属“预期性”指标', 'cn-factions-jiangsu-plan'),
        ('Guangdong', '70%', '新增算力中的国产化占比，到2025年底', '用词是“力争”；九个部门的方案', 'cn-o39b-guangdong-yuesuan-2024'),
        ('Tianjin', '超过60%', '全市算力中心的国产算力芯片使用占比，到2026年', '', 'cn-o39-tianjin-plan-2024'),
        ('Hebei', '60%以上', '新增算力基础软硬件设施的“自主可控”比例，到2025年', '河北省政府自己的网页', 'cn-o39-hebei-opinion-2024-wayback'),
        ('Shanghai', '超过50%', '新建智算中心的国产算力芯片使用占比，到2025年', '转载于其他网站的文本', 'cn-policy-shanghai-domestic-target'),
        ('Sichuan', '超过50%', '国产化算力设备占比', '用词是“力争”；转载于其他网站的文本', 'cn-factions-sichuan50'),
        ('Inner Mongolia', '50%以上', '国产化算力占比，到2025年，是该区国家算力枢纽的目标之一', '', 'cn-o39-nmg-plan-pdf-wayback'),
        ('Shandong', '90%', '全省数据中心的国产化算力占比，到2025年', '报纸对规划的报道', 'cn-o39-shandong-network-2022')]
    tab = {r['government']: r['saved_ids'].split()[0] for r in pr if r['result'] == 'share'}
    assert {g: s for g, _, _, _, s in shares} == tab, ('the shares listed are not the table\'s', tab)
    lab = '；'.join(t for _, _, t in seg)
    out = [f'<div class="prov"><div class="pv-bar" role="img" aria-label="31个省级政府：{esc(lab, quote=True)}。">'
           + ''.join(f'<i class="{c}" style="flex:{w}"></i>' for c, w, _ in seg) + '</div><div class="pv-keys">'
           + ''.join(f'<span><i class="k {c}"></i>{esc(t)}</span>' for c, _, t in seg) + '</div>', '<table class="pv"><tbody>']
    for g, sh, what, how, sid in shares:
        out.append(f'<tr><th>{esc(zh[g])}</th><td class="sh">{esc(sh)}</td><td>{esc(what)}{("；" + esc(how)) if how else ""} <a class="srcn" href="{url(sid)}">来源</a></td></tr>')
    out.append('</tbody></table></div>')
    return '\n'.join(out)


def evaluations():
    """AI chips on the state security-and-reliability evaluation lists, counted from tables/chip_evaluations.tsv, as
    the core's builder counts them."""
    rows = [r for r in table('chip_evaluations.tsv') if '人工智能训练推理芯片' in r['category'] and not r['cells'].startswith('序号')]
    lists = sorted({r['page_date'] for r in rows})
    makers = {r['cells'].split(' | ')[2] for r in rows}
    assert lists == ['2026-05-26', '2026-09-20'] and len(rows) == 11 and len(makers) == 8, (lists, len(rows), len(makers))
    return len(rows), len(makers), [date.fromisoformat(d) for d in lists]


def paper(evs):
    n, m, ds = evaluations()
    rows = [('20%', '政府采购中，符合本国产品标准的货物享受的报价扣除；自2026年1月1日起施行，符合该标准的外资企业产品平等参与', '国务院办公厅，2025年9月；财政部，2025年12月', 'cn-policy-domestic-product-standard-2025'),
            (f'全部{n}款', f'通过国家安全可靠测评的AI芯片，全部出自在中国境内注册的厂商，共{m}家（{ds[1].year}年{ds[0].month}月和{ds[1].month}月两批名单）。'
             '只有中国境内注册的实体可以送测；企业自愿申请，测评结果由企业和用户自主选择使用', f'测评中心，{ds[1].year}年{ds[1].month}月', 'cn-le14-itsec-2026-3'),
            ('46家', '美国企业的产品，政府采购人不得采购（不包括在华美资企业）。英伟达、英特尔、AMD、美光和高通不在其列', '财政部，2026年6月22日', 'cn-le14-mof-us-firms-measures-20260622')]
    lst = L.page('cn-le14-mof-us-firms-list-20260622')       # the list read whole: the names in the row are absent; a control is present
    assert 'lockheedmartin' in lst and not any(w in lst for w in ('nvidia', '英伟达', 'intel', '英特尔', 'advancedmicro', 'amd', '超威', 'micron', '美光', 'qualcomm', '高通', '芯片')), 'the list of 46 names a chip maker'
    out = ['<div class="paper">', provinces()]
    for big, txt, when, sid in rows:
        out.append(f'<div class="pp"><b>{esc(big)}</b><span>{esc(txt)} <a class="srcn" href="{url(sid)}">{esc(when)}</a></span></div>')
    out.append('<div class="pp none"><b>没有找到</b><span>在所阅读的政策网页和全国性文件目录中，没有找到公开发布的全国性国产AI芯片占比，也没有找到公开发布的不准购买英伟达芯片的命令。'
               f'有报道称，一份全国性规划草案要求至少80%的核心技术（包括AI芯片）为国产（彭博社，2026年6月，经<a class="srcn" href="{url("cn-le14-tnw-295b-plan-20260609")}">其他媒体转述</a>；消息来自未具名人士，他们说细节可能变化）；'
               '被问到这篇报道时，国家发展改革委没有给出占比，只说“在具体建设过程中，市场力量将起决定性作用”，并表示将“加强统筹协调和政策引导”'
               f'（<a class="srcn" href="{url("cn-le27-ndrc-presser-20260618-json")}">新闻发布会，2026年6月18日：网站的文本文件</a>）。'
               '找到的每一条有约束力的采购规定，针对的都是党政机关、事业单位或财政资金；2023年的美光案（这里最早的一条记录）则针对关键信息基础设施的运营者。</span></div>')
    out.append('</div>')
    return '\n'.join(out)


def vouchers():
    """Local computing vouchers: the general rate a voucher or rental subsidy pays of the bill for rented computing (the
    rate for an ordinary applicant; a higher rate for a named kind of firm, whatever the chip, is in the row's note), for
    home-made computing against other computing, as each rule states it (one measure throughout). The rows, their order and
    their rule for inclusion are the core builder's (mirror_check() compares the rates and saved ids); every rate and date
    is a "!" line of the data. Round 5 (core edit 6, Nov 24, 2026): the four rules found that day which the published rule
    counts (Sichuan, home-made computing only, its text as Jiemian carries it; Wuhu; Suzhou; Tianjin) and Shanghai's
    up to 100% for early-stage and small firms, as the core's builder has them."""
    rows = [  # place, rule (year and month on its page), home-made %, other %, saved id, note
        ('杭州市', (2024, 7), 30, 20, 'cn-counter-b4-2', ''),
        ('浙江省', (2025, 4), 30, 10, 'cn-le25-zhejiang-ai-measures-2025-smartcity', '对发放算力券的地方的指导；自2025年5月31日起实施；转载于其他网站的文本'),
        ('温州市', (2025, 8), 30, 10, 'cn-le15-zj-oss-web1825-e66330', ''),
        ('杭州市滨江区', (2026, 8), 60, 30, 'cn-le15-binjiang-2026-6-keceyun', '载于一家政策网站的文本'),
        ('北京经济技术开发区（是开发区，不是北京市）', (2024, 11), 30, 30, 'cn-le28-etown-29hao-20241126', '取代了2024年3月按40%对30%支付的规定；装国产芯片的服务器另有最高10%的采购支持'),
        ('深圳市龙华区', (2024, 11), 30, 30, 'cn-le28-sz-longhua-2024-20hao', ''),
        ('山西省', (2024, 6), 20, 20, 'cn-o39b-shanxi-measures-2024-jincheng', '国家级项目和大模型企业为30%；自2024年7月起施行'),
        ('深圳市', (2024, 12), 50, 50, 'cn-le28-sz-gxj-2024-13hao', '初创企业为60%；把模型迁移到国产芯片另有支持'),
        ('武汉市', (2025, 2), 50, 50, 'cn-le28-wuhan-2025-3hao', '最高20万元；2026年2月的一项规定对一人AI企业给同样的比例'),
        ('青岛市', (2026, 3), 20, 20, 'cn-le28-qingdao-2026-9hao-smartcity', '与其2025年3月的规定比例相同；转载于其他网站的文本'),
        ('上海市', (2025, 7), 30, 30, 'cn-le15-sheitc-8cea38', '按补早补小原则，对初创和小型企业市区协同给予最多1年、最高100%的租金补贴；建设支持最高10%，只给国产（自主）算力'),
        ('武汉市硚口区', (2025, 8), 50, 50, 'cn-le28-wuhan-qiaokou-2025-1hao', '在市级支持的基础上'),
        ('武汉市洪山区', (2025, 9), 20, 20, 'cn-le28-wuhan-hongshan-2025-2hao', '面向中小企业'),
        ('山东省', (2025, 5), 5, 5, 'cn-le28-shandong-ai-measures-2025-smartcity', '转载于其他网站的文本'),
        ('湖南省', (2025, 10), 30, 30, 'cn-le28-hunan-aiplus-smartcity', '转载于其他网站的文本'),
        ('四川省', (2026, 8), 20, 0, 'cn-ga05-sichuan-compute-net-measures-jiemian', '成立3年内的初创企业30%，人工智能一人公司40%；文本为新闻网站界面新闻所载，无文号、无日期；月份为报道的月份'),
        ('芜湖市', (2026, 7), 25, 25, 'cn-ga04-wh-voucher-rule-2026-24hao', '具身智能等未来产业领域企业45%，算力产业孵化载体内的中小微企业70%'),
        ('苏州市', (2026, 1), 30, 30, 'cn-ga04-sz-suzhou-aiplus-2026-18hao', '面向科技研发企业；按该市自己的解读，自2026年1月31日起施行；其2025年2月的规定为20%'),
        ('天津市', (2025, 5), 10, 10, 'cn-ga04-tj-voucher-rule-sina-20250514', '文本为新浪网一个页面所载，日期为2025年5月14日'),
    ]
    mx = 60
    assert max(max(hm, ot) for _, _, hm, ot, _, _ in rows) <= mx
    only = [r for r in rows if r[3] == 0]                    # a rule that pays for home-made computing only
    ti = [r for r in rows if r[2] != r[3] and r[3] > 0]; one = [r for r in rows if r[2] == r[3]]
    # the count by script of the published rule over both voucher tables (atlas/core_edit/p6_work_4/vcount.py; Nov 24, 2026: 19 counted, 4 tiered, 1 home-made only, 14 one rate)
    assert (len(rows), len(ti), len(only), len(one)) == (19, 4, 1, 14), (len(rows), len(ti), len(only), len(one))
    assert all(hm > ot for _, _, hm, ot, _, _ in ti), 'a rule pays more for other computing'
    key = lambda r: r[1]
    ti.sort(key=key); one.sort(key=key)

    def row(place, when, hm, ot, sid, note):
        if ot == 0:
            x = hm / mx
            dots = f'<i class="vd away" style="--x:{x:.4f}"></i><b class="vn side" style="left:calc({x * 100:.2f}% + 11px)">{hm}%，只补贴国产算力</b>'
        elif hm == ot:
            x = hm / mx
            side = f'right:calc({(1 - x) * 100:.2f}% + 11px)' if x > 0.6 else f'left:calc({x * 100:.2f}% + 11px)'
            dots = f'<i class="vd both" style="--x:{x:.4f}"></i><b class="vn side" style="{side}">一律{hm}%</b>'
        else:
            dots = (f'<i class="vl" style="--a:{ot / mx:.4f};--b:{hm / mx:.4f}"></i><i class="vd toward" style="--x:{ot / mx:.4f}"></i>'
                    f'<i class="vd away" style="--x:{hm / mx:.4f}"></i><b class="vn" style="--x:{ot / mx:.4f}">{ot}%</b><b class="vn" style="--x:{hm / mx:.4f}">{hm}%</b>')
        lab = f'国产{hm}%，其他算力不补贴' if ot == 0 else (f'国产{hm}%，其他{ot}%' if hm != ot else f'各类算力一律{hm}%')
        return (f'<div class="vr"><div class="vlab">{esc(place)} <a class="srcn" href="{url(sid)}">{when[0]}年{when[1]}月</a>{("<span class=vnote>" + esc(note) + "</span>") if note else ""}</div>'
                f'<div class="vt" role="img" aria-label="{esc(place, quote=True)}：{lab}">{dots}</div></div>')
    axis = '<div class="vr axis"><div></div><div class="vt">' + ''.join(f'<span style="--x:{v / mx:.4f}">{v}%</span>' for v in (0, 20, 40, 60)) + '</div></div>'
    out = ['<div class="vkey"><span><i class="sw away"></i>国产算力</span><span><i class="sw toward"></i>其他算力</span><span><i class="sw both"></i>各类算力一个比例</span></div>',
           '<div class="vgrid">',
           f'<div class="vgrp va"><h3>对国产算力补贴更多：{len(ti)}个</h3>' + ''.join(row(*r) for r in ti) + f'<h3>只补贴国产算力：{len(only)}个</h3>' + ''.join(row(*r) for r in only) + axis + '</div>',
           f'<div class="vgrp vb"><h3>各类算力一个比例：{len(one)}个</h3>' + ''.join(row(*r) for r in one) + axis + '</div>',
           f'<p class="fine vf">图中{len(rows)}个地方政府里，{len(ti)}个对国产算力补贴更多，同时仍补贴其他算力；{len(only)}个，即四川省，只补贴国产算力（其措施按新闻网站界面新闻所载的文本保存，无文号、无日期）；其余{len(one)}个各类算力一个比例。图中所示是普通申请者适用的比例。'
           '每个政府一行：取所找到的、写明账单补贴比例的最新一项普遍适用的规定（只针对某一类企业的更新规定见该行附注）；这些是找到并读过的规定，不是普查。'
           '没有列入的有：只见于媒体报道的规定（成都，50%对30%）、申报指南（北京市；南京市）、已不再有效或没有写明账单补贴比例的规定（其中包括深圳市龙岗区的规定）、'
           '尚未存入的规定（厦门）以及征求意见稿。'
           '只对用国产芯片建设或购置的支持另算：北京市2024年至2027年的方案，按投资额的一定比例支持“采购自主可控GPU芯片开展智能算力服务的企业”。'
           '分档用的是各规定自己的用词：“国产”或“自主”，对“非国产”“非自主”或“其他”。</p>', '</div>']
    return '\n'.join(out), len(ti), len(rows)


def bodies(evs):
    def P(*keys):
        return ''.join(pin(by(evs, k[0], k[1]) if isinstance(k, tuple) else by(evs, k)) for k in keys)
    held = [('国家网信办', P('cn-policy-cac-h20-original', ('man-cn-ft-20250821-regulators', 'BH'), 'cn-clips-alibaba-20f', 'man-cn-ft-20250917-6000d')),
            ('国家发展改革委', P(('man-cn-ft-20250821-regulators', 'BH'), 'cn-policy-ndrc-chip-adaptation-2026')),
            ('工业和信息化部', P('cn-factions-bloomberg-flexibility-202409-relay1', 'cn-le11-ft-h20justify-aggregoctt', ('man-cn-ft-20250821-regulators', 'BH'))),
            ('《华尔街日报》所说的丁薛祥牵头的芯片委员会', P('man-cn-factions-wsj-ding')),
            ('国家安全部', P('cn-acts-mss-xinhua-20250721')),
            ('官方媒体（中央广播电视总台旗下账号）', P('cn-le13-yuyuan-qq-20250810b')),
            ('海关', P('man-cn-ft-20251009-customs', 'cn-acts-reuters-customs-20260114')),
            ('财政部、工业和信息化部（只针对党政机关及相关事业单位的台式计算机采购）', P('cn-policy-desktop-2023'))]
    let = [('商务部', P('cn-policy-wang-nvidia', 'cn-policy-h20-mofcom', 'cn-tolerate-mof', 'cn-acts-mofcom-20261117')),
           ('国务院总理李强', P('cn-xi-round-f-6')),
           ('国务院副总理何立峰', P('cn-policy-he-welcomes')),
           ('路透社所说的工业和商务主管部门（原文：“industry and commerce ministries”）', P('cn-acts-reuters-deepseek-20260130')),
           ('工业和信息化部（The Information所报道的意向）', P('cn-acts-reuters-rtx5500-20260927'))]      # record 62 (core edit 7; the core's row of 03:00 UTC, Nov 25, 2026)
    firm = [('市场监管总局：针对英伟达公司本身的反垄断案件', P('cn-policy-samr-open-original', 'cn-policy-samr-further-original'))]
    col = lambda title, cls, rows: (f'<div class="bcol"><h4><i class="sw {cls}"></i>{title}</h4><ul>' + ''.join(f'<li><span>{esc(n)}</span><span class="pins">{p}</span></li>' for n, p in rows) + '</ul></div>')
    return ('<div class="bodies">' + col('限制英伟达，或引导买方转向国产芯片', 'away', held) + col('放行，或表示欢迎', 'toward', let) + '</div>'
            '<div class="bodies one">' + col('对英伟达公司本身采取行动', 'away', firm) + '</div>'
            '<p class="fine">英国《金融时报》（2026年11月13日，援引未具名人士）报道：国家网信办和国家安全部内部侧重安全的官员把对英伟达的依赖看作战略弱点（原文：“viewed dependence on Nvidia as a strategic vulnerability”），'
            '商务部倾向于进口（原文：“favoured imports”），2025年的限制行动由国家发展改革委牵头（原文：“was led by the National Development and Reform Commission”）。'
            f'美国贸易代表2026年11月20日说（<a href="{url("cn-le01-greer-bbg-20261120-youtube")}">彭博电视</a>；机器字幕，未经人耳核对，01:06至01:35）：'
            '情况并不像人们让你以为的那样铁板一块（原文：“not as monolithic as people would have you believe”）；'
            '按他自己的分析（原文：“my own analysis”），有人认为希望能买到（原文：“we’d like to have access”），也有人认为反正不要美国芯片（原文：“others who think, well, we don’t want American chips anyway”）。'
            '两条字幕轨的断句不同，因此他是否把这一分歧放在政府内部，并无定论。</p>'
            '<p class="fine">市场监管总局党组把英伟达案与高通公司、杜邦中国集团的案件一并列在“坚决落实党中央重大决策部署”和“敢于斗争”之下'
            f'（<a href="{url("cn-media-party-samr-september")}">共产党员手机报，2026年9月24日</a>）。英伟达的报告说，初步调查结论涉及美国出口管制要求它向中国市场提供的降规产品（原文：“degraded products”）。'
            '有一项规定（如未解除）方向正相反：市场监管总局2020年附条件批准英伟达收购迈络思，条件之一是英伟达须“向中国市场继续供应英伟达GPU加速器”；'
            '交易双方可在条件生效6年后申请解除'
            f'（<a href="{url("cn-policy-mellanox-conditions")}">公告全文</a>）。</p>')


def state_media():
    """The state and Party media items on Nvidia chips (tables/state_media_items.tsv: agent L13's census, rows 1 to 42, and
    agent GA02's rows 43 to 75, found by searches and links): how many, how many only warn, how many of those are dated up
    to Sept 24, 2025 with their first and last dates, and how many are later, counted as the core's builder counts them."""
    rows = table('state_media_items.tsv')
    st = Counter(r['stance'] for r in rows)
    warns = sorted(date.fromisoformat(r['date']) for r in rows if r['stance'] == 'warns')
    iso = sorted(date.fromisoformat(r['date']) for r in rows if re.fullmatch(r'\d{4}-\d\d-\d\d', r['date']))
    win = [d for d in warns if d <= date(2025, 9, 24)]; late = [r for r in rows if r['stance'] == 'warns' and date.fromisoformat(r['date']) > date(2025, 9, 24)]
    # the counts of atlas/core_edit/p6_work_5/count_census.py over the table (Nov 24, 2026), and what the template says of the later warnings
    assert (len(rows), st['warns'], len(win), len(late)) == (75, 14, 11, 3) and all(r['outlet'].startswith('Global Times') and r['date'].startswith('2026') for r in late), (len(rows), st)
    if not all(r['outlet'].startswith('Global Times (English)') for r in late):   # the Chinese note says 英文版 (not an assert: mirror_check compares the asserts with the core's)
        sys.exit(f"a later warning is not in Global Times's English edition: {[r['outlet'] for r in late]}")
    return dict(SM_N=str(len(rows)), SM_W=str(len(warns)), SM_WIN=str(len(win)), SM_WLATE={3: '3'}[len(late)], SM_W0=fmt(warns[0]), SM_W1=fmt(win[-1]), SM_MIX=str(st['mixed']),
                SM_FROM=f'{iso[0].year}年{iso[0].month}月', SM_TO=f'{iso[-1].year}年{iso[-1].month}月')


def ledger(group, title):
    out = [f'<section class="lcol"><h3>{title}</h3><ol>']
    for e in group:
        src = f'<a href="{esc(e["url"], quote=True)}">{esc(e["S"])}</a>' if e['url'] else esc(e['S'])
        out.append(f'<li id="e{e["n"]}" class="ev {e["dir"]}" data-n="{e["n"]}">{pin(e, tip=False)}<div><span class="when">{esc(e["when"])}</span> '
                   f'<span class="what">{esc(e["T"])}</span> <span class="src">{src}</span></div></li>')
    out.append('</ol></section>')
    return '\n'.join(out)


def main():
    evs, checks = load()
    bad = verify(evs, checks)
    if bad:
        print('\n'.join(bad)); sys.exit(f'{len(bad)} quotations or blocks failed; nothing written')
    mirror_check()
    # the same quotations as a quotes.tsv for the shared checker; stop if it fails
    with open(F / 'quotes.tsv', 'w', encoding='utf-8') as fh:
        fh.write('# saved id <TAB> the source\'s exact words. Written by cn_figure_build.py from figure_data.txt (Q lines, then ! lines).\n')
        for e in evs: fh.write(f"{e['sid']}\t{e['Q']}\n")
        for sid, q in checks: fh.write(f'{sid}\t{q}\n')
    r = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts' / 'cn_has.py'), str(F / 'quotes.tsv')], capture_output=True, text=True)
    print('cn_has.py:', (r.stdout.strip().splitlines() or ['(no output)'])[-1])
    if r.returncode != 0:
        print(r.stdout, r.stderr); sys.exit('cn_has.py failed on quotes.tsv; nothing written')
    b, c = number(evs)
    nolink = [e['sid'] for e in evs if not e['url']]
    tip = {e['n']: dict(w=e['when'], l=''.join(LANES[e['lane']][:2]), t=e['T'], q=e['Q'], z=e['Z'], s=e['S'], k=('有公开记录' if e['solid'] else '媒体报道，未具名消息人士')) for e in evs}
    page = (F / 'template.html').read_text(encoding='utf-8')
    bars_h, h = bars(evs)
    vouch_h, n_tiered, n_vouch = vouchers()
    parts = {'STRIP': strip(evs), 'BARS': bars_h, 'SHARE': share(), 'REVENUE': revenue(), 'PAPER': paper(evs), 'BODIES': bodies(evs), 'VOUCHERS': vouch_h,
             'LEDGER': ledger(b, '北京方面') + ledger(c, '企业'), 'EVJSON': json.dumps(tip, ensure_ascii=False).replace('</', '<\\/'),
             'N_EVENTS': str(len(evs)), 'N_SOLID': str(sum(e['solid'] for e in evs)), 'N_HOLLOW': str(sum(not e['solid'] for e in evs)),
             'HF_RWA': f'{h["rwa"][0]:,}', 'HF_ALL': f'{h["all"][0]:,}', **state_media()}
    for k, v in parts.items():
        assert f'%%{k}%%' in page, k
        page = page.replace(f'%%{k}%%', v)
    page = re.sub(r'%%REC:([a-z0-9-]+)%%', lambda m: str(by(evs, m.group(1))['n']), page)   # record numbers in the notes
    assert '%%' not in page, page[page.index('%%'):][:40]
    for e in evs:                                         # the records note types each fixed number (round 8): it must be the data's
        if e['N']: assert f'第{e["n"]}条记录是在这张图的英文版公开之后' in page, f'the records note does not name the fixed record number {e["n"]} ({e["sid"]})'
    assert '第61条记录是在这张图的英文版公开之后' not in page, 'control: a record number that is not fixed is named as fixed'
    assert 'href=""' not in page, 'an empty link'
    segs, loose = page_quotes_ok(page, evs, checks)
    if loose:
        print('\n'.join(loose)); sys.exit(f'{len(loose)} quoted passages on the page are not part of a checked quotation; nothing written')
    (F / f'{OUT}.html').write_text(page, encoding='utf-8')
    with open(F / 'figure_events_zh.tsv', 'w', encoding='utf-8') as fh:
        fh.write('n\tdate\tshown_as\tlane\tkind\tsource\taddress\tsaved_id\ttext\n')
        for e in sorted(evs, key=lambda e: e['n']):
            fh.write(f"{e['n']}\t{e['date']}\t{e['when']}\t{''.join(LANES[e['lane']][:2])}\t{e['kind']}\t{e['S']}\t{e['url'] or ''}\t{e['sid']}\t{e['T']}\n")
    per = {k: sum(e['lane'] == k for e in evs) for k in ORDER}
    nz = sum(bool(e['Z']) for e in evs)
    print(f'events {len(evs)} ({per}); on the record {parts["N_SOLID"]}, press reports {parts["N_HOLLOW"]}; quotations checked {len(evs) + len(checks)}, all found; control not found (as it must be)')
    print(f'tables: House table {h["all"][1]} rows ({h["all"][0]:,} chips; approved {h["appr"][0]:,}, Nvidia {h["appr_nv"][0]:,}; RWA {h["rwa"][0]:,}, Nvidia {h["rwa_nv"][0]:,}); '
          f'31 governments; evaluations {evaluations()[0]} AI chips; vouchers {n_tiered} of {n_vouch} tiered; state media {parts["SM_N"]} items, {parts["SM_W"]} warn ({parts["SM_W0"]} to {parts["SM_W1"]})')
    print(f'records with a Chinese source (original shown) {len(evs) - nz}; with an English source (my Chinese rendering beside the original) {nz}')
    print(f'quoted passages in the page text {len(segs)}, all part of a checked quotation; control fails (as it must); panels name the core\'s saved ids in the core\'s order')
    print('no address to link:', nolink or 'none')
    print('written', F / f'{OUT}.html', len(page), 'bytes')
    if '--png' in sys.argv:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            br = p.chromium.launch()
            pg = br.new_context(viewport={'width': 1500, 'height': 1000}, device_scale_factor=2, color_scheme='light', locale='zh-CN').new_page()
            pg.goto((F / f'{OUT}.html').as_uri()); pg.evaluate('document.fonts.ready.then(() => 1)'); pg.wait_for_timeout(900)
            for sel, name in (('#figure', f'{OUT}_full.png'), ('#hero', f'{OUT}_strip.png'), ('#top', f'{OUT}_top.png')):
                pg.locator(sel).screenshot(path=str(F / name)); print('image', F / name)
            br.close()


main()
