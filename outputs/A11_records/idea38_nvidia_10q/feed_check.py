"""Idea 38: read the two saved Nvidia investor-site feeds, the SEC's own record of Nvidia's filings (two readings saved by
other agents: cn-le05-sec-submissions-20261123 and, newest, cn-ga06-sec-submissions-20261124), the saved call transcript,
six saved reports and two project tables, and write the facts the note states.
Run: python3 -I feed_check.py   -> feed_check.tsv (key <TAB> value) and prints it.
Feeds: cn-o38-nvda-feed-secfilings-2026-c (every SEC filing of 2026 the site lists; -b is the first reading of the same feed) and cn-o38-nvda-feed-finreports-fy2027
(the documents listed for each quarter of fiscal 2027). Control: the filings feed must list the 10-Q of Aug 26, 2026."""
import json, re, sys
from datetime import datetime
from pathlib import Path
P = Path('research/primary')
HERE = Path(__file__).resolve().parent
out = []
def put(k, v): out.append((k, str(v)))
a = 'cn-o38-nvda-feed-secfilings-2026-c'      # the newest reading (round 2); the first reading is -b
m = json.loads((P / a / 'meta.json').read_text()); put('filings_feed_fetched_utc', m['fetched_utc']); put('filings_feed_sha256', m['sha256'])
rows = json.loads((P / a / 'body.json').read_text())['GetEdgarFilingListResult']
d = lambda s: datetime.strptime(s, '%m/%d/%Y %H:%M:%S')
rows.sort(key=lambda r: d(r['ReceivedDate']), reverse=True)
put('filings_listed_2026', len(rows))
m0 = json.loads((P / 'cn-o38-nvda-feed-secfilings-2026-b' / 'meta.json').read_text())
put('filings_feed_id', a); put('earlier_feed_fetched_utc', m0['fetched_utc']); put('earlier_feed_same_bytes', m0['sha256'] == m['sha256'])
for i, r in enumerate(rows[:4], 1): put(f'newest_{i}', f"{r['FilingTypeMnemonic']} | filed {d(r['FilingDate']):%Y-%m-%d} | received {r['ReceivedDate']} | {r['FilingDescription']}")
tq = [r for r in rows if r['FilingTypeMnemonic'].upper().startswith('10-Q')]
put('10Q_rows_2026', '; '.join(f"{d(r['FilingDate']):%Y-%m-%d}" for r in tq))
if not any(d(r['FilingDate']).strftime('%Y-%m-%d') == '2026-08-26' for r in tq): sys.exit('control failed: the feed does not list the 10-Q of Aug 26, 2026')
put('10Q_filed_after_2026-10-25', sum(1 for r in tq if d(r['FilingDate']) > datetime(2026, 10, 25)))
put('NT_10Q_rows_2026', sum(1 for r in rows if r['FilingTypeMnemonic'].upper().startswith('NT')))
b = 'cn-o38-nvda-feed-finreports-fy2027'
m = json.loads((P / b / 'meta.json').read_text()); put('reports_feed_fetched_utc', m['fetched_utc'])
for r in json.loads((P / b / 'body.json').read_text())['GetFinancialReportListResult']:
    cats = [x['DocumentTitle'] for x in r['Documents']]
    put(f"documents_listed_{r['ReportTitle'].replace(' ', '_')}", '; '.join(cats))
    put(f"has_10Q_{r['ReportTitle'].replace(' ', '_')}", '10-Q' in cats)
t = (P / 'cn-o38-nvda-q3fy27-call-transcript-pdf' / 'text.txt').read_text(encoding='utf-8')
body = t.split('STATUS: 200', 1)[1]
put('call_transcript_mentions_China', len(re.findall(r'\bChina\b', body)))
put('call_transcript_mentions_Hopper', len(re.findall(r'\bHopper\b', body)))
put('call_transcript_mentions_H200', len(re.findall(r'\bH-?200\b', body)))
put('call_transcript_mentions_export_control', len(re.findall(r'export controls?', body, re.I)))
put('china_share_of_data_center_revenue_pct', f'{2.4 / 107.6 * 100:.1f}')
AUTH = r"\bPRC\b|\bBeijing\b|Chinese government|China.s government|government of China|Chinese authorit|Chinese regulator"
for k, pat in (('PRC', r'\bPRC\b'), ('Beijing', r'\bBeijing\b'), ('Chinese_government', r'Chinese government|China.s government|government of China')):
    put(f'call_transcript_mentions_{k}', len(re.findall(pat, body)))
# the same words in each of the four call transcripts the note quotes; control: the word China is in each
CALLS = (('2025-08-27', 'ms-sgp-nvda-q2fy26-call-transcript-pdf'), ('2026-05-20', 'cn-o38-nvda-q1fy27-call-transcript-pdf'), ('2026-08-26', 'cn-o38-nvda-q2fy27-call-transcript-pdf'), ('2026-11-17', 'cn-o38-nvda-q3fy27-call-transcript-pdf'))
for dcall, sid in CALLS:
    bt = (P / sid / 'text.txt').read_text(encoding='utf-8', errors='replace').split('STATUS: 200', 1)[1]
    put(f'call_{dcall}_names_chinese_authority', len(re.findall(AUTH, bt))); put(f'call_{dcall}_says_China', len(re.findall(r'\bChina\b', bt)))
put('calls_counted', len(CALLS))
# --- the SEC's own record of the company's filings (data.sec.gov submissions file): two readings, both saved in research/primary.
# sec_*  : the newest reading, cn-ga06-sec-submissions-20261124 (saved Nov 24, 2026 by gap agent GA06; the argument's open list cites it)
# sec0_* : the first reading, cn-le05-sec-submissions-20261123 (saved Nov 23, 2026 by agent L05)
# Entries are ordered by filing date and then by the record's own acceptance time (acceptanceDateTime), newest first; a sort on
# the form's name would put an 8-K before a Form 4 of the same day whatever their times (round 8, core edit 7).
def sec(S, pre):
    sm = json.loads((P / S / 'meta.json').read_text()); put(f'{pre}_record_id', S); put(f'{pre}_record_fetched_utc', sm['fetched_utc']); put(f'{pre}_record_url', sm['url'])
    rc = json.loads((P / S / 'body.json').read_text())['filings']['recent']
    srows = sorted(zip(rc['filingDate'], rc['acceptanceDateTime'], rc['form'], rc['reportDate'], rc['accessionNumber']), reverse=True)
    srows = [(f, fm, rp, acc, at) for f, at, fm, rp, acc in srows]          # filed, form, report date, accession, accepted
    put(f'{pre}_record_entries', len(srows)); put(f'{pre}_newest_entry', f'{srows[0][1]} | {srows[0][0]}')
    day = [x for x in srows if x[0] == srows[0][0]]
    put(f'{pre}_newest_day_entries', ' ;; '.join(f'{x[1]} | report {x[2] or "-"} | {x[3]} | accepted {x[4]}' for x in day))
    sq = [x for x in srows if x[1] == '10-Q']
    if not any(x[0] == '2026-08-26' and x[2] == '2026-07-26' for x in sq): sys.exit(f'control failed: the SEC record {S} does not list the 10-Q of Aug 26, 2026')
    put(f'{pre}_10Q_rows', len(sq)); put(f'{pre}_newest_10Q', f'{sq[0][0]} | period {sq[0][2]} | {sq[0][3]}')
    put(f'{pre}_10Q_for_period_2026-10-25', sum(1 for x in srows if x[1].startswith('10-Q') and x[2] == '2026-10-25'))
    put(f'{pre}_10Q_filed_after_2026-10-25', sum(1 for x in srows if x[1].startswith('10-Q') and x[0] > '2026-10-25'))
    put(f'{pre}_NT_filings_2026', sum(1 for x in srows if x[1].startswith('NT') and x[0] >= '2026-01-01'))
sec('cn-ga06-sec-submissions-20261124', 'sec')
sec('cn-le05-sec-submissions-20261123', 'sec0')
# --- the project's table of Nvidia's wording, filing by filing (tables/nvidia_wording_by_filing.tsv)
T = HERE.parents[2] / 'tables'
wl = [l.split('\t') for l in (T / 'nvidia_wording_by_filing.tsv').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
wh, wrows = wl[0], [dict(zip(wl[0], r)) for r in wl[1:]]
put('wording_table_rows', len(wrows))
NEED = (('man-ms-nvda-2024q3-10q-58a58e', 'The Chinese government may also encourage customers to purchase from our China-based'),
        ('man-ms-sec-10q-2025-07', 'The Chinese government has and may continue to encourage customers to purchase from our'),
        ('man-ms-sec-10q-2025-10', 'government has encouraged customers to purchase from our China-based competitors and restricted customers from'),
        ('man-ms-sec-10k-fy2026', 'government has encouraged customers to purchase from our China-based competitors and discouraged customers'),
        ('man-ms-sec-10q-2026-04', 'Chinese government has encouraged customers to purchase from our China-based competitors and discouraged'),
        ('man-ms-sec-10q-2026-07', 'but such sales were restricted by the PRC government'),
        ('ms-p3-nvda-8k-20261117-pdf', 'We are not assuming any Data Center compute revenue from China in our outlook.'))
for sid, frag in NEED:
    hit = [r for r in wrows if r['saved_id'] == sid and frag in r['words']]
    if not hit: sys.exit(f'the wording table has no row for {sid} with: {frag}')
    put(f'wording_row_date_{sid}', hit[0]['date'])
if any(frag in r['words'] for r in wrows for frag in ('this sentence is not in any Nvidia filing',)): sys.exit('control failed')
# --- the word "foreclosed" in each report of the note's table (text.txt of each saved copy)
fc = {sid: len(re.findall(r'foreclosed', (P / sid / 'text.txt').read_text(encoding='utf-8', errors='replace'))) for sid, _ in NEED[:6]}
for sid, n in fc.items(): put(f'foreclosed_in_{sid}', n)
# --- revenue from customers headquartered in China (incl. Hong Kong): the nine quarters on the headquarters basis
rl = [l.split('\t') for l in (T / 'nvidia_china_revenue.tsv').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
rr = [dict(zip(rl[0], r)) for r in rl[1:]]
q = sorted((r['period_end'], int(r['value_musd']), r['how']) for r in rr if r['basis'] == 'headquarters' and re.match(r'Q[1-4] FY', r['period']))
put('rev_hq_quarters', len(q)); put('rev_hq_first_period_end', q[0][0]); put('rev_hq_last_period_end', q[-1][0])
put('rev_hq_values', '; '.join(f'{v:,}' for _, v, _ in q)); put('rev_hq_derived', sum(1 for _, _, h in q if h.startswith('derived')))
put('rev_hq_last_is_highest', q[-1][1] == max(v for _, v, _ in q))
(HERE / 'feed_check.tsv').write_text('key\tvalue\n' + '\n'.join('\t'.join(x) for x in out) + '\n', encoding='utf-8')
print('\n'.join('\t'.join(x) for x in out))
