"""Idea 36: build the table of results-call remarks from rows_chosen.txt, reading speaker, title and call date from the
saved pages, and checking every quotation against the saved copy before anything is written.

Run: python3 -I build_table.py   (in this folder)
Reads   rows_chosen.txt (saved id | what it is about | exact words || exact words), calls.tsv (the 39 calls saved)
Writes  table_fragment.txt  the table in the small markup of scripts/cn_doc_build.py, with hidden check lines
        results_calls_table.tsv  the same rows as a data file (date, company, speaker, title, words, saved id, address)
        calls_coverage.tsv  one line per call: rows chosen, candidate paragraphs
        extra_refs.tsv  the references file for cn_doc_build.py (one line per saved id used)
Stops with an error if a quotation is not found, if a row's quotations belong to different speakers, or if a speaker
or date cannot be read from the page.
Speaker and title: on stockanalysis.com pages, the name and title lines above the turn that holds the words; on
Alibaba's own PDF transcripts, the label line above the words ("Name:" or a centred name) and the title the same
transcript gives that name in its introduction. Date: the date the page itself prints.
"""
import csv, html, json, re, sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, 'scripts')
import cn_srclib as L
P = L.P
HERE = Path(__file__).resolve().parent
sq = L.squash
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
def nice(d): return f'{MON[d.month - 1]} {d.day}, {d.year}'

def sa_page(sid):
    h = (P / sid / 'body.html').read_text(encoding='utf-8', errors='replace')
    vis = html.unescape(re.sub(r'(?s)<[^>]+>', ' ', re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', h)))
    m = re.search(r'Earnings Call:\s+(Q[1-4] \d{4})\s+([A-Z][a-z]{2} \d{1,2}, \d{4})', re.sub(r'\s+', ' ', vis))
    if not m: sys.exit(f'{sid}: no call date line on the page')
    date_words = f'Earnings Call: {m.group(1)} {m.group(2)}'
    d = datetime.strptime(m.group(2), '%b %d, %Y')
    turns = []
    for blk in re.split(r'<div class="border-t border-sharp pt-5[^"]*">', h)[1:]:
        a = re.search(r'<div class="text-lg font-bold[^"]*">(.*?)</div>', blk, re.S)
        b = re.search(r'<div class="text-sm italic text-muted">(.*?)</div>', blk, re.S)
        name = html.unescape(re.sub(r'<[^>]+>', '', a.group(1))).strip() if a else ''
        title = html.unescape(re.sub(r'<[^>]+>', '', b.group(1))).strip() if b else ''
        body = ' '.join(html.unescape(re.sub(r'<[^>]+>', '', s)).strip() for s in re.findall(r'<span class="transcript-sentence[^>]*>(.*?)</span>', blk, re.S))
        turns.append((name, title, sq(body)))
    return d, date_words, turns, m.group(1)

LABEL = re.compile(r"^([A-Z][A-Za-z.\-' ]{2,40})(?: \(([^)]+)\))?:$")
def pdf_page(sid):
    t = (P / sid / 'text.txt').read_text(encoding='utf-8', errors='replace')
    m = re.search(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), (\d{1,2}) ([A-Z][a-z]+) (\d{4})', t)
    if not m: sys.exit(f'{sid}: no date on the cover')
    d = datetime.strptime(f'{m.group(2)} {m.group(3)} {m.group(4)}', '%d %B %Y')
    q = re.search(r'Alibaba Group\s+(.*?)\s+Conference Call', t[:1500].replace('\n', ' '))
    turns, name, firm, buf = [], '', '', []
    lines = t.split('\n'); i = 0
    def flush():
        nonlocal buf
        if buf: turns.append((name, firm, sq(' '.join(buf)))); buf = []
    while i < len(lines):
        ln = lines[i]; s = ln.strip()
        if re.match(r'^Alibaba Group .* Conference Call\s', s) or re.fullmatch(r'\d{1,3}', s): i += 1; continue
        mm = LABEL.match(s)
        if mm and not ln.startswith(' ' * 6): flush(); name, firm = mm.group(1), mm.group(2) or ''; i += 1; continue
        if ln.startswith(' ' * 20) and re.fullmatch(r"[A-Z][A-Za-z.\-' ]{2,40}", s):
            j = i + 1
            while j < len(lines) and not lines[j].strip(): j += 1
            if j < len(lines) and lines[j].startswith(' ' * 15) and re.search(r'Alibaba|Group|Officer|CEO|CFO|Chairman|Relations|President', lines[j]):
                flush(); name, firm = s, ''; i = j + 1; continue
        if s: buf.append(s)
        i += 1
    flush()
    intro = re.sub(r'\s+', ' ', t[:6000])
    return d, m.group(0), turns, (q.group(1) if q else ''), intro

# Round 10 (Nov 25, 2026; atlas/core_edit/hand_out/SF1_FOR_MAIN.txt section 6, code change 5, and core rows SF1-037 and 038 of
# tables/labs_said.tsv): on a stock-data-site page an English turn labelled only "Speaker N" can render a named speaker's turn
# that the page leaves out as not in English. named_before() walks back from such a turn over unnamed "Speaker N" turns that
# hold only the page's mark (on Alibaba's call of Nov 19, 2026, "Speaker 7" puts analysts' questions into Chinese, and once
# stands between the chief executive's turn and the English); the first other turn must be named, carry a title, and hold
# only the mark. The row keeps the page's label in the speaker column; the title column gives the named turn in the core
# table's words. Every quotation of a row must give the same named turn, and the page must announce interpretation.
SPK = re.compile(r'^Speaker \d+$')
MARK_ONLY = re.compile(r'^(\[(?:non-englishcontent|foreignlanguage)\])+$')
INTERP_WORDS = ('will provide consecutive interpretation', 'There will be consecutive interpretation')
def named_before(turns, k):
    j = k - 1
    while j >= 0 and SPK.match(turns[j][0]) and not turns[j][1] and MARK_ONLY.match(turns[j][2]): j -= 1
    if j >= 0 and turns[j][0] and turns[j][1] and not SPK.match(turns[j][0]) and MARK_ONLY.match(turns[j][2]): return (turns[j][0], turns[j][1], j)
    return None
_m = sq('[Non-English content]')
_ctl = [('Eddie Wu', 'CEO', _m), ('Speaker 7', '', _m), ('Speaker 4', '', sq('Thank you for the question.'))]
assert named_before(_ctl, 2)[:2] == ('Eddie Wu', 'CEO'), 'control: the named turn two back, over a mark-only Speaker turn'
assert named_before([('Eddie Wu', 'CEO', sq('Hello, in English.')), ('Speaker 4', '', sq('Thanks.'))], 1) is None, 'control: a named turn in English names nobody'
assert named_before([('Speaker 18', '', _m), ('Speaker 10', '', sq('Thanks.'))], 1) is None, 'control: a Chinese turn the page does not name names nobody'
assert named_before([('Eddie Wu', 'CEO', _m), ('Speaker 7', '', sq('A question in English.')), ('Speaker 4', '', sq('Thanks.'))], 2) is None, 'control: an English turn between'

rows_in = []
for ln in (HERE / 'rows_chosen.txt').read_text(encoding='utf-8').splitlines():
    if not ln.strip() or ln.startswith('#'): continue
    sid, about, words = [x.strip() for x in ln.split('|', 2)]
    rows_in.append((sid, about, [w.strip() for w in words.split('||')]))
calls = {r['saved_id']: r for r in csv.DictReader(open(HERE / 'calls.tsv', encoding='utf-8'), delimiter='\t') if r['saved_id']}
cache, out, bad = {}, [], []
for sid, about, quotes in rows_in:
    if sid not in calls: bad.append(f'{sid}: not in calls.tsv'); continue
    own = sid.endswith('-own')
    if sid not in cache: cache[sid] = pdf_page(sid) if own else sa_page(sid)
    pg = cache[sid]; d, date_words, turns = pg[0], pg[1], pg[2]
    who = set()
    for q in quotes:
        if not L.has(q, sid): bad.append(f'{sid}: NOT FOUND: {q[:80]}'); continue
        hit = [(n, t) for n, t, body in turns if sq(q) in body]
        if not hit: bad.append(f'{sid}: words found on the page but in no single turn: {q[:80]}'); continue
        who.update(hit)
    if len(who) != 1: bad.append(f'{sid}: {about}: speakers {sorted(who)}'); continue
    name, title = who.pop()
    named = None
    if not own and SPK.match(name) and not title:
        ks = {k for q in quotes for k, (n, ti, body) in enumerate(turns) if sq(q) in body}
        nb = {named_before(turns, k)[:2] if named_before(turns, k) else None for k in ks}
        if len(nb) == 1 and None not in nb:
            if not any(L.has(w, sid) for w in INTERP_WORDS): bad.append(f'{sid}: {about}: a named turn before the English, but the page does not announce interpretation'); continue
            nn, nt = nb.pop(); named = (nn, nt, len(ks) > 1, next(w for w in INTERP_WORDS if L.has(w, sid)))
            title = f"(no title for {name}: the English rendering of {'turns' if len(ks) > 1 else 'the turn'} the page labels {nn}, {nt})"
    checks = [date_words]
    if own:
        m = re.search(re.escape(name) + r', ([A-Z][A-Za-z ,&\-]+?)(?:;|\.| and )', pg[4])
        if not m: bad.append(f'{sid}: no title for {name} in the introduction'); continue
        title = m.group(1).strip(); checks += [f'{name}, {title}', f'{name}:' if L.has(f'{name}:', sid) else name]
    else:
        if not name: bad.append(f'{sid}: {about}: no speaker label'); continue
        checks.append(f'{name} {title}'.strip() if not named else name)
        if named: checks += [f'{named[0]} {named[1]}', named[3]]
    for c in checks:
        if not L.has(c, sid): bad.append(f'{sid}: check words not on the page: {c}')
    out.append({'date': d, 'company': calls[sid]['company'], 'speaker': name, 'title': title, 'about': about, 'quotes': quotes, 'sid': sid, 'checks': checks, 'url': calls[sid]['address'], 'quarter': pg[3], 'named': named})
_kq = 'The computing power required for inference computing is sufficiently supplied in the market.'
_kt = sa_page('cn-le09-kuaishou-call-20250325-sa')[2]
_kk = [k for k, (n, ti, body) in enumerate(_kt) if sq(_kq) in body]
if len(_kk) != 1 or not SPK.match(_kt[_kk[0]][0]) or named_before(_kt, _kk[0]) is not None: bad.append('control failed: Kuaishou, Mar 25, 2025 (its Chinese turn is labelled Speaker 18) must stay unnamed')
_named = [r for r in out if r['named']]
print(f"named turns given for {len(_named)} rows: " + '; '.join(f"{r['date']:%Y-%m-%d} {r['company']} {r['about']} -> {r['named'][0]}" for r in _named))
if bad: print('\n'.join(bad)); sys.exit(f'NOT WRITTEN: {len(bad)} problem(s)')
out.sort(key=lambda r: (r['date'], r['company']))
frag = ['| Date of the call | Company | Speaker, as the page gives it | About | Exact words |']
for r in out:
    if r['named']:
        nn, nt, many, _ = r['named']
        sp = f"{r['speaker']}, the English rendering of {'turns' if many else 'the turn'} the page labels {nn}, {nt} (read as the interpreter's)"
    else:
        sp = r['speaker'] + (f", {r['title']}" if r['title'] else ' (the page gives no name or title)')
    frag.append(f"| {nice(r['date'])} | {r['company']} | {sp} | {r['about']} | " + '; '.join(f'"{q}"' for q in r['quotes']) + f" [{r['sid']}] |")
seen = set()
for r in out:
    for c in r['checks']:
        if (r['sid'], c) not in seen: seen.add((r['sid'], c)); frag.append(f"!! {r['sid']} | {c}")
(HERE / 'table_fragment.txt').write_text('\n'.join(frag) + '\n', encoding='utf-8')
with open(HERE / 'results_calls_table.tsv', 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t'); w.writerow(['call_date', 'company', 'speaker_as_page_gives', 'title_as_page_gives', 'about_my_words', 'exact_words', 'saved_id', 'address'])
    for r in out: w.writerow([r['date'].strftime('%Y-%m-%d'), r['company'], r['speaker'], r['title'], r['about'], ' || '.join(r['quotes']), r['sid'], r['url']])
# coverage: one line per call
cand = {}
csv.field_size_limit(10**7)
if (HERE / 'candidates.tsv').exists():
    for c in csv.DictReader(open(HERE / 'candidates.tsv', encoding='utf-8'), delimiter='\t'): cand[c['saved_id']] = cand.get(c['saved_id'], 0) + 1
n_rows = {}
for r in out: n_rows[r['sid']] = n_rows.get(r['sid'], 0) + 1
with open(HERE / 'calls_coverage.tsv', 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t'); w.writerow(['company', 'call_date_from_index', 'saved_id', 'candidate_paragraphs', 'rows_in_table', 'from'])
    for sid, c in sorted(calls.items(), key=lambda kv: (kv[1]['company'], kv[1]['call_date'])): w.writerow([c['company'], c['call_date'], sid, cand.get(sid, 0), n_rows.get(sid, 0), c['from']])
# references file
def kind_label(c, sid):  # FIL: the company's own transcript; REC: a transcript site's record of words spoken on the record
    pg = cache.get(sid)
    if sid.endswith('-own'): return 'FIL', f"{c['company']}, results call for the {pg[3].replace(' Results', '')}, {nice(pg[0])}. The company's own English transcript, from its investor site"
    return 'REC', f"{c['company']}, results call labelled {pg[3]} by the site, {nice(pg[0])}. Transcript on the stock-data site stockanalysis.com. The text and speaker labels are the site's; nobody has checked them against the recording"
refs = []
for sid in sorted({r['sid'] for r in out}, key=lambda s: (cache[s][0], s)):
    k, lab = kind_label(calls[sid], sid); refs.append(f"{sid}\t{k}\t{lab}\t{calls[sid]['address']}")
(HERE / 'table_refs.tsv').write_text('\n'.join(refs) + '\n', encoding='utf-8')
by = {}
for r in out: by[r['company']] = by.get(r['company'], 0) + 1
print(f"{len(out)} rows from {len({r['sid'] for r in out})} calls of {len(calls)} saved; by company {by}; quotations checked {sum(len(r['quotes']) for r in out)}")
for r in out: print(f"  {r['date']:%Y-%m-%d} {r['company']:8s} {r['speaker']} | {r['title']} | {r['about']}")
