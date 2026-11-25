"""Idea 38: build the note (nvidia_10q.md and .html). Run: python3 -I build.py   (in this folder)
1. feed_check.py reads the saved feeds and transcript and writes feed_check.tsv (stops if its control fails)
2. the counts in nvidia_10q_base_src.txt are filled from feed_check.tsv and from a search of the saved rule (no count is typed)
3. scripts/cn_doc_build.py checks every quotation and hidden statement, then writes the note. Stops at the first failure."""
import csv, re, subprocess, sys, html
from datetime import datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent
P = Path('research/primary')
r = subprocess.run([sys.executable, '-I', str(HERE / 'feed_check.py')], capture_output=True, text=True)
if r.returncode: sys.exit('feed_check.py failed: ' + r.stdout[-300:] + r.stderr[-300:])
f = dict(l.rstrip('\n').split('\t', 1) for l in open(HERE / 'feed_check.tsv', encoding='utf-8').read().splitlines()[1:])
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
def nice(s):
    d = datetime.strptime(s, '%Y-%m-%d'); return f'{MON[d.month - 1]} {d.day}, {d.year}'
def stamp(s):
    d = datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ'); return f'{d:%H:%M} UTC on {MON[d.month - 1]} {d.day}, {d.year}'
rule = html.unescape(re.sub(r'(?s)<[^>]+>', ' ', (P / 'cn-o38-us-rule-fr-20261119-text' / 'body.html').read_text(encoding='utf-8', errors='replace')))
if len(re.findall(r'\bBrazil\b', rule)) == 0: sys.exit('control failed: Brazil not found in the rule text')
n_h200_rule = len(re.findall(r'H-?200', rule))
if n_h200_rule != 0: sys.exit(f'the rule text holds H200 {n_h200_rule} times: rewrite the sentence')
n_after = int(f['10Q_filed_after_2026-10-25'])
if n_after != 0 or f['has_10Q_Third_Quarter_2027'] != 'False': sys.exit('A 10-Q NOW SHOWS IN THE FEEDS: the note must be rewritten, not rebuilt')
words = {0: 'none', 2: 'twice'}
for pre in ('sec', 'sec0'):
    if int(f[f'{pre}_10Q_for_period_2026-10-25']) != 0 or int(f[f'{pre}_10Q_filed_after_2026-10-25']) != 0 or int(f[f'{pre}_NT_filings_2026']) != 0: sys.exit(f'A 10-Q OR A LATE-FILING NOTICE NOW SHOWS IN THE SEC RECORD ({f[pre + "_record_id"]}): the note must be rewritten, not rebuilt')
if f['sec_newest_10Q'] != f['sec0_newest_10Q'] or f['sec_10Q_rows'] != f['sec0_10Q_rows']: sys.exit('the two readings of the SEC record differ on the 10-Q rows: rewrite the sentence "In both readings"')
# round 8 (core edit 7): the newest reading's newest entries, in the record's own order of acceptance, newest first. The template
# names the 8-K for its one fact (atlas/ROUND8.txt R2) and the Form 4 by its form only; if the entries differ, the sentence is rewritten.
day = [x.split(' | ') for x in f['sec_newest_day_entries'].split(' ;; ')]
if [(x[0], x[1]) for x in day] != [('4', 'report 2026-11-19'), ('8-K', 'report 2026-11-22')] or f['sec_newest_entry'] != '4 | 2026-11-23': sys.exit(f"the newest entries of the SEC record changed ({f['sec_newest_day_entries']}): rewrite the sentence on them")
k8 = (P / 'cn-ga06-nvda-8k-20261123-pdf' / 'text.txt').read_text(encoding='utf-8', errors='replace')
if 'Date of Report (Date of earliest event reported): November 22, 2026' not in k8 or 'Date: November 23, 2026' not in k8: sys.exit('the saved 8-K is not the one the SEC record lists for Nov 23, 2026 (report date Nov 22): check the id')
if 'Date of Report (Date of earliest event reported): November 17, 2026' in k8: sys.exit('control failed')
if f['rev_hq_last_is_highest'] != 'True' or f['rev_hq_quarters'] != '9' or f['rev_hq_last_period_end'] != '2026-10-25': sys.exit('the revenue run changed: rewrite the sentence')
if f['foreclosed_in_man-ms-nvda-2024q3-10q-58a58e'] != '0' or any(f[k] == '0' for k in f if k.startswith('foreclosed_in_') and '2024q3' not in k): sys.exit('the count of the word foreclosed changed: rewrite the table')
if any(f[f'call_transcript_mentions_{k}'] != '0' for k in ('PRC', 'Beijing', 'Chinese_government')): sys.exit('the Nov 17 call names a Chinese authority after all: rewrite')
for k in [k for k in f if k.endswith('_names_chinese_authority')]:
    if f[k] != '0': sys.exit(f'{k} is not 0: a call names a Chinese authority after all: rewrite')
if any(f[k] == '0' for k in f if k.endswith('_says_China')) or f['calls_counted'] != '4': sys.exit('control failed: a call transcript without the word China, or not four calls')
snew, s10, s0new = f['sec_newest_entry'].split(' | '), f['sec_newest_10Q'].split(' | '), f['sec0_newest_entry'].split(' | ')
def head(s):
    d = datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ'); return f'{MON[d.month - 1]} {d.day}, {d.year}, {d:%H:%M} UTC'
new = [f[f'newest_{i}'].split(' | ') for i in (1, 2)]                      # type | filed ... | received <stamp> | description
rec = [x[2].replace('received ', '') for x in new]
def rday(s):
    d = datetime.strptime(s, '%m/%d/%Y %H:%M:%S'); return f'{MON[d.month - 1]} {d.day}, {d.year}'
FID = f['filings_feed_id']
hidden = [f"!! {FID} | FETCHED: {f['filings_feed_fetched_utc']}", f'!! {FID} | {rec[0]}', f'!! {FID} | {rec[1]}', f'!! {FID} | 08/26/2026 00:00:00',
          f"!! cn-o38-nvda-feed-secfilings-2026-b | FETCHED: {f['earlier_feed_fetched_utc']}"]
v = {'FILINGS_FETCHED': stamp(f['filings_feed_fetched_utc']), 'FILINGS_HEAD': head(f['filings_feed_fetched_utc']), 'EARLIER_FETCHED': stamp(f['earlier_feed_fetched_utc']),
     'EARLIER_SAME': 'was the same, byte for byte' if f['earlier_feed_same_bytes'] == 'True' else 'showed the same 10-Q rows',
     'NEWEST_SENTENCE': f'At that time the newest was a Form {new[0][0]} received on {rday(rec[0])}, and the one before it a Form {new[1][0]} received on {rday(rec[1])}.', 'FEED_HIDDEN': chr(10).join(hidden),
     'REPORTS_FETCHED': stamp(f['reports_feed_fetched_utc']), 'N_FILINGS': f['filings_listed_2026'],
     'TENQ_ROWS': ' and '.join(nice(x) for x in f['10Q_rows_2026'].split('; ')), 'TENQ_AFTER': words[n_after],
     'DOCS_Q3': f['documents_listed_Third_Quarter_2027'].replace('; ', ', '), 'SHARE': f['china_share_of_data_center_revenue_pct'],
     'N_CHINA': {2: 'twice'}[int(f['call_transcript_mentions_China'])], 'N_H200': {0: 'not at all'}[int(f['call_transcript_mentions_H200'])],
     'SEC_FETCHED': stamp(f['sec_record_fetched_utc']), 'SEC_HEAD': head(f['sec_record_fetched_utc']), 'SEC_NEWEST_DATE': nice(snew[1]),
     'SEC0_FETCHED': stamp(f['sec0_record_fetched_utc']), 'SEC0_NEWEST_FORM': s0new[0], 'SEC0_NEWEST_DATE': nice(s0new[1]),
     'SEC_10Q_DATE': nice(s10[0]), 'SEC_10Q_PERIOD': nice(s10[1].replace('period ', '')), 'SEC_N_10Q': f['sec_10Q_rows'],
     'SEC_HIDDEN': chr(10).join([f"!! {f['sec_record_id']} | FETCHED: {f['sec_record_fetched_utc']}", f"!! {f['sec_record_id']} | {s10[2]}"]
                               + [f"!! {f['sec_record_id']} | {x[2]}" for x in day] + [f"!! {f['sec_record_id']} | {x[3].replace('accepted ', '')}" for x in day]
                               + [f"!! {f['sec0_record_id']} | FETCHED: {f['sec0_record_fetched_utc']}", f"!! {f['sec0_record_id']} | {s10[2]}"]),
     'N_WORDING_ROWS': f['wording_table_rows'], 'REV_SEQ': f['rev_hq_values'].replace('; ', ', '), 'REV_FIRST': nice(f['rev_hq_first_period_end']),
     'REV_N': {9: 'nine'}[int(f['rev_hq_quarters'])], 'REV_DERIVED': {2: 'Two'}[int(f['rev_hq_derived'])]}
t = (HERE / 'nvidia_10q_base_src.txt').read_text(encoding='utf-8')
for k, x in v.items(): t = t.replace('{' + k + '}', str(x))
left = re.findall(r'\{[A-Z_0-9]+\}', t)
if left: sys.exit(f'unfilled: {left}')
if datetime.strptime(f['sec_record_fetched_utc'], '%Y-%m-%dT%H:%M:%SZ') <= datetime.strptime(f['filings_feed_fetched_utc'], '%Y-%m-%dT%H:%M:%SZ'): sys.exit('the SEC record is not the latest reading: fix the headline time')
(HERE / 'nvidia_10q_base.txt').write_text(t, encoding='utf-8')
FEED = 'https://investor.nvidia.com/feed/SECFiling.svc/GetEdgarFilingList?apiKey=SITE_PUBLIC_KEY&exchange=CIK&symbol=0001045810&formGroupIdList=&excludeNoDocuments=true&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=2026&excludeSelection=1'
REP = 'https://investor.nvidia.com/feed/FinancialReport.svc/GetFinancialReportList?apiKey=SITE_PUBLIC_KEY&reportTypes=First%20Quarter|Second%20Quarter|Third%20Quarter|Fourth%20Quarter&excludeReportTypes=&reportSubTypeList[]=&excludeSelection=1&year=2027'
for sid, u in ((FID, FEED), ('cn-o38-nvda-feed-secfilings-2026-b', FEED), ('cn-o38-nvda-feed-finreports-fy2027', REP)):
    import json as _j
    if _j.loads((P / sid / 'meta.json').read_text())['url'] != u: sys.exit(f'{sid}: the saved address is not the one in the references')
gen = [f"{FID}\tFIL\tNvidia investor site, its list of the company's SEC filings for 2026 (a data feed), as fetched a second time, at {stamp(f['filings_feed_fetched_utc'])}\t{FEED}",
       f"cn-o38-nvda-feed-secfilings-2026-b\tFIL\tThe same list of the company's SEC filings for 2026, as first fetched, at {stamp(f['earlier_feed_fetched_utc'])}\t{FEED}",
       f"cn-o38-nvda-feed-finreports-fy2027\tFIL\tNvidia investor site, its list of the documents posted for each quarter of fiscal 2027 (a data feed), as fetched at {stamp(f['reports_feed_fetched_utc'])}\t{REP}"]
(HERE / 'extra_refs.tsv').write_text('\n'.join(gen) + '\n' + (HERE / 'refs_hand.tsv').read_text(encoding='utf-8'), encoding='utf-8')
r = subprocess.run([sys.executable, '-I', 'scripts/cn_doc_build.py', str(HERE / 'nvidia_10q_base.txt'), '--refs', str(HERE / 'extra_refs.tsv'), '--title', 'Nvidia Report Not Filed', '--eyebrow', 'China chip policy: new research, idea 38'], capture_output=True, text=True)
print(r.stdout[-3000:], r.stderr[-800:]); sys.exit(r.returncode)
