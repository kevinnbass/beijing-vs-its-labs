"""Idea 37: turn the official video's roll-up caption files (WebVTT, 12 s each) into a timed word stream.
Run: python3 -I tools/captions_words.py idea37_hearing_record/captions <first> <last>   -> writes captions_<first>_<last>.tsv
Each cue repeats the lines on screen and adds words at the end of the last line; a new word is stamped with the start
time of the first cue that shows it. Times are the video's own clock (the cue times in the files)."""
import re, sys, hashlib
from pathlib import Path
d = Path(sys.argv[1]); a, b = int(sys.argv[2]), int(sys.argv[3])
cue = re.compile(r'(\d\d:\d\d:\d\d\.\d{3}) --> (\d\d:\d\d:\d\d\.\d{3})\n(.*?)(?=\n\n|\Z)', re.S)
prev_last, out, files = '', [], []
for n in range(a, b + 1):
    f = d / f'text_1_{n:05d}.vtt'
    raw = f.read_bytes(); files.append((f.name, len(raw), hashlib.sha256(raw).hexdigest()))
    for start, end, body in cue.findall(raw.decode('utf-8', 'replace')):
        lines = [x.strip() for x in body.split('\n') if x.strip()]
        if not lines: continue
        last = lines[-1]
        if last == prev_last: continue
        if prev_last and last.startswith(prev_last): new = last[len(prev_last):].strip()
        else: new = last            # the line rolled up: a new last line begins
        if new: out.append((start, new))
        prev_last = last
o = d.parent / f'captions_{a}_{b}.tsv'
o.write_text('video_time\tnew_caption_words\n' + '\n'.join(f'{t}\t{w}' for t, w in out) + '\n', encoding='utf-8')
(d.parent / f'captions_{a}_{b}_files.tsv').write_text('file\tbytes\tsha256\n' + '\n'.join('\t'.join(map(str, x)) for x in files) + '\n')
print(o, len(out), 'word groups from', len(files), 'files')
