#!/usr/bin/env python3
"""Test policy_documents.html in a headless browser against the counts build.py wrote (expected.json).

Run: python3 test_page.py
It opens the page file at two widths (1280 and 390 px) and checks, at each:
  1. the number of lines, and the count on each kind button, equal expected.json;
  2. each search in expected.json shows exactly the expected number of lines, typed into the box as a reader would,
     with the lines found open and the count line reading "N of 103 lines"; a search with a kind chosen, and the
     "confirmed in part" filter, show the expected numbers;
  3. a search for words that are nowhere shows no line and the "no line" message (the search can come back empty);
  4. the same search given in the address (#q=...) shows the same number;
  5. with every line open, and with every line closed, nothing reaches past the right edge of the window;
  6. every line starts open; "Close all" and "Open all" do what they say; the "how to read" card starts open at
     1280 px and closed at 390 px;
  8. in no line do the kind marks lie over the date or the body's name (round 3: at 390 px the long kind marks
     covered the date, seen only when the lower screenshots were opened);
  7. the page is no taller after it has been painted for a full-page picture than before (round 2: the font of the
     saved ids once made every line 1 px taller at first paint, so the last screenshot of the page was cut short).
Controls (the test can fail): the same checks are run on five faulty copies of the page held in memory (one line
removed; one "confirmed in part" mark taken off; the word "procurement" taken out of one line's search text; the
line-height rule of the saved ids taken out; the phone layout of a line's head put back as it was before round 3).
Each must be reported as a fault, at every width where the fault can show (the last one at 390 px only). It prints one line per width and exits 0 only if the page passes and every faulty
copy fails. It reads the page and expected.json and writes nothing.
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = HERE / 'policy_documents.html'
EXP = json.loads((HERE / 'expected.json').read_text(encoding='utf-8'))

VISIBLE = "() => [...document.querySelectorAll('details.r')].filter(r => !r.hidden).length"
OPEN = "() => [...document.querySelectorAll('details.r')].filter(r => !r.hidden && r.open).length"
EDGE = """() => { const vw = window.innerWidth; let worst = document.documentElement.scrollWidth - vw, who = '';
  for (const el of document.querySelectorAll('body *')) { const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
    if (r.right - vw > worst + 0.5) { worst = r.right - vw; who = el.tagName + '.' + el.className + ' ' + (el.textContent || '').trim().slice(0, 40); } }
  return [Math.round(worst), who]; }"""


OVERLAP = """() => { let n = 0; const hit = (a, b) => Math.min(a.right, b.right) - Math.max(a.left, b.left) > 1 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 1;
  const ink = el => { const g = document.createRange(); g.selectNodeContents(el); return g.getBoundingClientRect(); };      // where the words are, which can reach past a squeezed box
  for (const r of document.querySelectorAll('details.r')) { const d = ink(r.querySelector('summary .d')), w = ink(r.querySelector('summary .who'));
    for (const t of r.querySelectorAll('summary .tag')) { const b = t.getBoundingClientRect(); if (hit(d, b) || hit(w, b)) { n += 1; break; } } } return n; }"""


def checks(pg, width):
    """Run every check on an open page; return the list of faults found."""
    bad = []

    def check(label, got, want):
        if got != want: bad.append(f'{label}: got {got}, expected {want}')

    h0 = pg.evaluate('document.documentElement.scrollHeight')
    pg.screenshot(full_page=True, clip={'x': 0, 'y': 0, 'width': width, 'height': 100})        # painted, kept in memory, not saved
    check('page height after it is painted for a full-page picture', pg.evaluate('document.documentElement.scrollHeight'), h0)
    check('lines whose kind marks lie over the date or the body', pg.evaluate(OVERLAP), 0)
    check('lines on the page', pg.evaluate("() => document.querySelectorAll('details.r').length"), EXP['rows'])
    check('lines open at the start', pg.evaluate(OPEN), EXP['rows'])
    check('the "how to read" card is open at the start', pg.evaluate("() => document.getElementById('how').open"), width > 720)
    for kind, want in EXP['kinds'].items():
        check(f'count on the button {kind}', int(pg.inner_text(f'button[data-kind="{kind}"] .n')), want)
        pg.click(f'button[data-kind="{kind}"]'); check(f'lines after choosing {kind}', pg.evaluate(VISIBLE), want)
    pg.click('button[data-kind="all"]')
    pg.click('#part'); check('lines confirmed in part', pg.evaluate(VISIBLE), EXP['part']); pg.click('#part')
    check('lines after the part filter is taken off', pg.evaluate(VISIBLE), EXP['rows'])
    for q, want in EXP['queries'].items():
        pg.fill('#q', q); pg.wait_for_timeout(30)
        check(f'search "{q}"', pg.evaluate(VISIBLE), want)
        if want: check(f'search "{q}": lines found that are open', pg.evaluate(OPEN), want)
        check(f'search "{q}": the "no line" message is showing', pg.is_visible('#none'), want == 0)
        check(f'search "{q}": the count line', pg.inner_text('#count'), f'{want} of {EXP["rows"]} lines')
    for key, want in EXP['query_with_kind'].items():
        q, kind = key.split('|'); pg.fill('#q', q); pg.click(f'button[data-kind="{kind}"]')
        check(f'search "{q}" with kind {kind}', pg.evaluate(VISIBLE), want); pg.click('button[data-kind="all"]')
    pg.fill('#q', '')
    check('lines after the box is emptied', pg.evaluate(VISIBLE), EXP['rows'])
    check('the button reads', pg.inner_text('#toggle'), 'Close all')
    pg.evaluate("() => document.querySelectorAll('details.more, #how').forEach(d => d.open = true)")
    over, who = pg.evaluate(EDGE)
    if over > 1: bad.append(f'all open: {over} px past the right edge: {who}')
    pg.click('#toggle'); check('lines open after "Close all"', pg.evaluate(OPEN), 0)
    over, who = pg.evaluate(EDGE)
    if over > 1: bad.append(f'all closed: {over} px past the right edge: {who}')
    pg.click('#toggle'); check('lines open after "Open all"', pg.evaluate(OPEN), EXP['rows'])
    return bad


def faulty(src):
    """Five copies of the page, each with one planted fault, the words the fault report must begin with, and the widths where it must show."""
    one = re.search(r'<details class="r" open .*?</details>\n', src, flags=re.S)                 # the first line of the list, whole
    a = src.replace(one.group(0), '', 1)
    b = src.replace('data-part="1"', 'data-part="0"', 1)
    m = re.search(r'data-s="[^"]*procurement[^"]*"', src)
    c = src.replace(m.group(0), m.group(0).replace('procurement', 'xxxxxxxxxxx'), 1)
    d = src.replace('font-size:12.5px; line-height:1; color:var(--ink2);', 'font-size:12.5px; color:var(--ink2);', 1)
    assert d != src, 'the line-height rule of the saved ids is not in the page'
    e = src.replace('grid-template-columns:auto minmax(0,1fr); grid-template-areas:"d tags" "who who"', 'grid-template-columns:minmax(0,1fr) auto; grid-template-areas:"d tags" "who who"', 1)
    assert e != src, 'the phone layout rule of a line\'s head is not in the page'
    both = (1280, 390)
    return [('one line removed', a, 'lines on the page', both), ('one part mark taken off', b, 'lines confirmed in part', both),
            ('a search word taken out of one line', c, 'search "procurement"', both),
            ('the line-height rule of the saved ids taken out', d, 'page height after it is painted', both),
            ('the phone layout of a line\'s head as before round 3', e, 'lines whose kind marks lie over', (390,))]


def main():
    from playwright.sync_api import sync_playwright
    src = PAGE.read_text(encoding='utf-8')
    problems = []
    with sync_playwright() as p:
        br = p.chromium.launch()
        for width in (1280, 390):
            ctx = br.new_context(viewport={'width': width, 'height': 900})
            pg = ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(PAGE.as_uri(), wait_until='load'); pg.wait_for_timeout(300)
            bad = checks(pg, width)
            first = next(iter(EXP['queries'].items()))
            pg2 = ctx.new_page(); pg2.goto(PAGE.as_uri() + '#q=' + first[0], wait_until='load'); pg2.wait_for_timeout(200)
            if pg2.evaluate(VISIBLE) != first[1]: bad.append(f'search "{first[0]}" given in the address: got {pg2.evaluate(VISIBLE)}, expected {first[1]}')
            if errs: bad.append(f'page errors: {errs[:2]}')
            problems += [f'{width}px: {x}' for x in bad]
            caught = due = 0
            for name, text, must, widths in faulty(src):
                if width not in widths: continue
                due += 1
                pf = ctx.new_page(); pf.set_content(text, wait_until='load'); pf.wait_for_timeout(200)
                got = checks(pf, width)
                if any(x.startswith(must) for x in got): caught += 1
                else: problems.append(f'{width}px: CONTROL NOT CAUGHT: {name} (faults reported: {got[:2]})')
                pf.close()
            print(f'{width}px: {EXP["rows"]} lines; {len(EXP["kinds"])} kind buttons; {len(EXP["queries"])} searches; part filter; open and close; right edge; height when painted; marks clear of the date: '
                  f'{"pass" if not bad else str(len(bad)) + " fault(s)"}; faulty copies caught: {caught} of {due}')
            ctx.close()
        br.close()
    if problems:
        print('\n'.join(problems)); print(f'FAILED: {len(problems)} problem(s)'); sys.exit(1)
    print('test_page: the page passes every check at 1280 and 390 px, and every faulty copy was caught (4 at 1280 px, 5 at 390 px)')


if __name__ == '__main__':
    main()
