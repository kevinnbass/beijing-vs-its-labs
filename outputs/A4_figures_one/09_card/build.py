#!/usr/bin/env python3
"""Idea 9: a card for a post. One image of 1200 by 675 (exported at twice that size), light theme.

Run: python3 -I build.py                                   checks quotes.tsv with scripts/cn_has.py, writes card.html
     python3 build.py --png     the same, then writes card.png (2400 by 1350)
Reads quotes.tsv (this folder), ../h200_funnel.tsv (the six rows) and ../a4lib.py (shared helpers).
Nothing is written unless cn_has.py exits 0 and the guard finds every quotation and number on the page in quotes.tsv.
Bar lengths, the sums of Washington's table (made by a4lib.house() from the project's tables/house_licence_table.tsv)
and every date come from those files through a4lib.py, not from typing. Round 4: the rows follow the core figure's bars.
Round 5 (Nov 24, 2026, core edits 5 and 6): the licence table is named by its own title and its release, not as the
Commerce Department's; the committee's example of 445,000 chips for Tencent is not said to be the table's row of 75,000,
and the share is given both ways (a4lib.house()).
Round 9b (Nov 25, 2026, core edit 8b): an application names a data-centre operator or ultimate consignee; the five abroad
are those whose ultimate location is outside China; 48.6% also needs the further application not returned without action;
the July total is one that could be under 200,000; Bloomberg's report rests on people it did not name.
Before the card is called done or shown: scripts/render_and_look.py on card.html and on card.png.
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import a4lib as A   # noqa: E402

esc, qm, fmt = A.esc, A.qm, A.fmt
BAR = 300           # card pixels for the longest bar (2 million)


def px(css):
    """The card is drawn in card pixels (1200 wide) and scales with its box: every 'px' becomes container units. 'PX' stays a real pixel."""
    return re.sub(r'(-?\d+(?:\.\d+)?)px', lambda m: f'{float(m.group(1)) / 12:.4f}cqw', css)


CARD_CSS = px('''
.cardwrap { width: min(100%, 1200PX); container-type: inline-size; box-shadow: 0 0 0 1PX var(--border), 0 10PX 34PX rgba(11,11,11,0.07); }
#card { width: 1200px; height: 675px; background: var(--page); color: var(--ink); padding: 32px 44px 18px; display: grid; grid-template-columns: 452px minmax(0, 1fr);
  grid-template-rows: minmax(0, 1fr) auto; column-gap: 36px; row-gap: 12px; overflow: hidden; font-size: 16px; line-height: 1.4; }
#card p, #card h1, #card h2 { margin: 0; max-width: none; }
#card .l { display: flex; flex-direction: column; min-height: 0; }
#card .eb { font: 700 12.5px/1.2 var(--font-text); letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); }
#card .hl { font: 700 38px/1.08 var(--font-head); letter-spacing: -0.015em; margin-top: 12px; text-wrap: nowrap; }
#card .dk { font-size: 15.5px; line-height: 1.4; color: var(--ink2); margin-top: 12px; text-wrap: pretty; }
#card .says { margin-top: auto; padding-top: 18px; display: grid; gap: 14px; }
#card .say { border-left: 3px solid; padding: 1px 0 2px 16px; }
#card .say.away { border-color: var(--away); } #card .say.toward { border-color: var(--toward); }
#card .who { font: 700 12px/1.3 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink2); display: flex; align-items: center; gap: 8px; }
#card .q { font: 600 20.5px/1.25 var(--font-text); margin-top: 5px; letter-spacing: -0.005em; text-wrap: balance; }
#card .by { font-size: 13px; line-height: 1.35; color: var(--muted); margin-top: 5px; white-space: nowrap; }
#card i.mk { width: 12px; height: 12px; border-width: 2.5px; vertical-align: -1.5px; }
#card i.sw { width: 11px; height: 11px; border-radius: 2.5px; }
#card .fn { background: var(--surface); border: 1PX solid var(--border); border-radius: 14px; padding: 17px 22px 6px; display: flex; flex-direction: column; min-height: 0; }
#card .fn h2 { font: 700 21px/1.2 var(--font-head); }
#card .fs { font-size: 13px; line-height: 1.38; color: var(--ink2); margin-top: 3px; }
#card .fk { display: flex; gap: 16px; font-size: 12.5px; color: var(--ink2); margin-top: 7px; align-items: center; }
#card .fk span { display: inline-flex; align-items: center; gap: 6px; }
#card .rows { margin-top: 9px; display: grid; flex: 1; grid-auto-rows: 1fr; min-height: 0; }
#card .r { border-top: 1PX solid var(--grid); display: flex; flex-direction: column; justify-content: center; min-height: 0; }
#card .lab { display: flex; align-items: baseline; gap: 10px; white-space: nowrap; }
#card .lab b { font-weight: 600; font-size: 18.5px; }
#card .lab span { font-size: 12px; color: var(--muted); }
#card .bar { display: flex; align-items: center; gap: 10px; margin-top: 1px; height: 31px; }
#card .bar i { display: block; flex: none; height: 17px; border-radius: 0 4px 4px 0; }
#card .bar i.toward { background: var(--toward); } #card .bar i.away { background: var(--away); } #card .bar i.us { background: var(--us); }
#card .bar em { font: 700 28px/1 var(--font-head); font-style: normal; white-space: nowrap; letter-spacing: -0.01em; }
#card .bar em small { font: 500 15px/1 var(--font-text); color: var(--ink2); letter-spacing: 0; margin-right: 3px; }
#card .bar .nt { font-size: 12px; line-height: 1.25; color: var(--muted); white-space: nowrap; }
#card .ft { grid-column: 1 / -1; border-top: 1PX solid var(--axis); padding-top: 8px; font-size: 11.3px; line-height: 1.4; color: var(--muted); }
#card .ft .last { display: flex; justify-content: space-between; gap: 24px; white-space: nowrap; }
#card .ft b { color: var(--ink2); font-weight: 600; }
''')

PAGE_CSS = '''
.below { display: grid; gap: 16px; margin-top: 22px; }
@media (max-width: 700px) { table.tv thead { display: none; } table.tv tr { display: block; padding: 8px 0; border-bottom: 1px solid var(--grid); }
  table.tv td { display: block; border: 0; padding: 2px 0; } }
'''


def joined(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]


def main():
    qfile = HERE / 'quotes.tsv'
    A.check(qfile)                                   # stops here if a quotation is not found in its saved copy
    Q = A.quotes(qfile); A.guard_control(Q)
    rows, H = A.funnel(Q, card=True)                 # six rows: the funnel page's seven less the one the data file marks card=no
    allrows, _ = A.funnel(Q)
    left_out = [r for r in allrows if r['card'] == 'no']
    assert len(rows) == 6 and len(left_out) == 1
    top = max(r['chips'] for r in rows)
    press = [r for r in rows if r['tier'] == 'open']; docs = [r for r in rows if r['tier'] == 'solid']
    num = {2: 'two', 4: 'four', 6: 'six'}
    d_away, d_toward, d_call, d_q3 = A.day(Q, 'away'), A.day(Q, 'toward'), A.day(Q, 'nvq3'), A.day(Q, 'nvq3.end')
    period = fmt(A.date(*A.parse_date(Q['away.period'])))
    d_first, d_carried = A.day(Q, 'care.guidance'), A.day(Q, 'care.carried')   # Bloomberg's report, and the day The Business Times carried it
    alld = [r['date'] for r in rows] + [d_away, d_toward, d_first]
    span = f'{A.MON[min(alld).month - 1]} {min(alld).year} to {A.MON[max(alld).month - 1]} {max(alld).year}'
    delivered = next(r for r in rows if r['key'] == 'delivered'); both = delivered['chips']
    f = lambda v: f'{v:,}'
    places = ', '.join(H['places'][:-1]) + ' or ' + H['places'][-1]      # "whose ultimate location is A, B or C" (the table's own column)
    HEAD = 'Beijing mostly pulled one way on Nvidia chips. Its AI companies pulled the other.'     # the core figure's headline

    # ---- the card ----
    rr = []
    for r in rows:
        w = max(4, round(BAR * r['chips'] / top))
        note, src = '', f'<i class="mk {r["tier"]} {r["dir"]}"></i> {esc(r["by"])}, {fmt(r["date"])}'
        if r['key'] == 'wapproved':
            src = f'<i class="mk solid us"></i> US table, status {fmt(H["status"])}'
            note = f'<span class="nt">Nvidia’s chips, in {r["apps"]} applications.<br>AMD’s {f(H["appr_amd"][0])}, in {H["appr_amd"][1]} more, are apart.</span>'
        if r['key'] == 'wreturned':
            src = '<i class="mk solid us"></i> the same table'
            note = f'<span class="nt">Nvidia’s chips,<br>in {r["apps"]} applications</span>'
        if r['key'] == 'delivered': note = f'<span class="nt">to {r["buyers"][0]} and to {r["buyers"][1]}</span>'
        qual = f'<small>{esc(r["shown"][0])}</small>' if r['shown'][0] else ''
        rr.append(f'<div class="r"><p class="lab"><b>{esc(r["label"])}</b><span>{src}</span></p>'
                  f'<div class="bar"><i class="{r["dir"]}" style="width:{w / 12:.4f}cqw"></i><em>{qual}{esc(r["shown"][1])}</em>{note}</div></div>')
    reut_txt = '; '.join(fmt(d) for d in sorted(r['date'] for r in press if r['by'] == 'Reuters'))
    relays = [f'{"the " if r["by"].startswith("Financial") else ""}{r["by"]} ({fmt(r["date"])})' for r in press if r['by'] != 'Reuters']
    card = f"""<div class="cardwrap"><div id="card" role="img" aria-label="Card: {HEAD} The numbers are in the table below.">
 <div class="l">
  <p class="eb">China · Nvidia chips · {span}</p>
  <h1 class="hl">Beijing mostly pulled<br>one way on Nvidia chips.<br>Its AI companies<br>pulled the other.</h1>
  <p class="dk">From {d_first.year} Beijing’s security and planning side pressed AI companies, through unpublished guidance the press reported, to buy home-made chips. They kept ordering Nvidia’s.</p>
  <div class="says">
   <div class="say away"><p class="who"><i class="mk solid away"></i>Beijing holds Nvidia back</p>
    <p class="q">{qm(Q["away"])}</p>
    <p class="by">Nvidia, Form 10-Q, {fmt(d_away)}, on US-licensed H200 sales.</p></div>
   <div class="say toward"><p class="who"><i class="mk open toward"></i>The companies reach for Nvidia</p>
    <p class="q">{qm(Q["toward"].replace(", sources say", ""))}</p>
    <p class="by">Reuters headline, {fmt(d_toward)}, on a report citing unnamed people.</p></div>
  </div>
 </div>
 <section class="fn">
  <h2>The H200 chip, in {num[len(rows)]} numbers</h2>
  <p class="fs">{num[len(press)].capitalize()} press reports citing unnamed people, and {num[len(docs)]} sums from one United States government table of licence applications. Separate counts, not one tally. An application names a data-centre operator or ultimate consignee; it is not an order.</p>
  <p class="fk"><span><i class="sw toward"></i>toward Nvidia: ordering it, letting it in</span><span><i class="sw away"></i>away: held back</span><span><i class="sw us"></i>Washington’s table</span></p>
  <div class="rows">
{chr(10).join(rr)}
  </div>
 </section>
 <div class="ft">
  <p><b>Sources.</b> Reuters ({reut_txt}); {"; ".join(relays)}; the table {qm(Q["wapproved.date"])}, made public by the House Foreign Affairs Committee on {fmt(H["released"])}.
   Lines: Nvidia, Form 10-Q for the quarter to {period}; Reuters, {fmt(d_toward)}. The guidance from {d_first.year}: Bloomberg, {fmt(d_first)}.</p>
  <p><b>Read with care: five limits.</b> Beijing was not one actor; the pressure came as reported guidance and public warnings, not a published ban; some purchases were approved and some chips came in;
   the companies had reasons of their own, and American curbs pushed too; what Beijing meant by it is read both ways. <b>Washington’s table:</b> with AMD’s chips, {f(H["rwa"][0])} were returned without action,
   {H["share"]}% of the chips in the applications its summary records; it gives no reasons, and “approved” there is Washington’s licence, not Beijing’s.</p>
  <p class="last"><span><i class="mk solid"></i> <b>Filled mark:</b> on the record (a filing, a document, a named person). <i class="mk open"></i> <b>Open mark:</b> a press report citing unnamed people.</span><span>{A.NOTE}</span></p>
 </div>
</div></div>"""

    # ---- the page around it: the same content as a table, and the cautions ----
    trs = []
    for r in rows:
        shown = f'{r["shown"][0]} {r["shown"][1]}'.strip()
        if r['key'] == 'wapproved':
            words = (f'{qm(r["words"])}. The table marks each of them {qm(Q["table.marked"])}. Nvidia’s part, {f(r["chips"])} in {r["apps"]} applications, is our sum of the table’s rows; '
                     f'AMD’s is {f(H["appr_amd"][0])} in {H["appr_amd"][1]}.')
        elif r['key'] == 'wreturned':
            words = (f'The table marks these applications RWA, the export bureau’s short form: {qm(Q["table.rwa"])}. {f(r["chips"])} is our sum of the {r["apps"]} rows so marked with Nvidia as exporter; '
                     f'with AMD’s {H["rwa_amd"][1]} ({f(H["rwa_amd"][0])}) the count is {f(H["rwa"][0])}.')
        else: words = qm(r['words'])
        if r['tier'] == 'solid':
            src = A.link(r['sid'], f'Licence table, status {fmt(H["status"])}; made public by the House Foreign Affairs Committee, {fmt(H["released"])}')
            kind = '<i class="mk solid us"></i> on the record: a United States government table'
        else:
            src = A.link(r['sid'], f'{r["by"]}, {fmt(r["date"])}'); kind = f'<i class="mk open {r["dir"]}"></i> press report citing unnamed people'
        trs.append(f'<tr><td><b>{esc(r["label"])}</b><br>{esc(shown)}</td><td>{words}</td><td>{src}</td><td>{kind}</td></tr>')
    trs.append(f'<tr><td><b>Beijing holds Nvidia back</b><br>one line</td><td>{qm(Q["away"])}</td><td>{A.link(Q["away"].sid, f"Nvidia, Form 10-Q, {fmt(d_away)}")}</td>'
               f'<td><i class="mk solid away"></i> on the record: a company filing</td></tr>')
    trs.append(f'<tr><td><b>The companies reach for Nvidia</b><br>one line</td><td>{qm(Q["toward"])}</td><td>{A.link(Q["toward"].sid, f"Reuters, {fmt(d_toward)}")}</td>'
               f'<td><i class="mk open toward"></i> press report citing unnamed people</td></tr>')
    lo = left_out[0]
    page = A.head('Beijing vs. Labs Card', CARD_CSS + PAGE_CSS, theme='light') + f"""<body>
<div class="wrap">
 <p class="draft">{A.NOTE} A card for a post; the image file beside this page is card.png.</p>
{card}
 <div class="below">
  <section class="card">
   <h2>What the card rests on</h2>
   <p class="sub">Each number and line on the card, in the source’s own words. Every quotation was found in the saved copy of its source by a script.</p>
   <table class="tv"><thead><tr><th>On the card</th><th>The source’s words</th><th>Source</th><th>Kind</th></tr></thead><tbody>
{chr(10).join(trs)}
   </tbody></table>
  </section>
  <section class="card notes">
   <h2>Read with care</h2>
   <ul>
    <li>The {num[len(rows)]} numbers are separate counts: {num[len(press)]} press reports citing unnamed people and {num[len(docs)]} sums of one United States government table. They are not steps of one tally and do not add up.</li>
    <li>Washington’s table, {qm(Q["wapproved.date"])}, gives the status of each application; the House Foreign Affairs Committee made it public on {fmt(H["released"])}, and its summary cites {qm(Q["table.bis"])}. BIS is the Commerce Department’s Bureau of Industry and Security. The table covers {f(H["all"][0])} chips in {H["all"][1]} applications, Nvidia’s H200 and AMD’s MI325X.
     An application names a data-centre operator or ultimate consignee; it is not an order. “Approved” there is Washington’s licence, not Beijing’s. The table gives no reason for returning an application.</li>
    <li>The sums are ours, of the table’s rows. The card’s bars count Nvidia’s chips only; its footer gives the returned count with AMD’s, and says so. With AMD’s the approved count is {f(H["appr"][0])} and the returned count {f(H["rwa"][0])}, which is {H["share"]}% of the chips in the applications the summary records.
     All {H["abroad"][1]} applications whose ultimate location is {places} ({f(H["abroad"][0])} chips) are among those returned. The committee says some applications are {qm(Q["table.notfull"])}: {qm(Q["table.tencent"])}. The table’s only Tencent row of that date is for {f(H["tencent_shown"])} chips, approved;
     neither document says whether it is that application. The share would be {H["share_full"]}% if it is, counted at {f(H["tencent_full"])}, and {H["share_further"]}% if the {f(H["tencent_full"])} is a further application and was not returned without action (our arithmetic).</li>
    <li>The card leaves out one reported number that the funnel page carries: Beijing was still determining how many chips to approve, and the total could be {esc(lo["shown"][0])} {esc(lo["shown"][1])} ({esc(lo["by"])}, {fmt(lo["date"])}).</li>
    <li>The bar for the chips delivered is drawn for both named buyers together ({both:,}); the report gives about {A.count(delivered["number"]):,} each.</li>
    <li>On the record, in money and not in chips: on its results call of {fmt(d_call)}, for the quarter ended {fmt(d_q3)}, Nvidia said {qm(Q["nvq3"])}. The Hopper family includes the H200. Neither the call nor Reuters’s report of it says how many of those chips crossed into the mainland.</li>
    <li>The Reuters headline is from {fmt(d_toward)}, when the chip at issue was the H20. The United States allowed H200 sales to China only later.</li>
    <li>The sentence under the headline rests on the argument this card goes with. Bloomberg’s report of {fmt(d_first)} (carried by The Business Times on {fmt(d_carried)}), by people it did not name: {qm(Q["care.guidance"])}.</li>
    <li>The five limits, in the argument’s words: Beijing was not one actor; the pressure came as public warnings and unpublished guidance, not as a published ban (no published Chinese order against buying Nvidia chips was found in the 82 policy pages read);
     some purchases were approved and some chips came in; the companies had reasons of their own, and American curbs and conditions pushed too; and what Beijing meant by it is not settled.</li>
   </ul>
  </section>
 </div>
</div>
</body>
</html>
"""
    dates = [fmt(d) for d in alld] + [period, span, fmt(d_call), fmt(d_q3), fmt(d_carried), fmt(H['status']), fmt(H['released']), fmt(lo['date'])]
    # ours: sums of Washington's table and the shares made from them (a4lib.house); 2 x 10,000; 82 = the project's count of policy pages read
    ours = [H[k][0] for k in ('all', 'appr', 'appr_nv', 'appr_amd', 'rwa', 'rwa_nv', 'rwa_amd', 'abroad')] + [H[k][1] for k in ('all', 'appr_nv', 'appr_amd', 'rwa_nv', 'rwa_amd', 'abroad')]
    ours += [H['share'], H['share_full'], H['share_further'], H['tencent_shown'], both, '82', '10']          # 10: the filing's name, Form 10-Q
    assert H['tencent_status'] == 'Approved, not shipped'                  # the page says the Tencent row is approved
    A.guard(page, Q, ours=ours, dates=dates)
    # withdrawn by core edit 6 (atlas/core_edit/APPLIED_6.txt, part 05): the table is not called the Commerce Department's,
    # and the Tencent row of 75,000 is not called the application of 445,000
    for banned in ('750,000', 'four limits', 'Democrats', 'more than half', 'Commerce Department’s table', 'Commerce Department table',
                   'Commerce Department’s, with', 'shows that application', 'an application the table shows', 'counted in full',
                   # withdrawn by core edit 8b (Nov 25, 2026): the table's column names a data-centre operator or ultimate consignee and an ultimate
                   # location; the 48.6% reading needs the further application not returned; the July total is one that could be under 200,000
                   'names a consignee;', 'applications for consignees in', 'is a further application (our', 'chips under discussion in Beijing'):
        assert banned not in page, f'the page still says "{banned}"'
    out = HERE / 'card.html'
    out.write_text(page, encoding='utf-8'); print('written', out, len(page), 'bytes')
    print(f'rows on the card: {len(rows)} ({len(press)} press reports, {len(docs)} sums of Washington\'s table); Nvidia approved {f(H["appr_nv"][0])} in {H["appr_nv"][1]}, returned {f(H["rwa_nv"][0])} in {H["rwa_nv"][1]}; with AMD returned {f(H["rwa"][0])} of {f(H["all"][0])} = {H["share"]}%')
    if '--png' in sys.argv:
        A.png(out, [('#card', HERE / 'card.png')], width=1280, height=900,
              fits=[('#card .lab', '.fn'), ('#card .lab b', '.fn'), ('#card .lab span', '.fn'), ('#card .bar', '.fn'), ('#card .bar em', '.fn'), ('#card .nt', '.fn'), ('#card .rows', '.fn'), ('#card .fs', '.fn'),
                    ('#card .q', '.l'), ('#card .by', '.l'), ('#card .dk', '.l'), ('#card .hl', '.l'), ('#card .says', '.l'), ('#card .l', '#card'), ('#card .fn', '#card'),
                    ('#card .ft', '#card'), ('#card .ft p', '#card'), ('#card .ft .last span', '#card')])
        from PIL import Image
        with Image.open(HERE / 'card.png') as im: assert im.size == (2400, 1350), f'the card must be 2400 by 1350, got {im.size}'


main()
