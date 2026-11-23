#!/usr/bin/env python3
"""Print the readable text of a saved page (body without tags), squeezed. Run: python3 -I tools/show.py <id> [start] [length]"""
import html, re, sys
from pathlib import Path
P = Path('research/primary')
sid = sys.argv[1]; start = int(sys.argv[2]) if len(sys.argv) > 2 else 0; n = int(sys.argv[3]) if len(sys.argv) > 3 else 2500
d = P / sid; t = ''
bodies = [b for b in d.glob('body*') if b.suffix.lower() in ('.html', '.htm', '.json', '.txt')]
if bodies:
    raw = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', bodies[0].read_text(encoding='utf-8', errors='replace'))
    t = html.unescape(re.sub(r'(?s)<[^>]+>', ' ', raw))
else:
    t = (d / 'text.txt').read_text(encoding='utf-8', errors='replace')
t = re.sub(r'\s+', ' ', t)
print(f'[{sid}] {len(t)} chars; showing {start}..{start + n}')
print(t[start:start + n])
