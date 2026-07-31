#!/usr/bin/env python3
"""
browse.html uretici — SPA'nin taranabilirlik sorununu cozer.

NEDEN VAR (29 Tem 2026 tespiti):
  index.html'den sunulan ham HTML'de urun sayfalarina giden `<a href>` sayisi SIFIR.
  Tum gezinme JS ile istemcide uretiliyor, `#view` bos geliyor. Bu yuzden GSC her
  urun sayfasi icin "URL is unknown to Google" + "Referring page: None detected"
  diyordu — Google'in iki kesif yolundan biri (ic link) tamamen kapaliydi.

NE YAPAR:
  js/data.js'i okur, TUM urunlere ve kategorilere GERCEK `<a href>` iceren, JS
  gerektirmeyen statik bir browse.html uretir. index.html'in footer'indan buraya
  gercek bir link var; boylece Google icin taranabilir bir zincir olusuyor:
      / -> /browse.html -> /product/<kategori>/<idx>  (115 urun)

  Sayfa gercek ziyaretciye de faydali olacak sekilde tasarlandi (kategoriye gore
  gruplu, fiyat/puan bilgili tam katalog). Gizli link listesi DEGIL — gizli link
  spam sinyalidir ve isi daha kotu yapar.

Calistirma: python3 products/build_browse_page.py
bestseller_sync.py her turda bunu otomatik cagirir.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(SITE, 'js', 'data.js')
OUT = os.path.join(SITE, 'browse.html')

# index.html'deki CATS ile ayni id -> ad/emoji eslesmesi
CATS = [
    ('action-figures', 'Action Figures & Statues', '🦸'),
    ('arts-crafts', 'Arts & Crafts', '🎨'),
    ('baby-toddler', 'Baby & Toddler Toys', '🧸'),
    ('building-toys', 'Building Toys', '🧱'),
    ('dolls', 'Dolls & Accessories', '🎀'),
    ('dress-up', 'Dress Up & Pretend Play', '🎭'),
    ('games', 'Games', '🎲'),
    ('hobbies', 'Hobbies', '🛠️'),
    ('kids-electronics', "Kids' Electronics", '🤖'),
    ('learning-education', 'Learning & Education', '📚'),
    ('novelty', 'Novelty & Gag Toys', '🪄'),
    ('party', 'Party Supplies', '🎉'),
    ('puppets', 'Puppets', '🧦'),
    ('puzzles', 'Puzzles', '🧩'),
    ('sports-outdoor', 'Sports & Outdoor Play', '⚽'),
    ('plush', 'Stuffed Animals & Plush Toys', '🐻'),
    ('rc-vehicles', 'RC & Play Vehicles', '🏎️'),
    ('ride-ons', 'Tricycles, Scooters & Wagons', '🛴'),
    ('video-games', 'Video Games', '🕹️'),
]

CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{--cream:#FAF3E7;--ink:#14225A;--blue:#1D3FC4;--red:#E8442E;--gold:#F5B301;
--ink-08:rgba(20,34,90,.08);--ink-55:rgba(20,34,90,.55)}
body{margin:0;background:var(--cream);color:var(--ink);
font-family:Nunito,system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.6}
.wrap{max-width:1100px;margin:0 auto;padding:32px 20px 64px}
header{border-bottom:2px solid var(--ink-08);padding-bottom:22px;margin-bottom:30px}
.brand{font-family:Fraunces,Georgia,serif;font-weight:800;font-size:1.55rem;
text-decoration:none;color:var(--ink);display:inline-block}
.brand .dot{color:var(--red)}
h1{font-family:Fraunces,Georgia,serif;font-size:clamp(1.7rem,4vw,2.5rem);
margin:.5em 0 .25em;line-height:1.15}
.lede{color:var(--ink-55);max-width:62ch;margin:0 0 .4em}
nav.toc{display:flex;flex-wrap:wrap;gap:8px;margin:26px 0 8px}
nav.toc a{background:#fff;border:1px solid var(--ink-08);border-radius:999px;
padding:6px 14px;font-size:.9rem;font-weight:700;text-decoration:none;color:var(--ink)}
nav.toc a:hover{border-color:var(--blue);color:var(--blue)}
section{margin:44px 0 0}
h2{font-family:Fraunces,Georgia,serif;font-size:1.4rem;margin:0 0 4px;
padding-bottom:8px;border-bottom:2px solid var(--ink-08)}
h2 a{color:var(--ink);text-decoration:none}
h2 a:hover{color:var(--blue)}
.count{font-size:.85rem;font-weight:600;color:var(--ink-55);margin:0 0 14px}
ul{list-style:none;margin:0;padding:0;display:grid;gap:10px;
grid-template-columns:repeat(auto-fill,minmax(320px,1fr))}
li{background:#fff;border:1px solid var(--ink-08);border-radius:12px;padding:12px 14px}
li a{color:var(--blue);text-decoration:none;font-weight:700;display:block;
margin-bottom:3px}
li a:hover{text-decoration:underline}
.meta{font-size:.85rem;color:var(--ink-55)}
.meta .price{color:var(--ink);font-weight:800}
.star{color:var(--gold)}
footer{margin-top:56px;padding-top:22px;border-top:2px solid var(--ink-08);
font-size:.88rem;color:var(--ink-55)}
footer a{color:var(--blue)}
@media (prefers-color-scheme:dark){
:root{--cream:#12162a;--ink:#e8ecff;--ink-08:rgba(232,236,255,.12);
--ink-55:rgba(232,236,255,.6);--blue:#8fa8ff}
li,nav.toc a{background:rgba(255,255,255,.04)}}
"""


def esc(s):
    return html.escape(str(s), quote=True)


def main():
    src = open(DATA, encoding='utf-8').read()
    d = json.loads(re.search(r'window\.TS_DATA\s*=\s*(\{.*\})\s*;?\s*$', src, re.S).group(1))

    names = {c: (n, e) for c, n, e in CATS}
    order = [c for c, _, _ in CATS if c in d and d[c]]
    order += [c for c in d if c not in names and d[c]]
    total = sum(len(d[c]) for c in order)
    today = dt.date.today().isoformat()

    toc = '\n'.join(
        f'    <a href="#{esc(c)}">{names.get(c, (c, ""))[1]} {esc(names.get(c, (c, ""))[0])}</a>'
        for c in order)

    body = []
    for c in order:
        nm, em = names.get(c, (c.replace('-', ' ').title(), '🧸'))
        items = []
        for i, p in enumerate(d[c]):
            bits = []
            if p.get('price'):
                bits.append(f'<span class="price">{esc(p["price"])}</span>')
            if p.get('rating'):
                rc = f' · {p["rc"]:,} reviews' if p.get('rc') else ''
                bits.append(f'<span class="star">★</span> {esc(p["rating"])}{rc}')
            items.append(
                f'      <li><a href="/product/{esc(c)}/{i}">{esc(p["name"])}</a>'
                f'<div class="meta">{" · ".join(bits)}</div></li>')
        body.append(
            f'  <section id="{esc(c)}">\n'
            f'    <h2><a href="/shop/{esc(c)}">{em} {esc(nm)}</a></h2>\n'
            f'    <p class="count">{len(d[c])} toys · '
            f'<a href="/shop/{esc(c)}">browse this category</a></p>\n'
            f'    <ul>\n' + '\n'.join(items) + '\n    </ul>\n  </section>')

    # Kept under ~155 chars so Google doesn't truncate it in the SERP.
    DESC = esc(f"The complete ToyScout catalog: {total} of Amazon's best-selling, "
               f"top-rated toys across {len(order)} categories, with current prices and ratings.")

    # CollectionPage + ItemList (one entry per category section) + breadcrumb.
    # Gives the crawler a machine-readable map of what this page links to.
    LD = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "@id": "https://www.toyscout.net/browse.html",
                "url": "https://www.toyscout.net/browse.html",
                "name": f"All Toys — Browse the Full ToyScout Catalog ({total} Toys)",
                "description": (f"The complete ToyScout catalog: {total} of Amazon's "
                                f"best-selling, top-rated toys across {len(order)} categories, "
                                f"with current prices and ratings."),
                "isPartOf": {"@type": "WebSite", "name": "ToyScout",
                             "url": "https://www.toyscout.net/"},
                "dateModified": today,
                "mainEntity": {
                    "@type": "ItemList",
                    "numberOfItems": len(order),
                    "itemListElement": [
                        {"@type": "ListItem", "position": i + 1,
                         "name": names.get(c, (c, ""))[0],
                         "url": f"https://www.toyscout.net/shop/{c}"}
                        for i, c in enumerate(order)
                    ],
                },
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home",
                     "item": "https://www.toyscout.net/"},
                    {"@type": "ListItem", "position": 2, "name": "All Toys",
                     "item": "https://www.toyscout.net/browse.html"},
                ],
            },
        ],
    }, ensure_ascii=False, separators=(',', ':'))

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>All Toys — Browse the Full ToyScout Catalog ({total} Toys)</title>
<meta name="description" content="{DESC}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="https://www.toyscout.net/browse.html">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ToyScout">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="All Toys — Browse the Full ToyScout Catalog ({total} Toys)">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="https://www.toyscout.net/browse.html">
<meta property="og:image" content="https://www.toyscout.net/assets/hero-flying-blue.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="All Toys — Browse the Full ToyScout Catalog ({total} Toys)">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="https://www.toyscout.net/assets/hero-flying-blue.png">
<script type="application/ld+json">{LD}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700..900&family=Nunito:wght@400;700;800&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header>
  <a class="brand" href="/">Toy<span class="dot">·</span>Scout</a>
</header>

  <h1>Browse every toy on ToyScout</h1>
  <p class="lede">The complete catalog — {total} toys across {len(order)} categories,
  every one of them an Amazon best seller or top-rated pick. Prices and ratings are
  refreshed automatically every few days.</p>
  <p class="lede"><small>Last updated {today}</small></p>

  <nav class="toc" aria-label="Categories">
{toc}
  </nav>

{chr(10).join(body)}

<footer>
  <p><a href="/">← Back to ToyScout home</a> · <a href="/blog">Blog</a> ·
  <a href="/contact">Contact</a> · <a href="/disclosure">Affiliate Disclosure</a></p>
  <p>As an Amazon Associate, ToyScout earns from qualifying purchases.
  © 2026 ToyScout</p>
</footer>
</div>
<!-- Vercel Web Analytics — panelde kapaliysa 404 doner ve sessizce yok sayilir. -->
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""
    open(OUT, 'w', encoding='utf-8').write(page)
    links = page.count('href="/product/')
    print(f'browse.html yazildi — {total} urun, {len(order)} kategori, '
          f'{links} gercek urun linki ({len(page):,} bayt)')
    return links


if __name__ == '__main__':
    main()
