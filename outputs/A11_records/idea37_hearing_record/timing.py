"""Idea 37: work out when the exchange falls in the committee's own video, from files kept in this folder.
Run: python3 -I timing.py   -> exchange_timing.tsv (key <TAB> value) and prints it.
Inputs: captions/index_1.m3u8 (the video's list of 12-second pieces), captions_384_400.tsv (the video's own captions as a
timed word stream, made by ../tools/captions_words.py), video_excerpt/asr_excerpt_011700_011824.json (a speech program's
pass over 84 seconds of the video's sound; the excerpt starts at piece 386, which is (386-1)*12 = 4620 s into the video).
The commercial transcript's time marks are read from the saved copy cn-us-lutnick-0422-rev-transcript-b."""
import json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
P = Path('research/primary')
out = []
def put(k, v): out.append((k, str(v)))
def hms(x): return f'{int(x // 3600)}:{int(x % 3600 // 60):02d}:{int(x % 60):02d}'
segs = [float(x) for x in re.findall(r'#EXTINF:([0-9.]+)', (HERE / 'captions' / 'index_1.m3u8').read_text())]
put('video_pieces', len(segs)); put('video_length', hms(sum(segs))); put('video_length_seconds', round(sum(segs), 1))
FIRST_PIECE = 386; base = (FIRST_PIECE - 1) * segs[0]
put('excerpt_starts_at', hms(base)); put('excerpt_first_piece', FIRST_PIECE)
a = json.loads((HERE / 'video_excerpt' / 'asr_excerpt_011700_011824.json').read_text())
put('speech_program', a['model']); put('excerpt_seconds', round(a['duration'], 1))
ws = [w for s in a['segments'] for w in s['words']]
toks = [re.sub(r"[^a-z0-9']", '', w['w'].lower()) for w in ws]
def find(phrase, which='s', last=False):
    p = [re.sub(r"[^a-z0-9']", '', x.lower()) for x in phrase.split()]
    hits = [i for i in range(len(toks) - len(p) + 1) if toks[i:i + len(p)] == p]
    if len(hits) != 1: sys.exit(f'speech pass: "{phrase}" found {len(hits)} times')
    i = hits[0]
    return ws[i][which] if not last else ws[i + len(p) - 1]['e']
t1 = find('Their cloud companies my understanding'); t2 = find('Chinese central government has not let them as of yet buy the chips'); t3 = find('sold them chips as of yet', last=True)
put('speech_answer_begins', hms(base + t1)); put('speech_key_sentence_begins', hms(base + t2)); put('speech_answer_ends', hms(base + t3))
put('speech_key_sentence_heard', ' '.join(w['w'].strip() for w in ws if t2 <= w['s'] < find('So that\'s my understanding of what\'s')))
put('speech_whole_answer_heard', ' '.join(w['w'].strip() for w in ws if t1 <= w['s'] <= t3))
rows = [l.rstrip('\n').split('\t') for l in (HERE / 'captions_384_400.tsv').read_text(encoding='utf-8').splitlines()[1:]]
def sec(t): h, m, s = t.split(':'); return int(h) * 3600 + int(m) * 60 + float(s)
stream = [(sec(t), w) for t, wds in rows for w in wds.split()]
ctok = [re.sub(r"[^A-Z0-9']", '', w.upper()) for _, w in stream]
def cfind(phrase, last=False):
    p = phrase.upper().split()
    hits = [i for i in range(len(ctok) - len(p) + 1) if ctok[i:i + len(p)] == p]
    if len(hits) < 1: sys.exit(f'captions: "{phrase}" not found')
    return stream[hits[-1] + (len(p) - 1 if last else 0)][0], hits[-1]
c1, i1 = cfind('MY UNDERSTANDING IS THERE CLOUD COMPANIES'); c2, i2 = cfind('CHINESE CENTRAL GOVERNMENT HAS NOT LET THEM'); c3, i3 = cfind('SOLD THEM CHIPS OF YET', last=True)
put('captions_answer_begins', hms(c1)); put('captions_key_sentence_begins', hms(c2)); put('captions_answer_ends', hms(c3))
put('captions_words', ' '.join(w for _, w in stream[i1 - 2:i3 + 5]))
put('captions_lag_seconds_at_key_sentence', round(c2 - (base + t2)))
rev = (P / 'cn-us-lutnick-0422-rev-transcript-b' / 'text.txt').read_text(encoding='utf-8')
m = re.search(r'Secretary Howard Lutnick \( (\d\d):(\d\d) \):\s*Their cloud companies', rev)
if not m: sys.exit('commercial transcript: mark not found')
r1 = int(m.group(1)) * 60 + int(m.group(2)); put('commercial_transcript_mark', f'{m.group(1)}:{m.group(2)}')
put('offset_video_minus_commercial', f'{int((base + t1 - r1) // 60)} min {int((base + t1 - r1) % 60)} s')
marks = re.findall(r'\( (\d\d):(\d\d):(\d\d) \)', rev)
put('commercial_transcript_last_mark', ':'.join(marks[-1]))
put('link_start', hms(base + t1 - 6))
(HERE / 'exchange_timing.tsv').write_text('key\tvalue\n' + '\n'.join('\t'.join(x) for x in out) + '\n', encoding='utf-8')
print('\n'.join('\t'.join(x) for x in out))
