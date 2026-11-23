# What purchase notices name: Nvidia cards and home-made machines, 2024 to 2026

*It is a sample found by search and proves nothing about proportions. 47 notices from Chinese universities, research institutes and one earthquake agency: 24 name Nvidia hardware, and 14 of those 24 are one university's (Wuhan University); 7 name home-made accelerator hardware; 16 name no accelerator. Later records add China Mobile's purchases, which by the trade press's accounts put the larger part of a 2025 purchase and all of a March 2026 tender on equipment of Huawei's CANN software, and two universities' notices of July 2026 to buy Nvidia's RTX PRO 6000D. A notice to buy is neither a purchase made nor a delivery.*

Draft by Claude, Anthropic's model. Local; not published.

Written Nov 23, 2026 (UTC) for idea 35 of the chip-policy project, and brought into line the same day with the project's fourth edit of its core. Words between straight double quotes are a page's own words and were found in its saved copy by a script. English in round brackets and in the right-hand column is ours, not an official translation. The press pages cited report published tender documents, not unnamed people. Buyers are named as their notices name them: no saved page calls them public or state bodies, and this note does not.

## The question

Idea 35 asked for a census of tenders: how many name Nvidia hardware and how many name home-made chips, from 2024 to 2026. A true census is not possible here. China's purchase notices sit on thousands of sites, many notices never name the chip, and the time was a few hours. What follows is a bounded sample with a stated method, and, apart from it, later records that another agent of the project found.

## What the sample shows

**1.** **Universities' and institutes' own notices named Nvidia hardware in each of the three years.** The 24 notices in table 1 name the A100, A800, H100, H200, L40, L40S, L20, RTX A6000, RTX 4090, RTX 4090 D and RTX 5090. Most are small purchases, from a single card to a few servers. In the sample, the latest dated notice that names a chip of the A or H series is of Jun 30, 2025 (H200 cards, to rent); the three dated after it name the RTX 5090. Outside the sample, Wuhan University filed a purchase of A100 cards in July 2026 (see the later records), and Reuters reports a university's purchase record of October 2026 for two H200 chips (see what the project already held).

**2.** **The largest purchases in the sample are of Huawei machines, and their titles say home-made.** Sun Yat-sen University awarded 23.99 million yuan for one Huawei cluster [1]. Wuhan University of Science and Technology awarded 20.02 million yuan for ten sets and other items, in a project whose name says ultra-long-term special treasury bonds [2]. Both are in table 2.

**3.** **Most award notices do not name the chip.** Of the 14 award or result notices in the sample that come from the central government purchasing site, 12 name no accelerator by maker or model (most give a server brand and model), 2 name a Huawei Atlas machine, and the number that name an Nvidia model is 0. A count of notices by chip therefore misses much of what is bought.

**4.** **The sample leans on one university.** 14 of the 24 notices in table 1 are Wuhan University's, whose purchasing site publishes small purchases with their full specification. That is a fact about one site, not about China.

## What a purchase record can and cannot show

- **Can show.** That a named buyer asked for, or chose, a named product, in a stated number, at a stated budget or price, on a stated date and under stated conditions, in its own words. A tender, purchase notice or purchase filing shows what was asked for. A result or award notice, or a list of bid candidates, shows a contract decision.
- **Cannot show.** That the goods were delivered, paid for or put to use. How imported chips reached China, or whether a sale met United States export rules: no notice says. What share of all purchases went to Nvidia or to home-made hardware: many notices name no chip, and the notices here were found by search. Whose chips are in machines that a tender describes only by a software ecosystem (CUDA-like, CANN), unless the page says. And a trade site's account of a tender is not the tender itself.

## Method

- **Start.** The project held five Reuters reports that rest on tender documents and purchase records, and one university's own notice. They are set out in the section on what the project already held.
- **Searches.** 22 web searches on Nov 23, 2026, listed word for word in search_log.txt. Most were limited to the central government purchasing site (ccgp.gov.cn) or to universities' own sites (edu.cn). They asked for award notices (中标公告), result notices (成交公告) and purchase notices (采购公告) with Nvidia model names (H100, H200, H20, A100, A800, L40S, RTX 4090, RTX 5090) or with home-made names (昇腾 Ascend, Atlas, 寒武纪 Cambricon, 海光 Hygon, 昆仑芯 Kunlun, 鲲鹏 Kunpeng).
- **Saving.** Results that looked like a purchase of GPU or AI hardware were saved with the project's fetcher: 69 addresses tried, 64 saved, 5 not saved (4 answered not found, 1 could not be reached). Not every result was opened: the choice was made from titles and summaries. No search form on any purchasing site was used.
- **Sorting.** A notice goes in table 1 if it names Nvidia or an Nvidia model. It goes in table 2 if it names a home-made accelerator or a Huawei Atlas machine, or asks for AI hardware under the word 国产 (home-made). It goes in table 3 if the notice itself says GPU, AI, training or accelerated computing and names no accelerator by maker or model; most of these give a server brand and model. 17 saved pages are in no table: 6 whose notice does not itself say GPU, AI, training or accelerated computing, 3 dated before 2024, 3 that buy no accelerator, 3 that hold no usable content, and 2 that are not notices and are used further down. They are listed with reasons in left_out.txt.
- **Counting.** The counts come from a script (build.py) over the table file (notices.txt). The year is the year of the date on the page. The later records are not added to the counts: they were found another way.
- **Buyers.** Each buyer is described only by what its name says (a university, a vocational college, a research institute, an agency). No saved page says whether a buyer is a public or state body, so the note does not say it.
- **From my general knowledge, not from the notices.** Where a notice writes a model without its maker (L40, A6000, RTX 4090, RTX 5090, H100), that these are Nvidia models is my knowledge; each such row says the maker is not written. That Huawei's Atlas machines run on Huawei's Ascend chips is also my knowledge; one notice writes the two names together [3].

## What the project already held

- Reuters, Jan 14, 2024, on its own review of tender documents: "The review includes more than 100 tenders where state entities have procured A100 chips"; "Tsinghua University procured two H100 chips"; and "Buying or selling high-end U.S. chips is not illegal in China" [4]. The words "state entities" are Reuters's.
- Reuters, dated Apr 22, 2024 on the page: "10 Chinese entities acquired advanced Nvidia chips embedded in server products" [5].
- Reuters, Mar 27, 2026: Beihang University "said in a March 16 notice this year it had procured a machine-learning workstation built on a Super Micro system, configured with four Nvidia A100 chips" [6].
- Reuters, Nov 11, 2026: a defence-linked university "bought two H200 chips last month for 874,700 yuan", "according to an October 21 procurement record on its website" [7]. The project's record says that page answered not found when it was fetched on Nov 20, 2026.
- Reuters, Nov 13, 2026, a list of computing-centre projects, among them one in Jilin: "an April government prospectus describes another 2.26 billion yuan" project "combining Nvidia H100 processors with Chinese-developed chips" [8].
- A university's own notice, Nov 20, 2026. Beijing Institute of Technology's computing centre is fitted with "配置H100、H20、L40S、RTX 4090显卡及国产DCU加速卡" (H100, H20, L40S and RTX 4090 cards and home-made DCU accelerator cards) [9]. It is the only saved page cited in this note that names the H20: a script looked for the name in all 64 pages saved for the sample and found it in none, and found it in this one.

## Table 1. Notices that name Nvidia hardware (24)

| Date on the page; buyer; kind of notice | Hardware, in the notice's own words | What it is; amount; source |
|---|---|---|
| Mar 5, 2024. Wuhan University (university). Result notice | "NVidia RTX 4090 涡轮计算卡24G显存"; "提供GPU卡片≥8片" | A server with at least 8 RTX 4090 cards. 232,000 yuan. [10] |
| Mar 7, 2024. Wuhan University (university). Result notice | "尽管L40显卡的报价高于竞争对手A6000显卡，我们最终决定选择L40显卡" | The buyer chose L40 cards over A6000 cards though they cost more; the maker is not written. 146,900 yuan. [11] |
| Mar 15, 2024. Wuhan University (university). Result notice | "之前已经安装的显卡型号是Nvidia A100"; "A100显卡比A800显卡性能更强大" | One A100 card, chosen over an A800 offered at about the same price. 141,000 yuan. [12] |
| Mar 18, 2024. Nantong University (university). Result notice | "微星魔龙RTX 4090 D 24G GAMING X XSLIM" | One RTX 4090 D card (the notice also lists an RTX 4080 card). 22,250 yuan for the two cards. [13] |
| May 6, 2024. Shandong University, a school's own purchase (university). Result notice | "GPU卡：8*NVIDIA RTX 4090 涡轮版" | A server with 8 RTX 4090 cards. 185,500 yuan. [14] |
| May 20, 2024. Wuhan University (university). Result notice | "本次配置8块RTX 4090 24GB涡轮版" | A server with 8 RTX 4090 cards, bought with a secure terminal; the maker is not written. 249,800 yuan. [15] |
| Jun 22, 2024. Wuhan University (university). Result notice | "A100四卡服务器平台" | A server platform with four A100 cards. 395,000 yuan. First of two notices for the same item. [16] |
| Jul 5, 2024. Wuhan University (university). Result notice | "A100四卡服务器平台" | The same item, supplier and price as the row above, under a new project number: it looks like one purchase run twice. 395,000 yuan. Second of two notices for the same item. [17] |
| Aug 12, 2024. Wuhan University (university). Result notice | "NVidia 具有563亿个晶体管、14592 个CUDA核心和80GB DDR6 HBM3e显存" | A server with at least one Nvidia card described by its figures; the model is not written. 358,190 yuan. [18] |
| Sept 27, 2024. University of Chinese Academy of Sciences (university of the Academy of Sciences). Purchase notice, to rent servers | "单台服务器搭载8张Nvidia A800 /A100 80GB GPU"; "本项目不接受进口" | Three servers to rent for 8 months, each with 8 A800 or A100 cards; the same notice says imported products and services are not accepted. Budget 960,000 yuan for the three. [19] |
| Nov 6, 2024. Wuhan University (university). Result notice | "配置≥6块NVDIA RTX A6000 48GB"; "品牌要求：国产服务器品牌" | A server of a home-made brand fitted with at least 6 RTX A6000 cards (NVDIA is the notice's spelling). 341,500 yuan. [20] |
| Nov 18, 2024. Wuhan University (university). Result notice | "显卡 NVIDIA Tesla L20 48G 2" | A server with two L20 cards. 85,500 yuan. [21] |
| Nov 30, 2024. Wuhan University (university). Result notice | "NVidia 具有 763亿个晶体管、10240 个 CUDA 核心和 48GB HBM3e 显存" | A server with at least two Nvidia cards described by their figures; the model is not written. 85,500 yuan. [22] |
| Jan 6, 2025. Wuhan University (university). Result notice | "NVidia 具有563亿个晶体管、18176 个CUDA核心和48GB DDR6 HBM3e显存" | A server with at least two Nvidia cards described by their figures; the model is not written. 147,800 yuan. [23] |
| Mar 3, 2025. Wuhan University (university). Result notice | "NVIDIA L40S显卡" | One L40S card. 57,000 yuan. [24] |
| Mar 18, 2025. Beijing University of Posts and Telecommunications, School of Computer Science (university). Result notice | "英伟达/H100 80G PCIE 1张" | One H100 card. 203,000 yuan. [25] |
| Mar 31, 2025. Shenzhen University, College of Computer Science and Software Engineering (university). Result notice (a unit's own purchase) | "设备名称：Nvidia 4090"; "2.数量：6" | Six 4090 cards. 165,000 yuan (the proposed price). [26] |
| Apr 1, 2025. Wuhan University (university). Purchase notice | "H100GPU 1 件 235000" | One H100 card; the maker is not written. Budget 235,000 yuan. [27] |
| Jun 12, 2025. Wuhan University (university). Purchase notice | "NVidia 具有763亿个晶体管、6912 个CUDA核心和80GB HBM2e显存" | A server with at least one Nvidia card described by its figures; the model is not written. Budget 310,000 yuan. [28] |
| Jun 30, 2025. Institute of Artificial Intelligence, Hefei Comprehensive National Science Center (research institute). Purchase notice (a call for price offers), to rent a server | "1台 8 卡 Nvidia H200 GPU 的服务器（裸金属服务），租用期 6 个月" | One server with 8 H200 cards, to rent for 6 months. Budget 450,000 yuan. [29] |
| No date on the page; the project number is of 2025. Southern University of Science and Technology (university). Result notice | "显卡：8 块 VID Nvidia L40 2SLOT 48GB 显存"; "是否接受进口 拒绝进口" | A server with 8 L40 cards; the same notice says imports are refused. 469,000 yuan. [30] |
| Nov 26, 2025. Huazhong Agricultural University, College of Informatics (university). Result notice (a unit's own purchase) | "GPU卡：RTX 5090 1台" | One RTX 5090 card; the maker is not written. 29,900 yuan. [31] |
| Dec 9, 2025. East China University of Science and Technology, a research team (university). Result notice | "Nvidia RTX 5090 32G 显存" | Two servers, each described with an RTX 5090 card. 160,000 yuan for the two. [32] |
| May 6, 2026. Fudan University (university). Result notice | "5090显卡 (张) 15"; "英伟达/RTX32G" | Fifteen 5090 cards. 447,000 yuan. [33] |

## Table 2. Notices that name home-made accelerator hardware (7)

| Date on the page; buyer; kind of notice | Hardware, in the notice's own words | What it is; amount; source |
|---|---|---|
| Jan 17, 2024. Beihang University, Institute of Artificial Intelligence (university). Result notice | "国产AI加速卡 Atlas 300V Pro 昇腾/Atlas 300V Pro 2台" | Two Atlas 300V Pro cards, which the notice calls a home-made AI accelerator card and marks Ascend. 38,900 yuan. [3] |
| Undated in the saved copy; it gives Sept 3, 2024 as the date of the purchase notice. Tsinghua University (university). Award notice | "清华大学国产高性能 AI 服务器购置项目"; "华为 型号：Atlas 800T A2" | One Huawei Atlas server; the project is named for a home-made high-performance AI server. 2.19 million yuan. [34] |
| Dec 3, 2024. Wuhan University of Science and Technology (university). Award notice | "武汉科技大学2024年超长期特别国债-国产算力平台采购项目"; "品牌：华为（核心产品）等 规格型号：Atlas 800T A2（核心产品）等 数量：10套" | Ten sets, the core product a Huawei Atlas server; the project name says special treasury bonds and a home-made computing platform. 20.02 million yuan. [2] |
| Dec 27, 2024. Sun Yat-sen University (university). Award notice | "中山大学国产智能计算系统采购项目"; "高性能智能计算集群 华为 Atlas 900 A3 SuperPoD 1套 23,989,000.00" | One Huawei Atlas 900 cluster; the project is named for a home-made intelligent computing system. 35.01 million yuan in all, of which 23.99 million for the cluster. [1] |
| Nov 10, 2025. University of Science and Technology Liaoning (university). Tender notice | "平台支持对不同架构的国际AI算力芯片与国内AI算力芯片（包括但不限于华为昇腾、寒武纪、海光、天数智芯和燧原等）"; "配置不少于8颗GPU/NPU"; "需通过中国信息安全测评中心安全可靠测评" | Two inference servers with at least 8 accelerators each, maker not written; the management platform must handle foreign AI chips (none named) and home-made ones (five makers named); the processors must have passed the security-and-reliability evaluation of China's information-security evaluation centre. Budget 3.07 million yuan. [35] |
| Nov 26, 2025. Fujian Polytechnic of Information Technology (vocational college). Result notice | "算力服务器 华为 Atlas 800I A2 1 台 917,765.0000" | One Huawei Atlas server among Huawei servers, storage and switches. 3.67 million yuan in all, of which 917,765 for the Atlas server. [36] |
| Jul 8, 2026. Institute of Automation, Chinese Academy of Sciences (research institute). Tender notice, to rent cloud computing | "国产AI云服务器1"; "配置≥8 张 AI算力卡" | Three kinds of server labelled home-made AI cloud server and four kinds of AI cloud server without that word, each with at least 8 cards; no maker is written. Budget 9.5 million yuan. [37] |

## Table 3. Notices for GPU or AI purchases that name no accelerator (16)

| Date on the page; buyer; kind of notice | Hardware, in the notice's own words | What it is; amount; source |
|---|---|---|
| Jan 12, 2024. Nanjing University of Science and Technology (university). Award notice | "GPU计算服务器（含集群管理软件）"; "超益集伦 ServMAX® G448-X4" | GPU servers named by server model. [38] |
| Jan 25, 2024. Tsinghua University (university). Award notice | "GPU服务器集群—GPU算力服务器（8U）"; "景宏安信； H3C； Mellanox JHAX-821GE； R5500G5； MQM8700-HS2F" | A GPU server cluster named by server and switch models. 8.42 million yuan. [39] |
| Aug 3, 2024. ShanghaiTech University (university). Result notice | "GPU计算服务器"; "浪潮NF5468M6等" | A GPU server named by server model. [40] |
| Nov 27, 2024. Qinghai Earthquake Agency (agency). Award notice | "AI服务器Ⅰ型 中科可控 Suma X7340 H0"; "实配2块GPU卡" | AI servers of two Chinese brands, each with 2 cards whose maker is not written; home-made processor lines are named only in the software requirements. 9.58 million yuan for the whole purchase. [41] |
| Dec 9, 2024. Southwest University of Science and Technology (university). Result notice | "人工智能计算集群采购项目"; "异构计算节点2 联泰集群 G422X-TNRG2" | Computing nodes named by server model. [42] |
| Dec 11, 2024. Central China Normal University (university). Tender notice | "华中师范大学人工智能算力平台设备采购项目"; "服务器NPU卡 16 块" | 16 cards the notice calls NPU cards for servers; no maker is written. Budget 12.1 million yuan. [43] |
| Mar 6, 2025. China University of Mining and Technology (university). Purchase notice (a call for price offers) | "GPU 加速卡 单卡显存≥48GB，支持CUDA核心数≥10000" | Two cards described by their figures, among them a count of CUDA cores; no maker or model is written. [44] |
| May 9, 2025. Guangzhou Medical University (university). Result notice | "AI节点 华鲲振宇 HuaKun AT3500 G3" | AI nodes named by a Chinese server brand and model. [45] |
| May 12, 2025. Northwestern Polytechnical University (university). Award notice | "异构加速计算节点服务器" | An accelerated-computing node listed among Lenovo servers. [46] |
| Jul 7, 2025. Shanghai Jiao Tong University (university). Award notice | "人工智能模型训练和推理的硬件平台 中科可控 X7850H0 4台" | An AI training and inference platform named by server model. [47] |
| Jul 31, 2025. Xinjiang Institute of Ecology and Geography, Chinese Academy of Sciences (research institute). Award notice | "GPU深度学习人工智能服务器 思腾合力(天津)科技有限公司 IW4235-8GR" | A GPU server named by server model. [48] |
| Sept 12, 2025. Xi'an Jiaotong University (university). Award notice | "GPU服务器/智算融合平台 AMAX GMAX-H200/AMAXPlatforMax" | A server model whose name holds H200; the notice does not say which chip is inside. 2.639 million yuan. [49] |
| No date in the saved copy; the project number is of 2025. Beijing Institute of Technology, Zhuhai campus (university). Result notice | "社科学域服务器及 AIGC 团队设备"; "服务器 AMAX GMAX H200 1台 2450000" | A server model whose name holds H200; the notice does not say which chip is inside. 2.55 million yuan in all, of which 2.45 million for the server. [50] |
| Jan 5, 2026. University of Chinese Academy of Sciences (university of the Academy of Sciences). Award notice | "GPU服务器 浪潮 NF5688-M7-A0-R0-00 2 1475000" | Two GPU servers named by server model. [51] |
| Aug 19, 2026. China National Institute of Standardization (research institute). Award notice | "训练型服务器 华鲲振宇 HuaKun AT800 (Model 9000) A2 2 1378500" | Two training servers named by a Chinese server brand and model. [52] |
| Oct 19, 2026. Tianjin University (university). Result notice, rented computing | "合计提供16张GPU计算加速卡" | Two rented cloud servers with 16 cards in all; no maker is written. [53] |

## The count

| Year | Names Nvidia hardware | Names home-made accelerator hardware | Names no accelerator | All |
|---|---|---|---|---|
| 2024 | Nvidia: 13 | Home-made: 4 | No accelerator: 6 | All: 23 |
| 2025 | Nvidia: 10 | Home-made: 2 | No accelerator: 7 | All: 19 |
| 2026 | Nvidia: 1 | Home-made: 1 | No accelerator: 3 | All: 5 |
| All three years | Nvidia: 24 | Home-made: 7 | No accelerator: 16 | All: 47 |

This is a sample found by search. It proves nothing about proportions. The searches were not a random draw (9 of the 22 asked for Nvidia names and 13 for home-made names), one university supplies 14 of the 24 rows in the first column, and a notice that names no chip cannot be found by a chip's name at all. Of the 47 notices, 39 are award or result notices and 8 are tender or purchase notices, which show what a buyer asked for, not what it got. By buyer: 42 notices are from universities or colleges, 4 from research institutes and 1 from an agency (Qinghai's earthquake agency).

## Later records, found by another agent of the project

These are not in the sample or its count. The first was found by this note in its first round; the others were found and saved by a later agent of the project (its table is the core's tables/procurement_records.tsv). Each is quoted here from the saved page.

- **China Mobile, 2025: an inference purchase in six lots.** C114, a telecoms trade site, reported on Aug 19, 2025 that China Mobile's tender for AI inference servers had six lots: "标包1、标包2、标包3和标包4均为类CUDA生态设备，总含税价超17亿元；标包5和标包6为CANN生态设备，总含税价约34亿元" (lots 1 to 4 are equipment of the CUDA-like kind, over 1.7 billion yuan with tax; lots 5 and 6 are equipment of the CANN kind, about 3.4 billion yuan) [54]. The page does not say whose chips the CUDA-like lots hold. China Mobile's own notice is not held.
- **China Mobile, March 2026: a tender for CANN equipment only.** C114, Mar 17, 2026: "采购产品为人工智能超节点设备（CANN生态），采购规模约为6208卡（776套计算节点）。" (the product bought is AI supernode equipment, of the CANN ecosystem, about 6,208 cards in 776 computing nodes) [55]. On Apr 10, 2026 the same site reported five winning firms, with bids from 2.059 to 2.07 billion yuan, and wrote that the purchase was explicitly tied to Huawei's CANN, "并明确锁定华为CANN" [56].
- **A later carrier tender that names no chip.** C114, Nov 21, 2026: "中国移动此次采购人工智能超节点合计52160卡，计划选取6-7家中标人。" (China Mobile is buying 52,160 cards of AI supernode equipment in all and plans to choose six or seven winners) [57]. The core's table of procurement records gives the chip of this tender as not stated.
- **Two universities' notices for the RTX PRO 6000D, July 2026.** Beihang University's School of Computer Science posted a purchase notice (采购公告) on Jul 11, 2026 for four cards, "品牌 NVIDIA 规格型号 RTX PRO 6000D" (brand Nvidia, model RTX PRO 6000D), with a budget of 226,000 yuan, and asks that suppliers meet "符合《政府采购法》第二十二条规定的供应商基本条件" (the basic conditions for suppliers in Article 22 of the Government Procurement Law) [58]. Wuhan University filed on Jul 7, 2026 a decentralised purchase by competitive bidding (竞价), with a budget of 110,000 yuan, for the "国行合规RTX PRO 6000D型号，非消费级游戏卡、非改装卡、非海外版受限型号" (the compliant China-market RTX PRO 6000D model; not a gaming card, not a modified card, not a restricted overseas model), and holds suppliers to "参照《中华人民共和国政府采购法》第二十二条规定的资格条件" (the qualifications in Article 22 of the Government Procurement Law) [59]. A notice to buy is neither a purchase made nor a delivery. The project's argument cites both notices in its point 19.
- **Wuhan University: other Nvidia records of 2026.** A filing of Jul 6, 2026 for "6张合规拆机A100 40GB PCIe加速卡" (six compliant A100 40GB PCIe cards taken out of machines), with a budget of 150,000 yuan [60]. A result notice of Aug 13, 2026 for one "Nvidia 6000D 84GB显存" card, at 54,000 yuan [61]. A result notice records a contract decision, not a delivery.
- **A count from Wuhan University's own lists.** The same agent saved and read 72 result notices of Wuhan University dated Sept 1, 2025 to Nov 23, 2026, chosen from the university's own lists of result notices. 23 of them name Nvidia somewhere in the notice. build.py recounts both numbers from that agent's tables and checks that each of the 23 saved pages holds the name. They are the notices that agent chose to read, not a census of the university's purchases.

## Three details in the notices

- **Nvidia cards under a no-imports line.** Two notices that name Nvidia cards also refuse imports. The University of Chinese Academy of Sciences asked for servers with "8张Nvidia A800 /A100 80GB GPU" and wrote "本项目不接受进口" (this project does not accept imports) [19]. Southern University of Science and Technology bought a server with "8 块 VID Nvidia L40" under the line "是否接受进口 拒绝进口" (imports accepted or not: refused) [30]. A third asks for a "国产服务器品牌" (home-made server brand) fitted with "NVDIA RTX A6000" cards [20]. The notices do not say how the two fit together.
- **An evaluated processor, an open accelerator.** A Liaoning university's tender requires processors that passed the security-and-reliability evaluation of China's information-security evaluation centre, "需通过中国信息安全测评中心安全可靠测评", and leaves the maker of the accelerators open: "配置不少于8颗GPU/NPU" (fit no fewer than 8 GPU or NPU chips) [35]. The 2023 purchase rule for servers names the same two things and no accelerator: "应当将CPU、操作系统符合安全可靠测评要求纳入采购需求" (the purchase requirement shall include that the CPU and the operating system meet the security-and-reliability evaluation) [62].
- **A buyer's reasons, in its own words.** Wuhan University chose an A100 card over an A800 offered at nearly the same price because "A100显卡比A800显卡性能更强大" (the A100 card performs better than the A800) [12].

## One thing seen outside the sample

- **The Jilin project in Reuters's list has a primary page.** A project sheet on the Jilin provincial government's investment pages, dated Apr 27, 2026, describes a computing centre in Songyuan: "含 3600P 英伟达 H100 稀疏算力与 2400P 国产算力" (it includes 3,600P of Nvidia H100 computing and 2,400P of home-made computing). It calls the home-made part the backstop, "国产算力兜底", and gives "项目总投资 225893.09 万元" (a total investment of 2,258.93 million yuan) [63]. It also says "申请银行贷款，占总投资比重约 80%" (bank loans applied for, about 80% of the total investment); Reuters's list says the developer "expects bank loans to finance about 80% of the investment" [8]. Month, amount, hardware and the loan share match Reuters's lines. Reuters does not name the project, so the match is ours. It is a plan put to investors, not a purchase.
- A Shanghai government body, in a reply dated Apr 30, 2025 (published Nov 10, 2025), wrote that the three big telecom operators mainly buy home-made computing clusters: "三大运营商主要购置华为等国产化智算集群" [64]. China Mobile's records above are the trade press's accounts of one operator's notices.

## What was not found

- **No purchase notice that names the H20.** Four searches had the name among their words (7, 9, 13, 19); search 13 asked for it alone, on both groups of sites. It returned the Hefei notice for H200 cards in table 1, so it could see a notice that names a chip.
- **No notice in which a Cambricon, Hygon or Kunlun accelerator is the thing bought.** Four searches asked (6, 8, 14, 15). Searches of the same kind found the Huawei notices in table 2.
- **No notice from a police body, a court, a procuratorate, a hospital or a weather bureau that names an accelerator.** Searches 16 and 20 asked by those words.
- **No carrier's own notice.** China Mobile's purchasing site came up in one search and was not opened; a page saved from the national trading platform holds only titles. The China Mobile records in this note are a trade site's accounts.
- **In the sample, no notice of 2026 that names an Nvidia chip of the A or H series.** Three searches asked for 2026 notices (17, 19, 22). Between them they returned the 2025 notices for the H100 and the H200, so they could see a hit. The later records hold one: Wuhan University's filing of July 2026 for A100 cards [60].
- **Three notices seen in search summaries were gone.** Two pages at Beihang University and one at Northwestern Polytechnical University answered not found on Nov 23, 2026. By the search summaries, read and not saved, they concerned A100, A800 and RTX 5090 cards. Why the pages are gone is not known.

## What a reader may and may not conclude

- **May.** That Chinese universities and research institutes published notices naming Nvidia hardware in 2024, 2025 and 2026, and that two universities posted notices in July 2026 to buy the RTX PRO 6000D: these are their own documents. That some of the largest purchases of AI hardware in the sample were made under project names that say home-made. That many award notices name no chip. That, by a trade site's accounts of its notices, China Mobile put about 3.4 of over 5 billion yuan of a 2025 purchase, and all of a March 2026 tender, on CANN-ecosystem equipment.
- **May not.** Any share, ratio or trend between Nvidia and home-made hardware: this is a sample found by search. That a notice to buy was a purchase made, or that a card named in a notice was delivered. How the cards reached China, or whether any sale met United States export rules: no notice says. Whose chips are in China Mobile's CUDA-like lots. Anything about China's AI companies: none of their purchases is in the sample. Anything about bodies whose purchases are not published.

## The files

- notices.txt: the table as typed, one line per notice. notices.tsv: the same with the address and the saved id of every notice. counts.tsv: the count. quotes.tsv: every string taken from a page. left_out.txt: saved pages not used, with reasons. search_log.txt: the searches. refs_manual.tsv: references that are not sample notices. build.py rebuilds all of it and stops if a string is not found in its saved copy. Its check line on this build: 150 quotations checked, 150 found, 0 not found; controls behave.

## References

Each entry: its kind; what it is; the saved page's own title where the record holds one; the address; the saved copy (research/primary/<id>).

[1] An institution's own published notice. Sun Yat-sen University: award notice, Dec 27, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 中山大学国产智能计算系统采购项目（项目编号：中大招（货）[2024]428号、代理机构编号：0835-240Z13808421）中标结果公告. https://www.ccgp.gov.cn/cggg/zygg/zbgg/202412/t20241227_23978936.htm Saved copy: cn-o35-ccgp-sysu-202412

[2] An institution's own published notice. Wuhan University of Science and Technology: award notice, Dec 3, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 武汉科技大学2024年超长期特别国债-国产算力平台采购项目中标公告-信息公开网. https://xxgk.wust.edu.cn/info/2101/64762.htm Saved copy: cn-o35-wust-64762

[3] An institution's own published notice. Beihang University, Institute of Artificial Intelligence: result notice, Jan 17, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 人工智能研究院国产AI加速卡比价结果公示-北京航空航天大学招标采购中心. https://zbcg.buaa.edu.cn/info/1048/50096.htm Saved copy: cn-o35-buaa-50096

[4] Press report of words spoken on the record. A press report of published documents, not of spoken words: Reuters, Jan 14, 2024, as carried by Investing.com, on its own review of tender documents. Internet Archive capture of Jan 16, 2024. The tender documents themselves are not held. https://web.archive.org/web/20240116061406/https://www.investing.com/news/stock-market-news/exclusivechinas-military-and-government-acquire-nvidia-chips-despite-us-ban-3274170 Saved copy: cn-labs-state-tenders-2024-wayback

[5] Press report of words spoken on the record. A press report of published documents, not of spoken words: Reuters, dated Apr 22, 2024 on the page, as carried by MarketScreener, on its own review of tender documents. Internet Archive capture of Apr 23, 2024. https://web.archive.org/web/20240423040744/https://www.marketscreener.com/quote/stock/NVIDIA-CORPORATION-57355629/news/China-acquired-recently-banned-Nvidia-chips-in-Super-Micro-Dell-servers-tenders-show-46496801/ Saved copy: cn-counter-b8-2-wayback

[6] Press report of words spoken on the record. A press report of published documents, not of spoken words: Reuters, Mar 27, 2026, as carried by Investing.com, on universities' purchase notices. Internet Archive capture of the same day. https://web.archive.org/web/20260327084303/https://www.investing.com/news/stock-market-news/chinese-universities-with-military-links-bought-super-micro-servers-with-restricted-ai-chips-4584104 Saved copy: cn-counter-b8-3-wayback

[7] Press report of words spoken on the record. A press report of a published document, not of spoken words: Reuters, Nov 11, 2026, as carried by PiQ Markets, on a university's own purchase record. Page title: Exclusive-PLA-linked Chinese university bought Nvidia H200 chips despite US blacklist, records show. https://piqmarkets.com/reuters/exclusive-pla-linked-chinese-university-bought-nvidia-h200-chips-despite-us-blacklist-records-show-2026-11-11-05-13-08 Saved copy: cn-counter-b8-5

[8] Press report of words spoken on the record. A press report of published documents and company statements, not of spoken words: Reuters factbox, Nov 13, 2026, as carried by the radio station WSAU, listing computing-centre projects. Page title: Factbox-China’s $3 billion-plus pipeline of Nvidia-powered AI data centres. https://wsau.com/2026/11/13/chinas-3-billion-plus-pipeline-of-nvidia-powered-ai-data-centres/ Saved copy: cn-tolerate-projects-relay1

[9] Chinese state document. Beijing Institute of Technology, Analysis and Testing Center: notice that its computing centre has gone into formal operation, Nov 20, 2026. https://atc.bit.edu.cn/tzgg/77484ddab1ce4fbdbd6c14d5147a09dc.htm Saved copy: cn-tolerate-bit

[10] An institution's own published notice. Wuhan University: result notice, Mar 5, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 高性能GPU服务器成交结果公告-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1041/6798.htm Saved copy: cn-o35-whu-6798

[11] An institution's own published notice. Wuhan University: result notice, Mar 7, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 高性能GPU服务器成交结果公告-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1041/6809.htm Saved copy: cn-o35-whu-6809

[12] An institution's own published notice. Wuhan University: result notice, Mar 15, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 高性能服务器显卡采购成交结果公告-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1041/6885.htm Saved copy: cn-o35-whu-6885

[13] An institution's own published notice. Nantong University: result notice, Mar 18, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 南通大学招投标办公室-竞价结果. https://ztb.ntu.edu.cn/jjjg/6472.chtml Saved copy: cn-o35-ntu-6472

[14] An institution's own published notice. Shandong University, a school's own purchase: result notice, May 6, 2024. A purchase notice on the buyer's own site or on a government purchasing site. https://zcgl.sdu.edu.cn/sfw_cms/e?id=9fe2fade698ec68fc5762b8795750179&page=cms.psms.scatter.print Saved copy: cn-o35-sdu-compare

[15] An institution's own published notice. Wuhan University: result notice, May 20, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: GPU服务器(二次)成交结果公告-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1041/7375.htm Saved copy: cn-o35-whu-7375

[16] An institution's own published notice. Wuhan University: result notice, Jun 22, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: A100四卡服务器平台成交结果公告-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1041/7827.htm Saved copy: cn-o35-whu-7827

[17] An institution's own published notice. Wuhan University: result notice, Jul 5, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: A100四卡服务器平台成交结果公告-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1041/7986.htm Saved copy: cn-o35-whu-7986

[18] An institution's own published notice. Wuhan University: result notice, Aug 12, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: GPU计算服务器成交结果公告-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1041/8404.htm Saved copy: cn-o35-whu-8404

[19] An institution's own published notice. University of Chinese Academy of Sciences: purchase notice, to rent servers, Sept 27, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 中国科学院大学-电子电气与通信工程学院-A100*8 NvlinkGPU 服务器租赁项目竞争性磋商. https://www.ccgp.gov.cn/cggg/zygg/jzxcs/202409/t20240927_23265979.htm Saved copy: cn-o35-ccgp-ucas-a100-202409

[20] An institution's own published notice. Wuhan University: result notice, Nov 6, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 服务器成交结果公告-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1041/75481.htm Saved copy: cn-o35-whu-75481

[21] An institution's own published notice. Wuhan University: result notice, Nov 18, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: GPU服务器成交结果公告-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1041/77141.htm Saved copy: cn-o35-whu-77141

[22] An institution's own published notice. Wuhan University: result notice, Nov 30, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 高性能GPU服务器成交结果公告-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1041/79641.htm Saved copy: cn-o35-whu-79641

[23] An institution's own published notice. Wuhan University: result notice, Jan 6, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: GPU计算服务器成交结果公告-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1041/84341.htm Saved copy: cn-o35-whu-84341

[24] An institution's own published notice. Wuhan University: result notice, Mar 3, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: NVIDIA L40S显卡成交结果公告-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1041/86451.htm Saved copy: cn-o35-whu-86451

[25] An institution's own published notice. Beijing University of Posts and Telecommunications, School of Computer Science: result notice, Mar 18, 2025. A purchase notice on the buyer's own site or on a government purchasing site. https://cg.bupt.edu.cn/sfw/e?page=cms.psms.scatter.print&id=3f96ebdbeb05290cf73818714897e777 Saved copy: cn-o35-bupt-h100

[26] An institution's own published notice. Shenzhen University, College of Computer Science and Software Engineering: result notice (a unit's own purchase), Mar 31, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: GPU显卡项目采购信息公开（科研仪器设备类）-深圳大学招投标管理中心. https://bidding.szu.edu.cn/info/1023/37060.htm Saved copy: cn-o35-szu-37060

[27] An institution's own published notice. Wuhan University: purchase notice, Apr 1, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 【分散采购备案单】GPU高性能显卡-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1027/88171.htm Saved copy: cn-o35-whu-88171

[28] An institution's own published notice. Wuhan University: purchase notice, Jun 12, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 【分散采购备案单】GPU服务器-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1027/95711.htm Saved copy: cn-o35-whu-95711

[29] An institution's own published notice. Institute of Artificial Intelligence, Hefei Comprehensive National Science Center: purchase notice (a call for price offers), to rent a server, Jun 30, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 人工智能研究院量子大模型项目云服务器采购公告. https://iai.ustc.edu.cn/iaiWap/r233/20250630/7521.html Saved copy: cn-o35-ustc-iai-h200-7521

[30] An institution's own published notice. Southern University of Science and Technology: result notice, no date on the page; the project number is of 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 信息公告查询-南方科技大学竞采系统. https://jc.biddingoffice.sustech.edu.cn/3gobidding/bulletinsShow/show?id=928EB1976913431A809FF72C2E916083 Saved copy: cn-o35-sustech-00064

[31] An institution's own published notice. Huazhong Agricultural University, College of Informatics: result notice (a unit's own purchase), Nov 26, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: GPU卡设备采购结果公告-华中农业大学采购与招标中心. https://ztb.hzau.edu.cn/info/1312/38997.htm Saved copy: cn-o35-hzau-38997

[32] An institution's own published notice. East China University of Science and Technology, a research team: result notice, Dec 9, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 【成交公示】高性能运算服务器成交公告. https://zhxy.ecust.edu.cn/2025/1209/c6481a185623/page.htm Saved copy: cn-o35-ecust-202512

[33] An institution's own published notice. Fudan University: result notice, May 6, 2026. A purchase notice on the buyer's own site or on a government purchasing site. Page title: GPU计算卡采购结果公告. https://czzx.fudan.edu.cn/ee/ad/c39566a781997/page.htm Saved copy: cn-o35-fudan-5090-202604

[34] An institution's own published notice. Tsinghua University: award notice, undated in the saved copy; it gives Sept 3, 2024 as the date of the purchase notice. A purchase notice on the buyer's own site or on a government purchasing site. https://sbgysfw.sysc.tsinghua.edu.cn/tsinghua.war/tsinghua.api/publish/2024/09/25/19227CBB31822CB760B2D828C9FBA981/content.pdf Saved copy: cn-o35-tsinghua-atlas-202409

[35] An institution's own published notice. University of Science and Technology Liaoning: tender notice, Nov 10, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 人工智能服务器采购项目（第二次）招标公告. https://www.ccgp.gov.cn/cggg/dfgg/gkzb/202511/t20251110_25668468.htm Saved copy: cn-o35-ccgp-lnust-202511

[36] An institution's own published notice. Fujian Polytechnic of Information Technology: result notice, Nov 26, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 福建信息职业技术学院2025年智慧校园标准化建设子项目一算力资源建设结果公告（采购包1）. https://www.ccgp.gov.cn/cggg/dfgg/zbgg/202511/t20251126_25770975.htm Saved copy: cn-o35-ccgp-fjxx-202511

[37] An institution's own published notice. Institute of Automation, Chinese Academy of Sciences: tender notice, to rent cloud computing, Jul 8, 2026. A purchase notice on the buyer's own site or on a government purchasing site. Page title: AI云算力服务采购项目公开招标公告. https://www.ccgp.gov.cn/cggg/zygg/gkzb/202607/t20260708_26894173.htm Saved copy: cn-o35-ccgp-aicloud-202607

[38] An institution's own published notice. Nanjing University of Science and Technology: award notice, Jan 12, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 南京理工大学高性能GPU并行计算集群系统中标公告. https://www.ccgp.gov.cn/cggg/zygg/zbgg/202401/t20240112_21424967.htm Saved copy: cn-o35-ccgp-njust-202401

[39] An institution's own published notice. Tsinghua University: award notice, Jan 25, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 清华大学GPU服务器集群采购项目中标公告. http://www.ccgp.gov.cn/cggg/zygg/zbgg/202401/t20240125_21474425.htm Saved copy: cn-o35-ccgp-tsinghua-202401

[40] An institution's own published notice. ShanghaiTech University: result notice, Aug 3, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: GPU计算服务器及虚拟化服务器扩容的中标（成交）结果公告. https://www.ccgp.gov.cn/cggg/dfgg/zbgg/202408/t20240803_22804017.htm Saved copy: cn-o35-ccgp-shanghaitech-202408

[41] An institution's own published notice. Qinghai Earthquake Agency: award notice, Nov 27, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 青海省巨灾防范工程-数据平台-服务器及存储等设备采购项目中标公告. https://www.ccgp.gov.cn/cggg/zygg/zbgg/202411/t20241127_23724442.htm Saved copy: cn-o35-ccgp-qinghai-202411

[42] An institution's own published notice. Southwest University of Science and Technology: result notice, Dec 9, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 西南科技大学计算机科学与技术学院人工智能计算集群采购项目(二次)中标（成交）结果公告. https://www.ccgp.gov.cn/cggg/dfgg/zbgg/202412/t20241209_23824461.htm Saved copy: cn-o35-ccgp-swust-202412

[43] An institution's own published notice. Central China Normal University: tender notice, Dec 11, 2024. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 华中师范大学人工智能算力平台设备采购项目公开招标公告. https://www.ccgp.gov.cn/cggg/zygg/gkzb/202412/t20241211_23846072.htm Saved copy: cn-o35-ccgp-ccnu-202412

[44] An institution's own published notice. China University of Mining and Technology: purchase notice (a call for price offers), Mar 6, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 中国矿业大学采购与招标管理办公室-询价公告. https://zhbb.cumt.edu.cn/xjgg/11137.chtml Saved copy: cn-o35-cumt-11137

[45] An institution's own published notice. Guangzhou Medical University: result notice, May 9, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 广州医科大学人工智能大模型校内本地化部署采购项目（CZ2025-0397）结果公告. https://www.ccgp.gov.cn/cggg/dfgg/zbgg/202505/t20250509_24568109.htm Saved copy: cn-o35-ccgp-gzhmu-202505

[46] An institution's own published notice. Northwestern Polytechnical University: award notice, May 12, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 西北工业大学云计算及其应用技术国家地方联合工程研究中心创新平台能力提升建设项目高性能集群系统中标公告. https://www.ccgp.gov.cn/cggg/zygg/zbgg/202505/t20250512_24576314.htm Saved copy: cn-o35-ccgp-nwpu-202505

[47] An institution's own published notice. Shanghai Jiao Tong University: award notice, Jul 7, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 上海交通大学人工智能模型训练和推理平台中标公告. https://www.ccgp.gov.cn/cggg/zygg/zbgg/202507/t20250707_24915145.htm Saved copy: cn-o35-ccgp-sjtu-202507

[48] An institution's own published notice. Xinjiang Institute of Ecology and Geography, Chinese Academy of Sciences: award notice, Jul 31, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 中国科学院新疆生态与地理研究所GPU深度学习人工智能服务器采购项目中标公告. https://www.ccgp.gov.cn/cggg/zygg/zbgg/202507/t20250731_25079099.htm Saved copy: cn-o35-ccgp-cas-xinjiang-202507

[49] An institution's own published notice. Xi'an Jiaotong University: award notice, Sept 12, 2025. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 西安交通大学AI大模型GPU算力集群中标公告. https://www.ccgp.gov.cn/cggg/zygg/zbgg/202509/t20250912_25337528.htm Saved copy: cn-o35-ccgp-xjtu-202509

[50] An institution's own published notice. Beijing Institute of Technology, Zhuhai campus: result notice, no date in the saved copy; the project number is of 2025. A purchase notice on the buyer's own site or on a government purchasing site. https://cgzx.bitzh.edu.cn/__local/8/60/8D/C28C61B3B7AD1CFC2B51540B32B_1E5527CF_19976.pdf Saved copy: cn-o35-bitzh-179

[51] An institution's own published notice. University of Chinese Academy of Sciences: award notice, Jan 5, 2026. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 中国科学院大学网上采购平台-货物. http://caigou.ucas.ac.cn/zfjghw/2806.chtml Saved copy: cn-o35-ucas-2806

[52] An institution's own published notice. China National Institute of Standardization: award notice, Aug 19, 2026. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 中国标准化研究院国家数字标准馆算力建设（二期）采购项目中标公告. https://www.ccgp.gov.cn/cggg/zygg/zbgg/202608/t20260819_27166763.htm Saved copy: cn-o35-ccgp-cnis-202608

[53] An institution's own published notice. Tianjin University: result notice, rented computing, Oct 19, 2026. A purchase notice on the buyer's own site or on a government purchasing site. Page title: 天津大学计算机科学与技术学院算力服务采购项目成交公告. https://www.ccgp.gov.cn/cggg/zygg/cjgg/202610/t20261019_27515480.htm Saved copy: cn-o35-ccgp-tju-202610

[54] Press report of words spoken on the record. A press report of a published tender result, not of spoken words: C114, a Chinese telecoms trade site, Aug 19, 2025, on a China Mobile tender. The operator's own notice is not held. Page title: 50亿大单！中国移动AI服务器集采落地：中兴、超聚变、华鲲振宇位列前三 - C114通信网. https://m.c114.com.cn/w118-1295279.html Saved copy: cn-o35-c114-cmcc-inference-2025

[55] Press report of words spoken on the record. A press report of a published tender notice, not of spoken words: C114, a Chinese telecoms trade site, Mar 17, 2026, on China Mobile's tender for AI supernode equipment. The operator's own notice is not held. Page title: 中国移动2026-2027年人工智能超节点设备集采：规模为6208卡 - C114通信网. https://m.c114.com.cn/w3542-1307004.html Saved copy: cn-le17-c114-w3542-1307004

[56] Press report of words spoken on the record. A press report of a published list of bid candidates, not of spoken words: C114, Apr 10, 2026, on the result of the same China Mobile tender. Page title: 20亿大单！五家企业中标 中国移动超节点设备集采落地 - C114通信网. https://m.c114.com.cn/w118-1308371.html Saved copy: cn-le17-c114-w118-1308371

[57] Press report of words spoken on the record. A press report of a published tender notice, not of spoken words: C114, Nov 21, 2026, on China Mobile's second-batch tender for new-generation AI supernode equipment. Page title: 52160卡、近300亿元！中国移动启动第二批新一代AI超节点集采 - C114通信网. https://m.c114.com.cn/w118-1321457.html Saved copy: cn-le17-c114-w118-1321457

[58] An institution's own published notice. Beihang University, purchase notice of its school of computer science, Jul 11, 2026. Page title: 计算机学院RTX PRO 6000D（BUAAJJ20260084）采购公告-北京航空航天大学招标采购中心. https://zbcg.buaa.edu.cn/info/1088/61901.htm Saved copy: cn-le17-buaa-61901-6000d

[59] An institution's own published notice. Wuhan University, record of a decentralised purchase of high-memory GPU cards (RTX PRO 6000D), Jul 7, 2026. Page title: 【分散采购备案单】高显存GPU算力卡（RTX PRO 6000D）-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1027/134391.htm Saved copy: cn-le17-whuf-134391

[60] An institution's own published notice. Wuhan University, record of a decentralised purchase of GPU cards (A100 40GB), Jul 6, 2026. Page title: 【分散采购备案单】GPU算力卡设备-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1027/134121.htm Saved copy: cn-le17-whuf-134121

[61] An institution's own published notice. Wuhan University, result notice for one Nvidia 6000D card, Aug 13, 2026. Page title: nvidia6000D成交结果公告-武汉大学采购与招投标管理中心. https://zb.whu.edu.cn/info/1041/131281.htm Saved copy: cn-le17-whu-131281

[62] Chinese state document. Ministry of Finance and Ministry of Industry and Information Technology, notice on the government purchasing standard for general-purpose servers (2023 edition), published Dec 26, 2023. Page title: 财政部 工业和信息化部关于印发《通用服务器政府采购需求标准（2023年版）》的通知. https://www.mof.gov.cn/jrttts/202312/t20231226_3924137.htm Saved copy: cn-policy-server-procurement-2023

[63] Chinese state document. Jilin provincial government site, investment-promotion pages: a project sheet for a computing centre in Songyuan, Apr 27, 2026. Page title: 数字经济_投资促进. https://www.jl.gov.cn/szfzt/tzcj/zdxm/szjj/202604/t20260427_3626924.html Saved copy: cn-o35-jilin-songyuan-project

[64] Chinese state document. Shanghai Municipal Commission of Economy and Informatization, written reply to proposal No. 0093 of the city's political consultative conference, dated Apr 30, 2025; published on the commission's site on Nov 10, 2025. Page title: 对市政协十四届三次会议 第0093号提案的答复. https://www.sheitc.sh.gov.cn/rddbta/20251110/e6cfe3270ca5483e93cbc55701492e6d.html Saved copy: cn-counter-b11-5

Build check: 104 quotations and 110 further statements were looked for in the saved copies of 64 sources and all were found; a planted false quotation was rejected. 64 sources are documents, filings or named people on the record; 0 are press reports citing unnamed people, counts or machine transcripts. A quotation that is found shows what the source says, not that it is true.
