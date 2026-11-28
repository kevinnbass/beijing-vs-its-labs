The record as table files
China chip policy: did Beijing's chip policy pull against China's own AI companies?
Draft by Claude, Anthropic's model.

Made by build.py in this folder from the project's own files (figure/figure_data.txt, figure/figure_events.tsv,
argument/argument_base.txt, argument/argument_refs.tsv, tables/). Run "python3 -I build.py" to make them again.
All files are UTF-8 without a byte-order mark. In a spreadsheet program, open them through its import step and
choose UTF-8, or the Chinese will not show correctly.

FILES
  records.csv      62 dated records, 18 columns, comma-separated
  records.tsv      the same 62 records, tab-separated (no field holds a tab or a line break)
  references.csv   the 639 sources of the argument (ARGUMENT_referenced.md), 8 columns
  quotes.tsv       saved id and the source's own words for each record: the input of the quotation check
  tables/          44 plain tables copied from the project's tables folder (listed at the end)
  build.py         the script

COLUMNS OF records.csv AND records.tsv
  n              the record's mark number in the figure (figure/beijing_vs_labs.html), 1 to 62. The files are in
                 number order. Numbers go by date, Beijing's rows first, then the companies';
                 record 62 (Sept 27, 2026), added after the figure was made public, keeps the next
                 free number (the "N" line of figure_data.txt), so it stands out of date order
  date           the date as year-month-day. The date of the act where the page gives it, otherwise of the report
  date_shown     the date as the figure prints it
  date_exact     yes, or no where the source gives only a season or a month and the day in "date" is a placing
                 for the figure, not a fact (2 records: see date_shown)
  who            whose conduct the record is about: Beijing, or the companies. It is not who speaks: see source
  direction      toward Nvidia, or away from Nvidia (Beijing holding Nvidia back, or the companies turning to home-made chips)
  figure_row     the figure's own name for the row the record stands in
  kind           doc, rec or press
  kind_meaning   doc: a government document, an official on the record, or published state media
                 rec: a company, or a named person outside government, on the record (a filing, results, a named executive or analyst)
                 press: a press report citing unnamed people
  on_the_record  yes for doc and rec; no for press
  our_line       our one-line summary, as shown in the figure. Our words, not the source's
  source         the source as the figure names it
  source_words   the source's own words, exact. Chinese where the page is Chinese
  our_english    our English for Chinese source words. Ours, not an official translation. Empty where the
                 source words are English (23 records have it)
  address        where the page is, or was, on the web
  saved_id       the id of the saved copy (the public repository's sources.csv lists every id, with the page's address, the time it was saved and the sha256 of the saved file)
  also_source    the second source as the figure names it, where it gives one
  also_address   the address of that second source

COLUMNS OF references.csv
  number         the reference number in ARGUMENT_referenced.md, 1 to 639
  kind           one of: DOC, OFF, FIL, REC, PRESS, COUNT, CLIP, PUB, NAMED, ACCT, NOTICE
  kind_meaning   what each kind means, in the words that begin each reference of the argument's reference list:
                 DOC: Chinese state document
                 OFF: Official document, or an official on the record
                 FIL: Company filing or statement
                 REC: Press report of words spoken on the record
                 PRESS: Press report citing unnamed people
                 COUNT: Research firm's, broker's or research group's count
                 CLIP: Caption track or machine transcript, not checked by ear
                 PUB: Published commentary, report or statement (state media, industry body, research institute)
                 NAMED: Named person on the record
                 ACCT: A named outlet's account of a document, filing or official act
                 NOTICE: An institution's own published notice
  on_the_record  yes for DOC, OFF, FIL, REC, PUB, NAMED, ACCT, NOTICE; no for PRESS, COUNT, CLIP
  label          what the source is, as the argument's reference list words it
  page_title     the saved page's own title, where the argument prints one
  address        the address; every source has one
  saved_id       the id of the saved copy (the public repository's sources.csv lists every id, with the page's address, the time it was saved and the sha256 of the saved file). An id that begins "clip-" is not a saved page (clip-luckey): it
                 stands for a machine transcript in transcripts_two_clips.md, which nobody has checked by ear

COUNTS (taken from the files by build.py, not typed)
  Records: 62. About Beijing, away from Nvidia: 25. About Beijing, toward Nvidia: 13.
  About the companies, toward Nvidia: 14. About the companies, away from Nvidia: 10.
  By kind: doc 22, rec 14, press 26. So 36 records are on the record and 26 are press reports citing unnamed people.
  References: 639. DOC 176, OFF 80, FIL 108, REC 68, PRESS 81, COUNT 8, CLIP 9, PUB 44, NAMED 2, ACCT 14, NOTICE 49.
  On the record: 541. Press reports citing unnamed people, counts, captions or machine transcripts: 98.

CHECKS THE SCRIPT MADE BEFORE WRITING
  The two figure files hold the same 62 records, one to one, with the same line of ours.
  The mark numbers are those the published figure gives its marks (by date; a record with an "N" line keeps its number).
  scripts/cn_has.py on quotes.tsv: 62 quotations checked, 62 found, 0 not found; controls behave
  (its control, a planted quotation that is not in the saved copy, was rejected, as it must be)
  The reference numbers equal those printed in ARGUMENT_referenced.md.
  Each table was read back and equals what was written.

READ WITH CARE
  A quotation that is found shows what the source says, not that it is true.
  The two tiers are not the same kind of evidence. A press record (kind press) rests on unnamed people. The instructions
  that press reports say Beijing gave companies, the customs checks they report and most of the numbers are of that
  kind: reported, not published policy.
  One company's annual report says on the record that the cyberspace regulator asked Chinese technology companies in
  September 2025 to halt purchases of certain chips; it does not name Nvidia (the argument, point 11).
  A record in a Beijing row can be the words of someone else about Beijing (a company's filing, a US official).
  23 records quote Chinese texts (all of them documents or people on the record); the English beside them is ours.
  Not in these files: the 470 further checked lines of the figure's data file, most of them the quotations
  behind the numbers in the figure's panels (they are in
  figure/figure_data.txt, on the lines that begin with "!"), and the reference lists of the two tier files,
  OFFICIAL_RECORD.md and TIER2_REPORTING.md.

PLAIN TABLES (tables/)
  These 44 tables were made from Nov 23 to Nov 26, 2026 by the AI agents that did the project's research, each from
  saved pages, and are the project's own (the folder tables/ beside the argument). They are copied here so that the
  record can be read in a spreadsheet. All 44 are byte for byte the project's tables (build.py compares each copy's
  sha256 with the project's after writing; each is given below). Nothing in them is changed here. Their quotations were
  checked by the agents who made them, not again here.
  The tables were made before the present version of the argument: a table can cite a saved copy that the project, or
  its figure, has since replaced with a better one (the argument's reference list is the later word). Under 5 of
  the tables a "Read with care" line, computed by build.py, says which rows cite such a copy (and whether the argument
  itself still cites it), and, for the 2 tables with a column of the argument's reference numbers,
  that those numbers are the present ones. Rows of different tables count different things. Do not join them
  into one series. Each table begins with its makers' own notes, on lines that start with "#"; a program reading a
  table should skip those lines.

  tables/carriers_own_notices.tsv   120 rows, 11 columns
      What it is: What the state telecom carriers' own notices, and others' accounts of the same purchases, say about the chips in the carriers' purchases of AI computing, 2023 to November 2026: each page classed by who states it, with counts of chip words on the page. Column first_reading_verdict gives a first reading's verdict on each finding, supported or partly, and the last column, claim_as_read, the finding as read, with that reading's correction where the verdict is partly.
      Columns: search_list_line, saved_id, date, who_states, first_reading_verdict, first_reading_quote_found_by_script, nvidia_words_on_page, homemade_words_on_page, ecosystem_labels, origin_clause, claim_as_read (the first reading's correction where partly)
      Copy: byte for byte the project's table (sha256 06a05c8bb80802cb533a3cdd538f53e9ddc5151700f493dfacdd327bc49df86c).
  tables/chip_evaluations.tsv   180 rows, 5 columns
      What it is: The products in the security-and-reliability evaluation announcements saved from the China Information Technology Security Evaluation Center's site, one row per product per announcement.
      Columns: saved_id, title, page_date, category, cells
      Copy: byte for byte the project's table (sha256 fdea0be217ac8b324ecdd2bc0e96142ce502d1735bfecd302ddb6e7b1bfad8b5).
  tables/computing_centre_plans.tsv   49 rows, 12 columns
      What it is: Plans, filings, bond disclosures and tenders for computing centres in mainland China that name Nvidia chips or, for comparison, home-made ones, with the tier marked by the site that carries each page: 1 for government pages, company filings and institutions' own notices, 2 for trade or press accounts, including sites that reprint filings and tenders. Some official sites carry credited press reports. Rows with a page of each tier show both. Column chip_words gives the page's own words on the chips (each cell checked against its saved copy by script); number gives counts of chips, cards, servers, nodes, supernodes, sets, units, cabinets, racks or projects, computing power in P or PFLOPS, rack ratings in kW and percentage shares where stated, or says when a count is missing; state_linked_or_private, only what the page itself shows, and "not stated" otherwise.
      Columns: province, project, builder_as_the_page_names_it, money_as_the_page_says, date_on_page, chip_words, number, state_linked_or_private, page_kind, tier, saved_id, reached_before
      Copy: byte for byte the project's table (sha256 45d9e1831e41e323b8fab89411ca48ce47e565aac7f8a5ba805558422776e4bb).
  tables/customs_and_tariff_texts_read.tsv   131 rows, 23 columns
      What it is: The pages a search read for a rule on importing a graphics processor, an AI accelerator or a server (114 of them whole when it ran, 17 saved and read afterwards): China's customs and tariff announcements of January 2024 to November 2026 and what was read beside them, each with counts of chip words, customs numbers and words for licences, inspections and holds.
      Columns: saved_id, search_list_rows, address, host, government_host, page_title_as_saved, characters, nvidia_or_model_words, nvidia_or_model_count, codes_8471_8473_8542, n_集成电路, n_芯片, n_显卡, n_图形处理器, n_服务器, n_自动数据处理, n_许可证, n_检验, n_查验, n_扣留, n_不予放行, n_加征关税, n_原产地
      Copy: byte for byte the project's table (sha256 49fb0df3c382c1b6c037710991dfe62dfaa1016fd53a3910ca3c346430d250b7).
  tables/house_licence_table.tsv   54 rows, 10 columns
      What it is: The table of licence applications for Nvidia's H200 and AMD's MI325X, with their status on May 11, 2026, from the Commerce Department's Bureau of Industry and Security (BIS), as the House Foreign Affairs Committee made it public on Nov 19, 2026; one row per application.
      Columns: row, page, date_submitted, exporter, consignee, value, chip_count, status, location, group
      Copy: byte for byte the project's table (sha256 bd06920e873e9cf93a82190ee40374c699ced2cde9a2cf6c927ac0c59813f78b).
  tables/import_lists_read.tsv   22 rows, 12 columns
      What it is: China's published lists of goods whose import needs a licence or is banned, 2024 to 2026, each searched whole for computers, computer parts and chips, with the control that shows the search could find them.
      Columns: key, catalogue, year, announcement, saved_id, saved_file, text_layer, control, control_found, codes_8471_8473_8542_at_token_start, raw_4digit_counts_spaces_removed, word_counts_spaces_removed
      Copy: byte for byte the project's table (sha256 943551f2be572ff87a6b2a58f0993edbce49a2834b21ceac3e297cf7f511f633).
  tables/labs_said.tsv   74 rows, 10 columns
      What it is: What China's AI companies said about chip supply on results calls and in filings, January 2025 to November 2026.
      Columns: company, date, event, speaker, title, source_kind, exact_words, saved_id, cut, note
      Copy: byte for byte the project's table (sha256 59094554474f2242d32a0782d253936d7cfdb622fdfc27b245cbb579d628dc2e).
  tables/labs_said_more.tsv   29 rows, 10 columns
      What it is: The same for two more companies, iFlytek and SenseTime.
      Columns: company, date, event, speaker, title, source_kind, exact_words, saved_id, cut, note
      Copy: byte for byte the project's table (sha256 5a55171129cb78f6b11b0a2405ff59982341dd8321ed524fe561f7386285d940).
  tables/largest_records_naming_no_chip.tsv   10 rows, 7 columns
      What it is: The ten largest award or candidate records of the purchase records table (procurement_records.tsv) that name no chip, with the rule that picked them, the routes tried to find the chip (saved pages read again, and web searches) and what the saved pages say, as it stood on Nov 24, 2026.
      Columns: rank, table_line, buyer_project, value_in_table, routes_tried, what_the_pages_say, state
      Copy: byte for byte the project's table (sha256 5d02d705d2a03cc3c1958454e81abc0802d6e94bf809514860bc89bf7aff3ade).
  tables/local_vouchers.tsv   20 rows, 11 columns
      What it is: Local rules that pay part of the bill for computing: who issued each, when, and the rate for home-made and for other computing.
      Columns: body, level, date, document, rate_home, rate_other, kind, words, saved_id, copy, cuts
      Copy: byte for byte the project's table (sha256 b2cd654cfd0083fc551e8ee5905687aed092eb7606f4b8221813f16e3f121750).
  tables/local_vouchers_classes.tsv   247 rows, 6 columns
      What it is: The class of every local voucher rule of the two voucher tables by the published counting rule: 93 counted, of the rules found by searches that went province by province and city by city, saved and read (not a census of every local government): 8 pay more for home-made computing and still pay for other computing, 4 pay for home-made computing only, 80 pay one rate whatever the chip and 1 pays two rates by a type of computing facility that the rule does not name; 154 read and not counted, each with its reason. The class looks at the counted payment only: other provisions of a counted rule that give home-made computing something more are in local_vouchers_other_provisions.tsv.
      Columns: row_id, government, class, reason, deciding_words, saved_id
      Copy: byte for byte the project's table (sha256 62d5d7aeaf78230eed03ece96381f6ee6f3cad232437a108b9babfe7e16a745f).
  tables/local_vouchers_more.tsv   227 rows, 11 columns
      What it is: More such local rules, and other documents read about them (drafts, application notices and accounts of a rule among them), found in later searches.
      Columns: body, level, date, document, rate_home, rate_other, kind, words, saved_id, copy, cuts
      Copy: byte for byte the project's table (sha256 3fbf8f2de49494ccee99b961bbf185e75d75d5c0fa160f370487204d02019508).
  tables/local_vouchers_other_provisions.tsv   10 rows, 8 columns
      What it is: Provisions of the counted local voucher rules, other than the counted payment, that give home-made computing something other computing does not get: money to build, buy or run home-made computing facilities or equipment, an award or subsidy for adapting models or software to home-made chips or computing or for research built on them, a higher rate, cap or quota for using home-made computing in another provision, or a priority, purchasing preference, required share or condition in words that bind; one row per provision, each read and ruled on the rule's saved copy. A rule's class does not change by these rows: it is decided by the counted payment alone (local_vouchers_classes.tsv).
      Columns: row_id, government, class, kind, article, words, what_it_gives, saved_id
      Copy: byte for byte the project's table (sha256 3c4c4ae0612b42a5df4451d85f961a56bdb6b49641a420bb781aa124ad905fb4).
  tables/market_numbers.tsv   136 rows, 16 columns
      What it is: Published market numbers (shares, shipments, market sizes), one row per number. The column family names the measure; rows of different families are different measures.
      Columns: row_id, family, measure, geography, period, supplier_or_group, value, unit, counted_by, route, page_date, saved_id, words, tier, cuts, note
      Copy: byte for byte the project's table (sha256 10c5a038ed232c5cf6770a0b038ce8a82dad538b66123017833553f981e4fa62).
  tables/miit_texts_word_counts.tsv   54 rows, 20 columns
      What it is: Counts of eighteen words (home-made, chip, Nvidia, three share words and others) in 54 texts that the Ministry of Industry and Information Technology published on computing, AI, electronics and telecom, 2023 to 2026, one row per saved text.
      Columns: saved_id, chars, 国产_not_国产业, 自主可控, 安全可靠, 芯片, 算力芯片, 国产算力, 国产化, 本国产品, 信创, 英伟达, 替代, 不低于, 比例, %, ％, 算力, 安全, 占比
      Copy: byte for byte the project's table (sha256 03ffaa488b2752b59d644347291c5b490b150a1e72a6126bb1317d4e0b355497).
  tables/numbers_first_reports.tsv   23 rows, 6 columns
      What it is: The numbers in the story: who first reported each among the saved pages, and how later reports changed it. In a column's name, the ledger is the project's ledger of numbers (the numbers ledger among the project's outputs).
      Columns (one to a line, since some names hold commas):
        - number
        - what it counts
        - first report found (outlet, date, on whose word, saved id)
        - later reports and how they changed it
        - saved pages that contradict a first reporter or date in the argument or the ledger
        - note
      Copy: byte for byte the project's table (sha256 aa29c7bb6aaf9684b5ad19c25cefaa7c00bea7cc33e295b01e1c08a0e4decd4b).
  tables/nvidia_china_revenue.tsv   28 rows, 7 columns
      What it is: Nvidia's revenue from customers in China, Hong Kong included, period by period, in millions of US dollars (column value_musd), from its own filings: by the customer's billing location until its quarterly report for the quarter that ended Oct 26, 2025, and by the direct customer's headquarters from that report on, with earlier periods recast (column basis); not a count of chips that entered China.
      Columns: period, period_end, basis, value_musd, source, how, check
      Copy: byte for byte the project's table (sha256 666c0e2d1ebabec473e4a993efa1598fb87b54d1645ac728107f0937519ac285).
  tables/nvidia_wording_by_filing.tsv   113 rows, 8 columns
      What it is: Nvidia's own words on China, from its filings and results calls, and its executives' words and its statements as others carried them.
      Columns: date, period_end, document, saved_id, topic, speaker, words, note
      Copy: byte for byte the project's table (sha256 c64d164979fc0c9b9269abda24ccb1563cf05aca03703b53bd202a82b219aa52).
  tables/other_listed_buyers.tsv   11 rows, 13 columns
      What it is: Other listed companies that in 2026 disclosed, or put out a tender for, a purchase or lease of servers with Nvidia chips, or a purchase of computing servers that was not completed.
      Columns: date, code, name, title, pdf, downloaded, text_chars, names_nvidia_hardware, sha256, saved_id, kind, what_the_filing_says, search_list_rows
      Copy: byte for byte the project's table (sha256 93e1a1649da312760a10509d42eaa6fc1ef1e515cdab0428eb63641cb10f54f6).
  tables/press_originals.tsv   54 rows, 10 columns
      What it is: For each press report that an earlier version of the argument cited: whether the copy held is the publisher's own page or another outlet's.
      Columns: ref, saved_id_cited, report, date_of_report, through_a_relay, copy_held, original_held, other_copies_held, best_copy_held, best_copy_available_and_note
      Copy: byte for byte the project's table (sha256 97be6919c69f58663393be8343df210265e61c885b842aca03f4fc4125963e85).
      Read with care: 1 row(s) cite ms-bj-20260114-customs-h200-standard, a source the figure no longer cites; the figure cites cn-acts-reuters-customs-20260114 in its place; the argument itself still cites ms-bj-20260114-customs-h200-standard as reference 394.
      Read with care: its column "ref" gives the present reference numbers of the argument; 2 of the 54 rows keep a report the argument no longer cites (marked "not cited now"); press references added to the argument later are named in the table's own comment line.
  tables/procurement_notices_oct_nov_2026.tsv   27 rows, 11 columns
      What it is: Twenty-seven purchase notices for AI computing of Oct 13 to Nov 24, 2026, a reading sample: the chip words each prints, whether it names Nvidia, what it says on home-made products and imports, and whether it attaches a declaration on the home-made product standard.
      Columns: date, buyer, project, stage, quantity, value, chip_words, nvidia, home_made, saved_id, cuts
      Copy: byte for byte the project's table (sha256 01474828e110db99e29e5e24c09f6a402b7e97be0f8e52048050d531b319efd5).
  tables/procurement_notices_sweep.tsv   61 rows, 20 columns
      What it is: Sixty-one more purchase notices and filings on AI servers and cards, 2024 to November 2026, found by later searches and kept apart from the purchase records: how each names Nvidia, what it says on imports, and whether it requires or refuses Nvidia hardware by name.
      Columns: part, date, buyer, project, stage, quantity, value, chip_family_stated, nvidia, home_made, source_kind, saved_id, exact_words, cuts, item_line_as_printed, nvidia_named_by, imports_field, refuses_or_requires_nvidia_by_name, new_to_project_table, search_list_line
      Copy: byte for byte the project's table (sha256 54e27cf738e4ed1993e76155b081c4f96e7f39b23e1dc2eb9dcbc53ed9503ce2).
  tables/procurement_records.tsv   161 rows, 14 columns
      What it is: Purchase records found by searches: the telecom carriers' central purchases, awards that name Nvidia cards, tenders that require home-made chips or refuse imports, and other notices for context. These records give no measure of how often buyers ask for home-made chips or Nvidia cards.
      Columns: part, date, buyer, project, stage, quantity, value, chip_family_stated, nvidia, home_made, source_kind, saved_id, exact_words, cuts
      Copy: byte for byte the project's table (sha256 0ee7d7b0d30de62eccd4dfa48d474e54e97a6dd58ca6271843e03d4cfad37994).
  tables/provinces_31.tsv   31 rows, 10 columns
      What it is: The 31 provincial-level governments: whether a published plan sets a share for home-made computing, each by its plan's own measure (chips, equipment, hardware and software, or computing capacity), with the document's own words where its text was read. Some rows rest on accounts of a plan rather than its text, and for one government, Xinjiang, no computing plan's text was found, though its development and reform commission, in a reply posted Jul 24, 2026, says two were issued: column result gives the finding, column rests_on what it rests on, and column later_reading what a later reading changed.
      Columns: government, result, kind_of_document, binding_or_expected, documents_issuers_dates, exact_words, rests_on, saved_ids, later_reading, words_found_by_checker
      Copy: byte for byte the project's table (sha256 dbc999854ebfb18ec58266ec4a65ff40a8d0594baa646d077ecfb054bd3ca90b).
  tables/provincial_ict_plans.tsv   30 rows, 11 columns
      What it is: The provincial communications administrations' five-year plans for their sector, searched as a class for a home-made share of computing, chips or equipment: 30 units other than Zhejiang, with what could be read for each and the control that shows the search could find a share.
      Columns: unit, plan_found, group, issuer_and_number_as_the_page_gives_them, date, saved_id, home_made_share_number_in_its_own_words_or_none, how_the_number_is_labelled, words_on_home_made_chips_without_a_number, read_whole_in_the_saved_copy, note
      Copy: byte for byte the project's table (sha256 430c7c5b03c01be4ee1eeab49df8a15c5d5ed9c7f0c7b8244befd1300ede1b27).
  tables/purchase_notices_2024_2025.tsv   35 rows, 14 columns
      What it is: Purchase notices of January 2024 to June 2025, the window a search of Nov 25, 2026 covered, that name the H20, H800, A800, L20 or Nvidia; one row is a company's filing and one a scanned page read by eye.
      Columns: part, date, buyer, project, stage, quantity, value, chip_family_stated, nvidia, home_made, source_kind, saved_id, exact_words, cuts
      Copy: byte for byte the project's table (sha256 d7b51fd1c340da6deaa711cc6f616a5f8edf872accdf77d8bd9f6d76f5bd2a70).
  tables/replaced_copies.tsv   39 rows, 8 columns
      What it is: The 39 saved pages that are no longer cited, and the copy that replaces each where one is needed: 20 taken from the Hong Kong exchange's site and, since Nov 25, 2026, 19 taken from idc.com and trendforce.com, whose terms bar copies made by script, so the project stopped citing them.
      Columns: old_id, new_id, source, identical_bytes, old_sha256, new_sha256, quotations_carried, note
      Copy: byte for byte the project's table (sha256 f4a4b336ed034b2662ae3e7c5daa7db1d2d6ff27218666842f8a4f1f158efa15).
  tables/reported_claims_outlets.tsv   9 rows, 9 columns
      What it is: For nine claims the argument gives as reported by unnamed people: the first report, second reports with their own sources, relays, and any denial.
      Columns (one to a line, since some names hold commas):
        - claim
        - what is claimed
        - first report: outlet, date, its sourcing in its own words, saved id
        - independent second reports (own sourcing), each read
        - relays (count; ids)
        - denial or contradiction
        - verdict
        - not saved (leads only: pages a search named that could not be saved)
        - note
      Copy: byte for byte the project's table (sha256 16d3c98274716ef27285796503a1e83499ab4ecdce2cf21e27d56cecb5ad0240).
      Read with care: 1 row(s) cite ms-bj-20260114-customs-h200-standard, a source the figure no longer cites; the figure cites cn-acts-reuters-customs-20260114 in its place; the argument itself still cites ms-bj-20260114-customs-h200-standard as reference 394.
  tables/results_calls_authority_counts.tsv   48 rows, 7 columns
      What it is: Counts from a search of 118 company texts (76 results-call transcripts and 42 records of four smaller companies) for the names of Chinese authorities beside a chip word: by group and word, the hits and the hits beside a chip word, with what each of those is.
      Columns: check, group, word, hits, hits_beside_a_chip_word, saved_ids_of_those, what_those_are
      Copy: byte for byte the project's table (sha256 01cdc2d0448734c4f606f479b5c3bf14fa475d90ee4b152cd4db5e4b94bbc62e).
  tables/results_calls_read.tsv   61 rows, 8 columns
      What it is: The 61 results-call transcripts of eight Chinese companies, February 2025 to November 2026, that the word census reads: company, call, date, saved id, the site that carries the transcript, what the page says of its source and of any part made by a model, and the number of markers of passages not translated.
      Columns: company, call, call_date, saved_id, transcript_site, transcript_from, marked_as_made_by_a_model_or_machine, markers_of_passages_not_translated
      Copy: byte for byte the project's table (sha256 4d98de2b9dde41941dd85ba87a3a58b427218a949254cd57ca61681271a31514).
  tables/results_calls_word_census.tsv   20 rows, 4 columns
      What it is: How many of 61 results-call transcripts of eight Chinese companies, February 2025 to November 2026, hold each of 20 words or word patterns (Nvidia, Huawei, H20, domestic chips, the Cyberspace Administration, customs and others), with the control word.
      Columns: word, calls_with_it, calls_read, which
      Copy: byte for byte the project's table (sha256 c9bbad8f511fc57a16ebe7fdb010e7ba0ed23c4fdfdb2274aa09dcbbbf861e43).
  tables/rtx5500_buyers_later_notices.tsv   26 rows, 12 columns
      What it is: Every notice of the three listed buyers of cards named PRO 5500 (the purchase notices of two of them name Nvidia as the maker; Youzu's names none) on the exchanges' disclosure site from Oct 1 to Nov 25, 2026 that the census of notices does not hold, with the Shenzhen exchange's letter to one of them: 26 rows, the letter among them, each with what it says on the cards.
      Columns: date, code, name, title, pdf, downloaded, text_chars, names_card, sha256, saved_id, relation, what_it_says_on_the_cards
      Copy: byte for byte the project's table (sha256 23db87a9637c78987865155058e168eaadb65f3454c100d7732ee69350da58f2).
  tables/rtx5500_notices.tsv   333 rows, 9 columns
      What it is: Notices on the exchanges' disclosure site, Sept 14 to Nov 24, 2026, whose titles name a contract, a purchase or computing: 333 notices, 3 of which name a card PRO 5500, two of them as Nvidia's RTX PRO 5500.
      Columns: date, code, name, title, pdf, downloaded, text_chars, names_card, sha256
      Copy: byte for byte the project's table (sha256 e9758e57aa1a296f6894c136311321a9b0907bbc5b5cd254b0e8fada33bb0db6).
  tables/spokespeople_answers_census.tsv   31 rows, 9 columns
      What it is: Every answer found in which a Chinese government spokesperson was asked about Nvidia chips, about American chips or about the sale of chips to China, December 2024 to September 2026, counted by one written rule: for the foreign ministry every regular press conference searched and the matching pages read twice, for the commerce ministry its regular briefings read and a search for its written answers, which is not a census.
      Columns: date, ministry, spokesperson, asked_by, question_words_zh_as_on_page_or_gist, answer_class, answer_words_zh, saved_id, already_in_record
      Copy: byte for byte the project's table (sha256 5e4ff035d0c8397521c9b57b3aeb0bc571b0258cbef51e2540b32ccd1517ce81).
  tables/state_media_baseline_2024_2025h1.tsv   174 rows, 13 columns
      What it is: A baseline for the state-media table: state and Party media items on Nvidia chips, January 2024 to June 2025, by the same rule; gathered by other routes, not a census, and not counted in that table. 14 of its rows are from papers of the People's Daily group that the state-media table never holds (their notes begin GROUP-PAPER), so a comparison with that table counts the other 160.
      Columns: date, outlet, kind, stance, speaker, key_sentence, saved_id, held, original, other_carriers, search_list_row, note, subject
      Copy: byte for byte the project's table (sha256 38e3ca2961b405dd4b514ca7050a5a770a0f78e53dc77eb3157419d6dcd67e5c).
  tables/state_media_baseline_outside_scope.tsv   45 rows, 7 columns
      What it is: Items that the searches for that baseline found and left out of it, each with the reason.
      Columns: date, who_published, what, saved_id_or_address, held_or_found, search_list_row, why_outside
      Copy: byte for byte the project's table (sha256 34a3d6ce9955e6548a8bb0bdc2550eaf6a4cc511528e1b60c3621a5de2f1c294).
  tables/state_media_items.tsv   297 rows, 13 columns
      What it is: State and Party media items on Nvidia and its chips, July 2025 to November 2026, each with its stance and subject. The subject column distinguishes chips for AI computing from products with an Nvidia chip, Nvidia as a company and other topics.
      Columns: date, outlet, kind, stance, speaker, key_sentence, saved_id, held, original, other_carriers, search_list_row, note, subject
      Copy: byte for byte the project's table (sha256 f8e910d2d043ab4822e5aabd0fab313e50bc2cec14d315255fbfc2fbbf47a757).
      Read with care: 1 row(s) cite cn-media-yuyuan-thepaper, a source the figure no longer cites; the figure cites cn-le13-yuyuan-qq-20250810b in its place.
  tables/talks_and_acts.tsv   50 rows, 11 columns
      What it is: US-China trade meetings, May 2025 to November 2026, with what each side's readout says on chips, or that no written readout of that side was found, beside Beijing's dated acts and words on Nvidia chips.
      Columns: date_start, date_end, kind, event, cn_readout_on_chips, us_readout_on_chips, tier, saved_ids, checked_words, counted, note
      Copy: byte for byte the project's table (sha256 b8af63bdf8d6c1330d6e3f71425eaaad3c2f1c7b9fe661495d5eaa0cf8b90515).
      Read with care: 1 row(s) cite ms-bj-20260114-customs-h200-standard, a source the figure no longer cites; the figure cites cn-acts-reuters-customs-20260114 in its place; the argument itself still cites ms-bj-20260114-customs-h200-standard as reference 394.
  tables/trade_annual_summary.tsv   528 rows, 7 columns
      What it is: Yearly sums of monthly customs figures, series by series; column months_held gives how many months of the year each sum covers (127 of its 528 rows cover fewer than 12 months, every row of 2026 among them). No customs line counts Nvidia chips.
      Columns: series, measure, unit, year, months_held, sum, table
      Copy: byte for byte the project's table (sha256 dd157427a3b7d35577ccad5f130b6ecbd6015b712f6dfa927d5480f9d5d176f4).
  tables/trade_derived_figures.tsv   76 rows, 3 columns
      What it is: The sums and ratios worked out from the trade tables.
      Columns: figure, unit, value
      Copy: byte for byte the project's table (sha256 6028505f11d4c2ffeb1332c560305204dfdfd52ab35445633eafb746cda30ed4).
  tables/us_officials_statements.tsv   35 rows, 11 columns
      What it is: Named American officials' words on China buying, blocking or bargaining over Nvidia chips. Words from caption tracks are machine-made and not checked by ear.
      Columns: date, official, role, venue, saved_ids, where, words, cuts, tier, argument_cites, note
      Copy: byte for byte the project's table (sha256 6f0828c6d97d3b789b605655d9178c7d8799907381a0f35b9ba2470fa4d191fb).
      Read with care: its column "argument_cites" was recomputed against the present argument (the table's own comment line says how): 26 of the 35 rows name a source it cites, with the reference number.
  tables/wuhan_university_result_notices.tsv   81 rows, 7 columns
      What it is: Result notices (成交结果公告) of purchases by filed bidding (备案竞价) that Wuhan University's procurement centre published on its own site, June 2025 to November 2026, picked by titles on graphics cards, GPUs, servers and AI computing: 81 notices, each with its date, the price of the award, and the Nvidia words and home-made words found on the page.
      Columns: saved_id, page_date, project_name, amount_yuan, nvidia_words, home_made_or_import_words, text_around_first_nvidia_word
      Copy: byte for byte the project's table (sha256 6d93926bf6a2cbc4c1b723a22a891be909184316aa2c476d444647fc707584cd).
  tables/xi_items_database_check.tsv   156 rows, 9 columns
      What it is: A test of how complete People's Daily Online's database of Xi Jinping's speeches and activities is: 156 items of 2023 to November 2026 taken from Xinhua's lists and Qiushi's contents for their words on chips, computing power, AI, American firms or curbs, each looked for in the database, with the verdict and how it was reached.
      Columns: key, date, title, strong_words, database, database_ids, how_decided, xi_statements_list_within_3_days, outside_url
      Copy: byte for byte the project's table (sha256 7e3b0400ad2e1b893b59d8eae74ffbe024179d8837d685e1970186de373c1ee6).
  tables/xi_searches.tsv   92 rows, 8 columns
      What it is: The searches made of Xi Jinping's published speeches and activities, with the number of results each returned and the controls.
      Columns: site, words, period, mode, results, role, utc, log
      Copy: byte for byte the project's table (sha256 b699d9d205f75eca7ae09f746b45d337e3ed81c00afecba8b7bdc3a11b413465).
