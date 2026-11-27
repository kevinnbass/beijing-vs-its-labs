#!/usr/bin/env python3
# Repository copy. Changed from the working copy: paths, and load_clip() passes over the absent transcripts (README.md).
"""Build the referenced argument of the China chip-policy project, and the page of output ideas.

Reads   argument/argument_base.txt   the text, with saved ids in square brackets
        argument/argument_refs.tsv   one line per source: id, kind, label, address
        OUTPUT_IDEAS.md              the list of output ideas (same small markup)
Writes  ARGUMENT_referenced.md and .html, ARGUMENT_short.md (from
        argument/short_base.txt, checked the same way, with its own numbering), and OUTPUT_IDEAS.html

Nothing is written unless every check passes:
  - every id cited is in the references file and has a saved copy (sources/<id>);
  - every string between straight double quotes on a line stands in the saved copy of an id cited on that same line
    (spacing and the style of quote marks ignored; a quotation with " ... " is checked part by part);
  - every hidden line "!! id | words" (a statement the text makes without quoting) stands in that saved copy;
  - a planted false quotation is rejected and a known true one is found (the check can fail and can pass);
  - every reference has an address, or says why none is given.

Markup of the base file: "# " title, "@deck" and "@note" header lines, "## " section, a line that is only **bold** is a
sub-heading, "N. " a numbered point, "- " a list item, "| a | b |" a table row (first row is the header), "**bold**".
Run: python3 -I scripts/cn_argument_build.py
"""
import html, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cn_srclib as L

ROOT = Path(__file__).resolve().parents[1]
PROJ = ROOT
BASE = PROJ / 'argument' / 'argument_base.txt'
REFS = PROJ / 'argument' / 'argument_refs.tsv'
REFS_MORE = PROJ / 'argument' / 'argument_refs_more.tsv'
IDEAS = PROJ / 'OUTPUT_IDEAS.md'
FIGDATA = PROJ / 'figure' / 'figure_data.txt'
CLIPS = PROJ / 'transcripts_two_clips.md'

CITE = re.compile(r'\[((?:cn|ms|man|cnpol|clip)-[A-Za-z0-9-]+)\]')
QUOTE = re.compile(r'"([^"]+)"')
KIND = {'DOC': 'Chinese state document', 'OFF': 'Official document, or an official on the record', 'FIL': 'Company filing or statement',
        'REC': 'Press report of words spoken on the record', 'PRESS': 'Press report citing unnamed people',
        'COUNT': "Research firm's, broker's or research group's count", 'CLIP': 'Caption track or machine transcript, not checked by ear',
        'PUB': 'Published commentary, report or statement (state media, industry body, research institute)',
        'NAMED': 'Named person on the record',      # added Nov 23, 2026 for a named analyst's written testimony
        'ACCT': "A named outlet's account of a document, filing or official act",
        'NOTICE': "An institution's own published notice"}      # a university's purchase notice (no saved page calls the two universities state bodies)
SOLID = {'DOC', 'OFF', 'FIL', 'REC', 'PUB', 'NAMED', 'ACCT', 'NOTICE'}


SAVED_NOTE = True      # (b15, item 1d) the argument's reference list says where a reader finds a saved copy by its id; cn_doc_build.py turns it off (its notes cite ids the public sources.csv does not list)
LINK_FILES = True      # cn_doc_build.py turns this off: its outputs sit in other folders, where these relative links would not open


def load_clip():
    """The two clips' machine transcripts, as saved 'pages' the checker can read (time marks and [?] removed).
    clip-luckey: Palmer Luckey (section 2 of the transcripts file); clip-pottinger: Amanpour and Pottinger (section 1)."""
    if not CLIPS.exists(): return          # repository copy: the transcripts are not included; clip quotations then count as not found
    t = CLIPS.read_text(encoding='utf-8')
    one, two = t.split('## 2. Palmer Luckey', 1)
    one = one.split('## 1. Matt Pottinger', 1)[1]
    clean = lambda x: L.squash(re.sub(r'\[\d+:\d\d\]|\[\?\]', ' ', x))
    L._cache['clip-luckey'] = clean(two)
    L._cache['clip-pottinger'] = clean(one)


def load_refs():
    """argument_refs.tsv: every row must be cited by the argument. argument_refs_more.tsv (same columns): sources the
    argument no longer cites but other checked documents in outputs/ still may (a relay kept after the original
    article was saved by hand); those rows carry 'opt' and are not required to be cited."""
    refs = {}
    for f, opt in ((REFS, False), (REFS_MORE, True)):
        if not f.exists(): continue
        for ln in f.read_text(encoding='utf-8').splitlines():
            if not ln.strip() or ln.startswith('#'): continue
            c = ln.split('\t')
            if len(c) < 3 or c[1] not in KIND: sys.exit(f'references file: bad line: {ln[:80]}')
            if c[0] in refs: sys.exit(f'references file: {c[0]} twice')
            refs[c[0]] = {'kind': c[1], 'label': c[2].strip(), 'addr': c[3].strip() if len(c) > 3 else ''}
            if opt: refs[c[0]]['opt'] = True
    return refs


def meta(sid):
    try: return json.loads((L.P / sid / 'meta.json').read_text())
    except Exception: return {}


def shown(a):
    """An address as the reference list prints it: percent-codes written out, a long one cut short. The link keeps it whole."""
    from urllib.parse import unquote
    d = unquote(a)
    return d if len(d) <= 110 else d[:100] + '…'


def address(sid, r):
    if r['addr'] == '-': return None
    if r['addr']: return r['addr']
    m = meta(sid)
    route = str(m.get('route') or '')
    if sid.endswith('-wayback') and route.startswith('https://web.archive.org/'):
        return route.replace('id_/', '/', 1)
    return L.url_of(sid) or ''


NO_TITLE = {'cn-ga01-bnn-turnaround-20261123', 'ms-bj-202611-h200-hongkong-tnw', 'ms-bj-20251105-statefunded-standard', 'ms-bj-20260114-customs-h200-standard', 'cn-clips-evidence-1', 'cn-clips-reuters-hongkong-yahoo', 'cn-acts-reuters-customs-20260114', 'ms-bj-20250917-cac-6000d-engadget',
            'cn-ga31-twelve-2', 'cn-against2-ft-all-correction-20250917', 'cn-ga31-carriers2-37', 'man-cn-ft-202512-japan',
            'cn-counter-b13-3', 'cn-ga31-usoffwhitehousep3-12', 'cn-ga31-carriers2-15', 'cn-ga31-carriers-26',
            'cn-cnpress-hkej-h200-ndrc-20260819', 'cn-ga31-rtxlater-26', 'cn-ga31-rtxlater-81',
            'cn-le14-tnw-295b-plan-20260609', 'cn-cnpress-nbd-isoftstone-6000d-20261013', 'cn-counter-b8-5'}      # saved pages whose own headline the reference list does not print: the label says what the report is, and its address stays. The list was begun by touch-up 6b (Nov 24, 2026: a headline about a person and a matter the note leaves out) and extended on Nov 26 and 27, 2026 (rt1, b16e, b16f) by reading every printed page title: headlines that state a prohibition, a withheld approval or an instruction to companies as settled, that say where chips are or which named firm received or uses them, or that name a plan against one company as fact. The headlines themselves are not repeated here.


def title_of(sid):
    if sid in NO_TITLE: return ''
    f = L.P / sid / 'text.txt'
    t = ''
    if f.exists():
        m = re.search(r'^TITLE: (.*)$', f.read_text(encoding='utf-8', errors='replace')[:4000], re.M)
        if m: t = m.group(1).strip()
    if not t: t = str(meta(sid).get('title') or '').strip()
    t = re.sub(r'(?i)<br\s*/?>', ' ', t)                 # a saved page's title can carry a literal <br> (cn-policy-mic2025)
    t = re.sub(r'\s+', ' ', t).strip()
    return t if len(t) > 8 else ''


def check(lines, refs, need_all=True):
    """Return (problems, order of ids, count of quotations, count of hidden statements)."""
    bad, order, nq, nh = [], [], 0, 0
    hidden = []                                           # (line, saved id) of every "!!" line: its id must also be cited (edit 6e)
    for n, ln in enumerate(lines, 1):
        if ln.startswith('!!'):
            try: sid, words = [x.strip() for x in ln[2:].split('|', 1)]
            except ValueError: bad.append(f'line {n}: bad hidden line'); continue
            nh += 1; hidden.append((n, sid))
            if sid not in refs: bad.append(f'line {n}: hidden line names {sid}, not in the references file')
            elif not L.has(words, sid): bad.append(f'line {n}: NOT FOUND in {sid}: {words}')
            continue
        ids = CITE.findall(ln)
        for i in ids:
            if i not in refs: bad.append(f'line {n}: [{i}] is not in the references file')
            elif not i.startswith('clip-') and not (L.P / i).is_dir(): bad.append(f'line {n}: [{i}] has no saved copy')
            if i not in order: order.append(i)
        for q in QUOTE.findall(ln):
            nq += 1
            if not ids: bad.append(f'line {n}: quotation without a source on its line: {q[:70]}'); continue
            for part in [p for p in q.split(' ... ') if p.strip()]:
                if not any(i in refs and L.has(part, i) for i in ids):
                    bad.append(f'line {n}: NOT FOUND in {", ".join(ids)}: {part[:90]}')
    for i in refs:
        if need_all and i not in order and not refs[i].get('opt'): bad.append(f'references file: {i} is never cited')
    if need_all:      # a statement checked in a document the text never cites rests on a source its reference list leaves out (two such lines stood until edit 6e of Nov 24, 2026)
        for n, sid in hidden:
            if sid not in order: bad.append(f'line {n}: the hidden line checks words in {sid}, which the text never cites in square brackets')
    return bad, order, nq, nh


def controls():
    ok_false = not L.has('Beijing has published a ban on the purchase of Nvidia chips', 'cn-clips-evidence-1')
    ok_true = L.has('as Beijing withholds approval for large-scale imports', 'cn-clips-evidence-1')
    return ok_false and ok_true


# ---------- rendering ----------

def blocks(lines):
    """Group the base lines into blocks: (kind, payload)."""
    out, para, items, rows = [], [], [], []
    def flush():
        nonlocal para, items, rows
        if para: out.append(('p', ' '.join(para))); para = []
        if items: out.append(('ul', items)); items = []
        if rows: out.append(('table', rows)); rows = []
    for ln in lines:
        s = ln.rstrip()
        if s.startswith('!!'): continue
        if not s.strip(): flush(); continue
        if s.startswith('# '): flush(); out.append(('h1', s[2:]))
        elif s.startswith('## '): flush(); out.append(('h2', s[3:]))
        elif s.startswith('@deck '): flush(); out.append(('deck', s[6:]))
        elif s.startswith('@note '): flush(); out.append(('note', s[6:]))
        elif re.fullmatch(r'\*\*[^*]+\*\*', s): flush(); out.append(('h3', s[2:-2]))
        elif s.startswith('- '):
            if para or rows: flush()
            items.append(s[2:])
        elif s.startswith('|'):
            if para or items: flush()
            rows.append([c.strip() for c in s.strip('|').split('|')])
        elif re.match(r'\d+\. ', s):
            flush(); m = re.match(r'(\d+)\. (.*)', s); out.append(('pt', (m.group(1), m.group(2))))
        else:
            if items or rows: flush()
            para.append(s)
    flush()
    return out


def md_inline(s, num):
    return CITE.sub(lambda m: f'[{num[m.group(1)]}]', s)


def to_md(bl, num, refs, tail):
    o = []
    for k, v in bl:
        if k == 'h1': o.append(f'# {md_inline(v, num)}\n')
        elif k == 'deck': o.append(f'*{md_inline(v, num)}*\n')
        elif k == 'note': o.append(f'{md_inline(v, num)}\n')
        elif k == 'h2': o.append(f'## {md_inline(v, num)}\n')
        elif k == 'h3': o.append(f'### {md_inline(v, num)}\n')
        elif k == 'p': o.append(md_inline(v, num) + '\n')
        elif k == 'pt': o.append(f'**{v[0]}.** {md_inline(v[1], num)}\n')
        elif k == 'ul': o.append('\n'.join('- ' + md_inline(i, num) for i in v) + '\n')
        elif k == 'table':
            o.append('| ' + ' | '.join(v[0]) + ' |'); o.append('|' + '---|' * len(v[0]))
            o.extend('| ' + ' | '.join(md_inline(c, num) for c in r) + ' |' for r in v[1:]); o.append('')
    if refs is not None:
        o.append('## References\n')
        o.append('Each entry: its kind; what it is; the saved page\'s own title where the record holds one; the address; the id of the saved copy' + (SAVED_ID_WHERE if SAVED_NOTE else '') + '.\n')
        for sid, n in sorted(num.items(), key=lambda x: x[1]):
            r = refs[sid]; t = title_of(sid) if not sid.startswith('clip-') else ''; a = address(sid, r)
            line = f'[{n}] {KIND[r["kind"]]}. {r["label"]}.'
            if t: line += f' Page title: {t}.'
            line += f' {a}' if a else ' (No address given.)'
            if not sid.startswith('clip-'): line += f' Saved copy: {sid}'
            o.append(line + '\n')
        o.append(tail + '\n')
    return '\n'.join(o)


SAVED_ID_WHERE = ' (the public repository\'s sources.csv lists every id, with the page\'s address, the time it was saved and the sha256 of the saved file)'


def h_inline(s, num, refs):
    keep = []
    def cite(m):
        sid = m.group(1); n = num[sid]; r = refs[sid]
        cls = 'solid' if r['kind'] in SOLID else 'open'
        keep.append(f'<a class="c {cls}" href="#ref-{n}" title="{html.escape(KIND[r["kind"]] + ": " + r["label"], quote=True)}">{n}</a>')
        return f'\x00{len(keep) - 1}\x00'
    s = CITE.sub(cite, s) if num else s
    s = html.escape(s, quote=False)
    s = QUOTE.sub(lambda m: '“' + m.group(1).replace('“', '‘').replace('”', '’') + '”', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    if LINK_FILES: s = re.sub(r'(?<![\w/])(figure/[\w./-]+\.(?:html|tsv)|[A-Za-z0-9_]+\.(?:md|html))(?![\w/])', lambda m: f'<a href="{m.group(1)}">{m.group(1)}</a>', s)
    s = re.sub(r'</strong> (MADE in part|MADE|READY|NEW WORK)\.', r'</strong> <span class="tag">\1</span>', s)
    s = re.sub(r'\s+(\x00\d+\x00(?:\s*\x00\d+\x00)*)', lambda m: '\u202f' + re.sub(r'\s+', '', m.group(1)), s)
    return re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], s)


CSS = """
:root { --page:#f9f9f7; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#7a7872; --grid:#e1e0d9; --border:rgba(11,11,11,0.12);
  --wash:rgba(11,11,11,0.045); --toward:#256abf; --away:#c44e18; --link:#1c5cab; --on:#ffffff;
  --font-text:"Inter",system-ui,-apple-system,"Segoe UI","Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif; --font-head:"Space Grotesk","Inter",system-ui,sans-serif; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --page:#0d0d0d; --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#8f8d86;
  --grid:#2c2c2a; --border:rgba(255,255,255,0.14); --wash:rgba(255,255,255,0.06); --toward:#3987e5; --away:#d95926; --link:#86b6ef; --on:#0d0d0d; color-scheme:dark } }
:root[data-theme="dark"] { --page:#0d0d0d; --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --muted:#8f8d86; --grid:#2c2c2a; --border:rgba(255,255,255,0.14);
  --wash:rgba(255,255,255,0.06); --toward:#3987e5; --away:#d95926; --link:#86b6ef; --on:#0d0d0d; color-scheme:dark }
* { box-sizing:border-box; } html { -webkit-text-size-adjust:100%; scroll-behavior:smooth; }
body { margin:0; background:var(--page); color:var(--ink); font-family:var(--font-text); font-size:17px; line-height:1.62; }
a { color:var(--link); }
.wrap { max-width:1120px; margin:0 auto; padding:34px 16px 64px; }
.col { max-width:760px; margin:0 auto; overflow-wrap:break-word; }
.eyebrow { font:700 12px/1 var(--font-text); letter-spacing:0.1em; text-transform:uppercase; color:var(--muted); margin:0 0 12px; }
h1 { font-family:var(--font-head); font-size:clamp(28px,4.4vw,44px); line-height:1.08; letter-spacing:-0.015em; margin:0 0 14px; text-wrap:balance; }
.deck { margin:0 0 14px; color:var(--ink2); font-size:19px; line-height:1.45; }
.note { margin:0 0 4px; color:var(--muted); font-size:13.5px; line-height:1.45; }
.key { display:flex; flex-wrap:wrap; gap:8px 22px; margin:16px 0 0; padding:0; list-style:none; font-size:14px; color:var(--ink2); }
.key li { display:flex; align-items:center; gap:8px; }
figure { margin:26px 0 8px; }
figure > a { display:block; border:1px solid var(--border); border-radius:14px; overflow:hidden; background:#f9f9f7; padding:18px 20px 10px; }
@media (max-width: 640px) { figure > a { padding:10px 10px 6px; } }
figure img { display:block; width:100%; height:auto; }
figcaption { margin:10px auto 0; max-width:760px; color:var(--ink2); font-size:14.5px; line-height:1.45; }
h2 { font-family:var(--font-head); font-size:25px; line-height:1.2; margin:44px 0 12px; padding-top:18px; border-top:1px solid var(--grid); text-wrap:balance; }
h3 { font:700 12.5px/1.2 var(--font-text); letter-spacing:0.09em; text-transform:uppercase; color:var(--ink2); margin:26px 0 10px; }
p { margin:0 0 14px; }
p.pt { position:relative; padding-left:38px; } p.cont { padding-left:38px; }
p.pt > .n { position:absolute; left:0; top:1px; width:28px; text-align:right; font:700 15px/1.62 var(--font-head); color:var(--muted); font-variant-numeric:tabular-nums; }
ul.l { margin:0 0 14px; padding-left:20px; } ul.l li { margin:0 0 8px; }
a.c { display:inline; padding:1.5px 5px; margin:0 1px; border-radius:10px; font:700 10.5px/1 var(--font-text); white-space:nowrap;
  font-variant-numeric:tabular-nums; text-decoration:none; border:1.6px solid var(--ink2); vertical-align:2px; }
a.c.solid { background:var(--ink2); color:var(--page); } a.c.open { background:transparent; color:var(--ink); }
a.c:hover, a.c:focus-visible { outline:2px solid var(--ink); outline-offset:1px; }
.tw { overflow-x:auto; margin:0 0 16px; }
table { border-collapse:collapse; width:100%; min-width:560px; font-size:15px; line-height:1.45; }
th { text-align:left; font:700 12px/1.2 var(--font-text); letter-spacing:0.07em; text-transform:uppercase; color:var(--muted); padding:8px 12px 8px 0; border-bottom:1.5px solid var(--ink2); }
td { vertical-align:top; padding:10px 12px 10px 0; border-bottom:1px solid var(--grid); } td:first-child { font-weight:600; width:27%; } td:last-child { color:var(--ink2); width:30%; padding-right:0; }
ol.refs { list-style:none; margin:0; padding:0; font-size:14px; line-height:1.5; }
ol.refs li { position:relative; padding:9px 8px 9px 44px; border-top:1px solid var(--grid); overflow-wrap:anywhere; }
ol.refs li:target { background:var(--wash); }
ol.refs li > a.c { position:absolute; left:6px; top:13px; }
ol.refs .k { font:700 11px/1.2 var(--font-text); letter-spacing:0.06em; text-transform:uppercase; color:var(--muted); display:block; margin-bottom:2px; }
ol.refs .t { color:var(--ink2); } ol.refs .id { color:var(--muted); font-size:12.5px; }
.tail { margin-top:18px; color:var(--muted); font-size:13.5px; }
.grp h2 { margin-top:36px; } .grp p.pt { margin-bottom:9px; }
@media (max-width: 640px) {
  table { min-width:0; } thead { display:none; } tr { display:block; padding:10px 0; border-bottom:1px solid var(--grid); }
  td, td:first-child, td:last-child { display:block; width:auto; padding:0 0 3px; border:0; } td:last-child { font-size:14px; }
  td[data-l]:not(:first-child):not([data-l=""])::before { content:attr(data-l) ": "; font:700 11px/1.2 var(--font-text); letter-spacing:0.06em; text-transform:uppercase; color:var(--muted); margin-right:4px; }
}
.tag { display:inline-block; font:700 10.5px/1 var(--font-text); letter-spacing:0.06em; text-transform:uppercase; padding:3px 6px; border-radius:5px; background:var(--wash); color:var(--ink2); vertical-align:2px; margin-right:4px; }
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%%TITLE%%</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap">
<style>%%CSS%%</style>
</head>
<body>
<div class="wrap">
%%BODY%%
</div>
</body>
</html>
"""


def to_html(bl, num, refs, tail, title, eyebrow, figure):
    o, head_done = [], False
    def close_head():
        nonlocal head_done
        if head_done: return
        head_done = True
        if refs is not None:
            o.append('<ul class="key"><li><a class="c solid">1</a> a filled number: a document, a filing, a named person on the record, a published commentary, report or statement of state media, an industry body or a research institute, an institution\'s own notice, or a named outlet\'s account of a document</li>'
                     '<li><a class="c open">2</a> an open number: a press report citing unnamed people, a research firm\'s, broker\'s or research group\'s count, or captions and machine transcripts nobody has checked by ear</li></ul>')
        o.append('</div>')
        if figure: o.append(figure)
        o.append('<div class="col' + ('' if refs is not None else ' grp') + '">')
    o.append(f'<div class="col"><p class="eyebrow">{html.escape(eyebrow)}</p>')
    in_point, was = False, None      # a paragraph that follows a numbered point, or a table or paragraph inside one, keeps the point's indent
    for k, v in bl:
        if k in ('h2', 'h3', 'ul'): in_point = False
        if k == 'pt': in_point = True
        cont = in_point and k == 'p' and was in ('table', 'pt', 'p'); was = k
        if k == 'h1': o.append(f'<h1>{h_inline(v, num, refs)}</h1>')
        elif k == 'deck': o.append(f'<p class="deck">{h_inline(v, num, refs)}</p>')
        elif k == 'note': o.append(f'<p class="note">{h_inline(v, num, refs)}</p>')
        else:
            close_head()
            if k == 'h2': o.append(f'<h2>{h_inline(v, num, refs)}</h2>')
            elif k == 'h3': o.append(f'<h3>{h_inline(v, num, refs)}</h3>')
            elif k == 'p': o.append(('<p class="cont">' if cont else '<p>') + f'{h_inline(v, num, refs)}</p>')
            elif k == 'pt': o.append(f'<p class="pt" id="p{v[0]}"><span class="n">{v[0]}</span>{h_inline(v[1], num, refs)}</p>')
            elif k == 'ul': o.append('<ul class="l">' + ''.join(f'<li>{h_inline(i, num, refs)}</li>' for i in v) + '</ul>')
            elif k == 'table':
                o.append('<div class="tw"><table><thead><tr>' + ''.join(f'<th>{html.escape(c)}</th>' for c in v[0]) + '</tr></thead><tbody>')
                o.extend('<tr>' + ''.join(f'<td data-l="{html.escape(v[0][i] if i < len(v[0]) else "", quote=True)}">{h_inline(c, num, refs)}</td>' for i, c in enumerate(r)) + '</tr>' for r in v[1:])
                o.append('</tbody></table></div>')
    close_head()
    if refs is not None:
        o.append('<h2 id="references">References</h2>' + (f'<p class="note">Each entry ends with the id of the saved copy{html.escape(SAVED_ID_WHERE)}.</p>' if SAVED_NOTE else '') + '<ol class="refs">')
        for sid, n in sorted(num.items(), key=lambda x: x[1]):
            r = refs[sid]; t = title_of(sid) if not sid.startswith('clip-') else ''; a = address(sid, r)
            cls = 'solid' if r['kind'] in SOLID else 'open'
            lab = QUOTE.sub(lambda m: '“' + m.group(1) + '”', html.escape(r["label"], quote=False))      # a title in a label gets curly marks, as quotations in the text do
            li = f'<li id="ref-{n}"><a class="c {cls}" href="#ref-{n}">{n}</a><span class="k">{html.escape(KIND[r["kind"]])}</span>{lab}.'
            if t: li += f' <span class="t">Page title: {html.escape(t)}.</span>'
            if a: li += f' <a href="{html.escape(a, quote=True)}" rel="noopener">{html.escape(shown(a))}</a>'
            if not sid.startswith('clip-'): li += f' <span class="id">Saved copy: {html.escape(sid)}</span>'
            o.append(li + '</li>')
        o.append('</ol>')
        o.append(f'<p class="tail">{html.escape(tail)}</p>')
    o.append('</div>')
    return PAGE.replace('%%TITLE%%', html.escape(title)).replace('%%CSS%%', CSS).replace('%%BODY%%', '\n'.join(o))


def main():
    load_clip()
    refs = load_refs()
    lines = BASE.read_text(encoding='utf-8').splitlines()
    bad, order, nq, nh = check(lines, refs)
    for sid in order:
        if sid in refs and refs[sid]['addr'] != '-' and not address(sid, refs[sid]): bad.append(f'{sid}: no address (give one in the references file, or "-" with the reason in the label)')
    if not controls(): bad.append('controls: the planted false quotation was found, or the known true one was not')
    if bad:
        print('\n'.join(bad)); print(f'\nNOT WRITTEN: {len(bad)} problem(s)'); sys.exit(1)
    num = {sid: n for n, sid in enumerate(order, 1)}
    kinds = {}
    for sid in order: kinds[refs[sid]['kind']] = kinds.get(refs[sid]['kind'], 0) + 1
    solid = sum(v for k, v in kinds.items() if k in SOLID)
    tail = (f'Build check: {nq} quotations, and {nh} passages that back statements made without quoting, were looked for in the saved copies of {len(order)} sources and all were found; '
            f"a made-up quotation, put in as a test, was not found. {solid} sources are documents, filings or named people on the record, or published commentaries, reports or statements of state media, industry bodies or research institutes, institutions' own notices and named outlets' accounts of documents; {len(order) - solid} are press reports citing unnamed people, counts, or captions and machine transcripts. "
            'A quotation that is found shows what the source says, not that it is true.')
    bl = blocks(lines)
    n_events = sum(1 for ln in FIGDATA.read_text(encoding='utf-8').splitlines() if ln.startswith('@ '))
    figure = ('<figure><a href="figure/beijing_vs_labs.html"><img src="figure/beijing_vs_labs_top.png" alt="The figure: a dated strip of '
              f'{n_events} records in four rows, the H200 in reported numbers, Nvidia\'s share of AI chips in China, and its revenue from customers based in China by quarter"></a>'
              f'<figcaption>The record at a glance: {n_events} dated records in four rows, the H200 in reported numbers, Nvidia\'s share, and its own revenue from customers based in China. '
              'Its mark numbers are the figure\'s own, not this note\'s reference numbers. <a href="figure/beijing_vs_labs.html">Open the full figure</a>: each mark there shows the source\'s own words.</figcaption></figure>')
    (PROJ / 'ARGUMENT_referenced.md').write_text(to_md(bl, num, refs, tail), encoding='utf-8')
    (PROJ / 'ARGUMENT_referenced.html').write_text(to_html(bl, num, refs, tail, 'Beijing vs. Labs Argument', 'China chip policy · the argument, with references', figure), encoding='utf-8')
    print(f'argument: {len(order)} sources ({solid} on the record, {len(order) - solid} press, count or transcript); quotations checked {nq}, hidden statements {nh}, all found; control rejected (as it must be)')
    words = len(re.findall(r"[A-Za-z0-9$%'-]+", ' '.join(ln for ln in lines if not ln.startswith('!!'))))
    print(f'argument: about {words} words of text before the reference list')
    short = PROJ / 'argument' / 'short_base.txt'
    if short.exists():
        sl = short.read_text(encoding='utf-8').splitlines()
        sbad, sorder, snq, snh = check(sl, refs, need_all=False)
        if sbad:
            print('\n'.join('short version: ' + b for b in sbad)); print('short version NOT WRITTEN'); sys.exit(1)
        snum = {sid: n for n, sid in enumerate(sorder, 1)}
        stail = f'Build check: {snq} quotations, and {snh} passages that back statements made without quoting, were looked for in the saved copies of {len(sorder)} sources and all were found.'
        short_md = to_md(blocks(sl), snum, refs, stail)
        (PROJ / 'ARGUMENT_short.md').write_text(short_md, encoding='utf-8')
        (PROJ / 'ARGUMENT_short.txt').write_text(short_md, encoding='utf-8')      # the same text under a name a browser shows
        body = ' '.join(ln for ln in sl if ln.strip() and not ln.startswith(('!!', '#', '@')))
        print(f'short version: {len(CITE.sub("", body).split())} words, {len(sorder)} sources; quotations checked {snq}, hidden statements {snh}, all found')
    if IDEAS.exists():
        il = IDEAS.read_text(encoding='utf-8').splitlines()
        ib = blocks(il)
        n_ideas = sum(1 for k, _ in ib if k == 'pt')
        (PROJ / 'OUTPUT_IDEAS.html').write_text(to_html(ib, {}, None, '', 'Chip Policy Output Ideas', 'China chip policy · what could be made from it', ''), encoding='utf-8')
        print(f'ideas: {n_ideas} numbered ideas rendered')


if __name__ == '__main__':
    main()
