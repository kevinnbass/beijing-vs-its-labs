#!/usr/bin/env python3
"""Ask the Internet Archive (only through the machine's queue, wayback-get) for pages that refuse this machine.

Run: python3 -I tools/archive_pass.py archive/list.tsv
list.tsv: key <TAB> address <TAB> date wanted (YYYYMMDD or empty). Everything is written inside this folder's archive/:
  <key>.avail.json   the Archive's availability answer (kept; a rerun asks nothing twice)
  <key>.body         the capture as archived (web/<timestamp>id_/<address>); kept
  <key>.meta.json    address, capture address, capture time, sha256, bytes, status line
  <key>.txt          text of the capture (pdftotext for a PDF, tags removed for HTML)
These captures are NOT in research/primary: a quotation from them is "read, not saved" for the project's checkers.
"""
import hashlib, html, json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

A = Path(__file__).resolve().parents[1] / 'archive'


def main():
    for ln in Path(sys.argv[1]).read_text(encoding='utf-8').splitlines():
        if not ln.strip() or ln.startswith('#'): continue
        key, url, date = (ln.split('\t') + ['', ''])[:3]
        av = A / f'{key}.avail.json'; body = A / f'{key}.body'; meta = A / f'{key}.meta.json'
        if not (av.exists() and av.stat().st_size > 2):
            q = 'https://archive.org/wayback/available?url=' + re.sub(r'^https?://', '', url) + (f'&timestamp={date}' if date else '')
            p = subprocess.run(['wayback-get', q, '-o', str(av), '--max-wait', '2400'], capture_output=True, text=True)
            if p.returncode != 0: print(key, 'availability call failed, exit', p.returncode, flush=True); continue
        try: snap = (json.loads(av.read_text(encoding='utf-8', errors='replace')).get('archived_snapshots') or {}).get('closest') or {}
        except Exception: snap = {}
        if not snap.get('available') or str(snap.get('status')) != '200':
            print(key, 'no usable capture', json.dumps(snap), flush=True); continue
        ts = snap['timestamp']; cap = f'https://web.archive.org/web/{ts}id_/{url}'
        if not (body.exists() and body.stat().st_size > 0 and meta.exists()):
            p = subprocess.run(['wayback-get', cap, '-o', str(body), '--max-wait', '2400'], capture_output=True, text=True)
            raw = body.read_bytes() if body.exists() else b''
            meta.write_text(json.dumps({'key': key, 'url': url, 'capture': cap, 'capture_timestamp': ts,
                                        'fetched_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'exit': p.returncode,
                                        'status_line': (p.stderr.strip().splitlines() or [''])[-1], 'bytes': len(raw),
                                        'sha256': hashlib.sha256(raw).hexdigest()}, indent=1))
            if p.returncode != 0: print(key, 'capture fetch failed, exit', p.returncode, flush=True); continue
        raw = body.read_bytes()
        if raw[:4] == b'%PDF':
            t = subprocess.run(['pdftotext', '-layout', str(body), '-'], capture_output=True, timeout=120).stdout.decode('utf-8', 'replace')
        else:
            s = raw.decode('utf-8', 'replace')
            s = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', s)
            t = html.unescape(re.sub(r'(?s)<[^>]+>', ' ', s))
        (A / f'{key}.txt').write_text(t, encoding='utf-8')
        print(key, ts, 'bytes', len(raw), 'text characters', len(re.sub(r'\s+', '', t)), flush=True)
    (A / 'PASS_DONE').write_text(datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') + '\n')


main()
