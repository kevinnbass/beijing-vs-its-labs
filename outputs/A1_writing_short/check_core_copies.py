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
   longer be cited (loose_ends/hkexnews_saved_ids.tsv, the ids ROUND4.md names and, since round 8, the copies from
   idc.com and trendforce.com in loose_ends/terms_saved_ids.tsv).
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


def retired_matches(text, phrases):
    return [phrase for phrase in phrases if phrase in text]


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
                 'people’s daily had run', "people's daily had run", 'undated', 'state telecom operators',
                 # withdrawn by core edits 5 and 6 (Nov 24, 2026; outputs/ROUND5.md), added in round 5
                 'no chinese document found states it', 'states the motive', '42 items', '42 state', 'the seven that', 'aug 1 to sept 24', 'none after',
                 "commerce department's table", 'shows that application at 75,000', 'which the table shows at 75,000', 'were not reached (qingyang',
                 'voucher rules of five cities were not reached', 'read it two ways', 'every such rule still pays', '31 official', '31 saved official',
                 '30 official readouts', '213 sources', 'four others are not', 'under which line the chips are declared',
                 # withdrawn by core edit 7 (Nov 25, 2026; outputs/ROUND8.md): the argument has 299 sources, the figure 62 records; added in round 8
                 '297 sources', '61 records', '61 dated records',
                 # withdrawn by core edit 7c (Nov 25, 2026, ruling R3a): 300 sources; Nvidia's statement has two carriers
                 '299 sources', 'one carrier',
                 # withdrawn by core edits 8 and 8b and the voucher rounds (Nov 25, 2026; outputs/ROUND9.md): 392 sources; added in round 9
                 '300 sources', '345 sources', '347 sources', "pulled china's ai companies away", 'asked firms to stop buying chips', 'what exporters must do',
                 "chengdu's and qingyang's only through press", 'that could be read (all but one', 'which is of the rules found, not a census',
                 "the cyberspace regulator's review office", 'other home-made ones',
                 # withdrawn by the core's batch of 20:58 UTC and voucher round 7 (Nov 25, 2026; round 10): 395 sources; added in round 10
                 '392 sources', 'an application names a consignee', "saw in the market regulator's move", 'at 06:49 utc', 'the president, may 15',
                 # withdrawn by core batch 12 and the readers' leads (Nov 25, 2026; round 10b): 460 sources; the thread's delivery figure as the
                 # argument gives it; Greer's question; working words on the public pages
                 '395 sources', 'what the companies bought', 'obtained by several firms', 'is read two ways', 'the security and planning side',
                 'is the local file', 'no new image was made', 'made by make_thread_plain', 'brought into line with the argument', 'called buying the h200',
                 "read the regulator's nvidia move", 'says what luckey says', 'held most of them back', 'the ministries that approved',
                 # round 12 (Nov 26, 2026): wordings the two machine readers of the seventh public version found unclear or saying more than the argument
                 "fair competition for the market regulator's case [", 'none would turn the direction round', 'settle the open points', 'saved by hand and read whole',
                 'each reaching two companies', 'the same companies were also turning', 'whether about 600,000 chips are in hong kong',
                 'about 10,000 each to bytedance and tencent', 'four reported numbers', "each post is followed by its source's address",
                 'august 2026: the licensed sales', "says internet companies' clusters in the city",
                 'hongkong_stockpile',      # round 12: output 42's page was renamed (outputs/STATUS.tsv, 05:40 UTC, Nov 26, 2026)
                 # round 13 (Nov 26, 2026, core batch 15: 461 sources; Washington returned the applications, not the chips; Tianjin "as Sina
                 # carries it"; the tier words of the figure's kind doc), and wordings the readers of the eighth public version found unclear
                 '460 sources', 'chips approved and not shipped and others returned', '55% of the chips in the applications the summary records were',
                 'held as a page on sina', 'nothing here has been posted', 'before this text was written', 'annual report to the sec:',
                 'no published instruction from beijing to the companies was found', 'the short answer: yes,', 'all three are press reports from unnamed people',
                 "nvidia chips, 0:00 to 0:51, set against", 'published documents or officials']
# Round 14 (batch 16 and b16d): the old source count and the family's forms of the old third limit.
R14 = ['461 sources', 'some purchases were approved', 'some chips came in', 'some were approved', 'some came in',
       'some chips got in', 'some chips also came in']
RETIRED_WORDS += R14
RETIRED_IDS = {ln.split('\t')[0] for ln in (PROJ / 'loose_ends' / 'hkexnews_saved_ids.tsv').read_text(encoding='utf-8').splitlines() if ln.strip()}
if len(RETIRED_IDS) < 10: fail('control: the do-not-cite list is shorter than expected')
RETIRED_IDS |= {'cn-le08-moore-final-prospectus', 'cn-le29-sensetime-2025-annual-en', 'cn-media-yuyuan-thepaper', 'cn-factions-tencent-reuters-20261120-relay1',
                'cn-policy-ai-chip-evaluation', 'cn-clips-mfa-new-1', 'cn-us-lutnick-0422-coons-letter', 'cn-clips-trump-may15-wayback',
                'cn-acts-ft-lutnick-20250821-wayback', 'ms-bj-20250917-cac-6000d-engadget', 'cn-tolerate-customs-relay1',
                'cn-acts-reuters-deepseek-20260130'}      # round 10b (core batch 12): Reuters of Jan 30, 2026 is cited from its open copy on Yahoo Finance
# round 8 (core edit 7b, Nov 25, 2026; ruling R5): the copies saved from idc.com and trendforce.com, replaced today, read from their list
TERMS_IDS = {ln.split('\t')[0].strip() for ln in (PROJ / 'loose_ends' / 'terms_saved_ids.tsv').read_text(encoding='utf-8').splitlines() if ln.strip() and not ln.startswith('#')}
if len(TERMS_IDS) < 19: fail(f'control: the list of copies saved against a site\'s terms holds {len(TERMS_IDS)} ids, fewer than the 19 it had when added')
RETIRED_IDS |= TERMS_IDS
files = sorted(p for pat in ('*/*_base.txt', '*/*.md', '*/*.html', '*/thread_plain.txt', '*/timeline.txt', '*/*refs*.tsv')
               for p in HERE.glob(pat) if not p.parent.name.startswith('superseded'))
found_control = False
for p in files:
    low = p.read_text(encoding='utf-8').lower()
    if 'five limits' in low: found_control = True
    own = p.name.endswith('_base.txt') or p.name in ('thread_plain.txt', 'timeline.txt')      # my own words; built pages also carry the core's reference labels
    if own:
        for w in retired_matches(low, RETIRED_WORDS):
            fail(f'{p.relative_to(HERE)} holds the retired wording "{w}"')
    ids = set(re.findall(r'(?:cn|ms|man|cnpol)-[a-z0-9-]+', low))
    for sid in sorted(ids & RETIRED_IDS): fail(f'{p.relative_to(HERE)} holds the id {sid}, which may no longer be cited')
print(f'old wording: {len(files)} delivered files searched for {len(RETIRED_WORDS)} retired phrases and {len(RETIRED_IDS)} ids; control phrase "five limits" found: {found_control}')
if not found_control: fail('control: the search did not find a phrase that is present')
# round 9 control: the before-copies of round 9 hold the phrases round 9 retired (so the search can find them)
R9 = RETIRED_WORDS[RETIRED_WORDS.index('300 sources'):RETIRED_WORDS.index('392 sources')]      # round 10 phrases have their own control below
old9 = ' '.join(p.read_text(encoding='utf-8').lower() for p in HERE.glob('*/*.before-round9-20261125.txt'))
seen9 = [w for w in R9 if w in old9]
print(f'control: {len(seen9)} of the {len(R9)} phrases retired in round 9 are found in the before-copies of round 9 (300 and 345 sources were retired before them)')
if len(seen9) < len(R9) - 2: fail(f'control: round 9 phrases not found in the before-copies: {[w for w in R9 if w not in seen9]}')
# round 10 control: the before-copies of round 10 hold every phrase round 10 retired
R10 = RETIRED_WORDS[RETIRED_WORDS.index('392 sources'):RETIRED_WORDS.index('395 sources')]      # round 10b phrases have their own control below
old10 = ' '.join(p.read_text(encoding='utf-8').lower() for p in HERE.glob('*/*.before-round10-20261125.txt'))
seen10 = [w for w in R10 if w in old10]
print(f'control: {len(seen10)} of the {len(R10)} phrases retired in round 10 are found in the before-copies of round 10')
if len(seen10) != len(R10): fail(f'control: round 10 phrases not found in the before-copies: {[w for w in R10 if w not in seen10]}')
# round 10b control: the before-copies of round 10b (base texts, and the plain thread as it was built) hold every phrase round 10b retired
R10B = RETIRED_WORDS[RETIRED_WORDS.index('395 sources'):RETIRED_WORDS.index("fair competition for the market regulator's case [")]      # round 12 phrases have their own control below
old10b = ' '.join(p.read_text(encoding='utf-8').lower() for p in list(HERE.glob('*/*.before-round10b-20261125.txt')) + [HERE / 'scratch_round10b' / 'before' / '03_thread_thread_plain.txt'] if p.is_file())
seen10b = [w for w in R10B if w in old10b]
print(f'control: {len(seen10b)} of the {len(R10B)} phrases retired in round 10b are found in the before-copies of round 10b')
if len(seen10b) != len(R10B): fail(f'control: round 10b phrases not found in the before-copies: {[w for w in R10B if w not in seen10b]}')
# round 12 control: the before-copies of round 12 (scratch_round12/before: base texts and the plain thread as round 11 built it) hold every phrase round 12 retired
R12 = RETIRED_WORDS[RETIRED_WORDS.index("fair competition for the market regulator's case ["):RETIRED_WORDS.index('460 sources')]      # round 13 phrases have their own control below
old12 = ' '.join(p.read_text(encoding='utf-8').lower() for p in list((HERE / 'scratch_round12' / 'before').glob('*/*_base.txt')) + [HERE / 'scratch_round12' / 'before' / '03_thread' / 'thread_plain.txt'] if p.is_file())
seen12 = [w for w in R12 if w in old12]
print(f'control: {len(seen12)} of the {len(R12)} phrases retired in round 12 are found in the before-copies of round 12')
if len(seen12) != len(R12): fail(f'control: round 12 phrases not found in the before-copies: {[w for w in R12 if w not in seen12]}')
# round 13 control: the before-copies of round 13 (scratch_round13/before: base texts, the plain thread and the plain timeline as round 12 built them)
R13 = RETIRED_WORDS[RETIRED_WORDS.index('460 sources'):RETIRED_WORDS.index('461 sources')]
old13 = ' '.join(p.read_text(encoding='utf-8').lower() for p in list((HERE / 'scratch_round13' / 'before').glob('*/*_base.txt'))
                 + [HERE / 'scratch_round13' / 'before' / '03_thread' / 'thread_plain.txt', HERE / 'scratch_round13' / 'before' / '33_timeline_plain_text' / 'timeline.txt'] if p.is_file())
seen13 = [w for w in R13 if w in old13]
print(f'control: {len(seen13)} of the {len(R13)} phrases retired in round 13 are found in the before-copies of round 13')
if len(seen13) != len(R13): fail(f'control: round 13 phrases not found in the before-copies: {[w for w in R13 if w not in seen13]}')
# Excerpts from the round 14 before-copies.
old14 = ('The full argument has 21 points and 461 sources',
         'Third, some purchases were approved and some chips came in.',
         '7. Limit 3: some were approved, some came in.',
         'And, by the reports, some chips got in.',
         'Some chips also came in (question 8).')
seen14 = {w for line in old14 for w in retired_matches(line.lower(), RETIRED_WORDS)}
miss14 = [w for w in R14 if w not in seen14]
print(f'control: {len(R14) - len(miss14)} of the {len(R14)} phrases retired in round 14 are found in the old wording')
if miss14: fail(f'control: round 14 phrases not found in the old wording: {miss14}')
print('result: the folder agrees with the core in what it copies, and the retired wording is gone' if ok else 'result: FAILED')
sys.exit(0 if ok else 1)
