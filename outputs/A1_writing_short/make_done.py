#!/usr/bin/env python3
"""Write DONE.md for A1_writing_short. Every check line and count in it is copied from build_log.txt
(written by rebuild_all.sh), so nothing in DONE.md is typed from memory. Run: python3 -I make_done.py
Stops if the log does not end with "all builds and look checks passed"."""
import re, subprocess, sys
from pathlib import Path

sys.exit('make_done.py wrote the round 1 report only. DONE.md is now written by make_done_round2.py (round 1 text kept, Round 2 added).')

A = Path(__file__).resolve().parent
log = (A / 'build_log.txt').read_text(encoding='utf-8')
if 'all builds and look checks passed' not in log.strip().splitlines()[-1]: sys.exit('build_log.txt does not end with a pass: DONE.md NOT written')
sec = {}
for p in re.split(r'(?m)^== ', log):
    if p.strip():
        head, _, body = p.partition('\n'); sec[head.split(':')[0].strip()] = (head.strip(), body.rstrip())


def block(key):
    head, body = sec[key]
    return '```\n$ ' + head.split(': ', 1)[-1] + '\n' + body + '\n```'


looks = sec['look checks (render_and_look.py --check; exit 0 required)'][1].splitlines()


def look(name):
    for i, ln in enumerate(looks):
        if f'/{name} |' in ln:
            shots = re.search(r'\| (\d+) screenshots in', ln).group(1)
            return shots, '```\n' + ln + '\n' + looks[i + 1] + '\n```'
    sys.exit(f'no look line for {name}')


def num(pattern):
    m = re.search(pattern, log)
    if not m: sys.exit(f'not in the log: {pattern}')
    return m.group(1)


when = subprocess.run(['date', '-u', '+%b %-d, %Y, %H:%M UTC'], capture_output=True, text=True).stdout.strip()
AR = 'argument/argument_refs.tsv'
RL = 'python3 scripts/render_and_look.py'
s3, l3 = look('03_thread/thread.html'); s4, l4 = look('04_right_and_too_flat/right_too_flat.html')
s5, l5 = look('05_questions_and_answers/questions_answers.html'); s8, l8 = look('08_what_would_change/what_would_change.html')
w4, r4 = num(r'right_too_flat: about (\d+) words'), num(r'right_too_flat: about \d+ words; (\d+) sources')
n_posts = num(r'thread: (\d+) posts')
n_rec = num(r'timeline: (\d+) records')
kept, off = num(r'quoted phrases: \d+ in the table; (\d+) found'), num(r'(\d+) not found, marks taken off')

doc = f"""# DONE: A1_writing_short (ideas 3, 4, 5, 8 and 33)

Written {when}, by the agent A1 (Claude). All five ideas are made. Nothing was published, posted or sent.
Every check line below is copied by a script (`make_done.py`) from `{A}/build_log.txt`, the log of the last full
rebuild (`bash {A}/rebuild_all.sh`).

Each text was built with `scripts/cn_doc_build.py`, so every quotation and every hidden check line was found in the
saved copy of its source, and the builder's planted false quotation was rejected. A quotation that is found shows what
the source says, not that it is true.

## Idea 3: a thread (made)

- **Open:** `{A}/03_thread/thread.html`
- **To paste from:** `{A}/03_thread/thread_plain.txt` (the {n_posts} posts numbered 1/{n_posts} to {n_posts}/{n_posts}, each followed by its
  source's address on its own line; then the note on images; then the character counts).
- **Other files:** `thread.md`, `thread_base.txt` (the text), `make_thread_plain.py` (builds everything),
  `char_counts.tsv`.
- **Rebuild:** `python3 -I {A}/03_thread/make_thread_plain.py`
- **Build check and character counts** (each post counted with its number in front, as it would be pasted):

{block('idea 3')}

- **Look check** ({s3} screenshots opened, at 1280 px and 390 px):

{l3}

- **Images:** post 1 takes `figure/beijing_vs_labs_top.png`;
  post 6 takes `figure/beijing_vs_labs_strip.png`. No image was made.
- **What it does not show:** one source for each claim, not the argument's full list. Post 5 has two sources (two
  Reuters reports), so it has two address lines. The last post is a shorter form of the argument's last sentence and
  has no address. The three other reported numbers of the argument's table are left out for length.
- **To know:** the "X weighted" count uses X's counting rule as I know it (most characters count 1, Chinese and
  similar count 2, an address counts 23). That rule is from my general knowledge, not from a saved page. The posts hold
  only characters that count 1, so the two counts are the same. The first image is taller than it is wide.

## Idea 4: "Right, and too flat" (made)

- **Open:** `{A}/04_right_and_too_flat/right_too_flat.html`
- **Other files:** `right_too_flat.md`, `right_too_flat_base.txt`, `extra_refs.tsv` (one added source), `build.sh`.
- **Rebuild:** `bash {A}/04_right_and_too_flat/build.sh`
- **Build check:**

{block('idea 4')}

- **Look check** ({s4} screenshots opened, at 1280 px and 390 px):

{l4}

- **Shape:** the table has three columns: his words with the time, then the two columns asked for (what the record
  bears out; where his words are too flat). The first column is there so that each row says which words it judges. On
  a phone the cells stack, so each cell starts with its own label in bold.
- **What it does not show:** it follows `ASSESSMENT.md` section 5 and the argument's points 16, 18 and 19, and uses
  point 17 and point 20 only for the two limits they state. Its words at 0:44 to 0:46 are left out of this
  project. It does not judge his argument about
  what the United States should do. The words are from the speech program's transcript; nobody has checked them by ear.
- **To know:** it is one web page of about {w4} words (the builder's count), more than one sheet if printed with its
  {r4} references. One added source: a transcript site's text of the whole interview (`cn-clips-singju-luckey`), used
  for the sentence he says just before the clip. That page's own title has two long dashes; they show in the
  reference list.

## Idea 5: "Did China ban Nvidia? Questions and answers" (made)

- **Open:** `{A}/05_questions_and_answers/questions_answers.html`
- **Other files:** `questions_answers.md`, `questions_answers_base.txt`, `extra_refs.tsv` (one added source),
  `build.py` (builds, then counts questions, sentences and sources).
- **Rebuild:** `python3 -I {A}/05_questions_and_answers/build.py`
- **Build check and shape check** (ten questions; each answer at most three sentences; each with a source):

{block('idea 5')}

- **Look check** ({s5} screenshots opened, at 1280 px and 390 px; this is the second render, made after one header
  note was corrected):

{l5}

- **What it does not show:** one to three sources for each answer. Nvidia's share of the market is not among the ten
  questions. Chinese sources are given in English without the Chinese words; the English is ours.
- **To know:** one added source, the foreign ministry's press conference of Nov 9, 2026 (`cn-clips-mfa-new-1`), for
  the spokesman's answer about the 600,000 chips.

## Idea 8: "What would change the answer" (made)

- **Open:** `{A}/08_what_would_change/what_would_change.html`
- **Other files:** `what_would_change.md`, `what_would_change_base.txt`, `extra_refs.tsv` (seven added sources),
  `build.sh`, `check_filing_feed.py` (run by `build.sh` before the build; see "To know").
- **Rebuild:** `bash {A}/08_what_would_change/build.sh`
- **Build check:**

{block('idea 8')}

- **Look check** ({s8} screenshots opened, at 1280 px and 390 px; the whole page, rendered with `--max-tiles 12`;
  this is the fourth render, made after the layout, one heading and items 7 and 8 were changed):

{l8}

- **What it holds:** ten documents in four groups (from Beijing; figures; from the United States; recordings and
  articles). For each: what it would show, where it would be, what is held now instead. Then a section on which other
  ideas of the project are looking for five of them, and a last section on what is not open.
- **What it does not show:** it does not say that any of the ten exists; a header note says so. Where each would be
  kept is from my general knowledge of how such bodies publish, not from a saved page, unless a reference is given;
  the header note says that too. I searched the web for none of them. It does not report what ideas 34, 37, 38, 40
  and 42 found: they were still running when it was written.
- **To know:** seven added sources, each read in its saved copy. Five were already saved: the Customs Law
  (`cn-policy-customs-law-wayback`), the foreign ministry's press conference (`cn-clips-mfa-new-1`), Nvidia's written
  results commentary for the quarter to Oct 25, 2026 (`cn-counter-b17-1`), Senator Coons's release of May 5, 2026
  (`cn-us-lutnick-0422-coons-letter`) and the transcript site's text of Luckey's interview (`cn-clips-singju-luckey`).
  Two were saved on Nov 23, 2026 by the lane that works on ideas 37 and 38, while I was writing: Nvidia's own list of
  its filings for 2026 (`cn-o38-nvda-feed-secfilings-2026-b`) and the Senate committee's page for the hearing
  (`cn-o37-senate-hearing-page-b`). I use them only for what the pages themselves show. Item 7 says the list shows no
  quarterly report filed after Aug 26, 2026: `check_filing_feed.py` reads the saved list and stops the build if that is
  not so (its two lines are in the build check above). The list's address carries a site key, so the reference gives
  no address.

## Idea 33: the timeline as plain text (made)

- **Open:** `{A}/33_timeline_plain_text/timeline.txt` (plain lines) and
  `{A}/33_timeline_plain_text/timeline.md` (the same {n_rec} records as a table).
- **Other files:** `gen_timeline.py` (makes everything from `figure/figure_events.tsv`; nothing retyped),
  `timeline_base.txt`, `timeline_extra_refs.tsv`, `quote_marks_report.tsv`.
- **Rebuild:** `python3 -I {A}/33_timeline_plain_text/gen_timeline.py`
- **Build check and counts:**

{block('idea 33')}

- **No page to look at:** this idea is two text files, built with `--md-only`, so there is no look check.
- **Fields:** date is the table's `shown_as`; who is the table's `lane` (the row of the figure the record sits in,
  not always the speaker); what is the table's `text`; source is the table's `source` followed by its tier, taken from
  the table's `kind`; address is the table's `address`. Order: the table's `date`, then its record number.
- **What it does not show:** the source's own words for each record (they are in `figure/figure_data.txt`), and the
  saved ids.

## For the session that owns the project

1. **{off} lines of the figure put quotation marks round our English for Chinese words.** They are named in the
   idea 33 check lines above (the words "backdoors", "backdoor", "guiding" and "mainly") and in
   `{A}/33_timeline_plain_text/quote_marks_report.tsv`. The words are not in the saved copies, which are Chinese. In
   the timeline the script takes the marks off. The figure itself still shows them; I did not touch it. The other
   {kept} quoted phrases in the table were all found.
2. **`ASSESSMENT.md` section 5 dates Luckey's interview Nov 18, 2026.** The saved transcript page
   (`cn-clips-singju-luckey`) says "DealBook Summit 2026" and carries its own page date, Nov 20, 2026. A search of its
   text for a day from Nov 10 to Nov 19 found none (the same search finds "November 20"), so my texts give no day for
   the interview.
3. **Look records are outside my folder.** `render_and_look.py` wrote them where it always does,
   `research/looks/`: eight folders. Four hold the looks that count (`thread-768116d1c8c3`,
   `right_too_flat-89335d02dcfd`, `questions_answers-ffd2e597e4d5`, `what_would_change-8e3543bbc0a6`); four hold
   earlier renders that a later one replaced (`questions_answers-6dcb0c0ddbdc`, `what_would_change-59b95d865132`,
   `what_would_change-728f092cd950`, `what_would_change-4c2adfbc908d`). I wrote nothing else outside this folder, and
   I did not change `outputs/STATUS.tsv` or `outputs/VERIFY.tsv`.
4. **To check a look again:** `{RL} --check <page> --with <its base file> <its extra_refs.tsv, if it has one> {AR}`
   (the thread has no `extra_refs.tsv`). The exact commands are in `{A}/rebuild_all.sh`.

## Not done, and why

Nothing in the task was left undone. Outside this task and still open: neither clip has been checked by ear.
"""
(A / 'DONE.md').write_text(doc, encoding='utf-8')
print(f'DONE.md written: {len(doc.split())} words; check lines copied from build_log.txt')
