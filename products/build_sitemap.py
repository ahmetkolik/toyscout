#!/usr/bin/env python3
"""
sitemap.xml uretici — TEK ve TAM sitemap.

NEDEN VAR (30 Tem 2026 tespiti):
  Iki ayri sitemap vardi ve bolunme zarar veriyordu:
    - sitemap.xml         -> Google OKUYOR (Last read 30 Tem, Success, 124 sayfa)
                             ama yalnizca ESKI 97 urunu iceriyordu
    - sitemap-products.xml -> 115 urunun tamami vardi ama Google CEKEMIYOR
                             ("Couldn't fetch", 0 kesif, gunlerdir duzelmiyor)
  Yani yeni eklenen 18 urun + /shop/dolls, Google'in okudugu dosyada YOKTU.
  URL Inspection bu sayfalar icin "URL is unknown to Google" +
  "No referring sitemaps detected" diyordu.

  Cozum: her seyi Google'in kanitlanmis sekilde okudugu sitemap.xml'e koy.

NE URETIR:
  statik sayfalar + blog yazilari + /browse.html  (STATIC listesinden)
  + /shop/<kategori>   (katalogda urunu olan her kategori)
  + /product/<kategori>/<idx>  (115 urunun tamami)

Calistirma: python3 products/build_sitemap.py
bestseller_sync.py her turda otomatik cagirir (urun eklenince sitemap buyusun).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(SITE, 'js', 'data.js')
OUT = os.path.join(SITE, 'sitemap.xml')

# (yol, oncelik, degisim sikligi) — urun/kategori disi her sey
STATIC = [
    ('/', '1.0', 'daily'),
    ('/browse.html', '0.9', 'weekly'),
    ('/blog', '0.8', 'weekly'),
    ('/post1', '0.7', 'monthly'), ('/post2', '0.7', 'monthly'),
    ('/post3', '0.7', 'monthly'), ('/post4', '0.7', 'monthly'),
    ('/post5', '0.7', 'monthly'), ('/post6', '0.7', 'monthly'),
    ('/post7', '0.7', 'monthly'), ('/post8', '0.7', 'monthly'),
    ('/post9', '0.7', 'monthly'),
    ('/post10', '0.7', 'monthly'),
    ('/post11', '0.7', 'monthly'),
    ('/post12', '0.7', 'monthly'),
    ('/contact', '0.5', 'monthly'),
    ('/privacy', '0.3', 'yearly'),
    ('/terms', '0.3', 'yearly'),
    ('/disclosure', '0.4', 'yearly'),
]

CAT_ORDER = ['action-figures', 'arts-crafts', 'baby-toddler', 'building-toys', 'dolls',
             'games', 'learning-education', 'novelty', 'party', 'sports-outdoor',
             'plush', 'ride-ons']


def main():
    src = open(DATA, encoding='utf-8').read()
    d = json.loads(re.search(r'window\.TS_DATA\s*=\s*(\{.*\})\s*;?\s*$', src, re.S).group(1))
    cats = [c for c in CAT_ORDER if c in d and d[c]] + \
           [c for c in d if c not in CAT_ORDER and d[c]]
    today = dt.date.today().isoformat()

    rows = []

    def add(path, prio, freq):
        rows.append(
            f'  <url>\n'
            f'    <loc>https://www.toyscout.net{path}</loc>\n'
            f'    <lastmod>{today}</lastmod>\n'
            f'    <changefreq>{freq}</changefreq>\n'
            f'    <priority>{prio}</priority>\n'
            f'  </url>')

    for path, prio, freq in STATIC:
        add(path, prio, freq)
    for c in cats:
        add(f'/shop/{c}', '0.8', 'weekly')
    for c in cats:
        for i in range(len(d[c])):
            add(f'/product/{c}/{i}', '0.7', 'weekly')

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + '\n'.join(rows) + '\n</urlset>\n')
    open(OUT, 'w', encoding='utf-8').write(xml)

    n_prod = sum(len(d[c]) for c in cats)
    print(f'sitemap.xml yazildi — {len(rows)} URL '
          f'({len(STATIC)} statik + {len(cats)} kategori + {n_prod} urun)')
    return len(rows)


if __name__ == '__main__':
    main()