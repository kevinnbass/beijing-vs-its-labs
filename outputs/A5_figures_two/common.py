"""Shared parts of the five figures in this folder (China chip-policy project, outputs A5).

Each figure has its own folder with:  data.txt (the records, with the sources' own words)   build.py (reads data.txt)
                                       quotes.tsv (written by build.py from data.txt, then checked by scripts/cn_has.py)
                                       <name>.html, <name>.png, records.tsv (build products)
A build writes nothing but quotes.tsv until scripts/cn_has.py has found every line of it in the saved copies.

data.txt, one block per record:
  @ KEY KIND DATE DATELABEL SAVED-ID [name=value ...]
      KIND   doc   a government document, or an official on the record            (filled mark)
             rec   a company on the record: a filing, a results call, a named person (filled mark)
             pub   a published commentary, report or statement of state media, an industry body or a research institute (filled mark)
             acct  a named newspaper's account of a state document                 (filled mark)
             press a press report citing unnamed people                           (open mark)
             count a research firm's count, as reported by the press              (open mark)
             caps  captions of a broadcast, not checked by ear                    (open mark)
      DATE   YYYY-MM-DD, used for the order; DATELABEL "-" prints that date, otherwise the words given (_ for a space)
  T  the short label drawn beside the mark (our words)
  L  the line in the list of records (our words; straight double quotes only around a source's exact words)
  S  the source as shown
  Q  the page's own words (checked)          E  our English for the Q line above it (Chinese sources)
  D  words in the page that give the date (checked); "D other-id | words" when another saved copy carries the date.
     A record of captions has no date in its text: its record line carries upload=<saved id of the video's page>, and
     the loader reads the upload date in that page's saved body and requires it to equal DATE.
  N  a number-bearing phrase in the page that backs a number we show (checked); "N other-id | words" likewise
  V  a number the builder draws: "V name=number | words in the page that carry it" (checked; the number must be in the words)
Lines starting "#" are comments. Lines starting "! " are further checked phrases outside any record: ! SAVED-ID | words
"""
import html, json, re, subprocess, sys
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
NV = HERE.parents[3]                                   # .
PROJ = HERE.parents[1]                                 # research/cn_chip_policy_20261120
sys.path.insert(0, str(NV / 'scripts'))
import cn_srclib as L                                  # noqa: E402
import cn_argument_build as B                          # noqa: E402  (address(), load_refs(), load_clip(); importing it runs nothing)

MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
SOLID = ('doc', 'rec', 'pub', 'acct')
KIND_WORDS = {'doc': 'On the record: a government document or an official', 'rec': 'On the record: a filing or a named person',
              'pub': 'On the record: ' + B.KIND['PUB'],
              'acct': 'On the record: a named newspaper’s account of a state document',
              'press': 'Press report citing unnamed people', 'count': "A research firm's count, through the press",
              'caps': 'Captions, not checked by ear'}
NOTE = 'Draft by Claude, Anthropic’s model.'   # round 10, the session's ruling: nothing about being local or unpublished (untrue of a public copy)
esc = html.escape
WORDS = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
         11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen', 15: 'fifteen'}
TB = PROJ / 'tables'


def table(name):
    """Rows of a tab-separated table in the project's tables folder, as dicts (lines starting # are comments)."""
    lines = [l for l in (TB / name).read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    head = lines[0].split('\t')
    return [dict(zip(head, l.split('\t'))) for l in lines[1:]]


def state_media_summary():
    """Count the later state-media series by stance, subject and warning window."""
    rows = table('state_media_items.tsv')
    stances = Counter(r['stance'] for r in rows)
    subjects = Counter(r['subject'] for r in rows)
    assert stances == {'neutral': 126, 'self-reliance': 74, 'warns': 34,
                       'welcomes': 28, 'other': 21, 'mixed': 14}, stances
    assert subjects == {'chips for AI computing': 219, 'a product with an Nvidia chip': 40,
                        'other': 30, 'Nvidia as a company': 8}, subjects

    dates = sorted(date.fromisoformat(r['date']) for r in rows)
    warning_rows = [r for r in rows if r['stance'] == 'warns']
    warns = sorted(date.fromisoformat(r['date']) for r in warning_rows)
    burst = [d for d in warns if date(2025, 7, 31) <= d <= date(2025, 9, 24)]
    winter = [d for d in warns if date(2025, 12, 9) <= d <= date(2026, 1, 14)]
    other_warnings = Counter(warns) - Counter(burst) - Counter(winter)
    assert dates[0] == date(2025, 7, 1) and dates[-1] == date(2026, 11, 25), (dates[0], dates[-1])
    assert (len(rows), len(burst), len(winter), sum(other_warnings.values())) == (297, 23, 6, 5)
    assert other_warnings == Counter(date.fromisoformat(s) for s in (
        '2025-07-24', '2025-11-01', '2026-03-03', '2026-03-18', '2026-11-06')), other_warnings

    mixed_later = sum(r['stance'] == 'mixed' and r['date'] > '2025-09-30' for r in rows)
    ai_warnings = [r for r in warning_rows if r['subject'] == 'chips for AI computing']
    other_topics = [r for r in warning_rows if r['subject'] != 'chips for AI computing']
    burst_dates = {d.isoformat() for d in burst}
    ai_burst = sum(r['date'] in burst_dates for r in ai_warnings)
    assert (mixed_later, len(ai_warnings), ai_burst) == (10, 33, 22)
    assert [(r['saved_id'], r['subject'], r['date']) for r in other_topics] == [
        ('cn-media-stdaily-security-forum', 'other', '2025-09-24')
    ], other_topics
    start, end = [f'{MON[d.month - 1]} {d.year}' for d in (dates[0], dates[-1])]
    summary = (
        f'The project’s state-media table lists {len(rows)} items found from {start} to {end}. '
        f'{subjects["chips for AI computing"]} cover chips for AI computing. A separate '
        f'{subjects["a product with an Nvidia chip"]} cover products with an Nvidia chip. '
        f'{len(warns)} items only warn. {len(ai_warnings)} concern chips for AI computing. '
        f'The other is a forum report about home-made software and hardware at large. '
        f'{len(burst)} of these warnings date from {fmt(burst[0])} to {fmt(burst[-1])}, including {ai_burst} about the chips. '
        f'{len(winter)} date from {fmt(winter[0])} to {fmt(winter[-1])}, during coverage of US easing for the H200. '
        f'{stances["mixed"]} other items mix a warning with a welcome, {mixed_later} after September 2025. '
        f'After {fmt(burst[-1])}, the items are a sample from searches and a scan of the saved pages.'
    )
    return rows, summary


def upload_date(sid):
    """The upload date a saved video page gives in its own data (the checker does not read a page's scripts)."""
    b = (L.P / sid / 'body.html').read_text(encoding='utf-8', errors='replace')
    found = set(re.findall(r'"uploadDate":"(\d{4}-\d\d-\d\d)T', b))
    assert len(found) == 1, (sid, found)
    return date.fromisoformat(found.pop())


def figure_checks():
    """The core figure's own checked lines (figure/figure_data.txt): saved id -> the words its builder finds there."""
    out = {}
    for ln in (PROJ / 'figure' / 'figure_data.txt').read_text(encoding='utf-8').splitlines():
        if ln.startswith('! '):
            sid, q = ln[2:].split(' | ', 1); out.setdefault(sid.strip(), []).append(q.strip())
    return out


def core_literal(func, name):
    """A list written out in the core figure's builder (scripts/cn_figure_build.py), read without running it: the
    value assigned to `name` inside function `func`. Used so that rows the core lists by hand are not typed again here."""
    import ast
    tree = ast.parse((NV / 'scripts' / 'cn_figure_build.py').read_text(encoding='utf-8'))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == func)
    asg = [n for n in ast.walk(fn) if isinstance(n, ast.Assign) and len(n.targets) == 1 and getattr(n.targets[0], 'id', '') == name]
    assert len(asg) == 1, (func, name, len(asg))
    return ast.literal_eval(asg[0].value)


def smart(s):
    """Straight double quotes become curly ones; an apostrophe becomes a typographic one."""
    return re.sub(r'"([^"]*)"', '“\\1”', s).replace("'", '’')


def T(s):
    """Our own words, made safe for HTML."""
    return esc(smart(s), quote=False)


def fmt(d):
    return f'{MON[d.month - 1]} {d.day}, {d.year}'


# ---------- data ----------
def load(path):
    """Return (records, extra checks). A record is a dict; Q is a list of [words, our English or '']."""
    recs, extra, cur = [], [], None
    for n, ln in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        if not ln.strip() or ln.startswith('#'): continue
        if ln.startswith('@ '):
            p = ln.split()
            if len(p) < 6: sys.exit(f'{path} line {n}: a record line needs KEY KIND DATE DATELABEL SAVED-ID')
            key, kind, d, dl, sid = p[1:6]
            if kind not in KIND_WORDS: sys.exit(f'{path} line {n}: kind {kind}')
            cur = dict(key=key, kind=kind, date=date.fromisoformat(d), sid=sid, T='', L='', S='', Q=[], D=[], N=[], V={}, line=n)
            cur['when'] = fmt(cur['date']) if dl == '-' else dl.replace('_', ' ')
            for kv in p[6:]:
                k, v = kv.split('=', 1); cur[k] = v.replace('_', ' ')
            cur['solid'] = kind in SOLID
            if any(r['key'] == key for r in recs): sys.exit(f'{path} line {n}: key {key} twice')
            recs.append(cur)
        elif ln.startswith('! '):
            sid, q = ln[2:].split(' | ', 1); extra.append((sid.strip(), q.strip()))
        elif ln[:2] in ('T ', 'L ', 'S '):
            cur[ln[0]] = ln[2:].strip()
        elif ln.startswith('Q '):
            cur['Q'].append([ln[2:].strip(), ''])
        elif ln.startswith('E '):
            if not cur['Q'] or cur['Q'][-1][1]: sys.exit(f'{path} line {n}: an E line must follow its Q line')
            cur['Q'][-1][1] = ln[2:].strip()
        elif ln.startswith('V '):                      # a number the builder draws, with the page's words that carry it
            name, rest = ln[2:].split('=', 1); num, words = [x.strip() for x in rest.split(' | ', 1)]
            if not re.search(r'(?<![\d.,])' + re.escape(num) + r'(?![\d]|[.,]\d)', words): sys.exit(f'{path} line {n}: the number {num} is not written in its words')
            plain = num.replace(',', '')
            cur['V'][name.strip()] = float(plain) if '.' in plain else int(plain); cur['N'].append((cur['sid'], words))
        elif ln[:2] in ('D ', 'N '):
            body = ln[2:].strip()
            sid, q = [x.strip() for x in body.split(' | ', 1)] if ' | ' in body else (cur['sid'], body)
            cur[ln[0]].append((sid, q))
        else:
            sys.exit(f'{path} line {n} not understood: {ln[:70]}')
    for r in recs:
        if r.get('upload'):                          # captions: the date is the video page's own upload date
            if upload_date(r['upload']) != r['date']: sys.exit(f"{path} line {r['line']}: {r['key']}: the video page gives another upload date")
        elif not r['D']: sys.exit(f"{path} line {r['line']}: record {r['key']} needs a D line")
        if not (r['L'] and r['S'] and r['Q']): sys.exit(f"{path} line {r['line']}: record {r['key']} needs L, S and Q lines")
    return recs, extra


def checked_lines(recs, extra):
    """Every string the page relies on: (saved id, words), in file order, without repeats."""
    out = []
    for r in recs:
        out += [(r['sid'], q) for q, _ in r['Q']] + list(r['D']) + list(r['N'])
    out += list(extra)
    seen, uniq = set(), []
    for x in out:
        if x not in seen: seen.add(x); uniq.append(x)
    return uniq


def write_and_check_quotes(folder, lines, head):
    """Write quotes.tsv and run the project's checker on it. Stops the build when the checker does not exit 0."""
    f = Path(folder) / 'quotes.tsv'
    f.write_text(f'# {head}\n# Written by build.py from data.txt; checked by scripts/cn_has.py. Columns: saved id, tab, the source\'s exact words.\n'
                 + ''.join(f'{sid}\t{q}\n' for sid, q in lines), encoding='utf-8')
    r = subprocess.run([sys.executable, '-I', str(NV / 'scripts' / 'cn_has.py'), str(f)], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    print('cn_has.py:', out.splitlines()[-1] if out else '(no output)')
    if r.returncode != 0:
        print(out); sys.exit('cn_has.py did not pass: no page written')
    return out.splitlines()[-1]


def page_quotes_ok(page, lines):
    """Every string between curly quotes in the page's visible text must be part of a checked line."""
    B.load_clip()
    body = re.sub(r'(?is)<(script|style|title)\b.*?</\1>', ' ', page)
    text = html.unescape(re.sub(r'(?s)<[^>]+>', ' ', body))
    pool = [L.squash(q) for _, q in lines]
    bad = []
    for q in re.findall(r'“([^”]*)”', text):
        for part in [x for x in q.split(' ... ') if x.strip()]:
            s = L.squash(part)
            if not s or not any(s in p for p in pool): bad.append(part)
    if '"' in text: bad.append('a straight double quote is left in the visible text')
    if bad: sys.exit('quotation marks around words that are not in quotes.tsv: ' + ' | '.join(bad[:8]))
    return len(re.findall(r'“', text))


def number(recs, order=None):
    """Give each record its number (file order unless a key function is given), its address and its tooltip text."""
    refs = B.load_refs()
    for i, r in enumerate(sorted(recs, key=order) if order else recs, 1):
        r['n'] = i
        r['url'] = r.get('U') or B.address(r['sid'], refs.get(r['sid'], {'addr': ''})) or ''
    return sorted(recs, key=lambda r: r['n'])


def tips(recs, where):
    """Tooltip data: when, where it sits, our line, the page's words, the source, the kind."""
    out = {}
    for r in recs:
        q, e = r['Q'][0]
        out[r['n']] = dict(w=r['when'], l=where(r), t=smart(r['L']), q=inner_quotes(q), e=e, s=smart(r['S']), k=KIND_WORDS[r['kind']])
    return json.dumps(out, ensure_ascii=False).replace('</', '<\\/')


# ---------- pieces of a page ----------
def pin(r):
    return f'<i class="p {r["dir"]} {"solid" if r["solid"] else "hollow"}">{r["n"]}</i>'


def mark(r, tag=None):
    """A numbered mark with its date and short label; links to the record below and shows the source's words on hover."""
    lab = f'{r["n"]}. {r["when"]}: {smart(r["T"] or r["L"])}. {KIND_WORDS[r["kind"]]}'
    return (f'<a class="mk" href="#r{r["n"]}" data-n="{r["n"]}" data-tip="1" aria-label="{esc(lab, quote=True)}">{pin(r)}'
            f'<span class="mt"><b>{esc(r["when"])}</b> <span>{T(tag if tag is not None else r["T"])}</span></span></a>')


def inner_quotes(q):
    """Quote marks inside a quotation are shown as single ones and apostrophes as typographic ones (the checker ignores the style of quote marks)."""
    return q.replace('“', '‘').replace('”', '’').replace('"', '’').replace("'", '’').replace('ʼ', '’')


def quote_html(r, skip_in=''):
    """The page's own words, with our English after Chinese; a quotation the summary line already carries is not repeated."""
    out, had = [], L.squash(skip_in)
    for q, e in r['Q']:
        if had and L.squash(q) in had: continue
        out.append(f'“{esc(inner_quotes(q), quote=False)}”' + (f' ({T(e)})' if e else ''))
    return '; '.join(out)


def record_li(r, lead=''):
    src = f'<a href="{esc(r["url"], quote=True)}">{T(r["S"])}</a>' if r['url'] else T(r['S'])
    return (f'<li id="r{r["n"]}" class="ev" data-n="{r["n"]}">{pin(r)}<div><span class="when">{esc(r["when"])}</span> '
            f'{lead}<span class="what">{T(r["L"])}</span> <span class="said">{quote_html(r, skip_in=r["L"])}</span> '
            f'<span class="src">{src} · saved copy {esc(r["sid"])}</span></div></li>')


def records_block(recs, sub, li=None, extra=''):
    """The list of records under the figure, in two columns; on a phone it starts folded and opens when a mark is tapped."""
    li = li or record_li
    half = (len(recs) + 1) // 2
    return f"""
 <details class="card" id="records" open>
  <summary><h2>The records</h2><span class="fold">show or hide</span></summary>
  <p class="sub">{T(sub)}</p>
  <div class="cols">
   <section class="lcol"><ol>{''.join(li(r) for r in recs[:half])}</ol></section>
   <section class="lcol"><ol>{''.join(li(r) for r in recs[half:])}</ol></section>
  </div>{extra}
 </details>"""


def records_tsv(path, recs, cols):
    """The records as a table. The date column holds a date only where the page gives that day; where the figure shows
    other words ("Sept 2025", "No date given"), it is empty and shown_as carries the words (the order date is only a place)."""
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write('n\tdate\tshown_as\t' + '\t'.join(c for c, _ in cols) + '\tkind\tsource\taddress\tsaved_id\ttext\twords\n')
        for r in recs:
            fh.write('\t'.join([str(r['n']), str(r['date']) if r['when'] == fmt(r['date']) else '', r['when']] + [f(r) for _, f in cols] +
                               [r['kind'], r['S'], r['url'], r['sid'], r['L'], ' / '.join(q for q, _ in r['Q'])]) + '\n')


TOKENS = """
:root {
  --page: #f9f9f7; --surface: #fcfcfb; --ink: #0b0b0b; --ink2: #52514e; --muted: #7a7872;
  --grid: #e1e0d9; --axis: #c3c2b7; --border: rgba(11,11,11,0.12); --wash: rgba(11,11,11,0.045);
  --toward: #256abf; --away: #c44e18; --us: #898781; --rest: #cfcdc4; --pin-on: #ffffff; --link: #1c5cab;
  --toward-tint: rgba(37,106,191,0.085); --away-tint: rgba(196,78,24,0.085); --slot: rgba(11,11,11,0.028);
  --font-text: "Inter", system-ui, -apple-system, "Segoe UI", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-head: "Space Grotesk", "Inter", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink2: #c3c2b7; --muted: #8f8d86;
  --grid: #2c2c2a; --axis: #45453f; --border: rgba(255,255,255,0.14); --wash: rgba(255,255,255,0.06);
  --toward: #3987e5; --away: #d95926; --us: #898781; --rest: #45453f; --pin-on: #0d0d0d; --link: #86b6ef;
  --toward-tint: rgba(57,135,229,0.14); --away-tint: rgba(217,89,38,0.14); --slot: rgba(255,255,255,0.035); color-scheme: dark } }
:root[data-theme="dark"] {
  --page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink2: #c3c2b7; --muted: #8f8d86;
  --grid: #2c2c2a; --axis: #45453f; --border: rgba(255,255,255,0.14); --wash: rgba(255,255,255,0.06);
  --toward: #3987e5; --away: #d95926; --us: #898781; --rest: #45453f; --pin-on: #0d0d0d; --link: #86b6ef;
  --toward-tint: rgba(57,135,229,0.14); --away-tint: rgba(217,89,38,0.14); --slot: rgba(255,255,255,0.035); color-scheme: dark }
"""

BASE = """
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--page); color: var(--ink); font-family: var(--font-text); font-size: 16px; line-height: 1.5; }
[hidden] { display: none !important; }
a { color: var(--link); }
.wrap { max-width: 1312px; margin: 0 auto; padding: 28px 16px 48px; background: var(--page); }
#figure { background: var(--page); }
header { margin-bottom: 18px; }
.topline { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 4px 24px; margin: 0 0 12px; }
.eyebrow { font: 700 12px/1.35 var(--font-text); letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); margin: 0; }
.draft { font: 500 12px/1.35 var(--font-text); color: var(--muted); margin: 0; }
h1 { font-family: var(--font-head); font-size: clamp(27px, 3.3vw, 44px); line-height: 1.08; letter-spacing: -0.015em; margin: 0 0 12px; max-width: 27ch; text-wrap: balance; }
.deck { margin: 0; color: var(--ink2); font-size: 18px; line-height: 1.45; max-width: 82ch; }
.key { display: flex; flex-wrap: wrap; gap: 9px 26px; margin: 16px 0 0; padding: 0; list-style: none; font-size: 14.5px; color: var(--ink2); }
.key li { display: flex; align-items: center; gap: 8px; }
.key b { color: var(--ink); font-weight: 600; }
i.sw { display: inline-block; flex: none; width: 13px; height: 13px; border-radius: 50%; }
i.sw.toward { background: var(--toward); } i.sw.away { background: var(--away); }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 20px 22px; min-width: 0; }
.card h2 { font-family: var(--font-head); font-size: 22px; line-height: 1.2; margin: 0 0 4px; text-wrap: balance; }
.card .sub { margin: 0 0 12px; color: var(--ink2); font-size: 14.5px; max-width: 78ch; }
.card + .card, .gap { margin-top: 16px; }

/* numbered marks */
i.p { display: inline-grid; place-items: center; flex: none; width: 22px; height: 22px; border-radius: 50%; font: 700 11px/1 var(--font-text);
  font-style: normal; font-variant-numeric: tabular-nums; border: 2.5px solid; }
i.p.toward { border-color: var(--toward); } i.p.away { border-color: var(--away); }
i.p.neutral { border-color: var(--ink2); } i.p.solid.neutral { background: var(--ink2); color: var(--pin-on); }
i.p.hollow { background: var(--surface); color: var(--ink); }
i.p.solid.toward { background: var(--toward); color: var(--pin-on); } i.p.solid.away { background: var(--away); color: var(--pin-on); }
a.mk { display: flex; align-items: flex-start; gap: 8px; padding: 3px 5px; margin: 0 -5px; border-radius: 8px; text-decoration: none; color: inherit; font-size: 13px; line-height: 1.3; }
a.mk .mt { padding-top: 2.5px; min-width: 0; }
a.mk b { font-weight: 700; white-space: nowrap; font-variant-numeric: tabular-nums; }
a.mk .mt > span { color: var(--ink2); }
a.mk:hover, a.mk.hl, a.mk:focus-visible { background: var(--wash); outline: none; }
a.mk:hover i.p, a.mk.hl i.p, a.mk:focus-visible i.p { outline: 2.5px solid var(--ink); outline-offset: 1px; }

/* the records */
#records { margin-top: 16px; }
#records summary { display: flex; align-items: baseline; gap: 12px; cursor: pointer; list-style: none; }
#records summary::-webkit-details-marker { display: none; }
#records summary h2 { margin: 0 0 4px; }
#records summary .fold { font-size: 12.5px; color: var(--muted); text-decoration: underline; }
#records:not([open]) summary h2 { margin-bottom: 0; }
.cols { display: grid; grid-template-columns: 1fr; gap: 4px 34px; }
@media (min-width: 900px) { .cols { grid-template-columns: 1fr 1fr; } }
.lcol h3 { font: 700 13px/1.2 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin: 14px 0 8px; }
.lcol ol { list-style: none; margin: 0; padding: 0; }
li.ev { display: grid; grid-template-columns: 24px 1fr; gap: 10px; padding: 8px 6px; border-top: 1px solid var(--grid); border-radius: 6px; scroll-margin-top: 14px; overflow-wrap: anywhere; }
li.ev.hl, li.ev:target { background: var(--wash); }
.when { font-weight: 700; font-size: 13px; white-space: nowrap; }
.what { font-size: 14.5px; }
.said { display: block; font-size: 13.5px; color: var(--ink2); margin-top: 2px; }
.src { display: block; font-size: 12.5px; color: var(--muted); margin-top: 2px; }
.notes ul { margin: 6px 0 0; padding-left: 20px; color: var(--ink2); font-size: 14px; max-width: 112ch; }
.notes li { margin: 4px 0; }
.care { margin-top: 16px; padding: 14px 18px; border: 1px solid var(--border); border-left: 4px solid var(--ink); border-radius: 10px; background: var(--surface); }
.care h2 { font: 700 13px/1.2 var(--font-text); letter-spacing: 0.08em; text-transform: uppercase; margin: 0 0 6px; }
.care p, .care li { font-size: 14.5px; color: var(--ink2); margin: 0; max-width: 118ch; }
.care ul { margin: 0; padding-left: 18px; } .care li { margin: 3px 0; }
.care b { color: var(--ink); font-weight: 600; }
.srcline { font-size: 12.5px; color: var(--muted); margin: 10px 0 0; max-width: 130ch; }

#tip { position: fixed; z-index: 10; max-width: 370px; background: var(--ink); color: var(--page); padding: 10px 12px; border-radius: 10px; font-size: 13px; line-height: 1.4;
  box-shadow: 0 6px 24px rgba(0,0,0,0.25); pointer-events: none; }
#tip .tw { font-weight: 700; font-size: 12px; opacity: 0.8; } #tip .tt { font-weight: 600; margin: 2px 0 6px; }
#tip .tq { font-style: italic; opacity: 0.92; } #tip .te { opacity: 0.92; margin-top: 3px; } #tip .ts { margin-top: 6px; font-size: 12px; opacity: 0.75; }
"""

SCRIPT = """
const EV = %s;
const tip = document.getElementById('tip');
function line(cls, text) { const d = document.createElement('div'); d.className = cls; d.textContent = text; return d; }
function show(a) {
  const e = EV[a.dataset.n]; if (!e) return;
  const kids = [line('tw', [e.w, e.l].filter(Boolean).join(' \\u00b7 ')), line('tt', e.t)];
  if (e.q) kids.push(line('tq', '\\u201c' + e.q + '\\u201d'));
  if (e.e) kids.push(line('te', 'Our English: ' + e.e));
  const foot = [e.s, e.k].filter(Boolean).join(' \\u00b7 ');
  if (foot) kids.push(line('ts', foot));
  tip.replaceChildren(...kids);
  tip.hidden = false;
  const r = a.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
  let x = Math.min(Math.max(8, r.left + r.width / 2 - w / 2), window.innerWidth - w - 8), y = r.top - h - 10;
  if (y < 8) y = r.bottom + 10;
  tip.style.left = x + 'px'; tip.style.top = y + 'px';
}
function hl(n, on) { document.querySelectorAll('[data-n="' + n + '"]').forEach(el => el.classList.toggle('hl', on)); }
document.querySelectorAll('[data-n]').forEach(el => {
  const n = el.dataset.n, t = el.hasAttribute('data-tip');
  el.addEventListener('mouseenter', () => { hl(n, true); if (t) show(el); });
  el.addEventListener('mouseleave', () => { hl(n, false); tip.hidden = true; });
  el.addEventListener('focus', () => { hl(n, true); if (t) show(el); });
  el.addEventListener('blur', () => { hl(n, false); tip.hidden = true; });
});
window.addEventListener('scroll', () => { tip.hidden = true; }, { passive: true });
const recs = document.getElementById('records');
if (recs && recs.tagName === 'DETAILS') {
  const toRecord = () => { if (/^#r[0-9]+$/.test(location.hash)) { recs.open = true; const el = document.getElementById(location.hash.slice(1)); if (el) el.scrollIntoView(); } };
  if (window.matchMedia('(max-width: 820px)').matches && !/^#r[0-9]+$/.test(location.hash)) recs.open = false;
  document.querySelectorAll('a.mk, a.pinlink, a.u').forEach(a => a.addEventListener('click', () => { recs.open = true; }));
  window.addEventListener('hashchange', toRecord); toRecord();
}
"""


def page(title, eyebrow, h1, deck, key, figure, below, css, tipjson='{}'):
    """The whole page. `figure` goes inside #figure (the part exported as an image); `below` follows it."""
    assert 2 <= len(title.split()) <= 4, 'the page title must be two to four words'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap">
<style>
{TOKENS}{BASE}{css}
</style>
</head>
<body>
<div class="wrap">
 <div id="figure">
  <header>
   <div class="topline"><p class="eyebrow">{T(eyebrow)}</p><p class="draft">{NOTE}</p></div>
   <h1>{T(h1)}</h1>
   <p class="deck">{T(deck)}</p>
{key}
  </header>
{figure}
 </div>
{below}
</div>
<div id="tip" hidden></div>
<script>
{SCRIPT % tipjson}
</script>
</body>
</html>
"""


def finish(folder, name, page_html, lines):
    """Check the quotation marks in the finished page, then write it."""
    n = page_quotes_ok(page_html, lines)
    vis = html.unescape(re.sub(r'(?s)<[^>]+>', ' ', re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', page_html)))
    stray = re.findall(r'[^ ]*[{}][^ ]*|\bNone\b(?! [a-z])|\bnan\b|%%', vis)
    assert not stray, f'a placeholder or a stray value is left in the visible text: {stray[:5]}'
    out = Path(folder) / f'{name}.html'
    out.write_text(page_html, encoding='utf-8')
    print(f'{n} quotations in the page, each part of a checked line; written {out} ({len(page_html)} bytes)')
    return out


def export_png(html_path, shots, width=1400, margin=(40, 28)):
    """PNG images of parts of the page (device scale 2), each with a margin of page colour around it.
    Whatever follows the part on the page is hidden first, so that no edge of the next card shows in the margin."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_context(viewport={'width': width, 'height': 1000}, device_scale_factor=2, color_scheme='light').new_page()
        pg.goto(Path(html_path).as_uri()); pg.evaluate('document.fonts.ready.then(() => 1)'); pg.wait_for_timeout(800)
        for sel, out in shots:
            pg.evaluate("sel => { for (let s = document.querySelector(sel).nextElementSibling; s; s = s.nextElementSibling) s.style.display = 'none'; }", sel)
            b = pg.locator(sel).bounding_box()
            mx, my = margin
            clip = {'x': max(0, b['x'] - mx), 'y': max(0, b['y'] - my), 'width': b['width'] + 2 * mx, 'height': b['height'] + 2 * my}
            pg.screenshot(path=str(out), full_page=True, clip=clip)
            print('image', out, f"{round(clip['width'] * 2)} x {round(clip['height'] * 2)} px")
        br.close()
