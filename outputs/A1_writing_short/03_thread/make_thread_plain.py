#!/usr/bin/env python3
"""Idea 3: build the thread and write its plain-text form, from one checked text (thread_base.txt).

Run: python3 -I make_thread_plain.py
1. Builds thread.md and thread.html with scripts/cn_doc_build.py (every quotation and hidden statement is checked
   against the saved copies). If that build fails, nothing else is written.
2. Takes the numbered posts under "## The posts" in thread_base.txt, removes the reference marks, numbers them k/N,
   and writes thread_plain.txt: each post, then its source's address on its own line, then a note on images.
3. Counts the characters of each post as it would be pasted (with its "k/N " number) two ways and writes
   char_counts.tsv: plain characters (Unicode code points), and X's weighted count as I know its published rule
   (twitter-text: code points U+0000 to U+10FF, U+2000 to U+200D, U+2010 to U+201F and U+2032 to U+2037 count 1,
   every other one counts 2, after NFC; an address would count 23, and the posts hold none). That rule is from my
   general knowledge, not from a saved page. Stops with exit 1 if a post is over 280 by either count, if the
   thread is not 8 to 10 posts, or if an image named in the note is missing.
"""
import re, struct, subprocess, sys, unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parents[2]
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / 'scripts'))
import cn_argument_build as B

BASE = HERE / 'thread_base.txt'
LIMIT = 280
IMAGES = {1: PROJ / 'figure' / 'beijing_vs_labs_top.png', 5: PROJ / 'figure' / 'beijing_vs_labs_strip.png'}   # post 5 is limit 1 (not one actor)
N_REC = sum(1 for ln in (PROJ / 'figure' / 'figure_events.tsv').read_text(encoding='utf-8').splitlines()[1:] if ln.strip())   # counted, not typed
# Round 10b (Nov 25, 2026): the count of sources is the argument's own last build line (atlas/core_edit/hand_out/ARGUMENT_FINAL.txt, the last
# line beginning 'argument:'), as outputs/ROUND10.md asks; argument_refs.tsv alone no longer gives it (the argument also cites a row of
# argument_refs_more.tsv). Control: the built argument page must list the same number of references.
_fin = [ln for ln in (PROJ / 'atlas' / 'core_edit' / 'hand_out' / 'ARGUMENT_FINAL.txt').read_text(encoding='utf-8').splitlines() if ln.startswith('argument: ')]
if not _fin: sys.exit('ARGUMENT_FINAL.txt holds no line beginning "argument: "')
N_SRC = int(re.match(r'argument: (\d+) sources', _fin[-1]).group(1))
N_LISTED = len(re.findall(r'<li id="ref-\d+"', (PROJ / 'ARGUMENT_referenced.html').read_text(encoding='utf-8')))
if N_LISTED != N_SRC: sys.exit(f'the argument\'s last build line says {N_SRC} sources but ARGUMENT_referenced.html lists {N_LISTED}')
N_REFS_TSV = sum(1 for ln in (PROJ / 'argument' / 'argument_refs.tsv').read_text(encoding='utf-8').splitlines() if ln.strip() and not ln.startswith('#'))
N_PTS = sum(1 for ln in (PROJ / 'argument' / 'argument_base.txt').read_text(encoding='utf-8').splitlines() if re.match(r'\d+\. ', ln))
_arg = (PROJ / 'argument' / 'argument_base.txt').read_text(encoding='utf-8')
_m = re.search(r'(?ms)^## 5\. (\w+) limits on the claim$(.*?)^## ', _arg)          # the argument's own section of limits
if not _m: sys.exit('the argument has no section "## 5. ... limits on the claim"')
LIMIT_WORD = _m.group(1).lower()                                                   # "five"
N_LIM = len(re.findall(r'(?m)^\d+\. ', _m.group(2)))                               # its numbered points, counted
WHY = {1: f'the whole picture at a glance: the headline, the dated strip of {N_REC} records in four rows, the H200 in reported numbers, Nvidia\'s share, and Nvidia\'s own revenue from customers based in China',
       5: 'the dated strip alone: its two top rows show Beijing holding Nvidia back and Beijing letting Nvidia in, which is the point of this post'}


def weighted(s):
    s = unicodedata.normalize('NFC', s)
    one = lambda c: c <= 0x10FF or 0x2000 <= c <= 0x200D or 0x2010 <= c <= 0x201F or 0x2032 <= c <= 0x2037
    return sum(1 if one(ord(ch)) else 2 for ch in s)


def png_size(p):
    with open(p, 'rb') as f: head = f.read(24)
    if head[:8] != b'\x89PNG\r\n\x1a\n': sys.exit(f'not a PNG: {p}')
    return struct.unpack('>II', head[16:24])


def main():
    p = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts' / 'cn_doc_build.py'), str(BASE), '--title', 'Chip Policy Thread',
                        '--eyebrow', 'China chip policy · a thread of ten posts'], capture_output=True, text=True)
    print(p.stdout.strip())
    if p.returncode != 0:
        print(p.stderr.strip()); sys.exit('cn_doc_build.py did not pass: thread_plain.txt NOT written')

    refs = B.load_refs()
    posts, on = [], False
    for ln in BASE.read_text(encoding='utf-8').splitlines():
        if ln.startswith('## '): on = ln.strip() == '## The posts'; continue
        m = re.match(r'(\d+)\. (.*)', ln)
        if on and m:
            ids = B.CITE.findall(m.group(2))
            text = re.sub(r'\s+', ' ', B.CITE.sub('', m.group(2))).strip()
            posts.append((int(m.group(1)), text, ids))
    n = len(posts)
    if [k for k, _, _ in posts] != list(range(1, n + 1)): sys.exit('posts are not numbered 1..N in order')
    if not 8 <= n <= 10: sys.exit(f'{n} posts: the thread must be 8 to 10')
    word = {8: 'Eight', 9: 'Nine', 10: 'Ten'}[n]              # the count written in the deck must be the count of posts
    if f'@deck {word} posts' not in BASE.read_text(encoding='utf-8'): sys.exit(f'the deck does not say "{word} posts", but there are {n}')
    said = f'The full argument has {N_PTS} points and {N_SRC} sources'      # the counts written in the text must be the counts of the argument's files
    if said not in BASE.read_text(encoding='utf-8'): sys.exit(f'thread_base.txt does not say "{said}" (counted from argument_base.txt and argument_refs.tsv)')
    if {'four': 4, 'five': 5, 'six': 6}.get(LIMIT_WORD) != N_LIM: sys.exit(f'the argument\'s heading says {LIMIT_WORD} limits but its section holds {N_LIM} points')
    if f'with {LIMIT_WORD} limits' not in posts[0][1]: sys.exit(f'post 1 does not say "with {LIMIT_WORD} limits" (the argument has {N_LIM})')
    labelled = [k for k in range(1, N_LIM + 1) if sum(1 for _, t, _ in posts if t.startswith(f'Limit {k}')) == 1]
    if labelled != list(range(1, N_LIM + 1)): sys.exit(f'the posts must name Limit 1 to Limit {N_LIM} once each; found {labelled}')
    if not posts[4][1].startswith('Limit 1'): sys.exit('the strip image is set for post 5, which must be limit 1')
    for k, img in IMAGES.items():
        if not img.exists(): sys.exit(f'image missing: {img}')
        if k > n: sys.exit(f'image note names post {k}, but there are {n} posts')

    out = ['Thread: did Beijing pull against its own AI companies?', '',
           "Draft by Claude, Anthropic's model. Nothing here has been posted.",      # round 11 (Nov 26, 2026): the session's ruling, no ""
           f'{n} posts. Every quotation was found in the saved copy of its source before this text was written.',
           'Each post that cites a source is followed by its address on its own line; the last post sums up and has none. The address is not part of the post.',      # round 12 (Nov 26, 2026): the last post has no address
           'Words between quotation marks are a source\'s exact words. English given for a Chinese source is ours, not an official translation.',
           'Post 1 quotes the clip twice: the first sentence from a machine transcript (at 0:11), the second from the text of the post that carries the clip. Post 9 quotes a video\'s caption track (at 5:59). Nobody has checked any of them by ear.', '']
    counts, over = [], []
    for k, text, ids in posts:
        if 'http' in text: sys.exit(f'post {k} holds an address; the count would be wrong')
        full = f'{k}/{n} {text}'
        c_plain, c_x = len(full), weighted(full)
        counts.append((k, len(text), c_plain, c_x, LIMIT - max(c_plain, c_x)))
        if max(c_plain, c_x) > LIMIT: over.append(k)
        out.append(full)
        addrs = [B.address(i, refs[i]) for i in ids]
        if any(not a for a in addrs): sys.exit(f'post {k}: a source has no address')
        addrs = list(dict.fromkeys(addrs))                      # the clip and the post that carries it have one address
        out += addrs if addrs else [f'(No address: this post sums up the posts before it. The full argument, with {N_SRC} sources, is the project\'s argument page, ARGUMENT_referenced.html.)']
        out.append('')
    out += ['Which image goes with which post', '',
            'Two images go with this thread.']
    for k, img in sorted(IMAGES.items()):
        w, h = png_size(img)
        out.append(f'Post {k}/{n}: {img.relative_to(PROJ)} in the project\'s files ({w} by {h} pixels). Why: {WHY[k]}.')
    rest = ', '.join(str(k) for k in range(1, n + 1) if k not in IMAGES)
    out += [f'Posts {rest}: no image.',
            'The first image is taller than it is wide, so a preview may show only part of it until it is opened. The mark numbers in both images are the figure\'s own, not the post numbers.', '',
            'Character counts', '',
            f'Each post was counted with its number in front (for example "1/{n} "), as it would be pasted. The limit is {LIMIT}.',
            'post | characters | X weighted count | room left']
    out += [f'{k}/{n} | {c} | {x} | {room}' for k, _, c, x, room in counts]
    print(f'argument, counted by script: {N_PTS} points, {N_SRC} sources (its last build line; {N_LISTED} references on its page; {N_REFS_TSV} rows in argument_refs.tsv), {N_LIM} limits; figure: {N_REC} records')
    print(f'thread: {n} posts; characters with the number in front (plain / X weighted):')
    for k, _, c, x, room in counts: print(f'  {k}/{n}: {c} / {x}  (room left {room})')
    print(f'longest post: {max(c for _, _, c, _, _ in counts)} characters; limit {LIMIT}')
    if over: sys.exit(f'OVER {LIMIT}: posts {over}; thread_plain.txt and char_counts.tsv NOT written')
    (HERE / 'thread_plain.txt').write_text('\n'.join(out) + '\n', encoding='utf-8')
    (HERE / 'char_counts.tsv').write_text('post\tcharacters_without_number\tcharacters_with_number\tx_weighted_with_number\troom_left_of_280\n'
                                          + '\n'.join('\t'.join(map(str, c)) for c in counts) + '\n', encoding='utf-8')
    # control: the counter can exceed the limit and counts wide characters double
    assert weighted('中' * 141) == 282 and len('a' * 281) > LIMIT
    print('control: a 281-character line is over the limit, and 141 Chinese characters weigh 282')


if __name__ == '__main__':
    main()
