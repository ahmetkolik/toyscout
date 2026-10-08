#!/usr/bin/env python3
"""Which product pages may be indexed by Google, plus sitemap dates — one source for
prerender.py, build_sitemap.py, split_data.py (TS_INDEXABLE in js/catalog.js) and
bestseller_sync.write_sitemap.

Why (2026-10-08 audit): ~1,000 product pages carry only Amazon-copied text, and GSC shows
1,021 URLs "Discovered – currently not indexed". Thin pages dilute the site, so product
pages are `noindex,follow` and left out of sitemap.xml UNLESS they are whitelisted:
  (a) every product a blog post links to (a /product/<cat>/<idx> link, or an Amazon
      dp/<ASIN> link mapped back to its catalog position) — recomputed on every run, so a
      new post whitelists its products automatically; and
  (b) IMPRESSION_WHITELIST below: URLs that already get Google impressions.
Category, blog and home pages are always indexable.

Run directly to print the list: python3 products/seo_index.py
"""
import glob, json, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://www.toyscout.net'

# Product URLs that already earn Google impressions (GSC, 2026-10-08). Keep them indexable.
# Note: product URLs are position-based (/product/<cat>/<idx>), so a catalog reshuffle can
# point an entry at a different product — re-check against GSC after big imports.
IMPRESSION_WHITELIST = [
    '/product/arts-crafts/1', '/product/games/11', '/product/games/10',
    '/product/baby-toddler/9', '/product/baby-toddler/11', '/product/arts-crafts/23',
    '/product/arts-crafts/24', '/product/arts-crafts/25', '/product/arts-crafts/8',
    '/product/ride-ons/4', '/product/sports-outdoor/16', '/product/learning-education/0',
    '/product/plush/0',
    # Rattlebacks added 2026-10-08 for the GSC query "rattleback amazon" (31 impressions).
    '/product/learning-education/39', '/product/learning-education/40',
]

PROD_RE = re.compile(r'/product/([a-z-]+)/(\d+)')
ASIN_RE = re.compile(r'amazon\.com/(?:[^"\'\s]*/)?dp/([A-Z0-9]{10})')


def load_data():
    raw = open(os.path.join(ROOT, 'js', 'data.js'), encoding='utf-8').read()
    return json.loads(raw[raw.index('{'):raw.rindex('}') + 1])


def _index_html():
    return open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()


def posts_source(src=None):
    """Raw text of the `var POSTS={...}` block in index.html (brace-matched)."""
    src = src or _index_html()
    start = src.find('var POSTS={')
    if start < 0:
        return ''
    i = src.index('{', start)
    depth = 0
    for j in range(i, len(src)):
        if src[j] == '{':
            depth += 1
        elif src[j] == '}':
            depth -= 1
            if depth == 0:
                return src[i:j + 1]
    return src[i:]


def blog_texts():
    """Blog post content: the POSTS data in index.html plus generated post*.html pages."""
    out = [posts_source()]
    for f in sorted(glob.glob(os.path.join(ROOT, 'post*.html'))):
        out.append(open(f, encoding='utf-8').read())
    return out


def indexable_products(D=None):
    """Sorted list of '/product/<cat>/<idx>' paths that may be indexed."""
    D = D if D is not None else load_data()
    by_asin = {}
    for cat, items in D.items():
        for i, p in enumerate(items or []):
            if p.get('asin'):
                by_asin.setdefault(p['asin'], []).append(f'/product/{cat}/{i}')
    keep = set()
    for text in blog_texts():
        for cat, idx in PROD_RE.findall(text):
            keep.add(f'/product/{cat}/{int(idx)}')
        for asin in ASIN_RE.findall(text):
            keep.update(by_asin.get(asin, []))
    keep.update(IMPRESSION_WHITELIST)

    def valid(path):
        _, _, cat, idx = path.split('/')
        return cat in D and int(idx) < len(D[cat] or [])
    return sorted((p for p in keep if valid(p)), key=lambda p: (p.split('/')[2], int(p.split('/')[3])))


def blog_post_dates(src=None):
    """{'post18': 'YYYY-MM-DD', ...} from the Blog JSON-LD in index.html (dateModified, else datePublished)."""
    src = src or _index_html()
    m = re.search(r'<script type="application/ld\+json" id="ts-ldjson">(.*?)</script>', src, re.S)
    out = {}
    if not m:
        return out
    for node in json.loads(m.group(1)).get('@graph', []):
        if node.get('@type') == 'Blog':
            for bp in node.get('blogPost', []):
                key = bp.get('url', '').rstrip('/').rsplit('/', 1)[-1]
                d = bp.get('dateModified') or bp.get('datePublished')
                if key and d:
                    out[key] = d[:10]
    return out


def git_date(path):
    """Last commit date (YYYY-MM-DD) of a repo file, or '' outside git."""
    try:
        r = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', path],
                           cwd=ROOT, capture_output=True, text=True, timeout=20)
        return r.stdout.strip()
    except Exception:
        return ''


def data_date():
    """Date js/data.js last changed: git date, or the file mtime when it has uncommitted edits."""
    import datetime as dt
    g = git_date('js/data.js')
    try:
        dirty = subprocess.run(['git', 'status', '--porcelain', '--', 'js/data.js'], cwd=ROOT,
                               capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        dirty = 'x'
    if g and not dirty:
        return g
    return dt.date.fromtimestamp(os.path.getmtime(os.path.join(ROOT, 'js', 'data.js'))).isoformat()


if __name__ == '__main__':
    L = indexable_products()
    print('\n'.join(L))
    print(f'{len(L)} indexable product pages; data.js date {data_date()}')
