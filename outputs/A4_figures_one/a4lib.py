#!/usr/bin/env python3
"""Shared helpers for the builders in outputs/A4_figures_one (ideas 9, 11, 14, 15 and 21 of OUTPUT_IDEAS.md).

Q = quotes(path)       read a quotes.tsv. A line is "saved id<TAB>the source's exact words" (the form scripts/cn_has.py
                       checks). A comment line "#@ key" names the line under it, so a builder asks for Q['key'].
check(path)            run scripts/cn_has.py on the file; the build stops if it does not exit 0.
day(Q, key)            the date a page states, parsed from the page's own words (quotes.tsv lines key.date, and key.year
                       where those words carry no year). No date on a page is typed by hand.
guard(page, Q, ...)    the build stops if the page shows words between quotation marks, or a number, that no line of
                       quotes.tsv holds. What is ours by design (our arithmetic, reference numbers) is passed in `ours`.
ref(sid)               kind, label, address and tier (filled or open) of a source, from the argument's reference list.
png(...), pdf(...)     Playwright exports at device scale 2, as scripts/cn_figure_build.py --png does.

Nothing here writes outside the folder of the builder that calls it.
"""
import html, re, subprocess, sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]                       # .
SCRIPTS = ROOT / 'scripts'
PROJ = ROOT / 'research' / 'cn_chip_policy_20261120'
sys.path.insert(0, str(SCRIPTS))
import cn_srclib as L                        # noqa: E402
import cn_argument_build as B                # noqa: E402  (import only: load_refs, address, KIND, SOLID)

esc = html.escape
CREDIT = 'Draft by Claude, Anthropic’s model.'          # the credit an image carries in its pixels: true of a public copy (session ruling, Nov 25, 2026, round 10)
NOTE = CREDIT + ''              # page text only: the release's PUBLIC_WORDS rewrite takes the second sentence out
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
_MNAME = {n: i // 2 + 1 for i, n in enumerate(['jan', 'january', 'feb', 'february', 'mar', 'march', 'apr', 'april', 'may', 'may', 'jun', 'june',
                                               'jul', 'july', 'aug', 'august', 'sep', 'september', 'oct', 'october', 'nov', 'november', 'dec', 'december'])}
_MNAME['sept'] = 9


# ---------- quotations ----------
class Line(str):
    """The source's exact words; .sid is the saved id they were found in."""
    sid = ''


def quotes(path):
    out, key = {}, None
    for n, ln in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        if ln.startswith('#@ '): key = ln[3:].strip(); continue
        if not ln.strip() or ln.startswith('#'): continue
        if '\t' not in ln: sys.exit(f'{path} line {n}: no tab between id and words')
        sid, words = [x.strip() for x in ln.split('\t', 1)]
        if key is None: sys.exit(f'{path} line {n}: a line without a "#@ key" line above it')
        if key in out: sys.exit(f'{path} line {n}: key {key} twice')
        w = Line(words); w.sid = sid; out[key] = w; key = None
    return out


def check(path):
    r = subprocess.run(['python3', '-I', str(SCRIPTS / 'cn_has.py'), str(path)], capture_output=True, text=True)
    print('cn_has.py:', (r.stdout + r.stderr).strip().replace('\n', '\n           '))
    if r.returncode != 0: sys.exit(f'cn_has.py exit {r.returncode} on {path}: nothing written')


def curly(s):
    """The source's words for display: typographic apostrophes; the words themselves are untouched."""
    return s.replace("'", '’')


def qm(words):
    """Words between quotation marks, escaped for HTML."""
    return '“' + esc(curly(str(words))) + '”'


# ---------- dates ----------
def parse_date(words):
    for rx, order in ((r'(\d{4})-(\d{2})-(\d{2})', 'ymd'), (r'(\d{4})/(\d{1,2})/(\d{1,2})', 'ymd'), (r'(\d{4})年(\d{1,2})月(\d{1,2})日', 'ymd'),
                      (r'(\d{1,2})/(\d{1,2})/(\d{4})', 'mdy'), (r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b', 'mdy'), (r'([A-Z][a-z]+)\.? (\d{1,2}), (\d{4})', 'Mdy'), (r'(\d{1,2}) ([A-Z][a-z]+) (\d{4})', 'dMy'),
                      (r'(\d{1,2})-([A-Z][a-z]{2,8})-(\d{4})', 'dMy'),
                      (r'([A-Z][a-z]+)\.? (\d{1,2}) \((?:Reuters|Rtrs)\)', 'Md'), (r'(\d{1,2})月(\d{1,2})日', 'md'),
                      (r'\b([A-Z][a-z]+) (\d{1,2})\b', 'Md')):          # last: a month and a day with no year beside them
        for m in re.finditer(rx, words):
            got = dict(zip(order, m.groups()))
            mo = got.get('m') or got.get('M')
            mo = _MNAME.get(mo.lower()) if 'M' in got else int(mo)
            if not mo: continue                              # a capitalised word that is not a month: look further along
            return (int(got['y']) if 'y' in got else None, mo, int(got['d']))
    return None


def day(Q, key):
    p = parse_date(Q[key + '.date'])
    if p is None: sys.exit(f'no date could be read in the words of {key}.date: {Q[key + ".date"]}')
    y, m, d = p
    if y is None:
        ym = re.search(r'(20\d\d)', Q[key + '.year'])
        if not ym: sys.exit(f'no year in the words of {key}.year')
        y = int(ym.group(1))
    return date(y, m, d)


def fmt(d): return f'{MON[d.month - 1]} {d.day}, {d.year}'


assert parse_date('Published 12/31/2025') == (2025, 12, 31) and parse_date('PUBLISHED: 2026-01-28') == (2026, 1, 28)
assert parse_date('Nov 5 (Reuters) - About') == (None, 11, 5) and parse_date('于2025年7月31日约谈') == (2025, 7, 31)
assert parse_date('Published Sat, Sep 28, 2024') == (2024, 9, 28) and parse_date('no date here') is None
assert parse_date('Corrected Transcript 20-May-2026') == (2026, 5, 20) and parse_date('in the quarter ended October 25') == (None, 10, 25)
assert parse_date('Form 10 and Page 3 of it') is None
assert parse_date('ECRA Disclosure | 11.19.2026') == (2026, 11, 19) and parse_date('Status as of May 11, 2026') == (2026, 5, 11)


# ---------- the guard ----------
_NUM = re.compile(r'\d[\d,.]*\d|\d')


def visible(page):
    t = re.sub(r'(?is)<(script|style|title)\b.*?</\1>', ' ', page)
    t = re.sub(r'(?s)<!--.*?-->', ' ', t)
    said = ' '.join(m.group(2) for m in re.finditer(r'\b(aria-label|alt)="([^"]*)"', t))
    return html.unescape(re.sub(r'(?s)<[^>]+>', ' ', t) + ' ' + said)


def _nums(s):
    return {m.group(0).rstrip('.,').replace(',', '') for m in _NUM.finditer(s)}


def guard(page, Q, ours=(), dates=(), quiet=False):
    """Every quotation and every number the page shows must stand in quotes.tsv, be a date read by day(), or be in `ours`."""
    t = visible(page)
    pool = [L.squash(str(w)) for w in Q.values()]
    spans = re.findall(r'“([^”]+)”', t) + re.findall(r'"([^"]+)"', t)
    bad = [f'quotation not in quotes.tsv: {s[:80]}' for s in spans if not any(L.squash(s) in p for p in pool)]
    bad += [f'unfilled placeholder on the page: {m}' for m in sorted(set(re.findall(r'\{[A-Za-z_:.]+\}|%%\w*%%|\bNone\b|\bNaN\b', t)))]
    body = re.sub(r'https?://\S+', ' ', t)
    for d in sorted(set(dates), key=len, reverse=True): body = body.replace(d, ' ')
    have = set().union(*[_nums(str(w)) for w in Q.values()]) | {str(o).replace(',', '') for o in ours}
    bad += [f'number not in quotes.tsv and not declared ours: {n}' for n in sorted(_nums(body) - have)]
    if bad:
        if quiet: return bad
        print('\n'.join(bad)); sys.exit(f'guard: {len(bad)} unbacked quotations or numbers; nothing written')
    if not quiet: print(f'guard: {len(spans)} quotations and {len(_nums(body))} different numbers on the page, all backed by quotes.tsv, a checked date or a declared sum')
    return []


def guard_control(Q):
    """The guard must be able to fail: a planted quotation, a planted number and an unfilled placeholder are each refused."""
    b = guard('<p>“these words were never written by anyone at all” and 987654321, published {pub}</p>', Q, quiet=True)
    assert len(b) == 3, 'the guard let a planted quotation, number or unfilled placeholder through'


# ---------- the H200 numbers (ideas 9 and 11) ----------
def count(words):
    """'2 million' -> 2000000; '75,000' -> 75000. The count is read from the source's own way of writing it."""
    m = re.fullmatch(r'([\d,.]+)( million)?', words.strip())
    if not m: sys.exit(f'not a number as a source writes it: {words}')
    n = float(m.group(1).replace(',', ''))
    return int(round(n * 1_000_000)) if m.group(2) else int(n)


def house(Q):
    """Washington's table of licence applications ("H200 License and Equivalent Application Status as of May 11, 2026",
    made public by the House Foreign Affairs Committee on Nov 19, 2026; its summary cites "a BIS summary", BIS being the
    Commerce Department's Bureau of Industry and Security; neither document names the Commerce Department as the table's
    maker, so the outputs do not call it the department's table: core edit 6, part 05), summed here from the project's
    tables/house_licence_table.tsv (54 rows, read from the page images by the project). Nothing is typed: every figure is
    a sum of that table, and the two figures the committee's own summary prints (all chips; chips approved, with the count
    of applications) must stand in the builder's quotes.tsv and equal the sums, or the build stops.
    The committee's example of an application of 445,000 chips for Tencent (Dec 19, 2025): the table's only Tencent row of
    that date is for 75,000, and neither document says whether it is that application (core edit 6, part 05.1). So the
    share is given both ways: share_full if that row is the application (counted at 445,000), share_further if the
    445,000 is a further application."""
    lines = [l for l in (PROJ / 'tables' / 'house_licence_table.tsv').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    hdr = lines[0].split('\t')
    rows = [dict(zip(hdr, l.split('\t'))) for l in lines[1:]]
    for r in rows: r['n'] = int(r['chip_count'].replace(',', ''))

    def s(f=lambda r: True):
        sel = [r for r in rows if f(r)]
        return sum(r['n'] for r in sel), len(sel)
    A_, R_ = 'Approved, not shipped', 'RWA'
    t = dict(all=s(), appr=s(lambda r: r['status'] == A_), appr_nv=s(lambda r: r['status'] == A_ and r['exporter'] == 'Nvidia'),
             appr_amd=s(lambda r: r['status'] == A_ and r['exporter'] == 'AMD'), rwa=s(lambda r: r['status'] == R_),
             rwa_nv=s(lambda r: r['status'] == R_ and r['exporter'] == 'Nvidia'), rwa_amd=s(lambda r: r['status'] == R_ and r['exporter'] == 'AMD'),
             abroad=s(lambda r: r['location'] != 'China'))
    t['places'] = sorted({r['location'] for r in rows if r['location'] != 'China'})
    assert t['appr_nv'][0] + t['appr_amd'][0] == t['appr'][0] and t['rwa_nv'][0] + t['rwa_amd'][0] == t['rwa'][0], 'an exporter other than Nvidia and AMD among the approved or returned rows'
    assert all(r['status'] == R_ and r['exporter'] == 'Nvidia' for r in rows if r['location'] != 'China'), 'an application for a consignee abroad is not an Nvidia one returned without action'
    assert f"{t['all'][0]:,}" in Q['table.all'], 'the table does not sum to the figure in the committee\'s summary'
    assert f"{t['appr'][0]:,}" in Q['wapproved'] and f"across {t['appr'][1]} license applications" in Q['wapproved'], 'the approved rows do not sum to the summary\'s figure'
    cap = max(r['n'] for r in rows if r['status'] == A_)
    assert all(r['status'] == R_ for r in rows if r['n'] > cap), 'an application above the largest approved one is not marked returned'
    t['cap'], t['over'] = cap, len([r for r in rows if r['n'] > cap])
    t['share'] = round(100 * t['rwa'][0] / t['all'][0])                 # of the chips in the applications the summary records
    # the committee's example of an application the summary does not show in full: Nvidia, Dec 19, 2025, for Tencent.
    # The table's only Tencent row of that date; whether it is that application, neither document says.
    m = re.search(r'NVIDIA applied on December (\d+), (\d{4}), to export ([\d,]+) H200s to Tencent', Q['table.tencent'])
    assert m, 'the committee\'s example is not in quotes.tsv'
    same = [r for r in rows if 'Tencent' in r['consignee'] and r['date_submitted'] == f'12/{int(m.group(1))}/{m.group(2)}']
    assert len(same) == 1 and same[0]['exporter'] == 'Nvidia', 'the table does not hold exactly one Tencent row of that date, with Nvidia as exporter'
    t['tencent_full'], t['tencent_shown'], t['tencent_status'] = int(m.group(3).replace(',', '')), same[0]['n'], same[0]['status']
    # the names the table gives the consignees abroad (names only: the table does not call them subsidiaries)
    abroad = [r for r in rows if r['location'] != 'China']
    t['names'] = [n for n in ('ByteDance', 'BytePlus', 'TikTok', 'Alibaba') if any(n.lower() in r['consignee'].lower() for r in abroad)]
    assert all(any(n.lower() in r['consignee'].lower() for n in t['names']) for r in abroad), 'a consignee abroad carries none of the four names'
    t['share_full'] = round(1000 * t['rwa'][0] / (t['all'][0] + t['tencent_full'] - t['tencent_shown'])) / 10    # if the row is the application
    t['share_further'] = round(1000 * t['rwa'][0] / (t['all'][0] + t['tencent_full'])) / 10                     # if the 445,000 is a further one
    assert t['share_further'] < t['share_full'] < t['share'], 'the two readings of the committee\'s example should each lower the share'
    t['status'] = day(Q, 'wapproved'); t['released'] = day(Q, 'table.release')
    return t


def funnel(Q, card=False):
    """The rows of h200_funnel.tsv. A press row is tied to its sentence and date in the builder's quotes.tsv; a table row
    takes its count from house(). card=True leaves out the rows the file marks card=no. Counts and sums are made here."""
    lines = [ln for ln in (HERE / 'h200_funnel.tsv').read_text(encoding='utf-8').splitlines() if ln.strip() and not ln.startswith('#')]
    hdr, rows, H = lines[0].split('\t'), [], house(Q)
    for ln in lines[1:]:
        r = dict(zip(hdr, ln.split('\t')))
        assert r['tier'] in ('open', 'solid') and r['card'] in ('yes', 'no') and r['dir'] in ('toward', 'away', 'us'), r
        if card and r['card'] == 'no': continue
        w = Q[r['key']]
        if r['times'].startswith('table:'):              # a sum of Washington's table: on the record
            r['chips'], r['apps'] = H[r['times'][6:]]; r['shown'] = ('', f"{r['chips']:,}")
        else:
            if f"{r['qual']} {r['number']}".lower() not in w.lower(): sys.exit(f"{r['key']}: \"{r['qual']} {r['number']}\" is not in its sentence in quotes.tsv")
            n = count(r['number'])
            if r['times'] == '1': r['chips'], r['shown'] = n, (r['qual'], r['number'])
            elif r['times'] == 'each2':                  # two named buyers, each with this number: the bar is drawn for both
                m = re.match(r'(\w+) and (\w+) have each received', w)
                if not m: sys.exit(f"{r['key']}: the sentence does not name two buyers")
                r['buyers'] = m.groups(); r['chips'] = 2 * n; r['shown'] = (r['qual'], r['number'] + ' each')
            else: sys.exit(f"{r['key']}: times {r['times']} not understood")
        r['date'], r['sid'], r['words'] = day(Q, r['key']), w.sid, w
        assert (ref(w.sid)['tier'] == 'solid') == (r['tier'] == 'solid'), f"{r['key']}: its tier differs from the argument's reference list"
        rows.append(r)
    want = ['ordered', 'wapproved', 'wreturned', 'approved', 'discussed', 'delivered', 'waiting']
    assert [r['key'] for r in rows] == [k for k in want if not (card and k == 'discussed')], 'the rows, in the order of the core figure\'s bars'
    assert not any('750' in str(r['shown']) for r in rows), 'the old multiplication is back'
    return rows, H


# ---------- two readings of the project's own records ----------
MONTH = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def warnings():
    """The state and Party media items that only warn about Nvidia's chips, counted from the project's
    tables/state_media_items.tsv (stance = warns). Since core edit 6 (Nov 24, 2026) the table holds 75 items (rows 43 on
    were found by searches and links; after Sept 24, 2025 they are a sample, not a census) and the warnings run into 2026.
    Returned: the items in all, the warnings in all; those of the first year with a warning (the burst: count and span of
    dates); the later ones (count, their outlet, which must be one outlet, and their months)."""
    lines = [l for l in (PROJ / 'tables' / 'state_media_items.tsv').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    hdr = lines[0].split('\t'); rows = [dict(zip(hdr, l.split('\t'))) for l in lines[1:]]
    assert len(rows) > 30 and any(r['stance'] == 'mixed' for r in rows), 'control: the table should hold items of other stances too'
    assert all(len(l.split('\t')) == len(hdr) for l in lines[1:]), 'a row of the state-media table does not have its header\'s cells'
    warns = sorted((date.fromisoformat(r['date']), r['outlet']) for r in rows if r['stance'] == 'warns')
    assert warns, 'no warning in the table'
    y0 = warns[0][0].year
    burst = [d for d, _ in warns if d.year == y0]; later = [(d, o) for d, o in warns if d.year != y0]
    span = (f'{MON[burst[0].month - 1]} {burst[0].day} to {fmt(burst[-1])}' if burst[0].year == burst[-1].year else f'{fmt(burst[0])} to {fmt(burst[-1])}')
    outlets = {re.sub(r'\s*\(.*$', '', o).strip() for _, o in later}
    assert len(outlets) <= 1, f'the later warnings come from more than one outlet: {sorted(outlets)}; the sentences that say one outlet must change'
    mo = []
    for d, _ in later:
        if (d.year, d.month) not in [(a, b) for a, b in mo]: mo.append((d.year, d.month))
    yrs = sorted({a for a, _ in mo})
    if len(yrs) == 1: months = ' and '.join(MONTH[b - 1] for _, b in mo) + f' {yrs[0]}' if len(mo) <= 2 else None
    else: months = None
    assert later == [] or months, 'the later warnings span more than two months or more than one year: the wording that names their months must change'
    return {'items': len(rows), 'warn': len(warns), 'burst': len(burst), 'span': span, 'later': len(later),
            'later_outlet': next(iter(outlets)) if outlets else '', 'later_months': months or ''}


def caption_time(sid, words):
    """Where in a recording a caption line stands, as m:ss, read from the saved caption file's own time marks."""
    raw = (L.P / sid / 'body.html').read_text(encoding='utf-8', errors='replace')
    hits = []
    for m in re.finditer(r'(?s)<p begin="(\d\d):(\d\d):(\d\d)[^"]*"[^>]*>(.*?)</p>', raw):
        if L.squash(words) in L.squash(html.unescape(re.sub(r'<[^>]+>', ' ', m.group(4)))): hits.append(m)
    if len(hits) != 1: sys.exit(f'{sid}: the words stand in {len(hits)} caption lines, not one: {words}')
    h, mi, se = (int(x) for x in hits[0].groups()[:3])
    return f'{h * 60 + mi}:{se:02d}'


def posted(sid):
    """The day a saved video page says it was published, from its own datePublished mark (the page's text does not show it)."""
    raw = (L.P / sid / 'body.html').read_text(encoding='utf-8', errors='replace')
    m = re.search(r'itemprop="datePublished" content="(\d{4})-(\d{2})-(\d{2})', raw)
    if not m: sys.exit(f'{sid}: no datePublished mark in the saved page')
    return date(*(int(x) for x in m.groups()))


# ---------- sources ----------
_refs = None


def ref(sid):
    global _refs
    if _refs is None: _refs = B.load_refs()
    r = _refs[sid]
    return {'kind': B.KIND[r['kind']], 'label': r['label'], 'addr': B.address(sid, r) or '', 'tier': 'solid' if r['kind'] in B.SOLID else 'open'}


# ---------- pages ----------
FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap">'
_LIGHT = ('--page: #f9f9f7; --surface: #fcfcfb; --ink: #0b0b0b; --ink2: #52514e; --muted: #7a7872; --grid: #e1e0d9; --axis: #c3c2b7; '
          '--border: rgba(11,11,11,0.12); --wash: rgba(11,11,11,0.045); --toward: #256abf; --away: #c44e18; --us: #898781; --rest: #cfcdc4; --pin-on: #ffffff; --link: #1c5cab;')
_DARK = ('--page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink2: #c3c2b7; --muted: #8f8d86; --grid: #2c2c2a; --axis: #45453f; '
         '--border: rgba(255,255,255,0.14); --wash: rgba(255,255,255,0.06); --toward: #3987e5; --away: #d95926; --us: #898781; --rest: #45453f; --pin-on: #0d0d0d; --link: #86b6ef; color-scheme: dark;')
# colour and type tokens of ../figure/template.html (light and dark), and its base rules
CSS = (':root { ' + _LIGHT + ' --font-text: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif; --font-head: "Space Grotesk", "Inter", system-ui, sans-serif; }\n'
       '@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { ' + _DARK + ' } }\n'
       ':root[data-theme="dark"] { ' + _DARK + ' }\n' + '''
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--page); color: var(--ink); font-family: var(--font-text); font-size: 16px; line-height: 1.5; }
a { color: var(--link); }
.wrap { max-width: 1232px; margin: 0 auto; padding: 26px 16px 48px; background: var(--page); }
.draft { margin: 0 0 18px; font-size: 12.5px; line-height: 20px; color: var(--muted); }
.eyebrow { font: 700 12px/1.2 var(--font-text); letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); margin: 0 0 12px; }
h1 { font-family: var(--font-head); font-size: clamp(27px, 3.5vw, 44px); line-height: 1.08; letter-spacing: -0.015em; margin: 0 0 12px; max-width: 26ch; text-wrap: balance; }
.deck { margin: 0; color: var(--ink2); font-size: 17.5px; max-width: 76ch; }
.key { display: flex; flex-wrap: wrap; gap: 8px 24px; margin: 16px 0 0; padding: 0; list-style: none; font-size: 14.5px; color: var(--ink2); }
.key li { display: flex; align-items: center; gap: 8px; }
.key b { color: var(--ink); font-weight: 600; }
i.sw { display: inline-block; flex: none; width: 13px; height: 13px; border-radius: 3px; }
i.sw.toward { background: var(--toward); } i.sw.away { background: var(--away); } i.sw.us { background: var(--us); }
/* tier marks: filled = on the record; open = a press report citing unnamed people */
i.mk { display: inline-block; flex: none; width: 13px; height: 13px; border-radius: 50%; border: 2.5px solid var(--ink2); vertical-align: -1.5px; }
i.mk.solid { background: var(--ink2); } i.mk.open { background: var(--surface); }
i.mk.toward { border-color: var(--toward); } i.mk.away { border-color: var(--away); } i.mk.us { border-color: var(--us); }
i.mk.solid.toward { background: var(--toward); } i.mk.solid.away { background: var(--away); } i.mk.solid.us { background: var(--us); }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 20px 22px; min-width: 0; }
.card h2 { font-family: var(--font-head); font-size: 21px; line-height: 1.2; margin: 0 0 4px; text-wrap: balance; }
.card .sub { margin: 0 0 12px; color: var(--ink2); font-size: 14.5px; max-width: 76ch; }
.srcn { color: var(--muted); font-size: 12.5px; }
.notes { margin-top: 16px; }
.notes ul { margin: 6px 0 0; padding-left: 20px; color: var(--ink2); font-size: 14px; max-width: 108ch; }
.notes li { margin: 4px 0; }
.imgnote { display: none; margin: 14px 2px 0; font-size: 12px; line-height: 1.4; color: var(--muted); }
table.tv { width: 100%; border-collapse: collapse; font-size: 14px; }
table.tv th { text-align: left; font: 700 12px/1.3 var(--font-text); letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); padding: 6px 10px 6px 0; border-bottom: 1px solid var(--axis); }
table.tv td { padding: 8px 10px 8px 0; border-bottom: 1px solid var(--grid); vertical-align: top; color: var(--ink2); }
table.tv td b { color: var(--ink); }
.scrollx { overflow-x: auto; }
''')


FIG_EXPORT = '.wrap { max-width: none; width: 1256px; margin: 0; padding: 0; } #fig { padding: 28px; background: var(--page); } .imgnote { display: block; }'
IMGNOTE = f'<p class="imgnote">{CREDIT}</p>'    # goes last inside #fig: the image carries the credit in its footer, never "" (no release script reaches pixels)


def head(title, css='', theme=None):
    assert 2 <= len(title.split()) <= 4, 'a page title has two to four words'
    return (f'<!doctype html>\n<html lang="en"{f" data-theme={chr(34)}{theme}{chr(34)}" if theme else ""}>\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>{esc(title)}</title>\n{FONTS}\n<style>\n{CSS}{css}\n</style>\n</head>\n')


def link(sid, text=None):
    r = ref(sid)
    t = esc(text if text is not None else r['label'])
    return f'<a href="{esc(r["addr"], quote=True)}">{t}</a>' if r['addr'] else t


# ---------- exports ----------
def _fonts_ok(pg):
    pg.evaluate('document.fonts.ready.then(() => 1)'); pg.wait_for_timeout(700)
    ok = pg.evaluate('document.fonts.check(\'700 20px "Space Grotesk"\') && document.fonts.check(\'600 16px "Inter"\') && [...document.fonts].some(f => f.family.includes("Space Grotesk") && f.status === "loaded")')
    if not ok: sys.exit('the web fonts did not load: no image or PDF written (it would show fallback type)')


_FITS_JS = """pairs => { const bad = [];
  for (const [child, box] of pairs) for (const el of document.querySelectorAll(child)) {
    const b = el.closest(box); if (!b) continue;
    const r = el.getBoundingClientRect(), o = b.getBoundingClientRect(), cs = getComputedStyle(b);
    if (!r.width) continue;
    const right = o.right - parseFloat(cs.paddingRight) - parseFloat(cs.borderRightWidth), bottom = o.bottom - parseFloat(cs.paddingBottom) - parseFloat(cs.borderBottomWidth);
    if (r.right > right + 0.75 || r.bottom > bottom + 0.75) bad.push(child + ' "' + el.textContent.trim().slice(0, 40) + '" runs ' + Math.max(r.right - right, r.bottom - bottom).toFixed(1) + ' px out of ' + box);
  } return bad; }"""


def png(page, shots, width=1280, height=900, scheme='light', css=None, fits=()):
    """shots: (css selector, output path). Device scale 2. css: rules added for the export only (padding round a figure).
    fits: (child selector, box selector) pairs; the export stops if a child runs out of its box's content area."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_context(viewport={'width': width, 'height': height}, device_scale_factor=2, color_scheme=scheme).new_page()
        pg.goto(Path(page).as_uri())
        if css: pg.add_style_tag(content=css)
        _fonts_ok(pg)
        if fits:
            bad = pg.evaluate(_FITS_JS, [list(x) for x in fits])
            if bad: print('\n'.join(bad)); sys.exit(f'{len(bad)} elements run out of their box: no image written')
            # the control: a 60 px block planted in a 20 px box must be caught, then it is taken out again
            pg.evaluate("""() => { const d = document.createElement('div'); d.id = 'fitctl'; d.style.width = '20px';
                const s = document.createElement('span'); s.textContent = 'control'; s.style.cssText = 'display:inline-block;width:60px;height:4px'; d.appendChild(s); document.body.appendChild(d); }""")
            ctl = pg.evaluate(_FITS_JS, [['#fitctl span', '#fitctl']]); pg.evaluate("() => document.getElementById('fitctl').remove()")
            assert len(ctl) == 1, 'the fit check let a planted overflow through'
            print(f'fit check: nothing runs out of its box ({len(fits)} rules); a planted overflow was caught')
        for sel, out in shots:
            # what the image will show: the credit, and nothing that calls a public copy local or unpublished (control: the credit is found)
            shown = pg.locator(sel).inner_text()
            assert CREDIT in shown, f'control: the credit is not in the text of {sel}, so the check below could not see the footer'
            assert 'not published' not in shown.lower() and 'local;' not in shown.lower(), f'{sel}: the image would say the copy is local or not published'
            pg.locator(sel).screenshot(path=str(out))
            from PIL import Image
            with Image.open(out) as im: print('image', out, f'{im.size[0]} x {im.size[1]}')
        br.close()


def pdf(page, out, width, height, paper=None):
    """One sheet of the given size (CSS lengths, e.g. '210mm'), backgrounds printed, no browser margins."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_context(color_scheme='light').new_page()
        pg.goto(Path(page).as_uri())
        if paper: pg.evaluate('p => { document.documentElement.dataset.paper = p; }', paper)
        pg.emulate_media(media='print', color_scheme='light'); _fonts_ok(pg)
        pg.pdf(path=str(out), width=width, height=height, print_background=True, margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
        br.close()
    print('pdf', out)
