"""Write the two inputs of the Chinese figure, figure_data.txt and template.html, from the core's files and the Chinese parts.

Run: python3 -I make_inputs.py            writes both; stops if the core's English changed since the Chinese was made
     python3 -I make_inputs.py --refresh --accept
                                         updates the three English copies and records the current English T, S,
                                         optional A and strip wording in zh_lines.txt (ET, ES, EA, EC).
                                         Run this after reading the Chinese of every changed record.
Reads: english_originals/figure_data.txt, english_originals/template.html.copy (copies of the core's
       ../../../figure/figure_data.txt and template.html; the script stops if a copy is not the core's present file),
       zh_lines.txt (the Chinese of every record) and template_body_zh.txt (the Chinese page body).
Writes: figure_data.txt   the core's blocks in the core's order, each with its date, saved id, N, Q, E, U lines and label
                          place unchanged, the T, S and label words in Chinese, and a Z line where Q is English and the Chinese label for any second source; every
                          "!" check line of the core unchanged; then the extra check lines of zh_lines.txt.
                          (Round 8, after core edit 7 of Nov 25, 2026: a core block's "N" line, the record's fixed number,
                          is carried right after its "@" line, as the core has it.)
        template.html     the core template's head and styles with a few changes for Chinese type, then the Chinese body.
Compare the three English copies with the core and update the Chinese before refreshing and accepting.
"""
import argparse
import re, sys
from pathlib import Path

F = Path(__file__).resolve().parent
EN = F / 'english_originals'
CORE = F.parents[2] / 'figure'
MIRRORS = {
    'figure_data.txt': CORE / 'figure_data.txt',
    'template.html.copy': CORE / 'template.html',
    'cn_figure_build.py': CORE.parents[2] / 'scripts' / 'cn_figure_build.py',
}
CJK = re.compile(r'[぀-ヿ一-鿿]')
FIELDS = ('D', 'T', 'S', 'Z', 'C', 'CP', 'A', 'ET', 'ES', 'EA', 'EC')
LOCAL_BODY_MARKS = set()

HEAD_CHANGES = [  # in the core template's head: (the core's text, the Chinese page's text); each must occur exactly once
    ('<html lang="en">', '<html lang="zh-Hans">'),
    ('<title>Beijing vs. Its Labs</title>', '<title>北京与AI企业</title>'),
    ('  --font-text: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;',
     '  --font-text: "Inter", "Noto Sans CJK SC", "Noto Sans SC", "Source Han Sans SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", system-ui, -apple-system, "Segoe UI", sans-serif;'),
    ('  --font-head: "Space Grotesk", "Inter", system-ui, sans-serif;',
     '  --font-head: "Space Grotesk", "Inter", "Noto Sans CJK SC", "Noto Sans SC", "Source Han Sans SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", system-ui, sans-serif;'),
    ('font-family: var(--font-text); font-size: 16px; line-height: 1.5; }', 'font-family: var(--font-text); font-size: 16px; line-height: 1.65; }'),
    ('h1 { font-family: var(--font-head); font-size: clamp(28px, 3.5vw, 46px); line-height: 1.08; letter-spacing: -0.015em; margin: 0 0 12px; max-width: 24ch; text-wrap: balance; }',
     'h1 { font-family: var(--font-head); font-size: clamp(27px, 3.4vw, 44px); line-height: 1.2; margin: 0 0 12px; max-width: 21em; }\nh1 span { display: inline-block; }'),
    ('.deck { margin: 0; color: var(--ink2); font-size: 18px; max-width: 78ch; }',
     '.deck { margin: 0; color: var(--ink2); font-size: 18px; max-width: 42em; }\n.draft { margin: 14px 0 0; font-size: 12.5px; color: var(--muted); max-width: 60em; }'),
    ('.card .sub { margin: 0 0 12px; color: var(--ink2); font-size: 14.5px; max-width: 72ch; }',
     '.card .sub { margin: 0 0 12px; color: var(--ink2); font-size: 14.5px; max-width: 48em; text-wrap: pretty; }'),
    ('.bar-note { grid-column: 2; font-size: 12.5px; color: var(--muted); line-height: 1.35; }', '.bar-note { grid-column: 2; font-size: 12.5px; color: var(--muted); line-height: 1.5; }'),
    ('.revcard .big { margin: 0; font-size: 15.5px; font-weight: 600; max-width: 60ch; }', '.revcard .big { margin: 0; font-size: 15.5px; font-weight: 600; max-width: 36em; }'),
    ('.pp span { font-size: 14.5px; color: var(--ink2); line-height: 1.4; }', '.pp span { font-size: 14.5px; color: var(--ink2); line-height: 1.55; }'),
    ('table.pv { width: 100%; border-collapse: collapse; font-size: 13.5px; line-height: 1.35; color: var(--ink2); }', 'table.pv { width: 100%; border-collapse: collapse; font-size: 13.5px; line-height: 1.5; color: var(--ink2); }'),
    ('.vlab { font-size: 13.5px; line-height: 1.3; }', '.vlab { font-size: 13.5px; line-height: 1.45; }'),
    ('.notes ul { margin: 6px 0 0; padding-left: 20px; color: var(--ink2); font-size: 14px; max-width: 110ch; }', '.notes ul { margin: 6px 0 0; padding-left: 20px; color: var(--ink2); font-size: 14px; max-width: 60em; }'),
    ('#tip .tq { font-style: italic; opacity: 0.92; }', '#tip .tq { opacity: 0.95; } #tip .to { margin-top: 4px; font-size: 12px; opacity: 0.8; }'),
]


def read_zh(source):
    blocks, extra, cur = {}, [], None
    for n, ln in enumerate(source.splitlines(), 1):
        if not ln.strip() or ln.startswith('#'): continue
        if ln.startswith('@ '):
            _, lane, sid = ln.split()
            assert (lane, sid) not in blocks, f'zh_lines.txt line {n}: block given twice: {ln}'
            cur = blocks[(lane, sid)] = {}
        elif ln.startswith('! '): extra.append(ln)
        else:
            k, _, v = ln.partition(' ')
            assert k in FIELDS and cur is not None and k not in cur and v.strip(), f'zh_lines.txt line {n} not understood: {ln[:50]}'
            cur[k] = v.strip()
    return blocks, extra


def read_core(source):
    """The core data as a list of items: ('raw', line) or ('block', dict of its lines)."""
    items, cur = [], None
    for ln in source.splitlines():
        if ln.startswith('@ '):
            _, lane, kind, d, dl, sid = ln.split()
            cur = dict(lane=lane, kind=kind, date=d, dl=dl, sid=sid); items.append(('block', cur))
        elif cur is not None and ln[:2] in ('T ', 'S ', 'Q ', 'E ', 'U ', 'C ', 'N ', 'A '): cur[ln[0]] = ln[2:].strip()
        else:
            if ln.strip(): cur = None if ln.startswith('#') else cur      # a "!" check line inside a block (the core has two since Nov 25, 2026) does not end it
            items.append(('raw', ln))
    return items


def accept(core, source):
    """Return zh_lines.txt with the core's present English pins under each block."""
    en = {(b['lane'], b['sid']): b for k, b in core if k == 'block'}
    out, key = [], None

    def flush():
        nonlocal key
        if key:
            record = en[key]
            out.extend([f'ET {record["T"]}', f'ES {record["S"]}'])
            if 'A' in record:
                out.append(f'EA {record["A"]}')
            if 'C' in record:
                out.append(f'EC {record["C"].split(" ", 3)[3]}')
        key = None
    for ln in source.splitlines():
        if ln.startswith('@ '):
            flush(); _, lane, sid = ln.split(); key = (lane, sid); assert key in en, f'no such record in the core: {ln}'
            out.append(ln)
        elif ln[:3] in ('ET ', 'ES ', 'EA ', 'EC '): continue
        elif not ln.strip() or ln.startswith('#') or ln.startswith('!'):
            flush(); out.append(ln)
        else: out.append(ln)
    flush()
    return '\n'.join(out) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--refresh', action='store_true', help='update the English copies after input validation')
    parser.add_argument('--accept', action='store_true', help='record reviewed English wording in zh_lines.txt')
    args = parser.parse_args()
    english = {name: path.read_bytes() for name, path in MIRRORS.items()}
    stale = [name for name, data in english.items() if not (EN / name).is_file() or (EN / name).read_bytes() != data]
    if stale and not args.refresh:
        sys.exit(f'english_originals differs from the core: {", ".join(stale)}. Review the changes before using --refresh.')
    core = read_core(english['figure_data.txt'].decode('utf-8'))
    zh_path = F / 'zh_lines.txt'
    zh_text = zh_path.read_text(encoding='utf-8')
    if args.accept:
        zh_text = accept(core, zh_text)
    zh, extra = read_zh(zh_text)
    out, used, bad = [], set(), []
    for kind, b in core:
        if kind == 'raw': out.append(b); continue
        key = (b['lane'], b['sid']); z = zh.get(key)
        if z is None: bad.append(f'no Chinese for {key}'); continue
        used.add(key)
        if z.get('ET') != b['T']: bad.append(f'the core\'s English line changed, or was never accepted: {key}\n   core: {b["T"]}\n   was:  {z.get("ET")}')
        if z.get('ES') != b['S']: bad.append(f'the core\'s source line changed, or was never accepted: {key}\n   core: {b["S"]}\n   was:  {z.get("ES")}')
        if z.get('EA') != b.get('A'): bad.append(f"{key}: the core's second source changed or was never accepted")
        strip_text = b['C'].split(' ', 3)[3] if 'C' in b else None
        if z.get('EC') != strip_text: bad.append(f"{key}: the core's strip wording changed or was never accepted: {z.get('EC')!r} -> {strip_text!r}")
        if ('A' in b) != ('A' in z): bad.append(f'{key}: translate the second source label exactly where the core gives one')
        english_q = not CJK.search(b['Q'])
        if english_q != ('Z' in z): bad.append(f'{key}: a Z line is needed exactly where Q is English')
        if ('C' in b) != ('C' in z): bad.append(f'{key}: a C line is needed exactly where the core has one')
        if (b['dl'] != '-') != ('D' in z): bad.append(f'{key}: a D line is needed exactly where the core gives a date label')
        if any(('"' in z.get(k, '') or '“' in z.get(k, '')) for k in ('S', 'Z', 'D', 'A')): bad.append(f'{key}: quote marks in an S, Z, D or A line')
        if ' ' in z.get('D', ''): bad.append(f'{key}: a space in a D line')
        out.append(f'@ {b["lane"]} {b["kind"]} {b["date"]} {z.get("D", "-")} {b["sid"]}')
        if 'N' in b:
            assert re.fullmatch(r'\d+', b['N']), (key, b['N'])
            out.append(f'N {b["N"]}')
        out.append(f'T {z.get("T", "")}'); out.append(f'S {z.get("S", "")}'); out.append(f'Q {b["Q"]}')
        if 'A' in b and 'A' in z:
            sid, _ = b['A'].split(' | ', 1)
            out.append(f'A {sid} | {z["A"]}')
        if 'Z' in z: out.append(f'Z {z["Z"]}')
        if 'E' in b: out.append(f'E {b["E"]}')
        if 'U' in b: out.append(f'U {b["U"]}')
        if 'C' in b and 'C' in z:
            place = z.get('CP') or ' '.join(b['C'].split(' ', 3)[:3])
            assert re.fullmatch(r'(start|end|middle) -?[\d.]+ -?[\d.]+', place), (key, place)
            out.append(f'C {place} {z["C"]}')
    bad += [f'a block of zh_lines.txt is not a record of the core any more: {k}' for k in zh if k not in used]
    if bad:
        print('\n'.join(bad)); sys.exit(f'{len(bad)} problems; nothing written')
    head = ['# Data for the Chinese-language version of the figure "Beijing vs. its labs" (cn_figure_build.py in this folder reads this file).',
            '# WRITTEN BY make_inputs.py from english_originals/figure_data.txt (the core\'s data) and zh_lines.txt: do not edit it here.',
            '# Each block: the core\'s "@" line, Q, E, U lines and label place, unchanged; T, S and the label words in Simplified Chinese;',
            '# Z = my Chinese for an English Q (shown as a translation, never inside quote marks). The core\'s own header follows.', '']
    tail = ['', '# Added for the Chinese version: exact words the Chinese page puts between quote marks (from zh_lines.txt)'] + extra
    t = english['template.html.copy'].decode('utf-8')
    cut = t.index('<body>')
    h = t[:cut]
    for a, b in HEAD_CHANGES:
        assert h.count(a) == 1, f'the core template\'s head no longer has exactly one: {a[:70]}'
        h = h.replace(a, b)
    body = (F / 'template_body_zh.txt').read_text(encoding='utf-8')
    marks = lambda s: set(re.findall(r'%%[A-Z_0-9]+(?::[a-z0-9-]+)?%%', s))
    expected_marks = marks(t[cut:]) | LOCAL_BODY_MARKS
    body_marks = marks(body)
    if expected_marks != body_marks:
        sys.exit(f'Chinese body placeholders disagree with the core and local additions: '
                 f'missing {sorted(expected_marks - body_marks)}, unexpected {sorted(body_marks - expected_marks)}')
    for name in stale:
        (EN / name).write_bytes(english[name])
        print(f'english_originals/{name}: refreshed from {MIRRORS[name]}')
    if args.accept:
        zh_path.write_text(zh_text, encoding='utf-8')
    (F / 'figure_data.txt').write_text('\n'.join(head + out + tail) + '\n', encoding='utf-8')
    n = sum(1 for k, _ in core if k == 'block')
    print(f'figure_data.txt written: {n} records ({sum(1 for k in zh if "Z" in zh[k])} with a Z line), {sum(1 for k, b in core if k == "raw" and b.startswith("! "))} check lines of the core, {len(extra)} added')
    (F / 'template.html').write_text(h + body, encoding='utf-8')
    print(f'template.html written: the core\'s head with {len(HEAD_CHANGES)} changes, the Chinese body with {len(body_marks)} kinds of placeholder (the same as the core\'s)')


main()
