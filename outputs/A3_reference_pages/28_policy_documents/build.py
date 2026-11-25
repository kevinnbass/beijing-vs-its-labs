#!/usr/bin/env python3
"""Build the searchable page of the policy documents read for the China chip-policy project (idea 28).

Run: python3 -I build.py            (from any folder; it reads and writes by absolute path)

Reads   ../../../NOTE_policies_checked.md      the checked note: 103 policy lines, each read in its saved page
        ../../../policies_checked_quotes.tsv   the note's own table of quotations (row, saved id, verdict, words, form)
        research/primary/<id>/                 the saved copies (read only): page titles, and every string checked below
Writes  quotes.tsv              saved id <TAB> exact words: every passage shown, every date word shown, every quoted
                                string kept in quotation marks in the check notes
        policy_documents.html   the page (one file; plain JavaScript; no outside library)
        expected.json           the counts the page must show for a few searches (read by test_page.py)

The page is not written unless all of this holds:
  - the note parses into exactly the rows its own count table gives, each with a body, an address and a verdict;
  - the passages in the note are the same strings, row by row, as in the note's table of quotations;
  - every Chinese passage has our English beside it in the note;
  - scripts/cn_has.py passes on quotes.tsv (exit 0; its planted false quotation is rejected).
What the script decides and what it only carries over:
  - dates: the list's date; where the list had none, the date the note found in the page. The script then looks for
    the date in the saved copy in the usual written forms and shows the words it found, or says it found none;
  - a string between quotation marks inside the note's "body" or "verdict" lines is kept in quotation marks only when
    cn_has.py can find it in the saved copy; otherwise it is set in italics (the note's own English, a short word,
    or a reading the note made by eye). One word the note quotes as the list's own wording, which also happens to
    stand in the saved page, is set in italics too (LANE_WORDS);
  - the note's descriptions of the issuing body and its check notes are carried over as written;
  - our English is the note's, with double quotation marks taken out (our own English carries none).
  - the passage shown first on a line is the note's first passage of 20 characters or more (so a bare document number
    or date does not stand as the key sentence); the line's other passages open under it.
"""
import html, json, re, subprocess, sys, unicodedata
from collections import Counter, OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parents[2]
SCRIPTS = Path('scripts')
sys.path.insert(0, str(SCRIPTS))
import cn_argument_build as B

L = B.L
NOTE = PROJ / 'NOTE_policies_checked.md'
QTSV = PROJ / 'policies_checked_quotes.tsv'
OUT = HERE / 'policy_documents.html'

MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
MONTH = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# Dates the list left out. Each is stated by the note, in its section "Smaller points"; the words in the second
# place must stand in the note or the build stops.
UNDATED = {'33': ('2025-12-30', '33 (Dec 30, 2025)'), '43': ('2025-11-05', '43 (Nov 5, 2025)'), '45': ('2024-04-08', '45 (translation dated Apr 8, 2024)'),
           '78': ('2017-10-23', '78 (Oct 23, 2017)'), '83': ('2026-07-28', '83 and 84 (July 28, 2026)'), '84': ('2026-07-28', '83 and 84 (July 28, 2026)'),
           '85': ('2026-03-24', '85 (Mar 24, 2026)'), '101': ('2025-06-03', '101 (June 3, 2025)')}
# Date words read in the saved copy by this folder's author where the usual forms are not on the page (the page
# gives the day without the year in one place and the year in another). Every string goes through cn_has.py.
DATE_WORDS = {'5': ['新华社北京9月6日电', 'n1/2022/0907'],
              '58': ['新华社北京4月17日电', '2025年04月18日'],
              '34': ['中共中央政治局4月25日下午', '2025-04-27'],
              '35': ['中共中央政治局4月25日下午', '2025-04-27'],
              '11': ['7月17日,商务部部长王文涛会见', '2025-07-18'],
              '89': ['新华社北京12月31日电', '2026年01月01日'],
              '33': ['SINGAPORE, Dec 30 (Reuters)', 'news-html/20251230']}
# One date the note did not find and this folder's author read in the page: the city government's signing line.
FOUND_HERE = {'71': ('2017-04-17', ['上海市人民政府 2017年4月17日'])}

KIND_LABEL = OrderedDict([('official', 'Official text'), ('company', 'Company filing or statement'), ('press', 'Press report'),
                          ('carried', 'Official text or figure, carried by a news outlet'),
                          ('roadmap', "Advisory committee's roadmap, on a third party's site"),
                          ('translation', "Think tank's translation of a government text")])
GROUP = {'official': 'official', 'company': 'company', 'press': 'press', 'carried': 'other', 'roadmap': 'other', 'translation': 'other', 'local': 'local'}
GROUP_LABEL = OrderedDict([('all', 'All'), ('official', 'Official texts'), ('company', 'Company filings and statements'), ('press', 'Press reports'), ('other', 'Other'),
                           ('local', 'Local rules and provincial plans')])
TABLES = PROJ / 'tables'
# Round 4: where the note's English for a passage differs from the core's corrected wording for the same Chinese
# (loose_ends/L23_chinese_review/CHINESE_REVIEW.md; argument/argument_base.txt), the page uses the core's. List line ->
# (the note's words, the core's words). The build stops if a pair no longer matches the note.
EN_FIX = {
    '74': [('Core internet technology is our greatest vital gate, and dependence on others for core technology is our greatest hidden danger.',
            "The internet's core technology is our greatest weak point, and having core technology controlled by others is our greatest hidden danger.")],
    '58': [('More American companies, Nvidia included, are welcome to work the Chinese market in depth',
            'More American firms, Nvidia among them, are welcome to put down deeper roots in the Chinese market')],
    '11': [('We hope multinational companies, Nvidia included, will provide Chinese customers with quality, reliable products and services.',
            'We hope multinationals, Nvidia among them, will give Chinese customers high-quality, reliable products and services.')],
    '90': [('guiding home-made large models to step up adaptation to home-made computing chips',
            'guiding home-made large models to do more to adapt to home-made computing chips')],
    # Round 9 (Nov 25, 2026): two renderings the official record corrected in core edit 8b (its rows Frr02-021 and Frr07-019), which the
    # checked note still holds in their earlier words; the page takes the record's words
    '85': [('the share of intelligent computing, the rate of home-made equipment and the regional concentration',
            'the share of intelligent computing, the home-made rate and the regional concentration')],
    '91': [('to build research, production and operating centres in China',
            'to build research and development, production and operating centres in China')],
}
EN_SRC = {'74': 'argument', '58': 'argument', '11': 'argument', '90': 'argument', '85': 'record', '91': 'record'}   # round 9: whose corrected wording each line takes
# Round 4: the commission's page names Li Chao and his office (李超 2026/05/22 政研室) and does not call him spokesperson
# (loose_ends/L23_chinese_review, A12). Words of a note body or a table row replaced on this page; the build stops if
# one is not met exactly once.
BODY_FIX = [('State planner (NDRC), Li Chao of its policy research office (政研室; this page does not call him spokesperson), press conference transcript.',   # the owner corrected the note itself on Nov 23, 2026; the page's line is unchanged
             'State planner (NDRC), Li Chao of its policy research office, press conference transcript.'),
            ('国家发展改革委 (NDRC), spokesman Li Chao, as reported by Xinhua on gov.cn',
             '国家发展改革委 (NDRC), Li Chao of its policy research office, as reported by Xinhua on gov.cn'),
            ("as reproduced by ChinaStor, a trade site; the centres' own page is not saved.",
             "on the first centre's own site (the note read a trade site's reproduction; the centres' own page was saved later).")]
# Round 4 (outputs/ROUND4.md, section 2): a note line whose saved copy the project no longer cites is shown as read in
# the replacement copy, after the cross-check with the note's table (which stays as the note wrote it). Every passage and
# date word of the line must stand in the replacement, or the build stops. List line -> (new id, address, words shown).
REPOINT = {'60': ('cn-le14-itsec-2026-2', 'http://www.itsec.gov.cn/aqkkcp/cpgg/202605/t20260526_259396.html',
                  "the centres' own page (the note read a trade site's reproduction, cn-policy-ai-chip-evaluation, which the project no longer cites)")}
# Round 4 (outputs/ROUND4.md, section 3, item 3): a rule repealed by a later one is shown with that fact, checked in
# the later rule's saved copy. (table, row) -> (saved id of the later rule, its words, the note shown).
REPEALED = {('local_vouchers.tsv', 8): ('cn-le28-etown-29hao-20241126', '原政策(京技管发〔2024〕10号)同时废止',
            "Repealed. The zone's rule of Nov 26, 2024 (京技管发〔2024〕29号) says the former policy, No. 10 of 2024, is repealed at the same time, and pays 30% of the bill whatever the chip. The rates of up to 40% and up to 30% here are not the rule in force.")}
# Core edit 7b (Nov 25, 2026): words of a note's check note that name the project's own working files, replaced on this
# page by what they mean. List line -> [(the note's words, the page's words)]; the build stops if one is not met once.
REMARK_FIX = {'55': [('on the new copy (loose_ends/GA21_replacements/quotes.tsv, cn_has.py exit 0).',
                      'Confirmed on the new copy: the script found its passages in the saved page.')]}
# Core edit 8 (Nov 25, 2026): words of a table's cell that name the project's own working files, helpers or tools, replaced on this page by what
# they mean (the tables' own cells are unchanged: they are the session's). (table, row) -> [(the cell's words, the page's words)]; the build stops
# if one is not met exactly once, and stops if a line from the tables still shows such a word (WORKING below; control in local_lines()).
COPY_FIX = {}      # Nov 25, 2026 (the session): the ten cells this map reworded now hold those plain words in the tables themselves, so the page and the tables say the same; a new working word in a printed cell still stops the build
WORKING = re.compile(r"loose_ends|\bL\d\d\b|\bGA\d\d\b|this folder|WebFetch|cn_has|check_extracted|\bthe session\b|\.py\b")
RESULT = {'share': 'sets a share for home-made computing hardware', 'plan_no_share': 'a plan that was read sets no such share',
          'account_only': "known only from accounts of it, its issuer's own among them", 'not_reached': 'no computing plan was found'}


def table_rows(name):
    ls = [l for l in (TABLES / name).read_text(encoding='utf-8').split('\n') if l.strip() and not l.startswith('#')]
    h = ls[0].split('\t')
    rows = [dict(zip(h, l.split('\t'))) for l in ls[1:]]
    if any(len(l.split('\t')) != len(h) for l in ls[1:]): stop(f'tables/{name}: a row does not have {len(h)} fields')
    return rows


def local_lines():
    """Round 4: the local voucher rules and provincial plans of tables/provinces_31.tsv, local_vouchers.tsv and
    local_vouchers_more.tsv, as lines of a sixth kind. A passage is shown only where cn_has.py can find it in a saved
    copy named on the row (Word and zip copies cannot be read by it); a voucher row with no such passage is left out and
    counted. A province row is always shown (its result is the point), with its passages where they are found."""
    out, left, fixed_rows = [], [], set()
    if not WORKING.search("text made in L15's folder") or WORKING.search('合肥市 (Hefei city), agent measures'): stop('WORKING: the control of the working-word screen fails')
    for name, wk, sk in (('provinces_31.tsv', 'exact_words', 'saved_ids'), ('local_vouchers.tsv', 'words', 'saved_id'),
                         ('local_vouchers_more.tsv', 'words', 'saved_id')):
        for i, r in enumerate(table_rows(name), 1):
            sids = [x for x in re.split(r'[\s;,]+', r[sk]) if x and (L.P / x).is_dir()]
            qs = []
            for part in re.split(r'\s*\|\|\s*|\s+/\s+', r[wk]):
                part = re.sub(r'\s*\([A-Za-z][^()]*\)\s*$', '', part.strip()).strip().strip('"').strip('“”').strip()   # a bracketed note of the table's own, in English, is not the page's
                if len(L.squash(part)) < 6: continue
                sid = next((x for x in sids if L.has(part, x)), None)
                if sid: qs.append({'words': part, 'sid': sid})
            prov = name == 'provinces_31.tsv'
            if not qs and not prov:
                left.append(f'{name} row {i}'); continue
            when = r['documents_issuers_dates'] if prov else r['date']
            m = re.search(r'(20\d\d)-(\d\d)-(\d\d)', when)
            iso = m.group(0) if m else ''
            if not iso:
                m = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)[a-z]*\.? (\d{1,2}), (20\d\d)', when)
                if m: iso = f'{m.group(3)}-{[x[:3] for x in MON].index(m.group(1)[:3]) + 1:02d}-{int(m.group(2)):02d}'
            ns = lambda v: 'not stated' if v.strip() in ('', '-') else v.strip()
            if prov:
                who = f"{r['government']}: {RESULT[r['result']]}"
                reading = f"{RESULT[r['result']]}" + (f"; in the plan: {r['binding_or_expected']}" if r['binding_or_expected'].strip() else '')
                desc = r['documents_issuers_dates']
                extra = r['rests_on']
            else:
                who = r['body']
                reading = f"home-made computing: {ns(r['rate_home'])}; other computing: {ns(r['rate_other'])}; kind: {ns(r['kind'])}"
                desc = f"{r['document']}. Date as the table gives it: {r['date']}" if r['document'] else f"Date as the table gives it: {r['date']}"
                extra = r['copy'].strip()
            for old_, new_ in COPY_FIX.get((name, i), []):
                if extra.count(old_) != 1: stop(f'COPY_FIX: tables/{name} row {i}: "{old_}" stands {extra.count(old_)} times in the cell, not once')
                extra = extra.replace(old_, new_); fixed_rows.add((name, i))
            for cell_ in (who, reading, desc, extra):
                if WORKING.search(cell_): stop(f'tables/{name} row {i}: a cell this page prints holds a working word ("{WORKING.search(cell_).group(0)}"): add its plain words to COPY_FIX: {cell_[:160]}')
            out.append({'table': name, 'trow': i, 'prov': prov, 'result': r.get('result', ''), 'level': r.get('level', ''), 'iso': iso, 'who': who,
                        'reading': reading, 'desc': desc, 'extra': extra, 'quotes': qs, 'sids': sids or [x for x in re.split(r'[\s;,]+', r[sk]) if x]})
    if fixed_rows != set(COPY_FIX): stop(f'COPY_FIX: rows not met: {sorted(set(COPY_FIX) - fixed_rows)}')
    return out, left


def voucher_counts():
    """Round 5: the voucher counts the 'Read with care' box prints, taken from the argument's own sentence
    (argument/argument_base.txt, point 3) and checked against a count by script, which also gives the names. Stops if
    they differ. Core edit 8 (Nov 25, 2026): the count by script is the project's table of classes,
    tables/local_vouchers_classes.tsv (made by scripts/cn_voucher_classes.py --write from the two voucher tables by the
    published rule). Until then it was the output of core edit 6's count script
    (atlas/core_edit/edit6_parts/vcount_as_stands.out), which is fixed at the tables' size of that day (two fewer rules) and
    no longer describes them: two more rules are counted since (Xiamen's and Xinjiang's)."""
    arg = (PROJ / 'argument' / 'argument_base.txt').read_text(encoding='utf-8')
    # Round 9 (Nov 25, 2026; voucher rounds 3 to 6): the argument's sentence now names what the count is (rules found by searches that went province by
    # province and city by city, not a census), four rules that pay for home-made computing only, and a third class of two kinds (one rate; Hangzhou's
    # two rates by a type of facility it does not name). The page prints the argument's own numbers and names, each checked against the table of classes.
    m = re.search(r'(\d+) of the (\d+) found by searches that went province by province and city by city, saved and read \(not a census of every local government\), '
                  r'pay more for home-made computing and still pay for other computing, (\d+), those of ([^()]+?), pay for home-made computing only, and (\d+) state no higher rate '
                  r'for home-made computing: (\d+) of them pay one rate whatever the chip, and one, (\w+)\'s, pays (\d+)% or (\d+)% by a type of computing facility that it does not name', arg)
    if not m: stop("the argument's voucher sentence (point 3) was not found in the words this builder expects")
    t, n, h = int(m.group(1)), int(m.group(2)), int(m.group(3)); home_arg = m.group(4); third, o = int(m.group(5)), int(m.group(6))
    two_name, two_a, two_b = m.group(7), m.group(8), m.group(9)
    cls = table_rows('local_vouchers_classes.tsv')
    TI, HO, ONE, TWO, NOT = ('pays more for home-made and still pays for other computing', 'pays for home-made computing only', 'one rate',
                             'two rates by a type of computing facility that the rule does not name', 'read and not counted')
    cc = Counter(r['class'] for r in cls)
    if set(cc) != {TI, HO, ONE, TWO, NOT}: stop(f'tables/local_vouchers_classes.tsv has a class this builder does not know: {sorted(cc)}')
    n_rows = len(table_rows('local_vouchers.tsv')) + len(table_rows('local_vouchers_more.tsv'))
    if len(cls) != n_rows: stop(f'tables/local_vouchers_classes.tsv has {len(cls)} rows; the two voucher tables have {n_rows}: run scripts/cn_voucher_classes.py --write')
    got = (cc[TI] + cc[HO] + cc[ONE] + cc[TWO], cc[TI], cc[HO], cc[ONE] + cc[TWO], cc[ONE], cc[TWO])
    if got != (n, t, h, third, o, 1): stop(f'the argument says {t}/{h}/{third} ({o} one rate, 1 two rates) of {n}; the table of classes says {got}')
    tn = sorted(r['government'] for r in cls if r['class'] == TI); hn = sorted(r['government'] for r in cls if r['class'] == HO)
    two = [r['government'] for r in cls if r['class'] == TWO]
    if len(tn) != t or len(hn) != h or not all(x in home_arg for x in hn) or two != [two_name]:
        stop(f'names from the table of classes do not match the argument: {tn} {hn} / "{home_arg}" {two} / {two_name}')
    counted = [r['government'] for r in cls if r['class'] != NOT]
    if len(set(counted)) != len(counted): stop('a government is counted twice in the table of classes')
    return {'n': n, 'tiered': t, 'home': h, 'third': third, 'one': o, 'tiered_names': ', '.join(tn), 'home_arg': home_arg,
            'two_name': two_name, 'two_a': two_a, 'two_b': two_b, 'not': cc[NOT]}


def voucher_class_of():
    """Round 9 (Nov 25, 2026): each voucher line says whether the published counting rule counts it, as the project's table of classes
    gives it (row A<i> is row i of tables/local_vouchers.tsv, row B<i> row i of tables/local_vouchers_more.tsv). (table, row) -> words.
    Stops unless every row of the two tables has its class row, in order, and the class row's saved id is one the voucher row names."""
    cls = table_rows('local_vouchers_classes.tsv')
    out = {}
    for name, p in (('local_vouchers.tsv', 'A'), ('local_vouchers_more.tsv', 'B')):
        for i, r in enumerate(table_rows(name), 1):
            c = [x for x in cls if x['row_id'] == f'{p}{i}']
            if len(c) != 1: stop(f'tables/local_vouchers_classes.tsv: {len(c)} rows for {p}{i}')
            c = c[0]
            if c['saved_id'] and c['saved_id'] not in re.split(r'[\s;,]+', r['saved_id']): stop(f'tables/local_vouchers_classes.tsv row {p}{i}: its copy {c["saved_id"]} is not named by tables/{name} row {i}')
            if c['class'] == 'read and not counted':      # the table's row ids (A<i>, B<i>) in a reason are given as the rows of the two tables this page names
                why = re.sub(r'\(row ([AB])(\d+)\)', lambda m_: f'(row {m_.group(2)} of tables/{"local_vouchers.tsv" if m_.group(1) == "A" else "local_vouchers_more.tsv"})', c['reason'])
                if re.search(r'\b[AB]\d+\b', why): stop(f'a row id of the table of classes is left in a reason: {why}')
                out[(name, i)] = f'No: {why}'
            elif c['class'] in ('one rate', 'two rates by a type of computing facility that the rule does not name'):
                out[(name, i)] = f'Yes; it states no higher rate for home-made computing ({c["class"]})'
            else: out[(name, i)] = f'Yes; it {c["class"]}'
    if len(out) != len(cls): stop('the table of classes has rows the two voucher tables do not')
    return out


def stop(msg):
    print('NOT WRITTEN: ' + msg); sys.exit(1)


def esc(s):
    return html.escape(s, quote=True)


def show_date(iso):
    p = iso.split('-')
    if len(p) == 3: return f'{MON[int(p[1]) - 1]} {int(p[2])}, {p[0]}'
    if len(p) == 2: return f'{MON[int(p[1]) - 1]} {p[0]}'
    return iso


def date_forms(iso):
    p = iso.split('-'); y, m = int(p[0]), int(p[1])
    if len(p) == 3:
        d = int(p[2])
        return [f'{y}年{m}月{d}日', f'{y}年{m:02d}月{d:02d}日', f'{y}-{m:02d}-{d:02d}', f'{y}/{m:02d}/{d:02d}', f'{y}.{m:02d}.{d:02d}',
                f'{MONTH[m - 1]} {d}, {y}', f'{MONTH[m - 1][:3]} {d}, {y}', f'{d} {MONTH[m - 1]} {y}', f'{y}-{m}-{d}', f'{y}/{m}/{d}']
    return [f'{y}年{m}月', f'{MONTH[m - 1]} {y}', f'{y}-{m:02d}', f'{y}年{m:02d}月']


def has_cjk(s):
    return bool(re.search(r'[㐀-鿿]', s))


def parse_kinds(note):
    m = re.search(r'^\*\*Kinds of source\.\*\* (.*)$', note, flags=re.M)
    if not m: stop('the note has no "Kinds of source" paragraph')
    text = m.group(1)
    if not text.startswith('Most rows are official texts. '): stop('the "Kinds of source" paragraph does not begin as expected')
    kinds = {}
    for clause in text[len('Most rows are official texts. '):].rstrip('.').split(';'):
        head = re.split(r' (?:are|is) ', clause.strip(), maxsplit=1)
        if len(head) != 2: stop(f'kinds of source: a clause this script cannot read: {clause[:60]}')
        nums = re.findall(r'\d+', head[0]); what = head[1]
        if what.startswith('press reports'): k = 'press'
        elif what.startswith('official texts or figures as carried by news outlets'): k = 'carried'
        elif what.startswith('company filings or company statements'): k = 'company'
        elif what.startswith("an advisory committee's roadmap"): k = 'roadmap'
        elif what.startswith("a think tank's translation"): k = 'translation'
        else: stop(f'kinds of source: a kind this script does not know: {what[:60]}')
        for n in nums:
            if n in kinds: stop(f'kinds of source: row {n} is named twice')
            kinds[n] = k
    return kinds


def parse_note():
    note = NOTE.read_text(encoding='utf-8')
    kinds = parse_kinds(note)
    main, tail = note.split('\n## Counts by verdict', 1)
    counts = dict(re.findall(r'^\| (CONFIRMED|CONFIRMED IN PART|NOT IN THE PAGE|PAGE EMPTY|NOT HELD|All) \| (\d+) \|$', tail, flags=re.M))
    rows = []
    for part in re.split(r'^### ', main, flags=re.M)[1:]:
        lines = part.rstrip().splitlines()
        m = re.fullmatch(r'Row (\d+) · (\S+) · (FOR|AGAINST|context) · \[([^\]]+)\]', lines[0].strip())
        if not m: stop(f'a heading this script cannot read: {lines[0][:80]}')
        r = {'row': m.group(1), 'date0': m.group(2), 'sid': m.group(4), 'quotes': [], 'read_sid': m.group(4), 'read_note': ''}
        for ln in lines[1:]:
            if ln.startswith('- Body: '): r['body'] = ln[8:].strip()
            elif ln.startswith('- Address: '): r['addr'] = ln[11:].strip()
            elif ln.startswith("- The lane's claim: "): r['claim'] = ln[20:].strip()
            elif ln.startswith("- The lane's claim, as the new carrier words it: "): r['claim'] = ln[49:].strip()   # core edit 7b (Nov 25, 2026): a row re-read in another carrier's page
            elif ln.startswith('- The copy first read for this row, '):
                # core edit 7b (Nov 25, 2026; atlas/ROUND8.txt R5): the first copy is no longer cited; the note's sentence is shown without its
                # reference to the project's own files, and the build stops if the sentence does not read as expected
                c = re.fullmatch(r'- (The copy first read for this row, .*?, is no longer cited) \(ROUND8 R5; tables/replaced_copies\.tsv\)\.', ln)
                if not c: stop(f'row {r["row"]}: a "copy first read" line this script cannot read')
                r['first_copy'] = c.group(1) + '. The line was checked again in the copy named below: its passages and date words are that page\'s.'
            elif ln.startswith('- Verdict: '):
                v = re.fullmatch(r'\*\*([A-Z ]+)\*\*\.?\s*(.*)', ln[11:].strip())
                if not v: stop(f'row {r["row"]}: a verdict this script cannot read')
                r['verdict'], r['remark'] = v.group(1), v.group(2).strip()
            elif ln.startswith('- Read in: '):
                c = re.fullmatch(r'- Read in: (an Internet Archive capture of [A-Z][a-z]+ \d+, \d{4}), saved as \[([^\]]+)\]\. .*', ln)
                if not c: stop(f'row {r["row"]}: a "Read in" line this script cannot read')
                r['read_note'], r['read_sid'] = c.group(1), c.group(2)
            elif ln.startswith('- The page'):
                q = re.fullmatch(r'- The page( \(in the page body; not in the text copy\))?: "(.*)"', ln)
                if not q: stop(f'row {r["row"]}: a passage line this script cannot read: {ln[:70]}')
                r['quotes'].append({'words': q.group(2), 'form': 'body' if q.group(1) else 'page', 'en': ''})
            elif ln.startswith('  - My translation: '):
                if not r['quotes'] or r['quotes'][-1]['en']: stop(f'row {r["row"]}: a translation without its passage')
                r['quotes'][-1]['en'] = re.sub(r'["“”]', '', ln[20:]).strip()          # our own English carries no quote marks
            elif ln.strip():
                stop(f'row {r["row"]}: a line this script does not know: {ln[:70]}')
        for k in ('body', 'addr', 'claim', 'verdict'):
            if k not in r: stop(f'row {r["row"]}: no {k}')
        if not r['addr'].startswith('http'): stop(f'row {r["row"]}: the address is not a web address')
        r['kind'] = kinds.pop(r['row'], 'official')
        rows.append(r)
    if kinds: stop(f'kinds of source names rows that are not in the note: {sorted(kinds)}')
    got = Counter(r['verdict'] for r in rows)
    for k, v in counts.items():
        if k != 'All' and got.get(k, 0) != int(v): stop(f'the note counts {v} rows {k}; this script read {got.get(k, 0)}')
    if len(rows) != int(counts['All']): stop(f'the note counts {counts["All"]} rows; this script read {len(rows)}')
    if len({r['row'] for r in rows}) != len(rows): stop('a row number stands twice')

    # the one row whose first copy was a refusal page: the note's addendum reads it in a second copy
    empty = [r for r in rows if r['verdict'] == 'PAGE EMPTY']
    add = re.search(r'\n## Addendum by the main session[^\n]*\n\n(.*)', note, flags=re.S)
    if len(empty) != 1 or not add: stop('expected one PAGE EMPTY row and the addendum that reads it in another copy')
    a = re.search(r'Row (\d+) \([^)]*\) was PAGE EMPTY above\. The same article is now saved from (a radio station\'s site that carries Reuters) \[([^\]]+)\] \((https?://\S+)\)\. '
                  r'Verdict: \*\*CONFIRMED\*\*\. The page\'s words: "(.*?)"; "(.*?)" This is reporting', add.group(1))
    if not a or a.group(1) != empty[0]['row']: stop('the addendum does not read as expected')
    e = empty[0]
    e.update(verdict='CONFIRMED', second=True, read_sid=a.group(3), read_note='a second copy, ' + a.group(2), addr2=a.group(4),
             remark='The page first saved was a refusal page. The same article was then read in a second copy, and the line was confirmed there.',
             quotes=[{'words': a.group(5), 'form': 'page', 'en': ''}, {'words': a.group(6), 'form': 'page', 'en': ''}])
    for key, (iso, words) in UNDATED.items():
        if words not in note: stop(f'the note does not say "{words}" (the date used for row {key})')
    return rows, note


def cross_check(rows):
    """The passages parsed from the note must be the strings in the note's own table of quotations, row by row."""
    table = {}
    for ln in QTSV.read_text(encoding='utf-8').splitlines()[1:]:
        c = ln.split('\t')
        if len(c) != 5: stop(f'policies_checked_quotes.tsv: a line without five fields: {ln[:60]}')
        table.setdefault(c[0], []).append((c[1], c[3], c[4]))
    n = 0
    for r in rows:
        if r.get('second'):
            if r['row'] in table: stop(f'row {r["row"]} was a refusal page but has lines in the table of quotations')
            continue
        mine = [(r['read_sid'], q['words'], q['form']) for q in r['quotes']]
        if mine != table.get(r['row'], []): stop(f'row {r["row"]}: the passages in the note are not those in its table of quotations')
        n += len(mine)
    return n


def set_dates(rows):
    for r in rows:
        r['date_from'] = 'list'
        if r['date0'] == 'undated':
            if r['row'] in UNDATED: r['iso'], r['date_from'] = UNDATED[r['row']][0], 'page'
            elif r['row'] in FOUND_HERE: r['iso'], r['date_from'] = FOUND_HERE[r['row']][0], 'here'
            else: r['iso'] = ''
        else:
            if not re.fullmatch(r'\d{4}-\d\d(-\d\d)?', r['date0']): stop(f'row {r["row"]}: a date this script cannot read: {r["date0"]}')
            r['iso'] = r['date0']
        r['date_words'] = []
        if not r['iso']: continue
        if r['row'] in DATE_WORDS: r['date_words'] = DATE_WORDS[r['row']]
        elif r['row'] in FOUND_HERE: r['date_words'] = FOUND_HERE[r['row']][1]
        else:
            for f in date_forms(r['iso']):
                if L.has(f, r['read_sid']): r['date_words'] = [f]; break


QUOTED = re.compile(r'"([^"]+)"|“([^”]+)”')
# Words the note puts in quotation marks as the LANE's wording, which also happen to stand somewhere in the saved page.
# They are not shown as the page's words: (list line, words). Each must be met in the note, or the build stops.
LANE_WORDS = {('52', 'supported')}


def mark_quoted(text, sid, keep, row='', met=None):
    """HTML for a line of the note. A quoted string that cn_has.py can find in the saved copy keeps its quotation marks
    (and is added to keep, for quotes.tsv); any other quoted string is set in italics without quotation marks."""
    out, pos = [], 0
    for m in QUOTED.finditer(text):
        out.append(esc(text[pos:m.start()])); pos = m.end()
        q = m.group(1) or m.group(2)
        if (row, q) in LANE_WORDS:
            if met is not None: met.add((row, q))
            out.append('<i>' + esc(q) + '</i>')
        elif len(L.squash(q)) >= 6 and L.has(q, sid):
            keep.append((sid, q)); out.append('“' + esc(q) + '”')
        else:
            out.append('<i>' + esc(q) + '</i>')
    out.append(esc(text[pos:]))
    s = ''.join(out)
    s = re.sub(r'`([^`]+)`', r'\1', s)
    return re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)


def text_only(h):
    return html.unescape(re.sub(r'<[^>]+>', '', h))


def search_norm(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', s).lower()).strip()


CSS = """
:root { --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#7a7872; --grid:#e1e0d9; --axis:#c3c2b7;
  --border:rgba(11,11,11,0.12); --wash:rgba(11,11,11,0.045); --toward:#256abf; --away:#c44e18; --link:#1c5cab;
  --font-text:"Inter",system-ui,-apple-system,"Segoe UI","Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;
  --font-head:"Space Grotesk","Inter",system-ui,sans-serif; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --page:#0d0d0d; --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7;
  --muted:#8f8d86; --grid:#2c2c2a; --axis:#45453f; --border:rgba(255,255,255,0.14); --wash:rgba(255,255,255,0.06);
  --toward:#3987e5; --away:#d95926; --link:#86b6ef; color-scheme:dark } }
:root[data-theme="dark"] { --page:#0d0d0d; --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#8f8d86; --grid:#2c2c2a; --axis:#45453f;
  --border:rgba(255,255,255,0.14); --wash:rgba(255,255,255,0.06); --toward:#3987e5; --away:#d95926; --link:#86b6ef; color-scheme:dark }
* { box-sizing:border-box; }
html { -webkit-text-size-adjust:100%; }
body { margin:0; background:var(--page); color:var(--ink); font-family:var(--font-text); font-size:16px; line-height:1.5; }
[hidden] { display:none !important; }
a { color:var(--link); }
.wrap { max-width:1120px; margin:0 auto; padding:30px 16px 56px; }
.eyebrow { font:700 12px/1 var(--font-text); letter-spacing:0.1em; text-transform:uppercase; color:var(--muted); margin:0 0 12px; }
h1 { font-family:var(--font-head); font-size:clamp(27px,3.6vw,42px); line-height:1.08; letter-spacing:-0.015em; margin:0 0 12px; max-width:26ch; text-wrap:balance; }
.deck { margin:0 0 14px; color:var(--ink2); font-size:18px; line-height:1.45; max-width:74ch; }
.note { margin:0 0 4px; color:var(--muted); font-size:13.5px; line-height:1.45; max-width:92ch; }
.cols { display:grid; gap:14px; grid-template-columns:1fr; margin:20px 0 6px; }
@media (min-width: 900px) { .cols { grid-template-columns:1fr 1fr; } }
.card { background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:16px 18px; min-width:0; }
.card h2 { font:700 12px/1.2 var(--font-text); letter-spacing:0.09em; text-transform:uppercase; color:var(--ink2); margin:0 0 8px; }
.card ul { margin:0; padding-left:18px; font-size:14.5px; line-height:1.5; color:var(--ink2); }
.card li { margin:0 0 5px; } .card li b { color:var(--ink); font-weight:600; }
.tools { position:sticky; top:0; z-index:5; background:var(--page); padding:14px 0 10px; margin-top:10px; border-bottom:1.5px solid var(--ink2); }
.find { display:flex; flex-wrap:wrap; align-items:center; gap:8px 14px; }
.find label { font:700 12px/1 var(--font-text); letter-spacing:0.09em; text-transform:uppercase; color:var(--ink2); flex:0 0 auto; }
.find input { flex:1 1 260px; min-width:0; font:inherit; font-size:16px; padding:9px 12px; border:1.5px solid var(--ink2); border-radius:10px; background:var(--surface); color:var(--ink); }
.find input:focus-visible, button:focus-visible, summary:focus-visible { outline:2.5px solid var(--ink); outline-offset:2px; }
#count { flex:0 0 auto; font-size:14px; font-weight:600; color:var(--ink2); font-variant-numeric:tabular-nums; }
.bar { display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin:12px 0 0; }
button { font:600 13px/1 var(--font-text); padding:7px 10px; border-radius:999px; border:1.5px solid var(--border); background:var(--surface); color:var(--ink2); cursor:pointer; }
button[aria-pressed="true"] { background:var(--ink); color:var(--page); border-color:var(--ink); }
button .n { font-variant-numeric:tabular-nums; font-weight:500; opacity:0.8; margin-left:3px; }
.bar .gap { flex:1 1 12px; }
.try { margin:10px 0 0; font-size:13.5px; color:var(--muted); display:flex; flex-wrap:wrap; align-items:center; gap:6px; }
.try button { padding:5px 9px; font-weight:500; }
#none { margin:22px 0; color:var(--ink2); }
details.r { border-bottom:1px solid var(--grid); }
summary { list-style:none; cursor:pointer; position:relative; }
summary::-webkit-details-marker { display:none; }
details.r > summary { display:grid; grid-template-columns:104px minmax(0,1fr) auto; gap:2px 16px; padding:12px 26px 12px 0; }
details.r > summary::after, .how > summary::after { content:""; position:absolute; right:6px; top:19px; width:8px; height:8px; border-right:2px solid var(--muted); border-bottom:2px solid var(--muted); transform:rotate(45deg); }
details.r[open] > summary::after { transform:rotate(-135deg); top:23px; }
.how > summary { padding-right:26px; } .how > summary h2 { margin:0; } .how[open] > summary h2 { margin-bottom:8px; }
.how > summary::after { top:1px; } .how[open] > summary::after { transform:rotate(-135deg); top:5px; }
.d { font-size:14px; font-weight:600; font-variant-numeric:tabular-nums; white-space:nowrap; padding-top:1px; }
.d.no { font-weight:500; color:var(--muted); white-space:normal; }
.who { min-width:0; }
.b { margin:0; font-weight:600; font-size:15.5px; line-height:1.4; }
.t { margin:2px 0 0; color:var(--ink2); font-size:14.5px; line-height:1.45; overflow-wrap:anywhere; }
.t.no { color:var(--muted); }
.tags { display:flex; flex-wrap:wrap; gap:5px; justify-content:flex-end; align-content:flex-start; max-width:250px; }
.tag { font:700 10.5px/1.15 var(--font-text); letter-spacing:0.05em; text-transform:uppercase; padding:4px 6px; border-radius:5px; background:var(--wash); color:var(--ink2); text-align:right; }
.tag.v { background:transparent; border:1.5px solid var(--axis); padding:2.5px 5px; }
.tag.v.part { border-color:var(--ink); color:var(--ink); }
.x { padding:2px 0 18px 120px; max-width:980px; }
.q { margin:0 0 12px; padding:1px 0 1px 13px; border-left:3px solid var(--axis); }
.q p { margin:0; }
.q .w { font-size:16.5px; line-height:1.62; overflow-wrap:anywhere; }
.q .w.en0 { font-size:15.5px; line-height:1.5; }
.q .e { margin-top:3px; color:var(--ink2); font-size:15px; line-height:1.5; }
.lab { font:700 10.5px/1 var(--font-text); letter-spacing:0.07em; text-transform:uppercase; color:var(--muted); margin-right:6px; }
.more { margin:0 0 12px; }
.more > summary { display:inline-block; padding:4px 0; font-size:13.5px; font-weight:600; color:var(--ink2); text-decoration:underline; text-underline-offset:3px; }
.more[open] > summary { margin-bottom:8px; }
.m { margin:0 0 5px; font-size:13.5px; line-height:1.5; color:var(--ink2); overflow-wrap:anywhere; }
.m i { font-style:italic; }
.m a { overflow-wrap:anywhere; }
.m code { font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:12.5px; line-height:1; color:var(--ink2); }   /* line-height 1: the id's font must not change the height of its line (a late fallback font once made every line 1 px taller after the first paint) */
footer { margin-top:30px; padding-top:14px; border-top:1px solid var(--grid); color:var(--muted); font-size:13.5px; line-height:1.5; max-width:92ch; }
footer p { margin:0 0 6px; }
@media (max-width: 720px) {
  details.r > summary { grid-template-columns:auto minmax(0,1fr); grid-template-areas:"d tags" "who who"; gap:6px 10px; padding-right:24px; }   /* the date keeps its width; the kind marks wrap in what is left (they once lay over the date) */
  .d { grid-area:d; } .tags { grid-area:tags; max-width:none; } .who { grid-area:who; }
  .x { padding-left:0; }
  .deck { font-size:17px; }
}
"""

JS = r"""
(function () {
  var rows = Array.prototype.slice.call(document.querySelectorAll('details.r'));
  var hay = rows.map(function (r) { return r.getAttribute('data-s'); });
  var tight = hay.map(function (h) { return h.replace(/\s+/g, ''); });
  var input = document.getElementById('q'), count = document.getElementById('count'), none = document.getElementById('none');
  var kindButtons = Array.prototype.slice.call(document.querySelectorAll('button[data-kind]'));
  var toggle = document.getElementById('toggle');
  var partButton = document.getElementById('part');
  var kind = 'all', view = 'auto', part = false;
  var how = document.getElementById('how');
  if (window.matchMedia('(max-width: 720px)').matches) how.open = false;
  function norm(s) { return (s.normalize ? s.normalize('NFKC') : s).toLowerCase().replace(/\s+/g, ' ').trim(); }
  function apply() {
    var q = norm(input.value), terms = q ? q.split(' ') : [], shown = 0;
    var openAll = view !== 'closed';
    rows.forEach(function (r, i) {
      var ok = (kind === 'all' || r.getAttribute('data-kind') === kind) && (!part || r.getAttribute('data-part') === '1') &&
        terms.every(function (t) { return hay[i].indexOf(t) !== -1 || tight[i].indexOf(t) !== -1; });
      r.hidden = !ok;
      if (ok) { shown += 1; r.open = terms.length ? view !== 'closed' : openAll; }
    });
    count.textContent = shown === rows.length ? 'All ' + rows.length + ' lines' : shown + ' of ' + rows.length + ' lines';
    none.hidden = shown !== 0;
    kindButtons.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-kind') === kind ? 'true' : 'false'); });
    partButton.setAttribute('aria-pressed', part ? 'true' : 'false');
    toggle.textContent = (terms.length ? view !== 'closed' : openAll) ? 'Close all' : 'Open all';
  }
  function remember() {
    var parts = [];
    if (input.value.trim()) parts.push('q=' + encodeURIComponent(input.value.trim()));
    if (kind !== 'all') parts.push('kind=' + kind);
    if (part) parts.push('part=1');
    if (view !== 'auto') parts.push('view=' + view);
    try { history.replaceState(null, '', parts.length ? '#' + parts.join('&') : location.pathname + location.search); } catch (e) {}
  }
  function fromHash() {
    location.hash.replace(/^#/, '').split('&').forEach(function (p) {
      var k = p.split('=')[0], v = p.slice(k.length + 1);
      try { v = decodeURIComponent(v); } catch (e) {}
      if (k === 'q') input.value = v;
      if (k === 'kind' && document.querySelector('button[data-kind="' + v + '"]')) kind = v;
      if (k === 'part' && v === '1') part = true;
      if (k === 'view' && (v === 'open' || v === 'closed')) view = v;
    });
  }
  input.addEventListener('input', function () { apply(); remember(); });
  kindButtons.forEach(function (b) { b.addEventListener('click', function () { kind = b.getAttribute('data-kind'); apply(); remember(); }); });
  partButton.addEventListener('click', function () { part = !part; apply(); remember(); });
  toggle.addEventListener('click', function () { view = toggle.textContent === 'Open all' ? 'open' : 'closed'; apply(); remember(); });
  Array.prototype.forEach.call(document.querySelectorAll('button[data-try]'), function (b) {
    b.addEventListener('click', function () { input.value = b.getAttribute('data-try'); apply(); remember(); input.focus(); });
  });
  fromHash(); apply();
})();
"""

TRY = ['英伟达', 'Nvidia', '国产', 'Shanghai', 'procurement', 'Micron']
EXPECT = TRY + ['财库 119号', '安全可靠 测评', 'no-such-word-zzqx', '算力券', 'Province']


def main():
    B.load_clip()
    rows, note = parse_note()
    n_table = cross_check(rows)
    for r in rows:
        if r['row'] in REPOINT:
            new, addr, why = REPOINT[r['row']]
            old = r['read_sid']; r['sid'] = new; r['read_sid'] = new; r['read_note'] = ''
            r['addr2'] = r['addr']; r['addr'] = addr
            r['repoint_note'] = f'Shown as read in {why}. The passages and date words below were checked in that page.'
            for q in r['quotes']:
                if len(L.squash(q['words'])) >= 6 and not L.has(q['words'], new): stop(f'REPOINT: line {r["row"]}: a passage is not in {new}')
    if sorted(r['row'] for r in rows if r.get('repoint_note')) != sorted(REPOINT): stop('REPOINT: a line was not met')
    set_dates(rows)
    body_met = []
    for r in rows:
        for old, new in BODY_FIX:
            if old in r['body']: r['body'] = r['body'].replace(old, new); body_met.append(old)
    for r in rows:
        for old, new in REMARK_FIX.get(r['row'], []):
            if r['remark'].count(old) != 1: stop(f'REMARK_FIX: line {r["row"]}: the note no longer has "{old[:40]}" once')
            r['remark'] = r['remark'].replace(old, new)
    if any(not any(r['row'] == k for r in rows) for k in REMARK_FIX): stop('REMARK_FIX: a line was not met')
    if set(EN_SRC) != set(EN_FIX): stop('EN_SRC and EN_FIX name different lines')
    _core = {'argument': (PROJ / 'argument' / 'argument_base.txt').read_text(encoding='utf-8'), 'record': (PROJ / 'OFFICIAL_RECORD.md').read_text(encoding='utf-8')}
    for k_, pairs_ in EN_FIX.items():
        for _, new_ in pairs_:
            if new_ not in _core[EN_SRC[k_]] and EN_SRC[k_] == 'record':      # the argument's four were checked in round 4 against the argument as it then stood
                stop(f'EN_FIX: line {k_}: the record does not hold the wording the page takes from it: {new_[:60]}')
    for r in rows:
        for old, new in EN_FIX.get(r['row'], []):
            hit = [q for q in r['quotes'] if old in (q['en'] or '')]
            if len(hit) != 1: stop(f'EN_FIX: line {r["row"]}: the note no longer has "{old[:40]}" once')
            hit[0]['en'] = hit[0]['en'].replace(old, new)
    for r in rows:
        for q in r['quotes']:
            if has_cjk(q['words']) and not q['en']: stop(f'row {r["row"]}: a Chinese passage without our English')
    short = []          # passages under six characters: cn_has.py will not test them, so the page does not show them
    for r in rows:
        for q in r['quotes']:
            if len(L.squash(q['words'])) < 6: short.append(r['row'])
        r['quotes'] = [q for q in r['quotes'] if len(L.squash(q['words'])) >= 6]
        if not r['quotes']: stop(f'row {r["row"]}: no passage long enough to check')
    rows.sort(key=lambda r: (0, r['iso']) if r['iso'] else (1, ''))        # by date; the two without a date last (the sort keeps the note's order within a date)

    keep = []           # (saved id, words): quoted strings kept in quotation marks in the body and check lines
    lines_q = []        # (saved id, words): everything for quotes.tsv
    cards = []
    met = set()         # the LANE_WORDS entries met in the note
    for r in rows:
        sid = r['read_sid']
        title = re.sub(r'\s*<br\s*/?>\s*', ' ', B.title_of(sid))
        body_h = mark_quoted(r['body'], sid, keep, r['row'], met)
        remark_h = mark_quoted(r['remark'], sid, keep, r['row'], met) if r['remark'] else ''
        for q in r['quotes']: lines_q.append((sid, q['words']))
        for w in r['date_words']: lines_q.append((sid, w))
        kind_label = KIND_LABEL[r['kind']]
        v_label = 'Confirmed in part' if r['verdict'] == 'CONFIRMED IN PART' else ('Confirmed, in a second copy' if r.get('second') else 'Confirmed')
        if r['verdict'] not in ('CONFIRMED', 'CONFIRMED IN PART'): stop(f'row {r["row"]}: verdict {r["verdict"]} has no label')
        if r['iso']:
            d_html = f'<span class="d">{esc(show_date(r["iso"]))}</span>'
            if r['date_from'] == 'page': d_note = 'The list gave no date; this is the date the checked note found in the page.'
            elif r['date_from'] == 'here': d_note = 'The list gave no date and the checked note found none; this is the signing date read in the page for this list.'
            else: d_note = ''
            if r['date_words']:
                d_note += (' ' if d_note else '') + 'Date words found in the saved copy: ' + '; '.join('“' + esc(w) + '”' for w in r['date_words']) + '.'
            else:
                d_note += (' ' if d_note else '') + 'The date is the list\'s. The script did not find it written in the saved copy.'
        else:
            d_html = '<span class="d no">no date found</span>'
            d_note = 'The list gave no date and none was found in the copy read.'

        def passage(q):
            cjk = has_cjk(q['words'])
            where = ' <span class="lab">in the page body, not in the text copy</span>' if q['form'] == 'body' else ''
            h = f'<div class="q"><p class="w{"" if cjk else " en0"}"{" lang=\"zh-Hans\"" if cjk else ""}>“{esc(q["words"])}”{where}</p>'
            if q['en']: h += f'<p class="e"><span class="lab">Our English</span>{esc(q["en"])}</p>'
            return h + '</div>'

        # the passage shown first: the note's first one that is a sentence and not only a number or a date (20 characters or more)
        key = next((q for q in r['quotes'] if len(L.squash(q['words'])) >= 20), r['quotes'][0])
        rest = [q for q in r['quotes'] if q is not key]
        x = [passage(key)]
        if rest:
            x.append(f'<details class="more"><summary>{len(rest)} more passage{"s" if len(rest) > 1 else ""} from this page</summary>' + ''.join(passage(q) for q in rest) + '</details>')
        if remark_h: x.append(f'<p class="m"><span class="lab">Check note</span>{remark_h}</p>')
        if r.get('repoint_note'): x.append(f'<p class="m"><span class="lab">Copy</span>{esc(r["repoint_note"])}</p>')
        if r.get('first_copy'): x.append(f'<p class="m"><span class="lab">Copy</span>{esc(r["first_copy"])}</p>')
        x.append(f'<p class="m"><span class="lab">Date</span>{d_note}</p>')
        addr = f'<a href="{esc(r["addr"])}" rel="noopener">{esc(r["addr"])}</a>'
        if r.get('addr2'): addr += (f'. The copy the note read: ' if r.get('repoint_note') else '. Second copy: ') + f'<a href="{esc(r["addr2"])}" rel="noopener">{esc(r["addr2"])}</a>'
        x.append(f'<p class="m"><span class="lab">Address</span>{addr}</p>')
        ids = f'<code>{esc(r["sid"])}</code>'
        if r['read_sid'] != r['sid']: ids += f'. Read in {esc(r["read_note"])}, saved as <code>{esc(r["read_sid"])}</code>'
        x.append(f'<p class="m"><span class="lab">Saved copy</span>{ids}. Line {esc(r["row"])} of the list.</p>')
        t_html = f'<p class="t"{" lang=\"zh-Hans\"" if has_cjk(title) else ""}>{esc(title)}</p>' if title else '<p class="t no">No title is held for this copy.</p>'
        summ = (f'<summary>{d_html}<div class="who"><p class="b">{body_h}</p>{t_html}</div>'
                f'<span class="tags"><span class="tag">{esc(kind_label)}</span><span class="tag v{" part" if r["verdict"] == "CONFIRMED IN PART" else ""}">{esc(v_label)}</span></span></summary>')
        inner = summ + '<div class="x">' + ''.join(x) + '</div>'
        r['search'] = search_norm(' '.join([r['iso'], text_only(inner)]))
        cards.append(f'<details class="r" open data-kind="{GROUP[r["kind"]]}" data-part="{1 if r["verdict"] == "CONFIRMED IN PART" else 0}" data-s="{esc(r["search"])}">{inner}</details>')

    if met != LANE_WORDS: stop(f'LANE_WORDS entries not met in the note: {sorted(LANE_WORDS - met)}')

    local, left_out = local_lines()
    VCLASS = voucher_class_of()
    for r in local:
        for old, new in BODY_FIX:
            if old in r['who']: r['who'] = r['who'].replace(old, new); body_met.append(old)
    if sorted(body_met) != sorted(o for o, _ in BODY_FIX): stop(f'BODY_FIX: not each met once: {body_met}')
    rep_met = []
    for r in local:
        k = (r['table'], r['trow'])
        if k in REPEALED:
            sid_, words_, note_ = REPEALED[k]
            if not L.has(words_, sid_): stop(f'REPEALED: "{words_}" not found in {sid_}')
            r['repealed'] = note_; rep_met.append(k); lines_q.append((sid_, words_))
    if sorted(rep_met) != sorted(REPEALED): stop(f'REPEALED: rows not met: {sorted(set(REPEALED) - set(rep_met))}')
    local.sort(key=lambda r: (0 if r['prov'] else 1, (0, r['iso']) if r['iso'] else (1, '')))
    for r in local:
        for q in r['quotes']: lines_q.append((q['sid'], q['words']))
        sid0 = r['quotes'][0]['sid'] if r['quotes'] else (r['sids'][0] if r['sids'] and (L.P / r['sids'][0]).is_dir() else '')
        title = re.sub(r'\s*<br\s*/?>\s*', ' ', B.title_of(sid0)) if sid0 else ''
        d_html = f'<span class="d">{esc(show_date(r["iso"]))}</span>' if r['iso'] else '<span class="d no">no date given</span>'
        x = []
        for j, q in enumerate(r['quotes']):
            cj = has_cjk(q['words'])
            x.append(f'<div class="q"><p class="w{"" if cj else " en0"}"{" lang=\"zh-Hans\"" if cj else ""}>“{esc(q["words"])}”</p></div>')
        if not r['quotes']:
            x.append('<p class="m"><span class="lab">Passage</span>None shown: the project\'s table gives no words for this row that the checker finds in a saved copy.</p>')
        if r.get('repealed'): x.append(f'<p class="m"><span class="lab">In force?</span><b>{esc(r["repealed"])}</b></p>')
        if not r['prov']: x.append(f'<p class="m"><span class="lab">Counted by the published rule?</span>{esc(VCLASS[(r["table"], r["trow"])])}. From the project\'s table of classes, tables/local_vouchers_classes.tsv.</p>')
        if r['reading']: x.append(f'<p class="m"><span class="lab">Our reading, in English</span>{esc(r["reading"])}. This is the project\'s table, not a translation.</p>')
        x.append(f'<p class="m"><span class="lab">The document</span>{esc(r["desc"])}</p>')
        if r['extra']: x.append(f'<p class="m"><span class="lab">The copy held</span>{esc(r["extra"])}</p>')
        addr = B.address(sid0, {'addr': ''}) if sid0 else ''
        if addr: x.append(f'<p class="m"><span class="lab">Address</span><a href="{esc(addr)}" rel="noopener">{esc(addr)}</a></p>')
        x.append(f'<p class="m"><span class="lab">Saved copy</span>{", ".join("<code>" + esc(s_) + "</code>" for s_ in r["sids"])}. Row {r["trow"]} of tables/{esc(r["table"])}.</p>')
        t_html = f'<p class="t"{" lang=\"zh-Hans\"" if has_cjk(title) else ""}>{esc(title)}</p>' if title else '<p class="t no">No title is held for this copy.</p>'
        tag2 = 'Province' if r['prov'] else ('National statement' if r.get('level') == 'national' else ('Local rule, repealed' if r.get('repealed') else 'Local rule'))   # round 5: a national body's words get their own badge
        if not r['prov'] and tag2 == 'Local rule':      # round 9: a row the table of classes calls a draft, an application guide or a notice of a list is not badged a rule
            tag2 = {'No: a draft': 'Local draft', 'No: an application guide, not the rule': 'Application guide',
                    'No: a public notice of a list, not the rule': 'Notice of a list'}.get(VCLASS[(r['table'], r['trow'])], tag2)
        summ = (f'<summary>{d_html}<div class="who"><p class="b">{esc(r["who"])}</p>{t_html}</div>'
                f'<span class="tags"><span class="tag">{tag2}</span><span class="tag v">From the project\'s tables</span></span></summary>')
        inner = summ + '<div class="x">' + ''.join(x) + '</div>'
        r['search'] = search_norm(' '.join([r['iso'], text_only(inner)]))
        r['kind'] = 'local'
        cards.append(f'<details class="r" open data-kind="local" data-part="0" data-s="{esc(r["search"])}">{inner}</details>')
    c_res = Counter(r['result'] for r in local if r['prov'])
    # round 9: the care box names Tibet and Xinjiang; the build stops if the table no longer gives them those results
    _p31 = table_rows('provinces_31.tsv')
    if [r['government'] for r in _p31 if r['result'] == 'account_only'] != ['Tibet'] or [r['government'] for r in _p31 if r['result'] == 'not_reached'] != ['Xinjiang']:
        stop('tables/provinces_31.tsv no longer gives Tibet and Xinjiang the results the care box names')
    # core edit 8: the care box names Zhejiang's share with its scope; the words follow the table's row (a share, from the sector plan whose words the row quotes)
    zj = [r for r in table_rows('provinces_31.tsv') if r['government'] == 'Zhejiang']
    if not (len(zj) == 1 and zj[0]['result'] == 'share' and zj[0]['saved_ids'].split()[0] == 'cn-ga31-cndocs-52' and L.has('到2030年，浙江信息通信行业算力规模达150EFLOPS，国产化算力占比超60%', 'cn-ga31-cndocs-52')):
        stop('Zhejiang is not the share the care box describes (tables/provinces_31.tsv)')
    VC = voucher_counts()
    # core edit 8: the sentence on voucher rows left out follows the count (none is left out since the text of the Word and zip copies was put beside them
    # as text.article.txt and Xiamen's official file was filed among the saved sources)
    # round 9: the two rows left out since voucher round 5 are scans without a text layer (their copy cells say so); the sentence names what they are, by the cells
    _left_copy = [table_rows(x.split(' row ')[0])[int(x.split(' row ')[1]) - 1]['copy'] for x in left_out]
    _scan = all('text layer' in c for c in _left_copy)
    left_s = ((f'{len(left_out)} voucher rows are left out because none of their words could be checked by script (' + '; '.join(x.replace('.tsv row', '.tsv, row') for x in left_out) +
               (f'): {"both saved copies are files" if len(left_out) == 2 else "each saved copy is a file"} without a text layer, as the table says.' if _scan else
                '): they are held only as files the checker cannot read (a scan without a text layer, or a Word or zip file), or have no saved copy.'))
              if left_out else 'No voucher row is left out: each has words the checker finds in a saved copy (where the copy is a Word or zip file, in the text taken out of it and kept beside it).')
    n_vouch = sum(1 for r in local if not r['prov'])
    # round 9: how many of the voucher lines shown are counted, and the commonest reasons of those that are not (computed from the table of classes)
    _vs = [VCLASS[(r['table'], r['trow'])] for r in local if not r['prov']]
    v_shown_yes = sum(1 for v in _vs if v.startswith('Yes')); v_shown_no = n_vouch - v_shown_yes
    _whyc = Counter(re.sub(r' \(row \d+ of tables/[a-z_]+\.tsv\)$', '', v[4:]) for v in _vs if v.startswith('No: ')); _why = _whyc.most_common(3)
    v_shown_why = 'by reason, the commonest: ' + '; '.join(f'{k}, {w}' for w, k in _why) + ('; and other reasons' if len(_whyc) > 3 else '')
    if v_shown_yes != VC['n'] and not left_out: stop(f'{v_shown_yes} counted voucher lines shown, but the argument counts {VC["n"]} and no voucher row is left out')
    lines_q += keep
    seen, qlines = set(), []
    for sid, w in lines_q:
        if (sid, w) not in seen: seen.add((sid, w)); qlines.append(f'{sid}\t{w}')
    for sid, w in seen:
        if '\t' in w or '\n' in w: stop('a tab or line break inside a quotation')
    (HERE / 'quotes.tsv').write_text('# saved id <TAB> exact words from that saved copy. Written by build.py: every passage the page shows, every date word it shows,\n'
                                     '# and every quoted string it keeps in quotation marks in the body and check lines. Checked by scripts/cn_has.py.\n'
                                     + '\n'.join(qlines) + '\n', encoding='utf-8')
    run = subprocess.run([sys.executable, '-I', str(SCRIPTS / 'cn_has.py'), str(HERE / 'quotes.tsv')], capture_output=True, text=True)
    has_line = (run.stdout.strip().splitlines() or ['(no output)'])[-1]
    if run.returncode != 0:
        print(run.stdout + run.stderr); stop('cn_has.py did not pass on quotes.tsv')

    n103 = len(rows)
    n_pass = sum(len(r['quotes']) for r in rows)
    n_local = len(local); n_local_pass = sum(len(r['quotes']) for r in local)
    all_rows = rows + local
    n = len(all_rows)
    n_copies = len({r['read_sid'] for r in rows})
    c_kind = Counter(GROUP[r['kind']] for r in all_rows); c_exact = Counter(r['kind'] for r in rows)
    n_part = sum(1 for r in rows if r['verdict'] == 'CONFIRMED IN PART')
    n_dated = sum(1 for r in rows if r['iso']); n_dfound = sum(1 for r in rows if r['date_words'])
    n_cn = sum(1 for r in rows for q in r['quotes'] if has_cjk(q['words']))
    words = {'carried': ('official text or figure carried by a news outlet', 'official texts or figures carried by news outlets'),
             'roadmap': ("line from an advisory committee's roadmap", "lines from an advisory committee's roadmap"),
             'translation': ("think tank's translation of a government text", "think tanks' translations of government texts")}
    other_bits = '; '.join(f'{c_exact[k]} {words[k][0 if c_exact[k] == 1 else 1]}' for k in words if c_exact[k])

    def expect(qs, kind='all'):
        terms = search_norm(qs).split(' ') if search_norm(qs) else []
        return sum(1 for r in all_rows if (kind == 'all' or GROUP[r['kind']] == kind) and all(t in r['search'] or t in re.sub(r'\s+', '', r['search']) for t in terms))
    expected = {'rows': n, 'kinds': {k: (n if k == 'all' else c_kind[k]) for k in GROUP_LABEL}, 'queries': {q: expect(q) for q in EXPECT},
                'query_with_kind': {'国产|press': expect('国产', 'press')}, 'part': n_part}
    for q in TRY:
        if expected['queries'][q] == 0: stop(f'the example search "{q}" finds nothing')
    (HERE / 'expected.json').write_text(json.dumps(expected, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    short_note = (f'<p>Left out: {len(short)} passage{"s" if len(short) != 1 else ""} of the note under six characters long (line {", ".join(short)} of the list), which the checker will not test.</p>' if short else '')
    kind_buttons = ''.join(f'<button type="button" data-kind="{k}" aria-pressed="{"true" if k == "all" else "false"}">{esc(v)}<span class="n">{n if k == "all" else c_kind[k]}</span></button>' for k, v in GROUP_LABEL.items())
    try_buttons = ''.join(f'<button type="button" data-try="{esc(q)}">{esc(q)}</button>' for q in TRY)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Policy Documents, Searchable</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header>
<p class="eyebrow">China chip policy · the policy documents</p>
<h1>The policy documents: {n103} policy lines and {n_local} local rules and provincial plans</h1>
<p class="deck">Most are texts the Chinese state published. No published order against buying Nvidia chips was found among them. The review office's 2023 conclusion on Micron, which says operators of critical infrastructure should stop buying its products, is in the list. So such a text could have been found.</p>
<p class="note">Draft by Claude, Anthropic's model.</p>
<p class="note">Made by a script (build.py, beside this file) from the project's checked note, NOTE_policies_checked.md, and its table of quotations, and from three of the project's tables (tables/provinces_31.tsv, local_vouchers.tsv, local_vouchers_more.tsv). {n103} lines of a list of policy leads; {n_copies} saved pages; {n_pass} passages in the pages' own words, {n_cn} of them Chinese.</p>
</header>
<div class="cols">
<details class="card how" id="how" open><summary><h2>How to read a line</h2></summary><ul>
<li><b>A line</b> is one entry of a list of policy leads that a search run (the note calls it a lane) wrote. The checked note then read each lead in the saved copy of its page.</li>
<li><b>Confirmed</b> means the page carries what the lead said. <b>Confirmed in part</b> ({n_part} lines) means some part is not in the page; the check note says which.</li>
<li><b>Words between quotation marks</b> are the page's own, cut from the saved copy. The <b>English under Chinese is ours</b>, not an official translation. On {len(EN_FIX)} lines it is the core's wording as corrected after a second or later reading: the argument's (lines {", ".join(sorted((k for k in EN_FIX if EN_SRC[k] == 'argument'), key=int))} of the list) or the official record's (lines {", ".join(sorted((k for k in EN_FIX if EN_SRC[k] == 'record'), key=int))}).</li>
<li><b>In a check note</b>, words in italics are the note's own English, the list's own wording, or a reading the script could not check.</li>
<li><b>The date</b> is that of the document or act as the list gives it. A script looked for it in the saved copy: it found date words for {n_dfound} of the {n_dated} dated lines, and each line shows them.</li>
</ul></details>
<section class="card"><h2>Read with care</h2><ul>
<li><b>Two sources.</b> {n103} lines come from the checked note of policy leads. {n_local} more come from the project's tables of local rules and provincial plans, marked <i>From the project's tables</i>: all 31 provincial-level governments ({c_res['share']} set a share for home-made computing hardware, one of them, Zhejiang's, for the computing of one sector, its information and communications industry; {c_res['plan_no_share']} have a plan that was read and sets none; {c_res['account_only']}, Tibet, is known only from accounts of it, its issuer's own among them; for {c_res['not_reached']}, Xinjiang, no computing plan was found), and {n_vouch} rows of the project's tables of local voucher and subsidy rules whose words the checker finds in a saved copy: {v_shown_yes} of them are counted by the published counting rule and {v_shown_no} are not ({esc(v_shown_why)}), and each line says which, as the project's table of classes gives it. {left_s} On the lines from the tables the English is the table's reading of the rule, not a translation. Counting one rule in force for each local government whose text is saved and which states a share of the bill, the argument finds {VC['n']} among the rules found by searches that went province by province and city by city, saved and read (not a census of every local government): {VC['tiered']} pay more for home-made computing and still pay for other computing ({VC['tiered_names']}), {VC['home']}, those of {VC['home_arg']}, pay for home-made computing only, and {VC['third']} state no higher rate for home-made computing: {VC['one']} pay one rate whatever the chip, and one, {VC['two_name']}'s, pays {VC['two_a']}% or {VC['two_b']}% by a type of computing facility that it does not name. Beijing E-Town's tier was repealed on Nov 26, 2024.</li>
<li><b>Not every line is a government text.</b> {c_kind['official']} are official texts, {c_kind['company']} are company filings or statements, {c_kind['press']} are press reports, and {c_kind['other']} are of other kinds ({esc(other_bits)}). Each line carries its kind.</li>
<li><b>A press report is not published policy.</b> Beijing's instructions to companies are reported by the press from unnamed people; no line here is a published order of that kind.</li>
<li><b>Found means said, not true.</b> A passage that is found shows what the page says.</li>
<li><b>“Not found” is about these {n} lines only.</b> Nothing here shows what was never published, or what was published and not gathered.</li>
</ul></section>
</div>
<div class="tools">
<div class="find"><label for="q">Search</label><input id="q" type="search" autocomplete="off" spellcheck="false" placeholder="Chinese or English words"><span id="count" role="status" aria-live="polite">All {n} lines</span></div>
</div>
<div class="bar">{kind_buttons}<button type="button" id="part" aria-pressed="false">Confirmed in part only<span class="n">{n_part}</span></button><span class="gap"></span><button type="button" id="toggle">Close all</button></div>
<p class="try"><span>Try:</span>{try_buttons}<span>Two words find lines that hold both.</span></p>
<main id="list">
{chr(10).join(cards)}
<p id="none" hidden>No line holds those words. The search reads the date, the body, the title, the passages, our English, the check note, the address and the saved id.</p>
</main>
<footer>
<p>Build check: {esc(has_line)}. The passages are the same strings, row by row, as in the note's own table of quotations ({n_table} strings, plus the two of the line read in a second copy). A passage that is found shows what the page says, not that it is true.</p>
{short_note}
<p>Our English is the checked note's, shown without the quotation marks that note puts round a few terms: only a page's own words stand between quotation marks here. On {len(EN_FIX)} lines it is the core's corrected wording instead: the argument's (lines {", ".join(sorted((k for k in EN_FIX if EN_SRC[k] == 'argument'), key=int))} of the list) or the official record's (lines {", ".join(sorted((k for k in EN_FIX if EN_SRC[k] == 'record'), key=int))}).</p>
<p>The {n_local} lines marked <i>From the project's tables</i> come from tables/provinces_31.tsv, local_vouchers.tsv and local_vouchers_more.tsv: each passage shown was found by the same checker in a saved copy the row names; the English beside them is the table's reading, not a translation; the address is the one held with the saved copy.</p>
<p>The descriptions of the issuing body and the check notes are the checked note's own words, carried over by the script, except that Li Chao is not called the planner's spokesperson: the commission's page names him and his office only. Page titles are those held with the saved copies. Addresses are those the note gives.</p>
</footer>
</div>
<script>{JS}</script>
</body>
</html>
"""
    OUT.write_text(page, encoding='utf-8')
    print(f'local lines: {n_local} ({n_vouch} voucher rules, 31 provinces: ' + ', '.join(f'{k} {c_res[k]}' for k in RESULT) + f'), {n_local_pass} passages; voucher rows left out (no passage the checker can read): {len(left_out)} ({"; ".join(left_out)})')
    print(f'policy_documents.html: {n} lines, {n_copies} saved pages, {n_pass} passages ({n_cn} Chinese); kinds: ' + ', '.join(f'{k} {c_kind[k]}' for k in ('official', 'company', 'press', 'other')))
    print(f'verdicts (the {n103} note lines): confirmed {n103 - n_part}, confirmed in part {n_part}; dated lines {n_dated}, date words found in the saved copy for {n_dfound}; quoted strings kept in quotation marks in body and check lines: {len(keep)}')
    print(f'cn_has.py: {has_line}')
    print(f'passages of the note left out as too short for the checker: {len(short)} (list line {", ".join(short) or "-"})')
    print('lines whose date was not found written in the saved copy: ' + (', '.join(r['row'] for r in rows if r['iso'] and not r['date_words']) or 'none') +
          '; lines without a date: ' + (', '.join(r['row'] for r in rows if not r['iso']) or 'none'))


if __name__ == '__main__':
    main()
