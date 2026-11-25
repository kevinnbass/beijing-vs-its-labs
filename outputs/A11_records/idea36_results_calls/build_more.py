"""Idea 36, second table: remarks of other companies, and other records of the three, taken by script from the project's
two tables tables/labs_said.tsv and tables/labs_said_more.tsv (each made by another reader of the project). Nothing is fetched.

Run: python3 -I build_more.py   (in this folder; build.py runs it)
Reads   more_chosen.tsv (which rows and passages to show, who, my label, my English for Chinese words)
        ../../../tables/labs_said.tsv, labs_said_more.tsv, replaced_copies.tsv; ../../../loose_ends/hkexnews_saved_ids.tsv
        ../../../loose_ends/L09_labs_calls/census.tsv (that agent's word counts over 61 calls)
Writes  more_fragment.txt       the table in the small markup of scripts/cn_doc_build.py, with hidden check lines
        results_calls_more.tsv  the same rows as a data file
        more_refs.tsv           references for saved ids the argument's references file does not hold
        iflytek_census.tsv      counts of restriction words over the saved iFlytek texts, with a control page
        more_counts.tsv         key <TAB> value, for build.py
Stops if: a passage is not in its saved copy; a saved id is on a do-not-cite list and has no replacement with the same
bytes; on a stock-data-site transcript the passage is not inside one turn, or the turn's speaker label differs from the
table's, or the page's call date differs from the table's; the row's date is not printed on its page in any form tried;
a passage holds a straight double quote or a table bar; a control fails.
"""
import csv, html, json, re, sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, 'scripts')
import cn_srclib as L
P = L.P
HERE = Path(__file__).resolve().parent
PROJ = HERE.parents[2]
sq = L.squash
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
MONF = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
def nice(s):
    d = datetime.strptime(s, '%Y-%m-%d'); return f'{MON[d.month - 1]} {d.day}, {d.year}'

def lines_of(f):
    return {i: ln.split('\t') for i, ln in enumerate((PROJ / 'tables' / f).read_text(encoding='utf-8').splitlines())}
TAB = {'A': lines_of('labs_said.tsv'), 'B': lines_of('labs_said_more.tsv')}
for k in TAB:
    if TAB[k][1][:8] != ['company', 'date', 'event', 'speaker', 'title', 'source_kind', 'exact_words', 'saved_id']: sys.exit(f'table {k}: the columns changed')
banned = {l.split('\t')[0] for l in (PROJ / 'loose_ends' / 'hkexnews_saved_ids.tsv').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')}
# core edit 7b (Nov 25, 2026; atlas/ROUND8.txt R5): the copies saved from idc.com and trendforce.com are no longer cited either
TERMS = PROJ / 'loose_ends' / 'terms_saved_ids.tsv'
if not TERMS.is_file(): sys.exit(f'{TERMS} is missing: the list of copies saved against a site\'s terms is needed for the banned set')
terms = {l.split('\t')[0] for l in TERMS.read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')}
old_ids = {l.split('\t')[0] for l in (PROJ / 'tables' / 'replaced_copies.tsv').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')}
if len(terms) != 19 or not terms <= old_ids: sys.exit(f'{TERMS}: {len(terms)} ids, or some not among the old ids of tables/replaced_copies.tsv (core edit 7b lists 19, all there): read it before changing this line')
banned |= terms
banned |= {'cn-le08-moore-final-prospectus', 'cn-le29-sensetime-2025-annual-en', 'ms-bj-20260114-customs-h200-standard', 'cn-policy-ai-chip-evaluation', 'cn-media-yuyuan-thepaper', 'cn-factions-tencent-reuters-20261120-relay1', 'cn-labs-zhipu-results-20260331'}
repl = {}
rl = [l.split('\t') for l in (PROJ / 'tables' / 'replaced_copies.tsv').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
for r in rl[1:]:
    if r[3] == 'yes' and r[1] != '(none)': repl[r[0]] = r[1]          # only replacements whose bytes are the same
arg_refs = set()
for f in ('argument_refs.tsv', 'argument_refs_more.tsv'):
    for ln in (PROJ / 'argument' / f).read_text(encoding='utf-8').splitlines():
        if ln.strip() and not ln.startswith('#'): arg_refs.add(ln.split('\t')[0])

def sa_page(sid):
    """stockanalysis.com transcript page: (call date, the page's date line, turns as (name, title, squashed text), quarter label)."""
    h = (P / sid / 'body.html').read_text(encoding='utf-8', errors='replace')
    vis = html.unescape(re.sub(r'(?s)<[^>]+>', ' ', re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', h)))
    m = re.search(r'Earnings Call:\s+(Q[1-4] \d{4})\s+([A-Z][a-z]{2} \d{1,2}, \d{4})', re.sub(r'\s+', ' ', vis))
    if not m: sys.exit(f'{sid}: no call date line on the page')
    turns = []
    for blk in re.split(r'<div class="border-t border-sharp pt-5[^"]*">', h)[1:]:
        a = re.search(r'<div class="text-lg font-bold[^"]*">(.*?)</div>', blk, re.S)
        b = re.search(r'<div class="text-sm italic text-muted">(.*?)</div>', blk, re.S)
        name = html.unescape(re.sub(r'<[^>]+>', '', a.group(1))).strip() if a else ''
        title = html.unescape(re.sub(r'<[^>]+>', '', b.group(1))).strip() if b else ''
        body = ' '.join(html.unescape(re.sub(r'<[^>]+>', '', s)).strip() for s in re.findall(r'<span class="transcript-sentence[^>]*>(.*?)</span>', blk, re.S))
        turns.append((name, title, sq(body)))
    return datetime.strptime(m.group(2), '%b %d, %Y'), f'Earnings Call: {m.group(1)} {m.group(2)}', turns, m.group(1)

def date_on_page(sid, d):
    y, mo, da = d.split('-'); i = int(mo) - 1
    forms = [f'{MONF[i]} {int(da)}, {y}', f'{int(da)} {MONF[i]} {y}', f'{y}年{int(mo)}月{int(da)}日', f'{y}年{mo}月{da}日', f'时间 {y}.{mo}.{da}', f'PUBLISHED: {d}', f'{y}.{mo}.{da}', d, f'{y}/{mo}/{da}']
    for f in forms:
        if L.has(f, sid): return f
    return None

LABEL = {   # for saved ids the argument's references do not hold; {date} is filled from the table's date column
 'cn-le26-iflytek-ir-20250213': ('FIL', "iFlytek, record of investor-relations activity of {date} (an investor call), on the disclosure site cninfo.com.cn. The record lists the company's board secretary as its only attendee"),
 'cn-le26-iflytek-ir-20250422': ('FIL', "iFlytek, record of investor-relations activity: its results meeting of {date}, on the disclosure site cninfo.com.cn. The record lists who attended for the company, not who gave each answer"),
 'cn-le26-iflytek-2024-annual': ('FIL', "iFlytek, annual report for 2024, dated {date}, on the disclosure site cninfo.com.cn"),
 'cn-le26-sensetime-2024-results-en': ('FIL', "SenseTime, annual results announcement for the year ended Dec 31, 2024, dated {date} (English), on the host its investor page uses"),
 'cn-le29-zhipu-results-20260331-en': ('FIL', "Zhipu (Z.AI), annual results announcement, dated {date}, as linked from its own investor site"),
 'cn-le09-hk01-tencent-tong-domestic-chips': ('REC', "HK01 (a Hong Kong news site), {date}, reporting Dowson Tong of Tencent at Tencent Cloud Day Hong Kong. Reported speech, not a quotation"),
}
LABEL_CHECK = {  # words on the page that bear out what a label or a 'who' says
 'cn-le26-iflytek-ir-20250213': ['科大讯飞董事、副总裁、董事会秘书江涛', '投资者关系活动记录表'],
 'cn-le26-iflytek-ir-20250422': ['☑ 业绩说明会', '投资者关系活动记录表'],
 'cn-le26-iflytek-ir-20260429': ['☑ 业绩说明会'], 'cn-le26-iflytek-ir-20260821': ['☑ 业绩说明会'],
 'cn-le26-iflytek-2024-annual': ['2024 年年度报告'], 'cn-le26-iflytek-2026-interim': ['2026 年半年度报告'],
 'cn-le26-sensetime-2024-results-en': ['FOR THE YEAR ENDED DECEMBER 31, 2024', 'ANNUAL RESULTS ANNOUNCEMENT'],
 'cn-le29-zhipu-results-20260331-en': ['ANNUAL RESULTS ANNOUNCEMENT'], 'cn-le29-zhipu-2026-interim-results-en': ['INTERIM RESULTS ANNOUNCEMENT'],
 'cn-le09-hk01-tencent-tong-domestic-chips': ['集团高级执行副总裁、云与智慧产业事业群首席执行官汤道生', 'Tencent Cloud Day Hong Kong'],
 'cn-usside-070': ['tech.meituan.com'],
}
# Round 9 (Nov 25, 2026; the core now marks a Kingsoft Cloud answer as given through an interpreter): on these stock-data-site
# pages the quoted English is a translation by the page's own marks or words. The note goes into the row's "who" cell; the build
# stops unless the turn that holds the quotation begins with the page's mark of a passage not in English (where asked) and holds
# the page's words (where given), and (where named) unless the turn before it is that speaker's and holds only the mark.
# Columns: words the turn must hold, or None | the turn must begin with the mark | the speaker of a turn before it that holds only the mark, or None | the note.
INTERP = {
 'cn-le09-kingsoftcloud-call-20260819-sa': ('Allow me to quickly translate', True, None, 'the English follows a passage the page leaves out as not in English and the words "Allow me to quickly translate"'),
 'cn-le09-kingsoftcloud-call-20250820-sa': (None, True, None, 'the English follows a passage the page leaves out as not in English'),
 'cn-le09-kingsoftcloud-call-20250528-sa': ("very quickly to translate from Mr. Zou's response", False, 'Zou Tao', 'the turn begins "very quickly to translate from Mr. Zou\'s response", after a turn of Zou Tao\'s that the page leaves out as not in English'),
}
MARK0 = re.compile(r'^\[(foreignlanguage|non-englishcontent)\]')

sel = [l.split('\t') for l in (HERE / 'more_chosen.tsv').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
bad, out, sa_cache = [], [], {}
for t, line, sid0, pidx, cut, who, about, gloss in sel:
    c = TAB[t].get(int(line))
    if not c or c[7] != sid0: bad.append(f'{t}{line}: the table row is not {sid0}'); continue
    sid = repl.get(sid0, sid0)
    if sid in banned: bad.append(f'{sid0}: on a do-not-cite list, and no replacement with the same bytes'); continue
    if not (P / sid).is_dir(): bad.append(f'{sid}: no saved copy'); continue
    company, date = c[0], c[1]
    ps = [x.strip() for x in c[6].split('||')]
    cuts = dict(x.split('=', 1) for x in cut.split(';;') if x)
    quotes = []
    for k in pidx.split(','):
        p = ps[int(k) - 1]
        if k in cuts:
            if cuts[k] not in p: bad.append(f'{t}{line}: the cut is not inside passage {k}'); continue
            p = cuts[k]
        if '"' in p or '|' in p: bad.append(f'{t}{line}: passage {k} holds a straight quote or a bar'); continue
        if not L.has(p, sid): bad.append(f'{sid}: NOT FOUND: {p[:70]}'); continue
        quotes.append(p)
    gl = [] if gloss == '-' else [g.strip() for g in gloss.split('||')]
    if gl and len(gl) != len(quotes): bad.append(f'{t}{line}: {len(quotes)} passages, {len(gl)} English renderings'); continue
    if not gl and any(re.search(r'[一-鿿]', q) for q in quotes): bad.append(f'{t}{line}: a Chinese passage without an English rendering'); continue
    checks = []
    if sid.endswith('-sa'):
        if sid not in sa_cache: sa_cache[sid] = sa_page(sid)
        d, date_words, turns, quarter = sa_cache[sid]
        if d.strftime('%Y-%m-%d') != date: bad.append(f'{sid}: the page says {d:%Y-%m-%d}, the table {date}'); continue
        whoset = set()
        for q in quotes: whoset.update((n, ti) for n, ti, body in turns if sq(q) in body)
        if len(whoset) != 1: bad.append(f'{sid}: speakers {sorted(whoset)}'); continue
        name, title = whoset.pop()
        if name != c[3] or (not c[4].startswith('(') and title != c[4]): bad.append(f'{sid}: the page labels the speaker {name} | {title}; the table {c[3]} | {c[4]}'); continue
        if who != '@page': bad.append(f'{t}{line}: a stock-data-site row must take its speaker from the page'); continue
        who_txt = (f'{name}, {title}' if title else f'{name} (the page gives no name or title)') + '; results call, stock-data site'
        if sid in INTERP:
            must, mark0, prev, note = INTERP[sid]
            ti_ = [k for k, (n, ti, body) in enumerate(turns) if all(sq(q) in body for q in quotes)]
            if len(ti_) != 1: bad.append(f'{sid}: the quoted English is not in one turn'); continue
            body0 = turns[ti_[0]][2]
            if must and sq(must) not in body0: bad.append(f'{sid}: the turn does not hold: {must}'); continue
            if mark0 and not MARK0.match(body0): bad.append(f'{sid}: the turn does not begin with the mark of a passage not in English'); continue
            if prev and not (ti_[0] > 0 and turns[ti_[0] - 1][0] == prev and MARK0.match(turns[ti_[0] - 1][2]) and MARK0.sub('', turns[ti_[0] - 1][2]) == ''): bad.append(f'{sid}: the turn before is not {prev} with only the mark'); continue
            who_txt += '; ' + note
        checks += [date_words, f'{name} {title}'.strip()]
        kind, label = 'REC', f"{company}, results call labelled {quarter} by the site, {nice(date)}. Transcript on the stock-data site stockanalysis.com. The text and speaker labels are the site's; nobody has checked them against the recording"
    else:
        if who == '@page': bad.append(f'{t}{line}: @page is only for stock-data-site transcripts'); continue
        f = date_on_page(sid, date)
        if not f: bad.append(f'{sid}: the date {date} is not printed on the page in any form tried'); continue
        who_txt = who; checks.append(f)
        for w in LABEL_CHECK.get(sid, []):
            if not L.has(w, sid): bad.append(f'{sid}: label check not on the page: {w}')
            checks.append(w)
        kind, label = (LABEL[sid][0], LABEL[sid][1].format(date=nice(date))) if sid in LABEL else (None, None)
        if sid not in LABEL and sid not in arg_refs: bad.append(f'{sid}: no label written and not in the argument\'s references'); continue
    url = json.loads((P / sid / 'meta.json').read_text()).get('url') or ''
    out.append({'date': date, 'company': company, 'who': who_txt, 'about': about, 'quotes': quotes, 'gloss': gl, 'sid': sid, 'sid0': sid0, 'checks': checks, 'kind': kind, 'label': label, 'url': url, 'table': t, 'line': line})
if bad: print('\n'.join(bad)); sys.exit(f'NOT WRITTEN: {len(bad)} problem(s)')
out.sort(key=lambda r: (r['date'], r['company']))
frag = ['| Date | Company | Who, and what record | About | Exact words, with English in round brackets |']
for r in out:
    cell = '; '.join(f'"{q}"' + (f' ({g})' if r['gloss'] else '') for q, g in zip(r['quotes'], r['gloss'] or [''] * len(r['quotes'])))
    frag.append(f"| {nice(r['date'])} | {r['company']} | {r['who']} | {r['about']} | {cell} [{r['sid']}] |")
seen = set()
for r in out:
    for ch in r['checks']:
        if (r['sid'], ch) not in seen: seen.add((r['sid'], ch)); frag.append(f"!! {r['sid']} | {ch}")
(HERE / 'more_fragment.txt').write_text('\n'.join(frag) + '\n', encoding='utf-8')
with open(HERE / 'results_calls_more.tsv', 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t'); w.writerow(['date', 'company', 'who_and_record', 'about_my_words', 'exact_words', 'my_english', 'saved_id', 'saved_id_in_the_project_table', 'project_table', 'line', 'address'])
    for r in out: w.writerow([r['date'], r['company'], r['who'], r['about'], ' || '.join(r['quotes']), ' || '.join(r['gloss']), r['sid'], r['sid0'], 'labs_said.tsv' if r['table'] == 'A' else 'labs_said_more.tsv', r['line'], r['url']])
refs, done = [], set()
for r in out:
    if r['sid'] in done or r['sid'] in arg_refs: continue
    done.add(r['sid']); refs.append(f"{r['sid']}\t{r['kind']}\t{r['label']}\t{r['url']}")
(HERE / 'more_refs.tsv').write_text('\n'.join(refs) + '\n', encoding='utf-8')

# ---- counts for the note
cnt = []
def put(k, v): cnt.append(f'{k}\t{v}')
put('more_rows', len(out)); put('more_companies', len({r['company'] for r in out})); put('more_company_list', ', '.join(sorted({r['company'] for r in out})))
put('more_sa_rows', sum(1 for r in out if r['sid'].endswith('-sa'))); put('more_chinese_rows', sum(1 for r in out if r['gloss']))
put('more_sa_calls', len({r['sid'] for r in out if r['sid'].endswith('-sa')}))
press = [r for r in out if r['kind'] == 'REC' and not r['sid'].endswith('-sa')]
put('more_press_rows', len(press)); put('more_own_rows', len(out) - len(press) - sum(1 for r in out if r['sid'].endswith('-sa')))
if any(r['kind'] is None and not r['sid'].startswith(('cn-le26-iflytek', 'cn-usside-070', 'cn-le29-zhipu')) for r in out): sys.exit('a row whose kind is not known: count it by hand')
# agent L09's census over 61 calls of 8 companies, Jan 2025 to Nov 2026
cl = [l.split('\t') for l in (PROJ / 'loose_ends' / 'L09_labs_calls' / 'census.tsv').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
cen = {r[0]: r for r in cl[1:]}
n61 = int(cen['revenue (control)'][2])
if int(cen['revenue (control)'][1]) != n61: sys.exit('L09 census: the control word is not in every call')
put('l9_calls', n61)
for k, w in (('nvidia', 'Nvidia'), ('huawei', 'Huawei'), ('misspell', 'misspellings of Nvidia or Huawei'), ('cyberspace', 'Cyberspace Administration'), ('customs', 'customs'), ('h200', 'H200'), ('h20', 'H20')):      # the marks of passages not in English are recounted below (round 9)
    put(f'l9_{k}', cen[w][1])
# Round 9 (Nov 25, 2026): the reader's count of the marks of passages not in English missed marks that a page's markup splits
# ("[Non-English cont ent]") or spaces ("[ Foreign language]"); the core's own count was corrected the same day for the same
# kind of fault. Recount on the pages as a visitor sees them, over the reader's own list of calls. Controls: the strict pattern
# must give the reader's figure (the same reading of the pages), and the loose one must find both planted forms and not plain prose.
def _sp(w): return r'\s*'.join(re.escape(ch) for ch in w)
MARK_STRICT = re.compile(r'\[(?:Foreign language|Non-English content)\]', re.I)
MARK_LOOSE = re.compile(r'\[\s*(?:' + _sp('foreign') + r'\s+' + _sp('language') + '|' + _sp('non-english') + r'\s+' + _sp('content') + r')\s*\]', re.I)
if not (MARK_LOOSE.search('Hey [Non-English cont ent] Thanks') and MARK_LOOSE.search('delivery, [ Foreign language].') and not MARK_LOOSE.search('in foreign languages and non-English content')): sys.exit('control failed: the loose pattern for the marks')
def _vis(sid):
    if sid.endswith('-own'): return (P / sid / 'text.txt').read_text(encoding='utf-8', errors='replace')
    h = (P / sid / 'body.html').read_text(encoding='utf-8', errors='replace')
    return html.unescape(re.sub(r'(?s)<[^>]+>', ' ', re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', h)))
l9ids = [r['saved_id'] for r in csv.DictReader((l for l in (PROJ / 'loose_ends' / 'L09_labs_calls' / 'calls_read.tsv').read_text(encoding='utf-8').splitlines() if not l.startswith('#')), delimiter='\t')]
if len(l9ids) != n61: sys.exit(f'L09 calls_read.tsv lists {len(l9ids)} calls, its census {n61}')
vt = {s: _vis(s) for s in l9ids}
n_strict, n_loose = sum(1 for s in l9ids if MARK_STRICT.search(vt[s])), sum(1 for s in l9ids if MARK_LOOSE.search(vt[s]))
if n_strict != int(cen['untranslated passage marker'][1]): sys.exit(f'the strict recount ({n_strict}) is not the reader\'s count ({cen["untranslated passage marker"][1]}): reword the paragraph on the marks')
if n_loose < n_strict: sys.exit('control failed: the loose recount is below the strict one')
put('l9_untranslated', n_loose); put('l9_untranslated_reader', n_strict); put('l9_untranslated_missed', n_loose - n_strict)
put('l9_h20_which', '; '.join(f"{' '.join(x.split()[:-1])} {nice(x.split()[-1])}" for x in cen['H20'][3].split('; ')))
# my own count over the saved iFlytek texts (reports, investor records, exchange-platform answers), with a control page
ids = sorted(p.name for p in P.glob('cn-le26-iflytek-*') if (p / 'text.txt').exists())
WORDS = ['约谈', '窗口指导', '海关', '不得采购', '限制采购', '政府要求', '网信办', '算力']
CONTROL = 'cn-acts-peoplesdaily-bjd-20250801'
def counts(sid):
    s = re.sub(r'\s+', '', (P / sid / 'text.txt').read_text(encoding='utf-8', errors='replace')); return [s.count(w) for w in WORDS]
tab = {sid: counts(sid) for sid in ids + [CONTROL]}
if any(tab[sid][WORDS.index('算力')] == 0 for sid in ids): sys.exit('iFlytek census: a text layer lacks the control word 算力')
if tab[CONTROL][WORDS.index('约谈')] == 0 or tab[CONTROL][WORDS.index('网信办')] == 0: sys.exit('iFlytek census: the control page lacks the control words')
with open(HERE / 'iflytek_census.tsv', 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t'); w.writerow(['saved_id'] + WORDS)
    for sid in ids + [CONTROL]: w.writerow([sid] + tab[sid])
put('ifly_texts', len(ids)); put('ifly_reports', sum(1 for s in ids if re.search(r'-(annual|interim|q[1-4])$', s))); put('ifly_records', sum(1 for s in ids if '-ir-' in s)); put('ifly_answers', sum(1 for s in ids if '-irm-' in s))
for w in WORDS[:6]: put(f'ifly_{w}', sum(tab[s][WORDS.index(w)] for s in ids))
put('ifly_网信办', sum(tab[s][WORDS.index('网信办')] for s in ids))
put('control_约谈', tab[CONTROL][WORDS.index('约谈')]); put('control_网信办', tab[CONTROL][WORDS.index('网信办')])
(HERE / 'more_counts.tsv').write_text('key\tvalue\n' + '\n'.join(cnt) + '\n', encoding='utf-8')
print(f"{len(out)} rows from {len({r['sid'] for r in out})} saved copies; companies: {', '.join(sorted({r['company'] for r in out}))}; quotations checked {sum(len(r['quotes']) for r in out)}; ids replaced: {sorted((r['sid0'], r['sid']) for r in out if r['sid0'] != r['sid'])}")
