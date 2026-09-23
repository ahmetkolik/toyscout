#!/usr/bin/env python3
"""
ToyScout — Toys & Games TUM alt kategorilerinin Best Sellers + Hot New Releases
listelerinden urun ekler (26 Eyl 2026, kullanici istegi).

bestseller_sync.py'nin fonksiyonlarini (curl, liste ayristirma, urun sayfasi,
gorsel indirme, varyant kontrolu) yeniden kullanir; kalite kurallari AYNIDIR
(puan >= 4.4, yorum >= 50, varyant degil). Fark: kategori, urunun geldigi Amazon
alt kategorisinden dogrudan atanir (tahmin yok).

Her liste icin sira 1-30 (sayfa 1, sunucu tarafi) + 51-70 (sayfa 2) = 50 aday.
Sira 31-50 sayfa kaydirilinca yuklenen kisim; curl ile gelmez.

Kullanim:
  python3 products/subcat_sync.py --lists-only   # sadece aday sayilarini yaz, katalogu degistirme
  python3 products/subcat_sync.py                # ekle (data.js yedeklenir, 25 urunde bir kaydedilir)
YAPMADIKLARI: deploy etmez, commit etmez.
"""
from __future__ import annotations

import sys
import time

import bestseller_sync as b

# (Amazon alt kategori adi, node id, url slug, site kategori id)
SUBCATS = [
    ('Arts & Crafts', '166057011', 'Arts-Crafts-Supplies', 'arts-crafts'),
    ('Baby & Toddler Toys', '196601011', 'Baby-Toddler-Toys', 'baby-toddler'),
    ('Building Toys', '166092011', 'Building-Toys', 'building-toys'),
    ('Collectible Card Games', '166242011', 'Collectible-Card-Games', 'games'),
    ('Dolls & Accessories', '166118011', 'Dolls-Accessories', 'dolls'),
    ('Games & Accessories', '166220011', 'Games-Accessories', 'games'),
    ('Hobby, Remote & App Controlled Vehicles', '6925830011',
     'Hobby-Remote-App-Controlled-Vehicles-Parts', 'rc-vehicles'),
    ('Kids Dress Up & Pretend Play', '166316011', 'Kids-Dress-Up-Pretend-Play', 'dress-up'),
    ('Kids Electronics', '166164011', 'Kids-Electronics', 'kids-electronics'),
    ('Kids Musical Instruments', '166326011', 'Kids-Musical-Instruments', 'musical-instruments'),
    ('Kids Party Supplies', '1266203011', 'Kids-Party-Supplies', 'party'),
    ('Learning & Education Toys', '166269011', 'Learning-Education-Toys', 'learning-education'),
    ('Novelty Toys & Amusements', '166027011', 'Novelty-Toys-Amusements', 'novelty'),
    ('Puppets & Puppet Theaters', '166333011', 'Puppets-Puppet-Theaters', 'puppets'),
    ('Puzzles', '166359011', 'Puzzles', 'puzzles'),
    ('Sports & Outdoor Play Toys', '166420011', 'Sports-Outdoor-Play-Toys', 'sports-outdoor'),
    ('Stuffed Animals & Plush Toys', '166461011', 'Stuffed-Animals-Plush-Toys', 'plush'),
    ('Toy Figures & Playsets', '165993011', 'Toy-Figures-Playsets', 'action-figures'),
    ('Toy Vehicles', '23539911011', 'Toy-Vehicles', 'rc-vehicles'),
    ('Tricycles, Scooters & Wagons', '256994011', 'Tricycles-Scooters-Wagons', 'ride-ons'),
]

KINDS = [
    ('best', 'https://www.amazon.com/Best-Sellers-Toys-Games-{slug}/zgbs/toys-and-games/{node}'
             '?_encoding=UTF8&pg={pg}'),
    ('new', 'https://www.amazon.com/gp/new-releases/toys-and-games/{node}?_encoding=UTF8&pg={pg}'),
]
MAX_RANK_P2 = 70          # sayfa 2'den 51-70 alinir -> liste basina 50 aday
SAVE_EVERY = 25


def fetch_rows(url):
    for attempt in (1, 2, 3):
        rows = b.parse_list_page(b.curl(url))
        if rows:
            return rows
        time.sleep(b.DELAY * 3 * attempt)
    return []


def collect_candidates():
    """-> list of dict(asin, rank, rating, rc, price, cat, src, sub)"""
    cands, seen = [], set()
    for sub, node, slug, cat in SUBCATS:
        counts = {}
        for kind, tmpl in KINDS:
            n = 0
            for pg in (1, 2):
                rows = fetch_rows(tmpl.format(slug=slug, node=node, pg=pg))
                time.sleep(b.DELAY)
                if not rows:
                    b.log(f'  UYARI: {sub} [{kind}] sayfa {pg} alinamadi')
                for r in rows:
                    if pg == 2 and r['rank'] > MAX_RANK_P2:
                        continue
                    n += 1
                    if r['asin'] in seen:
                        continue
                    seen.add(r['asin'])
                    cands.append(dict(r, cat=cat, src=kind, sub=sub))
            counts[kind] = n
        b.log(f'  {sub:42s} best={counts["best"]:3d} new={counts["new"]:3d} -> {cat}')
    return cands


def main():
    lists_only = '--lists-only' in sys.argv
    b.log('=' * 66)
    b.log('Alt kategori senkronizasyonu (Best Sellers + Hot New Releases) basladi')
    cands = collect_candidates()
    d = b.load_catalog()
    index = {p['asin'] for items in d.values() for p in items}
    new = [c for c in cands if c['asin'] not in index]
    ok = [c for c in new if c['rating'] and c['rating'] >= b.MIN_RATING
          and c['rc'] and c['rc'] >= b.MIN_REVIEWS]
    b.log(f'benzersiz aday: {len(cands)}, katalogda olmayan: {len(new)}, '
          f'kalite esigini gecen: {len(ok)}')
    for kind in ('best', 'new'):
        b.log(f'  gecen [{kind}]: {sum(1 for c in ok if c["src"] == kind)}')
    if lists_only:
        return 0

    bak = b.backup()
    b.log(f'yedek: {bak}')
    added = skipped = 0
    for c in ok:
        asin, cat = c['asin'], c['cat']
        prod = b.fetch_product(asin)
        if not prod:
            time.sleep(6)
            prod = b.fetch_product(asin)
        time.sleep(b.DELAY)
        if not prod or not prod['name']:
            b.log(f'  ! {asin} urun sayfasi okunamadi, atlandi')
            skipped += 1
            continue
        if prod['rating'] and prod['rating'] < b.MIN_RATING:
            skipped += 1
            continue
        dup = b.is_variant(prod['name'], d)
        if dup:
            b.log(f'  - {asin} atlandi (varyant: {dup})')
            skipped += 1
            continue
        gallery = b.download_images(asin, prod['images'])
        if not gallery:
            b.log(f'  ! {asin} gorsel indirilemedi, atlandi')
            skipped += 1
            continue
        d.setdefault(cat, []).append({
            'asin': asin, 'name': prod['name'], 'img': gallery[0],
            'url': f'https://www.amazon.com/dp/{asin}?tag=kolico-20',
            'rc': prod['rc'] or c['rc'], 'rating': prod['rating'] or c['rating'],
            'bsr': prod['bsr'] or [{'rank': c['rank'], 'cat': c['sub']}],
            'gallery': gallery, 'bullets': prod['bullets'],
            'price': prod['price'] or c['price'], 'lo': prod['lo'],
        })
        added += 1
        b.log(f'  + {asin} [{cat}] ({c["src"]} #{c["rank"]}) {prod["rating"]}* '
              f'{prod["name"][:50]}')
        if added % SAVE_EVERY == 0:
            b.save_catalog(d)
    b.save_catalog(d)
    b.log(f'{added} urun eklendi, {skipped} atlandi. Katalog toplam: '
          f'{sum(len(v) for v in d.values())}')
    try:
        import build_sitemap
        b.log(f'sitemap.xml: {build_sitemap.main()} URL')
        import build_browse_page
        b.log(f'browse.html: {build_browse_page.main()} link')
    except Exception as e:
        b.log(f'UYARI: sitemap/browse uretilemedi ({type(e).__name__}: {e})')
    b.log('bitti. NOT: deploy/commit YAPILMADI.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
