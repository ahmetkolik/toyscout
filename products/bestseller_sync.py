#!/usr/bin/env python3
"""
ToyScout — Amazon Best Sellers (Toys & Games) senkronizasyonu.

5 gunde bir launchd ile calisir (net.toyscout.bestsellers).

Yaptiklari:
  1. js/data.js yedeklenir (son 10 yedek tutulur).
  2. Best Sellers listesi cekilir (sayfa basina 30 kart -> sira 1-30 ve 51-80).
  3. Katalogda ZATEN OLAN urunlerde fiyat / puan / yorum / Toys & Games BSR guncellenir.
  4. Listede olup katalogda OLMAYAN urunlerden kalite kurallarini gecenler,
     6 galeri gorseliyle birlikte eklenir.
  5. Urun eklendiyse sitemap-products.xml yeniden uretilir.
  6. Her sey products/bestseller_sync.log dosyasina yazilir.

YAPMADIKLARI: deploy etmez. Degisiklikler yereldedir; canliya cikmasi icin
ayrica push gerekir (bkz. DEPLOY notu asagida).

Kalite kurallari (kullanici karari, 29 Tem 2026):
  - Sadece MIN_RATING (4.4) ve uzeri, en az MIN_REVIEWS yorumu olan urunler eklenir.
  - Puani/yorumu olmayan yeni listelemeler eklenmez.
  - Varyant tuzagi: basligi katalogdaki bir urunle cok benzeyen ASIN eklenmez
    (ayni urunun renk/boy varyanti ayri ASIN olarak listede gorunebiliyor).
  - Kategorisi guvenle belirlenemeyen urun eklenmez, log'a "elle bakilacak" yazilir.
"""
from __future__ import annotations

import datetime as dt
import difflib
import glob
import html
import json
import os
import re
import subprocess
import sys
import time

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(SITE, 'js', 'data.js')
ASSETS = os.path.join(SITE, 'assets', 'products')
SITEMAP = os.path.join(SITE, 'sitemap-products.xml')
LOG = os.path.join(SITE, 'products', 'bestseller_sync.log')

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')

MIN_RATING = 4.4
MIN_REVIEWS = 50
KEEP_BACKUPS = 10
DELAY = 1.2          # Amazon'a nazik davran
SIM_THRESHOLD = 0.90  # baslik benzerligi -> varyant sayilir

LIST_URLS = [
    'https://www.amazon.com/Best-Sellers-Toys-Games/zgbs/toys-and-games/ref=zg_bs_pg_1?_encoding=UTF8&pg=1',
    'https://www.amazon.com/Best-Sellers-Toys-Games/zgbs/toys-and-games/ref=zg_bs_pg_2?_encoding=UTF8&pg=2',
]

# Amazon BSR alt kategori adi -> sitedeki kategori id'si.
# Ilk eslesen anahtar kelime kazanir; sirasi onemli (ozelden genele).
CAT_RULES = [
    ('action figure', 'action-figures'), ('toy figure', 'action-figures'),
    ('balloon', 'party'), ('party', 'party'),
    ('stuffed animal', 'plush'), ('plush', 'plush'), ('teddy', 'plush'),
    ('ride-on', 'ride-ons'), ('balance bike', 'ride-ons'), ('tricycle', 'ride-ons'),
    ('scooter', 'ride-ons'), ('bikes', 'ride-ons'),
    ('building', 'building-toys'), ('block', 'building-toys'), ('stacking', 'building-toys'),
    ('magnetic playboard', 'building-toys'),
    ('baby', 'baby-toddler'), ('infant', 'baby-toddler'), ('toddler', 'baby-toddler'),
    ('rattle', 'baby-toddler'), ('teether', 'baby-toddler'),
    ('card game', 'games'), ('board game', 'games'), ('game', 'games'), ('puzzle', 'games'),
    ('learning', 'learning-education'), ('education', 'learning-education'),
    ('flash card', 'learning-education'),
    ('sport', 'sports-outdoor'), ('outdoor', 'sports-outdoor'), ('water', 'sports-outdoor'),
    ('pool', 'sports-outdoor'), ('bubble', 'sports-outdoor'), ('swim', 'sports-outdoor'),
    ('novelty', 'novelty'), ('gag', 'novelty'), ('fidget', 'novelty'), ('squish', 'novelty'),
    ('slime', 'novelty'),
    ('craft', 'arts-crafts'), ('art', 'arts-crafts'), ('marker', 'arts-crafts'),
    ('crayon', 'arts-crafts'), ('pencil', 'arts-crafts'), ('paint', 'arts-crafts'),
    ('clay', 'arts-crafts'), ('dough', 'arts-crafts'), ('sticker', 'arts-crafts'),
    ('drawing', 'arts-crafts'), ('paper', 'arts-crafts'), ('scissor', 'arts-crafts'),
    ('glue', 'arts-crafts'), ('coloring', 'arts-crafts'),
]


def log(msg=''):
    line = f'{dt.datetime.now():%Y-%m-%d %H:%M:%S}  {msg}' if msg else ''
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def curl(url, out=None):
    cmd = ['curl', '-sS', '-L', '--compressed', '--max-time', '45',
           '-H', f'User-Agent: {UA}',
           '-H', 'Accept-Language: en-US,en;q=0.9',
           '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8']
    if out:
        cmd += ['-o', out, '-w', '%{http_code}']
        r = subprocess.run(cmd + [url], capture_output=True, text=True)
        return r.stdout.strip()
    return subprocess.run(cmd + [url], capture_output=True, text=True,
                          errors='ignore').stdout


def strip_tags(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


# ---------------------------------------------------------------- katalog I/O

def load_catalog():
    src = open(DATA, encoding='utf-8').read()
    m = re.search(r'window\.TS_DATA\s*=\s*(\{.*\})\s*;?\s*$', src, re.S)
    if not m:
        raise SystemExit('data.js ayristirilamadi — durduruldu, dosyaya dokunulmadi.')
    return json.loads(m.group(1))


def save_catalog(d):
    open(DATA, 'w', encoding='utf-8').write(
        'window.TS_DATA=' + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + ';')


def backup():
    stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    dest = f'{DATA}.bak-{stamp}'
    subprocess.run(['cp', DATA, dest], check=True)
    old = sorted(glob.glob(f'{DATA}.bak-*'))[:-KEEP_BACKUPS]
    for f in old:
        os.remove(f)
    return dest


# ---------------------------------------------------------------- liste + urun

def parse_list_page(h):
    """Bir Best Sellers sayfasindan satirlari cikar."""
    rows = []
    for blk in re.split(r'zg-bdg-text', h)[1:]:
            m = re.match(r'[^>]*>\s*#?(\d+)', blk)
            if not m:
                continue
            rank = int(m.group(1))
            seg = blk[:9000]
            a = re.search(r'/dp/([A-Z0-9]{10})', seg)
            if not a:
                continue
            rt = re.search(r'([\d.]+) out of 5 stars', seg)
            rc = re.search(r'>\s*([\d,]{2,})\s*</span>', seg)
            pr = re.search(r'\$([\d,]+\.\d\d)', seg)
            rows.append(dict(
                rank=rank, asin=a.group(1),
                rating=float(rt.group(1)) if rt else None,
                rc=int(rc.group(1).replace(',', '')) if rc else None,
                price=f'${pr.group(1)}' if pr else None))
    return rows


def fetch_list():
    """Iki liste sayfasini (sira 1-30 ve 51-80) tekrar denemeli olarak ceker.

    Amazon zaman zaman bos/engelli yanit donuyor; sessizce yarim listeyle
    devam etmemek icin her sayfa 3 kez denenir ve sayfa basina sonuc loglanir.
    """
    all_rows, failed = [], []
    for n, url in enumerate(LIST_URLS, 1):
        rows = []
        for attempt in range(1, 4):
            rows = parse_list_page(curl(url))
            if rows:
                break
            log(f'  liste sayfa {n}: {attempt}. deneme bos dondu, tekrar deneniyor')
            time.sleep(DELAY * 3 * attempt)
        if rows:
            log(f'  liste sayfa {n}: {len(rows)} urun '
                f'(sira {rows[0]["rank"]}-{rows[-1]["rank"]})')
            all_rows += rows
        else:
            failed.append(n)
            log(f'  liste sayfa {n}: 3 denemede de alinamadi — ATLANDI')
        time.sleep(DELAY)

    seen, out = set(), []
    for r in all_rows:
        if r['asin'] not in seen:
            seen.add(r['asin'])
            out.append(r)
    if failed:
        log(f'UYARI: {len(failed)} liste sayfasi alinamadi; bu turda listenin '
            f'yalnizca bir kismi islendi.')
    return out


def fetch_product(asin):
    h = curl(f'https://www.amazon.com/dp/{asin}')
    if len(h) < 50000 or 'captcha' in h.lower():
        return None
    d = {'asin': asin}

    m = re.search(r'id="productTitle"[^>]*>(.*?)</span>', h, re.S)
    d['name'] = strip_tags(m.group(1)).replace('​', '').strip() if m else None

    m = re.search(r'id="acrPopover"[^>]*title="([\d.]+) out of 5', h) \
        or re.search(r'([\d.]+) out of 5 stars', h)
    d['rating'] = float(m.group(1)) if m else None

    d['rc'] = None
    for pat in (r'id="acrCustomerReviewText"[^>]*>\s*([\d,]+)',
                r'data-hook="total-review-count"[^>]*>\s*([\d,]+)',
                r'"ratingCount"\s*:\s*(\d+)'):
        m = re.search(pat, h)
        if m:
            d['rc'] = int(m.group(1).replace(',', ''))
            break

    price = None
    for pat in (r'id="corePrice_feature_div".*?<span class="a-offscreen">\$([\d,.]+)',
                r'"priceAmount":([\d.]+)'):
        m = re.search(pat, h, re.S)
        if m:
            price = m.group(1).replace(',', '')
            break
    d['price'] = f'${price}' if price else None
    d['lo'] = float(price) if price else None

    bsr = []
    for blob in re.findall(r'Best Sellers Rank(.{0,900}?)(?:</ul>|</table>|</div>)', h, re.S):
        for rank, cat in re.findall(r'#([\d,]+)\s*in\s*([^(<#]{2,60})', strip_tags(blob)):
            c = cat.strip().rstrip(',').strip()
            if c and not any(x['cat'] == c for x in bsr):
                bsr.append({'rank': int(rank.replace(',', '')), 'cat': c})
        if bsr:
            break
    d['bsr'] = bsr

    bullets = []
    m = re.search(r'id="feature-bullets"(.*?)</div>\s*</div>', h, re.S)
    if m:
        for li in re.findall(r'<li[^>]*>(.*?)</li>', m.group(1), re.S):
            t = strip_tags(li)
            if len(t) > 15 and 'Make sure this fits' not in t:
                bullets.append(t)
    d['bullets'] = bullets[:6]

    imgs = []
    i = h.find("'colorImages': { 'initial'")
    if i != -1:
        for u in re.findall(
                r'"(?:hiRes|large)":"(https://m\.media-amazon\.com/images/I/[^"]+)"',
                h[i:i + 40000]):
            if u not in imgs:
                imgs.append(u)
    if not imgs:
        m = re.search(r'id="landingImage"[^>]*data-old-hires="([^"]+)"', h)
        if m:
            imgs = [m.group(1)]
    d['images'] = imgs[:6]
    return d


def pick_category(prod):
    """BSR alt kategori adlarindan + urun basligindan site kategorisi tahmin et."""
    hay = ' '.join(x['cat'] for x in prod['bsr'][1:]).lower()
    for kw, cat in CAT_RULES:
        if kw in hay:
            return cat
    name = (prod['name'] or '').lower()
    for kw, cat in CAT_RULES:
        if kw in name:
            return cat
    return None


def is_variant(name, catalog):
    """Katalogda cok benzer baslikli bir urun var mi (renk/boy varyanti)."""
    n = (name or '').lower()[:120]
    for items in catalog.values():
        for p in items:
            if difflib.SequenceMatcher(None, n, p['name'].lower()[:120]).ratio() >= SIM_THRESHOLD:
                return p['asin']
    return None


def download_images(asin, urls):
    gallery = []
    for i, u in enumerate(urls[:6]):
        fn = f'{asin}.jpg' if i == 0 else f'{asin}_{i}.jpg'
        dest = os.path.join(ASSETS, fn)
        if curl(u, out=dest) == '200' and os.path.getsize(dest) > 5000:
            gallery.append(f'assets/products/{fn}')
        elif os.path.exists(dest):
            os.remove(dest)
    return gallery


def write_sitemap(d):
    order = ['action-figures', 'arts-crafts', 'baby-toddler', 'building-toys', 'games',
             'learning-education', 'novelty', 'party', 'sports-outdoor', 'plush', 'ride-ons']
    cats = [c for c in order if c in d] + [c for c in d if c not in order]
    today = dt.date.today().isoformat()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    n = 0
    for c in cats:
        for i in range(len(d[c])):
            out += ['  <url>',
                    f'    <loc>https://www.toyscout.net/product/{c}/{i}</loc>',
                    f'    <lastmod>{today}</lastmod>',
                    '    <changefreq>weekly</changefreq>',
                    '    <priority>0.8</priority>', '  </url>']
            n += 1
    out.append('</urlset>')
    open(SITEMAP, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    return n


# ---------------------------------------------------------------- ana akis

def main():
    log('=' * 66)
    log('Best Sellers senkronizasyonu basladi')

    listing = fetch_list()
    if len(listing) < 20:
        log(f'HATA: listeden yalnizca {len(listing)} urun cikti — Amazon engellemis '
            f'olabilir. Katalog DEGISTIRILMEDI.')
        return 1
    log(f'listeden {len(listing)} urun alindi (sira '
        f'{min(r["rank"] for r in listing)}-{max(r["rank"] for r in listing)})')

    d = load_catalog()
    bak = backup()
    log(f'yedek: {os.path.basename(bak)}')
    index = {p['asin']: (c, p) for c, items in d.items() for p in items}

    # --- 1) mevcut urunleri guncelle
    upd = 0
    for r in listing:
        hit = index.get(r['asin'])
        if not hit:
            continue
        _, p = hit
        ch = []
        if r['price'] and p.get('price') != r['price']:
            ch.append(f"fiyat {p.get('price')}->{r['price']}")
            p['price'] = r['price']
            p['lo'] = float(r['price'].lstrip('$').replace(',', ''))
        if r['rating'] and p.get('rating') != r['rating']:
            ch.append(f"puan {p.get('rating')}->{r['rating']}")
            p['rating'] = r['rating']
        if r['rc'] and p.get('rc') != r['rc']:
            ch.append(f"yorum {p.get('rc')}->{r['rc']}")
            p['rc'] = r['rc']
        bsr = p.get('bsr') or []
        tg = [x for x in bsr if x.get('cat') == 'Toys & Games']
        if tg:
            if tg[0].get('rank') != r['rank']:
                ch.append(f"bsr {tg[0]['rank']}->{r['rank']}")
                tg[0]['rank'] = r['rank']
        else:
            bsr.insert(0, {'rank': r['rank'], 'cat': 'Toys & Games'})
            p['bsr'] = bsr
            ch.append(f"bsr +{r['rank']}")
        if ch:
            upd += 1
            log(f'  ~ {r["asin"]}  {"; ".join(ch)}')
    log(f'{upd} urun guncellendi')

    # --- 2) yeni urunleri ekle
    added = skipped = 0
    for r in listing:
        if r['asin'] in index:
            continue
        if not r['rating'] or r['rating'] < MIN_RATING or not r['rc'] or r['rc'] < MIN_REVIEWS:
            log(f'  - {r["asin"]} atlandi (kalite: {r["rating"]}* / {r["rc"]} yorum)')
            skipped += 1
            continue

        prod = fetch_product(r['asin'])
        time.sleep(DELAY)
        if not prod or not prod['name']:
            log(f'  ! {r["asin"]} urun sayfasi okunamadi, atlandi')
            skipped += 1
            continue
        if prod['rating'] and prod['rating'] < MIN_RATING:
            log(f'  - {r["asin"]} atlandi (urun sayfasi puani {prod["rating"]}*)')
            skipped += 1
            continue

        dup = is_variant(prod['name'], d)
        if dup:
            log(f'  - {r["asin"]} atlandi (varyant: katalogdaki {dup} ile ayni urun)')
            skipped += 1
            continue

        cat = pick_category(prod)
        if not cat or cat not in d:
            log(f'  ? {r["asin"]} kategori belirlenemedi — ELLE BAKILACAK: '
                f'{prod["name"][:60]!r} bsr={[x["cat"] for x in prod["bsr"][:3]]}')
            skipped += 1
            continue

        gallery = download_images(r['asin'], prod['images'])
        if not gallery:
            log(f'  ! {r["asin"]} gorsel indirilemedi, atlandi')
            skipped += 1
            continue

        d[cat].append({
            'asin': r['asin'], 'name': prod['name'], 'img': gallery[0],
            'url': f'https://www.amazon.com/dp/{r["asin"]}?tag=kolico-20',
            'rc': prod['rc'] or r['rc'], 'rating': prod['rating'] or r['rating'],
            'bsr': prod['bsr'] or [{'rank': r['rank'], 'cat': 'Toys & Games'}],
            'gallery': gallery, 'bullets': prod['bullets'],
            'price': prod['price'] or r['price'], 'lo': prod['lo'],
        })
        added += 1
        log(f'  + {r["asin"]} [{cat}] {prod["rating"]}* gorsel={len(gallery)} '
            f'{prod["name"][:52]}')

    save_catalog(d)
    total = sum(len(v) for v in d.values())
    log(f'{added} urun eklendi, {skipped} atlandi. Katalog toplam: {total}')

    if added:
        n = write_sitemap(d)
        log(f'sitemap-products.xml yeniden uretildi: {n} URL')

    # browse.html'i HER turda yeniden uret — fiyat/puan degistiyse orada da guncellensin.
    # Bu sayfa Google'in urun sayfalarina ulasabildigi TEK ic link zinciri (29 Tem 2026).
    try:
        import build_browse_page
        links = build_browse_page.main()
        log(f'browse.html yeniden uretildi: {links} gercek urun linki')
    except Exception as e:
        log(f'UYARI: browse.html uretilemedi ({type(e).__name__}: {e}) — '
            f'elle: python3 products/build_browse_page.py')

    log('bitti. NOT: deploy YAPILMADI — canliya cikmasi icin push gerekiyor.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:  # nolint
        log(f'BEKLENMEYEN HATA: {type(e).__name__}: {e}')
        log('Katalog yedegi products/ dizinindeki .bak dosyalarindan geri alinabilir.')
        sys.exit(1)
