#!/usr/bin/env python3
"""Round 4 reading aid: for each Chinese quotation in a base file, show the argument's own sentence around the same
Chinese (from argument/argument_base.txt), so the English beside it can be compared. Writes nothing.
Run: python3 -I tools/r4_compare29.py 29_chinese_passages/chinese_passages_base.txt
"""
import re, sys
CORE = 'argument/argument_base.txt'
core = open(CORE, encoding='utf-8').read()
CJK = re.compile(r'[一-鿿]')

def norm(s):
    return re.sub(r'[\s,，、;；:：。.“”"（）()]', '', s)

core_n = norm(core)
# the argument's own Chinese quotations
core_q = [q for q in re.findall(r'"([^"]+)"', core) if CJK.search(q)]
print('argument quotations holding Chinese:', len(core_q))
base = open(sys.argv[1], encoding='utf-8').read()
page_q = [q for q in re.findall(r'"([^"]+)"', base) if CJK.search(q)]
page_n = norm(base)
held = [q for q in core_q if norm(q) in page_n]
print('of them held in the page (normalised containment):', len(held))
print('page quotations holding Chinese:', len(page_q))
for line in base.splitlines():
    if not line.startswith('| ') or not CJK.search(line):
        continue
    cells = [c.strip() for c in line.strip('|').split('|')]
    if len(cells) < 3:
        continue
    print('=' * 100)
    print('PAGE  :', cells[0][:110])
    print('ENG   :', cells[2])
    for q in re.findall(r'"([^"]+)"', cells[1]):
        qn = norm(q)
        hits = [c for c in core_q if norm(c) in qn or qn in norm(c)]
        if not hits:
            print('  NOT IN ARGUMENT:', q[:60])
            continue
        for h in hits:
            i = core.find('"' + h + '"')
            print('  CORE :', core[max(0, i - 260):i + len(h) + 2 + 160].replace('\n', ' '))
missing = [q for q in core_q if norm(q) not in page_n]
print('=' * 100)
print('argument Chinese quotations not in the page:', len(missing))
for q in missing:
    i = core.find('"' + q + '"')
    print(' -', q[:50], '||', core[max(0, i - 90):i].replace('\n', ' ')[-90:])
