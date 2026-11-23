#!/usr/bin/env python3
"""Show where home-made words and percent signs stand in a saved page or a file. Run: python3 -I kw.py <id or path> [head N]
Reads only; prints the title lines, every place of a home-made word with 70 characters each side, and counts."""
import re, sys
from pathlib import Path
P = Path('research/primary')
WORDS = ['国产', '自主可控', '安全可控', '安全可靠', '自主化', '信创', '自主创新', '自主研发', '国芯']
a = sys.argv[1]
f = Path(a) if '/' in a else P / a / 'text.txt'
t = f.read_text(encoding='utf-8', errors='replace')
s = re.sub(r'\s+', '', t)
head = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == 'head' else 500
print('FILE', f, 'characters without spaces', len(s))
print('HEAD', s[:head])
for w in WORDS:
    hits = [m.start() for m in re.finditer(w, s)]
    print(f'-- {w}: {len(hits)}')
    for h in hits:
        print('   ', s[max(0, h - 70):h + len(w) + 90])
print('-- percent signs:', len(re.findall('[%％]', s)))
for m in re.finditer('[%％]', s):
    seg = s[max(0, m.start() - 60):m.end() + 5]
    if any(w in seg for w in WORDS): print('   NEAR', seg)
print('-- dates:', re.findall(r'20\d\d年\d+月\d+日', s)[:12])
