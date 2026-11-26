#!/usr/bin/env python3
"""Write the record of the China chip-policy project as table files (idea 30).

Run: python3 -I build.py          (from any folder; it reads and writes by absolute path)

Reads   ../../../figure/figure_data.txt      the dated records: our line, the source, the source's own words, our English
        ../../../figure/figure_events.tsv    the same records with the figure's mark number, the date as shown and the address
        ../../../argument/argument_base.txt  the argument (for the order in which its sources are first cited)
        ../../../argument/argument_refs.tsv  the argument's sources: saved id, kind, label, address
        ../../../tables/*.tsv                the project's plain tables (round 4), copied into tables/ here
        ../../../loose_ends/hkexnews_saved_ids.tsv, ../../../loose_ends/terms_saved_ids.tsv (since core edit 7b),
        ../../../tables/replaced_copies.tsv  the saved ids no longer cited (Hong Kong exchange pages; copies from idc.com
                                             and trendforce.com) and their replacements
Writes  records.csv, records.tsv   one line per dated record, 16 columns
        references.csv             one line per source of the argument, 8 columns
        quotes.tsv                 saved id <TAB> the source's own words, for scripts/cn_has.py
        tables/*.tsv               byte-for-byte copies of the project's plain tables (sha256 checked after writing)
        README.txt                 what each file and column holds, with counts taken from the data

Nothing is written unless every check passes:
  - the two figure files hold the same records, one to one (date, saved id and row), and the same line of ours;
  - figure_events.tsv numbers the records as scripts/cn_figure_build.py does since core edit 7 (Nov 25, 2026): by date,
    Beijing's rows first, except a record with an "N" line in figure_data.txt, which keeps the number given there;
  - every quotation stands in its saved copy (scripts/cn_has.py on quotes.tsv, exit 0), and that checker's own control
    (a planted false quotation) is rejected; quotes.tsv is written first because it is what the checker reads;
  - the reference numbers equal those printed in ARGUMENT_referenced.md;
  - each file, read back, has the rows and columns it should; no TSV field holds a tab or a line break;
  - every copied table's sha256 equals the project's table's; rows citing a saved id that outputs/ROUND4.md section 2
    retires are counted and named in README.txt with their replacement, not changed.
All files are UTF-8 without a byte-order mark; CSV fields are quoted where they hold a comma or a quote mark.
"""
import csv, hashlib, io, re, subprocess, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parents[2]
SCRIPTS = Path('scripts')
sys.path.insert(0, str(SCRIPTS))
import cn_argument_build as B

LANE = {'BH': ('Beijing holds Nvidia back', 'Beijing', 'away from Nvidia'),
        'BL': ('Beijing lets Nvidia in', 'Beijing', 'toward Nvidia'),
        'CN': ('The companies reach for Nvidia', 'the companies', 'toward Nvidia'),
        'CH': ('The companies turn to home-made chips', 'the companies', 'away from Nvidia')}
KIND = {'doc': 'a government document or an official on the record',
        'rec': 'a company, or a named person outside government, on the record (a filing, results, a named executive or analyst)',
        'press': 'a press report citing unnamed people'}
# One plain line on each of the project's tables (ours, written from the table's own notes). The build stops if the
# project's folder holds a table that has no line here.
ABOUT = {
    'chip_evaluations.tsv': "The products in the security-and-reliability evaluation announcements saved from the China Information Technology Security Evaluation Center's site, one row per product per announcement",
    'house_licence_table.tsv': "The table of licence applications for Nvidia's H200 and AMD's MI325X, with their status on May 11, 2026, from the Commerce Department's Bureau of Industry and Security (BIS), as the House Foreign Affairs Committee made it public on Nov 19, 2026; one row per application",
    'labs_said.tsv': "What China's AI companies said about chip supply on results calls and in filings, January 2025 to November 2026",
    'labs_said_more.tsv': "The same for two more companies, iFlytek and SenseTime",
    'local_vouchers.tsv': "Local rules that pay part of the bill for computing: who issued each, when, and the rate for home-made and for other computing",
    'local_vouchers_more.tsv': "More such local rules, and other documents read about them (drafts, application notices and accounts of a rule among them), found in later searches",
    # Round 9 (Nov 25, 2026, after voucher rounds 3 to 6): five classes now; the counts and the verbs are computed (v_only_verb, v_two_verb)
    'local_vouchers_classes.tsv': "The class of every local voucher rule of the two voucher tables by the published counting rule: {v_counted} counted, of the rules found by searches that went province by province and city by city, saved and read (not a census of every local government): {v_more} pay more for home-made computing and still pay for other computing, {v_only} {v_only_verb} for home-made computing only, {v_one} pay one rate whatever the chip and {v_two} {v_two_verb} two rates by a type of computing facility that the rule does not name; {v_not} read and not counted, each with its reason. The class looks at the counted payment only: other provisions of a counted rule that give home-made computing something more are in local_vouchers_other_provisions.tsv",
    'market_numbers.tsv': "Published market numbers (shares, shipments, market sizes), one row per number. The column family names the measure; rows of different families are different measures",
    'nvidia_china_revenue.tsv': "Nvidia's revenue from customers in China, Hong Kong included, period by period, from its own filings: by the customer's billing location until its quarterly report of October 2025, and by the direct customer's headquarters from that report on, with earlier periods recast (column basis); not a count of chips that entered China",   # round 10b: the readers' lead L455
    'nvidia_wording_by_filing.tsv': "Nvidia's own words on China, from its filings and results calls, and its executives' words and its statements as others carried them",
    'press_originals.tsv': "For each press report the argument cited at an earlier build: whether the copy held is the publisher's own page or another outlet's",
    'procurement_records.tsv': "Purchase records: the telecom carriers' central purchases, awards that name Nvidia cards, and tenders that require home-made chips",
    'provinces_31.tsv': "The 31 provincial-level governments: whether a published plan sets a share for home-made computing, each by its plan's own measure (chips, equipment, hardware and software, or computing capacity), with the document's own words where its text was read. Some rows rest on accounts of a plan rather than its text, and for one government, Xinjiang, no computing plan's text was found, though its development and reform commission, in a reply posted Jul 24, 2026, says two were issued: column result gives the finding, column rests_on what it rests on, and column l16_change what a later reading changed",   # round 10b: L452, L466
    'replaced_copies.tsv': "The {all} saved pages that are no longer cited, and the copy that replaces each where one is needed: {hk} taken from the Hong Kong exchange's site and, since Nov 25, 2026, {terms} taken from idc.com and trendforce.com, whose terms bar copies made by script, so the project stopped citing them",   # round 10b: L468
    'rtx5500_notices.tsv': "Notices on the exchanges' disclosure site, Sept 14 to Nov 24, 2026, whose titles name a contract, a purchase or computing: 333 notices, 3 of which name the RTX PRO 5500",
    'state_media_items.tsv': "State and Party media items on Nvidia and its chips, July 2025 to November 2026, each with its stance",
    'talks_and_acts.tsv': "US-China trade meetings, May 2025 to November 2026, with what each side's readout says on chips, or that no written readout of that side was found, beside Beijing's dated acts and words on Nvidia chips",   # round 10b: L454
    'trade_annual_summary.tsv': "Yearly sums of monthly customs figures, series by series. No customs line counts Nvidia chips",
    'trade_derived_figures.tsv': "The sums and ratios worked out from the trade tables",
    'us_officials_statements.tsv': "Named American officials' words on China buying, blocking or bargaining over Nvidia chips. Words from caption tracks are machine-made and not checked by ear",
    'xi_searches.tsv': "The searches made of Xi Jinping's published speeches and activities, with the number of results each returned and the controls",
    # Added Nov 25, 2026 (core edit 8): eleven tables of the gap sweep, copied into tables/ under plain names.
    'rtx5500_buyers_later_notices.tsv': "Every notice of the three listed buyers of Nvidia's RTX PRO 5500 cards on the exchanges' disclosure site from Oct 1 to Nov 25, 2026 that the census of notices does not hold, with the Shenzhen exchange's letter to one of them: 26 rows, the letter among them, each with what it says on the cards",
    'procurement_notices_sweep.tsv': "Sixty-one more purchase notices and filings on AI servers and cards, 2024 to November 2026, found by later searches and kept apart from the purchase records: how each names Nvidia, what it says on imports, and whether it requires or refuses Nvidia hardware by name",
    'other_listed_buyers.tsv': "Other listed companies that in 2026 disclosed, or put out a tender for, a purchase or lease of servers with Nvidia chips, or a purchase of computing servers that was not completed",
    'purchase_notices_2024_2025.tsv': "Purchase notices of January 2024 to June 2025, the window a search of Nov 25, 2026 covered, that name the H20, H800, A800, L20 or Nvidia; one row is a company's filing and one a scanned page read by eye",
    'computing_centre_plans.tsv': "Plans, filings, bond disclosures and tenders for computing centres in mainland China that name Nvidia chips or, for comparison, home-made ones, each marked as an official page or a press account",
    'import_lists_read.tsv': "China's published lists of goods whose import needs a licence or is banned, 2024 to 2026, each searched whole for computers, computer parts and chips, with the control that shows the search could find them",
    'customs_and_tariff_texts_read.tsv': "The pages a search read for a rule on importing a graphics processor, an AI accelerator or a server (114 of them whole when it ran, 17 saved and read afterwards): China's customs and tariff announcements of January 2024 to November 2026 and what was read beside them, each with counts of chip words, customs numbers and words for licences, inspections and holds",
    'provincial_ict_plans.tsv': "The provincial communications administrations' five-year plans for their sector, searched as a class for a home-made share of computing, chips or equipment: 30 units other than Zhejiang, with what could be read for each and the control that shows the search could find a share",
    'wuhan_university_result_notices.tsv': "Result notices of purchases by filed bidding that Wuhan University's procurement centre published on its own site, June 2025 to November 2026, picked by titles on graphics cards, GPUs, servers and AI computing: 81 notices, each with its date, its price, and the Nvidia words and home-made words found on the page",
    'xi_items_database_check.tsv': "A test of how complete People's Daily Online's database of Xi Jinping's speeches and activities is: 156 items of 2023 to November 2026 taken from Xinhua's lists and Qiushi's contents for their words on chips, computing power, AI, American firms or curbs, each looked for in the database, with the verdict and how it was reached",
    'largest_records_naming_no_chip.tsv': "The ten largest award or candidate records of the procurement table that name no chip, with the rule that picked them, the routes tried for the chip and what the saved pages say, as it stood on Nov 24, 2026",
    'results_calls_word_census.tsv': "How many of 61 results-call transcripts of eight Chinese companies, February 2025 to November 2026, hold each of 20 words or word patterns (Nvidia, Huawei, H20, domestic chips, the Cyberspace Administration, customs and others), with the control word",
    'spokespeople_answers_census.tsv': "Every answer found in which a Chinese government spokesperson was asked about Nvidia chips, about American chips or about the sale of chips to China, December 2024 to September 2026, counted by one written rule: for the foreign ministry every regular press conference searched and the matching pages read twice, for the commerce ministry its regular briefings read and a search for its written answers, which is not a census",
    'state_media_baseline_2024_2025h1.tsv': "A baseline for the state-media table: state and Party media items on Nvidia chips, January 2024 to June 2025, by the same rule; gathered by other routes, not a census, and not counted in that table. {bl_group} of its rows are from papers of the People's Daily group that the state-media table never holds (their notes begin GROUP-PAPER), so a comparison with that table counts the other {bl_other}",   # round 10b: L456; counted in copy_tables()
    'state_media_baseline_outside_scope.tsv': "Items that the searches for that baseline found and left out of it, each with the reason",
    'reported_claims_outlets.tsv': "For nine claims the argument gives as reported by unnamed people: the first report, second reports with their own sources, relays, and any denial",
    'numbers_first_reports.tsv': "The numbers in the story: who first reported each among the saved pages, and how later reports changed it. In a column's name, the ledger is the project's ledger of numbers (the numbers ledger among the project's outputs)",   # round 10b: L458
    'carriers_own_notices.tsv': "What the state telecom carriers' own notices, and others' accounts of the same purchases, say about the chips in the carriers' purchases of AI computing, 2023 to November 2026: each page classed by who states it, with counts of chip words on the page",
    # Added Nov 25, 2026 (round 9 of the outputs): four tables of core edit 8b, in the words of the table helper's note (hand_out/TAB10_FOR_MAIN.txt item 3)
    'miit_texts_word_counts.tsv': "Counts of eighteen words (home-made, chip, Nvidia, three share words and others) in 54 texts that the Ministry of Industry and Information Technology published on computing, AI, electronics and telecom, 2023 to 2026, one row per saved text",
    'procurement_notices_oct_nov_2026.tsv': "Twenty-seven purchase notices for AI computing of Oct 13 to Nov 24, 2026, a reading sample: the chip words each prints, whether it names Nvidia, what it says on home-made products and imports, and whether it attaches a declaration on the home-made product standard",
    'results_calls_read.tsv': "The 61 results-call transcripts of eight Chinese companies, February 2025 to November 2026, that the word census reads: company, call, date, saved id, the site that carries the transcript, what the page says of its source and of any part made by a model, and the number of markers of passages not translated",
    # Added Nov 25, 2026 (round 10 of the outputs): the table of voucher round 7 (atlas/core_edit/hand_out/VOUCHER7_FOR_MAIN.txt; register line T219), in the words of its first lines
    'local_vouchers_other_provisions.tsv': "Provisions of the counted local voucher rules, other than the counted payment, that give home-made computing something other computing does not get: money to build, buy or run home-made computing facilities or equipment, an award or subsidy for adapting models or software to home-made chips or computing or for research built on them, a higher rate, cap or quota for using home-made computing in another provision, or a priority, purchasing preference, required share or condition in words that bind; one row per provision, each read and ruled on the rule's saved copy. A rule's class does not change by these rows: it is decided by the counted payment alone (local_vouchers_classes.tsv)",
    'results_calls_authority_counts.tsv': "Counts from a search of 118 company texts (76 results-call transcripts and 42 records of four smaller companies) for the names of Chinese authorities beside a chip word: by group and word, the hits and the hits beside a chip word, with what each of those is",
}
REC_COLS = ['n', 'date', 'date_shown', 'date_exact', 'who', 'direction', 'figure_row', 'kind', 'kind_meaning', 'on_the_record',
            'our_line', 'source', 'source_words', 'our_english', 'address', 'saved_id']
REF_COLS = ['number', 'kind', 'kind_meaning', 'on_the_record', 'label', 'page_title', 'address', 'saved_id']


def stop(msg):
    print('NOT WRITTEN: ' + msg); sys.exit(1)


def plain(s):
    """Quote marks and apostrophes in one style, so the two figure files can be compared."""
    for a, b in (('’', "'"), ('‘', "'"), ('“', '"'), ('”', '"')): s = s.replace(a, b)
    return re.sub(r'\s+', ' ', s).strip()


def read_blocks():
    out, cur = [], None
    for ln in (PROJ / 'figure' / 'figure_data.txt').read_text(encoding='utf-8').splitlines():
        if ln.startswith('@ '):
            p = ln.split()
            if len(p) != 6 or p[1] not in LANE or p[2] not in KIND: stop(f'figure_data.txt: bad record line: {ln}')
            cur = {'lane': p[1], 'kind': p[2], 'date': p[3], 'label': p[4], 'sid': p[5], 'T': '', 'S': '', 'Q': '', 'E': '', 'U': '', 'N': ''}
            out.append(cur)
        elif cur is not None and re.match(r'[TSQEUCN] ', ln):
            # N (core edit 7, Nov 25, 2026): the record's fixed number, read as scripts/cn_figure_build.py reads it
            if ln[0] == 'N' and not re.fullmatch(r'[1-9]\d*', ln[2:].strip()): stop(f'figure_data.txt: an N line that is not a number: {ln[:60]}')
            if ln[0] != 'C':
                if cur[ln[0]]: stop(f'figure_data.txt: two {ln[0]} lines in the record of {cur["date"]} {cur["sid"]}')
                cur[ln[0]] = ln[2:].strip()
        elif ln.startswith(('#', '!')) or not ln.strip():
            if ln.startswith('#') and cur is not None and 'Quotations behind the numbers' in ln: cur = None
        else:
            stop(f'figure_data.txt: a line this script does not know: {ln[:60]}')
    return out


def numbers_as_the_figure_gives_them(blocks):
    """The mark numbers as scripts/cn_figure_build.py number() gives them since core edit 7 (Nov 25, 2026): by date,
    Beijing's rows first and then the companies', except a record with an "N" line, which keeps the number given there.
    Returns {(date, saved id, lane): number}. main() stops unless figure_events.tsv carries the same numbers."""
    free = [b for b in blocks if not b['N']]
    bj = sorted([b for b in free if b['lane'][0] == 'B'], key=lambda b: b['date'])
    co = sorted([b for b in free if b['lane'][0] == 'C'], key=lambda b: b['date'])
    num = {}
    for i, b in enumerate(bj + co, 1): num[(b['date'], b['sid'], b['lane'])] = i
    for b in blocks:
        if b['N']: num[(b['date'], b['sid'], b['lane'])] = int(b['N'])
    if sorted(num.values()) != list(range(1, len(blocks) + 1)): stop('the record numbers do not run from 1 to the number of records')
    if not all(int(b['N']) > len(free) for b in blocks if b['N']): stop('a fixed number falls among the numbers given by date')
    return num


def data_lines(text):
    """(comment lines, header cells, rows as lists) of one of the project's tables."""
    com, body = [], []
    for ln in text.split('\n'):
        if ln.startswith('#'): com.append(ln)
        elif ln.strip(): body.append(ln.split('\t'))
    return com, body[0], body[1:]


# Saved ids that outputs/ROUND4.md section 2 says must no longer be cited, beyond the 20 of
# loose_ends/hkexnews_saved_ids.tsv (whose replacements are read from tables/replaced_copies.tsv): old id -> new id.
RETIRED_MORE = {
    'cn-le08-moore-final-prospectus': 'cn-le08-moore-final-prospectus-cninfo',
    'cn-le29-sensetime-2025-annual-en': 'cn-le29-sensetime-2025-annual-en-tcurl',
    'ms-bj-20260114-customs-h200-standard': 'cn-acts-reuters-customs-20260114',
    'cn-policy-ai-chip-evaluation': 'cn-le14-itsec-2026-2',
    'cn-media-yuyuan-thepaper': 'cn-le13-yuyuan-qq-20250810b',
    'cn-factions-tencent-reuters-20261120-relay1': 'cn-o36-tencent-call-20261118-sa',
    'cn-labs-zhipu-results-20260331': 'cn-le29-zhipu-results-20260331-en',
}
FIGURE_RESOURCED = {'ms-bj-20260114-customs-h200-standard', 'cn-policy-ai-chip-evaluation', 'cn-media-yuyuan-thepaper',
                    'cn-factions-tencent-reuters-20261120-relay1', 'cn-labs-zhipu-results-20260331'}


def copy_tables(num):
    """Copy the project's plain tables into tables/ here, byte for byte (round 4: the copies must equal the project's
    tables, checked by sha256 after writing). Nothing in a copy is changed. What a reader needs to know about a table's
    rows is reported in README.txt instead, computed here:
      - rows (not the makers' "#" note lines) that cite a saved id outputs/ROUND4.md section 2 retires, with the id
        that replaces it (replaced_copies.tsv itself is the list of old and new ids and is not counted);
      - press_originals.tsv, column "ref", and us_officials_statements.tsv, column "argument_cites": both describe an
        earlier build of the argument; how many rows differ from the present reference numbers is counted.
    Returns a list of dicts for the README."""
    src, dst = PROJ / 'tables', HERE / 'tables'
    retired = {}
    for ln in (src / 'replaced_copies.tsv').read_text(encoding='utf-8').splitlines():
        c = ln.split('\t')
        if ln.startswith('#') or len(c) < 2 or c[0] == 'old_id': continue
        retired[c[0]] = c[1] if c[1] and not c[1].startswith('(') else ''
    ids_of = lambda name: [ln.split('\t')[0] for ln in (PROJ / 'loose_ends' / name).read_text(encoding='utf-8').splitlines()
                           if ln.strip() and not ln.startswith('#')]
    hk_old = ids_of('hkexnews_saved_ids.tsv')
    terms_old = ids_of('terms_saved_ids.tsv')   # core edit 7b (Nov 25, 2026; atlas/ROUND8.txt R5): the copies from idc.com and trendforce.com
    listed = set(hk_old) | set(terms_old)
    if set(retired) != listed: stop(f'replaced_copies.tsv and the two lists of ids no longer cited differ: {sorted(set(retired) ^ listed)[:5]}')
    n_listed = {'all': len(retired), 'hk': len(set(hk_old)), 'terms': len(set(terms_old) - set(hk_old))}
    # core edit 8 (Nov 25, 2026): the voucher counts in the one-line description are counted from the table, not typed (they went stale at 19 and 46)
    _, vh, vrows = data_lines((src / 'local_vouchers_classes.tsv').read_text(encoding='utf-8'))
    vc = Counter(r[vh.index('class')] for r in vrows)
    # round 9 (Nov 25, 2026): the class names are the classifier's own (scripts/cn_voucher_classes.py MORE, ONLY, ONE, TWO, NOT), a fifth
    # class since voucher round 3 (Hangzhou's two rates by a type it does not name); the counts are taken from the table and must equal the
    # classifier's compute() over the two voucher tables and the saved copies (the control: a table that has gone stale stops the build)
    import cn_voucher_classes as VC
    V_CLASSES = (VC.MORE, VC.ONLY, VC.ONE, VC.TWO, VC.NOT)
    if set(vc) - set(V_CLASSES): stop(f'local_vouchers_classes.tsv: a class this script does not know: {sorted(set(vc) - set(V_CLASSES))}')
    n_listed.update(v_more=vc[VC.MORE], v_only=vc[VC.ONLY], v_one=vc[VC.ONE], v_two=vc[VC.TWO], v_not=vc[VC.NOT],
                    v_counted=vc[VC.MORE] + vc[VC.ONLY] + vc[VC.ONE] + vc[VC.TWO])
    n_listed.update(v_only_verb='pays' if n_listed['v_only'] == 1 else 'pay', v_two_verb='pays' if n_listed['v_two'] == 1 else 'pay')
    _R = VC.compute()
    _want = {'v_more': _R['n'][VC.MORE], 'v_only': _R['n'][VC.ONLY], 'v_one': _R['n'][VC.ONE], 'v_two': _R['n'][VC.TWO], 'v_counted': len(_R['counted']), 'v_not': _R['not_counted']}
    if any(n_listed[k] != v for k, v in _want.items()):
        stop(f'local_vouchers_classes.tsv counts {[(k, n_listed[k]) for k in _want]} differ from the classifier\'s {sorted(_want.items())}: run scripts/cn_voucher_classes.py --write first')
    # round 10b (Nov 25, 2026; the readers' lead L456): the baseline's rows from papers the state-media table never holds, counted from the
    # table's own flag (a note that begins GROUP-PAPER); the table's first lines give the same count in words, and the build stops if they disagree
    _, bh, brows = data_lines((src / 'state_media_baseline_2024_2025h1.tsv').read_text(encoding='utf-8'))
    _bg = sum(1 for r in brows if r[bh.index('note')].startswith('GROUP-PAPER'))
    _bhead = (src / 'state_media_baseline_2024_2025h1.tsv').read_text(encoding='utf-8')
    if f'China City News: {_bg} rows), so a comparison with that table counts the other {len(brows) - _bg}' not in _bhead:
        stop(f'state_media_baseline_2024_2025h1.tsv: {_bg} GROUP-PAPER rows of {len(brows)} by its note column, which its own first lines do not give')
    n_listed.update(bl_group=_bg, bl_other=len(brows) - _bg)
    for o, n in RETIRED_MORE.items(): retired.setdefault(o, n)
    if len(retired) != len(listed | set(RETIRED_MORE)): stop('the ids no longer cited do not add up')
    for n in set(retired.values()) - {''}:
        if not (B.L.P / n).is_dir(): stop(f'replacement copy {n} has no saved folder')
    dst.mkdir(exist_ok=True)
    out, raws = [], {}
    for f in sorted(x for x in src.glob('*.tsv') if '.before-' not in x.name):   # the core's before-copies of an edit are not tables
        raw = f.read_bytes(); text = raw.decode('utf-8'); notes = []
        com, head, rows = data_lines(text)
        if f.name != 'replaced_copies.tsv':
            hits = Counter()
            for r in rows:
                line = '\t'.join(r)
                for o in retired:
                    if re.search(re.escape(o) + r'(?![\w-])', line): hits[o] += 1
            for o, k in sorted(hits.items()):
                if o in listed: why = 'a withdrawn copy, no longer cited by the project'
                elif o in FIGURE_RESOURCED: why = 'a source the figure no longer cites'
                else: why = 'a copy the project no longer cites'
                notes.append(f'{k} row(s) cite {o}, {why}; ' + ((f'tables/replaced_copies.tsv names {retired[o]} in its place' if o in listed else
                                                                 (f'the figure cites {retired[o]} in its place' if o in FIGURE_RESOURCED else f'the project cites {retired[o]} in its place')) if retired[o] else 'it has no replacement') +   # round 10b: no working file named (L459 to L462)
                             (f'; the argument itself still cites {o} as reference {num[o]}' if o in num else ''))
        if f.name == 'press_originals.tsv':
            i_ref, i_id = head.index('ref'), head.index('saved_id_cited')
            diff = sum(1 for r in rows if r[i_ref] != str(num.get(r[i_id], '')))
            gone = sum(1 for r in rows if r[i_id] not in num)
            if diff == gone:   # the owner renumbered the column on Nov 23, 2026 (loose_ends/C6_screen/tables_refresh.py)
                notes.append(f'its column "ref" gives the present reference numbers of the argument; {gone} of the {len(rows)} rows keep a report the '
                             f'argument no longer cites (marked "not cited now"); press references added to the argument later are named in the table\'s own comment line')
            else:
                notes.append(f'its column "ref" gives reference numbers of an earlier build of the argument: {diff} of the {len(rows)} differ from '
                             f'the present numbers, and {gone} of the ids are no longer cited by the argument (references.csv has the present numbers)')
        if f.name == 'us_officials_statements.tsv':
            i_c, i_id = head.index('argument_cites'), head.index('saved_ids')
            now = sum(1 for r in rows if any(x in num for x in re.findall(r'[a-z]+-[A-Za-z0-9-]+', r[i_id])))
            if all(('[' in r[i_c]) == any(x in num for x in re.findall(r'[a-z]+-[A-Za-z0-9-]+', r[i_id])) for r in rows):   # recomputed by the owner, Nov 23, 2026
                notes.append(f'its column "argument_cites" was recomputed against the present argument (the table\'s own comment line says how): {now} of the '
                             f'{len(rows)} rows name a source it cites, with the reference number')
            else:
                notes.append(f'its column "argument_cites" describes an earlier build of the argument; by the present argument {now} of the '
                             f'{len(rows)} rows name a source it cites (references.csv has the present numbers)')
        if any(len(r) != len(head) for r in rows): stop(f'{f.name}: a row does not have {len(head)} fields')
        if f.name not in ABOUT: stop(f'{f.name}: no plain line for this table in ABOUT')
        raws[f.name] = raw
        out.append({'name': f.name, 'rows': len(rows), 'cols': head, 'notes': notes, 'about': ABOUT[f.name].format(**n_listed),
                    'sha': hashlib.sha256(raw).hexdigest()})
    stale = sorted(x.name for x in dst.glob('*') if x.name not in raws)
    if stale: stop(f'tables/ here holds files the project\'s tables folder does not: {stale} (move them aside by hand)')
    for name, raw in raws.items(): (dst / name).write_bytes(raw)
    for t in out:
        if hashlib.sha256((dst / t['name']).read_bytes()).hexdigest() != t['sha'] or \
           hashlib.sha256((src / t['name']).read_bytes()).hexdigest() != t['sha']:
            stop(f'tables/{t["name"]}: the copy\'s sha256 is not the project\'s table\'s')
    return out


def main():
    blocks = read_blocks()
    with open(PROJ / 'figure' / 'figure_events.tsv', encoding='utf-8', newline='') as fh:
        events = list(csv.DictReader(fh, delimiter='\t'))
    if len(blocks) != len(events): stop(f'{len(blocks)} records in figure_data.txt but {len(events)} in figure_events.tsv')
    by = {}
    for e in events:
        k = (e['date'], e['saved_id'], e['lane'])
        if k in by: stop(f'figure_events.tsv: two lines for {k}')
        by[k] = e
    rows, fixed = [], []
    want_n = numbers_as_the_figure_gives_them(blocks)
    for b in blocks:
        k = (b['date'], b['sid'], LANE[b['lane']][0])
        e = by.pop(k, None)
        if e is None: stop(f'no line in figure_events.tsv for {k}')
        if int(e['n']) != want_n[(b['date'], b['sid'], b['lane'])]:
            stop(f'figure_events.tsv numbers {k} as {e["n"]}, but the figure\'s rule gives {want_n[(b["date"], b["sid"], b["lane"])]}')
        if b['N']: fixed.append((int(b['N']), b['date'], e['shown_as']))
        if plain(e['text']) != plain(b['T']): stop(f'the two files give different lines of ours for {k}')
        if plain(e['source']) != plain(b['S']): stop(f'the two files give different sources for {k}')
        if e['kind'] != b['kind']: stop(f'the two files give different kinds for {k}')
        if not b['Q'] or not b['T'] or not b['S']: stop(f'a record without its line, source or words: {k}')
        if not e['address'].startswith('http'): stop(f'no address for {k}')
        if b['U'] and b['U'] != e['address']: stop(f'the address given in figure_data.txt is not the one in figure_events.tsv for {k}')
        rows.append({'n': int(e['n']), 'date': b['date'], 'date_shown': e['shown_as'], 'date_exact': 'yes' if b['label'] == '-' else 'no',
                     'who': LANE[b['lane']][1], 'direction': LANE[b['lane']][2], 'figure_row': LANE[b['lane']][0],
                     'kind': b['kind'], 'kind_meaning': KIND[b['kind']], 'on_the_record': 'no' if b['kind'] == 'press' else 'yes',
                     'our_line': b['T'], 'source': b['S'], 'source_words': b['Q'], 'our_english': b['E'],
                     'address': e['address'], 'saved_id': b['sid']})
    if by: stop(f'lines of figure_events.tsv without a record: {sorted(by)}')
    rows.sort(key=lambda r: r['n'])
    if [r['n'] for r in rows] != list(range(1, len(rows) + 1)): stop('the mark numbers are not 1 to N without gaps')
    for r in rows:
        if not re.fullmatch(r'\d{4}-\d\d-\d\d', r['date']): stop(f'bad date {r["date"]}')
        if re.search(r'[一-鿿]', r['source_words']) and not r['our_english']: stop(f'Chinese words without our English: record {r["n"]}')

    # every quotation against its saved copy, with the project's checker
    qtext = '# saved id <TAB> the source\'s own words. One line per dated record (the figure\'s mark number order). Checked by scripts/cn_has.py.\n' + \
            ''.join(f'{r["saved_id"]}\t{r["source_words"]}\n' for r in rows)
    (HERE / 'quotes.tsv').write_text(qtext, encoding='utf-8')            # the checker's input; written first, then checked
    run = subprocess.run([sys.executable, '-I', str(SCRIPTS / 'cn_has.py'), str(HERE / 'quotes.tsv')], capture_output=True, text=True)
    has_line = (run.stdout.strip().splitlines() or ['(no output)'])[-1]
    if run.returncode != 0: print(run.stdout + run.stderr); stop('cn_has.py did not pass on the quotations')

    # the argument's sources, numbered as the argument numbers them
    B.load_clip()
    refs = B.load_refs()
    bad, order, nq, nh = B.check((PROJ / 'argument' / 'argument_base.txt').read_text(encoding='utf-8').splitlines(), refs)
    if bad: stop('the argument does not pass its own check: ' + '; '.join(bad[:3]))
    printed = dict(re.findall(r'^\[(\d+)\] .*?(?:Saved copy: (\S+))?$', (PROJ / 'ARGUMENT_referenced.md').read_text(encoding='utf-8'), flags=re.M))
    ref_rows = []
    for n, sid in enumerate(order, 1):
        r = refs[sid]
        if not sid.startswith('clip-') and printed.get(str(n)) != sid: stop(f'reference {n} is {sid} here but {printed.get(str(n))} in ARGUMENT_referenced.md')
        ref_rows.append({'number': n, 'kind': r['kind'], 'kind_meaning': B.KIND[r['kind']], 'on_the_record': 'yes' if r['kind'] in B.SOLID else 'no',
                         'label': r['label'], 'page_title': '' if sid.startswith('clip-') else B.title_of(sid),
                         'address': B.address(sid, r) or '', 'saved_id': sid})
    if len(printed) != len(ref_rows): stop(f'{len(printed)} references printed in ARGUMENT_referenced.md, {len(ref_rows)} here')

    def table(cols, data, dialect):
        buf = io.StringIO()
        w = csv.DictWriter(buf, cols, delimiter='\t' if dialect == 'tsv' else ',', lineterminator='\n',
                           quoting=csv.QUOTE_NONE if dialect == 'tsv' else csv.QUOTE_MINIMAL, quotechar=None if dialect == 'tsv' else '"')
        w.writeheader(); w.writerows(data)
        return buf.getvalue()

    for r in rows + ref_rows:
        for k, v in r.items():
            if isinstance(v, str) and re.search(r'[\t\r\n]', v): stop(f'a tab or line break inside the field {k}: {v[:40]}')
    out = {'records.csv': table(REC_COLS, rows, 'csv'), 'records.tsv': table(REC_COLS, rows, 'tsv'),
           'references.csv': table(REF_COLS, ref_rows, 'csv')}

    # read each table back before anything is written
    back_csv = list(csv.DictReader(io.StringIO(out['records.csv'])))
    back_tsv = [dict(zip(REC_COLS, ln.split('\t'))) for ln in out['records.tsv'].splitlines()[1:]]
    back_ref = list(csv.DictReader(io.StringIO(out['references.csv'])))
    want = [{k: str(v) for k, v in r.items()} for r in rows]
    if back_csv != want or back_tsv != want: stop('records.csv or records.tsv does not read back as written')
    if back_ref != [{k: str(v) for k, v in r.items()} for r in ref_rows]: stop('references.csv does not read back as written')

    tabs = copy_tables({sid: n for n, sid in enumerate(order, 1)})
    kinds_used = [k for k in B.KIND if any(r['kind'] == k for r in ref_rows)]
    kind_lines = '\n'.join(f'                 {k}: {B.KIND[k]}' for k in kinds_used)
    solid_used = [k for k in kinds_used if k in B.SOLID]; open_used = [k for k in kinds_used if k not in B.SOLID]
    clip_ids = [r['saved_id'] for r in ref_rows if r['saved_id'].startswith('clip-')]
    tab_lines = []
    for t in tabs:
        tab_lines.append(f'  tables/{t["name"]}   {t["rows"]} rows, {len(t["cols"])} columns')
        tab_lines.append(f'      What it is: {t["about"]}.')
        tab_lines.append(f'      Columns: {", ".join(t["cols"])}')
        tab_lines.append(f'      Copy: byte for byte the project\'s table (sha256 {t["sha"]}).')
        for nt in t['notes']: tab_lines.append(f'      Read with care: {nt}.')
    tab_block = '\n'.join(tab_lines)
    n_tab_noted = sum(1 for t in tabs if t['notes'])
    c_who = Counter((r['who'], r['direction']) for r in rows); c_kind = Counter(r['kind'] for r in rows)
    c_ref = Counter(r['kind'] for r in ref_rows)
    n_cn = sum(1 for r in rows if r['our_english']); n_approx = sum(1 for r in rows if r['date_exact'] == 'no')
    n_noaddr = sum(1 for r in ref_rows if not r['address'])
    n_extra = sum(1 for ln in (PROJ / 'figure' / 'figure_data.txt').read_text(encoding='utf-8').splitlines() if ln.startswith('! '))
    fixed.sort()
    if not fixed: n_note = ''
    elif len(fixed) == 1: n_note = (f';\n                 record {fixed[0][0]} ({fixed[0][2]}), added after the figure was made public, keeps the next\n'
                                    f'                 free number (the "N" line of figure_data.txt), so it stands out of date order')
    else: n_note = (f';\n                 records {", ".join(str(f[0]) for f in fixed[:-1])} and {fixed[-1][0]}, added after the figure was made public, keep the next\n'
                    f'                 free numbers (the "N" lines of figure_data.txt), so they stand out of date order')
    n_cn_solid = sum(1 for r in rows if r['our_english'] and r['kind'] != 'press')
    cn_note = 'all of them documents or people on the record' if n_cn_solid == n_cn else f'{n_cn_solid} of them documents or people on the record'
    readme = f"""The record as table files
China chip policy: did Beijing's chip policy pull against China's own AI companies?
Draft by Claude, Anthropic's model.

Made by build.py in this folder from the project's own files (figure/figure_data.txt, figure/figure_events.tsv,
argument/argument_base.txt, argument/argument_refs.tsv, tables/). Run "python3 -I build.py" to make them again.
All files are UTF-8 without a byte-order mark. In a spreadsheet program, open them through its import step and
choose UTF-8, or the Chinese will not show correctly.

FILES
  records.csv      {len(rows)} dated records, {len(REC_COLS)} columns, comma-separated
  records.tsv      the same {len(rows)} records, tab-separated (no field holds a tab or a line break)
  references.csv   the {len(ref_rows)} sources of the argument (ARGUMENT_referenced.md), {len(REF_COLS)} columns
  quotes.tsv       saved id and the source's own words for each record: the input of the quotation check
  tables/          {len(tabs)} plain tables copied from the project's tables folder (listed at the end)
  build.py         the script

COLUMNS OF records.csv AND records.tsv
  n              the record's mark number in the figure (figure/beijing_vs_labs.html), 1 to {len(rows)}. The files are in
                 number order. Numbers go by date, Beijing's rows first, then the companies'{n_note}
  date           the date as year-month-day. The date of the act where the page gives it, otherwise of the report
  date_shown     the date as the figure prints it
  date_exact     yes, or no where the source gives only a season or a month and the day in "date" is a placing
                 for the figure, not a fact ({n_approx} records: see date_shown)
  who            whose conduct the record is about: Beijing, or the companies. It is not who speaks: see source
  direction      toward Nvidia, or away from Nvidia (Beijing holding Nvidia back, or the companies turning to home-made chips)
  figure_row     the figure's own name for the row the record stands in
  kind           doc, rec or press
  kind_meaning   doc: {KIND['doc']}
                 rec: {KIND['rec']}
                 press: {KIND['press']}
  on_the_record  yes for doc and rec; no for press
  our_line       our one-line summary, as shown in the figure. Our words, not the source's
  source         the source as the figure names it
  source_words   the source's own words, exact. Chinese where the page is Chinese
  our_english    our English for Chinese source words. Ours, not an official translation. Empty where the
                 source words are English ({n_cn} records have it)
  address        where the page is, or was, on the web
  saved_id       the name of the saved copy (research/primary/<saved_id>)

COLUMNS OF references.csv
  number         the reference number in ARGUMENT_referenced.md, 1 to {len(ref_rows)}
  kind           one of: {", ".join(kinds_used)}
  kind_meaning   what each kind means, in the words that begin each reference of the argument's reference list:
{kind_lines}
  on_the_record  yes for {", ".join(solid_used)}; no for {", ".join(open_used)}
  label          what the source is, as the argument's reference list words it
  page_title     the saved page's own title, where the record holds one
  address        the address; empty where none is given, for the reason in the label ({n_noaddr} source)
  saved_id       the name of the saved copy. An id that begins "clip-" is not a folder ({", ".join(clip_ids) or "none here"}): it
                 stands for a machine transcript in transcripts_two_clips.md, which nobody has checked by ear

COUNTS (taken from the files by build.py, not typed)
  Records: {len(rows)}. About Beijing, away from Nvidia: {c_who[('Beijing', 'away from Nvidia')]}. About Beijing, toward Nvidia: {c_who[('Beijing', 'toward Nvidia')]}.
  About the companies, toward Nvidia: {c_who[('the companies', 'toward Nvidia')]}. About the companies, away from Nvidia: {c_who[('the companies', 'away from Nvidia')]}.
  By kind: doc {c_kind['doc']}, rec {c_kind['rec']}, press {c_kind['press']}. So {c_kind['doc'] + c_kind['rec']} records are on the record and {c_kind['press']} are press reports citing unnamed people.
  References: {len(ref_rows)}. {", ".join(f"{k} {c_ref[k]}" for k in kinds_used)}.
  On the record: {sum(c_ref[k] for k in solid_used)}. Press reports citing unnamed people, counts, captions or machine transcripts: {sum(c_ref[k] for k in open_used)}.

CHECKS THE SCRIPT MADE BEFORE WRITING
  The two figure files hold the same {len(rows)} records, one to one, with the same line of ours.
  The mark numbers are those the published figure gives its marks (by date; a record with an "N" line keeps its number).
  scripts/cn_has.py on quotes.tsv: {has_line}
  (its control, a planted quotation that is not in the saved copy, was rejected, as it must be)
  The reference numbers equal those printed in ARGUMENT_referenced.md.
  Each table was read back and equals what was written.

READ WITH CARE
  A quotation that is found shows what the source says, not that it is true.
  The two tiers are not the same kind of evidence. A press record (kind press) rests on unnamed people. Beijing's
  instructions to companies, the customs checks and most of the numbers are of that kind: reported, not published policy.
  One company's annual report says on the record that the cyberspace regulator asked Chinese technology companies in
  September 2025 to halt purchases of certain chips; it does not name Nvidia (the argument, point 11).
  A record in a Beijing row can be the words of someone else about Beijing (a company's filing, a US official).
  {n_cn} records quote Chinese texts ({cn_note}); the English beside them is ours.
  Not in these files: the {n_extra} further checked lines of the figure's data file, most of them the quotations
  behind the numbers in the figure's panels (they are in
  figure/figure_data.txt, on the lines that begin with "!"), and the reference lists of the two tier files.

PLAIN TABLES (tables/)
  These {len(tabs)} tables were made from Nov 23 to Nov 25, 2026 by the project's research agents, each from saved pages, and are
  the project's own (the folder tables/ beside the argument). They are copied here so that the record can be read in
  a spreadsheet. All {len(tabs)} are byte for byte the project's tables (build.py compares each copy's sha256 with the
  project's after writing; each is given below). Nothing in them is changed here. Their quotations were checked by the
  agents who made them, not again here.
  The tables were made before the argument's last rebuild: a table can cite a saved copy the argument has since
  replaced with a better one (the argument's reference list is the later word). Under {n_tab_noted} of the tables a
  "Read with care" line says which rows cite a saved copy the project no longer cites, and which column describes an
  earlier build of the argument; all such lines are computed by build.py. Rows of different tables count
  different things. Do not join them into one series. Each table begins with its makers' own notes, on lines that
  start with "#"; a program reading a table should skip those lines.

{tab_block}
"""
    out['README.txt'] = readme
    for name, text in out.items():
        (HERE / name).write_text(text, encoding='utf-8')
    print(f'records: {len(rows)} rows x {len(REC_COLS)} columns (csv and tsv); references: {len(ref_rows)} rows x {len(REF_COLS)} columns')
    print(f'cn_has.py: {has_line}')
    print(f'numbers: as the figure gives them (by date; kept by an N line: {", ".join(str(f[0]) for f in fixed) or "none"})')
    print(f'kinds: doc {c_kind["doc"]}, rec {c_kind["rec"]}, press {c_kind["press"]}; with our English: {n_cn}; dates that are placings: {n_approx}')
    print(f'tables: {len(tabs)} copied, all byte for byte (sha256 of each copy equals the project\'s); rows in all: {sum(t["rows"] for t in tabs)}')
    for t in tabs:
        for nt in t['notes']: print(f'  read with care: {t["name"]}: {nt}')


if __name__ == '__main__':
    main()
