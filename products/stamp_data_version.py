#!/usr/bin/env python3
"""js/data.js'ten js/catalog.js + js/detail/*.json uretir (split_data.py) ve
index.html ile pre-render sayfalarindaki <script src="/js/catalog.js?v=..."> surumunu
catalog.js'in icerik hash'ine gunceller.

Neden: vercel.json, ?v= parametresi OLAN /js/catalog.js ve /js/detail/* istekleri icin 1 yillik
`immutable` onbellek verir. Katalog her degistiginde (subcat_sync, bestseller_sync, elle duzenleme)
bu betik calistirilmali, yoksa ziyaretciler eski katalogu gorur. Kullanim: python3 products/stamp_data_version.py
"""
import glob, hashlib, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import split_data

# Eski (data.js) ve yeni (catalog.js) etiketi eslesir, boylece ilk calistirma gecisi de yapar.
TAG = re.compile(r'<script src="/js/(?:data|catalog)\.js(?:\?v=[0-9a-f]+)?"></script>')


def main():
    split_data.main()
    v = hashlib.md5(open(os.path.join(ROOT, 'js', 'catalog.js'), 'rb').read()).hexdigest()[:8]
    tag = f'<script src="/js/catalog.js?v={v}"></script>'
    p = os.path.join(ROOT, 'index.html')
    s = open(p, encoding='utf-8').read()
    n, k = TAG.subn(tag, s)
    if k != 1:
        raise SystemExit(f'katalog script etiketi bulunamadi/birden fazla ({k}) — index.html degismedi')
    open(p, 'w', encoding='utf-8').write(n)
    # prerender.py index.html'i kopyalar; hangi sirayla calistirilirsa calistirilsin surum ayni kalsin.
    pages = (glob.glob(os.path.join(ROOT, 'product', '*', '*', 'index.html')) + glob.glob(os.path.join(ROOT, 'shop', '*', 'index.html'))
             + [os.path.join(ROOT, d, 'index.html') for d in ('blog', 'contact', 'privacy', 'terms', 'disclosure')
                if os.path.exists(os.path.join(ROOT, d, 'index.html'))]
             + [f for f in [os.path.join(ROOT, '404.html')] if os.path.exists(f)])
    for f in pages:
        s = open(f, encoding='utf-8').read()
        n = TAG.sub(tag, s, count=1)
        if n != s:
            open(f, 'w', encoding='utf-8').write(n)
    print('catalog.js surumu:', v, f'({len(pages)} pre-render sayfasi)')
    return v


if __name__ == '__main__':
    main()
