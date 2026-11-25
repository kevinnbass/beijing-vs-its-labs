# How to keep the tracker up to date

Draft by Claude, Anthropic's model.

The page is `tracker.html` in this folder. It is built from four files in `data/`: `figure_data.txt` (the records),
`tracker_log.tsv` (the dated log), `state_of_play.txt` (the state of play at the top, added Nov 23, 2026) and
`house_licence_table.tsv` (a copy of the project's `tables/house_licence_table.tsv`, which the state of play counts).
Never edit `tracker.html` by hand: a rebuild replaces it.

## 0. Bring the state of play up to date

Edit `data/state_of_play.txt` (its header explains the markup): change the `@title` date, and add, change or drop
items. Each quotation must stand in the saved copy of an id cited in its item; each number must stand in a quotation
or hidden check of its item, or be a count the build makes (`{{RWA}}` and the others in `house()` in `build.py`), or
be listed with `!OURS` and its origin. For a negative ("lists none"), give a `!NOT` line and a `!!` line that shows the
same check can find a hit in that kind of page. Add a log line saying what changed, then run `python3 -I build.py`.
The next likely changes: Nvidia's 10-Q for the quarter ended Oct 25, 2026 (save it first, then replace the first
item of "The newest facts" and the first item of "What would change the answer next"); any published Chinese rule;
an end to the antitrust case.

Folder: `outputs/A9_repository_and_tracker/32_tracker/`

## 1. Save the page first

A record needs a saved copy under `research/primary/<id>/`. Save the page with the project's
`scripts/fetch.py` (or take a hand-saved PDF in as before), then read the saved copy: the date, who speaks, and the
exact words you will quote.

## 2. Add the record

Run this in the folder above, with every value in single quotes:

```
python3 -I add_record.py --date 2026-12-01 --row BH --kind press --id <saved id> \
  --line '<our line, one sentence>' --source '<the source as shown>' --words '<exact words of the saved page>'
```

- `--row`: `BH` Beijing holds Nvidia back, `BL` Beijing lets Nvidia in, `CN` the companies reach for Nvidia,
  `CH` the companies turn to home-made chips.
- `--kind`: `doc` a government document or an official on the record (filled mark), `rec` a company, or a named person outside
  government, on the record (filled mark), `press` a press report citing unnamed people (open mark).
- `--date`: the date of the act where the page states it, otherwise the date of the report. Read it in the page.
- Optional: `--english '<our English for Chinese words>'` (no quote marks in it), `--address '<address>'` where the
  saved copy's own address is missing or cut short, `--label 'Summer 2025'` to show words instead of the day.

The command refuses the record, and changes nothing, when the words are not in the saved copy, when words between
quote marks or a number in our line are not in it, when the date is not written in the page's readable text (give
`--date-not-in-page '<reason>'` if that is right, as for a label), or when the same words already stand in that row.
When it takes the record it appends it to `data/figure_data.txt`, writes a line dated today (UTC) into
`data/tracker_log.tsv`, and rebuilds the page.

To try a record without touching the real files: `python3 -I test_add_record.py` shows the pattern (it works on a
copy under `scratch_test/`), or pass `--dir <a copy of this folder's data>`.

## 3. Look at the page before calling it done

```
python3 scripts/render_and_look.py tracker.html \
  --with data/figure_data.txt data/tracker_log.tsv data/state_of_play.txt data/house_licence_table.tsv build.py \
  --widths 1280,390 --max-tiles 40
```

Open every screenshot it lists, then run the same command with `--looked ... --saw N --note "what you saw"`, and
finish with `--check tracker.html --with` and the same five files (exit 0).

## 4. Correct a record

Edit its block in `data/figure_data.txt` (the file's header explains the lines). Then add one line at the END of
`data/tracker_log.tsv`: today's date, `correction` (or `wording`, or `note` for a remark that changes no record), the
saved id, the number of records, what changed and why, and hidden checks for any date or number the line states (the
file's header explains the columns and the three kinds of check). Then run
`python3 -I build.py`. It writes the page only if every quotation, number and check is found in its saved copy and
the log's last count equals the number of records.

## 5. What the build prints

- `cn_has.py on quotes.tsv: exit 0`: every string in `quotes.tsv` was found in its saved copy.
- `records N (...)`: the counts shown on the page come from this run, not from typing.
- `date screen`: how many record dates are written in their saved pages. For records already in the list this is a
  report; the page's last note names the ones not found.

## 6. Not done by these scripts

They do not publish, upload or send anything. The figure (`../../../figure/`) and the argument are separate files
with their own builders: a record added here does not appear there.
