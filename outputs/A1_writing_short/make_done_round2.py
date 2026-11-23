#!/usr/bin/env python3
"""Write DONE.md for A1_writing_short after round 2: the round 1 report as it stood, then a section "Round 2".

Run: python3 -I make_done_round2.py
Reads   round1_superseded/DONE.md   the round 1 report, kept byte for byte
        build_log.txt               written by rebuild_all.sh (every check line and count below is copied from it)
        verify_round2.txt           the output of scripts/cn_outputs_verify.py A1_writing_short, if it has been run
Writes  DONE.md
It can be run before the look pass is finished: it then says which pages are still to be looked at.
"""
import re, subprocess, sys
from pathlib import Path

sys.exit('make_done_round2.py wrote the report up to round 2 only. DONE.md now ends with a hand-appended "Round 4" section: append later rounds with an editor, and do not run this script (it would drop that section).')

A = Path(__file__).resolve().parent
log = (A / 'build_log.txt').read_text(encoding='utf-8')
r1 = (A / 'superseded_round1' / 'DONE.md').read_text(encoding='utf-8')
sec = {}
for p in re.split(r'(?m)^== ', log):
    if p.strip():
        head, _, body = p.partition('\n'); sec[head.split(':')[0].strip()] = (head.strip(), body.rstrip())
for k in ('core copies', 'idea 3', 'idea 4', 'idea 5', 'idea 8', 'idea 33'):
    if not sec[k][1].endswith('exit=0'): sys.exit(f'build_log.txt: "{k}" did not pass: DONE.md NOT written')


def block(key):
    head, body = sec[key]
    return '```\n$ ' + head.split(': ', 1)[-1] + '\n' + body + '\n```'


def num(pattern):
    m = re.search(pattern, log)
    if not m: sys.exit(f'not in the log: {pattern}')
    return m.group(1)


PAGES = [('Idea 3, thread', '03_thread/thread.html'), ('Idea 4, right and too flat', '04_right_and_too_flat/right_too_flat.html'),
         ('Idea 5, questions and answers', '05_questions_and_answers/questions_answers.html'), ('Idea 8, what would change', '08_what_would_change/what_would_change.html')]
looks = sec['look checks (render_and_look.py --check; exit 0 required)'][1].splitlines()
state, look_lines = {}, []
for name, f in PAGES:
    ln = next((x for x in looks if f'/{f}' in x), None)
    if ln is None: sys.exit(f'no look line for {f}')
    done = ln.startswith('LOOKED:')
    shots = re.search(r'\| (\d+) screenshots in', ln).group(1) if done else '0'
    state[f] = done
    look_lines.append((name, f, done, shots, ln))
todo = [f for _, f, d, _, _ in look_lines if not d]
all_pass = 'all builds and look checks passed' in log.strip().splitlines()[-1]
vf = A / 'verify_round2.txt'
verify = vf.read_text(encoding='utf-8').strip() if vf.is_file() else ''
verify_ok = bool(verify) and ' 0 stale' in verify and '5/5 ok' in verify
complete = all_pass and not todo and verify_ok
when = subprocess.run(['date', '-u', '+%b %-d, %Y, %H:%M UTC'], capture_output=True, text=True).stdout.strip()
n_posts, longest = num(r'thread: (\d+) posts'), num(r'longest post: (\d+) characters')
pts, srcs = num(r'argument, counted by script: (\d+) points'), num(r'argument, counted by script: \d+ points, (\d+) sources')
q_all, q_kept, q_off = num(r'quoted phrases: (\d+) in the table'), num(r'quoted phrases: \d+ in the table; (\d+) found'), num(r'(\d+) not found, marks taken off')
n_rec = num(r'timeline: (\d+) records')
shots_total = sum(int(x[3]) for x in look_lines)

if complete:
    status = 'Round 2 is complete: every text is rebuilt and checked, and every screenshot of the four pages was opened at both widths.'
else:
    bits = []
    if todo: bits.append('still to be looked at again: ' + ', '.join(f'`{f}`' for f in todo))
    if not verify: bits.append('the verifier has not been run on the final files yet')
    elif not verify_ok: bits.append('the verifier does not yet report 5/5 base files ok and 0 stale looks')
    status = 'Round 2 is NOT complete. The corrected texts are built and their quotation checks pass. Open: ' + '; '.join(bits) + '.'

look_md = '\n'.join(f'- **{name}:** ' + (f'looked at, {shots} screenshots, every one opened.' if d else 'STILL TO LOOK AT (the page changed in this round; the round 1 look is stale).') + f'\n\n```\n{ln}\n```\n' for name, f, d, shots, ln in look_lines)
verify_md = ('```\n$ python3 -I scripts/cn_outputs_verify.py A1_writing_short\n' + verify + '\n```') if verify else 'Not run on the final files yet.'

r2 = f"""## Round 2

Written {when}, by the agent A1 (Claude). {status}

The core files were corrected after round 1 (`outputs/ROUND2.md`).
This section replaces the check lines, counts and look records of round 1 above. The files to open are the same:

- Idea 3: `{A}/03_thread/thread.html`, and to paste from `{A}/03_thread/thread_plain.txt`
- Idea 4: `{A}/04_right_and_too_flat/right_too_flat.html`
- Idea 5: `{A}/05_questions_and_answers/questions_answers.html`
- Idea 8: `{A}/08_what_would_change/what_would_change.html`
- Idea 33: `{A}/33_timeline_plain_text/timeline.txt` and `timeline.md`

### What changed, by the items of ROUND2.md

1. **The Shanghai reply.** Thread post 3, the sheet's second row and question 4 now say "dated Apr 30, 2025 (published
   Nov 10, 2025)", each with a check line for both dates. The timeline's record now stands at Apr 30, 2025.
2. **The company's question to the commerce ministry.** Question 7 and item 1 of "what would change" now say it was
   left on Jul 30, 2026, that the reply came on Aug 19, 2026, and that the reply speaks only of what exporters must do.
   The timeline's record now stands at Jul 30, 2026. The thread and the sheet do not use it.
3. **Luckey's quotation, split.** Thread post 1, the sheet's first two rows and item 9 of "what would change": the
   first sentence is quoted from the speech program's transcript, the second from the text of the post that carries
   the clip. No file joins them. Each says nobody has checked the words by ear.
4. **Micron.** Item 2 of "what would change" now says the cyberspace regulator's review office published its
   conclusion, and that operators "should stop buying". The timeline's first record is regenerated. Nothing else names Micron.
5. **About 750,000.** Not shown in any of my outputs. Nothing to change.
6. **The 2026 market share.** Not shown in any of my outputs. Nothing to change.
7. **New lines on the record.** Nvidia, May 20, 2026 ("we are uncertain whether any imports will be allowed into the
   country"): the sheet's fourth row and item 1 of "what would change". Nvidia's own call transcript for the quarter
   ended Oct 25, 2026 now stands where Reuters's wording stood: items 5 and 7 of "what would change", and a line under
   "What these answers leave out" in the questions. No output says why Nvidia stopped. Tencent's two lines are not used.
8. **The hearing and the 10-Q.** Items 7 and 8 of "what would change" now say what was looked for and found on
   Nov 23, 2026: the report was not yet filed; the committee's page offers the video and prepared remarks and no
   transcript; by a speech program's timing the exchange begins at about 1:17:20.
9. **The Hong Kong report.** "Reuters, Nov 5, 2026" stays. The thread and the questions add one line: the copy held is
   CNA's page, dated Nov 6, 2026 (checked in the page: "06 Nov 2026 11:47AM").
10. **Beijing's 2024 plan.** Not in my outputs. Nothing to change.
11. **Luckey's interview.** No output gave a day for it. Nothing to change.
12. **Quote marks on our own English.** The timeline is regenerated from the present `figure/figure_events.tsv`: {q_all}
    quoted phrases, {q_kept} found in their saved copies, {q_off} taken off (round 1 took 4 off). This closes the first
    note of round 1 "For the session that owns the project"; item 11 closes its second note.
13. **Counts.** The thread and the questions now say the argument has {pts} points and {srcs} sources. Both build scripts
    count these from the argument's files and stop if the text says otherwise. No output prints one of the argument's
    reference numbers.
14. **Other builders' findings.** Used in "what would change" only, one line each, in lines that begin "Looked for":
    customs figures (item 5), the Hong Kong record (item 6), the hearing (item 8), the clips (item 9). The page names
    the five notes by folder and file, under `outputs/`:
    `A10_trade_data/idea34_customs/customs_figures.html`, `A10_trade_data/idea42_hongkong/hongkong_stockpile.html`,
    `A11_records/idea37_hearing_record/hearing_record.html`, `A11_records/idea38_nvidia_10q/nvidia_10q.html`,
    `A8_clips/40_checked_by_ear/LISTEN_SHEET.html`. Provincial targets and results calls are not used.

Also new: `check_core_copies.py` checks that the sentences three of my texts copy from the argument still equal the
argument's own text. `rebuild_all.sh` runs it first.

One fault of my own in this round, found by the render and fixed: the first round 2 render of "what would change"
scrolled sideways at 390 px (635 px too wide), because its list of notes held long file paths. The list now gives
folder / folder / file, the page was rendered again, and that second render is the one looked at and recorded.

### The thread's characters, recounted by script

{n_posts} posts; the longest is {longest} characters; the limit is 280. Post 1 was rewritten for the split quotation and
post 3 for the two dates. The counts are in `{A}/03_thread/char_counts.tsv` and at the end of `thread_plain.txt`.

{block('idea 3')}

### Check lines of the other builds

{block('core copies')}

{block('idea 4')}

{block('idea 5')}

{block('idea 8')}

{block('idea 33')}

### Looks

Every page changed in this round, so every page was rendered again at 1280 px and 390 px, and every screenshot of
the final render was opened ({shots_total} in all). The lines are those of
`render_and_look.py --check` with the same `--with` list as the render (the page's base file, its `extra_refs.tsv`
where it has one, and `argument/argument_refs.tsv`).

{look_md}
The timeline (idea 33) is two text files and has no page to look at.

### The owner's verifier

{verify_md}

### What is still open

{"- Nothing in the task." if complete else "- " + status}
- Nobody has listened to Luckey's clip or to the hearing's video. Every text says so where it quotes them.
- Nvidia's report for the quarter ended Oct 25, 2026 was not yet filed on Nov 23, 2026. `check_filing_feed.py` reads
  the list saved that day; it does not fetch a new one. When a later list is saved, item 7 must be read again.
- The "Looked for" lines of "what would change" rest on other builders' notes. I read the notes; I did not check
  them against their sources.

### For the session that owns the project

1. **The Nov 5 dateline is not in the copy the argument cites.** The CNA page [cn-clips-evidence-1] shows only its own
   date, "06 Nov 2026 11:47AM". The Reuters dateline stands in the Yahoo copy [cn-clips-reuters-hongkong-yahoo]:
   "Nov 5 (Reuters) - About 600,000". That id is not in `argument/argument_refs.tsv`. I changed nothing in the core files.
2. **A folder of round 1 copies.** `{A}/round1_superseded/` holds the round 1 report, build log, plain thread and
   character counts. The plain thread there still has the joined quotation: do not paste from it.
3. **Look records** are in `research/looks/`, where `render_and_look.py` puts them. The four that
   count are named in the lines under "Looks" above. The folders of round 1, and `what_would_change-02918a27fbb7`
   (the round 2 render that scrolled sideways), are stale and left as they are.
4. **The verifier writes** `outputs/VERIFY.tsv` each time it runs; I ran it as ROUND2.md says. I changed nothing else
   outside my folder.
"""
head, _, rest = r1.partition('\n')
doc = head + '\n\n**Round 2, at the end of this file, replaces the check lines, counts and look records of round 1 below. Read it first.**\n' + rest.rstrip('\n') + '\n\n' + r2
(A / 'DONE.md').write_text(doc, encoding='utf-8')
print(f'DONE.md written: round 1 text kept, Round 2 section added; complete={complete}; still to look at: {len(todo)} page(s); verifier line present: {bool(verify)}')
