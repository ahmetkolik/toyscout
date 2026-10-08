#!/usr/bin/env python3
"""Per-route static HTML for crawlers: /product/<cat>/<idx>, /shop/<cat>, the shell pages
(/blog, /contact, /privacy, /terms, /disclosure) and /404.html.

Copies index.html and swaps title/description/canonical/og/robots tags, replaces the home
page's JSON-LD @graph with Organization + WebSite + the page's own entity (+ BreadcrumbList),
and puts a readable summary in <noscript>. The SPA still boots and re-renders as before
(Vercel serves a real file before applying rewrites; unknown /product and /shop paths 404).
Product pages are `noindex,follow` unless whitelisted (products/seo_index.py).
Re-run after ANY change to js/data.js or index.html (then stamp_data_version.py).
Output: product/, shop/, blog/, contact/, privacy/, terms/, disclosure/, 404.html
(generated; safe to delete and regenerate).
"""
import html, json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from split_data import has_price  # CLAUDE.md kurali: fiyat iceren ilan maddeleri sayfaya gitmez
import seo_index

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = seo_index.BASE
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
D = seo_index.load_data()
CAT = {m.group(1): m.group(2) for m in re.finditer(r'\["([a-z-]+)","([^"]+)","[^"]*"\]', src.split('var CATS')[1].split('];')[0])}
# Kategori SEO metni index.html'deki tek satirlik CAT_SEO JSON'undan okunur (tek kaynak).
SEO = json.loads(src.split('var CAT_SEO = ', 1)[1].split(';\n', 1)[0])
E = html.escape

LD_RE = re.compile(r'(<script type="application/ld\+json" id="ts-ldjson">)(.*?)(</script>)', re.S)
HOME_LD = json.loads(LD_RE.search(src).group(2))
# Only the site-wide nodes travel to sub-pages; the home graph's ItemList/Blog/Products don't.
SITE_NODES = [n for n in HOME_LD['@graph'] if n.get('@type') in ('Organization', 'WebSite')]
BLOG_NODE = next((n for n in HOME_LD['@graph'] if n.get('@type') == 'Blog'), None)

ROBOTS_IDX = 'index, follow, max-image-preview:large'
ROBOTS_NOIDX = 'noindex, follow'
SHELL_DIRS = ('blog', 'contact', 'privacy', 'terms', 'disclosure')

# Shell routes (titles/descriptions mirror updateSeo() in index.html).
SHELL = {
    'blog': ("The ToyScout Radar Blog — Amazon Toy Trends | ToyScout",
             "Weekly reads on Amazon's toy charts: Prime Day deals, STEM kits, outdoor picks and what's trending for every age group.",
             'The ToyScout Radar Blog'),
    'contact': ("Contact ToyScout",
                "Questions, feedback or partnership ideas? Get in touch with the ToyScout team.",
                'Contact ToyScout'),
    'privacy': ("Privacy Policy | ToyScout", "How ToyScout handles cookies, analytics and affiliate-link data.", 'Privacy Policy'),
    'terms': ("Terms of Use | ToyScout", "The terms that govern your use of ToyScout.", 'Terms of Use'),
    'disclosure': ("Affiliate Disclosure | ToyScout",
                   "ToyScout is an Amazon Associate — here's exactly how we earn and how it affects our picks.",
                   'Affiliate Disclosure'),
}


def absu(path):
    """Absolute site URL for a stored asset path ('assets/x.jpg' or '/assets/x.jpg')."""
    return BASE + '/' + (path or '').lstrip('/')


def cut(t, n):
    t = t or ''
    return t[:max(20, t.rfind(' ', 0, n))] + '…' if len(t) > n else t


def ldname(n):
    n = (n or '').strip()
    if len(n) <= 150:
        return n
    c = n[:150]
    sp = c.rfind(' ')
    return re.sub(r'[\s,;:\-–—(]+$', '', c[:sp] if sp > 80 else c)


def fmt(n):
    try:
        return f'{int(float(n or 0)):,}'
    except (TypeError, ValueError):
        return str(n)


def crumbs(*items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name, "item": BASE + path} for i, (name, path) in enumerate(items)]}


def ldjson(nodes, tag_id):
    body = json.dumps({"@context": "https://schema.org", "@graph": nodes}, ensure_ascii=False).replace('</', '<\\/')
    return f'<script type="application/ld+json" id="{tag_id}">{body}</script>'


def page(title, desc, path, body, ld_nodes, img=None, robots=ROBOTS_IDX):
    """path=None -> no canonical/og:url (404 page)."""
    s = src
    s = re.sub(r'<title>.*?</title>', lambda m: f'<title>{E(title)}</title>', s, count=1, flags=re.S)
    s = re.sub(r'(<meta name="description" content=")[^"]*"', lambda m: m.group(1) + E(desc, True) + '"', s, count=1)
    s, k = re.subn(r'<meta name="robots" content="[^"]*">', f'<meta name="robots" content="{robots}">', s, count=1)
    assert k == 1, 'robots meta not found in index.html'
    url = BASE + path if path else None
    s, k = re.subn(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">' if url else '', s, count=1)
    assert k == 1, 'static canonical not found in index.html'
    for prop, val in (('og:title', title), ('og:description', desc), ('og:url', url)):
        if val:
            s = re.sub(rf'(<meta property="{prop}" content=")[^"]*"', lambda m: m.group(1) + E(val, True) + '"', s, count=1)
    for nm, val in (('twitter:title', title), ('twitter:description', desc)):
        s = re.sub(rf'(<meta name="{nm}" content=")[^"]*"', lambda m: m.group(1) + E(val, True) + '"', s, count=1)
    if img:
        s = re.sub(r'(<meta (?:property="og:image"|name="twitter:image") content=")[^"]*"', lambda m: m.group(1) + E(img, True) + '"', s)
    # Home graph (Org, WebSite, ItemList, Blog, 5 Products) -> Org + WebSite only;
    # the page's own entity goes in ts-ldjson-dynamic, which the SPA replaces on navigation.
    s = LD_RE.sub(lambda m: ldjson(SITE_NODES, 'ts-ldjson'), s, count=1)
    if ld_nodes:
        s = s.replace('</head>', ldjson(ld_nodes, 'ts-ldjson-dynamic') + '\n</head>', 1)
    s = re.sub(r'<noscript>.*?</noscript>', lambda m: '<noscript>' + body + '</noscript>', s, count=1, flags=re.S)
    # Sub-pages: the home hero headline must not be a second <h1> (the page's own title is the H1).
    s = re.sub(r'<h1>(<span class="split" data-split>Toys worth</span>.*?)</h1>',
               lambda m: '<div class="hero-h" role="presentation">' + m.group(1) + '</div>', s, count=1, flags=re.S)
    return s


def write(path, content):
    out = os.path.join(ROOT, path.strip('/'), 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(content)


def wrap(inner):
    return f'<div style="font-family:sans-serif;padding:24px;max-width:900px;margin:auto">{inner}</div>'


def shell_pages():
    posts = (BLOG_NODE or {}).get('blogPost', [])
    for key, (title, desc, h1) in SHELL.items():
        path = '/' + key
        if key == 'blog':
            lis = ''.join(f'<li><a href="/{E(bp["url"].rsplit("/", 1)[-1])}">{E(bp["headline"])}</a></li>' for bp in posts)
            inner = f'<h1>{E(h1)}</h1><p>{E(desc)}</p><ul>{lis}</ul>'
            ld = [{"@type": "Blog", "name": "The ToyScout Radar Blog", "url": BASE + path,
                   "publisher": {"@id": BASE + "/#org"},
                   "blogPost": [{"@type": "BlogPosting", "headline": bp.get("headline"), "url": bp.get("url"),
                                 "datePublished": bp.get("datePublished")} for bp in posts]},
                  crumbs(('Home', '/'), ('Blog', path))]
        else:
            inner = f'<h1>{E(h1)}</h1><p>{E(desc)}</p>'
            ld = [{"@type": "ContactPage" if key == 'contact' else "WebPage", "name": title, "url": BASE + path},
                  crumbs(('Home', '/'), (h1, path))]
        inner += '<p><a href="/">ToyScout home</a> · <a href="/blog">Blog</a> · <a href="/contact">Contact</a> · <a href="/disclosure">Affiliate Disclosure</a></p>'
        write(path, page(title, desc, path, wrap(inner), ld))
    # 404.html: Vercel serves it for any unmatched path; the SPA then shows its not-found view.
    nf = page('Page not found | ToyScout', "This page doesn't exist. Browse today's Amazon best-selling toys on ToyScout instead.",
              None, wrap('<h1>Page not found</h1><p><a href="/">Browse today\'s best-selling toys</a> · <a href="/blog">Blog</a></p>'),
              None, robots=ROBOTS_NOIDX)
    open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(nf)
    return len(SHELL)


def main():
    for d in ('product', 'shop') + SHELL_DIRS:
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    indexable = set(seo_index.indexable_products(D))
    np = nc = nidx = 0
    for cat, items in D.items():
        if not items or cat not in CAT:
            continue
        cname = CAT[cat]
        # shop page
        lis = ''.join(f'<li><a href="/product/{cat}/{i}">{E(p["name"])}</a> — {(p.get("rating") or 0)}★ ({fmt((p.get("rc") or 0))} ratings)</li>'
                      for i, p in enumerate(items))
        cs = SEO.get(cat)
        desc = cs['d'] if cs else f"Today's best-selling {cname.lower()} on Amazon with star ratings, review counts and age filters — updated from the official best-seller chart."
        h1 = cs['h'] if cs else f"{cname} — Today's Amazon Best Sellers"
        intro = cs['i'] if cs else desc
        title = cs['t'] + ' | ToyScout' if cs else f"{cname} — Today's Amazon Best Sellers | ToyScout"
        ld = [{"@type": "ItemList", "name": f"{cname} — Amazon Best Sellers on ToyScout",
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": ldname(p['name']), "url": f"{BASE}/product/{cat}/{i}"} for i, p in enumerate(items)]},
              crumbs(('Home', '/'), (cname, f'/shop/{cat}'))]
        body = wrap(f'<h1>{E(h1)}</h1><p>{E(intro)}</p><ol>{lis}</ol><p><a href="/">ToyScout home</a></p>')
        write(f'/shop/{cat}', page(title, desc, f'/shop/{cat}', body, ld))
        nc += 1
        for i, p in enumerate(items):
            name = p['name']
            path = f'/product/{cat}/{i}'
            bsr = p.get('bsr') or []
            rating, rc = p.get('rating') or 0, p.get('rc') or 0
            rank = f"Amazon Toys & Games rank #{bsr[0]['rank']}. " if bsr else ''
            title = cut(name, 58) + ' — Reviews & Amazon Rank | ToyScout'
            desc = cut(f'{rank}{name} — rated {rating} out of 5 by {fmt(rc)} Amazon customers.', 158)
            gal = p.get('gallery') or [p['img']]
            bullets = [x for x in (p.get('bullets') or []) if not has_price(x)]
            # Fiyat/Offer yok (CLAUDE.md kurali: sitede hicbir yerde fiyat gosterilmez).
            # aggregateRating yok: Amazon puanlari ucuncu taraf toplu puan; Google yasakliyor.
            ld = [{"@type": "Product", "name": ldname(name), "image": [absu(g) for g in gal],
                   "description": (bullets or [name])[0], "url": BASE + path},
                  crumbs(('Home', '/'), (cname, f'/shop/{cat}'), (ldname(name), path))]
            bl = ''.join(f'<li>{E(b)}</li>' for b in bullets[:6])
            rk = ''.join(f'<li>#{b["rank"]} in {E(b["cat"])}</li>' for b in bsr[:3])
            body = wrap(f'<h1>{E(name)}</h1>'
                        f'<img src="{E("/" + gal[0].lstrip("/"))}" alt="{E(cut(name, 100))}" width="300">'
                        f'<p>Rated {rating} out of 5 by {fmt(rc)} Amazon customers. <a href="{E(p.get("url") or "")}" rel="nofollow sponsored">See today\'s price on Amazon</a>.</p>'
                        f'{"<ul>" + rk + "</ul>" if rk else ""}{"<h2>Key features (from the Amazon listing)</h2><ul>" + bl + "</ul>" if bl else ""}'
                        f'<p><a href="/shop/{cat}">More {E(cname)}</a> · <a href="/">ToyScout home</a></p>')
            ok = path in indexable
            nidx += ok
            write(path, page(title, desc, path, body, ld, absu(gal[0]), ROBOTS_IDX if ok else ROBOTS_NOIDX))
            np += 1
    ns = shell_pages()
    print(f'{np} product pages ({nidx} indexable, {np - nidx} noindex), {nc} category pages, {ns} shell pages + 404.html')


if __name__ == '__main__':
    sys.exit(main())
