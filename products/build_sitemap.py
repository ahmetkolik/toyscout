#!/usr/bin/env python3
"""
sitemap.xml uretici — TEK sitemap (Google'in okudugu dosya).

NEDEN VAR (30 Tem 2026 tespiti):
  Iki ayri sitemap vardi ve bolunme zarar veriyordu:
    - sitemap.xml         -> Google OKUYOR (Last read 30 Tem, Success, 124 sayfa)
                             ama yalnizca ESKI 97 urunu iceriyordu
    - sitemap-products.xml -> 115 urunun tamami vardi ama Google CEKEMIYOR
                             ("Couldn't fetch", 0 kesif, gunlerdir duzelmiyor)
  Cozum: her seyi Google'in kanitlanmis sekilde okudugu sitemap.xml'e koy.

8 Eki 2026 SEO duzeltmesi (1,021 URL "Discovered – currently not indexed"):
  - Urun sayfalari: SADECE seo_index.indexable_products() (blog yazilarinin linkledigi urunler +
    IMPRESSION_WHITELIST). Digerleri noindex,follow (prerender.py) ve sitemap'te YOK.
  - /contact, /privacy, /terms, /disclosure sitemap'te yok: indekslenebilir kalirlar (her sayfanin
    footer'inda linkli, kendi canonical'lari var) ama arama hedefi degiller.
  - lastmod anlamli: yazi -> Blog JSON-LD dateModified/datePublished; kategori/urun/browse ->
    js/data.js'in son git tarihi; /blog -> en yeni yazi; / -> hepsinin en yenisi.
  - Yazi listesi index.html'deki Blog JSON-LD'sinden okunur (elle yazilan eski STATIC listesinde
    post16-18 eksikti).

NE URETIR:
  / + /browse.html + /blog + /postN + /shop/<kategori> + indekslenebilir /product/<kategori>/<idx>

Calistirma: python3 products/build_sitemap.py
bestseller_sync.py / subcat_sync.py / new_releases_sync.py her turda otomatik cagirir.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import seo_index  # noqa: E402

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, 'sitemap.xml')

CAT_ORDER = ['action-figures', 'arts-crafts', 'baby-toddler', 'building-toys', 'dolls',
             'games', 'learning-education', 'novelty', 'party', 'sports-outdoor',
             'plush', 'ride-ons']


def main():
    d = seo_index.load_data()
    cats = [c for c in CAT_ORDER if c in d and d[c]] + \
           [c for c in d if c not in CAT_ORDER and d[c]]
    data_day = seo_index.data_date()
    posts = seo_index.blog_post_dates()
    keys = sorted(posts, key=lambda k: int(k.replace('post', '')))
    blog_day = max(posts.values()) if posts else data_day
    home_day = max(data_day, blog_day)
    prods = seo_index.indexable_products(d)

    rows = []

    def add(path, day, prio, freq):
        rows.append(
            f'  <url>\n'
            f'    <loc>https://www.toyscout.net{path}</loc>\n'
            f'    <lastmod>{day}</lastmod>\n'
            f'    <changefreq>{freq}</changefreq>\n'
            f'    <priority>{prio}</priority>\n'
            f'  </url>')

    add('/', home_day, '1.0', 'daily')
    add('/browse.html', data_day, '0.9', 'weekly')
    add('/blog', blog_day, '0.8', 'weekly')
    for k in keys:
        add(f'/{k}', posts[k], '0.7', 'monthly')
    for c in cats:
        add(f'/shop/{c}', data_day, '0.8', 'weekly')
    for p in prods:
        add(p, data_day, '0.6', 'weekly')

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + '\n'.join(rows) + '\n</urlset>\n')
    open(OUT, 'w', encoding='utf-8').write(xml)

    n_all = sum(len(d[c]) for c in cats)
    print(f'sitemap.xml yazildi — {len(rows)} URL (3 statik + {len(keys)} yazi + '
          f'{len(cats)} kategori + {len(prods)}/{n_all} indekslenebilir urun)')
    return len(rows)


if __name__ == '__main__':
    main()
