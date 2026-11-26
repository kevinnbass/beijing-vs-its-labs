#!/usr/bin/env python3
"""Build the searchable page of the policy documents read for the China chip-policy project (idea 28).

Run: python3 -I build.py            (from any folder; it reads and writes by absolute path)

Reads   ../../../NOTE_policies_checked.md      the checked note: 103 policy lines, each read in its saved page
        ../../../policies_checked_quotes.tsv   the note's own table of quotations (row, saved id, verdict, words, form)
        research/primary/<id>/                 the saved copies (read only): page titles, and every string checked below
Writes  quotes.tsv              saved id <TAB> exact words: every passage shown, every date word shown, every quoted
                                string kept in quotation marks in the check notes
        policy_documents.html   the page (one file; plain JavaScript; no outside library)
        expected.json           the counts the page must show for a few searches (read by test_page.py)

The page is not written unless all of this holds:
  - the note parses into exactly the rows its own count table gives, each with a body, an address and a verdict;
  - the passages in the note are the same strings, row by row, as in the note's table of quotations;
  - every Chinese passage has our English beside it in the note;
  - scripts/cn_has.py passes on quotes.tsv (exit 0; its planted false quotation is rejected).
What the script decides and what it only carries over:
  - dates: the list's date; where the list had none, the date the note found in the page. The script then looks for
    the date in the saved copy in the usual written forms and shows the words it found, or says it found none;
  - a string between quotation marks inside the note's "body" or "verdict" lines is kept in quotation marks only when
    cn_has.py can find it in the saved copy; otherwise it is set in italics (the note's own English, a short word,
    or a reading the note made by eye). One word the note quotes as the list's own wording, which also happens to
    stand in the saved page, is set in italics too (LANE_WORDS);
  - the note's descriptions of the issuing body and its check notes are carried over as written;
  - our English is the note's, with double quotation marks taken out (our own English carries none).
  - the passage shown first on a line is the note's first passage of 20 characters or more (so a bare document number
    or date does not stand as the key sentence); the line's other passages open under it.
"""
import html, json, re, subprocess, sys, unicodedata
from collections import Counter, OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parents[2]
SCRIPTS = Path('scripts')
sys.path.insert(0, str(SCRIPTS))
import cn_argument_build as B

L = B.L
NOTE = PROJ / 'NOTE_policies_checked.md'
QTSV = PROJ / 'policies_checked_quotes.tsv'
OUT = HERE / 'policy_documents.html'

MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
MONTH = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# Dates the list left out. Each is stated by the note, in its section "Smaller points"; the words in the second
# place must stand in the note or the build stops.
UNDATED = {'33': ('2025-12-30', '33 (Dec 30, 2025)'), '43': ('2025-11-05', '43 (Nov 5, 2025)'), '45': ('2024-04-08', '45 (translation dated Apr 8, 2024)'),
           '78': ('2017-10-23', '78 (Oct 23, 2017)'), '83': ('2026-07-28', '83 and 84 (July 28, 2026)'), '84': ('2026-07-28', '83 and 84 (July 28, 2026)'),
           '85': ('2026-03-24', '85 (Mar 24, 2026)'), '101': ('2025-06-03', '101 (June 3, 2025)')}
# Date words read in the saved copy by this folder's author where the usual forms are not on the page (the page
# gives the day without the year in one place and the year in another). Every string goes through cn_has.py.
DATE_WORDS = {'5': ['新华社北京9月6日电', 'n1/2022/0907'],
              '58': ['新华社北京4月17日电', '2025年04月18日'],
              '34': ['中共中央政治局4月25日下午', '2025-04-27'],
              '35': ['中共中央政治局4月25日下午', '2025-04-27'],
              '11': ['7月17日,商务部部长王文涛会见', '2025-07-18'],
              '89': ['新华社北京12月31日电', '2026年01月01日'],
              '33': ['SINGAPORE, Dec 30 (Reuters)', 'news-html/20251230']}
# One date the note did not find and this folder's author read in the page: the city government's signing line.
FOUND_HERE = {'71': ('2017-04-17', ['上海市人民政府 2017年4月17日'])}

KIND_LABEL = OrderedDict([('official', 'Official text'), ('company', 'Company filing or statement'), ('press', 'Press report'),
                          ('carried', 'Official text or figure, carried by a news outlet'),
                          ('roadmap', "Advisory committee's roadmap, on a third party's site"),
                          ('translation', "Think tank's translation of a government text")])
GROUP = {'official': 'official', 'company': 'company', 'press': 'press', 'carried': 'other', 'roadmap': 'other', 'translation': 'other', 'local': 'local'}
GROUP_LABEL = OrderedDict([('all', 'All'), ('official', 'Official texts'), ('company', 'Company filings and statements'), ('press', 'Press reports'), ('other', 'Other'),
                           ('local', 'Local rules and provincial plans')])
TABLES = PROJ / 'tables'
# Round 4: where the note's English for a passage differs from the core's corrected wording for the same Chinese
# (loose_ends/L23_chinese_review/CHINESE_REVIEW.md; argument/argument_base.txt), the page uses the core's. List line ->
# (the note's words, the core's words). The build stops if a pair no longer matches the note.
EN_FIX = {
    '74': [('Core internet technology is our greatest vital gate, and dependence on others for core technology is our greatest hidden danger.',
            "The internet's core technology is our greatest weak point, and having core technology controlled by others is our greatest hidden danger.")],
    '58': [('More American companies, Nvidia included, are welcome to work the Chinese market in depth',
            'More American firms, Nvidia among them, are welcome to put down deeper roots in the Chinese market')],
    '11': [('We hope multinational companies, Nvidia included, will provide Chinese customers with quality, reliable products and services.',
            'We hope multinationals, Nvidia among them, will give Chinese customers high-quality, reliable products and services.')],
    '90': [('guiding home-made large models to step up adaptation to home-made computing chips',
            'guiding home-made large models to do more to adapt to home-made computing chips')],
    # Round 9 (Nov 25, 2026): two renderings the official record corrected in core edit 8b (its rows Frr02-021 and Frr07-019), which the
    # checked note still holds in their earlier words; the page takes the record's words
    '85': [('the share of intelligent computing, the rate of home-made equipment and the regional concentration',
            'the share of intelligent computing, the home-made rate and the regional concentration')],
    '91': [('to build research, production and operating centres in China',
            'to build research and development, production and operating centres in China')],
    # Round 10 (Nov 25-26, 2026): the readers' leads. Lines 8, 63, 66: the buyers the rule binds, in the argument's words (the notices' same
    # sentence names them: 乡镇以上党政机关... in all three copies); line 25: the market regulator's notice of Sept 15, 2025 in the argument's words
    # (a preliminary finding against Nvidia, and a further investigation; the session's ruling for round 10). Lines 16, 47, 49, 50, 73, 101: a few
    # words of ours that make a term or a target clear.
    '8': [('Party and government organs at township level and above, and the public institutions directly under such Party committees and governments or serving those organs, shall',
           "Party and government bodies at township level and above, the public institutions directly under Party committees and governments at those levels, and the departments' public institutions that provide support to those bodies, shall")],
    '63': [('[such bodies,] when buying portable computers', "[Party and government bodies at township level and above, the public institutions directly under Party committees and governments at those levels, and the departments' public institutions that provide support to those bodies,] when buying portable computers")],
    '66': [('[such bodies,] when buying general-purpose servers', "[Party and government bodies at township level and above, the public institutions directly under Party committees and governments at those levels, and the departments' public institutions that provide support to those bodies,] when buying general-purpose servers")],
    '25': [('Recently, after a preliminary investigation, Nvidia violated the Anti-Monopoly Law and the regulator\'s announcement approving its purchase of Mellanox with restrictive conditions;',
            'Recently, a preliminary investigation made a preliminary finding against Nvidia under the Anti-Monopoly Law and under the regulator\'s announcement approving, with restrictive conditions, its purchase of Mellanox;')],
    '16': [('total capacity above 300 EFLOPS, intelligent computing reaching a 35% share', 'total computing capacity above 300 EFLOPS (a measure of computing power), with intelligent computing reaching 35% of it')],
    '47': [('home-made computing chips make up over 50% of use', 'home-made computing chips are to make up over 50% of those in use')],
    '49': [('deeply tied to the CUDA ecosystem;', "deeply tied to the CUDA ecosystem (Nvidia's software platform for its chips);")],
    '50': [('the strategic value of Xinchuang as a core support', 'the strategic value of Xinchuang (信创: replacing foreign information technology with home-made products) as a core support')],
    '73': [('where a concentration is carried out unlawfully', 'where a concentration (a merger, or one business taking control of another) is carried out unlawfully')],
    '101': [('carry out home-made Xinchuang substitution fully', 'carry out home-made Xinchuang (信创: replacing foreign information technology with home-made products) substitution fully')],
}
EN_SRC = {'74': 'argument', '58': 'argument', '11': 'argument', '90': 'argument', '85': 'record', '91': 'record',   # round 9: whose corrected wording each line takes
          '8': 'argument', '63': 'argument', '66': 'argument', '25': 'argument', '16': 'page', '47': 'page', '49': 'page', '50': 'page', '73': 'page', '101': 'page'}
# round 10: words the argument must still hold for the lines that take its wording in this round (the build stops if it no longer does)
EN_CHECK = {'8': "the public institutions directly under Party committees and governments at those levels, and the departments' public institutions that provide support to those bodies",
            '63': "the public institutions directly under Party committees and governments at those levels, and the departments' public institutions that provide support to those bodies",
            '66': "the public institutions directly under Party committees and governments at those levels, and the departments' public institutions that provide support to those bodies",
            '25': 'a preliminary finding against Nvidia, and a further investigation'}
# Round 4: the commission's page names Li Chao and his office (李超 2026/05/22 政研室) and does not call him spokesperson
# (loose_ends/L23_chinese_review, A12). Words of a note body or a table row replaced on this page; the build stops if
# one is not met exactly once.
BODY_FIX = [('State planner (NDRC), Li Chao of its policy research office (政研室; this page does not call him spokesperson), press conference transcript.',   # the owner corrected the note itself on Nov 23, 2026; the page's line is unchanged
             'State planner (NDRC), Li Chao of its policy research office, press conference transcript.'),
            ('国家发展改革委 (NDRC), spokesman Li Chao, as reported by Xinhua on gov.cn',
             '国家发展改革委 (NDRC), Li Chao of its policy research office, as reported by Xinhua on gov.cn'),
            ("as reproduced by ChinaStor, a trade site; the centres' own page is not saved.",
             "on the first centre's own site."),      # round 10: no history of copies on the page (readers' leads)
            ('Shanghai Municipal Commission of Economy and Informatization (a 2017 city policy).',      # round 10: the page's signature line is the city government's (上海市人民政府 2017年4月17日)
             "Shanghai Municipal People's Government (a 2017 city policy, on the site of the Shanghai Municipal Commission of Economy and Informatization)."),
            ('Shanghai Communications Administration and ten other city bodies', 'Shanghai Communications Administration and ten other bodies in Shanghai')]   # round 10: the core's names table (SF1-003)
# Round 4 (outputs/ROUND4.md, section 2): a note line whose saved copy the project no longer cites is shown as read in
# the replacement copy, after the cross-check with the note's table (which stays as the note wrote it). Every passage and
# date word of the line must stand in the replacement, or the build stops. List line -> (new id, address, words shown).
REPOINT = {'60': ('cn-le14-itsec-2026-2', 'http://www.itsec.gov.cn/aqkkcp/cpgg/202605/t20260526_259396.html',
                  "the centres' own page (the note read a trade site's reproduction, cn-policy-ai-chip-evaluation, which the project no longer cites)")}
# Round 4 (outputs/ROUND4.md, section 3, item 3): a rule repealed by a later one is shown with that fact, checked in
# the later rule's saved copy. (table, row) -> (saved id of the later rule, its words, the note shown).
REPEALED = {('local_vouchers.tsv', 8): ('cn-le28-etown-29hao-20241126', '原政策(京技管发〔2024〕10号)同时废止',
            "Repealed. The zone's rule of Nov 26, 2024 (京技管发〔2024〕29号) says the former policy, No. 10 of 2024, is repealed at the same time, and pays 30% of the bill whatever the chip. The rates of up to 40% and up to 30% here are not the rule in force."),
            # round 10 (readers' lead): the repeal of Huangpu's measures of 2024, read in the measures of 2025 that repeal them
            ('local_vouchers_more.tsv', 173): ('cn-le28-gz-huangpu-2025-7hao', '加快推进中小企业数字化转型发展若干措施》（穗埔工信规字〔2024〕2号）和',
            'Repealed. The district\'s measures of Jun 27, 2025 (穗开经信规字〔2025〕7号, row 10 of tables/local_vouchers_more.tsv) repeal these measures of 2024 (穗埔工信规字〔2024〕2号) with their implementing rules.')}
# Core edit 7b (Nov 25, 2026): words of a note's check note that name the project's own working files, replaced on this
# page by what they mean. List line -> [(the note's words, the page's words)]; the build stops if one is not met once.
REMARK_FIX = {'55': [('on the new copy (loose_ends/GA21_replacements/quotes.tsv, cn_has.py exit 0).',
                      'Confirmed on the new copy: the script found its passages in the saved page.')]}
# Core edit 8 (Nov 25, 2026): words of a table's cell that name the project's own working files, helpers or tools, replaced on this page by what
# they mean (the tables' own cells are unchanged: they are the session's). (table, row) -> [(the cell's words, the page's words)]; the build stops
# if one is not met exactly once, and stops if a line from the tables still shows such a word (WORKING below; control in local_lines()).
COPY_FIX = {}      # Nov 25, 2026 (the session): the ten cells this map reworded now hold those plain words in the tables themselves, so the page and the tables say the same; a new working word in a printed cell still stops the build
WORKING = re.compile(r"loose_ends|\bL\d\d\b|\bGA\d\d\b|this folder|WebFetch|cn_has|check_extracted|\bthe session\b|\.py\b|page saver|pdftotext|\bLEAD\b|words cell|\bthe checker\b|\bfetcher\b|by the search|the search's|owner's|\brow [AB]\d+\b|by script")   # round 10: more working words the readers found
RESULT = {'share': 'sets a share for home-made computing hardware', 'plan_no_share': 'a plan that was read sets no such share',
          'account_only': "known only from accounts of it, its issuer's own among them", 'not_reached': 'no computing plan was found'}

# Round 10 (Nov 25-26, 2026; builder o10-A3b of the session): two readers read this page against the argument, and a helper looked at every
# screenshot of it (LOOK28_FULL.txt). What they found in the words of the project's tables and of the checked note is shown here in plain words
# or in the argument's words. The tables and the note themselves are the session's and are not changed here: each entry below is also a row
# for the session to apply to the table or the note (exact old words, exact new words), after which the entry stops the build and is taken out,
# as COPY_FIX was in core edit 8. Every entry must be met exactly once, or the build stops.
# (table, row) -> [(column, the cell's words, the page's words)]
CELL_FIX = {
    ('provinces_31.tsv', 28): [('binding_or_expected', 'a green-power share only', 'shares only for green power and for the uptake of new smart terminals and agents')],   # the argument, point 3
    ('provinces_31.tsv', 29): [('binding_or_expected', 'not a share: the targets named are', 'by the accounts of it, no share for home-made hardware: the targets they name are')],
    ('provinces_31.tsv', 2): [('rests_on', 'saved official page (70% of 自主可控 computing)',
                               'saved official page (the opinions of Mar 24, 2025 on the intelligent-computing cloud: by 2027 the city strives for 200 EFLOPS of intelligent computing, over 70% of it 自主可控, independently controllable)')],
    ('provinces_31.tsv', 31): [('documents_issuers_dates', 'with 国产 and 自主可控 0 times', 'with 国产 (home-made) and 自主可控 (independently controllable) 0 times')],
    ('local_vouchers.tsv', 5): [('rate_home', '60% (国产人工智能算力)', 'up to 60% (国产人工智能算力)'), ('rate_other', '30% (非国产人工智能算力)', 'up to 30% (非国产人工智能算力)')],   # the rule's 按不超过 (ceilings)
    ('local_vouchers.tsv', 6): [('rate_home', '60% (自主人工智能算力)', 'up to 60% (自主人工智能算力)'), ('rate_other', '30% (非自主人工智能算力)', 'up to 30% (非自主人工智能算力)')],   # the argument's table: up to 60% / up to 30%
    ('local_vouchers.tsv', 9): [('body', '北京经济技术开发区 application guides (经开区信息技术产业局)',
                                 '北京经济技术开发区 (Beijing E-Town, an economic and technological development zone) application guides (经开区信息技术产业局, its IT industry bureau)')],
    ('local_vouchers.tsv', 10): [('copy', 'whose text the checker reads (first words); the two notes are official Word files (their text taken out and kept beside the saved files)',
                                  'whose text was searched (the first passage above); the two notes are official Word files, whose text was taken out and searched (the other passages)')],
    ('local_vouchers.tsv', 13): [('body', '上海市经济和信息化委员会', '上海市经济和信息化委员会 (Shanghai Commission of Economy and Informatization)')],
    ('local_vouchers.tsv', 14): [('document', 'the copies read by script carry no number', 'the other copies carry no number')],
    ('local_vouchers.tsv', 17): [('body', '宁夏回族自治区工业和信息化厅 reply, describing the 宁夏枢纽 policy opinions',
                                  '宁夏回族自治区工业和信息化厅 (Ningxia industry and IT department) reply, describing the 宁夏枢纽 (Ningxia computing hub) policy opinions')],
    ('local_vouchers.tsv', 19): [('copy', 'the words are found in the text taken out of the Word file and kept beside it', 'the words are found in the text of the official Word file')],
    # round 10 (look fault 8): saved ids inside a cell's prose ("unsaved" in an id reads as "not saved"); the ids stay in the Saved copy line
    ('local_vouchers.tsv', 18): [('date', "(the issuer's own page, cn-ga31-unsaved-sc-338hao-fgw-wayback)", "(the issuer's own page, in an Internet Archive capture)"),
                                 ('document', "on the issuer's own page in an Archive capture, cn-ga31-unsaved-sc-338hao-fgw-wayback;", "on the issuer's own page in an Internet Archive capture, which is saved;"),
                                 ('copy', '(cn-ga31-unsaved-sc-338hao-fgw-wayback: the number', '(the number'),
                                 ('copy', 'for projects on home-made chips (cn-le14-huabenlihe-policy-list) is this', 'for projects on home-made chips is this')],
    ('local_vouchers_more.tsv', 30): [('copy', '(tj.gov.cn; the copy saved as cn-le28-tj-compute-plan-2024-18hao is byte for byte the same)', '(tj.gov.cn; a second saved copy is byte for byte the same)')],
    ('provinces_31.tsv', 24): [('rests_on', 'of the Jingdezhen city copy (cn-ga31-unsaved-jiangxi-measures-2025-jdz-wayback)', 'of the Jingdezhen city copy')],
    ('local_vouchers.tsv', 20): [('rate_other', 'same', 'not stated'),
                                 ('copy', "a company's policy list (LEAD; official text not found", "a company's policy list (a lead only: the official text was not found")],
    ('local_vouchers_more.tsv', 2): [('body', '北京经济技术开发区信息技术产业局,', '北京经济技术开发区信息技术产业局 (Beijing E-Town IT industry bureau),')],
    ('local_vouchers_more.tsv', 3): [('body', '北京经济技术开发区信息技术产业局,', '北京经济技术开发区信息技术产业局 (Beijing E-Town IT industry bureau),'),
                                     ('document', '(citing 29号)', '(citing 京技管发〔2024〕29号)')],
    ('local_vouchers_more.tsv', 4): [('body', '北京经济技术开发区信息技术产业局,', '北京经济技术开发区信息技术产业局 (Beijing E-Town IT industry bureau),'),
                                     ('document', '(citing 29号, article 2)', '(citing 京技管发〔2024〕29号, article 2)')],
    ('local_vouchers_more.tsv', 6): [('body', '深圳市工业和信息化局, operating rules', '深圳市工业和信息化局 (Shenzhen industry and IT bureau), operating rules')],
    ('local_vouchers_more.tsv', 7): [('body', '深圳市发展和改革委员会, national AI voucher', '深圳市发展和改革委员会 (Shenzhen development and reform commission), national AI voucher')],
    ('local_vouchers_more.tsv', 11): [('copy', '(its extracted text is empty; the words were checked against the page body)', "(the words were found in the page's markup; its plain text came out empty)")],
    ('local_vouchers_more.tsv', 13): [('body', '武汉市人民政府, OPC measures', '武汉市人民政府 (Wuhan city government), OPC (one-person company) measures')],
    ('local_vouchers_more.tsv', 14): [('rate_home', 'up to 50% of the computing service fee, up to 200,000 yuan, on top of the city', '50% of the computing service fee, at most 200,000 yuan, on top of the city'),
                                      ('rate_other', 'up to 50%', '50%')],      # 按算力服务费的50%最高给予20万元
    ('local_vouchers_more.tsv', 17): [('body', '青岛市工业和信息化局, revised voucher rules', '青岛市工业和信息化局 (Qingdao industry and IT bureau), revised voucher rules')],
    ('local_vouchers_more.tsv', 19): [('body', '杭州市人民政府办公厅, 新势力 measures', '杭州市人民政府办公厅 (Hangzhou city government general office), 新势力 (new forces) measures')],
    ('local_vouchers_more.tsv', 20): [('body', '杭州市人民政府办公厅, AI+OPC measures', '杭州市人民政府办公厅 (Hangzhou city government general office), AI+OPC (one-person company) measures')],
    ('local_vouchers_more.tsv', 25): [('copy', 'the first quotation of the words cell is from', 'the first quotation above is from')],
    ('local_vouchers_more.tsv', 32): [('body', '深圳市工业和信息化局, payout of the home-made migration subsidy',
                                       '深圳市工业和信息化局 (Shenzhen industry and IT bureau): a centre recognised, and a planned payout of the home-made migration subsidy'),
                                      ('copy', '(its cells were read by hand, not by the checker)', '(its cells were read by eye)')],
    ('local_vouchers_more.tsv', 33): [('rate_home', '(100 million to 1 billion, cap 5 million)', '(from 100 million to under 1 billion, cap 5 million)'),   # 1亿元（含）—10亿元
                                      ('copy', 'with its text taken out by pdftotext (xm.gov.cn gives no answer); the text layer passes the 算力 control', 'whose text could be searched (xm.gov.cn gives no answer)')],
    ('local_vouchers_more.tsv', 35): [('body', '北京市经济和信息化局 北京市财政局', '北京市经济和信息化局 北京市财政局 (Beijing economy and IT bureau; finance bureau)'),
                                      ('kind', 'exclusion of flagged devices', 'no support for computing equipment that national departments have declared a security hazard or advised against using (the Word note: 国家有关部门明确声明存在安全隐患或不建议使用的算力设备)')],
    ('local_vouchers_more.tsv', 40): [('copy', '(the PDF answered 403 to the fetcher)', "(the PDF refused the project's request, error 403)")],
    ('local_vouchers_more.tsv', 45): [('rate_other', 'same (the condition is location, not chip)', "same, by the press article (its condition is location, not chip; the plan's text is not held)")],
    ('local_vouchers_more.tsv', 47): [('kind', 'separate incentives for home-made adaptation services, model services, data products and corpora',
                                       'separate incentives for adapting on home-made computing (30% of the contract), and for model services, data products and corpora')],   # the argument, point 17
    ('local_vouchers_more.tsv', 48): [('rate_other', '20% (computing services that are not 自主可控, and home-made large AI model token services)',
                                       '20% (computing services that are not 自主可控); home-made large AI model token services are paid 20% too')],
    ('local_vouchers_more.tsv', 51): [('document', "the two cities' voucher policies (算力券政策), not named in the reply; neither text is saved",
                                       "Shenyang's and Dalian's voucher policies (算力券政策), which the replies do not name; Shenyang's policy text has been saved since Nov 25, 2026 (row 103 of tables/local_vouchers_more.tsv), and Dalian's measures of 2025 are row 82 of that table"),
                                      ('copy', "says the two cities' vouchers support", 'says the vouchers of Shenyang and Dalian support'),
                                      ('copy', "(row 103 of this table); Dalian's measures of 2025 are row 82", "(row 103 of tables/local_vouchers_more.tsv); Dalian's measures of 2025 are row 82 of that table")],
    ('local_vouchers_more.tsv', 52): [('rate_other', 'same', 'not stated (the notice does not say whether the chip sets the tier)')],
    ('local_vouchers_more.tsv', 63): [('rate_other', 'same', 'not stated (the notice does not say whether the chip sets the tier)')],
    ('local_vouchers_more.tsv', 66): [('rate_home', 'paid from 10,000 yuan up', "paid only once a user's total for the year reaches 10,000 yuan (起付标准)")],
    ('local_vouchers_more.tsv', 69): [('rate_home', 'AI computing centres of 100 PFLOPS or more', 'AI computing centres of 100 PFLOPS (a measure of computing power) or more')],
    ('local_vouchers_more.tsv', 82): [('rate_other', "describe the two cities' vouchers in words that do not agree (row 103)",
                                       'describe the vouchers of Shenyang and Dalian in words that do not agree (row 103 of tables/local_vouchers_more.tsv)'),
                                      ('copy', "which speaks of the two cities' vouchers", 'which speaks of the vouchers of Shenyang and Dalian')],
    ('local_vouchers_more.tsv', 101): [('rate_home', "not read (by the search's account of the PDF: ", 'not read: the measures themselves were not reached (a search result described the PDF as paying '),
                                       ('rate_home', '2025-09-01 to 2028-08-31)', '2025-09-01 to 2028-08-31; no saved page shows it)'),
                                       ('rate_other', 'not read (the same account names one rate)', 'not read (that search result names one rate)')],
    ('local_vouchers_more.tsv', 103): [('rate_other', "Liaoning's data bureau describes the two cities' vouchers", "Liaoning's data bureau describes the vouchers of Shenyang and Dalian")],
    ('local_vouchers_more.tsv', 106): [('rate_home', "the city's 1028 industry system", "the city's “1028” industry system (the city's own name for a set of industries)")],
    ('local_vouchers_more.tsv', 113): [('rate_home', "the district adds 15% to the city's 30%",
                                        "the district adds a further 15% on top of the city's 30% subsidy (the summary does not say whether the 15% is of the bill or of the city's subsidy)")],
    ('local_vouchers_more.tsv', 114): [('date', 'in force on issue to 2027-06-30', 'in force from publication (自发布之日起) to 2027-06-30')],
    ('local_vouchers_more.tsv', 117): [('date', 'a trial in force on issue to 2026-12-20', 'a trial in force from publication (自发布之日起试行) to 2026-12-20')],
    ('local_vouchers_more.tsv', 126): [('document', '(by the search, 绍柯政办发〔2026〕4号; the measures are not saved)', '(绍柯政办发〔2026〕4号, the number a search result gave; the measures are not saved)')],
    ('local_vouchers_more.tsv', 128): [('date', 'signed 2024-07-17 (by the search)', "signed 2024-07-17 (the bureau's date on the file)")],   # 金华市数据局 2024年7月17日 in cn-ga31-vcityeast-25
    ('local_vouchers_more.tsv', 161): [('rate_home', 'up to 5 million yuan (by the search)', 'up to 5 million yuan a firm'),                  # 每家企业最高500万元 in cn-ga31-vcitysouth-74
                                       ('document', '(under 深福科工规〔2024〕7号, whose page gave no answer)', "(a guide to the district's measures of 2024, whose number no saved page shows)")],
    ('local_vouchers_more.tsv', 163): [('date', "in force to 2025-12-31; replaced on 2025-07-01 (the district's account)", "set to run to 2025-12-31, and replaced on 2025-07-01 by the district's account")],
    ('local_vouchers_more.tsv', 173): [('date', "(the search's reading of that rule)", '(that rule says so: row 10 of tables/local_vouchers_more.tsv)')],
    ('local_vouchers_more.tsv', 178): [('rate_other', 'same (no word for home-made computing in the clause) (a named centre)',
                                        "none: only computing bought from the named centre is paid, and the clause names no chip (Tianjin Daily, on the city government's site, says the centre runs 300P of purely home-made computing on Huawei's Ascend architecture)")],
    ('local_vouchers_more.tsv', 203): [('body', '贵阳市大数据发展管理局 and three other', '贵阳市大数据发展管理局 (Guiyang big data development administration) and three other')],
    ('local_vouchers_more.tsv', 207): [('rate_other', 'same (no word for home-made computing in the clause) (a named centre)', "none: only the named centre's services are paid, and the clause names no chip")],
    ('local_vouchers_more.tsv', 216): [('document', '(深福科工规〔2024〕7号 by the search; the page shows no number)', '(the page shows no document number; a search result gave 深福科工规〔2024〕7号, which no saved page shows)')],
}
# (table, row) -> [(words of the cell, the words shown)]: a passage cut before its verb is shown to the end of its clause (found by the checker in the copy)
WORDS_FIX = {('local_vouchers_more.tsv', 180): [('本措施自2025年9月18日', '本措施自2025年9月18日起施行，有效期3年')]}
# Words of the tables that recur on many lines: (pattern, the page's words). Each must be met at least once.
TERM_FIX = [(r"the owner's hand-saved PDFs", 'PDFs saved by hand'), (r"the owner's hand-saved PDF", 'a PDF saved by hand'), (r"owner's hand-saved PDF", 'a PDF saved by hand'),
            (r'gave no answer to the page saver', 'did not answer when the project tried to save it'),
            (r'\bDRC\b', 'development and reform commission'),
            (r'\brow B(\d+)\b', r'row \1 of tables/local_vouchers_more.tsv'),
            (r'PUE binding', "PUE (power usage effectiveness: a data centre's total power use over its computing equipment's) binding"),
            (r'; in the plan: no label\b', '; in the plan: not marked binding (约束性) or indicative (预期性)')]   # round 10: readers' leads L302, L304, L305
# A province line's heading and reading gain these words (the line's own document cell says why)
PROV_NOTE = {'Hainan': ('in its published text, which is marked abridged', True), 'Xinjiang': ('the date is that of a reply naming two plans whose texts were not found', False)}
# Words of the checked note's descriptions and check notes. The note calls the list of leads "the lane"; the page calls it the list.
NOTE_TERMS = [(r"\bthe lane's\b", "the list's"), (r'\bThe lane\b', 'The list'), (r'\bthe lane\b', 'the list'),
              (r'\(row (\d+)\)', r'(line \1 of this list)')]
# List line -> [(body or remark, the note's words, the page's words)]
NOTE_FIX = {
    '100': [('remark', 'I rendered that page and read it by eye:', 'That page was rendered and read by eye:'),
            ('remark', 'The text layer has only the list below.', 'The text layer has only the list quoted above.')],
    '16': [('remark', 'I searched for 180号, 工信部联通信 and 10月8日: none. Those three facts rest on the list.', 'A search of the PDF for 180号, 工信部联通信 and 10月8日 found none of them. Those three facts rest on the list alone.')],
    '8': [('remark', 'not in the text I read.', 'not in the text that was read.')],
    '46': [('remark', 'I read the whole processor table: 18 entries (counted by script, 18 "I级" marks', 'The whole processor table was read: 18 entries (counted by script: 18 "I级" (grade I) marks')],
    '64': [('remark', 'the CSET translation (line 45 of this list)', 'the CSET translation of the notice of that title (line 45 of this list)')],
}


def table_rows(name):
    ls = [l for l in (TABLES / name).read_text(encoding='utf-8').split('\n') if l.strip() and not l.startswith('#')]
    h = ls[0].split('\t')
    rows = [dict(zip(h, l.split('\t'))) for l in ls[1:]]
    if any(len(l.split('\t')) != len(h) for l in ls[1:]): stop(f'tables/{name}: a row does not have {len(h)} fields')
    return rows


def local_lines():
    """Round 4: the local voucher rules and provincial plans of tables/provinces_31.tsv, local_vouchers.tsv and
    local_vouchers_more.tsv, as lines of a sixth kind. A passage is shown only where cn_has.py can find it in a saved
    copy named on the row (Word and zip copies cannot be read by it); a voucher row with no such passage is left out and
    counted. A province row is always shown (its result is the point), with its passages where they are found."""
    out, left, fixed_rows = [], [], set()
    cell_met, words_met, term_hits = set(), set(), Counter()
    if not WORKING.search("text made in L15's folder") or WORKING.search('合肥市 (Hefei city), agent measures'): stop('WORKING: the control of the working-word screen fails')
    for name, wk, sk in (('provinces_31.tsv', 'exact_words', 'saved_ids'), ('local_vouchers.tsv', 'words', 'saved_id'),
                         ('local_vouchers_more.tsv', 'words', 'saved_id')):
        for i, r in enumerate(table_rows(name), 1):
            r = dict(r)
            for col_, old_, new_ in CELL_FIX.get((name, i), []):      # round 10: the cell's words shown as CELL_FIX gives them (each met once)
                if r[col_].count(old_) != 1: stop(f'CELL_FIX: tables/{name} row {i}, column {col_}: "{old_[:60]}" stands {r[col_].count(old_)} times, not once')
                r[col_] = r[col_].replace(old_, new_); cell_met.add((name, i, col_, old_))
            for old_, new_ in WORDS_FIX.get((name, i), []):
                if r[wk].count(old_) != 1: stop(f'WORDS_FIX: tables/{name} row {i}: "{old_}" stands {r[wk].count(old_)} times')
                r[wk] = r[wk].replace(old_, new_); words_met.add((name, i, old_))
            sids = [x for x in re.split(r'[\s;,]+', r[sk]) if x and (L.P / x).is_dir()]
            qs = []
            for part in re.split(r'\s*\|\|\s*|\s+/\s+', r[wk]):
                part = re.sub(r'\s*\([A-Za-z][^()]*\)\s*$', '', part.strip()).strip().strip('"').strip('“”').strip()   # a bracketed note of the table's own, in English, is not the page's
                if len(L.squash(part)) < 6: continue
                sid = next((x for x in sids if L.has(part, x)), None)
                if sid: qs.append({'words': part, 'sid': sid})
            prov = name == 'provinces_31.tsv'
            if not qs and not prov:
                left.append(f'{name} row {i}'); continue
            when = r['documents_issuers_dates'] if prov else r['date']
            # round 10: the first full date the cell gives, in either form (before, a later date written 2026-12-31 won over "Feb 13, 2025"
            # written first: Karamay's line showed its end date); checked on the three tables: that line is the only one this changes
            cands_ = [(m_.start(), m_.group(0)) for m_ in re.finditer(r'(20\d\d)-(\d\d)-(\d\d)', when)]
            cands_ += [(m_.start(), f'{m_.group(3)}-{[x[:3] for x in MON].index(m_.group(1)[:3]) + 1:02d}-{int(m_.group(2)):02d}')
                       for m_ in re.finditer(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)[a-z]*\.? (\d{1,2}), (20\d\d)', when)]
            iso = min(cands_)[1] if cands_ else ''
            if not iso:      # round 10 (look fault 5): a cell that gives only a month or a year is dated by the first one it gives
                ms = [m_ for m_ in (re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December) (20\d\d)\b', when),
                                    re.search(r'\b(20\d\d)\b', when)) if m_]
                if ms:
                    m = min(ms, key=lambda m_: m_.start())
                    iso = f'{m.group(2)}-{MONTH.index(m.group(1)) + 1:02d}' if m.lastindex == 2 else m.group(1)
            ns = lambda v: 'not stated' if v.strip() in ('', '-') else v.strip()
            if prov:
                pn = PROV_NOTE.get(r['government'])
                who = f"{r['government']}: {RESULT[r['result']]}" + (f' ({pn[0]})' if pn else '')
                reading = f"{RESULT[r['result']]}" + (f' ({pn[0]})' if pn and pn[1] else '') + (f"; in the plan: {r['binding_or_expected']}" if r['binding_or_expected'].strip() else '')
                desc = r['documents_issuers_dates']
                extra = r['rests_on']
            else:
                who = r['body']
                reading = f"home-made computing: {ns(r['rate_home'])}; other computing: {ns(r['rate_other'])}; kind: {ns(r['kind'])}"
                if r['rate_home'].strip().lower().startswith('no share') and ns(r['rate_other']) == 'not stated':   # round 10: a payment with no share is not shown under home-made computing
                    reading = f"{r['rate_home'].strip()} (the table gives no rate for home-made or for other computing apart); kind: {ns(r['kind'])}"
                desc = f"{r['document']}. Date as the table gives it: {r['date']}" if r['document'] else f"Date as the table gives it: {r['date']}"
                extra = r['copy'].strip()
            for old_, new_ in COPY_FIX.get((name, i), []):
                if extra.count(old_) != 1: stop(f'COPY_FIX: tables/{name} row {i}: "{old_}" stands {extra.count(old_)} times in the cell, not once')
                extra = extra.replace(old_, new_); fixed_rows.add((name, i))
            fields_ = [who, reading, desc, extra]
            for pat_, rep_ in TERM_FIX:
                for j_ in range(4):
                    fields_[j_], k_ = re.subn(pat_, rep_, fields_[j_]); term_hits[pat_] += k_
            who, reading, desc, extra = fields_
            for cell_ in (who, reading, desc, extra):      # round 10: no saved id inside the prose of a printed cell
                if re.search(r'\b(?:cn|ms|man)-[a-z0-9]+-[a-z0-9-]{3,}', cell_): stop(f'tables/{name} row {i}: a saved id stands in the prose of a printed cell: {cell_[:160]}')
            for cell_ in (who, reading, desc, extra):
                if WORKING.search(cell_): stop(f'tables/{name} row {i}: a cell this page prints holds a working word ("{WORKING.search(cell_).group(0)}"): add its plain words to COPY_FIX: {cell_[:160]}')
            out.append({'table': name, 'trow': i, 'prov': prov, 'result': r.get('result', ''), 'level': r.get('level', ''), 'iso': iso, 'who': who, 'kind_cell': '' if prov else r['kind'].strip(),
                        'reading': reading, 'desc': desc, 'extra': extra, 'quotes': qs, 'sids': sids or [x for x in re.split(r'[\s;,]+', r[sk]) if x]})
    if fixed_rows != set(COPY_FIX): stop(f'COPY_FIX: rows not met: {sorted(set(COPY_FIX) - fixed_rows)}')
    want_ = {(t_, i_, c_, o_) for (t_, i_), v_ in CELL_FIX.items() for c_, o_, _ in v_}
    if cell_met != want_: stop(f'CELL_FIX: entries not met: {sorted(want_ - cell_met)[:3]}')
    if words_met != {(t_, i_, o_) for (t_, i_), v_ in WORDS_FIX.items() for o_, _ in v_}: stop('WORDS_FIX: an entry was not met')
    if any(term_hits[p_] == 0 for p_, _ in TERM_FIX): stop(f'TERM_FIX: patterns met nowhere: {[p_ for p_, _ in TERM_FIX if not term_hits[p_]]}')
    if {g_ for g_ in PROV_NOTE} - {o_['who'].split(':')[0] for o_ in out if o_['prov']}: stop('PROV_NOTE: a government not met')
    return out, left


def voucher_counts():
    """Round 5: the voucher counts the 'Read with care' box prints, taken from the argument's own sentence
    (argument/argument_base.txt, point 3) and checked against a count by script, which also gives the names. Stops if
    they differ. Core edit 8 (Nov 25, 2026): the count by script is the project's table of classes,
    tables/local_vouchers_classes.tsv (made by scripts/cn_voucher_classes.py --write from the two voucher tables by the
    published rule). Until then it was the output of core edit 6's count script
    (atlas/core_edit/edit6_parts/vcount_as_stands.out), which is fixed at the tables' size of that day (two fewer rules) and
    no longer describes them: two more rules are counted since (Xiamen's and Xinjiang's)."""
    arg = (PROJ / 'argument' / 'argument_base.txt').read_text(encoding='utf-8')
    # Round 9 (Nov 25, 2026; voucher rounds 3 to 6): the argument's sentence now names what the count is (rules found by searches that went province by
    # province and city by city, not a census), four rules that pay for home-made computing only, and a third class of two kinds (one rate; Hangzhou's
    # two rates by a type of facility it does not name). The page prints the argument's own numbers and names, each checked against the table of classes.
    m = re.search(r'(\d+) of the (\d+) found by searches that went province by province and city by city, saved and read \(not a census of every local government\), '
                  r'pay more for home-made computing and still pay for other computing, (\d+), those of ([^()]+?), pay for home-made computing only, and (\d+) state no higher rate '
                  r'for home-made computing: (\d+) of them pay one rate whatever the chip, and one, (\w+)\'s, pays (\d+)% or (\d+)% by a type of computing facility that it does not name', arg)
    if not m: stop("the argument's voucher sentence (point 3) was not found in the words this builder expects")
    t, n, h = int(m.group(1)), int(m.group(2)), int(m.group(3)); home_arg = m.group(4); third, o = int(m.group(5)), int(m.group(6))
    two_name, two_a, two_b = m.group(7), m.group(8), m.group(9)
    cls = table_rows('local_vouchers_classes.tsv')
    TI, HO, ONE, TWO, NOT = ('pays more for home-made and still pays for other computing', 'pays for home-made computing only', 'one rate',
                             'two rates by a type of computing facility that the rule does not name', 'read and not counted')
    cc = Counter(r['class'] for r in cls)
    if set(cc) != {TI, HO, ONE, TWO, NOT}: stop(f'tables/local_vouchers_classes.tsv has a class this builder does not know: {sorted(cc)}')
    n_rows = len(table_rows('local_vouchers.tsv')) + len(table_rows('local_vouchers_more.tsv'))
    if len(cls) != n_rows: stop(f'tables/local_vouchers_classes.tsv has {len(cls)} rows; the two voucher tables have {n_rows}: run scripts/cn_voucher_classes.py --write')
    got = (cc[TI] + cc[HO] + cc[ONE] + cc[TWO], cc[TI], cc[HO], cc[ONE] + cc[TWO], cc[ONE], cc[TWO])
    if got != (n, t, h, third, o, 1): stop(f'the argument says {t}/{h}/{third} ({o} one rate, 1 two rates) of {n}; the table of classes says {got}')
    tn = sorted(r['government'] for r in cls if r['class'] == TI); hn = sorted(r['government'] for r in cls if r['class'] == HO)
    two = [r['government'] for r in cls if r['class'] == TWO]
    if len(tn) != t or len(hn) != h or not all(x in home_arg for x in hn) or two != [two_name]:
        stop(f'names from the table of classes do not match the argument: {tn} {hn} / "{home_arg}" {two} / {two_name}')
    counted = [r['government'] for r in cls if r['class'] != NOT]
    if len(set(counted)) != len(counted): stop('a government is counted twice in the table of classes')
    return {'n': n, 'tiered': t, 'home': h, 'third': third, 'one': o, 'tiered_names': ', '.join(tn), 'home_arg': home_arg,
            'two_name': two_name, 'two_a': two_a, 'two_b': two_b, 'not': cc[NOT]}


def voucher_class_of():
    """Round 9 (Nov 25, 2026): each voucher line says whether the published counting rule counts it, as the project's table of classes
    gives it (row A<i> is row i of tables/local_vouchers.tsv, row B<i> row i of tables/local_vouchers_more.tsv). (table, row) -> words.
    Stops unless every row of the two tables has its class row, in order, and the class row's saved id is one the voucher row names."""
    cls = table_rows('local_vouchers_classes.tsv')
    out = {}
    for name, p in (('local_vouchers.tsv', 'A'), ('local_vouchers_more.tsv', 'B')):
        for i, r in enumerate(table_rows(name), 1):
            c = [x for x in cls if x['row_id'] == f'{p}{i}']
            if len(c) != 1: stop(f'tables/local_vouchers_classes.tsv: {len(c)} rows for {p}{i}')
            c = c[0]
            if c['saved_id'] and c['saved_id'] not in re.split(r'[\s;,]+', r['saved_id']): stop(f'tables/local_vouchers_classes.tsv row {p}{i}: its copy {c["saved_id"]} is not named by tables/{name} row {i}')
            if c['class'] == 'read and not counted':      # the table's row ids (A<i>, B<i>) in a reason are given as the rows of the two tables this page names
                why = re.sub(r'\(row ([AB])(\d+)\)', lambda m_: f'(row {m_.group(2)} of tables/{"local_vouchers.tsv" if m_.group(1) == "A" else "local_vouchers_more.tsv"})', c['reason'])
                if re.search(r'\b[AB]\d+\b', why): stop(f'a row id of the table of classes is left in a reason: {why}')
                out[(name, i)] = f'No: {why}'
            elif c['class'] == 'one rate':      # round 10: the class "one rate" said as what it means (readers: rates that change by year or bracket are still one rate whatever the chip)
                out[(name, i)] = 'Yes; it states no higher rate for home-made computing (the same rate whatever the chip)'
            elif c['class'] == 'two rates by a type of computing facility that the rule does not name':
                out[(name, i)] = f'Yes; it states no higher rate for home-made computing ({c["class"]})'
            else: out[(name, i)] = f'Yes; it {c["class"]}'
    if len(out) != len(cls): stop('the table of classes has rows the two voucher tables do not')
    return out


def stop(msg):
    print('NOT WRITTEN: ' + msg); sys.exit(1)


def esc(s):
    return html.escape(s, quote=True)


def show_date(iso):
    p = iso.split('-')
    if len(p) == 3: return f'{MON[int(p[1]) - 1]} {int(p[2])}, {p[0]}'
    if len(p) == 2: return f'{MON[int(p[1]) - 1]} {p[0]}'
    return iso


def date_forms(iso):
    p = iso.split('-'); y, m = int(p[0]), int(p[1])
    if len(p) == 3:
        d = int(p[2])
        return [f'{y}年{m}月{d}日', f'{y}年{m:02d}月{d:02d}日', f'{y}-{m:02d}-{d:02d}', f'{y}/{m:02d}/{d:02d}', f'{y}.{m:02d}.{d:02d}',
                f'{MONTH[m - 1]} {d}, {y}', f'{MONTH[m - 1][:3]} {d}, {y}', f'{d} {MONTH[m - 1]} {y}', f'{y}-{m}-{d}', f'{y}/{m}/{d}']
    return [f'{y}年{m}月', f'{MONTH[m - 1]} {y}', f'{y}-{m:02d}', f'{y}年{m:02d}月']


def has_cjk(s):
    return bool(re.search(r'[㐀-鿿]', s))


def parse_kinds(note):
    m = re.search(r'^\*\*Kinds of source\.\*\* (.*)$', note, flags=re.M)
    if not m: stop('the note has no "Kinds of source" paragraph')
    text = m.group(1)
    if not text.startswith('Most rows are official texts. '): stop('the "Kinds of source" paragraph does not begin as expected')
    kinds = {}
    for clause in text[len('Most rows are official texts. '):].rstrip('.').split(';'):
        head = re.split(r' (?:are|is) ', clause.strip(), maxsplit=1)
        if len(head) != 2: stop(f'kinds of source: a clause this script cannot read: {clause[:60]}')
        nums = re.findall(r'\d+', head[0]); what = head[1]
        if what.startswith('press reports'): k = 'press'
        elif what.startswith('official texts or figures as carried by news outlets'): k = 'carried'
        elif what.startswith('company filings or company statements'): k = 'company'
        elif what.startswith("an advisory committee's roadmap"): k = 'roadmap'
        elif what.startswith("a think tank's translation"): k = 'translation'
        else: stop(f'kinds of source: a kind this script does not know: {what[:60]}')
        for n in nums:
            if n in kinds: stop(f'kinds of source: row {n} is named twice')
            kinds[n] = k
    return kinds


def parse_note():
    note = NOTE.read_text(encoding='utf-8')
    kinds = parse_kinds(note)
    main, tail = note.split('\n## Counts by verdict', 1)
    counts = dict(re.findall(r'^\| (CONFIRMED|CONFIRMED IN PART|NOT IN THE PAGE|PAGE EMPTY|NOT HELD|All) \| (\d+) \|$', tail, flags=re.M))
    rows = []
    for part in re.split(r'^### ', main, flags=re.M)[1:]:
        lines = part.rstrip().splitlines()
        m = re.fullmatch(r'Row (\d+) · (\S+) · (FOR|AGAINST|context) · \[([^\]]+)\]', lines[0].strip())
        if not m: stop(f'a heading this script cannot read: {lines[0][:80]}')
        r = {'row': m.group(1), 'date0': m.group(2), 'sid': m.group(4), 'quotes': [], 'read_sid': m.group(4), 'read_note': ''}
        for ln in lines[1:]:
            if ln.startswith('- Body: '): r['body'] = ln[8:].strip()
            elif ln.startswith('- Address: '): r['addr'] = ln[11:].strip()
            elif ln.startswith("- The lane's claim: "): r['claim'] = ln[20:].strip()
            elif ln.startswith("- The lane's claim, as the new carrier words it: "): r['claim'] = ln[49:].strip()   # core edit 7b (Nov 25, 2026): a row re-read in another carrier's page
            elif ln.startswith('- The copy first read for this row, '):
                # core edit 7b (Nov 25, 2026; atlas/ROUND8.txt R5): the first copy is no longer cited; the note's sentence is shown without its
                # reference to the project's own files, and the build stops if the sentence does not read as expected
                c = re.fullmatch(r'- (The copy first read for this row, .*?, is no longer cited) \(ROUND8 R5; tables/replaced_copies\.tsv\)\.', ln)
                if not c: stop(f'row {r["row"]}: a "copy first read" line this script cannot read')
                r['first_copy'] = 'Read in the copy named below: its passages and date words are that page\'s.'      # round 10: the copy first read is not recounted (readers' lead)
            elif ln.startswith('- Verdict: '):
                v = re.fullmatch(r'\*\*([A-Z ]+)\*\*\.?\s*(.*)', ln[11:].strip())
                if not v: stop(f'row {r["row"]}: a verdict this script cannot read')
                r['verdict'], r['remark'] = v.group(1), v.group(2).strip()
            elif ln.startswith('- Read in: '):
                c = re.fullmatch(r'- Read in: (an Internet Archive capture of [A-Z][a-z]+ \d+, \d{4}), saved as \[([^\]]+)\]\. .*', ln)
                if not c: stop(f'row {r["row"]}: a "Read in" line this script cannot read')
                r['read_note'], r['read_sid'] = c.group(1), c.group(2)
            elif ln.startswith('- The page'):
                q = re.fullmatch(r'- The page( \(in the page body; not in the text copy\))?: "(.*)"', ln)
                if not q: stop(f'row {r["row"]}: a passage line this script cannot read: {ln[:70]}')
                r['quotes'].append({'words': q.group(2), 'form': 'body' if q.group(1) else 'page', 'en': ''})
            elif ln.startswith('  - My translation: '):
                if not r['quotes'] or r['quotes'][-1]['en']: stop(f'row {r["row"]}: a translation without its passage')
                r['quotes'][-1]['en'] = re.sub(r'["“”]', '', ln[20:]).strip()          # our own English carries no quote marks
            elif ln.strip():
                stop(f'row {r["row"]}: a line this script does not know: {ln[:70]}')
        for k in ('body', 'addr', 'claim', 'verdict'):
            if k not in r: stop(f'row {r["row"]}: no {k}')
        if not r['addr'].startswith('http'): stop(f'row {r["row"]}: the address is not a web address')
        r['kind'] = kinds.pop(r['row'], 'official')
        rows.append(r)
    if kinds: stop(f'kinds of source names rows that are not in the note: {sorted(kinds)}')
    got = Counter(r['verdict'] for r in rows)
    for k, v in counts.items():
        if k != 'All' and got.get(k, 0) != int(v): stop(f'the note counts {v} rows {k}; this script read {got.get(k, 0)}')
    if len(rows) != int(counts['All']): stop(f'the note counts {counts["All"]} rows; this script read {len(rows)}')
    if len({r['row'] for r in rows}) != len(rows): stop('a row number stands twice')

    # the one row whose first copy was a refusal page: the note's addendum reads it in a second copy
    empty = [r for r in rows if r['verdict'] == 'PAGE EMPTY']
    add = re.search(r'\n## Addendum by the main session[^\n]*\n\n(.*)', note, flags=re.S)
    if len(empty) != 1 or not add: stop('expected one PAGE EMPTY row and the addendum that reads it in another copy')
    a = re.search(r'Row (\d+) \([^)]*\) was PAGE EMPTY above\. The same article is now saved from (a radio station\'s site that carries Reuters) \[([^\]]+)\] \((https?://\S+)\)\. '
                  r'Verdict: \*\*CONFIRMED\*\*\. The page\'s words: "(.*?)"; "(.*?)" This is reporting', add.group(1))
    if not a or a.group(1) != empty[0]['row']: stop('the addendum does not read as expected')
    e = empty[0]
    e.update(verdict='CONFIRMED', second=True, read_sid=a.group(3), read_note='a second copy, ' + a.group(2), addr2=a.group(4),
             remark='The page first saved was a refusal page. The same article was then read in a second copy, and the line was confirmed there.',
             quotes=[{'words': a.group(5), 'form': 'page', 'en': ''}, {'words': a.group(6), 'form': 'page', 'en': ''}])
    for key, (iso, words) in UNDATED.items():
        if words not in note: stop(f'the note does not say "{words}" (the date used for row {key})')
    return rows, note


def cross_check(rows):
    """The passages parsed from the note must be the strings in the note's own table of quotations, row by row."""
    table = {}
    for ln in QTSV.read_text(encoding='utf-8').splitlines()[1:]:
        c = ln.split('\t')
        if len(c) != 5: stop(f'policies_checked_quotes.tsv: a line without five fields: {ln[:60]}')
        table.setdefault(c[0], []).append((c[1], c[3], c[4]))
    n = 0
    for r in rows:
        if r.get('second'):
            if r['row'] in table: stop(f'row {r["row"]} was a refusal page but has lines in the table of quotations')
            continue
        mine = [(r['read_sid'], q['words'], q['form']) for q in r['quotes']]
        if mine != table.get(r['row'], []): stop(f'row {r["row"]}: the passages in the note are not those in its table of quotations')
        n += len(mine)
    return n


def set_dates(rows):
    for r in rows:
        r['date_from'] = 'list'
        if r['date0'] == 'undated':
            if r['row'] in UNDATED: r['iso'], r['date_from'] = UNDATED[r['row']][0], 'page'
            elif r['row'] in FOUND_HERE: r['iso'], r['date_from'] = FOUND_HERE[r['row']][0], 'here'
            else: r['iso'] = ''
        else:
            if not re.fullmatch(r'\d{4}-\d\d(-\d\d)?', r['date0']): stop(f'row {r["row"]}: a date this script cannot read: {r["date0"]}')
            r['iso'] = r['date0']
        r['date_words'] = []
        if not r['iso']: continue
        if r['row'] in DATE_WORDS: r['date_words'] = DATE_WORDS[r['row']]
        elif r['row'] in FOUND_HERE: r['date_words'] = FOUND_HERE[r['row']][1]
        else:
            for f in date_forms(r['iso']):
                if L.has(f, r['read_sid']): r['date_words'] = [f]; break


QUOTED = re.compile(r'"([^"]+)"|“([^”]+)”')
# Words the note puts in quotation marks as the LANE's wording, which also happen to stand somewhere in the saved page.
# They are not shown as the page's words: (list line, words). Each must be met in the note, or the build stops.
LANE_WORDS = {('52', 'supported')}


def mark_quoted(text, sid, keep, row='', met=None):
    """HTML for a line of the note. A quoted string that cn_has.py can find in the saved copy keeps its quotation marks
    (and is added to keep, for quotes.tsv); any other quoted string is set in italics without quotation marks."""
    out, pos = [], 0
    for m in QUOTED.finditer(text):
        out.append(esc(text[pos:m.start()])); pos = m.end()
        q = m.group(1) or m.group(2)
        if (row, q) in LANE_WORDS:
            if met is not None: met.add((row, q))
            out.append('<i>' + esc(q) + '</i>')
        elif len(L.squash(q)) >= 6 and L.has(q, sid):
            keep.append((sid, q)); out.append('“' + esc(q) + '”')
        else:
            out.append('<i>' + esc(q) + '</i>')
    out.append(esc(text[pos:]))
    s = ''.join(out)
    s = re.sub(r'`([^`]+)`', r'\1', s)
    return re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)


def text_only(h):
    return html.unescape(re.sub(r'<[^>]+>', '', h))


def search_norm(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', s).lower()).strip()


CSS = """
:root { --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#7a7872; --grid:#e1e0d9; --axis:#c3c2b7;
  --border:rgba(11,11,11,0.12); --wash:rgba(11,11,11,0.045); --toward:#256abf; --away:#c44e18; --link:#1c5cab;
  --font-text:"Inter",system-ui,-apple-system,"Segoe UI","Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;
  --font-head:"Space Grotesk","Inter",system-ui,sans-serif; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --page:#0d0d0d; --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7;
  --muted:#8f8d86; --grid:#2c2c2a; --axis:#45453f; --border:rgba(255,255,255,0.14); --wash:rgba(255,255,255,0.06);
  --toward:#3987e5; --away:#d95926; --link:#86b6ef; color-scheme:dark } }
:root[data-theme="dark"] { --page:#0d0d0d; --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#8f8d86; --grid:#2c2c2a; --axis:#45453f;
  --border:rgba(255,255,255,0.14); --wash:rgba(255,255,255,0.06); --toward:#3987e5; --away:#d95926; --link:#86b6ef; color-scheme:dark }
* { box-sizing:border-box; }
html { -webkit-text-size-adjust:100%; }
body { margin:0; background:var(--page); color:var(--ink); font-family:var(--font-text); font-size:16px; line-height:1.5; }
[hidden] { display:none !important; }
a { color:var(--link); }
.wrap { max-width:1120px; margin:0 auto; padding:30px 16px 56px; }
.eyebrow { font:700 12px/1 var(--font-text); letter-spacing:0.1em; text-transform:uppercase; color:var(--muted); margin:0 0 12px; }
h1 { font-family:var(--font-head); font-size:clamp(27px,3.6vw,42px); line-height:1.08; letter-spacing:-0.015em; margin:0 0 12px; max-width:26ch; text-wrap:balance; }
.deck { margin:0 0 14px; color:var(--ink2); font-size:18px; line-height:1.45; max-width:74ch; }
.note { margin:0 0 4px; color:var(--muted); font-size:13.5px; line-height:1.45; max-width:92ch; }
.cols { display:grid; gap:14px; grid-template-columns:1fr; margin:20px 0 6px; align-items:start; }   /* a card ends with its text */
h2.sep { font:700 12.5px/1.3 var(--font-text); letter-spacing:0.07em; text-transform:uppercase; color:var(--ink2); margin:26px 0 4px; padding:0 0 6px; border-bottom:1.5px solid var(--ink2); }
@media (min-width: 900px) { .cols { grid-template-columns:1fr 1fr; } }
.card { background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:16px 18px; min-width:0; }
.card h2 { font:700 12px/1.2 var(--font-text); letter-spacing:0.09em; text-transform:uppercase; color:var(--ink2); margin:0 0 8px; }
.card ul { margin:0; padding-left:18px; font-size:14.5px; line-height:1.5; color:var(--ink2); }
.card li { margin:0 0 5px; } .card li b { color:var(--ink); font-weight:600; }
.tools { position:sticky; top:0; z-index:5; background:var(--page); padding:14px 0 10px; margin-top:10px; border-bottom:1.5px solid var(--ink2); }
.find { display:flex; flex-wrap:wrap; align-items:center; gap:8px 14px; }
.find label { font:700 12px/1 var(--font-text); letter-spacing:0.09em; text-transform:uppercase; color:var(--ink2); flex:0 0 auto; }
.find input { flex:1 1 260px; min-width:0; font:inherit; font-size:16px; padding:9px 12px; border:1.5px solid var(--ink2); border-radius:10px; background:var(--surface); color:var(--ink); }
.find input:focus-visible, button:focus-visible, summary:focus-visible { outline:2.5px solid var(--ink); outline-offset:2px; }
#count { flex:0 0 auto; font-size:14px; font-weight:600; color:var(--ink2); font-variant-numeric:tabular-nums; }
.bar { display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin:12px 0 0; }
button { font:600 13px/1 var(--font-text); padding:7px 10px; border-radius:999px; border:1.5px solid var(--border); background:var(--surface); color:var(--ink2); cursor:pointer; }
button[aria-pressed="true"] { background:var(--ink); color:var(--page); border-color:var(--ink); }
button .n { font-variant-numeric:tabular-nums; font-weight:500; opacity:0.8; margin-left:3px; }
.bar .gap { flex:1 1 12px; }
.try { margin:10px 0 0; font-size:13.5px; color:var(--muted); display:flex; flex-wrap:wrap; align-items:center; gap:6px; }
.try button { padding:5px 9px; font-weight:500; }
#none { margin:22px 0; color:var(--ink2); }
details.r { border-bottom:1px solid var(--grid); }
summary { list-style:none; cursor:pointer; position:relative; }
summary::-webkit-details-marker { display:none; }
details.r > summary { display:grid; grid-template-columns:104px minmax(0,1fr) auto; gap:2px 16px; padding:12px 26px 12px 0; }
details.r > summary::after, .how > summary::after { content:""; position:absolute; right:6px; top:19px; width:8px; height:8px; border-right:2px solid var(--muted); border-bottom:2px solid var(--muted); transform:rotate(45deg); }
details.r[open] > summary::after { transform:rotate(-135deg); top:23px; }
.how > summary { padding-right:26px; } .how > summary h2 { margin:0; } .how[open] > summary h2 { margin-bottom:8px; }
.how > summary::after { top:1px; } .how[open] > summary::after { transform:rotate(-135deg); top:5px; }
.d { font-size:14px; font-weight:600; font-variant-numeric:tabular-nums; white-space:nowrap; padding-top:1px; }
.d.no { font-weight:500; color:var(--muted); white-space:normal; }
.who { min-width:0; }
.b { margin:0; font-weight:600; font-size:15.5px; line-height:1.4; }
.t { margin:2px 0 0; color:var(--ink2); font-size:14.5px; line-height:1.45; overflow-wrap:anywhere; }
.t.no { color:var(--muted); }
.tags { display:flex; flex-wrap:wrap; gap:5px; justify-content:flex-end; align-content:flex-start; max-width:250px; }
.tag { font:700 10.5px/1.15 var(--font-text); letter-spacing:0.05em; text-transform:uppercase; padding:4px 6px; border-radius:5px; background:var(--wash); color:var(--ink2); text-align:right; }
.tag.v { background:transparent; border:1.5px solid var(--axis); padding:2.5px 5px; }
.tag.v.part { border-color:var(--ink); color:var(--ink); }
.x { padding:2px 0 18px 120px; max-width:980px; }
.q { margin:0 0 12px; padding:1px 0 1px 13px; border-left:3px solid var(--axis); }
.q p { margin:0; }
.q .w { font-size:16.5px; line-height:1.62; overflow-wrap:anywhere; }
.q .w.en0 { font-size:15.5px; line-height:1.5; }
.q .e { margin-top:3px; color:var(--ink2); font-size:15px; line-height:1.5; }
.lab { font:700 10.5px/1 var(--font-text); letter-spacing:0.07em; text-transform:uppercase; color:var(--muted); margin-right:6px; }
.more { margin:0 0 12px; }
.more > summary { display:inline-block; padding:4px 0; font-size:13.5px; font-weight:600; color:var(--ink2); text-decoration:underline; text-underline-offset:3px; }
.more[open] > summary { margin-bottom:8px; }
.m { margin:0 0 5px; font-size:13.5px; line-height:1.5; color:var(--ink2); overflow-wrap:anywhere; }
.m i { font-style:italic; }
.m a { overflow-wrap:anywhere; }
.m code { font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:12.5px; line-height:1; color:var(--ink2); }   /* line-height 1: the id's font must not change the height of its line (a late fallback font once made every line 1 px taller after the first paint) */
footer { margin-top:30px; padding-top:14px; border-top:1px solid var(--grid); color:var(--muted); font-size:13.5px; line-height:1.5; max-width:92ch; }
footer p { margin:0 0 6px; }
@media (max-width: 720px) {
  details.r > summary { grid-template-columns:auto minmax(0,1fr); grid-template-areas:"d tags" "who who"; gap:6px 10px; padding-right:24px; }   /* the date keeps its width; the kind marks wrap in what is left (they once lay over the date) */
  .d { grid-area:d; } .tags { grid-area:tags; max-width:none; } .who { grid-area:who; }
  .x { padding-left:0; }
  .deck { font-size:17px; }
}
"""

JS = r"""
(function () {
  var rows = Array.prototype.slice.call(document.querySelectorAll('details.r'));
  var seps = Array.prototype.slice.call(document.querySelectorAll('h2.sep'));
  var hay = rows.map(function (r) { return r.getAttribute('data-s'); });
  var tight = hay.map(function (h) { return h.replace(/\s+/g, ''); });
  var input = document.getElementById('q'), count = document.getElementById('count'), none = document.getElementById('none');
  var kindButtons = Array.prototype.slice.call(document.querySelectorAll('button[data-kind]'));
  var toggle = document.getElementById('toggle');
  var partButton = document.getElementById('part');
  var kind = 'all', view = 'auto', part = false;
  var how = document.getElementById('how');
  if (window.matchMedia('(max-width: 720px)').matches) how.open = false;
  function norm(s) { return (s.normalize ? s.normalize('NFKC') : s).toLowerCase().replace(/\s+/g, ' ').trim(); }
  function apply() {
    var q = norm(input.value), terms = q ? q.split(' ') : [], shown = 0;
    var openAll = view !== 'closed';
    rows.forEach(function (r, i) {
      var ok = (kind === 'all' || r.getAttribute('data-kind') === kind) && (!part || r.getAttribute('data-part') === '1') &&
        terms.every(function (t) { return hay[i].indexOf(t) !== -1 || tight[i].indexOf(t) !== -1; });
      r.hidden = !ok;
      if (ok) { shown += 1; r.open = terms.length ? view !== 'closed' : openAll; }
    });
    count.textContent = shown === rows.length ? 'All ' + rows.length + ' lines' : shown + ' of ' + rows.length + ' lines';
    seps.forEach(function (h) { var g = h.getAttribute('data-g'); h.hidden = !rows.some(function (r) { return !r.hidden && r.getAttribute('data-g') === g; }); });
    none.hidden = shown !== 0;
    kindButtons.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-kind') === kind ? 'true' : 'false'); });
    partButton.setAttribute('aria-pressed', part ? 'true' : 'false');
    toggle.textContent = (terms.length ? view !== 'closed' : openAll) ? 'Close all' : 'Open all';
  }
  function remember() {
    var parts = [];
    if (input.value.trim()) parts.push('q=' + encodeURIComponent(input.value.trim()));
    if (kind !== 'all') parts.push('kind=' + kind);
    if (part) parts.push('part=1');
    if (view !== 'auto') parts.push('view=' + view);
    try { history.replaceState(null, '', parts.length ? '#' + parts.join('&') : location.pathname + location.search); } catch (e) {}
  }
  function fromHash() {
    location.hash.replace(/^#/, '').split('&').forEach(function (p) {
      var k = p.split('=')[0], v = p.slice(k.length + 1);
      try { v = decodeURIComponent(v); } catch (e) {}
      if (k === 'q') input.value = v;
      if (k === 'kind' && document.querySelector('button[data-kind="' + v + '"]')) kind = v;
      if (k === 'part' && v === '1') part = true;
      if (k === 'view' && (v === 'open' || v === 'closed')) view = v;
    });
  }
  input.addEventListener('input', function () { apply(); remember(); });
  kindButtons.forEach(function (b) { b.addEventListener('click', function () { kind = b.getAttribute('data-kind'); apply(); remember(); }); });
  partButton.addEventListener('click', function () { part = !part; apply(); remember(); });
  toggle.addEventListener('click', function () { view = toggle.textContent === 'Open all' ? 'open' : 'closed'; apply(); remember(); });
  Array.prototype.forEach.call(document.querySelectorAll('button[data-try]'), function (b) {
    b.addEventListener('click', function () { input.value = b.getAttribute('data-try'); apply(); remember(); input.focus(); });
  });
  fromHash(); apply();
})();
"""

TRY = ['英伟达', 'Nvidia', '国产', 'Shanghai', 'procurement', 'Micron']
EXPECT = TRY + ['财库 119号', '安全可靠 测评', 'no-such-word-zzqx', '算力券', 'Province']


def main():
    B.load_clip()
    rows, note = parse_note()
    n_table = cross_check(rows)
    for r in rows:
        if r['row'] in REPOINT:
            new, addr, why = REPOINT[r['row']]
            old = r['read_sid']; r['sid'] = new; r['read_sid'] = new; r['read_note'] = ''
            r['addr2'] = r['addr']; r['addr'] = addr
            r['repoint_note'] = "Read in the evaluation centres' own page: its passages and date words are that page's."      # round 10: no history of copies
            for q in r['quotes']:
                if len(L.squash(q['words'])) >= 6 and not L.has(q['words'], new): stop(f'REPOINT: line {r["row"]}: a passage is not in {new}')
    if sorted(r['row'] for r in rows if r.get('repoint_note')) != sorted(REPOINT): stop('REPOINT: a line was not met')
    set_dates(rows)
    body_met = []
    for r in rows:
        for old, new in BODY_FIX:
            if old in r['body']: r['body'] = r['body'].replace(old, new); body_met.append(old)
    for r in rows:
        for old, new in REMARK_FIX.get(r['row'], []):
            if r['remark'].count(old) != 1: stop(f'REMARK_FIX: line {r["row"]}: the note no longer has "{old[:40]}" once')
            r['remark'] = r['remark'].replace(old, new)
    if any(not any(r['row'] == k for r in rows) for k in REMARK_FIX): stop('REMARK_FIX: a line was not met')
    note_hits = Counter()
    for r in rows:          # round 10: the note's "lane" is this page's list; its "(row N)" is a line of the list
        for k_ in ('body', 'remark'):
            for pat_, rep_ in NOTE_TERMS:
                r[k_], n_ = re.subn(pat_, rep_, r[k_]); note_hits[pat_] += n_
    if any(note_hits[p_] == 0 for p_, _ in NOTE_TERMS): stop(f'NOTE_TERMS: patterns met nowhere: {[p_ for p_, _ in NOTE_TERMS if not note_hits[p_]]}')
    for r in rows:
        for k_, old, new in NOTE_FIX.get(r['row'], []):
            if r[k_].count(old) != 1: stop(f'NOTE_FIX: line {r["row"]}: "{old[:50]}" stands {r[k_].count(old)} times in its {k_}')
            r[k_] = r[k_].replace(old, new)
    if set(NOTE_FIX) - {r['row'] for r in rows}: stop('NOTE_FIX: a line was not met')
    for r in rows:
        for k_ in ('body', 'remark'):
            if re.search(r"\blane\b|\bI (read|rendered|searched)\b|\(row \d+\)", r[k_]): stop(f'line {r["row"]}: its {k_} still holds a working word: {r[k_][:120]}')
    if set(EN_SRC) != set(EN_FIX): stop('EN_SRC and EN_FIX name different lines')
    _core = {'argument': (PROJ / 'argument' / 'argument_base.txt').read_text(encoding='utf-8'), 'record': (PROJ / 'OFFICIAL_RECORD.md').read_text(encoding='utf-8')}
    for k_, pairs_ in EN_FIX.items():
        for _, new_ in pairs_:
            if EN_SRC[k_] == 'record' and new_ not in _core['record']:      # the argument's four were checked in round 4 against the argument as it then stood
                stop(f'EN_FIX: line {k_}: the record does not hold the wording the page takes from it: {new_[:60]}')
    for k_, w_ in EN_CHECK.items():
        if w_ not in _core['argument']: stop(f'EN_CHECK: line {k_}: the argument no longer holds "{w_[:60]}"')
    for r in rows:
        for old, new in EN_FIX.get(r['row'], []):
            hit = [q for q in r['quotes'] if old in (q['en'] or '')]
            if len(hit) != 1: stop(f'EN_FIX: line {r["row"]}: the note no longer has "{old[:40]}" once')
            hit[0]['en'] = hit[0]['en'].replace(old, new)
    for r in rows:
        for q in r['quotes']:
            if has_cjk(q['words']) and not q['en']: stop(f'row {r["row"]}: a Chinese passage without our English')
    short = []          # passages under six characters: cn_has.py will not test them, so the page does not show them
    for r in rows:
        for q in r['quotes']:
            if len(L.squash(q['words'])) < 6: short.append(r['row'])
        r['quotes'] = [q for q in r['quotes'] if len(L.squash(q['words'])) >= 6]
        if not r['quotes']: stop(f'row {r["row"]}: no passage long enough to check')
    rows.sort(key=lambda r: (0, r['iso']) if r['iso'] else (1, ''))        # by date; the two without a date last (the sort keeps the note's order within a date)

    keep = []           # (saved id, words): quoted strings kept in quotation marks in the body and check lines
    lines_q = []        # (saved id, words): everything for quotes.tsv
    cards = []
    met = set()         # the LANE_WORDS entries met in the note
    for r in rows:
        sid = r['read_sid']
        title = re.sub(r'\s*<br\s*/?>\s*', ' ', B.title_of(sid))
        body_h = mark_quoted(r['body'], sid, keep, r['row'], met)
        remark_h = mark_quoted(r['remark'], sid, keep, r['row'], met) if r['remark'] else ''
        for q in r['quotes']: lines_q.append((sid, q['words']))
        for w in r['date_words']: lines_q.append((sid, w))
        kind_label = KIND_LABEL[r['kind']]
        v_label = 'Confirmed in part' if r['verdict'] == 'CONFIRMED IN PART' else ('Confirmed, in a second copy' if r.get('second') else 'Confirmed')
        if r['verdict'] not in ('CONFIRMED', 'CONFIRMED IN PART'): stop(f'row {r["row"]}: verdict {r["verdict"]} has no label')
        if r['iso']:
            d_html = f'<span class="d">{esc(show_date(r["iso"]))}</span>'
            if r['date_from'] == 'page': d_note = 'The date is the one the page gives (the list of leads gave none).'      # round 10: readers' leads
            elif r['date_from'] == 'here': d_note = 'The date is the signing date in the page (the list of leads gave none).'
            else: d_note = ''
            if r['date_words']:
                d_note += (' ' if d_note else '') + 'Date words found in the saved copy: ' + '; '.join('“' + esc(w) + '”' for w in r['date_words']) + '.'
            else:
                d_note += (' ' if d_note else '') + 'The date is the list\'s. The script did not find it written in the saved copy.'
        else:
            d_html = '<span class="d no">no date found</span>'
            d_note = 'The list gave no date and none was found in the copy read.'

        def passage(q):
            cjk = has_cjk(q['words'])
            where = ' <span class="lab">in the page body, not in the text copy</span>' if q['form'] == 'body' else ''
            h = f'<div class="q"><p class="w{"" if cjk else " en0"}"{" lang=\"zh-Hans\"" if cjk else ""}>“{esc(q["words"])}”{where}</p>'
            if q['en']: h += f'<p class="e"><span class="lab">Our English</span>{esc(q["en"])}</p>'
            return h + '</div>'

        # the passage shown first: the note's first one that is a sentence and not only a number or a date (20 characters or more)
        key = next((q for q in r['quotes'] if len(L.squash(q['words'])) >= 20), r['quotes'][0])
        rest = [q for q in r['quotes'] if q is not key]
        x = [passage(key)]
        if rest:
            x.append(f'<details class="more"><summary>{len(rest)} more passage{"s" if len(rest) > 1 else ""} from this page</summary>' + ''.join(passage(q) for q in rest) + '</details>')
        if remark_h: x.append(f'<p class="m"><span class="lab">Check note</span>{remark_h}</p>')
        if r.get('repoint_note'): x.append(f'<p class="m"><span class="lab">Copy</span>{esc(r["repoint_note"])}</p>')
        if r.get('first_copy'): x.append(f'<p class="m"><span class="lab">Copy</span>{esc(r["first_copy"])}</p>')
        x.append(f'<p class="m"><span class="lab">Date</span>{d_note}</p>')
        addr = f'<a href="{esc(r["addr"])}" rel="noopener">{esc(r["addr"])}</a>'
        if r.get('addr2') and not r.get('repoint_note'): addr += '. Second copy: ' + f'<a href="{esc(r["addr2"])}" rel="noopener">{esc(r["addr2"])}</a>'
        x.append(f'<p class="m"><span class="lab">Address</span>{addr}</p>')
        ids = f'<code>{esc(r["sid"])}</code>'
        if r['read_sid'] != r['sid']: ids += f'. Read in {esc(r["read_note"])}, saved as <code>{esc(r["read_sid"])}</code>'
        x.append(f'<p class="m"><span class="lab">Saved copy</span>{ids}. Line {esc(r["row"])} of the list.</p>')
        t_html = f'<p class="t"{" lang=\"zh-Hans\"" if has_cjk(title) else ""}>{esc(title)}</p>' if title else '<p class="t no">No title is held for this copy.</p>'
        summ = (f'<summary>{d_html}<div class="who"><p class="b">{body_h}</p>{t_html}</div>'
                f'<span class="tags"><span class="tag">{esc(kind_label)}</span><span class="tag v{" part" if r["verdict"] == "CONFIRMED IN PART" else ""}">{esc(v_label)}</span></span></summary>')
        inner = summ + '<div class="x">' + ''.join(x) + '</div>'
        r['search'] = search_norm(' '.join([r['iso'], text_only(inner)]))
        if not cards: cards.append(f'<h2 class="sep" data-g="note">From the checked note: policy lines, by date</h2>')      # round 10 (look fault 2)
        cards.append(f'<details class="r" open data-kind="{GROUP[r["kind"]]}" data-g="note" data-part="{1 if r["verdict"] == "CONFIRMED IN PART" else 0}" data-s="{esc(r["search"])}">{inner}</details>')

    if met != LANE_WORDS: stop(f'LANE_WORDS entries not met in the note: {sorted(LANE_WORDS - met)}')

    n_note_q = len(lines_q)        # round 10: lines_q holds the note lines' strings up to here; the tables' lines' strings follow, then the check notes' quoted strings
    local, left_out = local_lines()
    VCLASS = voucher_class_of()
    for r in local:
        for old, new in BODY_FIX:
            if old in r['who']: r['who'] = r['who'].replace(old, new); body_met.append(old)
    if sorted(body_met) != sorted(o for o, _ in BODY_FIX): stop(f'BODY_FIX: not each met once: {body_met}')
    rep_met = []
    for r in local:
        k = (r['table'], r['trow'])
        if k in REPEALED:
            sid_, words_, note_ = REPEALED[k]
            if not L.has(words_, sid_): stop(f'REPEALED: "{words_}" not found in {sid_}')
            r['repealed'] = note_; rep_met.append(k); lines_q.append((sid_, words_))
    if sorted(rep_met) != sorted(REPEALED): stop(f'REPEALED: rows not met: {sorted(set(REPEALED) - set(rep_met))}')
    local.sort(key=lambda r: (0 if r['prov'] else 1, (0, r['iso']) if r['iso'] else (1, '')))
    # round 10: other provisions of counted rules (tables/local_vouchers_other_provisions.tsv), each shown on its rule's line; every row must be met
    OTHERP, op_met, badge_hits, seps_done = {}, set(), Counter(), set()
    for k_, op_ in enumerate(table_rows('local_vouchers_other_provisions.tsv')):
        t_ = 'local_vouchers.tsv' if op_['row_id'][0] == 'A' else 'local_vouchers_more.tsv'
        if VCLASS.get((t_, int(op_['row_id'][1:])), 'No').startswith('No'): stop(f'other provisions: row {op_["row_id"]} is not a counted rule')
        op_['parts'] = [w_.strip() for w_ in op_['words'].split(' / ') if w_.strip()]; op_['key'] = k_
        if not all(L.has(w_, op_['saved_id']) for w_ in op_['parts']): stop(f'other provisions: words of row {op_["row_id"]} not found in {op_["saved_id"]}')
        OTHERP.setdefault((t_, int(op_['row_id'][1:])), []).append(op_)
    for r in local:
        for q in r['quotes']: lines_q.append((q['sid'], q['words']))
        sid0 = r['quotes'][0]['sid'] if r['quotes'] else (r['sids'][0] if r['sids'] and (L.P / r['sids'][0]).is_dir() else '')
        title = re.sub(r'\s*<br\s*/?>\s*', ' ', B.title_of(sid0)) if sid0 else ''
        d_html = f'<span class="d">{esc(show_date(r["iso"]))}</span>' if r['iso'] else '<span class="d no">no date given</span>'
        x = []
        for j, q in enumerate(r['quotes']):
            cj = has_cjk(q['words'])
            other_ = q['sid'] != r['quotes'][0]['sid']     # round 10: a passage found in another saved copy of the line (a later rule that repeals it, a note, a report) says which
            x.append(f'<div class="q"><p class="w{"" if cj else " en0"}"{" lang=\"zh-Hans\"" if cj else ""}>“{esc(q["words"])}”'
                     + (f' <span class="lab">in the saved copy {esc(q["sid"])}</span>' if other_ else '') + '</p></div>')
        if not r['quotes']:
            x.append('<p class="m"><span class="lab">Passage</span>None shown: the project\'s table gives no words for this row that the checker finds in a saved copy.</p>')
        if r.get('repealed'): x.append(f'<p class="m"><span class="lab">In force?</span><b>{esc(r["repealed"])}</b></p>')
        if not r['prov']: x.append(f'<p class="m"><span class="lab">In the project\'s count?</span>{esc(VCLASS[(r["table"], r["trow"])])}. From the project\'s table of classes, tables/local_vouchers_classes.tsv, by its counting rule (one rule in force for each local government, whose text is saved and states a share of the bill).</p>')
        for op_ in OTHERP.get((r['table'], r['trow']), []):     # round 10: other provisions of a counted rule for home-made computing (tables/local_vouchers_other_provisions.tsv)
            x.append(f'<p class="m"><span class="lab">Another provision for home-made computing</span>{esc(op_["what_it_gives"])} ({esc(op_["article"])}). Its words: '
                     + '; '.join('“' + esc(w_) + '”' for w_ in op_['parts']) + '. From tables/local_vouchers_other_provisions.tsv; the count above looks at the counted payment only.</p>')
            for w_ in op_['parts']: lines_q.append((op_['saved_id'], w_))
            op_met.add(op_['key'])
        if r['reading']: x.append(f'<p class="m"><span class="lab">Our reading, in English</span>{esc(r["reading"])}. This is the project\'s table, not a translation.</p>')
        x.append(f'<p class="m"><span class="lab">The document</span>{esc(r["desc"])}</p>')
        if r['extra']: x.append(f'<p class="m"><span class="lab">The copy held</span>{esc(r["extra"])}</p>')
        addr = B.address(sid0, {'addr': ''}) if sid0 else ''
        if addr: x.append(f'<p class="m"><span class="lab">Address</span><a href="{esc(addr)}" rel="noopener">{esc(addr)}</a></p>')
        x.append(f'<p class="m"><span class="lab">Saved copy</span>{", ".join("<code>" + esc(s_) + "</code>" for s_ in r["sids"])}. Row {r["trow"]} of tables/{esc(r["table"])}.</p>')
        t_html = f'<p class="t"{" lang=\"zh-Hans\"" if has_cjk(title) else ""}>{esc(title)}</p>' if title else '<p class="t no">No title is held for this copy.</p>'
        tag2 = 'Province' if r['prov'] else ('National statement' if r.get('level') == 'national' else ('Local rule, repealed' if r.get('repealed') else 'Local rule'))   # round 5: a national body's words get their own badge
        if not r['prov'] and tag2 == 'Local rule':      # round 9: a row the table of classes calls a draft, an application guide or a notice of a list is not badged a rule
            tag2 = {'No: a draft': 'Local draft', 'No: an application guide, not the rule': 'Application guide',
                    'No: a public notice of a list, not the rule': 'Notice of a list'}.get(VCLASS[(r['table'], r['trow'])], tag2)
        if not r['prov'] and tag2 == 'Local rule':      # round 10 (readers' leads): a payout, a notice of results or an application guide by its own title is not badged a rule
            if r['kind_cell'].startswith('payout'): tag2 = 'Payout notice'
            elif '公示' in r['desc'] and '结果' in r['desc']: tag2 = 'Notice of results'
            elif re.search(r'办事指南|申请指南|申报指南', r['desc']): tag2 = 'Application guide'
            if tag2 != 'Local rule': badge_hits[tag2] += 1
        summ = (f'<summary>{d_html}<div class="who"><p class="b">{esc(r["who"])}</p>{t_html}</div>'
                f'<span class="tags"><span class="tag">{tag2}</span><span class="tag v">From the project\'s tables</span></span></summary>')
        inner = summ + '<div class="x">' + ''.join(x) + '</div>'
        r['search'] = search_norm(' '.join([r['iso'], text_only(inner)]))
        r['kind'] = 'local'
        g_ = 'prov' if r['prov'] else 'vouch'
        if g_ not in seps_done:       # round 10 (look fault 2): a heading where the lines from the tables begin, and where the voucher lines begin
            seps_done.add(g_)
            cards.append(f'<h2 class="sep" data-g="{g_}">' + ("From the project's tables: the 31 provincial-level governments, by the date of the plan read"
                         if g_ == 'prov' else "From the project's tables: local voucher and subsidy rules and documents read about them, by date") + '</h2>')
        cards.append(f'<details class="r" open data-kind="local" data-g="{g_}" data-part="0" data-s="{esc(r["search"])}">{inner}</details>')
    if op_met != set(range(len(table_rows('local_vouchers_other_provisions.tsv')))): stop('other provisions: a row was not shown on its rule\'s line')
    c_res = Counter(r['result'] for r in local if r['prov'])
    # round 9: the care box names Tibet and Xinjiang; the build stops if the table no longer gives them those results
    _p31 = table_rows('provinces_31.tsv')
    if [r['government'] for r in _p31 if r['result'] == 'account_only'] != ['Tibet'] or [r['government'] for r in _p31 if r['result'] == 'not_reached'] != ['Xinjiang']:
        stop('tables/provinces_31.tsv no longer gives Tibet and Xinjiang the results the care box names')
    # core edit 8: the care box names Zhejiang's share with its scope; the words follow the table's row (a share, from the sector plan whose words the row quotes)
    zj = [r for r in table_rows('provinces_31.tsv') if r['government'] == 'Zhejiang']
    if not (len(zj) == 1 and zj[0]['result'] == 'share' and zj[0]['saved_ids'].split()[0] == 'cn-ga31-cndocs-52' and L.has('到2030年，浙江信息通信行业算力规模达150EFLOPS，国产化算力占比超60%', 'cn-ga31-cndocs-52')):
        stop('Zhejiang is not the share the care box describes (tables/provinces_31.tsv)')
    VC = voucher_counts()
    # core edit 8: the sentence on voucher rows left out follows the count (none is left out since the text of the Word and zip copies was put beside them
    # as text.article.txt and Xiamen's official file was filed among the saved sources)
    # round 9: the two rows left out since voucher round 5 are scans without a text layer (their copy cells say so); the sentence names what they are, by the cells
    _left_copy = [table_rows(x.split(' row ')[0])[int(x.split(' row ')[1]) - 1]['copy'] for x in left_out]
    _scan = all('text layer' in c for c in _left_copy)
    left_s = ((f'{len(left_out)} voucher rows are left out because none of their words could be checked by script (' + '; '.join(x.replace('.tsv row', '.tsv, row') for x in left_out) +
               (f'): {"both saved copies are files" if len(left_out) == 2 else "each saved copy is a file"} without a text layer, as the table says.' if _scan else
                '): they are held only as files the checker cannot read (a scan without a text layer, or a Word or zip file), or have no saved copy.'))
              if left_out else 'No voucher row is left out: each has words the checker finds in a saved copy (where the copy is a Word or zip file, in the text taken out of it and kept beside it).')
    n_vouch = sum(1 for r in local if not r['prov'])
    # round 9: how many of the voucher lines shown are counted, and the commonest reasons of those that are not (computed from the table of classes)
    _vs = [VCLASS[(r['table'], r['trow'])] for r in local if not r['prov']]
    v_shown_yes = sum(1 for v in _vs if v.startswith('Yes')); v_shown_no = n_vouch - v_shown_yes
    _whyc = Counter(re.sub(r' \(row \d+ of tables/[a-z_]+\.tsv\)$', '', v[4:]) for v in _vs if v.startswith('No: ')); _why = _whyc.most_common(3)
    v_shown_why = 'by reason, the commonest: ' + '; '.join(f'{k}, {w}' for w, k in _why) + ('; and other reasons' if len(_whyc) > 3 else '')
    if v_shown_yes != VC['n'] and not left_out: stop(f'{v_shown_yes} counted voucher lines shown, but the argument counts {VC["n"]} and no voucher row is left out')
    n_local_q = len(lines_q) - n_note_q
    lines_q += keep
    seen, qlines, qlines_src = set(), [], []
    for j_, (sid, w) in enumerate(lines_q):
        if (sid, w) not in seen:
            seen.add((sid, w)); qlines.append(f'{sid}\t{w}')
            qlines_src.append((sid, w, 'local' if n_note_q <= j_ < n_note_q + n_local_q else 'note'))      # round 10: the footer counts them by source
    for sid, w in seen:
        if '\t' in w or '\n' in w: stop('a tab or line break inside a quotation')
    (HERE / 'quotes.tsv').write_text('# saved id <TAB> exact words from that saved copy. Written by build.py: every passage the page shows, every date word it shows,\n'
                                     '# and every quoted string it keeps in quotation marks in the body and check lines. Checked by scripts/cn_has.py.\n'
                                     + '\n'.join(qlines) + '\n', encoding='utf-8')
    run = subprocess.run([sys.executable, '-I', str(SCRIPTS / 'cn_has.py'), str(HERE / 'quotes.tsv')], capture_output=True, text=True)
    has_line = (run.stdout.strip().splitlines() or ['(no output)'])[-1]
    if run.returncode != 0:
        print(run.stdout + run.stderr); stop('cn_has.py did not pass on quotes.tsv')

    n103 = len(rows)
    n_pass = sum(len(r['quotes']) for r in rows)
    n_local = len(local); n_local_pass = sum(len(r['quotes']) for r in local)
    all_rows = rows + local
    n = len(all_rows)
    n_copies = len({r['read_sid'] for r in rows})
    c_kind = Counter(GROUP[r['kind']] for r in all_rows); c_exact = Counter(r['kind'] for r in rows)
    n_part = sum(1 for r in rows if r['verdict'] == 'CONFIRMED IN PART')
    n_dated = sum(1 for r in rows if r['iso']); n_dfound = sum(1 for r in rows if r['date_words'])
    n_cn = sum(1 for r in rows for q in r['quotes'] if has_cjk(q['words']))
    words = {'carried': ('official text or figure carried by a news outlet', 'official texts or figures carried by news outlets'),
             'roadmap': ("line from an advisory committee's roadmap", "lines from an advisory committee's roadmap"),
             'translation': ("think tank's translation of a government text", "think tanks' translations of government texts")}
    other_bits = '; '.join(f'{c_exact[k]} {words[k][0 if c_exact[k] == 1 else 1]}' for k in words if c_exact[k])

    def expect(qs, kind='all'):
        terms = search_norm(qs).split(' ') if search_norm(qs) else []
        return sum(1 for r in all_rows if (kind == 'all' or GROUP[r['kind']] == kind) and all(t in r['search'] or t in re.sub(r'\s+', '', r['search']) for t in terms))
    expected = {'rows': n, 'kinds': {k: (n if k == 'all' else c_kind[k]) for k in GROUP_LABEL}, 'queries': {q: expect(q) for q in EXPECT},
                'query_with_kind': {'国产|press': expect('国产', 'press')}, 'part': n_part}
    for q in TRY:
        if expected['queries'][q] == 0: stop(f'the example search "{q}" finds nothing')
    (HERE / 'expected.json').write_text(json.dumps(expected, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    short_note = (f'<p>Left out: {len(short)} passage{"s" if len(short) != 1 else ""} of the note under six characters long (line {", ".join(short)} of the list), which the script that checks quotations does not test.</p>' if short else '')
    # round 10: whose wording our English takes on the lines EN_FIX names (the argument's, the official record's, or a few words of ours)
    _ln = lambda src: ', '.join(sorted((k for k in EN_FIX if EN_SRC[k] == src), key=int))
    en_src_words = (f'On {sum(1 for k in EN_FIX if EN_SRC[k] != "page")} lines it is the project\'s corrected wording: the argument\'s (lines {_ln("argument")} of the list) '
                    f'or the official record\'s (lines {_ln("record")}); on {sum(1 for k in EN_FIX if EN_SRC[k] == "page")} lines (lines {_ln("page")}) a few words of ours make a term or a target clear.')
    q_note = len({x for x in qlines_src if x[2] == 'note'}); q_local = len({x for x in qlines_src if x[2] == 'local'})
    if q_note + q_local != len(qlines): stop(f'the quotation counts by source do not add up: {q_note} + {q_local} against {len(qlines)}')
    kind_buttons = ''.join(f'<button type="button" data-kind="{k}" aria-pressed="{"true" if k == "all" else "false"}">{esc(v)}<span class="n">{n if k == "all" else c_kind[k]}</span></button>' for k, v in GROUP_LABEL.items())
    try_buttons = ''.join(f'<button type="button" data-try="{esc(q)}">{esc(q)}</button>' for q in TRY)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Policy Documents, Searchable</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header>
<p class="eyebrow">China chip policy · the policy documents</p>
<h1>The policy documents: {n103} policy lines and {n_local} local rules and provincial plans</h1>
<p class="deck">Most are texts the Chinese state published. No published order against buying Nvidia chips was found among them. The review office's 2023 conclusion on Micron, which says operators of critical information infrastructure should stop buying its products, is in the list. So such a text could have been found.</p>
<p class="note">Draft by Claude, Anthropic's model.</p>
<p class="note">Made from the project's checked note of policy documents (NOTE_policies_checked.md) with its table of quotations, and from the project's tables of provincial plans and local voucher rules (tables/provinces_31.tsv, local_vouchers.tsv, local_vouchers_more.tsv, with local_vouchers_classes.tsv and local_vouchers_other_provisions.tsv). {n103} lines of a list of policy leads; {n_copies} saved pages; {n_pass} passages in the pages' own words, {n_cn} of them Chinese.</p>
</header>
<div class="cols">
<details class="card how" id="how" open><summary><h2>How to read a line</h2></summary><ul>
<li><b>A line</b> of the first {n103} is one entry of a list of policy leads that an earlier search made. The project's checked note then read each lead in the saved copy of its page, and its check note says what it found; where a check note speaks of the list, it means that list of leads.</li>
<li><b>Confirmed</b> means the page carries what the lead said. <b>Confirmed in part</b> ({n_part} lines) means some part is not in the page; the check note says which.</li>
<li><b>Words between quotation marks</b> are the page's own, cut from the saved copy. The <b>English under Chinese is ours</b>, not an official translation. {en_src_words}</li>
<li><b>In a check note</b>, words in italics are the note's own English, the list's own wording, or a reading the script could not check.</li>
<li><b>The date</b> is that of the document or act as the list gives it; where the list gave none, the date the page gives (each such line says so). A script looked for it in the saved copy: it found date words for {n_dfound} of the {n_dated} dated lines, and each line shows them.</li>
</ul></details>
<section class="card"><h2>Read with care</h2><ul>
<li><b>Two sources.</b> {n103} lines come from the checked note of policy leads. {n_local} more come from the project's tables of local rules and provincial plans, marked <i>From the project's tables</i>: all 31 provincial-level governments ({c_res['share']} were found to set a share for home-made computing hardware, one of them, Zhejiang's, for the computing of one sector, its information and communications industry; {c_res['plan_no_share']} have a plan that was read and sets none; {c_res['account_only']}, Tibet, is known only from accounts of it, its issuer's own among them; for {c_res['not_reached']}, Xinjiang, no computing plan was found), and {n_vouch} rows of the project's tables of local voucher and subsidy rules whose words a script finds in a saved copy: {v_shown_yes} of them are in the project's count and {v_shown_no} are not ({esc(v_shown_why)}), and each line says which, as the project's table of classes gives it. {left_s} On the lines from the tables the English is the table's reading of the rule, not a translation. Counting one rule in force for each local government whose text is saved in a form that could be checked by script and which states a share of the bill, the argument finds {VC['n']} among the rules found by searches that went province by province and city by city, saved and read (not a census of every local government): {VC['tiered']} pay more for home-made computing and still pay for other computing ({VC['tiered_names']}), {VC['home']}, those of {VC['home_arg']}, pay for home-made computing only, and {VC['third']} state no higher rate for home-made computing: {VC['one']} pay one rate whatever the chip, and one, {VC['two_name']}'s, pays {VC['two_a']}% or {VC['two_b']}% by a type of computing facility that it does not name. Beijing E-Town's tier was repealed on Nov 26, 2024.</li>
<li><b>Not every line is a government text.</b> Of the {n103} lines of the checked note, {c_kind['official']} are official texts, {c_kind['company']} are company filings or statements, {c_kind['press']} are press reports, and {c_kind['other']} are of other kinds ({esc(other_bits)}). Each line carries its kind.</li>
<li><b>A press report is not published policy.</b> Beijing's instructions to companies are reported by the press from unnamed people; no line here is a published order of that kind.</li>
<li><b>Found means said, not true.</b> A passage that is found shows what the page says.</li>
<li><b>“Not found” is about these {n} lines only.</b> Nothing here shows what was never published, or what was published and not gathered.</li>
</ul></section>
</div>
<div class="tools">
<div class="find"><label for="q">Search</label><input id="q" type="search" autocomplete="off" spellcheck="false" placeholder="Chinese or English words"><span id="count" role="status" aria-live="polite">All {n} lines</span></div>
</div>
<div class="bar">{kind_buttons}<button type="button" id="part" aria-pressed="false">Confirmed in part only<span class="n">{n_part}</span></button><span class="gap"></span><button type="button" id="toggle">Close all</button></div>
<p class="try"><span>Try:</span>{try_buttons}<span>Two words find lines that hold both.</span></p>
<main id="list">
{chr(10).join(cards)}
<p id="none" hidden>No line holds those words. The search reads the date, the issuing body, the title, the passages, our English, the check note, the address and the saved id.</p>
</main>
<footer>
<p>Every quotation on this page was looked for in its saved copy by a script, which found all of them: {esc(has_line)}. Of them, {q_note} are on the {n103} lines of the checked note (their passages, the same strings, row by row, as in the note's own table of quotations, {n_table} strings plus the two of the line read in a second copy; their date words; and the words their check notes quote) and {q_local} on the {n_local} lines from the tables. A passage that is found shows what the page says, not that it is true.</p>
{short_note}
<p>Our English is the checked note's, shown without the quotation marks that note puts round a few terms: only a page's own words stand between quotation marks here. {en_src_words}</p>
<p>The {n_local} lines marked <i>From the project's tables</i> come from tables/provinces_31.tsv, local_vouchers.tsv and local_vouchers_more.tsv: each passage shown was found by the same script in a saved copy the row names; the English beside them is the table's reading, not a translation, here and there in plainer words than the table's; the address is the one held with the saved copy.</p>
<p>The descriptions of the issuing body and the check notes are the checked note's own words, carried over by the script, except in a few places where this page puts them plainly: the note's name for the list of leads (a lane) is given as the list; the note's first person is left out; Li Chao is not called the planner's spokesperson (the commission's page names him and his office only); two issuers are named as the pages and the project's table of names name them; and no line recounts which copy was read first. Page titles are those held with the saved copies. Addresses are those the note gives.</p>
</footer>
</div>
<script>{JS}</script>
</body>
</html>
"""
    OUT.write_text(page, encoding='utf-8')
    print(f'local lines: {n_local} ({n_vouch} voucher rules, 31 provinces: ' + ', '.join(f'{k} {c_res[k]}' for k in RESULT) + f'), {n_local_pass} passages; voucher rows left out (no passage the checker can read): {len(left_out)} ({"; ".join(left_out)})')
    print(f'policy_documents.html: {n} lines, {n_copies} saved pages, {n_pass} passages ({n_cn} Chinese); kinds: ' + ', '.join(f'{k} {c_kind[k]}' for k in ('official', 'company', 'press', 'other')))
    print(f'verdicts (the {n103} note lines): confirmed {n103 - n_part}, confirmed in part {n_part}; dated lines {n_dated}, date words found in the saved copy for {n_dfound}; quoted strings kept in quotation marks in body and check lines: {len(keep)}')
    print(f'cn_has.py: {has_line}')
    print(f'passages of the note left out as too short for the checker: {len(short)} (list line {", ".join(short) or "-"})')
    print('lines whose date was not found written in the saved copy: ' + (', '.join(r['row'] for r in rows if r['iso'] and not r['date_words']) or 'none') +
          '; lines without a date: ' + (', '.join(r['row'] for r in rows if not r['iso']) or 'none'))


if __name__ == '__main__':
    main()
