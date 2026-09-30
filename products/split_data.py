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
import hashlib, json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DETAIL_KEYS = ('gallery', 'bullets', 'reviews')


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
            lp = {k: v for k, v in p.items() if k not in DETAIL_KEYS}
            # Ana sayfadaki "top picks" kartlari her kategorinin 0. urununun ilk maddesini gosterir.
            if i == 0 and p.get('bullets'):
                lp['sd'] = p['bullets'][0][:200]
            light[cat].append(lp)
            det.append({k: p[k] for k in DETAIL_KEYS if p.get(k)})
        body = dump(det)
        open(os.path.join(ddir, cat + '.json'), 'w', encoding='utf-8').write(body)
        ver[cat] = hashlib.md5(body.encode('utf-8')).hexdigest()[:8]
    # TS_SRC: hangi data.js'ten uretildigi (.claude/hooks/data-js-reminder.sh bayatligi buna bakar)
    out = 'window.TS_SRC="' + src + '";window.TS_DATA=' + dump(light) + ';window.TS_DETAIL_V=' + dump(ver) + ';\n'
    open(os.path.join(ROOT, 'js', 'catalog.js'), 'w', encoding='utf-8').write(out)
    print(f'catalog.js {len(out.encode()) // 1024} KB, {len(ver)} detay dosyasi')


if __name__ == '__main__':
    main()
