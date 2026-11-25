#!/usr/bin/env python3
"""Gate for the numbers ledger (round 4): recompute every count the ledger shows from the project's tables and stop
unless the base file carries each one exactly. Run before cn_doc_build.py:
    python3 -I counts_check.py && python3 -I scripts/cn_doc_build.py numbers_ledger_base.txt ...
Reads ../../../tables/house_licence_table.tsv, nvidia_china_revenue.tsv, provinces_31.tsv, market_numbers.tsv,
rtx5500_notices.tsv (the last two since round 5, Nov 24, 2026) and local_vouchers_classes.tsv (core edit 8, Nov 25, 2026); writes nothing.
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
    if len([r for r in H if r['date_submitted'] == '12/19/2025' and 'Tencent' in r['consignee']]) != 1: sys.exit('not the only Tencent row of Dec 19, 2025')
    alt = round(100 * rwa[1] / (total - 75000 + 445000), 1)   # the 75,000 row is the application of 445,000
    alt2 = round(100 * rwa[1] / (total + 445000), 1)          # the 445,000 is a further application
    groups = sorted({g.strip() for r in sea for g in r['group'].split('(')[0].replace(' and ', ',').split(',') if g.strip()})
    want += [
        f'| Returned without action (RWA) | {fmt(rwa[1])} | {rwa[0]} | {share}% of the chips in the applications the summary records. Among them every application for more than 75,000 chips ({["zero","one","two","three","four","five","six"][len(over)]})',
        f'all {fmt(sum(map(num, sea)))} chips for consignees in Malaysia, Indonesia and Thailand',
        f'Nvidia {fmt(ex[("Nvidia","RWA")][1])} in {ex[("Nvidia","RWA")][0]}; AMD {fmt(ex[("AMD","RWA")][1])} in {ex[("AMD","RWA")][0]} |',
        f'| Approved, not shipped | {fmt(st["Approved, not shipped"][1])} | {st["Approved, not shipped"][0]} | Nvidia {fmt(ex[("Nvidia","Approved, not shipped")][1])} in {ex[("Nvidia","Approved, not shipped")][0]}; AMD {fmt(ex[("AMD","Approved, not shipped")][1])} in {ex[("AMD","Approved, not shipped")][0]};',
        f'| Submitted | {fmt(st["Submitted"][1])} | {st["Submitted"][0]} | Nvidia {fmt(ex[("Nvidia","Submitted")][1])} in {ex[("Nvidia","Submitted")][0]}; AMD {fmt(ex[("AMD","Submitted")][1])} in {ex[("AMD","Submitted")][0]}; Semsotai USA {fmt(ex[("Semsotai USA","Submitted")][1])} in {ex[("Semsotai USA","Submitted")][0]} |',
        f'| Rejected | {fmt(st["Rejected"][1])} | {st["Rejected"][0]} | one {rej[0]["exporter"]} application, for {rej[0]["consignee"].split()[0]} |',
        f'| All | {fmt(total)} | {len(H)} | Nvidia {fmt(ex_all["Nvidia"][1])} in {ex_all["Nvidia"][0]}; AMD {fmt(ex_all["AMD"][1])} in {ex_all["AMD"][0]}; Semsotai USA {fmt(ex_all["Semsotai USA"][1])} in {ex_all["Semsotai USA"][0]} |',
        f'the returned share would be {alt}% if that row is the application, counted at 445,000, and {alt2}% if the 445,000 is a further application (ours)',
        f'among them **{share}%**; **{alt}%** or **{alt2}%** with the application of Dec 19, 2025 counted at 445,000 (as the table\'s row of that date, or as a further application); and **{fmt(sum(map(num, sea)))}**',
    ]
    if len(rej) != 1: sys.exit('not one rejected application')
    print(f'licence table: {len(H)} applications, {fmt(total)} chips; RWA {fmt(rwa[1])} in {rwa[0]} ({100*rwa[1]/total:.1f}%); '
          f'approved {fmt(st["Approved, not shipped"][1])}; submitted {fmt(st["Submitted"][1])}; rejected {fmt(st["Rejected"][1])}; '
          f'outside China {fmt(sum(map(num, sea)))} in {len(sea)} ({", ".join(groups)}); over 75,000: {len(over)}; with Dec 19 at 445,000: {alt}% (as that row) or {alt2}% (as a further application)')

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
    # core edit 8 (Nov 25, 2026): the voucher count the ledger prints, from the core's table of classes
    # round 9 (Nov 25, 2026; voucher rounds 3 to 6): a fifth class, Hangzhou's two rates by a type of facility it does not name, which with the one-rate
    # rules makes the third class, "states no higher rate for home-made computing"; the governments named in the row are taken from the table too
    V = Counter(r['class'] for r in rows('local_vouchers_classes.tsv'))
    MORE, ONLY, ONE, TWO, NOT = ('pays more for home-made and still pays for other computing', 'pays for home-made computing only', 'one rate',
                                 'two rates by a type of computing facility that the rule does not name', 'read and not counted')
    more, only, one, two = V[MORE], V[ONLY], V[ONE], V[TWO]
    counted = more + only + one + two
    if set(V) != {MORE, ONLY, ONE, TWO, NOT} or not (more and only and one and two) or counted + V[NOT] != sum(V.values()): sys.exit(f'voucher classes: an unknown class or an empty one: {dict(V)}')
    if two != 1 or [r['government'] for r in rows('local_vouchers_classes.tsv') if r['class'] == TWO] != ['Hangzhou']: sys.exit('the rule of two rates by an unnamed type is not Hangzhou\'s alone')
    words = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    want.append(f'**{more} of {counted}** local voucher rules pay more for home-made computing and still pay for other computing; **{only}** pay for home-made computing only; '
                f'**{one + two}** state no higher rate for home-made computing (**{one}** pay one rate whatever the chip; Hangzhou\'s pays 30% or 20% by a type of computing facility that it does not name)')
    gov = lambda c: [r['government'] for r in rows('local_vouchers_classes.tsv') if r['class'] == c]
    want.append(f'The {words[more]}, as shares of the bill')
    want += [f'{g} ' for g in gov(MORE) if g not in ('Wuhan', 'Longwan and Wenzhou Bay New Area')] + ['Wuhan\'s Data Bureau', 'Longwan district and Wenzhou Bay New Area']
    want.append(f'The {words[only]} that pay for home-made computing only: ' + ', '.join(sorted(gov(ONLY), key=lambda g: ('Sichuan', 'Ningbo', 'Huangyan').index(g) if g in ('Sichuan', 'Ningbo', 'Huangyan') else 9)[:-1]) + ' and the ' + sorted(gov(ONLY), key=lambda g: ('Sichuan', 'Ningbo', 'Huangyan').index(g) if g in ('Sichuan', 'Ningbo', 'Huangyan') else 9)[-1])
    want.append(f'**{more} of {counted}** voucher rules')
    print(f'vouchers: counted {counted} ({more} pay more, {only} home-made only, {one} one rate, {two} two rates by an unnamed type); read and not counted {V[NOT]}')

    M = rows('market_numbers.tsv')
    want.append(f'{len(M)} published market numbers')
    N = rows('rtx5500_notices.tsv'); k = sum(1 for r in N if r['names_card'] == 'yes')
    words = ['No', 'One', 'Two', 'Three', 'Four', 'Five']
    want.append(f'{words[k]} listed companies announced purchases of cards of that name: the next {words[k].lower()} rows. They are {k} of the {len(N)} notices')
    print(f'market numbers: {len(M)} rows; RTX PRO 5500 notices: {len(N)}, {k} name the card')
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
