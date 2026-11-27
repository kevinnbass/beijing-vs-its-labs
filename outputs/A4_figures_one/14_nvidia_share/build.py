#!/usr/bin/env python3
"""Idea 14: Nvidia's share of AI chips in China over time, as a page and an image.

Run: python3 -I build.py                                   checks quotes.tsv with scripts/cn_has.py, writes share.html
     python3 build.py --png     the same, then writes share.png (the figure alone, twice size)
Reads quotes.tsv, share.tsv and trendforce.tsv (this folder) and ../a4lib.py (shared helpers).
Round 4 (Nov 23, 2026), the core's wording: for 2025, IDC's data and Enflame's own sales (a prospectus: on the record);
TrendForce counts differently (foreign suppliers together 34% in 2025, 21% expected in 2026) and has a panel of its own.
Nothing is written unless cn_has.py exits 0, every share in share.tsv stands in its sentence, and the guard finds every
quotation and number on the page in quotes.tsv.
The "about 95%" is Reuters's own description; the 55% and 34% are a research firm's (IDC) counts. They are not one series:
the chart puts the 95% in a field of its own, on a grid of its own, and joins only the two IDC columns.
Round 10 (Nov 25, 2026, core batch 12 and two readers of the public page): the headline names IDC's counts of chips shipped;
the argument's new estimate (Bernstein, about 40% in 2025, by the Associated Press's report of Jun 29, 2026) is given in the
notes and not drawn (another measure); the 95% is Reuters's description with no date or count given; the five named Chinese
makers' rounded shares add to about 47%; the chief executive's "effectively fallen to zero" is given with no period or count.
Round 12 (Nov 26, 2026, readers of the seventh version): the eyebrow says "shares of the market" (not "who sold them": the IDC
figures count chips shipped, and TrendForce's include chips firms develop for their own use); the chart's note names each IDC
column's own measure (AI accelerator cards shipped in 2025; the market for data-centre AI chips in January to June 2026).
The page's top line is the credit alone (a4lib.NOTE).
Round 13 (Nov 26, 2026, both readers of the eighth version): the headline no longer says Nvidia's share "fell from 55% to 34%"
(a fall from one reading to the other that neither report states, across two measures); it gives each IDC reading with its own
measure, as the chart's note does: 55% of AI accelerator cards shipped in 2025, 34% of the market for data-centre AI chips in
January to June 2026, and Huawei's 28% in that half year.
Before the page or image is called done or shown: scripts/render_and_look.py on share.html and share.png.
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import a4lib as A   # noqa: E402

esc, qm, fmt = A.esc, A.qm, A.fmt
MONTH = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

CSS = '''
#fig { background: var(--page); }
header { margin-bottom: 18px; }
h1 { max-width: none; font-size: clamp(26px, 3.25vw, 40px); }
@media (max-width: 1000px) { h1 br { display: none; } }
i.sw.rest { background: repeating-linear-gradient(45deg, var(--rest) 0 3px, transparent 3px 6px); box-shadow: inset 0 0 0 1px var(--axis); }
.plot svg { display: block; width: 100%; height: auto; }
.plot svg.narrow { display: none; }
@media (max-width: 760px) { .plot svg.wide { display: none; } .plot svg.narrow { display: block; } }
svg text { font-family: var(--font-text); }
.wash { fill: var(--wash); }
.g { stroke: var(--grid); stroke-width: 1; } .g0 { stroke: var(--axis); stroke-width: 1; }
.tk { fill: var(--muted); font-weight: 500; text-anchor: end; }
.zh { fill: var(--muted); font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
.s.toward { fill: var(--toward); } .s.away { fill: var(--away); } .s.other { fill: var(--us); }
.s.under { fill: var(--surface); } .s.tint { fill: var(--toward); fill-opacity: 0.2; }
.s.rest { stroke: var(--axis); stroke-width: 1; }
.hb { fill: var(--rest); }
.band.toward { fill: var(--toward); fill-opacity: 0.11; }
.edge { fill: none; stroke-width: 2; stroke-linecap: round; } .edge.toward { stroke: var(--toward); }
.nm { font-weight: 600; text-anchor: middle; } .vl { font-family: var(--font-head); font-weight: 700; text-anchor: middle; letter-spacing: -0.01em; }
.on { fill: var(--pin-on); } .ink { fill: var(--ink); } .ink2 { fill: var(--ink2); }
.cp { fill: var(--ink); font-weight: 700; text-anchor: middle; } .cs { fill: var(--muted); font-weight: 500; text-anchor: middle; }
.ol { fill: var(--ink); font-weight: 600; } .od { fill: var(--ink2); font-weight: 500; }
.br { stroke: var(--ink2); stroke-width: 1; fill: none; }
.fine { font-size: 13.5px; color: var(--ink2); margin: 12px 0 0; max-width: 100ch; }
.fine b { color: var(--ink); font-weight: 600; }
.tf { margin-top: 16px; }
.tfrow { display: grid; grid-template-columns: 96px minmax(0, 1fr); gap: 4px 14px; align-items: center; padding: 9px 0; border-top: 1px solid var(--grid); }
.tflab b { display: block; font-weight: 600; font-size: 15.5px; line-height: 1.2; } .tflab span { display: block; font-size: 12.5px; color: var(--muted); }
.tfbar { display: flex; gap: 2px; height: 28px; }
.tfbar i { display: flex; align-items: center; padding-left: 9px; border-radius: 4px; min-width: 0; font: 700 15px/1 var(--font-head); font-style: normal; white-space: nowrap; }
.tfbar i.toward { background: var(--toward); color: var(--pin-on); } .tfbar i.away { background: var(--away); color: var(--pin-on); }
.tfbar i.own, i.sw.own { background: color-mix(in srgb, var(--away) 45%, var(--surface)); } .tfbar i.own { color: var(--ink); }
.tfsrc { margin: 9px 0 0; font-size: 13px; color: var(--ink2); }
.tf .key { margin: 0 0 10px; font-size: 13.5px; }
@media (max-width: 760px) { .tfrow { grid-template-columns: minmax(0, 1fr); } .tflab b, .tflab span { display: inline; } .tflab span { margin-left: 6px; } }
.below { display: grid; gap: 16px; margin-top: 16px; }
@media (max-width: 700px) { table.tv thead { display: none; } table.tv tr { display: block; padding: 8px 0; border-bottom: 1px solid var(--grid); }
  table.tv td { display: block; border: 0; padding: 2px 0; } }
'''


def load(Q):
    lines = [ln for ln in (HERE / 'share.tsv').read_text(encoding='utf-8').splitlines() if ln.strip() and not ln.startswith('#')]
    hdr, D = lines[0].split('\t'), {}
    for ln in lines[1:]:
        r = dict(zip(hdr, ln.split('\t'))); r['share'] = int(r['share']); w = Q[r['qkey']]
        named = r['label'] if r['who'] not in ('nvidia', 'chinese', 'amd', 'huawei') else ''
        ok = re.search(rf"{re.escape(named)}\D{{0,8}}{r['share']}%", w) if named else f"{r['share']}%" in w
        if not ok: sys.exit(f"share.tsv: {r['label']} {r['share']}% is not in the words of {r['qkey']}")
        D.setdefault(r['period'], []).append(r)
    assert sum(r['share'] for r in D['y2025']) == 100, '2025: the three shares the report gives should make 100'
    return D


def chart(D, cap, narrow=False):
    """Three columns. The first (Reuters's description) stands in a field and on a grid of its own; only the two IDC columns are joined."""
    if narrow:
        W, H, y0, y100 = 358, 404, 300, 58
        za, ca, gx, cb, cc = (34, 124), (48, 110), (136, 356), (148, 210), (278, 340)
        f = dict(name=10.5, val=19, about=10, tick=10, zh=9, cp=10.5, cs=10, nmdy=15, vldy=35)
    else:
        W, H, y0, y100 = 1152, 540, 440, 78
        za, ca, gx, cb, cc = (58, 332), (120, 270), (374, 1140), (432, 582), (762, 912)
        f = dict(name=14, val=32, about=14, tick=12, zh=11.5, cp=15, cs=12.5, nmdy=24, vldy=56)
    k = (y0 - y100) / 100
    Y = lambda p: y0 - p * k
    sid = 'n' if narrow else 'w'
    o = [f'<svg class="{"narrow" if narrow else "wide"}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="ch-t{sid} ch-d{sid}"><title id="ch-t{sid}">Nvidia’s share of AI chips in China, three readings</title>'
         f'<desc id="ch-d{sid}">{esc(cap["desc"])}</desc>'
         f'<defs><pattern id="hatch{sid}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect class="hb" width="3" height="7"/></pattern></defs>'
         f'<rect class="wash" x="{za[0]}" y="{y100 - 44}" width="{za[1] - za[0]}" height="{H - (y100 - 44) - 6}" rx="8"/>']
    for p in (0, 25, 50, 75, 100):
        cls = 'g0' if p == 0 else 'g'
        o.append(f'<line class="{cls}" x1="{za[0] + 8}" y1="{Y(p):.1f}" x2="{za[1] - 8}" y2="{Y(p):.1f}"/><line class="{cls}" x1="{gx[0]}" y1="{Y(p):.1f}" x2="{gx[1]}" y2="{Y(p):.1f}"/>'
                 f'<text class="tk" font-size="{f["tick"]}" x="{za[0] - 5}" y="{Y(p) + 4:.1f}">{p}{"%" if p == 100 else ""}</text>')
    zy = y100 - 24
    if narrow:
        o.append(f'<text class="zh" font-size="{f["zh"]}" x="{za[0] + 7}" y="{zy - 6}">Different</text><text class="zh" font-size="{f["zh"]}" x="{za[0] + 7}" y="{zy + 6}">yardstick</text>'
                 f'<text class="zh" font-size="{f["zh"]}" x="{gx[0]}" y="{zy}">IDC’s counts of chips shipped</text>')
    else:
        o.append(f'<text class="zh" font-size="{f["zh"]}" x="{za[0] + 14}" y="{zy}">A different yardstick</text>'
                 f'<text class="zh" font-size="{f["zh"]}" x="{gx[0]}" y="{zy}">Counts of AI chips shipped in China, by the research firm IDC</text>')

    def seg(c, p0, p1, cls, tip=''):
        fill = f' fill="url(#hatch{sid})"' if cls == 'rest' else ''
        tip = f'<title>{esc(tip)}</title>' if tip else ''
        return f'<rect class="s {cls}"{fill} x="{c[0]}" y="{Y(p1) + 1:.1f}" width="{c[1] - c[0]}" height="{max(1.5, (p1 - p0) * k - 2):.1f}" rx="3">{tip}</rect>'

    def inside(c, ptop, name, val, cls, about=False):
        cx = (c[0] + c[1]) / 2; y = Y(ptop)
        nm = ''.join(f'<text class="nm {cls}" font-size="{f["name"]}" x="{cx}" y="{y + f["nmdy"] + i * (f["name"] + 2):.1f}">{esc(n)}</text>' for i, n in enumerate(name))
        dy = f['vldy'] + (len(name) - 1) * (f['name'] + 2)
        v = (f'<tspan font-family="Inter, sans-serif" font-weight="600" font-size="{f["about"]}">about </tspan>' if about else '') + f'{val}%'
        return nm + f'<text class="vl {cls}" font-size="{f["val"]}" x="{cx}" y="{y + dy:.1f}">{v}</text>'

    # the field at left: Reuters's own description, drawn as a tint, not as a series bar
    b = D['before'][0]
    o.append(seg(ca, 0, b['share'], 'under') + seg(ca, 0, b['share'], 'tint', f'Nvidia, about {b["share"]}%: Reuters’s own description of the time before US export curbs tightened') + inside(ca, b['share'], ['Nvidia'], b['share'], 'ink', about=True))
    # 2025 and January to June 2026: stacked from the bottom (Nvidia) and from the top (Chinese makers)
    stacks = {}
    for key, c in (('y2025', cb), ('h2026', cc)):
        rows = D[key]; nv = next(r for r in rows if r['who'] == 'nvidia'); cn = [r for r in rows if r['dir'] == 'away']; ot = [r for r in rows if r['dir'] == 'other']
        per = cap[key][0][1] + ', ' + cap[key][1][1].rstrip(',')
        o.append(seg(c, 0, nv['share'], 'toward', f'Nvidia {nv["share"]}% · {per}') + inside(c, nv['share'], ['Nvidia'], nv['share'], 'on'))
        top, marks = 100, []
        for r in cn:
            o.append(seg(c, top - r['share'], top, 'away', f'{r["label"]} {r["share"]}% · {per}')); marks.append((r, top - r['share'], top)); top -= r['share']
        big = cn[0]
        o.append(inside(c, 100, ['Chinese', 'makers'] if (narrow and big['who'] == 'chinese') else [big['label']], big['share'], 'on'))
        mid = nv['share']
        for r in ot:
            o.append(seg(c, mid, mid + r['share'], 'other', f'{r["label"]} {r["share"]}% · {per}')); marks.append((r, mid, mid + r['share'])); mid += r['share']
        if top - mid > 0: o.append(seg(c, mid, top, 'rest', f'Not broken down in the report: {top - mid}% (our subtraction) · {per}'))
        stacks[key] = dict(nv=nv['share'], cn_low=top, rest=(mid, top), marks=marks)
    a, z = stacks['y2025'], stacks['h2026']
    # only Nvidia is joined across the two IDC columns: it is the one maker counted the same way in both reports.
    # Chinese makers are given together for 2025 and by name for 2026, so no line is drawn between those two.
    o.append(f'<polygon class="band toward" points="{cb[1]},{Y(0) - 1:.1f} {cb[1]},{Y(a["nv"]) + 1:.1f} {cc[0]},{Y(z["nv"]) + 1:.1f} {cc[0]},{Y(0) - 1:.1f}"/>'
             f'<line class="edge toward" x1="{cb[1] + 1}" y1="{Y(a["nv"]) + 1:.1f}" x2="{cc[0] - 1}" y2="{Y(z["nv"]) + 1:.1f}"/>')
    if not narrow:                                   # labels beside the thin parts; on a phone the table under the chart carries them
        amd = next(m for m in a['marks'] if m[0]['who'] == 'amd')
        o.append(f'<text class="ol" font-size="13" text-anchor="end" x="{cb[0] - 9}" y="{Y((amd[1] + amd[2]) / 2) + 4.5:.1f}">{amd[0]["label"]} {amd[0]["share"]}%</text>')
        small = [m for m in z['marks'] if m[0]['who'] != 'huawei']
        lo, hi = min(m[1] for m in small), max(m[2] for m in small); x = cc[1] + 9; ym = Y((lo + hi) / 2)
        half = len(small) // 2
        l1 = ', '.join(f'{m[0]["label"]} {m[0]["share"]}%' for m in small[:half]) + ','
        l2 = ', '.join(f'{m[0]["label"]} {m[0]["share"]}%' for m in small[half:])
        o.append(f'<path class="br" d="M{x - 3},{Y(hi) + 2:.1f} H{x} V{Y(lo) - 2:.1f} H{x - 3}"/>'
                 f'<text class="ol" font-size="13" x="{x + 9}" y="{ym - 13:.1f}">{cap["more"]}</text>'
                 f'<text class="od" font-size="12.5" x="{x + 9}" y="{ym + 4:.1f}">{esc(l1)}</text><text class="od" font-size="12.5" x="{x + 9}" y="{ym + 20:.1f}">{esc(l2)}</text>')
        ry = Y((z['rest'][0] + z['rest'][1]) / 2)
        o.append(f'<text class="ol" font-size="13" x="{x + 9}" y="{ry - 3:.1f}">Not broken down in the report</text>'
                 f'<text class="od" font-size="12.5" x="{x + 9}" y="{ry + 14:.1f}">{cap["rest"]}%, by our subtraction</text>')
    for c, key in ((ca, 'before'), (cb, 'y2025'), (cc, 'h2026')):
        cx = (c[0] + c[1]) / 2; lines = cap[key + ('.n' if narrow else '')]; y = y0 + (20 if narrow else 26)
        for i, (cls, t) in enumerate(lines):
            o.append(f'<text class="{cls}" font-size="{f["cp"] if cls == "cp" else f["cs"]}" x="{cx}" y="{y:.1f}">{esc(t)}</text>')
            y += (f['cp'] + 3 if lines[min(i + 1, len(lines) - 1)][0] == 'cp' else f['cs'] + 4.5)
    o.append('</svg>')
    return '\n'.join(o)


def trendforce(Q):
    """TrendForce's two readings (2025, and 2026 as expected), each figure read from its sentence in quotes.tsv."""
    lines = [ln for ln in (HERE / 'trendforce.tsv').read_text(encoding='utf-8').splitlines() if ln.strip() and not ln.startswith('#')]
    hdr, T = lines[0].split('\t'), {}
    for ln in lines[1:]:
        r = dict(zip(hdr, ln.split('\t'))); r['share'] = int(r['share'])
        nums = [int(x) for x in re.findall(r'(\d+) percent', Q[r['qkey']])]
        if len(nums) != 2: sys.exit(f"trendforce.tsv: the words of {r['qkey']} do not hold two figures")
        want = nums[0] if r['year'] == '2026' else nums[1]          # each sentence gives this year's figure first, then last year's
        if r['share'] != want: sys.exit(f"trendforce.tsv: {r['year']} {r['who']} {r['share']} is not what {r['qkey']} says ({want})")
        T.setdefault(r['year'], []).append(r)
    assert sorted(T) == ['2025', '2026'] and all(sum(r['share'] for r in T[y]) == 100 for y in T), 'each year\'s three shares should make 100'
    assert 'this year' in Q['tf.foreign'] and 'last year' in Q['tf.foreign'] and A.day(Q, 'tf').year == 2026, 'the report\'s "this year" is 2026'
    return T


def tfpanel(T):
    name = {'foreign': 'foreign suppliers together', 'makers': 'Chinese makers of AI chips', 'own': 'tech firms’ own chips'}
    out = []
    for y, lab in (('2025', ''), ('2026', 'expected')):
        said = ', '.join(f'{name[r["who"]]} {r["share"]}%' for r in T[y])
        segs = ''.join(f'<i class="{r["dir"]}" style="flex:{r["share"]}" title="{esc(name[r["who"]])}: {r["share"]}%"><span>{r["share"]}%</span></i>' for r in T[y])
        out.append(f'<div class="tfrow"><div class="tflab"><b>{y}</b>{f"<span>{lab}</span>" if lab else ""}</div>'
                   f'<div class="tfbar" role="img" aria-label="{y}{", " + lab if lab else ""}: {esc(said, quote=True)}">{segs}</div></div>')
    return '\n'.join(out)


def main():
    qfile = HERE / 'quotes.tsv'
    A.check(qfile)                                   # stops here if a quotation is not found in its saved copy
    Q = A.quotes(qfile); A.guard_control(Q)
    D = load(Q)
    page26 = A.L.page(Q['h2026.nvidia'].sid)
    assert 'huawei' in page26 and 'cambricon' in page26, 'control: the 2026 page should name Huawei and Cambricon'
    assert 'amd' not in page26, 'the 2026 page mentions AMD after all: the figure and its notes must change'
    d0, d1, d2 = A.day(Q, 'before'), A.day(Q, 'y2025'), A.day(Q, 'h2026')
    T = trendforce(Q); d_tf, d_enf = A.day(Q, 'tf'), A.day(Q, 'enflame')
    d_bern = A.day(Q, 'bernstein')                                     # round 10: the Associated Press's report of Bernstein's estimate
    assert A.ref(Q['bernstein'].sid)['tier'] == 'open' and 'Bernstein' in Q['bernstein.who']
    tf_when = f'{MONTH[d_tf.month - 1]} {d_tf.year}'                    # the page carries two stamps of the same month; the month is what is shown
    tf25 = next(r for r in T['2025'] if r['who'] == 'foreign')['share']; tf26 = next(r for r in T['2026'] if r['who'] == 'foreign')['share']
    tf_words = Q['tf.foreign'][Q['tf.foreign'].index('is expected'):]
    assert A.ref(Q['enflame'].sid)['tier'] == 'solid' and A.ref(Q['tf.foreign'].sid)['tier'] == 'open'
    enf_en = 'about 4 million AI accelerator cards were shipped in China in 2025; Nvidia, with about 2.2 million, held about 55% of the market'
    nv25 = next(r for r in D['y2025'] if r['who'] == 'nvidia')['share']; nv26 = next(r for r in D['h2026'] if r['who'] == 'nvidia')['share']
    cn25 = next(r for r in D['y2025'] if r['who'] == 'chinese')['share']; amd = next(r for r in D['y2025'] if r['who'] == 'amd')['share']
    hw = next(r for r in D['h2026'] if r['who'] == 'huawei')['share']; b95 = D['before'][0]['share']
    named = [r for r in D['h2026'] if r['dir'] == 'away']; more = [r for r in named if r['who'] != 'huawei']
    named_sum = sum(r['share'] for r in named)                    # our addition
    rest = 100 - sum(r['share'] for r in D['h2026'])              # our subtraction
    words = {4: 'Four', 5: 'five'}
    cap = {
        'desc': f'Before US export curbs tightened: Nvidia about {b95} per cent, in Reuters’s own description; not part of the series. 2025: Nvidia {nv25}, AMD {amd}, Chinese makers {cn25}. '
                f'January to June 2026: Nvidia {nv26}, Huawei {hw}, ' + ', '.join(f'{r["label"]} {r["share"]}' for r in more) + f', not broken down {rest}. The 2026 report does not mention AMD.',
        'more': f'{words[len(more)]} more Chinese makers', 'rest': rest,
        'before': [('cp', 'Before US export curbs tightened'), ('cs', 'Reuters’s own description,'), ('cs', fmt(d0))],
        'before.n': [('cp', 'Before US curbs'), ('cp', 'tightened'), ('cs', 'Reuters,'), ('cs', fmt(d0))],
        'y2025': [('cp', '2025'), ('cs', 'IDC, reported by Reuters,'), ('cs', fmt(d1))], 'y2025.n': [('cp', '2025'), ('cs', 'IDC, through Reuters,'), ('cs', fmt(d1))],
        'h2026': [('cp', 'Jan to Jun 2026'), ('cs', 'IDC, reported by Reuters,'), ('cs', fmt(d2))], 'h2026.n': [('cp', 'Jan to Jun 2026'), ('cs', 'IDC, through Reuters,'), ('cs', fmt(d2))],
    }
    L = lambda key, text: A.link(Q[key].sid, text)
    page = A.head('Nvidia’s China Share', CSS) + f'''<body>
<div class="wrap">
 <p class="draft">{A.NOTE}</p>
 <div id="fig">
  <header>
   <p class="eyebrow">China · AI chips · shares of the market</p>
   <h1>By IDC’s counts, Nvidia had {nv25}% of AI accelerator cards shipped in China in 2025, and {nv26}% of the market for data-centre AI chips in January to June 2026.<br> In that half year Huawei had {hw}%.</h1>
   <p class="deck">Counts of AI chips shipped in China in 2025 and in January to June 2026, by the research firm IDC, as reported by Reuters. The {b95}% at left is Reuters’s own description of an earlier time. It is not from the same series, so it stands apart. A second research firm, TrendForce, counts differently; its figures have a panel of their own. These are different measures, not one series.</p>
   <ul class="key">
    <li><i class="sw toward"></i><span><b>Nvidia</b></span></li>
    <li><i class="sw away"></i><span><b>Chinese makers</b></span></li>
    <li><i class="sw us"></i><span><b>AMD</b>, in the 2025 count only</span></li>
    <li><i class="sw rest"></i><span><b>Not broken down</b> in the report</span></li>
    <li><i class="mk open"></i><span><b>Open mark:</b> Reuters’s own description or a research firm’s figures</span></li>
    <li><i class="mk solid"></i><span><b>Filled mark:</b> on the record (a chip maker’s prospectus)</span></li>
   </ul>
  </header>
  <section class="card plot">
   <h2>Nvidia from the bottom, Chinese makers from the top</h2>
   <p class="sub">Each column is 100%, the whole market as one report gives it: in 2025 AI accelerator cards shipped, in January to June 2026 the market for data-centre AI chips. Nvidia’s share is joined across the two IDC columns; the first column stands apart.</p>
{chart(D, cap)}
{chart(D, cap, narrow=True)}
   <p class="fine"><b>Read with care.</b> The {b95}% is Reuters’s own description, and the report gives no date for it and no count behind it; the {nv25}% and {nv26}% are counts of chips shipped. A full year stands beside a half year.
    For 2025 the report gives Chinese makers together. For 2026 it names {words[len(named)]} of them and leaves {rest}% not broken down (our subtraction); it does not mention AMD.
    <i class="mk solid"></i> For 2025 a Chinese chip maker gives the same share on the record: by IDC’s data and its own sales, Enflame’s prospectus of {fmt(d_enf)} puts Nvidia at about 2.2 million of about 4 million cards shipped, about {nv25}%.</p>
  </section>
  <section class="card tf">
   <h2>A second research firm counts differently</h2>
   <p class="sub">TrendForce’s figures, as the trade site Silicon UK reported them in {tf_when}: the combined share of Nvidia, AMD and other foreign suppliers {qm(tf_words)}. For 2025 that is {tf25}% for all foreign suppliers together, where IDC’s count gives Nvidia alone {nv25}%. Different measures, not one series.</p>
   <ul class="key">
    <li><i class="sw toward"></i><span><b>Foreign suppliers together:</b> Nvidia, AMD and others</span></li>
    <li><i class="sw away"></i><span><b>Chinese makers of AI chips,</b> such as Huawei and Cambricon</span></li>
    <li><i class="sw own"></i><span><b>Tech firms’ own chips,</b> developed mainly for their own use</span></li>
   </ul>
{tfpanel(T)}
   <p class="tfsrc"><i class="mk open"></i> TrendForce, {L("tf.foreign", f"as reported by Silicon UK, {tf_when}")}. The 2026 figures are what the firm expected then, not a count.</p>
  </section>
 {A.IMGNOTE}
 </div>
 <div class="below">
  <section class="card">
   <h2>The numbers, in the sources’ words</h2>
   <p class="sub">Every quotation was found in the saved copy of its source by a script.</p>
   <table class="tv"><thead><tr><th>Reading</th><th>Nvidia</th><th>Others</th><th>Source</th></tr></thead><tbody>
    <tr><td><b>Before US export curbs tightened</b><br>no date given</td><td>about {b95}%: {qm(Q["before.nvidia"])}</td><td>Others: not given</td><td><i class="mk open"></i> {L("before.nvidia", f"Reuters, {fmt(d0)}")}, in its own words</td></tr>
    <tr><td><b>2025</b><br>the whole year</td><td>{nv25}%: {qm(Q["y2025.nvidia"])}</td><td>Chinese makers {cn25}%: {qm(Q["y2025.chinese"])}. AMD {amd}%: {qm(Q["y2025.amd"])}</td>
     <td><i class="mk open"></i> {L("y2025.nvidia", f"Reuters, {fmt(d1)}")}: {qm(Q["y2025.idc"])}.<br><i class="mk solid"></i> {L("enflame", f"Enflame, prospectus signed {fmt(d_enf)}")}, by IDC’s data and its own sales, {qm(Q["enflame.basis"])}:
      <span lang="zh-Hans">{qm(Q["enflame"])}</span> ({enf_en})</td></tr>
    <tr><td><b>Jan to Jun 2026</b><br>half a year</td><td>{nv26}%: {qm(Q["h2026.nvidia"])}</td><td>Huawei {hw}%: {qm(Q["h2026.huawei"])}. {qm(Q["h2026.others"])}. Not broken down: {rest}% (our subtraction). The page does not mention AMD</td>
     <td><i class="mk open"></i> {L("h2026.nvidia", f"Reuters, carried by Mint, {fmt(d2)}")}: {qm(Q["h2026.idc"])}</td></tr>
    <tr><td><b>TrendForce</b><br>2025, and 2026 as expected; a different measure</td><td>not given alone. Foreign suppliers together, {tf25}% then {tf26}%: {qm(Q["tf.foreign"])}</td>
     <td>Chinese makers of AI chips: {qm(Q["tf.makers.who"])} {qm(Q["tf.makers"])}. Tech firms’ own chips: {qm(Q["tf.own.who"])} {qm(Q["tf.own"])}</td>
     <td><i class="mk open"></i> {L("tf.foreign", f"Silicon UK, {tf_when}")}: {qm(Q["tf.who"])}</td></tr>
   </tbody></table>
  </section>
  <section class="card notes">
   <h2>Read with care</h2>
   <ul>
    <li>Not one series. The {b95}% is Reuters’s own sentence; it gives no date, no count and no source. The {nv25}% and {nv26}% are IDC’s counts. The chart does not join the first to the others.</li>
    <li>TrendForce’s figures are a third measure. For 2025 it gives all foreign suppliers together {tf25}%, where IDC’s count, as Reuters reported it, gives Nvidia {nv25}% and AMD {amd}%. The two firms do not measure the same thing, so neither is drawn on the other’s chart. TrendForce’s 2026 figures are a forecast made in {tf_when}.</li>
    <li>The {nv25}% for 2025 has two sources. Reuters reported IDC’s count. Enflame, a Chinese maker of AI chips, gives the same {nv25}% in its prospectus, from IDC’s data and its own sales. English in round brackets is ours, not an official translation.</li>
    <li>Not every estimate is drawn. Bernstein, a research and brokerage firm, by {L("bernstein", f"the Associated Press’s report of {fmt(d_bern)}")}, {qm(Q["bernstein"])}, where IDC’s data give {nv25}%. It is another measure, so it is not drawn.</li>
    <li>Not like for like on the Chinese side. For 2025 the report gives all Chinese makers together ({cn25}%). For 2026 it names {words[len(named)]}, whose shares, each rounded, add up to about {named_sum}% (our addition), and leaves {rest}% not broken down (our subtraction). The report says: {qm(Q["h2026.tracked"])}, and gives no share for the others. So the Chinese makers’ whole share in 2026 is not given.</li>
    <li>Huawei’s share in 2025 is not given as a percentage. The report says it led the Chinese makers, {qm(Q["y2025.huawei"])}.</li>
    <li>What the {nv26}% counts is not fully known: {qm(Q["h2026.notspecified"])}.</li>
    <li>Nvidia’s chief executive has put it lower, with no period or count given. Reuters, {fmt(d0)}, writes that he {qm(Q["before.warned"])}, {qm(Q["before.zero"])}; it does not say when he said it.</li>
    <li>AMD appears in the 2025 count only ({amd}%). The 2026 report does not mention AMD, so nothing is drawn for it there.</li>
    <li>A share of chips shipped in a period is not a share of chips in use.</li>
   </ul>
  </section>
 </div>
</div>
</body>
</html>
'''
    # ours: the rest of 100 and the sum of the named Chinese makers (both made above); 0 to 100 are the axis
    A.guard(page, Q, ours=[rest, named_sum, 0, 25, 50, 75, 100], dates=[fmt(d0), fmt(d1), fmt(d2), fmt(d_enf), tf_when, fmt(d_bern)])
    # round 10 (readers' leads on the public page): wordings replaced
    # round 12 (readers of the seventh version): the shares are not all of chips sold; each IDC column's own measure is named
    assert 'AI accelerator cards' in Q['y2025.total'] and 'market for data-centre AI chips' in Q['h2026.nvidia'], 'control: the two reports name their measures so'
    for banned in ('is a description, with no date', 'is the least the Chinese makers held', 'The 2025 share has two sources', 'has put it lower. Reuters',
                   'who sold them', 'at one reading', 'not published',
                   # round 13 (both readers of the eighth): no fall from one IDC measure to the other in the headline
                   'share fell from', 'Huawei reached'):
        assert banned not in page, f'the page still says "{banned}"'
    assert 'Nothing here is on the record' not in page and 'one series' in page
    out = HERE / 'share.html'
    out.write_text(page, encoding='utf-8'); print('written', out, len(page), 'bytes')
    print(f'shares drawn: before {b95}; 2025 Nvidia {nv25}, AMD {amd}, Chinese makers {cn25}; Jan to Jun 2026 Nvidia {nv26}, Huawei {hw}, ' + ', '.join(f'{r["label"]} {r["share"]}' for r in more) + f', not broken down {rest} (100 less the rest); named Chinese makers together {named_sum}')
    print('TrendForce, apart: ' + '; '.join(f'{y} ' + ', '.join(f'{r["who"]} {r["share"]}' for r in T[y]) for y in sorted(T)))
    if '--png' in sys.argv:
        A.png(out, [('#fig', HERE / 'share.png')], width=1256, height=1000, css=A.FIG_EXPORT, fits=[('.fine', '.card'), ('.key', '#fig'), ('.card', '#fig'), ('.imgnote', '#fig'), ('.tfbar i span', '.tfbar i'), ('.tfrow', '.card'), ('.tfsrc', '.card')])


main()
