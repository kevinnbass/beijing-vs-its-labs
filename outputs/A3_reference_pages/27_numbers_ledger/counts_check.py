#!/usr/bin/env python3
"""Gate for the numbers ledger (round 4): recompute every count the ledger shows from the project's tables and stop
unless the base file carries each one exactly. Run before cn_doc_build.py:
    python3 -I counts_check.py && python3 -I scripts/cn_doc_build.py numbers_ledger_base.txt ...
Reads ../../../tables/house_licence_table.tsv, nvidia_china_revenue.tsv, provinces_31.tsv; writes nothing.
A control: the same comparison run on a copy of the base file with one number changed must fail.
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAB = HERE.parents[2] / 'tables'


def rows(name):
    lines = [l for l in (TAB / name).read_text(encoding='utf-8').split('\n') if l.strip() and not l.startswith('#')]
    head = lines[0].split('\t')
    return [dict(zip(head, l.split('\t'))) for l in lines[1:]]


def fmt(n): return f'{n:,}'


def expected():
    want = []
    H = rows('house_licence_table.tsv'); num = lambda r: int(r['chip_count'].replace(',', ''))
    total = sum(map(num, H))
    st = defaultdict(lambda: [0, 0]); ex = defaultdict(lambda: [0, 0]); ex_all = defaultdict(lambda: [0, 0])
    for r in H:
        st[r['status']][0] += 1; st[r['status']][1] += num(r)
        ex[(r['exporter'], r['status'])][0] += 1; ex[(r['exporter'], r['status'])][1] += num(r)
        ex_all[r['exporter']][0] += 1; ex_all[r['exporter']][1] += num(r)
    if set(st) != {'RWA', 'Approved, not shipped', 'Submitted', 'Rejected'}: sys.exit(f'unexpected statuses: {sorted(st)}')
    rwa = st['RWA']; share = round(100 * rwa[1] / total)
    sea = [r for r in H if r['status'] == 'RWA' and r['location'] != 'China']
    over = [r for r in H if num(r) > 75000]
    if any(r['status'] != 'RWA' for r in over): sys.exit('an application over 75,000 is not RWA')
    if max(num(r) for r in H if r['status'] == 'Approved, not shipped') > 75000: sys.exit('an approved application is over 75,000')
    if any(r['location'] != 'China' for r in H if r['status'] == 'Approved, not shipped'): sys.exit('an approved application is outside China')
    rej = [r for r in H if r['status'] == 'Rejected']
    dec19 = [r for r in H if r['date_submitted'] == '12/19/2025' and r['exporter'] == 'Nvidia' and 'Tencent' in r['consignee']]
    if len(dec19) != 1 or num(dec19[0]) != 75000 or dec19[0]['status'] != 'Approved, not shipped': sys.exit('the Dec 19, 2025 Tencent row is not as the page says')
    alt = round(100 * rwa[1] / (total - 75000 + 445000), 1)
    groups = sorted({g.strip() for r in sea for g in r['group'].split('(')[0].replace(' and ', ',').split(',') if g.strip()})
    want += [
        f'| Returned without action (RWA) | {fmt(rwa[1])} | {rwa[0]} | {share}% of the chips in the applications the summary records. Among them every application for more than 75,000 chips ({["zero","one","two","three","four","five","six"][len(over)]})',
        f'all {fmt(sum(map(num, sea)))} chips for consignees in Malaysia, Indonesia and Thailand',
        f'Nvidia {fmt(ex[("Nvidia","RWA")][1])} in {ex[("Nvidia","RWA")][0]}; AMD {fmt(ex[("AMD","RWA")][1])} in {ex[("AMD","RWA")][0]} |',
        f'| Approved, not shipped | {fmt(st["Approved, not shipped"][1])} | {st["Approved, not shipped"][0]} | Nvidia {fmt(ex[("Nvidia","Approved, not shipped")][1])} in {ex[("Nvidia","Approved, not shipped")][0]}; AMD {fmt(ex[("AMD","Approved, not shipped")][1])} in {ex[("AMD","Approved, not shipped")][0]};',
        f'| Submitted | {fmt(st["Submitted"][1])} | {st["Submitted"][0]} | Nvidia {fmt(ex[("Nvidia","Submitted")][1])} in {ex[("Nvidia","Submitted")][0]}; AMD {fmt(ex[("AMD","Submitted")][1])} in {ex[("AMD","Submitted")][0]}; Semsotai USA {fmt(ex[("Semsotai USA","Submitted")][1])} in {ex[("Semsotai USA","Submitted")][0]} |',
        f'| Rejected | {fmt(st["Rejected"][1])} | {st["Rejected"][0]} | one {rej[0]["exporter"]} application, for {rej[0]["consignee"].split()[0]} |',
        f'| All | {fmt(total)} | {len(H)} | Nvidia {fmt(ex_all["Nvidia"][1])} in {ex_all["Nvidia"][0]}; AMD {fmt(ex_all["AMD"][1])} in {ex_all["AMD"][0]}; Semsotai USA {fmt(ex_all["Semsotai USA"][1])} in {ex_all["Semsotai USA"][0]} |',
        f'the returned share would be {alt}% (ours)',
        f'among them **{share}%** and, with the application of Dec 19, 2025 counted at 445,000, **{alt}%**; and **{fmt(sum(map(num, sea)))}**',
    ]
    if len(rej) != 1: sys.exit('not one rejected application')
    print(f'licence table: {len(H)} applications, {fmt(total)} chips; RWA {fmt(rwa[1])} in {rwa[0]} ({100*rwa[1]/total:.1f}%); '
          f'approved {fmt(st["Approved, not shipped"][1])}; submitted {fmt(st["Submitted"][1])}; rejected {fmt(st["Rejected"][1])}; '
          f'outside China {fmt(sum(map(num, sea)))} in {len(sea)} ({", ".join(groups)}); over 75,000: {len(over)}; with Dec 19 at 445,000: {alt}%')

    R = [r for r in rows('nvidia_china_revenue.tsv') if r['basis'] == 'headquarters' and r['period'].startswith('Q')]
    R.sort(key=lambda r: r['period_end'])
    if len(R) != 9: sys.exit(f'{len(R)} quarters on the headquarters basis, not 9')
    months = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
    for r in R:
        y, m, d = r['period_end'].split('-')
        want.append(f'| {months[int(m)-1]} {int(d)}, {y} | {fmt(int(r["value_musd"]))} |')
    top = max(R, key=lambda r: int(r['value_musd']))
    if top is not R[-1]: sys.exit('the latest quarter is not the highest')
    want.append(f'9.5% of Nvidia\'s revenue of $115,844 million' if round(100 * int(R[-1]['value_musd']) / 115844, 1) == 9.5 else 'SHARE CHANGED')
    first, low = int(R[2]['value_musd']), int(R[4]['value_musd'])
    if not 0.6 <= 1 - low / first <= 0.72: sys.exit('the fall is not about two thirds')
    print(f'revenue: 9 quarters, {R[0]["period_end"]} to {R[-1]["period_end"]}; latest {fmt(int(R[-1]["value_musd"]))} = {100*int(R[-1]["value_musd"])/115844:.2f}% of 115,844; '
          f'fall {first:,} to {low:,} = {100*(1-low/first):.0f}%')

    P = Counter(r['result'] for r in rows('provinces_31.tsv'))
    if sum(P.values()) != 31: sys.exit('not 31 provinces')
    want.append(f'{P["share"]} set a share; {P["plan_no_share"]} have a plan that was read and sets none')
    want.append(f'**{P["share"]} of 31** provincial-level governments set a share')
    if P['account_only'] != 1 or P['not_reached'] != 1: sys.exit('Tibet and Xinjiang are not one each')
    print(f'provinces: {dict(P)}')
    return want


def check(text, want):
    return [w for w in want if w not in text]


if __name__ == '__main__':
    base = (HERE / 'numbers_ledger_base.txt').read_text(encoding='utf-8')
    want = expected()
    miss = check(base, want)
    planted = base.replace('| 1,888,950 | 9 |', '| 1,888,951 | 9 |')
    control_ok = bool(check(planted, want)) and planted != base
    for m in miss: print('NOT IN THE BASE FILE: ' + m)
    print(f'counts_check: {len(want)} computed strings, {len(want) - len(miss)} found in the base file; control (one number changed) {"fails as it should" if control_ok else "DID NOT FAIL"}')
    sys.exit(0 if not miss and control_ok else 1)
