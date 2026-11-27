"""Build the map page "Places the sources name for Nvidia chips" (China chip-policy project, output idea 18).
(Round 12, Nov 26, 2026: folder and files renamed from the output's old title; the old folder is kept, unchanged.
 Round 13: the first note says which records have a mark on each place they name, from the G lines.)

Run: python3 -I build.py                                      checks every quotation, writes the page
     python3 -I build.py --png    the same, then exports PNG images of it
The map shows places that saved reports name. It does not show where chips are; the page and the map say so.
Reads, in this folder:
  places.txt      the records (its header explains the format): each is what one saved page says about the place or places it names
  template.html   the page around the map
  ../../../tables/house_licence_table.tsv   application counts and chip totals for the BIS record
  mapdata/ne_10m_admin_1_states_provinces.geojson   Natural Earth 1:10m states and provinces, version 5.1.2, public domain
                  (https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_10m_admin_1_states_provinces.geojson);
                  its sha256 is checked below. It is only parsed as data.
Nothing is written unless:
  1. every Q, +, ! and D line is found in its saved copy (research/primary/<id>), invisible characters ignored;
  2. every pair of quote marks in a T line, and in the finished page, holds words that are part of a checked line;
  3. scripts/cn_has.py passes on quotes.tsv (written here; a line that spans an invisible character in the saved copy
     is written in the pieces cn_has.py can find, and build.py itself has checked the whole line in one piece);
  4. the counts the template's sentences rest on hold (the build stops if a record is added that breaks them).
Writes: places_the_sources_name.html, quotes.tsv, places_drawn.tsv and, with --png, places_the_sources_name_full.png and
places_the_sources_name_map.png. The map is projected here (Lambert azimuthal equal-area) to inline SVG: no outside
library is needed to build or to view it. Before the page is called done: scripts/render_and_look.py.
"""
import hashlib, html, json, math, re, subprocess, sys, unicodedata
from datetime import date
from pathlib import Path

F = Path(__file__).resolve().parent
ROOT = F.parents[4]                                   # .
assert (ROOT / 'scripts' / 'cn_srclib.py').exists(), ROOT
sys.path.insert(0, str(ROOT / 'scripts'))
import cn_srclib as L   # noqa: E402

MAP = F / 'mapdata' / 'ne_10m_admin_1_states_provinces.geojson'
MAP_SHA = '22d0e3ad85eb3e27f17cabf8ba2d50e554fbc27a87796ff891d958185da62fb5'
OUT = 'places_the_sources_name'
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']
GROUPS = {'out': 'Outside mainland China', 'there': 'On the mainland: chips reported or said to be there',
          'plan': 'On the mainland: plans, tenders and contracts that name Nvidia chips'}
esc = html.escape


def smart(s):
    return re.sub(r'"([^"]*)"', '“\\1”', s).replace("'", '’')


# ---------- the records and their quotations ----------
def load():
    recs, extra, dates, cur = [], [], [], None
    for n, ln in enumerate((F / 'places.txt').read_text(encoding='utf-8').splitlines(), 1):
        if not ln.strip() or ln.startswith('#'): continue
        if ln.startswith('@ '):
            _, num, group, kind, status, direction, d, sid = ln.split()
            assert group in GROUPS and kind in ('paper', 'doc', 'rec', 'press') and status in ('there', 'plan') and direction in ('away', 'toward', 'us'), (n, ln)
            cur = dict(n=int(num), group=group, kind=kind, status=status, dir=direction, date=date.fromisoformat(d), sid=sid,
                       P='', W='', T='', S='', K='', Q='', U='', G='', F='', rawT='', plus=[], M=[], L=[])
            recs.append(cur)
        elif ln.startswith('! '):
            sid, q = ln[2:].split(' | ', 1); extra.append((sid.strip(), q.strip()))
        elif ln.startswith('D '):
            sid, q = ln[2:].split(' | ', 1); dates.append((sid.strip(), q.strip()))
        elif ln.startswith('A '):
            assert 'A' not in cur, f'line {n}: duplicate licence subtotal'
            applications, chips = ln[2:].split()
            cur['A'] = (int(applications), int(chips))
        elif ln.startswith('+ '):
            body = ln[2:].strip()
            if body.startswith('@'):
                sid, q = body[1:].split(' | ', 1); cur['plus'].append((sid.strip(), q.strip()))
            else: cur['plus'].append((cur['sid'], body))
        elif ln[:2] in ('M ', 'L '): cur[ln[0]].append(ln[2:].strip())
        elif ln[:2] in ('P ', 'W ', 'T ', 'S ', 'K ', 'Q ', 'U ', 'G ', 'F '):
            if ln[0] == 'T': cur['rawT'] = ln[2:].strip()
            if ln[0] == 'K': assert '"' not in ln and '“' not in ln, f'line {n}: no quote marks in a K line'
            cur[ln[0]] = smart(ln[2:].strip()) if ln[0] in 'PWTSK' else ln[2:].strip()
        else: sys.exit(f'line {n} not understood: {ln[:60]}')
    assert [r['n'] for r in recs] == list(range(1, len(recs) + 1)), 'records must be numbered 1, 2, 3 ... in order'
    return recs, extra, dates


def no_cf(s):
    """Without invisible format characters (zero-width space, word joiner ...), which some saved pages hold between words."""
    return ''.join(c for c in s if unicodedata.category(c) != 'Cf')


def has(q, sid):
    s = L.squash(no_cf(q))
    return len(s) >= 6 and s in no_cf(L.page(sid))


def pieces(q, sid):
    """The quotation cut where the saved copy holds an invisible character, so scripts/cn_has.py can find each piece."""
    raw = L.page(sid)
    keep = [i for i, c in enumerate(raw) if unicodedata.category(c) != 'Cf']
    clean = ''.join(raw[i] for i in keep)
    s = L.squash(no_cf(q)); at = clean.find(s)
    assert at >= 0, (sid, q)
    cuts = {k - at + 1 for k in range(at, at + len(s) - 1) if keep[k + 1] != keep[k] + 1}    # squashed characters before each cut
    out, cur, done = [], '', 0
    for ch in q:
        cur += ch; done += len(L.squash(no_cf(ch)))
        if done in cuts and len(L.squash(no_cf(ch))):
            out.append(cur.strip()); cur = ''; cuts.discard(done)
    if cur.strip(): out.append(cur.strip())
    for p in out:
        assert len(L.squash(p)) >= 6, f'a piece of this line is too short for cn_has.py; reword it: {q!r} -> {p!r}'
        assert L.has(p, sid), (sid, p)
    return out


def within(seg, verified):
    s = L.squash(no_cf(seg))
    return bool(s) and any(s in v for v in verified)


def shown_date(d):
    return f'{MON[d.month - 1]} {d.day}, {d.year}'


def k_ok(r):
    """Round 11 (Nov 26, 2026): the list under the map gives each place as a named source's dated report. The K line must
    begin "in", name the outlet or document that the S line names first, give the record's own date, and, for a press
    report, say that the outlet did not name its people."""
    k = r['K']
    return (k.startswith('in ') and shown_date(r['date']) in k and r['S'].split(',')[0].split(' ')[0].lower() in k.lower()
            and (r['kind'] != 'press' or 'did not name' in k))


def verify(recs, extra, dates):
    bad = []
    for r in recs:
        if not (r['P'] and r['W'] and r['T'] and r['S'] and r['K'] and r['Q'] and r['G']): bad.append(f"incomplete block {r['n']} {r['sid']}")
        if not k_ok(r): bad.append(f"record {r['n']}: the K line does not name the source and its date as the S and @ lines give them: {r['K']}")
        for sid, q in [(r['sid'], r['Q'])] + r['plus']:
            if not has(q, sid): bad.append(f"NOT FOUND in {sid}: {q[:80]}")
        own = [L.squash(no_cf(q)) for sid, q in [(r['sid'], r['Q'])] + r['plus']]          # the record's own checked lines, whichever saved page each stands in
        assert r['rawT'].count('"') % 2 == 0, f"odd number of quote marks: {r['rawT']}"
        for seg in re.findall(r'"([^"]*)"', r['rawT']):
            if not within(seg, own): bad.append(f"record {r['n']}: quoted words not part of a checked line of {r['sid']}: {seg}")
        if '"' in r['S'] or '“' in r['S'] or '“' in r['P'] or '“' in r['W']: bad.append(f"quote marks in a P, W or S line, record {r['n']}")
    for sid, q in extra + dates:
        if not has(q, sid): bad.append(f'NOT FOUND in {sid}: {q[:80]}')
    assert not has('this sentence was never written by anyone at all', recs[0]['sid']), 'the control quotation was found: the check cannot fail'
    assert not within('a place nobody ever named', [L.squash(r['Q']) for r in recs]), 'the control for quoted words passed: the check cannot fail'
    assert not k_ok(dict(recs[0], K='in a report of no date, by two people it did not name')) and not k_ok(dict(recs[0], K=recs[0]['K'].replace('Reuters', 'a news agency'))), 'the control for the K check passed: the check cannot fail'
    return bad


def page_quotes(page, recs, extra):
    verified = [L.squash(no_cf(q)) for r in recs for _, q in [(0, r['Q'])] + r['plus']] + [L.squash(no_cf(q)) for _, q in extra]
    text = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', page)
    text = html.unescape(re.sub(r'(?s)<[^>]+>', ' ', text))
    assert text.count('“') == text.count('”'), 'unbalanced curly quote marks in the page text'
    segs = re.findall(r'“([^“”]*)”', text)
    return segs, [s for s in segs if not within(s, verified)]


# ---------- the map ----------
LON0, LAT0, RKM = 106.0, 27.0, 6371.0088
S0, C0 = math.sin(math.radians(LAT0)), math.cos(math.radians(LAT0))
W, PAD, MARGIN, TOL, TOL_FAR, R = 800, 0.025, 14, 0.3, 0.45, 10        # TOL: how far (px) a thinned outline may stray; coarser outside the mainland
NOTE_AT = (139.0, 21.5)                               # the two-line note on the map stands at this latitude (open sea east of Taiwan), right-aligned at the frame's edge
EAST = (141.3, 35.0)                                  # the frame reaches east to here, so Japan's main island is recognisable
CTX = [('Mainland China', 103.0, 29.6, 'middle'), ('Mongolia', 103.5, 46.9, 'middle'), ('India', 79.5, 24.5, 'middle'), ('Japan', 139.4, 37.3, 'middle'),
       ('Malaysia', 101.9, 5.5, 'end'), ('Malaysia', 114.9, 2.9, 'middle'), ('Singapore', 104.5, 1.0, 'start')]   # orientation only; not marks


def project(lon, lat):
    """Lambert azimuthal equal-area, centred on LON0, LAT0; x east and y north in km."""
    lam, phi = math.radians(lon - LON0), math.radians(lat)
    sp, cp, cl = math.sin(phi), math.cos(phi), math.cos(lam)
    k = math.sqrt(2.0 / max(1e-9, 1.0 + S0 * sp + C0 * cp * cl))
    return RKM * k * cp * math.sin(lam), RKM * k * (C0 * sp - S0 * cp * cl)


def polys_of(g):
    return g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]


def area(pts):
    return 0.5 * sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts)))


def clip_ring(pts, x0, y0, x1, y1):
    """Sutherland-Hodgman: the ring cut to a rectangle."""
    def cut(pts, inside, cross):
        out = []
        if not pts: return out
        prev = pts[-1]; pin = inside(prev)
        for cur in pts:
            cin = inside(cur)
            if cin != pin: out.append(cross(prev, cur))
            if cin: out.append(cur)
            prev, pin = cur, cin
        return out
    def xat(a, b, x): return (x, a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]))
    def yat(a, b, y): return (a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]), y)
    pts = cut(pts, lambda p: p[0] >= x0, lambda a, b: xat(a, b, x0))
    pts = cut(pts, lambda p: p[0] <= x1, lambda a, b: xat(a, b, x1))
    pts = cut(pts, lambda p: p[1] >= y0, lambda a, b: yat(a, b, y0))
    return cut(pts, lambda p: p[1] <= y1, lambda a, b: yat(a, b, y1))


def simplify(pts, tol):
    """Douglas-Peucker on an open line, without recursion."""
    if len(pts) < 3: return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1: continue
        ax, ay = pts[a]; bx, by = pts[b]; dx, dy = bx - ax, by - ay; d2 = dx * dx + dy * dy
        best, bi = -1.0, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            if d2 == 0: d = math.hypot(px - ax, py - ay)
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / d2))
                d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
            if d > best: best, bi = d, i
        if best > tol:
            keep[bi] = True; stack.append((a, bi)); stack.append((bi, b))
    return [p for p, k in zip(pts, keep) if k]


def simplify_ring(pts, tol):
    if len(pts) < 5: return pts
    far = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2)
    a = simplify(pts[:far + 1], tol); b = simplify(pts[far:] + [pts[0]], tol)
    return a[:-1] + b[:-1]


def dpath(rings, close=True):
    out = []
    for r in rings:
        out.append('M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in r) + ('Z' if close else ''))
    return ''.join(out)


def build_map(recs):
    blob = MAP.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == MAP_SHA, 'the map file is not the one this build was written for'
    feats = []
    for f in json.loads(blob)['features']:
        g, p = f['geometry'], f['properties']
        if not g: continue
        polys = polys_of(g)
        xs = [c[0] for po in polys for c in po[0]]; ys = [c[1] for po in polys for c in po[0]]
        if max(xs) < 55 or min(xs) > 160 or max(ys) < -15 or min(ys) > 62: continue
        iso = p.get('iso_3166_2') or ''
        feats.append(dict(admin=p['admin'], iso=iso, name=p.get('name') or '', lab=(p.get('longitude'), p.get('latitude')), polys=polys,
                          main=(p['admin'] == 'China' and not iso.endswith('~')),      # ids ending in ~ are island groups, not provinces
                          km=[[[project(c[0], c[1]) for c in ring] for ring in po] for po in polys]))
    by_iso = {f['iso']: f for f in feats if f['iso']}
    by_admin = {}
    for f in feats: by_admin.setdefault(f['admin'], []).append(f)

    def find(tok):
        kind, key = tok.split(':', 1)
        got = [by_iso[key]] if kind == 'iso' and key in by_iso else by_admin.get(key, []) if kind == 'admin' else []
        assert got, f'not in the map file: {tok}'
        return got

    def centre(fs):
        a = cx = cy = 0.0
        for f in fs:
            for po in f['km']:
                ring = po[0]; s = 0.0; sx = sy = 0.0
                for i in range(len(ring)):
                    x0, y0 = ring[i - 1]; x1, y1 = ring[i]; cr = x0 * y1 - x1 * y0
                    s += cr; sx += (x0 + x1) * cr; sy += (y0 + y1) * cr
                if s:
                    a += abs(s) / 2; cx += abs(s) / 2 * sx / (3 * s); cy += abs(s) / 2 * sy / (3 * s)
        return cx / a, cy / a

    # the frame: mainland China and every area a record names, east to EAST, with a little air
    named, extra_pts = [f for f in feats if f['main']], []
    for r in recs:
        anchors, areas = [x.strip() for x in r['G'].split('|')]
        r['areas'] = [f for tok in areas.split(';') if tok.strip() for f in find(tok.strip())]
        r['anch'] = []
        for tok in anchors.split(';'):
            tok = tok.strip()
            if tok == 'centre':
                assert r['areas'], r['n']; r['anch'].append(('centre', centre(r['areas'])))
            elif tok.startswith('iso:'):
                f = find(tok)[0]; assert f['lab'][0] is not None, tok
                r['anch'].append((tok, project(*f['lab'])))
            else: r['anch'].append((tok, centre(find(tok))))
            if r['F'] == 'anchors': extra_pts.append(r['anch'][-1][1])          # this record: only its marks count for the frame
            elif tok != 'centre': named += find(tok)
        assert r['F'] in ('', 'anchors'), r['F']
        named += r['areas']
    pts = [c for f in named for po in f['km'] for c in po[0]] + [project(*EAST)] + extra_pts
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts); y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    px, py = (x1 - x0) * PAD, (y1 - y0) * PAD
    x0, x1, y0, y1 = x0 - px, x1 + px, y0 - py, y1 + py
    sc = W / (x1 - x0); H = round((y1 - y0) * sc)
    to = lambda x, y: ((x - x0) * sc, (y1 - y) * sc)

    # shapes: each feature cut to the frame and thinned
    npts = 0
    for f in feats:
        rings = []
        keep_small = f['admin'] in ('Hong Kong S.A.R.', 'Macau S.A.R') or any(f is a for r in recs for a in r['areas'])   # small places a record names stay
        for po in f['km']:
            for ring in po:
                q = [to(*c) for c in ring[:-1]]
                if max(p[0] for p in q) < -MARGIN or min(p[0] for p in q) > W + MARGIN or max(p[1] for p in q) < -MARGIN or min(p[1] for p in q) > H + MARGIN: continue
                q = clip_ring(q, -MARGIN, -MARGIN, W + MARGIN, H + MARGIN)
                if len(q) < 3: continue
                q = simplify_ring(q, TOL if (f['main'] or keep_small) else TOL_FAR)
                if len(q) < 3 or abs(area(q)) < (0.12 if keep_small else 0.7 if f['main'] else 1.6): continue
                rings.append(q); npts += len(q)
        f['d'] = dpath(rings)

    # borders between countries: a segment that two countries' shapes share, drawn once
    owners = {}
    key = lambda a, b: (a, b) if a <= b else (b, a)
    rnd = lambda c: (round(c[0], 5), round(c[1], 5))
    for f in feats:
        for po in f['polys']:
            for ring in po:
                prev = rnd(ring[0])
                for c in ring[1:]:
                    cur = rnd(c)
                    if cur != prev: owners.setdefault(key(prev, cur), set()).add(f['admin'])
                    prev = cur
    done, lines = set(), []
    for f in feats:
        for po in f['polys']:
            for ring in po:
                run, prev = [], rnd(ring[0])
                for c in ring[1:] + [None]:
                    cur = rnd(c) if c is not None else None
                    k = key(prev, cur) if cur is not None and cur != prev else None
                    if k is not None and len(owners[k]) > 1 and k not in done:
                        done.add(k)
                        if not run: run = [prev]
                        run.append(cur)
                    elif run:
                        lines.append(run); run = []
                    if cur is not None: prev = cur
    edges = []
    for run in lines:
        q = [to(*project(*c)) for c in run]
        part = []
        for p in q + [None]:
            if p is not None and -MARGIN <= p[0] <= W + MARGIN and -MARGIN <= p[1] <= H + MARGIN: part.append(p)
            else:
                if len(part) > 1:
                    part = simplify(part, TOL); edges.append(part); npts += len(part)
                part = []
    nborder = len(edges)

    tinted = []
    for r in recs:
        for f in r['areas']:
            if f not in tinted: tinted.append(f)
    for i, f in enumerate(feats): f['id'] = f'f{i}'
    land = [f for f in feats if f['d'] and not f['main']]; main = [f for f in feats if f['d'] and f['main']]
    for f in tinted: assert f['d'], f['name']
    assert len(main) == 31, f'{len(main)} mainland provinces drawn; the file holds 31'

    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="map-t map-d"><title id="map-t">Map of East and Southeast Asia with the places that saved reports name</title>'
           f'<desc id="map-d">Mainland China is drawn darker than its neighbours. Provinces and countries that a source names are shaded blue. Each numbered mark is one record, listed below the map: '
           'circles where chips are reported or said to be, diamonds for plans, tenders and contracts; filled marks are on the record, open marks rest on unnamed people. '
           'Under the map, each number is given with the place or places its source names, the source and the date. '
           'The map shows places that reports name, not where chips are.</desc>']
    out.append(f'<defs><clipPath id="frame"><rect x="0" y="0" width="{W}" height="{H}" rx="8"/></clipPath>')
    out.append('<g id="g-land">' + ''.join(f'<path id="{f["id"]}" d="{f["d"]}"/>' for f in land) + '</g>')
    out.append('<g id="g-main">' + ''.join(f'<path id="{f["id"]}" d="{f["d"]}"/>' for f in main) + '</g></defs>')
    out.append('<g clip-path="url(#frame)">')
    out.append('<use href="#g-land" class="casing"/><use href="#g-main" class="casing"/><use href="#g-land" class="land"/><use href="#g-main" class="main"/>')
    out.append('<g class="tint">' + ''.join(f'<use href="#{f["id"]}"/>' for f in tinted) + '</g>')
    out.append(f'<path class="edge" d="{dpath(edges, close=False)}"/>')
    out.append('</g>')
    for words, lon, lat, anchor in CTX:
        x, y = to(*project(lon, lat))
        out.append(f'<text class="ctx" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{esc(words)}</text>')
    nx, ny = W - 16, to(*project(*NOTE_AT))[1]         # said on the map itself, in open sea, so that it travels with any copy of the map
    for i, words in enumerate(('Places named in', 'reports and records,', 'not where chips are')):          # three short lines: clear of Taiwan
        out.append(f'<text class="mapnote" x="{nx:.1f}" y="{ny + 15 * i:.1f}" text-anchor="end">{words}</text>')
    marks = []
    for r in recs:
        r['xy'] = []
        for i, (tok, km) in enumerate(r['anch']):
            x, y = to(*km)
            dx, dy = (float(v) for v in r['M'][i].split()) if i < len(r['M']) else (0.0, 0.0)
            assert R + 2 < x + dx < W - R - 2 and R + 2 < y + dy < H - R - 2, (r['n'], tok, x, y)
            r['xy'].append((x, y)); marks.append((r, x + dx, y + dy))
    for i, (ra, xa, ya) in enumerate(marks):
        for rb, xb, yb in marks[i + 1:]:
            assert math.hypot(xa - xb, ya - yb) >= 2 * R + 3, f"marks {ra['n']} and {rb['n']} cover each other; add an M line"
    def shape(cls, x, y, plan, grow=0.0):
        if plan:
            h = 8.6 + grow
            return f'<rect class="{cls}" x="{x - h:.1f}" y="{y - h:.1f}" width="{2 * h:.1f}" height="{2 * h:.1f}" rx="2" transform="rotate(45 {x:.1f} {y:.1f})"/>'
        return f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{R + grow:.1f}"/>'
    out.append('<g class="halos">' + ''.join(shape('halo', x, y, r['status'] == 'plan', 2.6) for r, x, y in marks) + '</g>')
    for r, x, y in marks:
        out.append(f'<a href="#e{r["n"]}" class="pin {r["dir"]} {"solid" if r["solid"] else "hollow"}" data-n="{r["n"]}" data-tip="1" aria-label="{r["n"]}. {esc(r["P"], quote=True)}: {esc(r["T"], quote=True)}">'
                   + shape('m', x, y, r['status'] == 'plan') + f'<text x="{x:.1f}" y="{y + 4:.1f}">{r["n"]}</text></a>')
    for r in recs:
        for spec in r['L']:
            i, anchor, dx, dy, words = spec.split(' ', 4)
            x, y = r['xy'][int(i) - 1]
            out.append(f'<text class="plab" x="{x + float(dx):.1f}" y="{y + float(dy):.1f}" text-anchor="{anchor}">{esc(words)}</text>')
    out.append('</svg>')
    stats = dict(features=len(land) + len(main), mainland=len(main), tinted=len(tinted), points=npts, borders=nborder, height=H,
                 km_per_px=round(1 / sc, 2), marks=len(marks))
    return '\n'.join(out), stats


# ---------- the page ----------
def pin(r, tip=False):
    cls = f'p {r["dir"]} {"solid" if r["solid"] else "hollow"}{" plan" if r["status"] == "plan" else ""}'
    return f'<a href="#e{r["n"]}" class="{cls}" data-n="{r["n"]}"{" data-tip=1" if tip else ""} aria-label="record {r["n"]}"><span>{r["n"]}</span></a>'


def listing(recs):
    def block(g):
        out = [f'<h3>{esc(GROUPS[g])}</h3><ol>']
        for r in [r for r in recs if r['group'] == g]:
            src = f'<a href="{esc(r["url"], quote=True)}">{esc(r["S"])}</a>' if r['url'] else esc(r['S'])
            out.append(f'<li id="e{r["n"]}" class="ev {r["dir"]}" data-n="{r["n"]}">{pin(r)}<div><span class="place">{esc(r["P"])}</span> <span class="when">{esc(r["W"])}</span>'
                       f'<span class="what">{esc(r["T"])}</span><span class="src">{src}</span></div></li>')
        out.append('</ol>')
        return '\n'.join(out)
    return '<section class="lcol">' + block('out') + block('there') + '</section>\n<section class="lcol">' + block('plan') + '</section>'


def main():
    recs, extra, dates = load()
    bad = verify(recs, extra, dates)
    if bad:
        print('\n'.join(bad)); sys.exit(f'{len(bad)} quotations or blocks failed; nothing written')
    nq = 0
    with open(F / 'quotes.tsv', 'w', encoding='utf-8') as fh:
        fh.write('# saved id <TAB> the source\'s exact words. Written by build.py from places.txt. A line that spans an invisible character\n'
                 '# in the saved copy is written here in pieces; build.py has checked each whole line with those characters removed.\n')
        for r in recs:
            fh.write(f'# record {r["n"]}: {r["P"]}\n')
            for sid, q in [(r['sid'], r['Q'])] + r['plus']:
                for p in pieces(q, sid): fh.write(f'{sid}\t{p}\n'); nq += 1
        fh.write('# words behind the notes under the map\n')
        for sid, q in extra:
            for p in pieces(q, sid): fh.write(f'{sid}\t{p}\n'); nq += 1
        fh.write('# where each date shown was read\n')
        for sid, q in dates:
            for p in pieces(q, sid): fh.write(f'{sid}\t{p}\n'); nq += 1
    run = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts' / 'cn_has.py'), str(F / 'quotes.tsv')], capture_output=True, text=True)
    print('cn_has.py:', (run.stdout.strip().splitlines() or ['(no output)'])[-1])
    if run.returncode != 0:
        print(run.stdout, run.stderr); sys.exit('cn_has.py failed on quotes.tsv; nothing written')

    for r in recs:
        r['solid'] = r['kind'] != 'press'; r['url'] = r['U'] or L.url_of(r['sid'])
    n = lambda f: sum(1 for r in recs if f(r))
    c = dict(rec=len(recs), src=len({r['sid'] for r in recs}), out=n(lambda r: r['group'] == 'out'), plan=n(lambda r: r['group'] == 'plan'),
             there=n(lambda r: r['group'] == 'there'), there_solid=n(lambda r: r['group'] == 'there' and r['solid']),
             there_open=n(lambda r: r['group'] == 'there' and not r['solid']), away=n(lambda r: r['dir'] == 'away'), toward=n(lambda r: r['dir'] == 'toward'),
             circle=n(lambda r: r['status'] == 'there'), diamond=n(lambda r: r['status'] == 'plan'), solid=n(lambda r: r['solid']), hollow=n(lambda r: not r['solid']))
    # what the template's own sentences rest on
    assert (c['out'] + c['plan']) * 2 > c['rec'], 'the headline says "most": it no longer holds'
    c.update(out_press=n(lambda r: r['group'] == 'out' and r['status'] == 'there'), out_paper=n(lambda r: r['group'] == 'out' and r['status'] == 'plan'),
             us=n(lambda r: r['dir'] == 'us'), paper=n(lambda r: r['kind'] == 'paper'))
    assert c['there'] == 1 and c['away'] == 1 and c['us'] == 1 and min(c['out_press'], c['out_paper'], c['plan'], c['toward'], c['paper']) > 1, 'the deck and key are worded for these counts'
    assert [(r['P'], r['kind']) for r in recs if r['group'] == 'there'] == [('Jiangsu', 'doc')], 'the deck describes this one record'
    assert all(r['status'] == 'plan' for r in recs if r['group'] == 'plan') and all(r['status'] == 'there' for r in recs if r['group'] == 'there')
    assert {r['P'] for r in recs if r['group'] == 'out' and r['status'] == 'there'} == {'Hong Kong', 'Southeast Asia', 'Japan, outside Osaka'} and all(r['kind'] == 'press' for r in recs if r['group'] == 'out' and r['status'] == 'there'), 'the deck names these three press reports'
    assert [r['sid'] for r in recs if r['kind'] == 'paper'] == ['cn-tolerate-datasectionfiling', 'cn-usdocs-hfac-decisions-20261119'] == [r['sid'] for r in recs if r['group'] == 'out' and r['status'] == 'plan'], 'the deck and a note name these two documents'
    assert [r['sid'] for r in recs if r['dir'] == 'us'] == ['cn-usdocs-hfac-decisions-20261119'], 'grey is the licence table only'
    # the licence applications abroad: counted from the project's table of the Commerce Department's 54 rows (read only), never typed
    lic = [l.split('\t') for l in (ROOT / 'research/cn_chip_policy_20261120/tables/house_licence_table.tsv').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    lic = [dict(zip(lic[0], x)) for x in lic[1:]]; abroad = [x for x in lic if x['location'] != 'China']
    n_ab, sum_ab = len(abroad), sum(int(x['chip_count'].replace(',', '')) for x in abroad)
    assert len(lic) == 54 and all(x['status'] == 'RWA' and x['exporter'] == 'Nvidia' for x in abroad) and {x['location'] for x in abroad} == {'Malaysia', 'Indonesia', 'Thailand'}, 'the table no longer says what record 5 says'
    assert all(re.search(r'bytedance|byteplus|tiktok|alibaba', x['consignee'], re.I) for x in abroad)
    r5 = next(r for r in recs if r['dir'] == 'us')
    assert [r['n'] for r in recs if 'A' in r] == [r5['n']], 'the BIS record alone must give an expected licence subtotal'
    assert (n_ab, sum_ab) == r5['A'], f'BIS record expects {r5["A"]}, but the table gives {(n_ab, sum_ab)}'
    assert r5['T'].count('%%BIS_APPS%%') == 2 and r5['T'].count('%%BIS_CHIPS%%') == 1, 'the BIS record must print its computed counts'
    r5['T'] = r5['T'].replace('%%BIS_APPS%%', WORDS[n_ab]).replace('%%BIS_CHIPS%%', f'{sum_ab:,}')
    assert f'{sum_ab:,}' in r5['T'] and f' {WORDS[n_ab]} applications' in r5['T'] and f'All {WORDS[n_ab]} ' in r5['T'] and r5['P'] == 'Malaysia, Indonesia and Thailand', (n_ab, sum_ab)
    assert all(r['group'] == 'out' and not r['solid'] for r in recs if r['dir'] == 'away'), "the key describes the orange record as Reuters's report, by unnamed people, of chips stored in Hong Kong"
    # round 10 (Nov 25, 2026): the headline, deck and key name outlets, dates and record numbers; each is checked here against the records
    press_out = [(r['sid'], r['date'].isoformat(), r['S'].split(',')[0]) for r in recs if r['group'] == 'out' and r['status'] == 'there']
    assert press_out == [('cn-clips-evidence-1', '2026-11-05', 'Reuters'), ('cn-tolerate-ft-offshore', '2025-11-27', 'Financial Times'),
                         ('man-cn-ft-202512-japan', '2025-12-20', 'Financial Times')], f'the deck names these three reports, their outlets and dates: {press_out}'
    paper = [r for r in recs if r['kind'] == 'paper']
    assert [(r['date'].isoformat(), r['dir']) for r in paper] == [('2026-05-07', 'toward'), ('2026-05-11', 'us')], 'the deck dates the firm\'s notice and the licence table'
    ds = [r for r in recs if r['kind'] == 'paper' and r['dir'] == 'toward']
    assert len(ds) == 1 and 'does not name the customer' in ds[0]['T'] and '大阪府から千葉県' in ds[0]['Q'], 'the deck and the blue key describe this one notice'
    assert all(r['S'].split(',')[0].split(' ')[0] in ('Reuters', 'Bloomberg') for r in recs if r['group'] == 'plan'), 'the deck says the plans are as Reuters and Bloomberg report them'
    th = next(r for r in recs if r['group'] == 'there')
    assert th['sid'] == 'cn-tolerate-projects-relay1' and th['date'].isoformat() == '2026-11-13' and 'municipal government said in March 2025' in th['Q'], 'the deck names this report, its date and the city government'
    aw = [r for r in recs if r['dir'] == 'away']
    assert [(r['sid'], r['S'].split(',')[0], r['date'].isoformat()) for r in aw] == [('cn-clips-evidence-1', 'Reuters', '2026-11-05')] and 'two people' in aw[0]['Q'], 'the orange key names Reuters, its date and two unnamed people'
    nums = [str(r['n']) for r in paper]
    c.update(out_or_plan=c['out'] + c['plan'], solid_rep=c['solid'] - c['paper'])
    assert max(c.values()) < len(WORDS)
    lo, hi = min(r['date'] for r in recs), max(r['date'] for r in recs)
    svg, st = build_map(recs)
    # round 13 (Nov 26, 2026): the first note says which records have more than one mark and which has one mark for several places
    multi = [r for r in recs if len(r['anch']) > 1]
    for r in multi:
        assert len(re.split(r', | and ', r['P'])) == len(r['anch']) and not any(t == 'centre' for t, _ in r['anch']), f"record {r['n']}: one mark per place it names"
    cen = [r for r in recs if any(t == 'centre' for t, _ in r['anch'])]
    assert len(multi) >= 2 and len(cen) == 1 and len(cen[0]['anch']) == 1 and cen[0]['P'] == 'Southeast Asia' and sorted({f['admin'] for f in cen[0]['areas']}) == ['Malaysia', 'Singapore'] \
        and 'Singapore and Malaysia' in cen[0]['T'], 'the first note names the records with a mark on each place and the one mark for Southeast Asia, Malaysia and Singapore shaded'
    mnums = [str(r['n']) for r in multi]
    tip = {r['n']: dict(p=r['P'], w=r['W'], t=r['T'], q=r['Q'], s=r['S'],
                        k=('The document itself, saved' if r['kind'] == 'paper' else 'On the record, as reported' if r['solid'] else 'Press report, unnamed sources') + ' · ' + ('a plan, tender or application, not a delivery' if r['status'] == 'plan' else 'chips reported or said to be here'))
           for r in recs}
    page = (F / 'template.html').read_text(encoding='utf-8')
    parts = {'MAP': svg, 'LIST': listing(recs), 'EVJSON': json.dumps(tip, ensure_ascii=False).replace('</', '<\\/'),
             'SPAN': f'{MON[lo.month - 1]} {lo.year} to {MON[hi.month - 1]} {hi.year}',
             'N_REC': WORDS[c['rec']].capitalize(), 'N_SRC': WORDS[c['src']], 'N_OUT_PRESS': WORDS[c['out_press']].capitalize(), 'N_OUT_PAPER': WORDS[c['out_paper']].capitalize(),
             'N_PLAN': WORDS[c['plan']].capitalize(), 'N_THERE': WORDS[c['there']].capitalize(), 'N_US': str(c['us']), 'N_PAPER': WORDS[c['paper']], 'N_PAPER_CAP': WORDS[c['paper']].capitalize(),
             'N_AWAY': str(c['away']), 'N_TOWARD': str(c['toward']), 'N_CIRCLE': str(c['circle']), 'N_DIAMOND': str(c['diamond']),
             'N_SOLID': str(c['solid']), 'N_HOLLOW': str(c['hollow']),
             'MAPSRC': '\n'.join(f'    <li>{pin(r)}<span><b>{esc(r["P"])}</b>, {esc(r["K"])}</span></li>' for r in recs),
             'N_OUT_OR_PLAN': WORDS[c['out_or_plan']], 'N_SOLID_REP': WORDS[c['solid_rep']], 'REC_DS': str(ds[0]['n']),
             'PAPER_NUMS': ', '.join(nums[:-1]) + ' and ' + nums[-1],
             'MULTI_NUMS': ', '.join(mnums[:-1]) + ' and ' + mnums[-1], 'CENTRE_NUM': str(cen[0]['n'])}
    for k, v in sorted(parts.items(), key=lambda kv: -len(kv[0])):          # longer names first: N_PAPER_CAP before N_PAPER
        assert f'%%{k}%%' in page, k
        page = page.replace(f'%%{k}%%', v)
    assert '%%' not in page, page[page.index('%%'):][:40]
    segs, loose = page_quotes(page, recs, extra)
    if loose:
        print('\n'.join(loose)); sys.exit(f'{len(loose)} quoted passages on the page are not part of a checked line; nothing written')
    (F / f'{OUT}.html').write_text(page, encoding='utf-8')
    with open(F / 'places_drawn.tsv', 'w', encoding='utf-8') as fh:
        fh.write('n\tplace\tshown_as\tgroup\tkind\tmark\tcolour\tsource\taddress\tsaved_id\ttext\n')
        for r in recs:
            fh.write(f"{r['n']}\t{r['P']}\t{r['W']}\t{r['group']}\t{r['kind']}\t{'diamond' if r['status'] == 'plan' else 'circle'}, {'filled' if r['solid'] else 'open'}\t"
                     f"{dict(away='orange', toward='blue', us='grey')[r['dir']]}\t{r['S']}\t{r['url'] or ''}\t{r['sid']}\t{r['T']}\n")
    print(f'records {c["rec"]} from {c["src"]} saved sources: outside the mainland {c["out"]} (press reports {c["out_press"]}, on paper {c["out_paper"]}), on the mainland {c["there"]}, plans {c["plan"]}; orange {c["away"]}, blue {c["toward"]}, grey {c["us"]}; licence applications abroad {n_ab} ({sum_ab:,} chips, all RWA); '
          f'filled {c["solid"]}, open {c["hollow"]}; circles {c["circle"]}, diamonds {c["diamond"]}')
    print(f'lines checked {sum(1 + len(r["plus"]) for r in recs) + len(extra) + len(dates)}, all found (written to quotes.tsv as {nq} pieces); control not found (as it must be)')
    print(f'quoted passages in the page text {len(segs)}, all part of a checked line; control fails (as it must)')
    print('map:', st)
    print('no address to link:', [r['sid'] for r in recs if not r['url']] or 'none')
    print('written', F / f'{OUT}.html', len(page.encode('utf-8')), 'bytes')
    if '--png' in sys.argv:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            br = p.chromium.launch()
            pg = br.new_context(viewport={'width': 1500, 'height': 1000}, device_scale_factor=2, color_scheme='light').new_page()
            pg.goto((F / f'{OUT}.html').as_uri()); pg.evaluate('document.fonts.ready.then(() => 1)'); pg.wait_for_timeout(700)
            for sel, name in (('#figure', f'{OUT}_full.png'), ('#mapcard', f'{OUT}_map.png')):
                pg.locator(sel).screenshot(path=str(F / name)); print('image', F / name)
            br.close()


main()
