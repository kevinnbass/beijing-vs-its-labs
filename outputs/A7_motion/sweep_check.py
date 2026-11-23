#!/usr/bin/env python
"""Ask each motion page, at every second of its video, whether anything is out of place. No frames are kept.

Run: python3 sweep_check.py
Why: the stills that are looked at are few (every 2 s for the strip animation; one for each caption of the explainer).
This asks the page itself at every whole second, in the same headless browser and with the same flags as frames.py:
  - window.overflowReport(): text past its caption box, the key or the count past the card, the headline into the date,
    anything past the frame, a label beside a mark nearer than 1.5 strip units to any mark on screen;
  - for the explainer, that exactly one caption is fully shown, or none or two while one caption gives way to the next
    (never for longer than one second);
  - that the count of marks on screen never falls and ends at the number of records.
Control: a label set down on a mark must be reported, or the sweep proves nothing.
It also prints, for the last frame, the distances the fix list of round 4 asks for (V7: label 11 from marks 12 and 13;
V8: label 21 from mark 28), found by saved id, not by number. Exit 0 only if nothing is reported and the control behaves.
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGES = ((HERE / '25_strip_animation', 'strip_animation.html'), (HERE / '24_explainer', 'explainer.html'))
PAIRS = (  # label of (saved id) against mark (saved id, row): what the fix list asks to be measured
    ('V7', 'man-cn-factions-wsj-ding', 'cn-le13-yuyuan-qq-20250810b', 'BH'),
    ('V7', 'man-cn-factions-wsj-ding', 'cn-le11-ft-h20justify-aggregoctt', 'BH'),
    ('V8', 'cn-acts-reuters-customs-20260114', 'cn-policy-ndrc-chip-adaptation-2026', 'BH'),
    ('V8', 'cn-acts-reuters-customs-20260114', 'cn-us-lutnick-0422-rev-transcript-b', 'BH'),
)
GAP = """([lab, mk]) => { const S = JSON.parse(document.getElementById('scene').textContent), sv = document.getElementById('strip');
  const k = sv.getBoundingClientRect().width / sv.viewBox.baseVal.width, b = document.getElementById('c' + lab).getBBox(), o = S.marks.find(m => m.n === mk);
  const dx = Math.max(b.x - o.x, 0, o.x - (b.x + b.width)), dy = Math.max(b.y - o.cy, 0, o.cy - (b.y + b.height)), g = Math.hypot(dx, dy) - (S.geom.R + 1.25);
  return [+g.toFixed(2), +(g * k).toFixed(2)]; }"""


def main():
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(HERE))
    import a7lib as L
    evs, _, _ = L.load_events()
    num = {(e['sid'], e['lane']): e['n'] for e in evs}
    one = lambda sid: next(e['n'] for e in evs if e['sid'] == sid and e['C'])
    from playwright.sync_api import sync_playwright
    bad = 0
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--disable-lcd-text', '--font-render-hinting=none'])
        pg = b.new_context(viewport={'width': 1280, 'height': 720}, device_scale_factor=1, color_scheme='light').new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        for folder, name in PAGES:
            P = json.loads((folder / 'capture.json').read_text(encoding='utf-8'))
            pg.goto((folder / name).as_uri() + '?capture=1', wait_until='load'); pg.wait_for_function('window.READY === true', timeout=60000)
            dur = P['frames'] / P['fps']; faults, shown_before, odd, last_odd = [], 0, 0, -9
            times = list(range(0, int(dur) + 1)) + [(P['frames'] - 1) / P['fps']]
            for t in times:
                pg.evaluate('t => window.setT(t)', min(t, (P['frames'] - 1) / P['fps']))
                faults += [f'{t} s: {x}' for x in pg.evaluate('window.overflowReport()')]
                shown = pg.evaluate("[...document.querySelectorAll('#strip g.pin')].filter(g => g.style.display !== 'none').length")
                if shown < shown_before: faults.append(f'{t} s: marks on screen fell from {shown_before} to {shown}')
                shown_before = shown
                if P.get('expect'):
                    full = pg.evaluate("[...document.querySelectorAll('.cap')].filter(c => +c.style.opacity > 0.99).length")
                    if full != 1:
                        odd += 1
                        if t - last_odd <= 1: faults.append(f'{t} s: no single caption fully shown for two seconds running')
                        last_odd = t
            if shown_before != len(evs): faults.append(f'ends with {shown_before} marks on screen, not {len(evs)}')
            gaps = []
            for fix, lab_sid, mk_sid, lane in PAIRS:
                lab, mk = one(lab_sid), num[(mk_sid, lane)]
                u, px = pg.evaluate(GAP, [lab, mk]); gaps.append(f'{fix}: label {lab} stands {u} strip units = {px} px from mark {mk}')
            ctl = P['label_control']
            pg.evaluate('''([id, x, y]) => { const el = document.getElementById(id); el.setAttribute('x', x); el.setAttribute('y', y); el.setAttribute('text-anchor', 'middle'); }''', [ctl['id'], ctl['x'], ctl['y']])
            seen = any(x.startswith('label of mark') for x in pg.evaluate('window.overflowReport()'))
            bad += len(faults) + (not seen)
            print(f'{name}: {len(times)} moments asked (every second of {dur:.2f} s, and the last frame), {len(faults)} faults'
                  + (f'; a caption was giving way to the next at {odd} of them' if P.get('expect') else '') + f'; marks end at {shown_before} of {len(evs)}; control (a label set down on a mark) {"reported" if seen else "NOT REPORTED"}')
            for x in faults[:12]: print('  FAULT', x)
            for x in gaps: print('  ' + x)
        b.close()
    if errs: print('page errors:', errs); bad += 1
    sys.exit(1 if bad else 0)


main()
