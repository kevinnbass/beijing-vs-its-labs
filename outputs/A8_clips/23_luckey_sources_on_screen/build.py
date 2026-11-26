#!/usr/bin/env python3
"""Build Luckey's 56 seconds with the sources on screen (idea 23): a local video file with burned-in captions.

Run: python3 -I build.py            (everything)      python3 -I build.py --no-video   (checks and captions.ass only)
Reads   ../40_checked_by_ear/compared.json   the first speech pass's words and times, cut into parts (L1 ... L8)
        bands.txt                             the lower band: verdict and source line for each part (hand-written)
        lines.tsv                             where each line of the upper band starts (the words come from the speech pass)
        the saved video, research/primary/cnpol-x-overton-video-2123392702821580811/body.bin (read only)
        the saved post, research/primary/cnpol-x-overton-2123392702821580811 (its date; and the one line of the upper band
        that is shown from the post's text and not from the speech pass: see FROM_POST)
Writes  quotes.tsv            every source line and transcript line shown, for scripts/cn_has.py
        captions.ass          the subtitle file ffmpeg burns in
        luckey_with_sources.mp4
        stills/still_1 ... still_9 (.png, 1600 x 900): one for each state of the lower band (round 4; six before, with a sheet of three)
Order: checks first. If a quotation in bands.txt has no "!!" line, or scripts/cn_has.py does not find every line of
quotes.tsv in its saved copy (exit 0 required), nothing more is written. ffmpeg runs at low priority on 4 threads.
The picture is the clip as posted, made smaller, with its sound unchanged. A LOCAL FILE FOR THE OWNER'S OWN USE: NOT TO BE POSTED.
Round 7 (Nov 24, 2026, builder OB10): the project leaves out the words of part L6b (the session's ruling; compared.json
carries that part as "left_out", with the bracket in place of its words). The upper band shows only the bracket there, with
no label; quotes.tsv leaves the part out; the lower band is empty (bands.txt); "Read with care" says that stretch is left
out; and a box in the page's surface colour, holding the same bracket, covers the clip's own burned-in captions in the
picture for CAPTION_COVER (found frame by frame: tmp_work/ob10/strip_43.png ... strip_47.png). After the video is written,
cover_check() reads frames of it and stops the build if a caption's white shows inside the box while it is on, with a
control that the same test finds the caption in the clip itself and in the video once the box is off. The sound is copied
unchanged, as before.
Round 7, second part (OB10, at the coordinator's word that the ruling covers sound too): the sound of the same stretch,
CAPTION_COVER, is silent. ../40_checked_by_ear/cut_copies.py (the one place this is done, also for the listening sheet's
copies) decodes the clip's sound to 16-bit samples, sets the stretch to zero and writes a WAV; ffmpeg stores it
losslessly (FLAC) in the video. After the video is written, cut_copies.check_sound() stops the build unless every sample
in the stretch is 0 (controls: the clip's same stretch and the two seconds before it in the new video are not silent) and
every sample before and after it equals the clip's own decoded sample (control: a shift of one sample is seen).
cut_copies.check_edges() first checks that the left-out line lies inside the stretch and that no word of the second
pass runs across its edges. "Read with care" says the stretch is left out in picture and sound.
"""
import csv, json, re, subprocess, sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]                                   # .
PROJ = HERE.parents[2]                                   # research/cn_chip_policy_20261120
PRIMARY = ROOT / 'research' / 'primary'
VIDEO_ID, POST_ID = 'cnpol-x-overton-video-2123392702821580811', 'cnpol-x-overton-2123392702821580811'
SRC = PRIMARY / VIDEO_ID / 'body.bin'
DATA = HERE.parent / '40_checked_by_ear' / 'compared.json'
OUT = HERE / 'luckey_with_sources.mp4'
W, H = 1920, 1080
VW, VH, VX, VY = 1088, 612, 416, 64                      # the picture: 16:9, centred under the header
B1Y, B1H, B2Y, B2H = 688, 160, 860, 196                  # the two bands under the picture
PAD = 72
# colours (the figure's dark set), written as ASS wants them: &HBBGGRR&
INK, INK2, MUTED, TOWARD, AWAY = '&HECEFF0&', '&HB7C2C3&', '&H868D8F&', '&HE58739&', '&H2659D9&'
PAGE_HEX, SURFACE_HEX = '0x0d0d0d', '0x1a1a19'
DISC = 'm 12 0 b 18.63 0 24 5.37 24 12 b 24 18.63 18.63 24 12 24 b 5.37 24 0 18.63 0 12 b 0 5.37 5.37 0 12 0'
RING = DISC + ' m 12 3.5 b 7.31 3.5 3.5 7.31 3.5 12 b 3.5 16.69 7.31 20.5 12 20.5 b 16.69 20.5 20.5 16.69 20.5 12 b 20.5 7.31 16.69 3.5 12 3.5'
# Round 4: one full-size still for each of the nine states of the lower band (the brief asked for six).
STILLS = [('L1', 4.0), ('L3', 3.0), ('L4', 2.0), ('L5a', 2.6), ('L5b', 2.0), ('L5c', 3.2), ('L6a', 6.4), ('L6b', 1.0), ('L6b', 3.4), ('L8', 4.0)]   # (part, seconds after its band appears)
# Round 7: the stretch in which the clip's own burned-in captions show the words of the left-out part, found frame by frame
# (tmp_work/ob10/strip_*.png): the first such frame is at 44.50 s and the last at 46.67 s; the frames at 44.46 and 46.71 s
# hold no caption. The box covers 44.44 to 46.70 s. COVER_BOX is in the clip's own pixels (1920 x 1080): the captions stand
# at about x 670 to 1240, y 670 to 740, so the box leaves 40 px or more around them.
# OB10, consistency ruling: the stretch is now 0:44 to 0:49 (parts L6b and L7), 44.44 to 49.27 s, with a wider box (the
# caption words of the longer stretch span x 574 to 1338); why each edge and the box: ../40_checked_by_ear/cut_copies.py.
CAPTION_COVER = (44.44, 49.27)
COVER_BOX = (480, 640, 960, 130)                            # x, y, w, h in the clip's own pixels
CHECK_AT = (44.50, 45.00, 45.50, 45.84, 46.30, 46.67, 47.40, 48.00, 48.60, 49.24)   # inside the cover; the clip shows a caption
CHECK_OFF = 49.36                                           # after the cover: the next sentence's first caption
CTRL = (480, 670, 1150, 749)                                # caption rows left of the chair (which is white in every frame)
SOUND_WAV = HERE / 'tmp_work' / 'sound' / 'luckey_sound_silenced.wav'   # scratch: the clip's sound with CAPTION_COVER silent
sys.path.insert(0, str(HERE.parent / '40_checked_by_ear'))            # python3 -I does not add it
import cut_copies as CC                                               # noqa: E402  (round 7: one place for the silence and its checks)
if (CC.STRETCH['luckey'][1:], CC.COVER['luckey'][0], CC.COVER['luckey'][1], CC.COVER['luckey'][2], CC.CTRL['luckey']) != (CAPTION_COVER, COVER_BOX, CHECK_AT, CHECK_OFF, CTRL):
    sys.exit('STOPPED: the stretch, box or check times here differ from ../40_checked_by_ear/cut_copies.py')
TABLE = PROJ / 'tables' / 'house_licence_table.tsv'
FONT_DIR = Path('/usr/share/fonts/opentype/inter')
SRC_SIZES = (38, 36, 34, 32, 30)        # the lower line's type size; the first at which it fits in three lines is used
RIGHT_LABEL = 'WHAT THE SAVED RECORD SAYS'
# Round 2 (core change 3): the first speech pass has no word between Luckey's two main sentences; the text of the post and a
# second speech pass have "Like" there. So the second sentence is shown from the text of the post, not from the first pass.
FROM_POST = {'L4': 'there are Chinese companies that want to buy Nvidia GPUs'}     # part -> words to find in the post's text
LABEL = 'MACHINE TRANSCRIPT · NOT CHECKED BY EAR'
LABEL_POST = 'THE TEXT OF THE POST, NOT THE SPEECH PROGRAM · NOT CHECKED BY EAR'
QUOTE = re.compile(r'"([^"]+)"')
# who is who, for a newcomer: (saved id, the line shown, the words in the saved copy that carry it)
WHO = [('cnpol-x-overton-2123392702821580811', 'Palmer Luckey is the founder of Anduril.', 'Anduril founder Palmer Luckey'),
       ('cn-clips-singju-luckey', '“Jensen” is Jensen Huang of Nvidia.', 'Jensen Huang’s ouster at Nvidia')]
MARK = re.compile(r'\[(solid|open)(?: (away|toward))?\] ?')


def squash(s):
    return re.sub(r'[\s"\'’‘“”]+', '', s).lower()


def run(cmd, **kw):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if r.stdout.strip(): print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr.strip()[-1500:]); sys.exit(f'STOPPED: {" ".join(str(c) for c in cmd[:3])} ... exit {r.returncode}')
    return r.stdout


def ts(t):
    t = max(0.0, t); cs = int(round(t * 100)); h, cs = divmod(cs, 360000); m, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f'{h}:{m:02d}:{s:02d}.{cs:02d}'


def clock(t):
    return f'{int(t // 60)}:{int(t % 60):02d}'


def mark(kind, colour):
    return '{\\p1\\1c' + colour + '}' + (DISC if kind == 'solid' else RING) + '{\\p0\\1c' + INK + '} '


def show(text):
    """Band text for the screen: marks drawn, straight double quotes made curly."""
    text = MARK.sub(lambda m: mark(m.group(1), {'away': AWAY, 'toward': TOWARD, None: INK}[m.group(2)]), text)
    return QUOTE.sub(lambda m: '“' + m.group(1) + '”', text)


def table_numbers():
    """Nvidia's chips marked "Approved, not shipped" in the project's copy of the licence table (BIS's, released by the House
    Foreign Affairs Committee on Nov 19, 2026), tied to the
    one total the committee's saved summary states (879,868 chips in 21 applications, Nvidia's and AMD's together)."""
    rows = list(csv.DictReader((l for l in TABLE.read_text(encoding='utf-8').splitlines() if not l.startswith('#')), delimiter='\t'))
    n = lambda r: int(r['chip_count'].replace(',', ''))
    ok = [r for r in rows if r['status'].startswith('Approved')]
    if any(r['status'] != 'Approved, not shipped' for r in ok): sys.exit('STOPPED: an approved application is not marked "Approved, not shipped"')
    if sum(n(r) for r in ok) != 879868 or len(ok) != 21: sys.exit('STOPPED: the approved rows no longer make the 879,868 chips in 21 applications of the summary')
    nv = [r for r in ok if r['exporter'] == 'Nvidia']
    if any(r['location'] != 'China' for r in nv): sys.exit('STOPPED: an approved Nvidia application is not for a place in China')
    return {'NV_APPROVED': f'{sum(n(r) for r in nv):,}'}


def face(size, bold=False):
    """The Inter face as libass sets it: the nominal size is the height from ascender to descender, not the em."""
    from PIL import ImageFont
    path = str(FONT_DIR / ('Inter-Bold.otf' if bold else 'Inter-Regular.otf'))
    asc, desc = ImageFont.truetype(path, 1000).getmetrics()
    return ImageFont.truetype(path, size * 1000 / (asc + desc))


def width(text, size, bold=False, spacing=0.0):
    return face(size, bold).getlength(text) + spacing * len(text)


def lines_needed(text, size, room):
    """How many lines the lower band's text takes at this size (greedy wrapping, as WrapStyle 1 does; a mark is 24 px wide)."""
    f, n, cur = face(size), 1, 0.0
    space = f.getlength(' ')
    for word in MARK.sub('\x01 ', text).split():
        w = 24.0 if word == '\x01' else f.getlength(QUOTE.sub(lambda m: '“' + m.group(1) + '”', word).replace('"', '”'))
        if cur and cur + space + w > room: n, cur = n + 1, w
        else: cur = cur + (space if cur else 0) + w
    return n


def load_bands(units, duration, policy_pages):
    bands, cur = [], None
    for ln in (HERE / 'bands.txt').read_text(encoding='utf-8').splitlines():
        if ln.startswith('#') or not ln.strip(): continue
        if ln.startswith('@ '):
            head, tag = [x.strip() for x in ln[2:].split('|', 1)]
            part, _, plus = head.partition(' ')
            if part not in units: sys.exit(f'bands.txt: no part named {part}')
            cur = {'part': part, 'start': units[part]['start'] + (float(plus) if plus else 0.0), 'tag': tag, 'text': '', 'checks': []}
            bands.append(cur)
        elif ln.startswith('!!'):
            sid, words = [x.strip() for x in ln[2:].split('|', 1)]; cur['checks'].append((sid, words))
        else:
            cur['text'] = (cur['text'] + ' ' + ln.strip()).strip()
    bands[0]['start'] = 0.0
    for a, b in zip(bands, bands[1:]):
        if b['start'] <= a['start']: sys.exit('bands.txt: entries are not in the order of the clip')
        a['end'] = b['start']
    bands[-1]['end'] = duration
    for b in bands:
        b['text'] = b['text'].replace('{POLICY_PAGES}', str(policy_pages))
        if '{NV_APPROVED}' in b['text']: b['text'] = b['text'].replace('{NV_APPROVED}', table_numbers()['NV_APPROVED'])
        if '{' in b['text'] or '}' in b['text']: sys.exit(f'bands.txt: {b["part"]}: a brace is left in the text')
        for q in QUOTE.findall(b['text']):
            if not any(squash(q) in squash(w) for _, w in b['checks']): sys.exit(f'bands.txt: {b["part"]}: the quotation has no "!!" line: {q[:60]}')
        room = W - 2 * PAD
        fit = [sz for sz in SRC_SIZES if lines_needed(b['text'], sz, room) <= 3]
        if not fit: sys.exit(f'bands.txt: {b["part"]}: the text does not fit in three lines even at size {SRC_SIZES[-1]}')
        b['size'], b['lines'] = fit[0], lines_needed(b['text'], fit[0], room)
        gap = room - width(b['tag'], 23, True, 1.5) - width(RIGHT_LABEL, 23, True, 1.5)
        if gap < 40: sys.exit(f'bands.txt: {b["part"]}: the verdict line is too long ({gap:.0f} px left before the label on the right; 40 needed)')
        b['gap'] = gap
    return bands


def chunks(units, duration, post_text):
    """The upper band: the transcript in short lines. lines.tsv says at which word each line starts."""
    starts = [float(l) for l in (HERE / 'lines.tsv').read_text(encoding='utf-8').splitlines() if l.strip() and not l.startswith('#')]
    words = [dict(w, part=u['id']) for u in units.values() if u['in_transcript'] for w in u['words']]
    at = {round(w['s'], 2) for w in words}
    for t in starts:
        if round(t, 2) not in at: sys.exit(f'lines.tsv: no word of the first pass starts at {t}')
    for u in units.values():
        if u['in_transcript'] and round(u['start'], 2) not in {round(t, 2) for t in starts}: sys.exit(f'lines.tsv: part {u["id"]} does not start a line')
    out = []
    for w in words:
        if round(w['s'], 2) in {round(t, 2) for t in starts}: out.append({'part': w['part'], 'start': w['s'], 'text': w['w'], 'last': w['e']})
        else: out[-1]['text'] += ' ' + w['w']; out[-1]['last'] = w['e']
    for a, b in zip(out, out[1:]): a['end'] = b['start']
    out[-1]['end'] = min(duration, out[-1]['last'] + 0.6)
    out[0]['start'] = max(0.0, out[0]['start'] - 0.3)
    # Round 7: a part whose words the project leaves out is one line holding only the bracket, and nothing else
    for u in units.values():
        if not u.get('left_out'): continue
        mine = [c for c in out if c['part'] == u['id']]
        if len(mine) != 1 or len(u['words']) != 1 or not (u['text'].startswith('[') and u['text'].endswith(']')) or mine[0]['text'] != u['text']:
            sys.exit(f'STOPPED: the left-out part {u["id"]} must be one line of the upper band holding only the bracket')
        if not (CAPTION_COVER[0] <= u['start'] and u['end'] <= CAPTION_COVER[1]):
            sys.exit(f'STOPPED: the left-out part {u["id"]} ({u["start"]} to {u["end"]} s) runs outside the cover of the picture\'s captions {CAPTION_COVER}')
        mine[0].update(left_out=True, label='')
    if not any(c.get('left_out') for c in out): sys.exit('STOPPED: compared.json no longer marks a left-out part; the cover and the read-with-care line would be wrong')
    letters = lambda t: re.sub(r'[^a-z0-9]', '', t.lower())
    for part, anchor in FROM_POST.items():
        mine = [c for c in out if c['part'] == part]
        if len(mine) != 1: sys.exit(f'{part} must be one line of the upper band to be shown from the post')
        m = re.search(r'[^“”.]*' + re.escape(anchor) + r'[^“”.]*\.', post_text)
        if not m: sys.exit(f'STOPPED: the post no longer holds: {anchor}')
        sentence = m.group(0).strip()
        if letters(mine[0]['text']) not in letters(sentence): sys.exit(f'STOPPED: the post and the first pass differ at {part} by more than a word before the sentence')
        like = [n for n in units['L3']['notes'] if n['witness'] == 'second pass' and n['kind'] != 'spelling only']
        if part == 'L4' and not like: sys.exit('STOPPED: the second pass no longer differs from the first before L4; the read-with-care line would be wrong')
        mine[0].update(text=sentence, src=POST_ID, label=LABEL_POST, first_pass=mine[0]['text'])
    return out


def cover_check():
    """Round 7: read frames of the new video and of the clip. Inside CAPTION_COVER the box must hold no caption white (pixels
    at 230 or more in all three colours); controls: the clip itself shows caption white in the box's place at each of those
    times, and the new video shows it again just after the cover (CHECK_OFF). Stops the build otherwise."""
    from PIL import Image
    d = HERE / 'tmp_work' / 'cover_check'; d.mkdir(parents=True, exist_ok=True)
    bx, by_, bw, bh = COVER_BOX
    ox0, oy0 = VX + bx * VW / 1920, VY + by_ * VH / 1080
    ox1, oy1 = ox0 + bw * VW / 1920, oy0 + bh * VH / 1080
    inner = (int(ox0) + 2, int(oy0) + 2, int(ox1) - 2, int(oy1) - 2)
    cx0, cy0, cx1, cy1 = CTRL
    vctrl = (int(VX + cx0 * VW / 1920), int(VY + cy0 * VH / 1080), int(VX + cx1 * VW / 1920), int(VY + cy1 * VH / 1080))
    def white(png, box):
        b = Image.open(png).convert('RGB').crop(box).tobytes()
        return sum(1 for i in range(0, len(b), 3) if min(b[i], b[i + 1], b[i + 2]) >= 230)
    rows = []
    for t in CHECK_AT + (CHECK_OFF,):
        a, b = d / f'video_{t:.2f}.png', d / f'clip_{t:.2f}.png'
        run(['nice', '-n', '19', 'ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', OUT, '-frames:v', '1', a])
        run(['nice', '-n', '19', 'ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', SRC, '-frames:v', '1', b])
        rows.append((t, white(b, (cx0, cy0, cx1, cy1)), white(a, inner), white(a, vctrl)))
    for t, wc, wv, wa in rows:
        print(f'  cover check {t:.2f} s ({"after the cover" if t == CHECK_OFF else "inside the cover"}): ' + (f'caption white in CTRL: clip {wc}, new video {wa}' if t == CHECK_OFF else f'caption white in CTRL of the clip {wc}; white anywhere in the new video\'s box {wv}'))
    if any(wc < 300 for _, wc, _, _ in rows): sys.exit('STOPPED: control failed: the clip shows no caption at a time where one was found; the check could not see a leak')
    if rows[-1][3] < 50: sys.exit('STOPPED: control failed: after the cover the test finds no caption in the new video')
    if any(wv > 0 for _, _, wv, _ in rows[:-1]): sys.exit('STOPPED: white shows inside the cover of the new video')
    print(f'cover check: no caption white inside the cover at {len(rows) - 1} times; controls behave')


def main():
    data = json.loads(DATA.read_text(encoding='utf-8'))['clips']['luckey']
    units = {u['id']: u for u in data['units']}
    duration = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', SRC]).strip())
    if abs(duration - data['duration']) > 0.1: sys.exit('STOPPED: the video and the speech pass differ in length')
    note = (PROJ / 'NOTE_policies_checked.md').read_text(encoding='utf-8')
    # the policy pages read: an entry counts unless its verdict is PAGE EMPTY; one read in an Internet Archive capture is taken at the
    # capture; a saved page behind several entries counts once (103 entries on 83 saved pages, one empty: 82)
    _docs = []
    for _e in re.split(r'(?m)^### Row ', note)[1:]:
        _m = re.match(r'(\d+) · ([^·]+) · ([^·]+) · \[([^\]]+)\]', _e); _c = re.search(r'- Read in: [^\n]*saved as \[([^\]]+)\]', _e)
        if re.search(r'Verdict: \*\*([^*]+)\*\*', _e).group(1) != 'PAGE EMPTY': _docs.append(_c.group(1) if _c else _m.group(4))
    policy_pages = len(set(_docs))
    raw = (PRIMARY / POST_ID / 'text.txt').read_text(encoding='utf-8')
    tw = json.loads(raw[raw.index('{'):])['tweet']
    d = datetime.strptime(tw['created_at'], '%a %b %d %H:%M:%S %z %Y')
    posted = f'{d.strftime("%b")} {d.day}, {d.year}'
    bands = load_bands(units, duration, policy_pages)
    said = chunks(units, duration, tw['text'])

    q = ['# Every source line and every transcript line the video shows (saved id <TAB> exact words), for scripts/cn_has.py.',
         '# Written by build.py from bands.txt, the first speech pass and (one line of the upper band) the text of the post; do not edit.',
         '# clip-luckey is the machine transcript.']
    for b in bands: q += [f'{sid}\t{words}' for sid, words in b['checks']]
    q += [f'{c.get("src", "clip-luckey")}\t{c["text"]}' for c in said if not c.get('left_out')]   # round 7: a left-out part shows only the bracket
    q.append(f'{POST_ID}\t{tw["created_at"]}')
    q += [f'{sid}\t{words}' for sid, _, words in WHO]
    (HERE / 'quotes.tsv').write_text('\n'.join(q) + '\n', encoding='utf-8')
    run(['python3', '-I', ROOT / 'scripts' / 'cn_has.py', HERE / 'quotes.tsv'])   # exit 0 required: run() stops the build otherwise

    end = ts(duration + 1)
    ev = []
    def add(layer, a, b, style, text, ml=0, mr=0, mv=0): ev.append(f'Dialogue: {layer},{a},{b},{style},,{ml},{mr},{mv},,{text}')
    def at(layer, style, x, y, text, an=7): add(layer, ts(0), end, style, '{\\an%d\\pos(%d,%d)\\q2}%s' % (an, x, y, text))
    # header
    at(1, 'Head', 40, 14, f'Palmer Luckey, {int(duration)} seconds, with the sources on screen')
    at(3, 'Small', W - 40, 20, "Draft by Claude, Anthropic's model.", an=9)   # round 11 (the session's ruling, outputs/ROUND11.md): the credit is only this, in text and in pixels
    # left of the picture: the key
    at(4, 'Tag', 40, 88, 'KEY')
    key = [(132, 'solid', INK, 'On the record: a document,\\Na filing or a named person'), (212, 'open', INK, 'A press report citing\\Nunnamed people'),
           (292, 'solid', AWAY, 'Away from Nvidia chips'), (340, 'solid', TOWARD, 'Toward Nvidia chips')]
    for n, (y, kind, colour, text) in enumerate(key):
        at(5 + 2 * n, 'Side', 40, y + 4, '{\\p1\\1c' + colour + '}' + (DISC if kind == 'solid' else RING) + '{\\p0}')
        at(6 + 2 * n, 'Side', 80, y, text)
    at(12, 'Tag', 40, 404, 'WHO IS WHO')
    add(13, ts(0), end, 'Side', '{\\an7}' + WHO[0][1] + ' ' + WHO[1][1] + f'\\N\\NClip posted on X by @{tw["author"]["screen_name"]} on {posted}.', 40, W - VX + 40, 444)
    # right of the picture: read with care
    at(14, 'Tag', VX + VW + 40, 88, 'READ WITH CARE')
    swapped = [c for c in said if c.get('src')]
    left = [u for u in units.values() if u.get('left_out')]
    care = ('The transcript is a speech program\'s. Nobody has checked it by ear.\\N\\N'
            + ''.join(f'At {clock(c["start"])} the upper line is the text of the post instead: two speech passes differ on a word there.\\N\\N' for c in swapped)
            + (f'From {clock(left[0]["start"])} to {clock(left[-1]["end"])} the words are left out of this project, in picture and sound.\\N\\N' if left else '') +
            'Words between quotation marks are a source\'s own, found in its saved copy by a script.\\N\\N'
            'The large captions inside the picture came with the clip.\\N\\N'
            'Pause to read. A lower line can stay a second or two after the words it answers.')
    add(15, ts(0), end, 'Side', '{\\an7}' + care, VX + VW + 40, 40, 132)
    # upper band: the machine transcript, with a clock
    t0, pos = 0.0, '{\\an7\\pos(%d,%d)\\q2\\1c%s}' % (PAD, B1Y + 14, MUTED)
    for c in [c for c in said if 'label' in c]:                                  # the label says where the line comes from
        if c['start'] > t0: add(16, ts(t0), ts(c['start']), 'Tag', pos + LABEL)  # (round 7: a left-out line has no label)
        if c['label']: add(16, ts(c['start']), ts(c['end']), 'Tag', pos.replace(MUTED, INK) + c['label'])
        t0 = c['end']
    add(16, ts(t0), end, 'Tag', pos + LABEL)
    for s in range(int(duration) + 1):
        add(17, ts(s), ts(min(s + 1, duration + 1)), 'Tag', '{\\an9\\pos(%d,%d)\\q2\\1c%s}%s' % (W - PAD, B1Y + 14, MUTED, clock(s)))
    for c in said: add(18, ts(c['start']), ts(c['end']), 'Said', '{\\an7}' + c['text'], PAD, PAD, B1Y + 48)
    # round 7: over the clip's own captions while they show the left-out words, a box (drawn by ffmpeg) holding the same bracket
    bx, by_, bw, bh = COVER_BOX
    sx, sy = VW / 1920, VH / 1080
    if width(left[0]['text'], 26) > bw * sx - 16: sys.exit('STOPPED: the bracket does not fit inside the box over the picture\'s captions')
    add(22, ts(CAPTION_COVER[0]), ts(CAPTION_COVER[1]), 'Side', '{\\an5\\pos(%d,%d)\\q2}%s' % (round(VX + (bx + bw / 2) * sx), round(VY + (by_ + bh / 2) * sy), left[0]['text']))
    # lower band: the verdict and the source (round 7: an entry with no verdict and no text shows nothing)
    for b in bands:
        if b['tag']: add(19, ts(b['start']), ts(b['end']), 'Tag', '{\\an7\\pos(%d,%d)\\q2}%s' % (PAD, B2Y + 14, b['tag']))
        if b['text']: add(20, ts(b['start']), ts(b['end']), 'Src', '{\\an7' + ('' if b['size'] == SRC_SIZES[0] else '\\fs%d' % b['size']) + '}' + show(b['text']), PAD, PAD, B2Y + 50)
    at(21, 'Tag', W - PAD, B2Y + 14, '{\\1c' + MUTED + '}' + RIGHT_LABEL, an=9)
    style = lambda name, size, colour, bold, spacing: f'Style: {name},Inter,{size},{colour},&H000000FF,&H00000000,&H00000000,{bold},0,0,0,100,100,{spacing},0,1,0,0,7,0,0,0,1'
    ass = '\n'.join(['[Script Info]', '; Written by build.py. Do not edit: change bands.txt or build.py and rebuild.', 'ScriptType: v4.00+', f'PlayResX: {W}', f'PlayResY: {H}',
                     'WrapStyle: 1', 'ScaledBorderAndShadow: yes', 'YCbCr Matrix: TV.709', '', '[V4+ Styles]',
                     'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
                     style('Head', 32, INK.replace('&H', '&H00').rstrip('&'), -1, 0), style('Small', 24, MUTED.replace('&H', '&H00').rstrip('&'), 0, 0),
                     style('Tag', 23, INK2.replace('&H', '&H00').rstrip('&'), -1, 1.5), style('Side', 26, INK2.replace('&H', '&H00').rstrip('&'), 0, 0),
                     style('Said', 46, INK.replace('&H', '&H00').rstrip('&'), 0, 0), style('Src', 38, INK.replace('&H', '&H00').rstrip('&'), 0, 0), '',
                     '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text'] + ev) + '\n'
    (HERE / 'captions.ass').write_text(ass, encoding='utf-8')
    print(f'wrote captions.ass: {len(said)} transcript lines, {len(bands)} source bands; the policy pages count is {policy_pages}; the clip runs {duration:.2f} s')
    for b in bands: print(f'  band {clock(b["start"])} to {clock(b["end"])} ({b["end"] - b["start"]:.1f} s, {len(MARK.sub("", b["text"]).split())} words, size {b["size"]}, {b["lines"]} lines, {b["gap"]:.0f} px beside the verdict line) {b["part"]}: {b["tag"]}')
    if '--no-video' in sys.argv: return

    load = json.loads(Path('HOME/.local/state/cluster/load_keeper.status.json').read_text()).get('main_run_mean')
    if load is not None and load >= 32: sys.exit(f'STOPPED before the video: the machine is busy (main_run_mean {load}); run again later')
    CC.check_edges('luckey', json.loads(DATA.read_text(encoding='utf-8')))   # round 7: the left-out line inside the stretch
    CC.silenced_wav(SRC, *CAPTION_COVER, SOUND_WAV)                        # the clip's sound, the stretch set to zero
    cover = f"drawbox=x={bx}:y={by_}:w={bw}:h={bh}:color={SURFACE_HEX}:t=fill:enable='between(t,{CAPTION_COVER[0]:.2f},{CAPTION_COVER[1]:.2f})',"
    graph = (f'color=c={PAGE_HEX}:s={W}x{H}:r=24000/1001[bg];[0:v]{cover}scale={VW}:{VH}:flags=lanczos[v];[bg][v]overlay={VX}:{VY}:shortest=1,'
             f'drawbox=x=40:y={B1Y}:w={W - 80}:h={B1H}:color={SURFACE_HEX}:t=fill,drawbox=x=40:y={B2Y}:w={W - 80}:h={B2H}:color={SURFACE_HEX}:t=fill,'
             'ass=captions.ass:fontsdir=/usr/share/fonts/opentype/inter,format=yuv420p[out]')
    tmp = HERE / 'luckey_with_sources.part.mp4'
    run(['nice', '-n', '19', 'ffmpeg', '-v', 'error', '-y', '-threads', '4', '-i', SRC, '-i', SOUND_WAV, '-filter_complex', graph, '-map', '[out]', '-map', '1:a:0', '-c:a', 'flac',
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-threads', '4', '-movflags', '+faststart', '-f', 'mp4', tmp], cwd=HERE)
    tmp.replace(OUT)
    got = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', OUT]).strip())
    if abs(got - duration) > 0.2: sys.exit(f'STOPPED: the new video runs {got:.2f} s, the clip {duration:.2f} s')
    cover_check()
    CC.check_sound(SRC, OUT, *CAPTION_COVER)                  # round 7: the stretch silent, every other sample the clip's own
    print('sound: the stretch is silent and the rest is the clip\'s own sound, sample for sample; controls behave')
    by = {b['part']: b for b in bands}
    (HERE / 'stills').mkdir(exist_ok=True)
    listing = []
    names = [f'still_{n}_{clock(by[part]["start"] + plus).replace(":", "m")}s.png' for n, (part, plus) in enumerate(STILLS, 1)]
    for old in sorted(list((HERE / 'stills').glob('still_*.png')) + list((HERE / 'stills').glob('other_states.png'))):   # a still of an earlier build: moved aside, not removed
        if old.name not in names:
            (HERE / 'tmp_work' / 'superseded').mkdir(parents=True, exist_ok=True)
            old.rename(HERE / 'tmp_work' / 'superseded' / f'{datetime.now().strftime("%H%M%S")}_{old.name}')
    for n, (part, plus) in enumerate(STILLS, 1):
        t = by[part]['start'] + plus
        name = names[n - 1]
        run(['nice', '-n', '19', 'ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', OUT, '-frames:v', '1', '-vf', 'scale=1600:900:flags=lanczos', HERE / 'stills' / name])
        listing.append(f'{name}\t{t:.2f}\t{clock(t)}\t{part}\t{by[part]["tag"] or "(nothing: the words of this stretch are left out of this project)"}')
    (HERE / 'stills' / 'stills.tsv').write_text('file\tseconds\ttime\tpart\twhat the lower band shows\n' + '\n'.join(listing) + '\n', encoding='utf-8')
    print(f'wrote {OUT.name} ({OUT.stat().st_size / 1e6:.1f} MB, {got:.2f} s) and {len(STILLS)} stills in stills/')


if __name__ == '__main__':
    main()
