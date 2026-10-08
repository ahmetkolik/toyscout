#!/usr/bin/env python3
"""js/data.js'i sayfanin yukledigi hafif dosyalara boler.

js/data.js tek dogru kaynak olarak kalir (tum sync/prerender betikleri onu okur/yazar).
Bu betik ondan sunlari uretir:
  js/catalog.js            window.TS_DATA = liste alanlari (detay alanlari haric) +
                           window.TS_DETAIL_V = {kategori: detay dosyasi hash'i}
  js/detail/<kategori>.json  urun sirasiyla hizali dizi: {gallery, bullets, reviews}
                           — sadece o kategoride bir urun sayfasi acilinca yuklenir.
Neden: detay alanlari data.js'in ~%85'i; her ilk ziyarette 2.9 MB (950 KB gzip) inmesin.
Dogrudan calistirmaya gerek yok: stamp_data_version.py bunu cagirir.
"""
import hashlib, json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DETAIL_KEYS = ('gallery', 'bullets', 'reviews')

# CLAUDE.md kurali: sitede hicbir yerde fiyat gosterilmez. Amazon ilan maddeleri ("SAVE UP TO $70",
# "$7.99/month") ve musteri yorumlari ("got it for $12") da fiyat tasiyabiliyor; bunlar sayfaya gitmez
# (data.js'te kalir). "$1 bills" gibi oyuncak para birimleri fiyat degildir, haric tutulur.
PRICE_RE = re.compile(r'\$\s?\d[\d,]*(?:\.\d+)?(?!\s*(?:bills?|BILLS?|coins?)\b)|\d+\s?\u00a2')


def has_price(text):
    return bool(PRICE_RE.search(text or ''))


def clean_detail(p):
    """Sayfaya gidecek detay alanlari — fiyat iceren madde/yorumlar ayiklanmis."""
    out = {}
    if p.get('gallery'):
        out['gallery'] = p['gallery']
    b = [x for x in (p.get('bullets') or []) if not has_price(x)]
    if b:
        out['bullets'] = b
    r = [x for x in (p.get('reviews') or []) if not has_price(x.get('title')) and not has_price(x.get('body'))]
    if r:
        out['reviews'] = r
    return out


def dump(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')


def main():
    raw = open(os.path.join(ROOT, 'js', 'data.js'), encoding='utf-8').read()
    src = hashlib.md5(raw.encode('utf-8')).hexdigest()[:8]
    data = json.loads(raw[raw.index('{'):raw.rindex('}') + 1])
    ddir = os.path.join(ROOT, 'js', 'detail')
    shutil.rmtree(ddir, ignore_errors=True)
    os.makedirs(ddir)
    light, ver = {}, {}
    for cat, items in data.items():
        light[cat], det = [], []
        for i, p in enumerate(items):
            # price/lo sayfaya hic gitmez (CLAUDE.md kurali: sitede fiyat gosterilmez).
            lp = {k: v for k, v in p.items() if k not in DETAIL_KEYS and k not in ('price', 'lo')}
            # Ana sayfadaki "top picks" kartlari her kategorinin 0. urununun ilk maddesini gosterir.
            cd = clean_detail(p)
            if i == 0 and cd.get('bullets'):
                lp['sd'] = cd['bullets'][0][:200]
            light[cat].append(lp)
            det.append(cd)
        body = dump(det)
        open(os.path.join(ddir, cat + '.json'), 'w', encoding='utf-8').write(body)
        ver[cat] = hashlib.md5(body.encode('utf-8')).hexdigest()[:8]
    # TS_SRC: hangi data.js'ten uretildigi (.claude/hooks/data-js-reminder.sh bayatligi buna bakar)
    # TS_INDEXABLE: product paths allowed in Google's index (seo_index.py); updateSeo() sets
    # noindex,follow on every other product page, matching prerender.py and sitemap.xml.
    import seo_index
    idx = seo_index.indexable_products(data)
    out = ('window.TS_SRC="' + src + '";window.TS_DATA=' + dump(light) + ';window.TS_DETAIL_V=' + dump(ver)
           + ';window.TS_INDEXABLE=' + dump(idx) + ';\n')
    open(os.path.join(ROOT, 'js', 'catalog.js'), 'w', encoding='utf-8').write(out)
    print(f'catalog.js {len(out.encode()) // 1024} KB, {len(ver)} detay dosyasi')


if __name__ == '__main__':
    main()
