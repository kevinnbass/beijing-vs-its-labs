"""Round 10 (Nov 25, 2026): which numbered point of the argument holds given words, read from argument/argument_base.txt
by script, so a note never types a point number. points(anchor) -> sorted list of point numbers whose text (hidden '!!'
lines left out) holds the anchor; section(n) -> the text of section '## n.' (the numbers table is section 4);
open_list() -> the text under '## What this note leaves open'. Controls: point 1 holds Xi Jinping; an anchor that is in no
point gives []."""
import re
from pathlib import Path
ARG = Path(__file__).resolve().parents[3] / 'argument' / 'argument_base.txt'
_L = ARG.read_text(encoding='utf-8').splitlines()
_P, _S, cur, sec = {}, {}, None, None
for ln in _L:
    if ln.startswith('## '):
        cur = None; m = re.match(r'## (\d+)\.', ln); sec = int(m.group(1)) if m else ln[3:].strip()
    m = re.match(r'^(\d{1,2})\. \*\*', ln)
    if m: cur = int(m.group(1))
    if ln.startswith('!!'): continue
    if cur is not None: _P[cur] = _P.get(cur, '') + '\n' + ln
    if sec is not None: _S[sec] = _S.get(sec, '') + '\n' + ln
def points(anchor): return sorted(n for n, t in _P.items() if anchor in t)
def one(anchor):
    p = points(anchor)
    if len(p) != 1: raise SystemExit(f'arg_points: {anchor[:60]!r} is in points {p}, not in exactly one')
    return p[0]
def section(n): return _S.get(n, '')
def open_list(): return _S.get('What this note leaves open', '')
if 1 not in points('Xi Jinping') or points('this sentence is in no point of the argument'): raise SystemExit('arg_points: control failed')
if len(_P) != max(_P) or max(_P) < 20: raise SystemExit(f'arg_points: points read {sorted(_P)}')
