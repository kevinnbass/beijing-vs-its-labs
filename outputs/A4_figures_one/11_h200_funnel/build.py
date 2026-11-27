#!/usr/bin/env python3
"""Idea 11: the H200 funnel alone. Seven bars with their sources and dates, as a page and an image.

Run: python3 -I build.py                                   checks quotes.tsv with scripts/cn_has.py, writes funnel.html
     python3 build.py --png     the same, then writes funnel.png (the figure alone, twice size)
Reads quotes.tsv (this folder), ../h200_funnel.tsv (the seven rows), ../a4lib.py (shared helpers) and, through
a4lib.house(), the project's tables/house_licence_table.tsv (Washington's table of licence applications).
Nothing is written unless cn_has.py exits 0 and the guard finds every quotation and number on the page in quotes.tsv,
in a date read from a page, or among the sums made here.
Round 4 (Nov 23, 2026): the bars follow the core figure's. Five are press reports citing unnamed people; two are sums of
one United States government table (status as of May 11, 2026). The old multiplied ceiling for Washington's step is gone.
The bars are separate counts, not one tally; an application names a data-centre operator or ultimate consignee and is not
an order. Both are said on the figure.
Round 9b (Nov 25, 2026, core edit 8b): the five abroad are those whose ultimate location is outside China; 48.6% also needs
the further application not returned without action; the 75,000 limit is Reuters's, by two people it did not name; the
approval of Jan 28, 2026 is the one Reuters reported; no report here says how many H200 chips entered the mainland.
Round 10 (Nov 25, 2026, core batch 12 and two readers of the public page): the bars are set side by side by what they count,
not as stages of a sale (title, deck, heading); a press row's date is its report's day of publication; the report of
Aug 18, 2026 names two buyers and the Hong Kong report speaks of several; the argument's two later accounts that say
otherwise of the orders (Voice of America's Chinese service, Jan 29, 2026; TechWeb as Sina carries it, Jul 17, 2026).
Round 11 (Nov 26, 2026, outputs/ROUND11.md thing 2): every drawn label of a press report carries the report: the bars'
labels begin "Reported:" (../h200_funnel.tsv), and each press mark of the dated strip reads "reported <date>" under a noun
for what was reported (the strip's labels were "ordered", "Beijing approved", "delivered", "stored": flat statements);
Nvidia's figures are said to be a share of revenue and a sum of sales (a reader: the 10-Q's is a share, not a sum).
Round 12 (Nov 26, 2026, outputs/ROUND12.md; core batch 14): the press bars' labels, with the words under the first, are the
step cells of the argument's table of numbers (a4lib.funnel() stops if one is not); the Hong Kong bar's second line names what
is counted, "Nvidia's advanced AI chips" (the report's words in short), not "to China". The page's top line is the credit alone.
Round 13 (Nov 26, 2026, outputs/ROUND13.md; core batch 15, rows B15-056 to -058): Washington returned without action the
APPLICATIONS for 55% of the chips the summary records, for 1,888,950, never the chips: bar 3's label (../h200_funnel.tsv), its
line in the dated list, the words under it and the notes say so. The summary's own definition of "PRC companies" is quoted
under bar 2 (a reader of the eighth). The headline keeps "to a few buyers": the report of Aug 18, 2026 names two, and the Hong
Kong report of Nov 5, 2026 says "Several major Chinese internet companies have each obtained about 10,000" (tried and undone).
The chief executive spoke the day after Reuters reported that Beijing had approved purchases (was "the report of Beijing's
approvals", which a core label of the Hong Kong report had used for another report).
Round 5 (Nov 24, 2026, core edits 5 and 6): the licence table is named by its own title and its release, not as the
Commerce Department's; the committee's example of 445,000 chips for Tencent is not said to be the table's row of 75,000,
and the share is given both ways (a4lib.house()).
Before the page or image is called done or shown: scripts/render_and_look.py on funnel.html and funnel.png.
"""
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import a4lib as A   # noqa: E402

esc, qm, fmt = A.esc, A.qm, A.fmt
# round 11: what each mark of the strip counts, as a noun; a press mark's second line says "reported" before its date
STRIP = {'ordered': 'orders', 'wapproved': 'Washington’s table', 'wreturned': 'Washington’s table', 'approved': 'Beijing’s approval',
         'discussed': 'possible total', 'delivered': 'deliveries', 'waiting': 'chips in Hong Kong'}
# round 10: a press row's date is the day its report was published, not the day of what it reports (the readers' leads 7 to 9)
LIST = {'ordered': 'orders reported', 'wapproved': 'approved by Washington (status date)', 'wreturned': 'applications returned by Washington (status date)',
        'approved': 'Beijing’s approval reported', 'discussed': 'discussion reported', 'delivered': 'deliveries reported', 'waiting': 'chips in Hong Kong reported'}
NUM = {2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven'}

CSS = '''
#fig { background: var(--page); }
header { margin-bottom: 18px; }
h1 { max-width: none; font-size: clamp(26px, 3.25vw, 40px); }
@media (max-width: 1000px) { h1 br { display: none; } }
.pin { display: inline-grid; place-items: center; flex: none; width: 22px; height: 22px; border-radius: 50%; font: 700 11px/1 var(--font-text); border: 2.5px solid;
  background: var(--surface); color: var(--ink); font-variant-numeric: tabular-nums; }
.pin.toward { border-color: var(--toward); } .pin.away { border-color: var(--away); } .pin.us { border-color: var(--us); }
.pin.solid { background: var(--ink2); border-color: var(--ink2); color: var(--pin-on); }      /* filled: on the record */
.row { display: grid; grid-template-columns: 22px minmax(200px, 290px) minmax(0, 1fr); gap: 4px 14px; padding: 14px 0 13px; border-top: 1px solid var(--grid); align-items: start; }
.lab b { display: block; font-weight: 600; font-size: 16.5px; line-height: 1.3; }
.lab span { display: block; font-size: 13.5px; color: var(--ink2); line-height: 1.35; margin-top: 2px; }
.track { display: flex; align-items: center; gap: 10px; min-height: 24px; min-width: 0; }
.track i { display: block; flex: none; height: 18px; min-width: 4px; border-radius: 0 4px 4px 0; width: calc((100% - 270px) * var(--f)); }
.track i.toward { background: var(--toward); } .track i.away { background: var(--away); } .track i.us { background: var(--us); }
.track em { font: 700 24px/1 var(--font-head); font-style: normal; white-space: nowrap; letter-spacing: -0.01em; }
.track em small { font: 500 14px/1 var(--font-text); color: var(--ink2); margin-right: 3px; letter-spacing: 0; }
.ours { font-size: 12.5px; color: var(--muted); line-height: 1.3; }
.said { margin: 7px 0 0; font-size: 13.5px; color: var(--ink2); line-height: 1.4; max-width: 84ch; }
.onrec { display: grid; grid-template-columns: 22px 1fr; gap: 14px; border-top: 1px solid var(--axis); padding-top: 13px; font-size: 14.5px; color: var(--ink2); line-height: 1.45; }
.onrec b { color: var(--ink); font-weight: 600; } .onrec p { margin: 0; }
.onrec ul { list-style: none; margin: 6px 0 0; padding: 0; } .onrec li { padding: 5px 0 0; font-size: 13.5px; line-height: 1.42; max-width: 104ch; }
.onrec i.mk { margin: 4px 0 0 4px; }
.srcn a { white-space: nowrap; }
@media (max-width: 760px) { .srcn a { white-space: normal; } }
.when { margin-top: 16px; }
.when svg { display: block; width: 100%; height: auto; }
svg text { font-family: var(--font-text); }
.ax { stroke: var(--axis); stroke-width: 1; } .tk { stroke: var(--axis); stroke-width: 1; }
.mo { font-size: 12px; font-weight: 500; fill: var(--muted); } .mo.yr { fill: var(--ink2); font-weight: 600; }
.pw { font-size: 12.5px; font-weight: 700; fill: var(--ink); text-anchor: middle; } .pd { font-size: 12px; font-weight: 500; fill: var(--ink2); text-anchor: middle; }
circle.c { fill: var(--surface); stroke-width: 2.5; } circle.c.toward { stroke: var(--toward); } circle.c.away { stroke: var(--away); } circle.c.us { stroke: var(--us); }
circle.c.solid { fill: var(--ink2); stroke: var(--ink2); }
.pn { font-size: 11px; font-weight: 700; fill: var(--ink); text-anchor: middle; } .pn.on { fill: var(--pin-on); }
.order { display: none; list-style: none; margin: 4px 0 0; padding: 0; }
.order li { display: flex; align-items: center; gap: 10px; padding: 7px 0; border-top: 1px solid var(--grid); font-size: 14.5px; }
.order li b { font-weight: 600; } .order li span { color: var(--ink2); margin-left: auto; white-space: nowrap; }
.order li span.pin { margin-left: 0; }                 /* the mark stays at the left; only the date goes to the right */
.order li span.pin.solid { color: var(--pin-on); }
@media (max-width: 760px) {
  .row { grid-template-columns: 22px minmax(0, 1fr); } .barcol { grid-column: 1 / -1; }
  .track { flex-direction: column; align-items: flex-start; gap: 5px; } .track em { order: 1; } .track .ours { order: 2; } .track i { order: 3; width: calc(100% * var(--f)); }
  .when svg { display: none; } .order { display: block; }
}
'''


def strip(rows):
    """When each count dates from: one mark per bar on a line of months. Bars that share a date (the two sums of
    Washington's table) stand side by side under one label."""
    W, H, GL, GR, AY = 1152, 104, 34, 34, 62
    a = date(min(r['date'] for r in rows).year, min(r['date'] for r in rows).month, 1)
    last = max(r['date'] for r in rows)
    b = date(last.year + (last.month == 12), last.month % 12 + 1, 1)
    X = lambda d: GL + (d - a).days / (b - a).days * (W - GL - GR)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="st-t st-d"><title id="st-t">When each count was reported</title>'
           f'<desc id="st-d">{esc("; ".join(str(r["n"]) + " " + LIST[r["key"]] + ", " + fmt(r["date"]) for r in sorted(rows, key=lambda r: (r["date"], r["n"]))))}</desc>',
           f'<line class="ax" x1="{GL}" y1="{AY}" x2="{W - GR}" y2="{AY}"/>']
    d = a
    while d <= b:
        x = X(d); first = d == a or d.month == 1
        if d < b:
            out.append(f'<line class="tk" x1="{x:.1f}" y1="{AY}" x2="{x:.1f}" y2="{AY + 6}"/><text class="mo{" yr" if first else ""}" x="{x + 4:.1f}" y="{AY + 22}">{A.MON[d.month - 1]}{" " + str(d.year) if first else ""}</text>')
        else:
            out.append(f'<line class="tk" x1="{x:.1f}" y1="{AY}" x2="{x:.1f}" y2="{AY + 6}"/>')
        d = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    days = sorted({r['date'] for r in rows})
    labs = []
    for dd in days:
        grp = [r for r in rows if r['date'] == dd]
        assert len({STRIP[r['key']] for r in grp}) == 1 and len({r['tier'] for r in grp}) == 1, 'bars that share a date share a label and a tier'
        second = ('reported ' if grp[0]['tier'] == 'open' else '') + f'{A.MON[dd.month - 1]} {dd.day}'     # round 11: a press mark says "reported"
        labs.append([dd, X(dd), STRIP[grp[0]['key']], second, 'middle', grp])
    wide = lambda s, px: len(s) * px * 0.6               # a rough width of a label, used only to keep two labels apart
    for a, b in zip(labs, labs[1:]):
        if a[1] + max(wide(a[2], 12.5), wide(a[3], 12)) / 2 + 8 > b[1] - max(wide(b[2], 12.5), wide(b[3], 12)) / 2:
            assert a[4] != 'start', 'three labels too close to set apart'
            a[4], b[4] = 'end', 'start'                  # the left one ends at its mark, the right one starts at its own
    for dd, x, word, second, anc, grp in labs:
        tx = x + {'middle': 0, 'end': 10, 'start': -10}[anc]; st = '' if anc == 'middle' else f' style="text-anchor:{anc}"'
        out.append(f'<text class="pw" x="{tx:.1f}" y="16"{st}>{esc(word)}</text><text class="pd" x="{tx:.1f}" y="32"{st}>{esc(second)}</text>')
        for i, r in enumerate(grp):
            cx = x + (i - (len(grp) - 1) / 2) * 24
            solid = r['tier'] == 'solid'
            out.append(f'<circle class="c {r["dir"]}{" solid" if solid else ""}" cx="{cx:.1f}" cy="{AY - 14}" r="10"/><text class="pn{" on" if solid else ""}" x="{cx:.1f}" y="{AY - 10}">{r["n"]}</text>')
    out.append('</svg>')
    return '\n'.join(out)


def joined(xs, last='and'):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + f' {last} ' + xs[-1]


def main():
    qfile = HERE / 'quotes.tsv'
    A.check(qfile)                                   # stops here if a quotation is not found in its saved copy
    Q = A.quotes(qfile); A.guard_control(Q)
    rows, H = A.funnel(Q)
    for n, r in enumerate(rows, 1): r['n'] = n
    top = max(r['chips'] for r in rows)
    press = [r for r in rows if r['tier'] == 'open']; docs = [r for r in rows if r['tier'] == 'solid']
    R = {r['key']: r for r in rows}
    delivered = R['delivered']; per = A.count(delivered['number'])
    d_rec = A.day(Q, 'onrecord'); period = fmt(date(*A.parse_date(Q['onrecord.period'])))
    d_q1, d_q3, d_q3end, d_cap = A.day(Q, 'nvq1'), A.day(Q, 'nvq3'), A.day(Q, 'nvq3.end'), A.day(Q, 'cap')
    first, last = min(r['date'] for r in rows), max(r['date'] for r in rows)
    bydate = sorted(rows, key=lambda r: (r['date'], r['n']))
    f = lambda v: f'{v:,}'
    places, names = joined(H['places'], 'or'), joined(H['names'])     # "whose ultimate location is A, B or C" (the table's own column)
    cap = A.count(Q['cap'].split('up to ')[1].split(' chips')[0])           # the cap Reuters reported, read from its sentence
    assert cap == H['cap'], 'the largest approved application in the table is not the May cap Reuters reported'
    assert Q['cap.later'].sid == delivered['sid'] and delivered['date'] > d_cap, 'the later cap must come from the August report'
    assert H['tencent_status'] == 'Approved, not shipped'
    status, released = fmt(H['status']), fmt(H['released'])
    # round 10: the two later accounts on the orders (the argument, section 4's opening); the chief executive spoke the day after Reuters's report of the approvals
    d_ceo, d_tw = A.day(Q, 'orders.ceo'), A.day(Q, 'orders.techweb')
    assert (d_ceo - R['approved']['date']).days == 1, 'the chief executive\'s words are not of the day after the report of the approvals'
    assert Q['later.several'].sid == R['waiting']['sid'], 'the report of several buyers is not the Hong Kong report'

    under = {
        'ordered': f'{qm(Q["ordered"])}; the report gives this on the word of {qm("two of the people")} it spoke to.',
        'wapproved': (f'The committee’s summary: {qm(Q["wapproved"])}. By its definition, “PRC companies” are {qm(Q["table.prc"])}. The table marks each of the {H["appr"][1]} {qm(Q["table.marked"])}. Nvidia is the exporter in {H["appr_nv"][1]} of them, '
                      f'AMD in {H["appr_amd"][1]} ({f(H["appr_amd"][0])} chips, kept apart here). No approved application in this table is for more than {f(H["cap"])} chips.'),
        'wreturned': (f'The table marks these RWA, the export bureau’s short form: {qm(Q["table.rwa"])}. Among Nvidia’s {H["rwa_nv"][1]} are all {H["abroad"][1]} applications whose ultimate location is {places} '
                      f'({f(H["abroad"][0])} chips), named for {names}. With AMD’s {H["rwa_amd"][1]}, the applications returned are for {f(H["rwa"][0])} of the table’s {f(H["all"][0])} chips, {H["share"]}% of the chips the summary records. '
                      f'The table gives no reasons, and the committee says some applications are {qm(Q["table.notfull"])}.'),
        'approved': f'{qm(Q["approved"])}. {qm(Q["approved.conditions"])}.',
        'discussed': f'{qm(Q["discussed.what"])}; {qm(Q["discussed"])}.',
        'delivered': (f'The Financial Times, citing two unnamed people, reported: {qm(Q["delivered"])}. '
                      f'By one of them, {qm(Q["delivered.outside"])} ({A.link(Q["delivered.outside"].sid, "Financial Times, on Yahoo Finance")}).'),
        'waiting': (f'Reuters, citing two unnamed people, reported: {qm(Q["waiting"])}, {qm(Q["waiting.withholds"])}. '
                    f'The report calls them {qm(Q["waiting.h200"].split("size of ")[1])}.'),
    }
    srclink = {
        'wapproved': lambda r: A.link(r['sid'], f'House Foreign Affairs Committee, summary made public {released}'),
        'wreturned': lambda r: A.link(r['sid'], f'the licence table, status {status}'),
    }
    rr = []
    for r in rows:
        note = ''
        if r['key'] == 'wapproved': note = f'<span class="ours">our sum of the table’s {r["apps"]} rows with Nvidia as exporter</span>'
        if r['key'] == 'wreturned': note = f'<span class="ours">our sum of the table’s {r["apps"]} rows with Nvidia as exporter</span>'
        if r['key'] == 'delivered': note = f'<span class="ours">the bar is drawn for both buyers the report names: 2 × {per:,}</span>'
        qual = f'<small>{esc(r["shown"][0])}</small>' if r['shown'][0] else ''
        link = srclink[r['key']](r) if r['key'] in srclink else A.link(r['sid'], f'{r["by"]}, {fmt(r["date"])}')
        rr.append(f'''<div class="row"><span class="pin {r["dir"]}{" solid" if r["tier"] == "solid" else ""}" aria-hidden="true">{r["n"]}</span>
 <div class="lab"><b>{esc(r["label"])}</b><span>{esc(r["what"])}</span></div>
 <div class="barcol"><div class="track"><i class="{r["dir"]}" style="--f:{r["chips"] / top:.4f}"></i><em>{qual}{esc(r["shown"][1])}</em>{note}</div>
  <p class="said">{under[r["key"]]} <span class="srcn">{link}</span></p></div></div>''')
    order = ''.join(f'<li><span class="pin {r["dir"]}{" solid" if r["tier"] == "solid" else ""}" aria-hidden="true">{r["n"]}</span><b>{LIST[r["key"]]}</b><span>{fmt(r["date"])}</span></li>' for r in bydate)
    docnums = joined(str(r['n']) for r in docs)

    # round 10: the title is not "Funnel" (the bars are not stages of one sale)
    page = A.head(f'H200 In {NUM[len(rows)].capitalize()} Counts', CSS) + f'''<body>
<div class="wrap">
 <p class="draft">{A.NOTE}</p>
 <div id="fig">
  <header>
   <p class="eyebrow">China · Nvidia’s H200 chip · {A.MON[first.month - 1]} {first.year} to {A.MON[last.month - 1]} {last.year}</p>
   <h1>Reported ordered: {esc(' '.join(R['ordered']['shown']))} H200 chips.<br> Reported delivered: about {per:,} each, to a few buyers.</h1>
   <p class="deck">{NUM[len(press)].capitalize()} press reports citing unnamed people, and {NUM[len(docs)]} sums from one United States government table of licence applications. They are separate counts, not one tally: they do not add up, and they are not stages of one sale. They are set side by side by what they count, not in date order. An application names a data-centre operator or ultimate consignee; it is not an order. Bars are drawn to one scale.</p>
   <ul class="key">
    <li><i class="sw toward"></i><span><b>Toward Nvidia:</b> seeking, buying, using or welcoming it</span></li>
    <li><i class="sw away"></i><span><b>Away from Nvidia:</b> holding it back</span></li>
    <li><i class="sw us"></i><span><b>Washington’s table</b> of licence applications</span></li>
    <li><span class="pin toward" aria-hidden="true">1</span><span><b>Open mark:</b> a press report citing unnamed people. {NUM[len(press)].capitalize()} bars</span></li>
    <li><span class="pin us solid" aria-hidden="true">2</span><span><b>Filled mark:</b> on the record. Bars {docnums}, and Nvidia’s own account</span></li>
   </ul>
  </header>
  <section class="card">
   <h2>The H200 in {NUM[len(rows)]} separate counts</h2>
   <p class="sub">The H200 is the Nvidia chip the United States allowed for sale to approved customers in China. Under each bar: the source’s own words, and how a sum was made.</p>
{chr(10).join(rr)}
   <div class="onrec"><i class="mk solid"></i><div><p><b>On the record: Nvidia’s own account, in money, not in chips.</b></p>
    <ul>
     <li><b>Results call of {fmt(d_q1)}.</b> {qm(Q["nvq1"])}. <span class="srcn">{A.link(Q["nvq1"].sid, "Nvidia, transcript of the call")}</span></li>
     <li><b>Quarter to {period}, filed {fmt(d_rec)}.</b> {qm(Q["onrecord.fraction"])}. {qm(Q["onrecord"])}. <span class="srcn">{A.link(Q["onrecord"].sid, "Nvidia, Form 10-Q")}</span></li>
     <li><b>Results call of {fmt(d_q3)}, for the quarter ended {fmt(d_q3end)}.</b> {qm(Q["nvq3"])}; {qm(Q["nvq3.stopped"])}. Nvidia gave no reason. The Hopper family includes the H200.
      <span class="srcn">{A.link(Q["nvq3"].sid, "Nvidia, transcript of the call")}</span></li>
    </ul></div></div>
  </section>
  <section class="card when">
   <h2>When each count was reported</h2>
   <p class="sub">In date order: {", ".join(str(r["n"]) for r in bydate)}. Each press report stands at the day it was published, which can be after what it reports: the report of {fmt(delivered["date"])} says the chips were received {qm(Q["delivered"].split("processors ")[1])}. A later count does not update an earlier one; each counts a different thing. Bars {docnums} give the table’s status on {status}; the table was made public on {released}.</p>
{strip(rows)}
   <ol class="order">{order}</ol>
  </section>
 {A.IMGNOTE}
 </div>
 <section class="card notes">
  <h2>Read with care</h2>
  <ul>
   <li>The bars count different things at different dates, so no bar is a share of another. {NUM[len(press)].capitalize()} rest on unnamed people; {NUM[len(docs)]} are sums of a government table.</li>
   <li>Washington’s table, {qm(Q["wapproved.date"])}, gives the status of each licence application. The House Foreign Affairs Committee made it public on {released}; its summary cites {qm(Q["table.bis"])}. BIS is the Commerce Department’s Bureau of Industry and Security. The table covers {f(H["all"][0])} chips in {H["all"][1]} applications: {qm(Q["table.products"])}
    It does not say which chip a row is; bars {docnums} count the rows with Nvidia as exporter. An application names a data-centre operator or ultimate consignee; it is not an order. “Approved” in bar {R["wapproved"]["n"]} is Washington’s licence; bar {R["approved"]["n"]} is Beijing’s approval, by a press report.</li>
   <li>The sums are ours, of the table’s rows as the project read them from its page images; the totals equal the figures the committee’s summary prints. Nvidia’s chips and AMD’s are not added in the bars. With AMD’s, the approved count is {f(H["appr"][0])} chips in {H["appr"][1]} applications, and the {H["rwa"][1]} applications returned without action are for {f(H["rwa"][0])} chips.</li>
   <li>The {H["share"]}% counts the chips in the returned applications as a share of the chips in the applications the summary records, not of everything applied for. The committee’s example: {qm(Q["table.tencent"])}. The table’s only Tencent row of that date is for {f(H["tencent_shown"])} chips, approved; neither document says whether it is that application. The share would be {H["share_full"]}% if it is, counted at {f(H["tencent_full"])}, and {H["share_further"]}% if the {f(H["tencent_full"])} is a further application and was not returned without action (our arithmetic).</li>
   <li>No approved application in the table is above {f(H["cap"])} chips, and all {NUM[H["over"]]} above that number were returned. On {fmt(d_cap)} Reuters, by two people it did not name, reported a limit for each approved buyer: {qm(Q["cap"])}. It also wrote that {qm(Q["cap.nodelivery"])}, and that the {qm(Q["cap.tangle"])}. The Financial Times, through {A.link(Q["cap.later"].sid, f"Reuters on {fmt(delivered['date'])}")}, later reported, citing people it did not name, that Washington {qm(Q["cap.later"])}. It named {esc(" and ".join(delivered["buyers"]))}.</li>
   <li>The approval Reuters reported on {fmt(R["approved"]["date"])} was not yet a purchase: a source said {qm(Q["approved.notconverting"])}.</li>
   <li>The possible total of July ({esc(R["discussed"]["shown"][0])} {esc(R["discussed"]["shown"][1])}) was, in the report’s words, {qm(Q["discussed.half"])}.</li>
   <li>The report of {fmt(delivered["date"])} names two buyers. A later report speaks of several: {qm(Q["later.several"])} ({A.link(Q["later.several"].sid, f"Reuters, {fmt(R['waiting']['date'])}")}).</li>
   <li>Two later accounts say otherwise of the orders reported in bar {R["ordered"]["n"]}. Nvidia’s chief executive, the day after Reuters reported that Beijing had approved purchases, said <span lang="zh-Hans">{qm(Q["orders.ceo"])}</span> (I think the Chinese government is still deciding; we have not yet received purchase orders), as {A.link(Q["orders.ceo"].sid, f"Voice of America’s Chinese service, {fmt(d_ceo)}")}, renders him.
    TechWeb, as {A.link(Q["orders.techweb"].sid, "Sina carries it")}, reported on {fmt(d_tw)}, from industry insiders it did not name, that <span lang="zh-Hans">{qm(Q["orders.techweb"])}</span> (China’s AI firms had placed almost no bulk purchase orders for Nvidia’s H200). English in round brackets is ours, not an official translation.</li>
   <li>Nvidia’s figures are in money, not in chips: a share of its revenue in the quarterly report, a sum of its sales on the call. Neither its call of {fmt(d_q3)} nor Reuters’s report of it says how many of those chips crossed into the mainland.</li>
   <li>No report here says how many H200 chips have entered the mainland.</li>
  </ul>
 </section>
</div>
</body>
</html>
'''
    dates = ([fmt(r['date']) for r in rows] + [fmt(d_rec), period, fmt(d_q1), fmt(d_q3), fmt(d_q3end), fmt(d_cap), status, released, fmt(d_ceo), fmt(d_tw)]
             + [f'{A.MON[r["date"].month - 1]} {r["date"].day}' for r in rows])
    # ours: the sums of Washington's table and the shares made from them (a4lib.house); the numbers 1 to 7 on the marks;
    # "2 x" for the two buyers named in the sentence; 10: the filing's name, Form 10-Q
    ours = [H[k][0] for k in ('all', 'appr', 'appr_nv', 'appr_amd', 'rwa', 'rwa_nv', 'rwa_amd', 'abroad')] + [H[k][1] for k in ('all', 'appr', 'appr_nv', 'appr_amd', 'rwa', 'rwa_nv', 'rwa_amd', 'abroad')]
    ours += [H['share'], H['share_full'], H['share_further'], H['tencent_shown'], H['cap'], *range(1, len(rows) + 1), '10']
    A.guard(page, Q, ours=ours, dates=dates)
    # withdrawn by core edit 6 (atlas/core_edit/APPLIED_6.txt, part 05): the table is not called the Commerce Department's,
    # and the Tencent row of 75,000 is not called the application of 445,000
    # round 11 (outputs/ROUND11.md thing 2): every press row's label carries the report; control: the two table rows do not
    assert all(r['label'].startswith('Reported: ') == (r['tier'] == 'open') for r in rows), 'a press row\'s label does not begin "Reported: "'
    for banned in ('>Delivered<', '>Stored in Hong Kong', '>Ordered by', '>Approved by Beijing', '>Under discussion', 'a stockpile of H200', '>stored<', '>delivered<',
                   '>ordered<', '>Beijing approved<', '>discussed<', 'sums of money, not counts'):
        assert banned not in page, f'round 11: the page still says "{banned}"'
    # round 12: the steps as the argument now words them (control: each press bar's step stands on the page in its two parts)
    assert all(f'<b>{esc(r["label"])}</b><span>{esc(r["what"])}</span>' in page and (r['step'] == r['label'] or r['step'] == r['label'] + ' ' + r['what']) for r in press), 'a press bar does not show its step'
    for banned in ('>Reported: delivered<', '>Reported: under discussion in Beijing<', 'awaiting shipment</b>', '<span>to China</span>', 'Local; not published', 'not published'):
        assert banned not in page, f'round 12: the page still says "{banned}"'
    # round 13 (core batch 15, rows B15-056 to -058): applications were returned, not chips; the headline names the two buyers
    assert '<b>Applications returned by Washington without action</b>' in page and 'applications returned by Washington (status date)' in page, 'control: bar 3 says applications'
    for banned in ('>Returned by Washington', '>returned by Washington (status date)', 'the returned count', 'of the chips in the applications the summary records. ',
                   'report of Beijing’s approvals'):
        assert banned not in page, f'round 13: the page still says "{banned}"'
    for banned in ('750,000', 'cleared by Washington', 'Democrats', 'more than half', 'subsidiar', 'Commerce Department’s table', 'Commerce Department table',
                   'Commerce Department’s, with', 'shows that application', 'an application the table shows', 'counted in full',
                   # withdrawn by core edit 8b (Nov 25, 2026): the table's column names a data-centre operator or ultimate consignee and an ultimate
                   # location; the 48.6% reading needs the further application not returned; the 75,000 limit is reported by two unnamed people;
                   # Beijing's approval is a press report; the negative on the mainland is said of the reports here
                   'names a consignee;', 'applications for consignees in', 'is a further application (our', 'reported that cap', 'Beijing’s approval of',
                   'entered the mainland is not known',
                   # round 10 (readers' leads on the public page): the bars are not stages of a sale; "first" report not tested
                   'in the order of a sale', 'step by step', 'The first report of deliveries', 'H200 Funnel'):
        assert banned not in page, f'the page still says "{banned}"'
    out = HERE / 'funnel.html'
    out.write_text(page, encoding='utf-8'); print('written', out, len(page), 'bytes')
    print(f'bars: {len(rows)} ({len(press)} press reports, {len(docs)} sums of Washington\'s table): ' + '; '.join(f'{r["n"]} {r["key"]} {r["chips"]:,}' for r in rows))
    print(f'table: all {f(H["all"][0])} in {H["all"][1]}; approved {f(H["appr"][0])} in {H["appr"][1]} (Nvidia {f(H["appr_nv"][0])} in {H["appr_nv"][1]}, AMD {f(H["appr_amd"][0])} in {H["appr_amd"][1]}); '
          f'returned {f(H["rwa"][0])} in {H["rwa"][1]} (Nvidia {f(H["rwa_nv"][0])} in {H["rwa_nv"][1]}, AMD {f(H["rwa_amd"][0])} in {H["rwa_amd"][1]}) = {H["share"]}% of the table; abroad {f(H["abroad"][0])} in {H["abroad"][1]}; '
          f'above the table’s largest approval ({f(H["cap"])} chips): {H["over"]}, all returned; the share {H["share_full"]}% if the Tencent row of {f(H["tencent_shown"])} is the application of {f(H["tencent_full"])}, '
          f'{H["share_further"]}% if that is a further application')
    if '--png' in sys.argv:
        A.png(out, [('#fig', HERE / 'funnel.png')], width=1256, height=1000, css=A.FIG_EXPORT,
              fits=[('.track', '.card'), ('.track em', '.card'), ('.track .ours', '.card'), ('.lab', '.row'), ('.said', '.card'), ('.onrec li', '.card'), ('.card', '#fig'), ('.imgnote', '#fig')])


main()
