"""Build the figure "The US side, step by step": what Washington allowed and what was shipped or sold, as dated steps.

Run: python3 -I build.py                                   checks every quotation, writes the page and records.tsv
     python3 -I build.py --png   the same, then exports us_side_steps.png
Reads data.txt (../common.py explains the format). Writes quotes.tsv from it and runs scripts/cn_has.py on that file; if the
checker does not pass, nothing else is written. Every number shown is a "V" line of data.txt with the page's words beside it.
The numbers do not count the same things (licence applications for two companies' chips; a ceiling per firm for one chip;
chips received by two buyers; a share of revenue; a sum in dollars). So nothing is drawn to scale and no step is drawn as
a part of another: each step states its number with the yardstick it is counted in.
"""
import re, sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as C   # noqa: E402

NAME = 'us_side_steps'
LANES = {'allowed': ('Washington allowed or licensed', 'what could be sold: decisions, licences, ceilings'),
         'out': ('Shipped or sold', 'what went out, by officials’, Nvidia’s and press accounts')}

CSS = """
/* Layout: headline and key; the warning (five yardsticks); the steps (a dated rail, then two lanes: allowed | shipped or sold); read with care; the records. */
.ys { display: grid; grid-template-columns: 1fr; gap: 6px 22px; margin-top: 8px; }
@media (min-width: 760px) { .ys { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (min-width: 1100px) { .ys { grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 6px 14px; } }
.ys div { border-top: 2px solid var(--ink2); padding-top: 6px; font-size: 13px; line-height: 1.35; color: var(--ink2); }
.ys div b { display: block; font: 700 14.5px/1.25 var(--font-text); color: var(--ink); margin-bottom: 2px; }
.st { display: grid; grid-template-columns: minmax(200px, 0.78fr) minmax(0, 1.2fr) minmax(0, 1.2fr); gap: 6px 8px; }
.st-h { padding: 2px 4px 8px; border-bottom: 3px solid var(--ink2); align-self: end; }
.st-h.corner { border-color: transparent; font: 700 12px/1.2 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); padding-left: 44px; }
.st-h b { display: block; font: 700 18px/1.2 var(--font-head); }
.st-h span { display: block; font-size: 12.5px; color: var(--muted); margin-top: 2px; }
.stw { position: relative; padding: 9px 10px 9px 44px; }
.stw::before { content: ""; position: absolute; left: 14px; top: -6px; bottom: -6px; border-left: 2px solid var(--axis); }
.stw.first::before { top: 20px; } .stw.last::before { bottom: calc(100% - 20px); }
.stw i.p { position: absolute; left: 4px; top: 9px; }
.stw a { text-decoration: none; color: inherit; display: block; border-radius: 8px; }
.stw a:hover i.p, .stw a.hl i.p, .stw a:focus-visible i.p { outline: 2.5px solid var(--ink); outline-offset: 1px; }
.stw b { display: block; font: 700 15.5px/1.25 var(--font-text); font-variant-numeric: tabular-nums; white-space: normal; }
.stw span { display: block; font-size: 12.5px; line-height: 1.35; color: var(--ink2); margin-top: 2px; }
.sc { border-radius: 10px; padding: 9px 13px 10px; min-width: 0; background: var(--slot); }
.sc.has { background: var(--wash); }
.sc.stop { background: var(--surface); box-shadow: inset 0 0 0 2.5px var(--ink); }
.sc .cl { display: none; }
.sc .big { font: 700 23px/1.12 var(--font-head); letter-spacing: -0.012em; text-wrap: balance; }
.sc .big small { font: 600 15px/1.2 var(--font-text); letter-spacing: 0; color: var(--ink2); }
.sc .unit { margin: 6px 0 0; padding-left: 8px; border-left: 3px solid var(--ink2); font: 700 11px/1.35 var(--font-text); letter-spacing: 0.05em; text-transform: uppercase; color: var(--ink2); }
.sc .unit span { font-weight: 500; color: var(--muted); }
.sc p { font-size: 13px; line-height: 1.4; color: var(--ink2); margin: 6px 0 0; max-width: 56ch; }
.brk { grid-column: 1 / -1; display: flex; align-items: center; gap: 12px; margin: 8px 0 2px; font: 700 12px/1.3 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink); }
.brk::before { content: ""; width: 30px; border-top: 2px dashed var(--ink); opacity: 0.55; } .brk::after { content: ""; flex: 1; border-top: 2px dashed var(--ink); opacity: 0.55; }
.scale { font-size: 12.5px; color: var(--muted); margin: 10px 0 0; }
.lt { margin-top: 16px; padding-top: 12px; border-top: 2px dashed var(--axis); }
.lt h3 { font: 700 12px/1.3 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink); margin: 0 0 8px; }
.lt table { border-collapse: collapse; font-size: 14px; font-variant-numeric: tabular-nums; }
.lt th { text-align: left; font: 700 12px/1.3 var(--font-text); color: var(--muted); padding: 4px 18px 6px 0; border-bottom: 1px solid var(--axis); }
.lt td { padding: 5px 18px 5px 0; border-bottom: 1px solid var(--grid); }
.lt td:nth-child(n+2), .lt th:nth-child(n+2) { text-align: right; }
.lt tr.all td { font-weight: 700; border-bottom: 0; }
.lt p { font-size: 13px; line-height: 1.45; color: var(--ink2); margin: 8px 0 0; max-width: 112ch; }
@media (max-width: 820px) {
  .st { display: block; }
  .st-h { display: none; }
  .stw { margin-top: 6px; padding-bottom: 4px; }
  .stw::before { display: none; }
  .sc { display: none; margin: 6px 0 0 44px; }
  .sc.has, .sc.stop { display: block; }
  .sc .cl { display: block; font: 700 11.5px/1.25 var(--font-text); letter-spacing: 0.07em; text-transform: uppercase; color: var(--muted); margin-bottom: 4px; }
  .sc .big { font-size: 21px; }
  .brk { margin: 16px 0 4px; }
}
"""


def n(x):
    return f'{x:,}'


def main():
    recs, extra = C.load(HERE / 'data.txt')
    by = {r['key']: r for r in recs}
    for r in recs:
        r['lanes'] = r['lane'].split(',')
        assert all(x in LANES for x in r['lanes']) and r['dir'] == 'neutral', r['key']
    lines = C.checked_lines(recs, extra)
    summary = C.write_and_check_quotes(HERE, lines, 'Quotations and number-bearing phrases behind the figure "The US side, step by step".')
    recs = C.number(recs)                                          # file order is date order
    assert [r['date'] for r in recs] == sorted(r['date'] for r in recs), 'the records are in date order'
    n_solid = sum(r['solid'] for r in recs); n_open = len(recs) - n_solid

    # the results call of Nov 17, 2026, in Nvidia's own transcript. It gave no reason for the stop: the transcript names
    # China in two places only, the two sentences quoted here (the count shows the search can see a hit).
    assert by['call']['date'] == by['stop']['date'] == date(2026, 11, 17) and by['call']['sid'] == by['stop']['sid']
    hearing = C.L.page('cn-o37-senate-hearing-page-b')                      # the committee's own page: testimony to download, no transcript
    assert 'transcript' not in hearing and 'downloadtestimony' in hearing
    call_text = C.L.page(by['call']['sid'])
    assert call_text.count('china') == 2 and all(C.L.squash(q) in call_text for q in (by['call']['Q'][0][0], by['stop']['Q'][0][0]))

    v = {k: by[k]['V'] for k in by}
    under = v['tenq']['pct'] / 100 * v['tenq']['dc']                                # our multiplication: 1% of $89.0 billion
    assert abs(under - 0.89) < 1e-9

    # Washington's licence table (tables/house_licence_table.tsv: the Commerce Department's 54 rows), counted here and
    # checked against the committee's own totals, which are checked phrases of the last step (its N lines)
    lt = C.table('house_licence_table.tsv')
    cnt = lambda r: int(r['chip_count'].replace(',', ''))
    st = {}
    for r in lt:
        s = st.setdefault(r['status'], [0, 0]); s[0] += cnt(r); s[1] += 1
    total = sum(cnt(r) for r in lt)
    committee_words = ' '.join(w for _, w in by['committee']['N'])

    def said(pat):
        m = re.search(pat, committee_words); assert m, pat
        return int(m.group(1).replace(',', ''))
    appr = [r for r in lt if r['status'] == 'Approved, not shipped']
    ex = {e: (sum(cnt(r) for r in appr if r['exporter'] == e), sum(r['exporter'] == e for r in appr)) for e in ('Nvidia', 'AMD')}
    assert len(lt) == 54 and total == said(r'applications to sell ([\d,]+) covered'), total
    assert st['Approved, not shipped'] == [said(r'([\d,]+) covered integrated circuits to PRC companies across'), said(r'across (\d+) license applications')]
    assert sum(x[0] for x in ex.values()) == st['Approved, not shipped'][0] and sum(x[1] for x in ex.values()) == len(appr)
    assert max(cnt(r) for r in appr) == v['cleared']['each']          # no approved application is above the 75,000 Reuters reported
    assert set(st) == {'Approved, not shipped', 'RWA', 'Submitted', 'Rejected'}, set(st)
    rwa = st['RWA']; rwa_pct = rwa[0] / total * 100
    abroad = [r for r in lt if r['location'] != 'China']
    assert all(r['status'] == 'RWA' for r in abroad) and all(r['status'] == 'RWA' for r in lt if cnt(r) > 75_000)
    n_abroad = sum(cnt(r) for r in abroad); n_big = sum(cnt(r) > 75_000 for r in lt)
    assert {r['location'] for r in abroad} == {'Malaysia', 'Indonesia', 'Thailand'}, {r['location'] for r in abroad}      # round 9: the table's ultimate location, as the core now words it
    t_row = [r for r in lt if r['date_submitted'] == '12/19/2025' and 'Tencent' in r['consignee']]
    assert len(t_row) == 1 and t_row[0]['status'] == 'Approved, not shipped'
    tencent = said(r'to export ([\d,]+) H200s to Tencent')
    # round 5 (core edit 6, point 16): neither document says whether the table's only Tencent row of Dec 19, 2025 (75,000,
    # approved) is the application of 445,000, so both readings are given, as the argument gives them (49.52% or 48.57%)
    full_pct = rwa[0] / (total - cnt(t_row[0]) + tencent) * 100        # our arithmetic: if that row is the application, counted at 445,000
    more_pct = rwa[0] / (total + tencent) * 100                         # our arithmetic: if the 445,000 is a further application
    assert round(rwa_pct) == 55 and round(full_pct, 1) == 49.5 and round(more_pct, 1) == 48.6 and cnt(t_row[0]) == 75_000, (rwa_pct, full_pct, more_pct)
    third = [r for r in lt if r['exporter'] not in ('Nvidia', 'AMD')]
    assert {r['exporter'] for r in third} == {'Semsotai USA'} and all(r['status'] == 'Submitted' for r in third)
    dc3 = [float(m.group(1)) for _, w in by['call']['N'] for m in [re.search(r'Data Center revenue for the third quarter was a record \$([0-9.]+) billion', w)] if m]
    assert len(dc3) == 1; dc3 = dc3[0]
    pct3 = v['call']['sold'] / dc3 * 100                                             # our division: $2.4 billion over $107.6 billion
    assert 2.0 < pct3 < 2.5
    days_later = (by['committee']['date'] - by['stop']['date']).days

    # what each step shows, lane by lane: (big words, yardstick, note)
    show = {
        ('post', 'allowed'): ('H200 sales allowed', 'a decision · no number of chips', 'to “approved customers in China”, in the President’s words.'),
        ('licences', 'allowed'): ('Licences granted', 'licences · H200 · no number given', 'for what Nvidia’s filing calls “small amounts of H200 products”.'),
        ('lutnick', 'out'): ('None sold yet', 'H200 chips sold', '“So we have not sold them chips as of yet.” He calls it his understanding.'),
        ('cleared', 'allowed'): (f'about {v["cleared"]["firms"]} firms, up to {n(v["cleared"]["each"])} each', 'firms, and a ceiling per firm · H200',
                                 f'By this report of May 14, 2026, from unnamed people. In Washington’s own table (step {by["committee"]["n"]}) no approved application is above {n(v["cleared"]["each"])}.'),
        ('cleared', 'out'): ('No delivery', 'H200 deliveries', '“not a single delivery has been made so far”'),
        ('call1', 'out'): ('No revenue yet', 'US dollars · licensed H200 sales', '“we have yet to generate any revenue, and we are uncertain whether any imports will be allowed into the country”'),
        ('kessler', 'out'): ('Shipments have begun', 'H200 shipments · no number given', '“minimal exports of any H200s to China so far”; the number was “very few”.'),
        ('ft', 'allowed'): (f'up to {n(v["ft"]["each"])} each', 'a ceiling per firm · H200', f'A higher ceiling than the {n(v["cleared"]["each"])} reported in May. The two come from different reports.'),
        ('ft', 'out'): (f'about {n(v["ft"]["got"])} each, to two buyers', 'chips received · H200 · ByteDance and Tencent', 'received “in recent weeks”, the report says.'),
        ('tenq', 'out'): (f'less than {v["tenq"]["pct"]}% of Data Center revenue', 'a share of Nvidia’s revenue · H200 shipments under the licences',
                          f'Data Center revenue that quarter was ${v["tenq"]["dc"]} billion, so less than ${under:.2f} billion (our multiplication). Nvidia: “a fraction of the allowed shipments”.'),
        ('call', 'out'): (f'${v["call"]["sold"]} billion sold', 'US dollars · licensed Hopper products, the H200 among them',
                          f'“Q3 sales of licensed Hopper Data Center products to China was $2.4 billion.” About {pct3:.0f}% of that quarter’s Data Center revenue of ${dc3} billion (our division). No count of chips is given.'),
        ('stop', 'out'): ('Nvidia says shipments have stopped', '', '“we are no longer shipping licensed Hopper Data Center products to China”. Nvidia gave no reason.'),
        ('committee', 'allowed'): (f'{n(st["Approved, not shipped"][0])} approved', 'chips in licence applications · Nvidia’s H200 and AMD’s MI325X together',
                                   f'In {st["Approved, not shipped"][1]} applications: Nvidia {n(ex["Nvidia"][0])} in {ex["Nvidia"][1]}, AMD {n(ex["AMD"][0])} in {ex["AMD"][1]}. '
                                   f'The table holds {len(lt)} applications for {n(total)} chips; each status is in the table below.'),
        ('committee', 'out'): ('Not shipped, as of May 11, 2026', 'licence applications · their status', 'Every approved application is marked “Approved, not shipped”.'),
    }
    for (k, lane) in show: assert lane in by[k]['lanes'], (k, lane)
    assert sum(len(r['lanes']) for r in recs) == len(show)

    g = ['<div class="st" role="table" aria-label="Dated steps on the US side">',
         '<div class="st-h corner">Date and who says it</div>']
    g += [f'<div class="st-h"><b>{C.T(LANES[k][0])}</b><span>{C.T(LANES[k][1])}</span></div>' for k in LANES]
    for i, r in enumerate(recs):
        if r['key'] == 'committee':
            g.append(f'<div class="brk">Made public {C.WORDS[days_later]} days later: the licence record, looking back</div>')
        pos = ' first' if i == 0 else (' last' if i == len(recs) - 1 else '')
        lab = f'{r["n"]}. {r["when"]}: {C.smart(r["T"])}. {C.KIND_WORDS[r["kind"]]}'
        g.append(f'<div class="stw{pos}"><a class="pinlink" href="#r{r["n"]}" data-n="{r["n"]}" data-tip="1" aria-label="{C.esc(lab, quote=True)}">{C.pin(r)}<b>{C.esc(r["when"])}</b><span>{C.T(r["T"])}</span></a></div>')
        for lane in LANES:
            if lane in r['lanes']:
                big, unit, note = show[(r['key'], lane)]
                cls = 'stop' if r['key'] == 'stop' else 'has'
                g.append(f'<div class="sc {cls}" role="cell"><div class="cl">{C.T(LANES[lane][0])}</div><div class="big">{big}</div>' + (f'<div class="unit"><span>Counted in</span> {unit}</div>' if unit else '') + f'<p>{note}</p></div>')
            else:
                g.append('<div class="sc" role="cell"></div>')
    g.append('</div>')
    names = {'Approved, not shipped': 'Approved, not shipped', 'RWA': 'Returned without action', 'Submitted': 'Submitted', 'Rejected': 'Rejected'}
    trs = ''.join(f'<tr><td>{names[k]}</td><td>{n(st[k][0])}</td><td>{st[k][1]}</td></tr>' for k in ('Approved, not shipped', 'RWA', 'Submitted', 'Rejected'))
    trs += f'<tr class="all"><td>All</td><td>{n(total)}</td><td>{len(lt)}</td></tr>'
    g.append(f"""   <div class="lt">
    <h3>Step {by['committee']['n']}: Washington’s table by status, May 11, 2026</h3>
    <table><thead><tr><th>Status</th><th>Chips</th><th>Applications</th></tr></thead><tbody>{trs}</tbody></table>
    <p>Our sums of the table’s {len(lt)} rows; they match the committee’s own totals. Nvidia’s and AMD’s chips are added together, as in the table; a third exporter, Semsotai USA, has {n(sum(cnt(r) for r in third))} chips in {len(third)} applications, all still submitted.
    Returned without action is {rwa_pct:.0f}% of the chips in the applications the summary records, among them every application above 75,000 chips ({C.WORDS[n_big]}) and every one whose ultimate location is Malaysia, Indonesia or Thailand ({n(n_abroad)} chips). The table gives no reasons.
    The committee says the summary does not show every application in full; for example, Nvidia applied on Dec 19, 2025 “to export 445,000 H200s to Tencent”. The table’s only Tencent row of that date is for {n(cnt(t_row[0]))}, approved, and neither document says whether it is that application. If it is, counted at 445,000, the share returned would be {full_pct:.1f}%; if the 445,000 is a further application and was not returned without action, {more_pct:.1f}% (our arithmetic).</p>
   </div>""")

    figure = f"""
  <section class="care" style="margin-top:0">
   <h2>Read this first: these numbers do not count the same things</h2>
   <p>No step is a part of the step before it, and none can be subtracted from another. Five different yardsticks are in use:</p>
   <div class="ys">
    <div><b>Chips in licence applications</b>Nvidia’s H200 and AMD’s MI325X together. Washington’s licence table, status of May 11, 2026, made public by the House Foreign Affairs Committee.</div>
    <div><b>Firms, and a ceiling per firm</b>The H200 only. Press reports citing unnamed people.</div>
    <div><b>Chips received</b>The H200, by two named buyers. A press report citing unnamed people.</div>
    <div><b>A share of revenue</b>Nvidia’s Data Center revenue in one quarter. Its filing.</div>
    <div><b>US dollars</b>Licensed Hopper products sold in one quarter. Nvidia’s results calls.</div>
   </div>
  </section>
  <section class="card gap" id="steps">
{chr(10).join(g)}
   <p class="scale">The steps are in date order; the spacing is not to scale, and no bar is drawn because the numbers share no scale. A quarter’s figure sits at the date it was made public.</p>
  </section>
  <section class="care">
   <h2>Read with care</h2>
   <ul>
    <li><b>Sold or shipped “to China” is not the same as arrived in the mainland.</b> The August report says small batches “have been allowed to enter mainland China” and also that “Beijing wants them to keep the hardware outside mainland China”. Where the chips sold later are now is not known.</li>
    <li><b>The licence table is Washington’s own record, looking back.</b> It gives each application’s status on May 11, 2026, and was made public on Nov 19, 2026 by the House Foreign Affairs Committee, by unanimous consent. An application names a data-centre operator or ultimate consignee; it is not an order, and an approval there is Washington’s licence, not Beijing’s.</li>
    <li><b>This is the American side only.</b> Why so little went out is a separate question: Nvidia’s filing says such sales “were restricted by the PRC government”, and the Commerce Secretary said the Chinese central government had not let the companies buy.</li>
    <li><b>The last quarter’s filing is not out.</b> Nvidia’s quarterly report (Form 10-Q) for the quarter ended Oct 25, 2026 was not yet filed when looked for on Nov 23, 2026. Its commentary on the quarter says: “We plan to file our 10-Q in the coming weeks.” The $2.4 billion is from its results call and that commentary.</li>
    <li>Open marks rest on unnamed people. The two ceilings ({n(v["cleared"]["each"])} and {n(v["ft"]["each"])} a firm) come from two different reports. Washington’s table states no ceiling; no approved application in it is above {n(v["cleared"]["each"])}.</li>
    <li>The H200 is, in Reuters’s words, “Nvidia’s second-most powerful AI chip”. Hopper is the chip family it belongs to. BIS is the Commerce Department’s Bureau of Industry and Security; by the committee’s summary the approvals were BIS’s.</li>
   </ul>
  </section>"""

    key = f"""   <ul class="key">
    <li><i class="p solid neutral" aria-hidden="true">1</i><span><b>Filled:</b> on the record (an official, a filing, a government record, a named executive). {n_solid} records</span></li>
    <li><i class="p hollow neutral" aria-hidden="true">1</i><span><b>Open:</b> a press report citing unnamed people. {n_open} records</span></li>
    <li><span>Marks are grey: this figure is about Washington and Nvidia, not about which way Beijing pulled.</span></li>
   </ul>"""

    below = C.records_block(recs, 'One line for each numbered step: its date, our summary, the page\'s own words, and the source. Point at a step\'s number to read the words there.')
    page = C.page(
        title='US Licences And Shipments',
        eyebrow='United States · licensed Nvidia chip sales to China · December 2025 to November 2026',
        h1='Washington said yes in December 2025. Shipments began in mid‑2026. In November Nvidia said they had stopped.',
        deck=f'{len(recs)} dated steps on the American side: what Washington allowed, and what officials, Nvidia and the press say went out. '
             'In April and May 2026 nothing had been sold or delivered. By July an official called exports minimal. In November Nvidia gave its sales for the quarter and said it was no longer shipping. It gave no reason. '
             f'Washington’s own table, made public in November, shows {n(st["Approved, not shipped"][0])} of Nvidia’s and AMD’s chips approved by May 11, 2026, each approved application marked not shipped, and {rwa_pct:.0f}% of the chips in the applications its summary records returned without action.',
        key=key, figure=figure, below=below, css=CSS,
        tipjson=C.tips(recs, lambda r: ' and '.join(LANES[x][0].lower() for x in r['lanes'])))
    out = C.finish(HERE, NAME, page, lines)
    C.records_tsv(HERE / 'records.tsv', recs, [('lane', lambda r: '; '.join(LANES[x][0] for x in r['lanes'])), ('numbers_shown', lambda r: '; '.join(f'{k}={x}' for k, x in r['V'].items()))])
    print(f'steps {len(recs)}; on the record {n_solid}, press reports {n_open}; licence table {len(lt)} rows, {n(total)} chips, by status {st}, approved by exporter {ex}, '
          f'returned {rwa_pct:.1f}% ({full_pct:.1f}% if the Tencent row is the 445,000 application, {more_pct:.1f}% if that is a further one); our arithmetic: under ${under:.2f} billion, third-quarter share {pct3:.2f}%; {summary}')
    if '--png' in sys.argv:
        C.export_png(out, [('#figure', HERE / f'{NAME}.png')])


main()
