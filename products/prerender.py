#!/usr/bin/env python3
"""Per-route static HTML for crawlers: /product/<cat>/<idx> and /shop/<cat>.

Copies index.html and swaps title/description/canonical/og tags, adds Product/ItemList
JSON-LD and a readable summary in <noscript>. The SPA still boots and re-renders as before
(Vercel serves a real file before applying the /index.html rewrites).
Re-run after ANY change to js/data.js or index.html head (then stamp_data_version.py).
Output: product/, shop/ (generated; safe to delete and regenerate).
"""
import html, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://www.toyscout.net'
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
raw = open(os.path.join(ROOT, 'js', 'data.js'), encoding='utf-8').read()
D = json.loads(raw[raw.index('{'):raw.rindex('}') + 1])
CAT = {m.group(1): m.group(2) for m in re.finditer(r'\["([a-z-]+)","([^"]+)","[^"]*"\]', src.split('var CATS')[1].split('];')[0])}
E = html.escape


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
    return f'{n or 0:,}'


def page(title, desc, path, body, ld, img=None):
    s = src
    s = re.sub(r'<title>.*?</title>', lambda m: f'<title>{E(title)}</title>', s, count=1, flags=re.S)
    s = re.sub(r'(<meta name="description" content=")[^"]*"', lambda m: m.group(1) + E(desc, True) + '"', s, count=1)
    url = BASE + path
    s = s.replace('<!-- canonical is injected per-route by updateSeo(); a static tag here would declare every route a duplicate of "/" -->',
                  f'<link rel="canonical" href="{url}">')
    for prop, val in (('og:title', title), ('og:description', desc), ('og:url', url)):
        s = re.sub(rf'(<meta property="{prop}" content=")[^"]*"', lambda m: m.group(1) + E(val, True) + '"', s, count=1)
    for nm, val in (('twitter:title', title), ('twitter:description', desc)):
        s = re.sub(rf'(<meta name="{nm}" content=")[^"]*"', lambda m: m.group(1) + E(val, True) + '"', s, count=1)
    if img:
        s = re.sub(r'(<meta (?:property="og:image"|name="twitter:image") content=")[^"]*"', lambda m: m.group(1) + img + '"', s)
    ldtag = '<script type="application/ld+json" id="ts-ldjson-dynamic">' + json.dumps(ld, ensure_ascii=False).replace('</', '<\\/') + '</script>\n'
    s = s.replace('</head>', ldtag + '</head>', 1)
    s = re.sub(r'<noscript>.*?</noscript>', lambda m: '<noscript>' + body + '</noscript>', s, count=1, flags=re.S)
    return s


def write(path, content):
    out = os.path.join(ROOT, path.strip('/'), 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(content)


def main():
    for d in ('product', 'shop'):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    np = nc = 0
    for cat, items in D.items():
        if not items or cat not in CAT:
            continue
        cname = CAT[cat]
        # shop page
        lis = ''.join(f'<li><a href="/product/{cat}/{i}">{E(p["name"])}</a> — {E(p.get("price") or "")} · {(p.get("rating") or 0)}★ ({fmt((p.get("rc") or 0))} ratings)</li>'
                      for i, p in enumerate(items))
        desc = f"Today's best-selling {cname.lower()} on Amazon with live prices, star ratings, review counts and age filters — updated from the official best-seller chart."
        ld = {"@context": "https://schema.org", "@type": "ItemList", "name": f"{cname} — Amazon Best Sellers on ToyScout",
              "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": ldname(p['name']), "url": f"{BASE}/product/{cat}/{i}"} for i, p in enumerate(items)]}
        body = f'<div style="font-family:sans-serif;padding:24px;max-width:900px;margin:auto"><h1>{E(cname)} — Today\'s Amazon Best Sellers</h1><p>{E(desc)}</p><ol>{lis}</ol><p><a href="/">ToyScout home</a></p></div>'
        write(f'/shop/{cat}', page(f"{cname} — Today's Amazon Best Sellers | ToyScout", desc, f'/shop/{cat}', body, ld))
        nc += 1
        for i, p in enumerate(items):
            name = p['name']
            bsr = p.get('bsr') or []
            price = p.get('price') or 'See price on Amazon'
            rating, rc = p.get('rating') or 0, p.get('rc') or 0
            rank = f"Amazon Toys & Games rank #{bsr[0]['rank']}. " if bsr else ''
            title = cut(name, 58) + ' — Review, Price & Rank | ToyScout'
            desc = cut(f'{rank}{name} — {price}, rated {rating} out of 5 by {fmt(rc)} Amazon customers.', 158)
            gal = p.get('gallery') or [p['img']]
            pn = None
            m = re.sub(r'[^0-9.]', '', str(price))
            try:
                pn = float(m) if m else None
            except ValueError:
                pn = None
            pn = pn or p.get('lo') or None
            ld = {"@context": "https://schema.org", "@type": "Product", "name": ldname(name),
                  "image": [BASE + g for g in gal], "description": (p.get('bullets') or [name])[0],
                  "url": f"{BASE}/product/{cat}/{i}"}
            if pn:
                ld["offers"] = {"@type": "Offer", "price": pn, "priceCurrency": "USD",
                                "availability": "https://schema.org/InStock", "url": p.get('url')}
            if rc > 0:
                ld["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": rating, "reviewCount": rc, "bestRating": 5}
            bl = ''.join(f'<li>{E(b)}</li>' for b in (p.get('bullets') or [])[:6])
            rk = ''.join(f'<li>#{b["rank"]} in {E(b["cat"])}</li>' for b in bsr[:3])
            body = (f'<div style="font-family:sans-serif;padding:24px;max-width:900px;margin:auto"><h1>{E(name)}</h1>'
                    f'<img src="{E(gal[0])}" alt="{E(cut(name, 100))}" width="300">'
                    f'<p>{E(price)} · rated {rating} out of 5 by {fmt(rc)} Amazon customers.</p>'
                    f'{"<ul>" + rk + "</ul>" if rk else ""}{"<h2>Key features (from the Amazon listing)</h2><ul>" + bl + "</ul>" if bl else ""}'
                    f'<p><a href="/shop/{cat}">More {E(cname)}</a> · <a href="/">ToyScout home</a></p></div>')
            write(f'/product/{cat}/{i}', page(title, desc, f'/product/{cat}/{i}', body, ld, BASE + gal[0]))
            np += 1
    print(f'{np} product pages, {nc} category pages')


if __name__ == '__main__':
    sys.exit(main())
