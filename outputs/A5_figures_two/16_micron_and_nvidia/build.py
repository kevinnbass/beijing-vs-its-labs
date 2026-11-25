"""Build the figure "Micron and Nvidia side by side": what Beijing published in each case.

Run: python3 -I build.py                                   checks every quotation, writes the page and records.tsv
     python3 -I build.py --png   the same, then exports micron_and_nvidia.png
Reads data.txt (../common.py explains the format). Writes quotes.tsv from it and runs scripts/cn_has.py on that file; if the
checker does not pass, nothing else is written. Counts on the page are counted here from data.txt.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as C   # noqa: E402

NAME = 'micron_and_nvidia'
ROWS = ('order', 'published', 'unpublished')

CSS = """
/* Layout: headline and key; a table of three questions (rows) asked of two cases (columns); read with care; the records. */
.cmp { display: grid; grid-template-columns: minmax(150px, 0.62fr) minmax(0, 1fr) minmax(0, 1.5fr); gap: 8px 10px; }
.cmp-h { padding: 2px 4px 8px; border-bottom: 3px solid var(--away); }
.cmp-h.corner { border-color: transparent; }
.cmp-h b { display: block; font: 700 26px/1.1 var(--font-head); letter-spacing: -0.01em; }
.cmp-h span { display: block; font: 700 12px/1.3 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin-bottom: 3px; }
.q { padding: 12px 10px 10px 0; align-self: start; }
.q b { display: block; font: 700 16px/1.25 var(--font-text); text-wrap: balance; }
.q span { display: block; font-size: 12.5px; line-height: 1.35; color: var(--muted); margin-top: 4px; }
.cell { border-radius: 11px; padding: 11px 14px 12px; min-width: 0; background: var(--slot); }
.cell .cl { display: none; }
.cell.has { background: var(--away-tint); }
.cell.none { background: transparent; box-shadow: inset 0 0 0 2px var(--axis); background-image: repeating-linear-gradient(135deg, var(--slot) 0 6px, transparent 6px 14px); }
.verdict { font: 700 30px/1.05 var(--font-head); letter-spacing: -0.015em; margin: 1px 0 6px; }
.cell p { font-size: 14px; line-height: 1.42; color: var(--ink2); margin: 6px 0 0; max-width: 62ch; }
.cell p b { color: var(--ink); font-weight: 600; }
.cell .zh { font-size: 15px; color: var(--ink); margin: 8px 0 0; }
.cell .zh span { color: var(--ink2); font-size: 14px; }
.marks { display: grid; grid-template-columns: 1fr; gap: 0 18px; margin-top: 2px; }
@media (min-width: 1040px) { .marks.two { grid-template-columns: 1fr 1fr; } }
.quiet { font-size: 14px; color: var(--muted); margin: 0; }
.tally { font: 700 12px/1.3 var(--font-text); letter-spacing: 0.06em; text-transform: uppercase; color: var(--ink2); margin: 0 0 4px; }
@media (max-width: 820px) {
  .cmp { display: block; }
  .cmp-h { display: none; }
  .q { padding: 14px 0 2px; border-top: 2px solid var(--axis); margin-top: 12px; }
  .q:first-of-type { border-top: 0; margin-top: 0; padding-top: 0; }
  .cell { margin-top: 8px; }
  .cell .cl { display: block; font: 700 11.5px/1.25 var(--font-text); letter-spacing: 0.07em; text-transform: uppercase; color: var(--ink2); margin-bottom: 5px; }
  .verdict { font-size: 26px; }
}
"""


def main():
    recs, extra = C.load(HERE / 'data.txt')
    for r in recs:
        r['rows'] = r['row'].split(',')
        assert r['case'] in ('micron', 'nvidia') and all(x in ROWS for x in r['rows']) and r['dir'] == 'away', r['key']
    lines = C.checked_lines(recs, extra)
    summary = C.write_and_check_quotes(HERE, lines, 'Quotations and number-bearing phrases behind the figure "Micron and Nvidia side by side".')
    recs = C.number(recs, order=lambda r: (r['case'] != 'micron', min(ROWS.index(x) for x in r['rows']), r['date']))
    cell = {(c, w): sorted([r for r in recs if r['case'] == c and w in r['rows']], key=lambda r: r['date']) for c in ('micron', 'nvidia') for w in ROWS}
    # the finding, checked against the data: Micron has a published order; no Nvidia record is one
    assert len(cell[('micron', 'order')]) == 1 and not cell[('nvidia', 'order')] and not cell[('micron', 'unpublished')]
    m = cell[('micron', 'order')][0]
    pub = cell[('nvidia', 'published')]; unp = cell[('nvidia', 'unpublished')]
    assert all(r['solid'] for r in pub)
    n_press = sum(not r['solid'] for r in unp); n_fil = sum(r['solid'] for r in unp)
    n_solid = sum(r['solid'] for r in recs); n_open = len(recs) - n_solid
    words = C.WORDS
    # the finance ministry's purchase bar by name (issued Jun 22, 2026): its list of 46 American firms names none of the chip makers searched for.
    # Checked in the list's saved text; the control is a defence firm's name, which must be found. Round 9 (core edit 8b): the page says "none of the
    # chip makers searched for", not "no chip maker" (a negative over every maker), as the record and the argument now say; the count is made here.
    lst = C.L.page('cn-le14-mof-us-firms-list-20260622')
    MAKERS = [('Nvidia', ('nvidia', '英伟达')), ('Micron', ('micron', '美光')), ('Intel', ('intel', '英特尔')), ('Qualcomm', ('qualcomm', '高通')),
              ('AMD', ('amd', 'advancedmicro', '超威')), ('Broadcom', ('broadcom', '博通')), ('Texas Instruments', ('texasinstruments', '德州仪器'))]
    makers = [w for _, ws in MAKERS for w in ws]
    assert 'lockheedmartin' in lst and not [m for m in makers if m in lst], [m for m in makers if m in lst]
    maker_names = ', '.join(n for n, _ in MAKERS[:-1]) + ' and ' + MAKERS[-1][0]
    # state and Party media (tables/state_media_items.tsv): the items that only warn about Nvidia's chips, and their dates
    sm = C.table('state_media_items.tsv')
    warns = sorted(C.date.fromisoformat(r['date']) for r in sm if r['stance'] == 'warns')
    # round 5 (core edit 6): rows 43 to 75 were added (found by searches and links; after Sept 24, 2025 a sample, not a census)
    win = [d for d in warns if d <= C.date(2025, 9, 24)]; late = [r for r in sm if r['stance'] == 'warns' and C.date.fromisoformat(r['date']) > C.date(2025, 9, 24)]
    assert (len(sm), len(warns), len(win), len(late)) == (75, 19, 16, 3), (len(sm), len(warns), len(win))
    assert all(r['outlet'].startswith('Global Times') and r['date'].startswith('2026') for r in late), late

    figure = f"""
  <section class="card" id="cmp">
   <div class="cmp">
    <div class="cmp-h corner"></div>
    <div class="cmp-h"><span>2023</span><b>Micron</b></div>
    <div class="cmp-h"><span>2024 to 2026</span><b>Nvidia</b></div>

    <div class="q"><b>Did Beijing publish a text saying buyers should stop?</b><span>a conclusion, a decision or a notice that names the company’s products</span></div>
    <div class="cell has"><div class="cl">Micron · 2023</div>
     <div class="verdict">Yes, published</div>
     {C.mark(m, 'the review office’s conclusion')}
     <p class="zh">“应停止采购美光公司产品” <span>(should stop buying Micron’s products)</span></p>
     <p><b>Addressed to buyers:</b> “关键信息基础设施的运营者” (operators of critical information infrastructure).</p>
     <p><b>Issued by</b> the cyberspace regulator’s review office (the Cybersecurity Review Office), and published on the regulator’s site.</p>
    </div>
    <div class="cell none"><div class="cl">Nvidia · 2024 to 2026</div>
     <div class="verdict">None found</div>
     <p><b>in the 82 policy pages read.</b> A text of this kind could have been found: the Micron conclusion is among those pages.</p>
     <p>When the finance ministry issued a purchase bar by name, on Jun 22, 2026, “不得采购46家美国企业（不包括在华美资企业）生产的产品” (government buyers may not buy products made by 46 American firms, leaving out American-funded firms in China), its list named none of the {words[len(MAKERS)]} chip makers searched for ({maker_names}, in English and in Chinese).</p>
    </div>

    <div class="q"><b>What else did it publish against the company?</b><span>acts the state body announced itself</span></div>
    <div class="cell has"><div class="cl">Micron · 2023</div>
     {C.mark(m, 'the same text gives the review’s result')}
     <p>“不予通过网络安全审查” (does not pass the cybersecurity review), “按照《网络安全法》等法律法规” (under the Cybersecurity Law and other laws and regulations).</p>
    </div>
    <div class="cell has"><div class="cl">Nvidia · 2024 to 2026</div>
     <div class="marks">{''.join(C.mark(r) for r in pub)}</div>
     <p><b>Addressed to Nvidia itself:</b> it is investigated, and it must explain and hand in proof. None of the {words[len(pub)]} tells a buyer to stop.</p>
     <p><b>State media warned in public.</b> Of {len(sm)} state and Party media items on Nvidia chips found, {len(warns)} only warn about them: {len(win)} dated {C.fmt(win[0])} to {C.fmt(win[-1])}, and {words[len(late)]} later ones in Global Times in 2026 (the items after September 2025 are what two rounds of searches found, a sample and not a full count). They warn and urge; none forbids buying. They are not drawn here.</p>
    </div>

    <div class="q"><b>Where does an instruction not to buy appear without being published?</b><span>press reports citing unnamed people, and what companies told the US securities regulator</span></div>
    <div class="cell"><div class="cl">Micron · 2023</div>
     <p class="quiet">Not searched for in this project. The words were in the published conclusion.</p>
    </div>
    <div class="cell has"><div class="cl">Nvidia · 2024 to 2026</div>
     <p class="tally">{n_press} press reports citing unnamed people · {n_fil} company filings</p>
     <div class="marks two">{''.join(C.mark(r) for r in unp)}</div>
    </div>
   </div>
  </section>
  <section class="care">
   <h2>Read with care</h2>
   <ul>
    <li><b>The comparison cuts both ways.</b> Beijing can publish such a text and, for Nvidia, none was found; or its way with Nvidia was guidance it did not publish, as press reports and company filings say. The figure cannot tell these apart.</li>
    <li><b>None found is a statement about what was read:</b> the 82 policy pages read for this project. It is not a claim that no such text exists.</li>
    <li>The Micron conclusion came from the Cybersecurity Review Office, which sits in the cyberspace regulator: “网络安全审查办公室设在国家互联网信息办公室” (the office is set up in the Cyberspace Administration). It speaks to operators of critical information infrastructure, not to every buyer, and it is not about Nvidia.</li>
    <li>Alibaba’s filing does not name Nvidia: it says “certain chips”. Nvidia’s own reports changed their words over time: from Nov 19, 2025 the Chinese government “restricted customers from purchasing, importing, or using our data center products”; from Feb 25, 2026, “discouraged customers from purchasing, importing, or using our data center products”. From November 2025 the same reports also say Nvidia is “already effectively foreclosed from the China market by U.S. export controls”.</li>
    <li>Open marks rest on unnamed people. In the answers found, Beijing’s spokespeople confirmed none of them: “我不了解你提到的情况” (I am not aware of what you mention), said the foreign ministry on Aug 13, 2025; asked about another report on Dec 10, 2025, it said “具体情况建议向中方主管部门询问” (for the details, ask the competent Chinese departments).</li>
    <li>The marks under Nvidia are a selection, not a count of everything reported. English renderings of Chinese are ours, not official translations.</li>
   </ul>
  </section>"""

    key = f"""   <ul class="key">
    <li><i class="p solid away" aria-hidden="true">1</i><span><b>Filled:</b> on the record (a government document or a company filing). {n_solid} records</span></li>
    <li><i class="p hollow away" aria-hidden="true">1</i><span><b>Open:</b> a press report citing unnamed people. {n_open} records</span></li>
    <li><span>All marks are orange: every act here points away from the foreign chip.</span></li>
   </ul>"""

    below = C.records_block(recs, 'One line for each numbered mark: the date of the act where the page gives it, otherwise the date of the report; our summary; '
                                  'the page\'s own words; the source. Point at a mark in the figure to read the words there.')
    page = C.page(
        title='Micron And Nvidia',
        eyebrow='China · two foreign chip makers · what Beijing published · 2023 to 2026',
        h1='For Micron, Beijing published a conclusion: buyers should stop. For Nvidia, a case and a summons.',
        deck=f'What Beijing put in writing in two cases. In 2023 the cyberspace regulator’s review office published its conclusion that Micron’s products failed a security review, and that operators of critical infrastructure should stop buying them. '
             f'From 2024 to 2026 the published acts found about Nvidia were an antitrust case and a summons, and state media warned about its chips in public. An instruction not to buy Nvidia chips was found only in press reports citing unnamed people and in what companies told the US securities regulator.',
        key=key, figure=figure, below=below, css=CSS,
        tipjson=C.tips(recs, lambda r: 'Micron, 2023' if r['case'] == 'micron' else 'Nvidia, 2024 to 2026'))
    out = C.finish(HERE, NAME, page, lines)
    C.records_tsv(HERE / 'records.tsv', recs, [('case', lambda r: r['case']), ('row', lambda r: r['row'])])
    print(f'records {len(recs)}: Micron {sum(r["case"] == "micron" for r in recs)}, Nvidia published {len(pub)}, Nvidia not published {len(unp)} ({n_press} press, {n_fil} filings); {summary}')
    if '--png' in sys.argv:
        C.export_png(out, [('#figure', HERE / f'{NAME}.png')])


main()
