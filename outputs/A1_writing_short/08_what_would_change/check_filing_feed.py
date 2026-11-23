#!/usr/bin/env python3
"""Idea 8, item 8: does the saved record of Nvidia's SEC filings show a quarterly report for the quarter ended Oct 25, 2026?

Run: python3 -I check_filing_feed.py
Reads research/primary/cn-le05-sec-submissions-20261123/body.json: the Securities and Exchange Commission's own
record of the company's filings, saved by the project on Nov 23, 2026 (the argument cites it). Reads only; it does
not fetch a newer list. The page says: not yet filed when looked for on Nov 23, 2026. Exit 0 only if the saved
record says exactly that: its newest quarterly report (10-Q) is the one filed Aug 26, 2026 for the period ended
Jul 26, 2026, and no annual or quarterly report covers a period ending on or after Oct 25, 2026.
Controls: the record must hold the report filed Aug 26, 2026 (so the search can see a quarterly report), and some
filing dated after Aug 26, 2026 (so the record reaches past that day).
"""
import json, sys
from pathlib import Path

SID = 'cn-le05-sec-submissions-20261123'
d = Path(__file__).resolve().parents[5] / 'research' / 'primary' / SID
rec = json.loads((d / 'body.json').read_text(encoding='utf-8'))['filings']['recent']
fetched = json.loads((d / 'meta.json').read_text())['fetched_utc']
rows = list(zip(rec['form'], rec['filingDate'], rec['reportDate']))
periodic = sorted((f, fd, rd) for f, fd, rd in rows if f in ('10-Q', '10-K'))
q = sorted((fd, rd) for f, fd, rd in rows if f == '10-Q')
newest = max(fd for _, fd, _ in rows)
print(f'{SID}: saved {fetched}; {len(rows)} filings in the record, the newest dated {newest}; {len(q)} quarterly reports (10-Q)')
print(f'newest quarterly report: filed {q[-1][0]} for the period ended {q[-1][1]}')
ok = True
if ('2026-08-26', '2026-07-26') not in q: print('CONTROL FAILED: the report filed 2026-08-26 is not in the record'); ok = False
if not newest > '2026-08-26': print('CONTROL FAILED: the record does not reach past 2026-08-26'); ok = False
late = [(f, fd, rd) for f, fd, rd in periodic if rd >= '2026-10-25' or (f == '10-Q' and fd > '2026-08-26')]
if late: print(f'CHANGE THE TEXT: a report for the quarter ended Oct 25, 2026, or a later one, is in the record: {late}'); ok = False
if q[-1] != ('2026-08-26', '2026-07-26'): print('CHANGE THE TEXT: the newest quarterly report is not the one the page names'); ok = False
print('result: no report for a period ending on or after 2026-10-25 is in the record; both controls hold' if ok else 'result: FAILED')
sys.exit(0 if ok else 1)
