# Repository copy. Changed from the working copy: paths only (README.md, "Files changed from the working copies").
"""Shared helpers for the China chip-policy outputs (the figure and the referenced argument).

page(sid)        every saved form of sources/<sid> as one normalised string (text files and bodies without tags;
                 since Nov 23, 2026 also a web page stored as body.pdf or body.bin, told by its first bytes)
has(quote, sid)  True when the quotation stands in the saved copy, ignoring spacing and the style of quote marks
url_of(sid)      the page's address from meta.json; None when it is missing or cut short (a hand-saved PDF's header)
"""
import html, json, re, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources'
_cache = {}


def norm(s):
    s = unicodedata.normalize('NFKC', s)
    for a, b in (('’', "'"), ('‘', "'"), ('ʼ', "'"), ('“', '"'), ('”', '"'), ('—', '-'), ('–', '-'), ('ﬃ', 'ffi'), ('ﬄ', 'ffl'), ('ﬁ', 'fi'), ('ﬂ', 'fl'), ('ﬀ', 'ff')):
        s = s.replace(a, b)
    s = re.sub('[\u200b\u200c\u200d\u2060\ufeff\u00ad]', '', s)      # zero-width marks and soft hyphens that some sites put inside words
    return re.sub(r'\s+', ' ', s).lower()


def squash(s):
    return re.sub(r'[\s"\']+', '', norm(s))


def page(sid):
    if sid in _cache: return _cache[sid]
    d = P / sid; t = ''
    if d.is_dir():
        for n in ('text.txt', 'text.article.txt', 'transcription.txt'):
            if (d / n).exists(): t += ' ' + (d / n).read_text(encoding='utf-8', errors='replace')
        for b in d.glob('body*'):
            ext = b.suffix.lower(); web = ext in ('.html', '.htm', '.json', '.txt')
            if ext in ('.pdf', '.bin') and b.stat().st_size < 12_000_000:      # a web page the fetch tool stored under a document's name
                with b.open('rb') as f: head = f.read(4096)
                web = not head.startswith(b'%PDF') and bool(re.search(rb'(?i)<(!doctype|html|head|body)\b', head))
            if web and b.stat().st_size < 12_000_000:
                raw = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', b.read_text(encoding='utf-8', errors='replace'))
                t += ' ' + html.unescape(re.sub(r'(?s)<[^>]+>', ' ', raw))
    _cache[sid] = squash(t)
    return _cache[sid]


def has(quote, sid):
    q = squash(quote)
    return len(q) >= 6 and q in page(sid)


def url_of(sid):
    try: u = json.loads((P / sid / 'meta.json').read_text()).get('url')
    except Exception: return None
    if not u or not str(u).startswith('http'): return None
    tail = re.sub(r'^https?://[^/]+', '', u)
    if sid.startswith('man-') and (len(tail) < 40 and not re.search(r'\.(htm|html|pdf)$', tail) and not re.search(r'-[0-9a-f]{6,}$|\d{5,}$', tail)):
        return None                                    # a hand-saved PDF prints its address cut short
    return u
