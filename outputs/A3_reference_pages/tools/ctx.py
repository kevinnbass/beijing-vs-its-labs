#!/usr/bin/env python3
"""Print the places where a pattern stands in a saved copy, with the words around it. A reading aid; it writes nothing.

Run: python3 -I tools/ctx.py <saved id> <regular expression> [width] [max hits]
The text read is the same one the checkers read (text files, then page bodies with tags removed), with runs of
spaces closed but nothing else changed, so what is printed can be copied as a quotation.
"""
import html, re, sys, unicodedata
from pathlib import Path

P = Path('research/primary')


def text(sid):
    d = P / sid; t = ''
    if sid.startswith('clip-'):
        return Path('transcripts_two_clips.md').read_text(encoding='utf-8')
    for n in ('text.txt', 'text.article.txt', 'transcription.txt'):
        if (d / n).exists(): t += '\n' + (d / n).read_text(encoding='utf-8', errors='replace')
    for b in sorted(d.glob('body*')):
        if b.suffix.lower() in ('.html', '.htm', '.json', '.txt') and b.stat().st_size < 12_000_000:
            raw = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', b.read_text(encoding='utf-8', errors='replace'))
            t += '\n' + html.unescape(re.sub(r'(?s)<[^>]+>', ' ', raw))
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', t))


def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    sid, pat = sys.argv[1], sys.argv[2]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 160
    mx = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    if not sid.startswith('clip-') and not (P / sid).is_dir(): sys.exit(f'no saved copy named {sid}')
    t = text(sid); n = 0
    for m in re.finditer(pat, t, flags=re.I):
        n += 1
        if n > mx: continue
        print(f'[{n}] ...{t[max(0, m.start() - w):m.end() + w]}...')
    print(f'{sid}: {n} place(s) for /{pat}/ in {len(t):,} characters')


if __name__ == '__main__':
    main()
