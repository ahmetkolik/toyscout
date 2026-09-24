#!/usr/bin/env python3
"""index.html'deki <script src="/js/data.js?v=..."> surumunu js/data.js'in icerik hash'ine gunceller.

Neden: vercel.json, ?v= parametresi OLAN /js/data.js istekleri icin 1 yillik `immutable` onbellek verir.
Katalog her degistiginde (subcat_sync, bestseller_sync, elle duzenleme) bu betik calistirilmali,
yoksa ziyaretciler eski katalogu gorur. Kullanim: python3 products/stamp_data_version.py
"""
import hashlib, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def main():
    v = hashlib.md5(open(os.path.join(ROOT, 'js', 'data.js'), 'rb').read()).hexdigest()[:8]
    p = os.path.join(ROOT, 'index.html')
    s = open(p, encoding='utf-8').read()
    n, k = re.subn(r'<script src="/js/data\.js(?:\?v=[0-9a-f]+)?"></script>', f'<script src="/js/data.js?v={v}"></script>', s)
    if k != 1:
        raise SystemExit(f'data.js script etiketi bulunamadi/birden fazla ({k}) — index.html degismedi')
    open(p, 'w', encoding='utf-8').write(n)
    print('data.js surumu:', v)
    return v
if __name__ == '__main__':
    main()
