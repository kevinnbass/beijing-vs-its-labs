"""Idea 36: count, over the saved call transcripts in calls.tsv, how many calls hold each word (whole page text, any speaker).
Run: python3 -I tools/word_census.py -> idea36_results_calls/word_census.tsv. A control word ("revenue") must be in every call."""
import csv, re, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
P = Path('research/primary')
HERE = Path(__file__).resolve().parents[1] / 'idea36_results_calls'
import html
def text(sid):
    d = P / sid
    if sid.endswith('-own'): return (d / 'text.txt').read_text(encoding='utf-8', errors='replace')
    h = (d / 'body.html').read_text(encoding='utf-8', errors='replace')
    h = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', h)
    return html.unescape(re.sub(r'(?s)<[^>]+>', ' ', h))
WORDS = {'revenue (control)': r'\brevenue\b', 'untranslated passage marker': r'\[(?:Foreign language|Non-English content)\]', 'Nvidia': r'nvidia', 'H20': r'\bH20\b', 'H200': r'\bH[- ]?200\b', 'H800': r'\bH800\b', 'A100 or V100': r'\b[AV]100\b',
         'Huawei': r'huawei', 'misspellings of Nvidia or Huawei': r'in[- ]?vidia|en[- ]?vidia|n[- ]vidia|nvdia|navidia|hua ?wei|wah ?way', 'Ascend': r'\bascend\b', 'Cyberspace Administration': r'cyberspace', 'customs': r'\bcustoms\b', 'Hong Kong (chips context not checked)': r'hong kong',
         'import/imported/imports (of chips or GPUs, same sentence)': r'[^.]*\b(?:chips?|GPUs?|semiconductor)[^.]*\bimport(?:s|ed|ing|ation)?\b[^.]*|[^.]*\bimport(?:s|ed|ing|ation)?\b[^.]*\b(?:chips?|GPUs?|semiconductor)[^.]*',
         'export control / export restriction': r'export[- ](?:control|restriction)|restrictions? on the chip export|chip export', 'BIS': r'\bBIS\b', 'domestic chip(s)': r'domestic(?:ally)?[- ](?:\w+[- ]){0,3}chips?', 'T-Head': r't-head', 'Kunlun': r'kunlun', 'ASIC': r'\bASICs?\b'}
rows = [r for r in csv.DictReader(open(HERE / 'calls.tsv', encoding='utf-8'), delimiter='\t') if r['saved_id']]
out = []
for w, pat in WORDS.items():
    rx = re.compile(pat, re.I); hits = []
    for r in rows:
        if rx.search(text(r['saved_id'])): hits.append(f"{r['company']} {r['call_date']}")
    out.append((w, len(hits), len(rows), '; '.join(hits) if len(hits) <= 14 else f'{len(hits)} calls'))
(HERE / 'word_census.tsv').write_text('word\tcalls_with_it\tcalls_read\twhich\n' + '\n'.join('\t'.join(map(str, o)) for o in out) + '\n', encoding='utf-8')
for o in out: print('\t'.join(map(str, o)))
