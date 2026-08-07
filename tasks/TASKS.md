# ToyScout — Görev ve Hatırlatma Kaydı

**Bu dosya tek doğruluk kaynağıdır.** Tüm tekrarlayan görevler, hatırlatmalar ve
açık işler burada. Oturum içi zamanlanmış işler (cron) Claude kapanınca siliniyordu;
bu yüzden her şey ya `launchd` ajanına ya da bu dosyaya bağlandı.

**Durumu doğrulamak için:** `bash tasks/verify.sh`

Son güncelleme: 7 Ağu 2026 — **büyük temizlik turu (B0-AGU7)**: Downloads kopyası
çatalladığı yakalandı ve **silindi** (5 ürün kurtarıldı) · Best Sellers ajanı 4 Ağu
turunu kaçırmıştı, elle tetiklendi (**katalog 117 → 132**) · `verify.sh`'in yanlış
yeşil verdiği yer düzeltildi · **post12 yayında** · GSC turu: tıkanmış 3 istek + post12
gönderildi. Deploy: `178fbe6` · `9135dff` · `3a48efc`.
Onceki: 3 Ağu 2026 — **GSC turu (B0-YENI)**: yapılandırılmış veri
doğrulaması **Passed**, sitemap bugün okundu; indeksleme istekleri tıkandı.
Aynı gün **takvim bölümü (§0) eklendi** — tarihli her iş tek tabloda.
Onceki: 1 Ağu 2026 — **video denetimi (A5-C)** · **post11 yayında (A7)** ·
GSC turu (B0-A: bekleyen 2 istek + sitemap temizligi).
Onceki: 31 Tem 2026 — GSC turu · A4 kapanışı · **Supabase analitik kesintisi
düzeltildi (A6)** · **blog kaldıraç verisi (A7)** · post10 yayında ·
**video tam denetimi + Sheet yeniden düzenlendi (A5, A5-B)**.
Deploy'lar: `26fb4f8` · `e1238bc` · `5f408b1` · `1c3f717` · `52cffbe`

---

## 0. ⏱ YAKIN TAKVİM — hangi gün ne yapılacak

Tarihli her iş burada. Ayrıntı için parantezdeki bölüme bak. Bir işi bitirince
hem buradan hem ilgili bölümden işaretle.

| Ne zaman | İş | Kim/Nasıl | Bölüm |
|---|---|---|---|
| **Her gün 22:15** | GSC turu (denetim + ~10 indeksleme isteği) | launchd bildirir, tur **elle** yapılır | A2 |
| **7–11 Ağu 2026** | 16-A…20-B videoları (10 ürün) | CapCut, henüz üretilmedi | A5-B |
| **10 Ağu 2026** | **post13** blog yazısı (3 günde bir kadans) | elle yazılıp deploy | A7 |
| **~12 Ağu 2026** | Best Sellers senkronu (5 günde bir; sayaç 7 Ağu turundan başlar) | **tam otomatik** — ama **deploy etmez**, sonucu gözden geçirip push et | A1 |
| **Her A1 turundan sonra** | Log'da `Supabase ping: 200` satırını doğrula + `verify.sh`'te "son gercek calisma" | `bash tasks/verify.sh` | A6 |
| Tarihsiz, sıradaki turda | `B0GCC4HQRP` (Mattel KPop Rumi bebek) — kategori elle atanacak | 7 Ağu turu "ELLE BAKILACAK" dedi | A1 |
| **12–16 Ağu 2026** | 21-A…25-B videoları (10 ürün) | Sheet'e eklendi, henüz üretilmedi | A5-B |
| Tarihsiz, telefonda | TikTok mükerrer silme + 9 açıklama düzeltmesi | **sadece telefondan** | A5 |
| Tarihsiz | 09-A (SEREED) videosu · 04-A kısa sürüm yeniden yükleme | üretim | A5-C |
| Tarihsiz, karar bekliyor | Görsel tarama yükü (`Disallow: /frames/`) | kullanıcı kararı | B |
| ~~4 Ağu~~ | ~~post12~~ | ✅ 7 Ağu'da yayında (3 gün gecikmeli) | A7 |
| ~~4 Ağu~~ | ~~Best Sellers senkronu~~ | ✅ kaçırıldı, 7 Ağu'da elle tetiklendi | B0-AGU7 |
| ~~Tarihsiz~~ | ~~`/post11`, `/product/arts-crafts/24`, `/25` indeksleme~~ | ✅ 7 Ağu'da üçü de gönderildi | B0-AGU7 |
| ~~Tarihsiz~~ | ~~`toyscout-master` Vercel projesini sil~~ | ✅ kullanıcı sildi, 7 Ağu — adres artık 404 | B0-AGU7 |
| ~~Tarihsiz~~ | ~~Vercel Web Analytics'i aç~~ | ✅ 7 Ağu — script 200 döndü | A6 |

**Sabit çalışma kuralları (her turda geçerli):**
- Tüm iş **`~/Projects/toyscout`**'ta yapılır. `~/Downloads/toyscout-master`
  **7 Ağu 2026'da silindi** (Çöp Kutusu'nda `toyscout-master-silindi-20260807`).
  Yeniden indirilirse **hemen sil** — 3 Ağu'da bir tur oraya yazılıp kayboldu (A0).
- Tur başında **`bash tasks/verify.sh`** — TASKS.md'ye değil, makineye bak.
- GSC mülkü **`authuser=0`**'da (⚠️ 7 Ağu'da değişti, eskiden `authuser=2`'ydi —
  Chrome hesap sırası kayabiliyor; "erişiminiz yok" görürsen `u/0…u/3`'ü sırayla dene).
  Doğrudan giriş adresi B0-YENI'de.
- Deploy: bu klasör git deposu değil, **`gh api` Git Data API** ile push edilir (D).

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
| Script | `~/Library/Application Support/toyscout/gsc_reminder.sh` ⚠️ proje dışında |
| Sıklık | Her gün **22:15** |
| Log | `~/Library/Application Support/toyscout/gsc_reminder.log` |
| Durdur | `launchctl unload ~/Library/LaunchAgents/net.toyscout.gsc.plist` |

⚠️ **Script ve log proje klasöründe DEĞİL.** Projedeki `products/gsc_reminder.*`
dosyaları taşınmadan önceki kalıntılar; launchd'nin gerçekten çalıştırdığı kopya
`~/Library/Application Support/toyscout/` altında. 3 Ağu'ya kadar `verify.sh`
projedeki bayat log'a baktığı için ajan **5 gündür ölü** görünüyordu — oysa her
gün çalışıyordu. Script artık mutlak yolu okuyor (bkz. B0-YENI).

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

## A5-C. ✅ 1 AĞU VİDEO DENETİMİ — kampanya iki platformda da TAM

Kullanıcı "hepsi planlandı ve yüklendi" dedi; **platformlardan tek tek sayılarak
doğrulandı.**

| | 31 Tem | 1 Ağu | Değişim |
|---|---:|---:|---|
| YouTube Shorts | 27 | **27** (18 yayında + 9 zamanlı, 2-6 Ağu) | — |
| YouTube uzun video | 1 | **0** | 04-A silindi |
| TikTok gönderi | 16 | **29** (19 yayında + 10 zamanlı, 2-6 Ağu) | **+13** |

**Sayı tutuyor:** kampanya 30 slot − 06-A (iptal) − 09-A (üretilmedi) = **28 gerçek video**.
YouTube 27 + silinen 04-A = 28 ✓ · TikTok 29 = 28 + Crayola mükerreri ✓
**TikTok 31 Tem'de 12 video geriydi, o açık kapandı** — artık her iki platform da
2-6 Ağu arası dolu.

### ✅ 04-A Candy Land uzun format — YouTube'da ÇÖZÜLDÜ (yarım)
`dnkiQr9BkHI` **silinmiş**: Studio "Videolar" sekmesi tamamen boş, video URL'si
`"status":"ERROR","reason":"Video unavailable"` dönüyor. **Ama kısa sürüm yüklenmedi**
→ 04-A artık YouTube'da hiç yok. Sorun "yanlış format"tan "eksik video"ya dönüştü.
7 denetimdir açık olan madde bu yüzden kapanmadı, yeniden tanımlandı.

### ❌ Değişmeyen üç boşluk
- **09-A (SEREED denge bisikleti `B08SGH7NKX`)** — hâlâ iki platformda da yok.
- **Crayola mükerreri** — TikTok profilinde 94 ve 97 izlenmeli iki kart yan yana
  duruyor. Silme hâlâ yapılmamış (yalnızca telefondan mümkün, bkz. A5).
- **16-A…20-B** — 7-11 Ağu için Sheet'te planlı, **henüz üretilmedi**; zamanlanmış
  listede bu 10 ürünün hiçbiri yok (SKYJO, Sassy halka, Hoyle, Elmer's, Surfer Dudes,
  Bezente, Max Liquidator, Airbition, Crayola toplu, GOER).

### 🐞 Tarayıcı tuzağı — TikTok Studio "Gönderiler" listesi
Liste sanallaştırılmış ve kaydırınca **boş satır** render ediyor; sayaç da
"Gönderiler 16" gibi yanlış/eksik bir rakam gösteriyor. **Sayım için Studio'yu değil
`tiktok.com/@toyscoutnet` profil ızgarasını kullan** — orada 6'lı satırlar hâlinde
hepsi görünüyor. Studio'daki arama kutusu da yazılan metni almıyor.

---

## B0-AGU7. 7 AĞU 2026 — iki sessiz arıza yakalandı, dördü de kapatıldı

**Turun başında `verify.sh` 13/13 YEŞİL veriyordu. Üçü yalandı.** Aşağıdakilerin
hiçbiri kayıttan anlaşılmıyordu; hepsi makineye bakarak bulundu.

### 🔴 1. İki kopya çatalladı — 5 ürün canlıya hiç çıkmamış

31 Tem'de "byte-byte aynı" denen `~/Downloads/toyscout-master` ile
`~/Projects/toyscout` ayrışmıştı:

| | Projects (doğru) | Downloads (bayat taban) |
|---|---|---|
| Ürün | 117 (= canlı) | **122** |
| Blog | post1–11 | post1–**9** |
| `index.html` | 1 Ağu, 167 KB | 3 Ağu, **153 KB** |

Downloads eski bir GitHub zip'iydi ama **3 Ağu 18:55'te katalog turu orada
çalıştırılmış**. Sonuç: `B01HLJ7RNK`, `B06XL1B7QN`, `B07D4RN9NH`, `B0991GLP6L`,
`B0CGHC2BSR` yalnızca yanlış klasörde, canlıda yok.

**Yapılan:** 5 ürün + 26 görsel Projects'e taşındı, 117 ortak üründe 73 alan
(fiyat/puan/yorum/BSR) tazelendi, deploy `178fbe6`. Downloads kopyası **silindi**.
⚠️ Downloads `index.html`'i olduğu gibi deploy edilseydi post10 + post11 silinecekti.

### 🔴 2. Best Sellers ajanı 4 Ağu turunu kaçırdı — verify.sh göremiyordu

`launchctl print` → **`runs = 1`**: ajan 30 Tem'deki elle kickstart'tan beri hiç
tetiklenmemiş. 5 günlük `StartInterval`'e göre ~4 Ağu turu düşmüş.

**Neden yeşil görünüyordu:** `verify.sh` "son çalışma"yı log'un son tarih satırından
okuyordu; o satır 31 Tem'deki `Supabase ping: 200`'dü — sync'ten değil, **ayrı bir kod
yolundan** gelen bir satır. A0'daki hatanın birebir aynısı: izleyici yanlış sinyale bakıyor.

**Yapılan:** `check_agent()` artık `launchctl print`'ten **`runs`** sayacını ve
ajanın kendi **`*.stdout.log`** mtime'ını okuyor; 6 günden eskiyse KIRMIZI verip
`launchctl kickstart` komutunu yazıyor. Log'un son satırı yalnızca stdout log yoksa,
"dolaylı kanıt" etiketiyle kullanılıyor.

Tur elle tetiklendi (exit 0, `runs=2`): **10 yeni ürün, 44 ürün tazelendi,
katalog 122 → 132**, sitemap 163 URL. Deploy `9135dff`.
**ELLE BAKILACAK:** `B0GCC4HQRP` (Mattel KPop Demon Hunters Rumi) kategori
belirlenemedi, katalogda yok — `dolls` kategorisine elle eklenebilir.

### 🟠 3. Mükerrer canlı kopya: `toyscout-master.vercel.app`

Downloads kopyasında bir `.vercel` bağlantısı çıktı (`projectName: toyscout-master`)
ve **o adres 200 dönüyor** — 3 Ağu'da oradan ayrı bir Vercel projesi deploy edilmiş.
Hafifletici: sayfa `<link rel="canonical" href="https://www.toyscout.net/">` taşıyor,
yani Google asıl siteye yönlendiriyor. Yine de tarama bütçesi yiyor.
`vercel.json`'daki 301 listesi bu hostu **kapsamıyor** (yalnızca `toyscout.vercel.app`
ve `toyscout-kolik.vercel.app` var).
**✅ ÇÖZÜLDÜ — kullanıcı 7 Ağu'da projeyi sildi;** `toyscout-master.vercel.app` artık **404**.

### ✅ 4. GSC turu — tıkanmış üç istek de geçti

Mülk artık **`authuser=0`**'da (3 Ağu'da `authuser=2`'ydi; `u/2` şimdi
toyscoutnet@gmail.com, `u/1` info@kolikshop.com, `u/3` iamsudeai@gmail.com).

| Rapor | Değer | Not |
|---|---|---|
| `/sitemap.xml` | Success, **Last read 7 Ağu**, 147 sayfa | yerel 163'e çıktı, sonraki okumada güncellenir |
| Pages | Indexed 4 / Not indexed 40 | ⚠️ **Last update 7/24** — rapor **14 gündür donmuş**, bu sayılar 2 haftalık |
| Product snippets | 55 geçerli, 0 geçersiz | 3 Ağu ile aynı |
| Merchant listings | 47 geçerli, 0 geçersiz | 3 Ağu ile aynı |
| Review snippets | 161 geçerli, 0 geçersiz | 3 Ağu ile aynı |
| Breadcrumbs | 10 geçerli | 9'du |
| Manual actions | No issues detected | temiz |

**📈 Performance (28 gün): 0 tıklama · 277 gösterim · ort. konum 29.2.**
3 Ağu'da 3 aylık toplam 185'ti; 28 günde 277 — yükseliş sürüyor, tıklama hâlâ 0.

**İndeksleme istekleri — 4/4 başarılı** (3 Ağu'da 5 denemede geçmeyenler dahil):
`/post11` ✅ · `/product/arts-crafts/24` ✅ · `/product/arts-crafts/25` ✅ · `/post12` ✅.
**Kural işe yaradı:** her URL için Overview'a dönüp yenile → kutuya iki kez tıkla →
yaz → **zoom ile doğrula** → Enter. Kutuya navigate sonrası ilk yazma her seferinde
yutuldu; zoom doğrulaması olmasa üçü de boş Enter'la gidecekti.

### 🔎 "Discovered - currently not indexed" listesinde ürün sayfası YOK
37 URL'nin tamamı statik sayfa, blog yazısı ve `/shop/*` kategori sayfası — ve
büyük kısmı **sondaki slash mükerreri** (`/blog/`, `/contact/`, `/post1/`,
`/shop/games/` …). Bu URL'ler 308 ile slash'sıza dönüyor; iç linklerimizde
slash'lı sürüm **yok** (sitemap, browse.html, index.html tarandı, temiz).
Google kendi tahminiyle veya eski dış linklerden bulmuş. **Kovalanacak bir hata değil.**
Not: bu liste 7/24 tarihli, yani 30 Tem'deki ürün sitemap düzeltmesinden **önceki**
duruma ait — ürünlerin listede olmaması bundan.

---

## B0-YENI. 3 AĞU GSC TURU (21:0x–21:4x) — denetim temiz, istekler tıkandı

**2 Ağu turu atlandı** (kayıt yok), bu tur 2 günlük aradan sonra yapıldı.

### ⚠️ ÖNCE BUNU OKU — GSC mülkü ÜÇÜNCÜ Google hesabında
Chrome'da varsayılan hesap (`authuser=0`) **toyscoutnet@gmail.com** ve bu hesabın
**hiç mülkü yok**; `authuser=1` **info@kolikshop.com** (yalnızca kolikshop.com).
ToyScout mülkü **`authuser=2`**'de. Doğrudan giriş:
`https://search.google.com/u/2/search-console?resource_id=https%3A%2F%2Fwww.toyscout.net%2F`
Mülk tipi **URL-prefix** (`https://www.toyscout.net/`), domain property değil —
`sc-domain:toyscout.net` her hesapta "erişiminiz yok" verir. Her turda buradan başla.

### 🔧 `verify.sh` düzeltildi (3 Ağu)
`net.toyscout.gsc` için proje içindeki **eski** log'a (`products/gsc_reminder.log`,
son satır 29 Tem) bakıyordu ve ajan 5 gündür çalışmıyormuş gibi görünüyordu.
Gerçek log launchd'nin çalıştırdığı yerde:
`~/Library/Application Support/toyscout/gsc_reminder.log` (son çalışma **2 Ağu 22:15**,
düzenli). `check_agent` artık mutlak yolları da kabul ediyor.

### Denetim sonuçları
| Rapor | Değer | Not |
|---|---|---|
| `/sitemap.xml` | Success, **Last read 3 Ağu**, 147 sayfa | yereldeki `sitemap.xml` de 147 ✓ |
| Pages | Indexed **4** / Not indexed **40** (37 Discovered + 3 alternate canonical) | **Last update 7/24** — rapor 10 gün bayat, hareketsizlik bundan |
| Product snippets | **55** geçerli, 0 geçersiz | 31 Tem'de 49 |
| Merchant listings | **47** geçerli, 0 geçersiz | 31 Tem'de 43 |
| Review snippets | **161** geçerli, 0 geçersiz | 31 Tem'de 145 |
| Breadcrumbs | **9** geçerli, 0 geçersiz | değişmedi |
| Manual actions | No issues detected | temiz |
| Core Web Vitals | "Not enough usage data" (mobil+masaüstü) | trafik düşük, beklenen |

### 📈 Performance (3 ay) — gösterimler ilk kez belirgin yükselişte
**0 tıklama · 185 gösterim · ort. konum 30.1.** Grafik 28 Tem'e kadar günde 0-5
gösterimde yatayken 29 Tem–1 Ağu arasında **günde ~45 gösterime** fırladı — bu,
28-31 Tem'deki keşif/sitemap düzeltmelerinin ilk ölçülebilir karşılığı.
Tıklama hâlâ 0: ortalama konum 30 (3. sayfa), yani görünürlük var, sıralama yok.

### ✅ VALIDATE FIX KAPANDI
Merchant listings → `Missing field "price" (in offers)` → **Validation: Passed, 0 öğe.**
29 Tem'de başlatılan doğrulama başarıyla bitti; bu açık iş listeden silindi.

### ❌ İndeksleme istekleri — 1 başarılı, 6 hata
- ✅ `/post10` → "Indexing requested" (öncelikli tarama kuyruğuna eklendi).
- ❌ `/post11` → **5 denemede de** "Oops! Something went wrong — We had a problem
  submitting your indexing request." (turun ilk işiydi, hâlâ gönderilemedi)
- ❌ `/product/arts-crafts/24` → aynı hata (dialog önce "Testing if live URL can be
  indexed" diyor, ~30 sn sonra hataya düşüyor).
- **Teşhis:** kota mesajı ("Quota exceeded") DEĞİL, jenerik gönderim hatası.
  Bilinen tuzak (29 Tem'de öğrenilmişti, bu turda tekrar doğrulandı): **istekler arasında
  sayfa yenilenmezse GSC bu hatayı verir ve ardından oturuma hız sınırı koyar.**
  Bu turda ilk istek yenilemesiz arka arkaya denendiği için sınır tetiklendi;
  sonradan Overview'a dönüp doğru akışla (yenile → kutuya iki kez tıkla → yaz →
  Enter → REQUEST INDEXING) yapılan deneme de geçmedi, yani sınır oturum boyunca sürüyor.
- **Kural: bir URL için en fazla 2 deneme. Hata gelirse turu bitir, ertesi güne bırak.**
  Bu turda 5 deneme yapıldı ve muhtemelen o yüzden kalan ~8 istek hiç gönderilemedi.
- **Sıradaki turun İLK İŞİ: `/post11` + `/product/arts-crafts/24` + `/25`.**

---

## B0-A. ✅ 1 AĞU GSC TURU (20:2x) — bekleyen her şey kapatıldı

**Kota sıfırlanmıştı** (31 Tem'deki istekler ~08:30'daydı, üzerinden ~35 saat geçti).

- ✅ **Kalan 2 indeksleme isteği gönderildi:** `/product/arts-crafts/20` ·
  `/product/baby-toddler/9`. İkisi de "Indexing requested" onayı verdi.
  **Kampanyadaki indeksleme istek listesi böylece BOŞALDI.**
- ✅ **`/sitemap-products.xml` GSC'den KALDIRILDI.** Artık tek sitemap `/sitemap.xml`
  (Last read 31 Tem, Success, **146 sayfa** — 31 Tem'de 143'tü, post10 ile arttı).
  Kaldırma yolu: Sitemaps → satıra tıkla → detay sayfası → sağ üst **⋮ → Remove sitemap**.
  (Liste satırındaki ⋮ menüsünde bu seçenek YOK, sadece detay sayfasında var.)
- ✅ `robots.txt`'ten de `sitemap-products.xml` satırı çıkarıldı. **Dosyanın kendisi
  duruyor** — `verify.sh` onu katalog sayısı karşılaştırması için kullanıyor.
- ℹ️ Indexed 4 / Not indexed 40 (37 Discovered + 3 alternate canonical) — dünle aynı.
  **Bu rapor günlerce gecikmeli, hareketsizlik normal.** Panik yok.

### ⚠️ Tuzak: URL Inspection'ın "referring sitemap" alanı gecikmeli
`/product/baby-toddler/9` denetimde **"No referring sitemaps detected"** +
"URL is unknown to Google" dedi. **Sitemap kusurlu DEĞİL** — `curl` ile doğrulandı,
12 baby-toddler URL'sinin hepsi (`/0`…`/11`) sitemap'te. Aynı sitemap'teki
`/product/arts-crafts/20` ise "Discovered" + sitemap ilişkili görünüyordu.
Yani GSC'nin **URL başına** sitemap ilişkilendirmesi, sitemap okumasından bağımsız
ve gecikmeli güncelleniyor. **Bunu sitemap hatası sanıp tekrar araştırma.**

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

### Vercel Web Analytics — kod tarafı BİTTİ, panel düğmesi kullanıcıda

**31 Tem'de yapıldı:** `<script defer src="/_vercel/insights/script.js">` **12 sayfaya**
eklendi — `index.html` + `post1…post10.html` + `browse.html`. Blog sayfaları ve
browse.html ayrı statik dosyalar; sadece index.html'e koymak **en çok gösterim alan
`/blog` ve `/post*` trafiğini ölçüsüz bırakırdı** (bkz. A7). Üreteçlere de eklendi
(`build_blog_pages.py`, `build_browse_page.py`), yani yeniden üretimde kaybolmaz.
Deploy `01fa7d1`, canlı doğrulandı.

Bu SPA `history.pushState` kullanıyor; Vercel'in script'i pushState'i kendisi
sarmaladığı için **rota değişimleri de otomatik sayılıyor** — ek kod gerekmedi.

- [x] ~~**SON ADIM — KULLANICI YAPMALI: Vercel panelinden Analytics'i aç.**~~
      **✅ AÇILDI 7 Ağu 2026.** `/_vercel/insights/script.js` artık **200** dönüyor
      (2.495 bayt, `server: Vercel`, gerçek ETag; curl ile 6 kez doğrulandı).
      ⚠️ **Tuzak:** Claude'un kullandığı Chrome profilinde bir içerik engelleyici
      `/_vercel/insights/` isteklerini kesiyor — tarayıcıda **503**, sayfa içi
      `fetch` ise `Failed to fetch` veriyor ve `window.va` tanımsız kalıyor.
      Aynı sayfadan `/js/data.js` sorunsuz geliyor, yani sunucu tarafı sağlam.
      **Bunu "analitik bozuk" sanma** — yalnızca engelleyicili tarayıcılar sayılmaz.
      Panelde veri görünüp görünmediğini engelleyicisiz bir tarayıcıdan/telefondan
      ziyaret ederek doğrula.
      `vercel.com/kolik/toyscout` → **Analytics** → **Enable** (ücretsiz kademe var).
      Claude tarayıcıdan yapamadı: Vercel oturumu kapalıydı ve **giriş yapmak/kimlik
      bilgisi girmek Claude'a yasak.**
      **Doğrulama:** `curl -o /dev/null -w "%{http_code}" https://www.toyscout.net/_vercel/insights/script.js`
      → şu an **404**, açılınca **200** dönmeli. Script zaten yerinde, ikinci bir
      deploy gerekmiyor; düğmeye basıldığı an veri akmaya başlar.
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

## A5. YouTube / TikTok — 31 Tem 2026 TAM DENETİM (platformlardan doğrulandı)

**Google Sheet:** `ToyScout YouTube Shorts Yayın Takip Çizelgesi`
(`1P1Uzw7FH8s71WrsKFaPWby1456x4L6GXotvSPuJA1Cs`)

### Sayım — iki platformdan tek tek okundu
- **YouTube:** 27 Shorts → **14 yayında**, 13 zamanlanmış (31 Tem – 5 Ağu).
- **TikTok:** 16 gönderi → 12 yayında, 4 zamanlanmış (31 Tem – 1 Ağu).

### ✅ Kapanan iki madde
- **08-B (ALASOU) ARTIK YAYINDA.** "30 Tem'e zamanlıydı, takıldı" durumu çözülmüş —
  YouTube'da *Yayınlandı*, TikTok'ta **590 görüntülenme** (yeni TikTok rekoru).
- **Eski denetimin "01-A…03-B TikTok Studio'da GÖRÜNMÜYOR" tespiti YANLIŞTI.**
  Altısı da orada (01-A 16 Tem, 01-B 16 Tem, 02-A/02-B 17 Tem, 03-A 19 Tem, 03-B 17 Tem).
  20 Tem denetiminde listede yeterince aşağı kaydırılmamış. **Bu satırı bir daha kovalama.**

### ❌ Kampanyadaki tek gerçek boşluk
**09-A (SEREED denge bisikleti, `B08SGH7NKX`) hiç üretilmedi** — iki platformda da yok.
Sheet'te `Durum` = **EKSİK — üretilmedi** olarak işaretlendi (diğer 28 slot `YAPILDI`).

### ⛔ TikTok mükerrer silme — WEB'DEN MÜMKÜN DEĞİL
Crayola Ultra Clean iki kez yayınlanmış:
`24 Tem 7:00` → 94 görüntülenme / 0 beğeni (video `7665358627472968982`)
`25 Tem 7:00` → 97 görüntülenme / 1 beğeni (video `7665358944545557782`)
**Silinecek olan 24 Tem'deki** (her metrikte düşük). İki video aslında farklı çekim,
aynı ürün + aynı açıklama.

31 Tem'de 5 farklı yoldan denendi, hepsinde aynı duvar:
> **"Ticari içeriğe sahip videolar yalnızca TikTok uygulamasında düzenlenebilir."**

"Sil" seçeneği menüde **gri/pasif**. 29 Tem'de açıklamalar için bulunan kısıt
**silmeyi de kapsıyor.** → **Telefondan:** TikTok → Profil → 24 Tem Crayola → ⋯ → Sil.

### ⚠️ Türkçe sızıntı 4 değil, ~9 gönderide
TikTok açıklamalarının başında Türkçe katalog adı duran gönderiler:
01-A (ayrıca **`01-A` slot kodu** da sızmış), 01-B, 02-A, 02-B, 03-A, 03-B, 04-A, 04-B, 05-A.
Hepsi ticari içerik işaretli → **yalnızca telefondan düzeltilebilir.**
Ayrıca hashtag yazım hataları: `#kidsoftiktoks`, `#outdoortoy`, `#todlertoys`,
`#boardgamesoftiktok`, 01-B'de `#amazonfinds` iki kez.

### ⚠️ 04-A Candy Land — İKİ platformda da uzun format
YouTube `dnkiQr9BkHI` (3:31, Shorts listesinde yok) **ve** TikTok'ta 03:30.
Yeniden kırpılıp ikisine de kısa sürüm yüklenmeli. 7 denetimdir açık.

### 🔵 TikTok, YouTube'u ezmeye devam ediyor
07-A Kikidex: TikTok **694** / YouTube 12 · 08-B: TikTok **590** / YouTube 1 ·
08-A Oball: TikTok **281** / YouTube 6 · 07-B Mr. Sketch: TikTok 172 / YouTube 59.
**Optimizasyon çabası TikTok'a yoğunlaşmalı.**

---

## A5-B. 📋 Sheet 31 Tem'de yeniden düzenlendi

1. **`Durum` sütunu (L2:L30)** → 28 slot `YAPILDI`, 09-A `EKSİK — üretilmedi`.
2. **10 yeni video eklendi: `16-A` … `20-B`** (satır 31-40), 7-11 Ağu 2026.
   Seçim yöntemi: `js/data.js`'teki 30 Tem Best Sellers senkronundan, **kampanyada
   kullanılmamış**, 4.6★+ ve 5.000+ yorumlu ürünler; yorum sayısına göre sıralandı.
   **Varyant tuzağına düşmemek için elendi:** Oball çıngırağı (08-A'nın varyantı),
   UNO Splash (05-A), Play-Doh 42'li (01-A) — mevcut videolara fazla benziyordu.

   | Slot | Ürün | ASIN | Yorum | Puan |
   |---|---|---|---:|---:|
   | 16-A | magilano SKYJO | B06XZ9K244 | 75.577 | 4.8 |
   | 16-B | Sassy Halka Dizme | B07NXDJ52C | 65.204 | 4.8 |
   | 17-A | Hoyle Su Geçirmez Kağıt | B000J3Z7TC | 24.675 | 4.7 |
   | 17-B | Elmer's Yapıştırıcı 1 Galon | B0006HUJJO | 15.919 | 4.8 |
   | 18-A | Surfer Dudes | B0DZJ7NJQS | 6.927 | 4.7 |
   | 18-B | Bezente Balon 100'lü | B0BZCHMVTK | 13.865 | 4.6 |
   | 19-A | Max Liquidator Su Tabancası | B0796JVBJ8 | 10.559 | 4.7 |
   | 19-B | Airbition Konuşan Kartlar | B0CRYJB6GK | 8.830 | 4.6 |
   | 20-A | Crayola Toplu Kuru Boya 24'lü | B00Y4QBJAQ | 7.509 | 4.8 |
   | 20-B | GOER 30 Yaş Balon Seti | B093672RHQ | 15.406 | 4.6 |

   Kategori dağılımı: oyun 2 · bebek 1 · sanat 2 · parti 2 · spor 1 · yenilik 1 · öğrenme 1.
   17-B (slime) ve 20-A (öğretmen/okula dönüş) mevsimsel olarak şu an zirvede.

3. **10 yeni video daha eklendi: `21-A` … `25-B`** (7 Ağu 2026; ana sekme satır 41-50,
   TikTok sekmesi satır 42-51), **12-16 Ağu 2026**. 16-A…20-B'nin tamamı iki platforma
   da zamanlandığı için sıra bir sonraki partiye geldi.
   Seçim: 7 Ağu Best Sellers turundan sonraki 132 ürünlük katalogdan, **kampanyada
   kullanılmamış**, 4.6★+ ve 3.000+ yorumlu ürünler; yorum sayısına göre sıralandı.

   | Slot | Ürün | ASIN | Fiyat | Yorum | Puan |
   |---|---|---|---:|---:|---:|
   | 21-A | Crayola Mini Twistables 50'li | B07D4T2XKB | $13.83 | 50.551 | 4.7 |
   | 21-B | LeapFrog LeapTop Touch | B06XL1B7QN | $29.90 | 30.697 | 4.7 |
   | 22-A | Hasbro Connect 4 | B06XY881H4 | $11.41 | 19.320 | 4.8 |
   | 22-B | RUBFAC Altın Balon 129'lu | B09T6QFR2J | $7.19 | 9.236 | 4.6 |
   | 23-A | Prang Fon Kartonu | B0009IR3UI | $4.79 | 6.898 | 4.7 |
   | 23-B | 260 Balon Hayvan Balonu 100'lü | B09L7MDNH6 | $5.88 | 5.914 | 4.6 |
   | 24-A | LiKee Vantuzlu Banyo Oyuncakları | B097B3K46R | $9.99 | 5.229 | 4.8 |
   | 24-B | nobasco Mochi Squishy 30'lu | B0BVNSDG2W | $6.99 | 5.020 | 4.6 |
   | 25-A | USAOPOLY Flip 7 | B0DWGVM7RY | $7.97 | 4.878 | **4.9** |
   | 25-B | MAGNA-TILES microMAGS 26 Parça | B0CX4RLCXW | $19.97 | 3.354 | 4.8 |

   Kategori dağılımı: sanat 2 · oyun 2 · parti 2 · bebek 1 · öğrenme 1 · yenilik 1 · yapı 1.
   **Varyant tuzağına düşmemek için elendi:** tüm Play-Doh hamur paketleri (01-A varyantı),
   Bunch O Balloons 350'lik (03-A), UNO Splash (05-A), Oball çıngırağı (08-A),
   Crayola Broad Line kalemler (06-B), Crayola silinebilir kuru boya (20-A),
   JoyCat suyla boyama (05-B).
   ⚠️ **İki üründe fiyat yok** (Gamfeiny denge bisikleti `B0BLMF98S8`, iPlay iLearn
   bas-bırak arabalar `B0BTBV51KY`) — Amazon o gün `curl`'ü engellediği için fiyat
   çekilemedi, ikisi de listeden çıkarıldı. Bir sonraki senkron fiyatı getirirse aday olurlar.
   ⚠️ **25-B not:** MAGNA-TILES, 01-B'deki PicassoTiles'a kategori olarak komşu; farkı
   *seyahat boyu* 26 parça olması. Videoda bu açı öne çıkarılmalı, yoksa tekrar gibi durur.

4. **`TikTok Başlık ve Hashtag` sekmesi baştan yazıldı.** Eskiden satırların çoğu sekme
   karakterleriyle **tek hücreye** sıkışmıştı, kopyalanamıyordu. Artık **A1:E41**, 40 video:

   | Sütun | İçerik |
   |---|---|
   | A | Video (slot) |
   | B | Ürün |
   | **C** | **TAM METİN — TikTok'a yapıştır** (caption + 5 hashtag, TEK hücre) |
   | D | Caption (ayrı) |
   | E | Hashtag'ler (5'i birden, TEK hücre) |

   **Kullanım: C sütunundaki hücreye tek tık + Cmd+C → doğrudan TikTok caption
   alanına yapıştır.** Hiçbir birleştirme gerekmiyor. Hashtag'ler ayrı da lazım
   olursa E sütununda tek hücrede duruyor.
   Türkçe ad sızıntıları temizlendi, iptal edilen 06-A notuyla korundu.

---

## A5-ESKI. 20 Tem denetimi (arşiv)

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
3 günde bir. **post11 "Best baby shower gifts under $25 in 2026" 1 Ağu'da yayınlandı**
(7 gerçek katalog ürünü / 7 affiliate link, statik `post11.html`, canonical +
BlogPosting JSON-LD, sitemap 147 URL).

**Neden 3 Ağu yerine 1 Ağu:** takvim kendi koyduğumuz bir taban, Google'ın şartı değil;
içerik darboğaz olduğu için erken yayın yalnızca kazandırır. **Ritim korundu —
sıradaki post12 = 4 Ağu 2026.**

**Kategori seçimi veriye dayandı:** `baby-toddler` katalogda 12 ürünle en büyük
işlenmemiş kategoriydi (learning-education 2, plush 1, dolls 1 — yazıya yetmiyor).
Ayrıca `CAT_BLOG["baby-toddler"]` eşlemesi post4'ten ("3-Year-Old Girls", zayıf eşleşme)
post11'e çevrildi.
Kalan boş konular: ride-ons (5 ürün), action-figures (4); ayrıca Kasım öncesi
Black Friday/Cyber Monday (sorgu verisi var). plush/dolls/learning-education
**katalog derinliği yetmediği için yazı konusu yapılamaz** — önce ürün gerekir.

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
- [x] **Kalan 2 indeksleme isteği — 1 Ağu'da GÖNDERİLDİ.** Liste boşaldı.
- [x] **`sitemap-products.xml` GSC'den KALDIRILDI (1 Ağu)** + robots.txt'ten çıkarıldı.
- [x] ~~**Sıradaki turun İLK İŞİ: `/post11` indeksleme isteği**~~ — 7 Ağu'da gönderildi (B0-AGU7) — 3 Ağu'da 5 denemede de
      "problem submitting" hatası verdi (bkz. B0-YENI). Yanına `/product/arts-crafts/24`
      ve `/25` (30 Tem'de eklenen iki yeni ürün, ikisi de hiç taranmamış).
      Blog sayfası ürün sayfasından ~9 kat verimli (A7), post11 sıranın başında.
- [x] **VALIDATE FIX — GEÇTİ (3 Ağu).** Merchant listings `Missing field "price"`
      doğrulaması **Passed**, 0 geçersiz öğe.
      ℹ️ 3 Ağu: Product snippets 55, Merchant listings 47, Review snippets 161,
      Breadcrumbs 9, hepsi **0 geçersiz** (31 Tem: 49/43/145/9 — hepsi arttı).
- [x] ~~**Vercel Web Analytics'i aç** (bkz. A6)~~ — 7 Ağu'da açıldı, script 200.
- [x] **post11 — 1 Ağu'da YAYINLANDI** (2 gün erken, gerekçe A7'de). Sıradaki **post12 = 4 Ağu**.
- [x] ~~**post12 — 4 Ağu 2026.**~~ — 7 Ağu'da yayında, party favor konusu (B0-AGU7) Konu katalog derinliğine göre seçilecek (A7'deki
      kurallar + "yeni yazı eklerken 9 nokta" listesi). Blog, ürün sayfasından
      ~9 kat verimli olduğu için kadans kaçırılmamalı.
- [x] ~~**~4 Ağu: Best Sellers senkron çıktısını gözden geçir ve DEPLOY ET.**~~ — tur kaçırılmıştı, 7 Ağu'da elle çalıştırılıp deploy edildi (B0-AGU7) Ajan
      otomatik çalışır ama **push etmez** — `js/data.js`, `sitemap-products.xml` ve
      `browse.html` yerelde kalır. Tur sonrası: `bash tasks/verify.sh` ("canlı X
      ürün, yerelde Y" uyarısı çıkarsa deploy bekliyor demektir), log'da
      `Supabase ping: 200` satırını doğrula, sonra `gh api` ile push (D).
- [ ] **Görsel tarama yükü kararı.** Crawl stats: 90 günde 208 istek / 91.9 MB,
      **%75-78'i görsel**, HTML yalnızca %13. Diskte `assets/products` 697 dosya /114 MB;
      bunun **576'sı galeri varyantı (`_1`…`_5`) = 95 MB**, ana görseller 19 MB.
      **Ama bunu "görseller HTML'i aç bırakıyor" diye okuma:** Google'ın crawl-budget
      kavramı 1M+ sayfalı siteler için; 146 URL'de düşük tarama **talep düşüklüğü**.
      `robots.txt` ile galeriyi kapatmak bütçeyi HTML'e kaydırmaz ve Google
      "render için gereken kaynağı engelleme" diyor. **Yapılabilir ama garantisi yok —
      karar kullanıcıda.** Zararsız kısmı: `Disallow: /frames/` (241 dekoratif kare).
- [ ] **📱 TELEFONDAN YAPILACAK — TikTok mükerrer silme.** 24 Tem 7:00 Crayola
      (`7665358627472968982`, 94 izlenme). Web'den imkânsız, bkz. A5.
      1 Ağu'da profil ızgarasında hâlâ duruyor (94 ve 97 izlenmeli iki kart).
- [ ] **📱 TELEFONDAN YAPILACAK — 9 TikTok açıklamasındaki Türkçe ad + `01-A` slot kodu.**
- [ ] **09-A videosu (SEREED denge bisikleti)** — 1 Ağu'da yeniden doğrulandı,
      iki platformda da hâlâ yok. Ürün sitede var (`B08SGH7NKX`).
- [ ] **04-A Candy Land — YouTube'da artık HİÇ YOK.** Uzun video 1 Ağu'dan önce
      silinmiş (`dnkiQr9BkHI` → "Video unavailable"), yerine kısa sürüm yüklenmemiş.
      Kısa sürüm kırpılıp YouTube'a yüklenmeli. TikTok tarafı ayrıca doğrulanmadı
      (Studio listesi/araması bozuk, bkz. A5-C). Bkz. A5-C.
- [ ] **16-A…20-B videoları** — 7-11 Ağu 2026, Sheet'te `PLANLANDI`, **1 Ağu itibarıyla
      henüz üretilmedi** (zamanlanmış listede bu 10 ürünün hiçbiri yok). Bkz. A5-B tablosu.
      Amazon ürün videosundan CapCut ile hazırlanacak.

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