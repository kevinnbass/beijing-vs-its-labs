#!/usr/bin/env python3
"""Add one dated record to the tracker, log it and rebuild the page.

Run (in this folder), with every value in single quotes:
  python3 -I add_record.py --date 2026-12-01 --row BH --kind press --id <saved id> \\
      --line '<our line, one sentence>' --source '<the source as shown>' --words '<the exact words of the saved page>'
Optional:
  --english '<our English for Chinese words>'   shown in round brackets after the words; no quote marks in it
  --address '<the page address>'                only where the saved copy's own address is cut short or missing
  --label 'Summer 2025'                         shown instead of the date (the date still places the record)
  --date-not-in-page '<reason>'                 needed when the date is not written in the saved page, or with --label
  --dir DIR                                     work on another copy of the tracker (DIR/data/...), for a trial

  --row   BH Beijing holds Nvidia back | BL Beijing lets Nvidia in | CN the companies reach for Nvidia |
          CH the companies turn to home-made chips
  --kind  doc a government document or an official on the record | rec a company on the record |
          press a press report citing unnamed people
  --id    the folder name of the saved page under research/primary

The record is REFUSED, and nothing is changed, when:
  - the saved copy does not exist, or the words are not in it (spacing and the style of quote marks are ignored);
  - words between straight double quotes in our line are not in the saved copy, or a number in our line is not;
  - the date is not written in the readable text of the saved page and no reason is given;
  - the same words from the same page already stand in the same row;
  - the planted false quotation is found (the check itself is broken).
When it is accepted the command appends the record to data/figure_data.txt, appends a dated line to
data/tracker_log.tsv (today's date in UTC, read from the clock) and runs build.py. If the build fails, both files
are put back as they were.
"""
import argparse, sys
from datetime import date, datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as B   # noqa: E402

L = B.L


def refuse(why):
    print('REFUSED: ' + why)
    print('Nothing was changed.')
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description='Add one dated record to the tracker.', allow_abbrev=False)
    for k in ('date', 'row', 'kind', 'id', 'line', 'source', 'words'): ap.add_argument('--' + k, required=True)
    ap.add_argument('--english', default=''); ap.add_argument('--address', default=''); ap.add_argument('--label', default='')
    ap.add_argument('--date-not-in-page', dest='reason', default=''); ap.add_argument('--dir', default=str(HERE))
    a = ap.parse_args()
    folder = Path(a.dir).resolve()
    data, logf = folder / 'data' / 'figure_data.txt', folder / 'data' / 'tracker_log.tsv'
    for f in (data, logf):
        if not f.is_file(): refuse(f'not found: {f}')
    for k in ('line', 'source', 'words', 'english', 'address', 'label', 'reason'):
        v = getattr(a, k)
        if '\t' in v or '\n' in v: refuse(f'--{k} holds a tab or a line break')
        setattr(a, k, v.strip())
    if a.row not in B.LANES: refuse(f'--row must be one of {", ".join(B.LANES)}')
    if a.kind not in B.KINDS: refuse(f'--kind must be one of {", ".join(B.KINDS)}')
    try: d = date.fromisoformat(a.date)
    except ValueError: refuse('--date must be written as YYYY-MM-DD')
    today = datetime.now(timezone.utc).date()
    if d > today: refuse(f'the date {d} is after today ({today}, UTC)')
    if not (L.P / a.id).is_dir(): refuse(f'no saved copy named {a.id} under research/primary')
    if a.address and not a.address.startswith('http'): refuse('--address must start with http')
    if L.has(*B.CONTROL): refuse('the planted false quotation was found: the check cannot fail, so no record is taken')
    rec = dict(lane=a.row, kind=a.kind, date=d, dl=a.label or None, sid=a.id, T=a.line, S=a.source, Q=a.words, E=a.english, U=a.address, C='', line=0)
    old_data, old_log = data.read_bytes(), logf.read_bytes()
    evs, checks = B.load_data(data)
    log = B.load_log(logf)
    if len(L.squash(a.words)) < 6: refuse('the words are too short to check (under 6 characters)')
    bad, _ = B.check_record(rec, checks)
    if bad: refuse('; '.join(bad))
    if any(e['sid'] == a.id and e['lane'] == a.row and L.squash(e['Q']) == L.squash(a.words) for e in evs):
        refuse('the same words from the same page already stand in this row')
    found = None if a.label else B.date_in_page(d, a.id)
    if not found and not a.reason:
        refuse(f'the date {B.fmt(d)} is not written in the readable text of the saved page {a.id}' + (' (a label is shown instead of the date)' if a.label else '') +
               '. Read the date in the page and correct it, or give --date-not-in-page with the reason.')
    if log and today < log[-1]['date']: refuse(f"today ({today}, UTC) is before the last log line ({log[-1]['date']})")
    block = ['', f'# added {today.isoformat()} by add_record.py',
             f"@ {a.row} {a.kind} {d.isoformat()} {a.label.replace(' ', '_') if a.label else '-'} {a.id}", f'T {a.line}', f'S {a.source}', f'Q {a.words}']
    if a.english: block.append(f'E {a.english}')
    if a.address: block.append(f'U {a.address}')
    who, what, _ = B.LANES[a.row]
    text = f'Added: {a.label or B.fmt(d)}, {who} {what}. {a.line.rstrip(".")}. Source: {a.source.rstrip(".")}.'
    if a.reason: text += f' The date is not written in the saved page: {a.reason.rstrip(".")}.'
    n = len(evs) + 1
    data.write_bytes(old_data.rstrip(b'\n') + b'\n' + '\n'.join(block).encode('utf-8') + b'\n')
    logf.write_bytes(old_log.rstrip(b'\n') + b'\n' + f'{today.isoformat()}\taddition\t{a.id}\t{n}\t{text}\t'.encode('utf-8') + b'\n')
    ok, lines = B.build(folder)
    if not ok:
        data.write_bytes(old_data); logf.write_bytes(old_log)
        print('\n'.join(x for x in lines if x))
        refuse('the rebuild failed with the new record; the data file and the log were put back as they were')
    print(f'ADDED: {a.label or B.fmt(d)} | {who} {what} | {a.id}')
    print(f'date in the page: {found or "not looked for (reason given)"}; records now {n}; log line written for {today.isoformat()}')
    print('\n'.join(x for x in lines if x))
    print('Now look at the page before calling it done (HOW_TO_UPDATE.md, step 3).')


if __name__ == '__main__':
    main()
