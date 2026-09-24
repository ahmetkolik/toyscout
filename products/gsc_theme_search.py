#!/usr/bin/env python3
"""ToyScout — GSC talep temali hedefli urun arama/ekleme.

bestseller_sync.py genel Toys & Games Best Sellers listesinin (top 80)
disinda kalan, ama notes/*-gsc-keyword-log.md'de yuksek gosterimli oldugu
tespit edilen temalari (squishy/fidget, family board games, baby rattle,
balance bike...) doğrudan Amazon arama sonuclarindan tarar.

22 Eyl 2026 kullanici karariyla puan/yorum esigi yok — sadece varyant
kontrolu (ayni urunun renk/boy varyanti eklenmez) uygulanir; bkz.
bestseller_sync.py ayni tarihli notu. Kategori, BSR tahminiyle degil,
hangi tema aramasindan geldigine gore DOGRUDAN atanir (daha guvenilir).

Katalogu asla tam yeniden yazmaz: mevcut js/data.js yuklenir, sadece yeni
gecen ASIN'ler eklenir, sonra kaydedilir. fetch_products.py'nin aksine
links.txt dosyalarina bagli degildir.

Kullanim:
    python3 products/gsc_theme_search.py --dry-run   # neyin ekleneceğini gosterir, dosyaya dokunmaz
    python3 products/gsc_theme_search.py             # gercekten ekler
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bestseller_sync as bs  # noqa: E402

# (arama sorgusu, hedef site kategorisi, bu temadan en fazla kac urun eklensin)
THEMES = [
    ("squishy toys", "novelty", 4),
    ("fidget toys", "novelty", 3),
    ("family board games", "games", 4),
    ("baby wrist rattle", "baby-toddler", 3),
]

SEARCH_URL = ("https://www.amazon.com/s?k={q}&i=toys-and-games"
              "&s=review-rank")


def fetch_search_candidates(query):
    """Bir arama sonucu sayfasindan (asin, rating, reviews) listesi cikarir."""
    url = SEARCH_URL.format(q=query.replace(" ", "+"))
    html = bs.curl(url)
    if len(html) < 50000 or "captcha" in html.lower():
        bs.log(f'  UYARI: "{query}" arama sayfasi alinamadi/engellenmis oldu, atlandi')
        return []
    out, seen = [], set()
    for m in re.finditer(r'data-asin="([A-Z0-9]{10})"', html):
        asin = m.group(1)
        if asin in seen:
            continue
        seen.add(asin)
        seg = html[m.end():m.end() + 9000]
        rt = re.search(r'([\d.]+) out of 5 stars', seg)
        rc = re.search(r'aria-label="([\d,]+) ratings?"', seg)
        out.append(dict(
            asin=asin,
            rating=float(rt.group(1)) if rt else None,
            rc=int(rc.group(1).replace(',', '')) if rc else None,
        ))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                     help="siteyi degistirmeden neyin ekleneceğini gosterir")
    args = ap.parse_args()

    bs.log("=" * 66)
    bs.log(f'GSC temali hedefli arama basladi (dry-run={args.dry_run})')

    d = bs.load_catalog()
    known_asins = {p["asin"] for items in d.values() for p in items}
    bak = None if args.dry_run else bs.backup()
    if bak:
        bs.log(f"yedek: {__import__('os').path.basename(bak)}")

    added = skipped = 0
    for query, cat, limit in THEMES:
        if cat not in d:
            bs.log(f'  ! kategori "{cat}" katalogda yok, "{query}" atlandi')
            continue
        bs.log(f'[{query}] -> {cat}')
        candidates = fetch_search_candidates(query)
        bs.log(f'  {len(candidates)} aday bulundu')
        got = 0
        for c in candidates:
            if got >= limit:
                break
            if c["asin"] in known_asins:
                continue

            prod = bs.fetch_product(c["asin"])
            time.sleep(bs.DELAY)
            if not prod or not prod["name"]:
                bs.log(f'  ! {c["asin"]} urun sayfasi okunamadi, atlandi')
                skipped += 1
                continue

            dup = bs.is_variant(prod["name"], d)
            if dup:
                bs.log(f'  - {c["asin"]} atlandi (varyant: katalogdaki {dup} ile ayni urun)')
                skipped += 1
                continue

            if args.dry_run:
                bs.log(f'  (dry-run) + {c["asin"]} [{cat}] {prod["rating"]}* '
                       f'{prod["name"][:60]}')
                known_asins.add(c["asin"])
                got += 1
                added += 1
                continue

            gallery = bs.download_images(c["asin"], prod["images"])
            if not gallery:
                bs.log(f'  ! {c["asin"]} gorsel indirilemedi, atlandi')
                skipped += 1
                continue

            d[cat].append({
                "asin": c["asin"], "name": prod["name"], "img": gallery[0],
                "url": f'https://www.amazon.com/dp/{c["asin"]}?tag=kolico-20',
                "rc": prod["rc"] or c["rc"], "rating": prod["rating"] or c["rating"],
                "bsr": prod["bsr"] or [],
                "gallery": gallery, "bullets": prod["bullets"],
                "price": prod["price"], "lo": prod["lo"],
            })
            known_asins.add(c["asin"])
            got += 1
            added += 1
            bs.log(f'  + {c["asin"]} [{cat}] {prod["rating"]}* gorsel={len(gallery)} '
                   f'{prod["name"][:52]}')

    if args.dry_run:
        bs.log(f'(dry-run) toplam {added} urun eklenecekti, {skipped} atlandi. '
               f'Dosyaya dokunulmadi.')
        return 0

    bs.save_catalog(d)
    total = sum(len(v) for v in d.values())
    bs.log(f'{added} urun eklendi, {skipped} atlandi. Katalog toplam: {total}')

    if added:
        n = bs.write_sitemap(d)
        bs.log(f'sitemap-products.xml yeniden uretildi: {n} URL')
        try:
            import build_sitemap
            n = build_sitemap.main()
            bs.log(f'sitemap.xml yeniden uretildi: {n} URL')
        except Exception as e:
            bs.log(f'UYARI: sitemap.xml uretilemedi ({type(e).__name__}: {e})')
        try:
            import build_browse_page
            links = build_browse_page.main()
            bs.log(f'browse.html yeniden uretildi: {links} gercek urun linki')
        except Exception as e:
            bs.log(f'UYARI: browse.html uretilemedi ({type(e).__name__}: {e})')

    bs.ping_supabase()
    bs.log('bitti. NOT: deploy YAPILMADI — canliya cikmasi icin push gerekiyor.')
    return 0


if __name__ == "__main__":
    sys.exit(main())
