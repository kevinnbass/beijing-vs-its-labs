#!/usr/bin/env python3
"""Idea 15: six sentences. A wall of six short quotations: three show Beijing pulling away from Nvidia, three show
the companies pulling toward it. Each has its speaker or body, date, source and a filled or open mark for its tier.
One line beneath gives the limit.

Run: python3 -I build.py                                   checks quotes.tsv with scripts/cn_has.py, writes six_sentences.html
     python3 build.py --png     the same, then writes six_sentences.png (the wall alone, twice size)
Reads quotes.tsv and sentences.tsv (this folder) and ../a4lib.py (shared helpers).
Nothing is written unless cn_has.py exits 0 and the guard finds every quotation and number on the page in quotes.tsv.
Chinese words stand between quotation marks exactly as the page has them; our English is in round brackets, without marks.
Before the page or image is called done or shown: scripts/render_and_look.py on six_sentences.html and six_sentences.png.
Round 5 (Nov 24, 2026, core edit 6): the state-media sentence under the limit gives the warnings as the project's table now
counts them (a4lib.warnings(): those of the first year and the later ones), with the table's own caution on the later rows.
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import a4lib as A   # noqa: E402

esc, qm, fmt = A.esc, A.qm, A.fmt
SIDE = {'away': 'Beijing pulls away from Nvidia', 'toward': 'The companies pull toward it'}
NUMW = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'}

CSS = '''
#fig { background: var(--page); }
header { margin-bottom: 20px; }
.wall { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: auto repeat(3, auto); grid-auto-flow: column; gap: 14px 18px; }
.colh { display: flex; align-items: center; gap: 9px; margin: 0; font: 700 13px/1.2 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink); }
.qc { background: var(--surface); border: 1px solid var(--border); border-left: 4px solid var(--axis); border-radius: 12px; padding: 20px 22px 16px; display: flex; flex-direction: column; min-width: 0; }
.qc.away { border-left-color: var(--away); } .qc.toward { border-left-color: var(--toward); }
.qc .q { font: 600 21.5px/1.32 var(--font-text); letter-spacing: -0.006em; margin: 0; text-wrap: pretty; }
.qc .q.zh { font-family: "Noto Sans CJK SC", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", var(--font-text); font-weight: 700; font-size: 22px; line-height: 1.45; letter-spacing: 0.01em; text-indent: -0.42em; }
.qc .en { font-size: 15.5px; line-height: 1.42; color: var(--ink2); margin: 8px 0 0; }
.at { margin-top: auto; padding-top: 16px; display: grid; grid-template-columns: 14px minmax(0, 1fr); gap: 2px 10px; font-size: 13.5px; line-height: 1.42; color: var(--ink2); }
.at i.mk { margin-top: 3px; }
.at b { color: var(--ink); font-weight: 600; }
.at .kind { grid-column: 2; font-size: 12.5px; color: var(--muted); }
.limit { margin-top: 16px; background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 18px 22px; display: grid; grid-template-columns: 150px minmax(0, 1fr); gap: 6px 22px; align-items: start; }
.limit h2 { margin: 3px 0 0; font: 700 13px/1.2 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; }
.limit .q { font: 600 20px/1.32 var(--font-text); margin: 0; }
.limit .at { padding-top: 10px; }
.limit .more { margin: 10px 0 0; font-size: 14.5px; color: var(--ink2); max-width: 88ch; }
.foot { margin: 14px 2px 0; font-size: 13px; color: var(--ink2); }
.imgnote { margin-top: 6px; }
@media (max-width: 800px) {
  .wall { grid-template-columns: minmax(0, 1fr); grid-template-rows: none; grid-auto-flow: row; }
  .colh.toward { margin-top: 12px; } .qc .q { font-size: 19px; } .qc .q.zh { font-size: 19.5px; }
  .limit { grid-template-columns: minmax(0, 1fr); }
}
'''


def load(Q):
    lines = [ln for ln in (HERE / 'sentences.tsv').read_text(encoding='utf-8').splitlines() if ln.strip() and not ln.startswith('#')]
    hdr, rows = lines[0].split('\t'), []
    for ln in lines[1:]:
        r = dict(zip(hdr, (ln.split('\t') + [''] * len(hdr))[:len(hdr)]))
        assert r['side'] in SIDE and r['tier'] in ('solid', 'open'), r
        r['words'] = Q[r['key']]; r['date'] = A.day(Q, r['key']); r['zh'] = bool(re.search(r'[一-鿿]', r['words']))
        r['pub'] = A.day(Q, r['key'] + '.pub') if '{pub}' in r['when'] else None
        if r['zh'] != bool(r['ours']): sys.exit(f"{r['key']}: Chinese words need our English, and only Chinese words do")
        rows.append(r)
    for side in SIDE: assert sum(r['side'] == side for r in rows) == 3, 'three sentences a side'
    return rows


def attribution(r, date_text):
    kind = A.ref(r['words'].sid)
    assert (kind['tier'] == 'solid') == (r['tier'] == 'solid'), f"{r['key']}: the tier differs from the argument's reference list ({kind['kind']})"
    when = r['when'].replace('{date}', date_text).replace('{pub}', fmt(r['pub']) if r['pub'] else '')
    assert '{' not in when, when
    return (f'<p class="at"><i class="mk {r["tier"]} {r["side"]}" title="{"on the record" if r["tier"] == "solid" else "press report citing unnamed people"}"></i>'
            f'<span><b>{esc(r["who"])}</b>, {A.link(r["words"].sid, when)}</span><span class="kind">{esc(r["kind"])}.{" " + esc(r["note"]) if r["note"] else ""}</span></p>')


def cardhtml(r):
    q = f'<p class="q zh" lang="zh-Hans">{qm(r["words"])}</p><p class="en">({esc(r["ours"])})</p>' if r['zh'] else f'<p class="q">{qm(r["words"])}</p>'
    return f'<article class="qc {r["side"]}">{q}{attribution(r, fmt(r["date"]))}</article>'


def main():
    qfile = HERE / 'quotes.tsv'
    A.check(qfile)                                   # stops here if a quotation is not found in its saved copy
    Q = A.quotes(qfile); A.guard_control(Q)
    rows = load(Q)
    n_solid, n_open = sum(r['tier'] == 'solid' for r in rows), sum(r['tier'] == 'open' for r in rows)
    num = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five'}
    d_lim, d_car = A.day(Q, 'limit'), A.day(Q, 'limit.carried')
    W = A.warnings()             # the state-media items that only warn, counted from the project's table
    cols = ''
    for side in ('away', 'toward'):
        cols += f'<h2 class="colh {side}"><i class="sw {side}"></i>{SIDE[side]}</h2>\n' + '\n'.join(cardhtml(r) for r in rows if r['side'] == side) + '\n'
    lim = A.ref(Q['limit'].sid); assert lim['tier'] == 'open'
    page = A.head('Six Sentences', CSS) + f'''<body>
<div class="wrap">
 <p class="draft">{A.NOTE}</p>
 <div id="fig">
  <header>
   <p class="eyebrow">China · Nvidia chips · six sentences from the record</p>
   <h1>Beijing mostly pulled one way on Nvidia chips. Its AI companies pulled the other.</h1>
   <p class="deck">Three sentences show the Chinese state pulling away from Nvidia. Three show China’s AI companies pulling toward it. {num[n_solid]} are on the record; {num[n_open].lower()} are press reports citing unnamed people.</p>
   <ul class="key">
    <li><i class="mk solid"></i><span><b>Filled mark:</b> on the record (a government document, a filing, a named official)</span></li>
    <li><i class="mk open"></i><span><b>Open mark:</b> a press report citing unnamed people</span></li>
   </ul>
  </header>
  <div class="wall">
{cols}  </div>
  <section class="limit">
   <h2>The limit</h2>
   <div><p class="q">{qm(Q["limit"])}</p>
    <p class="at"><i class="mk open" title="press report citing unnamed people"></i><span><b>Bloomberg</b>, {A.link(Q["limit"].sid, f"{fmt(d_lim)}, as carried by The Business Times on {fmt(d_car)}")}</span><span class="kind">A press report citing unnamed people.</span></p>
    <p class="more">By this and later reports the pressure came as unpublished guidance; state media also warned in public. Of the {W["warn"]} state and Party media items found that only warn about Nvidia’s chips, {W["burst"]} are dated {W["span"]}, and {NUMW[W["later"]]} later, all in {W["later_outlet"]}, in {W["later_months"]} (the items after September 2025 are what two rounds of searches found, a sample and not a full count). No published Chinese order against buying Nvidia chips was found in the 82 policy pages read.
     This is one of five limits on the headline. The others: Beijing was not one actor; some purchases were approved and some chips came in; the companies had reasons of their own, and American curbs pushed too; and what Beijing meant by it is read both ways.</p></div>
  </section>
  <p class="foot">Words between quotation marks are the source’s own and were found in its saved copy by a script. English in round brackets is ours, not an official translation.</p>
  {A.IMGNOTE}
 </div>
</div>
</body>
</html>
'''
    # ours: 82 = the project's count of policy pages read (the argument, point 18); the counts of state-media warnings are
    # made from the project's table by a4lib.warnings()
    A.guard(page, Q, ours=['82', W['warn'], W['burst']], dates=[fmt(r['date']) for r in rows] + [fmt(r['pub']) for r in rows if r['pub']] + [fmt(d_lim), fmt(d_car), W['span'], W['later_months']])
    # withdrawn by core edit 6 (atlas/core_edit/APPLIED_6.txt, part 02 and B1): the warnings are not all of Aug 1 to Sept 24, 2025
    for banned in ('four limits', 'spokesperson', 'Beijing pulled one way', 'all dated', 'Aug 1 to', 'none after', 'the seven', ' 42 ', 'not a census', 'found by searches and links',     # the last two: touch-up 6b (Nov 24, 2026), item 21
                   'on the summer of 2025', 'which serve market demand'):     # withdrawn by core edit 8b (Nov 25, 2026): the Journal's "last year"; point 5's English
        assert banned not in page, f'the page still says "{banned}"'
    out = HERE / 'six_sentences.html'
    out.write_text(page, encoding='utf-8'); print('written', out, len(page), 'bytes')
    print(f'sentences: {len(rows)} ({n_solid} on the record, {n_open} press reports); by side: ' + ', '.join(f'{SIDE[s]} {sum(r["side"] == s for r in rows)}' for s in SIDE) + '; plus the limit line (a press report)')
    if '--png' in sys.argv:
        A.png(out, [('#fig', HERE / 'six_sentences.png')], width=1256, height=1000, css=A.FIG_EXPORT, fits=[('.q', '.qc'), ('.en', '.qc'), ('.at', '.qc'), ('.qc', '#fig'), ('.limit', '#fig'), ('.foot', '#fig'), ('.imgnote', '#fig')])


main()
