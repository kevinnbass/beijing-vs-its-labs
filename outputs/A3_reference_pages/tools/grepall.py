#!/usr/bin/env python3
"""Search a named set of saved copies for a pattern and print each place with the words around it. A reading aid.

Run: python3 -I tools/grepall.py <regular expression> [width] [max hits per page] [extra id ...]
The set: every id in the argument's references file and in the figure's data file, plus any ids given.
It reads only those folders under research/primary (no walk of the drive) and writes nothing.
"""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ctx

PROJ = Path('.')


def ids():
    out = []
    for ln in (PROJ / 'argument' / 'argument_refs.tsv').read_text(encoding='utf-8').splitlines():
        if ln.strip() and not ln.startswith('#'): out.append(ln.split('\t')[0])
    for ln in (PROJ / 'figure' / 'figure_data.txt').read_text(encoding='utf-8').splitlines():
        if ln.startswith('@ '): out.append(ln.split()[-1])
        elif ln.startswith('! '): out.append(ln[2:].split('|')[0].strip())
    return list(dict.fromkeys(out))


def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    pat = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 90
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    todo = list(dict.fromkeys(ids() + sys.argv[4:]))
    for sid in todo:
        if not sid.startswith('clip-') and not (ctx.P / sid).is_dir(): print(f'## {sid}: no saved copy'); continue
        t = ctx.text(sid); n = 0
        for m in re.finditer(pat, t, flags=re.I):
            n += 1
            if n <= mx: print(f'{sid} [{n}] ...{t[max(0, m.start() - w):m.end() + w]}...')
    print(f'searched {len(todo)} saved copies for /{pat}/')


if __name__ == '__main__':
    main()
