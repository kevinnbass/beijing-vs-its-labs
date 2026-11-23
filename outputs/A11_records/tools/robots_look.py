"""Read robots.txt for the sample addresses given (one per line in a file) and say whether `*` and `Claude-User` may fetch each.
Run: python3 -I tools/robots_look.py tools/robots_samples.txt   -> writes robots_look.tsv beside the samples file, prints it.
A robots.txt answering 401/403 counts as disallow all; 404 as allow all (the standard's reading, as scripts/robots_check.py)."""
import sys, urllib.robotparser
from pathlib import Path
from urllib.parse import urlparse
import requests
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
src = Path(sys.argv[1]); out = []
cache = {}
for u in [x.strip() for x in src.read_text().splitlines() if x.strip() and not x.startswith('#')]:
    p = urlparse(u); base = f'{p.scheme}://{p.netloc}'
    if base not in cache:
        try:
            r = requests.get(base + '/robots.txt', headers={'User-Agent': UA}, timeout=(10, 20))
            cache[base] = (r.status_code, r.text)
        except Exception as e:
            cache[base] = (0, f'{type(e).__name__}')
    st, txt = cache[base]
    if st in (401, 403): res = {'*': False, 'Claude-User': False}
    elif st == 404: res = {'*': True, 'Claude-User': True}
    elif st == 200:
        rp = urllib.robotparser.RobotFileParser(); rp.parse(txt.splitlines())
        res = {a: rp.can_fetch(a, u) for a in ('*', 'Claude-User')}
    else: res = {'*': None, 'Claude-User': None}
    out.append(f"{p.netloc}\t{st}\t*={res['*']}\tClaude-User={res['Claude-User']}\t{u}")
(src.parent / 'robots_look.tsv').write_text('\n'.join(out) + '\n')
print('\n'.join(out))
