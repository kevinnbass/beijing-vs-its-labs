#!/usr/bin/env python3
"""Idea 25: the dated strip as a short silent animation (marks appear in date order, with a running date).

Run:  python3 -I build.py                                           checks, then writes the page and the capture plan
      nice -n 19 python3 frames.py      captures the frames and encodes the video files

Reads   ../../../figure/figure_data.txt   the dated records (the same file the figure is built from)
        ../../../figure/template.html      the figure's headline, key and notes: every sentence shown here must stand there
        ../a7lib.py                        the copied strip geometry, the page engine
Writes  quotes.tsv            every source line behind what the strip shows; scripts/cn_has.py must pass or nothing is built
        strip_animation.html  the page: one 1280 x 720 frame drawn for any time t (opens paused on the last frame)
        capture.json          what frames.py is to capture: frame rate, frame count, file names, still frames

Timing: 1.8 s of the empty strip, 19.2 s in which a line crosses the strip at an even pace and each mark appears as the
line reaches its date, 4.5 s of the full strip. 2023 and 2024 are drawn narrower, so they pass faster.
Counts and mark numbers shown (records, filled, open, the marks named in the note) are computed here from the data
file, not typed. Layout since round 4 (61 records): the key stands in a column at the right of the strip, inside its
card, and the strip is drawn at about 0.9 of the figure's size (see ../a7lib.py, card_layout).
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent))
import a7lib as L   # noqa: E402

FPS, INTRO, SWEEP, HOLD = 30, 1.8, 19.2, 4.5
CARD_TOP, PAD = 124, 7

EXTRA_CSS = """
#eyebrow { left:28px; top:20px; }
#h1 { left:28px; top:40px; font-size:32px; line-height:1.14; }
#clockbox { right:28px; top:16px; }
#date { font-size:48px; line-height:1.05; }
#count { font-size:16px; margin-top:5px; }
#tally { font-size:13.5px; margin-top:3px; }
#card { left:16px; top:%%CARD_TOP%%px; width:1248px; height:%%CARD_H%%px; }
#card svg { left:8px; top:%%PAD%%px; width:%%SVG_W%%px; height:%%SVG_H%%px; }
.stage ul.key { left:%%KEY_L%%px; top:16px; width:%%KEY_W%%px; }
#foot { left:28px; top:%%FOOT_Y%%px; width:1224px; font-size:13.5px; line-height:1.45; }
#foot p + p { margin-top:4px; }
#draft { right:28px; bottom:9px; font-size:11.5px; }
"""
OPENNESS = "Some purchases were reported approved, by press reports citing people they did not name, and Nvidia’s own filings report licensed sales to China."
COMPANIES = "The companies also bought and used home-made chips, by their own and their suppliers’ accounts."

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


def main():
    evs, checks, G, lane_names = L.load_events()
    lane_names, figure_check = L.check_against_figure(evs, lane_names)
    print('figure check:', figure_check)
    n_q = L.write_quotes(HERE / 'quotes.tsv', L.strip_quotes(evs, checks), 'Idea 25, the strip as a short animation: the source words behind every mark, label and dashed line.')
    print('cn_has.py:', L.run_has(HERE / 'quotes.tsv'), f'({n_q} lines in quotes.tsv)')

    total, solid = len(evs), sum(e['solid'] for e in evs)
    num = lambda sid: next(e['n'] for e in evs if e['sid'] == sid)          # a mark's number, by its saved id (never typed)
    not_nv = sorted((num('cn-policy-micron-decision'), num('cn-policy-desktop-2023')))
    case = sorted((num('cn-policy-samr-open-original'), num('cn-policy-samr-further-original')))
    n_t = L.template_has(' '.join(L.HEADLINE), *L.KEY_SENTENCES,
                         'Open marks rest on unnamed people.', 'no Chinese authority confirmed any of them',
                         'No published Chinese order against buying Nvidia chips was found in the policy pages and national document lists read.',
                         'are not about Nvidia.', 'are an antitrust case against Nvidia the company.',
                         'The records are a selection made to show both sides, not a census. The count of marks in a row is not a measure.',
                         'Some purchases were reported approved by outlets citing people they did not name. Nvidia’s own filings report licensed sales to China.',
                         'The companies also bought and used home-made chips.')
    print(f'template: {n_t} sentences of the headline, key and notes stand in figure/template.html')
    argument = L.PROJ / 'ARGUMENT_referenced.md'
    answer = next(line for line in argument.read_text(encoding='utf-8').splitlines() if line.startswith('**The answer.** '))
    approved = 'Third, ' + OPENNESS[0].lower() + OPENNESS[1:-1].replace('’', "'") + ' (point 19).'
    companies = 'they also bought, used and trained on home-made chips, by their own and their suppliers\' accounts (points 9 and 20).'
    if approved not in answer or companies not in answer:
        sys.exit('the argument no longer gives the strip footnote’s approvals, licensed sales and company attribution')

    x0, x1 = L.GL, max(e['x'] for e in evs)
    when = lambda x: round(INTRO + (x - x0) / (x1 - x0) * SWEEP, 4)
    frames = round((INTRO + SWEEP + HOLD) * FPS)
    scene = dict(fps=FPS, frames=frames, total=total, dim=1.0, geom=L.geom_json(),
                 marks=[dict(n=e['n'], x=round(e['x'], 2), cy=round(e['cy'], 2), on=when(e['x']), pulse=[when(e['x'])], focus=[[0, 1e9]]) for e in evs],
                 flags=[dict(i=i, on=when(L.X(d))) for i, (d, _, _) in enumerate(L.FLAGS)],
                 segs=[dict(t0=INTRO, t1=INTRO + SWEEP, x0=x0, x1=round(x1, 2))], tally_on=INTRO + SWEEP + 0.4)
    assert all(INTRO < m['on'] <= INTRO + SWEEP for m in scene['marks']) and all(INTRO < f['on'] < INTRO + SWEEP for f in scene['flags'])
    order = [m['n'] for m in sorted(scene['marks'], key=lambda m: m['on'])]
    by_n = {e['n']: e for e in evs}
    assert all(by_n[a]['date'] <= by_n[b]['date'] for a, b in zip(order, order[1:])), 'marks must appear in date order'

    c = L.card_layout(G, PAD)
    foot_y = CARD_TOP + c['card_h'] + 11
    css = EXTRA_CSS
    for k, v in (('CARD_TOP', CARD_TOP), ('PAD', PAD), ('CARD_H', c['card_h']), ('SVG_W', c['svg_w']), ('SVG_H', c['svg_h']), ('KEY_L', c['key_left']), ('KEY_W', c['key_w']), ('FOOT_Y', foot_y)):
        css = css.replace(f'%%{k}%%', str(v))
    assert '%%' not in css
    first, last = min(e['date'] for e in evs), max(e['date'] for e in evs)
    stage = f"""<p class="eyebrow" id="eyebrow">China · Nvidia chips · {first.year} to {MONTHS[last.month - 1]} {last.year}</p>
<h1 id="h1">{L.esc(L.HEADLINE[0])}<br>{L.esc(L.HEADLINE[1])}</h1>
<div class="clock" id="clockbox"><div id="date"></div><div id="count"></div><div id="tally">{solid} filled, on the record · {total - solid} open, press reports</div></div>
<div class="card" id="card">
{L.strip_svg(evs, G, lane_names)}
{L.KEY}
</div>
<div class="foot" id="foot"><p><b>Read with care.</b> Open marks rest on unnamed people; in the answers found, no Chinese authority confirmed any of them. No published Chinese order against buying Nvidia chips was found in the policy pages and national document lists read. Marks {not_nv[0]} and {not_nv[1]} are not about Nvidia; marks {case[0]} and {case[1]} are an antitrust case against Nvidia the company. The records are a selection made to show both sides, not a census: the count of marks in a row is not a measure. {OPENNESS} {COMPANIES}</p>
<p><b>Source.</b> One mark for each of {total} dated records, 2023 to November 2026. A script found each record’s own words in a saved copy of its source. The numbers on the marks are those of the figure “{L.esc(" ".join(L.HEADLINE))}”, which lists every record.</p></div>
<p class="draft" id="draft">Draft by Claude, Anthropic’s model.</p>"""
    # round 10 (the session's ruling, Nov 25, 2026): the frame carries the credit only; words saying the copy is local or
    # unpublished are untrue of a public copy, and a release cannot reach pixels. They must never be drawn into the frame.
    # round 11 (the session's ruling, Nov 26, 2026): that note stands nowhere, pixels included: not in the frame and not in
    # the page below it. OLD_NOTE is spelled in two parts so that no public copy of this file holds it.
    OLD_NOTE = 'Local; not ' + 'published.'
    def frame_says_local(st):                     # the credit line names no local or unpublished state; nothing in the frame says "not published" or "Local;"
        draft = re.search(r'<p class="draft" id="draft">(.*?)</p>', st, re.S).group(1).lower()
        return [w for w in ('local', 'publish') if w in draft] + [w for w in ('not published.', 'local;') if w in st.lower()]
    if frame_says_local(stage): sys.exit(f'the frame says {frame_says_local(stage)}: it carries the credit only')
    assert frame_says_local(stage.replace('model.</p>', f'model. {OLD_NOTE}</p>')), 'control: the old credit line must be refused'
    below = f"""  <p>The dated strip as a short silent animation: the {total} marks appear in date order while the date runs at the top right. This page draws any moment of it; the video files beside it were captured from this page frame by frame. No one has yet watched them play through: they were checked by script and as still frames.</p>
  <p>The video file, <code>strip_animation.mp4</code> (1280 by 720, no sound):</p>
  <video data-src="strip_animation.mp4" data-poster="stills/strip_animation_00s.png" controls muted playsinline preload="none" width="1280" height="720"></video>
  <p>For a post: <code>strip_animation.gif</code> or <code>strip_animation.webp</code> (both 1280 by 720).</p>
  <p class="small">Draft by Claude, Anthropic’s model.</p>"""
    if 'local; not' in (stage + below).lower(): sys.exit('the page says the copy is local or not published: the credit only (round 11)')
    assert 'local; not' in (below + OLD_NOTE).lower(), 'control: the old note must be seen'
    (HERE / 'strip_animation.html').write_text(L.page('Dated Strip Animation', stage, below, scene, css), encoding='utf-8')

    dur = frames / FPS
    stills = [[f'{t:02d}s', t * FPS] for t in range(0, int(dur), 2)] + [['last', frames - 1]]            # a frame every 2 seconds, and the last
    plan = dict(page='strip_animation.html', fps=FPS, frames=frames, mp4='strip_animation.mp4', master='_master_lossless.mkv', crf=15,
                gif=dict(file='strip_animation.gif', fps=15, width=1280, colors=160), webp=dict(file='strip_animation.webp', fps=15, width=1280, quality=82),
                stills=stills, expect=[])
    hk = next(e for e in evs if e['sid'] == 'cn-clips-evidence-1' and e['C'])
    plan['label_control'] = dict(id=f'c{hk["n"]}', x=round(evs[0]['x'], 1), y=round(evs[0]['cy'] + 4, 1))     # the control: this label, set down on mark 1, must be reported
    plan['made_from'] = L.made_from(HERE, [L.FIG / 'figure_data.txt', L.FIG / 'figure_events.tsv', L.FIG / 'beijing_vs_labs.html', L.FIG / 'template.html', argument, HERE.parent / 'a7lib.py', HERE / 'build.py', HERE / 'quotes.tsv', HERE / 'strip_animation.html'])
    (HERE / 'capture.json').write_text(json.dumps(plan, indent=1), encoding='utf-8')
    per = {k: sum(e['lane'] == k for e in evs) for k in L.ORDER}
    print(f'records {total} ({per}); filled (on the record) {solid}, open (press reports) {total - solid}; marks not about Nvidia {not_nv}, the antitrust case {case}')
    print(f'layout: strip drawn at {c["scale"]:.3f} of the figure\'s size ({c["svg_w"]} x {c["svg_h"]} px), card {c["card_h"]} px high, note from y {foot_y}')
    print(f'timing: {frames} frames at {FPS} a second = {dur:.2f} s; first mark at {min(m["on"] for m in scene["marks"]):.2f} s, last at {max(m["on"] for m in scene["marks"]):.2f} s; marks appear in date order (checked)')
    print('written', HERE / 'strip_animation.html', 'and capture.json; stills planned at frames', [s[1] for s in stills])


main()
