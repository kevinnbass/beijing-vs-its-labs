#!/usr/bin/env python3
"""Idea 8: the numbers and names the page shows, each taken from a file and compared with the page's own words.

Run: python3 -I check_numbers.py     (reads only; exit 1 on any difference)
  tables/house_licence_table.tsv     chips in the table, chips returned without action and their share, chips approved
  tables/trade_derived_figures.tsv   China's imports of computer parts, Jan to Sep 2025 and 2026, as printed
  loose_ends/hkexnews_saved_ids.tsv  ids that may no longer be cited: none may stand in the page
  outputs/<folder>/<folder>/<file>   the five notes the page names must exist
Control: a number changed by one must not be found in the page.
"""
import csv, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parents[2]
text = (HERE / 'what_would_change_base.txt').read_text(encoding='utf-8')
bad = []

rows = list(csv.reader((ln for ln in (PROJ / 'tables' / 'house_licence_table.tsv').read_text(encoding='utf-8').splitlines() if ln.strip() and not ln.startswith('#')), delimiter='\t'))
hl = [dict(zip(rows[0], r)) for r in rows[1:]]
chips = lambda r: int(r['chip_count'].replace(',', ''))
total = sum(chips(r) for r in hl); rwa = sum(chips(r) for r in hl if r['status'] == 'RWA')
appr = sum(chips(r) for r in hl if r['status'] == 'Approved, not shipped'); pct = round(100 * rwa / total)
print(f'licence table: {len(hl)} rows, {total:,} chips; RWA {rwa:,} ({100 * rwa / total:.2f}%, shown as {pct}%); "Approved, not shipped" {appr:,}; plain "Approved" rows: {sum(1 for r in hl if r["status"] == "Approved")}')
for said in (f'{total:,} chips', f'{rwa:,} are in applications marked RWA', f'{pct}% of the chips in the applications the summary records', f'Another {appr:,} are in applications marked',
             f"the table's {len(hl)} rows", f'approved {appr:,} of', f'returned {rwa:,} without action'):
    if said not in text: bad.append(f'the page does not say "{said}"')
if f'{rwa + 1:,}' in text: bad.append('control: a changed number was found in the page')

line = next((ln for ln in (PROJ / 'tables' / 'trade_derived_figures.tsv').read_text(encoding='utf-8').splitlines()
             if ln.startswith('China customs table 14, Parts and accessories of automatic data processing machines: Jan-Sep 2025 and Jan-Sep 2026 as printed')), None)
if not line: bad.append('the customs line is not in tables/trade_derived_figures.tsv')
else:
    m = re.search(r'(\d+) -> (\d+)', line.split('\t')[2])
    a, b = int(m.group(1)) / 1e6, int(m.group(2)) / 1e6            # thousand US$ to billion US$
    print(f'customs, parts and accessories of computers, as printed: Jan-Sep 2025 US${a:.1f} billion; Jan-Sep 2026 US${b:.1f} billion')
    if f'US${b:.1f} billion in January to September 2026, against US${a:.1f} billion a year earlier' not in text: bad.append('the page does not give the two customs figures as the table has them')

retired = {ln.split('\t')[0] for ln in (PROJ / 'loose_ends' / 'hkexnews_saved_ids.tsv').read_text(encoding='utf-8').splitlines() if ln.strip()}
cited = set(re.findall(r'\[((?:cn|ms|man|cnpol|clip)-[A-Za-z0-9-]+)\]', text)) | {ln[2:].split('|', 1)[0].strip() for ln in text.splitlines() if ln.startswith('!!')}
hit = sorted(cited & retired)
print(f'ids cited: {len(cited)}; on the do-not-cite list of {len(retired)}: {len(hit)}')
if len(retired) < 10: bad.append('control: the do-not-cite list is shorter than expected')
if hit: bad.append(f'cites ids that may no longer be cited: {hit}')

notes = [ln.split(': ', 1)[1] for ln in text.splitlines() if ln.startswith('- Idea ')]
missing = [n for n in notes if not (PROJ / 'outputs' / Path(*[p.strip() for p in n.split(' / ')])).is_file()]
print(f'notes named: {len(notes)}; missing: {len(missing)}')
if len(notes) != 5: bad.append(f'{len(notes)} notes named, expected 5')
if missing: bad.append(f'notes named but not found: {missing}')
if (PROJ / 'outputs' / 'A10_trade_data' / 'no_such_note.html').is_file(): bad.append('control: a missing file was reported as present')

items = re.findall(r'(?m)^\*\*(\d+)\. ', text)
print(f'documents listed: {len(items)}')
if items != [str(i) for i in range(1, len(items) + 1)]: bad.append(f'the documents are not numbered 1 to {len(items)} in order')
print('result: every number, id and note name agrees with its file' if not bad else 'result: FAILED\n' + '\n'.join(bad))
sys.exit(1 if bad else 0)
