#!/usr/bin/env python3
"""Build the table files of ideas 34 and 42 from the saved copies, and a check file for each idea.

Run: python3 -I build_tables.py            (from anywhere; reads research/primary/<id>/, writes only into this folder)

Reads   the saved UN Comtrade monthly answers  cn-o34-comtrade-m-YYYYMM   (reporters: USA 842, Hong Kong 344; China 156 was asked for too)
        the saved China customs tables         cn-o34-gacc-t14-imports-YYYYMM, cn-le18-gacc-t14-202509, cn-o34-gacc-t16-imports-bycountry-202609
        (round 4, read only, another builder's folder loose_ends/L18_trade_data and the core's tables/)
        Singapore's raw table answers          loose_ends/L18_trade_data/raw_singstat/*.json, each tested against the sha256 in its MANIFEST.tsv.
                                               They are NOT in research/primary, so scripts/cn_has.py cannot test them.
        Hong Kong's own monthly division tables cn-le18-hk-csd-410-50031 (imports), cn-le18-hk-csd-410-50032 (total exports)
        Taiwan's exports by destination        loose_ends/L18_trade_data/taiwan_groups_monthly.tsv, with that folder's check strings for the cells used
        the core's table of trade figures      tables/trade_derived_figures.tsv (our sums must equal its values, or the script stops)
        the saved coverage spreadsheet         cn-o34-gacc-coverage-imports-2024-xls (strings read from the binary file)
        the saved Hong Kong release tables     cn-o42-hk-trade-release-202609-tables
        the saved classification circular      cn-o42-hk-tid-circular-2026-51
Writes  idea34_customs/china_customs_imports.tsv, china_imports_by_origin_202609.tsv, us_exports_monthly.tsv,
        us_exports_summary.tsv, coverage_codes.tsv, classification_decisions_2025.tsv, singapore_line_84718010.tsv,
        derived_figures.tsv, numbers_check.tsv
        idea42_hongkong/hk_trade_monthly.tsv, hk_trade_summary.tsv, hk_release_divisions_202609.tsv, hk_divisions_monthly.tsv,
        derived_figures.tsv, numbers_check.tsv
Each numbers_check.tsv holds, for every figure in the tables, the exact piece of the saved copy it was read from
(saved id <TAB> words). The script then runs scripts/cn_has.py on both files and stops with exit 1 if either fails.
Sums and differences are marked "ours" in the tables: they are this script's arithmetic, not a source's figure.
"""
import hashlib, html, json, re, subprocess, sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
P = ROOT / 'research' / 'primary'
PROJ = ROOT / 'research' / 'cn_chip_policy_20261120'
L18 = PROJ / 'loose_ends' / 'L18_trade_data'          # another builder's folder: read only
O34, O42 = HERE / 'idea34_customs', HERE / 'idea42_hongkong'
MONTHS = [f'{y}{m:02d}' for y in (2025, 2026) for m in range(1, 13) if not (y == 2026 and m > 8)]
HEAD = {'847150': '8471.50 processing units', '847180': '8471.80 other units of computers',
        '847330': '8473.30 parts and accessories of computers', '854231': '8542.31 processors and controllers (chips)'}
PARTNER = {0: 'World', 156: 'Mainland China', 344: 'Hong Kong', 446: 'Macau', 490: 'Other Asia, not elsewhere specified (code 490)', 842: 'United States',
           410: 'South Korea', 702: 'Singapore', 458: 'Malaysia'}
THREE = ('847150', '847180', '847330')          # the headings the US proclamation of Jan 14, 2026 names
check34, check42 = [], []


def plain(sid):
    t = (P / sid / 'body.html').read_text(encoding='utf-8', errors='replace')
    return t, re.sub(r'\s+', ' ', html.unescape(re.sub(r'(?s)<[^>]+>', ' ', re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', t))))


def write(path, header, rows):
    path.write_text('\n'.join(['\t'.join(header)] + ['\t'.join(str(c) for c in r) for r in rows]) + '\n', encoding='utf-8')
    print(f'wrote {path.relative_to(HERE)}: {len(rows)} rows')


# ---------- A. China customs, table 14 (major import commodities), five issues ----------
ISSUES = [('202509', 'cn-le18-gacc-t14-202509'), ('202512', 'cn-o34-gacc-t14-imports-202512'), ('202603', 'cn-o34-gacc-t14-imports-202603'),
          ('202606', 'cn-o34-gacc-t14-imports-202606'), ('202609', 'cn-o34-gacc-t14-imports-202609')]
LINES = [('Automatic data processing machines and parts thereof', 'whole of 8471, 8473.30 and three monitor headings'),
         ('Automatic data processing machines', '8471.30 to 8471.49'),
         ('Central processing units', '8471.50'),
         ('Storage units', '8471.70'),
         ('Parts and accessories of automatic data processing machines', '8473.30'),
         ('Electronic integrated circuits', '8542.3 (all integrated circuits: processors, memories, amplifiers, others)')]
NUM = r'(-?[\d,]+(?:\.\d+)?|-)'
gacc = {}
for per, sid in ISSUES:
    _, p = plain(sid)
    m = re.search(r'（14）Major Import Commodities in Quantity and Value,(\d+)\.(\d{4}) (\d{4}/\d+/\d+)', p)
    assert m and f'{m.group(2)}{int(m.group(1)):02d}' == per, (sid, m and m.group(0))
    check34.append((sid, m.group(0)))
    assert 'Unit:US$1,000' in p
    for name, codes in LINES:
        mm = re.search(re.escape(name) + r' (\S+) ' + ' '.join([NUM] * 6) + r'(?= [A-Z])', p)
        assert mm, (sid, name)
        unit, mq, mv, cq, cv, pq, pv = mm.groups()
        gacc[(per, name)] = dict(unit=unit, mq=mq, mv=int(mv.replace(',', '')), cq=cq, cv=int(cv.replace(',', '')), pq=pq, pv=pv, sid=sid, codes=codes)
        check34.append((sid, mm.group(0)))
rows = []
for name, codes in LINES:
    for per, _sid in ISSUES:
        g = gacc[(per, name)]
        cum = 'January to ' + {'12': 'December', '03': 'March', '06': 'June', '09': 'September'}[per[4:]] + ' ' + per[:4]
        rows.append([name, codes, per, g['mv'], cum, g['cv'], g['pv'], g['unit'], g['mq'], g['cq'], g['pq'], 'source', g['sid']])
    q1, h1, m9 = (gacc[(x, name)]['cv'] for x in ('202603', '202606', '202609'))
    y25 = gacc[('202512', name)]['cv']
    for lab, val in (('2026 first quarter (January to March)', q1), ('2026 second quarter (ours: January-June minus January-March)', h1 - q1),
                     ('2026 third quarter (ours: January-September minus January-June)', m9 - h1),
                     ('2025 monthly average (ours: January-December 2025 divided by 12)', round(y25 / 12))):
        rows.append([name, codes, '', '', lab, val, '', '', '', '', '', 'ours', ''])
write(O34 / 'china_customs_imports.tsv',
      ['line_in_the_customs_table', 'tariff_headings_per_2024_coverage_spreadsheet', 'issue_month', 'month_value_usd_thousand', 'period', 'period_value_usd_thousand',
       'pct_change_column_value (as printed; it fits the MONTH against the same month a year earlier, not the period)', 'quantity_unit', 'month_quantity', 'period_quantity', 'pct_change_column_quantity (as printed)', 'kind', 'saved_id'], rows)

# ---------- B. China customs, table 16 (imports by origin and two-digit chapter), September 2026 ----------
sid = 'cn-o34-gacc-t16-imports-bycountry-202609'
t, p = plain(sid)
m = re.search(r'（16）Imports by Selected Countries \(Regions\) and by HS Divisions,9\.2026 2026/\d+/\d+', p); assert m
check34.append((sid, m.group(0)))
cells = lambda r: [re.sub(r'\s+', ' ', html.unescape(re.sub(r'(?s)<[^>]+>', ' ', c))).strip() for c in re.findall(r'(?is)<t[dh][^>]*>(.*?)</t[dh]>', r)]
trs = [cells(r) for r in re.findall(r'(?is)<tr[^>]*>(.*?)</tr>', t)]
hdr = next(c for c in trs if c and c[0] == 'Sec. & Div.')
countries = hdr[1:]
rows = []
for c in trs:
    if c and c[0] in ('TOTAL', '84', '85') and len(c) == 1 + 2 * len(countries):
        for want in ('Hong Kong，China', 'Taiwan，China', 'United States', 'Republic of Korea', 'Japan'):
            k = countries.index(want)
            rows.append([c[0], want.replace('，', ', '), c[1 + 2 * k].replace(',', ''), c[2 + 2 * k].replace(',', ''), sid])
            check34.append((sid, f'{c[1 + 2 * k]} {c[2 + 2 * k]}'))
write(O34 / 'china_imports_by_origin_202609.tsv', ['chapter (84 machinery incl. computers; 85 electrical incl. chips)', 'origin', 'september_2026_usd_thousand', 'january_to_september_2026_usd_thousand', 'saved_id'], rows)

# ---------- C. coverage spreadsheet (binary .xls): which headings each table line covers ----------
sid = 'cn-o34-gacc-coverage-imports-2024-xls'
raw = (P / sid / 'body.bin').read_bytes().decode('latin-1')
rows = []
for name, _ in LINES:
    mm = re.search(re.escape(name) + r'[^\x20-\x7e]{1,6}([0-9][0-9,\-]{3,60})', raw)
    rows.append([name, mm.group(1) if mm else 'not read', sid])
write(O34 / 'coverage_codes.tsv', ['line_in_the_customs_table', 'tariff_codes_as_written_in_the_spreadsheet (first digits of the heading; read from the binary file, not checkable by cn_has)', 'saved_id'], rows)

# ---------- D. the 2025 classification decisions (as reproduced by Hong Kong's trade department) ----------
sid = 'cn-o42-hk-tid-circular-2026-51'
txt = (P / sid / 'text.txt').read_text(encoding='utf-8', errors='replace')
dec = re.findall(r'(Z2025-\d{4})\s+(\d{4}\.\d{4})', txt)
rows = [[a, b, 'yes' if b[:4] in ('8471', '8473', '8542') else 'no', sid] for a, b in dec]
for a, b in dec: check34.append((sid, f'{a} {b}'))
write(O34 / 'classification_decisions_2025.tsv', ['decision_number', 'tariff_number', 'in_8471_8473_or_8542', 'saved_id'], rows)
n_dec, n_hit = len(dec), sum(1 for r in rows if r[2] == 'yes')

# ---------- E. UN Comtrade monthly answers: the United States and Hong Kong as reporters ----------
ORDER = None
def frag(rec):
    """The exact run of the saved answer from "reporterCode" to "primaryValue" for one record (as fetch.py wrote it into text.txt)."""
    s = json.dumps(rec, ensure_ascii=False, indent=1)
    a, b = s.index('"reporterCode"'), s.index('"primaryValue"')
    return re.sub(r'\s+', ' ', s[a:s.index('\n', b)]).rstrip(',')

data, china_rows = {}, 0
for per in MONTHS:
    sid = f'cn-o34-comtrade-m-{per}'
    j = json.loads((P / sid / 'body.json').read_text(encoding='utf-8'))
    for r in j['data']:
        assert r['period'] == per and r['partner2Code'] == 0 and r['motCode'] == 0 and r['customsCode'] == 'C00'
        if r['reporterCode'] == 156: china_rows += 1
        key = (r['reporterCode'], per, r['flowCode'], r['partnerCode'], r['cmdCode'])
        assert key not in data, key
        data[key] = (r['primaryValue'], sid, frag(r))
val = lambda *k: data[k][0] if k in data else None
def use(chk, *k):
    if k in data: chk.append((data[k][1], data[k][2]))
    return val(*k)
mil = lambda v: '' if v is None else f'{v / 1e6:.1f}'

rows, summ, RAW = [], [], {}     # RAW (round 9 of the outputs, Nov 25, 2026): each month's sums in dollars, before rounding; every sum of months is taken from these
for per in MONTHS:
    tot3 = {'X': 0.0, 'RX': 0.0}
    for cmd in ('847150', '847180', '847330', '854231'):
        for pc in (156, 344, 446):
            x, rx = use(check34, 842, per, 'X', pc, cmd), use(check34, 842, per, 'RX', pc, cmd)
            rows.append([per, HEAD[cmd], PARTNER[pc], mil(x), mil(rx), f'cn-o34-comtrade-m-{per}'])
            if cmd in THREE:
                tot3['X'] += x or 0; tot3['RX'] += rx or 0
    chip = sum(val(842, per, 'X', pc, '854231') or 0 for pc in (156, 344, 446))
    chip_rx = sum(val(842, per, 'RX', pc, '854231') or 0 for pc in (156, 344, 446))
    hk3 = sum(val(842, per, 'X', 344, c) or 0 for c in THREE)
    summ.append([per, mil(tot3['X']), mil(tot3['RX']), mil(hk3), mil(chip), mil(chip_rx)])
    RAW[('us', per)] = [None, tot3['X'], tot3['RX'], hk3, chip, chip_rx]
write(O34 / 'us_exports_monthly.tsv', ['month', 'heading', 'destination', 'exports_usd_million', 'of_which_re_exports_usd_million (goods of foreign origin)', 'saved_id'], rows)
# round 9 of the outputs: a sum of months was the sum of month values already rounded to 0.1 million (1688.6 for 1,688,747,607 dollars: atlas lead fa97:1,
# FIXFIG_fg9_FOR_MAIN.txt); it is now the sum of the dollar values, rounded once, as the core's tables/trade_annual_summary.tsv sums them
tot = lambda rs, i, kind='us': mil(sum(RAW[(kind, r[0])][i] for r in rs))
s25, s26 = [r for r in summ if r[0] < '202601'], [r for r in summ if r[0] >= '202601']
summ.append(['2025 January to December (ours: sum)'] + [tot(s25, i) for i in range(1, 6)])
summ.append(['2026 January to August (ours: sum)'] + [tot(s26, i) for i in range(1, 6)])
write(O34 / 'us_exports_summary.tsv',
      ['month', 'three_named_headings_to_mainland_hong_kong_macau_usd_million (ours: sum of 8471.50, 8471.80, 8473.30)', 'of_which_re_exports_usd_million (ours: sum)',
       'three_named_headings_to_hong_kong_alone_usd_million (ours: sum)', 'chips_8542.31_to_mainland_hong_kong_macau_usd_million (ours: sum)', 'of_which_re_exports_usd_million (ours: sum) '], summ)

rows, hsum = [], []
HKM = [m for m in MONTHS if (344, m, 'M', 0, '847330') in data]
for per in HKM:
    for cmd in ('847150', '847180', '847330', '854231'):
        v = [use(check42, 344, per, 'M', pc, cmd) for pc in (0, 842, 490, 156, 410)] + [use(check42, 344, per, 'X', pc, cmd) for pc in (0, 156)]
        rows.append([per, HEAD[cmd]] + [mil(x) for x in v] + [f'cn-o34-comtrade-m-{per}'])
    us3 = sum(val(344, per, 'M', 842, c) or 0 for c in THREE)
    tw3 = sum(val(344, per, 'M', 490, c) or 0 for c in THREE)
    w3 = sum(val(344, per, 'M', 0, c) or 0 for c in THREE)
    x3 = sum(val(344, per, 'X', 0, c) or 0 for c in THREE)
    hsum.append([per, mil(us3), mil(tw3), mil(w3), mil(x3), mil(w3 - x3), mil(val(344, per, 'M', 0, '854231')), mil(val(344, per, 'X', 0, '854231')),
                 mil((val(344, per, 'M', 0, '854231') or 0) - (val(344, per, 'X', 0, '854231') or 0))])
    RAW[('hk', per)] = [None, us3, tw3, w3, x3, w3 - x3, val(344, per, 'M', 0, '854231') or 0, val(344, per, 'X', 0, '854231') or 0,
                        (val(344, per, 'M', 0, '854231') or 0) - (val(344, per, 'X', 0, '854231') or 0)]
write(O42 / 'hk_trade_monthly.tsv', ['month', 'heading', 'imports_all_origins_usd_million', 'imports_origin_united_states', 'imports_origin_other_asia_nes_code_490 (often read as Taiwan; it is not the same as Taiwan\'s own exports to Hong Kong: see the note)',
                                     'imports_origin_mainland_china', 'imports_origin_south_korea', 'total_exports_all_destinations_usd_million', 'total_exports_to_mainland_china', 'saved_id'], rows)
h25, h26 = [r for r in hsum if r[0] < '202601'], [r for r in hsum if r[0] >= '202601']
hsum.append(['2025 January to December (ours: sum)'] + [tot(h25, i, 'hk') for i in range(1, 9)])
hsum.append([f'2026 January to {HKM[-1][4:]} (ours: sum)'] + [tot(h26, i, 'hk') for i in range(1, 9)])
write(O42 / 'hk_trade_summary.tsv',
      ['month', 'three_named_headings_imports_origin_united_states_usd_million (ours: sum of 8471.50, 8471.80, 8473.30)', 'three_named_headings_imports_origin_other_asia_nes_code_490 (ours: sum)',
       'three_named_headings_imports_all_origins (ours: sum)', 'three_named_headings_total_exports (ours: sum)', 'imports_minus_exports_three_headings (ours)',
       'chips_8542.31_imports_all_origins', 'chips_8542.31_total_exports', 'chips_imports_minus_exports (ours)'], hsum)
# round 9 of the outputs (Nov 25, 2026): Hong Kong's sums here must equal the core's tables/trade_annual_summary.tsv (the same UN Comtrade answers, summed by year
# there); the core holds no series with the United States as reporter, so the US sums above are not compared with it
ANN = {}
for ln in (PROJ / 'tables' / 'trade_annual_summary.tsv').read_text(encoding='utf-8').splitlines():
    c = ln.split('\t')
    if len(c) == 7 and c[2] == 'US dollars' and c[3].isdigit(): ANN[(c[0], c[1], c[3])] = (int(c[4]), float(c[5]))
n_ann = 0
for yr, ms in (('2025', h25), ('2026', h26)):
    for col, series, cmds in ((1, 'Comtrade Hong Kong M partner USA', THREE), (2, 'Comtrade Hong Kong M partner Other Asia, nes', THREE), (3, 'Comtrade Hong Kong M partner World', THREE),
                              (4, 'Comtrade Hong Kong X partner World', THREE), (6, 'Comtrade Hong Kong M partner World', ('854231',)), (7, 'Comtrade Hong Kong X partner World', ('854231',))):
        held = {ANN[(series, f'HS {c}', yr)][0] for c in cmds}
        assert held == {len(ms)}, (series, yr, held, len(ms))
        core_sum = sum(ANN[(series, f'HS {c}', yr)][1] for c in cmds); ours = sum(RAW[('hk', r[0])][col] for r in ms)
        assert abs(core_sum - ours) < 1, (series, yr, core_sum, ours); n_ann += 1
assert ANN[('Comtrade Hong Kong M partner USA', 'HS 847330', '2026')][1] != ANN[('Comtrade Hong Kong M partner USA', 'HS 847330', '2025')][1]      # control: the lookup tells two cells apart

# ---------- F. Hong Kong government release for September 2026: two commodity divisions ----------
sid = 'cn-o42-hk-trade-release-202609-tables'
txt = (P / sid / 'text.txt').read_text(encoding='utf-8', errors='replace')
rows = []
for tab, flow in (('Table 6 : Value of Total Exports of 10 Principal Commodity Divisions', 'total exports'), ('Table 7 : Value of Imports of 10 Principal Commodity Divisions', 'imports')):
    seg = txt[txt.index(tab):]
    for name in ('Office machines and automatic data processing machines', 'Electrical machinery, apparatus and appliances, and electrical'):
        mm = re.search(re.escape(name) + r'\s+([\d,]+)\s+([+-][\d.]+)\s+([\d,]+)\s+([+-][\d.]+)', seg); assert mm, (tab, name)
        rows.append([flow, name + (' parts thereof' if name.endswith('electrical') else ''), mm.group(1).replace(',', ''), mm.group(2), mm.group(3).replace(',', ''), mm.group(4), sid])
        check42.append((sid, re.sub(r'\s+', ' ', mm.group(0))))
write(O42 / 'hk_release_divisions_202609.tsv', ['flow', 'commodity_division', 'september_2026_hkd_million', 'pct_change_on_september_2025', 'january_to_september_2026_hkd_million', 'pct_change_on_january_to_september_2025', 'saved_id'], rows)

# ---------- G. which months China has given UN Comtrade ----------
sid = 'cn-o34-comtrade-da-china-monthly'
da = [r for r in json.loads((P / sid / 'body.json').read_text(encoding='utf-8'))['data'] if r['reporterCode'] == 156 and r['freqCode'] == 'M']
china_first, china_last = min(r['period'] for r in da), max(r['period'] for r in da)
check34.append((sid, f'"period": {china_last}, "reporterCode": 156'))

# ---------- H. the arithmetic the two notes use (all "ours") ----------
PRICE = 27000            # "priced at around $27,000 each": a press report citing unnamed people (saved id cn-acts-reuters-customs-20260114; round 4: the Yahoo copy the figure now uses)
f = float
# Nvidia's own figures, on the record. Read from the saved copies, not typed (round 2).
def saved_text(sid): return re.sub(r'\s+', ' ', (P / sid / 'text.txt').read_text(encoding='utf-8', errors='replace'))
NV = [('cn-acts-reuters-customs-20260114', r'priced at around \$(27,000) each'),
      ('man-ms-sec-10q-2026-07', r'Data Center revenue was \$([\d.]+) billion'),
      ('man-ms-sec-10q-2026-07', r'Shipments of Data Center Hopper products to China during the second quarter of .scal year 2027 were less than (1)% of Data Center revenue'),
      ('cn-o38-nvda-q3fy27-call-transcript-pdf', r'Q3 sales of licensed Hopper Data Center products to China was \$([\d.]+) billion'),
      ('cn-counter-b17-1', r'Shipments of Data Center Hopper products to China during the quarter were \$([\d.]+) billion')]
nv = []
for sid, rx in NV:
    mm = re.search(rx, saved_text(sid)); assert mm, (sid, rx)
    nv.append(mm.group(1)); check34.append((sid, mm.group(0))); check42.append((sid, mm.group(0)))
assert int(nv[0].replace(',', '')) == PRICE and nv[2] == '1' and nv[3] == nv[4]
NV_Q2_DC, NV_Q3_CN = f(nv[1]) * 1e9, f(nv[3]) * 1e9          # 89.0 billion (quarter to Jul 26, 2026); 2.4 billion (quarter to Oct 25, 2026)
NV_Q2_CAP = NV_Q2_DC / 100                                    # "less than 1%" of it
Q3_FIRST, Q3_LAST, DATA_LAST = date(2026, 7, 27), date(2026, 10, 25), date(2026, 8, 31)   # the quarter before ended Jul 26, 2026 (the 10-Q); the US figures end with August
us = {r[0]: r for r in summ}
y25, y26 = us['2025 January to December (ours: sum)'], us['2026 January to August (ours: sum)']
mx = max(summ[:len(MONTHS)], key=lambda r: f(r[1]))
parts = lambda per: gacc[(per, 'Parts and accessories of automatic data processing machines')]
ics = lambda per: gacc[(per, 'Electronic integrated circuits')]
q3_parts = parts('202609')['cv'] - parts('202606')['cv']
d34 = [['price of one H200 used below, US dollars', PRICE, 'a press report citing unnamed people; not an official figure'],
       ['600,000 chips at that price, billion US dollars', f'{600000 * PRICE / 1e9:.1f}', '600,000 x 27,000'],
       ['10,000 chips at that price, million US dollars', f'{10000 * PRICE / 1e6:.0f}', '10,000 x 27,000'],
       ['chips that 2.4 billion US dollars buys at that price', f'{NV_Q3_CN / PRICE:,.0f}', '2,400,000,000 / 27,000'],
       ['US exports, three named headings, to mainland China, Hong Kong and Macau: 2025, million US dollars', y25[1], 'sum of 12 months'],
       ['the same: average month of 2025', f'{f(y25[1]) / 12:.0f}', 'sum / 12'],
       ['the same: January to August 2026', y26[1], 'sum of 8 months'],
       ['the same: average month of January to August 2026', f'{f(y26[1]) / 8:.0f}', 'sum / 8'],
       ['the same: highest month in the 20 months', f'{mx[1]} ({mx[0]})', 'maximum'],
       ['the same: August 2026', us['202608'][1], 'one month'],
       ['January to August 2026 total as a number of chips at that price', f'{f(y26[1]) * 1e6 / PRICE:,.0f}', 'total / 27,000; a ceiling, since the headings hold many other goods'],
       ['16.2 billion divided by the January to August 2026 total', f'{600000 * PRICE / (f(y26[1]) * 1e6):.1f}', 'ratio'],
       ['price at which the January to August 2026 total would hold 600,000 chips, US dollars a chip', f'{f(y26[1]) * 1e6 / 600000:,.0f}', 'total / 600,000'],
       ['that price as a share of the press price, per cent', f'{f(y26[1]) * 1e6 / 600000 / PRICE * 100:.0f}', 'ratio'],
       ['Nvidia, quarter to Jul 26, 2026: Data Center revenue, billion US dollars', f'{NV_Q2_DC / 1e9:.1f}', 'read from its quarterly report'],
       ['Nvidia, quarter to Jul 26, 2026: 1% of Data Center revenue (its Hopper shipments to China were less than this), billion US dollars', f'{NV_Q2_CAP / 1e9:.2f}', '89.0 billion x 1%'],
       ['that bound as a number of chips at the press price', f'{NV_Q2_CAP / PRICE:,.0f}', 'bound / 27,000'],
       ['Nvidia, quarter to Oct 25, 2026: sales of licensed Hopper products to China, billion US dollars', f'{NV_Q3_CN / 1e9:.1f}', 'read from its results call and its commentary'],
       ['days in that quarter (Jul 27 to Oct 25, 2026)', (Q3_LAST - Q3_FIRST).days + 1, 'count of days'],
       ['of which inside the months the US export figures cover (to Aug 31, 2026)', (DATA_LAST - Q3_FIRST).days + 1, 'count of days'],
       ['US exports, three named headings, to the three places, July plus August 2026, million US dollars', f'{(RAW[("us", "202607")][1] + RAW[("us", "202608")][1]) / 1e6:.1f}', 'sum of the two months in us_exports_summary.tsv (of the dollar values)'],
       ['that as a share of 2.4 billion, per cent', f'{(RAW[("us", "202607")][1] + RAW[("us", "202608")][1]) / NV_Q3_CN * 100:.0f}', 'ratio; customs value against sales, so rough'],
       ['US exports under all four headings to the three places, January to August 2026, million US dollars', f'{f(y26[1]) + f(y26[4]):.1f}', 'three named headings plus 8542.31'],
       ['that four-heading total as a number of chips at that price', f'{(f(y26[1]) + f(y26[4])) * 1e6 / PRICE:,.0f}', 'total / 27,000; an outer bound, since the chip heading holds every processor sent from the United States'],
       ['US exports of chips (8542.31) to the three places, January to August 2026, million US dollars', y26[4], 'sum of 8 months'],
       ['of which re-exports (goods of foreign origin)', y26[5], 'sum of 8 months'],
       ['China customs: parts and accessories of computers (8473.30), 2025, billion US dollars', f'{parts("202512")["cv"] / 1e6:.1f}', 'table 14, December 2025 issue'],
       ['the same: January to September 2026', f'{parts("202609")["cv"] / 1e6:.1f}', 'table 14, September 2026 issue'],
       ['the same: September 2026 alone', f'{parts("202609")["mv"] / 1e6:.1f}', 'table 14, September 2026 issue'],
       ['the same: third quarter of 2026', f'{q3_parts / 1e6:.1f}', 'January-September minus January-June'],
       ['the same: average month of 2025', f'{parts("202512")["cv"] / 12 / 1e6:.2f}', 'January-December 2025 divided by 12'],
       ['the same: average month of January to September 2026', f'{parts("202609")["cv"] / 9 / 1e6:.2f}', 'January-September 2026 divided by 9'],
       ['the same: January to September 2026 divided by all of 2025', f'{parts("202609")["cv"] / parts("202512")["cv"]:.1f}', 'ratio'],
       ['the same: September 2026 divided by the average month of 2025', f'{parts("202609")["mv"] / (parts("202512")["cv"] / 12):.1f}', 'ratio'],
       ['the same: December 2025 alone', f'{parts("202512")["mv"] / 1e6:.1f}', 'table 14, December 2025 issue'],
       ['270 million as a share of that third quarter, per cent', f'{270e6 / (q3_parts * 1e3) * 100:.1f}', 'ratio'],
       ['China customs: integrated circuits, September 2026, billion US dollars', f'{ics("202609")["mv"] / 1e6:.1f}', 'table 14, September 2026 issue'],
       ['the same: January to September 2026', f'{ics("202609")["cv"] / 1e6:.1f}', 'table 14, September 2026 issue'],
       ['270 million as a share of September 2026 integrated-circuit imports, per cent', f'{270e6 / (ics("202609")["mv"] * 1e3) * 100:.2f}', 'ratio'],
       ['China customs: processing units (8471.50), January to September 2026, billion US dollars', f'{gacc[("202609", "Central processing units")]["cv"] / 1e6:.1f}', 'table 14, September 2026 issue']]
# ---------- I. round 4: what the core's trade table and L18's files add (read only) ----------
core = {}
for ln in (PROJ / 'tables' / 'trade_derived_figures.tsv').read_text(encoding='utf-8').splitlines():
    if ln.startswith('#') or not ln.strip(): continue
    c = ln.split('\t')
    if len(c) == 3: core[c[0].strip()] = c[2].strip()
def same_as_core(label, ours):
    assert label in core, label
    assert abs(float(core[label]) - ours) < 0.51, (label, core[label], ours)

# I.1 China customs, the parts line: the nine months of 2026 against the same nine months of 2025 (both as printed)
p25, p26 = parts('202509'), parts('202609')
tonnes = lambda g, k: f(g[k].replace(',', ''))
assert core['China customs table 14, Parts and accessories of automatic data processing machines: Jan-Sep 2025 and Jan-Sep 2026 as printed (Sep issues): value; quantity (T)'].startswith(f'{p25["cv"]} -> {p26["cv"]} (x4.35)')
ratio = lambda name: gacc[('202609', name)]['cv'] / gacc[('202509', name)]['cv']
d34 += [['China customs: parts and accessories of computers (8473.30), January to September 2025, billion US dollars', f'{p25["cv"] / 1e6:.1f}', 'table 14, September 2025 issue (saved by L18)'],
        ['the same: January to September 2026 divided by January to September 2025', f'{p26["cv"] / p25["cv"]:.2f}', 'ratio of the two printed nine-month values'],
        ['the same: weight, January to September 2025, then 2026, tonnes', f'{tonnes(p25, "cq"):,.0f} then {tonnes(p26, "cq"):,.0f}', 'as printed (unit T)'],
        ['the same: value per tonne, January to September 2025, then 2026, thousand US dollars', f'{p25["cv"] / tonnes(p25, "cq"):,.0f} then {p26["cv"] / tonnes(p26, "cq"):,.0f}', 'value / weight'],
        ['the same: September 2026 against September 2025, month values, per cent change', f'{(p26["mv"] / p25["mv"] - 1) * 100:.1f}', f'ours; the September 2026 issue prints {p26["pv"]} in its percentage column'],
        ['the same: January to September 2026 against January to September 2025, per cent change', f'{(p26["cv"] / p25["cv"] - 1) * 100:.1f}', 'ours; so the printed column is the month, not the period'],
        ['the same: September 2026 against September 2025, weight, per cent change', f'{(tonnes(p26, "mq") / tonnes(p25, "mq") - 1) * 100:.1f}', f'ours; the September 2026 issue prints {p26["pq"]}'],
        ['China customs: integrated circuits, January to September 2025, billion US dollars', f'{ics("202509")["cv"] / 1e6:.1f}', 'table 14, September 2025 issue'],
        ['China customs: processing units (8471.50), January to September 2025, billion US dollars', f'{gacc[("202509", "Central processing units")]["cv"] / 1e6:.1f}', 'table 14, September 2025 issue'],
        ['January to September 2026 divided by January to September 2025: integrated circuits; processing units; storage units', f'{ratio("Electronic integrated circuits"):.2f}; {ratio("Central processing units"):.2f}; {ratio("Storage units"):.2f}', 'ratios of printed nine-month values']]

# I.2 Singapore, line 84718010: the raw answers of its statistics service, as L18 kept them
SG = L18 / 'raw_singstat'
man = {c[0]: c for c in (ln.split('\t') for ln in (SG / 'MANIFEST.tsv').read_text(encoding='utf-8').splitlines() if ln.strip() and not ln.startswith('#'))}
sg_files = {}
def sg_data(fn):
    raw = (SG / fn).read_bytes()
    assert man[fn][2] == '200' and hashlib.sha256(raw).hexdigest() == man[fn][3], f'{fn}: does not match its manifest line'
    sg_files[fn] = man[fn][5]
    D = json.loads(raw)['Data']; assert not D.get('isMore'), fn
    return D
MON = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
def sg_per(x): y, m = x.split(); return f'{y}{MON[m]:02d}'
def sg_put(d, key, v, fn):
    if key in d: assert d[key] == v, (fn, key, d[key], v)      # the service repeats a few rows; a repeat with another value stops the script
    d[key] = v
sgv, sgq, sg_names, sg_repeats = {}, {}, {}, 0
for y in (2025, 2026):
    D = sg_data(f'847180_{y}_p0.json'); assert D['id'] == 'T010001' and D['unitMeasurement'] == 'Thousand Dollars'
    for r in D['rows']:
        if r['hs8Products']:
            k = (sg_per(r['period']), r['tradeType'], r['market'], r['hs8Products'][:8]); sg_repeats += k in sgv
            sg_put(sgv, k, f(r['value']), D['id']); sg_names[r['hs8Products'][:8]] = r['hs8Products']
    D = sg_data(f'T010002_847180_{y}_p0.json'); assert D['id'] == 'T010002'
    for r in D['rows']: sg_put(sgq, (sg_per(r['period']), r['tradeType'], r['market'], r['hs8Products'][:8]), f(r['quantity']), D['id'])
ogv, ogq = {}, {}
for r in sg_data('origins_T010001_847180_2025_2026.json')['rows']:
    if r['hs8Products']: sg_put(ogv, (sg_per(r['period']), r['market'], r['hs8Products'][:8]), f(r['value']), 'origins value')
for r in sg_data('origins_T010002_847180_2025_2026.json')['rows']: sg_put(ogq, (sg_per(r['period']), r['market'], r['hs8Products'][:8]), f(r['quantity']), 'origins quantity')
rate = {sg_per(c['key']): f(c['value']) for r in sg_data('M700051_2026_Jun_Oct.json')['row'] if r['rowText'] == 'US Dollar' and r['uoM'] == 'Singapore Dollar Per US Dollar' for c in r['columns']}
LINE = '84718010'
assert sg_names[LINE] == '84718010 - CONTROL & ADAPTOR UNITS OF AUTOMATIC DATA PROCESSING MACHINES (NMB)'
check34.append(('cn-le18-sg-T010001-metadata', sg_names[LINE])); check34.append(('cn-le18-sg-T010001-metadata', sg_names['84718070']))
check34.append(('cn-le18-sg-T010001-metadata', 'Merchandise Trade Value by Commodity and Market, Monthly'))
SGM = [f'{y}{m:02d}' for y in (2025, 2026) for m in range(1, 13) if not (y == 2026 and m > 10)]
H1, H2 = [m for m in SGM if '202601' <= m <= '202606'], [m for m in SGM if '202607' <= m <= '202610']
sgs = lambda d, tt, mk, months, line=LINE: sum(d.get((m, tt, mk, line), 0.0) for m in months)
ogs = lambda d, mk, months: sum(d.get((m, mk, LINE), 0.0) for m in months)
sg_rows = [[m] + [f'{d.get((m, tt, mk, LINE), 0.0):.0f}' for tt, mk in (('RE-EXPORTS', 'MAINLAND CHINA'), ('RE-EXPORTS', 'HONG KONG'), ('RE-EXPORTS', 'WORLD'), ('IMPORTS', 'WORLD')) for d in (sgv, sgq)]
        + [f'847180_{m[:4]}_p0.json and T010002_847180_{m[:4]}_p0.json'] for m in SGM]
write(O34 / 'singapore_line_84718010.tsv',
      ['month', 're_exports_to_mainland_china_sgd_thousand', 'units', 're_exports_to_hong_kong_sgd_thousand', 'units ', 're_exports_to_the_world_sgd_thousand', 'units  ',
       'imports_from_the_world_sgd_thousand', 'units   ', 'raw files in loose_ends/L18_trade_data/raw_singstat (sha256 in MANIFEST.tsv there; not in research/primary)'], sg_rows)
cn1, cn2, cn25 = sgs(sgv, 'RE-EXPORTS', 'MAINLAND CHINA', H1), sgs(sgv, 'RE-EXPORTS', 'MAINLAND CHINA', H2), sgs(sgv, 'RE-EXPORTS', 'MAINLAND CHINA', [m for m in SGM if m < '202601'])
u1, u2 = sgs(sgq, 'RE-EXPORTS', 'MAINLAND CHINA', H1), sgs(sgq, 'RE-EXPORTS', 'MAINLAND CHINA', H2)
hk1, hk2, hku2 = sgs(sgv, 'RE-EXPORTS', 'HONG KONG', H1), sgs(sgv, 'RE-EXPORTS', 'HONG KONG', H2), sgs(sgq, 'RE-EXPORTS', 'HONG KONG', H2)
usd2 = sum(sgv[(m, 'RE-EXPORTS', 'MAINLAND CHINA', LINE)] / rate[m] for m in H2)
ja_sgd = sum(sgv[(m, 'RE-EXPORTS', 'MAINLAND CHINA', LINE)] for m in ('202607', '202608'))
ja_usd = sum(sgv[(m, 'RE-EXPORTS', 'MAINLAND CHINA', LINE)] / rate[m] for m in ('202607', '202608'))
same_as_core('Singapore re-exports to MAINLAND CHINA, line 84718010, Jan-Jun 2026', cn1)
same_as_core('Singapore re-exports to MAINLAND CHINA, line 84718010, Jul-Oct 2026', cn2)
same_as_core('Singapore re-exports to MAINLAND CHINA, line 84718010, Jul-Oct 2026, units', u2)
same_as_core('Singapore re-exports to HONG KONG, line 84718010, Jan-Jun 2026', hk1)
same_as_core('Singapore re-exports to HONG KONG, line 84718010, Jul-Oct 2026', hk2)
same_as_core('Singapore re-exports to MAINLAND CHINA, line 84718010, Jul-Oct 2026, in US dollars at Singapore monthly average rates', usd2)
us_sg = {m: use(check34, 842, m, 'X', 702, '847180') for m in MONTHS}
# the United States' exports to Singapore under all three named headings (same reporter, same measure as section E)
us_sg3 = {m: sum(use(check34, 842, m, 'X', 702, c) or 0 for c in THREE) / 1e6 for m in MONTHS}
M26H1 = [m for m in MONTHS if '202601' <= m <= '202606']
M26 = [m for m in MONTHS if m >= '202601']
us_sg3_h1 = sum(us_sg3[m] for m in M26H1) / len(M26H1)
us_sg3_26 = sum(us_sg3[m] for m in M26)
us3_h1 = sum(RAW[('us', m)][1] for m in M26H1) / 1e6 / len(M26H1)      # round 9 of the outputs: of the dollar values
with_sg_chips = (f(y26[1]) + us_sg3_26) * 1e6 / PRICE
us_sg3_plus = f(y26[1]) + us_sg3_26      # round 10 of the outputs: the sum the note now prints before the division
RAWSRC = 'raw answers of Singapore\'s statistics service, kept by L18 with their sha256; not in research/primary'
d34 += [['Singapore, line 84718010 (control and adaptor units): re-exports to mainland China, all of 2025, thousand Singapore dollars', f'{cn25:,.0f}', RAWSRC],
        ['the same: January to June 2026 (units in brackets)', f'{cn1:,.0f} ({u1:,.0f})', RAWSRC],
        ['the same: July to October 2026 (units in brackets)', f'{cn2:,.0f} ({u2:,.0f})', RAWSRC],
        ['the same, month by month, July, August, September, October 2026', '; '.join(f'{sgv[(m, "RE-EXPORTS", "MAINLAND CHINA", LINE)]:,.0f}' for m in H2), RAWSRC],
        ['the same: value per unit, January to June 2026, then July to October 2026, thousand Singapore dollars', f'{cn1 / u1:.2f} then {cn2 / u2:.1f}', 'value / units; the tables do not say what one unit is'],
        ['the same: share of the line\'s re-exports to the whole world that went to mainland China, July to October 2026, per cent', f'{cn2 / sgs(sgv, "RE-EXPORTS", "WORLD", H2) * 100:.0f}', 'ratio'],
        ['Singapore, line 84718010: domestic exports to mainland China, July to October 2026, thousand Singapore dollars', f'{sgs(sgv, "DOMESTIC EXPORTS", "MAINLAND CHINA", H2):,.0f}', RAWSRC],
        ['Singapore, line 84718010: imports by origin, July to October 2026, thousand Singapore dollars (units): Taiwan; Mexico; United States; all origins',
         '; '.join(f'{ogs(ogv, mk, H2):,.0f} ({ogs(ogq, mk, H2):,.0f})' for mk in ('TAIWAN', 'MEXICO', 'UNITED STATES OF AMERICA')) + f'; {sgs(sgv, "IMPORTS", "WORLD", H2):,.0f}', RAWSRC],
        ['Singapore, line 84718070 (sound cards and video cards): re-exports to mainland China, January to June 2026, then July to October 2026, thousand Singapore dollars',
         f'{sgs(sgv, "RE-EXPORTS", "MAINLAND CHINA", H1, "84718070"):,.0f} then {sgs(sgv, "RE-EXPORTS", "MAINLAND CHINA", H2, "84718070"):,.0f}', RAWSRC],
        ['Singapore, line 84718010, re-exports to mainland China, July to October 2026, in US dollars at Singapore\'s own monthly average rates, thousand', f'{usd2:,.0f}', 'each month / its rate (table M700051); a customs value, not sales'],
        ['the same, July plus August 2026: thousand Singapore dollars, then thousand US dollars', f'{ja_sgd:,.0f} then {ja_usd:,.0f}', 'two months'],
        ['US exports to Singapore under 8471.80, July and August 2026, million US dollars (the United States as reporter)', f'{us_sg["202607"] / 1e6:.1f} and {us_sg["202608"] / 1e6:.1f}', 'UN Comtrade, saved'],
        ['the same: lowest and highest month, January 2025 to August 2026', f'{min(us_sg.values()) / 1e6:.1f} and {max(us_sg.values()) / 1e6:.1f}', 'minimum and maximum of 20 months'],
        ['US exports to Singapore under the three named headings, July and August 2026, million US dollars', f'{us_sg3["202607"]:.1f} and {us_sg3["202608"]:.1f}', 'UN Comtrade, saved; every kind of goods'],
        ['the same: average month of January to June 2026', f'{us_sg3_h1:.1f}', 'sum of 6 months / 6'],
        ['the same: all of January to August 2026', f'{us_sg3_26:,.1f}', 'sum of 8 months'],
        ['US exports to mainland China, Hong Kong and Macau under the three named headings: July and August 2026, then the average month of January to June 2026, million US dollars', f'{f(us["202607"][1]):.1f} and {f(us["202608"][1]):.1f}, then {us3_h1:.1f}', 'from us_exports_summary.tsv'],
        ['January to August 2026: US exports under the three headings to the three places plus those to Singapore, million US dollars', f'{us_sg3_plus:,.1f}', f'{f(y26[1]):,.1f} + {us_sg3_26:,.1f}'],
        ['January to August 2026: US exports under the three headings to the three places plus Singapore, as a number of chips at the press price', f'{with_sg_chips:,.0f}', f'({f(y26[1]):,.1f} + the Singapore total) million / 27,000; every kind of goods counted as if an H200'],
        ['Singapore, line 84718010: re-exports to mainland China, average month of January to June 2026, thousand Singapore dollars', f'{cn1 / 6:,.0f}', 'six-month sum / 6'],
        ['Singapore raw files read, each matching its sha256 in the manifest', len(sg_files), f'fetched {min(sg_files.values())} to {max(sg_files.values())} by L18; repeated rows with one value, taken once: {sg_repeats}']]

# I.3 Taiwan's own exports (its finance ministry's groups, as L18 tabled them): computers to mainland China and Hong Kong against the world
tw, twfrag = {}, {}
for ln in (L18 / 'taiwan_groups_monthly.tsv').read_text(encoding='utf-8').splitlines():
    c = ln.split('\t')
    if len(c) == 5 and c[0].isdigit(): tw[(c[0], c[1], c[2])] = f(c[3]); assert c[4] == 'cn-le18-tw-mof-exp-cnhk-groups'
for ln in (L18 / 'numbers_check.tsv').read_text(encoding='utf-8').splitlines():
    c = ln.split('\t')
    if len(c) == 4 and c[0] == 'cn-le18-tw-mof-exp-cnhk-groups': twfrag[(c[2], c[3])] = c[1]
def tw_sum(dest, group, months, chk):
    for m in months: chk.append(('cn-le18-tw-mof-exp-cnhk-groups', twfrag[(m, f'{dest} {group}')]))
    return sum(tw[(m, dest, group)] for m in months)
TW26 = [f'2026{m:02d}' for m in range(1, 11)]
ADP, PARTS_TW = '自動資料處理機及其附屬單元', '電腦之零附件'
tw_share = (tw_sum('中國大陸', ADP, TW26, check34) + tw_sum('香港', ADP, TW26, check34)) / tw_sum('全球', ADP, TW26, check34) * 100
same_as_core('Taiwan exports of ADP machines (all 8471) to mainland China plus Hong Kong as a share of exports to the world, Jan-Oct 2026', round(tw_share, 2))
# round 10 of the outputs: the note says the group holds all of heading 8471. Test it here, every month, against Taiwan's own table by
# six-digit code (L18's taiwan_hs6_monthly.tsv of the saved page cn-le18-tw-mof-exp-hs6-all8471-8542), each cell re-checked in the saved page.
TW6 = 'cn-le18-tw-mof-exp-hs6-all8471-8542'
tw6, tw6frag = {}, {}
for ln in (L18 / 'taiwan_hs6_monthly.tsv').read_text(encoding='utf-8').splitlines():
    c = ln.split('\t')
    if len(c) == 4 and c[0].isdigit() and c[1].startswith('8471'): tw6[(c[0], c[1])] = f(c[2]); assert c[3] == TW6
for ln in (L18 / 'numbers_check.tsv').read_text(encoding='utf-8').splitlines():
    c = ln.split('\t')
    if len(c) == 4 and c[0] == TW6: tw6frag[(c[2], c[3])] = c[1]
TW_ALL = sorted({m for (m, d, g) in tw if d == '全球' and g == ADP})
TW_CODES = sorted({k for (m, k) in tw6})
tw_eq = 0
for m in TW_ALL:
    s = 0.0
    for k in TW_CODES:
        check34.append((TW6, tw6frag[(m, f'world {k}')])); s += tw6[(m, k)]
    check34.append(('cn-le18-tw-mof-exp-cnhk-groups', twfrag[(m, f'全球 {ADP}')]))
    tw_eq += abs(s - tw[(m, '全球', ADP)]) < 0.5
assert len(TW_CODES) == 8 and tw_eq == len(TW_ALL) and TW_ALL[0] == '202301' and TW_ALL[-1] == '202610', (TW_CODES, tw_eq, len(TW_ALL))
assert sum(abs(sum(tw6[(m, k)] for k in TW_CODES if k != '847150') - tw[(m, '全球', ADP)]) < 0.5 for m in TW_ALL) == 0      # control: without one code no month is equal
NUMW = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
hkx25 = sum(use(check34, 344, m, 'X', 156, '847330') for m in HKM if m <= '202507')
hkx26 = sum(use(check34, 344, m, 'X', 156, '847330') for m in HKM if '202601' <= m <= '202607')
same_as_core('Comtrade Hong Kong exports to mainland China, HS 847330, Jan-Jul 2025', hkx25); same_as_core('Comtrade Hong Kong exports to mainland China, HS 847330, Jan-Jul 2026', hkx26)
d34.append(['Hong Kong total exports of computer parts (8473.30) to mainland China, by Hong Kong\'s own figures: January to July 2025, then January to July 2026, billion US dollars', f'{hkx25 / 1e9:.2f} then {hkx26 / 1e9:.2f}', 'sums of 7 months each (UN Comtrade, saved)'])
d34.append(['Taiwan (finance ministry groups): exports of computers, all of heading 8471, to mainland China plus Hong Kong as a share of its exports to the world, January to October 2026, per cent', f'{tw_share:.2f}', 'L18\'s table of the saved ministry page; its 30 cells re-checked here'])
d34.append([f'Taiwan: months from {TW_ALL[0]} to {TW_ALL[-1]} in which the group for computers (exports to the world) equals the sum of the {len(TW_CODES)} six-digit codes that begin 8471, in thousand US dollars', f'{tw_eq} of {len(TW_ALL)}', f'the two saved ministry pages, {len(TW_ALL) * (len(TW_CODES) + 1)} cells re-checked here; control: without 8471.50 no month is equal'])
# round 12 of the outputs (Nov 26, 2026): the highest month of US exports of processor chips (8542.31) to the three places, for the customs note's point 21
MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
CHIP_MAX = max(MONTHS, key=lambda m: RAW[('us', m)][4])
assert RAW[('us', CHIP_MAX)][4] < 1e9 and RAW[('us', CHIP_MAX)][4] == max(RAW[('us', m)][4] for m in MONTHS), 'control: the highest month of chips is under a billion dollars'
d34.append([f'US exports of chips (8542.31) to the three places: the highest month of the {len(MONTHS)}, million US dollars', f'{MONTH_NAMES[int(CHIP_MAX[4:]) - 1]} {CHIP_MAX[:4]}: {RAW[("us", CHIP_MAX)][4] / 1e6:,.1f}', 'largest monthly sum of the three places'])
write(O34 / 'derived_figures.tsv', ['figure', 'value', 'how (all arithmetic is ours)'], d34)
hk = {r[0]: r for r in hsum}
k26 = next(k for k in hk if k.startswith('2026 January to'))
hmx = max(hsum[:len(HKM)], key=lambda r: f(r[1]))
rel = {(r[0], r[1][:6]): r for r in rows}       # rows = the release's division lines (section F)
d42 = [['600,000 chips at 27,000 US dollars each, billion US dollars', f'{600000 * PRICE / 1e9:.1f}', '600,000 x 27,000; the price is a press figure from unnamed people'],
       ['the same in Hong Kong dollars at 7.8 to the US dollar, billion', f'{600000 * PRICE * 7.8 / 1e9:.0f}', 'the 7.8 rate is from general knowledge of the peg, not from a saved page'],
       ['16.2 billion divided by 2.4 billion', f'{600000 * PRICE / NV_Q3_CN:.2f}', 'ratio; 2.4 billion is the licensed sales Nvidia stated for the quarter to Oct 25, 2026'],
       ['Nvidia: 1% of 89.0 billion (quarter to Jul 26, 2026) plus 2.4 billion (quarter to Oct 25, 2026), billion US dollars', f'{(NV_Q2_CAP + NV_Q3_CN) / 1e9:.2f}', 'sum; the first part is an upper bound'],
       ['that sum as a share of 16.2 billion, per cent', f'{(NV_Q2_CAP + NV_Q3_CN) / (600000 * PRICE) * 100:.0f}', 'ratio; depends on the press price'],
       ['2.4 billion as a number of chips at the press price', f'{NV_Q3_CN / PRICE:,.0f}', '2,400,000,000 / 27,000'],
       ['office machines and computers division, September 2026: total exports minus imports, million Hong Kong dollars', int(rel[('total exports', 'Office')][2]) - int(rel[('imports', 'Office')][2]), 'difference, the release tables 6 and 7'],
       ['the same division, average month of January to September 2026: total exports minus imports, million Hong Kong dollars', f'{(int(rel[("total exports", "Office")][4]) - int(rel[("imports", "Office")][4])) / 9:.0f}', 'difference of the nine-month totals, divided by 9'],
       ['Hong Kong imports of US origin, three named headings, 2025, million US dollars', hk['2025 January to December (ours: sum)'][1], 'sum of 12 months'],
       ['the same: January to July 2026', hk[k26][1], 'sum of 7 months'],
       ['the same: highest month in the 19 months', f'{hmx[1]} ({hmx[0]})', 'maximum'],
       ['Hong Kong imports of origin Other Asia, nes (code 490), three named headings, January to July 2026, million US dollars', hk[k26][2], 'sum of 7 months'],
       ['Hong Kong imports, three named headings, all origins, January to July 2026, million US dollars', hk[k26][3], 'sum of 7 months'],
       ['Hong Kong total exports, three named headings, January to July 2026, million US dollars', hk[k26][4], 'sum of 7 months'],
       ['Hong Kong chips (8542.31): imports minus total exports, 2025, million US dollars', hk['2025 January to December (ours: sum)'][8], 'difference of sums'],
       ['the same: January to July 2026', hk[k26][8], 'difference of sums'],
       ['office machines and computers division, imports, September 2026, million Hong Kong dollars', rel[('imports', 'Office')][2], 'the release, table 7'],
       ['the same division, total exports, September 2026, million Hong Kong dollars', rel[('total exports', 'Office')][2], 'the release, table 6'],
       ['the same division, imports, January to September 2026, million Hong Kong dollars', rel[('imports', 'Office')][4], 'the release, table 7'],
       ['the same division, total exports, January to September 2026, million Hong Kong dollars', rel[('total exports', 'Office')][4], 'the release, table 6'],
       ['the same division, imports, average month of January to September 2026, million Hong Kong dollars', f'{int(rel[("imports", "Office")][4]) / 9:.0f}', 'January-September divided by 9'],
       ['months, of the 19, in which total exports exceeded imports under the three named headings', sum(1 for r in hsum[:len(HKM)] if f(r[5]) < 0), 'count'],
       ['smallest and largest monthly excess of exports over imports, three named headings, million US dollars', f'{-max(f(r[5]) for r in hsum[:len(HKM)]):.1f} and {-min(f(r[5]) for r in hsum[:len(HKM)]):.1f}', 'minimum and maximum'],
       ['months, of the 19, in which chip (8542.31) imports exceeded total exports', sum(1 for r in hsum[:len(HKM)] if f(r[8]) > 0), 'count'],
       ['US exports to Hong Kong, three named headings, January to August 2026, million US dollars (US as reporter)', y26[3], 'sum of 8 months']]
# Hong Kong imports under the three named headings by origin: the average month of 2025 against the average month of 2026 so far
def hk3(per, pc): return sum(val(344, per, 'M', pc, c) or 0 for c in THREE)
m25, m26 = [m for m in HKM if m < '202601'], [m for m in HKM if m >= '202601']
AVG = {}      # round 12 of the outputs: the averages, unrounded, for the note's point 7 (checked below)
for lab, pcs in (('all origins', (0,)), ('mainland China origin', (156,)), ('South Korea origin', (410,)), ('origin Other Asia, nes (code 490)', (490,)), ('United States origin', (842,))):
    a = sum(hk3(m, pc) for m in m25 for pc in pcs) / len(m25) / 1e6
    b = sum(hk3(m, pc) for m in m26 for pc in pcs) / len(m26) / 1e6
    d42.append([f'Hong Kong imports, three named headings, {lab}: average month of 2025, then of January to July 2026, million US dollars', f'{a:.0f} then {b:.0f}', f'sums divided by {len(m25)} and by {len(m26)}'])
    AVG[lab] = (a / 1e3, b / 1e3)
xa = sum(sum(val(344, m, 'X', 0, c) or 0 for c in THREE) for m in m25) / len(m25) / 1e6
xb = sum(sum(val(344, m, 'X', 0, c) or 0 for c in THREE) for m in m26) / len(m26) / 1e6
d42.append(['Hong Kong total exports, three named headings: average month of 2025, then of January to July 2026, million US dollars', f'{xa:.0f} then {xb:.0f}', 'sums divided by 12 and by 7'])
tw_mar25 = hk3('202503', 490) / 1e6
d42.append(['Hong Kong imports of origin Other Asia, nes (code 490), three named headings, March 2025 alone, million US dollars', f'{tw_mar25:.1f}', 'one month'])
d42.append(['Hong Kong imports, three named headings, origins United States and Other Asia, nes (code 490) together, February to July 2026, million US dollars', f'{sum(hk3(m, pc) for m in m26 if m >= "202602" for pc in (842, 490)) / 1e6:.1f}', 'sum of 6 months, two origins'])
# ---------- J. round 4, Hong Kong ----------
# J.1 Hong Kong's total exports to mainland China by heading, January to July of each year (its own figures, through UN Comtrade)
JJ25, JJ26 = [m for m in HKM if m <= '202507'], [m for m in HKM if '202601' <= m <= '202607']
hkx = {}
for cmd in ('847330', '847180', '847150', '854231'):
    a, b = (sum(use(check42, 344, m, 'X', 156, cmd) for m in ms) for ms in (JJ25, JJ26))
    hkx[cmd] = (a, b)
    same_as_core(f'Comtrade Hong Kong exports to mainland China, HS {cmd}, Jan-Jul 2025', a); same_as_core(f'Comtrade Hong Kong exports to mainland China, HS {cmd}, Jan-Jul 2026', b)
    d42.append([f'Hong Kong total exports to mainland China, {HEAD[cmd]}: January to July 2025, then January to July 2026, billion US dollars', f'{a / 1e9:.2f} then {b / 1e9:.2f}', 'sums of 7 months each'])
hk_to_cn_26 = sum(hkx[c][1] for c in THREE)
d42.append(['Hong Kong total exports under the three named headings, January to July 2026: all destinations, then mainland China, billion US dollars', f'{f(hk[k26][4]) / 1e3:.1f} then {hk_to_cn_26 / 1e9:.1f}', 'sums of 7 months'])
# J.2 the label "Other Asia, nes" against Taiwan's own exports to Hong Kong, one heading (8473.30)
for lab, ms in (('2025', m25), ('January to July 2026', m26)):
    hk_side = sum(use(check42, 344, m, 'M', 490, '847330') for m in ms) / 1e3
    tw_side = tw_sum('香港', PARTS_TW, ms, check42)
    d42.append([f'Hong Kong imports under 8473.30 recorded as origin Other Asia, nes (code 490), {lab}, against Taiwan\'s own exports of computer parts to Hong Kong, thousand US dollars; ratio',
                f'{hk_side:,.0f} against {tw_side:,.0f}; {hk_side / tw_side:.2f}', 'imports are by origin and CIF, exports by destination and FOB: two measures, set side by side'])
# J.2b Taiwan's own exports to Hong Kong run to October 2026 (its finance ministry's groups; every maker's goods)
IC_TW = '積體電路'
JO26 = [m for m in TW26 if m >= '202607']
tw_hk = {g: tw_sum('香港', g, TW26, check42) for g in (ADP, PARTS_TW, IC_TW)}
d42 += [['Taiwan\'s exports to Hong Kong, January to October 2026, thousand US dollars: computers (all of heading 8471); computer parts (8473.30); integrated circuits', f'{tw_hk[ADP]:,.0f}; {tw_hk[PARTS_TW]:,.0f}; {tw_hk[IC_TW]:,.0f}', 'L18\'s table of the saved ministry page; cells re-checked here'],
        ['the same, computers plus computer parts, January to October 2026, billion US dollars', f'{(tw_hk[ADP] + tw_hk[PARTS_TW]) / 1e6:.2f}', 'sum of two groups'],
        ['the same, computers plus computer parts, July to October 2026, billion US dollars', f'{(tw_sum("香港", ADP, JO26, check42) + tw_sum("香港", PARTS_TW, JO26, check42)) / 1e6:.2f}', 'sum of two groups, four months'],
        ['the same, October 2026 alone, million US dollars', f'{(tw[("202610", "香港", ADP)] + tw[("202610", "香港", PARTS_TW)]) / 1e3:.0f}', 'one month']]
# J.3 Hong Kong's own monthly division tables (its statistics office's data service, saved by L18)
hkdiv = {}
for sid, sv, flow in (('cn-le18-hk-csd-410-50031', 'VAL_IM', 'imports'), ('cn-le18-hk-csd-410-50032', 'VAL_TX', 'total exports')):
    for r in json.loads((P / sid / 'body.json').read_text(encoding='utf-8'))['dataSet']:
        if r['freq'] == 'M' and r['COMMD'] in (75, 77) and r['sv'] == sv and r['svDesc'] == 'HK$ million' and '202501' <= r['period'] <= '202612':
            x = json.dumps(r, ensure_ascii=False, indent=1)
            hkdiv[(flow, r['COMMD'], r['period'])] = (r['figure'], sid, re.sub(r'\s+', ' ', x[x.index('"COMMD"'):x.rindex('}')]).strip())
DIVM = sorted({k[2] for k in hkdiv}); assert DIVM[0] == '202501' and DIVM[-1] == '202609', DIVM
def dv(flow, div, m, chk=check42):
    v, sid, fr = hkdiv[(flow, div, m)]; chk.append((sid, fr)); return v
rows = [[m, dv('imports', 75, m), dv('total exports', 75, m), dv('total exports', 75, m) - dv('imports', 75, m), dv('imports', 77, m), dv('total exports', 77, m), 'cn-le18-hk-csd-410-50031 and cn-le18-hk-csd-410-50032'] for m in DIVM]
write(O42 / 'hk_divisions_monthly.tsv', ['month', 'division_75_office_machines_and_computers_imports_hkd_million', 'division_75_total_exports_hkd_million', 'division_75_exports_minus_imports (ours)',
                                         'division_77_electrical_machinery_imports_hkd_million', 'division_77_total_exports_hkd_million', 'saved_ids'], rows)
assert rows[-1][1] == int(rel[('imports', 'Office')][2]) and rows[-1][2] == int(rel[('total exports', 'Office')][2])      # the monthly table and the press release agree for September 2026
gap = {r[0]: r[3] for r in rows}
g25, g26 = [gap[m] for m in DIVM if m < '202601'], [gap[m] for m in DIVM if m >= '202601']
d42 += [['office machines and computers division (75), imports, June, July, August, September 2026, million Hong Kong dollars', '; '.join(f'{dv("imports", 75, m):,}' for m in ('202606', '202607', '202608', '202609')), 'Hong Kong\'s monthly table 410-50031'],
        ['the same division, total exports, June, July, August, September 2026, million Hong Kong dollars', '; '.join(f'{dv("total exports", 75, m):,}' for m in ('202606', '202607', '202608', '202609')), 'Hong Kong\'s monthly table 410-50032'],
        ['the same division: total exports minus imports, June, July, August, September 2026, million Hong Kong dollars', '; '.join(f'{gap[m]:,}' for m in ('202606', '202607', '202608', '202609')), 'ours'],
        ['the same: average month of 2025, then of January to September 2026', f'{sum(g25) / len(g25):,.0f} then {sum(g26) / len(g26):,.0f}', 'ours, from the monthly figures'],
        ['the same: August plus September 2026', f'{gap["202608"] + gap["202609"]:,}', 'ours'],
        ['months, of the 21 from January 2025 to September 2026, in which the division\'s total exports exceeded its imports', sum(1 for m in DIVM if gap[m] > 0), 'count'],
        ['Singapore, line 84718010: re-exports to Hong Kong, January to June 2026, then July to October 2026, thousand Singapore dollars (units of the second in brackets)', f'{hk1:,.0f} then {hk2:,.0f} ({hku2:,.0f})', RAWSRC],
        ['Singapore, line 84718010: re-exports to mainland China, July to October 2026, thousand Singapore dollars', f'{cn2:,.0f}', RAWSRC]]
write(O42 / 'derived_figures.tsv', ['figure', 'value', 'how (all arithmetic is ours)'], d42)

# ---------- checks ----------
for path, chk in ((O34 / 'numbers_check.tsv', check34), (O42 / 'numbers_check.tsv', check42)):
    seen, out = set(), []
    for sid, w in chk:
        if (sid, w) not in seen: seen.add((sid, w)); out.append(f'{sid}\t{w}')
    path.write_text('# Every figure in this folder\'s table files, as the exact piece of the saved copy it was read from. Checked by scripts/cn_has.py.\n' + '\n'.join(out) + '\n', encoding='utf-8')
    r = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts' / 'cn_has.py'), str(path)], capture_output=True, text=True)
    print(f'{path.relative_to(HERE)}: {r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[-300:]}')
    if r.returncode != 0:
        print(r.stdout[-1500:]); sys.exit(1)
# ---------- K. round 4: the figures the two notes state must equal this script's values ----------
n0 = lambda x: f'{x:,.0f}'
jul_aug_us = (RAW[('us', '202607')][1] + RAW[('us', '202608')][1]) / 1e6      # round 9 of the outputs: of the dollar values
q1p, h1p, m9p = parts('202603')['cv'], parts('202606')['cv'], parts('202609')['cv']
mon = lambda m: n0(sgv[(m, 'RE-EXPORTS', 'MAINLAND CHINA', LINE)])
gacc_b = lambda per, name: f'{gacc[(per, name)]["cv"] / 1e6:.1f} billion'
IC, CPU, PARTS = 'Electronic integrated circuits', 'Central processing units', 'Parts and accessories of automatic data processing machines'
NOTE34 = [f'the line was {gacc_b("202609", PARTS)} dollars, against {gacc_b("202509", PARTS)} in January to September 2025: {p26["cv"] / p25["cv"]:.2f} times as much',
          f'were {gacc_b("202609", PARTS)} US dollars in January to September 2026, against {gacc_b("202509", PARTS)} in the same months of 2025',
          f'from {n0(tonnes(p25, "cq"))} tonnes to {n0(tonnes(p26, "cq"))} tonnes',
          f'about {n0(p25["cv"] / tonnes(p25, "cq"))} thousand dollars in the first period and about {n0(p26["cv"] / tonnes(p26, "cq"))} thousand in the second',
          f'integrated circuits was {ratio(IC):.2f} times that of a year earlier, of storage units {ratio("Storage units"):.2f} times, and of processing units {ratio(CPU):.2f} times',
          f'{q1p / 1e6:.1f} billion dollars in the first quarter of 2026, {(h1p - q1p) / 1e6:.1f} billion in the second and {(m9p - h1p) / 1e6:.1f} billion in the third',
          f'December 2025 alone was {parts("202512")["mv"] / 1e6:.1f} billion dollars, twice the 2025 monthly average of {parts("202512")["cv"] / 12 / 1e6:.2f} billion',
          f'prints {p26["pv"]} for value and {p26["pq"]} for weight',
          f'+{(p26["mv"] / p25["mv"] - 1) * 100:.1f}% in value and +{(tonnes(p26, "mq") / tonnes(p25, "mq") - 1) * 100:.1f}% in weight',
          f'+{(p26["cv"] / p25["cv"] - 1) * 100:.1f}% in value',
          f'[cn-o34-gacc-t14-imports-202512] | {gacc_b("202509", IC)} | {gacc_b("202609", IC)} | {gacc_b("202512", IC)} |',
          f'| Processing units of computers (8471.50) | {gacc_b("202509", CPU)} | {gacc_b("202609", CPU)} | {gacc_b("202512", CPU)} |',
          f'| Parts and accessories of computers (8473.30) | {gacc_b("202509", PARTS)} | {gacc_b("202609", PARTS)} | {gacc_b("202512", PARTS)} |',
          f'in January to June 2026 ({n0(cn1)} thousand) and about {cn2 / 1e6:.1f} billion in July to October 2026 ({n0(cn2)} thousand): {mon("202607")} thousand in July, {mon("202608")} in August, {mon("202609")} in September and {mon("202610")} in October',
          f'about {cn1 / 1e3:.0f} million Singapore dollars in January to June 2026 and about {cn2 / 1e6:.1f} billion in July to October 2026',
          f'In all of 2025 they were {n0(cn25)} thousand',
          f'{n0(sgs(sgv, "RE-EXPORTS", "MAINLAND CHINA", H1, "84718070"))} thousand in January to June 2026 and {n0(sgs(sgv, "RE-EXPORTS", "MAINLAND CHINA", H2, "84718070"))} thousand in July to October',
          f'{n0(u2)} units in the four months, at about {cn2 / u2:.1f} thousand Singapore dollars a unit, against {cn1 / u1:.2f} thousand a unit',
          f'{n0(sgs(sgv, "IMPORTS", "WORLD", H2))} thousand Singapore dollars in all, of which {n0(ogs(ogv, "TAIWAN", H2))} thousand of Taiwan origin, {n0(ogs(ogv, "MEXICO", H2))} thousand of Mexico origin and {n0(ogs(ogv, "UNITED STATES OF AMERICA", H2))} thousand of United States origin',
          f'about {usd2 / 1e6:.2f} billion US dollars',
          f'{n0(ja_sgd)} thousand Singapore dollars, about {ja_usd / 1e6:.2f} billion US dollars',
          f'exports to Singapore under the three named headings of {us_sg3["202607"]:.1f} and {us_sg3["202608"]:.1f} million dollars',
          f'against {us_sg3_h1:.1f} million in an average month of January to June 2026',
          f'{us_sg["202607"] / 1e6:.1f} and {us_sg["202608"] / 1e6:.1f} million dollars were under heading 8471.80',
          f'were {f(us["202607"][1]):.1f} and {f(us["202608"][1]):.1f} million dollars, against {us3_h1:.1f} million in an average month of January to June',
          f'about {cn1 / 6 / 1e3:.1f} million Singapore dollars',
          f'together carried {jul_aug_us:.1f} million dollars to the three places',
          f'{us_sg3_26:,.1f} million dollars in the eight months; added to the {f(y26[1]):,.1f} million, they make {us_sg3_plus:,.1f} million dollars, and the same division gives about {round(with_sg_chips, -2):,.0f} chips',      # round 10
          f'{hkx25 / 1e9:.2f} billion US dollars in January to July 2025 and {hkx26 / 1e9:.2f} billion in January to July 2026',      # round 10: US added
          f'were {tw_share:.2f}% of its exports of the group to the world',
          f'came to {f(y26[1]):,.1f} million dollars', f'(about {round(f(y26[1]) * 1e6 / PRICE, -2):,.0f})', f'never passed {int(f(mx[1])) + 1} million dollars',
          f'| All of January to August 2026 | {f(y26[1]):,.1f} million dollars |', f'{f(y26[1]):,.1f} million dollars divided by 27,000 dollars is about {round(f(y26[1]) * 1e6 / PRICE, -2):,.0f} chips',      # round 9 of the outputs
          f'{p26["cv"] / p25["cv"]:.2f} times as much computer parts by value', f'{NUMW[len(sg_files)].capitalize()} of those answers were read again for this note',      # round 10: reworded
          f'{270e6 / (q3_parts * 1e3) * 100:.1f}% of the parts line in the third quarter of 2026 ({q3_parts / 1e6:.1f} billion dollars), or {270e6 / (ics("202609")["mv"] * 1e3) * 100:.2f}% of China\'s imports of integrated circuits in September 2026 alone ({ics("202609")["mv"] / 1e6:.1f} billion dollars)',
          f'the sum of the {NUMW[len(TW_CODES)]} codes that begin 8471, in thousands of US dollars, in every month (our comparison)']
NOTE34 += [f'its highest month of the {len(MONTHS)} was {MONTH_NAMES[int(CHIP_MAX[4:]) - 1]} {CHIP_MAX[:4]}, at {RAW[("us", CHIP_MAX)][4] / 1e6:,.1f} million dollars']      # round 12
NOTE34 += [f"The US customs export figures used for the estimate above end in {DATA_LAST:%B %Y} and cover only "
           f"{(DATA_LAST - Q3_FIRST).days + 1} of the quarter's {(Q3_LAST - Q3_FIRST).days + 1} days."]
dvs = lambda flow, ms: [f'{dv(flow, 75, m, []):,}' for m in ms]
JJAS = ('202606', '202607', '202608', '202609')
im, ex = dvs('imports', JJAS), dvs('total exports', JJAS)
NOTE42 = [f'{im[0]} million Hong Kong dollars in June 2026, {im[1]} million in July, {im[2]} million in August and {im[3]} million in September',
          f'{ex[0]} million, {ex[1]} million, {ex[2]} million and {ex[3]} million',
          f'by {gap["202608"]:,} million Hong Kong dollars, against {gap["202607"]:,} million in July', f'the excess was {gap["202609"]:,} million',
          f'come to {gap["202608"] + gap["202609"]:,} million', f'at {n0(sum(g26) / len(g26))} million each', f'average excess was {n0(sum(g25) / len(g25))} million a month',
          f'about {600000 * PRICE * 7.8 / 1e9:.0f} billion Hong Kong dollars',
          f'{tw_hk[ADP] / 1e6:.2f} billion US dollars of computers', f'{tw_hk[PARTS_TW] / 1e6:.2f} billion of computer parts, {(tw_hk[ADP] + tw_hk[PARTS_TW]) / 1e6:.2f} billion together',
          f'{(tw_sum("香港", ADP, JO26, []) + tw_sum("香港", PARTS_TW, JO26, [])) / 1e6:.2f} billion together',
          f'in October alone, {(tw[("202610", "香港", ADP)] + tw[("202610", "香港", PARTS_TW)]) / 1e3:.0f} million',
          f'{tw_hk[IC_TW] / 1e6:.1f} billion dollars to Hong Kong in the ten months',
          f'{(tw_hk[ADP] + tw_hk[PARTS_TW]) / 1e6:.2f} billion US dollars of computers and computer parts',
          f'about {hk1 / 1e3:.0f} million Singapore dollars in January to June 2026 and about {hk2 / 1e3:.0f} million in July to October',
          f'about {cn2 / 1e6:.1f} billion went to mainland China',
          f'far below the {600000 * PRICE / 1e9:.1f} billion dollars of point 1']
r_hk = {}
for lab, ms in (('2025', m25), ('2026', m26)):
    r_hk[lab] = sum(val(344, m, 'M', 490, '847330') for m in ms) / 1e3 / sum(tw[(m, '香港', PARTS_TW)] for m in ms)
NOTE42 += [f'were {r_hk["2025"]:.2f} times Taiwan\'s own recorded exports of computer parts to Hong Kong in 2025, and {r_hk["2026"]:.2f} times in January to July 2026']
NOTE42 += [f'{hkx["847330"][0] / 1e9:.2f} billion dollars in January to July 2025 and {hkx["847330"][1] / 1e9:.2f} billion in January to July 2026',
           f'under 8471.80 they were {hkx["847180"][0] / 1e9:.2f} and {hkx["847180"][1] / 1e9:.2f} billion, and under 8471.50, {hkx["847150"][0] / 1e9:.2f} and {hkx["847150"][1] / 1e9:.2f} billion',
           f'{f(hk[k26][4]) / 1e3:.1f} billion dollars in January to July 2026, {hk_to_cn_26 / 1e9:.1f} billion went to the mainland',
           f'came to {f(y26[3]):,.1f} million dollars over the eight months January to August 2026']      # round 9 of the outputs
A0, A1, A2, A3, A4 = (AVG[k] for k in ('all origins', 'mainland China origin', 'South Korea origin', 'United States origin', 'origin Other Asia, nes (code 490)'))
assert all(before < after for before, after in (A1, A2, A3)) and A4[0] > A4[1], 'Hong Kong imports: the direction of change by origin in point 7'
NOTE42 += [f'The average month was {A0[0]:.1f} billion dollars in 2025 and {A0[1]:.1f} billion in January to July 2026. By origin, average monthly imports rose from {A1[0]:.1f} to {A1[1]:.1f} billion '
           f'for mainland China, from {A2[0]:.2f} to {A2[1]:.1f} billion for South Korea and from {A3[0]:.2f} to {A3[1]:.2f} billion for the United States, and fell from {A4[0]:.2f} to {A4[1]:.2f} billion under Other Asia, nes']      # round 12: point 7, rounded once
hk25 = hk['2025 January to December (ours: sum)']
NOTE42 += [f'| {lab} | {f(hk25[i]):,.1f} million dollars | {f(hk[k26][i]):,.1f} million dollars |' for i, lab in
           ((1, 'Imports of United States origin'), (2, 'Imports under Other Asia, nes (code 490)'), (3, 'Imports, all origins'), (4, 'Total exports, all destinations'))]
note_ok = 0
for path, phrases, control in ((O34 / 'customs_figures_base.txt', NOTE34, f'the line was {p26["cv"] / 1e6 + 1:.1f} billion dollars'), (O42 / 'reuters_hongkong_report_base.txt', NOTE42, f'by {gap["202608"] + 1:,} million Hong Kong dollars')):
    text = path.read_text(encoding='utf-8')
    missing = [ph for ph in phrases if ph not in text]
    if missing or control in text:
        print(f'{path.relative_to(HERE)}: the note does not state these figures as the script computes them:'); print('\n'.join('   ' + m for m in missing)); sys.exit(1)
    note_ok += len(phrases)
print(f'figures stated in the two notes that equal the script\'s values: {note_ok} of {len(NOTE34) + len(NOTE42)} phrases (a planted wrong figure is in neither note)')
print(f'China as a reporter in the {len(MONTHS)} saved Comtrade months: {china_rows} rows')
print(f'China\'s monthly periods listed by Comtrade: {len(da)}, from {china_first} to {china_last}')
print(f'classification decisions of 2025 read: {n_dec}; in headings 8471, 8473 or 8542: {n_hit}')
print(f'Hong Kong as a reporter: months {HKM[0]} to {HKM[-1]} ({len(HKM)} months)')
print(f'Singapore raw files: {len(sg_files)} read, each matching its sha256 in L18\'s manifest; {sg_repeats} repeated rows with one value, taken once; our sums equal the core\'s tables/trade_derived_figures.tsv')
print(f'Hong Kong division tables: months {DIVM[0]} to {DIVM[-1]} ({len(DIVM)} months); September 2026 equals the press release')
print(f'Hong Kong sums (three headings and chips, 2025 and January to {HKM[-1][4:]} 2026): {n_ann} of {n_ann} equal the core\'s tables/trade_annual_summary.tsv, months held checked; '
      'sums of months are now taken from the dollar values before rounding (round 9 of the outputs)')
