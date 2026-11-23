#!/usr/bin/env python3
"""Take a picture of one place in a built page: the table row or list item that holds given words. A looking aid.

Run: python3 tools/spot.py <page.html> "<words in the row>" <out.png> [width]
It writes only the PNG named (keep it under tools/tmp_spot/). It does not replace render_and_look.py, whose record is the
one that counts; it lets a changed row far down a long page be looked at directly.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

page, words, out = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
width = int(sys.argv[4]) if len(sys.argv) > 4 else 390
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': width, 'height': 900}, device_scale_factor=2 if width < 600 else 1)
    pg.goto(page.as_uri(), wait_until='load'); pg.wait_for_timeout(500)
    loc = pg.locator('tbody tr, ul.l li', has_text=words).first          # the text's own rows and list items, not the reference list
    loc.scroll_into_view_if_needed()
    box = loc.bounding_box()
    over = pg.evaluate('document.documentElement.scrollWidth - window.innerWidth')
    loc.screenshot(path=out)
    print(f'{page.name} at {width}px: row is {round(box["width"])} x {round(box["height"])} px; page wider than window by {over} px; saved {out}')
    b.close()
