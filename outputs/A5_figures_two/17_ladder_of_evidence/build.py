"""Build the figure "The ladder of evidence": the argument's sources on five rungs, and which rung each point stands on.

Run: python3 -I build.py                                   counts, checks every quotation, writes the page and sources.tsv
     python3 -I build.py --png   the same, then exports ladder_of_evidence.png
Counts come from two files of the project, never from typing:
  ../../argument/argument_refs.tsv   the argument's sources and their kinds  -> sources per rung
  ../../argument/argument_base.txt   the argument's text with saved ids       -> which point cites which source
Kinds to rungs (round 4: the argument has eleven kinds; its own builder counts all but PRESS, COUNT and CLIP as on the record):
  1 DOC, PUB      Chinese state documents and published commentary, reports or statements by state media, industry bodies or research institutes
  2 FIL, NOTICE   company filings and statements, and institutions' own published purchase notices
  3 OFF, NAMED    officials, official records, a named analyst's written testimony and a named executive's post
  4 REC, ACCT     press reports naming their source: a named person's words, a company's statement (round 8: the argument's
                  REC rows include company statements, among them Nvidia's statement as two news sites carried it, The
                  Standard and the Daily Caller News Foundation, edit 7c), or a named news outlet's account of a document, a filing
                  or an official act (round 9: the core's label for ACCT was widened in core edit 8b, and a Reuters factbox made
                  from tender documents and company statements became ACCT)
  5 PRESS, COUNT, CLIP   press reports citing unnamed people, research or broker figures, and captions or transcripts not checked by ear
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
ARGUMENT = C.PROJ / 'ARGUMENT_referenced.md'
RUNG_OF = {'DOC': 1, 'PUB': 1, 'FIL': 2, 'NOTICE': 2, 'OFF': 3, 'NAMED': 3, 'REC': 4, 'ACCT': 4, 'PRESS': 5, 'COUNT': 5, 'CLIP': 5}
RUNGS = {  # name, what sits on it, what it shows about this claim, what it does not show ({SM} is filled in from tables/state_media_items.tsv)
    1: ('Chinese state documents and published material', 'texts of the Chinese party-state and its bodies, and published commentaries, reports or statements by state media, industry bodies and research institutes (including China Telecom’s AI institute and the Shenzhen Loop Area Institute)',
        'The declared line: end dependence on foreign core technology and use home-made chips. The purchase rules for government buying, the provincial targets, '
        'the antitrust case and the summons. A Shanghai government body’s own statement that internet companies’ own clusters in the city run mainly on Nvidia. '
        'State media warned in public. {SM} A Party paper also printed a scholar’s advice to stock imported chips.',
        'Any order telling companies not to buy Nvidia chips. None was found in the 82 policy pages read. The commentaries warn and urge; none forbids.'),
    2: ('Company filings and statements, and buyers’ own notices', 'what companies told securities regulators, exchanges and investors: filings, results releases, the company’s own transcript of a results call; and buyers’ own purchase notices (among them universities, a hospital, research institutes, government bodies, telecom carriers, postal buyers, financial institutions and other companies)',
        'Alibaba told the US securities regulator that the cyberspace regulator asked Chinese technology companies to halt purchases of certain chips. Nvidia told it that the Chinese government restricted customers’ purchases, a word its later reports changed to discouraged, '
        'and that its licensed sales were restricted; the same reports say it is effectively foreclosed from the China market by US export controls. On its own results calls Nvidia said in May 2026 '
        'that it had no revenue yet from the licensed H200 chips, and in November 2026 that it had sold $2.4 billion of licensed Hopper products to China in a quarter and was no longer shipping. '
        'Alibaba also says its own chips are in scaled production. Listed Chinese firms told the Shenzhen exchange of purchases of cards named PRO 5500. '
        'One university’s notice reports buying two Nvidia cards. A tender site carries Shanghai Jiao Tong University’s preliminary procurement intention to rent six to eight servers with eight cards each. It is not yet a tender. Some central buyers’ notices of November 2026 ask for home-made computing. An award of April 2025 by the purchasing centre for central state bodies, for a university’s IT centre, names Nvidia H20 modules under a tender that allowed no imported products. {CARRIERS} Three notices show different ways buyers set terms tied to the security-and-reliability evaluation: China Post’s Shandong branch, in purchase requirements it put out for comment, asks that the accelerator cards pass it, if results for such cards are published before the bids close; Shanghai Pudong Development Bank asks for GPU chips that meet the requirements of its category for AI training and inference chips; and a unit of China Southern Power Grid asks the AI card modules of one lot to meet the requirements of its guide. A hospital tender awards points for proof of passing the evaluation.',
        'Who gave an instruction about Nvidia chips, or how it was given. Alibaba’s sentence names the cyberspace regulator and no chip maker, and does not say how the request was made. Nvidia gave no reason for stopping. A notice to buy is not a purchase made, and a contract is not a delivery.'),
    3: ('Officials, official records and named people', 'named officials, in their own body’s account, a state news agency’s, or a transcript of the hearing or event (the body’s or the host’s own, or a transcript service’s, such as Rev’s or Factba.se’s); official records, most of them American (hearings, reports, rules, the licence table); an analyst’s written testimony and an executive’s own post about his company’s AI model',
        'American officials give their own understanding. The US Commerce Secretary, Howard Lutnick, gave these as his understanding: “my understanding is their cloud companies want to buy these chips” and “Chinese central government has not let them as of yet buy the chips because they’re trying to keep their investment focused on their own domestic industry”. American bodies read Beijing’s acts as leverage in trade talks, or as a push for more advanced chips. Washington’s own licence table, giving the status of applications as of May 11, 2026, marks every approved application not shipped. '
        'Chinese officials stand on both sides in public: the state planner says it is guiding home-made models to do more to adapt to home-made chips; a vice premier and the commerce minister welcome Nvidia, and the premier tells American firms, Nvidia’s among them, that an open policy is a lasting commitment; asked about the reports, spokespeople confirm nothing.',
        'Any Chinese official saying that purchases were stopped.'),
    4: ('Press reports of on-the-record words and acts', 'a named person’s words at a hearing, on a results call (one report gives an answer on Tencent’s call to an executive it does not name), on television or in a post, a company’s statement, or a named news outlet’s account of a document, a filing or an official act, as a news outlet (its own transcripts included, such as CNBC’s), a post or a transcript site gives them',
        'The Treasury Secretary’s view that Chinese orders were few. A Tencent executive’s answer that put a shortage of chips partly down to policy restrictions on certain foreign-designed GPUs being brought into China; he does not say whose policy, and the transcripts differ on which executive spoke. '
        'And the companies’ own turn to home-made chips, in their executives’ words.',
        'The words as first spoken, checked against a recording. Each of these passes through a reporter, a post, a transcript site or a news outlet’s own transcript of its programme; the speaker labels of the Tencent transcripts are the site’s and are unchecked.'),
    5: ('Unnamed sources, research figures and unchecked transcripts', 'press reports citing unnamed people, figures from research firms, brokers or research groups, and caption tracks or transcripts that nobody has checked by ear',
        'Who told whom, and when: the guidance not to buy, the warning about traitors, the customs checks, the split inside Beijing. Estimates of how many chips Chinese companies were reported to have ordered and how many Beijing was reported to approve, as well as reported deliveries and stock figures; '
        'the counts single buyers give of their own purchases are on rung 2. Research firms’ figures on Nvidia’s market share and that of other foreign suppliers. KZ Consulting presents figures whose underlying source it does not name. The clip that raised the question, and the Trade Representative’s words on Bloomberg Television and a Bloomberg podcast and the Treasury Secretary’s on two Bloomberg programmes, in caption tracks or transcripts.',
        'Confirmation by Beijing. In the answers found, Beijing’s spokespeople confirmed none of these reports.'),
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



# Only these identified work titles take single quote marks. A different span,
# even on the same reference, remains a quotation for the page check.
LABEL_TITLES = {
    'cn-usdocs-hfac-decisions-20261119': 'H200 License and Equivalent Application Status as of May 11, 2026',
    'cn-le01-greer-bbg-20260515-subs-ttml': 'Greer: US, China Willing to Continue Trade Truce',
    'cn-ga05-shanghai-digital-15fyp-20260728': 'Digital Shanghai',
    'cn-ga02-gt-isnt-buying-opinion-202611': "China 'isn't buying' Nvidia chips. Why are some Americans so rattled?",
    'man-cn-ft-20250821-regulators': 'China turns against Nvidia’s AI chip after ‘insulting’ Howard Lutnick remarks',
    'cn-usdocs-house-kratsios-20260114': "Advancing America's AI Action Plan",
    'cn-usdocs-fr-remote-20261119': 'Addressing Remote Access to Advanced Semiconductors',
    'cn-tolerate-draft': "China's new export curbs draw a line around its AI crown jewels",
    'man-cn-ft-202508-deepseek': 'DeepSeek’s next AI model delayed by attempt to use Chinese chips',
    'cn-usside-071': 'Kimi K2.5: Visual Agentic Intelligence',
    'cn-ga31-smalllabs-46': 'How We Scaled Kimi K2.5',
    'cn-ga31-smalllabs-18': 'Step-3 is Large yet Affordable: Model-system Co-design for Cost-effective Decoding',
    'cn-ga31-smdailiesp3-57': 'DeepSeek unveils AI model for domestic chips in symbolic break from Nvidia reliance',
    'cn-ga31-counter-13': 'Global Premiere | SLAI Achieves Full-Parameter Post-Training of DeepSeek-V4-Pro on Domestic Computing Cluster',
    'cn-ga08-arxiv-telechat-xing4-pdf': 'TeleChat to Xing4',
    'cn-ga08-arxiv-telechat2-report-pdf': 'Technical Report of TeleChat2, TeleChat2.5 and T1',
    'cn-ga31-companies-14': '国产大模型用上全国产算力',
    'cn-ga31-smalllabs-17': '面壁智能联合清华正式开源中国首个基于昇腾训练的 1.58-bit 端侧大模型 BitCPM-CANN',
    'cn-media-party-samr-september': '市场监管总局：坚持党建引领 践行监管为民',
    'cn-le03-select-buywhat-pr': "Buy What It Can, Steal What It Must: China's Campaign to Acquire Frontier AI Capabilities",
    'cn-usdocs-select-rigging-game-report': 'Rigging the Game',
    'cn-le03-select-rigging-page': 'Rigging the Game',
    'cn-factions-information-20240513-sopa': 'Chinese Regulators Tell Local Tech Firms to Buy Fewer Nvidia Chips',
    'cn-le11-ft-h20justify-aggregoctt': 'China tells Alibaba, ByteDance to justify purchases of Nvidia AI chips',
    'cn-counter-b5-1': "Nvidia's roller coaster for China AI chips takes a new turn",
    'man-cn-ft-20251009-customs': 'China launches customs crackdown on Nvidia AI chips',
    'man-e2596eab15f4': 'Jensen Huang’s years-long effort to get close to China',
    'cn-acts-bloomberg-jan8': 'China to Approve Nvidia H200 Buying as Soon as This Quarter',
    'cn-tolerate-ftaug26': 'China eases limits on Nvidia H200 chips as AI race escalates',
    'cn-labs-tencent-marchcall': '全文|腾讯Q4业绩会实录',
    'cn-le04-standard-900000-20261120': 'US signed off on sales of nearly 900,000 AI chips to China in six months, committee says',
    'cn-tolerate-ifp': 'How to Increase America’s AI Lead Over China',
    'cn-ga01-ft-cards-20261013-wayback': 'China faces uphill battle to wean tech firms off Nvidia chips',
    'cn-ga02-cd-h20-lackluster-20250812': "Demand for Nvidia's H20 chip lackluster",
    'cn-le10-h20-price-20240201-yahoofin': "Exclusive-Nvidia's new China-focused AI chip set to be sold at similar price to Huawei product",
    'cn-against2-wsj-h20-reluctance-20240108': "Slower Nvidia Chip Out in Q2 But China Firms 'Don't Want It'",
    'cn-usside-048': "Trump officials torpedoed Nvidia's push to export AI chips to China",
    'cn-ga07-kaine-crec-html-s8884-2': 'Nvidia',
    'cn-o34-nvidia-export-page': 'NVIDIA Parts Classification',
}


def reference_label(sid, label):
    title = LABEL_TITLES.get(sid)
    if title:
        escaped = re.escape(title)
        label = re.sub(rf'"{escaped}"|“{escaped}”', f'‘{title}’', label, count=1)

    # The argument's quoted English glosses are printed beside the exact
    # words in the original language here. The page checks those words.
    if sid == 'cn-ga09-sina-tencent-q1call-hk-20260514':
        label = label.replace('"a Tencent executive"', '“腾讯高管” (a Tencent executive)', 1)
    if sid == 'cn-ga31-importcat-43':
        label = label.replace('(the "first line")', '(“一线”, the first line)', 1)
    return label


def check_reference_label_quotes(lines):
    sid = 'cn-tolerate-ifp'
    title = LABEL_TITLES[sid]
    plain = 'A reference label with no title'
    assert reference_label(sid, plain) == plain
    for left, right in (('"', '"'), ('“', '”')):
        heading = f'{left}{title}{right}'
        assert C.page_quotes_ok(C.T(reference_label(sid, heading)), lines) == 0
        sourced = f'{heading}. It says {left}Chinese regulators are reportedly reviewing whether this demand is necessary{right}.'
        assert C.page_quotes_ok(C.T(reference_label(sid, sourced)), lines) == 1
        for control_sid, prefix in ((sid, heading + '. '), ('control-without-title', '')):
            invented = 'A made-up statement in a label must fail this check'
            rendered = C.T(reference_label(control_sid, f'{prefix}{left}{invented}{right}'))
            try:
                C.page_quotes_ok(rendered, lines)
            except SystemExit as exc:
                assert invented in str(exc), str(exc)
            else:
                raise AssertionError('The page quote check missed an invented statement in a reference label')
    print('reference label controls: known title styled, sourced statement accepted, invented statement rejected with or without a title (straight and curly quotes)')


def main():
    allrefs = B.load_refs()                    # since round 4 it also returns rows of argument_refs_more.tsv, flagged opt: not the argument's own
    fp ={p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:12] for p in (B.REFS, B.REFS_MORE, B.BASE)}      # which bytes were counted
    base = [ln for ln in B.BASE.read_text(encoding='utf-8').splitlines() if not ln.startswith('!!')]
    # round 10: a row of argument_refs_more.tsv (flagged opt) that the argument's text now cites is one of its sources, as the argument's own
    # builder counts it (Reuters, Jan 8, 2026, at point 15: its last build line counts 460 sources); an uncited opt row is not
    cited = {sid for ln in base for sid in B.CITE.findall(ln)}
    refs = {s: r for s, r in allrefs.items() if not r.get('opt') or s in cited}
    # the argument's own reference numbers: the order of first citation
    num = {}
    for ln in base:
        for sid in B.CITE.findall(ln):
            num.setdefault(sid, len(num) + 1)
    assert set(num) == set(refs), 'the argument cites exactly the sources of its references file'
    rung = {sid: RUNG_OF[r['kind']] for sid, r in refs.items()}
    per = Counter(rung.values()); kinds = Counter(r['kind'] for r in refs.values())
    total = len(refs); on = sum(per[k] for k in (1, 2, 3, 4)); off = per[5]
    built_counts = re.findall(
        r'were looked for in the saved copies of (\d+) sources and all were found[.;].*? (\d+) sources are .*?; (\d+) are',
        ARGUMENT.read_text(encoding='utf-8').splitlines()[-1])
    assert built_counts == [(str(total), str(on), str(off))] and on + off == total, (total, on, off, built_counts)

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
    # Each label must identify a buyer class before the build describes the new notices.
    buyer_prefixes = (
        ('purchasing centre', ('Purchasing centre for central state bodies',)),
        ('carrier', ('China Mobile', 'China Telecom', 'China Unicom', 'Unicom Digital Technology',
                     'A Jiangsu company that bears China Unicom')),
        ('drug regulator', ('Center for Medical Device Evaluation',)),
        ('evaluation examples', ("China Post Group's Shandong branch", 'Shanghai Pudong Development Bank',
                                 'CSG Digital Grid Research Institute')),
        ('postal buyer', ('China Post Group',)),
        ('other companies', ('Baosight Software', 'China Southern Power Grid', 'China Tower')),
        ('research institute', ('The 722nd Research Institute', 'Institute of AI, Hefei', 'Henan Academy of Medical Sciences')),
        ('hospital', ('Beijing Anzhen Hospital',)),
        ('local government', ('Shanghai Fengxian District Big Data Center', 'Song County Public Security Bureau',
                              'Zhoukou Municipal Health Commission', 'Nanjing Municipal Public Security Bureau')),
        ('finance', ('China Foreign Exchange Trade System', 'China Cinda Asset Management')),
        ('news agency', ('China News Service',)),
        ('masked buyer', ('Award notice for computing cards',)),
    )
    nclass = Counter()
    for label in notices:
        kind = next((c for c, prefixes in buyer_prefixes if label.startswith(prefixes)), None)
        if kind is None and 'Universit' in label.split(',')[0]:
            kind = 'university'
        assert kind is not None, label
        nclass[kind] += 1
    assert nclass == {'university': 14, 'carrier': 12, 'local government': 4, 'evaluation examples': 3,
                      'research institute': 3, 'other companies': 3, 'purchasing centre': 2, 'postal buyer': 2,
                      'finance': 2, 'drug regulator': 1, 'hospital': 1, 'news agency': 1, 'masked buyer': 1}, nclass
    assert refs['cn-ga31-evaltedumedp2-19']['kind'] == 'NOTICE'
    assert all(refs.get(s, {}).get('kind') == 'NOTICE' for s in ('cn-ga31-evaluation-35', 'cn-ga31-evaluation-25', 'cn-ga31-evaluation-22'))
    # round 10 (the core's batch of 20:58 UTC, Nov 25, 2026, row AP10-23): the award notice's label now names its issuer as the tender document's does,
    # so two labels begin with the centre's name: its tender document and its award, both of GC-HGX250062 (rung 2's words give both as the centre's)
    _pc = sorted(l for l in notices if l.startswith('Purchasing centre for central state bodies'))
    assert len(_pc) == 2 and sum('tender document' in l for l in _pc) == 1 and sum('award notice' in l for l in _pc) == 1 and all('GC-HGX250062' in l for l in _pc), _pc
    assert all(refs.get(s, {}).get('kind') == 'NOTICE' for s in ('cn-ga31-h20notices-7', 'cn-ga31-h20notices-19', 'cn-ga31-operators-63', 'cn-ga31-operators-7', 'cn-ga31-operators-32'))      # the award naming H20 modules, its tender document, and three carrier notices the words of rung 2 rest on
    assert {f for f in ('IDC', 'TrendForce') if any(f in l for l in lab_of('COUNT'))} == {'IDC', 'TrendForce'}, lab_of('COUNT')                                   # research firms' counts (two firms)
    assert all(refs.get(s, {}).get('kind') == 'FIL' for s in ('cn-filings-tianyang-20261013-contract', 'cn-le08-youzu-contract-20261104', 'cn-ga01-hzyl-contract-20261112'))   # listed firms' notices of PRO 5500 purchases: rung 2
    assert all(refs.get(s, {}).get('kind') == 'NOTICE' for s in ('cn-ga13-nwpu-som-88690-wayback', 'cn-ga13-ccgp-nmpa-cmde-ai-rental-27742397', 'cn-ga13-ccgp-pku-inference-card-27734000'))
    assert {s for s, r in refs.items() if r['kind'] == 'NAMED'} == {
        'cn-usdocs-uscc-hearing-20250206', 'cn-ga31-smalllabsp2-17'}
    assert kinds['ACCT'] >= 2
    # round 12 (work list 27): rung 1's words name two research institutes; their three sources are PUB, and so are three industry bodies' (plural in the words)
    assert all(refs.get(s, {}).get('kind') == 'PUB' for s in ('cn-ga31-counter-13', 'cn-ga08-gh-teleai-telechat2-page', 'cn-ga08-arxiv-telechat2-report-pdf'))
    assert sum(bool(re.search(r'Association|Internet Society', l)) for l in lab_of('PUB')) >= 2, lab_of('PUB')
    _, media_summary = C.state_media_summary()
    RUNGS[1] = RUNGS[1][:2] + (RUNGS[1][2].replace('{SM}', media_summary),) + RUNGS[1][3:]
    assert '{' not in RUNGS[1][2]
    extra_counts = {
        'cn-ga31-associationsp2-32': ('KZ Consulting', 'the source of the aggregates is not named'),
        'cn-ga31-brokerscnp3-9': ('CCID Consulting', 'its count'),
        'cn-counter-b18-3': ('Mitsui', 'citing Bernstein'),
    }
    for sid, words in extra_counts.items():
        assert refs[sid]['kind'] == 'COUNT' and all(w in refs[sid]['label'] for w in words), sid
    assert all(s in extra_counts or re.search(r'the research firm (IDC|TrendForce|Bernstein)\b', r['label'])
               for s, r in refs.items() if r['kind'] == 'COUNT'), lab_of('COUNT')
    clip = lab_of('CLIP')
    # round 10 (code change 7 of atlas/core_edit/hand_out/SF1_FOR_MAIN.txt, after rows SF1-007 and SF1-009): two labels name Bloomberg Television (the
    # Trade Representative's); the Treasury Secretary's two are Bloomberg's Balance of Power and Bloomberg Surveillance (rung 5's words)
    bess = [l for l in clip if 'Bessent' in l]
    assert sum('Bloomberg Talks (a Bloomberg podcast)' in l for l in clip) == 1 and sum('Bloomberg Television' in l for l in clip) >= 2, clip
    assert len(bess) == 2 and sum('Balance of Power' in l for l in bess) == 1 and all('Bloomberg Surveillance' in l for l in bess) and not any('Bloomberg Television' in l for l in bess), bess
    # round 9 (core edit 8b): the carriers' own notices, as the argument now words them, and how many of their pages name Nvidia, counted from
    # tables/carriers_own_notices.tsv (its classes of a carrier's own notice, filing or news page and a site's record of a notice); the control is
    # that the same column finds Nvidia words on press rows of the table
    cn_rows = C.table('carriers_own_notices.tsv')
    OWN = ("carrier's own notice", "a tender site's account of the notice", "carrier's own page", "carrier's own filing")
    own = [r for r in cn_rows if r['who_states'].startswith(OWN)]
    pages = {r['saved_id'] for r in own}; named = {r['saved_id'] for r in own if r['nvidia_words_on_page'] != 'none'}
    ctl = [r for r in cn_rows if r['who_states'].startswith('press') and r['nvidia_words_on_page'] != 'none']
    jiangsu = 'cn-ga31-carrierown-14'
    shenzhen = 'cn-ga31-carrierownp3-23'
    assert named == {jiangsu, shenzhen} and ctl, (len(pages), named, len(ctl))
    assert refs[jiangsu]['kind'] == 'NOTICE' and refs[shenzhen]['kind'] == 'DOC'
    claim = "claim_as_read (the first reading's correction where partly)"
    shenzhen_row, = (r for r in own if r['saved_id'] == shenzhen)
    jiangsu_row, = (r for r in own if r['saved_id'] == jiangsu)
    assert all(words in shenzhen_row[claim] for words in ('Shenzhen company', 'software services', "tender site's copy", 'specifies no chip purchase or card origin')), shenzhen_row
    assert jiangsu_row['date'] == '2024-09-23' and all(words in jiangsu_row[claim] for words in ("the notice names no owner", "China Unicom's procurement and tendering site", 'elastic rental of AI computing')), jiangsu_row
    # Point 5 counts these notices, one filing and one news page apart from the two that name Nvidia or its cards.
    cls = Counter(next(o for o in OWN if r['who_states'].startswith(o)) for r in {r['saved_id']: r for r in own if r['saved_id'] not in named}.values())
    assert (cls["carrier's own filing"], cls["carrier's own page"]) == (1, 1), cls
    # round 11 (work list B 52): the argument's point 5 counts, by script over the saved pages, the pages that ask for nothing of the kind;
    # the number is read from the argument's own sentence and checked against the table
    m_least = re.findall(r'At least (\d+) of the (\d+) ask for nothing of the kind', B.BASE.read_text(encoding='utf-8'))
    assert len(m_least) == 1 and int(m_least[0][1]) == len(pages) - len(named), (m_least, len(pages) - len(named))
    least = int(m_least[0][0])
    carrier_count = len(pages) - len(named)
    carrier_summary = (
        f'None of the {carrier_count} carrier notices, filing and news page counted in point 5 names Nvidia or an Nvidia model. '
        f'Some ask for home-made chips or name a software ecosystem. At least {least} of the {carrier_count} ask for neither and set no rule on origin. '
        f'{C.WORDS[len(named)].capitalize()} other notices name Nvidia or its cards. In 2024 a Jiangsu company that bears China Unicom’s name asked to rent computing '
        'on NV RTX 3090, NV RTX 4090 and NV Tesla A100 cards. It published its tender on China Unicom’s procurement site. The notice names no owner. '
        'In a copy on a tender site, China Unicom’s Shenzhen company seeks software services compatible with Nvidia GPUs and Ascend NPUs. The notice specifies no chip purchase or card origin.'
    )
    RUNGS[2] = RUNGS[2][:2] + (RUNGS[2][2].replace('{CARRIERS}', carrier_summary),) + RUNGS[2][3:]
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
    check_reference_label_quotes(lines)
    label = {sid: reference_label(sid, r['label']) for sid, r in refs.items()}
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
        if k == 5: extra_count = f'<span>sources: {kinds["PRESS"]} press reports, {C.T(B.KIND["COUNT"])} ({kinds["COUNT"]}), {kinds["CLIP"]} caption tracks or machine transcripts</span>'
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
    say_out = (f'{str(C.WORDS.get(len(outside), len(outside))).capitalize()} of the {total} sources are cited only outside the points and the table, '
               f'in the argument’s opening and in its list of what is left open (reference{"s" if len(outside) != 1 else ""} {listing([num[s] for s in outside])}).') if outside else ''

    figure = f"""
  <section class="card" id="ladder">
   <h2>The five rungs, by how each statement reached us, the most direct on top</h2>
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
   <p class="srcline">Counts: made by script from the argument’s list of its {total} sources and their kinds, and from its text (which point cites which source). Nothing here was counted by hand.</p>
  </section>
  <section class="care">
   <h2>Read with care</h2>
   <ul>
    <li><b>A rung says how a statement reached us, not whether it is true.</b> A document can be wrong and an unnamed person right. A quotation that was found in a saved copy shows what the source says.</li>
    <li><b>The rungs follow the argument’s own labels</b> for its {total} sources; the same source sits on one rung only. The argument has {C.WORDS[len(kinds)]} kinds of source; this figure puts its state documents and what state media, industry bodies and research institutes published on rung 1, filings and buyers’ own purchase notices on rung 2, officials, official records and named people’s own statements on rung 3, and reports of named people’s words or companies’ statements, and news outlets’ accounts of documents, filings or official acts, on rung 4. Rungs 1 to 4 hold exactly the kinds the argument counts as on the record. A named person’s words on rung 4 still pass through a reporter, a post, a transcript site or a news outlet’s own transcript.</li>
    <li>What the count cannot weigh: one company filing may carry more than several press reports. The count of squares is not a score.</li>
    <li>English renderings of Chinese are ours, not official translations.</li>
   </ul>
  </section>"""

    key = f"""   <ul class="key">
    <li><span class="u" aria-hidden="true"></span><span><b>Filled:</b> on the record (rungs 1 to 4: state documents, published commentaries and reports, filings and institutions’ notices, officials and official records, named people’s words and news outlets’ accounts of documents or acts). {on} sources</span></li>
    <li><span class="u open" aria-hidden="true"></span><span><b>Open:</b> unnamed people, figures from research firms, brokers or research groups, and unchecked captions or transcripts. {off} sources</span></li>
    <li><span>Numbers in circles are the argument’s own reference numbers.</span></li>
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
  <p class="sub">The reference list of the argument, sorted onto the rungs. The numbers are the argument’s own. Each entry ends with the id of the saved copy{C.T(B.SAVED_ID_WHERE)}; the clips have none. The list starts folded (it is long); a square on the ladder opens it at its source.</p>
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
        eyebrow=f'China · Nvidia chips · how each source reached us · {total} sources of the referenced argument',
        h1='The direction of Beijing’s policy, toward home-made chips, rests on documents and filings. The unpublished guidance rests mostly on unnamed people.',
        deck=f'The {total} sources behind the argument, sorted onto five rungs by how each statement reached us. {on} are documents, filings or named people on the record (including institutional notices, published commentary, reports and statements, and named outlets’ accounts of documents or acts). '
             f'{off} are press reports citing unnamed people, figures from research firms, brokers or research groups, and unchecked captions or transcripts: they carry who told whom, and {t5} of the {t_all} sources behind the numbers.',
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
