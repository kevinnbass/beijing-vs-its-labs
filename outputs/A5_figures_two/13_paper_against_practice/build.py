"""Build the figure "Paper against practice": targets for home-made chips beside what was in use and what was shipped.

Run: python3 -I build.py                                   checks every quotation, writes the page and records.tsv
     python3 -I build.py --png   the same, then exports paper_against_practice.png
Reads data.txt (../common.py explains the format). Writes quotes.tsv from it and runs scripts/cn_has.py on that file; if the
checker does not pass, nothing else is written. Every number drawn is a "V" line of data.txt, with the page's words beside it.
The two sides are not one measure, so they are not drawn on one scale: the targets are thresholds on their own tracks (the
hatched zone is "over this share"), the counts are stacked bars in their own panel.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as C   # noqa: E402

NAME = 'paper_against_practice'

CSS = """
/* Layout: headline and key; two panels (on paper | in practice) with a "not the same measure" divider; what each one measures; the records. */
.duo { display: grid; grid-template-columns: 1fr; gap: 12px; }
@media (min-width: 980px) { .duo { grid-template-columns: minmax(0, 6fr) 76px minmax(0, 7fr); gap: 0; align-items: start; } .duo > .neq { align-self: stretch; } }   /* each card keeps its own height; the divider runs the full height */
.tagline { font: 700 12px/1.2 var(--font-text); letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); margin: 0 0 6px; }
.neq { display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 12px; text-align: center; padding: 2px 0; }
.neq .rule { flex: 1; height: 0; border-top: 2px dashed var(--axis); }
.neq .badge { flex: none; width: 46px; height: 46px; border-radius: 50%; border: 2.5px solid var(--ink); display: grid; place-items: center; font: 700 27px/1 var(--font-head); background: var(--page); padding-bottom: 3px; }
.neq .say { flex: none; font: 700 11.5px/1.3 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink); max-width: 20ch; }
@media (min-width: 980px) { .neq { flex-direction: column; gap: 10px; padding: 0; } .neq .rule { width: 0; height: auto; border-top: 0; border-left: 2px dashed var(--axis); } .neq .say { max-width: 64px; } }

/* targets */
.tg { padding: 10px 0 9px; border-top: 1px solid var(--grid); }
.tg-top { display: flex; flex-wrap: wrap; align-items: baseline; gap: 2px 12px; }
.tg-top .place { font: 700 15px/1.2 var(--font-text); min-width: 78px; }
.tg-top .big { font: 700 25px/1.05 var(--font-head); letter-spacing: -0.01em; white-space: nowrap; }
.tg-top .by { font-size: 14px; color: var(--ink2); flex: 1; }
.tg-top a.pinlink { align-self: center; text-decoration: none; }
.track { position: relative; height: 14px; margin: 7px 0 0; background: var(--slot); border-radius: 4px; }
.track .zone { position: absolute; top: 0; bottom: 0; right: 0; border-radius: 0 4px 4px 0; box-shadow: inset 0 0 0 1.5px var(--away);
  background: repeating-linear-gradient(135deg, var(--away) 0 2px, transparent 2px 7px); opacity: 0.85; }
.track .tick { position: absolute; top: -4px; bottom: -4px; width: 3px; margin-left: -1.5px; background: var(--away); border-radius: 2px; }
.track .tick.mid { width: 2px; margin-left: -1px; }
.exp { display: inline-block; margin-right: 5px; padding: 1px 7px; border: 1.5px solid var(--ink2); border-radius: 999px; font: 700 10.5px/1.4 var(--font-text); letter-spacing: 0.06em; text-transform: uppercase; color: var(--ink); white-space: nowrap; vertical-align: 1px; }
.track.none { background: transparent; box-shadow: inset 0 0 0 1.5px var(--axis); }
.track.none::after { content: ""; position: absolute; inset: 0; border-radius: 4px; background: repeating-linear-gradient(90deg, var(--axis) 0 1px, transparent 1px 12px); opacity: 0.35; }
.tk { position: relative; height: 15px; margin-top: 3px; font-size: 11.5px; color: var(--muted); }
.tk span { position: absolute; top: 0; transform: translateX(-50%); white-space: nowrap; }
.tk span.l { transform: none; } .tk span.r { transform: translateX(-100%); }
.tk span.e { transform: translateX(-100%); padding-right: 3px; }      /* a label that ends at its tick, so two labels on one track keep apart */
.tg-note { font-size: 13px; line-height: 1.38; color: var(--ink2); margin: 3px 0 0; }
.tg-src { font-size: 12px; line-height: 1.35; color: var(--muted); }
.axisnote { font-size: 12px; color: var(--muted); margin: 8px 0 0; }

/* practice */
.pr { padding: 13px 0 12px; border-top: 1px solid var(--grid); }
.pr h3 { font: 700 15px/1.3 var(--font-text); margin: 0 0 2px; display: flex; flex-wrap: wrap; align-items: center; gap: 4px 8px; }
.pr h3 a.pinlink { text-decoration: none; }
.pr .lede { font-size: 13px; color: var(--ink2); margin: 0 0 9px; max-width: 86ch; }
.pr.both .lede { margin-bottom: 0; }
.use { display: grid; grid-template-columns: 1fr; gap: 8px; }
@media (min-width: 620px) { .use { grid-template-columns: 1fr 1fr; } }
.use > div { border-radius: 9px; padding: 9px 12px 10px; }
.use > div.toward { background: var(--toward-tint); } .use > div.away { background: var(--away-tint); }
.use .who { display: flex; align-items: center; gap: 7px; font: 700 12px/1.25 var(--font-text); letter-spacing: 0.05em; text-transform: uppercase; color: var(--ink2); }
.use .who i.sw { width: 10px; height: 10px; }
.use .what { font: 700 21px/1.15 var(--font-head); letter-spacing: -0.01em; margin: 5px 0 4px; }
.use .zh { font-size: 13px; line-height: 1.4; color: var(--ink2); }
.sh { padding: 4px 0 2px; }
.sh + .sh { margin-top: 10px; }
.sh-lab { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 8px; font-weight: 700; font-size: 14px; margin-bottom: 5px; }
.sh-lab span { font-weight: 400; font-size: 12.5px; color: var(--muted); }
.sh-lab a.pinlink { text-decoration: none; }
.sh-bar { display: flex; gap: 2px; height: 26px; }
.sh-bar i { display: block; min-width: 0; }
.sh-bar i:first-child { border-radius: 4px 0 0 4px; } .sh-bar i:last-child { border-radius: 0 4px 4px 0; }
.sh-bar i.toward { background: var(--toward); } .sh-bar i.away { background: var(--away); } .sh-bar i.other { background: var(--us); }
.sh-bar i.rest { background: repeating-linear-gradient(45deg, var(--rest) 0 4px, transparent 4px 8px); box-shadow: inset 0 0 0 1px var(--axis); }
.sh-keys { display: flex; gap: 2px; font-size: 13px; font-weight: 700; margin-top: 4px; line-height: 1.25; }
.sh-keys span { min-width: 0; }
.sh-keys small { display: block; font-size: 12px; font-weight: 400; color: var(--ink2); }
.sh-cap { font-size: 13px; color: var(--ink2); margin-top: 5px; }
@media (max-width: 600px) {
  .sh-keys { flex-wrap: wrap; gap: 3px 14px; }
  .sh-keys span { flex: none !important; display: flex; align-items: baseline; gap: 5px; }
  .sh-keys span:empty, .sh-keys span.k-other { display: none; }
  .sh-keys span::before { content: ""; flex: none; width: 10px; height: 10px; border-radius: 2px; align-self: center; }
  .sh-keys span.k-toward::before { background: var(--toward); } .sh-keys span.k-away::before { background: var(--away); }
  .sh-keys span.k-rest::before { background: repeating-linear-gradient(45deg, var(--rest) 0 3px, transparent 3px 6px); box-shadow: inset 0 0 0 1px var(--axis); }
  .sh-keys small { display: inline; }
  .tg-top .by { flex-basis: 100%; order: 3; }
  .tg-top a.pinlink { margin-left: auto; }
}
.legend { display: flex; flex-wrap: wrap; gap: 5px 16px; font-size: 12.5px; color: var(--ink2); margin: 0 0 8px; padding: 0; list-style: none; }
.legend li { display: flex; align-items: center; gap: 6px; }
.legend i { display: inline-block; width: 12px; height: 12px; border-radius: 3px; }
.legend i.toward { background: var(--toward); } .legend i.away { background: var(--away); } .legend i.other { background: var(--us); }
.legend i.rest { background: repeating-linear-gradient(45deg, var(--rest) 0 3px, transparent 3px 6px); box-shadow: inset 0 0 0 1px var(--axis); }

/* what each measures */
.msr { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 14px; }
.msr th { text-align: left; font: 700 11.5px/1.3 var(--font-text); letter-spacing: 0.07em; text-transform: uppercase; color: var(--muted); padding: 4px 14px 5px 0; border-bottom: 1px solid var(--axis); }
.msr td { vertical-align: top; padding: 6px 14px 6px 0; border-bottom: 1px solid var(--grid); color: var(--ink2); }
.msr td:first-child { color: var(--ink); font-weight: 600; white-space: nowrap; }
.msr tr:last-child td { border-bottom: 0; }
@media (max-width: 700px) {
  .msr, .msr tbody, .msr tr, .msr td { display: block; } .msr thead { display: none; }
  .msr tr { padding: 7px 0; border-bottom: 1px solid var(--grid); } .msr tr:last-child { border-bottom: 0; }
  .msr td { border: 0; padding: 1px 0; } .msr td[data-h]::before { content: attr(data-h) ": "; font-weight: 600; color: var(--ink); }
}
"""


def pinlink(r):
    lab = f'record {r["n"]}: {C.smart(r["S"])}'
    return f'<a class="pinlink" href="#r{r["n"]}" data-n="{r["n"]}" data-tip="1" aria-label="{C.esc(lab, quote=True)}">{C.pin(r)}</a>'


def main():
    recs, extra = C.load(HERE / 'data.txt')
    by = {r['key']: r for r in recs}
    lines = C.checked_lines(recs, extra)
    summary = C.write_and_check_quotes(HERE, lines, 'Quotations and number-bearing phrases behind the figure "Paper against practice".')
    recs = C.number(recs)
    n_solid = sum(r['solid'] for r in recs); n_open = len(recs) - n_solid
    with_target = [r for r in recs if 'target' in r['V']]
    # the governments drawn are exactly those that tables/provinces_31.tsv finds setting a share
    p31 = C.table('provinces_31.tsv'); res = {}
    for r in p31: res[r['result']] = res.get(r['result'], 0) + 1
    share_set = {r['government'] for r in p31 if r['result'] == 'share'}
    assert len(p31) == 31 and {r['place'] for r in with_target} == share_set, ({r['place'] for r in with_target} ^ share_set)
    # round 5 (core edit 6): the one government known only from accounts (Tibet) now rests first on its issuer's own account
    acc = [r for r in p31 if r['result'] == 'account_only']
    assert len(acc) == 1 and "the issuer's own account" in acc[0]['rests_on'] and 'press account' in acc[0]['rests_on'], acc
    who_set = f'{C.WORDS[len(share_set)]} of China’s 31 provincial-level governments'
    n_home = sum(r['term'] == 'home-made' for r in with_target); n_ctrl = sum(r['term'] == 'controllable' for r in with_target)
    assert n_home + n_ctrl == len(with_target) and n_ctrl == 1
    for r in with_target:                                              # the plan's own word stands in its quoted sentence
        assert ('自主可控' in r['Q'][0][0]) == (r['term'] == 'controllable') and (('国产' in r['Q'][0][0]) == (r['term'] == 'home-made')), r['key']

    def phrase(r):
        """The share as its own Chinese words put it: 以上 'or more', 超过 'over', 达到 or 将达 'reach' (the number alone)."""
        q, t = r['Q'][0][0], r['V']['target']
        kinds = [w for w in ('以上', '超过', '达到', '将达') if w in q]
        if not kinds and '占比超' in q: kinds = ['占比超']      # core edit 8: 占比超 without 过 (Zhejiang: 占比超60%, a share over 60%)
        assert len(kinds) == 1, (r['key'], kinds)
        return {'以上': f'{t}% or more', '超过': f'over {t}%', '达到': f'{t}%', '将达': f'{t}%', '占比超': f'over {t}%'}[kinds[0]]

    # ---- on paper ----
    def target(key, big, by_words, note):
        r = by[key]; v = r['V']
        t = v.get('target')
        two = 'mid' in v                                              # a plan that gives two dated values (Jiangsu: 2025 and 2030)
        if two: assert all(y in r['D'][0][1] for y in (r['midyear'], r['year'])), 'both years stand in the checked heading of the plan\'s table'
        tag = '<span class="exp">Expected, not binding</span>' if r.get('status') == 'expected' else ''
        if t is None:
            track = '<div class="track none" role="img" aria-label="no percentage set"></div>'
        else:
            mid = f'<i class="tick mid" style="left:{v["mid"]}%"></i>' if two else ''
            aria = f'{v["mid"]}% by {r["midyear"]}, {phrase(r)} by {r["year"]}' if two else f'target: {phrase(r)}'
            track = (f'<div class="track" role="img" aria-label="{aria}"><i class="zone" style="left:{t}%"></i>{mid}<i class="tick" style="left:{t}%"></i></div>')
        ticks = '<div class="tk"><span class="l" style="left:0">0</span>'
        if t is not None:
            if two: ticks += f'<span class="e" style="left:{v["mid"]}%">{r["midyear"]}: {v["mid"]}%</span><span style="left:{t}%">{r["year"]}: {t}%</span>'
            else: ticks += f'<span{" class=\"e\"" if t >= 85 else ""} style="left:{t}%">{t}%</span>'      # near 100%, the label ends at its tick so it keeps clear of "100%"
        ticks += '<span class="r" style="left:100%">100%</span></div>'
        return (f'<div class="tg"><div class="tg-top"><b class="place">{C.T(r["place"])}</b><span class="big">{C.T(big)}</span><span class="by">{C.T(by_words)}</span>{pinlink(r)}</div>'
                f'{track}{ticks}<p class="tg-note">{tag}{note} <span class="tg-src">Source: {C.T(r["S"])}.</span></p></div>')

    j, s = by['jiangsu']['V'], by['shanghai-target']['V']
    order = ['shandong', 'jiangsu', 'guangdong', 'tianjin', 'hebei', 'zhejiang', 'nmg', 'shanghai-target', 'sichuan', 'national']
    P = {k: phrase(by[k]) for k in order if k != 'national'}
    # Jiangsu: the plan's table gives 50 and 70 and marks the line expected; "binding" stands once in the saved copy, on the energy-efficiency line
    jp = C.L.page(by['jiangsu']['sid'])
    assert by['jiangsu']['status'] == 'expected' and '预期性' in by['jiangsu']['N'][0][1] and jp.count('约束性') == 1 and 'pue≤1.25<1.25约束性' in jp
    assert (by['jiangsu']['midyear'], j['mid'], by['jiangsu']['year'], j['target']) == ('2025', 50, '2030', 70)
    assert [r['key'] for r in recs if r['side'] == 'paper'] == order, 'the targets are drawn in the order of data.txt'
    assert [by[k]['V'].get('target', -1) for k in order] == sorted([by[k]['V'].get('target', -1) for k in order], reverse=True), 'the targets are drawn largest first'
    # the January to June 2026 report does not mention AMD (a control word shows the search can see a hit)
    page26 = C.L.page(by['idc-2026']['sid']); assert 'amd' not in page26 and 'huawei' in page26 and 'nvidia' in page26
    paper = f"""
   <section class="card paper">
    <p class="tagline">On paper</p>
    <h2>Targets that provincial-level governments set</h2>
    <p class="sub">Goals of {who_set}, the ones found to set a share. They do not all count the same thing: each track says what its plan counts. The hatched zone is the share asked for: the line and above.</p>
{target('shandong', P['shandong'], 'by 2025', 'Home-made computing in the province. Known from the provincial daily’s account of the plan; the plan’s own text is not held.')}
{target('jiangsu', P['jiangsu'], f'by {by["jiangsu"]["year"]} ({j["mid"]}% by {by["jiangsu"]["midyear"]})', f'Home-made chips in use in newly built computing centres. The plan’s own table gives {j["mid"]} for {by["jiangsu"]["midyear"]} and {j["target"]} for {by["jiangsu"]["year"]}, and marks the line “预期性” (expected), not “约束性” (binding).')}
{target('guangdong', P['guangdong'], 'by the end of 2025', 'Home-made computing in what is newly added, not chips alone. The wording is “力争” (strive for).')}
{target('tianjin', P['tianjin'], 'by 2026', 'Home-made chips in use in all the city’s computing centres, not only new ones.')}
{target('hebei', P['hebei'], 'by 2025', 'Newly added computing software and hardware that is “自主可控” (independently controllable): not chips alone, and not the word home-made.')}
{target('zhejiang', P['zhejiang'], 'by 2030', 'Home-made computing in one sector’s computing: the province’s information and communications industry. A project’s target in that sector’s five-year plan, posted Jul 29, 2026; it stands outside the plan’s table of indicators.')}
{target('nmg', P['nmg'], 'by 2025', 'Home-made computing, among the goals for the region’s national computing hub.')}
{target('shanghai-target', P['shanghai-target'], 'by 2025', 'Home-made chips in use in the city’s newly built intelligent computing centres.')}
{target('sichuan', P['sichuan'], 'plan for 2024 to 2027', 'Home-made computing equipment, not chips alone. The wording is “力争” (strive for).')}
{target('national', 'no percentage', 'national opinions, Dec 25, 2023', 'No published national plan found in the 82 policy pages read sets a home-made share for computing centres. Two national texts among them hold a home-made percentage of other kinds: a 20% price preference for home-made goods where they compete with others in a government purchase, and an advisory committee’s roadmap of October 2015 that expected home-made products in several fields to reach stated shares of the home market by 2025, among them high-performance computers and servers at over 80% and mobile-terminal chips at 40% (guidance, not an instruction, in the words of the industry ministry’s vice minister at its launch). Bloomberg reported in June 2026, from unnamed people, a draft national plan with “at least 80 per cent of the core technology, AI chips included” from local suppliers; no such plan was found published.')}
    <p class="axisnote">Scale of the {C.WORDS[len(order)]} tracks: a share in that place, as its plan defines it. A goal, not a count. Of the other {31 - len(share_set)} provincial-level governments, {res['plan_no_share']} have a plan that was read and sets no share, {C.WORDS[res['account_only']]} is known only from accounts of its plan (its issuer’s own among them), and for {C.WORDS[res['not_reached']]} no computing plan was found (tables/provinces_31.tsv).</p>
   </section>"""

    # ---- in practice ----
    sr, a, b = by['shanghai-reply'], by['idc-2025'], by['idc-2026']
    va, vb = a['V'], b['V']
    assert va['nvidia'] + va['chinese'] + va['amd'] == 100
    four = vb['thead'] + vb['cambricon'] + vb['kunlunxin'] + vb['hygon']                       # our sum of the four makers named after Huawei
    rest = 100 - vb['nvidia'] - vb['huawei'] - four                                           # our subtraction
    named_cn = vb['huawei'] + four                                                            # our sum
    assert rest > 0

    def bar(segs, label):
        return (f'<div class="sh-bar" role="img" aria-label="{C.esc(label, quote=True)}">' + ''.join(f'<i class="{cls}" style="flex:{w}"></i>' for cls, w, _, _ in segs) + '</div>'
                '<div class="sh-keys">' + ''.join(f'<span class="k-{cls}" style="flex:{w}">{C.T(t)}<small>{C.T(sm)}</small></span>' for cls, w, t, sm in segs) + '</div>')

    seg25 = [('toward', va['nvidia'], f'Nvidia {va["nvidia"]}%', ''), ('other', va['amd'], '', ''), ('away', va['chinese'], f'Chinese makers {va["chinese"]}%', '')]
    seg26 = [('toward', vb['nvidia'], f'Nvidia {vb["nvidia"]}%', ''), ('away', vb['huawei'], f'Huawei {vb["huawei"]}%', ''),
             ('away', vb['thead'], f'Four more {four}%', 'Chinese makers'), ('away', vb['cambricon'], '', ''), ('away', vb['kunlunxin'], '', ''), ('away', vb['hygon'], '', ''),
             ('rest', rest, f'Rest {rest}%', 'not broken down')]
    # the label "Four more" sits under the first of the four small segments and needs their whole width: merge the four flex cells in the key row
    key26 = [('toward', vb['nvidia'], f'Nvidia {vb["nvidia"]}%', ''), ('away', vb['huawei'], f'Huawei {vb["huawei"]}%', ''), ('away', four, f'Four more {four}%', 'Chinese makers'), ('rest', rest, f'Rest {rest}%', 'not broken down')]
    bar26 = (f'<div class="sh-bar" role="img" aria-label="Nvidia {vb["nvidia"]}%, Huawei {vb["huawei"]}%, four more Chinese makers {four}%, the rest {rest}%">'
             + ''.join(f'<i class="{cls}" style="flex:{w}"></i>' for cls, w, _, _ in seg26) + '</div>'
             '<div class="sh-keys">' + ''.join(f'<span class="k-{cls}" style="flex:{w}">{C.T(t)}<small>{C.T(sm)}</small></span>' for cls, w, t, sm in key26) + '</div>')

    practice = f"""
   <section class="card practice">
    <p class="tagline">In practice</p>
    <h2>What was in use, and what was shipped</h2>
    <p class="sub">A city government’s own description, and a research firm’s counts for the whole country.</p>
    <div class="pr">
     <h3>In use in Shanghai, in a government body’s words {pinlink(sr)}</h3>
     <p class="lede">Shanghai’s Commission of Economy and Informatization, written reply dated Apr 30, 2025 (published Nov 10, 2025). It gives no percentage.</p>
     <div class="use">
      <div class="toward"><div class="who"><i class="sw toward"></i>Internet companies’ own clusters</div><div class="what">mainly Nvidia</div>
       <div class="zh">“主要以英伟达高性能卡为主” (mainly Nvidia high-performance cards)</div></div>
      <div class="away"><div class="who"><i class="sw away"></i>The three state telecom operators</div><div class="what">mainly Huawei and other home-made</div>
       <div class="zh">“三大运营商主要购置华为等国产化智算集群” (the three operators mainly buy Huawei and other home-made intelligent-computing clusters)</div></div>
     </div>
    </div>
    <div class="pr">
     <h3>Shipped in all of China, by a research firm’s count</h3>
     <p class="lede">AI accelerator cards shipped in China, by maker. Counts by the research firm IDC, as reported by Reuters.</p>
     <ul class="legend"><li><i class="toward"></i>Nvidia</li><li><i class="away"></i>Chinese makers</li><li><i class="other"></i>AMD</li><li><i class="rest"></i>not broken down in the report</li></ul>
     <div class="sh"><div class="sh-lab">2025 {pinlink(a)}<span>about 4 million cards</span></div>
{bar(seg25, f'Nvidia {va["nvidia"]}%, AMD {va["amd"]}%, Chinese makers {va["chinese"]}%')}
      <div class="sh-cap">Nvidia {va["nvidia"]}%, AMD {va["amd"]}%, Chinese makers together {va["chinese"]}%. <span class="tg-src">Source: IDC, reported by Reuters, Apr 1, 2026.</span></div></div>
     <div class="sh"><div class="sh-lab">January to June 2026 {pinlink(b)}<span>2.008 million cards</span></div>
{bar26}
      <div class="sh-cap">Nvidia {vb["nvidia"]}%, Huawei {vb["huawei"]}%; then T-Head {vb["thead"]}%, Cambricon {vb["cambricon"]}%, Kunlunxin {vb["kunlunxin"]}%, Hygon {vb["hygon"]}%. The six named makers leave {rest}% (our subtraction).
      The five Chinese makers named add up to {named_cn}% (our sum); the report gives no total for Chinese makers and does not mention AMD. <span class="tg-src">Source: IDC, reported by Reuters, Oct 13, 2026.</span></div></div>
    </div>
    <div class="pr both">
     <h3>Shanghai is on both sides of this figure {pinlink(by['shanghai-target'])} {pinlink(sr)}</h3>
     <p class="lede">Its plan set the goal of over {s["target"]}% home-made chips in new centres by 2025. Its commission’s reply of Apr 30, 2025 describes the clusters that internet companies run. A goal for new centres and a description of clusters in use are still two different things.</p>
    </div>
   </section>"""

    figure = f"""
  <div class="duo">{paper}
   <div class="neq" aria-label="Not the same measure"><span class="rule"></span><span class="badge">≠</span><span class="say">Not the same measure</span><span class="rule"></span></div>{practice}
  </div>
  <section class="care">
   <h2>Read with care: what each one measures</h2>
   <table class="msr">
    <thead><tr><th></th><th>Who says it</th><th>What it measures</th><th>Where and when</th></tr></thead>
    <tbody>
     <tr><td>The targets</td><td data-h="Who says it">a provincial-level government, in a plan</td><td data-h="What it measures">a goal: a share of the chips, equipment or computing in that place. Three count home-made chips (Jiangsu and Shanghai in new centres, Tianjin in all); Guangdong, Inner Mongolia and Shandong home-made computing (Guangdong in what is newly added); Zhejiang home-made computing in one sector, its information and communications industry; Sichuan home-made equipment; Hebei software and hardware called independently controllable. Jiangsu’s plan marks its own target as expected, not binding; Shandong’s is known from a newspaper’s account</td><td data-h="Where and when">one government each; goals for 2025, 2026 and 2030, and a plan that runs to 2027</td></tr>
     <tr><td>The Shanghai reply</td><td data-h="Who says it">a city government body</td><td data-h="What it measures">no number: which cards the clusters of each kind of owner mainly run on</td><td data-h="Where and when">Shanghai; dated Apr 30, 2025 (published Nov 10, 2025)</td></tr>
     <tr><td>The research firm’s counts</td><td data-h="Who says it">IDC, as reported by Reuters</td><td data-h="What it measures">cards shipped in a period, by maker. Reuters words the first as AI accelerator cards and the second as the market for data-centre AI chips, so the two bars are not shown as one series</td><td data-h="Where and when">all of China; 2025, and January to June 2026</td></tr>
    </tbody>
   </table>
   <p style="margin-top:8px">So the two sides cannot be set on one scale: a provincial or city target is not tested by national shipments, and neither number proves or disproves the other. The research firm’s count is of what was shipped, not of what any one buyer uses.
   English renderings of Chinese are ours, not official translations.</p>
  </section>"""

    key = f"""   <ul class="key">
    <li><i class="sw away"></i><span><b>Orange:</b> the targets on paper, and Chinese makers</span></li>
    <li><i class="sw toward"></i><span><b>Blue:</b> Nvidia</span></li>
    <li><i class="p solid away" aria-hidden="true">1</i><span><b>Filled number:</b> a government document, or a newspaper’s account of one. {n_solid} records</span></li>
    <li><i class="p hollow toward" aria-hidden="true">1</i><span><b>Open number:</b> a research firm’s count, through the press. {n_open} records</span></li>
   </ul>"""

    below = C.records_block(recs, 'One line for each numbered source: its date, our summary, the page\'s own words, and the source. Point at a number in the figure to read the words there.')
    page = C.page(
        title='Paper Against Practice',
        eyebrow='China · home-made chip targets and what was in use · 2023 to 2026',
        h1='On paper, half or more home‑made. In practice, Nvidia was still the biggest single supplier.',
        deck=f'Targets that {who_set} set for computing ({C.WORDS[n_home]} for home-made chips, equipment or computing, {C.WORDS[n_ctrl]} for what it calls independently controllable), '
             'beside what a Shanghai government body wrote and what a research firm counted. '
             'The two sides do not measure the same thing, so each has its own panel and its own scale. By the counts, Nvidia stayed the largest maker while its share fell.',
        key=key, figure=figure, below=below, css=CSS,
        tipjson=C.tips(recs, lambda r: 'On paper' if r['side'] == 'paper' else 'In practice'))
    out = C.finish(HERE, NAME, page, lines)
    C.records_tsv(HERE / 'records.tsv', recs, [('side', lambda r: r['side']), ('numbers_drawn', lambda r: '; '.join(f'{k}={v}' for k, v in r['V'].items()))])
    print(f'records {len(recs)}; government documents {n_solid}, research firm\'s counts {n_open}; drawn: targets {[(by[k]["place"], by[k]["V"].get("target")) for k in order]}, 2025 {va}, Jan-Jun 2026 {vb}; '
          f'our arithmetic: four more makers {four}, rest {rest}, named Chinese makers {named_cn}; {summary}')
    if '--png' in sys.argv:
        C.export_png(out, [('#figure', HERE / f'{NAME}.png')])


main()
