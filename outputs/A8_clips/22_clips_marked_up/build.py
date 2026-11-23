#!/usr/bin/env python3
"""Build the two clips marked up, sentence by sentence (idea 22).

Run: python3 -I build.py
Reads   ../40_checked_by_ear/compared.json   the clips cut into sentences and parts, with the first speech pass's words and times
        marks.txt                             the verdict and the reason for each part (hand-written; see its header)
        extra_refs.tsv                        sources that the project's own references file does not list
Writes  clips_marked_up_base.txt, then runs scripts/cn_doc_build.py on it, which writes clips_marked_up.md and .html only
        if every quotation and every hidden statement is found in the saved copy of a source cited beside it.
The sentence words, the times and every count in the document come from the data, not from typing.
"""
import csv, json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
DATA = HERE.parent / '40_checked_by_ear' / 'compared.json'
TABLE = HERE.parents[2] / 'tables' / 'house_licence_table.tsv'
LABEL = {'A': 'Borne out by the record', 'AB': 'Borne out on direction; too flat as worded', 'B': 'Too flat',
         'C': 'Not established by any saved source', 'D': 'Outside what this project checked'}
SHORT = {'A': 'Borne out'}
ORDER = ['A', 'AB', 'B', 'C', 'D']
NUM = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']


def clock(t):
    return f'{int(t // 60)}:{int(t % 60):02d}'


def length_words(sec):
    m, s = divmod(int(sec), 60)
    return f'{m} minute{"s" if m != 1 else ""} {s} seconds' if m else f'{s} seconds'


def load_marks():
    marks, cur = {}, None
    for ln in (HERE / 'marks.txt').read_text(encoding='utf-8').splitlines():
        if ln.startswith('#') or not ln.strip(): continue
        if ln.startswith('@ '):
            parts = [x.strip() for x in ln[2:].split('|')]
            if parts[1] not in LABEL: sys.exit(f'marks.txt: unknown code in: {ln}')
            if parts[0] in marks: sys.exit(f'marks.txt: {parts[0]} twice')
            cur = marks[parts[0]] = {'code': parts[1], 'qual': parts[2] if len(parts) > 2 else '', 'text': [], 'hidden': [], 'own': ''}
        elif cur is None: sys.exit(f'marks.txt: text before the first entry: {ln[:60]}')
        elif ln.startswith('= '):                                  # the part's words, quoted from another saved source than the first speech pass
            if cur['text'] or cur['own']: sys.exit(f'marks.txt: a "= " line must come straight after its "@" line: {ln[:60]}')
            cur['own'] = ln[2:].strip()
        elif ln.startswith('!!'): cur['hidden'].append(ln)
        else: cur['text'].append(ln.strip())
    return marks


def label(m):
    if m['qual']: return f'{SHORT.get(m["code"], LABEL[m["code"]])}, {m["qual"]}'
    return LABEL[m['code']]


def clip_lines(clip, c, marks):
    out = []
    units = [u for u in c['units'] if u['in_transcript']]
    sentences = []
    for u in units:
        if not sentences or sentences[-1][0] != u['sentence']: sentences.append((u['sentence'], []))
        sentences[-1][1].append(u)
    for sid, us in sentences:
        head = f'Sentence {sid} · {clock(us[0]["start"])} to {clock(us[-1]["end"])}'
        if clip == 'pottinger': head += f' · {us[0]["speaker"]}'
        out += [f'**{head}**', '']
        for u in us:
            m = marks[u['id']]
            if '"' in u['text']: sys.exit(f'{u["id"]}: the transcript words hold a straight double quote')
            when = f'**{clock(u["start"])} to {clock(u["end"])}.** ' if len(us) > 1 else ''
            words = m['own'] or f'"{u["text"]}" [{c["cite"]}]'
            out.append(f'{when}{words} **{label(m)}.** {" ".join(m["text"])}')
            out += m['hidden'] + ['']
    return out, len(sentences), len(units)


def table_numbers():
    """Sums over the project's copy of the Commerce Department's table of licence applications (status on May 11, 2026)."""
    rows = list(csv.DictReader((l for l in TABLE.read_text(encoding='utf-8').splitlines() if not l.startswith('#')), delimiter='\t'))
    n = lambda r: int(r['chip_count'].replace(',', ''))
    tot = sum(n(r) for r in rows)
    if tot != 3444160: sys.exit(f'STOPPED: the table sums to {tot:,}, not the 3,444,160 the committee\'s summary states')
    nv = [r for r in rows if r['exporter'] == 'Nvidia' and r['status'] == 'Approved, not shipped']
    if any(r['status'] != 'Approved, not shipped' for r in rows if r['status'].startswith('Approved')): sys.exit('STOPPED: an approved application is not marked "Approved, not shipped"')
    rwa = sum(n(r) for r in rows if r['status'] == 'RWA')
    sea = [r for r in rows if r['location'] in ('Malaysia', 'Indonesia', 'Thailand')]
    if not sea or any(r['status'] != 'RWA' for r in sea): sys.exit('STOPPED: an application for Malaysia, Indonesia or Thailand is not marked RWA')
    return {'NV_APPROVED': f'{sum(n(r) for r in nv):,}', 'NV_APPS': str(len(nv)), 'RWA_CHIPS': f'{rwa:,}', 'RWA_PCT': str(round(100 * rwa / tot)),
            'SEA_CHIPS': f'{sum(n(r) for r in sea):,}', 'SEA_APPS': NUM[len(sea)]}


def main():
    data = json.loads(DATA.read_text(encoding='utf-8'))
    marks = load_marks()
    nums = table_numbers()
    for uid, m in marks.items():
        m['text'] = [re.sub(r'\{([A-Z_]+)\}', lambda x: nums[x.group(1)], t) for t in m['text']]
        if any('{' in t or '}' in t for t in m['text']): sys.exit(f'marks.txt: {uid}: a brace is left in the text')
    diff_rows = [l.split('\t') for l in (DATA.parent / 'differences.tsv').read_text(encoding='utf-8').splitlines()[1:] if l.strip()]
    n_other = sum(1 for r in diff_rows if r[5] != 'spelling only')         # places where another reading has other words
    ids = [u['id'] for c in data['clips'].values() for u in c['units'] if u['in_transcript']]
    if sorted(ids) != sorted(marks): sys.exit(f'marks.txt and the clips do not match: {sorted(set(ids) ^ set(marks))}')
    L, P = data['clips']['luckey'], data['clips']['pottinger']
    body_l, ns_l, nu_l = clip_lines('luckey', L, marks)
    body_p, ns_p, nu_p = clip_lines('pottinger', P, marks)
    count = lambda c, code: sum(1 for u in c['units'] if u['in_transcript'] and marks[u['id']]['code'] == code)
    asked = sum(1 for u in P['units'] if u['speaker'] == 'Amanpour')
    d_l = L['counts']['published_transcript_differences']
    like = [n for u in L['units'] if u['id'] == 'L3' for n in u['notes'] if n['witness'] == 'second pass' and n['other'] == 'Like']
    if not like: sys.exit('STOPPED: the second pass no longer has the word Like after sentence L3; the note on L4 would be wrong')
    W2_AT = 'cnpol-x-overton-2123392702821580811 | Like there are Chinese companies that want to buy Nvidia GPUs.'
    today = datetime.now(timezone.utc)
    o = ['# The two clips, sentence by sentence',
         f"@deck Every sentence of Palmer Luckey's {length_words(L['duration'])} and of Matt Pottinger's {length_words(P['duration'])} with Christiane Amanpour, each with a verdict and its sources.",
         '',
         f'@note Draft by Claude, Anthropic\'s model. Local; not published. Built {today.strftime("%b")} {today.day}, {today.year} (UTC).',
         "@note The words of both clips are a speech program's transcripts [clip-luckey] [clip-pottinger], but for one sentence of Luckey's (L4), which is quoted from the text of the post that carries the clip. Nobody has checked any of them by ear. Times are minutes and seconds into each clip. A page for checking them by ear is in the folder 40_checked_by_ear, beside this one.",
         "@note Anthropic has argued in public for controls on chip exports to China (that is from the model's general knowledge; no saved page is cited for it), so judge this note by its sources.",
         '',
         '## How to read the verdicts',
         '',
         '- **Borne out by the record.** A saved source states it. Where that source is a press report citing unnamed people, the line says so.',
         '- **Too flat.** The direction is right, but the wording says more than the record shows.',
         "- **Not established by any saved source.** Nothing saved for this project states it. Where the sentence charges a person or a company with wrongdoing, the line says that it is the speaker's allegation and stops there.",
         '- **Outside what this project checked.** A question, an opinion, a forecast, or a matter this project did not look into.',
         '',
         "The verdicts follow the project's assessment of the two clips and its referenced argument. They do not go beyond them. Words between quotation marks were found in the saved copy by a script. Where Chinese words are quoted, the English beside them is ours, not an official translation.",
         '',
         "The argument's answer to Luckey's claim is yes on direction, with five limits. Beijing was not one actor. The pressure came as public warnings and unpublished guidance, not as a published ban. Some purchases were approved and some chips came in. The companies had reasons of their own, and American curbs and conditions pushed too. And what Beijing meant by it is not settled. Sentences L3 and L5 below give a source for each.",
         '',
         f'The speech program punctuated the clips into {ns_l} and {ns_p} sentences. Long sentences are cut into parts so that each part gets one verdict: {nu_l} parts and {nu_p} parts.',
         '']
    # a list, not a table: at phone width the page drops a table's header row, and the two columns of numbers lose their names
    for code in ORDER: o.append(f"- **{LABEL[code]}:** {count(L, code)} of the {nu_l} parts of Luckey's clip, {count(P, code)} of the {nu_p} parts of Pottinger's.")
    o += ['',
          f"**Read with care.** These are counts of parts of sentences, not of weight. Of the {count(P, 'D')} parts of Pottinger's clip marked outside, {NUM[asked]} are the interviewer's question and the rest are opinions and forecasts.",
          '',
          f"## 1. Palmer Luckey ({length_words(L['duration'])})",
          '',
          f"Posted on X by @overton_news on Nov 19, 2026 [clip-luckey]. The clip is part of a talk with Andrew Ross Sorkin at the DealBook Summit 2026; the saved transcript gives no day for the talk. That transcript, published by The Singju Post, holds the clip's passage with {NUM[d_l]} small differences of wording [cn-clips-singju-luckey]. One of them lies between his two main sentences. There the transcript has \"Chinese companies like this\", and the text of the post has \"Like there are Chinese companies\" [cnpol-x-overton-2123392702821580811]. A second speech pass has the word Like there too; the first speech pass has no word there. So the second of the two sentences (L4) is quoted below from the text of the post.",
          '!! cn-clips-singju-luckey | Palmer Luckey joined Andrew Ross Sorkin at the DealBook Summit 2026',
          f'!! {W2_AT}',
          ''] + body_l + [
          '**What the clip leaves out**', '',
          'In the published transcript of the whole talk he says, just before the words of the clip: "I don\'t think that we should be exporting chips to China" [cn-clips-singju-luckey]. The clip alone does not show that.',
          '',
          f"## 2. Matt Pottinger with Christiane Amanpour ({length_words(P['duration'])})",
          '',
          f"Posted on X by @amanpour on Nov 18, 2026 [clip-pottinger]. The first {NUM[len({u['sentence'] for u in P['units'] if u['speaker'] == 'Amanpour'})]} sentences are the interviewer's question. Who speaks each sentence is judged from the words.",
          ''] + body_p + [
          '## How the two clips fit together',
          '',
          "Pottinger blames Jensen Huang for China's AI models. Luckey says Beijing kept Nvidia's chips out. Both can hold, for different chips and years. Chinese companies did train models on Nvidia chips (sentences P4 and P12). By Washington's own table, none of the Nvidia chips it had approved by May 11, 2026 had shipped (sentence P12). On the H200 chips at issue in 2026, Nvidia's report for the quarter to Jul 26, 2026 says shipments under the H200 licences \"account for less than 1% of Data Center revenue in our most recent quarter\" [man-ms-sec-10q-2026-07]. On its results call for the quarter ended Oct 25, 2026 it said: \"Q3 sales of licensed Hopper Data Center products to China was $2.4 billion\", and then \"we are no longer shipping licensed Hopper Data Center products to China\" [cn-o38-nvda-q3fy27-call-transcript-pdf]. It gave no reason, and it did not say how many of those chips crossed into mainland China.",
          '!! man-ms-sec-10q-2026-07 | For the quarterly period ended July 26, 2026',
          '!! cn-o38-nvda-q3fy27-call-transcript-pdf | Q3 2027 Earnings Call',
          '',
          '## What this note does not show',
          '',
          '- Neither clip has been checked by ear. If a word changes, the verdict on its sentence may need another look.',
          f'- Other machine readings and published texts of the two clips have other words in {n_other} places; the listening sheet in the folder 40_checked_by_ear lists them. Each was read against its verdict here, and none changes one.',
          '- The pages on the outages and on attacks (sentences P6 to P11) were saved on Nov 20, 2026, days after the events. Later accounts may differ.',
          '- It says nothing on whether any law was broken.',
          '!! cn-clips-whitehouse-outages | FETCHED: 2026-11-20',
          '']
    base = HERE / 'clips_marked_up_base.txt'
    base.write_text('\n'.join(o), encoding='utf-8')
    r = subprocess.run(['python3', '-I', str(ROOT / 'scripts' / 'cn_doc_build.py'), str(base), '--refs', str(HERE / 'extra_refs.tsv'),
                        '--title', 'Two Clips Marked Up', '--eyebrow', 'China chip policy · the two clips'], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr.strip()); sys.exit('STOPPED: cn_doc_build.py did not pass; nothing was written')
    print('verdicts by clip (parts): ' + '; '.join(f'{LABEL[c]}: {count(L, c)} + {count(P, c)}' for c in ORDER))


if __name__ == '__main__':
    main()
