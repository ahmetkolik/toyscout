# ToyScout — Görev ve Hatırlatma Kaydı

**Bu dosya tek doğruluk kaynağıdır.** Tüm tekrarlayan görevler, hatırlatmalar ve
açık işler burada. Oturum içi zamanlanmış işler (cron) Claude kapanınca siliniyordu;
bu yüzden her şey ya `launchd` ajanına ya da bu dosyaya bağlandı.

**Durumu doğrulamak için:** `bash tasks/verify.sh`

Son güncelleme: 31 Tem 2026 — GSC turu · A4 kapanışı · **Supabase analitik kesintisi
düzeltildi (A6)** · **blog kaldıraç verisi (A7)** · post10 yayında.
Deploy'lar: `26fb4f8` · `e1238bc` · `5f408b1` · `1c3f717`

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

### ⚠️ 31 Tem: `~/Downloads/toyscout-master` GERİ GELMİŞ

30 Tem 17:26'da klasörün yeni bir kopyası `~/Downloads`'a inmiş (dosya adı `-master`,
yani GitHub zip indirmesi). İçerik `diff -rq` ile **byte-byte aynı** — bayat değil, ama:
- launchd ajanı `WorkingDirectory=/Users/ahmet/Projects/toyscout`'a bakıyor,
- log'lar ve `js/data.js.bak-*` yedekleri orada,
- Claude Code hafızası ikiye ayrılmış durumda.

**Downloads kopyasında yapılan hiçbir düzenlemeyi otomasyon görmez.** Tek doğru klasör
`~/Projects/toyscout`. Downloads kopyası silinmeli. (Bir Claude oturumu 31 Tem'de
yanlışlıkla orada açıldı — tüm iş `~/Projects/toyscout`'a taşınarak yapıldı.)

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

## B0. ✅ 31 TEM GSC TURU YAPILDI — KEŞİF SORUNU ÇÖZÜLDÜ

**Bu, 28 Tem'den beri süren indeksleme krizinin kapanışıdır.**

| Sinyal | 30 Tem | 31 Tem | Sonuç |
|---|---|---|---|
| `/sitemap.xml` Discovered | 124 | **143** | ✅ yeni sürüm okundu |
| Ürün sayfası "Sitemaps" alanı | "No referring sitemaps detected" | **`/sitemap.xml`** | ✅ **ASIL SİNYAL** |
| Ürün sayfası durumu | "URL is unknown to Google" | **"Discovered – currently not indexed"** | ✅ Google artık biliyor |
| `/browse.html` | bilinmiyor | **29 Tem 15:10'da TARANDI** (Googlebot smartphone) | ✅ görevini yaptı |
| "Crawled – currently not indexed" | — | **0 sayfa** | ✅ |

**Teşhis değişti.** Artık sorun keşif değil: Google 37 sayfayı biliyor ("Discovered"),
ama taramaya öncelik vermiyor. Bu teknik bir kusur değil, **site otoritesi/değer sinyali**
meselesi. Elle indeksleme isteği bunu çözmez — günlük kota ~3-10 istek, katalog 117 sayfa.
**Bundan sonra kaldıraç: içerik (blog) + gerçek dış link, elle istek değil.**

**31 Tem'de gönderilen indeksleme istekleri:** `/product/arts-crafts/23` ✅,
`/product/ride-ons/4` ✅, `/product/arts-crafts/22` (ilk tık yuttu, ikincide **Quota Exceeded**).
Kota doldu → tur kuralına göre durduruldu.
**Kalan 2 hedef:** `/product/arts-crafts/20`, `/product/baby-toddler/9`.

**"Alternate page with proper canonical tag: 3" — HATA DEĞİL, KAPATILDI.**
Üç sayfa şunlar: `/post4` (14 Tem'de taranmış, yani statik blog düzeltmesinden **önce** —
bayat veri, yeniden taranınca düşecek), `/shop/plush/` ve `/shop/building-toys/`
(**sondaki slash**; `vercel.json`'da `trailingSlash:false` var, `curl` ile doğrulandı:
308 → slash'sız sürüme yönleniyor). Yani doğru davranışın raporlanması. Kovalama.

**⚠️ `/sitemap-products.xml` hâlâ "Couldn't fetch", 0 keşif.** Ama artık **gereksiz**:
`sitemap.xml` 143 URL ile tüm ürünleri kapsıyor ve okunuyor. Öneri: bu sitemap'i
GSC'den kaldır, sürekli hata gürültüsü üretmesin.

### Akış kuralları (kanla öğrenildi — 31 Tem'de tekrar doğrulandı)
- **Navigate sonrası İLK yazma her seferinde yutuluyor.** Kutuya iki kez tıklamak yetmiyor;
  yazdıktan sonra **zoom ile kutuyu doğrula**, boşsa tekrar yaz. Ancak doğruladıktan sonra Enter.
- Enter'dan sonra sayfanın yüklenmesini bekle; **REQUEST INDEXING'e erken tıklarsan tık boşa gider.**
- Onay için modal'a güvenme, satırdaki kalıcı **"✓ Indexing requested"** yazısına bak.
- Kota dolunca **"Quota Exceeded"** kırmızı modal'ı çıkar → o turu bitir.

---

## B0-ESKI. 30 Tem turu (arşiv)

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

## A6. 🔴 ANALİTİK — Supabase duraklama tuzağı (31 Tem 2026'da yakalandı)

**Olan:** Supabase projesi (`vijagongnjfddhtlwecu`) **INACTIVE** durumdaydı.
Ücretsiz plan **~7 gün hareketsizlikte projeyi otomatik duraklatıyor.** Duraklayınca
`index.html`'deki `sbInsert()` sessizce başarısız oluyor.

**Kaybedilen:** son `amazon_clicks` kaydı **14 Tem 20:29** — yani **17 gün** boyunca
affiliate tıklaması, iletişim mesajı ve bülten kaydı hiç yazılmadı.
Toplam tarihsel veri: **7 tıklama** (hepsi 12-14 Tem, ikisi eski `/#/product/` hash'li
URL'den, biri `referrer: vercel.com` → büyük olasılıkla kendi testleri), **0 bülten,
0 mesaj**. Amazon Associates paneli 27 Tem'de 34 tıklama diyordu — **aradaki fark bu
kesintiden.** Yani gerçek kaynak Amazon paneli, bizim tablo değil.

**⚠️ Teşhis tuzağı:** proje `COMING_UP` iken `list_tables` **boş** döner ve
`relation "amazon_clicks" does not exist` hatası alırsın. **Tabloların silindiğini
sanma** — restore bitmeden sorgulama. Tablolar ve veri yerindeydi.

### Yapılanlar (31 Tem)
- [x] Proje **restore** edildi, REST API doğrulandı (INSERT 201).
- [x] Tablolar `create table if not exists` + indeks + **RLS** ile sağlamlaştırıldı.
      Politika: anon/authenticated **yalnızca INSERT**. SELECT bilerek YOK —
      publishable anahtar herkese açık, aksi halde tüm e-postalar okunabilirdi.
      Doğrulandı: anon SELECT `[]` dönüyor, sızıntı yok.
- [x] **Kalıcı çözüm: `bestseller_sync.py`'ye `ping_supabase()` eklendi.**
      Tur 5 günde bir çalıştığı için 7 günlük duraklama eşiği hiç görülmez.
      Ping başarısızsa log'a **UYARI** yazar. Python HTTPS bu makinede bozuk → `curl`.
- [x] **Form sessiz başarısızlığı düzeltildi.** İletişim formu ve bülten kutusu, kayıt
      başarısız olsa bile koşulsuz "✓ Message sent" / "✓ You're in!" diyordu. Artık
      `sbInsert()` bir promise döndürüyor ve başarı mesajı **yalnızca HTTP ok** ise
      gösteriliyor; değilse hata + `info@kolikshop.com` yönlendirmesi.
      Tarayıcıdan uçtan uca test edildi: form → Supabase → satır yazıldı.

### Kalan
- [ ] **Vercel Web Analytics KAPALI** (API 404: "Web Analytics not found").
      Şu an sitede ziyaretçi/sayfa görüntüleme ölçümü **hiç yok** — GSC yalnızca
      organik aramayı gösteriyor, TikTok/Pinterest'ten gelen trafik hiçbir yerde
      görünmüyor. Vercel panelinden **Analytics sekmesi → Enable** (tek tık, ücretsiz
      kademe var), sonra `index.html`'e script eklenir. **Kullanıcı yapmalı.**
- [ ] Her A1 turundan sonra log'da `Supabase ping: 200` satırını doğrula.

---

## A3. Pinterest — periyodik kontrol + SEO optimizasyonu (kullanıcı isteği, 30 Tem 2026)

Hesap: **`toyscoutnet`** · 11 pano · **108 pin** · katalog **117 ürün**

**⛔ HÂLÂ BLOKE — 31 Tem'de yeniden test edildi, durum aynı.**
`boards_list` **çalışıyor** (pano okuma kapsamı sağlam), ama `user_get_info` ve
`pins_list` **401**. Yani token'da pano okuma var, **pin okuma/yazma ve hesap kapsamı yok**.
Bu kısmi kapsam kaybı → tam yeniden yetkilendirme gerekiyor (OAuth iznini kullanıcı
kendi vermeli, Claude veremez).
**İlk iş: Pinterest bağlantısını yeniden yetkilendir.** O yapılmadan aşağıdaki
hiçbir madde uygulanamaz.

### Boşluk analizi (31 Tem — `boards_list` ↔ `js/data.js`, doğrulandı)

| Pano | Ürün | Pin | Fark |
|---|---:|---:|---:|
| Arts & Crafts for Kids | 26 | 19 | **−7** |
| Baby & Toddler Toys | 12 | 10 | −2 |
| Action Figures | 4 | 3 | −1 |
| Games | 12 | 11 | −1 |
| **Dolls & Accessories** | 1 | 0 | −1 · **PANO HİÇ YOK** |
| Building Toys · Learning · Novelty | 4·2·18 | 5·3·19 | +1 (blog pinleri, normal) |
| Party · Plush · Ride-ons · Sports | 15·1·5·17 | aynı | 0 (tam) |
| **TOPLAM** | **117** | **108** | **12 ürün pini eksik** (+3 blog pini) |

**Pano açıklaması boş olanlar:** Action Figures, Arts & Crafts (diğer 9'unda var).

### Yapılacaklar (token yenilenince, öncelik sırasıyla)

**1. 🔴 ÜRÜN PİNLERİNİN LİNKLERİ KIRIK — 30 Tem'de tarayıcıdan DOĞRULANDI.**
Örnek pin (`1106618939714542588`, Taba Squishy Hamster) hedefi: **`/#/product/games/9`**
Site yönlendirmeyi `location.pathname` ile okuyor; **hash hiç okunmuyor.** Yani bu pin
kullanıcıyı ürün sayfasına değil **ana sayfaya** bırakıyor. ~100 ürün pini, ~100 kopuk
yolculuk. Sadece SEO kaybı değil, dönüşüm kaybı.
Doğru biçim: `https://www.toyscout.net/product/<kategori>/<idx>`

**⚠️ Basit `#` silme yetmez:** ürün eklendikçe/silindikçe indeksler kayıyor
(bkz. [[urun-katalog-bulgulari-2026-07]] URL kaydırma tuzağı). Her pin, **ürün adından
doğrulanarak** yeniden eşlenmeli. Kontrol edilen örnekte `games/9` hâlâ doğruydu ama
bu garanti değil.

**Blog pinleri SAĞLAM** — kontrol edilen blog pini `/post2`'ye gidiyordu, gerçek yol.
Sorun yalnızca ürün pinlerinde.

**Yan bulgu — yanlış pano/kategori:** "Taba Squishy Hamster" hem Pinterest'te **Games**
panosunda hem katalogda `games` kategorisinde. Squishy oyuncak, oyun değil → `novelty`
olmalı. Katalogdaki otomatik kategori eşlemesi gözden geçirilmeli.

**Hesap durumu (30 Tem):** `toyscoutnet` · **63 aylık görüntülenme** · 0 takipçi.
Profil bio'su ve site linki düzgün, domain doğrulanmış.

**YÖNTEM NOTU:** Tarayıcı UI'dan pin düzenleme mümkün (`... → Edit Pin`) ama pin başına
6-8 tıklama = 100 pin için ~700 işlem, üstelik arayüz kararsız. **Doğru yol MCP token'ını
yenileyip programatik düzenlemek** — aynı iş dakikalar sürer. Token yenilenmeden UI'dan
tek tek uğraşma.

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

## A4. ✅ ÇÖZÜLDÜ — blog yazıları artık sunucuda statik (30-31 Tem)

**Ana madde bitti.** `post1.html`…`post9.html` üretildi (`products/build_blog_pages.py`),
`vercel.json` rewrite'ları `/post9` → **`/post9.html`** olarak değiştirildi, deploy edildi.
Canlıdan doğrulandı: `curl /post9` artık yazının kendi `<title>`'ını ve canonical'ını dönüyor.

### 31 Tem'de yapılan kalan işler

- [x] **`browse.html`'e OG/Twitter + JSON-LD eklendi.** `CollectionPage` + `ItemList`
      (12 kategori) + `BreadcrumbList`. **Üreteç `products/build_browse_page.py` düzenlendi**,
      `browse.html` doğrudan değil — aksi halde sonraki `bestseller_sync` turu ezerdi.
      Bozuk (satır sonu içeren) description da düzeltildi. Deploy `26fb4f8`, canlı doğrulandı.
- [x] **meta description 187 → 144 karakter.** Hem statik etikette hem `updateSeo()`
      varsayılanında güncellendi (ikisi ayrı yerde, ikisi de değişmeliydi).
- [x] **Blog teaser görsellerine `width`/`height` eklendi** (3 statik `<img>`).

### ❌ İPTAL — "index.html'e statik canonical ekle" maddesi YANLIŞTI

**Eklenmeyecek, bir daha gündeme getirilmeyecek.** `index.html` tek bir sayfa değil:
`vercel.json` rewrite'ları ile `/`, `/shop/*`, `/product/*`, `/contact`, `/privacy`,
`/terms`, `/disclosure` rotalarının **hepsine** aynı dosya servis ediliyor.
Ham HTML'e `<link rel="canonical" href="https://www.toyscout.net/">` koymak,
JS çalıştırmayan tarayıcıya **117 ürün sayfasının hepsinin ana sayfanın kopyası olduğunu**
söyler — yani şu an olmayan bir felaketi yaratır. `index.html:10`'daki kod yorumu
bunu zaten açıklıyor ve haklı. Canonical'ı `updateSeo()` rota başına enjekte etmeye
devam etmeli.
**Kanıt Google'ın JS'i render ettiği yönünde:** Product snippets 49, Review snippets 145
geçerli öğe; `/product/games/11` indeksli.
*(Gerçek çözüm istenirse: ürün sayfalarını da `post*.html` gibi statik üretmek — 117 dosya,
ayrı ve büyük bir iş. Şu an gerek yok, keşif zaten çalışıyor.)*

### ❌ İPTAL — "görsellerde width/height yok → CLS riski" maddesi de yanıltıcıydı

CSS'te **bütün görsel kutuları zaten yer ayırıyor**: `.pcard .ph{aspect-ratio:1/.86}`,
`.bpost .bp-img{aspect-ratio:16/9}`, `.pd-imgbox .main{aspect-ratio:1/1}`, logo'da açık
`width/height`. Görselden kaynaklı CLS zaten engellenmiş.
**Core Web Vitals'ın "No data" demesinin sebebi kod değil trafik:** CWV gerçek kullanıcı
alan verisi (CrUX) ister, o da minimum trafik eşiği gerektirir. Sitede 0 tıklama var.
Trafik gelmeden bu kutu yeşile dönmez.

---

## A4-ESKI. Özgün tespit (arşiv, 30 Tem)

**`/post1` … `/post9` ham HTML'de ana sayfayla BİREBİR AYNI içeriği dönüyor.**
Doğrulandı (`curl /post9`): `<title>` ana sayfanın başlığı, `#view` kapsayıcısı **boş**,
yazının tek satırı bile ham HTML'de yok, canonical yok (JS enjekte ediyor).

**Neden kritik:** JS çalıştırmayan bir tarayıcı için 9 blog yazısının hepsi ana sayfanın
kopyası. GSC'deki *"Alternate page with proper canonical tag: 3"* uyarısının kaynağı
büyük olasılıkla bu. Üstelik blog yazıları bu sitenin **asıl organik trafik kaldıracı** —
ürün sayfaları rekabet edemez, uzun kuyruk sorguları yazılardan gelir. O yazılar
sunucuda yok.

**Çözüm (browse.html ile aynı desen):** `post1.html` … `post9.html` statik dosyaları üret.
- Kaynak: `index.html` içindeki `var POSTS={...}` (26 KB, 9 yazı,
  her biri `meta` + `h` + `body()` fonksiyonu).
- `body()` şu yardımcıları çağırıyor: `aProd`, `amazonSearchUrl` → statik üretimde
  bunlara stub yazılmalı (Node ile eval en pratik yol).
- Her sayfada: benzersiz `<title>`, meta description, **canonical**, OG + Twitter,
  `BlogPosting` JSON-LD, breadcrumb, ilgili ürünlere gerçek `<a href>`.
- `vercel.json`: `/post9` → `/index.html` yerine **`/post9.html`** olarak değiştir
  (9 satır). SPA içi gezinme `data-go` ile çalışmaya devam eder.

**Diğer tespitler (aynı taramadan):**
- `index.html` ham HTML'de **canonical YOK** — sadece JS enjekte ediyor. Kendine
  referans veren bir canonical statik olarak eklenmeli.
- meta description **187 karakter** — ~155'e kısalt, aramada kesiliyor.
- Görsellerde `width`/`height` yok → CLS riski (Core Web Vitals "No data" durumda).
- `browse.html`'de **OG/Twitter etiketi ve JSON-LD yok** — `CollectionPage` +
  `ItemList` + breadcrumb eklenmeli.

---

## A5. YouTube / TikTok kanal denetimi (31 Tem 2026)

### 🔵 ANA BULGU: TikTok, YouTube'u ezici farkla geçiyor

Aynı videolar, aynı gün, iki platform:

| Video | TikTok | YouTube | Fark |
|---|---:|---:|---:|
| Kikidex çizim tahtası | **694** | 5 | **139×** |
| UNO kart oyunu | **168** | 3 | 56× |
| Oball bebek topu | **269** | 0 | — |
| Bluey su boyama | **138** | 19 | 7× |
| Mr. Sketch kokulu kalem | **170** | 36 | 4.7× |
| Havuz şezlongu | **111** | 90 | 1.2× |

**TikTok toplam ≈ 1.741 görüntülenme · YouTube 28 günde 159.** Yaklaşık **11 kat**.
YouTube: 1 abone, 0,3 saat izlenme süresi.

**Sonuç: emek dağılımı TikTok'a kaymalı.** Aynı videoyu iki platforma yüklemek zaten
maliyetsiz, ama optimizasyon (başlık, hashtag, saat, ses seçimi) çabası TikTok'a
yoğunlaşmalı. YouTube Shorts bu kanal için henüz karşılık vermiyor.

### 🔴 Düzeltilecek hatalar

**1. TikTok'ta MÜKERRER gönderi.** Crayola Ultra Clean iki kez yayınlanmış:
`24 Tem 7:00` (94 görüntülenme) ve `25 Tem 7:00` (97). Aynı ürün, aynı açıklama.
YouTube'da aynı hata 24 Tem'de bulunup silinmişti; TikTok'taki hâlâ duruyor.
Mükerrer içerik erişimi baskılar → **birini sil.**

**2. Türkçe katalog adları TikTok açıklamalarına sızmış (4 gönderi).**
ABD kitlesine İngilizce açıklamanın önünde Türkçe ürün adı duruyor:
- `Crayola Ultra Clean Yıkanabilir Kalem 40'lı Washable markers that…` (×2)
- `Bluey Aqua Su ile Boyama (Reusable) This $4 Bluey toy…`
- `Aqua Monterey 4'ü1 Arada Havuz Şezlongu This pool float…`
- `05-A UNO Kart Oyunu The $11 game…` ← ayrıca **slot kodu** da sızmış

07-A'daki aynı hatayı kullanıcı 29 Tem'de düzeltmişti; bu 4'ü kalmış.
**Not:** ticari içerik işaretli TikTok gönderilerinin açıklaması **yalnızca telefondan**
düzenlenebiliyor (29 Tem'de öğrenildi).

**3. YouTube 08-B (ALASOU) takılmış.** `30 Tem` için zamanlanmış ama 31 Tem'de hâlâ
"Planlandı" görünüyor — yayına geçmemiş. Kontrol edilmeli, gerekirse elle yayınla.

**4. 04-A Candy Land** hâlâ Shorts listesinde yok (uzun format, `dnkiQr9BkHI`).
6 denetimdir açık.

### Durum (31 Tem)

YouTube 18 Shorts: **13 yayında**, 5 zamanlanmış (31 Tem – 1 Ağu).
TikTok 12 gönderi: **8 yayında**, 4 zamanlanmış.
Yeni içerik planından **11-A (LeapFrog)** her iki platforma da yüklenmiş, 1 Ağu'ya
zamanlı (planda 2 Ağu'ydu, sorun değil).

### İzleme notu

YouTube'da bir izleyici yorumu: **"That's AI"**. İzleyiciler yapay zekâ üretimi
videoları fark ediyor. Yeni yöntem (Amazon ürün videosu + CapCut) bu açıdan da
avantajlı olabilir — gerçek ürün görüntüsü kullanılacak.

---

## A7. 📈 BLOG = ASIL KALDIRAÇ (31 Tem'de GSC verisiyle kanıtlandı)

90 günlük Performance: **81 gösterim, 0 tıklama, ortalama pozisyon 24.2** (3. sayfa).
Sayfa bazında gösterimler:

| Sayfa | Gösterim |
|---|---:|
| `/` | 23 |
| **`/blog`** | **18** |
| **`/post5`** | **16** |
| `/shop/sports-outdoor` | 13 |
| `/shop/dolls` | 6 |
| `/shop/building-toys` | 3 |
| `/product/arts-crafts/1` | 2 |
| `/product/learning-education/0` · `/post4` · `/product/plush/0` | 1'er |

**9 blog yazısı 35 gösterim (%43); 117 ürün sayfası toplam 4.** Sayfa başına blog,
katalogdan ~9 kat verimli. Üstelik post4/post5 bunu **ham HTML'de ana sayfanın kopyası
olarak servis edilirken** aldı (statik hâle 30 Tem'de geçtiler) — yani bu taban, tavan değil.

Marka dışı sorgular da blog konulu: *"cyber monday kids art & coloring deals"*,
*"black friday kids art & coloring deals"*, *"building toy"*, *"outdoor sports toys market"*.
**En çok gösterim alan kategori arts-crafts** (katalogdaki en büyük kategori, 26 ürün).

**Kural: yeni yazı konusu seçerken bu tabloya bak.** Ürün sayfası üretmek yerine yazı
üretmek daha getirili. Mevsimsel kanca + en iyi performans gösteren kategori birleşimi
en iyi sonucu veriyor.

### Yayın takvimi
3 günde bir. **post10 "Best back-to-school art supplies under $15 in 2026" 31 Tem'de
yayınlandı** (deploy `1c3f717`, canlı doğrulandı: 7 gerçek katalog ürünü, 7 affiliate
link, statik `post10.html`, canonical + BlogPosting JSON-LD).
**Sıradaki: post11 — 3 Ağu 2026.** Boştaki konular: baby-toddler, plush, ride-ons,
dolls, action-figures; ayrıca Kasım öncesi Black Friday/Cyber Monday (sorgu verisi var).

### ⚠️ Yeni yazı eklerken — 9 nokta + bir tuzak
`index.html`: POSTS · yönlendirme dizisi · `render()` zinciri · `updateSeo()` ·
JSON-LD `blogPost` · ana sayfa teaser · `vBlog()` `bp()`.
Ayrıca `vercel.json` rewrite ve `products/build_sitemap.py`.
**Ana sayfa teaser'ında 3 kart tutulmalı** (grid 3'lü; 4. kart tek başına satır açar) —
en eskisini çıkar, `/blog`'da zaten duruyor.

**🐛 31 Tem'de düzeltilen hata:** `build_blog_pages.py`'deki regex `(post\d)` tek haneliydi;
**post10, post1 diye eşleşiyordu** ve kendi görselini/tarihini alamıyordu. `(post\d+)`
yapıldı. İki haneli ilk yazı olduğu için şimdi ortaya çıktı — benzer tek-hane regex'i
başka yerde kalmadı (tarandı).

---

## B. Açık işler (tarihli, bitince buradan sil)

- [x] **29 Tem 22:1x — İLK OLUMLU SİNYAL: `/product/games/11` INDEKSLENDİ.**
      Aynı akşam saat başında "URL is unknown to Google" diyen sayfa, istek
      gönderildikten ~45 dakika sonra **"URL is on Google · Page is indexed"** oldu;
      Product snippets 5 geçerli öğe görüyor. **Anlamı:** Google bu SPA'nın ürün
      sayfalarını render edip indeksleyebiliyor — sorun render değil, sayfaya
      ULAŞAMAMASIYDI. `browse.html` yaklaşımının doğru olduğunun ilk kanıtı.
- [x] **`/browse.html` — TARANDI.** URL Inspection (31 Tem): Last crawl **29 Tem 15:10**,
      Googlebot smartphone. Kendisi "Crawled – currently not indexed" — ama **görevi
      indekslenmek değil, link keşfi sağlamaktı ve onu yaptı.** Çıplak link listesi
      olduğu için Google'ın indekslememesi normal, kovalanmayacak.
- [x] **ASIL KÖK SORUN (taranabilir link/sitemap keşfi) — ÇÖZÜLDÜ.** 31 Tem'de
      doğrulandı: ürün sayfaları artık "Discovered", kaynak `/sitemap.xml`.
      Ayrıntı ve rakamlar B0'da.
- [x] **Sitemap okunmuyor sorunu — ÇÖZÜLDÜ.** `/sitemap.xml` 143 URL, Success, 30 Tem okundu.
- [ ] **Kalan 2 indeksleme isteği** (31 Tem'de kota doldu):
      `/product/arts-crafts/20` · `/product/baby-toddler/9`
- [ ] **`sitemap-products.xml`'i GSC'den KALDIR.** Hâlâ "Couldn't fetch"/0 keşif ve
      artık gereksiz — `sitemap.xml` tüm ürünleri kapsıyor ve okunuyor. Sürekli hata
      gürültüsü üretiyor, sinyali kirletiyor.
- [ ] **VALIDATE FIX sonucu** — Merchant listings `Missing field "price"` doğrulaması
      *Started* durumda, birkaç gün sürer.
      ℹ️ 31 Tem: Product snippets 49, Merchant listings 43, Review snippets 145, Breadcrumbs 9,
      hepsi **0 geçersiz**. (30 Tem'de 56/51/166 idi — rakamlar gün gün oynuyor, panik yok.)
- [ ] **Vercel Web Analytics'i aç** (bkz. A6) — şu an ziyaretçi ölçümü sıfır.
- [ ] **post11 — 3 Ağu** (bkz. A7 konu listesi).
- [ ] **Görsel tarama yükü kararı.** Crawl stats: 90 günde 208 istek / 91.9 MB,
      **%75-78'i görsel**, HTML yalnızca %13. Diskte `assets/products` 697 dosya /114 MB;
      bunun **576'sı galeri varyantı (`_1`…`_5`) = 95 MB**, ana görseller 19 MB.
      **Ama bunu "görseller HTML'i aç bırakıyor" diye okuma:** Google'ın crawl-budget
      kavramı 1M+ sayfalı siteler için; 146 URL'de düşük tarama **talep düşüklüğü**.
      `robots.txt` ile galeriyi kapatmak bütçeyi HTML'e kaydırmaz ve Google
      "render için gereken kaynağı engelleme" diyor. **Yapılabilir ama garantisi yok —
      karar kullanıcıda.** Zararsız kısmı: `Disallow: /frames/` (241 dekoratif kare).
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
