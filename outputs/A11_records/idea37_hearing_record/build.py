"""Idea 37: build the note (hearing_record.md and .html). Run: python3 -I build.py   (in this folder)
1. timing.py works out the times from the caption files and the speech pass kept in this folder (exchange_timing.tsv)
2. the times and counts in hearing_record_base_src.txt are filled from that file and from small counts made here
3. scripts/cn_doc_build.py checks every quotation and hidden statement against the saved copies, then writes the note."""
import re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
r = subprocess.run([sys.executable, '-I', str(HERE / 'timing.py')], capture_output=True, text=True)
if r.returncode: sys.exit('timing.py failed: ' + r.stdout[-300:] + r.stderr[-300:])
f = dict(l.split('\t', 1) for l in (HERE / 'exchange_timing.tsv').read_text(encoding='utf-8').splitlines()[1:])
def spoken(t):
    h, m, s = [int(x) for x in t.split(':')]
    return f"{h} hour{'s' if h != 1 else ''} {m} minutes {s} seconds"
tt = (HERE / 'lutnick_testimony_fy27_docx_text.txt').read_text(encoding='utf-8')
if not re.search(r'semiconductor', tt, re.I): sys.exit('control failed: semiconductor not in the testimony text')
n_hits = len(re.findall(r'\bChina\b|Nvidia|H-?200|\bchips?\b', tt, re.I))
vtt = sorted((HERE / 'captions').glob('text_1_*.vtt'))
def cue_edge(p, last=False):
    c = re.findall(r'(\d\d:\d\d:\d\d)\.\d{3} --> (\d\d:\d\d:\d\d)\.\d{3}', p.read_text(encoding='utf-8', errors='replace'))
    return (c[-1][1] if last else c[0][0]).lstrip('0')
v = {'T_BEGIN': spoken(f['speech_answer_begins']), 'T_BEGIN_S': f['speech_answer_begins'], 'T_KEY': f['speech_key_sentence_begins'], 'T_END': f['speech_answer_ends'],
     'C_BEGIN': f['captions_answer_begins'], 'C_KEY': f['captions_key_sentence_begins'], 'C_END': f['captions_answer_ends'], 'V_LEN': spoken(f['video_length']).replace(' 2 seconds', ' 2 seconds'),
     'V_PIECES': f['video_pieces'], 'T_LINK': f['link_start'], 'N_TESTIMONY_HITS': {0: 'none'}[n_hits], 'N_VTT': len(vtt), 'CAP_FROM': cue_edge(vtt[0]), 'CAP_TO': cue_edge(vtt[-1], True),
     'EXC_SECONDS': str(int(float(f['excerpt_seconds']))), 'EXC_START': f['excerpt_starts_at'], 'ASR_MODEL': f['speech_program'].split('/')[-1], 'REV_MARK': f['commercial_transcript_mark'],
     'OFFSET': f['offset_video_minus_commercial'].replace(' min ', ' minutes ').replace(' s', ' seconds'), 'LAG': f['captions_lag_seconds_at_key_sentence'],
     'ASR_ANSWER': f['speech_whole_answer_heard'], 'CAP_WORDS': f['captions_words']}
if '"' in v['ASR_ANSWER'] + v['CAP_WORDS']: sys.exit('a straight quote mark in machine text')
# the note says the argument's two quotations, and the commercial transcript's key sentence, are in the speech program's hearing: check it
k = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
for q in ('my understanding is their cloud companies want to buy these chips',
          "Chinese central government has not let them as of yet buy the chips because they're trying to keep their investment focused on their own domestic industry",
          "And central government has not let them, Chinese central government has not let them as of yet buy the chips because they're trying to keep their investment focused on their own domestic industry."):
    if k(q) not in k(v['ASR_ANSWER']): sys.exit('NOT in the speech pass: ' + q)
if k('this sentence was never spoken at the hearing') in k(v['ASR_ANSWER']): sys.exit('control failed')
REV = Path('research/primary/cn-us-lutnick-0422-rev-transcript-b')
n_html = len(re.findall(r'Sen\. Coons', (REV / 'body.html').read_text(encoding='utf-8', errors='replace')))
n_text = len(re.findall(r'Sen\. Coons', (REV / 'text.txt').read_text(encoding='utf-8', errors='replace')))
if n_html < 5 or n_text != 0 or 'Senator Fischer (' not in (REV / 'text.txt').read_text(encoding='utf-8', errors='replace'): sys.exit(f'the count of the label Sen. Coons changed: page {n_html}, text {n_text}')
v['N_COONS_HTML'] = str(n_html); v['N_COONS_TEXT'] = {0: 'not once'}[n_text]
t = (HERE / 'hearing_record_base_src.txt').read_text(encoding='utf-8')
for k, x in v.items(): t = t.replace('{' + k + '}', str(x))
left = re.findall(r'\{[A-Z_0-9]+\}', t)
if left: sys.exit(f'unfilled: {left}')
(HERE / 'hearing_record_base.txt').write_text(t, encoding='utf-8')
r = subprocess.run([sys.executable, '-I', 'scripts/cn_doc_build.py', str(HERE / 'hearing_record_base.txt'), '--refs', str(HERE / 'extra_refs.tsv'), '--title', 'Hearing Record Found', '--eyebrow', 'China chip policy: new research, idea 37'], capture_output=True, text=True)
print(r.stdout[-3000:], r.stderr[-800:]); sys.exit(r.returncode)
