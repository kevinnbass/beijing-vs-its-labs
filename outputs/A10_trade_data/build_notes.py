#!/usr/bin/env python3
"""Build the two notes of this folder (ideas 34 and 42) with scripts/cn_doc_build.py, holding back saved pages' own
headlines that the project's rule d (atlas/CONFIRM9_BRIEF.txt, list d) bars as a document's name. The core keeps such
titles out through NO_TITLE in scripts/cn_argument_build.py; this script adds the ids this folder cites that the core's
set does not hold, and changes no shared file.

Run: python3 -I build_notes.py            (from anywhere; writes only the .md and .html beside each _base.txt here)

Round 11 of the outputs (Nov 26, 2026): The Next Web's page of Nov 6, 2026 (ms-bj-202611-h200-hongkong-tnw) has a headline
of the kind rule d lists, so its own title is not printed; its label names it by outlet, date and what it is.
After each build the script reads every "Page title:" the page prints and stops (exit 1) if one matches the screen BAD
below (the kinds of headline rule d lists, and approvals held back); a planted title must be caught first.
"""
import re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parents[3] / 'scripts'
HOLD = {'ms-bj-202611-h200-hongkong-tnw'}
NOTES = [(HERE / 'idea34_customs' / 'customs_figures_base.txt', 'Customs Figures Test', 'China chip policy · customs figures'),
         (HERE / 'idea42_hongkong' / 'hongkong_stockpile_base.txt', "A Check of Reuters's Report of Chips Stored in Hong Kong",
          "China chip policy · Reuters's report of chips stored in Hong Kong")]
BAD = re.compile(r'(?i)\bbans?\b|\bbanned\b|not\s+permitted|withh[eo]ld|holds? back|held back|refus|\bden(y|ies|ied)\b')
TITLE = re.compile(r'Page title: (.*?)\.(?: https?://| \(No address| Saved copy|$)', re.M)

if BAD.search('PLANTED: a regulator holds back approval') is None or BAD.search('PLANTED: a regulator eases limits') is not None:
    sys.exit('control failed: the headline screen does not tell a held-back approval from an eased limit')

CODE = ("import sys; sys.path.insert(0, %r); import cn_argument_build as B; B.NO_TITLE = set(B.NO_TITLE) | %r; "
        "import cn_doc_build; sys.argv = ['cn_doc_build.py'] + sys.argv[1:]; cn_doc_build.main()") % (str(SCRIPTS), HOLD)
for base, title, eyebrow in NOTES:
    r = subprocess.run([sys.executable, '-I', '-c', CODE, str(base), '--refs', str(HERE / 'extra_refs.tsv'), '--title', title, '--eyebrow', eyebrow])
    if r.returncode != 0: sys.exit(f'{base.name}: cn_doc_build refused (exit {r.returncode})')
    md = base.with_name(base.name.replace('_base.txt', '.md')).read_text(encoding='utf-8')
    titles = TITLE.findall(md)
    bad = [t for t in titles if BAD.search(t)]
    if bad: sys.exit(f'{base.name}: a page title the series may not print as a name: {bad}')
    print(f'{base.name}: {len(titles)} page titles printed, none matches the screen for rule d')
