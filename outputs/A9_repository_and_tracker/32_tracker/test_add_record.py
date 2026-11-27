#!/usr/bin/env python3
"""Try add_record.py on a scratch copy of the tracker: false records must be refused, a true one taken.

Run: python3 -I test_add_record.py
It copies data/ into scratch_test/run-<UTC time>/data/ (a new folder each run; the real data is not touched) and runs:
  1. a FALSE record (words that are not in the saved page)            -> must be refused, files unchanged
  2. true words under a WRONG date (not written in the page)          -> must be refused, files unchanged
  3. a failure in the second figure-events lookup                     -> must restore the inputs and outputs
  4. a TRUE record (words, date and saved page agree)                 -> must be taken: one more record, one more log line
  5. the same true record again                                       -> must be refused as already there
Then it checks that the real data files did not change. Exit 0 only if all hold.
"""
import hashlib, shutil, subprocess, sys
from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import add_record  # noqa: E402

SID = 'cn-policy-firms-want-nvidia'          # Reuters, Sept 4, 2025, on TradingView: in the argument, not in the figure's records
TRUE = ['--date', '2025-09-04', '--row', 'CN', '--kind', 'press', '--id', SID,
        '--line', 'Chinese firms "still want Nvidia chips despite government pressure not to buy", in the words of the report\'s headline',
        '--source', 'Reuters, on TradingView',
        '--words', 'Chinese firms still want Nvidia chips despite government pressure not to buy, sources say']


def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()


def swap(args, key, value):
    out = list(args); out[out.index(key) + 1] = value; return out


def count(f): return sum(1 for ln in f.read_text(encoding='utf-8').splitlines() if ln.startswith('@ '))


def second_lookup_control(run, data, log):
    before = (data.read_bytes(), log.read_bytes())
    real_lookup = add_record.B.lane_labels
    calls = 0
    saw_writes = False
    failure = 'planted failure in the second figure-events lookup'

    def lookup():
        nonlocal calls, saw_writes
        calls += 1
        if calls == 2:
            saw_writes = data.read_bytes() != before[0] and log.read_bytes() != before[1]
            raise ValueError(failure)
        return real_lookup()

    argv = ['add_record.py', '--dir', str(run), *TRUE]
    output = StringIO()
    exit_code = 0
    with patch.object(add_record.B, 'lane_labels', side_effect=lookup), patch.object(sys, 'argv', argv), redirect_stdout(output):
        try:
            add_record.main()
        except SystemExit as exc:
            exit_code = exc.code
    restored = (data.read_bytes(), log.read_bytes()) == before
    outputs_absent = not any((run / name).exists() for name in ('tracker.html', 'quotes.tsv'))
    good = calls == 2 and saw_writes and restored and outputs_absent and exit_code == 1 and failure in output.getvalue()
    print(f'{"PASS" if good else "FAIL"}  3 second figure-events lookup: exit {exit_code}; '
          f'lookup calls {calls}; both inputs written before failure: {saw_writes}; restored: {restored}; outputs absent: {outputs_absent}')
    return good


def main():
    run = HERE / 'scratch_test' / ('run-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    (run / 'data').mkdir(parents=True, exist_ok=False)
    files = ('figure_data.txt', 'tracker_log.tsv', 'state_of_play.txt', 'house_licence_table.tsv')      # the last two since Nov 23, 2026 (round 4)
    for n in files: shutil.copyfile(HERE / 'data' / n, run / 'data' / n)
    real = {n: sha(HERE / 'data' / n) for n in files}
    d, g = run / 'data' / 'figure_data.txt', run / 'data' / 'tracker_log.tsv'
    n0, ok = count(d), True

    def step(name, args, want_exit, want_word, want_change):
        nonlocal ok
        before = (sha(d), sha(g))
        r = subprocess.run([sys.executable, '-I', str(HERE / 'add_record.py'), '--dir', str(run)] + args, capture_output=True, text=True)
        changed = (sha(d), sha(g)) != before
        good = r.returncode == want_exit and want_word in r.stdout and changed == want_change
        ok = ok and good
        first = (r.stdout.strip().splitlines() or ['(no output)'])[0]
        print(f'{"PASS" if good else "FAIL"}  {name}: exit {r.returncode} (wanted {want_exit}); files {"changed" if changed else "unchanged"} (wanted {"changed" if want_change else "unchanged"}); said: {first[:150]}')
        if not good: print(r.stdout[-1500:], r.stderr[-800:])

    step('1 false words', swap(TRUE, '--words', 'Beijing has published a ban on the purchase of Nvidia chips'), 1, 'REFUSED', False)
    step('2 true words, wrong date', swap(TRUE, '--date', '2025-08-01'), 1, 'REFUSED', False)
    ok = second_lookup_control(run, d, g) and ok
    step('4 true record', TRUE, 0, 'ADDED', True)
    n1 = count(d)
    last = g.read_text(encoding='utf-8').rstrip('\n').splitlines()[-1].split('\t')
    good = n1 == n0 + 1 and last[1] == 'addition' and last[2] == SID and last[3] == str(n1) and (run / 'tracker.html').is_file() and SID in (run / 'tracker.html').read_text(encoding='utf-8')
    ok = ok and good
    print(f'{"PASS" if good else "FAIL"}  4 after it: records {n0} -> {n1}; last log line: {last[0]} {last[1]} {last[2]} {last[3]}; the scratch page was rebuilt and holds the new record: {good}')
    step('5 the same record again', TRUE, 1, 'REFUSED', False)
    same = all(sha(HERE / 'data' / n) == h for n, h in real.items())
    ok = ok and same
    print(f'{"PASS" if same else "FAIL"}  the real data files are unchanged: {same}')
    print(f'scratch copy: {run}')
    print('ALL PASS' if ok else 'SOME FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
