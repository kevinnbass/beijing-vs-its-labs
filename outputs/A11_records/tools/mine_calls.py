"""Idea 36: list every paragraph of the saved results-call transcripts that touches chip supply, with its speaker.
Run: python3 -I tools/mine_calls.py   -> writes idea36_results_calls/candidates.tsv and candidates.txt (for reading)
Reads idea36_results_calls/calls.tsv. Two page forms:
  stockanalysis.com pages (body.html): each turn is a block with the speaker's name, a title line, then paragraphs of
     sentence spans carrying start times in seconds;
  Alibaba's own PDF transcripts (text.txt from pdftotext): a turn starts at a line "Name:" or at a centred name line
     followed by a title line; "(Translation)" / "(Original)" marks are the company's.
This only finds candidates. Every row of the final table is read and chosen by hand from candidates.txt."""
import csv, html, re, sys
from pathlib import Path
P = Path('research/primary')
HERE = Path(__file__).resolve().parents[1] / 'idea36_results_calls'
KEY = re.compile(r"(?i)\bchips?\b|\bGPUs?\b|nvidia|semiconductor|\bexport|\bimport(?!an)|sanction|kunlun|t-head|\bH20\b|\bH200\b|\bASICs?\b|supply[- ]chain|supply constraint|supply of (?:compute|computing)|domestic(?:ally)? (?:produced|made|suppl|chip|GPU|alternative|compute)|self-developed|in-house|homegrown|home-grown|localiz|geopolit|\bbans?\b|\brestrict")

def turns_sa(sid):
    h = (P / sid / 'body.html').read_text(encoding='utf-8', errors='replace')
    out = []
    for blk in re.split(r'<div class="border-t border-sharp pt-5[^"]*">', h)[1:]:
        m = re.search(r'<div class="text-lg font-bold[^"]*">(.*?)</div>', blk, re.S)
        name = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else ''
        m2 = re.search(r'<div class="text-sm italic text-muted">(.*?)</div>', blk, re.S)
        title = html.unescape(re.sub(r'<[^>]+>', '', m2.group(1))).strip() if m2 else ''
        for p in re.findall(r'<p class="text-default[^"]*">(.*?)</p>', blk, re.S):
            sents = re.findall(r'data-start-sec="([0-9.]+)"[^>]*>(.*?)</span>', p, re.S)
            if not sents: continue
            text = ' '.join(html.unescape(re.sub(r'<[^>]+>', '', s)).strip() for _, s in sents)
            out.append((name, title, float(sents[0][0]), text))
    return out

def turns_pdf(sid):
    t = (P / sid / 'text.txt').read_text(encoding='utf-8', errors='replace')
    lines = t.split('\n')
    out, name, title, buf = [], '', '', []
    def flush():
        nonlocal buf
        para = ' '.join(x.strip() for x in buf if x.strip())
        if para: out.append((name, title, None, para))
        buf = []
    i = 0
    while i < len(lines):
        ln = lines[i]; s = ln.strip()
        if re.match(r'^Alibaba Group .* Conference Call\s', s) or re.fullmatch(r'\d{1,3}', s): i += 1; continue
        m = re.fullmatch(r'([A-Z][A-Za-z.\-\' ]{2,40}):', s)
        if m: flush(); name, title = m.group(1), ''; i += 1; continue
        # centred name line followed (after blanks) by a centred title line
        if ln.startswith(' ' * 20) and re.fullmatch(r"[A-Z][A-Za-z.\-' ]{2,40}", s):
            j = i + 1
            while j < len(lines) and not lines[j].strip(): j += 1
            if j < len(lines) and lines[j].startswith(' ' * 15) and re.search(r'Alibaba|Officer|CEO|CFO|Chairman|Relations|President|Analyst|Securit|Research|Capital|Bank', lines[j]):
                flush(); name, title = s, lines[j].strip(); i = j + 1; continue
        if not s: flush()
        else: buf.append(s)
        i += 1
    flush()
    return out

rows = list(csv.DictReader(open(HERE / 'calls.tsv', encoding='utf-8'), delimiter='\t'))
cand, txt, stats = [], [], []
for r in rows:
    sid = r['saved_id']
    if not sid: continue
    turns = turns_pdf(sid) if sid.endswith('-own') else turns_sa(sid)
    n = 0
    for k, (name, title, sec, text) in enumerate(turns):
        if KEY.search(text):
            n += 1
            cand.append((r['company'], r['call_date'], sid, str(k), name, title, '' if sec is None else f'{sec:.0f}', text))
            txt.append(f"### {r['company']} {r['call_date']} {sid} #{k} | {name} | {title} | t={'' if sec is None else int(sec)}\n{text}\n")
    stats.append((r['company'], r['call_date'], sid, len(turns), n, len({t[0] for t in turns})))
with open(HERE / 'candidates.tsv', 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f, delimiter='\t'); w.writerow(['company', 'call_date', 'saved_id', 'para_no', 'speaker', 'title', 'start_sec', 'text']); w.writerows(cand)
(HERE / 'candidates.txt').write_text('\n'.join(txt), encoding='utf-8')
for s in stats: print('\t'.join(map(str, s)))
print(f'# {len(cand)} candidate paragraphs in {len(stats)} calls; {sum(len(c[7]) for c in cand)} characters')
