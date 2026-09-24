import sys, os, glob, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import bestseller_sync as b
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res')
d = b.load_catalog()
have = {p['asin'] for v in d.values() for p in v}
b.backup()
added = skip = 0
stats = {}
for f in sorted(glob.glob(RES + '/*.json')):
    r = json.load(open(f))
    a = r['asin']
    if a in have or a == 'TEST':
        continue
    m = r.get('meta') or {}
    cat = m.get('cat')
    if not cat or not r.get('name'):
        skip += 1; continue
    rating = r.get('rating') or m.get('lrating'); rc = r.get('rc') or m.get('lrc')
    if not rating or rating < b.MIN_RATING or not rc or rc < b.MIN_REVIEWS:
        skip += 1; stats['kalite'] = stats.get('kalite', 0) + 1; continue
    if not r.get('price'):
        skip += 1; stats['fiyat yok'] = stats.get('fiyat yok', 0) + 1; continue
    if b.is_variant(r['name'], d):
        skip += 1; stats['varyant'] = stats.get('varyant', 0) + 1; continue
    gal = b.download_images(a, r.get('images') or [])
    if not gal:
        skip += 1; stats['gorsel'] = stats.get('gorsel', 0) + 1; continue
    price = float(r['price'])
    d.setdefault(cat, []).append({
        'asin': a, 'name': r['name'], 'img': gal[0],
        'url': f'https://www.amazon.com/dp/{a}?tag=kolico-20',
        'rc': rc, 'rating': rating,
        'bsr': r.get('bsr') or [{'rank': m.get('rank', 0), 'cat': m.get('sub', 'Toys & Games')}],
        'gallery': gal, 'bullets': r.get('bullets') or [],
        'price': f'${price:.2f}', 'lo': price})
    have.add(a); added += 1
b.save_catalog(d)
print('eklendi', added, 'atlandi', skip, stats, 'toplam', sum(len(v) for v in d.values()))
