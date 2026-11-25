#!/usr/bin/env python3
# Repository copy. Changed from the working copy: paths only (README.md, "Files changed from the working copies").
"""Build one checked document of the China chip-policy project from a base text file.

Run: python3 -I scripts/cn_doc_build.py <path/name_base.txt> [--refs extra_refs.tsv] [--title "Two To Four Words"]
                                         [--eyebrow "small line above the headline"] [--md-only]
Writes <path/name>.md and <path/name>.html beside the base file. Nothing is written unless every check passes.

The base file uses the same small markup as the argument (see scripts/cn_argument_build.py):
  "# " title, "@deck" one line under it, "@note" small header lines, "## " section, a line that is only **bold** is a
  sub-heading, "N. " a numbered point, "- " a list item, "| a | b |" a table row (first row is the header), "**bold**".
  A saved id in square brackets, like [cn-clips-alibaba-20f], becomes a numbered reference.
  A line "!! id | words" is not printed: it checks that the words stand in that saved copy (for a statement made
  without quoting). Check strings must be at least 6 characters long once spaces are removed.
Checks: every id cited is in a references file and has a saved copy; every string between straight double quotes on a
line stands in the saved copy of an id cited on that same line; every "!!" line holds; a planted false quotation fails.
So: put between straight double quotes ONLY a source's exact words, and cite its id on the same line. Your own English
for Chinese words goes in round brackets without quote marks.

References: argument/argument_refs.tsv (the argument's sources) plus the file given with --refs
(same columns: id <TAB> kind <TAB> label <TAB> address; kinds DOC OFF FIL REC PRESS COUNT CLIP). Two machine
transcripts can be cited: [clip-luckey] and [clip-pottinger] (not checked by ear: say so where you quote them).
"""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cn_argument_build as B

L = B.L


def main():
    args = sys.argv[1:]
    opt = {}
    for k in ('--refs', '--title', '--eyebrow'):
        if k in args:
            i = args.index(k); opt[k] = args[i + 1]; del args[i:i + 2]
    md_only = '--md-only' in args
    args = [a for a in args if not a.startswith('--')]
    if len(args) != 1: sys.exit(__doc__)
    base = Path(args[0]).resolve()
    stem = re.sub(r'(_base)?\.txt$', '', base.name)
    B.LINK_FILES = False
    B.load_clip()
    refs = B.load_refs()
    refs.setdefault('clip-pottinger', {'kind': 'CLIP', 'label': 'Matt Pottinger with Christiane Amanpour, in a clip of 2 minutes 22 seconds posted on X by @amanpour, Nov 18, 2026. Words from a speech program\'s transcript of the clip (the project’s transcript file, held back: see HELD_BACK.md); nobody has checked them by ear', 'addr': 'https://x.com/amanpour/status/2123118808290189692'})
    if '--refs' in opt:
        for ln in Path(opt['--refs']).read_text(encoding='utf-8').splitlines():
            if not ln.strip() or ln.startswith('#'): continue
            c = ln.split('\t')
            if len(c) < 3 or c[1] not in B.KIND: sys.exit(f'extra references file: bad line: {ln[:80]}')
            refs[c[0]] = {'kind': c[1], 'label': c[2].strip(), 'addr': c[3].strip() if len(c) > 3 else ''}
    lines = base.read_text(encoding='utf-8').splitlines()
    bad, order, nq, nh = B.check(lines, refs, need_all=False)
    for sid in order:
        if sid in refs and refs[sid]['addr'] != '-' and not B.address(sid, refs[sid]): bad.append(f'{sid}: no address (give one in the references file, or "-" with the reason in the label)')
    if not B.controls(): bad.append('controls: the planted false quotation was found, or the known true one was not')
    if bad:
        print('\n'.join(bad)); print(f'\nNOT WRITTEN: {len(bad)} problem(s)'); sys.exit(1)
    num = {sid: n for n, sid in enumerate(order, 1)}
    solid = sum(1 for sid in order if refs[sid]['kind'] in B.SOLID)
    tail = (f'Build check: {nq} quotations and {nh} further statements were looked for in the saved copies of {len(order)} sources and all were found; '
            f'a planted false quotation was rejected. {solid} sources are documents, filings or named people on the record; {len(order) - solid} are press reports citing unnamed people, counts or machine transcripts. '
            'A quotation that is found shows what the source says, not that it is true.') if order else ''
    bl = B.blocks(lines)
    use_refs = refs if order else None
    (base.parent / f'{stem}.md').write_text(B.to_md(bl, num, use_refs, tail), encoding='utf-8')
    if not md_only:
        (base.parent / f'{stem}.html').write_text(B.to_html(bl, num, use_refs, tail, opt.get('--title', 'Chip Policy Note'), opt.get('--eyebrow', 'China chip policy'), ''), encoding='utf-8')
    words = len(B.CITE.sub('', ' '.join(ln for ln in lines if ln.strip() and not ln.startswith(('!!', '@')))).split())
    print(f'{stem}: about {words} words; {len(order)} sources ({solid} on the record); quotations checked {nq}, hidden statements {nh}, all found; control rejected')


if __name__ == '__main__':
    main()
