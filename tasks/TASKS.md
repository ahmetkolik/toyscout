# ToyScout — Görev ve Hatırlatma Kaydı

**Bu dosya tek doğruluk kaynağıdır.** Tüm tekrarlayan görevler, hatırlatmalar ve
açık işler burada. Oturum içi zamanlanmış işler (cron) Claude kapanınca siliniyordu;
bu yüzden her şey ya `launchd` ajanına ya da bu dosyaya bağlandı.

**Durumu doğrulamak için:** `bash tasks/verify.sh`

Son güncelleme: 30 Tem 2026

---

## A0. ✅ TCC ARIZASI GİDERİLDİ (30 Tem 2026)

Proje `~/Downloads/toyscout-master` → **`~/Projects/toyscout`** taşındı.
`~/Downloads` macOS TCC korumasındaydı ve launchd ajanları oradaki dosyaları
açamıyordu (`Operation not permitted`). `~/Projects` korumasız.

**Doğrulandı — sadece "yüklendi" demedim, gerçekten çalıştırdım:**
`launchctl kickstart -k` ile tetiklendi → **exit 0, stderr boş**, tur tamamlandı
(49 ürün güncellendi, 2 ürün eklendi, sitemap + browse.html yeniden üretildi).

**Taşımada güncellenenler:** `net.toyscout.bestsellers.plist` (4 yol),
`tasks/TASKS.md`, Claude Code hafıza dizini
(`~/.claude/projects/-Users-ahmet-Projects-toyscout/memory/` — 14 dosya kopyalandı).
Script'ler `__file__` tabanlı göreli yol kullandığı için kod değişikliği gerekmedi.

**Eski `~/.claude/projects/-Users-ahmet-Downloads-toyscout-master/` dizini artık
okunmuyor** — silinebilir, karışıklık yaratmasın.

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

## B0. ⭐ SIRADAKİ İŞ — 31 Tem 2026 GSC turu

**30 Tem turunda ne oldu:**
- ✅ **`/sitemap.xml` OKUNDU** — Last read 26 Tem → **30 Tem, Success, 124 sayfa**
  (dün 25'ti). Dün "sitemap hiç okunmuyor" teşhisi artık geçerli değil.
- ✅ **Yeni kök sorun bulundu ve çözüldü:** `sitemap.xml` yalnızca ESKİ 97 ürünü
  içeriyordu; 29 Tem'de eklenen 18 ürün + `/shop/dolls` sadece
  `sitemap-products.xml`'deydi — yani Google'ın ÇEKEMEDİĞİ dosyada. Google'ın okuduğu
  dosyada bu sayfalar yoktu. `products/build_sitemap.py` yazıldı, `sitemap.xml` artık
  **143 URL** (16 statik + 12 kategori + 115 ürün). Deploy `96c3b881`, canlı doğrulandı.
  `bestseller_sync.py` her turda otomatik yeniden üretiyor.
- ✅ `sitemap.xml` GSC'ye yeniden gönderildi (Submitted 30 Tem).
- ❌ **Kalan 5 indeksleme isteği GÖNDERİLEMEDİ** — URL Inspection kutusu girdi kabul
  etmemeye başladı (eklenti/renderer kararsızdı, 3 deneme). Aşağıda duruyorlar.
- ℹ️ İndeksleme sayıları hâlâ 4 indeksli / 40 değil — bu rapor günlerce gecikmeli.
  Ama Product snippets **56**, Merchant listings **51**, Review snippets **166** geçerli
  öğe görüyor; bu, Google'ın 4 sayfadan çok daha fazlasını taradığına işaret.

**31 Tem'de bakılacaklar:**
1. `/sitemap.xml` Discovered sayısı **124 → 143**'e çıktı mı? (yeni sürüm okundu mu)
2. `/product/arts-crafts/23` gibi YENİ bir ürün sayfası artık
   "No referring sitemaps detected" demiyor mu? **En net sinyal bu.**
3. İndeksli sayfa sayısı 4'ten hareket etti mi?
4. `/browse.html` indekslendi mi?

**Kalan 5 indeksleme isteği** (29 Tem'de hız sınırı, 30 Tem'de eklenti arızası):
```
https://www.toyscout.net/product/arts-crafts/23     Play-Doh 42'li   (4.9★ 17.343)
https://www.toyscout.net/product/ride-ons/4          SEREED bisiklet  (4.8★ 16.217)
https://www.toyscout.net/product/arts-crafts/22      Crayola 24'lü    (4.8★  7.510)
https://www.toyscout.net/product/arts-crafts/20      Prang karton     (4.7★  6.892)
https://www.toyscout.net/product/baby-toddler/9      LiKee fırıldak   (4.8★  5.210)
```

**2. `/browse.html` indekslendi mi?** (29 Tem 22:0x'te istek gönderildi, onaylandı)

**3. EN NET SİNYAL — bir ürün sayfasında "Referring page" değişti mi?**
Herhangi bir `/product/...` URL'ini denetle. "None detected" yerine `/browse.html`
görünüyorsa iç link zinciri çalışmaya başlamış demektir.

**4. `/sitemap-products.xml` "Success" oldu mu?** (29 Tem 21:0x'te yeniden gönderildi)
`/sitemap.xml` Last read tarihi 26 Tem'den ileri gitti mi?

**Akış kuralları (kanla öğrenildi):** Her istekten sonra Overview'a dön ve kutuya
**iki kez** tıkla (navigate sonrası ilk yazma yutuluyor). Yenilemeden arka arkaya
istek atarsan hız sınırı devreye girer. Onay için modal'a güvenme — satırdaki kalıcı
**"✓ Indexing requested"** yazısına bak.

---

## A3. Pinterest — periyodik kontrol + SEO optimizasyonu (kullanıcı isteği, 30 Tem 2026)

Hesap: **`toyscoutnet`** · 11 pano · **108 pin** · katalog **117 ürün**

**⛔ ŞU AN BLOKE — Pinterest MCP token'ı yetkisini kaybetmiş.** `boards_list` çalışıyor,
ama `pins_list`, `user_get_info` ve `pins_create` **401** dönüyor. Pin okunamıyor,
oluşturulamıyor, düzenlenemiyor. **İlk iş: Pinterest bağlantısını yeniden yetkilendir.**
O yapılmadan aşağıdaki hiçbir madde uygulanamaz.

### Boşluk analizi (30 Tem — pano pin sayıları ↔ katalog)

| Pano | Ürün | Pin | Fark |
|---|---:|---:|---:|
| Arts & Crafts for Kids | 26 | 19 | **−7** |
| Baby & Toddler Toys | 12 | 10 | −2 |
| Action Figures | 4 | 3 | −1 |
| Games | 12 | 11 | −1 |
| **Dolls & Accessories** | 1 | 0 | −1 · **PANO HİÇ YOK** |
| Building Toys / Learning / Novelty | — | — | +1 (blog pinleri, normal) |
| Party · Plush · Ride-ons · Sports | — | — | 0 (tam) |

### Yapılacaklar (token yenilenince, öncelik sırasıyla)

**1. ⚠️ Eski pinlerin linklerini düzelt — EN YÜKSEK ETKİLİ.**
Mevcut ürün pinleri **hash'li link** kullanıyor (`/#...`), bu yüzden ne trafik ne SEO
değeri üretiyorlar. Artık gerçek URL'ler var:
`https://www.toyscout.net/product/<kategori>/<idx>`. Düzeltilirse hem tıklama siteye
gelir hem de **harici link sinyali** oluşur — [[spa-taranabilirlik-sorunu]] göz önüne
alınırsa siteye dışarıdan gelen ilk gerçek linkler bunlar olacak.

**2. Rich Pins'i etkinleştir.** Domain zaten Pinterest'te doğrulanmış
(`p:domain_verify` meta etiketi `index.html`'de duruyor, silinmemeli). Ürün sayfalarında
zaten `Product` yapılandırılmış verisi var → **Product Rich Pins** açılabilir; fiyat ve
stok bilgisi pinde otomatik görünür, tıklama oranını belirgin artırır. Tek seferlik iş.

**3. Görsel oranı — sessiz ama büyük kayıp.** Pinterest **2:3 dikey** (1000×1500)
görselleri belirgin şekilde öne çıkarıyor; bizim ürün fotoğrafları Amazon'dan geldiği
için **kare**. Kare görseller akışta eziliyor. Çözüm: `assets/products/<ASIN>.jpg`'den
2:3 dikey pin görseli üreten bir script (ürün fotoğrafı üstte, altta ürün adı + fiyat +
puan şeridi, ToyScout logosu). `products/build_browse_page.py` ile aynı mantıkta
otomatikleştirilebilir.

**4. Başlık/açıklama SEO şablonu** (yeni ve düzeltilen tüm pinlerde):
- **Başlık:** birincil anahtar kelime **başta**, ~40 karakterde anlam tamamlanmalı.
  `SKYJO — The Card Game With 75,000 Five-Star Reviews`
- **Açıklama:** ilk 100 karakter kritik (akışta görünen kısım). Doğal cümle içinde
  anahtar kelime, sonra fiyat/puan, sonra eylem çağrısı. 200-400 karakter ideal.
- **Hashtag:** 3-5 tane, sona. Pinterest hashtag ağırlığını düşürdü — **anahtar kelimeli
  açıklama hashtag'den çok daha değerli**, abartma.
- **`alt_text`:** görseli betimle (erişilebilirlik + indeksleme).
- **Pano açıklamaları** da anahtar kelimeli olmalı; şu an bazıları boş
  (Action Figures, Arts & Crafts panolarının açıklaması yok).

**5. Eksik ~12 pini tamamla** + `Dolls & Accessories` panosunu oluştur.

**6. Tazelik.** Pinterest yeni pini ödüllendiriyor. Toplu 100 pin atmak yerine
**5 günde bir birkaç yeni pin** daha iyi çalışır — Best Sellers senkronizasyonuyla aynı
ritim, katalog büyüdükçe yeni ürünler pinlenir.

**Periyot:** 5 günde bir, A1 turuyla birlikte kontrol et.

---

## B. Açık işler (tarihli, bitince buradan sil)

- [x] **29 Tem 22:1x — İLK OLUMLU SİNYAL: `/product/games/11` INDEKSLENDİ.**
      Aynı akşam saat başında "URL is unknown to Google" diyen sayfa, istek
      gönderildikten ~45 dakika sonra **"URL is on Google · Page is indexed"** oldu;
      Product snippets 5 geçerli öğe görüyor. **Anlamı:** Google bu SPA'nın ürün
      sayfalarını render edip indeksleyebiliyor — sorun render değil, sayfaya
      ULAŞAMAMASIYDI. `browse.html` yaklaşımının doğru olduğunun ilk kanıtı.
- [ ] **`/browse.html` takibi — 30 Tem'den itibaren (EN ÖNEMLİ ÖLÇÜT).**
      29 Tem 22:0x'te indeksleme isteğine gönderildi ("Indexing requested" onaylı).
      Taranınca Google 115 ürün + 12 kategori linkini tek seferde görecek.
      **Bakılacak iki sinyal:** (1) `/browse.html` indekslendi mi, (2) rastgele bir ürün
      sayfasında "Referring page" artık "None detected" yerine `/browse.html` gösteriyor mu.
      İkincisi daha erken ve daha net sinyal. Bkz. `spa-taranabilirlik-sorunu` hafızası.
- [ ] **İndeksleme turu — devam, 30 Tem.** 29 Tem akşamı **5 istek gönderildi**
      (`/browse.html`, `/product/games/10`, `/product/baby-toddler/11`, `/shop/dolls`,
      `/product/sports-outdoor/16`). Arada bir kez hız sınırına takıldı
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
