"""Idea 36: build the note (results_calls.md and .html) from its parts. Run: python3 -I build.py   (in this folder)
1. build_table.py: reads rows_chosen.txt and the saved pages, writes table_fragment.txt, table_refs.tsv, calls_coverage.tsv
2. fills the counts in results_calls_head.txt and results_calls_tail.txt from the data files (no count is typed)
3. writes results_calls_base.txt and extra_refs.tsv, then runs scripts/cn_doc_build.py, which checks every quotation.
Stops at the first failure."""
import csv, subprocess, sys
from datetime import datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent
PY = [sys.executable, '-I']
r0 = subprocess.run(PY + [str(HERE.parent / 'tools' / 'word_census.py')], capture_output=True, text=True)
if r0.returncode: sys.exit('word_census.py failed: ' + r0.stderr[-300:])
r = subprocess.run(PY + [str(HERE / 'build_table.py')], cwd=HERE, capture_output=True, text=True)
print(r.stdout.splitlines()[0] if r.stdout else '', r.stderr[-800:])
if r.returncode: sys.exit('build_table.py failed')
r2 = subprocess.run(PY + [str(HERE / 'build_more.py')], cwd=HERE, capture_output=True, text=True)
print(r2.stdout.splitlines()[-1] if r2.stdout else '', r2.stderr[-800:])
if r2.returncode: sys.exit('build_more.py failed: ' + r2.stdout[-600:])
mc = dict(l.split('\t', 1) for l in (HERE / 'more_counts.tsv').read_text(encoding='utf-8').splitlines()[1:])
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
def nice(s):
    d = datetime.strptime(s, '%Y-%m-%d'); return f'{MON[d.month - 1]} {d.day}, {d.year}'
cov = list(csv.DictReader(open(HERE / 'calls_coverage.tsv', encoding='utf-8'), delimiter='\t'))
tab = list(csv.DictReader(open(HERE / 'results_calls_table.tsv', encoding='utf-8'), delimiter='\t'))
own = sorted(c['call_date_from_index'] for c in cov if c['saved_id'].endswith('-own'))
norow = [c for c in cov if c['rows_in_table'] == '0']
per_co = {}
for c in cov: per_co.setdefault(c['company'], []).append(c)
assert len({len(v) for v in per_co.values()}) == 1, 'the three companies do not have the same number of calls'
v = {'N_ROWS': len(tab), 'N_CALLS': len(cov), 'N_CALLS_ROWS': len(cov) - len(norow), 'N_CALLS_NOROWS': len(norow),
     'N_CAND': sum(int(c['candidate_paragraphs']) for c in cov), 'N_OWN': len(own), 'OWN_FIRST': nice(own[0]), 'OWN_LAST': nice(own[-1]),
     'N_Q': len(per_co['Tencent']),
     'N_SA_TENCENT': sum(1 for c in per_co['Tencent'] if not c['saved_id'].endswith('-own')), 'N_SA_BAIDU': sum(1 for c in per_co['Baidu'] if not c['saved_id'].endswith('-own')),
     'N_SA_ALIBABA': {1: 'one'}[sum(1 for c in per_co['Alibaba'] if not c['saved_id'].endswith('-own'))]}
by = {}
for c in norow: by.setdefault(c['company'], []).append(nice(c['call_date_from_index']))
sa = [r for r in tab if not r['saved_id'].endswith('-own')]
ali_sa = [r for r in sa if r['company'] == 'Alibaba']
assert all(r['saved_id'].endswith('-own') or r['address'].startswith('https://stockanalysis.com/') for r in tab), 'a row from a third kind of source'
assert len({r['call_date'] for r in ali_sa}) == 1, 'Alibaba rows from the stock-data site span more than one call'
assert not [r for r in tab if r['company'] in ('Tencent', 'Baidu') and r['saved_id'].endswith('-own')], 'a Tencent or Baidu row from an own transcript'
v.update({'N_SA_ROWS': len(sa), 'N_T_ROWS': sum(1 for r in tab if r['company'] == 'Tencent'), 'N_B_ROWS': sum(1 for r in tab if r['company'] == 'Baidu'),
          'N_ALI_SA_ROWS': {3: 'three', 4: 'four'}[len(ali_sa)], 'ALI_SA_DATE': nice(ali_sa[0]['call_date']), 'N_ALI_OWN_ROWS': sum(1 for r in tab if r['company'] == 'Alibaba') - len(ali_sa)})
v['NOROW_LIST'] = '; '.join(f"{co} ({', '.join(ds)})" for co, ds in sorted(by.items()))
show = ['Nvidia', 'Huawei', 'Cyberspace Administration', 'customs', 'H200', 'H20', 'H800', 'A100 or V100', 'import/imported/imports (of chips or GPUs, same sentence)', 'export control / export restriction', 'BIS', 'domestic chip(s)', 'T-Head', 'Kunlun']
name = {'import/imported/imports (of chips or GPUs, same sentence)': 'import, imported or imports in one sentence with chip, GPU or semiconductor', 'export control / export restriction': 'export control, export restriction or chip export', 'domestic chip(s)': 'domestic chip or chips', 'customs': 'customs (the border service)', 'A100 or V100': 'A100 or V100'}
cen = {r['word']: r for r in csv.DictReader(open(HERE / 'word_census.tsv', encoding='utf-8'), delimiter='\t')}
assert int(cen['revenue (control)']['calls_with_it']) == len(cov), 'control word is not in every call'
for w0 in ('Nvidia', 'Huawei', 'misspellings of Nvidia or Huawei'):
    if int(cen[w0]['calls_with_it']) != 0: sys.exit(f'{w0} is now found in a call: rewrite the sentences that say it is not')
for k in ('约谈', '窗口指导', '海关', '不得采购', '限制采购', '政府要求'):
    if mc[f'ifly_{k}'] != '0': sys.exit(f'{k} is now found in an iFlytek text: rewrite the paragraph that says none occurs')
for k in ('nvidia', 'huawei', 'misspell', 'cyberspace', 'customs', 'h200'):
    if mc[f'l9_{k}'] != '0': sys.exit(f'the wider census now finds {k}: rewrite the paragraph')
un = cen['untranslated passage marker']
if 'Tencent 2025-08-13' in cen['H20']['which']: sys.exit('H20 is now found in the Tencent call of Aug 13, 2025: rewrite finding 3')
for call in ('Tencent 2026-03-18', 'Tencent 2026-05-13'):
    if call in un['which']: sys.exit(f'{call} now has an untranslated mark: rewrite the paragraph on the commission appendix')
v.update({'M_SA_CALLS': mc['more_sa_calls'], 'M_OWN_ROWS': mc['more_own_rows'], 'M_PRESS_ROWS': {1: 'one'}[int(mc['more_press_rows'])]})
v.update({'M_ROWS': mc['more_rows'], 'M_SA_ROWS': mc['more_sa_rows'], 'M_ZH_ROWS': mc['more_chinese_rows'], 'L9_CALLS': mc['l9_calls'], 'L9_NVIDIA': mc['l9_nvidia'], 'L9_HUAWEI': mc['l9_huawei'],
          'L9_CYBER': mc['l9_cyberspace'], 'L9_CUSTOMS': mc['l9_customs'], 'L9_H200': mc['l9_h200'], 'L9_H20': mc['l9_h20'], 'L9_H20_WHICH': mc['l9_h20_which'], 'L9_UNTRANS': mc['l9_untranslated'],
          'N_UNTRANS': {1: 'one'}[int(un['calls_with_it'])], 'UNTRANS_WHICH': '; '.join(f"{x.split()[0]}, {nice(x.split()[1])}" for x in un['which'].split('; ')),
          'IFLY_TEXTS': mc['ifly_texts'], 'IFLY_REPORTS': mc['ifly_reports'], 'IFLY_RECORDS': mc['ifly_records'], 'IFLY_ANSWERS': mc['ifly_answers'], 'IFLY_WXB': {2: 'twice'}[int(mc['ifly_网信办'])], 'C_YUETAN': {2: 'twice'}[int(mc['control_约谈'])]})
lines = []
for w in show:
    r = cen[w]; n = int(r['calls_with_it'])
    which = ''
    if 0 < n <= 6: which = ' (' + '; '.join(f"{x.split()[0]} {nice(x.split()[1])}" for x in r['which'].split('; ')) + ')'
    lines.append(f"- {name.get(w, w)}: in {n} of {r['calls_read']} calls{which}.")
v['CENSUS_LINES'] = '\n'.join(lines)
def fill(t):
    for k, x in v.items(): t = t.replace('{' + k + '}', str(x))
    assert '{' not in t.replace('{N', '{N') or all(('{' + k + '}') not in t for k in v), 'unfilled'
    return t
base = (fill((HERE / 'results_calls_head.txt').read_text(encoding='utf-8')) + (HERE / 'table_fragment.txt').read_text(encoding='utf-8') + fill((HERE / 'results_calls_mid.txt').read_text(encoding='utf-8'))
        + (HERE / 'more_fragment.txt').read_text(encoding='utf-8') + fill((HERE / 'results_calls_tail.txt').read_text(encoding='utf-8')))
import re
left = re.findall(r'\{[A-Z_0-9]+\}', base)
if left: sys.exit(f'unfilled placeholders: {left}')
(HERE / 'results_calls_base.txt').write_text(base, encoding='utf-8')
(HERE / 'extra_refs.tsv').write_text((HERE / 'table_refs.tsv').read_text(encoding='utf-8') + (HERE / 'more_refs.tsv').read_text(encoding='utf-8') + (HERE / 'refs_hand.tsv').read_text(encoding='utf-8'), encoding='utf-8')
r = subprocess.run(PY + ['scripts/cn_doc_build.py', str(HERE / 'results_calls_base.txt'), '--refs', str(HERE / 'extra_refs.tsv'), '--title', 'Results Calls On Chips', '--eyebrow', 'China chip policy: new research, idea 36'], capture_output=True, text=True)
print(r.stdout[-3000:], r.stderr[-800:])
sys.exit(r.returncode)
