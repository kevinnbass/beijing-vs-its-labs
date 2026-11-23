"""Working preview of a page while it is being built (not the recorded look: that is scripts/render_and_look.py).
Run: python3 -I tools/preview.py <page.html> [widths, e.g. 1280,390] [dark]
Saves tiles of 1,400 px of page height into scratch_preview/ (working files, not outputs) and prints their paths and any sideways overflow.
"""
import sys, math
from pathlib import Path
from playwright.sync_api import sync_playwright
f = Path(sys.argv[1]).resolve()
widths = [int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else '1280,390').split(',')]
scheme = 'dark' if 'dark' in sys.argv[3:] else 'light'
out = Path(__file__).resolve().parents[1] / 'scratch_preview'; out.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in widths:
        pg = b.new_context(viewport={'width': w, 'height': 900}, device_scale_factor=2 if w < 600 else 1, color_scheme=scheme).new_page()
        pg.goto(f.as_uri(), wait_until='load'); pg.evaluate('document.fonts.ready.then(() => 1)'); pg.wait_for_timeout(700)
        h = pg.evaluate('Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)')
        over = pg.evaluate('document.documentElement.scrollWidth - window.innerWidth')
        n = max(1, math.ceil(h / 1400))
        if n > 1 and h - (n - 1) * 1400 < 200: n -= 1
        print(f'{w}px {scheme}: page height {h}, sideways overflow {over}')
        for i in range(n):
            name = out / f'{f.stem}-{w}-{scheme}-{i + 1:02d}.png'
            hh = h - i * 1400 if i == n - 1 else 1400
            pg.screenshot(path=str(name), full_page=True, clip={'x': 0, 'y': i * 1400, 'width': w, 'height': hh}); print('  ', name)
    b.close()
