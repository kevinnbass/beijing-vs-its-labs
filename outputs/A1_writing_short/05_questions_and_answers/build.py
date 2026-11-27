#!/usr/bin/env python3
"""Idea 5: build the questions-and-answers page and check its shape and its counts.

Run: python3 -I build.py
1. Builds questions_answers.md and .html with scripts/cn_doc_build.py (quotations and hidden statements checked).
2. Shape: ten questions; each answer at most three sentences; each answer cites at least one saved source.
   Sentences are counted on the answer text with reference marks removed: a sentence ends at . ! or ? followed by a
   space or the end. Inside a quotation only its last mark counts. Control: a four-sentence answer must count as 4.
3. Counts the text shows, each taken from a file and compared with the words in the text (the run stops if they differ):
     the argument's points, sources and limits     argument/argument_base.txt; the sources from the argument's last build line
                                                   (atlas/core_edit/hand_out/ARGUMENT_FINAL.txt), checked against ARGUMENT_referenced.html
     state-media items, and those that only warn    tables/state_media_items.tsv (subjects and warnings before, during and after the burst)
     the applications returned without action        tables/house_licence_table.tsv (those for 55% of the table's chips)
   and no id on the do-not-cite list (loose_ends/hkexnews_saved_ids.tsv) may be cited.
Exit 1 if the build or any check fails.
"""
import csv, re, subprocess, sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parents[2]
ROOT = HERE.parents[4]
BASE = HERE / 'questions_answers_base.txt'
CITE = re.compile(r'\[((?:cn|ms|man|cnpol|clip)-[A-Za-z0-9-]+)\]')
WORDS = {4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight'}


def sentences(answer):
    s = CITE.sub('', answer)
    s = re.sub(r'"([^"]+)"', lambda m: re.sub(r'[.!?](?=.)', '', m.group(1)), s)   # keep only a quotation's last mark
    s = re.sub(r'\s+', ' ', s).strip()
    return len(re.findall(r'[.!?](?=\s|$)', s))


def table(name):
    rows = list(csv.reader((ln for ln in (PROJ / 'tables' / name).read_text(encoding='utf-8').splitlines() if ln.strip() and not ln.startswith('#')), delimiter='\t'))
    return [dict(zip(rows[0], r)) for r in rows[1:]]


def day(iso):
    d = date.fromisoformat(iso)
    return f'{["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"][d.month - 1]} {d.day}'


def main():
    p = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts' / 'cn_doc_build.py'), str(BASE), '--refs', str(HERE / 'extra_refs.tsv'),
                        '--title', 'China Nvidia Questions', '--eyebrow', 'China chip policy · ten questions and answers'], capture_output=True, text=True)
    print(p.stdout.strip())
    if p.returncode != 0: print(p.stderr.strip()); sys.exit('cn_doc_build.py did not pass')
    assert sentences('One. Two: "a. b. c." [cn-x] Three? Four.') == 4 and sentences('Yes. He said: "No. Never." [cn-x] Done.') == 3, 'control: the sentence counter is wrong'
    text = BASE.read_text(encoding='utf-8')
    rows, bad, on = [], [], False
    for ln in text.splitlines():
        if ln.startswith('## '): on = ln.strip() == '## The ten questions'; continue
        m = re.match(r'(\d+)\. \*\*([^*]+\?)\*\* (.*)', ln)
        if on and m:
            k, q, a = int(m.group(1)), m.group(2), m.group(3)
            n, ids = sentences(a), CITE.findall(a)
            rows.append((k, q, n, len(set(ids))))
            if n > 3: bad.append(f'question {k}: {n} sentences')
            if not ids: bad.append(f'question {k}: no source')
    if len(rows) != 10 or [r[0] for r in rows] != list(range(1, 11)): bad.append(f'{len(rows)} questions found, expected 10 numbered 1 to 10')

    # the argument's own counts
    arg = (PROJ / 'argument' / 'argument_base.txt').read_text(encoding='utf-8')
    # round 10b (Nov 25, 2026): the sources are counted by the argument's own last build line (atlas/core_edit/hand_out/ARGUMENT_FINAL.txt),
    # as outputs/ROUND10.md asks (argument_refs.tsv alone gives one fewer: the argument also cites a row of argument_refs_more.tsv);
    # control: the built argument page lists the same number of references
    fin = [ln for ln in (PROJ / 'atlas' / 'core_edit' / 'hand_out' / 'ARGUMENT_FINAL.txt').read_text(encoding='utf-8').splitlines() if ln.startswith('argument: ')]
    n_src = int(re.match(r'argument: (\d+) sources', fin[-1]).group(1)) if fin else -1
    footer = (PROJ / 'ARGUMENT_referenced.md').read_text(encoding='utf-8').rstrip().splitlines()[-1]
    match = re.search(r'^Build check: .*saved copies of (\d+) sources', footer)
    if not match or int(match[1]) != n_src:
        bad.append("the argument's Markdown footer and build log disagree on the source count")
    n_listed = len(re.findall(r'<li id="ref-\d+"', (PROJ / 'ARGUMENT_referenced.html').read_text(encoding='utf-8')))
    if n_listed != n_src: bad.append(f'the argument\'s last build line says {n_src} sources, its page lists {n_listed}')
    n_pts = sum(1 for ln in arg.splitlines() if re.match(r'\d+\. ', ln))
    sec = re.search(r'(?ms)^## 5\. (\w+) limits on the claim$(.*?)^## ', arg)
    n_lim = len(re.findall(r'(?m)^\d+\. ', sec.group(2))) if sec else 0
    print(f'argument, counted by script: {n_pts} points, {n_src} sources, {n_lim} limits')
    for said in (f'The full argument has {n_pts} points and {n_src} sources', f'with {WORDS.get(n_lim)} limits'):
        if said not in text: bad.append(f'the text does not say "{said}"')
    most = max(r[3] for r in rows)
    if f'one to {WORDS.get(most, most)} sources' not in text: bad.append(f'the text does not say "one to {WORDS.get(most, most)} sources" (the most any answer cites is {most})')

    # state media: all items, and those that only warn
    sm = table('state_media_items.tsv')
    warnings = [r for r in sm if r['stance'] == 'warns']
    warn = sorted(r['date'] for r in warnings)
    compute_warnings = sum(r['subject'] == 'chips for AI computing' for r in warnings)
    other_warnings = [r for r in warnings if r['subject'] != 'chips for AI computing']
    other_ids = [r['saved_id'] for r in other_warnings]
    if other_ids != ['cn-media-stdaily-security-forum']:
        bad.append(f'the warning subjects no longer support naming only the forum report separately: {other_ids}')
    else:
        forum = other_warnings[0]
        said = (f"a {day(forum['date'])} {forum['outlet']} report that describes a call at a security forum "
                f"to switch faster to home-made software and hardware [{forum['saved_id']}]")
        if said not in text:
            bad.append(f'the text does not say "{said}"')
    start, end = '2025-07-31', '2025-09-24'  # the window in argument point 4
    early = [d for d in warn if d < start]
    win = [d for d in warn if start <= d <= end]
    late = [d for d in warn if d > end]
    h200 = [d for d in late if '2025-12-09' <= d <= '2026-01-14']
    span = f'{day(win[0])} to {day(win[-1])}, {win[-1][:4]}'
    h200_span = f'{day(h200[0])}, {h200[0][:4]} to {day(h200[-1])}, {h200[-1][:4]}'
    print(f'state media, from tables/state_media_items.tsv: {len(sm)} items; {len(warn)} only warn '
          f'({compute_warnings} about chips for AI computing; {len(early)} before, {len(win)} from {span}, {len(late)} after); '
          f'{len(h200)} of the later warnings from {h200_span}')
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    alld = sorted(r['date'] for r in sm); window = f'from {months[int(alld[0][5:7]) - 1]} {alld[0][:4]} to {months[int(alld[-1][5:7]) - 1]} {alld[-1][:4]}'
    print(f"state media: the table's items are dated {alld[0]} to {alld[-1]} ({window})")
    compute = sum(r['subject'] == 'chips for AI computing' for r in sm)
    products = sum(r['subject'] == 'a product with an Nvidia chip' for r in sm)
    for said in (
        f'the {len(sm)} state and Party media items on Nvidia and its chips found {window}',
        f'{len(win)} of the {len(warn)} that only warn',
        f'Of the {len(warn)} items that only warn, {compute_warnings} are about the chips for AI computing.',
        span,
        'one is earlier' if len(early) == 1 else f'{len(early)} are earlier',
        f'{len(h200)} of the {len(late)} found later date from {h200_span}',
        f'{compute} items on chips for AI computing separately from the {products} on products with an Nvidia chip',
    ):
        if said not in text: bad.append(f'the text does not say "{said}"')
    if 'warn against' in text: bad.append('the text says "warn against": the table counts warnings that do not speak of buying')

    # Washington's table of licence applications
    hl = table('house_licence_table.tsv')
    chips = lambda r: int(r['chip_count'].replace(',', ''))
    total = sum(chips(r) for r in hl); rwa = sum(chips(r) for r in hl if r['status'] == 'RWA')
    statuses = sorted({r['status'] for r in hl}); pct = round(100 * rwa / total)
    appr = [r for r in hl if r['status'].startswith('Approved')]
    print(f'licence table, from tables/house_licence_table.tsv: {len(hl)} applications, {total:,} chips; returned without action {rwa:,} ({100 * rwa / total:.2f}%, shown as {pct}%); '
          f'approved {sum(chips(r) for r in appr):,} in {len(appr)}, every one marked "Approved, not shipped": {all(r["status"] == "Approved, not shipped" for r in appr)}; statuses {statuses}')
    if not appr or not all(r['status'] == 'Approved, not shipped' for r in appr): bad.append('not every approval in the table is marked "Approved, not shipped"')
    # round 13 (Nov 26, 2026, core batch 15, rows B15-056 to -058): Washington returned the APPLICATIONS, never the chips, as the argument now says
    said = f'returned without action the applications for {pct}% of the chips'
    if said not in text: bad.append(f'the text does not say "{said}"')
    if f'{pct}% of the chips in the applications the summary records were in applications returned' in text: bad.append('the text keeps the wording core batch 15 replaced')
    if f'returned without action the applications for {pct + 1}% of the chips' in text: bad.append('control: a changed share was found')
    if f'{total:,}' not in text: bad.append(f'the hidden check line with the table\'s total, {total:,}, is missing')
    if 'more than half' in text: bad.append('the text says "more than half"')

    # ids that may no longer be cited
    retired = {ln.split('\t')[0] for ln in (PROJ / 'loose_ends' / 'hkexnews_saved_ids.tsv').read_text(encoding='utf-8').splitlines() if ln.strip()}
    cited = set(CITE.findall(text)) | {ln[2:].split('|', 1)[0].strip() for ln in text.splitlines() if ln.startswith('!!')}
    hit = sorted(cited & retired)
    print(f'ids cited: {len(cited)}; on the do-not-cite list of {len(retired)}: {len(hit)}')
    if len(retired) < 10: bad.append('control: the do-not-cite list is shorter than expected')
    if hit: bad.append(f'cites ids that may no longer be cited: {hit}')

    for k, q, n, s in rows: print(f'  {k}. {q}  sentences in the answer: {n}; sources cited: {s}')
    print(f'questions: {len(rows)}; longest answer: {max(r[2] for r in rows)} sentences; control: a four-sentence answer counts as 4')
    if bad: print('\n'.join(bad)); sys.exit(1)


if __name__ == '__main__':
    main()
