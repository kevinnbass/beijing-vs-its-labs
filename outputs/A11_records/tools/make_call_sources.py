"""Idea 36: write the list of results-call transcripts to save, from the saved index pages (no address is typed by hand).
Run: python3 -I tools/make_call_sources.py   -> writes idea36_results_calls/calls.tsv (company, call date, quarter label,
     saved id, address, where from) and prints the lines to append to sources.tsv.
Call dates: stockanalysis.com's eventDate; Alibaba's own site gives eventDate in milliseconds (read here in UTC+8, Hong Kong)."""
import json, re, glob, datetime
from pathlib import Path
P = Path('research/primary')
HERE = Path(__file__).resolve().parents[1]
rows = []
def sa(index_id, company, base, start='2023-10'):
    h = (P / index_id / 'body.html').read_text(encoding='utf-8', errors='replace')
    for slug, date, title in sorted(set(re.findall(r'detailSlug:"([^"]+)",eventDate:"([^"]+)",eventTitle:"([^"]+)"', h)), key=lambda r: r[1]):
        if date >= start and re.match(r'Q[1-4] \d{4}$', title):
            rows.append((company, date, title, f'{base}{slug}/', 'stockanalysis.com'))
sa('cn-o36-index-stockanalysis-tencent', 'Tencent', 'https://stockanalysis.com/quote/hkg/0700/transcripts/')
sa('cn-o36-index-stockanalysis-baidu-hk', 'Baidu', 'https://stockanalysis.com/quote/hkg/9888/transcripts/')
sa('cn-o36-index-stockanalysis-alibaba-hk', 'Alibaba', 'https://stockanalysis.com/quote/hkg/9988/transcripts/', start='2026-11')
tz = datetime.timezone(datetime.timedelta(hours=8))
for y in ('2023', '2024', '2025', '2026'):
    data = json.loads(glob.glob(str(P / f'cn-o36-index-alibaba-ir-q{y}' / 'body.*'))[0] and open(glob.glob(str(P / f'cn-o36-index-alibaba-ir-q{y}' / 'body.*'))[0]).read())
    for it in data['content']:
        u = (it.get('urls') or {}).get('transcriptUrl_en_US') or ''
        ev = it.get('eventDate')
        if not ev: continue
        date = datetime.datetime.fromtimestamp(ev / 1000, tz).strftime('%Y-%m-%d')
        if date < '2023-10': continue
        rows.append(('Alibaba', date, it['documentTitle']['en_US'], u, "Alibaba's investor site" if u else "Alibaba's investor site: no transcript posted"))
rows.sort(key=lambda r: (r[0], r[1]))
out, src = [], []
seen = {}
for company, date, title, url, where in rows:
    held = 'cn-labs-tencent-q2-call-20250813-relay1' if url.endswith('/346447-q2-2025/') else ''
    sid = held or (f"cn-o36-{company.lower()}-call-{date.replace('-', '')}" + ('-own' if where.startswith('Alibaba') else '-sa'))
    if not url: sid = ''
    out.append('\t'.join((company, date, title, sid, url, where + (' (saved earlier by the project)' if held else ''))))
    if sid and not held: src.append(f'{sid}\t{url}')
(HERE / 'idea36_results_calls' / 'calls.tsv').write_text('company\tcall_date\tquarter_as_labelled\tsaved_id\taddress\tfrom\n' + '\n'.join(out) + '\n', encoding='utf-8')
print('\n'.join(src)); print(f'# {len(out)} calls listed, {len(src)} to save')
