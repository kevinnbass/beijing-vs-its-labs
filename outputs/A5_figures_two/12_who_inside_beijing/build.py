"""Build the figure "Who inside Beijing": state bodies (rows) against kinds of act (columns).

Run: python3 -I build.py                                   checks every quotation, writes the page and records.tsv
     python3 -I build.py --png   the same, then exports who_inside_beijing.png
Reads data.txt (the records; ../common.py explains the format). Writes quotes.tsv from it and runs scripts/cn_has.py on
that file; if the checker does not pass, nothing else is written. Counts on the page are counted here from data.txt and
from the project's tables (tables/state_media_items.tsv, provinces_31.tsv, chip_evaluations.tsv).
Round 4 (Nov 23, 2026): follows the core figure's panel "Inside Beijing: not one actor": the same bodies on each side,
the antitrust case against Nvidia the company drawn apart from the grid.
The page is a build product: a rebuild replaces it. Before it is called done: scripts/render_and_look.py.
"""
import re, sys
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as C   # noqa: E402

NAME = 'who_inside_beijing'
BANDS = [  # band title, [(row key, name, what it is)]; ordered so that the bodies seen only on the "away" side come first
    ('Security and planning', [('cac', 'Cyberspace regulator', 'Cyberspace Administration of China'),
                               ('mss', 'Security ministry', 'Ministry of State Security'),
                               ('ndrc', 'State planner', 'National Development and Reform Commission (NDRC)')]),
    ('Customs, rule-setters and state media', [('customs', 'Customs', 'customs authorities and their officers at the ports'),
                                               ('rules', 'Purchase-rule and evaluation bodies', 'finance and industry ministries, State Council’s office, evaluation centres; the purchase rules apply to government purchasing only'),
                                               ('media', 'State media', 'People’s Daily’s commentary account; an account of the state broadcaster')]),
    ('Premier and vice premiers', [('ding', 'Vice Premier Ding Xuexiang', 'heads the chip committee, as the Wall Street Journal describes it'),
                                   ('li', 'Premier Li Qiang', 'received American business leaders in May 2026'),
                                   ('he', 'Vice Premier He Lifeng', 'received Nvidia’s chief executive in April 2025')]),
    ('On both sides', [('miit', 'Industry ministry', 'Ministry of Industry and Information Technology')]),
    ('Commerce', [('mofcom', 'Commerce ministry', 'Ministry of Commerce')]),
    ('No body named in the report', [('nobody', '“Beijing”, “authorities”, “officials”', 'reports that say the state acted without naming the body')]),
]
APART = ('samr', 'Market regulator', 'State Administration for Market Regulation')       # the antitrust case: against Nvidia the company, drawn apart
COLS = [  # key, direction, title, what it covers
    ('acted', 'away', 'Summoned Nvidia, or warned in public', 'acts and texts it published itself'),
    ('told', 'away', 'Reported: told companies not to buy', 'or to use home-made chips; or held chips at the border'),
    ('rules', 'away', 'Rules or guidance favouring home-made chips', 'purchase rules, a list, guidance'),
    ('welcomed', 'toward', 'Welcomed Nvidia, or spoke for access', 'in public: welcomes, protests at US curbs, help for computing abroad'),
    ('approved', 'toward', 'Reported: approved purchases', 'with conditions; or let chips in'),
]
# Round 11 (ROUND11.md, thing 2): the two columns hold press reports (and, in 'told', one company's filing): their heads carry the report.
PHONE_LABEL = {'told': 'Reported: told companies not to buy, or held chips at the border', 'approved': 'Reported: approved purchases, or let chips in'}     # on a phone the column's second line is not shown
ROWKEYS = [k for _, rows in BANDS for k, _, _ in rows]
ROWNAME = {k: n for _, rows in BANDS for k, n, _ in rows}
ROWNAME[APART[0]] = APART[1]
COLKEYS = [c[0] for c in COLS]
COLNAME = {c[0]: c[2] for c in COLS}
COLNAME['case'] = 'The antitrust case against Nvidia the company (set apart)'

CSS = """
/* Layout: headline and key; the grid (bodies down, kinds of act across); how one newspaper described the split; read with care; the records. */
.g { display: grid; grid-template-columns: minmax(168px, 0.95fr) 1.05fr 1.4fr 1.3fr 1.15fr 1.2fr; gap: 4px 5px; align-items: stretch; }
.g-head, .r { display: contents; }
.side { display: flex; align-items: center; gap: 8px; font: 700 12px/1.2 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink);
  padding: 0 2px 7px; border-bottom: 3px solid; }
.side.away { grid-column: 2 / span 3; border-color: var(--away); } .side.toward { grid-column: 5 / span 2; border-color: var(--toward); margin-left: 9px; }
.k-welcomed { margin-left: 9px; }
.corner { grid-column: 1; }
.ch { padding: 6px 8px 8px; }
.ch b { display: block; font: 700 14px/1.22 var(--font-text); text-wrap: balance; }
.ch span { display: block; font-size: 12px; line-height: 1.3; color: var(--muted); margin-top: 2px; }
.ch.first { align-self: end; font: 700 12px/1.2 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); padding-left: 0; }
.band { grid-column: 1 / -1; font: 700 12px/1.2 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); padding: 9px 0 1px; border-top: 1px solid var(--axis); margin-top: 5px; }
.band.b0 { margin-top: 0; }
.rh { padding: 7px 10px 7px 0; align-self: center; }
.rh b { display: block; font: 700 15px/1.22 var(--font-text); }
.rh span { display: block; font-size: 12px; line-height: 1.3; color: var(--muted); margin-top: 2px; }
.c { background: var(--slot); border-radius: 9px; padding: 4px 9px; min-height: 46px; display: flex; flex-direction: column; justify-content: center; min-width: 0; }
.c.has.away { background: var(--away-tint); } .c.has.toward { background: var(--toward-tint); }
.c .cl { display: none; }
.apart { grid-column: 2 / -1; background: var(--slot); border-radius: 9px; padding: 6px 12px 9px; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.55fr); gap: 4px 22px; align-items: start; box-shadow: inset 0 0 0 1.5px var(--axis); }
.apart .am { display: flex; flex-direction: column; }
.apart p { margin: 3px 0 0; font-size: 13px; line-height: 1.42; color: var(--ink2); }
.apart p b { color: var(--ink); font-weight: 600; }
.split { margin: 16px 0 0; padding-top: 13px; border-top: 1px solid var(--axis); display: grid; grid-template-columns: 1fr; gap: 6px 26px; font-size: 14.5px; color: var(--ink2); }
.split h3 { font: 700 12px/1.3 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin: 2px 0 0; }
.split p { margin: 0; max-width: 100ch; }
.split b { color: var(--ink); font-weight: 600; }
@media (min-width: 900px) { .split { grid-template-columns: 250px 1fr; } }
.who { font-weight: 700; font-size: 14.5px; }
@media (max-width: 820px) {
  .g { display: block; }
  .g-head { display: none; }
  .r { display: block; padding: 10px 0 6px; border-top: 1px solid var(--grid); }
  .band { border-top: 2px solid var(--axis); padding-top: 12px; margin-top: 10px; }
  .band + .r { border-top: 0; padding-top: 4px; }
  .band.b0 { border-top: 0; margin-top: 0; padding-top: 0; }
  .k-welcomed { margin-left: 0; }
  .rh { padding: 0 0 4px; }
  .c { display: none; }
  .c.has { display: block; margin-top: 6px; padding: 7px 10px 6px; }
  .c .cl { display: flex; align-items: center; gap: 7px; font: 700 11.5px/1.25 var(--font-text); letter-spacing: 0.06em; text-transform: uppercase; color: var(--ink2); margin-bottom: 3px; }
  .c .cl i.sw { width: 9px; height: 9px; }
  .apart { display: block; margin-top: 6px; }
  .apart p { margin-top: 6px; }
}
"""


def main():
    recs, extra = C.load(HERE / 'data.txt')
    # Core edit 8 (Nov 25, 2026): the words behind Zhejiang's share, which the note on published orders names with its scope. They are checked here and
    # NOT held in data.txt, because atlas figure 11 (scripts/cn_atlas_11_who_inside_beijing.py) reads data.txt and would take every "!" line there as
    # one of its own sources; the province note is this page's alone.
    extra += [('cn-ga31-cndocs-52', '到2030年，浙江信息通信行业算力规模达150EFLOPS，国产化算力占比超60%'),
              ('cn-ga31-cndocs-52', '重点工程4:算力网络一体化提升工程'),
              ('cn-ga31-cndocs-52', '省通信管理局省发展改革委关于印发《浙江省信息通信业发展“十五五”规划》的通知'),
              # Round 11: the question of Nov 9, 2026 names the report ("the 600,000 chips Reuters reported in Hong Kong", the core's short form)
              ('cn-acts-mfa-20261109', '路透社报道，约60万枚英伟达先进人工智能芯片存放在香港')]
    for r in recs:
        r['rows'] = r['row'].split(',')
        if r['col'] == 'case':
            assert r['rows'] == [APART[0]] and r['dir'] == 'away', r['key']; continue
        assert all(k in ROWKEYS for k in r['rows']) and r['col'] in COLKEYS and r['dir'] in ('away', 'toward'), r['key']
        assert r['dir'] == dict((c[0], c[1]) for c in COLS)[r['col']], f"{r['key']}: direction does not match its column"
    # Round 11 (ROUND11.md, thing 2): every press record's label carries the report ("reported", or the outlet named in it)
    bare = [r['key'] for r in recs if r['kind'] == 'press' and not re.search(r'\breported\b|\breports\b|^Reuters|Financial Times|Wall Street Journal', r['T'])]
    assert not bare, f'press labels without the report: {bare}'
    lines = C.checked_lines(recs, extra)
    summary = C.write_and_check_quotes(HERE, lines, 'Quotations and number-bearing phrases behind the figure "Who inside Beijing".')
    order = ROWKEYS[:-1] + [APART[0], ROWKEYS[-1]]                 # the case apart sits above the row of reports that name no body
    recs = C.number(recs, order=lambda r: (min(order.index(k) for k in r['rows']), (COLKEYS + ['case']).index(r['col']), r['date']))

    n_solid = sum(r['solid'] for r in recs); n_open = len(recs) - n_solid
    cell = {(rk, ck): [] for rk in ROWKEYS for ck in COLKEYS}
    case = sorted([r for r in recs if r['col'] == 'case'], key=lambda r: r['date'])
    for r in recs:
        if r['col'] == 'case': continue
        for rk in r['rows']: cell[(rk, r['col'])].append(r)
    for v in cell.values(): v.sort(key=lambda r: r['date'])
    named = ROWKEYS[:-1]                                           # every row but "no body named"
    away_rows = [rk for rk in named if any(cell[(rk, ck)] for ck in ('acted', 'told', 'rules'))]
    toward_rows = [rk for rk in named if any(cell[(rk, ck)] for ck in ('welcomed', 'approved'))]
    both = [rk for rk in named if rk in away_rows and rk in toward_rows]
    assert (len(away_rows), len(toward_rows), both) == (8, 4, ['miit']) and len(case) == 2, (away_rows, toward_rows, both)      # as the core figure's panel has it

    # counts taken from the project's tables
    sm = C.table('state_media_items.tsv'); st = Counter(r['stance'] for r in sm)
    warns = sorted(date.fromisoformat(r['date']) for r in sm if r['stance'] == 'warns')
    # round 5 (core edit 6): rows 43 to 75 were added (found by searches and links; after Sept 24, 2025 a sample, not a census).
    # The warnings up to Sept 24, 2025 (the burst after the summons) and the later ones, as the core figure's state_media() counts them.
    win = [d for d in warns if d <= date(2025, 9, 24)]; late = [r for r in sm if r['stance'] == 'warns' and date.fromisoformat(r['date']) > date(2025, 9, 24)]
    iso = sorted(date.fromisoformat(r['date']) for r in sm if re.fullmatch(r'\d{4}-\d\d-\d\d', r['date']))
    # core edit 8 (Nov 25, 2026): the recount of the table by its written rule (second coders and a third reader): 19 items only warn, 16 of them up to
    # Sept 24, 2025, 3 later, 7 mixed; (75, 14, 11, 3, 8) before it.
    assert (len(sm), len(warns), len(win), len(late), st['mixed']) == (75, 19, 16, 3, 7), (len(sm), st)
    assert all(r['outlet'].startswith('Global Times') and r['date'].startswith('2026') for r in late), late
    media_ids = {r['saved_id'] for r in sm if r['stance'] == 'warns'}
    assert all(r['sid'] in media_ids for r in recs if 'media' in r['rows']), 'a state-media mark is not one of the census\'s warning items'
    pr = Counter(r['result'] for r in C.table('provinces_31.tsv')); assert sum(pr.values()) == 31, pr
    zj = [r for r in C.table('provinces_31.tsv') if r['government'] == 'Zhejiang']      # core edit 8: the note names Zhejiang's share with its scope; it must be a share in the table, from the sector plan
    assert pr['share'] == 9 and len(zj) == 1 and zj[0]['result'] == 'share' and zj[0]['saved_ids'].split()[0] == 'cn-ga31-cndocs-52', (pr, zj)
    ev = [r for r in C.table('chip_evaluations.tsv') if '人工智能训练推理芯片' in r['category'] and not r['cells'].startswith('序号')]
    per_list = Counter(r['page_date'] for r in ev)
    assert per_list == {'2026-05-26': 9, '2026-09-20': 2}, per_list   # the record of the evaluation list says nine, then two more
    # the finding, checked against the data: no mark of the security and planning bodies points toward Nvidia, none of the commerce ministry away
    assert not any(cell[(rk, ck)] for rk in ('cac', 'mss', 'ndrc') for ck in ('welcomed', 'approved'))
    assert not any(cell[('mofcom', ck)] for ck in ('acted', 'told', 'rules'))

    g = ['<div class="g" role="table" aria-label="State bodies against kinds of act">', '<div class="g-head" role="row">',
         '<div class="corner"></div><div class="side away"><i class="sw away"></i>Away from Nvidia</div><div class="side toward"><i class="sw toward"></i>Toward Nvidia</div>',
         '<div class="ch first" role="columnheader">State body</div>']
    g += [f'<div class="ch {d} k-{k}" role="columnheader"><b>{C.T(t)}</b><span>{C.T(s)}</span></div>' for k, d, t, s in COLS]
    g.append('</div>')
    for bi, (band, rows) in enumerate(BANDS):
        g.append(f'<div class="band b{bi}">{C.T(band)}</div>')
        for rk, name, what in rows:
            g.append(f'<div class="r" role="row"><div class="rh" role="rowheader"><b>{name}</b><span>{what}</span></div>')
            for ck, d, title, what_c in COLS:
                ms = cell[(rk, ck)]
                inner = (f'<div class="cl"><i class="sw {d}"></i>{C.T(PHONE_LABEL.get(ck, title))}</div>' + ''.join(C.mark(r) for r in ms)) if ms else ''
                g.append(f'<div class="c {d} k-{ck}{" has" if ms else ""}" role="cell">{inner}</div>')
            g.append('</div>')
        if bi == len(BANDS) - 2:                                   # before the last band: the antitrust case, apart
            g.append('<div class="band">Set apart: a case against Nvidia the company</div>')
            g.append(f'<div class="r" role="row"><div class="rh" role="rowheader"><b>{APART[1]}</b><span>{APART[2]}</span></div>'
                     f'<div class="apart" role="cell"><div class="am">{"".join(C.mark(r) for r in case)}</div>'
                     '<p><b>Not counted on either side.</b> By Nvidia’s own account the preliminary finding concerns the “degraded products” that American export controls required it to offer the Chinese market: '
                     'it faults Nvidia for what it held back, not for selling. No page read says the case has ended; the regulator’s review of Apr 10, 2026 still lists it. '
                     'Whether it was meant as leverage in trade talks is read both ways.</p></div></div>')
    g.append('</div>')
    # Round 9 (Nov 25, 2026): where the page gives the act no date (DATELABEL No_date_given, set in data.txt for atlas figure 11), the grid says
    # "No date given"; the list of records and the pop-ups add the date of the report, which is DATE for these records (checked: it stands in the S line).
    undated = [r for r in recs if r['when'] == 'No date given']
    assert undated and all(C.fmt(r['date']) in r['S'] for r in undated), [r['key'] for r in undated if C.fmt(r['date']) not in r['S']]
    for r in undated: r['when'] = f'No date given; reported {C.fmt(r["date"])}'

    figure = f"""
  <section class="card" id="grid">
{chr(10).join(g)}
   <div class="split">
    <h3>How one newspaper put the split</h3>
    <p>The Financial Times, Nov 13, 2026, in a passage that names no source: the commerce ministry <b>“favoured imports”</b>, while <b>“the national security-focused officials within”</b> the cyberspace regulator and the security ministry
    <b>“viewed dependence on Nvidia as a strategic vulnerability”</b>. <b>“Over the past year, the latter position has gained ground.”</b> The paper speaks of officials within those two bodies, not of the bodies as such.</p>
    <h3>And an American official</h3>
    <p>The US Trade Representative, on Bloomberg Television, video posted Nov 20, 2026 (captions, not checked by ear; 1:06 to 1:35): the Chinese side is <b>“not as monolithic as people would have you believe”</b>.
    In his “own analysis” there are some who think “we’d like to have access” and “others who think, well, we don’t want American chips anyway”. The video’s two caption tracks break the sentence in different places, so whether he puts the split inside the government needs a listen.</p>
   </div>
  </section>
  <section class="care">
   <h2>Read with care</h2>
   <ul>
    <li><b>Open marks rest on unnamed people.</b> In the answers found, Beijing’s spokespeople confirmed none of them: “我不了解你提到的情况” (I am not aware of what you mention), said the foreign ministry on Aug 13, 2025; asked on Nov 9, 2026 about the 600,000 chips Reuters reported in Hong Kong, it said “具体情况建议向中方主管部门询问” (for the details, ask the competent Chinese departments).</li>
    <li><b>The marks are a selection, not a count.</b> An act by several bodies is drawn once in each body’s row, with the same number. The grouping of the rows is ours. {C.WORDS[len(away_rows)].capitalize()} of the named rows (each a body, a group of bodies or a person) have a mark on the side that points away from Nvidia and {C.WORDS[len(toward_rows)]} on the side that points toward it; the industry ministry is on both.</li>
    <li><b>The state-media marks are warnings, not orders.</b> Of {len(sm)} state and Party media items on Nvidia chips found from {C.MON[iso[0].month - 1]} {iso[0].year} to {C.MON[iso[-1].month - 1]} {iso[-1].year}, {len(win)} of the {len(warns)} that only warn about them date from {C.fmt(win[0])} to {C.fmt(win[-1])}, and the {C.WORDS[len(late)]} found later are in Global Times in 2026; {C.WORDS[st['mixed']]} of the {len(sm)} mix a warning with a welcome. The items after September 2025 are what two rounds of searches found, a sample and not a full count. The security ministry’s article names no maker.</li>
    <li><b>No published order against buying Nvidia chips was found</b> in the 82 policy pages read. The 2023 purchase rules bind Party and government bodies from township level up, the public institutions directly under Party committees and governments at those levels, and the departments’ public institutions that provide support to those bodies; other units may leave their requirement out. No published national plan found sets a home-made share for computing centres: every such share found is a province’s or a city’s ({pr['share']} of 31 provincial-level governments were found to set one for home-made computing; one of them, Zhejiang’s, is for the computing of one sector, the province’s information and communications industry, by 2030, as a project’s target), and the national computing-network opinions of December 2023 set none. These shares are not drawn.</li>
    <li>The chip at issue in these marks changed: the H20 (2024 to 2025), the RTX PRO 6000D (2025), the H200 (from December 2025). English renderings of Chinese are ours, not official translations.</li>
   </ul>
  </section>"""

    key = f"""   <ul class="key">
    <li><i class="sw away"></i><span><b>Away from Nvidia:</b> acting against it, or for home-made chips</span></li>
    <li><i class="sw toward"></i><span><b>Toward Nvidia:</b> welcoming it, speaking for access, or, by press reports, approving purchases</span></li>
    <li><i class="p solid away" aria-hidden="true">1</i><span><b>Filled:</b> on the record (a government document, a filing, a named official, a state-media commentary). {n_solid} records</span></li>
    <li><i class="p hollow away" aria-hidden="true">1</i><span><b>Open:</b> a press report citing unnamed people. {n_open} records</span></li>
   </ul>"""

    # Round 10 (ROUND10.md, second ruling): the Tencent News copy of Yuyuan Tantian's post does not say whose account it is. The record line
    # that ties the account to the state broadcaster also opens the award list that states it, as the argument's point 4 cites it.
    # The words quoted are data.txt's N line for that record (checked by cn_has.py with the rest).
    AWARD = 'cn-le13-cja36-winners-xinhuanet-20261108'
    yy = [r for r in recs if r['sid'] == 'cn-le13-yuyuan-qq-20250810b']
    assert len(yy) == 1 and 'state broadcaster' in yy[0]['L'] and (AWARD, '发布端/账号/媒体名称：玉渊谭天Bilibili账号 原创单位：中央广播电视总台') in yy[0]['N'], yy
    award_url = C.B.address(AWARD, C.B.load_refs().get(AWARD, {'addr': ''}))
    assert award_url.startswith('https://www.xinhuanet.com/'), award_url

    def li(r):
        out = C.record_li(r)
        if r is not yy[0]: return out
        add = (f' · whose account: the list of the 36th China Journalism Award gives, for its Bilibili account, “原创单位：中央广播电视总台” (originating unit: China Media Group, the state broadcaster), '
               f'<a href="{C.esc(award_url, quote=True)}">the list on Xinhua’s site</a> · saved copy {AWARD}')
        assert out.count('</span></div></li>') == 1
        return out.replace('</span></div></li>', add + '</span></div></li>')

    below = C.records_block(recs, 'One line for each numbered mark, in the order of the grid: the date of the act, as far as the page gives it (where it gives none, the line says so and gives the date of the report); '
                            'our summary; the page\'s own words; the source. Point at a mark in the grid to read the words there.', li=li)

    page = C.page(
        title='Who Inside Beijing',
        eyebrow='China · Nvidia chips · who inside Beijing did what · 2023 to November 2026',
        h1='Inside Beijing, security and planning bodies held Nvidia back. The commerce side welcomed it.',
        deck=f'{len(recs)} acts, each from a saved source, sorted by who acted and by the kind of act. The cyberspace regulator, the security ministry and the state planner '
             'appear only on the side that points away from Nvidia. The commerce ministry appears only on the side that points toward it: it welcomed Nvidia in public, spoke up for access and, by press reports, approved purchases. '
             'The antitrust case against Nvidia the company is set apart.',
        key=key, figure=figure, below=below, css=CSS,
        tipjson=C.tips(recs, lambda r: ' · '.join(ROWNAME[k].replace('“', '').replace('”', '') for k in r['rows']) + ' · ' + COLNAME[r['col']]))
    out = C.finish(HERE, NAME, page, lines)
    C.records_tsv(HERE / 'records.tsv', recs, [('body', lambda r: '; '.join(ROWNAME[k].replace('“', '').replace('”', '') for k in r['rows'])), ('kind_of_act', lambda r: COLNAME[r['col']]), ('direction', lambda r: r['dir'])])
    per = {ck: sum(r['col'] == ck for r in recs) for ck in COLKEYS + ['case']}
    print(f'records {len(recs)} ({per}); on the record {n_solid}, press reports {n_open}; bodies and people with a mark away {len(away_rows)}, toward {len(toward_rows)}, on both {both}; '
          f'state media {len(sm)} items, {len(warns)} warn ({len(win)} from {C.fmt(win[0])} to {C.fmt(win[-1])}, {len(late)} later), {st["mixed"]} mixed; provinces with a share {pr["share"]} of 31; {summary}')
    if '--png' in sys.argv:
        C.export_png(out, [('#figure', HERE / f'{NAME}.png')])


main()
