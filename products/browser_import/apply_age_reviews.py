#!/usr/bin/env python3
"""Tarayicidan cekilen (extract_age_reviews.js) sonuclari katalogda gunceller:
  - age      : Amazon 'Manufacturer recommended age' -> 0–2 / 3–5 / 6–8 / 9–12 / Teen+ (yoksa alan EKLENMEZ)
  - reviews  : 4-5 yildizli en fazla 3 yorum (yalnizca zaten yorumu olmayan urunlere; elle kuratorlu olanlara dokunmaz)
  - price/lo/rating/rc : sayfadan okunabildiyse guncellenir

Kullanim: python3 products/browser_import/apply_age_reviews.py <res_klasoru> [--dry]
"""
import glob, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import bestseller_sync as b

def bracket(months):
    if months is None: return None
    if months < 36: return '0–2'
    if months < 72: return '3–5'
    if months < 108: return '6–8'
    if months < 156: return '9–12'
    return 'Teen+'

def clean(t):
    t = re.sub(r'\s+', ' ', t or '').strip()
    t = re.sub(r'(Read more|Read less)\s*$', '', t).strip()
    return t

def main():
    res = sys.argv[1]; dry = '--dry' in sys.argv
    d = b.load_catalog()
    idx = {p['asin']: p for v in d.values() for p in v}
    st = dict(files=0, age=0, noage=0, rev=0, price=0, rating=0, rc=0, capt=0)
    for f in glob.glob(res + '/*.json'):
        r = json.load(open(f)); st['files'] += 1
        p = idx.get(r['asin'])
        if not p: continue
        a = bracket(r.get('ageMonths'))
        if a: p['age'] = a; st['age'] += 1
        else: st['noage'] += 1
        if not p.get('reviews') and r.get('reviews'):
            revs = []
            for v in r['reviews'][:3]:
                body = clean(v.get('body'))
                if len(body) < 40: continue
                revs.append({'name': clean(v.get('name')) or 'Amazon customer', 'stars': int(round(v.get('stars') or 5)),
                             'title': clean(v.get('title')), 'date': clean(v.get('date')), 'body': body,
                             'verified': bool(v.get('verified'))})
            if revs: p['reviews'] = revs; st['rev'] += 1
        if r.get('price'):
            pr = float(r['price'])
            if pr > 0 and abs(pr - (p.get('lo') or 0)) > 0.001:
                p['price'] = f'${pr:.2f}'; p['lo'] = pr; st['price'] += 1
        if r.get('rating') and r['rating'] != p.get('rating'): p['rating'] = r['rating']; st['rating'] += 1
        if r.get('rc') and r['rc'] != p.get('rc'): p['rc'] = r['rc']; st['rc'] += 1
    print(st, 'toplam urun', len(idx))
    if dry: print('(dry — katalog degismedi)'); return
    b.backup(); b.save_catalog(d)
if __name__ == '__main__':
    main()
