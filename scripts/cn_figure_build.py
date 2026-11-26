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
evaluation lists), state_media_items.tsv (the census of state and Party media items). The local-voucher rows are the counted
rules of scripts/cn_voucher_classes.py (over tables/local_vouchers.tsv and tables/local_vouchers_more.tsv); vouchers() below holds
only each row's label and note; every rate and date of a note is a "!" line.
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
    # The second flag says what the post of Dec 8, 2025 says: the United States "will allow" the H200 ("!" line on
    # cn-clips-followup-3-relay1); round 12, by the session's ruling for every figure (atlas/ROUND10_BRIEF.txt).
    for d, lab, anchor in ((date(2025, 7, 15), 'Jul 2025 · US clears H20 sales again', 'end'), (date(2025, 12, 8), 'Dec 8, 2025 · US says it will allow H200', 'start'), (date(2026, 11, 17), 'Nov 17, 2026 · H200 shipments stop', 'end')):
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
    # Round 13 (Nov 26, 2026, the session's message to builder r13e): a bar whose count rests on unnamed people carries the report
    # in its own label ("Reported: ..."), as the records' titles and output A4's funnel do; the two sums of Washington's table stay.
    rows = [  # label, value text, chips (for the width), class, note, events
        ('Reported: ordered by Chinese companies for 2026', 'more than 2,000,000', 2_000_000, 'toward', 'Reuters, Dec 31, 2025', [by(evs, 'cn-labs-h200-two-million-202512-relay1-wayback')]),
        ('Approved by Washington: Nvidia as exporter', f(h['appr_nv'][0]), h['appr_nv'][0], 'us',
         f'in {h["appr_nv"][1]} applications, each marked “Approved, not shipped” at May 11, 2026. With AMD’s comparable chip '
         f'({f(h["appr_amd"][0])} in {h["appr_amd"][1]} applications) the count is {f(h["appr"][0])}. The table “H200 License and Equivalent Application Status as of May 11, 2026”, '
         'released by the House Foreign Affairs Committee, Nov 19, 2026; the sums are mine', []),
        ('Returned by Washington without action: Nvidia as exporter', f(h['rwa_nv'][0]), h['rwa_nv'][0], 'us',
         f'in {h["rwa_nv"][1]} applications, among them all {h["abroad"][1]} that give {places} as the chips’ location ({f(h["abroad"][0])} chips), named for ByteDance, BytePlus, TikTok and Alibaba. '
         f'With AMD’s {h["rwa_amd"][1]}, {f(h["rwa"][0])} of the table’s {f(h["all"][0])} chips. The table gives no reasons. Same table', []),
        ('Reported: approved by Beijing, with conditions', 'more than 400,000', 400_000, 'toward', 'for ByteDance, Alibaba and Tencent. Reuters, Jan 28, 2026', [by(evs, 'ms-bj-20260128-h200-nod-standard')]),
        ('Reported: total Beijing was weighing by July', 'fewer than 200,000', 200_000, 'toward', 'The Information, through Reuters, Jul 8, 2026', [by(evs, 'cn-acts-reuters-ti-cap-20260708-relay1')]),
        ('Reported: reached the two buyers named', 'about 10,000 each', 20_000, 'toward', 'ByteDance and Tencent (Financial Times, through Reuters, Aug 18, 2026); several firms by November (Reuters, Nov 5, 2026)', [by(evs, 'cn-tolerate-reutersaug26-relay1-wayback')]),
        ('Reported: stored in Hong Kong, awaiting shipment to China', 'about 600,000', 600_000, 'away', 'as Beijing “withholds approval for large-scale imports”. Reuters, Nov 5, 2026', [by(evs, 'cn-clips-evidence-1')]),
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
    sets no share). The nine shares measure different things, so they are listed with what each counts, never drawn as
    one series. Each share's words are a "!" line. Core edit 8 (Nov 25, 2026): Zhejiang is a ninth, by the written rule
    (a published plan that sets a share); its share is for one sector's computing and is a project target, said in its row."""
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
        ('Zhejiang', 'over 60%', 'of the computing of one sector, the province’s information and communications industry, by 2030', 'a project target (工程目标) in that sector’s five-year plan, by the provincial communications administration and development and reform commission', 'cn-ga31-cndocs-52'),
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
    """Local computing vouchers and like subsidies: the general rate a local rule pays of a firm's bill for rented or bought
    computing (the rate for an ordinary applicant; a higher rate for a named kind of firm, whatever the chip, is in the
    rule's saved copy), for home-made computing against other computing, as each rule states it (one measure throughout).
    WHICH rules are drawn, each rule's two rates and its class are not typed here: they are the counted rows of
    scripts/cn_voucher_classes.py (compute(): the published counting rule over tables/local_vouchers.tsv and
    tables/local_vouchers_more.tsv; its result is also tables/local_vouchers_classes.tsv). One row per government: its rule in
    force whose official text or a full copy is saved, whose rate words the checker finds, and which states a share of the
    bill. This function holds only what the page says of each row (SHOWN: the place, the month on its page, the saved copy
    the row links, a note); a counted row without an entry stops the build, and so does an entry for a row not counted.
    Every rate and date of a note is a "!" line of the data file.
    Voucher round 3 (Nov 25, 2026): 38 rules where 21 were drawn; the third class is "state no higher rate for home-made
    computing", and inside it Hangzhou's plan of 2025 (30% or 20% "by the type of computing facility", a type it does not
    name) is drawn apart, with its own mark, never as a one-rate rule.
    Voucher round 5 (Nov 25, 2026): 90 rules, the rules found by searches that went province by province and city by city.
    The panel is redrawn for them: the rules that favour home-made computing (pay more for it, or pay for it only) and
    Hangzhou's are full rows, each with its note; the rules of one rate are a compact list in columns, by kind of government
    (province-level, city, district or zone) and by rate, each with its place, its month linking the saved copy, its one
    rate as a dot on the same 0 to 60% scale and its number; a dagger marks a rule that gives the payment another name than
    voucher; a letter marks a note, the notes standing under the list (the notes kept are those on home-made computing and
    those the rulings ask for). The list takes more rules without redesign (its columns grow); the scale ends at 60% (a
    higher general rate stops the build at the assert below).
    Voucher round 8 (Nov 25, 2026): 91 rules. Shantou's implementing rules are counted (its month is the page's posting
    date: the page gives no date of signature); Langfang is read on the city's disclosure platform and the Zhengzhou
    Airport Zone in a capture of the zone's own page, whose signature is of Aug 2025 (the month shown until then was a
    commercial copy's)."""
    import cn_voucher_classes as VC
    R = VC.compute(); C = R['counted']
    SHOWN = {  # row of the voucher tables: place, rule (month on its page), the saved copy the row links (a saved id of the row), note
        'A3': ('Hangzhou city', 'Jun 2025', 'cn-ga31-voucherrulesmissing-40', '30% in general; for training, inference and applications on computing facilities, 30% or 20% “by the type of computing facility” (按照算力设施的不同类型), and the plan does not say which type gets which; up to 50% for small and medium firms whose intelligent-computing contracts come to 500,000 yuan a year or less; in force from Jul 15, 2025, when it repealed the rule of Jul 2024 that paid 30% for home-made and 20% for other facilities; the text on the city archives’ site'),
        'A6': ('Binjiang district, Hangzhou', 'Aug 2026', 'cn-ga31-twelve-18', 'the text on the district consultative conference’s site'),
        'A7': ('Wenzhou city', 'Aug 2025', 'cn-le15-zj-oss-web1825-e66330', ''),
        'A12': ('Shanghai city', 'Jul 2025', 'cn-le15-sheitc-8cea38', 'building support, up to 10%, for home-made computing only'),
        'A14': ('Chengdu city', 'Apr 2026', 'cn-ga31-vouchernamedrules-5', 'for 自主可控 (independently controllable) computing; small and medium firms’ rates each raised by 10%; in force from May 13, 2026; the rules on a consultancy’s page, compared by eye with the bureau’s signed file, a scan'),
        'A18': ('Sichuan province', 'Aug 2026', 'cn-ga31-unsaved-sc-338hao-fgw-wayback', '30% for start-ups under three years old, 40% for one-person AI firms; the provincial development and reform commission’s measures (川发改数据〔2026〕338号), written Aug 11 and published Aug 13, 2026'),
        'B1': ('Beijing E-Town, a development zone', 'Nov 2024', 'cn-le28-etown-29hao-20241126', 'replaced a rule of Mar 2024 that paid up to 40% and up to 30%; cloud firms buying servers with home-made chips get a separate subsidy of up to 10%'),
        'B5': ('Shenzhen city', 'Dec 2024', 'cn-le28-sz-gxj-2024-13hao', 'separate support for moving models to home-made chips'),
        'B8': ('Longhua district, Shenzhen', 'Nov 2024', 'cn-le28-sz-longhua-2024-20hao', ''),
        'B10': ('Guangzhou Development Zone and Huangpu district', 'Jun 2025', 'cn-le28-gz-huangpu-2025-7hao', ''),
        'B15': ('Hongshan district, Wuhan', 'Sept 2025', 'cn-le28-wuhan-hongshan-2025-2hao', ''),
        'B17': ('Qingdao city', 'Mar 2026', 'cn-le28-qingdao-2026-9hao-smartcity', ''),
        'B21': ('Zhejiang province', 'Apr 2025', 'cn-ga31-plantexts-1', 'guidance to places that issue vouchers; signed Apr 17, 2025 (浙政发〔2025〕10号), in force from May 31, 2025; the government’s own PDF'),
        'B34': ('Hubei province', 'Sept 2026', 'cn-ga31-plantexts-12', 'up to 3 million yuan a unit a year; one-person firms 30% whatever the computing; the text with its notice on the Wuhan Data Bureau’s site'),
        'B40': ('Wuhu city', 'Jul 2026', 'cn-ga04-wh-voucher-rule-2026-24hao', ''),
        'B42': ('Suzhou city', 'Jan 2026', 'cn-ga04-sz-suzhou-aiplus-2026-18hao', ''),
        'B44': ('Tianjin city', 'Apr 2025', 'cn-ga31-twelve-17', ''),
        'B46': ('Xinjiang region', 'May 2026', 'cn-ga31-provtexts-9', ''),
        'B47': ('Guizhou province', 'Jan 2026', 'cn-ga31-plantexts-13', 'a separate 30% for adapting to home-made computing'),
        'B48': ('Wuhan city', 'Sept 2026', 'cn-ga31-sciowhole-115', 'the Data Bureau’s voucher measures, in force from Oct 29, 2026 for one year; the city’s measures of Feb 2025, still in force, pay 50% up to 200,000 yuan whatever the chip'),
        'B49': ('Anhui province', 'Aug 2025', 'cn-ga31-voucherrulesmissing-37', ''),
        'B50': ('Liaoning province', 'Oct 2026', 'cn-ga31-voucherrulesmissing-8', ''),
        'B53': ('Hunan province', 'May 2026', 'cn-ga31-unsaved3-sciowhole114-gxt-gfxwj', 'the rules’ stated aim includes steering buyers to home-made computing first, at the same rate'),
        'B55': ('Beijing city', 'Jun 2026', 'cn-ga31-voucherrulesmissing-4', 'a supplier must be able to serve on home-made chips with home-made software: a condition on the supplier, not a higher rate and not a rule that only such service is paid'),
        'B59': ('Heilongjiang province', 'Apr 2026', 'cn-ga31-voucherrulesmissing-9', ''),
        'B61': ('Jiangsu province', 'Sept 2026', 'cn-ga31-voucherrulesmissing-11', 'a ceiling for province and city together; each city divided into districts sets its own rate inside it'),
        'B64': ('Fujian province', 'Feb 2026', 'cn-ga31-voucherrulesmissing-74', ''),
        'B66': ('Jiangxi province', 'Aug 2026', 'cn-ga31-voucherrulesmissing-15', ''),
        'B67': ('Shandong province', 'Jan 2026', 'cn-ga31-voucherrulesmissing-16', ''),
        'B69': ('Henan province', 'Aug 2025', 'cn-ga31-voucherrulesmissing-17', ''),
        'B76': ('Ningbo city', 'Mar 2026', 'cn-ga31-voucherrulesmissing-71', 'only contracts for home-made computing qualify; up to 1.5 million yuan a buyer a year; a yearly rule, its fourth voucher period ending Dec 31, 2026; read on a commercial policy platform’s page that carries the notice whole'),
        'B80': ('Xiamen city', 'Oct 2026', 'cn-ga31-voucherrulesmissing-30', ''),
        'B81': ('Tianfu New Area, Sichuan', 'Apr 2024', 'cn-ga31-voucherrulesmissing-34', ''),
        'B84': ('Hebei province', 'Nov 2026', 'cn-ga31-voucherrulesmissing-36', ''),
        'B91': ('Shanxi province', 'Sept 2026', 'cn-ga31-voucher2-shanxi-rules-yuncheng', ''),
        'B93': ('Baiyun district, Guangzhou', 'Mar 2026', 'cn-ga31-voucherrulesmissing-54', ''),
        'B96': ('Inner Mongolia region', 'Sept 2024', 'cn-ga31-voucherrulesmissing-59', ''),
        'B97': ('Lingang Special Area, Shanghai', 'May 2025', 'cn-ga31-voucherrulesmissing-60', 'apart from rental, up to 10% of the purchase of equipment with independently controllable chips'),
        'B100': ('Qinghai province', 'Mar 2024', 'cn-ga31-unsaved4copies-43', ''),
        'B103': ('Shenyang city', 'Jan 2026', 'cn-ga31-vouchernamedrules-4', 'its province’s data bureau says in one reply that the vouchers go to users of local home-made computing; the city’s own text names no origin'),
        'B105': ('Wuxi city', 'May 2025', 'cn-ga31-vcityeast-2', ''),
        'B106': ('Changzhou city', 'Jan 2025', 'cn-ga31-vcityeast-83', ''),
        'B109': ('Nantong city', 'Sept 2025', 'cn-ga31-vcityeast-46', ''),
        'B114': ('Yancheng city', 'Oct 2026', 'cn-ga31-vcityeast-47', ''),
        'B117': ('Lianyungang city', 'Nov 2026', 'cn-ga31-vcityeast-18', ''),
        'B119': ('Suqian city', 'Feb 2026', 'cn-ga31-vcityeast-19', ''),
        'B123': ('Jiaxing city', 'Oct 2024', 'cn-ga31-vcityeast-23', ''),
        'B127': ('Jinhua city', 'Oct 2025', 'cn-ga31-vcityeast-61', ''),
        'B129': ('Huangyan district, Taizhou', 'Jul 2025', 'cn-ga31-vcityeast-55', 'for 自主 (independent) intelligent computing bought for a firm’s own research; for spending from Jan 1, 2025 to Dec 31, 2027 (黄政发〔2025〕18号); no rate for other computing'),
        'B130': ('Quzhou city', 'Mar 2026', 'cn-ga31-vcityeast-28', ''),
        'B134': ('Qiantang district, Hangzhou', 'Dec 2025', 'cn-ga31-vcityeast-33', ''),
        'B135': ('Xuhui district, Shanghai', 'Apr 2025', 'cn-ga31-vcityeast-34', ''),
        'B139': ('Minhang district, Shanghai', 'Feb 2026', 'cn-ga31-vcityeast-35', ''),
        'B142': ('Songjiang district, Shanghai', 'Nov 2025', 'cn-ga31-vcityeast-39', ''),
        'B145': ('Qingpu district, Shanghai', 'Sept 2026', 'cn-ga31-vcityeast-41', ''),
        'B146': ('Putuo district, Shanghai', 'Jan 2025', 'cn-ga31-vcityeast-42', ''),
        'B151': ('Foshan city', 'Aug 2025', 'cn-ga31-vcitysouth-1', ''),
        'B152': ('Dongguan city', 'Feb 2025', 'cn-ga31-vcitysouth-3', ''),
        'B153': ('Binhaiwan New Area, Dongguan', 'May 2026', 'cn-ga31-vcitysouth-53', 'the same 50% pays for the New Area’s computing, for data, and for adapting to home-made operating systems and chips'),
        'B154': ('Zhuhai city', 'Mar 2026', 'cn-ga31-vcitysouth-70', ''),
        'B155': ('Shantou city', 'Nov 2026', 'cn-ga31-vcitysouth-9', ''),
        'B156': ('Zhongshan city', 'Jan 2026', 'cn-ga31-vcitysouth-14', ''),
        'B158': ('Shaoguan city', 'Apr 2026', 'cn-ga31-vcitysouth-15', ''),
        'B160': ('Guangming district, Shenzhen', 'Mar 2025', 'cn-ga31-vcitysouth-24', ''),
        'B162': ('Nansha district, Guangzhou', 'Jul 2025', 'cn-ga31-vcitysouth-26', ''),
        'B167': ('Fuzhou city', 'Mar 2024', 'cn-ga31-vcitysouth-41', ''),
        'B168': ('Quanzhou city', 'Dec 2025', 'cn-ga31-vcitysouth-33', ''),
        'B169': ('Zhangzhou city', 'Jul 2025', 'cn-ga31-vcitysouth-34', ''),
        'B171': ('Nanning city', 'Apr 2025', 'cn-ga31-vcitysouth-39', ''),
        'B172': ('Tianhe district, Guangzhou', 'Nov 2024', 'cn-ga31-vcitysouth-46', ''),
        'B175': ('Chaoyang district, Beijing', 'May 2026', 'cn-ga31-vcitynorth-3', ''),
        'B176': ('Shijingshan district, Beijing', 'Mar 2024', 'cn-ga31-vcitynorth-4', ''),
        'B177': ('Fengtai district, Beijing', 'Oct 2025', 'cn-ga31-vcitynorth-8', ''),
        'B178': ('Hebei district, Tianjin', 'Apr 2024', 'cn-ga31-vcitynorth-10', 'pays for computing bought from one named centre, the Tianjin AI Computing Center, which Tianjin Daily calls wholly home-made; in force for four years from its publication (article 14)'),
        'B179': ('Langfang city', 'Feb 2025', 'cn-ga31-voucher8-langfang-2025-zfxxgk', ''),
        'B180': ('Datong city', 'Aug 2025', 'cn-ga31-vcitynorth-15', ''),
        'B181': ('Zhengzhou city', 'May 2024', 'cn-ga31-vcitynorth-20', ''),
        'B182': ('Zhengzhou High-tech Zone', 'Jul 2025', 'cn-ga31-vcitynorth-56', ''),
        'B183': ('Zhengzhou Airport Zone', 'Aug 2025', 'cn-ga31-voucher8-airport-2025-www-wayback', ''),
        'B185': ('Haidian district, Beijing', 'Aug 2025', 'cn-ga31-voucher5-haidian-2025-measures', 'the rate sentence encourages large-model firms to use home-made computing, at the same rate; the district’s application guide pays that 50% on contracts for GPU computing'),
        'B191': ('Huainan city', 'Nov 2026', 'cn-ga31-vcitywest-2', ''),
        'B192': ('Changsha Economic and Technological Development Zone', 'Mar 2026', 'cn-ga31-vcitywest-6', 'for renting home-made intelligent computing for agent applications, up to 1 million yuan a year; the zone’s measures of Mar 23, 2026, on a provincial news site'),
        'B193': ('Wuchang district, Wuhan', 'May 2026', 'cn-ga31-vcitywest-27', ''),
        'B194': ('Chengdu High-tech Zone', 'Sept 2026', 'cn-ga31-vcitywest-12', ''),
        'B196': ('Hefei High-tech Zone', 'Jan 2025', 'cn-ga31-vcitywest-50', ''),
        'B197': ('Nanchang High-tech Zone', 'Apr 2026', 'cn-ga31-vcitywest-48', ''),
        'B206': ('Longwan district and Wenzhou Bay New Area, Wenzhou', 'May 2026', 'cn-ga31-voucherearlierrules-48', 'the district and the new area carry out Wenzhou’s 30% and 10%, in force from Jun 21, 2026 to Dec 31, 2027; the rules on a media site'),
        'B207': ('Lucheng district, Wenzhou', 'Oct 2023', 'cn-ga31-voucherearlierrules-35', ''),
        'B209': ('Suzhou Industrial Park', 'Nov 2025', 'cn-ga31-voucher5-sip-2025-37hao', 'the park’s measures of Nov 12, 2025, which repeal its measures of 2023, read on the signed file as a commercial policy platform’s file store holds it'),
        'B214': ('Zhongkai High-tech Zone, Huizhou', 'Apr 2026', 'cn-ga31-voucher5-zhongkai-plan-wayback', 'an action plan with a rate in force, from Apr 1, 2026 to Dec 31, 2027; read in an Internet Archive capture of the zone’s page'),
        'B216': ('Futian district, Shenzhen', 'Nov 2024', 'cn-ga31-voucher5-futian-2024-wayback', ''),
    }
    assert set(SHOWN) == set(C), ('the panel’s rows are not the counted rules', sorted(set(SHOWN) ^ set(C)))
    rows = {}
    for k, (place, when, sid, note) in SHOWN.items():
        ids = [x.strip() for x in R['ROWS'][k]['saved_id'].split(';')]
        assert sid in ids and (sid == C[k]['sid'] or k == 'A18'), (k, 'the row links a copy that is not the one the count reads')      # Sichuan links the issuer's own page (an Archive capture); the count reads the news site's full text
        rows[k] = (place, when, C[k]['h'], C[k]['o'], sid, note)
    mx = 60
    assert max(max(r[2], r[3]) for r in rows.values()) <= mx
    key = lambda k: (int(rows[k][1].split()[-1]), MON.index(rows[k][1].split()[0]))
    grp = lambda cls: sorted((k for k in C if C[k]['cls'] == cls), key=key)
    ti, only, one, two = grp(VC.MORE), grp(VC.ONLY), grp(VC.ONE), grp(VC.TWO)
    third = two + one
    # the panel's counts are the classifier's, and the table it writes says the same
    assert f'{len(rows)} / {len(ti)} / {len(only)} / {len(third)}' == R['line']
    cls = [l.split('\t') for l in (TB / 'local_vouchers_classes.tsv').read_text(encoding='utf-8').split('\n') if l and not l.startswith('#')][1:]
    assert {c[0]: c[2] for c in cls if c[2] != VC.NOT} == {k: C[k]['cls'] for k in C}, 'tables/local_vouchers_classes.tsv is not the classifier’s result: run scripts/cn_voucher_classes.py --write'
    assert all(rows[k][2] > rows[k][3] > 0 for k in ti) and all(rows[k][3] == 0 for k in only) and all(rows[k][2] == rows[k][3] for k in third)
    tiers = {k: sorted(int(x) for x in VC.BYTYPE.search(C[k]['sent']).groups()) for k in two}      # a rule of two rates by an unnamed type: its two rates, from its own sentence
    assert all(len(set(v)) == 2 and max(v) <= mx for v in tiers.values())

    def row(k):
        place, when, hm, ot, sid, note = rows[k]
        if k in tiers:
            lo, hi = tiers[k]
            dots = (f'<i class="vl unk" style="--a:{lo / mx:.4f};--b:{hi / mx:.4f}"></i><i class="vd unk" style="--x:{lo / mx:.4f}"></i>'
                    f'<i class="vd unk" style="--x:{hi / mx:.4f}"></i><b class="vn" style="--x:{lo / mx:.4f}">{lo}%</b><b class="vn" style="--x:{hi / mx:.4f}">{hi}%</b>')
            lab = f'{hi}% or {lo}%, by a type of computing facility that the rule does not name'
        elif ot == 0:
            x = hm / mx
            side = f'right:calc({(1 - x) * 100:.2f}% + 11px)' if x >= 0.5 else f'left:calc({x * 100:.2f}% + 11px)'      # the words stay inside the row's own track
            dots = f'<i class="vd away" style="--x:{x:.4f}"></i><b class="vn side" style="{side}">{hm}%, home-made only</b>'
            lab = f'home-made {hm}%, no voucher for other computing'
        else:
            dots = (f'<i class="vl" style="--a:{ot / mx:.4f};--b:{hm / mx:.4f}"></i><i class="vd toward" style="--x:{ot / mx:.4f}"></i>'
                    f'<i class="vd away" style="--x:{hm / mx:.4f}"></i><b class="vn" style="--x:{ot / mx:.4f}">{ot}%</b><b class="vn" style="--x:{hm / mx:.4f}">{hm}%</b>')
            lab = f'home-made {hm}%, other {ot}%'
        tag = '' if C[k]['voucher'] else ' <span class="vtag">not called a voucher</span>'
        return (f'<div class="vr"><div class="vlab">{esc(place)} <a class="srcn" href="{url(sid)}">{esc(when)}</a>{tag}</div>'
                f'<div class="vt" role="img" aria-label="{esc(place, quote=True)}: {lab}">{dots}</div>{("<div class=vnote>" + esc(note) + "</div>") if note else ""}</div>')
    axis = '<div class="vr axis"><div></div><div class="vt">' + ''.join(f'<span style="--x:{v / mx:.4f}">{v}%</span>' for v in (0, 20, 40, 60)) + '</div></div>'
    place = lambda k: rows[k][0]
    listed = lambda names: names[0] if len(names) == 1 else (('; ' if any(',' in n for n in names) else ', ').join(names[:-1]) + ('; and ' if any(',' in n for n in names) else ' and ') + names[-1])      # a place with a comma in it: the list takes semicolons
    # the one-rate rules, compact: by kind of government, then by rate (highest first) and place
    PROVINCE_LEVEL_CITIES = ('Beijing city', 'Shanghai', 'Tianjin', 'Chongqing')      # the four cities of province level
    def kind(k):
        lv = R['ROWS'][k]['level']
        if 'province' in lv or C[k]['gov'] in PROVINCE_LEVEL_CITIES: return 0
        return 1 if lv == 'city' else 2
    KINDS = ('Province-level governments', 'Cities', 'Districts, zones and new areas')
    by_kind = [sorted((k for k in one if kind(k) == i), key=lambda k: (-rows[k][2], place(k))) for i in range(3)]
    assert sum(map(len, by_kind)) == len(one) and all(by_kind)
    letters, foot = {}, []
    for k in [k for g in by_kind for k in g]:
        if rows[k][5]:
            letters[k] = 'abcdefghijklmnopqrstuvwxyz'[len(letters)]; foot.append((letters[k], k))
    assert len(letters) <= 26
    def mini(k):
        place_, when, hm, ot, sid, note = rows[k]
        dag = '' if C[k]['voucher'] else '<span class="vdag" title="not called a voucher">†</span>'
        fn = f'<sup class="vfl">{letters[k]}</sup>' if k in letters else ''
        return (f'<div class="vm"><span class="vml">{esc(place_)} <a class="srcn" href="{url(sid)}">{esc(when)}</a>{dag}{fn}</span>'
                f'<span class="vmt" role="img" aria-label="{esc(place_, quote=True)}: {hm}% for all computing"><i style="--x:{hm / mx:.4f}"></i></span><b class="vmp">{hm}%</b></div>')
    minis = ''.join(f'<div class="vmh">{KINDS[i]}: {len(g)}</div>' + ''.join(mini(k) for k in g) for i, g in enumerate(by_kind))
    notes = ''.join(f'<p><b>{l}</b> {esc(place(k))}: {esc(rows[k][5])}</p>' for l, k in foot)
    (hz,) = two; lo, hi = tiers[hz]; (old,) = R['earlier'][hz]
    old_h, old_o = VC.pct(R['ROWS'][old]['rate_home']), VC.pct(R['ROWS'][old]['rate_other']); old_year = R['ROWS'][old]['date'][:4]
    assert old_year.isdigit() and old_h > old_o > 0
    adapt = [k for k in one if k in getattr(VC, 'ADAPT', {})]
    assert len(adapt) == 2 and all(k in letters for k in adapt), 'the two rules counted under the second named exception, each with its note'
    nv = sum(not C[k]['voucher'] for k in one)
    alt = R['alt']
    out = ['<div class="vkey"><span><i class="sw away"></i>home-made computing</span><span><i class="sw toward"></i>other computing</span><span><i class="sw both"></i>one rate for all</span>'
           '<span><i class="sw unk"></i>a rate by a type of facility the rule does not name</span></div>',
           '<div class="vgrid">',
           f'<div class="vgrp va"><h3>Pay more for home-made computing: {len(ti)}</h3>' + ''.join(row(k) for k in ti) + f'<h3>Pay for home-made computing only: {len(only)}</h3>' + ''.join(row(k) for k in only) + axis + '</div>',
           f'<p class="fine vf">{len(ti)} of the {len(rows)} local governments shown pay more for home-made computing and still pay for other computing; {len(only)}, {listed([place(k) for k in only])}, pay for home-made computing only; '
           f'the other {len(third)} state no higher rate for home-made computing: {len(one)} pay one rate for all, and {place(hz)} pays {hi}% or {lo}% “by the type of computing facility” (按照算力设施的不同类型), a type its plan does not name '
           f'(its rule of {old_year}, since repealed, paid {old_h}% for home-made and {old_o}% for other facilities). The rate shown is the one for an ordinary applicant; most rules state it as a ceiling (up to). '
           f'What is counted is a rule that pays a share of a firm’s bill for rented or bought computing: most call the payment a computing voucher (算力券) or a like name; {len(R["other_name"])} give it another name, a subsidy, a reward or support, and are tagged or marked †. '
           'One row per government (a province, a city, a district or a zone): its latest general rule found that is in force and states a share of the bill. '
           'These are the rules found by searches that went province by province and city by city, saved and read, not a census of every local government: '
           'the searches covered the 31 province-level governments, 24 named cities and new areas, and the cities, districts and zones on the lists of four searches that went city by city; other districts and counties only as they turned up. '
           f'{len(R["own"])} of the {len(rows)} are read on an official page or file of the issuing government or body, and {len(R["elsewhere"])} in another copy (another body’s site, a news or commercial site, or an Internet Archive capture). '
           'Left out: rules known only from the press or a summary (Yuhang district, Keqiao district and Jinan city among them), application guides (Beijing city’s economy bureau; Nanjing), plans with no date of effect (Nanjing’s Jiangbei New Area), '
           'rules repealed, expired or with no share of the bill (Longgang district of Shenzhen, and Nanchang city’s top-up of a provincial award, among them), rules whose text was not reached or only as a scan (Chongqing; Xihu district of Hangzhou), and drafts. '
           f'Counted other ways (rules / paying more / home-made only / no higher rate): with {place(hz)}’s two tiers read as home-made and other, as its repealed rule had them, {alt["hangzhou_more"]}; with {place(hz)} left out, {alt["hangzhou_out"]}. '
           'Support for building or buying with home-made chips only is separate: Beijing city’s plan for 2024 to 2027 supports, by a share of the investment, “采购自主可控GPU芯片开展智能算力服务的企业” (firms that buy independently controllable GPU chips to provide computing services). '
           'The tiers are the rules’ own words: 国产 or 自主 (home-made, independent) against 非国产, 非自主 or 其他 (other).</p>',
           f'<div class="vgrp vb"><div class="vbtop"><div><h3>State no higher rate for home-made computing: {len(third)}</h3>'
           f'<h4>Two rates by a type of computing facility that the rule does not name: {len(two)}</h4>' + ''.join(row(k) for k in two) + axis + '</div>'
           f'<div><h4>One rate for all computing: {len(one)}</h4><p class="vexpl">Each rule: its place, the month of the rule (a link to its saved copy), and its one rate, a dot on the same scale from 0 to 60%. '
           f'† the rule calls the payment a subsidy, a reward or support, not a voucher ({nv} of the {len(one)}). A letter marks a note under the list. '
           f'Two of these rules name home-made computing in the sentence that sets their rate, but only at that one rate: {listed([place(k) for k in sorted(adapt, key=place)])} (notes {", ".join(letters[k] for k in sorted(adapt, key=place))}). '
           'Other support for home-made chips, apart from the rate, stands in the notes.</p></div></div>'
           f'<div class="vmini">{minis}</div><div class="vfoot">{notes}</div></div>', '</div>']
    return '\n'.join(out), len(ti), len(rows)


def bodies(evs):
    def P(*keys):
        return ''.join(pin(by(evs, k[0], k[1]) if isinstance(k, tuple) else by(evs, k)) for k in keys)
    held = [('Cyberspace regulator', P('cn-policy-cac-h20-original', ('man-cn-ft-20250821-regulators', 'BH'), 'cn-clips-alibaba-20f', 'man-cn-ft-20250917-6000d')),
            ('State planner (NDRC)', P(('man-cn-ft-20250821-regulators', 'BH'), 'cn-policy-ndrc-chip-adaptation-2026')),
            ('Industry ministry', P('cn-factions-bloomberg-flexibility-202409-relay1', 'cn-le11-ft-h20justify-aggregoctt', ('man-cn-ft-20250821-regulators', 'BH'))),
            ('Vice Premier Ding Xuexiang’s chip committee, as the Journal describes it', P('man-cn-factions-wsj-ding')),
            ('Security ministry', P('cn-acts-mss-xinhua-20250721')),
            ('State media (the Yuyuan Tantian account)', P('cn-le13-yuyuan-qq-20250810b')),
            ('Customs', P('man-cn-ft-20251009-customs', 'cn-acts-reuters-customs-20260114')),
            ('Finance and industry ministries (a purchase rule for Party and state bodies’ desktop computers)', P('cn-policy-desktop-2023'))]
    let = [('Commerce ministry', P('cn-policy-wang-nvidia', 'cn-policy-h20-mofcom', 'cn-tolerate-mof', 'cn-acts-mofcom-20261117')),
           ('Premier Li Qiang', P('cn-xi-round-f-6')),
           ('Vice Premier He Lifeng', P('cn-policy-he-welcomes')),
           ('“Industry and commerce ministries”, as Reuters put it', P('cn-ga31-sv1-reuters-deepseek-yahoo')),      # record 23 (the open copy since core batch 12, Nov 25, 2026)
           ('Industry ministry, as The Information reported its intention', P('cn-acts-reuters-rtx5500-20260927'))]      # record 62 (core edit 7, Nov 25, 2026)
    firm = [('Market regulator: an antitrust case against Nvidia the company', P('cn-policy-samr-open-original', 'cn-policy-samr-further-original'))]
    col = lambda title, cls, rows: (f'<div class="bcol"><h4><i class="sw {cls}"></i>{title}</h4><ul>' + ''.join(f'<li><span>{esc(n)}</span><span class="pins">{p}</span></li>' for n, p in rows) + '</ul></div>')
    return ('<div class="bodies">' + col('Held Nvidia back, or steered buyers to home-made chips', 'away', held) + col('Let it in, or welcomed it', 'toward', let) + '</div>'
            '<div class="bodies one">' + col('Acted against Nvidia the company', 'away', firm) + '</div>'
            '<p class="fine">The Financial Times (Nov 13, 2026): security-focused officials within the cyberspace regulator and the security ministry “viewed dependence on Nvidia as a strategic vulnerability”, '
            'the commerce ministry “favoured imports”, and, by people the paper does not name, the 2025 push to restrict “was led by the National Development and Reform Commission”. '
            f'The US Trade Representative, Nov 20, 2026 (<a href="{url("cn-le01-greer-bbg-20261120-youtube")}">Bloomberg Television</a>; machine captions, not checked by ear, 01:06 to 01:35): it is “not as monolithic as people would have you believe”; '
            'in his “own analysis” there are some who think “we’d like to have access” and “others who think, well, we don’t want American chips anyway”. '
            'The two caption tracks break the sentence differently, so whether he puts the split inside the government is not settled.</p>'
            '<p class="fine">An unsigned article on the work of the market regulator’s Party group lists the Nvidia case, with its cases on Qualcomm and DuPont China, under “坚决落实党中央重大决策部署” (carrying out the Party centre’s major decisions) and “敢于斗争” (daring to struggle) '
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
    assert (len(rows), st['warns'], len(win), len(late)) == (75, 19, 16, 3) and all(r['outlet'].startswith('Global Times') and r['date'].startswith('2026') for r in late), (len(rows), st)
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
