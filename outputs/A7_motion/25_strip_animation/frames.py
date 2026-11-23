#!/usr/bin/env python
"""Capture a motion page frame by frame and encode the silent video files beside it.

Run, in this folder, after build.py:
    nice -n 19 python3 frames.py              everything
    nice -n 19 python3 frames.py --no-capture the GIF, WebP, stills and probe again, from the files already made

Reads capture.json (written by build.py): the page, the frame rate, the number of frames, the file names, the still
frames to export and, for a page with captions, the checked text each chapter must show.
Steps:
  1. reads main_run_mean in the load keeper's status file and stops at 32 or more (README_FOR_BUILDERS section 6), and
     stops if a file the page was built from has changed since build.py ran (capture.json holds their sha256);
  2. opens the page in headless Chromium at 1280 x 720 with ?capture, waits for its fonts, and stops if the web fonts
     did not load (the look would differ);
  3. before any frame is kept: at every chapter it compares the caption the page shows with the checked text, and at
     every chapter and still it asks the page whether anything runs past its box or a label beside a mark comes
     nearer than 1.5 strip units to any mark (with a control: a label set down on a mark); a fault stops the run;
     it prints, for the last frame, how near each label comes to its own mark and to the nearest other mark;
  4. for frame i it calls window.setT(i / rate), takes a PNG screenshot and pipes it to ffmpeg (nice -n 19, 4 threads),
     which writes the MP4 (H.264, yuv420p, BT.709, no audio stream) and a lossless master in one pass. No frame files;
  5. writes capture_record.json (when captured, the sha256 of the page and of the video) and, on every run, stops
     unless the video on disk is the capture of the page on disk;
  6. makes the GIF and the WebP from the lossless master, exports the still frames from the MP4 itself, and writes
     probe.txt (ffprobe: codec, size, frame rate, frames, duration, audio streams).
"""
import hashlib, json, re, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOAD = Path('HOME/.local/state/cluster/load_keeper.status.json')
NICE = ['nice', '-n', '19']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def norm(s):
    for a, b in (('“', '"'), ('”', '"'), ('’', "'"), ('‘', "'"), (' ', ' '), ('\xa0', ' ')): s = s.replace(a, b)
    return re.sub(r'\s+\[', '[', re.sub(r'\s+', ' ', s)).strip()


def run(cmd, what):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-4000:]); sys.exit(f'{what} failed (exit {r.returncode})')
    return r.stdout


def load_gate():
    try: v = json.loads(LOAD.read_text())['main_run_mean']
    except Exception as e:
        print(f'load: main_run_mean could not be read ({e}); not started'); sys.exit(1)
    print(f'load: main_run_mean {v} (the line is 32)')
    if v >= 32: sys.exit('main_run_mean is 32 or more: wait and run again')


def inputs_gate(P):
    differ = lambda want: [f for f, h in want.items() if not (HERE / f).is_file() or hashlib.sha256((HERE / f).read_bytes()).hexdigest() != h]
    first = next(iter(P['made_from']))
    if differ({first: '0' * 64}) != [first]: sys.exit('control: a changed file was not noticed')
    changed = differ(P['made_from'])
    if changed: sys.exit('changed since build.py last ran: ' + ', '.join(changed) + '. Run build.py again, look at the page, then capture.')
    print(f'inputs: {len(P["made_from"])} files unchanged since build.py ran (sha256); a wrong sha256 was noticed (control)')


def capture(P):
    from playwright.sync_api import sync_playwright
    fps, n = P['fps'], P['frames']
    with sync_playwright() as p:
        br = p.chromium.launch(args=['--disable-lcd-text', '--font-render-hinting=none'])
        pg = br.new_context(viewport={'width': 1280, 'height': 720}, device_scale_factor=1, color_scheme='light').new_page()
        errs = []
        pg.on('console', lambda m: errs.append('console: ' + m.text[:200]) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errs.append('page error: ' + str(e)[:300]))
        pg.goto((HERE / P['page']).as_uri() + '?capture=1', wait_until='load')
        pg.wait_for_function('window.READY === true', timeout=60000)
        fonts = pg.evaluate('[...document.fonts].filter(f => f.status === "loaded").map(f => f.family.replace(/"/g, "") + " " + f.weight)')
        fams = sorted(set(fonts))
        print('web fonts loaded:', ', '.join(fams) or 'none')
        if not any(f.startswith('Space Grotesk') for f in fams) or not any(f.startswith('Inter') for f in fams):
            sys.exit('the web fonts (Inter, Space Grotesk) did not load: the frames would not match the look on record. Not captured.')
        if errs: sys.exit('the page reported errors: ' + '; '.join(errs))
        size = pg.evaluate('(() => { const r = document.getElementById("stage").getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()')
        if size != [0, 0, 1280, 720]: sys.exit(f'the stage is not the 1280 x 720 frame: {size}')
        # where the key's orange and blue dots stand in the frame (../browser_check.py reads their colour in the playing video there)
        key_px = pg.evaluate('''Object.fromEntries([['orange', 'away'], ['blue', 'toward']].map(([k, c]) => { const r = document.querySelector('#key i.sw.' + c).getBoundingClientRect(); return [k, [Math.round(r.left + r.width / 2), Math.round(r.top + r.height / 2)]]; }))''')
        # checks before any frame is kept
        bad = []
        for e in P.get('expect', []):
            pg.evaluate('t => window.setT(t)', e['frame'] / fps)
            got = pg.evaluate('window.captionText()')
            if not isinstance(got, dict): bad.append(f'frame {e["frame"]}: {got}'); continue
            want = (e['k'], norm(e['title']), norm(e['text']), [norm(x) for x in e['items']])
            have = (got['k'], norm(got['title']), norm(got['text']), [norm(x) for x in got['items']])
            if want != have: bad.append(f'frame {e["frame"]}: caption {e["k"]} on screen differs from the checked text:\n   checked: {want}\n   screen:  {have}')
        if P.get('expect'):
            pg.evaluate('t => window.setT(t)', P['expect'][0]['frame'] / fps)
            pg.evaluate('document.querySelector("#cap" + %d + " .txt").append(" planted")' % P['expect'][0]['k'])
            got = pg.evaluate('window.captionText()')
            if norm(got['text']) == norm(P['expect'][0]['text']): bad.append('control: a planted word in a caption was not noticed')
            pg.reload(wait_until='load'); pg.wait_for_function('window.READY === true', timeout=60000)
            print(f'captions: {len(P["expect"])} chapters compared with the checked text' + ('' if bad else ', all equal; a planted word was noticed (control)'))
        spots = sorted(set([e['frame'] for e in P.get('expect', [])] + [s[1] for s in P['stills']]))
        for f in spots:
            pg.evaluate('t => window.setT(t)', f / fps)
            bad += [f'frame {f}: {x}' for x in pg.evaluate('window.overflowReport()')]
        print(f'overflow: {len(spots)} frames asked, {sum(1 for b in bad if "ends at" in b or "runs past" in b)} with text past its box')
        ctl = P.get('label_control')                # a label known to run into a mark must be reported, or the check proves nothing
        if ctl:
            pg.evaluate('t => window.setT(t)', (n - 1) / fps)
            gaps = pg.evaluate('window.labelGaps()')        # measured on the last frame, before the control disturbs it
            pg.evaluate('''([id, x, y]) => { const el = document.getElementById(id); el.setAttribute('x', x); el.setAttribute('y', y); el.setAttribute('text-anchor', 'middle'); }''', [ctl['id'], ctl['x'], ctl['y']])
            hit = [x for x in pg.evaluate('window.overflowReport()') if x.startswith('label of mark')]
            if not hit: bad.append('control: a label known to run into a mark was not reported')
            pg.reload(wait_until='load'); pg.wait_for_function('window.READY === true', timeout=60000)
            print(f'labels: {len(spots)} frames asked, {sum(1 for b in bad if "label of mark" in b)} with a label nearer than 1.5 units to a mark; control: a label set down on a mark was reported ({hit[0] if hit else "NOT REPORTED"})')
            for g in gaps: print(f'  label "{g["text"]}": {g["own"]} units from its own mark; nearest other mark {g["other"]}, {g["gap"]} units = {g["px"]} px in the frame')
            if any(g['px'] < 4 for g in gaps): print('  NOTE: a label stands under 4 px from another mark (the fix list, V8: move it in the core data)')
        if bad:
            print('\n'.join(bad)); sys.exit('not captured')
        cmd = NICE + ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', str(fps), '-c:v', 'png', '-i', '-',
                      '-map', '0:v', '-an', '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(P['crf']),
                      '-profile:v', 'high', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv', '-movflags', '+faststart', '-threads', '4', str(HERE / P['mp4'])]
        if P.get('master'):                         # a lossless copy, only where a GIF or WebP is to be made from it
            cmd += ['-map', '0:v', '-an', '-c:v', 'libx264rgb', '-preset', 'veryfast', '-crf', '0', '-threads', '4', str(HERE / P['master'])]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        t0 = time.time()
        try:
            for i in range(n):
                pg.evaluate('t => window.setT(t)', i / fps)
                ff.stdin.write(pg.screenshot(type='png'))
                if i % 250 == 0 and i: print(f'  frame {i} of {n}, {time.time() - t0:.0f} s')
            ff.stdin.close()
        except BrokenPipeError:
            print(ff.stderr.read().decode()[-3000:]); sys.exit('ffmpeg stopped reading frames')
        err = ff.stderr.read().decode(); rc = ff.wait()
        if rc != 0: print(err[-3000:]); sys.exit(f'ffmpeg failed (exit {rc})')
        if errs: sys.exit('the page reported errors during capture: ' + '; '.join(errs[:5]))
        br.close()
    print(f'captured {n} frames in {time.time() - t0:.0f} s; written {P["mp4"]}' + (f' and {P["master"]}' if P.get('master') else ''))
    rec = dict(captured_utc=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), page=P['page'], page_sha256=sha(HERE / P['page']), mp4=P['mp4'], mp4_sha256=sha(HERE / P['mp4']),
               frames=n, fps=fps, fonts=fams, key_px=key_px, made_from=P['made_from'])
    (HERE / 'capture_record.json').write_text(json.dumps(rec, indent=1), encoding='utf-8')
    print(f'record: capture_record.json (page sha256 {rec["page_sha256"][:16]}, video sha256 {rec["mp4_sha256"][:16]}, {rec["captured_utc"]})')


def record_gate(P):
    """The video on disk must be the capture of the page on disk (asked on every run, after a capture too)."""
    f = HERE / 'capture_record.json'
    if not f.is_file(): sys.exit('no capture_record.json: capture first')
    rec = json.loads(f.read_text(encoding='utf-8'))
    if rec['page_sha256'] != sha(HERE / P['page']): sys.exit(f'{P["page"]} has changed since {P["mp4"]} was captured from it: capture again (run without --no-capture)')
    if rec['mp4_sha256'] != sha(HERE / P['mp4']): sys.exit(f'{P["mp4"]} is not the file the record describes: capture again')
    if rec['made_from'] != P['made_from']: print('note: a file upstream of the page changed after the capture, and build.py gave the same page again (same sha256): the video is still current')
    return rec


def derive(P):
    if not P.get('master'): return
    master = str(HERE / P['master'])
    g = P.get('gif')
    if g:
        vf = (f"fps={g['fps']},scale={g['width']}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors={g['colors']}:stats_mode=full[p];"
              f"[b][p]paletteuse=dither=none:diff_mode=rectangle")
        run(NICE + ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', master, '-filter_complex', vf, '-loop', '0', str(HERE / g['file'])], 'the GIF')
        print(f'written {g["file"]}: {(HERE / g["file"]).stat().st_size / 1e6:.2f} MB')
    w = P.get('webp')
    if w:
        run(NICE + ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', master, '-vf', f"fps={w['fps']},scale={w['width']}:-1:flags=lanczos", '-c:v', 'libwebp_anim',
                    '-lossless', '0', '-q:v', str(w['quality']), '-compression_level', '5', '-loop', '0', '-an', '-threads', '4', str(HERE / w['file'])], 'the WebP')
        print(f'written {w["file"]}: {(HERE / w["file"]).stat().st_size / 1e6:.2f} MB')


def stills(P):
    d = HERE / 'stills'; d.mkdir(exist_ok=True)
    stem = Path(P['mp4']).stem
    for name, f in P['stills']:
        out = d / f'{stem}_{name}.png'
        run(NICE + ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(HERE / P['mp4']), '-vf', f'select=eq(n\\,{f})', '-frames:v', '1', '-update', '1', str(out)], f'still {name}')
        print(f'still: frame {f} ({f / P["fps"]:.2f} s) -> stills/{out.name}')
    g = P.get('gif')
    if g:                                           # one frame of the GIF itself, to look at its colours and its size
        f = P['stills'][-2][1]; out = d / f'{stem}_gif_check.png'
        run(NICE + ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', f'{f / P["fps"]:.3f}', '-i', str(HERE / g['file']), '-frames:v', '1', '-update', '1', str(out)], 'the GIF check frame')
        print(f'still: the GIF at {f / P["fps"]:.2f} s -> stills/{out.name}')
    w = P.get('webp')
    if w:                                           # and one frame of the animated WebP (Pillow reads it; ffmpeg does not)
        from PIL import Image
        want_ms = P['stills'][-2][1] / P['fps'] * 1000; out = d / f'{stem}_webp_check.png'
        with Image.open(HERE / w['file']) as im:
            ms = 0
            for i in range(getattr(im, 'n_frames', 1)):
                im.seek(i); im.load(); ms += im.info.get('duration', 0)
                if ms >= want_ms: break
            im.convert('RGB').save(out)
        print(f'still: the WebP at {ms / 1000:.2f} s (its frame {i}) -> stills/{out.name}')


def probe(P, rec):
    lines = []
    for key in ('mp4', 'gif', 'webp'):
        f = P.get(key) if key == 'mp4' else (P.get(key) or {}).get('file')
        if not f or not (HERE / f).exists(): continue
        if key == 'webp':                           # ffprobe does not read an animated WebP; Pillow does
            from PIL import Image
            with Image.open(HERE / f) as im:
                n = getattr(im, 'n_frames', 1); ms = 0
                for i in range(n):
                    im.seek(i); im.load(); ms += im.info.get('duration', 0)
                line = f'{f}: animated WebP (read with Pillow), {im.size[0]} x {im.size[1]}, {n} frames, duration {ms / 1000:.2f} s, {(HERE / f).stat().st_size / 1e6:.2f} MB, no audio (the format has none)'
            lines.append(line); print('probe:', line); continue
        v = run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries',
                 'stream=codec_name,profile,width,height,pix_fmt,r_frame_rate,nb_read_frames,color_space:format=format_name,duration,size', '-of', 'default=noprint_wrappers=1', str(HERE / f)], 'ffprobe')
        a = run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', str(HERE / f)], 'ffprobe')
        kv = dict(x.split('=', 1) for x in v.strip().splitlines() if '=' in x)
        line = (f'{f}: codec {kv.get("codec_name")}' + (f' ({kv["profile"]})' if kv.get('profile') not in (None, 'unknown') else '') + f', {kv.get("width")} x {kv.get("height")}, {kv.get("pix_fmt")}, '
                f'{kv.get("r_frame_rate")} frames a second, {kv.get("nb_read_frames")} frames, duration {kv.get("duration")} s, {int(kv.get("size", 0)) / 1e6:.2f} MB, '
                f'audio streams {len(a.split())}, container {kv.get("format_name")}')
        lines.append(line); print('ffprobe:', line)
    line = (f'{P["mp4"]} (sha256 {rec["mp4_sha256"][:16]}) was captured {rec["captured_utc"]} from {rec["page"]} (sha256 {rec["page_sha256"][:16]}); '
            + 'built from ' + ', '.join(f'{Path(f).name} {h[:12]}' for f, h in P['made_from'].items() if f != rec['page']))
    lines.append(line); print('record:', line)
    (HERE / 'probe.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    P = json.loads((HERE / 'capture.json').read_text(encoding='utf-8'))
    load_gate(); inputs_gate(P)
    if '--no-capture' not in sys.argv: capture(P)
    rec = record_gate(P)
    derive(P); stills(P); probe(P, rec)


main()
