#!/usr/bin/env python3
"""Show where key words stand in saved copies. Run: python3 -I tools/kw.py <id> [<id> ...] [--kw a,b,c] [--w 70]
Reads every saved form of research/primary/<id> (text.txt and bodies without tags). Read-only."""
import html, json, re, sys
from pathlib import Path
P = Path('research/primary')
args = sys.argv[1:]
kws = ['国产', '自主可控', '安全可靠', '安全可控', '自主化']
w = 70
if '--kw' in args:
    i = args.index('--kw'); kws = args[i + 1].split(','); del args[i:i + 2]
if '--w' in args:
    i = args.index('--w'); w = int(args[i + 1]); del args[i:i + 2]
for sid in args:
    d = P / sid
    try: m = json.loads((d / 'meta.json').read_text())
    except Exception: m = {}
    t = ''
    for n in ('text.txt',):
        if (d / n).exists(): t += ' ' + (d / n).read_text(encoding='utf-8', errors='replace')
    for b in d.glob('body*'):
        if b.suffix.lower() in ('.html', '.htm', '.json', '.txt'):
            raw = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', b.read_text(encoding='utf-8', errors='replace'))
            t += ' ' + html.unescape(re.sub(r'(?s)<[^>]+>', ' ', raw))
    t = re.sub(r'\s+', '', t)
    tm = re.search(r'TITLE:(.{0,90})', t)
    print(f'=== {sid} status={m.get("status")} chars={len(t)} url={m.get("url")}')
    print('    counts:', ' '.join(f'{k}={t.count(k)}' for k in kws), f'%={t.count("%") + t.count("％")}')
    seen = set()
    for k in kws:
        for mm in re.finditer(re.escape(k), t):
            s = max(0, mm.start() - w); e = min(len(t), mm.end() + w)
            seg = t[s:e]
            if '%' in seg or '％' in seg or '以上' in seg or '占比' in seg or '比例' in seg:
                key = (s // 40)
                if key in seen: continue
                seen.add(key)
                print(f'    [{k}] …{seg}…')
