#!/usr/bin/env python3
# Repository copy. Unchanged from the working copy but for this line. It reads a working folder that is not part of this repository (README.md).
"""Verify what the builders left under research/cn_chip_policy_20261120/outputs/ (reads only; writes VERIFY.tsv there).

Run: python3 -I scripts/cn_outputs_verify.py [folder-name ...]        (no names: every folder in STATUS.tsv)
For each builder's folder it reports:
  DONE.md        present or not
  base files     every *_base.txt checked again as scripts/cn_doc_build.py checks it (quotations in the saved copies),
                 with the references file plus any *refs*.tsv beside the base file; nothing is rebuilt
  quotes.tsv     every such file checked again as scripts/cn_has.py checks it
  looks          for every .html, .png, .jpg, .webp and .svg that is not inside a folder named frames*, stills* or tmp*:
                 whether scripts/render_and_look.py holds a recorded look at exactly the present bytes
                 (LOOKED), only at other bytes (STALE), or none (NONE)
Exit 0 only if every folder asked for has DONE.md, no failing base file and no failing quotes file.
A missing look is listed, not counted as a failure: some files are parts of a page that was looked at whole.
"""
import hashlib, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cn_argument_build as B

L = B.L
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research' / 'cn_chip_policy_20261120' / 'outputs'
LOOKS = ROOT / 'research' / 'looks'
SKIP_DIR = re.compile(r'^(frames|stills|tmp|scratch|node_modules|__pycache__)', re.I)


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def look_index():
    """file path -> list of (key recorded, deps, looked?) from every LOOK.json."""
    idx = {}
    for lj in LOOKS.glob('*/run-*/LOOK.json'):
        try: r = json.loads(lj.read_text())
        except Exception: continue
        if str(OUT) not in str(r.get('file', '')): continue
        idx.setdefault(r['file'], []).append((r.get('key_sha256'), r.get('with', []), bool(r.get('looked'))))
    return idx


def look_state(f, idx):
    recs = idx.get(str(f))
    if not recs: return 'NONE'
    fs = sha(f)
    for key, deps, looked in recs:
        if not looked: continue
        h = hashlib.sha256(); h.update(bytes.fromhex(fs)); ok = True
        for d in deps:
            if not Path(d).is_file(): ok = False; break
            h.update(bytes.fromhex(sha(d)))
        if ok and h.hexdigest() == key: return 'LOOKED'
    return 'STALE'


def refs_for(base):
    refs = B.load_refs()
    refs.setdefault('clip-pottinger', {'kind': 'CLIP', 'label': 'machine transcript', 'addr': '-'})
    for x in sorted(set(base.parent.glob('*refs*.tsv')) | set(base.parent.parent.glob('*refs*.tsv'))):      # beside the base file, or one folder up
        for ln in x.read_text(encoding='utf-8').splitlines():
            if not ln.strip() or ln.startswith('#'): continue
            c = ln.split('\t')
            if len(c) >= 3 and c[1] in B.KIND: refs[c[0]] = {'kind': c[1], 'label': c[2].strip(), 'addr': c[3].strip() if len(c) > 3 else ''}
    return refs


def check_quotes(q):
    n = miss = 0
    for ln in q.read_text(encoding='utf-8').splitlines():
        if not ln.strip() or ln.startswith('#') or '\t' not in ln: continue
        sid, words = [x.strip() for x in ln.split('\t', 1)]
        n += 1
        if (not sid.startswith('clip-') and not (L.P / sid).is_dir()) or len(L.squash(words)) < 6 or not L.has(words, sid): miss += 1
    return n, miss


def main():
    B.load_clip()
    if not B.controls(): sys.exit('controls failed: the checker cannot be trusted')
    rows = [ln.split('\t') for ln in (OUT / 'STATUS.tsv').read_text(encoding='utf-8').splitlines()[1:] if ln.strip()]
    folders = sorted({r[2] for r in rows if not r[2].startswith('(')})
    want = [a for a in sys.argv[1:] if not a.startswith('--')] or folders
    idx = look_index()
    out, fail = ['folder\tDONE.md\tbase files (ok/all)\tquotations in base files\tquotes.tsv files (ok/all)\tquotations in quotes.tsv\tpages and images LOOKED\tSTALE\tNONE'], 0
    for name in want:
        d = OUT / name
        if not d.is_dir():
            print(f'{name}: NO FOLDER'); fail += 1; out.append(f'{name}\tno folder'); continue
        done = (d / 'DONE.md').is_file()
        bases = [p for p in sorted(d.rglob('*_base.txt')) if not any(SKIP_DIR.match(x) for x in p.relative_to(d).parts[:-1])]
        b_ok = b_q = 0; problems = []
        for b in bases:
            bad, order, nq, nh = B.check(b.read_text(encoding='utf-8').splitlines(), refs_for(b), need_all=False)
            b_q += nq + nh
            if bad: problems.append(f'  base FAILS {b.relative_to(OUT)}: {len(bad)} problem(s), first: {bad[0][:150]}')
            else: b_ok += 1
        qs = [p for p in sorted(d.rglob('quotes*.tsv')) if not any(SKIP_DIR.match(x) for x in p.relative_to(d).parts[:-1])]
        q_ok = q_n = 0
        for q in qs:
            n, miss = check_quotes(q); q_n += n
            if miss or n == 0: problems.append(f'  quotes FAIL {q.relative_to(OUT)}: {miss} of {n} not found' if n else f'  quotes EMPTY {q.relative_to(OUT)}')
            else: q_ok += 1
        st = {'LOOKED': [], 'STALE': [], 'NONE': []}
        for f in sorted(d.rglob('*')):
            if f.is_file() and f.suffix.lower() in ('.html', '.png', '.jpg', '.jpeg', '.webp', '.svg') and not any(SKIP_DIR.match(x) for x in f.relative_to(d).parts[:-1]):
                st[look_state(f, idx)].append(f)
        bad_here = (not done) or b_ok != len(bases) or q_ok != len(qs)
        fail += bad_here
        print(f'{name}: DONE.md {"yes" if done else "MISSING"} | base files {b_ok}/{len(bases)} ok ({b_q} quotations and statements) | quotes.tsv {q_ok}/{len(qs)} ok ({q_n} quotations) | looks: {len(st["LOOKED"])} looked, {len(st["STALE"])} stale, {len(st["NONE"])} none')
        for p in problems: print(p)
        for f in st['STALE']: print(f'  STALE look: {f.relative_to(OUT)}')
        for f in st['NONE']: print(f'  no look:    {f.relative_to(OUT)}')
        out.append(f'{name}\t{"yes" if done else "MISSING"}\t{b_ok}/{len(bases)}\t{b_q}\t{q_ok}/{len(qs)}\t{q_n}\t{len(st["LOOKED"])}\t{len(st["STALE"])}\t{len(st["NONE"])}')
    (OUT / 'VERIFY.tsv').write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'\n{len(want)} folder(s) checked; {fail} with something missing or failing')
    sys.exit(1 if fail else 0)


if __name__ == '__main__':
    main()
