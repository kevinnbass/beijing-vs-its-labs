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
STILLS = [('L1', 4.0), ('L3', 3.0), ('L4', 2.0), ('L5a', 2.6), ('L5b', 2.0), ('L5c', 3.2), ('L6a', 6.4), ('L6b', 1.4), ('L8', 4.0)]   # (part, seconds after its band appears)
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
    """Nvidia's chips marked "Approved, not shipped" in the project's copy of the Commerce Department's table, tied to the
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


def main():
    data = json.loads(DATA.read_text(encoding='utf-8'))['clips']['luckey']
    units = {u['id']: u for u in data['units']}
    duration = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', SRC]).strip())
    if abs(duration - data['duration']) > 0.1: sys.exit('STOPPED: the video and the speech pass differ in length')
    note = (PROJ / 'NOTE_policies_checked.md').read_text(encoding='utf-8')
    policy_pages = len(set(re.findall(r'^### Row (\d+) ', note, flags=re.M)))    # the policy pages read: one "### Row N" entry each
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
    q += [f'{c.get("src", "clip-luckey")}\t{c["text"]}' for c in said]
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
    at(3, 'Small', W - 40, 20, "Draft by Claude, Anthropic's model. Local; not published.", an=9)
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
    care = ('The transcript is a speech program\'s. Nobody has checked it by ear.\\N\\N'
            + ''.join(f'At {clock(c["start"])} the upper line is the text of the post instead: two speech passes differ on a word there.\\N\\N' for c in swapped) +
            'Words between quotation marks are a source\'s own, found in its saved copy by a script.\\N\\N'
            'The large captions inside the picture came with the clip.\\N\\N'
            'Pause to read. A lower line can stay a second or two after the words it answers.')
    add(15, ts(0), end, 'Side', '{\\an7}' + care, VX + VW + 40, 40, 132)
    # upper band: the machine transcript, with a clock
    t0, pos = 0.0, '{\\an7\\pos(%d,%d)\\q2\\1c%s}' % (PAD, B1Y + 14, MUTED)
    for c in swapped:                                                            # the label says where the line comes from
        add(16, ts(t0), ts(c['start']), 'Tag', pos + LABEL)
        add(16, ts(c['start']), ts(c['end']), 'Tag', pos.replace(MUTED, INK) + c['label']); t0 = c['end']
    add(16, ts(t0), end, 'Tag', pos + LABEL)
    for s in range(int(duration) + 1):
        add(17, ts(s), ts(min(s + 1, duration + 1)), 'Tag', '{\\an9\\pos(%d,%d)\\q2\\1c%s}%s' % (W - PAD, B1Y + 14, MUTED, clock(s)))
    for c in said: add(18, ts(c['start']), ts(c['end']), 'Said', '{\\an7}' + c['text'], PAD, PAD, B1Y + 48)
    # lower band: the verdict and the source
    for b in bands:
        add(19, ts(b['start']), ts(b['end']), 'Tag', '{\\an7\\pos(%d,%d)\\q2}%s' % (PAD, B2Y + 14, b['tag']))
        add(20, ts(b['start']), ts(b['end']), 'Src', '{\\an7' + ('' if b['size'] == SRC_SIZES[0] else '\\fs%d' % b['size']) + '}' + show(b['text']), PAD, PAD, B2Y + 50)
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
    graph = (f'color=c={PAGE_HEX}:s={W}x{H}:r=24000/1001[bg];[0:v]scale={VW}:{VH}:flags=lanczos[v];[bg][v]overlay={VX}:{VY}:shortest=1,'
             f'drawbox=x=40:y={B1Y}:w={W - 80}:h={B1H}:color={SURFACE_HEX}:t=fill,drawbox=x=40:y={B2Y}:w={W - 80}:h={B2H}:color={SURFACE_HEX}:t=fill,'
             'ass=captions.ass:fontsdir=/usr/share/fonts/opentype/inter,format=yuv420p[out]')
    tmp = HERE / 'luckey_with_sources.part.mp4'
    run(['nice', '-n', '19', 'ffmpeg', '-v', 'error', '-y', '-threads', '4', '-i', SRC, '-filter_complex', graph, '-map', '[out]', '-map', '0:a', '-c:a', 'copy',
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-threads', '4', '-movflags', '+faststart', '-f', 'mp4', tmp], cwd=HERE)
    tmp.replace(OUT)
    got = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', OUT]).strip())
    if abs(got - duration) > 0.2: sys.exit(f'STOPPED: the new video runs {got:.2f} s, the clip {duration:.2f} s')
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
        listing.append(f'{name}\t{t:.2f}\t{clock(t)}\t{part}\t{by[part]["tag"]}')
    (HERE / 'stills' / 'stills.tsv').write_text('file\tseconds\ttime\tpart\twhat the lower band shows\n' + '\n'.join(listing) + '\n', encoding='utf-8')
    print(f'wrote {OUT.name} ({OUT.stat().st_size / 1e6:.1f} MB, {got:.2f} s) and {len(STILLS)} stills in stills/')


if __name__ == '__main__':
    main()
