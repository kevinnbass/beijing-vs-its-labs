#!/usr/bin/env python3
"""Idea 8: the numbers and names the page shows, each taken from a file and compared with the page's own words.

Run: python3 -I check_numbers.py     (reads only; exit 1 on any difference)
  tables/house_licence_table.tsv     chips in the table, chips returned without action and their share, chips approved
  tables/trade_derived_figures.tsv   China's imports of computer parts, Jan to Sep 2025 and 2026, as printed
  loose_ends/hkexnews_saved_ids.tsv  ids that may no longer be cited: none may stand in the page
  outputs/<folder>/<folder>/<file>   the five notes the page names must exist
Round 5 (Nov 24, 2026) adds: the share with the application of 445,000 both ways; words the page copies from the argument
  (each must stand in argument/argument_base.txt); wordings withdrawn by core edits 5 and 6 (none may stand in the page).
Round 8 (Nov 25, 2026, core edits 7 and 7c) adds one copied phrase, Nvidia's sentence as The Standard carries it (ruling
R3a), and withdraws "one carrier" and "one site" (the statement has two carriers).
Round 9 (Nov 25, 2026, core edit 8b and voucher rounds 5 and 6) changes three copied phrases (point 11's words on Alibaba and
the 27 transcripts; the five cities, Chengdu now read in a full copy), adds the phrases the page now copies (banned-import
lists, customs and tariff texts, the reply's words, the catalogues, the SEC record of Nov 25, the hearing prints, Chongqing,
the count's searches) and withdraws nine wordings the core replaced and one this round found untrue on the page ("the reply names no chip
maker"); a control finds each of the ten in the page's before-copy of round 9.
Controls: a number changed by one, a share changed by 0.1 and a count changed in a copied phrase must not be found.
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

# the application of 445,000 the committee names (round 5): the table's only Nvidia row for Tencent of Dec 19, 2025, and
# the returned share counted with the 445,000 both ways (the argument's section 4; atlas/core_edit/APPLIED_6.txt B1)
ten = [r for r in hl if r['date_submitted'] == '12/19/2025' and r['exporter'] == 'Nvidia' and r['consignee'].startswith('Tencent')]
if len(ten) != 1 or chips(ten[0]) != 75000 or ten[0]['status'] != 'Approved, not shipped':
    bad.append(f'the table does not hold exactly one approved Nvidia row for Tencent of Dec 19, 2025 for 75,000 chips: {ten}')
else:
    same, further = 100 * rwa / (total - 75000 + 445000), 100 * rwa / (total + 445000)
    print(f'with the 445,000: {same:.2f}% if the Tencent row of Dec 19, 2025 is that application, {further:.2f}% if it is a further one')
    for said in ('The table\'s only Tencent row of that date is an Nvidia application for 75,000 chips, approved',
                 f'it would be {same:.1f}% if that row is the application and {further:.1f}% if the 445,000 is a further one'):
        if said not in text: bad.append(f'the page does not say "{said}"')
    if f'{same + 0.1:.1f}%' in text: bad.append('control: a changed share was found in the page')

# words the page copies from the argument (round 5): each must stand, as written, in argument/argument_base.txt and in the page
ARG = (PROJ / 'argument' / 'argument_base.txt').read_text(encoding='utf-8')
COPIED = ['the latest annual reports of fifteen US-listed Chinese companies',
          "only Alibaba's says a Chinese authority asked Chinese technology companies to stop buying certain chips",     # round 9 (core edit 8b, Frt1-026)
          'the 76 results-call transcripts of eight Chinese companies, November 2023 to November 2026, and 42 records of four smaller model makers',   # round 8: 43 -> 42, as the argument now has it (changed after edit 7, Nov 25, 2026)
          'no speaker and no record names a Chinese authority as restricting chip purchases, though 27 of the transcripts leave out passages spoken in another language',   # round 9: 25 -> 27 (core edit 8b)
          'in Chinese records of 25 of those 27 calls', 'no speaker names a Chinese authority beside a chip word either',             # round 9 (core edit 8b)
          "nor do the President's own posts on four calls with Xi and on two rounds",
          'of the round of September 2026,',
          'or of the video calls of Dec 5, 2025 and Apr 30, 2026 was found in the Treasury',
          'names five calls between Xi and the President from January 2025 to November 2026; both sides',
          "Of five cities' voucher rules sought, Suzhou's and Wuhu's were reached, Nanjing's only through an application guide, Qingyang's only through press accounts, and Chengdu's at first only through press accounts and then in a consultancy's full copy of its revised rules, compared by eye with the bureau's signed file, a scan",   # round 9 (voucher round 5)
          "reached the text of Chongqing's measures of August 2025, held only as their issuing notice in an Internet Archive capture",   # round 9
          'found by searches that went province by province and city by city, saved and read',                                         # round 9 (ruling S1 of the voucher rounds)
          'nor do the lists of banned imports in force [cn-ga31-importcat-43]; the sixth batch, of 2005, lists 17 kinds of asbestos and chemicals',   # round 9 (core edit 8b)
          'the announcements of the customs administration and of the Customs Tariff Commission found for January 2024 to November 2026',
          'set no licence, hold or chip-specific inspection on importing these goods, and none names Nvidia or a chip model',
          'not a census of every numbered announcement',
          'speaks only of exporters and export controls; it does not answer the question about imports',                               # round 9 (core edit 8b, Fra01-021)
          'three Chinese catalogues, of technologies banned or restricted from import, of goods under import licence, and of dual-use items and technologies under import and export licence',
          'or on Nov 25, 2026 at 06:49 UTC [cn-ga31-official-sec-submissions-20261125]',
          '409 Senate hearing prints of the 119th Congress issued or changed since Apr 22, 2026 holds none of this hearing',
          'Tianjin\'s rule names as its basis the national computing-network opinions of December 2023, which say "鼓励面向中小企业发放算力券、运力券"',
          'no saved page says under which line an importer in China or Hong Kong declares the chips',
          'Nvidia\'s own classification list, "provided for informational purposes only", gives the subheadings it applies itself: 8471.80 for its HGX H200 and HGX H20 parts, 8473.30 for its H200 NVL and H20 NVL16 parts and 8471.50 for its DGX H200 systems',
          'has nothing on Nvidia after the notice of Sept 15, 2025',
          'posted Jun 5, 2026, lists the further investigation with no outcome',
          'its report of Oct 13, 2026 on the RTX PRO 5500',
          "neither document says whether",
          'One Chinese official text sets the chip beside the talks: asked on Jul 18, 2025',            # round 7 (core edit 6e, G): point 21's new sentence
          'the answer neither confirms nor denies that the chip was part of the talks',
          'despite receiving some licenses, we have since stopped shipping H200s to China']   # round 8 after core edit 7c (R3a): The Standard's words, as point 19 quotes them
low_arg = ARG.lower()
miss_arg = [c for c in COPIED if c.lower() not in low_arg]
miss_page = [c for c in COPIED if c.lower() not in text.lower()]
print(f'copied from the argument: {len(COPIED) - len(miss_arg)} of {len(COPIED)} stand in the argument, {len(COPIED) - len(miss_page)} of {len(COPIED)} in the page')
if miss_arg: bad.append(f'no longer in the argument: {miss_arg}')
if miss_page: bad.append(f'not in the page: {miss_page}')
if COPIED[2].replace('76', '77').lower() in low_arg: bad.append('control: a changed count was found in the argument')

# wordings withdrawn by core edits 5 and 6 (round 5): none may stand in the page
WITHDRAWN = ['were not reached (qingyang', 'voucher rules of five cities were not reached', 'read it two ways', 'no chinese document found states it',
             'states the motive', "commerce department's table", 'shows that application at 75,000', 'which the table shows at 75,000',
             'under which line the chips are declared', 'four others are not', 'its interim chief executive', '31 saved official pages', '30 official readouts',
             '24 of the transcripts', 'hgx boards', 'nvl16 cards',     # the last three: touch-up 6b (Nov 24, 2026), items 22 and 26
             'one carrier', 'one site',                                # core edit 7c (Nov 25, 2026, ruling R3a): Nvidia's statement has two carriers
             # round 9 (core edit 8b and the voucher rounds, Nov 25, 2026): words the core replaced
             'asked firms to stop buying chips', '25 of the transcripts leave out', 'what exporters must do', "chengdu's and qingyang's only through press",
             'that could be read (all but one', "pulled china's ai companies away", 'catalogues of goods and technologies banned',
             'which is of the rules found, not a census', "the cyberspace regulator's review office",
             'the reply names no chip maker']          # round 9: the reply names AMD (its own terminal products) and chip firms it invests in; it names no maker of the servers or their chips
NEW9 = WITHDRAWN[-10:]
hits = [w for w in WITHDRAWN if w in text.lower()]
print(f'withdrawn wordings searched: {len(WITHDRAWN)}; found: {len(hits)}')
if hits: bad.append(f'withdrawn wordings stand in the page: {hits}')
before9 = HERE / 'what_would_change_base.before-round9-20261125.txt'      # control: the page as round 8 left it holds every wording round 9 withdrew
if before9.is_file():
    old_low = before9.read_text(encoding='utf-8').lower()
    seen = [w for w in NEW9 if w in old_low]
    print(f'control: {len(seen)} of the {len(NEW9)} wordings withdrawn in round 9 are found in the before-copy of round 9')
    if len(seen) != len(NEW9): bad.append(f'control: withdrawn wordings not found in the before-copy, so the search may be wrong: {[w for w in NEW9 if w not in seen]}')
if 'then interim chief executive' not in text.lower(): bad.append('control: the phrase "then interim chief executive" is not found by the same search')

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
