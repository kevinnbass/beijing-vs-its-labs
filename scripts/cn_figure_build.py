# Repository copy. Changed from the working copy: paths only (README.md, "Files changed from the working copies").
"""Build the figure "Beijing vs. its labs" (China chip-policy project).

Run: python3 -I scripts/cn_figure_build.py                         checks every quotation, writes the page
     python3 scripts/cn_figure_build.py --png      the same, then exports PNG images of it (needs Playwright)
Reads figure/figure_data.txt (its header explains the format). Every "Q" and "!" line
must be found in its saved copy (sources/<id>), or nothing is written. Writes, in that figure folder:
  beijing_vs_labs.html       the page (self-contained apart from two web fonts)
  figure_events.tsv          the numbered events as drawn (number, date, lane, kind, source, address, saved id)
  beijing_vs_labs_*.png      with --png: the whole figure, and the dated strip alone
The page is a build product: a rebuild replaces it. Numbers on the page come from the data file, the project's tables
and this script only. Tables read (research/cn_chip_policy_20261120/tables/): house_licence_table.tsv (the House
committee's licence table), provinces_31.tsv (the 31 provincial-level governments), chip_evaluations.tsv (the state
evaluation lists), state_media_items.tsv (the census of state and Party media items). The local-voucher rows are in
vouchers() below, drawn from tables/local_vouchers.tsv and tables/local_vouchers_more.tsv (agent L28's table), every rate a "!" line.
Notes in the template name records as %%REC:<saved id>%%; the build puts in the record's number.
Records are numbered by date, Beijing's rows first, then the companies'; a block with an "N" line keeps the number given
there (core edit 7, Nov 25, 2026: record 62, added after the figure was made public, so that no record changed its number).
Before the page is called done or published: scripts/render_and_look.py (look at every screenshot).
Fourth edit (Nov 23, 2026, agent F1): the drafter D4's changes (loose_ends/D4_figure), checked and corrected by F1
(loose_ends/F1_figure_build/CHANGES.txt).
"""
import html, json, re, sys
from collections import Counter
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import cn_srclib as L   # noqa: E402

F = ROOT / 'figure'
TB = ROOT / 'tables'
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
LANES = {'BH': ('Beijing', 'holds Nvidia back', 'away'), 'BL': ('Beijing', 'lets Nvidia in', 'toward'),
         'CN': ('The companies', 'reach for Nvidia', 'toward'), 'CH': ('The companies', 'turn to home-made chips', 'away')}
ORDER = ['BH', 'BL', 'CN', 'CH']
esc = html.escape


def smart(s):
    return re.sub(r'"([^"]*)"', '“\\1”', s).replace("'", '’')


def fmt(d): return f'{MON[d.month - 1]} {d.day}, {d.year}'


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
            cur = dict(lane=lane, kind=kind, date=date.fromisoformat(d), dl=None if dl == '-' else dl.replace('_', ' '), sid=sid, T='', S='', Q='', E='', U='', C='', N='')
            evs.append(cur)
        elif ln.startswith('! '):
            sid, q = ln[2:].split(' | ', 1); checks.append((sid.strip(), q.strip()))
        elif ln[:2] in ('T ', 'S ', 'Q ', 'E ', 'U ', 'C ', 'N '):
            cur[ln[0]] = smart(ln[2:].strip()) if ln[0] in 'TSC' else ln[2:].strip()
        else: sys.exit(f'line {n} not understood: {ln[:60]}')
    return evs, checks


def verify(evs, checks):
    bad = []
    for e in evs:
        if not (e['T'] and e['S'] and e['Q']): bad.append(f"incomplete block {e['sid']}")
        elif not L.has(e['Q'], e['sid']): bad.append(f"NOT FOUND in {e['sid']}: {e['Q'][:70]}")
    for sid, q in checks:
        if not L.has(q, sid): bad.append(f'NOT FOUND in {sid}: {q[:70]}')
    assert not L.has('this sentence was never written by anyone at all', evs[0]['sid']), 'the control quotation was found: the check cannot fail'
    return bad


def number(evs):
    """Number the records by date, Beijing's rows first and then the companies', except a record with an "N" line, which
    keeps the number given there (core edit 7, Nov 25, 2026: a record added after the figure was made public takes the
    next free number, so no earlier record changes its number). Returns each side's records by date, fixed ones included,
    for the lists under the chart."""
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
    out.append(f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="strip-t strip-d"><title id="strip-t">Dated record, 2023 to November 2026</title>'
               f'<desc id="strip-d">Each numbered mark is one dated record, listed below the chart. Four rows: Beijing holds Nvidia back, Beijing lets Nvidia in, the companies reach for Nvidia, the companies turn to home-made chips.</desc>')
    out.append(f'<rect class="era" x="{GL}" y="{top}" width="{xb - GL:.1f}" height="{bottom - top}"/>')
    ticks = [(date(2023, 1, 1), '2023'), (date(2024, 1, 1), '2024')] + [(date(y_, m, 1), (f'{MON[m - 1]} {y_}' if m == 1 else MON[m - 1])) for y_ in (2025, 2026) for m in (1, 4, 7, 10)]
    for d, lab in ticks:
        x = X(d); strong = d.month == 1
        out.append(f'<line class="grid{" yr" if strong else ""}" x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom + 6}"/><text class="tick{" yr" if strong else ""}" x="{x + 4:.1f}" y="{bottom + 22}">{lab}</text>')
    out.append(f'<text class="eranote" x="{GL + 6}" y="{bottom + 37}">2023 and 2024 are drawn narrower</text>')
    # The third flag: Nvidia, Nov 17, 2026: "we are no longer shipping licensed Hopper Data Center products to China";
    # Reuters: "The Hopper family includes the H200" (both "!" lines). Why it stopped is not said here.
    for d, lab, anchor in ((date(2025, 7, 15), 'Jul 2025 · US clears H20 sales again', 'end'), (date(2025, 12, 8), 'Dec 8, 2025 · US allows the H200', 'start'), (date(2026, 11, 17), 'Nov 17, 2026 · H200 shipments stop', 'end')):
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
        out.append(f'<a href="#e{e["n"]}" class="pin {e["dir"]} {"solid" if e["solid"] else "hollow"}" data-n="{e["n"]}" data-tip="1" aria-label="{e["n"]}. {esc(e["when"])}: {esc(e["T"], quote=True)}">'
                   f'<circle cx="{e["x"]:.1f}" cy="{cy:.1f}" r="{R}"/><text x="{e["x"]:.1f}" y="{cy + 4:.1f}">{e["n"]}</text></a>')
        if e['C']:                                         # a short label beside the mark: "start|end dx dy words"
            anchor, dx, dy, words = e['C'].split(' ', 3)
            out.append(f'<text class="call" x="{e["x"] + float(dx):.1f}" y="{cy + float(dy):.1f}" text-anchor="{anchor}">{e["n"]} · {esc(words)}</text>')
    out.append('</svg>')
    return '\n'.join(out)


# ---------- panels ----------
def pin(e, tip=True):
    return f'<a href="#e{e["n"]}" class="p {e["dir"]} {"solid" if e["solid"] else "hollow"}" data-n="{e["n"]}"{" data-tip=1" if tip else ""} aria-label="record {e["n"]}">{e["n"]}</a>'


def by(evs, sid, lane=None):
    m = [e for e in evs if e['sid'] == sid and (lane is None or e['lane'] == lane)]
    assert len(m) == 1, (sid, lane, len(m)); return m[0]


def hfac():
    """The House committee's table (by its summary, a BIS summary; status as of May 11, 2026): sums by exporter, status and
    location, made here from tables/house_licence_table.tsv (54 rows, read twice from the page images and checked
    against the text layer by agent L04). The totals must equal the summary's own figures, which "!" lines check in the
    saved summary. The table does not say which chip each row is (the summary: Nvidia's H200 and AMD's MI325X); the
    bars say "Nvidia as exporter". RWA is "Returned without action" on the export bureau's own pages ("!" line)."""
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
    places = ', '.join(h['abroad_places'][:-1]) + ' and ' + h['abroad_places'][-1]
    rows = [  # label, value text, chips (for the width), class, note, events
        ('Ordered by Chinese companies for 2026', 'more than 2,000,000', 2_000_000, 'toward', 'Reuters, Dec 31, 2025', [by(evs, 'cn-labs-h200-two-million-202512-relay1-wayback')]),
        ('Approved by Washington: Nvidia as exporter', f(h['appr_nv'][0]), h['appr_nv'][0], 'us',
         f'in {h["appr_nv"][1]} applications, each marked “Approved, not shipped” at May 11, 2026. With AMD’s comparable chip '
         f'({f(h["appr_amd"][0])} in {h["appr_amd"][1]} applications) the count is {f(h["appr"][0])}. The table “H200 License and Equivalent Application Status as of May 11, 2026”, '
         'released by the House Foreign Affairs Committee, Nov 19, 2026; the sums are mine', []),
        ('Returned by Washington without action: Nvidia as exporter', f(h['rwa_nv'][0]), h['rwa_nv'][0], 'us',
         f'in {h["rwa_nv"][1]} applications, among them all {h["abroad"][1]} for consignees in {places} ({f(h["abroad"][0])} chips), named for ByteDance, BytePlus, TikTok and Alibaba. '
         f'With AMD’s {h["rwa_amd"][1]}, {f(h["rwa"][0])} of the table’s {f(h["all"][0])} chips. The table gives no reasons. Same table', []),
        ('Approved by Beijing, with conditions', 'more than 400,000', 400_000, 'toward', 'for ByteDance, Alibaba and Tencent. Reuters, Jan 28, 2026', [by(evs, 'ms-bj-20260128-h200-nod-standard')]),
        ('Total Beijing was weighing by July', 'fewer than 200,000', 200_000, 'toward', 'The Information, through Reuters, Jul 8, 2026', [by(evs, 'cn-acts-reuters-ti-cap-20260708-relay1')]),
        ('Reached the two buyers named', 'about 10,000 each', 20_000, 'toward', 'ByteDance and Tencent (Financial Times, through Reuters, Aug 18, 2026); several firms by November (Reuters, Nov 5, 2026)', [by(evs, 'cn-tolerate-reutersaug26-relay1-wayback')]),
        ('Stored in Hong Kong, awaiting shipment to China', 'about 600,000', 600_000, 'away', 'as Beijing “withholds approval for large-scale imports”. Reuters, Nov 5, 2026', [by(evs, 'cn-clips-evidence-1')]),
    ]
    out = ['<div class="bars">']
    for lab, val, n, cls, note, es in rows:
        head, _, last = lab.rpartition(' ')        # the last word and the marks stay on one line (LOOK_REPORT_3 fault 17)
        lab_h = f'{esc(head)} <span class="nw">{esc(last)}{chr(160)}{"".join(pin(e) for e in es)}</span>' if es else esc(lab)
        out.append(f'<div class="bar-row"><div class="bar-lab">{lab_h}</div>'
                   f'<div class="bar-track"><i class="{cls}" style="--f:{n / 2_000_000:.4f}"></i><b>{esc(val)}</b></div>'
                   f'<div class="bar-note">{esc(note)}</div></div>')
    out.append('</div>')
    return '\n'.join(out), h


def share():
    rows = [('Before US curbs tightened', [('toward', 95, 'Nvidia about 95%'), ('rest', 5, '')], 'Nvidia: about 95% of China’s advanced chip market.', 'Reuters, May 14, 2026'),
            ('2025', [('toward', 55, 'Nvidia 55%'), ('other', 4, ''), ('away', 41, 'Chinese makers 41%')],
             'Nvidia 55%, AMD 4%, Chinese makers 41% of AI accelerator cards shipped. By IDC’s data and its own sales, Enflame’s prospectus puts Nvidia at about 2.2 million cards of about 4 million.',
             'IDC, reported by Reuters, Apr 1, 2026; Enflame’s prospectus, Sept 2026'),
            ('Jan to Jun 2026', [('toward', 34, 'Nvidia 34%'), ('away', 28, 'Huawei 28%'), ('rest', 38, 'others 38%')], 'Nvidia 34%, Huawei 28%. In the other 38% the report names T-Head 7%, Cambricon 5%, Kunlunxin 4% and Hygon 3%; the remaining 19% (my subtraction) is not broken down.', 'IDC, reported by Reuters, Oct 13, 2026')]
    out = ['<div class="share">']
    for lab, segs, cap, src in rows:
        out.append(f'<div class="sh-row"><div class="sh-lab">{esc(lab)}</div><div class="sh-bar" role="img" aria-label="{esc(cap, quote=True)}">' +
                   ''.join(f'<i class="{c}" style="flex:{w}"></i>' for c, w, _ in segs) + '</div>'
                   '<div class="sh-keys">' + ''.join(f'<span style="flex:{w}">{esc(t)}</span>' for _, w, t in segs) + '</div>'
                   f'<div class="sh-cap">{esc(cap)} <span class="srcn">{esc(src)}</span></div></div>')
    out.append('<div class="sh-cap">Grey is AMD (4% in 2025). Hatched is the part the report does not break down.</div>')
    out.append('</div>')
    return '\n'.join(out)


def revenue():
    """Nvidia's revenue from direct customers headquartered in China and Hong Kong, by quarter, in millions of dollars.
    Every number is a cell of a filing's own table (checked by the "!" lines at the end of figure_data.txt); the two
    fourth quarters are a year's figure less its first nine months, computed here."""
    q = [('2024-10-27', 8142, '', 'man-ms-sec-10q-2025-10'),
         ('2025-01-26', 25048 - 17230, '25,048 for the year less 17,230 for its first nine months', 'man-ms-sec-10k-fy2026'),
         ('2025-04-27', 9659, '', 'man-ms-sec-10q-2026-04'),
         ('2025-07-27', 3985, '', 'man-ms-sec-10q-2026-07'),
         ('2025-10-26', 2973, '', 'man-ms-sec-10q-2025-10'),
         ('2026-01-25', 19677 - 16617, '19,677 for the year less 16,617 for its first nine months', 'man-ms-sec-10k-fy2026'),
         ('2026-04-26', 4550, '', 'man-ms-sec-10q-2026-04'),
         ('2026-07-26', 7880, '', 'man-ms-sec-10q-2026-07'),
         ('2026-10-25', 11050, '', 'ms-p3-nvda-8k-20261117-pdf')]
    mx = max(v for _, v, _, _ in q)
    bn = lambda v: str((Decimal(v) / 1000).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
    said = '; '.join(f'{fmt(date.fromisoformat(d))}: {v:,}' for d, v, _, _ in q)
    out = [f'<div class="revwrap"><div class="rev" role="img" aria-label="Millions of dollars by quarter ended. {esc(said, quote=True)}">']
    for d, v, how, sid in q:
        dt = date.fromisoformat(d)
        tip = f'Quarter ended {fmt(dt)}: ${v:,} million' + (f' (my subtraction: {how})' if how else '')
        out.append(f'<div class="rv" title="{esc(tip, quote=True)}"><b>{bn(v)}{"*" if how else ""}</b><i style="--h:{v / mx:.4f}"></i><span>{MON[dt.month - 1]}<em>{dt.year}</em></span></div>')
    out.append('</div>')
    docs = [('man-ms-sec-10q-2025-10', 'quarter ended Oct 26, 2025'), ('man-ms-sec-10k-fy2026', 'year ended Jan 25, 2026'), ('man-ms-sec-10q-2026-04', 'quarter ended Apr 26, 2026'),
            ('man-ms-sec-10q-2026-07', 'quarter ended Jul 26, 2026'), ('ms-p3-nvda-8k-20261117-pdf', 'results filed Nov 17, 2026')]
    out.append('<p class="fine">Quarter ended in the month shown. * My subtraction: the year’s figure less its first nine months. Nvidia’s reports: ' +
               ', '.join(f'<a href="{url(sid)}">{esc(lab)}</a>' for sid, lab in docs) + '.</p>')
    # Nvidia's own words on the latest quarter's licensed sales ("!" lines on cn-o38-nvda-q3fy27-call-transcript-pdf)
    out.append('<p class="fine">Of the latest quarter Nvidia said that “Q3 sales of licensed Hopper Data Center products to China was $2.4 billion” '
               'and that “we are no longer shipping licensed Hopper Data Center products to China” '
               f'(<a href="{url("cn-o38-nvda-q3fy27-call-transcript-pdf")}">results call, Nov 17, 2026</a>). It did not say why.</p></div>')
    return '\n'.join(out)


def provinces():
    """The 31 provincial-level governments by what their published plans were found to set: counted here from
    tables/provinces_31.tsv (agent L16, with L25's changes; Chongqing's 2026 plan, cn-o39-chongqing-hub-plan-2026-wayback,
    sets no share). The eight shares measure different things, so they are listed with what each counts, never drawn as
    one series. Each share's words are a "!" line."""
    pr = table('provinces_31.tsv')
    cnt = Counter(r['result'] for r in pr)
    assert len(pr) == 31 and sum(cnt.values()) == 31 and set(cnt) == {'share', 'plan_no_share', 'account_only', 'not_reached'}, cnt
    one = lambda k: [r['government'] for r in pr if r['result'] == k]
    acc, nr = one('account_only'), one('not_reached')
    seg = [('away', cnt['share'], f'{cnt["share"]} set a share'), ('rest', cnt['plan_no_share'], f'{cnt["plan_no_share"]} have a plan read, with no share'),
           ('other', cnt['account_only'], f'{cnt["account_only"]} known only from accounts of its plan ({", ".join(acc)})'),
           ('none', cnt['not_reached'], f'{cnt["not_reached"]} not reached ({", ".join(nr)})')]
    shares = [  # government, share as written, of what and by when, how it is worded or held, saved id
        ('Jiangsu', '70% or more', 'of chips in new computing centres, by 2030 (50% for 2025)', 'marked indicative (预期性)', 'cn-factions-jiangsu-plan'),
        ('Guangdong', '70%', 'of newly added computing, by the end of 2025', 'strives for (力争); a plan of nine bodies', 'cn-o39b-guangdong-yuesuan-2024'),
        ('Tianjin', 'over 60%', 'of chips in the city’s computing centres, by 2026', '', 'cn-o39-tianjin-plan-2024'),
        ('Hebei', '60% or more', 'of newly added computing software and hardware, independently controllable (自主可控), by 2025', 'the province’s own page', 'cn-o39-hebei-opinion-2024-wayback'),
        ('Shanghai', 'over 50%', 'of chips in new intelligent-computing centres, by 2025', 'a copy on another site', 'cn-policy-shanghai-domestic-target'),
        ('Sichuan', 'over 50%', 'of computing equipment', 'strives for (力争); a copy on another site', 'cn-factions-sichuan50'),
        ('Inner Mongolia', '50% or more', 'of computing, by 2025, among the goals for the region’s national computing hub', '', 'cn-o39-nmg-plan-pdf-wayback'),
        ('Shandong', '90%', 'of the province’s data-centre computing, by 2025', 'a newspaper’s account of the plan', 'cn-o39-shandong-network-2022')]
    tab = {r['government']: r['saved_ids'].split()[0] for r in pr if r['result'] == 'share'}
    assert {g: s for g, _, _, _, s in shares} == tab, ('the shares listed are not the table\'s', tab)
    lab = '; '.join(t for _, _, t in seg)
    out = [f'<div class="prov"><div class="pv-bar" role="img" aria-label="31 provincial-level governments: {esc(lab, quote=True)}.">'
           + ''.join(f'<i class="{c}" style="flex:{w}"></i>' for c, w, _ in seg) + '</div><div class="pv-keys">'
           + ''.join(f'<span><i class="k {c}"></i>{esc(t)}</span>' for c, _, t in seg) + '</div>', '<table class="pv"><tbody>']
    for g, sh, what, how, sid in shares:
        out.append(f'<tr><th>{esc(g)}</th><td class="sh">{esc(sh)}</td><td>{esc(what)}{("; " + esc(how)) if how else ""} <a class="srcn" href="{url(sid)}">source</a></td></tr>')
    out.append('</tbody></table></div>')
    return '\n'.join(out)


def evaluations():
    """AI chips on the state security-and-reliability evaluation lists, counted from tables/chip_evaluations.tsv (agent
    L14's parse of the evaluation centre's nine announcements)."""
    rows = [r for r in table('chip_evaluations.tsv') if '人工智能训练推理芯片' in r['category'] and not r['cells'].startswith('序号')]
    lists = sorted({r['page_date'] for r in rows})
    makers = {r['cells'].split(' | ')[2] for r in rows}
    assert lists == ['2026-05-26', '2026-09-20'] and len(rows) == 11 and len(makers) == 8, (lists, len(rows), len(makers))
    return len(rows), len(makers), [date.fromisoformat(d) for d in lists]


def paper(evs):
    n, m, ds = evaluations()
    rows = [('20%', 'price edge in government purchasing for goods that meet China’s home-made product standard; in force from Jan 1, 2026, and products of foreign-funded firms that meet the standard take part on equal terms', 'State Council office, Sept 2025; finance ministry, Dec 2025', 'cn-policy-domestic-product-standard-2025'),
            (f'{n} of {n}', f'AI chips that have passed the state security-and-reliability evaluation come from makers registered in China, {m} of them (lists of {MON[ds[0].month - 1]} and {MON[ds[1].month - 1]} {ds[1].year}). '
             'Only entities registered in China may apply; firms apply of their own accord, and buyers choose whether to use the results', f'evaluation centre, {MON[ds[1].month - 1]} {ds[1].year}', 'cn-le14-itsec-2026-3'),
            ('46', 'US firms whose products government buyers may not buy (not counting US-owned firms in China). Nvidia, Intel, AMD, Micron and Qualcomm are not among them', 'finance ministry, Jun 22, 2026', 'cn-le14-mof-us-firms-measures-20260622')]
    lst = L.page('cn-le14-mof-us-firms-list-20260622')       # the list read whole: the names in the row are absent; a control is present
    assert 'lockheedmartin' in lst and not any(w in lst for w in ('nvidia', '英伟达', 'intel', '英特尔', 'advancedmicro', 'amd', '超威', 'micron', '美光', 'qualcomm', '高通', '芯片')), 'the list of 46 names a chip maker'
    out = ['<div class="paper">', provinces()]
    for big, txt, when, sid in rows:
        out.append(f'<div class="pp"><b>{esc(big)}</b><span>{esc(txt)} <a class="srcn" href="{url(sid)}">{esc(when)}</a></span></div>')
    out.append('<div class="pp none"><b>None found</b><span>a published national share for home-made AI chips, or a published order not to buy Nvidia’s, in the policy pages and the national document lists read. '
               f'A draft national plan with at least 80% of its core technology home-made, AI chips included, was reported (Bloomberg, Jun 2026, through <a class="srcn" href="{url("cn-le14-tnw-295b-plan-20260609")}">relays</a>; unnamed people, who said details could change); '
               'asked about the report, the state planner gave no share and said “在具体建设过程中，市场力量将起决定性作用” (in the actual building, market forces will play the decisive role), and that it would strengthen coordination and policy guidance '
               f'(<a class="srcn" href="{url("cn-le27-ndrc-presser-20260618-json")}">press conference, Jun 18, 2026: the site’s text file</a>). '
               'Every binding purchase rule found is addressed to Party and state bodies, public institutions or public money, or, in the Micron case of 2023 (the earliest record here), to operators of critical information infrastructure.</span></div>')
    out.append('</div>')
    return '\n'.join(out)


def vouchers():
    """Local computing vouchers: the general rate a voucher or rental subsidy pays of the bill for rented computing (the rate
    for an ordinary applicant; a higher rate for a named kind of firm, whatever the chip, is in the row's note), for home-made
    computing against other computing, as each rule states it (one measure throughout). Rule for a row (agent F1,
    applied row by row to tables/local_vouchers.tsv, agent L15, and tables/local_vouchers_more.tsv, agent L28): a local rule in force (not a draft, a plan or an application guide) whose official text or a full copy
    is saved under research/primary, whose words the checker finds, and which states a share of the bill for rented
    computing. One row per government: its latest such rule of general application; an earlier rule of the same
    government, or a later one for one class of firm only (Wuhan's of Feb 2026, for one-person AI firms), goes in the row's
    note. Every rate and date is a "!" line. Left out, and said so under the chart: a press account only (Chengdu),
    application guides (Beijing city; Nanjing), rules no longer in force or without a share of the bill (Longgang district;
    Guangzhou's Huangpu district; Hangzhou's rule of 2026, a share of R&D spending), a copy not yet saved (Xiamen), and drafts.
    Since core edit 6 (Nov 24, 2026, at the owner's word) the list also holds the four rules found that day which the same
    rule counts: Sichuan (a voucher for home-made computing only; its text held as a news site carries it), Wuhu, Suzhou and
    Tianjin. A rule that pays for home-made computing only is drawn as one orange dot. The counts are asserted against
    the count by script over both tables (atlas/core_edit/p6_work_4/vcount.py)."""
    rows = [  # place, rule (month on its page), home-made %, other %, saved id, note
        ('Hangzhou city', 'Jul 2024', 30, 20, 'cn-counter-b4-2', ''),
        ('Zhejiang province', 'Apr 2025', 30, 10, 'cn-le25-zhejiang-ai-measures-2025-smartcity', 'guidance to places that issue vouchers; in force from May 31, 2025; a copy on another site'),
        ('Wenzhou city', 'Aug 2025', 30, 10, 'cn-le15-zj-oss-web1825-e66330', ''),
        ('Binjiang district, Hangzhou', 'Aug 2026', 60, 30, 'cn-le15-binjiang-2026-6-keceyun', 'a copy on a policy site'),
        ('Beijing E-Town, a development zone', 'Nov 2024', 30, 30, 'cn-le28-etown-29hao-20241126', 'replaced a rule of Mar 2024 that paid 40% against 30%; servers with home-made chips get a separate purchase subsidy of up to 10%'),
        ('Longhua district, Shenzhen', 'Nov 2024', 30, 30, 'cn-le28-sz-longhua-2024-20hao', ''),
        ('Shanxi province', 'Jun 2024', 20, 20, 'cn-o39b-shanxi-measures-2024-jincheng', '30% for national projects and model makers; in force from Jul 2024'),
        ('Shenzhen city', 'Dec 2024', 50, 50, 'cn-le28-sz-gxj-2024-13hao', '60% for start-ups; separate support for moving models to home-made chips'),
        ('Wuhan city', 'Feb 2025', 50, 50, 'cn-le28-wuhan-2025-3hao', 'up to 200,000 yuan; the same rate for one-person AI firms in a rule of Feb 2026'),
        ('Qingdao city', 'Mar 2026', 20, 20, 'cn-le28-qingdao-2026-9hao-smartcity', 'the same rate as its rule of Mar 2025; a copy on another site'),
        ('Shanghai city', 'Jul 2025', 30, 30, 'cn-le15-sheitc-8cea38', 'up to 100% for a year at most, city and districts together, for early-stage and small firms; building support, up to 10%, for home-made computing only'),
        ('Qiaokou district, Wuhan', 'Aug 2025', 50, 50, 'cn-le28-wuhan-qiaokou-2025-1hao', 'on top of the city’s'),
        ('Hongshan district, Wuhan', 'Sept 2025', 20, 20, 'cn-le28-wuhan-hongshan-2025-2hao', 'for small and medium firms'),
        ('Shandong province', 'May 2025', 5, 5, 'cn-le28-shandong-ai-measures-2025-smartcity', 'a copy on another site'),
        ('Hunan province', 'Oct 2025', 30, 30, 'cn-le28-hunan-aiplus-smartcity', 'a copy on another site'),
        ('Sichuan province', 'Aug 2026', 20, 0, 'cn-ga05-sichuan-compute-net-measures-jiemian', '30% for start-ups, 40% for one-person AI firms; the text as a news site, Jiemian, carries it, without number or date; the month is that of the reports'),
        ('Wuhu city', 'Jul 2026', 25, 25, 'cn-ga04-wh-voucher-rule-2026-24hao', '45% for firms in future industries, 70% for small firms in incubators'),
        ('Suzhou city', 'Jan 2026', 30, 30, 'cn-ga04-sz-suzhou-aiplus-2026-18hao', 'for technology R&D firms; in force from Jan 31, 2026, by the city’s own reading; its rule of Feb 2025 paid 20%'),
        ('Tianjin city', 'May 2025', 10, 10, 'cn-ga04-tj-voucher-rule-sina-20250514', 'the text as a page on Sina carries it, dated May 14, 2025'),
    ]
    mx = 60
    assert max(max(hm, ot) for _, _, hm, ot, _, _ in rows) <= mx
    only = [r for r in rows if r[3] == 0]                    # a rule that pays for home-made computing only
    ti = [r for r in rows if r[2] != r[3] and r[3] > 0]; one = [r for r in rows if r[2] == r[3]]
    # the count by script of the published rule over both voucher tables (atlas/core_edit/p6_work_4/vcount.py; Nov 24, 2026: 19 counted, 4 tiered, 1 home-made only, 14 one rate)
    assert (len(rows), len(ti), len(only), len(one)) == (19, 4, 1, 14), (len(rows), len(ti), len(only), len(one))
    assert all(hm > ot for _, _, hm, ot, _, _ in ti), 'a rule pays more for other computing'
    key = lambda r: (int(r[1].split()[-1]), MON.index(r[1].split()[0]))
    ti.sort(key=key); one.sort(key=key)

    def row(place, when, hm, ot, sid, note):
        if ot == 0:
            x = hm / mx
            dots = f'<i class="vd away" style="--x:{x:.4f}"></i><b class="vn side" style="left:calc({x * 100:.2f}% + 11px)">{hm}%, home-made computing only</b>'
        elif hm == ot:
            x = hm / mx
            side = f'right:calc({(1 - x) * 100:.2f}% + 11px)' if x > 0.6 else f'left:calc({x * 100:.2f}% + 11px)'
            dots = f'<i class="vd both" style="--x:{x:.4f}"></i><b class="vn side" style="{side}">{hm}% for all</b>'
        else:
            dots = (f'<i class="vl" style="--a:{ot / mx:.4f};--b:{hm / mx:.4f}"></i><i class="vd toward" style="--x:{ot / mx:.4f}"></i>'
                    f'<i class="vd away" style="--x:{hm / mx:.4f}"></i><b class="vn" style="--x:{ot / mx:.4f}">{ot}%</b><b class="vn" style="--x:{hm / mx:.4f}">{hm}%</b>')
        lab = f'home-made {hm}%, no voucher for other computing' if ot == 0 else (f'home-made {hm}%, other {ot}%' if hm != ot else f'{hm}% for all computing')
        return (f'<div class="vr"><div class="vlab">{esc(place)} <a class="srcn" href="{url(sid)}">{esc(when)}</a>{("<span class=vnote>" + esc(note) + "</span>") if note else ""}</div>'
                f'<div class="vt" role="img" aria-label="{esc(place, quote=True)}: {lab}">{dots}</div></div>')
    axis = '<div class="vr axis"><div></div><div class="vt">' + ''.join(f'<span style="--x:{v / mx:.4f}">{v}%</span>' for v in (0, 20, 40, 60)) + '</div></div>'
    out = ['<div class="vkey"><span><i class="sw away"></i>home-made computing</span><span><i class="sw toward"></i>other computing</span><span><i class="sw both"></i>one rate for all</span></div>',
           '<div class="vgrid">',
           f'<div class="vgrp va"><h3>Pay more for home-made computing: {len(ti)}</h3>' + ''.join(row(*r) for r in ti) + f'<h3>Pay for home-made computing only: {len(only)}</h3>' + ''.join(row(*r) for r in only) + axis + '</div>',
           f'<div class="vgrp vb"><h3>One rate for all computing: {len(one)}</h3>' + ''.join(row(*r) for r in one) + axis + '</div>',
           f'<p class="fine vf">{len(ti)} of the {len(rows)} local governments shown pay more for home-made computing and still pay for other computing; {len(only)}, Sichuan province, pays for home-made computing only (its measures are held as the news site Jiemian carries their text, without number or date); the other {len(one)} pay one rate for all. The rate shown is the one for an ordinary applicant. '
           'One row per government: its latest general rule found that states a share of the bill (a later rule for one class of firm is in the row’s note); these are the rules found and read, not a census. '
           'Left out: rules known only from the press (Chengdu, 50% against 30%), application guides (Beijing city; Nanjing), rules no longer in force or with no share of the bill (Longgang district, Shenzhen, among them), '
           'not yet among the saved pages (Xiamen), and drafts. '
           'Support for building or buying with home-made chips only is separate: Beijing city’s plan for 2024 to 2027 supports, by a share of the investment, “采购自主可控GPU芯片开展智能算力服务的企业” (firms that buy independently controllable GPU chips to provide computing services). '
           'The tiers are the rules’ own words: 国产 or 自主 (home-made, independent) against 非国产, 非自主 or 其他 (other).</p>', '</div>']
    return '\n'.join(out), len(ti), len(rows)


def bodies(evs):
    def P(*keys):
        return ''.join(pin(by(evs, k[0], k[1]) if isinstance(k, tuple) else by(evs, k)) for k in keys)
    held = [('Cyberspace regulator', P('cn-policy-cac-h20-original', ('man-cn-ft-20250821-regulators', 'BH'), 'cn-clips-alibaba-20f', 'man-cn-ft-20250917-6000d')),
            ('State planner (NDRC)', P(('man-cn-ft-20250821-regulators', 'BH'), 'cn-policy-ndrc-chip-adaptation-2026')),
            ('Industry ministry', P('cn-factions-bloomberg-flexibility-202409-relay1', 'cn-le11-ft-h20justify-aggregoctt', ('man-cn-ft-20250821-regulators', 'BH'))),
            ('Vice Premier Ding Xuexiang’s chip committee, as the Journal describes it', P('man-cn-factions-wsj-ding')),
            ('Security ministry', P('cn-acts-mss-xinhua-20250721')),
            ('State media (the state broadcaster’s account)', P('cn-le13-yuyuan-qq-20250810b')),
            ('Customs', P('man-cn-ft-20251009-customs', 'cn-acts-reuters-customs-20260114')),
            ('Finance and industry ministries (a purchase rule for Party and state bodies’ desktop computers)', P('cn-policy-desktop-2023'))]
    let = [('Commerce ministry', P('cn-policy-wang-nvidia', 'cn-policy-h20-mofcom', 'cn-tolerate-mof', 'cn-acts-mofcom-20261117')),
           ('Premier Li Qiang', P('cn-xi-round-f-6')),
           ('Vice Premier He Lifeng', P('cn-policy-he-welcomes')),
           ('“Industry and commerce ministries”, as Reuters put it', P('cn-acts-reuters-deepseek-20260130')),
           ('Industry ministry, as The Information reported its intention', P('cn-acts-reuters-rtx5500-20260927'))]      # record 62 (core edit 7, Nov 25, 2026)
    firm = [('Market regulator: an antitrust case against Nvidia the company', P('cn-policy-samr-open-original', 'cn-policy-samr-further-original'))]
    col = lambda title, cls, rows: (f'<div class="bcol"><h4><i class="sw {cls}"></i>{title}</h4><ul>' + ''.join(f'<li><span>{esc(n)}</span><span class="pins">{p}</span></li>' for n, p in rows) + '</ul></div>')
    return ('<div class="bodies">' + col('Held Nvidia back, or steered buyers to home-made chips', 'away', held) + col('Let it in, or welcomed it', 'toward', let) + '</div>'
            '<div class="bodies one">' + col('Acted against Nvidia the company', 'away', firm) + '</div>'
            '<p class="fine">The Financial Times (Nov 13, 2026, citing unnamed people): security-focused officials within the cyberspace regulator and the security ministry “viewed dependence on Nvidia as a strategic vulnerability”, '
            'the commerce ministry “favoured imports”, and the 2025 push to restrict “was led by the National Development and Reform Commission”. '
            f'The US Trade Representative, Nov 20, 2026 (<a href="{url("cn-le01-greer-bbg-20261120-youtube")}">Bloomberg Television</a>; machine captions, not checked by ear, 01:06 to 01:35): it is “not as monolithic as people would have you believe”; '
            'in his “own analysis” there are some who think “we’d like to have access” and “others who think, well, we don’t want American chips anyway”. '
            'The two caption tracks break the sentence differently, so whether he puts the split inside the government is not settled.</p>'
            '<p class="fine">The market regulator’s Party group lists the Nvidia case, with its cases on Qualcomm and DuPont China, under “坚决落实党中央重大决策部署” (carrying out the Party centre’s major decisions) and “敢于斗争” (daring to struggle) '
            f'(<a href="{url("cn-media-party-samr-september")}">Party members’ paper, Sept 24, 2026</a>). Nvidia’s reports say the preliminary finding concerns the “degraded products” US export controls required it to offer the Chinese market. '
            'A standing rule cuts the other way: the regulator’s 2020 approval of Nvidia’s Mellanox purchase obliges Nvidia to keep supplying its accelerators '
            'to the Chinese market, unless lifted since (the parties may apply to lift the conditions six years after they took effect) '
            f'(<a href="{url("cn-policy-mellanox-conditions")}">decision</a>).</p>')


def state_media():
    """The state and Party media items on Nvidia chips (tables/state_media_items.tsv: agent L13's census, rows 1 to 42, and
    agent GA02's rows 43 to 75, found by searches and links): how many, how many only warn, how many of those are dated up to
    Sept 24, 2025 (the burst after the summons) with their first and last dates, and how many are later."""
    rows = table('state_media_items.tsv')
    st = Counter(r['stance'] for r in rows)
    warns = sorted(date.fromisoformat(r['date']) for r in rows if r['stance'] == 'warns')
    iso = sorted(date.fromisoformat(r['date']) for r in rows if re.fullmatch(r'\d{4}-\d\d-\d\d', r['date']))
    win = [d for d in warns if d <= date(2025, 9, 24)]; late = [r for r in rows if r['stance'] == 'warns' and date.fromisoformat(r['date']) > date(2025, 9, 24)]
    # the counts of atlas/core_edit/p6_work_5/count_census.py over the table (Nov 24, 2026), and what the template says of the later warnings
    assert (len(rows), st['warns'], len(win), len(late)) == (75, 14, 11, 3) and all(r['outlet'].startswith('Global Times') and r['date'].startswith('2026') for r in late), (len(rows), st)
    return dict(SM_N=str(len(rows)), SM_W=str(len(warns)), SM_WIN=str(len(win)), SM_WLATE={3: 'three'}[len(late)], SM_W0=fmt(warns[0]), SM_W1=fmt(win[-1]), SM_MIX=str(st['mixed']),
                SM_FROM=f'{MON[iso[0].month - 1]} {iso[0].year}', SM_TO=f'{MON[iso[-1].month - 1]} {iso[-1].year}')


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
    b, c = number(evs)
    nolink = [e['sid'] for e in evs if not e['url']]
    tip = {e['n']: dict(w=e['when'], l=' '.join(LANES[e['lane']][:2]), t=e['T'], q=e['E'] or e['Q'], tr=bool(e['E']), s=e['S'], k=('On the record' if e['solid'] else 'Press report, unnamed sources')) for e in evs}
    page = (F / 'template.html').read_text(encoding='utf-8')
    bars_h, h = bars(evs)
    vouch_h, n_tiered, n_vouch = vouchers()
    parts = {'STRIP': strip(evs), 'BARS': bars_h, 'SHARE': share(), 'REVENUE': revenue(), 'PAPER': paper(evs), 'BODIES': bodies(evs), 'VOUCHERS': vouch_h,
             'LEDGER': ledger(b, 'Beijing') + ledger(c, 'The companies'), 'EVJSON': json.dumps(tip, ensure_ascii=False).replace('</', '<\\/'),
             'N_EVENTS': str(len(evs)), 'N_SOLID': str(sum(e['solid'] for e in evs)), 'N_HOLLOW': str(sum(not e['solid'] for e in evs)),
             'HF_RWA': f'{h["rwa"][0]:,}', 'HF_ALL': f'{h["all"][0]:,}', **state_media()}
    for k, v in parts.items():
        assert f'%%{k}%%' in page, k
        page = page.replace(f'%%{k}%%', v)
    page = re.sub(r'%%REC:([a-z0-9-]+)%%', lambda m: str(by(evs, m.group(1))['n']), page)   # record numbers in the notes
    assert '%%' not in page, page[page.index('%%'):][:40]
    assert 'href=""' not in page, 'an empty link'
    (F / 'beijing_vs_labs.html').write_text(page, encoding='utf-8')
    with open(F / 'figure_events.tsv', 'w', encoding='utf-8') as fh:
        fh.write('n\tdate\tshown_as\tlane\tkind\tsource\taddress\tsaved_id\ttext\n')
        for e in sorted(evs, key=lambda e: e['n']):
            fh.write(f"{e['n']}\t{e['date']}\t{e['when']}\t{' '.join(LANES[e['lane']][:2])}\t{e['kind']}\t{e['S']}\t{e['url'] or ''}\t{e['sid']}\t{e['T']}\n")
    per = {k: sum(e['lane'] == k for e in evs) for k in ORDER}
    print(f'events {len(evs)} ({per}); on the record {parts["N_SOLID"]}, press reports {parts["N_HOLLOW"]}; quotations checked {len(evs) + len(checks)}, all found; control not found (as it must be)')
    print(f'tables: House table {h["all"][1]} rows ({h["all"][0]:,} chips; approved {h["appr"][0]:,}, Nvidia {h["appr_nv"][0]:,}; RWA {h["rwa"][0]:,}, Nvidia {h["rwa_nv"][0]:,}); '
          f'31 governments; evaluations {evaluations()[0]} AI chips; vouchers {n_tiered} of {n_vouch} tiered; state media {parts["SM_N"]} items, {parts["SM_W"]} warn ({parts["SM_W0"]} to {parts["SM_W1"]})')
    print('no address to link:', nolink or 'none')
    print('written', F / 'beijing_vs_labs.html', len(page), 'bytes')
    if '--png' in sys.argv:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            br = p.chromium.launch()
            pg = br.new_context(viewport={'width': 1500, 'height': 1000}, device_scale_factor=2, color_scheme='light').new_page()
            pg.goto((F / 'beijing_vs_labs.html').as_uri()); pg.evaluate('document.fonts.ready.then(() => 1)'); pg.wait_for_timeout(700)
            for sel, name in (('#figure', 'beijing_vs_labs_full.png'), ('#hero', 'beijing_vs_labs_strip.png'), ('#top', 'beijing_vs_labs_top.png')):
                pg.locator(sel).screenshot(path=str(F / name)); print('image', F / name)
            br.close()


main()
