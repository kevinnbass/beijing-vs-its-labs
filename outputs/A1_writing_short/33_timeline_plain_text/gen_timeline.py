#!/usr/bin/env python3
"""Idea 33: the timeline as plain text, generated from the figure's table of records. Nothing is retyped.

Run: python3 -I gen_timeline.py
Reads   ../../../figure/figure_events.tsv   (n, date, shown_as, lane, kind, source, address, saved_id, text, also_source, also_address)
        ../../../figure/figure_data.txt     (to cross-check the records and find the saved ID for each second source)
        ../../../argument/argument_refs.tsv and argument_refs_more.tsv (to know which saved ids already have a reference line)
        ../../../loose_ends/hkexnews_saved_ids.tsv (ids that may no longer be cited: the run stops if the table holds one)
Writes  timeline_base.txt        the list in the project's small markup, with one hidden check line per quotation
        timeline_extra_refs.tsv  reference lines for the saved ids the argument's list does not hold
        timeline.md              built from timeline_base.txt by scripts/cn_doc_build.py (--md-only)
        timeline.txt             the same records as plain lines: date | who | what | source | address
        quote_marks_report.tsv   every quoted phrase in the table: kept (found in the saved copy) or marks taken off

Columns: date = the table's shown_as; row (called who until round 10b) = the table's lane (the row of the figure the record sits in);
what = the table's text; source = the table's source names, then its tier (from the table's kind); address = the sources' addresses in the same order.
Order: the table's date column, then its record number. A record with no exact day (its shown_as holds words, such
as the warning about traitors) stands where the figure places it, and a note names every such record.
Cross-check: every record's date, date label, row and wording are compared with figure/figure_data.txt (the run
stops on any difference), so the list follows the figure's data file, not only the table made from it.
Since round 8 (Nov 25, 2026, core edit 7) the data file's "N" line is read as scripts/cn_figure_build.py reads it: records
are numbered by date, Beijing's rows first and then the companies', except a record with an "N" line, which keeps that
number (record 62). The table's numbers must equal that numbering; the timeline itself prints no record number.

Quotation marks: the table's text puts curly marks round some words. A phrase keeps its marks only if it stands in
a saved source linked to the record (scripts/cn_srclib.py: has). Where it does not (English put for Chinese
words, or a paraphrase), the marks are taken off and the phrase is listed in quote_marks_report.tsv.
timeline.txt is written only after cn_doc_build.py has passed (exit 0), and that build re-checks every kept phrase.
Round 10b (Nov 25, 2026): the header names no script and says the list is drawn word for word from the figure's table; the second
field is called row (it was who); rebuilt from figure_data.txt as builder r12e left it (main figure built 22:41 and 22:44 UTC).
"""
import re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parents[2]                      # research/cn_chip_policy_20261120
ROOT = HERE.parents[4]                      # .
sys.path.insert(0, str(ROOT / 'scripts'))
import cn_srclib as L                       # the project's own checker (read only)

EVENTS = PROJ / 'figure' / 'figure_events.tsv'
FIGDATA = PROJ / 'figure' / 'figure_data.txt'
ARGREFS = [PROJ / 'argument' / 'argument_refs.tsv', PROJ / 'argument' / 'argument_refs_more.tsv']
RETIRED = PROJ / 'loose_ends' / 'hkexnews_saved_ids.tsv'
FULL_DAY = re.compile(r'[A-Z][a-z]{2,4} \d{1,2}, \d{4}')
BUILD = ROOT / 'scripts' / 'cn_doc_build.py'

TIER = {'doc': 'on the record: a government document, an official, or published state media',   # the figure's kind "doc" in the words of figure_data.txt's
                                                                                              # header since core batch 15 (row B15-043); no word here says who a body belongs to
        'rec': 'on the record: a company or a named person outside government',
        'press': 'press report citing unnamed people'}
COLS = ['n', 'date', 'shown_as', 'lane', 'kind', 'source', 'address', 'saved_id', 'text', 'also_source', 'also_address']
CURLY = re.compile(r'“([^“”]+)”')


def load():
    lines = EVENTS.read_text(encoding='utf-8').splitlines()
    head = lines[0].split('\t')
    if head != COLS: sys.exit(f'unexpected columns in {EVENTS.name}: {head}')
    rows = []
    for k, ln in enumerate(lines[1:], 2):
        if not ln.strip(): continue
        c = ln.split('\t')
        if len(c) != len(COLS): sys.exit(f'line {k}: {len(c)} columns, expected {len(COLS)}')
        r = dict(zip(COLS, c))
        if not re.fullmatch(r'\d{4}-\d\d-\d\d', r['date']): sys.exit(f'line {k}: bad date {r["date"]}')
        if r['kind'] not in TIER: sys.exit(f'line {k}: unknown kind {r["kind"]}')
        if any('|' in v for v in c): sys.exit(f'line {k}: a field holds "|", which would break the five-field line')
        if any('"' in r[field] for field in ('text', 'source', 'also_source')):
            sys.exit(f'line {k}: a straight double quote in the text or source')
        if any(d in v for v in c for d in ('—', '–')): sys.exit(f'line {k}: a long dash')
        if not r['address'].startswith('http'): sys.exit(f'line {k}: no address')
        if bool(r['also_source']) != bool(r['also_address']) or (
            r['also_address'] and (not r['also_address'].startswith('http') or r['also_address'] == r['address'])
        ):
            sys.exit(f'line {k}: the second source must have its own address')
        if not (L.P / r['saved_id']).is_dir(): sys.exit(f'line {k}: no saved copy named {r["saved_id"]}')
        rows.append(r)
    rows.sort(key=lambda r: (r['date'], int(r['n'])))
    return rows


def number(fig):
    """The figure's record numbers, as scripts/cn_figure_build.py number() gives them since core edit 7 (Nov 25, 2026): by
    date, Beijing's rows first and then the companies', except a record with an "N" line, which keeps the number given there.
    Returns one number per record of fig, in fig's order; raises ValueError where the numbers would not run 1 to N."""
    free = [d for d in fig if not d['N']]
    b = sorted([d for d in free if d['code'][0] == 'B'], key=lambda d: d['date'])
    c = sorted([d for d in free if d['code'][0] == 'C'], key=lambda d: d['date'])
    num = {id(d): i for i, d in enumerate(b + c, 1)}
    for d in fig:
        if d['N']: num[id(d)] = int(d['N'])
    if sorted(num.values()) != list(range(1, len(fig) + 1)): raise ValueError('the record numbers do not run from 1 to the number of records')
    if any(num[id(d)] <= len(free) for d in fig if d['N']): raise ValueError('a fixed number falls among the numbers given by date')
    return [num[id(d)] for d in fig]


def main():
    rows = load()
    data = FIGDATA.read_text(encoding='utf-8').splitlines()
    lane_head = next((line for line in data if line.startswith('# LANE:')), '')
    bl = re.search(r'\bBL ([^|]+)', lane_head)
    if not bl:
        sys.exit('figure_data.txt has no BL row name in its LANE header')
    lanes_by_code = {
        'BH': 'Beijing holds Nvidia back',
        'BL': bl[1].strip(),
        'CN': 'The companies reach for Nvidia',
        'CH': 'The companies turn to home-made chips',
    }
    fig, cur = [], None                    # the figure's data file: @ LANE KIND DATE DATELABEL SAVED-ID, then T (the line shown)
    for ln in data:
        if ln.startswith('@ '):
            c = ln.split()
            if len(c) != 6: sys.exit(f'figure_data.txt: unexpected record line: {ln}')
            cur = {'lane': lanes_by_code[c[1]], 'code': c[1], 'kind': c[2], 'date': c[3], 'label': c[4].replace('_', ' '), 'saved_id': c[5], 'text': None, 'source': '', 'A': '', 'N': ''}; fig.append(cur)
        elif ln.startswith('T ') and cur is not None and cur['text'] is None: cur['text'] = ln[2:].strip()
        elif ln.startswith('S ') and cur is not None: cur['source'] = ln[2:].strip()
        elif ln.startswith('A ') and cur is not None: cur['A'] = ln[2:].strip()
        elif ln.startswith('N ') and cur is not None: cur['N'] = ln[2:].strip()      # round 8: the record's fixed number (core edit 7)
    # round 13 (Nov 26, 2026): the tier's words follow the data file's own header for the kind "doc" (row B15-043); stop if that header changes
    DOC_HEAD = '# KIND: doc  a government document, an official on the record, or published state media'
    if not any(ln.startswith(DOC_HEAD) for ln in data[:20]):
        sys.exit('figure_data.txt no longer describes the kind doc as the tier words here assume: read its header and reword TIER')
    n_fig = len(fig)
    if n_fig != len(rows): sys.exit(f'{len(rows)} rows in the table but {n_fig} records in figure_data.txt')
    key = lambda d: (d['saved_id'], d['date'], d['lane'], L.norm(d['text']))
    left = sorted(key(d) for d in fig); right = sorted(key(r) for r in rows)
    if left != right:
        diff = [a for a in left if a not in right][:3]
        sys.exit(f'the table and figure_data.txt differ in id, date, row or wording, for example: {diff}')
    bent = dict(rows[0]); bent['text'] = bent['text'] + ' x'       # control: one changed word must show as a difference
    if sorted(key(d) for d in fig) == sorted(key(r) for r in [bent] + rows[1:]): sys.exit('control: a changed wording was not seen')
    records = {key(d): d for d in fig}
    # round 8: the table's record numbers against the numbering of figure_data.txt (N lines kept), with a control
    by_key = {key(r): int(r['n']) for r in rows}
    differs = lambda ns: [(d['saved_id'], n, by_key[key(d)]) for d, n in zip(fig, ns) if by_key[key(d)] != n]
    try: nums = number(fig)
    except ValueError as e: sys.exit(f'figure_data.txt: {e}')
    if differs(nums): sys.exit(f'the table numbers records otherwise than figure_data.txt does (by date, N lines kept), for example: {differs(nums)[:3]}')
    fixed = [(d['saved_id'], d['N']) for d in fig if d['N']]
    try: by_date_only = differs(number([dict(d, N='') for d in fig]))
    except ValueError: by_date_only = ['numbering by date alone failed']
    if fixed and not by_date_only: sys.exit('control: numbering by date alone, the N lines left out, was not seen to differ from the table')
    for r in rows:                         # a date label of words must be the table's shown_as; "-" means a full day is shown
        record = records[key(r)]
        lab = record['label']
        if L.norm(r['source']) != L.norm(record['source']):
            sys.exit(f'record {r["n"]}: the table and figure_data.txt have different source names')
        if record['A']:
            sid, label = record['A'].split(' | ', 1)
            if not (L.P / sid).is_dir(): sys.exit(f'record {r["n"]}: no second saved copy named {sid}')
            if (L.norm(r['also_source']), r['also_address']) != (L.norm(label), L.url_of(sid)):
                sys.exit(f'record {r["n"]}: the table and figure_data.txt have different second sources')
            r['also_id'] = sid
        elif r['also_address']:
            sys.exit(f'record {r["n"]}: the table has a second source absent from figure_data.txt')
        else:
            r['also_id'] = ''
        if (lab == '-') != bool(FULL_DAY.fullmatch(r['shown_as'])) or (lab != '-' and lab != r['shown_as']):
            sys.exit(f'record {r["n"]}: the table shows "{r["shown_as"]}" but figure_data.txt has the label "{lab}"')
    retired = {ln.split('\t')[0] for ln in RETIRED.read_text(encoding='utf-8').splitlines() if ln.strip()}
    if len(retired) < 10: sys.exit('control: the list of ids not to cite is shorter than expected')
    hit = sorted({r[field] for r in rows for field in ('saved_id', 'also_id') if r[field] in retired})
    if hit: sys.exit(f'the table cites ids that may no longer be cited: {hit}')

    # quotation marks: keep only where the words stand in the saved copy
    report, hidden = [], {}
    for r in rows:
        kept = []
        def fix(m, r=r, kept=kept):
            q = m.group(1)
            for sid in (r['saved_id'], r['also_id']):
                if sid and L.has(q, sid):
                    kept.append((sid, q))
                    report.append((r['n'], sid, 'kept', q))
                    return m.group(0)
            why = 'too short to check' if len(L.squash(q)) < 6 else 'not in the saved copy'
            report.append((r['n'], r['saved_id'], f'marks taken off ({why})', q)); return q
        r['what'] = CURLY.sub(fix, r['text'])
        if '“' in r['what'].replace('“', '', len(kept)) or r['what'].count('“') != r['what'].count('”'):
            sys.exit(f'record {r["n"]}: unbalanced quotation marks in: {r["text"]}')
        hidden[r['n']] = kept
        r['src'] = '; '.join(filter(None, (r['source'], r['also_source'], TIER[r['kind']])))
        r['links'] = '; '.join(filter(None, (r['address'], r['also_address'])))
    n_kept = sum(1 for x in report if x[2] == 'kept')
    off = [x for x in report if x[2] != 'kept']
    # controls: the phrase check can pass and can fail
    if not L.has('as Beijing withholds approval', 'cn-clips-evidence-1'): sys.exit('control: a known true phrase was not found')
    if L.has('Beijing has published a ban on the purchase of Nvidia chips', 'cn-clips-evidence-1'): sys.exit('control: a planted false phrase was found')

    known = {ln.split('\t')[0] for f in ARGREFS for ln in f.read_text(encoding='utf-8').splitlines() if ln.strip() and not ln.startswith('#')}
    extra, seen = [], set()
    for r in rows:
        kind = {'doc': 'DOC', 'press': 'PRESS'}.get(r['kind']) or ('REC' if 'reported by' in r['source'] else 'FIL')
        for sid, label, address in (
            (r['saved_id'], r['source'], r['address']),
            (r['also_id'], r['also_source'], r['also_address']),
        ):
            if not sid or sid in known or sid in seen: continue
            seen.add(sid)
            extra.append(f'{sid}\t{kind}\t{label}, {r["shown_as"]}\t{address}')
    (HERE / 'timeline_extra_refs.tsv').write_text(
        '# Reference lines for saved ids of the timeline that the argument\'s two reference files do not hold (written by gen_timeline.py)\n'
        + '\n'.join(extra) + '\n', encoding='utf-8')

    count = {k: sum(1 for r in rows if r['kind'] == k) for k in TIER}
    on_record = count['doc'] + count['rec']
    first, last = rows[0]['shown_as'], rows[-1]['shown_as']
    off_n = sorted({int(x[0]) for x in off})
    lanes = {v: sum(1 for r in rows if r['lane'] == v) for v in lanes_by_code.values()}
    loose = [r for r in rows if not FULL_DAY.fullmatch(r['shown_as'])]
    loose_txt = '; '.join(f'{r["shown_as"]} ({r["source"]})' for r in loose)
    notes = [
        "Draft by Claude, Anthropic's model.",      # round 11 (Nov 26, 2026): the session's ruling, no ""
        f'Drawn word for word from the table of records of the project\'s main figure (figure/figure_events.tsv): {len(rows)} records, in date order, from {first} to {last}.',   # round 10b: no script name
        'Each line: date | row | what | source | address. The second field is the row of the main figure the record sits in: which side it is about and which way it points. '
        'A row\'s name gives that direction only: a row holds statements, filings, notices and press reports alike, and not every record in it is itself an act of holding back or letting in. '
        'It does not name the speaker; the source field does. When there are two sources, the addresses are in source order.',      # round 12 (Nov 26, 2026): what a row name says, and what it does not
        'For a press report the date is the report\'s day; what it reports can be earlier (the record of Nov 7, 2023 reports an order of August 2023).',      # round 12: checked below
        f'Two tiers, marked at the end of each source: {on_record} records are on the record ({count["doc"]} government documents, officials or published state media, {count["rec"]} companies or named people outside government); {count["press"]} are press reports citing unnamed people.',
        'By row: ' + '; '.join(f'{v}, {n}' for v, n in lanes.items()) + '.',
        f'Words between quotation marks are the source\'s own: all {n_kept} such phrases were found in a saved source linked to the record.'
        + (f' In {len(off_n)} records the figure\'s line put marks round words that are not in the saved copy (our English for a Chinese word, or a summary); the marks are taken off here.' if off else ''),
        'English given for Chinese sources is ours, not an official translation.',
    ] + ([f'{len(loose)} records have no exact day, and their date field carries the figure\'s own words: {loose_txt}. Each stands in the list where the figure places it; that place is not a date.'] if loose else [])
    ex = [r for r in rows if r['shown_as'] == 'Nov 7, 2023' and r['kind'] == 'press' and 'in August 2023' in r['text']]      # round 12: the note's example
    if len(ex) != 1: sys.exit('the note\'s example (a press record of Nov 7, 2023 reporting an order of August 2023) is not in the table')
    # the notes hold no straight double quotes: the builder would read them as quotations
    if any('"' in n for n in notes): sys.exit('a note holds a straight double quote')
    base_notes = notes
    base = ['# The record as a dated list', f'@deck {len(rows)} dated records of what Chinese authorities did about Nvidia chips and what China\'s AI companies did, on the record or as the press reported it, as plain lines for pasting.', '']
    base += [f'@note {n}' for n in base_notes] + ['', '| date | row | what | source | address |']
    for r in rows:
        base += [f'!! {sid} | {q}' for sid, q in hidden[r['n']]]      # a record's check lines stand above its own row, never beside the next record's date
        base.append(f'| {r["shown_as"]} | {r["lane"]} | {r["what"]} | {r["src"]} | {r["links"]} |')
    (HERE / 'timeline_base.txt').write_text('\n'.join(base) + '\n', encoding='utf-8')
    (HERE / 'quote_marks_report.tsv').write_text('record\tsaved_id\tresult\tphrase\n' + '\n'.join('\t'.join(x) for x in report) + '\n', encoding='utf-8')

    p = subprocess.run([sys.executable, '-I', str(BUILD), str(HERE / 'timeline_base.txt'), '--refs', str(HERE / 'timeline_extra_refs.tsv'),
                        '--title', 'Chip Policy Timeline', '--eyebrow', 'China chip policy · the dated record as plain text', '--md-only'],
                       capture_output=True, text=True)
    print(p.stdout.strip())
    if p.returncode != 0:
        print(p.stderr.strip()); sys.exit('cn_doc_build.py did not pass: timeline.txt NOT written')

    txt = [f'The record as a dated list: {len(rows)} records, {first} to {last}', ''] + notes + ['', 'date | row | what | source | address']
    txt += [' | '.join((r['shown_as'], r['lane'], r['what'], r['src'], r['links'])) for r in rows]
    (HERE / 'timeline.txt').write_text('\n'.join(txt) + '\n', encoding='utf-8')

    print(f'timeline: {len(rows)} records from {EVENTS.name} (figure_data.txt holds {n_fig}); {first} to {last}')
    print(f'tiers: {count["doc"]} government documents, officials or published state media, {count["rec"]} companies or named people on the record, {count["press"]} press reports citing unnamed people')
    print('rows: ' + '; '.join(f'{v} {n}' for v, n in lanes.items()))
    print(f'compared with figure_data.txt: id, date, date label, row and wording equal in {len(rows)} of {len(rows)} records; ids on the do-not-cite list: 0 of {len(retired)} listed')
    print(f'record numbers: equal to the numbering of figure_data.txt in {len(rows)} of {len(rows)} (by date, Beijing\'s rows first; kept by an N line: '
          f'{", ".join(f"{s} as {n}" for s, n in fixed) or "none"}); control: numbering by date alone differs from the table in {len(by_date_only)} records')
    print(f'records with no exact day: {len(loose)} ({loose_txt or "none"})')
    print(f'quoted phrases: {len(report)} in the table; {n_kept} found in the saved copy and kept; {len(off)} not found, marks taken off (records {", ".join(map(str, off_n)) or "none"})')
    for x in off: print(f'  record {x[0]} [{x[1]}] {x[2]}: {x[3]}')
    print(f'records with a second source and address: {sum(bool(r["also_id"]) for r in rows)}')
    print(f'extra reference lines written: {len(extra)}; controls: true phrase found, false phrase rejected')


if __name__ == '__main__':
    main()
