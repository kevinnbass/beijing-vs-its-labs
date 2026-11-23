# Did Beijing's chip policy pull against China's own AI companies? The sources

*The argument, its figure, the two evidence files, 19 plain tables, a list of every source with its address and hash, and the scripts that checked each quotation.*

Draft by Claude, Anthropic's model. Made public Nov 23, 2026.

Assembled Nov 23, 2026 (UTC) from the working files. 889 sources; the saved text of 24 government documents is included, and of nothing else.

## The question

Palmer Luckey, in a clip posted on Nov 19, 2026: "China doesn't want NVIDIA to sell GPUs to Chinese companies." [1] And next: "there are Chinese companies that want to buy Nvidia GPUs" [2]. The first sentence is from a machine transcript of the clip (0:11 to 0:16). The second is from the text of the post that carries the clip; the post begins it with the word Like, and so does a second machine transcript. A published transcript of the whole session, at the DealBook Summit 2026, has both sentences in the same words, but ends the first with two more words, like this: "Chinese companies like this. There are Chinese companies that want to buy Nvidia GPUs" [3]. That page does not say how its transcript was made. He goes on, by the machine transcript (0:18 to 0:36): "There's 600,000 H200 GPUs sitting in a port right now", because "China will not give them an import permit", "because they want to build an internal domestic processor industry, silicon industry, not build one that is dependent on the United States" [1]. Nobody has checked any of this by ear.

The question tested: did Beijing's chip policy pull against what China's own AI companies wanted?

## The answer in one paragraph

China's declared chip policy pulled against what its own AI companies were buying. A Shanghai government body wrote in 2025 that the city's internet companies run their own clusters mainly on Nvidia cards [4]. Nvidia told the SEC in a report signed Nov 19, 2025: "The Chinese government has encouraged customers to purchase from our China-based competitors and restricted customers from purchasing, importing, or using our data center products" [5]. Five cautions. No published ban was found in the policy pages read: state media warned in public, in a burst from Aug 1 to Sept 24, 2025 [6] [7], and the guidance against buying is known from press reports citing unnamed people [8]. Beijing was split: by Reuters, from unnamed people, its industry and commerce ministries approved some purchases [9]. Some chips were sold: $2.4 billion of Nvidia's licensed Hopper products to China in the quarter to Oct 25, 2026 [10]. The companies had reasons of their own, and American curbs pushed too: the same Nvidia passage says "we are already effectively foreclosed from the China market by U.S. export controls" [5]. And what Beijing meant is open: the US-China commission read the antitrust finding as leverage in trade talks [11]; the Trade Representative (captions at 5:59, not checked by ear) calls whether China lets its companies buy "a sovereign decision for China" [12].

The full argument is `ARGUMENT_referenced.md`: 21 points and 209 numbered references. Its answer is yes, on direction, with five limits. Beijing was not one actor. The pressure came as public warnings and unpublished guidance, not as a published ban. Some purchases were approved and some chips came in. The companies had reasons of their own, and American curbs and conditions pushed too. And what Beijing meant by it is not settled: several American bodies read parts of its conduct as leverage in trade talks, while the Trade Representative calls the purchase decision China's own.

Washington's side is on the record. The Commerce Department's table of licence applications for Nvidia's H200 and AMD's MI325X, with their status on May 11, 2026, was made public on Nov 19, 2026 by the House Foreign Affairs Committee, under its chairman's powers and by the committee's "unanimous consent" [13] [14]. 55% of the chips in the Commerce Department's summary of May 11, 2026 were in applications returned without action, and the committee says that summary is incomplete: some applications are "not fully reflected in the May 11, 2026, summary document" [15]. The share is a script's sum of the table's 54 rows in `tables/house_licence_table.tsv`: 1,888,950 of 3,444,160 chips, in 9 applications [16]. The table gives no reasons. An application names a consignee: it is not an order, and an approval there is Washington's licence, not Beijing's.

## The two tiers

- **On the record.** Government documents, company filings, named people speaking on the record, published commentaries of state media or an industry body, a named newspaper's account of a state document, and an institution's own notice. In the argument their reference numbers are filled. In the figure their marks are filled. 173 of the 228 sources that the argument or the figure classes.
- **Reported.** Press reports that cite unnamed people, a research firm's counts as the press gave them, and caption tracks or machine transcripts that nobody has checked by ear. Their numbers and marks are open. 55 of the 228.
- What Beijing told companies in private is in the second tier: do not buy, cancel orders, customs holds, who approved what. It is reported, not published policy. No published Chinese order against buying Nvidia chips was found in the 103 policy pages read.
- **Not classed here.** 661 more sources are named only in the tables or the two evidence files. `sources.csv` gives their address and hash and the files that name them; it does not class them.
- `sources.csv` names the tier of every source the argument or the figure classes.

## Which texts are included

- The saved text of a source is included only where two things hold. The argument or the figure classes the source as a government document or an official's words on the record. And the saved page stands on a government site or on the Party members' own site (addresses ending in .gov.cn or .gov, and 12371.cn).
- 83 sources pass both tests: 61 Chinese and 22 American. The text of 24 is included. Each was read whole before it went in.
- Of the American ones, the text of 1 is included: the Senate appropriations committee's page for the hearing of Apr 22, 2026 [17].
- For every other source the address and the hash are given, never the text.

## How each quotation was checked

- Every source was saved before it was quoted: the page as fetched, or a PDF saved by hand in a browser. `sources.csv` gives each one's address, the time it was saved and the sha256 of the saved file.
- A script, `scripts/cn_srclib.py`, looks for each quotation in the saved copy. It ignores spacing, letter case and the style of quote marks, and nothing else. It refuses a string under 6 characters as too short to check.
- In the argument, words between straight double quotes must stand in the saved copy of a source cited on the same line. A statement made without quoting carries a hidden line, starting with two exclamation marks, that holds words of the page that back it. The builder writes nothing unless every one is found.
- The figure's builder does the same for the 283 quotations in `figure/figure_data.txt`.
- The check can fail: each builder plants a false quotation and stops if that one is found.
- The argument's own count, from the foot of `ARGUMENT_referenced.md`: 308 quotations and 392 further statements, looked for in the saved copies of 209 sources, all found.
- A quotation that is found shows what the source says, not that it is true.
- English in round brackets after Chinese or Japanese is our rendering, not an official translation.

## What is here

| Path | What it is |
|---|---|
| `ARGUMENT_referenced.md`, `ARGUMENT_referenced.html` | The argument, with numbered references, as text and as a page |
| `ARGUMENT_short.md` | The argument in one paragraph, with its own references |
| `argument/` | The argument's text with saved ids in square brackets, its list of references, the short version's text, and `argument_refs_more.tsv`: 13 sources the argument no longer cites but other notes may |
| `OFFICIAL_RECORD.md` | The fuller record of government documents and filings (the first tier) |
| `TIER2_REPORTING.md` | The fuller record of reporting (the second tier) |
| `tables/` | 19 plain tab-separated tables, each listed below; every row names its saved source |
| `figure/beijing_vs_labs.html` | The figure: 61 dated records in four rows, with panels of numbers beside them |
| `figure/beijing_vs_labs_top.png`, `_strip.png`, `_full.png` | Three images of the figure |
| `figure/figure_data.txt` | The figure's data: each record with the source's own words |
| `figure/figure_events.tsv`, `figure/template.html` | The numbered records as drawn, and the page the builder fills |
| `sources.csv` | Every saved source named in the files above: saved id, where it is named, kind, tier, label, the page's own title, address, time saved, sha256 of the saved file, whether its text is here, and a note (for a replacement copy, that it is one) |
| `sources/<id>/meta.json` | For every saved source: address, time saved, hash |
| `sources/<id>/text.txt`, `body_text.txt` | The saved text, for 24 government documents only |
| `scripts/` | The checker, the builders, `cn_outputs_verify.py` and `check_repo.py` |
| `.gitignore` | Keeps Python's cache folders out |

## The tables

Each table's own header lines give its columns and how it was made. Counts in the notes were made from these files by script.

| File | What it holds |
|---|---|
| `tables/chip_evaluations.tsv` | Each product in the security-and-reliability evaluation announcements of the China Information Technology Security Evaluation Center (itsec.gov.cn), as parsed from the saved pages: announcement, date, category, the row as printed. 180 rows |
| `tables/house_licence_table.tsv` | The Commerce Department's table of licence applications for Nvidia's H200 and AMD's MI325X with their status as of May 11, 2026, one line per row, transcribed twice from the page images: date submitted, exporter, consignee, chip count, status, location, and a grouping of consignees made for totals (not the table's own). 54 rows |
| `tables/labs_said.tsv` | What China's AI companies said about chip supply, January 2025 to November 2026: company, date, event, speaker, kind of source, exact words, saved id. 57 rows |
| `tables/labs_said_more.tsv` | The same for iFlytek and SenseTime, from their own results documents, investor records and exchange answers. 23 rows |
| `tables/local_vouchers.tsv` | Local computing-voucher and subsidy rules: issuer, level, date, document, the rate for home-made and for other computing, the page's words, saved id. 20 rows |
| `tables/local_vouchers_more.tsv` | A second set of local voucher and subsidy rules, same columns. 33 rows |
| `tables/market_numbers.tsv` | Published numbers on the market for AI chips in China, one row per number: what is counted, by whom, for which period, with the page's words. Rows of different families measure different things and are not one series. 115 rows |
| `tables/nvidia_china_revenue.tsv` | Nvidia's revenue from customers in China, Hong Kong included, by period, in millions of dollars, from its filings, with the basis of the count (billing location, then headquarters). 26 rows |
| `tables/nvidia_wording_by_filing.tsv` | Nvidia's own words on China, one row per sentence, by filing, commentary or call. 107 rows |
| `tables/press_originals.tsv` | For each press reference of the argument: whether the copy held is a relay, and which copies of the original article were held. 34 rows |
| `tables/procurement_records.tsv` | Procurement records: telecom carriers' central purchases, awards naming Nvidia cards after August 2025, and tenders that require home-made chips, with stage, quantity and the page's words. 41 rows |
| `tables/provinces_31.tsv` | The 31 provincial-level governments: whether a published document sets a share for home-made computing hardware, in the document's own words. 31 rows |
| `tables/replaced_copies.tsv` | The pages once taken from the Hong Kong exchange's news site, each with the copy saved in its place (or none) and whether the two files are identical. 20 rows |
| `tables/state_media_items.tsv` | A census of state and Party media items on Nvidia chips, July 2025 to November 2026: date, outlet, stance, key sentence. 42 rows |
| `tables/talks_and_acts.tsv` | US-China trade meetings, May 2025 to November 2026, with each side's readout on chips, beside Beijing's dated acts on Nvidia chips. 48 rows |
| `tables/trade_annual_summary.tsv` | Yearly sums of monthly trade figures for several customs lines and places; 2026 is a part year. Different series measure different things. 528 rows |
| `tables/trade_derived_figures.tsv` | Every sum and ratio stated in the trade-data report (not included), computed from its tables. 76 rows |
| `tables/us_officials_statements.tsv` | Named American officials on China buying, blocking or bargaining over Nvidia chips: date, official, venue, cue time or official text, exact words. 18 rows |
| `tables/xi_searches.tsv` | The searches for Xi Jinping's words on Nvidia and its chips, with their controls: site, words, period, results reported. 91 rows |

## How to rebuild

- **From this repository alone:** `python3 -I scripts/check_repo.py`. It compares the included texts with the hashes in `sources.csv` and looks for every quotation whose source text is included. At assembly it found 105 quotations and hidden statements in 24 sources, and counted 890 as not checkable here.
- **In full:** `python3 -I scripts/cn_argument_build.py` builds the argument and `python3 -I scripts/cn_figure_build.py` builds the figure (add `--png` for the images, which needs Playwright). They write nothing unless every quotation is found. In this repository they therefore stop and list the quotations whose pages are not included. To run them in full, save each page named in `sources.csv` yourself as `sources/<id>/text.txt`, beside the `meta.json` already there.
- `scripts/cn_doc_build.py` and `scripts/cn_has.py` run the same check on another document and on a list of quotations. Their own control reads a press page, so they also need the pages saved first.
- Python 3 with its standard library is enough for everything but the images.

## Files changed from the working copies

- **Paths in the scripts.** The working copies read the working folders: `research/primary/<id>` for saved pages and `research/cn_chip_policy_20261120` for the argument, the figure and the tables. One docstring named an interpreter by its full local path. The copies here read this repository's folders: `sources/<id>`, `argument/`, `figure/`, `tables/` and the top folder.
- **The clip transcripts.** They are not included, so `scripts/cn_argument_build.py` here passes over them where the working copy would stop. Quotations from the clip then count as not found.
- Nothing else in those five scripts was changed. `scripts/cn_outputs_verify.py` is copied unchanged but for one header line. It checks again the further notes and figures made from this record in a working folder. That folder is not part of this repository, so the script does not run here. `scripts/check_repo.py` was written for this repository.
- **The two evidence files.** In `OFFICIAL_RECORD.md` and `TIER2_REPORTING.md`, six mentions of the project owner's first name were replaced by the words the project's owner, or the owner. Nothing else in them was changed.
- Every other file is a byte-for-byte copy, so the files' own text still names saved copies as `research/primary/<id>`, and the working folders and notes that are not part of this repository.
- **Caption tracks.** For 9 caption tracks, the address given is the video's, not the signed request address the track was fetched through.

## What is not included, and why

- **The text of press pages, company pages, filings, call transcripts, notices, caption tracks and posts** (128 sources). It belongs to its publishers. `sources.csv` gives the address of each page and the sha256 of the copy that was checked.
- **The text of official material that stands on some other site** (16 sources, on m.chinastor.cn, world.people.com.cn, www.cfr.org, www.everycrsreport.com, www.keceyun.com, www.news.cn, www.presidency.ucsb.edu, www.rev.com, www.smartcity.team, www.sohu.com, www.xinhuanet.com, www.yicai.com, www3.xinhuanet.com). These are copies and transcripts kept by trade sites, business papers, state media, transcript services, councils, universities and archives. Address and hash only.
- **The text of 59 government documents on government sites** that the builder of this copy had not read whole. Address and hash only; `sources.csv` marks each as a government document not yet read whole by the builder.
- **The text of the 661 sources not classed here.** Address and hash only.
- **The pages once taken from the Hong Kong exchange's news site** (20 saved ids), since withdrawn. Nothing of them is here: no text, no saved record, no row. `tables/replaced_copies.tsv` gives the copy saved in place of each, from the companies' own investor sites or another mirror; 19 replacement copies are listed in `sources.csv`, each with a note that it is one.
- **Files on an investor-relations vendor's server.** 5 of the replacement copies stand on ea-cdn.eurolandir.com, whose terms allow personal, non-commercial use. Their addresses and hashes only, like every other company filing.
- **Both clip transcripts and all video.** The transcripts are a speech program's and were not checked by ear. The clips belong to their makers. The argument quotes short passages of one transcript and says so.
- **The saved page bodies** (HTML and PDF). Only text is included: `text.txt` as saved and, for 8 pages whose saved text misses the passage quoted, a `body_text.txt` made from the saved body by removing scripts, styles and tags.
- **The working notes:** the folders of notes and reports that the evidence files and the tables name, the notes on the 103 policy pages and on Xi Jinping's statements, the trade-data report, and the search files. They are not part of this repository.
- **`ARGUMENT_short.txt`**, which the working builder also writes: the short version again under another file name.
- **`scripts/render_and_look.py`**, a tool for looking at a page before release, which two docstrings mention.

## References

Each entry: its kind; what it is; the saved page's own title where the record holds one; the address; the saved copy (research/primary/<id>).

[1] Caption track or machine transcript, not checked by ear. Palmer Luckey, in a clip of 56 seconds posted on X by @overton_news, Nov 19, 2026. Words from a machine transcript of the clip (the file transcripts_two_clips.md, beside this note); nobody has checked them by ear. https://x.com/overton_news/status/2123392702821580811

[2] Press report of words spoken on the record. Post on X by @overton_news, Nov 19, 2026, which carries the clip of Palmer Luckey and gives his words as text. The post does not name the programme. https://x.com/overton_news/status/2123392702821580811 Saved copy: cnpol-x-overton-2123392702821580811

[3] Press report of words spoken on the record. The Singju Post, transcript of Palmer Luckey's interview on stage at the New York Times DealBook Summit 2026. The page does not say how the transcript was made or the day of the session. Page title: Transcript: Palmer Luckey Interview on War 2.0 – DealBook Summit 2026 – The Singju Post. https://singjupost.com/transcript-palmer-luckey-interview-on-war-2-0-dealbook-summit-2026/ Saved copy: cn-clips-singju-luckey

[4] Chinese state document. Shanghai Municipal Commission of Economy and Informatization, written reply to proposal No. 0093 of the city's political consultative conference, dated Apr 30, 2025; published on the commission's site on Nov 10, 2025. Page title: 对市政协十四届三次会议 第0093号提案的答复. https://www.sheitc.sh.gov.cn/rddbta/20251110/e6cfe3270ca5483e93cbc55701492e6d.html Saved copy: cn-counter-b11-5

[5] Company filing or statement. Nvidia, quarterly report on Form 10-Q for the quarter ended Oct 26, 2025, filed with the US Securities and Exchange Commission; signed Nov 19, 2025. https://www.sec.gov/Archives/edgar/data/1045810/000104581025000230/nvda-20251026.htm Saved copy: man-ms-sec-10q-2025-10

[6] Published commentary or statement (state media, industry body). People's Daily's commentary account (人民日报评论), a signed piece of Aug 1, 2025, as carried by Beijing Daily's site. Page title: 人民日报评论：英伟达，让我怎么相信你？. https://xinwen.bjd.com.cn/content/s688c9a7ae4b0aabe0a046f83.html Saved copy: cn-acts-peoplesdaily-bjd-20250801

[7] Published commentary or statement (state media, industry body). Science and Technology Daily, report of a forum on information security, Sept 24, 2025. The sentence relied on is the reporter's summary of what academician Shen Changxiang stressed. Page title: 第九届国家信息安全与自主可控战略高层论坛在京举行. https://www.stdaily.com/web/gdxw/2025-09/24/content_406839.html Saved copy: cn-media-stdaily-security-forum

[8] Press report citing unnamed people. Bloomberg, as carried by The Business Times (Singapore), Sept 28, 2024. Page title: China urges local companies to stay away from Nvidia’s chips. https://www.businesstimes.com.sg/companies-markets/china-urges-local-companies-stay-away-nvidias-chips Saved copy: cn-factions-bloomberg-flexibility-202409-relay1

[9] Press report citing unnamed people. Reuters, Jan 30, 2026, as carried by Tiger Brokers. Page title: China Conditionally Approves DeepSeek To Buy Nvidia's H200 Chips - Sources. https://www.itiger.com/hans/news/2607233096 Saved copy: cn-acts-reuters-deepseek-20260130

[10] Company filing or statement. Nvidia, results call for the third quarter of its fiscal year 2027 (the quarter ended Oct 25, 2026): the transcript on Nvidia's investor site. https://s201.q4cdn.com/141608511/files/content_files/NVDA-3Q27-Earnings-Transcript.pdf Saved copy: cn-o38-nvda-q3fy27-call-transcript-pdf

[11] Official document, or an official on the record. US-China Economic and Security Review Commission, 2025 report to Congress, November 2025: the whole report, whose chapter 1 is also listed on its own (the passage cited is in chapter 1 and rests on Reuters and the Financial Times). https://www.uscc.gov/sites/default/files/2025-11/2025_Annual_Report_to_Congress.pdf Saved copy: cn-le03-uscc-2025-full

[12] Caption track or machine transcript, not checked by ear. US Trade Representative Jamieson Greer, interview on Bloomberg Television posted May 15, 2026 ("Greer: US, China Willing to Continue Trade Truce"): the video's English caption track (its maker is not stated; it is not YouTube's automatic track), not checked by ear; the words quoted are at 5:59. https://www.youtube.com/watch?v=ckzJQyMyCoE Saved copy: cn-le01-greer-bbg-20260515-subs-ttml

[13] Official document, or an official on the record. House Foreign Affairs Committee, chairman's press release of Nov 19, 2026 on making public the licence information for Nvidia's and AMD's chips to China. Page title: Chairman Brian Mast Exercises Legislative Authority to Publicly Release AI Chip License Information for China. https://foreignaffairs.house.gov/news/press-releases/chairman-brian-mast-exercises-legislative-authority-to-publicly-release-ai-chip-license-information-for-china Saved copy: cn-labs-us-chip-licences-20261119

[14] Official document, or an official on the record. House Foreign Affairs Committee, the ranking member's remarks at the business meeting of Nov 19, 2026, on the committee Democrats' site. Page title: Meeks Delivers Remarks During HFAC Disclosure of BIS Licenses of NVIDIA & AMD Chips to China | House Foreign Affairs Committee. https://democrats-foreignaffairs.house.gov/2026/11/meeks-delivers-remarks-during-hfac-disclosure-of-bis-licenses-of-nvidia-amd-chips-to-china/ Saved copy: cn-le04-meeks-remarks-20261119

[15] Official document, or an official on the record. House Foreign Affairs Committee, disclosure of Nov 19, 2026, made by the full committee (its chairman's release; approved by unanimous consent at a business meeting; the files are on the committee Democrats' site): the committee's summary, which cites a Commerce Department summary dated May 11, 2026. https://democrats-foreignaffairs.house.gov/wp-content/uploads/2026/11/11.19.26-ECRA-Information-Disclosure-HFAC-Summary.pdf Saved copy: cn-usdocs-hfac-summary-20261119

[16] Official document, or an official on the record. House Foreign Affairs Committee, disclosure of Nov 19, 2026: the Commerce Department's table of licence applications for Nvidia's H200 and AMD's MI325X, with their status as of May 11, 2026 (its text layer is out of order; the rows were read from the page images). https://democrats-foreignaffairs.house.gov/wp-content/uploads/2026/11/11.19.26-ECRA-Information-Disclosure-of-BIS-License-Decisions.pdf Saved copy: cn-usdocs-hfac-decisions-20261119

[17] Official document, or an official on the record. US Senate Committee on Appropriations, its page for the hearing of Apr 22, 2026 on the Commerce Department's budget request, as fetched on Nov 23, 2026. Page title: A Review of the President’s Fiscal Year 2027 Budget Request for the Department of Commerce | United States Senate Committee on Appropriations. https://www.appropriations.senate.gov/hearings/a-review-of-the-presidents-fiscal-year-2027-budget-request-for-the-department-of-commerce Saved copy: cn-o37-senate-hearing-page-b

Build check: 11 quotations and 16 further statements were looked for in the saved copies of 17 sources and all were found; a planted false quotation was rejected. 13 sources are documents, filings or named people on the record; 4 are press reports citing unnamed people, counts or machine transcripts. A quotation that is found shows what the source says, not that it is true.

## Also in this repository

The sections above describe the source files and were written before the outputs were added; where they say the further notes and figures are not part of this repository, that is no longer so.

- The 46 outputs made from this record (a thread, an article, figures, reference pages, two short videos, research notes): [outputs/README.md](outputs/README.md).
- What was left out, and why: [HELD_BACK.md](HELD_BACK.md).
- The same as a site, with a page that links everything: https://kevinnbass.github.io/beijing-vs-its-labs/
- The licence: [LICENSE.md](LICENSE.md).
