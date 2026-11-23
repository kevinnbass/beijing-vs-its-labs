#!/usr/bin/env python3
"""Check this repository from its own files.

Run: python3 -I scripts/check_repo.py
1. sources.csv: every text file it lists is present with the sha256 it gives, and no text file is present that it
   does not list.
2. Quotations: every quotation of the argument (argument/argument_base.txt, argument/short_base.txt) and of the
   figure's data (figure/figure_data.txt) whose source text is held here is looked for in that text, the way the
   builders do it (scripts/cn_srclib.py: spacing, letter case and the style of quote marks are ignored).
   A quotation whose source text is not held here is counted as not checkable here: sources.csv gives the address
   of the page and the hash of the copy that was checked.
3. Controls: a planted false quotation must be rejected and a known true one found, so the check can fail and pass.
Exit 0 only if nothing held here fails.
"""
import csv, hashlib, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cn_srclib as L
import cn_argument_build as B

ROOT = Path(__file__).resolve().parents[1]
TEXTS = ('text.txt', 'body_text.txt')


def held(sid):
    return any((L.P / sid / n).is_file() for n in TEXTS)


def main():
    bad, found, skipped, sources = [], 0, 0, set()
    rows = list(csv.DictReader(open(ROOT / 'sources.csv', encoding='utf-8', newline='')))
    listed = set()
    for r in rows:
        for name, col in (('text.txt', 'text_sha256'), ('body_text.txt', 'body_text_sha256')):
            f = L.P / r['saved_id'] / name
            if r[col]:
                listed.add(f)
                if not f.is_file(): bad.append(f'sources.csv lists {f.relative_to(ROOT)} but it is not here')
                elif hashlib.sha256(f.read_bytes()).hexdigest() != r[col]: bad.append(f'{f.relative_to(ROOT)}: sha256 differs from sources.csv')
    for f in sorted(L.P.glob('*/*.txt')):
        if f not in listed: bad.append(f'{f.relative_to(ROOT)} is here but sources.csv does not list it')
    n_texts = len(listed)

    def look(where, words, ids):
        nonlocal found, skipped
        have = [i for i in ids if held(i)]
        hit = [i for i in have if L.has(words, i)]
        if hit: found += 1; sources.update(hit[:1])
        elif have and len(have) == len(ids): bad.append(f'{where}: NOT FOUND in {", ".join(have)}: {words[:80]}')
        else: skipped += 1

    for name in ('argument/argument_base.txt', 'argument/short_base.txt'):
        for n, ln in enumerate((ROOT / name).read_text(encoding='utf-8').splitlines(), 1):
            if ln.startswith('!!'):
                sid, words = [x.strip() for x in ln[2:].split('|', 1)]
                look(f'{name} line {n}', words, [sid]); continue
            ids = B.CITE.findall(ln)
            for q in B.QUOTE.findall(ln):
                for part in [p for p in q.split(' ... ') if p.strip()]:
                    if ids: look(f'{name} line {n}', part, ids)
    cur = None
    for n, ln in enumerate((ROOT / 'figure' / 'figure_data.txt').read_text(encoding='utf-8').splitlines(), 1):
        if ln.startswith('@ '): cur = ln.split()[-1]
        elif ln.startswith('Q ') and cur: look(f'figure/figure_data.txt line {n}', ln[2:].strip(), [cur])
        elif ln.startswith('! '):
            sid, words = ln[2:].split(' | ', 1); look(f'figure/figure_data.txt line {n}', words.strip(), [sid.strip()])
    ok_false = not L.has('Beijing has published a ban on the purchase of Nvidia chips', 'cn-policy-micron-decision')
    ok_true = L.has('应停止采购美光公司产品', 'cn-policy-micron-decision')
    if not (ok_false and ok_true): bad.append('controls: the planted false quotation was found, or the known true one was not')
    for b in bad: print(b)
    print(f'{n_texts} text files match sources.csv; quotations and hidden statements looked for in the texts held here: {found} found in {len(sources)} sources, '
          f'{len([b for b in bad if "NOT FOUND" in b])} not found; {skipped} not checkable here (source text not included); controls {"behave" if ok_false and ok_true else "FAILED"}')
    sys.exit(1 if bad or found == 0 else 0)


if __name__ == '__main__':
    main()
