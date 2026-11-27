"""Shared code for the two motion outputs of the China chip-policy project (ideas 24 and 25).

Used by 24_explainer/build.py and 25_strip_animation/build.py. Nothing in this file writes a file.

  load_events()              returns records, quotation checks, geometry and row names from ../../figure/figure_data.txt,
                             with the dated records numbered and placed exactly as
                             scripts/cn_figure_build.py does. Its load(), number(), X() and the placing loop of strip()
                             are copied here, because importing that script would rebuild the figure. Since core edit 7
                             (Nov 25, 2026) a block with an "N" line keeps that number (record 62 stands at its date,
                             Sept 27, 2026, between records 34 and 35), as the core's builder now reads it.
  check_against_figure(evs, lane_names)  returns the row names for drawing and a check result. Stops unless record
                             numbers, dates, titles, source labels and second addresses agree with figure_events.tsv, every mark
                             stands where figure/beijing_vs_labs.html draws its circle, and the three dashed lines and
                             the labels beside marks carry the figure page's own words at its own places (x, y and
                             anchor; so the copy cannot drift)
  strip_svg(evs, G, lane_names)  the strip as SVG for a 1280 px video frame: the same geometry and callouts, the left
                             gutter cropped away, each row's name set inside the row as a small tag, and the note
                             "2023 and 2024 are drawn narrower" moved from under the dates to above its band
  KEY, card_layout(G, pad)   the key, set as a column at the right of the strip inside its card, and the sizes that
                             go with it. Since the fourth edit of the core (61 records, 13 sub-rows) the strip no
                             longer fits a 720 px frame at the figure's size under a headline and above text, so
                             both videos draw it at about 0.9 of that size and give the freed column to the key
  template_has(*sentences)   stops unless each sentence stands in figure/template.html (headline, key, notes)
  house_table(), state_media()   the counts the captions show, summed here from tables/*.tsv (never typed)
  strip_quotes(evs, checks)  the lines of quotes.tsv behind what the strip shows
  made_from(here, files)     sha256 of the files a page is built from (frames.py refuses a capture if one changed)
  write_quotes / run_has     write a quotes.tsv and run scripts/cn_has.py on it (the build stops unless it exits 0)
  page(...)                  the HTML page: a 1280 x 720 stage, the scene data, and the engine that draws time t
                             (window.setT(seconds)); frames.py calls setT once per frame and takes a screenshot
"""
import hashlib, html, json, os, re, subprocess, sys
from datetime import date, datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent            # .../outputs/A7_motion
PROJ = HERE.parents[1]                            # .../research/cn_chip_policy_20261120
ROOT = PROJ.parents[1]                            # the project root (scripts/, research/)
FIG = PROJ / 'figure'
SCRIPTS = ROOT / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from cn_srclib import url_of   # noqa: E402

MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
LANES = {'BH': ('Beijing', 'away'), 'BL': ('Beijing', 'toward'),
         'CN': ('The companies', 'toward'), 'CH': ('The companies', 'away')}
ORDER = ['BH', 'BL', 'CN', 'CH']
esc = html.escape


def smart(s):
    return re.sub(r'"([^"]*)"', '“\\1”', s).replace("'", '’')


def fmt(d): return f'{MON[d.month - 1]} {d.day}, {d.year}'


# ---------- the data: copied from scripts/cn_figure_build.py (load, number) ----------
def load():
    evs, checks, lane_names, cur = [], [], {}, None
    for n, ln in enumerate((FIG / 'figure_data.txt').read_text(encoding='utf-8').splitlines(), 1):
        if ln.startswith('# LANE: '):
            lane_names = dict(lane.split(' ', 1) for lane in ln.removeprefix('# LANE: ').split(' | '))
        if not ln.strip() or ln.startswith('#'): continue
        if ln.startswith('@ '):
            _, lane, kind, d, dl, sid = ln.split()
            assert lane in LANES and kind in ('doc', 'rec', 'press'), (n, ln)
            cur = dict(lane=lane, kind=kind, date=date.fromisoformat(d), dl=None if dl == '-' else dl.replace('_', ' '), sid=sid, T='', S='', Q='', E='', U='', C='', N='', A='')
            evs.append(cur)
        elif ln.startswith('! '):
            sid, q = ln[2:].split(' | ', 1); checks.append((sid.strip(), q.strip()))
        elif ln[:2] in ('T ', 'S ', 'Q ', 'E ', 'U ', 'C ', 'N ', 'A '):
            cur[ln[0]] = smart(ln[2:].strip()) if ln[0] in 'TSC' else ln[2:].strip()
        else: sys.exit(f'figure_data.txt line {n} not understood: {ln[:60]}')
    assert set(lane_names) == set(LANES), lane_names
    return evs, checks, lane_names


def number(evs):
    """Number the records by date, Beijing's rows first and then the companies', except a record with an "N" line, which
    keeps the number given there (core edit 7, Nov 25, 2026: a record added after the figure was made public takes the
    next free number, so no earlier record changes its number). Copied from scripts/cn_figure_build.py as edit 7 left it,
    without its address lookup (the videos print no address); the two asserts are the core's own."""
    free = [e for e in evs if not e['N']]
    b = sorted([e for e in free if e['lane'][0] == 'B'], key=lambda e: e['date'])
    c = sorted([e for e in free if e['lane'][0] == 'C'], key=lambda e: e['date'])
    for i, e in enumerate(b + c, 1): e['n'] = i
    for e in evs:
        if e['N']: e['n'] = int(e['N'])
    assert sorted(e['n'] for e in evs) == list(range(1, len(evs) + 1)), 'the record numbers do not run from 1 to the number of records'
    assert all(e['n'] > len(free) for e in evs if e['N']), 'a fixed number falls among the numbers given by date'
    for e in evs:
        e['when'] = e['dl'] or fmt(e['date'])
        e['dir'] = LANES[e['lane']][1]; e['solid'] = e['kind'] != 'press'


# ---------- the strip's geometry: copied from scripts/cn_figure_build.py (X, and the placing loop of strip) ----------
W, GL, GR = 1400, 216, 26
A, BK, C = date(2023, 1, 1), date(2025, 1, 1), date(2026, 12, 1)
FRAC, R, PITCH = 0.15, 10, 23
FLAGS = ((date(2025, 7, 15), 'Jul 2025 · US clears H20 sales again', 'end'), (date(2025, 12, 8), 'Dec 8, 2025 · US says it will allow H200', 'start'),   # round 10: the core's label since 22:44 UTC, Nov 25, 2026 (r12e)
         (date(2026, 11, 17), 'Nov 17, 2026 · Nvidia reports H200 halt', 'end'))
VX, VY = GL - 12, 8                                # the video crops the figure's left gutter and a little of its top margin: the view starts here


def view_h(G):                                     # ... and ends under the tick labels (the note on 2023 and 2024 moves above its band)
    return G['bottom'] + 28 - VY


def X(d):
    x0, x1 = GL, W - GR
    if d < BK: return x0 + (d - A).days / (BK - A).days * FRAC * (x1 - x0)
    return x0 + FRAC * (x1 - x0) + (d - BK).days / (C - BK).days * (1 - FRAC) * (x1 - x0)


def place(evs):
    top, y, lanes = 50, 50, {}
    for k in ORDER:
        placed = []
        for e in sorted([e for e in evs if e['lane'] == k], key=lambda e: e['date']):
            x, lv = X(e['date']), 0
            while any(l == lv and abs(x - px) < PITCH + 1 for px, l in placed): lv += 1   # PITCH + 1 since the figure's fourth edit: rings never touch
            placed.append((x, lv)); e['x'], e['lv'] = x, lv
        h = (max(l for _, l in placed) + 1) * PITCH + 16
        lanes[k] = (y, h); y += h + (16 if k == 'BL' else 0)
    bottom = y
    for e in evs:
        y0, h = lanes[e['lane']]
        e['cy'] = y0 + h - 8 - R - e['lv'] * PITCH
    return dict(top=top, bottom=bottom, H=bottom + 40, lanes=lanes)


def load_events():
    evs, checks, lane_names = load()
    for e in evs:
        if not (e['T'] and e['S'] and e['Q']): sys.exit(f"incomplete block {e['sid']}")
    number(evs)
    G = place(evs)
    evs.sort(key=lambda e: e['n'])
    return evs, checks, G, lane_names


def check_against_figure(evs, lane_names):
    """Check what the figure shows, then return its row names and a build log line."""
    rows = [ln.split('\t') for ln in (FIG / 'figure_events.tsv').read_text(encoding='utf-8').splitlines()[1:] if ln.strip()]
    if len(rows) != len(evs): sys.exit(f'figure_events.tsv has {len(rows)} records, figure_data.txt gives {len(evs)}')
    drawn_names = {}
    for r, e in zip(rows, evs):
        if len(r) != 11: sys.exit(f'record {e["n"]} does not have eleven columns in figure_events.tsv')
        lane = e['lane']
        who, _ = LANES[lane]
        name = lane_names[lane]
        if lane.startswith('C'):
            name = 'The ' + name
        want = (str(e['n']), str(e['date']), e['when'], name, e['kind'], e['sid'])
        got = (r[0], r[1], r[2], r[3], r[4], r[7])
        if want != got: sys.exit(f'record {e["n"]} differs from figure_events.tsv: {want} / {got}')
        also_source, also_address = '', ''
        if e['A']:
            sid, label = e['A'].split(' | ', 1)
            also_source, also_address = smart(label), url_of(sid)
            if not also_address: sys.exit(f'record {e["n"]} has no address in the saved metadata for {sid}')
        if (r[5], r[8], r[9]) != (e['S'], e['T'], also_source):
            sys.exit(f'record {e["n"]} source or title differs from figure_events.tsv')
        if r[10] != also_address:
            sys.exit(f'record {e["n"]} second address differs from figure_events.tsv')
        drawn_names[lane] = r[3].removeprefix(who + ' ')
    page_ = (FIG / 'beijing_vs_labs.html').read_text(encoding='utf-8')
    drawn = {int(m.group(1)): (float(m.group(2)), float(m.group(3))) for m in
             re.finditer(r'data-n="(\d+)" data-tip="1"[^>]*><circle cx="([\d.]+)" cy="([\d.]+)" r="10"/>', page_)}
    if len(drawn) != len(evs): sys.exit(f'the figure page draws {len(drawn)} marks on its strip, the data gives {len(evs)}')
    for e in evs:
        cx, cy = drawn[e['n']]
        if abs(cx - e['x']) > 0.06 or abs(cy - e['cy']) > 0.06: sys.exit(f'mark {e["n"]} stands at {e["x"]:.1f},{e["cy"]:.1f} here and at {cx},{cy} in the figure')
    assert not any(abs(d[0] - 1.0) < 0.01 for d in drawn.values()), 'control: no mark stands at x = 1'
    # the three dashed lines and the short labels beside marks: the same words at the same places as the figure draws
    flags = re.findall(r'<line class="flag" x1="([\d.]+)"[^>]*/><text class="flagt" x="[\d.]+" y="26" text-anchor="(\w+)">([^<]*)</text>', page_)
    mine = [(f'{X(d):.1f}', anchor, esc(lab)) for d, lab, anchor in FLAGS]
    if flags != mine: sys.exit(f'the dashed lines differ from the figure page: here {mine}, there {flags}')
    assert flags != [(x, a, lab + ' today') for x, a, lab in mine], 'control: a changed label must be noticed'
    calls = sorted(re.findall(r'<text class="call"[^>]*>([^<]*)</text>', page_))
    mine_c = sorted(f'{e["n"]} · {esc(e["C"].split(" ", 3)[3])}' for e in evs if e['C'])
    if calls != mine_c: sys.exit(f'the labels beside marks differ from the figure page: here {mine_c}, there {calls}')
    # round 13 (Nov 26, 2026): each label also stands at the figure page's own x, y and anchor. Until round 12 only the words were
    # compared here; the places were compared outside the build (scratch_r12/label_places.py), so a label the figure moved without
    # rewording would have passed this check.
    there = {}
    for m in re.finditer(r'<text class="call"([^>]*)>([^<]*)</text>', page_):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
        there[m.group(2)] = (float(a['x']), float(a['y']), a['text-anchor'])
    here = {}
    for e in evs:
        if e['C']:
            anchor, dx, dy, words = e['C'].split(' ', 3)
            here[f'{e["n"]} · {esc(words)}'] = (e['x'] + float(dx), e['cy'] + float(dy), anchor)
    same = lambda a, b: abs(a[0] - b[0]) <= 0.06 and abs(a[1] - b[1]) <= 0.06 and a[2] == b[2]
    off = [(k, here[k], there.get(k)) for k in here if k not in there or not same(here[k], there[k])]
    if off: sys.exit(f'labels beside marks stand elsewhere than in the figure page (here, there): {off}')
    k0 = sorted(here)[0]
    assert not same((here[k0][0], here[k0][1] + 1, here[k0][2]), there[k0]), 'control: a label moved by one unit must be noticed'
    assert not same((here[k0][0], here[k0][1], 'middle'), there[k0]), 'control: a label with another anchor must be noticed'
    return drawn_names, (f'{len(evs)} records equal figure_events.tsv (number, date, row, kind, saved id, source, title and second address); {len(drawn)} mark positions, {len(flags)} dashed lines '
                         f'and {len(calls)} labels (words, x, y and anchor) equal the figure page')


# ---------- the strip as SVG for the video ----------
def strip_svg(evs, G, lane_names):
    top, bottom, H, lanes = G['top'], G['bottom'], G['H'], G['lanes']
    xb = X(BK)
    o = [f'<svg id="strip" viewBox="{VX} {VY} {W - VX} {view_h(G)}" role="img" aria-label="Dated strip, 2023 to November 2026: four rows of numbered marks, one mark for each dated record">']
    for k in ORDER:
        y0, h = lanes[k]
        o.append(f'<rect class="rowhl" id="row-{k}" x="{VX}" y="{y0}" width="{W - VX}" height="{h}" opacity="0"/>')
    o.append(f'<rect class="era" x="{GL}" y="{top}" width="{xb - GL:.1f}" height="{bottom - top}"/>')
    ticks = [(date(2023, 1, 1), '2023'), (date(2024, 1, 1), '2024')] + [(date(y_, m, 1), (f'{MON[m - 1]} {y_}' if m == 1 else MON[m - 1])) for y_ in (2025, 2026) for m in (1, 4, 7, 10)]
    for d, lab in ticks:
        x = X(d); strong = d.month == 1
        o.append(f'<line class="grid{" yr" if strong else ""}" x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom + 6}"/><text class="tick{" yr" if strong else ""}" x="{x + 4:.1f}" y="{bottom + 22}">{lab}</text>')
    o.append(f'<text class="eranote" x="{GL + 5}" y="{top - 7}">2023 and 2024 are drawn narrower</text>')
    for i, (d, lab, anchor) in enumerate(FLAGS):
        x = X(d); dx = -7 if anchor == 'end' else 7
        o.append(f'<g id="flag{i}"><line class="flag" x1="{x:.1f}" y1="14" x2="{x:.1f}" y2="{bottom}"/><text class="flagt" x="{x + dx:.1f}" y="26" text-anchor="{anchor}">{esc(lab)}</text></g>')
    for k in ORDER:
        y0, h = lanes[k]; who, dr = LANES[k]; what = lane_names[k]
        o.append(f'<line class="lane" x1="0" y1="{y0 + h}" x2="{W}" y2="{y0 + h}"/>')
        o.append(f'<g class="rowtag"><rect x="{GL + 5}" y="{y0 + 4}" width="200" height="21" rx="10.5"/><circle class="sw {dr}" cx="{GL + 17}" cy="{y0 + 14.5}" r="5"/>'
                 f'<text x="{GL + 28}" y="{y0 + 19.3}"><tspan class="who">{esc(who)}</tspan> <tspan class="what">{esc(what)}</tspan></text></g>')
    y0, h = lanes['BL']
    o.append(f'<line class="band" x1="0" y1="{y0 + h + 8}" x2="{W}" y2="{y0 + h + 8}"/>')
    o.append(f'<line class="ph" id="ph" x1="{GL}" y1="{top - 8}" x2="{GL}" y2="{bottom}" opacity="0"/>')
    for e in evs:
        x, cy, n = e['x'], e['cy'], e['n']
        o.append(f'<g class="pin {e["dir"]} {"solid" if e["solid"] else "hollow"}" id="m{n}" style="display:none"><circle class="halo" cx="{x:.1f}" cy="{cy:.1f}" r="0" opacity="0"/>'
                 f'<g class="body"><circle class="dot" cx="{x:.1f}" cy="{cy:.1f}" r="{R}"/><text x="{x:.1f}" y="{cy + 4:.1f}">{n}</text></g></g>')
        if e['C']:                                  # the figure's short label beside the mark: "start|end dx dy words"
            anchor, dx, dy, words = e['C'].split(' ', 3)
            o.append(f'<text class="call" id="c{n}" x="{x + float(dx):.1f}" y="{cy + float(dy):.1f}" text-anchor="{anchor}" style="display:none">{n} · {esc(words)}</text>')
    o.append('</svg>')
    return '\n'.join(o)


def geom_json():
    ms = lambda d: int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)
    return dict(x0=GL, xb=round(X(BK), 2), x1=W - GR, A=ms(A), BK=ms(BK), C=ms(C), R=R)


# ---------- quotations behind what the strip shows ----------
EXTRA = (  # words on the strip that a record's own "Q" line does not carry: (saved id, the page's words, what they back)
    ('cn-ga31-sv1-reuters-deepseek-yahoo', "These conditions are being decided by China's state planner", 'the label "conditional yes, reported" (the core\'s words since rt1, Nov 26, 2026; Reuters, Jan 30, 2026, on Yahoo Finance; the core cites this open copy since CORE BATCH 12)'),
    ('cn-policy-tencent-us-curbs-relay1', 'following new moves by the United States to restrict chip supplies to China', 'the label "after US curbs"'),
    ('man-cn-factions-wsj-ding', 'Last summer, top Chinese chip developer Huawei Technologies held a closed-door', 'the "traitor" mark stands after a briefing of summer 2025; the report gives no date for the warning'),
    ('man-cn-factions-wsj-ding', 'according to people familiar with the message', 'the same mark: an open mark'),
    ('cn-clips-followup-3-relay1', 'December 8, 2025', 'the dashed line "Dec 8, 2025 · US says it will allow H200": its date'),
    ('cn-acts-reuters-halt-20261118-relay2', 'Nov 18 (Reuters)', 'the dashed line "Nov 17, 2026 · Nvidia reports H200 halt": the report is of Wednesday Nov 18'),
    ('cn-acts-reuters-halt-20261118-relay2', 'said during an earnings call on Tuesday', 'the same line: the call was the day before, Nov 17'),
    ('cn-o38-nvda-q3fy27-call-transcript-pdf', 'we are no longer shipping licensed Hopper Data Center products to China', "the same line, in Nvidia's own transcript of the call (no reason is given there: none is shown)"),
    ('cn-o38-nvda-q3fy27-call-transcript-pdf', 'All our statements are made as of today, November 17, 2026', "the same line: the call's date, in Nvidia's own transcript"),
)
FLAG_CHECKS = ('cn-policy-h20-mofcom', 'cn-clips-followup-3-relay1', 'cn-acts-reuters-halt-20261118-relay2')   # "!" lines of figure_data.txt behind the three dashed lines
NUMBER_CHECKS = ('About 600,000 of Nvidia',)        # "!" lines behind a number in a label


def strip_quotes(evs, checks):
    out = [('#', 'One line per record drawn: the words of its source (the "Q" line of figure/figure_data.txt).', '')]
    for e in evs: out.append((e['sid'], e['Q'], f'mark {e["n"]}'))
    out.append(('#', 'The three dashed lines and the numbers in labels (the "!" lines of figure_data.txt).', ''))
    for sid in FLAG_CHECKS:
        m = [q for s, q in checks if s == sid]
        if not m: sys.exit(f'figure_data.txt has no "!" line for {sid}')
        out.extend((sid, q, 'dashed line') for q in dict.fromkeys(m))
    for start in NUMBER_CHECKS:
        m = list(dict.fromkeys((s, q) for s, q in checks if q.startswith(start)))
        if not m: sys.exit(f'figure_data.txt: no "!" line starting "{start}"')
        out.extend((s, q, 'number in a label') for s, q in m)
    out.append(('#', 'Words on the strip that no "Q" line carries.', ''))
    out.extend(EXTRA)
    return out


def write_quotes(path, lines, head):
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(f'# {head}\n# Columns: saved id <TAB> the page\'s exact words. Written by build.py; checked by scripts/cn_has.py.\n')
        for sid, q, why in lines:
            if sid == '#': fh.write(f'# {q}\n')
            else: fh.write(f'{sid}\t{q}\n')
    return sum(1 for s, _, _ in lines if s != '#')


def run_has(path):
    r = subprocess.run([sys.executable, '-I', str(SCRIPTS / 'cn_has.py'), str(path)], capture_output=True, text=True)
    line = (r.stdout.strip().splitlines() or ['(no output)'])[-1]
    if r.returncode != 0:
        print(r.stdout, r.stderr); sys.exit(f'cn_has.py failed on {path} (exit {r.returncode}); nothing built')
    return line


def made_from(here, files):
    """sha256 of every file a page is built from, keyed by its path relative to the idea's folder. build.py puts this in
    capture.json; frames.py refuses to capture when one of them has changed since (the figure's data file was edited by
    its owner while these outputs were being made: a capture must never show an older state than the page on disk)."""
    out = {}
    for f in files:
        out[os.path.relpath(f, here)] = hashlib.sha256(Path(f).read_bytes()).hexdigest()
    return out


def policy_rows():
    """How many policy pages the project's note read (the "82 policy pages read"): an entry of NOTE_policies_checked.md
    counts as read unless its verdict is PAGE EMPTY; an entry read in an Internet Archive capture is taken at the
    capture; a saved page behind several entries counts once (the note has 103 entries on 83 saved pages, one empty)."""
    docs = []
    for e in re.split(r'(?m)^### Row ', (PROJ / 'NOTE_policies_checked.md').read_text(encoding='utf-8'))[1:]:
        m = re.match(r'(\d+) · ([^·]+) · ([^·]+) · \[([^\]]+)\]', e)
        v = re.search(r'Verdict: \*\*([^*]+)\*\*', e).group(1); c = re.search(r'- Read in: [^\n]*saved as \[([^\]]+)\]', e)
        if v != 'PAGE EMPTY': docs.append(c.group(1) if c else m.group(4))
    return len(set(docs))


# ---------- the page ----------
KEY = ('<ul class="key" id="key">'
       '<li><b><i class="sw away"></i>Away from Nvidia</b><span>holding it back, or choosing home-made chips</span></li>'
       '<li><b><i class="sw toward"></i>Toward Nvidia</b><span>seeking, buying, using or welcoming it</span></li>'
       '<li><b><i class="pr"><i class="mk solid away"></i><i class="mk solid toward"></i></i>Filled</b><span>on the record (a government document, published state media, a filing, a named person)</span></li>'
       '<li><b><i class="pr"><i class="mk hollow away"></i><i class="mk hollow toward"></i></i>Open</b><span>a press report citing unnamed people</span></li>'
       '</ul>')
KEY_SENTENCES = ('Away from Nvidia:', 'holding it back, or choosing home-made chips', 'Toward Nvidia:', 'seeking, buying, using or welcoming it', 'Filled:',
                 'on the record (a government document, published state media, a filing, a named person)', 'Open:', 'a press report citing unnamed people')
HEADLINE = ('Beijing pushed for home-made chips.', 'China’s AI companies still sought Nvidia.')
KEY_W = 150                                        # the key's column, inside the strip's card, in frame pixels


def card_layout(G, pad_top):
    """Sizes of the strip's card in a 1280 px frame: the strip drawn at the left, the key in a column of KEY_W px at the right."""
    svg_w = 1232 - KEY_W
    scale = svg_w / (W - VX)
    svg_h = round(view_h(G) * scale, 1)
    return dict(svg_w=svg_w, svg_h=svg_h, scale=scale, card_h=round(svg_h + pad_top + 7), key_left=8 + svg_w + 8, key_w=KEY_W - 4)


def template_has(*sentences):
    """Each sentence must stand in the figure's template (so the headline, the key and the notes cannot drift from it)."""
    flat = lambda t: re.sub(r'\s+', ' ', html.unescape(t).replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"'))
    t = flat(re.sub(r'<[^>]+>', '', (FIG / 'template.html').read_text(encoding='utf-8')))
    assert 'this sentence is in no template at all' not in t
    for x in sentences:
        if flat(x) not in t: sys.exit(f'not in figure/template.html: {x}')
    return len(sentences)


def tsv(name):
    """Rows of a table in the project's tables folder, as dicts (lines starting # are comments), as scripts/cn_figure_build.py reads them."""
    lines = [l for l in (PROJ / 'tables' / name).read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    head = lines[0].split('\t')
    return [dict(zip(head, l.split('\t'))) for l in lines[1:]]


def house_table():
    """Sums over the licence table (applications for the H200 and AMD's MI325X, status at May 11, 2026, from the Commerce
    Department's Bureau of Industry and Security, BIS; made public by the House Foreign Affairs Committee on Nov 19,
    2026), from tables/house_licence_table.tsv. Its two totals must equal the figures printed in the committee's summary
    (the captions check those there by quotation)."""
    rows = [dict(exp=r['exporter'], chips=int(r['chip_count'].replace(',', '')), status=r['status']) for r in tsv('house_licence_table.tsv')]
    sel = lambda **k: [r for r in rows if all(r[a] == b for a, b in k.items())]
    tot = lambda rs: sum(r['chips'] for r in rs)
    t = dict(all=tot(rows), n_all=len(rows), appr=tot(sel(status='Approved, not shipped')), n_appr=len(sel(status='Approved, not shipped')),
             appr_nv=tot(sel(status='Approved, not shipped', exp='Nvidia')), n_appr_nv=len(sel(status='Approved, not shipped', exp='Nvidia')),
             rwa=tot(sel(status='RWA')), n_rwa=len(sel(status='RWA')))
    if (t['all'], t['n_all'], t['appr'], t['n_appr']) != (3_444_160, 54, 879_868, 21): sys.exit(f"house_licence_table.tsv no longer sums to the summary's figures: {t}")
    t['rwa_pct'] = int(100 * t['rwa'] / t['all'] + 0.5)
    assert 0 < t['appr_nv'] < t['appr'] and 0 < t['rwa'] < t['all']
    return t


def state_media():
    """Count the warnings in the same date windows as argument points 4 and 18."""
    rows = tsv('state_media_items.tsv')
    warning_rows = [r for r in rows if r['stance'] == 'warns']
    forum, = (r for r in warning_rows if r['subject'] != 'chips for AI computing')
    assert forum['saved_id'] == 'cn-media-stdaily-security-forum' and forum['subject'] == 'other', forum
    chips = sum(r['subject'] == 'chips for AI computing' for r in warning_rows)
    warns = sorted((date.fromisoformat(r['date']), r['saved_id'], r['outlet']) for r in warning_rows)
    start, end = date(2025, 7, 31), date(2025, 9, 24)
    h200_start, h200_end = date(2025, 12, 9), date(2026, 1, 14)
    burst = [w for w in warns if start <= w[0] <= end]
    h200 = [w for w in warns if h200_start <= w[0] <= h200_end]
    outside = [w for w in warns if not start <= w[0] <= end]
    last = [w for w in warns if w[0] > h200_end]
    assert 0 < len(warns) < len(rows) and len(burst) + len(outside) == len(warns)
    assert burst and (burst[0][0], burst[-1][0]) == (start, end), burst
    assert h200 and (h200[0][0], h200[-1][0]) == (h200_start, h200_end), h200
    assert last and all(d.year == 2026 and outlet.startswith('Global Times') for d, _, outlet in last), last
    return dict(n=len(rows), warns=len(warns), chips=chips, burst=burst, h200=h200, outside=outside, last=last)


CSS = """
:root { --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#7a7872; --border:rgba(11,11,11,0.12); --link:#1c5cab;
  --font-text:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif; --font-head:"Space Grotesk","Inter",system-ui,sans-serif; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --page:#0d0d0d; --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#8f8d86; --border:rgba(255,255,255,0.14); --link:#86b6ef; color-scheme:dark } }
:root[data-theme="dark"] { --page:#0d0d0d; --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#8f8d86; --border:rgba(255,255,255,0.14); --link:#86b6ef; color-scheme:dark }
* { box-sizing:border-box; }
html { -webkit-text-size-adjust:100%; }
body { margin:0; background:var(--page); color:var(--ink); font-family:var(--font-text); font-size:16px; line-height:1.5; }
.outer { max-width:1312px; margin:0 auto; padding:16px 16px 40px; }
.fit { position:relative; overflow:hidden; width:1280px; height:720px; border-radius:8px; box-shadow:0 0 0 1px var(--border); }
.below { max-width:760px; margin:14px 0 0; }
.below p { margin:0 0 10px; color:var(--ink2); font-size:15px; }
.below p.small { color:var(--muted); font-size:13px; }
.below code { font-size:13px; overflow-wrap:anywhere; }
.below video { display:block; width:100%; height:auto; margin:0 0 12px; border-radius:8px; background:#f9f9f7; box-shadow:0 0 0 1px var(--border); }
.ctl { display:flex; flex-wrap:wrap; align-items:center; gap:10px 14px; margin:0 0 14px; }
.ctl button { font:600 15px/1 var(--font-text); padding:10px 16px; border-radius:8px; border:1px solid var(--border); background:var(--surface); color:var(--ink); cursor:pointer; }
.ctl input { flex:1 1 180px; min-width:0; accent-color:#256abf; }
.ctl span { font-size:13px; color:var(--muted); font-variant-numeric:tabular-nums; white-space:nowrap; }
.capture body { background:#f9f9f7; } .capture .outer { max-width:none; margin:0; padding:0; } .capture .below { display:none; }
.capture .fit { border-radius:0; box-shadow:none; }

/* the stage is one video frame, 1280 x 720, always in the light colours of figure/template.html */
.stage { position:absolute; left:0; top:0; width:1280px; height:720px; overflow:hidden; transform-origin:0 0; color-scheme:light;
  --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#7a7872; --grid:#e1e0d9; --axis:#c3c2b7; --border:rgba(11,11,11,0.12);
  --wash:rgba(11,11,11,0.045); --toward:#256abf; --away:#c44e18; --pin-on:#ffffff;
  background:var(--page); color:var(--ink); font-family:var(--font-text); line-height:1.4; -webkit-font-smoothing:antialiased; }
.stage p, .stage h1, .stage ul { margin:0; }
.stage .eyebrow { position:absolute; font:700 12px/1 var(--font-text); letter-spacing:0.1em; text-transform:uppercase; color:var(--muted); white-space:nowrap; }
.stage h1 { position:absolute; font-family:var(--font-head); font-weight:700; letter-spacing:-0.015em; color:var(--ink); white-space:nowrap; }
.stage ul.key { position:absolute; list-style:none; padding:0 0 0 10px; margin:0; color:var(--ink2); font-size:12.5px; line-height:1.36; border-left:1px solid var(--grid); }
.stage ul.key li { display:block; margin:0 0 11px; }
.stage ul.key li:last-child { margin-bottom:0; }
.stage ul.key b { display:flex; align-items:center; gap:6px; color:var(--ink); font-weight:600; font-size:12.5px; white-space:nowrap; }
.stage ul.key span { display:block; margin-top:2px; }
.stage i.sw { display:inline-block; flex:none; width:13px; height:13px; border-radius:50%; }
.stage i.sw.toward { background:var(--toward); } .stage i.sw.away { background:var(--away); }
.stage i.pr { display:inline-flex; flex:none; gap:3px; }
.stage i.mk { display:inline-block; width:14px; height:14px; border-radius:50%; border:2.5px solid; }
.stage i.mk.away { border-color:var(--away); } .stage i.mk.toward { border-color:var(--toward); }
.stage i.mk.hollow { background:var(--surface); } .stage i.mk.solid.away { background:var(--away); } .stage i.mk.solid.toward { background:var(--toward); }
.stage .clock { position:absolute; text-align:right; white-space:nowrap; }
.stage #date { font-family:var(--font-head); font-weight:700; letter-spacing:-0.01em; color:var(--ink); font-variant-numeric:tabular-nums; }
.stage #count, .stage #tally { color:var(--ink2); font-weight:500; font-variant-numeric:tabular-nums; }
.stage .card { position:absolute; background:var(--surface); border:1px solid var(--border); border-radius:12px; }
.stage .card svg { position:absolute; display:block; }
.stage svg text { font-family:var(--font-text); text-rendering:geometricPrecision; }
/* round 10: geometricPrecision keeps the strip's words in proportion when the page scales the 1280 frame down (phone
   view, scale about 0.28): without it the browser rounds each small glyph's width up, and the Dec 8 label ran 2 px into
   the Nov 17 label at 390 px (scratch_r10/test_gp.py). */
.era { fill:var(--wash); }
.grid { stroke:var(--grid); stroke-width:1; } .grid.yr { stroke:var(--axis); }
.tick { font-size:12px; font-weight:500; fill:var(--muted); } .tick.yr { fill:var(--ink2); font-weight:600; }
.eranote { font-size:11px; fill:var(--muted); }
.flag { stroke:var(--ink2); stroke-width:1; stroke-dasharray:3 3; } .flagt { font-size:12px; font-weight:600; fill:var(--ink2); }
.lane { stroke:var(--grid); stroke-width:1; } .band { stroke:var(--axis); stroke-width:1.5; }
.call { font-size:12px; font-weight:600; fill:var(--ink); paint-order:stroke; stroke:var(--surface); stroke-width:4px; stroke-linejoin:round; }
.rowtag rect { fill:var(--surface); stroke:var(--axis); stroke-width:1; }
.rowtag text { font-size:13.5px; } .rowtag .who { font-weight:700; fill:var(--ink); } .rowtag .what { font-weight:500; fill:var(--ink2); }
circle.sw.toward { fill:var(--toward); } circle.sw.away { fill:var(--away); }
.rowhl { fill:rgba(11,11,11,0.04); }
.ph { stroke:var(--ink); stroke-width:1.3; }
.pin circle.dot { stroke-width:2.5; }
.pin.toward circle.dot { stroke:var(--toward); } .pin.away circle.dot { stroke:var(--away); }
.pin.hollow circle.dot { fill:var(--surface); }
.pin.solid.toward circle.dot { fill:var(--toward); } .pin.solid.away circle.dot { fill:var(--away); }
.pin text { font-size:11px; font-weight:700; text-anchor:middle; fill:var(--ink); font-variant-numeric:tabular-nums; }
.pin.solid text { fill:var(--pin-on); }
.pin circle.halo { fill:none; stroke-width:2.5; } .pin.toward circle.halo { stroke:var(--toward); } .pin.away circle.halo { stroke:var(--away); }
.stage .foot { position:absolute; color:var(--ink2); } .stage .foot b { color:var(--ink); font-weight:600; }
.stage .draft { position:absolute; color:var(--muted); white-space:nowrap; }
.stage .nb { white-space:nowrap; }
"""

JS = r"""
(function () {
'use strict';
const S = JSON.parse(document.getElementById('scene').textContent);
const CAP = new URLSearchParams(location.search).has('capture');
if (CAP) document.documentElement.classList.add('capture');
const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'];
const $ = id => document.getElementById(id);
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const easeOut = u => 1 - Math.pow(1 - clamp(u, 0, 1), 3);
// how far "on" a thing is at time t, for a list of [from, to] spans; it rises and falls over `fade` seconds
function level(spans, t, fade) {
  let v = 0;
  for (const r of spans) v = Math.max(v, Math.min(clamp((t - r[0]) / fade, 0, 1), 1 - clamp((t - r[1]) / fade, 0, 1)));
  return v;
}
function pop(u) { return u >= 1 ? 1 : (u < 0.6 ? 0.35 + 0.83 * easeOut(u / 0.6) : 1.18 - 0.18 * ((u - 0.6) / 0.4)); }
function dateAt(x) {
  const g = S.geom;
  const ms = x < g.xb ? g.A + (x - g.x0) / (g.xb - g.x0) * (g.BK - g.A) : g.BK + (x - g.xb) / (g.x1 - g.xb) * (g.C - g.BK);
  const d = new Date(Math.min(ms, g.C - 1));
  return MON[d.getUTCMonth()] + ' ' + d.getUTCFullYear();
}
const marks = S.marks.map(m => { const g = $('m' + m.n); return Object.assign({ g: g, body: g.querySelector('.body'), halo: g.querySelector('.halo'), call: $('c' + m.n) }, m); });
const flags = (S.flags || []).map(f => Object.assign({ el: $('flag' + f.i) }, f));
const caps = (S.chapters || []).map(c => Object.assign({ el: $('cap' + c.k) }, c));
const rows = Object.keys(S.rows || {}).map(k => ({ el: $('row-' + k), spans: S.rows[k] }));
const ph = $('ph'), elDate = $('date'), elCount = $('count'), elTally = $('tally'), elBar = $('bar');

function init() {            // the row tags are sized to their words, once the fonts are in
  document.querySelectorAll('#strip g.rowtag').forEach(g => {
    const t = g.querySelector('text'), r = g.querySelector('rect');
    r.setAttribute('width', (t.getComputedTextLength() + 33).toFixed(1));
  });
}

window.setT = function (t) {
  let shown = 0;
  for (const m of marks) {
    const age = t - m.on;
    if (age < 0) { m.g.style.display = 'none'; if (m.call) m.call.style.display = 'none'; continue; }
    shown++;
    const f = S.dim + (1 - S.dim) * level(m.focus, t, 0.35), s = pop(age / 0.36);
    m.g.style.display = '';
    m.body.setAttribute('transform', 'translate(' + m.x + ' ' + m.cy + ') scale(' + s.toFixed(4) + ') translate(' + (-m.x) + ' ' + (-m.cy) + ')');
    m.body.setAttribute('opacity', (clamp(age / 0.12, 0, 1) * f).toFixed(3));
    let ho = 0, hr = 0;
    for (const p of m.pulse) { const u = (t - p) / 0.7; if (u >= 0 && u < 1) { ho = 0.6 * (1 - u); hr = S.geom.R + 3 + 13 * easeOut(u); } }
    m.halo.setAttribute('r', hr.toFixed(2)); m.halo.setAttribute('opacity', ho.toFixed(3));
    if (m.call) { m.call.style.display = ''; m.call.setAttribute('opacity', (clamp((age - 0.1) / 0.3, 0, 1) * f).toFixed(3)); }
  }
  for (const f of flags) f.el.setAttribute('opacity', clamp((t - f.on) / 0.3, 0, 1).toFixed(3));
  for (const r of rows) r.el.setAttribute('opacity', level(r.spans, t, 0.35).toFixed(3));
  // the moving line and the running date
  let x = S.segs.length ? S.segs[0].x0 : S.geom.x1, on = 0;
  for (const g of S.segs) {
    if (t < g.t0) break;
    x = g.x0 + (g.x1 - g.x0) * clamp((t - g.t0) / (g.t1 - g.t0), 0, 1);
    on = Math.min(clamp((t - g.t0) / 0.2, 0, 1), 1 - clamp((t - g.t1) / 0.3, 0, 1));
  }
  ph.setAttribute('x1', x.toFixed(2)); ph.setAttribute('x2', x.toFixed(2)); ph.setAttribute('opacity', (0.5 * on).toFixed(3));
  if (elDate) elDate.textContent = dateAt(x);
  if (elCount) elCount.textContent = shown + ' of ' + S.total + ' records';
  if (elTally) elTally.style.opacity = clamp((t - S.tally_on) / 0.4, 0, 1).toFixed(3);
  for (let i = 0; i < caps.length; i++) {
    const c = caps[i], last = i === caps.length - 1;
    const o = Math.min(i === 0 ? 1 : clamp((t - c.t0) / 0.35, 0, 1), last ? 1 : 1 - clamp((t - (c.t1 - 0.25)) / 0.25, 0, 1));   // the first caption is there from the first frame
    c.el.style.opacity = o.toFixed(3); c.el.style.visibility = o > 0 ? 'visible' : 'hidden';
  }
  if (elBar) elBar.style.width = (100 * clamp(t / ((S.frames - 1) / S.fps), 0, 1)).toFixed(2) + '%';
};
// what the frame at time t says in its caption box (frames.py compares this with the checked captions)
window.captionText = function () {
  const c = caps.filter(c => +c.el.style.opacity > 0.99);
  if (c.length !== 1) return '(' + c.length + ' captions visible)';
  const part = sel => [...c[0].el.querySelectorAll(sel)].map(el => {
    const k = el.cloneNode(true);
    k.querySelectorAll('.c').forEach(ch => ch.replaceWith(document.createTextNode(' [' + ch.textContent + ']')));
    k.querySelectorAll('.ln').forEach(ln => ln.append(' '));
    return k.textContent.replace(/\s+/g, ' ').trim();
  });
  return { k: c[0].k, title: part('.ttl')[0], text: part('.txt')[0], items: part('.src li, .nums li') };
};
// does anything in the caption box or the frame run past its edge, or a label run into a mark?
window.overflowReport = function () {
  const out = [], st = $('stage').getBoundingClientRect();
  for (const c of caps) {
    if (+c.el.style.opacity < 0.99) continue;
    const box = c.el.parentElement.getBoundingClientRect();
    for (const el of c.el.querySelectorAll('*')) { const r = el.getBoundingClientRect(); if (r.width && (r.bottom > box.bottom + 0.5 || r.right > box.right + 0.5)) { out.push('caption ' + c.k + ': ' + el.className + ' ends at ' + Math.round(r.right) + ',' + Math.round(r.bottom) + ' in a box ending at ' + Math.round(box.right) + ',' + Math.round(box.bottom)); break; } }
  }
  // a label beside a mark must stand clear of every mark on screen (the figure's first label for mark 31 ran 2.2 units into mark 25;
  // by design the nearest a label comes to a mark is 2.7 units, to its own)
  for (const m of marks) {
    if (!m.call || m.call.style.display === 'none') continue;
    const b = m.call.getBBox();
    for (const o of marks) {
      if (o.g.style.display === 'none') continue;
      const dx = Math.max(b.x - o.x, 0, o.x - (b.x + b.width)), dy = Math.max(b.y - o.cy, 0, o.cy - (b.y + b.height));
      const gap = Math.hypot(dx, dy) - (S.geom.R + 1.25);
      if (gap < 1.5) out.push('label of mark ' + m.n + ' stands ' + gap.toFixed(1) + ' from mark ' + o.n + ' (under 1.5 strip units)');
    }
  }
  const card = $('card').getBoundingClientRect();
  for (const el of $('stage').querySelectorAll('ul.key li, #count')) { const r = el.getBoundingClientRect(); if (el.closest('#card') && r.width && (r.bottom > card.bottom - 2 || r.right > card.right - 2)) out.push((el.id || 'a key line') + ' runs past the card'); }
  const hd = $('h1').getBoundingClientRect(), ck = document.querySelector('.clock').getBoundingClientRect();
  if (hd.right > ck.left - 12 && hd.bottom > ck.top && hd.top < ck.bottom) out.push('the headline runs into the date');
  for (const el of $('stage').querySelectorAll('h1, .eyebrow, ul.key li, .clock, .foot, .draft')) { const r = el.getBoundingClientRect(); if (r.width && (r.right > st.right + 0.5 || r.bottom > st.bottom + 0.5)) out.push((el.className || el.tagName) + ' runs past the frame'); }
  return out;
};

// for each label on screen: how near it comes to its own mark and to the nearest other mark, in strip units and frame pixels
window.labelGaps = function () {
  const k = $('strip').getBoundingClientRect().width / $('strip').viewBox.baseVal.width, out = [];
  for (const m of marks) {
    if (!m.call || m.call.style.display === 'none') continue;
    const b = m.call.getBBox(); let own = null, best = null;
    for (const o of marks) {
      if (o.g.style.display === 'none') continue;
      const dx = Math.max(b.x - o.x, 0, o.x - (b.x + b.width)), dy = Math.max(b.y - o.cy, 0, o.cy - (b.y + b.height));
      const gap = Math.hypot(dx, dy) - (S.geom.R + 1.25);
      if (o.n === m.n) own = gap; else if (best === null || gap < best[1]) best = [o.n, gap];
    }
    out.push({ n: m.n, text: m.call.textContent, own: +own.toFixed(1), other: best[0], gap: +best[1].toFixed(1), px: +(best[1] * k).toFixed(1) });
  }
  return out;
};

const fitEl = $('fit'), stage = $('stage'), play = $('play'), seek = $('seek'), clock = $('clock');
let frame = S.frames - 1, playing = false;
function fit() {
  if (CAP) return;
  const k = Math.min(1, (document.documentElement.clientWidth - 32) / 1280);
  fitEl.style.width = (1280 * k).toFixed(1) + 'px'; fitEl.style.height = (720 * k).toFixed(1) + 'px'; stage.style.transform = 'scale(' + k + ')';
}
function show(f) {
  frame = clamp(Math.round(f), 0, S.frames - 1); window.setT(frame / S.fps);
  seek.value = frame; clock.textContent = (frame / S.fps).toFixed(1) + ' s of ' + ((S.frames - 1) / S.fps).toFixed(1) + ' s';
}
play.addEventListener('click', () => {
  if (playing) { playing = false; play.textContent = 'Play'; return; }
  playing = true; play.textContent = 'Pause';
  const from = frame >= S.frames - 1 ? 0 : frame, start = performance.now() - from / S.fps * 1000;
  (function tick() {
    if (!playing) return;
    const f = Math.floor((performance.now() - start) / 1000 * S.fps);
    if (f >= S.frames - 1) { show(S.frames - 1); playing = false; play.textContent = 'Play again'; return; }
    show(f); requestAnimationFrame(tick);
  })();
});
seek.addEventListener('input', () => { playing = false; play.textContent = 'Play'; show(+seek.value); });
window.addEventListener('resize', fit);
// Capture works before the video and its opening still exist.
if (!CAP) document.querySelectorAll('video[data-src]').forEach(v => {
  if (v.dataset.poster) v.poster = v.dataset.poster;
  v.src = v.dataset.src;
});
const ready = () => { init(); fit(); const m = /t=([\d.]+)/.exec(location.hash); show(m ? parseFloat(m[1]) * S.fps : S.frames - 1); window.READY = true; };
const faces = ['700 33px "Space Grotesk"', '400 16px "Inter"', '500 16px "Inter"', '600 16px "Inter"', '700 16px "Inter"'];
Promise.all(faces.map(f => document.fonts.load(f).catch(() => null))).then(() => document.fonts.ready).then(ready, ready);
})();
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%%TITLE%%</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap">
<style>%%CSS%%</style>
</head>
<body>
<div class="outer">
 <div class="fit" id="fit"><div class="stage" id="stage">
%%STAGE%%
 </div></div>
 <div class="below">
  <div class="ctl"><button id="play" type="button">Play</button><input id="seek" type="range" min="0" max="%%LAST%%" step="1" value="%%LAST%%" aria-label="Position in the animation"><span id="clock"></span></div>
%%BELOW%%
 </div>
</div>
<script type="application/json" id="scene">%%SCENE%%</script>
<script>%%JS%%</script>
</body>
</html>
"""


def page(title, stage, below, scene, extra_css=''):
    assert 2 <= len(title.split()) <= 4, title
    parts = {'TITLE': esc(title), 'CSS': CSS + extra_css, 'STAGE': stage, 'BELOW': below, 'LAST': str(scene['frames'] - 1),
             'SCENE': json.dumps(scene, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'), 'JS': JS}
    out = PAGE
    for k, v in parts.items():
        assert f'%%{k}%%' in out, k
        out = out.replace(f'%%{k}%%', v)
    assert '%%' not in out, out[out.index('%%'):][:40]
    return out
