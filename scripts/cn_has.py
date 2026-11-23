#!/usr/bin/env python3
# Repository copy. Changed from the working copy: paths only (README.md, "Files changed from the working copies").
"""Check quotations against saved copies, for figures and pages not built with cn_doc_build.py.

Run: python3 -I scripts/cn_has.py <quotes.tsv>
The file holds one line per quotation: saved id <TAB> the source's exact words (blank lines and # comments ignored).
Spacing and the style of quote marks are ignored. A string under 6 characters (spaces removed) is refused as too short.
Ids: any folder name under sources, or clip-luckey / clip-pottinger (the machine transcripts).
Prints each miss; exit 0 only if every line is found and the controls behave (a planted false line must fail).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cn_argument_build as B

L = B.L


def main():
    if len(sys.argv) != 2: sys.exit(__doc__)
    B.load_clip()
    n = miss = 0
    for k, ln in enumerate(Path(sys.argv[1]).read_text(encoding='utf-8').splitlines(), 1):
        if not ln.strip() or ln.startswith('#'): continue
        if '\t' not in ln: print(f'line {k}: no tab between id and words'); miss += 1; continue
        sid, q = [x.strip() for x in ln.split('\t', 1)]
        n += 1
        if not sid.startswith('clip-') and not (L.P / sid).is_dir(): print(f'line {k}: no saved copy named {sid}'); miss += 1
        elif len(L.squash(q)) < 6: print(f'line {k}: too short to check: {q}'); miss += 1
        elif not L.has(q, sid): print(f'line {k}: NOT FOUND in {sid}: {q[:100]}'); miss += 1
    ok = B.controls()
    print(f'{n} quotations checked, {n - miss} found, {miss} not found; controls {"behave" if ok else "FAILED"}')
    sys.exit(0 if (miss == 0 and ok and n > 0) else 1)


if __name__ == '__main__':
    main()
