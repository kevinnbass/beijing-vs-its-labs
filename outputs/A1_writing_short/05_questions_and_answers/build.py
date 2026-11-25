#!/usr/bin/env python3
"""Idea 5: build the questions-and-answers page and check its shape and its counts.

Run: python3 -I build.py
1. Builds questions_answers.md and .html with scripts/cn_doc_build.py (quotations and hidden statements checked).
2. Shape: ten questions; each answer at most three sentences; each answer cites at least one saved source.
   Sentences are counted on the answer text with reference marks removed: a sentence ends at . ! or ? followed by a
   space or the end. Inside a quotation only its last mark counts. Control: a four-sentence answer must count as 4.
3. Counts the text shows, each taken from a file and compared with the words in the text (the run stops if they differ):
     the argument's points, sources and limits     argument/argument_base.txt, argument/argument_refs.tsv
     state-media items, and those that only warn    tables/state_media_items.tsv (75; 19 only warn, 16 of them from Jul 31 to Sept 24, 2025 and 3 later)
     the share of chips returned without action     tables/house_licence_table.tsv (55% of the table's chips)
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
    n_src = sum(1 for ln in (PROJ / 'argument' / 'argument_refs.tsv').read_text(encoding='utf-8').splitlines() if ln.strip() and not ln.startswith('#'))
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
    warn = sorted(r['date'] for r in sm if r['stance'] == 'warns')
    win = [d for d in warn if d <= '2025-09-24']; late = [d for d in warn if d > '2025-09-24']      # the burst after the summons, and the warnings found later (core edit 6)
    span = f'{day(win[0])} to {day(win[-1])}, {win[-1][:4]}'
    print(f'state media, from tables/state_media_items.tsv: {len(sm)} items; {len(warn)} only warn, dated {warn[0]} to {warn[-1]} ("{span}")')
    for said in (f'the {len(sm)} state and Party media items found', f'{len(win)} of the {len(warn)} that only warn', span, f'the {dict([(3, "three")]).get(len(late), len(late))} found later'):
        if said not in text: bad.append(f'the text does not say "{said}"')
    if 'warn against' in text: bad.append('the text says "warn against": two of the seven items do not speak of buying')

    # Washington's table of licence applications
    hl = table('house_licence_table.tsv')
    chips = lambda r: int(r['chip_count'].replace(',', ''))
    total = sum(chips(r) for r in hl); rwa = sum(chips(r) for r in hl if r['status'] == 'RWA')
    statuses = sorted({r['status'] for r in hl}); pct = round(100 * rwa / total)
    appr = [r for r in hl if r['status'].startswith('Approved')]
    print(f'licence table, from tables/house_licence_table.tsv: {len(hl)} applications, {total:,} chips; returned without action {rwa:,} ({100 * rwa / total:.2f}%, shown as {pct}%); '
          f'approved {sum(chips(r) for r in appr):,} in {len(appr)}, every one marked "Approved, not shipped": {all(r["status"] == "Approved, not shipped" for r in appr)}; statuses {statuses}')
    if not appr or not all(r['status'] == 'Approved, not shipped' for r in appr): bad.append('not every approval in the table is marked "Approved, not shipped"')
    if f'{pct}% of the chips in the applications the summary records' not in text: bad.append(f'the text does not say "{pct}% of the chips in the applications the summary records"')
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
