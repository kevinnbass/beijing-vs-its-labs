#!/usr/bin/env python
"""Does each MP4 of this folder play in a browser, at the right size and in the right colours?

Run: python3 browser_check.py
For each video it opens the video's own local page in Google Chrome (headless; the Chromium that Playwright brings is
asked too), puts the file alone on the page in a <video> at 1280 x 720, seeks to the last second, takes a screenshot
of what the browser shows and reads three pixels: the page background, the orange key dot and the blue key dot. Each
must be within 16 (of 255, on each of red, green and blue) of its design colour (#f9f9f7, #c44e18, #256abf).
Why 16: H.264 video for browsers stores colour at half resolution and rounds it. On these 13-pixel dots, seven encoder
settings tried on Nov 23, 2026 (crf 12 to 16, with and without finer colour steps) all left one channel 3 to 8 off,
and the explainer's blue dot reads 11 off in its blue channel; the background is exact. 16 is about 6% of the range.
Controls: a text file given as a video must fail to load, and a pixel of the background must NOT pass as orange.
Both files are local; the pages ask the web only for their two fonts, as always. Exit 0 only if every line passes.
"""
import io, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
def videos():
    """file, its page, a text file for the control, then x, y of: background, the key's orange dot, the key's blue dot.
    The two dots' places are read from capture_record.json, where frames.py wrote them when it captured the video."""
    out = []
    for folder, stem, ctl in (('25_strip_animation', 'strip_animation', 'quotes.tsv'), ('24_explainer', 'explainer', 'chapters.tsv')):
        d = HERE / folder
        k = json.loads((d / 'capture_record.json').read_text(encoding='utf-8'))['key_px']
        out.append((d / f'{stem}.mp4', d / f'{stem}.html', d / ctl, (6, 6), tuple(k['orange']), tuple(k['blue'])))
    return out


WANT = {'background': (0xf9, 0xf9, 0xf7), 'orange': (0xc4, 0x4e, 0x18), 'blue': (0x25, 0x6a, 0xbf)}
JS = """async (src) => {
  document.documentElement.innerHTML = '<body style="margin:0;background:#000"></body>';
  const v = document.createElement('video'); v.muted = true; v.preload = 'auto'; v.width = 1280; v.height = 720; v.style.display = 'block'; document.body.append(v);
  const step = (ev, ms) => new Promise(res => { v.addEventListener(ev, () => res(ev), {once: true}); v.addEventListener('error', () => res('error ' + (v.error && v.error.code)), {once: true}); setTimeout(() => res('timeout'), ms); });
  let p = step('loadeddata', 15000); v.src = src; let r = await p;
  if (r !== 'loadeddata') return {r};
  p = step('seeked', 15000); v.currentTime = Math.max(0, v.duration - 1); r = await p;
  if (r !== 'seeked') return {r};
  await new Promise(res => requestAnimationFrame(() => requestAnimationFrame(res)));
  return {r: 'played', w: v.videoWidth, h: v.videoHeight, d: v.duration};
}"""


TOL = 16


def near(a, b): return all(abs(x - y) <= TOL for x, y in zip(a, b))


def main():
    from playwright.sync_api import sync_playwright
    bad = 0
    with sync_playwright() as p:
        for name, kw in (('Google Chrome', {'channel': 'chrome'}), ('Chromium (Playwright)', {})):
            try: b = p.chromium.launch(**kw)
            except Exception as e:
                print(f'{name}: not available here ({str(e).splitlines()[0][:80]})'); continue
            from PIL import Image
            pg = b.new_context(viewport={'width': 1280, 'height': 720}, device_scale_factor=1).new_page()
            for f, page, ctl, *pts in videos():
                pg.goto(page.as_uri() + '?capture=1'); got = pg.evaluate(JS, f.as_uri())
                if got['r'] != 'played':
                    print(f'{name} {b.version}: {f.name}: DID NOT PLAY ({got["r"]})'); bad += 1; continue
                pg.wait_for_timeout(300)
                im = Image.open(io.BytesIO(pg.screenshot(type='png'))).convert('RGB')
                px = dict(zip(WANT, [im.getpixel(x) for x in pts]))
                ok = got['w'] == 1280 and got['h'] == 720 and all(near(px[k], WANT[k]) for k in WANT)
                pg.goto(page.as_uri() + '?capture=1'); c1 = pg.evaluate(JS, ctl.as_uri())['r']
                c2 = near(px['background'], WANT['orange'])
                ctl_ok = c1.startswith('error') and not c2
                bad += (not ok) + (not ctl_ok)
                print(f'{name} {b.version}: {f.name}: {"plays" if ok else "FAILS"}, {got["w"]} x {got["h"]}, {got["d"]:.2f} s; frame in the last second: '
                      + ', '.join(f'{k} {px[k]} (design {WANT[k]}, furthest channel {max(abs(a - c) for a, c in zip(px[k], WANT[k]))} off)' for k in WANT) + f'; allowed {TOL}; controls {"behave" if ctl_ok else "FAILED"} (a text file as video: {c1}; background taken for orange: {c2})')
            b.close()
    sys.exit(1 if bad else 0)


main()
