#!/usr/bin/env python3
"""Build the tracker page: the dated record as a list, newest first, under a dated log of additions and corrections.

Run:  python3 -I build.py              builds this folder
      python3 -I build.py --dir DIR    builds another copy (DIR/data/figure_data.txt and DIR/data/tracker_log.tsv)
Reads   data/figure_data.txt   the records, in the format of the figure's data file (its header explains it)
        data/tracker_log.tsv   the dated log (its header explains the columns)
        data/state_of_play.txt the state of play shown at the top (its header explains the markup; added Nov 23, 2026)
        data/house_licence_table.tsv  a copy of the project's tables/house_licence_table.tsv, which the state of play counts
Writes  quotes.tsv             every quotation, number and hidden check the page rests on: saved id <TAB> words
        tracker.html           the page
tracker.html is written only if every check passes:
  - every record is complete and its saved copy exists (research/primary/<id>);
  - every Q line (the source's exact words) stands in the saved copy of its id;
  - every string between straight double quotes in a T line or in a log line stands in that saved copy;
  - every number in a T line stands in that saved copy (years and chip names apart); a number too short for the
    checker (under 6 characters) needs a "!" line of the same id that holds it;
  - every "!" line of the data file and every hidden check of the log holds ("NOT id | words" must not be found);
  - a planted false quotation is rejected, so the check can fail;
  - the last log line's count of records equals the number of records in the data file;
  - in the state of play: every quotation stands in the saved copy of an id cited in its item; every hidden check holds
    and every negative one does not; every number stands in a quotation or hidden check of its item, or is a count of
    the House table made here, or is listed as the project's own count; the table's total and approved count, put into
    the summary's own words, are found in the summary;
  - scripts/cn_has.py passes on quotes.tsv (exit 0).
It also prints a date screen (is each record's date written in its saved page?). For records already in the list that
is a report, not a stop; add_record.py refuses a new record whose date is not in its page unless a reason is given.
A quotation that is found shows what the source says, not that it is true.
Round 8 (core edit 7, Nov 25, 2026): a record of the figure's data file may carry an "N" line, its fixed number in the
figure (record 62 keeps 62 though it stands at its date among the others). This page shows no record numbers, so the
line is read (as scripts/cn_figure_build.py reads it) and checked only to be a whole number given to one record;
a record added here with add_record.py takes no "N" line.
"""
import html, re, subprocess, sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]                                    # the project root, which holds scripts/ and research/primary/
assert (ROOT / 'scripts' / 'cn_srclib.py').is_file(), f'scripts/cn_srclib.py not found under {ROOT}'
sys.path.insert(0, str(ROOT / 'scripts'))
import cn_srclib as L   # noqa: E402

MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
LANES = {'BH': ('Beijing', 'holds Nvidia back', 'away'), 'BL': ('Beijing', 'lets Nvidia in', 'toward'),
         'CN': ('The companies', 'reach for Nvidia', 'toward'), 'CH': ('The companies', 'turn to home-made chips', 'away')}
KINDS = {'doc': 'On the record: a government document or an official', 'rec': 'On the record: a company or a named person outside government',
         'press': 'Press report citing unnamed people'}
CITE = re.compile(r'\[((?:cn|ms|man|cnpol)-[A-Za-z0-9-]+)\]')
CITES = re.compile(r'\[(?:cn|ms|man|cnpol)-[A-Za-z0-9-]+\](?:\s*\[(?:cn|ms|man|cnpol)-[A-Za-z0-9-]+\])*')
DATE_RX = re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)[a-z]*\.? \d{1,2}(?!\d)(?:, \d{4})?|\b\d{1,2}:\d\d\b')
SUMMARY, TABLE = 'cn-usdocs-hfac-summary-20261119', 'cn-usdocs-hfac-decisions-20261119'
TENCENT_FULL = 445_000      # the committee's figure for Nvidia's application of Dec 19, 2025 for Tencent (checked in the summary below)
LOGKINDS = {'state': 'State', 'addition': 'Addition', 'correction': 'Correction', 'wording': 'Wording', 'note': 'Note'}
QUOTE = re.compile(r'"([^"]+)"')
NUM = re.compile(r'(?<![A-Za-z0-9-])\$?\d[\d,]*(?:\.\d+)?(?:\s(?:million|billion))?%?(?![A-Za-z0-9]|-[A-Za-z])')
CHIPNAME = re.compile(r'(?:RTX|PRO|Pro)\s$')
CONTROL = ('Beijing has published a ban on the purchase of Nvidia chips', 'cn-clips-evidence-1')
esc = html.escape


def fmt(d): return f'{MON[d.month - 1]} {d.day}, {d.year}'


def smart(s): return re.sub(r'"([^"]*)"', '“\\1”', s).replace("'", '’')


def load_data(f):
    """Return (records, extra checks). A record: lane, kind, date, dl (date label or None), sid, T, S, Q, E, U, C, N (the
    figure's fixed number, or '')."""
    evs, checks, cur = [], [], None
    for n, ln in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
        if not ln.strip() or ln.startswith('#'): continue
        if ln.startswith('@ '):
            p = ln.split()
            if len(p) != 6 or p[1] not in LANES or p[2] not in KINDS: sys.exit(f'{f.name} line {n}: bad record line: {ln[:70]}')
            cur = dict(lane=p[1], kind=p[2], date=date.fromisoformat(p[3]), dl=None if p[4] == '-' else p[4].replace('_', ' '), sid=p[5], T='', S='', Q='', E='', U='', C='', N='', line=n)
            evs.append(cur)
        elif ln.startswith('! '):
            sid, q = ln[2:].split(' | ', 1); checks.append((sid.strip(), q.strip()))
        elif ln[:2] in ('T ', 'S ', 'Q ', 'E ', 'U ', 'C ', 'N ') and cur is not None: cur[ln[0]] = ln[2:].strip()
        else: sys.exit(f'{f.name} line {n} not understood: {ln[:70]}')
    fixed = [e['N'] for e in evs if e['N']]
    if any(not x.isdigit() or int(x) < 1 for x in fixed) or len(set(fixed)) != len(fixed):
        sys.exit(f'{f.name}: an "N" line (a fixed record number) is not a whole number above 0, or is given twice: {fixed}')
    return evs, checks


def load_log(f):
    """Return the log lines in file order. Columns: date, kind, saved id or "-", records after, text, hidden checks."""
    out = []
    for n, ln in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
        if not ln.strip() or ln.startswith('#'): continue
        c = ln.split('\t')
        if len(c) < 5 or c[1] not in LOGKINDS or not c[3].isdigit(): sys.exit(f'{f.name} line {n}: bad log line: {ln[:70]}')
        checks = []
        for part in [p.strip() for p in (c[5] if len(c) > 5 else '').split(';;') if p.strip()]:
            neg = 'word' if part.startswith('NOTWORD ') else part.startswith('NOT ')
            sid, words = [x.strip() for x in part[8 if neg == 'word' else 4 if neg else 0:].split('|', 1)]
            checks.append((neg, sid, words))
        out.append(dict(date=date.fromisoformat(c[0]), kind=c[1], sid=c[2].strip(), after=int(c[3]), text=c[4].strip(), checks=checks, line=n))
    return out


def numbers(text):
    """The numbers in one of our lines that a saved page must hold: not years, not chip names."""
    out = []
    for m in NUM.finditer(text):
        v = m.group(0).rstrip(',')
        if re.fullmatch(r'(19|20)\d\d', v) or CHIPNAME.search(text[:m.start()]): continue
        out.append(v)
    return out


def in_page(words, sid):
    """Like the checker, but without its length floor (for short numbers)."""
    q = L.squash(words)
    return bool(q) and q in L.page(sid)


def date_page(sid):
    """The saved page for the date screen: its text and bodies, without the fetch record and the address line."""
    d = L.P / sid; t = ''
    for n in ('text.txt', 'text.article.txt', 'transcription.txt'):
        if (d / n).exists(): t += ' ' + '\n'.join(x for x in (d / n).read_text(encoding='utf-8', errors='replace').splitlines() if not x.startswith(('FETCHED:', 'URL:')))
    for b in d.glob('body*'):
        if b.suffix.lower() in ('.html', '.htm', '.json', '.txt') and b.stat().st_size < 12_000_000:
            raw = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', b.read_text(encoding='utf-8', errors='replace'))
            t += ' ' + html.unescape(re.sub(r'(?s)<[^>]+>', ' ', raw))
    return L.squash(t)


def plain_page(sid):
    """The saved page as plain lower-case words with their spaces kept (the checker's own form has none), for whole-word checks."""
    d = L.P / sid; t = ''
    for n in ('text.txt', 'text.article.txt'):
        if (d / n).exists(): t += ' ' + (d / n).read_text(encoding='utf-8', errors='replace')
    for b in d.glob('body*'):
        if b.suffix.lower() in ('.html', '.htm') and b.stat().st_size < 12_000_000:
            raw = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', b.read_text(encoding='utf-8', errors='replace'))
            t += ' ' + html.unescape(re.sub(r'(?s)<[^>]+>', ' ', raw))
    return L.norm(t)


def whole_word(word, plain):
    return re.search(r'(?<![a-z0-9])' + re.escape(word.lower()) + r'(?![a-z0-9])', plain) is not None


def date_forms(d):
    m, M = MON[d.month - 1], MONTHS[d.month - 1]
    short = {m, M[:3], M[:3] + '.', m + '.'}
    forms = [d.isoformat(), f'{d.year}年{d.month}月{d.day}日', f'{d.year}年{d.month:02d}月{d.day:02d}日', f'{d.year}/{d.month:02d}/{d.day:02d}', f'{d.year}/{d.month}/{d.day}',
             f'{d.year}.{d.month:02d}.{d.day:02d}', f'{d.month:02d}/{d.day:02d}/{d.year}', f'{M} {d.day}, {d.year}', f'{M} {d.day} {d.year}', f'{d.day} {M} {d.year}', f'{d.day:02d} {M} {d.year}']
    for s in sorted(short): forms += [f'{s} {d.day}, {d.year}', f'{s} {d.day} {d.year}', f'{d.day} {s} {d.year}', f'{d.day:02d} {s} {d.year}']
    return forms


def date_in_page(d, sid):
    """'full' when the whole date is written in the page; 'month and day' when a Chinese page writes the month and day
    (4月25日) and the year elsewhere in it; None when neither. Only the page's readable text counts, not its markup."""
    p = date_page(sid)
    if any(L.squash(f) in p for f in date_forms(d)): return 'full'
    if re.search(rf'(?<!\d){d.month}月{d.day}日', p) and (f'{d.year}年' in p or f'{d.year}-' in p): return 'month and day'
    return None


def check_record(e, extra_ids=()):
    """Problems of one record, and its (saved id, words) pairs for quotes.tsv."""
    bad, pairs = [], []
    where = f"record {e['sid']} ({e['date']})"
    if not (e['T'] and e['S'] and e['Q']): return [f'{where}: incomplete (T, S and Q are needed)'], pairs
    if not (L.P / e['sid']).is_dir(): return [f"{where}: no saved copy named {e['sid']}"], pairs
    if not L.has(e['Q'], e['sid']): bad.append(f"{where}: the source's words were NOT FOUND in the saved copy: {e['Q'][:80]}")
    pairs.append((e['sid'], e['Q']))
    for q in QUOTE.findall(e['T']):
        if not L.has(q, e['sid']): bad.append(f'{where}: words between quote marks in our line were NOT FOUND in the saved copy: {q[:80]}')
        pairs.append((e['sid'], q))
    for q in QUOTE.findall(e['S'] + ' ' + e['E']): bad.append(f'{where}: quote marks in the source line or the English rendering (only a source\'s exact words go between them): {q[:60]}')
    for v in numbers(e['T']):
        if not in_page(v, e['sid']): bad.append(f'{where}: the number {v} in our line was NOT FOUND in the saved copy')
        elif len(L.squash(v)) >= 6: pairs.append((e['sid'], v))
        elif not any(sid == e['sid'] and L.squash(v) in L.squash(w) for sid, w in extra_ids): bad.append(f'{where}: the number {v} is too short for the checker; add a line "! {e["sid"]} | <words of the page that hold it>"')
    return bad, pairs


def verify(evs, checks, log):
    bad, pairs = [], []
    for e in evs:
        b, p = check_record(e, checks); bad += b; pairs += p
    for sid, q in checks:
        if not (L.P / sid).is_dir(): bad.append(f'"!" line: no saved copy named {sid}')
        elif not L.has(q, sid): bad.append(f'"!" line NOT FOUND in {sid}: {q[:80]}')
        pairs.append((sid, q))
    for g in log:
        where = f"log line {g['line']}"
        for q in QUOTE.findall(g['text']):
            if g['sid'] == '-': bad.append(f'{where}: a quotation needs a saved id in the third column: {q[:60]}'); continue
            if not L.has(q, g['sid']): bad.append(f"{where}: NOT FOUND in {g['sid']}: {q[:80]}")
            pairs.append((g['sid'], q))
        for neg, sid, words in g['checks']:
            if not (L.P / sid).is_dir(): bad.append(f'{where}: no saved copy named {sid}'); continue
            if neg == 'word':                              # a short word (a name of three letters) that must not stand in the page as a whole word
                p = plain_page(sid)
                if not whole_word('Nvidia', p): bad.append(f'{where}: the whole-word check cannot see words in {sid} (its control word was not found)')
                elif whole_word(words, p): bad.append(f'{where}: the word {words} must NOT stand in {sid}, and it does')
                continue
            found = L.has(words, sid)
            if neg and found: bad.append(f'{where}: words that must NOT be in {sid} were found: {words[:80]}')
            if not neg and not found: bad.append(f'{where}: hidden check NOT FOUND in {sid}: {words[:80]}')
            if not neg: pairs.append((sid, words))
    if L.has(*CONTROL): bad.append('control: the planted false quotation was found, so the check cannot fail')
    if not log: bad.append('the log is empty')
    elif log[-1]['after'] != len(evs): bad.append(f"the last log line says {log[-1]['after']} records; the data file holds {len(evs)}")
    for a, b in zip(log, log[1:]):
        if b['date'] < a['date']: bad.append(f"log line {b['line']}: its date is earlier than the line before it")
    return bad, pairs


def house(f):
    """Counts of the licence table the House Foreign Affairs Committee made public (a copy of tables/house_licence_table.tsv).
    Returns (values, problems)."""
    lines = [ln for ln in f.read_text(encoding='utf-8').splitlines() if ln.strip() and not ln.startswith('#')]
    head = lines[0].split('\t'); rows = [dict(zip(head, ln.split('\t'))) for ln in lines[1:]]
    bad = []
    for r in rows: r['n'] = int(r['chip_count'].replace(',', ''))
    st = lambda s: [r for r in rows if r['status'] == s]
    S = lambda rs: f"{sum(r['n'] for r in rs):,}"
    if {r['status'] for r in rows} != {'RWA', 'Approved, not shipped', 'Submitted', 'Rejected'}: bad.append(f'house table: unexpected statuses {sorted({r["status"] for r in rows})}')
    allc, rwa, appr = sum(r['n'] for r in rows), sum(r['n'] for r in st('RWA')), st('Approved, not shipped')
    cap = max(r['n'] for r in appr)
    sea = [r for r in rows if r['location'] in ('Malaysia', 'Indonesia', 'Thailand')]
    if any(r['status'] != 'RWA' for r in sea): bad.append('house table: an application for Malaysia, Indonesia or Thailand is not RWA')
    if any(r['status'] != 'RWA' for r in rows if r['n'] > cap): bad.append('house table: an application above the largest approved one is not RWA')
    ten = [r for r in rows if r['date_submitted'] == '12/19/2025' and r['exporter'] == 'Nvidia' and 'Tencent' in r['consignee']]
    if len(ten) != 1: bad.append(f'house table: {len(ten)} rows for Nvidia\'s application of Dec 19, 2025 for Tencent (one expected)')
    ten_any = [r for r in rows if r['date_submitted'] == '12/19/2025' and 'Tencent' in r['consignee']]
    if len(ten_any) != 1: bad.append(f'house table: {len(ten_any)} Tencent rows of Dec 19, 2025 from any exporter (the state of play says the table has only one)')
    if not L.has(f'export {TENCENT_FULL:,} H200s to Tencent', SUMMARY): bad.append('the summary does not give the Tencent application at the figure used here')
    tch = ten[0]['n'] if ten else 0
    v = dict(ALL=f'{allc:,}', ALL_N=str(len(rows)), RWA=f'{rwa:,}', RWA_N=str(len(st('RWA'))), RWA_PCT=f'{round(100 * rwa / allc)}%',
             APPR=S(appr), APPR_N=str(len(appr)), APPR_NV=S([r for r in appr if r['exporter'] == 'Nvidia']), APPR_NV_N=str(sum(r['exporter'] == 'Nvidia' for r in appr)),
             APPR_AMD=S([r for r in appr if r['exporter'] == 'AMD']), APPR_AMD_N=str(sum(r['exporter'] == 'AMD' for r in appr)),
             SUB=S(st('Submitted')), SUB_N=str(len(st('Submitted'))), REJ=S(st('Rejected')), REJ_N=str(len(st('Rejected'))),
             SEA=S(sea), CAP=f'{cap:,}', TENCENT_CHIPS=f'{tch:,}', TENCENT_STATUS=(ten[0]['status'].lower() if ten else '?'),
             ALT_PCT=f'{100 * rwa / (allc - tch + TENCENT_FULL):.1f}%',      # if the table's Tencent row is the committee's application of 445,000
             ALT_FURTHER_PCT=f'{100 * rwa / (allc + TENCENT_FULL):.1f}%')           # if the 445,000 is a further application, not in the table
    if sum(len(st(s)) for s in ('RWA', 'Approved, not shipped', 'Submitted', 'Rejected')) != len(rows): bad.append('house table: statuses do not add up')
    return v, bad


def fill(s, vals):
    out = re.sub(r'\{\{([A-Z_]+)\}\}', lambda m: vals.get(m.group(1), '{{' + m.group(1) + '}}'), s)
    return out


def raw_has(sid, words):
    """True when the words stand in a saved body as fetched, markup included (spacing, quote marks and case ignored)."""
    q = L.squash(words)
    return len(q) >= 6 and any(q in L.squash(b.read_text(encoding='utf-8', errors='replace')) for b in (L.P / sid).glob('body*') if b.stat().st_size < 12_000_000)


def load_state(f):
    st = dict(title='', sub='', src={}, groups=[])
    item = None
    for n, ln in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
        if not ln.strip() or ln.startswith('# '): continue
        if ln.startswith('@title '): st['title'] = ln[7:].strip()
        elif ln.startswith('@sub '): st['sub'] = ln[5:].strip()
        elif ln.startswith('@src '):
            p = [x.strip() for x in ln[5:].split('|')]
            st['src'][p[0]] = (p[1], p[2] if len(p) > 2 and p[2] else None)
        elif ln.startswith('## '): st['groups'].append((ln[3:].strip(), []))
        elif ln.startswith('- '):
            if not st['groups']: sys.exit(f'{f.name} line {n}: an item before any group heading')
            item = dict(text=ln[2:].strip(), checks=[], ours={}, line=n); st['groups'][-1][1].append(item)
        elif ln.startswith(('!! ', '!NOT ', '!RAW ', '!OURS ')) and item is not None:
            kind, rest = ln.split(' ', 1)
            a, b = [x.strip() for x in rest.split('|', 1)]
            if kind == '!OURS': item['ours'][a] = b
            else: item['checks'].append(({'!!': 'has', '!NOT': 'not', '!RAW': 'raw'}[kind], a, b))
        else: sys.exit(f'{f.name} line {n} not understood: {ln[:70]}')
    return st


def verify_state(st, vals):
    """Problems of the state of play, and its (saved id, words) pairs for quotes.tsv."""
    bad, pairs = [], []
    if not (st['title'] and st['groups']): bad.append('state of play: no title or no items')
    for heading, items in st['groups']:
        for it in items:
            where = f"state of play line {it['line']}"
            ids = CITE.findall(it['text'])
            for i in ids:
                if not (L.P / i).is_dir(): bad.append(f'{where}: no saved copy named {i}')
                if i not in st['src']: bad.append(f'{where}: [{i}] has no @src label')
            text = fill(it['text'], vals)
            if '{{' in text: bad.append(f'{where}: a count is not known: {text[text.index("{{"):][:30]}')
            quotes = QUOTE.findall(text)
            words = quotes + [fill(w, vals) for k, _, w in it['checks'] if k in ('has', 'raw')]
            plain = DATE_RX.sub(' ', CITES.sub(' ', re.sub(r'\{\{[A-Z_]+\}\}', ' ', it['text'])))
            for q in QUOTE.findall(plain): plain = plain.replace(f'"{q}"', ' ')
            for v in numbers(plain):
                if v in it['ours']: continue
                if not any(L.squash(v) in L.squash(w) for w in words): bad.append(f'{where}: the number {v} stands in no quotation or hidden check of its item')
            for q in quotes:
                hit = next((i for i in ids if L.has(q, i)), None)
                if hit: pairs.append((hit, q))
                else: bad.append(f'{where}: NOT FOUND in {", ".join(ids) or "(no id cited)"}: {q[:80]}')
            for k, sid, w in it['checks']:
                w = fill(w, vals)
                if not (L.P / sid).is_dir(): bad.append(f'{where}: no saved copy named {sid}'); continue
                if k == 'has':
                    if L.has(w, sid): pairs.append((sid, w))
                    else: bad.append(f'{where}: hidden check NOT FOUND in {sid}: {w[:80]}')
                elif k == 'not':
                    if len(L.squash(w)) < 6: bad.append(f'{where}: a negative check under 6 characters cannot fail: {w}')
                    elif L.has(w, sid): bad.append(f'{where}: words that must NOT be in {sid} were found: {w[:80]}')
                elif not raw_has(sid, w): bad.append(f'{where}: NOT FOUND in the saved body of {sid}: {w[:80]}')
            it['shown'] = text
    return bad, pairs


def state_html(st):
    def cite(m):
        links = []
        for i in CITE.findall(m.group(0)):
            label, addr = st['src'][i]
            u = addr or L.url_of(i)
            links.append(f'<a class="cite" href="{esc(u, quote=True)}" rel="noopener">{esc(label)}</a>' if u else esc(label))
        return '\0(' + '; '.join(links) + ')\0'
    out = [f' <h2>{esc(st["title"])}</h2>', f' <p class="sub">{esc(smart(st["sub"]))}</p>']
    for heading, items in st['groups']:
        out.append(f' <h3 class="sg">{esc(heading)}</h3>\n <ul class="sp">')
        for it in items:
            parts = CITES.sub(cite, smart(it['shown'])).split('\0')
            out.append('  <li>' + ''.join(p if i % 2 else esc(p) for i, p in enumerate(parts)) + '</li>')      # odd parts: the links, escaped above
        out.append(' </ul>')
    return '\n'.join(out)


def key_of(e): return f"r-{e['sid']}-{e['lane'].lower()}"


CSS = """
:root { --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#7a7872; --grid:#e1e0d9; --axis:#c3c2b7;
  --border:rgba(11,11,11,0.12); --wash:rgba(11,11,11,0.045); --toward:#256abf; --away:#c44e18; --link:#1c5cab;
  --font-text:"Inter",system-ui,-apple-system,"Segoe UI","Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif; --font-head:"Space Grotesk","Inter",system-ui,sans-serif; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --page:#0d0d0d; --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#8f8d86;
  --grid:#2c2c2a; --axis:#45453f; --border:rgba(255,255,255,0.14); --wash:rgba(255,255,255,0.06); --toward:#3987e5; --away:#d95926; --link:#86b6ef; color-scheme:dark } }
:root[data-theme="dark"] { --page:#0d0d0d; --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#8f8d86; --grid:#2c2c2a; --axis:#45453f;
  --border:rgba(255,255,255,0.14); --wash:rgba(255,255,255,0.06); --toward:#3987e5; --away:#d95926; --link:#86b6ef; color-scheme:dark }
* { box-sizing:border-box; } html { -webkit-text-size-adjust:100%; scroll-behavior:smooth; }
body { margin:0; background:var(--page); color:var(--ink); font-family:var(--font-text); font-size:16px; line-height:1.5; }
a { color:var(--link); }
.wrap { max-width:900px; margin:0 auto; padding:30px 16px 56px; }
.eyebrow { font:700 12px/1.2 var(--font-text); letter-spacing:0.1em; text-transform:uppercase; color:var(--muted); margin:0 0 12px; }
h1 { font-family:var(--font-head); font-size:clamp(27px,4.6vw,42px); line-height:1.08; letter-spacing:-0.015em; margin:0 0 12px; text-wrap:balance; }
.deck { margin:0 0 10px; color:var(--ink2); font-size:18px; line-height:1.45; }
.note { margin:0 0 4px; color:var(--muted); font-size:13.5px; line-height:1.45; }
.key { display:grid; grid-template-columns:1fr; gap:8px 26px; margin:18px 0 0; padding:0; list-style:none; font-size:14.5px; color:var(--ink2); }
@media (min-width: 700px) { .key { grid-template-columns:1fr 1fr; } }
.key li { display:flex; align-items:flex-start; gap:9px; } .key b { color:var(--ink); font-weight:600; }
.key .m { margin-top:3px; }
.m { display:inline-block; flex:none; width:15px; height:15px; border-radius:50%; border:2.5px solid; }
.m.toward { border-color:var(--toward); } .m.away { border-color:var(--away); }
.m.open { background:var(--surface); } .m.solid.toward { background:var(--toward); } .m.solid.away { background:var(--away); }
.card { background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:20px 22px; margin-top:16px; min-width:0; }
@media (max-width: 520px) { .card { padding:16px 14px; } }
.card h2 { font-family:var(--font-head); font-size:22px; line-height:1.2; margin:0 0 4px; text-wrap:balance; }
.card .sub { margin:0 0 10px; color:var(--ink2); font-size:14.5px; }
ol.log, ol.recs { list-style:none; margin:0; padding:0; }
ol.log li { display:grid; grid-template-columns:104px 1fr; gap:4px 14px; padding:10px 0; border-top:1px solid var(--grid); font-size:14.5px; line-height:1.45; }
@media (max-width: 520px) { ol.log li { grid-template-columns:1fr; } }
.lw { font-weight:700; font-size:13px; white-space:nowrap; } .lw .tag { display:block; margin-top:5px; width:max-content; }
@media (max-width: 520px) { .lw .tag { display:inline-block; margin:0 0 0 8px; } }
.tag { font:700 10.5px/1 var(--font-text); letter-spacing:0.06em; text-transform:uppercase; padding:3px 6px; border-radius:5px; background:var(--wash); color:var(--ink2); }
.cnt { color:var(--muted); font-size:13px; }
.who { margin:0; padding:0; list-style:none; font-size:14.5px; color:var(--ink2); } .who li { padding:7px 0; border-top:1px solid var(--grid); } .who b { color:var(--ink); font-weight:600; }
h3.yr { font:700 13px/1 var(--font-text); letter-spacing:0.08em; text-transform:uppercase; color:var(--muted); margin:22px 0 8px; }
h3.yr span { font-weight:500; letter-spacing:0.02em; text-transform:none; }
li.rec { display:grid; grid-template-columns:17px 1fr; gap:12px; padding:12px 6px; border-top:1px solid var(--grid); border-radius:6px; scroll-margin-top:14px; }
li.rec:target { background:var(--wash); }
li.rec .m { margin-top:3px; }
li.rec > div { min-width:0; overflow-wrap:anywhere; }
.top { margin:0 0 3px; font-size:13px; color:var(--ink2); display:flex; flex-wrap:wrap; gap:2px 12px; align-items:baseline; }
.when { font-weight:700; color:var(--ink); white-space:nowrap; }
.what { margin:0 0 5px; font-size:16px; line-height:1.4; font-weight:500; }
.q { margin:0 0 4px; font-size:14.5px; line-height:1.45; color:var(--ink2); padding-left:10px; border-left:2px solid var(--axis); }
.q .ql { font:700 10.5px/1 var(--font-text); letter-spacing:0.06em; text-transform:uppercase; color:var(--muted); display:block; margin-bottom:3px; }
.src { margin:0; font-size:13px; color:var(--muted); }
.notes ul { margin:6px 0 0; padding-left:20px; color:var(--ink2); font-size:14.5px; } .notes li { margin:5px 0; }
.state h3.sg { font:700 12.5px/1.2 var(--font-text); letter-spacing:0.08em; text-transform:uppercase; color:var(--muted); margin:18px 0 4px; }
.state ul.sp { margin:0; padding-left:20px; font-size:15.5px; line-height:1.5; } .state ul.sp li { margin:8px 0; overflow-wrap:anywhere; }
a.cite { font-size:13.5px; }
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chip Policy Tracker</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap">
<style>%%CSS%%</style>
</head>
<body>
<div class="wrap">
<header>
 <p class="eyebrow">China · Nvidia chips · the dated record, kept up to date</p>
 <h1>Beijing mostly pulled one way on Nvidia chips. Its AI companies pulled the other.</h1>
 <p class="deck">%%N%% dated records of what Chinese authorities did about Nvidia’s chips and what China’s big AI companies did, newest first, under the state of play and a dated log. The exceptions on each side are listed too: Beijing sometimes let chips in, and the companies also turned to home-made ones.</p>
 <p class="note">Draft by Claude, Anthropic’s model. Last entry in the log: %%LAST%%.</p>
 <ul class="key">
  <li><i class="m away solid"></i><span><b>Orange, away from Nvidia:</b> holding it back, or choosing home-made chips. %%N_AWAY%% records</span></li>
  <li><i class="m toward solid"></i><span><b>Blue, toward Nvidia:</b> buying it, using it, letting it in. %%N_TOWARD%% records</span></li>
  <li><i class="m toward solid"></i><i class="m away solid"></i><span><b>Filled:</b> on the record (a government document, a filing, a named person). %%N_SOLID%% records</span></li>
  <li><i class="m toward open"></i><i class="m away open"></i><span><b>Open:</b> a press report citing unnamed people. %%N_OPEN%% records</span></li>
 </ul>
</header>
<section class="card state" id="state">
%%STATE%%
</section>
<section class="card" id="log">
 <h2>Log of additions and corrections</h2>
 <p class="sub">Newest first. Each entry gives the day it was written, its kind, and how many records the list held after it.</p>
 <ol class="log">
%%LOG%%
 </ol>
</section>
<section class="card" id="who">
 <h2>Who is who</h2>
 <ul class="who">
  <li><b>Beijing</b> stands for the leaders and bodies of the Chinese state named in the records: Xi Jinping, Premier Li Qiang, Vice Premiers He Lifeng and Ding Xuexiang; the cyberspace regulator (Cyberspace Administration of China) and its review office; the state planner (National Development and Reform Commission, NDRC); the market regulator (State Administration for Market Regulation); the commerce, finance, industry and security ministries; customs; and the state’s evaluation centre for information security. State media and the Party’s journal speak in some records too. Two universities’ notices to buy Nvidia cards stand in the row of Beijing letting Nvidia in: the notices hold suppliers to the government procurement law’s conditions, and no saved page calls the universities state bodies.</li>
  <li><b>The companies</b> are the Chinese AI companies named in the records: Alibaba, Baidu, ByteDance, Tencent, DeepSeek, Zhipu, iFlytek and 360. A Shanghai government body’s account of what the city’s internet companies use stands in their row.</li>
  <li><b>American officials</b> appear where they speak of Beijing: the Commerce Secretary, Howard Lutnick, at a Senate hearing, and Jeffrey Kessler at a House hearing.</li>
  <li><b>The chips</b> are Nvidia’s. The models named in the records include the H20, the RTX Pro 6000D and the H200. Home-made chips are those of Chinese makers, among them Huawei, Alibaba’s T-Head unit and Baidu.</li>
 </ul>
</section>
<section class="card" id="records">
 <h2>The record, newest first</h2>
 <p class="sub">The date is the date of the act where the saved page states it, otherwise the date of the report. Each line in larger type is our summary. Under it stand the source’s own words, found in the saved copy by a script, and a link to the page.</p>
%%RECORDS%%
</section>
<section class="card notes">
 <h2>Read with care</h2>
 <ul>
  <li>Open marks rest on unnamed people. What they say Beijing told companies is reported, not published policy.</li>
  <li>No published Chinese order against buying Nvidia chips was found in the 82 policy pages read. The published acts against Nvidia that were found are a summons and an antitrust case.</li>
  <li>The records are a selection made to show both sides, not a census. The number of records on a side is not a measure.</li>
  <li>A quotation that is found shows what the source says, not that it is true.</li>
  <li>The state of play is written on its date from the saved sources; it does not update itself. Its counts of the licence table that the House Foreign Affairs Committee made public are a script’s sums of the table’s rows, and they add Nvidia’s and AMD’s chips together.</li>
  <li>Caption tracks and machine transcripts have not been checked by ear; where one is quoted, the time in the recording is given.</li>
  <li>English in round brackets after Chinese is our rendering, not an official translation.</li>
  <li>%%DATENOTE%%</li>
 </ul>
</section>
</div>
</body>
</html>
"""


def rec_html(e):
    who, what, dr = LANES[e['lane']]
    solid = e['kind'] != 'press'
    url = e['U'] or L.url_of(e['sid'])
    src = f'<a href="{esc(url, quote=True)}" rel="noopener">{esc(smart(e["S"]))}</a>' if url else esc(smart(e['S']))
    q = f'“{esc(e["Q"])}”' + (f' ({esc(e["E"])})' if e['E'] else '')
    return (f'<li class="rec" id="{esc(key_of(e), quote=True)}"><i class="m {dr} {"solid" if solid else "open"}" title="{esc(KINDS[e["kind"]], quote=True)}"></i><div>'
            f'<p class="top"><span class="when">{esc(e["dl"] or fmt(e["date"]))}</span><span>{esc(who)} · {esc(what)}</span><span>{esc(KINDS[e["kind"]])}</span></p>'
            f'<p class="what">{esc(smart(e["T"]))}</p>'
            f'<p class="q"><span class="ql">The source’s words</span>{q}</p>'
            f'<p class="src">{src}</p></div></li>')


def log_html(g, anchors):
    link = f' <a href="#{esc(anchors[g["sid"]], quote=True)}">See the record</a>.' if g['sid'] in anchors else ''
    plural = 's' if g['after'] != 1 else ''
    return (f'  <li><div class="lw">{esc(fmt(g["date"]))}<span class="tag">{esc(LOGKINDS[g["kind"]])}</span></div>'
            f'<div>{esc(smart(g["text"]))}{link} <span class="cnt">{g["after"]} record{plural} after this entry.</span></div></li>')


def build(folder, quiet=False):
    """Check and build one tracker folder. Returns (ok, lines to print)."""
    data, logf = folder / 'data' / 'figure_data.txt', folder / 'data' / 'tracker_log.tsv'
    evs, checks = load_data(data)
    log = load_log(logf)
    bad, pairs = verify(evs, checks, log)
    vals, hb = house(folder / 'data' / 'house_licence_table.tsv')
    st = load_state(folder / 'data' / 'state_of_play.txt')
    sb, sp = verify_state(st, vals)
    bad += hb + sb; pairs += sp
    out = []
    if bad: return False, bad + [f'NOT WRITTEN: {len(bad)} problem(s)']
    seen, lines = set(), ['# Every quotation, number and hidden check the tracker page rests on. Written by build.py; do not edit.',
                          '# saved id <TAB> words that stand in the saved copy (research/primary/<id>)']
    for sid, w in pairs:
        if (sid, w) not in seen: seen.add((sid, w)); lines.append(f'{sid}\t{w}')
    (folder / 'quotes.tsv').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    r = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts' / 'cn_has.py'), str(folder / 'quotes.tsv')], capture_output=True, text=True)
    tail = (r.stdout.strip().splitlines() or ['(no output)'])[-1]
    out.append(f'cn_has.py on quotes.tsv: exit {r.returncode}: {tail}')
    if r.returncode != 0: return False, out + r.stdout.strip().splitlines()[:-1] + [r.stderr.strip(), 'NOT WRITTEN: cn_has.py failed']
    order = sorted(range(len(evs)), key=lambda i: (-evs[i]['date'].toordinal(), i))
    recs, year = [], None
    per_year = {}
    for e in evs: per_year[e['date'].year] = per_year.get(e['date'].year, 0) + 1
    for i in order:
        e = evs[i]
        if e['date'].year != year:
            if year is not None: recs.append(' </ol>')
            year = e['date'].year
            recs.append(f' <h3 class="yr">{year} <span>· {per_year[year]} record{"s" if per_year[year] != 1 else ""}</span></h3>\n <ol class="recs">')
        recs.append('  ' + rec_html(e))
    recs.append(' </ol>')
    anchors = {}
    for e in evs: anchors.setdefault(e['sid'], key_of(e))
    screen = [(e, None if e['dl'] else date_in_page(e['date'], e['sid'])) for e in evs]
    labelled = [f"{e['sid']} ({e['dl']})" for e, r in screen if e['dl']]
    partly = [f"{e['sid']} ({e['date']})" for e, r in screen if r == 'month and day']
    nodate = [f"{e['sid']} ({e['date']})" for e, r in screen if not e['dl'] and r is None]
    n_full = sum(r == 'full' for _, r in screen)
    plural = lambda n, w: f'{n} {w}' + ('' if n == 1 else 's')
    datenote = (f'A script looked for each record’s date in the readable text of its saved page. It found {n_full} in full and {len(partly)} by month and day, with the year elsewhere in the page. '
                f'{plural(len(labelled), "record")} {"carries" if len(labelled) == 1 else "carry"} a label instead of a day. ')
    missing = [f'<a href="#{esc(key_of(e), quote=True)}">{esc(fmt(e["date"]))}</a> ({esc(smart(e["S"]))})' for e, r in screen if not e['dl'] and r is None]
    datenote += ('It did not find ' + '; '.join(missing) + '. Check such a date against the page before quoting it.') if missing else 'None was missing.'
    n_solid = sum(e['kind'] != 'press' for e in evs)
    n_away = sum(LANES[e['lane']][2] == 'away' for e in evs)
    parts = {'CSS': CSS, 'N': str(len(evs)), 'LAST': fmt(log[-1]['date']), 'N_SOLID': str(n_solid), 'N_OPEN': str(len(evs) - n_solid),
             'N_AWAY': str(n_away), 'N_TOWARD': str(len(evs) - n_away), 'DATENOTE': datenote, 'STATE': state_html(st),
             'LOG': '\n'.join(log_html(g, anchors) for g in reversed(log)), 'RECORDS': '\n'.join(recs)}
    page = PAGE
    for k, v in parts.items():
        assert f'%%{k}%%' in page, k
        page = page.replace(f'%%{k}%%', v)
    assert '%%' not in page, page[page.index('%%'):][:40]
    (folder / 'tracker.html').write_text(page, encoding='utf-8')
    per = {k: sum(e['lane'] == k for e in evs) for k in LANES}
    out.append(f'records {len(evs)} ({per}); on the record {n_solid}, press reports {len(evs) - n_solid}; log lines {len(log)}; '
               f'checked {len(seen)} strings (quotations, numbers, hidden checks), all found; control not found (as it must be)')
    n_items = sum(len(items) for _, items in st['groups'])
    out.append(f'state of play: {n_items} items in {len(st["groups"])} groups; {len(sp)} quotations and hidden checks found, '
               f'{sum(k == "not" for _, items in st["groups"] for it in items for k, _, _ in it["checks"])} negative checks not found (as they must not be), '
               f'{sum(k == "raw" for _, items in st["groups"] for it in items for k, _, _ in it["checks"])} found in a saved body\'s markup; House table counted: '
               f'{vals["ALL"]} chips in {vals["ALL_N"]} rows, returned without action {vals["RWA"]} ({vals["RWA_PCT"]}), approved {vals["APPR"]} in {vals["APPR_N"]}')
    out.append(f'date screen: of {len(evs)} record dates, {n_full} are written in full in the readable text of their saved pages; '
               f'{len(partly)} by month and day with the year elsewhere in the page ({"; ".join(partly) or "none"}); '
               f'{len(labelled)} carry a label instead of a day ({"; ".join(labelled) or "none"}); not found: {"; ".join(nodate) or "none"}')
    out.append(f'written {folder / "tracker.html"} ({len(page.encode("utf-8"))} bytes) and {folder / "quotes.tsv"}')
    return True, out


def main():
    args = sys.argv[1:]
    folder = HERE
    if '--dir' in args:
        i = args.index('--dir'); folder = Path(args[i + 1]).resolve(); del args[i:i + 2]
    if args: sys.exit(__doc__)
    ok, lines = build(folder)
    print('\n'.join(x for x in lines if x))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
