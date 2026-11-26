#!/usr/bin/env python3
"""Idea 8, item 8: do the saved records of Nvidia's SEC filings show a quarterly report for the quarter ended Oct 25, 2026?

Run: python3 -I check_filing_feed.py
Reads two saved copies of the Securities and Exchange Commission's own record of the company's filings (the argument
cites both): research/primary/cn-le05-sec-submissions-20261123/body.json, saved Nov 23, 2026, and
research/primary/cn-ga06-sec-submissions-20261124/body.json, saved Nov 24, 2026. Reads only; it fetches nothing.
The page says: not yet filed when looked for on Nov 23, 2026, nor when fetched again on Nov 24, 2026, with filings up
to Nov 23. Exit 0 only if each saved record says exactly that: its newest quarterly report (10-Q) is the one filed
Aug 26, 2026 for the period ended Jul 26, 2026, no annual or quarterly report covers a period ending on or after
Oct 25, 2026, and the Nov 24 copy's newest filing is dated Nov 23, 2026.
Controls: each record must hold the report filed Aug 26, 2026 (so the search can see a quarterly report), and some
filing dated after Aug 26, 2026 (so the record reaches past that day).
(Round 5, Nov 24, 2026: the second record added; before-copy check_filing_feed.before-round5-20261124.py.)
(Round 9, Nov 25, 2026: a third record, research/primary/cn-ga31-official-sec-submissions-20261125, fetched Nov 25, 2026 at
06:49 UTC, which the argument now cites; the page says it too lists no report for that quarter, with filings up to Nov 23;
before-copy check_filing_feed.before-round9-20261125.py.)
(Round 10, Nov 25, 2026: the argument now cites the reading of the same record at 10:45 UTC, research/primary/
cn-ga31-official-sec-submissions-20261125-b (core row AP10-28 to -31; its body has the same sha256 as the 06:49 reading), and so does
the page; the third record read here is that one. Before-copy check_filing_feed.before-round10-20261125.py.)
(Round 10b, Nov 25, 2026: the argument's core batch 12 cites the reading of 22:16 UTC, research/primary/
cn-ga31-official-sec-submissions-20261125-c, and so does the page; the third record read here is that one. Before-copy
check_filing_feed.before-round10b-20261125.py.)
"""
import json, sys
from pathlib import Path

PRIMARY = Path(__file__).resolve().parents[5] / 'research' / 'primary'
ok = True
for SID, said_newest in (('cn-le05-sec-submissions-20261123', None), ('cn-ga06-sec-submissions-20261124', '2026-11-23'),
                          ('cn-ga31-official-sec-submissions-20261125-c', '2026-11-23')):    # round 10b: the record of Nov 25, 2026, 22:16 UTC, which the argument cites
    d = PRIMARY / SID
    rec = json.loads((d / 'body.json').read_text(encoding='utf-8'))['filings']['recent']
    fetched = json.loads((d / 'meta.json').read_text())['fetched_utc']
    rows = list(zip(rec['form'], rec['filingDate'], rec['reportDate']))
    periodic = sorted((f, fd, rd) for f, fd, rd in rows if f in ('10-Q', '10-K'))
    q = sorted((fd, rd) for f, fd, rd in rows if f == '10-Q')
    newest = max(fd for _, fd, _ in rows)
    print(f'{SID}: saved {fetched}; {len(rows)} filings in the record, the newest dated {newest}; {len(q)} quarterly reports (10-Q)')
    print(f'newest quarterly report: filed {q[-1][0]} for the period ended {q[-1][1]}')
    if ('2026-08-26', '2026-07-26') not in q: print('CONTROL FAILED: the report filed 2026-08-26 is not in the record'); ok = False
    if not newest > '2026-08-26': print('CONTROL FAILED: the record does not reach past 2026-08-26'); ok = False
    if said_newest and newest != said_newest: print(f'CHANGE THE TEXT: the page says filings up to {said_newest}; the record\'s newest is {newest}'); ok = False
    late = [(f, fd, rd) for f, fd, rd in periodic if rd >= '2026-10-25' or (f == '10-Q' and fd > '2026-08-26')]
    if late: print(f'CHANGE THE TEXT: a report for the quarter ended Oct 25, 2026, or a later one, is in the record: {late}'); ok = False
    if q[-1] != ('2026-08-26', '2026-07-26'): print('CHANGE THE TEXT: the newest quarterly report is not the one the page names'); ok = False
print('result: no report for a period ending on or after 2026-10-25 is in any of the three records; both controls hold in each' if ok else 'result: FAILED')
sys.exit(0 if ok else 1)
