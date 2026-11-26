#!/usr/bin/env python3
"""Idea 24: a silent explainer. The dated strip, in twelve chapters, with on-screen captions and no voice.
First made at 89 seconds (the idea asked for 60 to 90); slowed in round 2 to a reading pace; in round 4 re-made for
the core's five limits and its longer closing sentence, which the reading pace turns into about four minutes.

Run:  python3 -I build.py                                           checks, then writes the page and the capture plan
      nice -n 19 python3 frames.py      captures the frames and encodes explainer.mp4

Reads   captions_base.txt     the captions and their source lines, in the small markup of scripts/cn_doc_build.py
        chapters.tsv          which marks of the strip each caption brings on screen
        extra_refs.tsv        sources that only hidden check lines cite
        ../../../figure/figure_data.txt, ../../../figure/template.html, ../a7lib.py      the dated records, the figure's
                              headline and key, and the copied strip geometry
        ../../../tables/house_licence_table.tsv, state_media_items.tsv                  the counts three captions state
Order of work, and what stops it:
  1. scripts/cn_doc_build.py builds captions.md and captions.html from captions_base.txt. It writes nothing unless every
     quotation and every hidden "!!" line is found in the saved copy of its source. If it fails, this script stops.
  2. The captions for the page are taken from the same base file with the same numbering. frames.py later compares the
     text the page shows in each chapter with captions.md, and stops on any difference.
  3. The last two captions, joined, must be the sentence of ../../../ARGUMENT_referenced.md, section 6, word for word.
     There must be five captions titled "Limit N of 5". The count of policy pages must equal the rows of
     ../../../NOTE_policies_checked.md. The 579,868 chips and the 55% must equal sums over the licence table the House
     committee released. The state-media items (how many, how many only warn, how many of those in the burst of the
     first year with its first and last dates, and the later ones, their outlet and year) must equal the sums over
     tables/state_media_items.tsv, and the argument must give the same counts (round 5, after core edit 6). Phrases
     the core withdrew ("750,000", "four limits", "more than half of the chips applied for", "Democrats", "the
     Commerce Department's table") must not appear.
  4. quotes.tsv (the source words behind every mark, label and dashed line of the strip) must pass scripts/cn_has.py.
  5. chapters.tsv must bring every record on screen exactly once.
Writes  captions.md, captions.html (through cn_doc_build.py), quotes.tsv, explainer.html, capture.json.
Timing, two rules, each rounded up to a frame; a chapter lasts the longer of the two:
  1. the words of its caption divided by 2.5. In the numbers chapter the four cells are the caption's substance, so
     each cell's label and value are counted too;
  2. every word in its caption box (caption and source lines) divided by 4, so that a reader at an ordinary pace can
     also take in the source lines.
The build prints both rates for each chapter and stops if either rule is broken.
"""
import json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent))
import a7lib as L   # noqa: E402
sys.path.insert(0, str(L.SCRIPTS))
import cn_argument_build as B   # noqa: E402  (importing it builds nothing: its main() is guarded)

FPS, RATE, BOX_RATE, DIM = 25, 2.5, 4.0, 0.28    # the most words a second: of the caption (RATE), of everything in the caption box (BOX_RATE)
ROWS = r'((?:Reported: )?.+?:) (.+?\.) (.+)'      # a line of the numbers chapter: what is counted (a press count begins "Reported: ", as the argument's table of numbers labels it since core batch 14), its value (the source's words where quoted), the source
DOC_TITLE, DOC_EYEBROW = 'Twelve Checked Captions', 'China chip policy · captions of the explainer video'
KINDS = ('On the record', 'Reported', 'Captions, not checked by ear', 'Our own reading', 'Our own count', "From the project's")   # how a source line may begin
GONE = ('750,000', 'four limits', 'more than half of the chips applied for', 'Democrats', 'more exact', 'at a lower rate',
        "Commerce Department's table", 'Commerce Department table', "Commerce Department's summary", 'Aug 1 to Sept 24')    # wording the core withdrew (the last four: core edit 6)
NUMWORD = {2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'}
CARD_TOP, PAD = 48, 4
esc = L.esc

EXTRA_CSS = """
#h1 { left:24px; top:12px; font-size:24px; line-height:1.2; }
#clockbox { right:24px; top:6px; }
#date { font-size:31px; line-height:1.15; }
#card { left:16px; top:%%CARD_TOP%%px; width:1248px; height:%%CARD_H%%px; }
#card svg { left:8px; top:%%PAD%%px; width:%%SVG_W%%px; height:%%SVG_H%%px; }
.stage ul.key { left:%%KEY_L%%px; top:12px; width:%%KEY_W%%px; }
#count { position:absolute; left:%%COUNT_L%%px; bottom:12px; font-size:13px; line-height:1.35; white-space:nowrap; }
#capbox { left:16px; top:%%CAP_Y%%px; width:1248px; height:%%CAP_H%%px; }
.cap { position:absolute; left:18px; right:18px; top:9px; bottom:7px; opacity:0; visibility:hidden; }
.cap .lab { display:flex; align-items:baseline; gap:10px; }
.cap .num { font:700 11.5px/1 var(--font-text); letter-spacing:0.09em; text-transform:uppercase; color:var(--muted); white-space:nowrap; }
.cap .ttl { font:700 18.5px/1.2 var(--font-head); letter-spacing:-0.005em; color:var(--ink); }
.cap .txt { font-size:22px; line-height:1.36; color:var(--ink); margin-top:5px; text-wrap:pretty; }
.cap.mid .txt { font-size:21px; }
.cap.long .txt { font-size:20px; }
.cap ul { list-style:none; padding:0; }
.cap .src { margin-top:7px; font-size:13.5px; line-height:1.4; color:var(--ink2); }
.cap .src li { display:flex; align-items:baseline; gap:7px; }
.cap .src i.tier { display:inline-block; flex:none; width:10px; height:10px; border-radius:50%; border:2px solid var(--ink2); transform:translateY(1px); }
.cap .src i.tier.solid { background:var(--ink2); } .cap .src i.tier.open { background:var(--surface); } .cap .src i.tier.plain { border-color:transparent; }
.cap .nums { display:grid; grid-template-columns:repeat(4, 1fr); column-gap:22px; margin-top:9px; }
.cap .nums li { border-top:2px solid var(--axis); padding-top:6px; min-width:0; }
.cap .nums .ln { display:block; }
.cap .nums .lab2 { font-size:13px; line-height:1.3; color:var(--ink2); font-weight:500; }
.cap .nums .val { font:700 17.5px/1.22 var(--font-head); color:var(--ink); margin:2px 0 3px; }
.cap .nums .from { font-size:12.5px; line-height:1.3; color:var(--muted); }
.stage .c { display:inline-block; padding:1.5px 5px; margin:0 1px; border-radius:10px; font:700 10.5px/1 var(--font-text); font-variant-numeric:tabular-nums;
  border:1.6px solid var(--ink2); vertical-align:2px; white-space:nowrap; }
.stage .c.solid { background:var(--ink2); color:var(--page); } .stage .c.open { background:transparent; color:var(--ink); }
#draft { left:24px; bottom:6px; font-size:11px; }
#bar { position:absolute; left:0; bottom:0; height:3px; width:0; background:var(--ink2); opacity:0.4; }
"""


def chip(sid, num, refs):
    r = refs[sid]
    return f'<span class="c {"solid" if r["kind"] in B.SOLID else "open"}" title="{esc(B.KIND[r["kind"]], quote=True)}">{num[sid]}</span>'


def inline(s, num, refs):
    """One line of the base text as HTML: [id] becomes its numbered chip, "words" get typographic quote marks."""
    s = B.CITE.sub(lambda m: f'\x00{m.group(1)}\x00', s)
    s = esc(s, quote=False)
    s = B.QUOTE.sub(lambda m: '“' + m.group(1) + '”', s).replace("'", '’')
    assert '"' not in s and '**' not in s, s
    assert not re.search(r'\x00\s*\x00', s), 'two references side by side'
    # the word before a reference and its chip stay on one line
    return re.sub(r'(\S+)\s*\x00([^\x00]+)\x00', lambda m: f'<span class="nb">{m.group(1)} {chip(m.group(2), num, refs)}</span>', s)


def plain(s, num):
    """The same line as plain text with reference numbers, as cn_doc_build.py writes it into captions.md."""
    return B.CITE.sub(lambda m: f'[{num[m.group(1)]}]', s)


def words(s):
    return len(B.CITE.sub('', s.replace('**', '')).split())


def cells(c):
    """The items of a caption as number cells (label, value, source), or None when they are source lines."""
    if all(i.startswith(KINDS) for i in c['items']): return None
    rows = [re.fullmatch(ROWS, i) for i in c['items']]
    if not all(rows): sys.exit(f'caption {c["k"]}: a line is neither a source line (it does not say what kind of source it is) nor a number cell')
    return rows


def read_words(c):
    """The words a chapter asks a viewer to read: the caption, and in a chapter of number cells each cell's label and value."""
    rows = cells(c)
    return words(c['text']) + (sum(words(m.group(1)) + words(m.group(2)) for m in rows) if rows else 0)


def load_all_refs():
    """The argument's references plus this folder's extra_refs.tsv, read as scripts/cn_doc_build.py reads --refs."""
    refs = B.load_refs()
    for ln in (HERE / 'extra_refs.tsv').read_text(encoding='utf-8').splitlines():
        if not ln.strip() or ln.startswith('#'): continue
        c = ln.split('\t')
        if len(c) < 3 or c[1] not in B.KIND: sys.exit(f'extra_refs.tsv: bad line: {ln[:80]}')
        if c[0] in refs: sys.exit(f'extra_refs.tsv: {c[0]} is already in the argument\'s references')
        refs[c[0]] = {'kind': c[1], 'label': c[2].strip(), 'addr': c[3].strip() if len(c) > 3 else ''}
    return refs


def read_captions(lines, num):
    caps, cur, on = [], None, False
    for kind, v in B.blocks(lines):
        if kind == 'h2': on = v.strip() == 'The captions'; continue
        if not on: continue
        if kind == 'pt':
            m = re.fullmatch(r'\*\*([^*]+)\*\* (.+)', v[1])
            if not m: sys.exit(f'caption {v[0]} does not start with its title in bold')
            cur = dict(k=int(v[0]), title=m.group(1), text=m.group(2), items=[]); caps.append(cur)
        elif kind == 'ul' and cur is not None and not cur['items']: cur['items'] = list(v)
        else: sys.exit(f'the captions section holds something that is not a caption or its source lines: {kind}')
    if [c['k'] for c in caps] != list(range(1, len(caps) + 1)): sys.exit('captions are not numbered 1, 2, 3 ...')
    return caps


def read_md():
    """The captions as captions.md holds them: what the video must show."""
    sec = (HERE / 'captions.md').read_text(encoding='utf-8').split('## The captions', 1)[1].split('## References', 1)[0]
    out = []
    for ln in sec.splitlines():
        m = re.fullmatch(r'\*\*(\d+)\.\*\* \*\*([^*]+)\*\* (.+)', ln.strip())
        if m: out.append(dict(k=int(m.group(1)), title=m.group(2), text=m.group(3), items=[]))
        elif ln.startswith('- '): out[-1]['items'].append(ln[2:].strip())
        elif ln.strip(): sys.exit(f'captions.md: a line in the captions section was not understood: {ln[:80]}')
    return out


def assign(evs):
    """chapters.tsv -> for each chapter the marks that are new in it and the marks lit again."""
    key = {(e['lane'], e['sid']): e for e in evs}
    assert len(key) == len(evs)
    rows = []
    for n, ln in enumerate((HERE / 'chapters.tsv').read_text(encoding='utf-8').splitlines(), 1):
        if not ln.strip() or ln.startswith('#'): continue
        c = ln.split('\t')
        if len(c) != 4 or c[1] not in ('new', 'again') or c[2] not in L.LANES: sys.exit(f'chapters.tsv line {n} not understood: {ln[:70]}')
        rows.append((int(c[0]), c[1], c[2], c[3].strip(), n))
    new = {}
    for ch, role, lane, sid, n in rows:
        if role == 'new' and not sid.startswith('*'):
            if (lane, sid) not in key: sys.exit(f'chapters.tsv line {n}: no record {sid} in row {lane}')
            if (lane, sid) in new: sys.exit(f'chapters.tsv line {n}: {sid} is new twice')
            new[(lane, sid)] = ch
    for ch, role, lane, sid, n in rows:
        if role == 'new' and sid.startswith('*'):
            want = {'*': None, '*solid': True, '*press': False}[sid]
            hit = [k for k, e in key.items() if k[0] == lane and k not in new and (want is None or e['solid'] == want)]
            if not hit: sys.exit(f'chapters.tsv line {n}: {lane} {sid} matches no record')
            for k in hit: new[k] = ch
    left = [k for k in key if k not in new]
    if left: sys.exit(f'chapters.tsv: {len(left)} records never appear: {left[:4]}')
    again = {}
    for ch, role, lane, sid, n in rows:
        if role == 'again':
            ks = [k for k in key if k[0] == lane] if sid == '*' else [(lane, sid)]
            for k in ks:
                if k not in key: sys.exit(f'chapters.tsv line {n}: no record {sid} in row {lane}')
                if new[k] >= ch: sys.exit(f'chapters.tsv line {n}: {k[1]} is lit again before it has appeared')
                again.setdefault(ch, []).append(k)
    return {key[k]['n']: ch for k, ch in new.items()}, {ch: [key[k]['n'] for k in ks] for ch, ks in again.items()}


def caption_html(c, n_caps, num, refs):
    w = read_words(c) if cells(c) else words(c['text'])
    size = ' long' if w > 52 else ' mid' if w > 40 else ''
    o = [f'<div class="cap{size}" id="cap{c["k"]}"><div class="lab"><span class="num">{c["k"]} of {n_caps}</span><span class="ttl">{inline(c["title"], num, refs)}</span></div>',
         f'<p class="txt">{inline(c["text"], num, refs)}</p>']
    rows = cells(c)
    if rows:                         # a row of numbers: what it counts, its value, the source
        o.append('<ul class="nums">' + ''.join(f'<li><span class="ln lab2">{inline(m.group(1), num, refs)}</span><span class="ln val">{inline(m.group(2), num, refs)}</span>'
                                               f'<span class="ln from">{inline(m.group(3), num, refs)}</span></li>' for m in rows) + '</ul>')
    else:
        tier = lambda it: 'solid' if it.startswith('On the record') else 'open' if it.startswith(('Reported', 'Captions')) else 'plain'
        o.append('<ul class="src">' + ''.join(f'<li><i class="tier {tier(it)}"></i><span>{inline(it, num, refs)}</span></li>' for it in c['items']) + '</ul>')
    o.append('</div>')
    return '\n'.join(o)


def check_substance(caps):
    """The checks of step 3 of the docstring. Returns lines for the build log."""
    everything = lambda c: c['title'] + ' ' + c['text'] + ' ' + ' '.join(c['items'])
    out = []
    # the sentence that survives: the last two captions, joined
    arg = re.sub(r'\s+', ' ', (L.PROJ / 'ARGUMENT_referenced.md').read_text(encoding='utf-8'))
    joined = caps[-2]['text'] + ' ' + caps[-1]['text']
    head = '**One sentence that survives all five limits.** '
    if head + joined + ' ## ' not in arg: sys.exit('the last two captions, joined, are not the sentence of ARGUMENT_referenced.md, section 6, word for word')
    assert head + joined.replace('2024', '2023') + ' ## ' not in arg, 'control: a changed sentence must not be found'
    out.append(f'the last two captions, joined ({words(joined)} words), are the argument\'s sentence word for word')
    # five limits
    limits = [c['k'] for c in caps if re.fullmatch(r'Limit [1-5] of 5\.', c['title'])]
    if [c['title'] for c in caps if c['k'] in limits] != [f'Limit {i} of 5.' for i in range(1, 6)]: sys.exit('the captions do not hold "Limit 1 of 5" to "Limit 5 of 5", in order')
    if 'Five limits on the claim' not in arg: sys.exit('the argument no longer has five limits')
    out.append(f'five limits, captions {limits}')
    # wording the core withdrew
    for c in caps:
        for g in GONE:
            if g.lower() in everything(c).lower(): sys.exit(f'caption {c["k"]} holds wording the core withdrew: {g}')
    assert any('the 82 policy pages' in everything(c) for c in caps), 'control: a phrase that is there must be seen'
    # policy pages
    pages = L.policy_rows()
    note = (L.PROJ / 'NOTE_policies_checked.md').read_text(encoding='utf-8')
    if '[cn-policy-micron-decision]' not in note: sys.exit('a caption says the 2023 conclusion on Micron is among the policy pages read; the note does not list it')
    assert '[cn-policy-no-such-page]' not in note, 'control: an id that is not in the note must not be found'
    seen = [int(m.group(1)) for c in caps for m in re.finditer(r'(\d+) policy pages', everything(c))]
    if not seen or any(n != pages for n in seen): sys.exit(f'a caption gives {seen} policy pages; the note has {pages} pages read')
    # the House committee's table
    t = L.house_table()
    cell = [i for c in caps for i in c['items'] if i.startswith('Licensed by Washington for Nvidia')]
    want = f'{t["appr_nv"]:,} chips, each application "Approved, not shipped".'
    if len(cell) != 1 or want not in cell[0]: sys.exit(f'the cell for Washington\'s licences must read: {want}')
    # round 12 (Nov 26, 2026): Washington returned the APPLICATIONS, not chips (the figure's note since core batch 14, row ZH5-C06; the
    # argument's answer: "... 1,888,950 (55%; the sum is mine) were in applications it returned without action"); the old caption's words are refused
    share = f'Washington returned without action the applications for {t["rwa_pct"]}% of the chips its summary of May 11, 2026 records'
    old_share = f'Washington returned without action {t["rwa_pct"]}% of the chips in the applications'
    if sum(share in c['text'] for c in caps) != 1: sys.exit(f'one caption must read: {share}')
    if any(old_share in everything(c) for c in caps): sys.exit(f'a caption still says Washington returned chips: {old_share}')
    assert old_share in f'{old_share} its summary', 'control: the old words must be seen where they stand'
    answer = f'of the {t["all"]:,} chips in the licence applications that Washington\'s summary of May 11, 2026 records, {t["rwa"]:,} ({t["rwa_pct"]}%; the sum is mine) were in applications it returned without action'
    if not all(x in arg for x in (f'{t["appr_nv"]:,} in Nvidia\'s {t["n_appr_nv"]}', f'{t["rwa"]:,} of the {t["all"]:,} chips in it, {t["rwa_pct"]}%', answer)): sys.exit('the argument no longer gives these sums of the House table')
    assert answer.replace(f'{t["rwa"]:,}', f'{t["rwa"] + 1:,}') not in arg, 'control: a wrong sum must not be found in the argument'
    assert f'{t["appr"]:,} chips, each application' not in cell[0], 'control: the sum of both makers must not pass for Nvidia\'s'
    out.append(f'House table: Nvidia approved and not shipped {t["appr_nv"]:,} in {t["n_appr_nv"]} applications; returned without action {t["rwa"]:,} of {t["all"]:,} = {t["rwa_pct"]}% (summed here, equal to the captions and to the argument)')
    # the state-media items (since core edit 6: a census of 42 and further items found by searches and links)
    sm = L.state_media()
    mon = lambda d: f'{L.MON[d.month - 1]} {d.day}'
    assert sm['first'].year == sm['last'].year
    later = sm['later']
    if not later: sys.exit('no warning found after the first year: caption 7 must be reworded')
    yrs = sorted({d.year for d, _, _ in later})
    if len(yrs) != 1 or not all(o.startswith('Global Times') for _, _, o in later): sys.exit(f'the later warnings are not all Global Times items of one year: {later}')
    line = (f'Of the {sm["warns"]} state-media items found that only warn about Nvidia\'s chips, {sm["n_burst"]} date from {mon(sm["first"])} to {mon(sm["last"])}, {sm["last"].year}; '
            f'the {NUMWORD[len(later)]} found later are Global Times items of {yrs[0]}.')
    hit = [c for c in caps if line in c['text']]
    if len(hit) != 1: sys.exit(f'one caption must read: {line}')
    its = ' '.join(hit[0]['items'])
    if f'{sm["n"]} state and Party media items' not in its or f'[{sm["first_id"]}]' not in its or f'[{sm["last_id"]}]' not in its: sys.exit('the source line of the state-media count must give the count of items and cite the first and the last of the warnings')
    if not all(f'[{sid}]' in its for _, sid, _ in later): sys.exit('the source lines of the state-media count must cite each later warning')
    # fork OUTB, Nov 25, 2026 (after core edit 8): the source line itself states the count of the burst and how many of its items bear the first date;
    # both are taken from the table here (the recount of that day moved 11 to 16 and left 'the 11 run from' standing in the line, on screen)
    n_first = sum(1 for r in L.tsv('state_media_items.tsv') if r['stance'] == 'warns' and r['date'] == sm['first'].isoformat())
    want_run = f'the {sm["n_burst"]} run from {mon(sm["first"])}, {sm["first"].year}' + (f' ({NUMWORD[n_first]} items that day' if n_first > 1 else '')
    if want_run not in its: sys.exit(f'the source line of the state-media count must read: {want_run} ...')
    if f'the {sm["n_burst"] + 1} run from' in its: sys.exit('control failed: a wrong count of the burst was found in the source line')
    if 'a sample and not a full count' not in its: sys.exit('the source line of the state-media count must say that the later items are a sample and not a full count')     # touch-up 6b (Nov 24, 2026), item 21
    # the argument must give the same counts (its answer and point 4)
    # touch-up 6b (Nov 24, 2026): the answer no longer carries the counts; point 18 does, in these words, and the caveat reads as below
    want_arg = (f'{sm["n_burst"]} of the {sm["warns"]} that only warn about Nvidia\'s chips are dated {mon(sm["first"])} to {mon(sm["last"])}, {sm["last"].year}',
                f'Of {sm["n"]} state and Party media items on Nvidia chips found', f'The {NUMWORD[len(later)]} found later are Global Times items of {yrs[0]}', 'a sample of what these outlets printed and not a full count')
    if not all(x in arg for x in want_arg): sys.exit(f'the argument no longer gives these counts of the state-media table: {[x for x in want_arg if x not in arg]}')
    assert f'{sm["n_burst"] + 1} of the {sm["warns"]} that only warn' not in arg, 'control: a wrong count must not be found in the argument'
    out.append(f'state media: {sm["warns"]} of {sm["n"]} items only warn; {sm["n_burst"]} of them {sm["first"]} to {sm["last"]}, {len(later)} later ({", ".join(str(d) for d, _, _ in later)}, all Global Times) '
               f'(counted here, equal to caption {hit[0]["k"]} and to the argument)')
    return out, pages


def main():
    # 1. the captions document: every quotation checked, or nothing goes on
    r = subprocess.run([sys.executable, '-I', str(L.SCRIPTS / 'cn_doc_build.py'), str(HERE / 'captions_base.txt'), '--refs', str(HERE / 'extra_refs.tsv'), '--title', DOC_TITLE, '--eyebrow', DOC_EYEBROW], capture_output=True, text=True)
    print('cn_doc_build.py:', (r.stdout.strip().splitlines() or ['(no output)'])[-1])
    if r.returncode != 0:
        print(r.stdout, r.stderr); sys.exit('the captions document did not pass its checks; nothing built')
    # 2. the same captions, with the same numbering, for the page
    B.load_clip(); refs = load_all_refs()
    lines = (HERE / 'captions_base.txt').read_text(encoding='utf-8').splitlines()
    bad, order, nq, nh = B.check(lines, refs, need_all=False)
    if bad: sys.exit('captions_base.txt: ' + '; '.join(bad[:3]))
    num = {sid: n for n, sid in enumerate(order, 1)}
    caps, md = read_captions(lines, num), read_md()
    if len(caps) < 8: sys.exit(f'only {len(caps)} captions')
    mine = [dict(k=c['k'], title=c['title'], text=plain(c['text'], num), items=[plain(i, num) for i in c['items']]) for c in caps]
    if mine != md: sys.exit('the captions read from the base file differ from captions.md')
    for c in caps:
        if not c['items']: sys.exit(f'caption {c["k"]} names no source')
        cells(c)                                         # stops if a line is neither a source line nor a number cell
    # 3. substance
    notes, pages = check_substance(caps)
    # 4. the strip
    evs, checks, G = L.load_events()
    print('figure check:', L.check_against_figure(evs))
    n_q = L.write_quotes(HERE / 'quotes.tsv', L.strip_quotes(evs, checks), 'Idea 24, the explainer: the source words behind every mark, label and dashed line of the strip. (The captions are checked through captions_base.txt.)')
    print('cn_has.py:', L.run_has(HERE / 'quotes.tsv'), f'({n_q} lines in quotes.tsv)')
    n_t = L.template_has(' '.join(L.HEADLINE), *L.KEY_SENTENCES)
    # 5. chapters and timing
    new, again = assign(evs)
    by_n = {e['n']: e for e in evs}
    all_words = lambda c: words(c['text']) + sum(words(i) for i in c['items'])
    up = lambda w, rate: -(-w * FPS * 10 // int(rate * 10))             # words / rate seconds, rounded up to a whole frame
    n_fr, edges = 0, [0.0]
    for c in caps:
        n_fr += max(up(read_words(c), RATE), up(all_words(c), BOX_RATE))
        edges.append(n_fr / FPS)
    frames = n_fr; TOTAL = frames / FPS
    pace = lambda c, t0, t1: f'{t1 - t0:5.2f} s; caption {words(c["text"])} words, counted {read_words(c)} ({read_words(c) / (t1 - t0):.2f} a second); with source lines {all_words(c)} ({all_words(c) / (t1 - t0):.1f} a second)'
    dur = lambda c: edges[c['k']] - edges[c['k'] - 1]
    assert all(read_words(c) / dur(c) <= RATE + 1e-9 and all_words(c) / dur(c) <= BOX_RATE + 1e-9 for c in caps), 'a chapter asks for more words a second than the two rules allow'
    assert all(read_words(c) / (dur(c) - 0.5) > RATE or all_words(c) / (dur(c) - 0.5) > BOX_RATE for c in caps), 'control: every chapter cut by half a second must break a rule'
    marks = {e['n']: dict(n=e['n'], x=round(e['x'], 2), cy=round(e['cy'], 2), on=None, pulse=[], focus=[]) for e in evs}
    segs, chapters, rows, report = [], [], {k: [] for k in L.ORDER}, []
    for c in caps:
        k, t0, t1 = c['k'], edges[c['k'] - 1], edges[c['k']]
        last = k == len(caps)
        chapters.append(dict(k=k, t0=t0, t1=t1))
        fresh = sorted(n for n, ch in new.items() if ch == k)
        lit = sorted(marks) if last else sorted(set(again.get(k, [])) - set(fresh))
        if last and fresh: sys.exit('the last chapter lights every mark again; chapters.tsv must not give it new marks')
        if not fresh + lit: sys.exit(f'chapters.tsv gives chapter {k} no marks')
        xs_all = [by_n[n]['x'] for n in fresh + lit]
        xs, xe = max(L.GL, min(xs_all) - 40), max(xs_all)
        ta = t0 + (1.4 if k == 1 else 0.9); span = max(2.5, min(6.0, 0.4 * (t1 - t0)))
        at = lambda x: round(ta + (x - xs) / (xe - xs) * span, 4)
        segs.append(dict(t0=ta, t1=round(ta + span, 4), x0=round(xs, 2), x1=round(xe, 2)))
        for n in fresh:
            t = at(by_n[n]['x']); marks[n].update(on=t); marks[n]['pulse'].append(t); marks[n]['focus'].append([t, t1])
        for n in lit:
            t = at(by_n[n]['x']); marks[n]['pulse'].append(t); marks[n]['focus'].append([t, 1e9 if last else t1])
        lanes = sorted({by_n[n]['lane'] for n in fresh + lit})
        if len(lanes) <= 2:
            for ln in lanes: rows[ln].append([t0 + 0.3, t1])
        assert ta + span < t1 - 1.5, (k, ta + span, t1)
        report.append(f'  {k}. {pace(c, t0, t1)}: ' + (f'every mark lit again' if last else f'{len(fresh)} new marks {fresh}' + (f', lit again {lit}' if lit else '')))
    assert all(m['on'] is not None for m in marks.values())
    scene = dict(fps=FPS, frames=frames, total=len(evs), dim=DIM, geom=L.geom_json(), marks=[marks[n] for n in sorted(marks)], flags=[dict(i=i, on=-1) for i in range(len(L.FLAGS))],
                 segs=segs, chapters=chapters, rows=rows, tally_on=1e9)
    # 6. the page
    cl = L.card_layout(G, PAD)
    cap_y = CARD_TOP + cl['card_h'] + 6; cap_h = 720 - 23 - cap_y
    css = EXTRA_CSS
    for k, v in (('CARD_TOP', CARD_TOP), ('PAD', PAD), ('CARD_H', cl['card_h']), ('SVG_W', cl['svg_w']), ('SVG_H', cl['svg_h']), ('KEY_L', cl['key_left']), ('KEY_W', cl['key_w']),
                 ('COUNT_L', cl['key_left'] + 11), ('CAP_Y', cap_y), ('CAP_H', cap_h)):
        css = css.replace(f'%%{k}%%', str(v))
    assert '%%' not in css
    stage = f"""<h1 id="h1">{esc(' '.join(L.HEADLINE))}</h1>
<div class="clock" id="clockbox"><div id="date"></div></div>
<div class="card" id="card">
{L.strip_svg(evs, G)}
{L.KEY}
<div id="count"></div>
</div>
<div class="card" id="capbox">
{chr(10).join(caption_html(c, len(caps), num, refs) for c in caps)}
</div>
<p class="draft" id="draft">Small numbers: the references of the captions document. English renderings of Chinese are ours, not official translations. Draft by Claude, Anthropic’s model.</p>
<div id="bar"></div>"""
    # round 10 (the session's ruling, Nov 25, 2026): the frame carries the credit only; words saying the copy is local or
    # unpublished are untrue of a public copy, and a release cannot reach pixels. They must never be drawn into the frame.
    # round 11 (the session's ruling, Nov 26, 2026): that note stands nowhere, pixels included: not in the frame, not in the page
    # below it, not in the captions document. OLD_NOTE is spelled in two parts so that no public copy of this file holds it.
    OLD_NOTE = 'Local; not ' + 'published.'
    def frame_says_local(st):                     # the credit line names no local or unpublished state; nothing in the frame says "not published" or "Local;"
        draft = re.search(r'<p class="draft" id="draft">(.*?)</p>', st, re.S).group(1).lower()
        return [w for w in ('local', 'publish') if w in draft] + [w for w in ('not published.', 'local;') if w in st.lower()]   # caption 4 says "not published policy": that stays
    if frame_says_local(stage): sys.exit(f'the frame says {frame_says_local(stage)}: it carries the credit only')
    assert frame_says_local(stage.replace('model.</p>', f'model. {OLD_NOTE}</p>')), 'control: the old credit line must be refused'
    below = f"""  <p>A silent explainer of {int(TOTAL // 60)} minutes {round(TOTAL % 60)} seconds: the dated strip in {len(caps)} chapters. Each caption stays on screen while the marks it speaks of appear in date order. This page draws any moment of it; the video beside it was captured from this page frame by frame. No one has yet watched the video play through: it was checked by script and as still frames.</p>
  <p>The video file, <code>explainer.mp4</code> (1280 by 720, no sound, no voice):</p>
  <video data-src="explainer.mp4" controls muted playsinline preload="metadata" width="1280" height="720"></video>
  <p>The captions as a checked text, with the list of sources: <a href="captions.html">captions.html</a>.</p>
  <p class="small">Draft by Claude, Anthropic’s model.</p>"""
    says = [n for n, x in (('the page', stage + below), ('captions.md', (HERE / 'captions.md').read_text(encoding='utf-8')), ('captions.html', (HERE / 'captions.html').read_text(encoding='utf-8'))) if 'local; not' in x.lower()]
    if says: sys.exit(f'{says} say the copy is local or not published: the credit only (round 11)')
    assert 'local; not' in (below + OLD_NOTE).lower(), 'control: the old note must be seen'
    (HERE / 'explainer.html').write_text(L.page('Chip Policy Explainer', stage, below, scene, css), encoding='utf-8')
    slug = lambda s: re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')
    ends = [frames - 1 if c['k'] == len(caps) else round((edges[c['k']] - 0.6) * FPS) for c in caps]
    stills = [['00_first', 0]] + [[f'{c["k"]:02d}_{slug(c["title"])}', f] for c, f in zip(caps, ends)]          # the first frame, then one frame for each caption (the last is the last frame)
    expect = [dict(frame=f, k=m['k'], title=m['title'], text=m['text'], items=m['items']) for m, f in zip(md, ends)]
    plan = dict(page='explainer.html', fps=FPS, frames=frames, mp4='explainer.mp4', master=None, crf=16, gif=None, webp=None, stills=stills, expect=expect)
    hk = next(e for e in evs if e['sid'] == 'cn-clips-evidence-1' and e['C'])
    plan['label_control'] = dict(id=f'c{hk["n"]}', x=round(evs[0]['x'], 1), y=round(evs[0]['cy'] + 4, 1))     # the control: this label, set down on mark 1, must be reported
    plan['made_from'] = L.made_from(HERE, [L.FIG / 'figure_data.txt', L.FIG / 'figure_events.tsv', L.FIG / 'beijing_vs_labs.html', L.FIG / 'template.html', L.PROJ / 'ARGUMENT_referenced.md',
                                           L.PROJ / 'tables' / 'house_licence_table.tsv', L.PROJ / 'tables' / 'state_media_items.tsv', HERE.parent / 'a7lib.py', HERE / 'build.py',
                                           HERE / 'captions_base.txt', HERE / 'extra_refs.tsv', HERE / 'captions.md', HERE / 'chapters.tsv', HERE / 'quotes.tsv', HERE / 'explainer.html'])
    (HERE / 'capture.json').write_text(json.dumps(plan, indent=1, ensure_ascii=False), encoding='utf-8')
    print(f'captions: {len(caps)}, equal to captions.md; {len(order)} sources cited; quotations checked {nq}, hidden statements {nh}; policy pages counted {pages}; {n_t} sentences of the headline and key stand in figure/template.html')
    for x in notes: print('substance:', x)
    print(f'records {len(evs)}: each is new in exactly one chapter (checked). Chapters:')
    print('\n'.join(report))
    print(f'layout: strip drawn at {cl["scale"]:.3f} of the figure\'s size, card {cl["card_h"]} px high, caption box {cap_h} px high from y {cap_y}')
    print(f'timing: {frames} frames at {FPS} a second = {frames / FPS:.2f} s ({int(TOTAL // 60)} min {TOTAL % 60:.2f} s); no chapter over {RATE} words a second for its caption or {BOX_RATE} for all its words (checked, with a control); words in captions {sum(words(c["text"]) for c in caps)}, in source lines and cells {sum(words(i) for c in caps for i in c["items"])}')
    print('written', HERE / 'explainer.html', 'and capture.json; stills planned at frames', [s[1] for s in stills])


main()
