"""Build the figure "The ladder of evidence": the argument's sources on five rungs, and which rung each point stands on.

Run: python3 -I build.py                                   counts, checks every quotation, writes the page and sources.tsv
     python3 -I build.py --png   the same, then exports ladder_of_evidence.png
Counts come from two files of the project, never from typing:
  ../../argument/argument_refs.tsv   the argument's sources and their kinds  -> sources per rung
  ../../argument/argument_base.txt   the argument's text with saved ids       -> which point cites which source
Kinds to rungs (round 4: the argument has eleven kinds; its own builder counts all but PRESS, COUNT and CLIP as on the record):
  1 DOC, PUB      Chinese state documents, and published commentary of state media or an industry body
  2 FIL, NOTICE   company filings and statements, and a buyer's own published purchase notice (core edit 8, Nov 25, 2026: universities, a
                  centre of the drug regulator, the purchasing centre for central state bodies, and the state telecom carriers'
                  tender notices, most of them as tender sites carry them)
  3 OFF, NAMED    officials on the record and official records; one named analyst's written testimony
  4 REC, ACCT     press reports naming their source: a named person's words, a company's statement (round 8: the argument's
                  REC rows include company statements, among them Nvidia's statement as two news sites carried it, The
                  Standard and the Daily Caller News Foundation, edit 7c), or a named news outlet's account of a document, a filing
                  or an official act (round 9: the core's label for ACCT was widened in core edit 8b, and a Reuters factbox made
                  from tender documents and company statements became ACCT)
  5 PRESS, COUNT, CLIP   unnamed people, research firms' counts (the core's COUNT label also names brokers; the build asserts that
                  every COUNT source of the argument is a research firm's), caption tracks or machine transcripts not checked by ear
The examples and their words are in data.txt; quotes.tsv is written from it and checked by scripts/cn_has.py before
anything else is written.
"""
import hashlib, json, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as C   # noqa: E402
B = C.B

NAME = 'ladder_of_evidence'
RUNG_OF = {'DOC': 1, 'PUB': 1, 'FIL': 2, 'NOTICE': 2, 'OFF': 3, 'NAMED': 3, 'REC': 4, 'ACCT': 4, 'PRESS': 5, 'COUNT': 5, 'CLIP': 5}
RUNGS = {  # name, what sits on it, what it shows about this claim, what it does not show ({SM} is filled in from tables/state_media_items.tsv)
    1: ('Chinese state documents and state media', 'texts of the Chinese party-state and its bodies; what state media and an industry body published: commentary, reports, statements',
        'The declared line: end dependence on foreign core technology and use home-made chips. The purchase rules for government buying, the provincial targets, '
        'the antitrust case and the summons. A Shanghai government body’s own statement that internet companies’ own clusters in the city run mainly on Nvidia. '
        'And the public warnings: state media warned about Nvidia’s chips, {SM}; a Party paper also printed a scholar’s advice to stock imported chips.',
        'Any order telling companies not to buy Nvidia chips. None was found in the 82 policy pages read. The commentaries warn and urge; none forbids.'),
    2: ('Company filings and own notices', 'what companies told securities regulators, exchanges and investors: filings, results releases, the company’s own transcript of a results call; and buyers’ own purchase notices (universities, a centre of the drug regulator, the purchasing centre for central state bodies, and the state telecom carriers, most of whose notices are held as tender sites carry them)',
        'Alibaba told the US securities regulator that the cyberspace regulator asked Chinese technology companies to halt purchases of certain chips. Nvidia told it that the Chinese government restricted, and later discouraged, customers’ purchases, '
        'and that its licensed sales were restricted; the same reports say it is effectively foreclosed from the China market by US export controls. On its own results calls Nvidia said in May 2026 '
        'that it had no revenue yet from the licensed chips, and in November 2026 that it had sold $2.4 billion of licensed Hopper products to China in a quarter and was no longer shipping. '
        'Alibaba also says its own chips are in scaled production. Listed Chinese firms told the Shenzhen exchange of purchases of cards named PRO 5500. '
        'Universities’ own notices of 2026 seek, buy or rent Nvidia cards, from two cards to six to eight eight-card servers; some central buyers’ notices of November 2026 ask for home-made computing. An award of April 2025 by the purchasing centre for central state bodies, for a university’s IT centre, names Nvidia H20 modules under a tender that allowed no imported products. {CARRIERS}',
        'Who gave the instruction, or how. Alibaba’s sentence does not name Nvidia. Nvidia gave no reason for stopping. A notice to buy is not a purchase made, and a contract is not a delivery.'),
    3: ('Officials and official records', 'named officials, in their own body’s account or a transcript; official records, most of them American (hearings, reports, rules, the licence table); one analyst’s written testimony. Executives’ words reach us through rungs 2 and 4',
        'American officials state the conflict in their own names, as their understanding; American bodies read Beijing’s acts as leverage in trade talks, or as a push for more advanced chips. Washington’s own licence table marks every approved application not shipped. '
        'Chinese officials stand on both sides in public: the state planner says it is guiding home-made models to do more to adapt to home-made chips; a vice premier and the commerce minister welcome Nvidia, and the premier tells American firms, Nvidia’s among them, that an open policy is a lasting commitment; asked about the reports, spokespeople confirm nothing.',
        'Any Chinese official saying that purchases were stopped.'),
    4: ('Press reports naming their source', 'a named person’s words at a hearing, on a results call, on television or in a post, a company’s statement, or a named news outlet’s account of a document, a filing or an official act, as a news outlet, a post or a transcript site gives them',
        'The Treasury Secretary’s view that Chinese orders were few. A Tencent executive’s remark that policy restrictions kept foreign-designed chips out of China; he does not say whose policy. '
        'And the companies’ own turn to home-made chips, in their executives’ words.',
        'A first-hand record. Each of these passes through a reporter, a post or a transcript site; the speaker labels of the Tencent transcripts are the site’s and are unchecked.'),
    5: ('Press reports citing unnamed people', 'also research firms’ counts, and caption tracks or machine transcripts that nobody has checked by ear',
        'Who told whom, and when: the guidance not to buy, the warning about traitors, the customs checks, the split inside Beijing. Every count of the chips ordered across China’s companies, approved by Beijing, delivered and waiting; '
        'the counts single buyers give of their own purchases are on rung 2. Nvidia’s market share, and the foreign suppliers’ share. The clip that raised the question, and the Trade Representative’s and the Treasury Secretary’s words on Bloomberg Television and a Bloomberg podcast, in caption tracks or transcripts.',
        'Confirmation. In the answers found, Beijing’s spokespeople confirmed none of these reports.'),
}
GROUPS = [  # label, the points in it (the argument's own sections; "T" is its table of numbers)
    ('The declared line', [1, 2, 3, 4]), ('What the companies used and wanted', [5, 6, 7, 8, 9]), ('What Beijing did: on the record', [10, 11, 12]),
    ('What Beijing did: as reported', [13, 14, 15, 16]), ('Numbers', ['T']), ('Five limits on the claim', [17, 18, 19, 20, 21])]

CSS = """
/* Layout: headline and key; the ladder (five rungs, firmest on top); a matrix of the argument's points against the rungs; read with care; the sources. */
.u { display: inline-block; width: 13px; height: 13px; border-radius: 3px; background: var(--ink2); vertical-align: middle; }
.u.open { background: var(--surface); box-shadow: inset 0 0 0 2px var(--ink2); }
.key .u { flex: none; }
a.u:hover, a.u.hl, a.u:focus-visible { outline: 2px solid var(--ink); outline-offset: 1px; }
.rung { display: grid; grid-template-columns: 46px minmax(0, 0.9fr) minmax(0, 1.25fr) minmax(0, 1.35fr); gap: 4px 22px; padding: 14px 0 13px; border-top: 1px solid var(--grid); position: relative; }
.rung:first-of-type { border-top: 0; padding-top: 4px; }
.rk { position: relative; display: flex; justify-content: center; }
.rk::before { content: ""; position: absolute; top: -15px; bottom: -14px; left: 50%; border-left: 2px solid var(--axis); }
.rung:first-of-type .rk::before { top: 4px; } .rung.last .rk::before { bottom: 50%; }
.rk span { position: relative; display: grid; place-items: center; width: 34px; height: 34px; border-radius: 50%; font: 700 16px/1 var(--font-head); background: var(--ink2); color: var(--pin-on); border: 2.5px solid var(--ink2); }
.rung.open .rk span { background: var(--surface); color: var(--ink); }
.rn h3 { font: 700 17px/1.2 var(--font-text); margin: 0; text-wrap: balance; }
.rn .of { font-size: 12.5px; line-height: 1.35; color: var(--muted); margin: 3px 0 8px; }
.rn .cnt { display: flex; align-items: baseline; gap: 8px; margin-bottom: 7px; }
.rn .cnt b { font: 700 34px/0.95 var(--font-head); letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
.rn .cnt span { font-size: 13px; color: var(--ink2); }
.units { display: flex; flex-wrap: wrap; gap: 3px; max-width: 238px; }
.rung h4 { font: 700 11.5px/1.3 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin: 2px 0 5px; }
.shows p { font-size: 14.5px; line-height: 1.45; margin: 0; }
.shows p.not { font-size: 13.5px; color: var(--ink2); margin-top: 7px; }
.shows p.not b { color: var(--ink); font-weight: 600; }
.exs a.mk .mt { font-size: 13px; }
.exs a.mk .mt > span { color: var(--ink2); }
.exs a.mk .said2 { color: var(--ink) !important; }
.line { display: flex; align-items: center; gap: 12px; margin: 2px 0; font: 700 12px/1.3 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink); }
.line::before, .line::after { content: ""; flex: 1; border-top: 2px dashed var(--ink); opacity: 0.55; }
.line span { text-align: center; }
@media (max-width: 900px) {
  .rung { grid-template-columns: 40px minmax(0, 1fr); }
  .rung .shows, .rung .exs { grid-column: 2; margin-top: 8px; }
  .rk::before { display: none; }
}

/* the matrix */
.hint { display: none; margin: 0 0 6px; font-size: 13px; font-weight: 600; color: var(--ink2); }
@media (max-width: 860px) { .hint { display: block; } }
.scroll { overflow-x: auto; margin: 0 -6px; padding: 2px 6px 4px; }
.mx { display: grid; gap: 4px 3px; min-width: 780px; align-items: center; }
.mx .gh { font: 700 11px/1.25 var(--font-text); letter-spacing: 0.05em; text-transform: uppercase; color: var(--ink2); padding: 0 3px 5px; border-bottom: 2px solid var(--axis); align-self: end; text-wrap: balance; }
.mx .pn { font: 700 12.5px/1 var(--font-text); color: var(--ink2); text-align: center; padding: 3px 0 2px; font-variant-numeric: tabular-nums; }
.mx .rl { font: 600 13px/1.25 var(--font-text); padding-right: 10px; display: flex; align-items: center; gap: 8px; }
.mx .rl i { flex: none; display: grid; place-items: center; width: 20px; height: 20px; border-radius: 50%; font: 700 11px/1 var(--font-text); font-style: normal; background: var(--ink2); color: var(--pin-on); border: 2px solid var(--ink2); }
.mx .rl.open i { background: var(--surface); color: var(--ink); }
.mx .k { display: grid; place-items: center; height: 28px; border-radius: 6px; font: 700 13px/1 var(--font-text); font-variant-numeric: tabular-nums; }
.mx .k.solid { background: var(--ink2); color: var(--pin-on); }
.mx .k.open { background: var(--surface); color: var(--ink); box-shadow: inset 0 0 0 2px var(--ink2); }
.mx .k.zero { background: var(--slot); }
.mx .sep { margin-left: 9px; }
.ptlist { font-size: 12.5px; line-height: 1.55; color: var(--ink2); margin: 10px 0 0; max-width: 150ch; }
.ptlist b { color: var(--ink); font-weight: 700; }
li.ev .what { font-size: 13.5px; }
/* reference numbers run to three digits: the mark widens into a pill instead of clipping the number */
i.p { width: auto; min-width: 22px; padding: 0 3px; border-radius: 11px; }
li.ev { grid-template-columns: 32px 1fr; }
"""


def main():
    allrefs = B.load_refs()                    # since round 4 it also returns rows of argument_refs_more.tsv, flagged opt: not the argument's own
    refs = {s: r for s, r in allrefs.items() if not r.get('opt')}
    fp ={p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:12] for p in (B.REFS, B.BASE)}      # which bytes were counted
    base = [ln for ln in B.BASE.read_text(encoding='utf-8').splitlines() if not ln.startswith('!!')]
    # the argument's own reference numbers: the order of first citation
    num = {}
    for ln in base:
        for sid in B.CITE.findall(ln):
            num.setdefault(sid, len(num) + 1)
    assert set(num) == set(refs), 'the argument cites exactly the sources of its references file'
    rung = {sid: RUNG_OF[r['kind']] for sid, r in refs.items()}
    per = Counter(rung.values()); kinds = Counter(r['kind'] for r in refs.values())
    total = len(refs); on = sum(per[k] for k in (1, 2, 3, 4)); off = per[5]
    assert on + off == total

    # which point cites which source
    # A point runs from its numbered line to the next numbered line or heading: the paragraphs and tables under it count
    # for it (round 4: several points of the new argument go on over more than one paragraph). Section 4 is the numbers ("T").
    pts, titles, sec, cur = {}, {}, '', None
    for ln in base:
        if ln.startswith('## '):
            sec = ln[3:]; cur = 'T' if sec.startswith('4.') else None
            continue
        m = re.match(r'(\d+)\. \*\*(.*?)\*\*', ln)
        if m:
            cur = int(m.group(1)); titles[cur] = m.group(2).rstrip('.'); pts[cur] = []
        ids = list(dict.fromkeys(B.CITE.findall(ln)))
        if ids and cur is not None:
            pts.setdefault(cur, []); pts[cur] += [i for i in ids if i not in pts[cur]]
    titles['T'] = 'The table of numbers and Nvidia’s share'
    assert sorted(k for k in pts if k != 'T') == list(range(1, 22)), 'the argument has 21 numbered points'
    assert set(kinds) <= set(RUNG_OF), set(kinds) - set(RUNG_OF)
    assert on == sum(v for k, v in kinds.items() if k in B.SOLID), 'the rungs above the line hold exactly the kinds the argument counts as on the record'
    # round 5: the words of the rungs that describe kinds rest on these (a change in the references stops the build here)
    lab_of = lambda k: [r['label'] for r in refs.values() if r['kind'] == k]
    notices = lab_of('NOTICE')
    # core edit 8: the notices are universities' (the central purchasing centre's tender document for one of them among them), one of a centre of the drug
    # regulator, and the state carriers' tender notices; a notice of any other kind of buyer stops the build, so the words of rung 2 are looked at again
    NCLASS = (('carrier', ('China Mobile', 'China Telecom', 'China Unicom')), ('drug regulator', ('National Medical Products Administration',)), ('university', ('Universit',)))
    nclass = [next((c for c, ws in NCLASS if any(w in l for w in ws)), None) for l in notices]
    assert None not in nclass, [l for l, c in zip(notices, nclass) if c is None]
    assert nclass.count('drug regulator') == 1 and nclass.count('university') >= 8 and nclass.count('carrier') >= 6, Counter(nclass)
    assert sum('Purchasing centre for central state bodies' in l for l in notices) == 1, 'the central purchasing centre\'s tender document'
    assert all(refs.get(s, {}).get('kind') == 'NOTICE' for s in ('cn-ga31-h20notices-7', 'cn-ga31-h20notices-19', 'cn-ga31-operators-63', 'cn-ga31-operators-7', 'cn-ga31-operators-32'))      # the award naming H20 modules, its tender document, and three carrier notices the words of rung 2 rest on
    assert {f for f in ('IDC', 'TrendForce') if any(f in l for l in lab_of('COUNT'))} == {'IDC', 'TrendForce'}, lab_of('COUNT')                                   # research firms' counts (two firms)
    assert all(refs.get(s, {}).get('kind') == 'FIL' for s in ('cn-filings-tianyang-20261013-contract', 'cn-le08-youzu-contract-20261104', 'cn-ga01-hzyl-contract-20261112'))   # listed firms' notices of PRO 5500 purchases: rung 2
    assert all(refs.get(s, {}).get('kind') == 'NOTICE' for s in ('cn-ga13-nwpu-som-88690-wayback', 'cn-ga13-ccgp-nmpa-cmde-ai-rental-27742397', 'cn-ga13-ccgp-pku-inference-card-27734000'))
    assert kinds['NAMED'] == 1 and kinds['ACCT'] >= 2
    sm = C.table('state_media_items.tsv'); warns = sorted(C.date.fromisoformat(r['date']) for r in sm if r['stance'] == 'warns')
    win = [d for d in warns if d <= C.date(2025, 9, 24)]
    assert (len(sm), len(warns), len(win)) == (75, 19, 16), (len(sm), len(warns), len(win))      # the table since core edit 6 (atlas/core_edit/p6_work_5/count_census.py)
    RUNGS[1] = RUNGS[1][:2] + (RUNGS[1][2].replace('{SM}', f'in {len(warns)} of {len(sm)} state and Party media items found that only warn about them, {len(win)} of them dated {C.fmt(win[0])} to {C.fmt(win[-1])} and {len(warns) - len(win)} later, in Global Times in 2026 (the items after September 2025 are what two rounds of searches found, a sample and not a full count)'),) + RUNGS[1][3:]
    assert '{' not in RUNGS[1][2]
    # round 9 (core edit 8b): the kinds' words of rungs 4 and 5 rest on these
    assert all(('IDC' in l or 'TrendForce' in l) for l in lab_of('COUNT')), lab_of('COUNT')          # every count is a research firm's (no broker's)
    clip = lab_of('CLIP')
    assert sum('Bloomberg Talks (a Bloomberg podcast)' in l for l in clip) == 1 and sum('Bloomberg Television' in l for l in clip) >= 3, clip
    # round 9 (core edit 8b): the carriers' own notices, as the argument now words them, and how many of their pages name Nvidia, counted from
    # tables/carriers_own_notices.tsv (its classes of a carrier's own notice, filing or news page and a site's record of a notice); the control is
    # that the same column finds Nvidia words on press rows of the table
    cn_rows = C.table('carriers_own_notices.tsv')
    OWN = ("carrier's own notice", "a tender site's account of the notice", "carrier's own page", "carrier's own filing")
    own = [r for r in cn_rows if r['who_states'].startswith(OWN)]
    pages = {r['saved_id'] for r in own}; named = {r['saved_id'] for r in own if r['nvidia_words_on_page'] != 'none'}
    ctl = [r for r in cn_rows if r['who_states'].startswith('press') and r['nvidia_words_on_page'] != 'none']
    assert named == {'cn-ga31-carrierown-14'} and refs['cn-ga31-carrierown-14']['kind'] == 'NOTICE' and ctl, (len(pages), named, len(ctl))
    RUNGS[2] = RUNGS[2][:2] + (RUNGS[2][2].replace('{CARRIERS}', f'The carriers’ own notices ask for home-made chips by maker or by origin, or label their lots by software ecosystem; of the {len(pages)} such pages read, {len(pages) - len(named)} name neither Nvidia nor an Nvidia model, and the other, a small tender of 2024 by a Jiangsu company that bears China Unicom’s name, names Nvidia cards as NV RTX 3090, NV RTX 4090 and NV Tesla A100.'),) + RUNGS[2][3:]
    assert '{' not in RUNGS[2][2]
    cols = [p for _, ps in GROUPS for p in ps]
    cellc = {(p, k): sum(rung[i] == k for i in pts[p]) for p in cols for k in range(1, 6)}
    only1 = [p for p in cols if p != 'T' and cellc[(p, 1)] and not any(cellc[(p, k)] for k in (2, 3, 4, 5))]
    only5 = [p for p in cols if p != 'T' and cellc[(p, 5)] and not any(cellc[(p, k)] for k in (1, 2, 3, 4))]
    outside = sorted([s for s in refs if not any(s in pts[p] for p in cols)], key=lambda s: num[s])      # cited only in the opening or in the list of what is left open
    t_all, t5 = len(pts['T']), cellc[('T', 5)]

    # the examples
    recs, extra = C.load(HERE / 'data.txt')
    for r in recs:
        assert r['sid'] in refs, f"{r['key']}: {r['sid']} is not one of the argument's sources"
        assert int(r['rung']) == rung[r['sid']], f"{r['key']}: rung {r['rung']} but its kind is {refs[r['sid']]['kind']}"
        r['n'] = num[r['sid']]; r['solid'] = rung[r['sid']] < 5
    lines = C.checked_lines(recs, extra)
    summary = C.write_and_check_quotes(HERE, lines, 'Quotations and number-bearing phrases behind the figure "The ladder of evidence".')

    addr = {sid: (B.address(sid, r) or '') for sid, r in refs.items()}
    label = {sid: re.sub(r'"([^"]*)"', '‘\\1’', r['label']) for sid, r in refs.items()}       # a title inside a label takes single quote marks
    by_rung = {k: sorted([s for s in refs if rung[s] == k], key=lambda s: num[s]) for k in range(1, 6)}

    def units(k):
        return ''.join(f'<a class="u{"" if k < 5 else " open"}" href="#r{num[s]}" data-n="{num[s]}" data-tip="1" aria-label="source {num[s]}: {C.esc(label[s], quote=True)}"></a>' for s in by_rung[k])

    def example(r):
        q, e = r['Q'][0]
        said = f'“{C.esc(C.inner_quotes(q), quote=False)}”' + (f' ({C.T(e)})' if e else '')
        lab = f'source {r["n"]}: {C.smart(r["T"])}'
        return (f'<a class="mk" href="#r{r["n"]}" data-n="{r["n"]}" data-tip="1" aria-label="{C.esc(lab, quote=True)}">{C.pin(r)}'
                f'<span class="mt"><span class="said2">{said}</span> <span>{C.T(r["T"])}, {C.esc(r["when"])}</span></span></a>')

    lad = []
    for k in range(1, 6):
        name, of, shows, nots = RUNGS[k]
        extra_count = ''
        if k == 5: extra_count = f'<span>sources: {kinds["PRESS"]} press reports, {kinds["COUNT"]} counts, {kinds["CLIP"]} caption tracks or transcripts</span>'
        if k == 5:
            lad.append(f'<div class="line"><span>Above this line, on the record: {on} sources · below it: {off}</span></div>')
        lad.append(f"""<div class="rung{' open last' if k == 5 else ''}">
     <div class="rk"><span>{k}</span></div>
     <div class="rn"><h3>{name}</h3><p class="of">{of}</p><div class="cnt"><b>{per[k]}</b>{extra_count or f'<span>source{"s" if per[k] != 1 else ""}</span>'}</div><div class="units">{units(k)}</div></div>
     <div class="shows"><h4>What it shows about this claim</h4><p>{shows}</p><p class="not"><b>Not on this rung:</b> {nots}</p></div>
     <div class="exs"><h4>For example</h4>{''.join(example(r) for r in recs if int(r['rung']) == k)}</div>
    </div>""")

    def pname(p): return 'T' if p == 'T' else str(p)
    widths = ' '.join('minmax(0, 1.9fr)' if p == 'T' else 'minmax(0, 1fr)' for p in cols)
    mx = [f'<div class="mx" style="grid-template-columns: minmax(190px, 5fr) {widths}" role="table" aria-label="Sources cited at each point of the argument, by rung">']
    mx.append('<div></div>')
    for gi, (g, ps) in enumerate(GROUPS):
        mx.append(f'<div class="gh{" sep" if gi else ""}" style="grid-column: span {len(ps)}">{C.T(g)}</div>')
    mx.append('<div class="pn" style="text-align:left;font-weight:600">Point</div>')
    firsts = {ps[0] for gi, (_, ps) in enumerate(GROUPS) if gi}
    for p in cols:
        mx.append(f'<div class="pn{" sep" if p in firsts else ""}" title="{C.esc(C.smart(titles[p]), quote=True)}">{pname(p)}</div>')
    for k in range(1, 6):
        mx.append(f'<div class="rl{" open" if k == 5 else ""}"><i>{k}</i>{RUNGS[k][0]}</div>')
        for p in cols:
            c = cellc[(p, k)]
            cls = 'zero' if not c else ('solid' if k < 5 else 'open')
            mx.append(f'<div class="k {cls}{" sep" if p in firsts else ""}" role="cell" aria-label="point {pname(p)}, rung {k}: {c} source{"s" if c != 1 else ""}">{c or ""}</div>')
    mx.append('</div>')
    ptlist = ' · '.join(f'<b>{pname(p)}</b> {C.T(titles[p])}' for p in cols)

    def listing(ps):
        ps = [str(p) for p in ps]
        assert ps, 'listing() needs at least one item; the sentences below say "No point ..." for an empty list'
        return ps[0] if len(ps) == 1 else ', '.join(ps[:-1]) + ' and ' + ps[-1]

    def points(ps, verb_one, verb_many):
        return f'Point {ps[0]} {verb_one}' if len(ps) == 1 else f'Points {listing(ps)} {verb_many}'

    # round 5 (core edit 6): since the argument's sources grew in core edits 6 and 6e no point cites only rung 1, so the sentence says that
    # and names the points that cite only sources on the record (no rung-5 source), counted here like every other number
    on_only = [p for p in cols if p != 'T' and not cellc[(p, 5)]]
    if only1:
        say1 = points(only1, 'cites only rung 1.', 'cite only rung 1.')
    else:
        say1 = 'No point cites only rung 1; ' + (points(on_only, 'cites only sources on the record (rungs 1 to 4).', 'cite only sources on the record (rungs 1 to 4).').replace('Point', 'point', 1) if on_only else 'every point cites at least one source of the lowest rung.')
    if only5:
        say5 = points(only5, 'cites only the lowest rung', 'cite only the lowest rung') + f', and so do {t5} of the {t_all} sources behind the numbers.'
    else:
        say5 = f'No point cites only the lowest rung; {t5} of the {t_all} sources behind the numbers are on it.'
    say_out = (f'{C.WORDS.get(len(outside), len(outside)).capitalize()} of the {total} sources are cited only outside the points and the table, '
               f'in the argument’s opening and in its list of what is left open (reference{"s" if len(outside) != 1 else ""} {listing([num[s] for s in outside])}).') if outside else ''

    figure = f"""
  <section class="card" id="ladder">
   <h2>The five rungs, firmest on top</h2>
   <p class="sub">Each square is one of the argument’s {total} sources. A filled square is on the record; an open one is not. Point at a square to see which source it is.</p>
   {''.join(lad)}
  </section>
  <section class="card gap" id="matrix">
   <h2>Which rung each point of the argument stands on</h2>
   <p class="sub">The argument’s {len(pts) - 1} points and its table of numbers, in its own order. A number is how many sources of that rung the point cites.
   {say1} {say5}
   {say_out}</p>
   <p class="hint">Swipe the table sideways to see every point.</p>
   <div class="scroll" tabindex="0" role="group" aria-label="Table of points against rungs; scroll sideways on a narrow screen">
{chr(10).join(mx)}
   </div>
   <p class="ptlist">{ptlist}</p>
   <p class="srcline">Counts: made by this figure’s build script from the argument’s list of sources (argument/argument_refs.tsv: {total} sources and their kinds) and its text (argument/argument_base.txt: which point cites which source). Nothing here was counted by hand. The files as counted: {B.REFS.name} sha256 {fp[B.REFS.name]}, {B.BASE.name} sha256 {fp[B.BASE.name]}. If the argument changes, run build.py again.</p>
  </section>
  <section class="care">
   <h2>Read with care</h2>
   <ul>
    <li><b>A rung says how a statement reached us, not whether it is true.</b> A document can be wrong and an unnamed person right. A quotation that was found in a saved copy shows what the source says.</li>
    <li><b>The rungs follow the argument’s own labels</b> for its {total} sources; the same source sits on one rung only. The argument has {C.WORDS[len(kinds)]} kinds of source; this figure puts its state documents and what state media and an industry body published on rung 1, filings and buyers’ own purchase notices on rung 2, officials, official records and {C.WORDS[kinds['NAMED']]} analyst’s testimony on rung 3, and reports of named people’s words or companies’ statements, and news outlets’ accounts of documents, filings or official acts, on rung 4. Rungs 1 to 4 hold exactly the kinds the argument counts as on the record. A named person’s words on rung 4 still pass through a reporter, a post or a transcript site.</li>
    <li>What the count cannot weigh: one company filing may carry more than several press reports. The count of squares is not a score.</li>
    <li>English renderings of Chinese are ours, not official translations.</li>
   </ul>
  </section>"""

    key = f"""   <ul class="key">
    <li><span class="u" aria-hidden="true"></span><span><b>Filled:</b> on the record (a document, a filing, a named person). {on} sources</span></li>
    <li><span class="u open" aria-hidden="true"></span><span><b>Open:</b> unnamed people, research firms’ counts, caption tracks or machine transcripts. {off} sources</span></li>
    <li><span>Numbers in circles are the reference numbers of the referenced argument (ARGUMENT_referenced).</span></li>
   </ul>"""

    def src_li(s):
        k = rung[s]; n = num[s]
        pin = f'<i class="p neutral {"solid" if k < 5 else "hollow"}">{n}</i>'
        a = f'<a href="{C.esc(addr[s], quote=True)}">address</a>' if addr[s] else 'no address given'
        tail = '' if s.startswith('clip-') else f' · saved copy {C.esc(s)}'
        return (f'<li id="r{n}" class="ev" data-n="{n}">{pin}<div><span class="what">{C.T(label[s])}.</span> '
                f'<span class="src">{B.KIND[refs[s]["kind"]]} · {a}{tail}</span></div></li>')

    def group(k):
        return f'<h3>Rung {k} · {RUNGS[k][0]} ({per[k]})</h3><ol>{"".join(src_li(s) for s in by_rung[k])}</ol>'

    below = f"""
 <details class="card" id="records">
  <summary><h2>The {total} sources, by rung</h2><span class="fold">show or hide</span></summary>
  <p class="sub">The reference list of the argument, sorted onto the rungs. The numbers are the argument’s own. The list starts folded (it is long); a square on the ladder opens it at its source.</p>
  <div class="cols">
   <section class="lcol">{group(1)}{group(2)}{group(3)}</section>
   <section class="lcol">{group(4)}{group(5)}</section>
  </div>
 </details>"""

    tip = {}
    for s in refs:
        tip[num[s]] = dict(w=B.KIND[refs[s]['kind']], l=f'rung {rung[s]}', t=C.smart(label[s]), q='', e='', s='', k='')
    for r in recs:
        q, e = r['Q'][0]; tip[r['n']].update(q=C.inner_quotes(q), e=e)
    page = C.page(
        title='Ladder Of Evidence',
        eyebrow=f'China · Nvidia chips · how firm each source is · {total} sources of the referenced argument',
        h1='The direction rests on documents and filings. The mechanics rest on unnamed people.',
        deck=f'The {total} sources behind the argument, sorted onto five rungs by how each statement reached us. {on} are documents, filings or named people on the record. '
             f'{off} are press reports citing unnamed people, research firms’ counts, or caption tracks and machine transcripts: they carry who told whom, and {t5} of the {t_all} sources behind the numbers.',
        key=key, figure=figure, below=below, css=CSS, tipjson=json.dumps(tip, ensure_ascii=False).replace('</', '<\\/'))
    out = C.finish(HERE, NAME, page, lines)
    with open(HERE / 'sources.tsv', 'w', encoding='utf-8') as fh:
        fh.write('ref_n\trung\trung_name\tkind\tsaved_id\tlabel\taddress\tcited_at_points\n')
        for s in sorted(refs, key=lambda s: num[s]):
            at = ','.join(pname(p) for p in cols if s in pts[p])
            fh.write(f'{num[s]}\t{rung[s]}\t{RUNGS[rung[s]][0]}\t{refs[s]["kind"]}\t{s}\t{refs[s]["label"]}\t{addr[s]}\t{at}\n')
    print(f'inputs {fp}')
    print(f'sources {total}: by kind {dict(kinds)}; per rung {[per[k] for k in range(1, 6)]}; on the record {on}, not {off}; '
          f'points citing only rung 1: {only1}; only rung 5: {only5}; numbers table: {t5} of {t_all} on rung 5; cited outside the points: {[(num[s], s) for s in outside]}; examples {len(recs)}; {summary}')
    if '--png' in sys.argv:
        C.export_png(out, [('#figure', HERE / f'{NAME}.png')])


main()
