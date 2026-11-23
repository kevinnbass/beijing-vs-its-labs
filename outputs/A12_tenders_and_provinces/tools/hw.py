#!/usr/bin/env python3
"""Show hardware names in saved notices. Run: python3 -I tools/hw.py <id> [...]   Read-only."""
import html, json, re, sys
from pathlib import Path
P = Path('research/primary')
NV = r'(?i)英伟达|nvidia|\bH100|\bH200|\bH20\b|\bH800|\bA100|\bA800|\bL40S?|RTX ?\d{4}D?|RTX ?PRO|\bA6000|\bV100|\bT4\b|Tesla|GeForce|\b[45]090D?\b|\bGB200|\bB200'
CN = r'(?i)昇腾|ascend|Atlas ?\d{3}|寒武纪|cambricon|MLU ?\d{3}|思元|海光|hygon|DCU|昆仑芯|kunlun|鲲鹏|kunpeng|飞腾|摩尔线程|沐曦|壁仞|天数智芯|燧原|景嘉微|平头哥|含光|910B|910C|国产'
for sid in sys.argv[1:]:
    d = P / sid
    try: m = json.loads((d / 'meta.json').read_text())
    except Exception: m = {}
    t = ''
    if (d / 'text.txt').exists(): t += (d / 'text.txt').read_text(encoding='utf-8', errors='replace')
    for b in d.glob('body*'):
        if b.suffix.lower() in ('.html', '.htm', '.json', '.txt'):
            raw = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', b.read_text(encoding='utf-8', errors='replace'))
            t += ' ' + html.unescape(re.sub(r'(?s)<[^>]+>', ' ', raw))
    t = re.sub(r'\s+', ' ', t)
    tm = re.search(r'TITLE: (.{0,80})', t)
    print(f'=== {sid} status={m.get("status")} chars={len(t)} | {tm.group(1) if tm else ""}')
    for name, rx in (('NV', NV), ('CN', CN)):
        hits = {}
        for mm in re.finditer(rx, t): hits[mm.group(0)] = hits.get(mm.group(0), 0) + 1
        print(f'    {name}:', ', '.join(f'{k}×{v}' for k, v in sorted(hits.items(), key=lambda x: -x[1])[:14]) or '-')
    dm = re.findall(r'20\d\d[年\-/.]\s?\d{1,2}[月\-/.]\s?\d{1,2}日?', t)
    print('    dates:', ', '.join(dict.fromkeys(dm).keys().__iter__().__class__ and list(dict.fromkeys(dm))[:6]))
