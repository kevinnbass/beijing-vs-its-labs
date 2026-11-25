"""Control for the builder's mirror check (cn_figure_build.py, mirror_check): show that the comparison is not empty and can fail.

Run: python3 -I check_mirror_control.py
It reads the core's builder (english_originals/cn_figure_build.py) and this folder's builder as text, never runs them.
1. For each panel function it prints how many saved ids each builder names (the comparison must not be of two empty lists).
2. It changes one saved id, and then one voucher row's label, in a copy of this folder's builder held in memory, and shows that
   the same comparison then reports a difference. Exit 0 only if the true builders agree and both altered copies differ.
"""
import ast, re, sys
from pathlib import Path

F = Path(__file__).resolve().parent
ID = re.compile(r"""['"]((?:cn|man|ms)-[a-z0-9-]+)['"]""")
RATE = re.compile(r"'([AB]\d+)': \('[^']*', (?:'\w+ \d{4}'|\(\d{4}, \d+\)), '((?:cn|man|ms)-[a-z0-9-]+)'")      # a voucher row: its label in the tables and the saved copy it links (voucher round 3: the rates are no longer typed in either builder)
FNS = ('bars', 'revenue', 'provinces', 'paper', 'vouchers', 'bodies')


def funcs(src):
    tree = ast.parse(src)
    return {n.name: ast.get_source_segment(src, n) for n in tree.body if isinstance(n, ast.FunctionDef)}


def differs(en, zh):
    return [fn for fn in FNS if ID.findall(en[fn]) != ID.findall(zh[fn])] + (['voucher rows'] if RATE.findall(en['vouchers']) != RATE.findall(zh['vouchers']) else [])


en_src, zh_src = (F / 'english_originals' / 'cn_figure_build.py').read_text(encoding='utf-8'), (F / 'cn_figure_build.py').read_text(encoding='utf-8')
en, zh = funcs(en_src), funcs(zh_src)
for fn in FNS: print(f'{fn}: core names {len(ID.findall(en[fn]))} saved ids, this builder {len(ID.findall(zh[fn]))}')
print(f'voucher rows (label and linked copy): core {len(RATE.findall(en["vouchers"]))}, this builder {len(RATE.findall(zh["vouchers"]))}')
ok = all(len(ID.findall(en[fn])) > 0 for fn in FNS) and len(RATE.findall(zh['vouchers'])) > 0 and differs(en, zh) == []
print('true builders:', 'agree' if differs(en, zh) == [] else f'DIFFER in {differs(en, zh)}')
a = zh_src.replace("'cn-policy-wang-nvidia'", "'cn-policy-he-welcomes'", 1); assert a != zh_src
b = zh_src.replace("'B8': ('深圳市龙华区'", "'B9': ('深圳市龙华区'", 1); assert b != zh_src
da, db = differs(en, funcs(a)), differs(en, funcs(b))
print('control 1, one saved id changed in the bodies panel: reported in', da or 'NOTHING')
print('control 2, one voucher row given another label (B8 to B9): reported in', db or 'NOTHING')
sys.exit(0 if ok and da == ['bodies'] and db == ['voucher rows'] else 1)
