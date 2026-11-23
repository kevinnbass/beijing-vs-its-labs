The record as table files
China chip policy: did Beijing's chip policy pull against China's own AI companies?
Draft by Claude, Anthropic's model. Local; not published.

Made by build.py in this folder from the project's own files (figure/figure_data.txt, figure/figure_events.tsv,
argument/argument_base.txt, argument/argument_refs.tsv, tables/). Run "python3 -I build.py" to make them again.
All files are UTF-8 without a byte-order mark. In a spreadsheet program, open them through its import step and
choose UTF-8, or the Chinese will not show correctly.

FILES
  records.csv      61 dated records, 16 columns, comma-separated
  records.tsv      the same 61 records, tab-separated (no field holds a tab or a line break)
  references.csv   the 209 sources of the argument (ARGUMENT_referenced.md), 8 columns
  quotes.tsv       saved id and the source's own words for each record: the input of the quotation check
  tables/          19 plain tables copied from the project's tables folder (listed at the end)
  build.py         the script

COLUMNS OF records.csv AND records.tsv
  n              the record's mark number in the figure (figure/beijing_vs_labs.html), 1 to 61
  date           the date as year-month-day. The date of the act where the page gives it, otherwise of the report
  date_shown     the date as the figure prints it
  date_exact     yes, or no where the source gives only a season or a month and the day in "date" is a placing
                 for the figure, not a fact (2 records: see date_shown)
  who            whose conduct the record is about: Beijing, or the companies. It is not who speaks: see source
  direction      toward Nvidia, or away from Nvidia (toward home-made chips)
  figure_row     the figure's own name for the row the record stands in
  kind           doc, rec or press
  kind_meaning   doc: a government document or an official on the record
                 rec: a company, or a named person outside government, on the record (a filing, results, a named executive or analyst)
                 press: a press report citing unnamed people
  on_the_record  yes for doc and rec; no for press
  our_line       our one-line summary, as shown in the figure. Our words, not the source's
  source         the source as the figure names it
  source_words   the source's own words, exact. Chinese where the page is Chinese
  our_english    our English for Chinese source words. Ours, not an official translation. Empty where the
                 source words are English (23 records have it)
  address        where the page is, or was, on the web
  saved_id       the name of the saved copy (research/primary/<saved_id>)

COLUMNS OF references.csv
  number         the reference number in ARGUMENT_referenced.md, 1 to 209
  kind           one of: DOC, OFF, FIL, REC, PRESS, COUNT, CLIP, PUB, NAMED, ACCT, NOTICE
  kind_meaning   as the argument's builder words each kind:
                 DOC: Chinese state document
                 OFF: Official document, or an official on the record
                 FIL: Company filing or statement
                 REC: Press report of words spoken on the record
                 PRESS: Press report citing unnamed people
                 COUNT: Research firm's count, through the press
                 CLIP: Caption track or machine transcript, not checked by ear
                 PUB: Published commentary or statement (state media, industry body)
                 NAMED: Named person on the record
                 ACCT: A named newspaper's account of a state document
                 NOTICE: An institution's own published notice
  on_the_record  yes for DOC, OFF, FIL, REC, PUB, NAMED, ACCT, NOTICE; no for PRESS, COUNT, CLIP
  label          what the source is, as the argument's reference list words it
  page_title     the saved page's own title, where the record holds one
  address        the address; empty where none is given, for the reason in the label (1 source)
  saved_id       the name of the saved copy. An id that begins "clip-" is not a folder (clip-luckey): it
                 stands for a machine transcript in transcripts_two_clips.md, which nobody has checked by ear

COUNTS (taken from the files by build.py, not typed)
  Records: 61. About Beijing, away from Nvidia: 24. About Beijing, toward Nvidia: 13.
  About the companies, toward Nvidia: 14. About the companies, away from Nvidia: 10.
  By kind: doc 22, rec 14, press 25. So 36 records are on the record and 25 are press reports citing unnamed people.
  References: 209. DOC 52, OFF 43, FIL 36, REC 19, PRESS 37, COUNT 3, CLIP 6, PUB 9, NAMED 1, ACCT 1, NOTICE 2.
  On the record: 163. Press reports citing unnamed people, counts, captions or machine transcripts: 46.

CHECKS THE SCRIPT MADE BEFORE WRITING
  The two figure files hold the same 61 records, one to one, with the same line of ours.
  scripts/cn_has.py on quotes.tsv: 61 quotations checked, 61 found, 0 not found; controls behave
  The reference numbers equal those printed in ARGUMENT_referenced.md.
  Each table was read back and equals what was written.

READ WITH CARE
  A quotation that is found shows what the source says, not that it is true.
  The two tiers are not the same kind of evidence. A press record (kind press) rests on unnamed people. Beijing's
  instructions to companies, the customs checks and most of the numbers are of that kind: reported, not published policy.
  A record in a Beijing row can be the words of someone else about Beijing (a company's filing, a US official).
  23 records quote Chinese texts (all of them documents or people on the record); the English beside them is ours.
  Not in these files: the 222 further checked lines of the figure's data file, most of them the quotations
  behind the numbers in the figure's panels (they are in
  figure/figure_data.txt, on the lines that begin with "!"), and the reference lists of the two tier files.

PLAIN TABLES (tables/)
  These 19 tables were made on Nov 23, 2026 by the project's research agents, each from saved pages, and are
  the project's own (the folder tables/ beside the argument). They are copied here so that the record can be read in
  a spreadsheet. All 19 are byte for byte the project's tables (build.py compares each copy's sha256 with the
  project's after writing; each is given below). Nothing in them is changed here. Their quotations were checked by the
  agents who made them, not again here.
  The tables were made before the argument's last rebuild: a table can cite a saved copy the argument has since
  replaced with a better one (the argument's reference list is the later word). Under 4 of the tables a
  "Read with care" line says which rows cite a saved copy the project no longer cites, and which column describes an
  earlier build of the argument; all such lines are computed by build.py. Rows of different tables count
  different things. Do not join them into one series. Each table begins with its makers' own notes, on lines that
  start with "#"; a program reading a table should skip those lines.

  tables/chip_evaluations.tsv   180 rows, 5 columns
      What it is: The products in the security-and-reliability evaluation announcements saved from the China Information Technology Security Evaluation Center's site, one row per product per announcement.
      Columns: saved_id, title, page_date, category, cells
      Copy: byte for byte the project's table (sha256 7c01eee412ccaf5efaf22738497f17215258c04e3d103854002262b38c56f076).
  tables/house_licence_table.tsv   54 rows, 10 columns
      What it is: The Commerce Department's table of licence applications for Nvidia's H200 and AMD's MI325X, with their status on May 11, 2026, as the House Foreign Affairs Committee made it public on Nov 19, 2026; one row per application.
      Columns: row, page, date_submitted, exporter, consignee, value, chip_count, status, location, group
      Copy: byte for byte the project's table (sha256 f4041b78a957a6788998843d6ee425b523dffb41b5b3cefc413e754aabe0a674).
  tables/labs_said.tsv   57 rows, 10 columns
      What it is: What China's AI companies said about chip supply on results calls and in filings, January 2025 to November 2026.
      Columns: company, date, event, speaker, title, source_kind, exact_words, saved_id, cut, note
      Copy: byte for byte the project's table (sha256 4f94eebf1fb0eeb9410c38b195bb02d864ace807e489e20de04032d31cf48074).
  tables/labs_said_more.tsv   23 rows, 10 columns
      What it is: The same for two more companies, iFlytek and SenseTime.
      Columns: company, date, event, speaker, title, source_kind, exact_words, saved_id, cut, note
      Copy: byte for byte the project's table (sha256 da25c25b4568ab8b38a7c54d7c445206a6d5c7be8f53145b16528b4019eaaa67).
  tables/local_vouchers.tsv   20 rows, 11 columns
      What it is: Local rules that pay part of the bill for computing: who issued each, when, and the rate for home-made and for other computing.
      Columns: body, level, date, document, rate_home, rate_other, kind, words, saved_id, copy, cuts
      Copy: byte for byte the project's table (sha256 9c7faba761f253f0ca5445f6eab06a01a912f8e5b9daa43fb0238c79c492d9c7).
  tables/local_vouchers_more.tsv   33 rows, 11 columns
      What it is: More such local rules, found in a second search.
      Columns: body, level, date, document, rate_home, rate_other, kind, words, saved_id, copy, cuts
      Copy: byte for byte the project's table (sha256 6ef00c7bd5a590642d34264210e8dbf1514efc72693a16382e2692fa0b44ea9c).
  tables/market_numbers.tsv   115 rows, 16 columns
      What it is: Published market numbers (shares, shipments, market sizes), one row per number. The column family names the measure; rows of different families are different measures.
      Columns: row_id, family, measure, geography, period, supplier_or_group, value, unit, counted_by, route, page_date, saved_id, words, tier, cuts, note
      Copy: byte for byte the project's table (sha256 e9acdce1221d74c973d651e23d6af7db4c5d4152ecf30cd90315547011d03362).
  tables/nvidia_china_revenue.tsv   26 rows, 7 columns
      What it is: Nvidia's revenue from customers in China, Hong Kong included, period by period, from its own filings.
      Columns: period, period_end, basis, value_musd, source, how, check
      Copy: byte for byte the project's table (sha256 512bd6066ad6ce3462a9385f50e77ab585cfeac3ae337bd9d1caff40f96c92fc).
  tables/nvidia_wording_by_filing.tsv   107 rows, 8 columns
      What it is: Nvidia's own sentences on China, filing by filing and call by call.
      Columns: date, period_end, document, saved_id, topic, speaker, words, note
      Copy: byte for byte the project's table (sha256 9362c6448f642301d0fe2a57eee96c8e56f1bafb843f006f993dd040e9a98728).
  tables/press_originals.tsv   34 rows, 10 columns
      What it is: For each press report the argument cited at an earlier build: whether the copy held is the publisher's own page or another outlet's.
      Columns: ref, saved_id_cited, report, date_of_report, through_a_relay, copy_held, original_held, other_copies_held, best_copy_held, best_copy_available_and_note
      Copy: byte for byte the project's table (sha256 d0500699d4d1bbba19473c849ccd7edc2ad847ff4bc07db300fbf76a8ec72a15).
      Read with care: 1 row(s) cite ms-bj-20260114-customs-h200-standard, a source the figure no longer cites; outputs/ROUND4.md names cn-acts-reuters-customs-20260114 in its place; the argument itself still cites ms-bj-20260114-customs-h200-standard as reference 132.
      Read with care: its column "ref" gives the present reference numbers of the argument; 3 of the 34 rows keep a report the argument no longer cites (marked "not cited now"); press references added to the argument later are named in the table's own comment line.
  tables/procurement_records.tsv   41 rows, 14 columns
      What it is: Purchase records: the telecom carriers' central purchases, awards that name Nvidia cards, and tenders that require home-made chips.
      Columns: part, date, buyer, project, stage, quantity, value, chip_family_stated, nvidia, home_made, source_kind, saved_id, exact_words, cuts
      Copy: byte for byte the project's table (sha256 fb1e54dfbc02fa7e2eb8dbd81fbbe0da00f52cad8ddde9477d974c6cc7eada18).
  tables/provinces_31.tsv   31 rows, 10 columns
      What it is: The 31 provincial-level governments: whether a published plan sets a share for home-made computing hardware, in the document's own words.
      Columns: government, result, kind_of_document, binding_or_expected, documents_issuers_dates, exact_words, rests_on, saved_ids, l16_change, words_found_by_checker
      Copy: byte for byte the project's table (sha256 078e58ceea4b41d2acbc325b6af1c1ad72ff6cf6000e0c29df09a47bb94af5c7).
  tables/replaced_copies.tsv   20 rows, 8 columns
      What it is: The 20 saved pages that are no longer cited, and the copy that replaces each.
      Columns: old_id, new_id, source, identical_bytes, old_sha256, new_sha256, quotations_carried, note
      Copy: byte for byte the project's table (sha256 d08d6ae3bc208c4cd6b58490cc3e4a498e42f595d7ac540f419fc896221101d9).
  tables/state_media_items.tsv   42 rows, 12 columns
      What it is: State and Party media items on Nvidia chips, July 2025 to November 2026, each with its stance.
      Columns: date, outlet, kind, stance, speaker, key_sentence, saved_id, held, original, other_carriers, lane_row, note
      Copy: byte for byte the project's table (sha256 16cf8fbd436f4c34622e72fefc5d03803ae1d5db146f12c35730543451ca4ca9).
      Read with care: 1 row(s) cite cn-media-yuyuan-thepaper, a source the figure no longer cites; outputs/ROUND4.md names cn-le13-yuyuan-qq-20250810b in its place.
  tables/talks_and_acts.tsv   48 rows, 11 columns
      What it is: US-China trade meetings, May 2025 to November 2026, with each side's readout, beside Beijing's dated acts on Nvidia chips.
      Columns: date_start, date_end, kind, event, cn_readout_on_chips, us_readout_on_chips, tier, saved_ids, checked_words, counted, note
      Copy: byte for byte the project's table (sha256 4a2bd525dd47cefa56b981aa1227a278510be8356e0cb76c783ef1d68a4a13b4).
      Read with care: 1 row(s) cite ms-bj-20260114-customs-h200-standard, a source the figure no longer cites; outputs/ROUND4.md names cn-acts-reuters-customs-20260114 in its place; the argument itself still cites ms-bj-20260114-customs-h200-standard as reference 132.
  tables/trade_annual_summary.tsv   528 rows, 7 columns
      What it is: Yearly sums of monthly customs figures, series by series. No customs line counts Nvidia chips.
      Columns: series, measure, unit, year, months_held, sum, table
      Copy: byte for byte the project's table (sha256 a63b683020162fc34ce30b4def4f1297b1311fc60103ffe1936bc5570e814341).
  tables/trade_derived_figures.tsv   76 rows, 3 columns
      What it is: The sums and ratios worked out from the trade tables.
      Columns: figure, unit, value
      Copy: byte for byte the project's table (sha256 e5d06a775cd3f40a9073d158a475d312d010aa6587fa9b0116b5f2fedd13c87c).
  tables/us_officials_statements.tsv   18 rows, 11 columns
      What it is: Named American officials' words on China buying, blocking or bargaining over Nvidia chips. Words from caption tracks are machine-made and not checked by ear.
      Columns: date, official, role, venue, saved_ids, where, words, cuts, tier, argument_cites, note
      Copy: byte for byte the project's table (sha256 545f267cda3e778d8cbaee3685387554665fc3d8e03baccd559e36430f7cb64f).
      Read with care: its column "argument_cites" was recomputed against the present argument (the table's own comment line says how): 12 of the 18 rows name a source it cites, with the reference number.
  tables/xi_searches.tsv   91 rows, 8 columns
      What it is: The searches made of Xi Jinping's published speeches and activities, with the number of results each returned and the controls.
      Columns: site, words, period, mode, results, role, utc, log
      Copy: byte for byte the project's table (sha256 7e2e087da74cdcc025185b201eb7dd3c0090338a5c3f6bb4715b47be450875ef).
