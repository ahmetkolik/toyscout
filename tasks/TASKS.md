# ToyScout — Görev ve Hatırlatma Kaydı

**Bu dosya tek doğruluk kaynağıdır.** Tüm tekrarlayan görevler, hatırlatmalar ve
açık işler burada. Oturum içi zamanlanmış işler (cron) Claude kapanınca siliniyordu;
bu yüzden her şey ya `launchd` ajanına ya da bu dosyaya bağlandı.

**Durumu doğrulamak için:** `bash tasks/verify.sh`

Son güncelleme: 29 Tem 2026

---

## A. Tekrarlayan görevler (launchd — makinede kalıcı)

### A1. Amazon Best Sellers senkronizasyonu — TAM OTOMATİK

| | |
|---|---|
| Ajan | `net.toyscout.bestsellers` |
| Plist | `~/Library/LaunchAgents/net.toyscout.bestsellers.plist` |
| Script | `products/bestseller_sync.py` |
| Sıklık | 5 günde bir (`StartInterval` 432000 sn) |
| İlk tur | 29 Tem 2026 (elle) → sonraki ~3 Ağu 2026 |
| Log | `products/bestseller_sync.log` |
| Durdur | `launchctl unload ~/Library/LaunchAgents/net.toyscout.bestsellers.plist` |
| Elle çalıştır | `python3 products/bestseller_sync.py` |

Yaptığı: `js/data.js` yedeği → Best Sellers listesi → mevcut ürünlerde
fiyat/puan/yorum/BSR güncelle → yeni ürünleri 6 görselle ekle →
`sitemap-products.xml` yeniden üret.

**DEPLOY ETMEZ.** Değişiklikler yereldedir; canlıya çıkması için ayrıca push gerekir.
Bu bilinçli: Amazon bozuk fiyat döndürdüğünde gözden geçirilmeden yayına girmesin.
Yani her turdan sonra sonucu gözden geçirip deploy etmek gerekir.

Kalite kuralları (kullanıcı kararı, 29 Tem 2026):
- Yalnızca **4.4★ ve üzeri**, en az 50 yorumu olan ürünler eklenir.
- Puanı/yorumu olmayan yeni listelemeler eklenmez.
- **Varyant tuzağı:** başlığı katalogdaki bir ürüne %90+ benzeyen ASIN eklenmez
  (aynı ürünün renk/boy varyantı listede ayrı görünebiliyor).
- Kategorisi güvenle belirlenemeyen ürün eklenmez, log'a "ELLE BAKILACAK" yazılır.

### A2. Günlük GSC turu — SADECE HATIRLATICI

| | |
|---|---|
| Ajan | `net.toyscout.gsc` |
| Plist | `~/Library/LaunchAgents/net.toyscout.gsc.plist` |
| Script | `products/gsc_reminder.sh` |
| Sıklık | Her gün **22:15** |
| Log | `products/gsc_reminder.log` |
| Durdur | `launchctl unload ~/Library/LaunchAgents/net.toyscout.gsc.plist` |

**Bu iş otomatikleştirilemez.** Search Console'da "Request indexing" akışı Google
oturumu açık bir tarayıcı gerektiriyor, API'siz script'le yapılamıyor. Ajan yalnızca
macOS bildirimi gönderir; turu Claude Code ile elle yaparsın.

**22:15 rastgele değil:** indeksleme kotası takvim günü değil **24 saat kayan
pencere**. 28 Tem 22:00'de kullanılan kota 29 Tem 09:30'da hâlâ doluydu ve o gün
tek istek gönderilemedi. Her gün aynı saatte tur yapılırsa pencere tam kapanır.

Tur içeriği: GSC → Pages sayıları · Sitemaps durumu · Product/Review snippets ·
Manual actions · Core Web Vitals · **~10 URL indeksleme isteği** (kota dolunca dur).
Öncelik: hiç taranmamış yeni ürün/kategori sayfaları → blog.

---

## B. Açık işler (tarihli, bitince buradan sil)

- [ ] **İndeksleme turu — devam, 30 Tem.** 29 Tem 21:00'de **4 istek gönderildi**
      (`/product/games/10`, `/product/baby-toddler/11`, `/shop/dolls`,
      `/product/sports-outdoor/16`). 5.'de hız sınırına takıldı
      ("We had a problem submitting your indexing request"). Kalan hedefler sırayla:
      `/product/games/11` · `/product/arts-crafts/23` · `/product/ride-ons/4` ·
      `/product/arts-crafts/22` · `/product/arts-crafts/20` · `/product/baby-toddler/9`
- [ ] **`sitemap-products.xml` doğrulaması — 30 Tem.** 29 Tem 21:00'de **yeniden
      gönderildi** (önceki durum "Couldn't fetch", 0 keşif). Dosyada teknik sorun YOK:
      HTTP 200, `application/xml`, geçerli XML, robots.txt'de listeli, 115 URL.
      Yarın "Success" ve Discovered > 0 olmalı.
- [ ] **ASIL KÖK SORUN (29 Tem araştırması): ürün sayfalarına taranabilir link YOK.**
      Sunucudan gelen ham HTML'de `<a href="/product/...">` sayısı **sıfır** (115 ürünün
      hiçbirine). Kategori linki yalnızca 7 adet ve hepsi aynı yere
      (`/shop/sports-outdoor`). `#view` kapsayıcısı **boş** geliyor; tüm gezinme ve içerik
      JS ile istemcide üretiliyor. `<noscript>` ise tam ekran "ToyScout requires
      JavaScript" uyarısı gösteriyor.
      **Sonuç:** Google'ın iki keşif yolu da kapalı — sitemap okunmuyor VE iç link yok.
      URL Inspection'ın her sayfada "Referring page: None detected" +
      "URL is unknown to Google" demesinin sebebi bu.
      Google JS render edebilir ama render ayrı ve gecikmeli bir kuyruk; otoritesi
      sıfıra yakın bir sitede pratikte sıraya hiç gelmiyor.
      **Önerilen çözüm:** ham HTML'e gerçek `<a href>` linkleri koymak — örn. script'le
      üretilen statik "tüm ürünler" sayfası + footer'dan gerçek linkle bağlamak.
      Build step gerektirmez, mevcut mimariye uyar. Kullanıcı onayı bekliyor.
- [ ] **Sitemap hiç okunmuyor (ikincil).** URL Inspection her sayfada
      **"No referring sitemaps detected"** ve **"URL is unknown to Google"** diyor;
      `/sitemap.xml` Last read hâlâ **26 Tem** (3 gün önce), yalnızca 25 sayfa keşfedilmiş.
      Yani sayfalar tek tek elle isteniyor, sitemap üzerinden toplu keşif çalışmıyor.
      30 Tem'de hâlâ okunmadıysa asıl mesele bu — elle istek bunu telafi edemez.
- [ ] **VALIDATE FIX sonucu** — Merchant listings `Missing field "price"` doğrulaması
      *Started* durumda, birkaç gün sürer.
- [ ] **09-A videosu (SEREED denge bisikleti)** — kampanyada hiç üretilmemiş tek slot.
      Ürün 29 Tem'de siteye eklendi (`B08SGH7NKX`), artık kendi sayfası var.
- [ ] **04-A format hatası** — Candy Land videosu (`dnkiQr9BkHI`) hâlâ 3:31 uzun
      format, Shorts değil. 5 denetimdir duruyor.
- [ ] **11-A…15-B videoları** — 2-6 Ağu 2026 için 10 içerik planı Google Sheet'te
      hazır (`PLANLANDI`). Videolar Amazon ürün videosundan CapCut ile hazırlanacak.

---

## C. Bilinçli yapılmayanlar (tekrar gündeme gelirse)

- **GSC `hasMerchantReturnPolicy` / `shippingDetails` uyarıları** (44'er öğe) kasıtlı
  açık bırakıldı — ToyScout satıcı değil affiliate; Amazon'un iade/kargo şartlarını
  kendi yapılandırılmış verisinde beyan etmesi yanlış bilgi olur.
- **Best Sellers 31-50 ve 81-100 aralığı** — Amazon liste sayfası başına yalnızca 30
  kart veriyor, bu 40 ürün HTML'e hiç gelmiyor. 29 Tem'de 20 alt kategori taranarak
  elle tamamlandı (12 ürün bulundu, 5'i eklendi). Otomatik script bu aralığı
  taramıyor; gerekirse `find_gaps` yaklaşımı tekrarlanır.

---

## D. Ortam notları (aynı duvara iki kez çarpmamak için)

- **Bu klasör bir git deposu değil.** Deploy GitHub Git Data API ile yapılır
  (`gh api` üzerinden): `git/ref` → `git/commits` → `git/blobs` → `git/trees`
  (`base_tree` ile) → `git/commits` → `PATCH git/refs/heads/master`.
- **Klonlama çalışmaz.** `frames/` yüzünden `git clone` timeout oluyor;
  `--depth 1 --filter=blob:none` kısmi klon bile 7 dakikada bitmedi (29 Tem).
- **Python HTTPS isteği atamıyor** — bu makinedeki Python'da CA sertifikaları eksik
  (`CERTIFICATE_VERIFY_FAILED`). GitHub API çağrılarını `gh api` üzerinden yap.
- **Amazon `curl` ile açılıyor** — normal masaüstü User-Agent +
  `Accept-Language: en-US` yeterli, captcha yok. Tarayıcı scrape'ine gerek yok.
- **Deploy sonrası doğrulama** Vercel edge cache yüzünden `?cb=$RANDOM` ile yapılmalı.
- `tasks/` ve `notes/` `.vercelignore`'da — GitHub'da duruyor, canlı sitede 404.
