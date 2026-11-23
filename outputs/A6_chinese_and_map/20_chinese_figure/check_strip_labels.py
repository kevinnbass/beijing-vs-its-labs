"""Check that no label on the dated strip touches a numbered mark (run after cn_figure_build.py).

Run: python3 -I check_strip_labels.py
Why: in the English figure a label once touched a mark (ROUND3.md, item 2). Chinese labels have other widths, so the
Chinese strip is measured on its own, in the browser, at the widths it is shown and exported at.
For every label (the labels beside marks and the three dated flags) and every mark it takes the distance from the
mark's edge to the label's box, in strip units (the strip is drawn 1,400 units wide). A distance under MIN_GAP fails.
Control: the first label is moved onto another record's mark and measured again; if that is not reported as a
collision the check cannot fail and the script stops with an error. Exit 0 only if every width passes and the control
behaves. Round 4: 61 marks, 10 labels (7 beside marks, 3 dated flags).
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

F = Path(__file__).resolve().parent
PAGE = F / 'beijing_vs_labs_zh.html'
MIN_GAP, WIDTHS = 2.0, (1500, 1280, 390)

MEASURE = """() => {
  const svg = document.querySelector('#hero svg'), k = 1400 / svg.getBoundingClientRect().width;
  const marks = [...svg.querySelectorAll('a.pin circle')].map(c => { const r = c.getBoundingClientRect();
    return {n: c.parentElement.dataset.n, cx: (r.left + r.width / 2) * k, cy: (r.top + r.height / 2) * k, rad: r.width / 2 * k}; });
  const labels = [...svg.querySelectorAll('text.call, text.flagt')].map(t => { const r = t.getBoundingClientRect();
    return {t: t.textContent, l: r.left * k, r: r.right * k, top: r.top * k, b: r.bottom * k}; });
  return {marks, labels};
}"""
MOVE = """() => {
  const svg = document.querySelector('#hero svg');
  const lab = svg.querySelector('text.call'), n0 = lab.textContent.split(' ')[0];
  const pin = [...svg.querySelectorAll('a.pin')].find(a => a.dataset.n !== n0), c = pin.querySelector('circle');
  lab.setAttribute('x', c.getAttribute('cx')); lab.setAttribute('y', c.getAttribute('cy')); lab.setAttribute('text-anchor', 'middle');
  return [n0, pin.dataset.n];
}"""


def gaps(d):
    out = []
    for lab in d['labels']:
        for m in d['marks']:
            dx = max(lab['l'] - m['cx'], 0.0, m['cx'] - lab['r']); dy = max(lab['top'] - m['cy'], 0.0, m['cy'] - lab['b'])
            out.append(((dx * dx + dy * dy) ** 0.5 - m['rad'], lab['t'], m['n']))
    return sorted(out)


def main():
    ok = True
    with sync_playwright() as p:
        br = p.chromium.launch()
        for w in WIDTHS:
            pg = br.new_context(viewport={'width': w, 'height': 1000}, device_scale_factor=1, locale='zh-CN').new_page()
            pg.goto(PAGE.as_uri()); pg.evaluate('document.fonts.ready.then(() => 1)'); pg.wait_for_timeout(500)
            d = pg.evaluate(MEASURE); g = gaps(d)
            assert len(d['marks']) == 61 and len(d['labels']) == 10, (len(d['marks']), len(d['labels']))
            own = lambda x: x[1].split(' ')[0] == x[2]                      # a label beside its own mark is meant to sit close
            other = [x for x in g if not own(x)]
            print(f'width {w}: {len(d["labels"])} labels, {len(d["marks"])} marks; smallest distance {g[0][0]:.1f} ("{g[0][1]}" and mark {g[0][2]}); '
                  f'smallest to another record\'s mark: {other[0][0]:.1f} ("{other[0][1]}" and mark {other[0][2]}), then {other[1][0]:.1f} ("{other[1][1]}" and mark {other[1][2]})')
            if g[0][0] < MIN_GAP:
                ok = False
                for x in g:
                    if x[0] < MIN_GAP: print(f'   TOUCHES: "{x[1]}" and mark {x[2]} ({x[0]:.1f})')
            n0, target = pg.evaluate(MOVE); c = gaps(pg.evaluate(MEASURE))
            hit = [x for x in c if x[0] < MIN_GAP and x[1].startswith(n0 + ' ') and x[2] == target]
            if not hit: sys.exit(f'width {w}: the control (label {n0} moved onto mark {target}) was not reported: the check cannot fail')
            print(f'   control: label {n0} moved onto mark {target} is reported ({hit[0][0]:.1f}), as it must be')
        br.close()
    print('no label touches a mark' if ok else 'A LABEL TOUCHES A MARK')
    sys.exit(0 if ok else 1)


main()
