#!/usr/bin/env python3
"""Idea 21: a one-page brief to print. One sheet: the top of the existing figure, about 200 words, ten references with addresses.

Run: python3 -I build.py                                   checks quotes.tsv with scripts/cn_has.py, writes brief.html
     python3 build.py --pdf     the same, then writes brief_A4.pdf and brief_Letter.pdf (Playwright's
                                                            page.pdf) and a picture of each sheet (pdftoppm): brief_A4.png, brief_Letter.png
Reads brief.txt (the text and the references), quotes.tsv (this folder), ../a4lib.py, and shows ../../../figure/beijing_vs_labs_top.png
(the image is not copied: rebuild the PDFs after the figure is rebuilt).
Round 5 (Nov 24, 2026, core edit 6): the state-media warnings as a4lib.warnings() now counts them; a reference line may quote
a title ({q:key}, from the same saved page); the licence table is named by its title and release.
Round 4 (Nov 23, 2026): the core's top image now also holds three panels of numbers and is 1.45 times as tall as wide; whole,
it would print about 105 mm wide with unreadable type. The brief therefore shows that image down to the foot of its first
card: the headline, the key and the dated strip. The cut is found here in the image itself (crop_line), not typed.
Nothing is written unless cn_has.py exits 0, every quotation in the text is cited beside it, and the guard finds every quotation and
number on the page in quotes.tsv. A PDF is refused if the sheet overflows, runs to a second page, or draws the figure too small
or out of proportion.
To look at a PDF: scripts/render_and_look.py on its PNG. Before the page is called done: render_and_look.py on brief.html too.
Round 12 (Nov 26, 2026, outputs/ROUND12.md): the Hong Kong sentence says "Reuters reported that ..." in itself; limit (2) gives the
months the state-media items were found in ({sm:found}, from a4lib.warnings()). Built after the main figure's final export of
round 14 (atlas/core_edit/hand_out/R14_MAINFIG_FINAL.txt); the build line prints the image's sha256.
"""
import hashlib, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import a4lib as A   # noqa: E402

esc, qm, fmt = A.esc, A.qm, A.fmt
FIG = '../../../figure/beijing_vs_labs_top.png'
HEADLINE = 'Beijing mostly pulled one way on Nvidia chips. Its AI companies pulled the other.'     # the core figure's, checked in its template
MONTH = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
NUMW = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'}
PAPER = {'A4': ('210mm', '297mm', 'a4', 210.0), 'Letter': ('215.9mm', '279.4mm', 'letter', 215.9)}
MIN_FIG_MM = {'A4': 170, 'Letter': 160}             # under these widths the build stops: the strip's own type gets too small to read

CSS = '''
:root { --pw: 210mm; --ph: 297mm; }
:root[data-paper="letter"] { --pw: 215.9mm; --ph: 279.4mm; }
@page { margin: 0; }
.sheet { width: var(--pw); height: var(--ph); margin: 18px auto; padding: 8mm 10mm 7mm; background: var(--page); color: var(--ink);
  box-shadow: 0 0 0 1px var(--border), 0 10px 34px rgba(11,11,11,0.08); display: flex; flex-direction: column; overflow: hidden; font-size: 8.5pt; line-height: 1.38; }
.top { display: flex; justify-content: space-between; gap: 6mm; margin: 0 0 2.2mm; font-size: 6.2pt; line-height: 1.3; color: var(--muted); }
/* the figure: the top image, shown down to the foot of its first card. The box takes the room the text leaves. */
.figbox { flex: 1 1 0; min-height: 0; container-type: size; display: flex; justify-content: center; align-items: flex-start; }
.figbox img { display: block; flex: none; width: min(100cqw, calc(100cqh * var(--ar))); height: auto; object-fit: cover; object-position: top center; }
.words { margin-top: 3.2mm; }
.words h1 { font: 700 11.6pt/1.16 var(--font-head); letter-spacing: -0.01em; margin: 0 0 2mm; max-width: none; text-wrap: wrap; }
.words h1 span { color: var(--ink2); font-weight: 600; }
.cols { column-count: 3; column-gap: 5mm; }
.cols p { margin: 0 0 1.4mm; }
.cols p:last-child { margin-bottom: 0; }
.lab { font: 700 6.7pt/1.2 var(--font-text); letter-spacing: 0.07em; text-transform: uppercase; color: var(--ink); margin-right: 0.5mm; }
a.c, span.c { display: inline-grid; place-items: center; width: 9.4pt; height: 9.4pt; border-radius: 50%; font: 700 6pt/1 var(--font-text); text-decoration: none;
  vertical-align: 0.5pt; border: 0.9pt solid var(--ink2); color: var(--ink); margin-left: 0.5pt; font-variant-numeric: tabular-nums; }
.nw { white-space: nowrap; }
.c.solid { background: var(--ink2); color: #ffffff; } .c.open { background: var(--surface); }
.refs { margin-top: 2.8mm; border-top: 0.25mm solid var(--axis); padding-top: 2mm; }
.refs h2 { font: 700 6.7pt/1.2 var(--font-text); letter-spacing: 0.07em; text-transform: uppercase; color: var(--ink); margin: 0 0 1.4mm; }
.refs ol { list-style: none; margin: 0; padding: 0; column-count: 2; column-gap: 6mm; font-size: 6.9pt; line-height: 1.34; color: var(--ink2); }
.refs li { display: grid; grid-template-columns: 9.4pt minmax(0, 1fr); gap: 1.5mm; break-inside: avoid; padding-bottom: 1.05mm; }
.refs li span.c { margin: 0.2pt 0 0; }
.refs .u { overflow-wrap: anywhere; color: var(--link); text-decoration: none; }
.keyline { margin: 0.7mm 0 0; font-size: 6.7pt; line-height: 1.34; color: var(--muted); }
.keyline .c { width: 6.8pt; height: 6.8pt; vertical-align: -0.6pt; margin: 0 1pt 0 0; }
@media screen and (min-width: 1180px) { .sheet { zoom: 1.4; } }
@media screen and (max-width: 860px) {
  .sheet { width: auto; height: auto; margin: 0; padding: 20px 16px 30px; box-shadow: none; overflow: visible; font-size: 15px; line-height: 1.5; }
  .top { display: block; font-size: 12.5px; margin-bottom: 12px; } .top span { display: block; }
  .figbox { display: block; flex: none; container-type: normal; } .figbox img { width: 100%; }
  .words { margin-top: 18px; } .words h1 { font-size: 22px; margin-bottom: 12px; } .cols { column-count: 1; } .cols p { margin-bottom: 12px; }
  .lab, .refs h2 { font-size: 12px; } .refs h2 { margin-bottom: 6px; } a.c, span.c { width: 17px; height: 17px; font-size: 10px; border-width: 1.5px; vertical-align: 1px; }
  .refs { margin-top: 18px; padding-top: 12px; } .refs ol { column-count: 1; font-size: 13px; line-height: 1.45; } .refs li { grid-template-columns: 17px minmax(0, 1fr); gap: 8px; padding-bottom: 8px; }
  .keyline { font-size: 12.5px; margin-top: 6px; } .keyline .c { width: 12px; height: 12px; }
}
@media print { .sheet { margin: 0; box-shadow: none; } }
'''


def crop_line(png):
    """Where the figure's first card (the dated strip) ends in the top image: the brief shows the image down to there.
    A row is classed by how much of it differs from the page colour: a card's rows nearly all do (the card's surface is
    not the page's colour), a gap's rows not at all, the header's rows only where there is type."""
    from PIL import Image
    with Image.open(png) as im:
        im = im.convert('RGB'); W, H = im.size; px = im.load(); page = px[W - 3, 3]
        xs = range(0, W, 4)
        frac = lambda y: sum(max(abs(px[x, y][i] - page[i]) for i in range(3)) > 1 for x in xs) / len(xs)
        y = 0
        while y < H and frac(y) <= 0.9: y += 1          # the header; then the first card begins
        top = y
        while y < H and frac(y) > 0.9: y += 1            # the first card's rows
        end = y
        while y < H and frac(y) < 0.005: y += 1          # the gap under it
        gap = y - end
    if not (0.05 * H < top < end < H and end - top > 0.15 * H and gap >= 16 and y < H):
        sys.exit(f'the top image is not laid out as expected (header to {top}, first card to {end}, gap {gap}, height {H}): no brief written')
    return W, H, end + min(8, gap // 2)


def load():
    title = answer = None; paras, refs = [], {}
    for n, ln in enumerate((HERE / 'brief.txt').read_text(encoding='utf-8').splitlines(), 1):
        if not ln.strip() or ln.startswith('#'): continue
        if ln.startswith('@title '): title = ln[7:].strip()
        elif ln.startswith('@answer '): answer = ln[8:].strip()
        elif ln.startswith('@p '): lab, text = ln[3:].split(' | ', 1); paras.append((lab.strip(), text.strip()))
        elif ln.startswith('= '): key, lab = ln[2:].split(' | ', 1); refs[key.strip()] = lab.strip()
        else: sys.exit(f'brief.txt line {n} not understood: {ln[:60]}')
    return title, answer, paras, refs


def main():
    qfile = HERE / 'quotes.tsv'
    A.check(qfile)                                   # stops here if a quotation is not found in its saved copy
    Q = A.quotes(qfile); A.guard_control(Q)
    title, answer, paras, refdef = load()
    Hs, Wm = A.house(Q), A.warnings()                # Washington's table, summed; the state-media items that only warn, counted
    order, dates, ours = [], [], []
    for _, text in paras:
        cited = re.findall(r'\[([a-z]+)\]', text)
        for k in cited:
            if k not in refdef: sys.exit(f'[{k}] is cited but has no reference line in brief.txt')
            if k not in order: order.append(k)
        for k in re.findall(r'\{q:([a-z]+)\}', text):
            if Q[k].sid not in {Q[c].sid for c in cited}: sys.exit(f'the quotation {k} is not cited in its own paragraph')
    if set(order) != set(refdef): sys.exit(f'references never cited: {sorted(set(refdef) - set(order))}')
    if len(order) != 10: sys.exit(f'the brief has ten references; brief.txt cites {len(order)}')
    if 'five limits' not in answer or sum(f'({i})' in paras[-1][1] for i in range(1, 6)) != 5: sys.exit('the brief gives five limits, numbered 1 to 5')
    num = {k: i for i, k in enumerate(order, 1)}
    tier = {k: A.ref(Q[k].sid)['tier'] for k in order}

    def fill(text):
        def one(m):
            kind, k = m.group(1), m.group(2)
            if kind == 'q': return qm(Q[k])
            if kind == 'h': ours.append(Hs[k]); return str(Hs[k])
            if kind == 'sm':
                if k in ('span', 'found'): dates.append(Wm[k]); return Wm[k]          # round 12: found = the months the items were found in
                if Wm[k] not in NUMW: ours.append(Wm[k])
                return NUMW.get(Wm[k], str(Wm[k]))
            if kind == 't':
                t = A.caption_time(Q[k].sid, Q[k]); ours.extend(t.split(':')); return t
            if kind == 'my':                         # a month and year: in the page's own words where it gives no day, else from its date
                mm = re.search(r'\b(' + '|'.join(MONTH) + r') (20\d\d)\b', Q[k + '.date'])
                if mm and A.parse_date(Q[k + '.date']) is None: dates.append(mm.group(0)); return mm.group(0)
            d = A.day(Q, k)
            if kind == 'd': dates.append(fmt(d)); return fmt(d)
            if kind == 'my': dates.append(f'{MONTH[d.month - 1]} {d.year}'); return f'{MONTH[d.month - 1]} {d.year}'
            if kind == 'y': return str(d.year)
            if kind == 'n':
                mm = re.match(r'(About|More than|Fewer than) ([\d,]+)', Q[k])
                if not mm: sys.exit(f'{k}: no number phrase at the start of its line')
                return f'{mm.group(1).lower()} {mm.group(2)}'
            sys.exit(f'unknown mark {m.group(0)}')
        t = re.sub(r'\{(q|d|my|y|n|h|sm|t):([a-z]+)\}', one, esc(text, quote=False))
        if '{' in t: sys.exit(f'an unfilled mark in the text: {t[t.index("{"):][:30]}')
        # the mark stays on the line of the word it follows
        return re.sub(r'(\S+)\s*\[([a-z]+)\]', lambda m: f'<span class="nw">{m.group(1)}<a class="c {tier[m.group(2)]}" href="#r{num[m.group(2)]}" aria-label="reference {num[m.group(2)]}">{num[m.group(2)]}</a></span>', t)

    cols = '\n'.join(f'<p><b class="lab">{esc(lab)}</b> {fill(text)}</p>' for lab, text in paras)
    lis = []
    for k in order:
        r = A.ref(Q[k].sid); label = refdef[k]
        if not r['addr']: sys.exit(f'{k}: no address for {Q[k].sid}')
        if '{date}' in label: d = fmt(A.day(Q, k)); dates.append(d); label = label.replace('{date}', d)
        if '{pub}' in label: d = fmt(A.day(Q, k + '.pub')); dates.append(d); label = label.replace('{pub}', d)
        if '{month}' in label:
            mm = re.search(r'(?i)\b(' + '|'.join(MONTH) + r') (20\d\d)\b', Q[k + '.month'])
            if not mm: sys.exit(f'{k}.month holds no month and year')
            d = f'{mm.group(1).capitalize()} {mm.group(2)}'; dates.append(d); label = label.replace('{month}', d)
        if '{posted}' in label: d = fmt(A.posted(Q[k + '.title'].sid)); dates.append(d); label = label.replace('{posted}', d)
        for qk in re.findall(r'\{q:([a-z.]+)\}', label):           # a title in the source's own words, from quotes.tsv (same saved id)
            if Q[qk].sid != Q[k].sid: sys.exit(f'{k}: the quoted words {qk} are not from the reference\'s own saved page')
            label = label.replace('{q:' + qk + '}', '“' + A.curly(str(Q[qk])) + '”')
        if '{' in label: sys.exit(f'{k}: an unfilled mark in its reference line')
        lis.append(f'<li id="r{num[k]}"><span class="c {tier[k]}">{num[k]}</span><span>{esc(label)} '
                   f'<a class="u" href="{esc(r["addr"], quote=True)}">{esc(r["addr"])}</a></span></li>')
    n_solid = sum(t == 'solid' for t in tier.values())
    figfile = (HERE / FIG).resolve()
    if HEADLINE not in (A.PROJ / 'figure' / 'template.html').read_text(encoding='utf-8'): sys.exit('the core figure no longer carries the headline this brief expects')
    W, H, C = crop_line(figfile)
    page = A.head('One-Page Brief', CSS, theme='light') + f'''<body>
<main class="sheet">
 <p class="top"><span>{A.CREDIT}</span><span>A brief to print. Figure: the head and dated strip of beijing_vs_labs.html. Full argument: ARGUMENT_referenced.html.</span></p>
 <div class="figbox"><img src="{FIG}" style="--ar:{W / C:.5f}; aspect-ratio:{W} / {C}" alt="The top of the figure. Its headline: {HEADLINE} Under it, the key and the dated record in four rows."></div>
 <section class="words">
  <h1><span>{esc(title)}</span> {esc(answer)}</h1>
  <div class="cols">
{cols}
  </div>
 </section>
 <section class="refs">
  <h2>References</h2>
  <ol>
{chr(10).join(lis)}
  </ol>
  <p class="keyline"><span class="c solid"></span>Filled number: on the record (a document, a filing, a named person). <span class="c open"></span>Open number: a press report citing unnamed people, or captions not checked by ear.
   Quoted words are the sources’ own, found in the saved copies by a script. English for Chinese sources is ours, not official.</p>
 </section>
</main>
</body>
</html>
'''
    # ours: the reference numbers 1 to 10 (1 to 5 also number the limits); 82 = the project's count of policy pages read
    # (the argument, point 18); and what fill() made: the share of Washington's table, the caption's time
    A.guard(page, Q, ours=[*range(1, 11), '82', *ours], dates=dates)
    # withdrawn by core edit 6 (atlas/core_edit/APPLIED_6.txt): the warnings are not all of Aug 1 to Sept 24, 2025; the table is not the Commerce Department's
    for banned in ('four limits', 'spokesperson', '750,000', 'Democrats', 'more than half', 'all date from', 'Aug 1 to', 'Commerce Department’s table', 'US Commerce Department, table',
                   # withdrawn by core edit 8b (Nov 25, 2026): the planner's 加大力度; the Shanghai clusters in the city; the readout's own date
                   'models to adapt to', 'the city’s internet companies run', 'meeting with Nvidia’s chief executive, Jul',
                   # round 10c (the session's ruling): the sheets are PDFs no release script rewrites; they carry the credit only
                   'not published', 'Local;',
                   # round 12: the Hong Kong sentence names its report; limit (2) gives its period
                   '. In November 2026, about', 'items found that only warn'):
        if banned in page: sys.exit(f'the page still says "{banned}"')
    words = re.sub(r'<a class="c[^>]*>\d+</a>', ' ', cols)
    words = sum(1 for w in re.sub(r'<[^>]+>', ' ', f'{title} {answer} {words}').split() if re.search(r'\w', w))   # a stray full stop is not a word
    out = HERE / 'brief.html'
    out.write_text(page, encoding='utf-8'); print('written', out, len(page), 'bytes')
    print(f'text: {words} words; references: {len(order)} ({n_solid} on the record, {len(order) - n_solid} press reports or captions); '
          f'figure {figfile.name} sha256 {hashlib.sha256(figfile.read_bytes()).hexdigest()[:16]}, {W} x {H}, shown down to row {C} (the foot of its first card)')
    if '--pdf' in sys.argv: pdfs(out, W / C)


def pdfs(out, ar):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        for name, (w, h, key, wmm) in PAPER.items():
            pg = br.new_context().new_page()
            pg.goto(out.as_uri()); pg.evaluate('p => { document.documentElement.dataset.paper = p; }', key)
            pg.emulate_media(media='print', color_scheme='light'); A._fonts_ok(pg)
            m = pg.evaluate('''() => { const s = document.querySelector('.sheet'), i = document.querySelector('.figbox img'), r = i.getBoundingClientRect(), b = document.querySelector('.figbox').getBoundingClientRect(),
                  k = document.querySelector('.keyline').getBoundingClientRect(), sr = s.getBoundingClientRect();
                return {sh: s.scrollHeight, ch: s.clientHeight, sw: s.scrollWidth, cw: s.clientWidth, iw: r.width, ih: r.height, bh: b.height, bw: b.width, nw: i.naturalWidth, w: sr.width, room: sr.bottom - k.bottom}; }''')
            if not m['nw']: sys.exit('the figure image did not load: no PDF written')
            if m['sh'] > m['ch'] + 1 or m['sw'] > m['cw'] + 1 or m['room'] < 0: sys.exit(f'{name}: the sheet overflows ({m}): no PDF written')
            if abs(m['iw'] / m['ih'] / ar - 1) > 0.01 or m['ih'] > m['bh'] + 0.5 or m['iw'] > m['bw'] + 0.5: sys.exit(f'{name}: the figure is drawn out of proportion or out of its box ({m}): no PDF written')
            k = wmm / m['w']; drawn = m['iw'] * k
            if drawn < MIN_FIG_MM[name]: sys.exit(f'{name}: the figure would be {drawn:.0f} mm wide, under {MIN_FIG_MM[name]}: no PDF written')
            f = HERE / f'brief_{name}.pdf'
            pg.pdf(path=str(f), width=w, height=h, print_background=True, margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
            info = subprocess.run(['pdfinfo', str(f)], capture_output=True, text=True, check=True).stdout
            pages = int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1)); size = re.search(r'^Page size:\s+(.*)$', info, re.M).group(1)
            if pages != 1: sys.exit(f'{name}: the PDF has {pages} pages, not one')
            subprocess.run(['pdftoppm', '-png', '-r', '150', '-singlefile', str(f), str(HERE / f'brief_{name}')], check=True)
            print(f'pdf {f}: 1 page, {size}; figure drawn {drawn:.0f} mm wide; blank left under the figure {(m["bh"] - m["ih"]) * k:.1f} mm; room left under the last line {m["room"] * k:.1f} mm; picture brief_{name}.png')
        br.close()


main()
