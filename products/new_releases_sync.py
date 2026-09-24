#!/usr/bin/env python3
"""ToyScout — Amazon New Releases (Toys & Games) toplu ekleme.

Amazon'un "New Releases" listesini (zg_bsnr, ayni sayfalama sekli
bestseller_sync.py'nin Best Sellers listesiyle ayni: sayfa basina ~30 urun,
sira numaralari atlamali) birden fazla sayfa gezerek ~TARGET_TOTAL urune
ulasana kadar tarar.

22 Eyl 2026 kullanici karariyla puan/yorum esigi YOK (bkz. bestseller_sync.py
ayni tarihli not) — yeni cikan urunlerin cogunun henuz yorumu az/hic yok,
hepsi eklenir. Sadece varyant kontrolu (veri dogrulugu, kalite esigi degil)
ve kategori tespiti (BSR + baslik) uygulanir; kategori belirlenemeyen urun
"ELLE BAKILACAK" olarak loglanir ve eklenmez.

Katalogu asla tam yeniden yazmaz: mevcut js/data.js yuklenir, sadece yeni
ASIN'ler eklenir, sonra kaydedilir.

Kullanim:
    python3 products/new_releases_sync.py --dry-run
    python3 products/new_releases_sync.py
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bestseller_sync as bs  # noqa: E402

TARGET_TOTAL = 100
MAX_PAGES = 6
LIST_URL = ("https://www.amazon.com/gp/new-releases/toys-and-games/"
            "ref=zg_bsnr_pg_{pg}_toys-and-games?ie=UTF8&pg={pg}")


def parse_list_page(h):
    """bestseller_sync.parse_list_page ile ayni format (zg-bdg-text rozetleri)."""
    return bs.parse_list_page(h)


def fetch_new_releases(max_pages=MAX_PAGES, target_total=TARGET_TOTAL):
    all_rows, seen = [], set()
    for pg in range(1, max_pages + 1):
        url = LIST_URL.format(pg=pg)
        rows = []
        for attempt in range(1, 4):
            rows = parse_list_page(bs.curl(url))
            if rows:
                break
            bs.log(f'  New Releases sayfa {pg}: {attempt}. deneme bos dondu, tekrar deneniyor')
            time.sleep(bs.DELAY * 3 * attempt)
        new = [r for r in rows if r["asin"] not in seen]
        for r in new:
            seen.add(r["asin"])
        all_rows += new
        if rows:
            bs.log(f'  New Releases sayfa {pg}: {len(rows)} urun, {len(new)} yeni '
                    f'(toplam {len(all_rows)})')
        else:
            bs.log(f'  New Releases sayfa {pg}: 3 denemede de alinamadi — ATLANDI')
        if len(all_rows) >= target_total:
            break
        time.sleep(bs.DELAY)
    return all_rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-pages", type=int, default=MAX_PAGES)
    ap.add_argument("--target", type=int, default=TARGET_TOTAL)
    args = ap.parse_args()

    bs.log("=" * 66)
    bs.log(f'New Releases toplu ekleme basladi (dry-run={args.dry_run}, '
            f'hedef={args.target}, max_sayfa={args.max_pages})')

    listing = fetch_new_releases(args.max_pages, args.target)
    bs.log(f'toplam {len(listing)} benzersiz New Releases urunu bulundu')

    d = bs.load_catalog()
    known_asins = {p["asin"] for items in d.values() for p in items}
    bak = None if args.dry_run else bs.backup()
    if bak:
        bs.log(f'yedek: {os.path.basename(bak)}')

    added = skipped = manual = 0
    for r in listing:
        if r["asin"] in known_asins:
            continue

        prod = bs.fetch_product(r["asin"])
        time.sleep(bs.DELAY)
        if not prod or not prod["name"]:
            bs.log(f'  ! {r["asin"]} urun sayfasi okunamadi, atlandi')
            skipped += 1
            continue

        dup = bs.is_variant(prod["name"], d)
        if dup:
            bs.log(f'  - {r["asin"]} atlandi (varyant: katalogdaki {dup} ile ayni urun)')
            skipped += 1
            continue

        cat = bs.pick_category(prod)
        if not cat or cat not in d:
            bs.log(f'  ? {r["asin"]} kategori belirlenemedi — ELLE BAKILACAK: '
                    f'{prod["name"][:60]!r} bsr={[x["cat"] for x in prod["bsr"][:3]]}')
            manual += 1
            continue

        if args.dry_run:
            bs.log(f'  (dry-run) + {r["asin"]} [{cat}] {prod["rating"]}*/{prod["rc"]}yorum '
                    f'{prod["name"][:52]}')
            known_asins.add(r["asin"])
            added += 1
            continue

        gallery = bs.download_images(r["asin"], prod["images"])
        if not gallery:
            bs.log(f'  ! {r["asin"]} gorsel indirilemedi, atlandi')
            skipped += 1
            continue

        d[cat].append({
            "asin": r["asin"], "name": prod["name"], "img": gallery[0],
            "url": f'https://www.amazon.com/dp/{r["asin"]}?tag=kolico-20',
            "rc": prod["rc"], "rating": prod["rating"],
            "bsr": prod["bsr"] or [], "gallery": gallery, "bullets": prod["bullets"],
            "price": prod["price"], "lo": prod["lo"],
        })
        known_asins.add(r["asin"])
        added += 1
        bs.log(f'  + {r["asin"]} [{cat}] {prod["rating"]}*/{prod["rc"]}yorum '
                f'gorsel={len(gallery)} {prod["name"][:45]}')

    if args.dry_run:
        bs.log(f'(dry-run) toplam {added} urun eklenecekti, {skipped} atlandi, '
                f'{manual} elle bakilacak. Dosyaya dokunulmadi.')
        return 0

    bs.save_catalog(d)
    total = sum(len(v) for v in d.values())
    bs.log(f'{added} urun eklendi, {skipped} atlandi, {manual} elle bakilacak. '
            f'Katalog toplam: {total}')

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
