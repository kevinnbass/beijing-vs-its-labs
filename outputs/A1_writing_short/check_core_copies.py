#!/usr/bin/env python3
"""Does this folder still agree with the core files in the words it copies from them, and is the old wording gone?

Run: python3 -I check_core_copies.py     (reads only; exit 1 on any difference)
1. Copied sentences. 04_right_and_too_flat and 05_questions_and_answers copy, word for word, the sentence the
   argument gives after "One sentence that survives all <N> limits." (argument/argument_base.txt). It must be equal.
2. 08_what_would_change opens with a short statement of the answer. Each of its sentences must stand, as written,
   in the argument's paragraph "The answer." (the argument's own paragraph is longer and carries quotations).
3. The number of limits. The argument's section "## 5. <N> limits on the claim" is counted; the thread, the
   questions and the list of documents must each say that number.
4. Old wording. The texts written here (the base files, the plain thread, the plain timeline) must not hold any
   phrase the rounds have retired (list below). No delivered file, built pages included, may hold an id that may no
   longer be cited (loose_ends/hkexnews_saved_ids.tsv and the ids ROUND4.md names).
Controls: a copy with one word changed must be reported as different; a phrase known to be present must be found
by the same search that looks for the retired ones.
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parents[1]
ARG = (PROJ / 'argument' / 'argument_base.txt').read_text(encoding='utf-8')
ARGL = ARG.splitlines()
WORDS = {4: 'four', 5: 'five', 6: 'six'}
ok = True


def fail(msg):
    global ok
    ok = False; print('FAILED: ' + msg)


def after(pattern):
    hits = [m.group(1).strip() for ln in ARGL for m in [re.match(pattern, ln)] if m]
    if len(hits) != 1: sys.exit(f'the argument does not hold exactly one line matching {pattern!r}')
    return hits[0]


# 1. the surviving sentence
survives = after(r'\*\*One sentence that survives all \w+ limits\.\*\* (.*)')
for f in ('04_right_and_too_flat/right_too_flat_base.txt', '05_questions_and_answers/questions_answers_base.txt'):
    same = survives in (HERE / f).read_text(encoding='utf-8').splitlines()
    print(f'surviving sentence: {"same as the argument" if same else "DIFFERS from the argument"} in {f}')
    if not same: fail(f'{f} does not carry the argument\'s surviving sentence')
if survives.replace('millions', 'thousands') in (HERE / '04_right_and_too_flat/right_too_flat_base.txt').read_text(encoding='utf-8').splitlines():
    fail('control: a changed sentence was found')
else: print('control: a copy with one word changed is not found')

# 2. the short statement of the answer in 08
answer = after(r'\*\*The answer\.\*\* (.*)')
t8 = (HERE / '08_what_would_change/what_would_change_base.txt').read_text(encoding='utf-8').splitlines()
i = t8.index('## The answer these would test')
para = next(ln for ln in t8[i + 1:] if ln.strip())
sents = [s.strip() for s in re.split(r'(?<=\.)\s+', para) if s.strip()]
miss = [s for s in sents if s.rstrip('.') not in answer]
print(f'08, statement of the answer: {len(sents) - len(miss)} of {len(sents)} sentences stand in the argument\'s own paragraph')
if miss: fail(f'08: not in the argument\'s answer paragraph: {miss}')
if 'Sixth, nothing' in answer or len(sents) < 5: fail('control: the sentence check is not working')

# 3. the number of limits
sec = re.search(r'(?ms)^## 5\. (\w+) limits on the claim$(.*?)^## ', ARG)
n_lim = len(re.findall(r'(?m)^\d+\. ', sec.group(2))) if sec else 0
word = WORDS.get(n_lim, '?')
if not sec or sec.group(1).lower() != word: fail('the argument\'s heading and its count of limits disagree')
print(f'limits in the argument: {n_lim} ("{word}")')
for f, said in (('03_thread/thread_base.txt', f'with {word} limits'), ('05_questions_and_answers/questions_answers_base.txt', f'with {word} limits'),
                ('08_what_would_change/what_would_change_base.txt', f'{word.capitalize()} limits apply.'), ('04_right_and_too_flat/right_too_flat_base.txt', None)):
    if said and said not in (HERE / f).read_text(encoding='utf-8'): fail(f'{f} does not say "{said}"')

# 4. old wording and ids that may no longer be cited
RETIRED_WORDS = ['four limits', 'four cautions', '20 points', '750,000', 'more than half', 'democrat', 'at a lower rate', 'public universit', 'state universit',
                 'more exact', 'warn against', 'first press report', "bloomberg's first report", 'sept 28, 2024', '70 sources', '63 sources', '53 records', '59 records',
                 'people’s daily had run', "people's daily had run", 'undated', 'state telecom operators']
RETIRED_IDS = {ln.split('\t')[0] for ln in (PROJ / 'loose_ends' / 'hkexnews_saved_ids.tsv').read_text(encoding='utf-8').splitlines() if ln.strip()}
if len(RETIRED_IDS) < 10: fail('control: the do-not-cite list is shorter than expected')
RETIRED_IDS |= {'cn-le08-moore-final-prospectus', 'cn-le29-sensetime-2025-annual-en', 'cn-media-yuyuan-thepaper', 'cn-factions-tencent-reuters-20261120-relay1',
                'cn-policy-ai-chip-evaluation', 'cn-clips-mfa-new-1', 'cn-us-lutnick-0422-coons-letter', 'cn-clips-trump-may15-wayback',
                'cn-acts-ft-lutnick-20250821-wayback', 'ms-bj-20250917-cac-6000d-engadget', 'cn-tolerate-customs-relay1'}
files = sorted(p for pat in ('*/*_base.txt', '*/*.md', '*/*.html', '*/thread_plain.txt', '*/timeline.txt', '*/*refs*.tsv')
               for p in HERE.glob(pat) if not p.parent.name.startswith('superseded'))
found_control = False
for p in files:
    low = p.read_text(encoding='utf-8').lower()
    if 'five limits' in low: found_control = True
    own = p.name.endswith('_base.txt') or p.name in ('thread_plain.txt', 'timeline.txt')      # my own words; built pages also carry the core's reference labels
    for w in RETIRED_WORDS:
        if own and w in low: fail(f'{p.relative_to(HERE)} holds the retired wording "{w}"')
    ids = set(re.findall(r'(?:cn|ms|man|cnpol)-[a-z0-9-]+', low))
    for sid in sorted(ids & RETIRED_IDS): fail(f'{p.relative_to(HERE)} holds the id {sid}, which may no longer be cited')
print(f'old wording: {len(files)} delivered files searched for {len(RETIRED_WORDS)} retired phrases and {len(RETIRED_IDS)} ids; control phrase "five limits" found: {found_control}')
if not found_control: fail('control: the search did not find a phrase that is present')
print('result: the folder agrees with the core in what it copies, and the retired wording is gone' if ok else 'result: FAILED')
sys.exit(0 if ok else 1)
