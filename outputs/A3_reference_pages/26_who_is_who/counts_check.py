#!/usr/bin/env python3
"""Gate for "who is who" (round 10, Nov 25, 2026): recompute every count the page prints in its provinces and vouchers rows
from the core's tables and scripts, and stop unless the base file carries each one exactly. Run before cn_doc_build.py:
    python3 -I counts_check.py && python3 -I scripts/cn_doc_build.py who_is_who_base.txt ...
Reads (only): ../../../tables/provinces_31.tsv; the voucher classes as scripts/cn_voucher_classes.py computes them (and its
table, tables/local_vouchers_classes.tsv, which must agree); the other provisions as scripts/cn_voucher_other.py counts them.
A control: the same comparison on a copy of the base file with one count changed must fail.
"""
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAB = HERE.parents[2] / 'tables'
sys.path.insert(0, 'scripts')
import cn_voucher_classes as VC      # noqa: E402
import cn_voucher_other as VO        # noqa: E402


def rows(name):
    lines = [l for l in (TAB / name).read_text(encoding='utf-8').split('\n') if l.strip() and not l.startswith('#')]
    head = lines[0].split('\t')
    return [dict(zip(head, l.split('\t'))) for l in lines[1:]]


def expected():
    want = []
    P = rows('provinces_31.tsv')
    c = Counter(r['result'] for r in P)
    if sum(c.values()) != 31: sys.exit('not 31 provincial-level governments')
    shandong = [r for r in P if r['government'] == 'Shandong']
    if len(shandong) != 1 or shandong[0]['result'] != 'share': sys.exit('Shandong is not one of those that set a share')
    # round 11 (Nov 26, 2026): the core's words since batch 13b, ruling 3b (four of the nine measure computing capacity, not hardware)
    want.append(f'On the record: {c["share"]} of the 31 were found to set a share for home-made computing, each by its plan\'s own measure: chips, equipment, hardware and software, or computing capacity')
    want.append(f'{c["plan_no_share"]} have a plan that was read and sets none')
    print(f'provinces: {dict(c)}')
    # the classes, from the classifier itself and from the core's table (which must agree)
    R = VC.compute()
    T = Counter(r['class'] for r in rows('local_vouchers_classes.tsv'))
    n = {k: R['n'][k] for k in (VC.MORE, VC.ONLY, VC.ONE, VC.TWO)}
    if tuple(T[k] for k in n) != tuple(n.values()): sys.exit('the table of classes differs from the classifier: run scripts/cn_voucher_classes.py --write')
    counted = sum(n.values()); third = n[VC.ONE] + n[VC.TWO]
    two = [r['government'] for r in rows('local_vouchers_classes.tsv') if r['class'] == VC.TWO]
    if two != ['Hangzhou']: sys.exit('the rule of two rates by an unnamed type is not Hangzhou\'s alone')
    only = sorted((r['government'] for r in rows('local_vouchers_classes.tsv') if r['class'] == VC.ONLY),
                  key=lambda g: ('Sichuan', 'Ningbo', 'Huangyan').index(g) if g in ('Sichuan', 'Ningbo', 'Huangyan') else 9)
    want.append(f'{n[VC.MORE]} of the {counted} found by searches that went province by province and city by city')
    want.append(f'{n[VC.ONLY]} (' + ', '.join(g + "'s" for g in only[:-1]) + f' and the {only[-1]}\'s) pay for home-made computing only')
    want.append(f'and {third} state no higher rate for home-made computing: {n[VC.ONE]} pay one rate whatever the chip, and Hangzhou\'s pays')
    # the other provisions, by cn_voucher_other's own functions
    cls, cnt = VO.classes()
    prov = VO.read_tsv(VO.TABLE)
    bad = VO.problems(prov, cls, cnt)
    if bad: sys.exit('the table of other provisions is refused: ' + bad[0])
    t = {name: (rules, anyk) for name, rules, per, anyk in VO.tally(prov, cnt)}
    rules3, any3 = t['state no higher rate for home-made computing']
    if len(rules3) != third: sys.exit('the other provisions script and the classifier differ on the third class')
    if t['pay more for home-made and still pay for other computing'][1] or t['pay for home-made computing only'][1]: sys.exit('a rule of the first two classes now gives something by another provision: reword the row')
    want.append(f'{len(any3)} of the {third} give home-made computing something by another provision of the same rule')
    print(f'vouchers: {counted} counted ({n[VC.MORE]} / {n[VC.ONLY]} / {n[VC.ONE]} one rate / {n[VC.TWO]} two rates); other provisions: {len(any3)} of the {third}')
    return want


if __name__ == '__main__':
    base = (HERE / 'who_is_who_base.txt').read_text(encoding='utf-8')
    want = expected()
    miss = [w for w in want if w not in base]
    planted = base.replace(want[0], want[0].replace(' of the 31 ', ' of the 30 '))
    control_ok = planted != base and any(w not in planted for w in want)
    for m in miss: print('NOT IN THE BASE FILE: ' + m)
    print(f'counts_check: {len(want)} computed strings, {len(want) - len(miss)} found in the base file; control (one count changed) {"fails as it should" if control_ok else "DID NOT FAIL"}')
    sys.exit(0 if not miss and control_ok else 1)
