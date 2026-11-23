"""Idea 36 reading aid: from candidates.tsv print, per paragraph, only the sentences that hit a tight list of words,
each with its neighbouring sentences. Run: python3 -I tools/snips.py <Company> [max_chars_per_paragraph]"""
import csv, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1] / 'idea36_results_calls'
T = re.compile(r"(?i)\bchips?\b|chipset|\bGPUs?\b|nvidia|semiconductor|\bexport|\bimport(?:s|ed|ing|ation)?\b|sanction|kunlun|t-head|\bH20\b|\bH200\b|\bASICs?\b|\bbans?\b|\bbanned\b|restrict|supply[- ]chain|supply constraint|suppl(?:y|ies) of|domestic(?:ally)?[- ](?:produced|made|suppl|chip|GPU|alternative|compute|hardware)|homegrown|home-grown|geopolit|u\.s\. (?:government|curbs|control|polic)")
co = sys.argv[1]; cap = int(sys.argv[2]) if len(sys.argv) > 2 else 900
csv.field_size_limit(10**7)
for r in csv.DictReader(open(HERE / 'candidates.tsv', encoding='utf-8'), delimiter='\t'):
    if r['company'] != co: continue
    sents = re.split(r'(?<=[.?!])\s+(?=[A-Z"(])', r['text'])
    keep = set()
    for i, s in enumerate(sents):
        if T.search(s): keep.update({i - 1, i, i + 1})
    keep = sorted(k for k in keep if 0 <= k < len(sents))
    if not keep: continue
    out, prev = [], None
    for k in keep:
        if prev is not None and k != prev + 1: out.append('[...]')
        out.append(sents[k]); prev = k
    body = ' '.join(out)
    if len(body) > cap: body = body[:cap] + ' [cut]'
    print(f"## {r['call_date']} #{r['para_no']} {r['speaker']} | {r['title']}\n{body}\n")
