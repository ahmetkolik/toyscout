# Ürün Yönetimi

Sitedeki ürünler bu klasörden yönetilir. Her kategori klasörü sitedeki bir
kategoriye karşılık gelir.

## Ürün ekleme

1. İlgili kategori klasöründeki `links.txt` dosyasını aç
   (ör. `products/building-toys/links.txt`).
2. Her satıra bir Amazon ürün linki yapıştır:

   ```
   https://www.amazon.com/dp/B01N9Y1H0X
   ```

   İstersen yaş grubu ve rozet ekleyebilirsin:

   ```
   https://www.amazon.com/dp/B01N9Y1H0X | age=3-5 | badge=TRENDING NOW
   ```

   Yaş seçenekleri: `0-2`, `3-5`, `6-8`, `9-12`, `Teen+`

3. Terminalde çalıştır:

   ```bash
   python3 products/fetch_products.py
   ```

   Script her link için Amazon'dan ürün adını, fiyatını, puan/değerlendirme
   sayısını, açıklama maddelerini ve ürün fotoğrafını çeker; fotoğrafı
   `assets/products/` altına indirir ve siteyi (`ToyScout Home.dc.html`)
   otomatik günceller.

## Ürün çıkarma

`links.txt` içindeki satırı sil (veya başına `#` koy) ve scripti tekrar
çalıştır. Ürün siteden kalkar.

## Notlar

- Çekilen veriler `products/.cache/` altında saklanır; aynı ürün ikinci kez
  Amazon'dan indirilmez. Fiyat/puan bilgilerini tazelemek için:
  `python3 products/fetch_products.py --refresh`
- Amazon Associates etiketini (`tag`) `fetch_products.py` dosyasının başındaki
  `AFFILIATE_TAG` değişkenine yaz (ör. `"toyscout-20"`) — tüm linklere
  otomatik eklenir.
- Amazon bazen otomatik istekleri engeller (captcha). Bir ürün çekilemezse
  script uyarı verir; birkaç dakika sonra tekrar çalıştırmak genelde yeterlidir.
- Link eklenmemiş kategoriler sitede örnek (placeholder) ürünleri göstermeye
  devam eder.
