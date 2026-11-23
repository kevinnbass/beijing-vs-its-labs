"""Show the words around a phrase in a saved page (reading aid for the builder; nothing is written).
Run: python3 -I tools/ctx.py <saved id> <phrase> [width]
"""
import html, re, sys, unicodedata
from pathlib import Path
P = Path('research/primary')
sid, phrase = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 300
d = P / sid; t = ''
for n in ('text.txt', 'text.article.txt', 'transcription.txt'):
    if (d / n).exists(): t += ' ' + (d / n).read_text(encoding='utf-8', errors='replace')
if phrase not in t:
    for b in d.glob('body*'):
        if b.suffix.lower() in ('.html', '.htm', '.json', '.txt') and b.stat().st_size < 12_000_000:
            raw = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', b.read_text(encoding='utf-8', errors='replace'))
            t += ' ' + html.unescape(re.sub(r'(?s)<[^>]+>', ' ', raw))
t = re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', t))
hits = [m.start() for m in re.finditer(re.escape(phrase), t)]
print(f'{sid}: {len(hits)} place(s) for "{phrase}"; page length {len(t)}')
for i in hits[:int(sys.argv[4]) if len(sys.argv) > 4 else 1]:
    print('...' + t[max(0, i - w): i + len(phrase) + w] + '...\n')
