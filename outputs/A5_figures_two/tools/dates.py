"""Reading aid: which written forms of a date stand in a saved page (nothing is written).
Run: python3 -I tools/dates.py <saved id>=<YYYY-MM-DD> ...
"""
import re, sys, html, unicodedata
from datetime import date
from pathlib import Path
sys.path.insert(0, 'scripts')
import cn_srclib as L
MONL = ['January','February','March','April','May','June','July','August','September','October','November','December']
MONS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def raw(sid):
    d = L.P / sid; t = ''
    for n in ('text.txt', 'text.article.txt', 'transcription.txt'):
        if (d / n).exists(): t += ' ' + (d / n).read_text(encoding='utf-8', errors='replace')
    for b in d.glob('body*'):
        if b.suffix.lower() in ('.html', '.htm', '.json', '.txt') and b.stat().st_size < 12_000_000:
            r = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', b.read_text(encoding='utf-8', errors='replace'))
            t += ' ' + html.unescape(re.sub(r'(?s)<[^>]+>', ' ', r))
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', t))
for arg in sys.argv[1:]:
    sid, ds = arg.split('=')
    d = date.fromisoformat(ds); y, m, dd = d.year, d.month, d.day
    forms = [f'{y}-{m:02d}-{dd:02d}', f'{y}/{m:02d}/{dd:02d}', f'{y}年{m}月{dd}日', f'{y}年{m:02d}月{dd:02d}日', f'{m}月{dd}日', f'{MONL[m-1]} {dd}, {y}', f'{MONS[m-1]} {dd}, {y}',
             f'{MONL[m-1]} {dd}', f'{MONS[m-1]} {dd}', f'{MONS[m-1].upper()} {dd} {y}', f'{dd} {MONL[m-1]} {y}', f'{m:02d}/{dd:02d}/{y}', f'{dd:02d}/{m:02d}/{y}', f'{y}.{m:02d}.{dd:02d}', f'Sept {dd}', f'{y}{m:02d}{dd:02d}']
    t = raw(sid)
    print(f'== {sid} {ds} (page {len(t)} chars)')
    for f in forms:
        hits = [x.start() for x in re.finditer(re.escape(f), t)]
        if hits:
            i = hits[0]
            print(f'   {len(hits):3d} x "{f}": ...{t[max(0, i - 45): i + len(f) + 45]}...')
