#!/usr/bin/env python3
"""ToyScout urun senkronizasyonu.

products/<kategori>/links.txt dosyalarindaki Amazon linklerini okur,
her urunun adini, fiyatini, puanini, degerlendirme sayisini, aciklama
maddelerini ve ana fotografini Amazon.com'dan ceker; fotografi
assets/products/ altina indirir ve tum veriyi "ToyScout Home.dc.html"
icindeki realProducts() bolumune yazar.

Kullanim:
    python3 products/fetch_products.py            # yeni linkleri ceker (cache kullanir)
    python3 products/fetch_products.py --refresh  # her seyi yeniden ceker
    python3 products/fetch_products.py --dry-run  # siteyi degistirmeden ozet gosterir

Not: Amazon zaman zaman otomatik istekleri engeller (captcha/503). Bir urun
cekilemezse atlanir ve uyari basilir; daha sonra tekrar calistirmak yeterlidir.
Kalici cozum icin Amazon PA-API kullanimi onerilir.
"""

import html as html_mod
import json
import re
import ssl
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

def _ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
        try:
            ctx.load_default_certs()
            # macOS sistem Python'unda kok sertifikalar eksik olabilir
            ssl.create_default_context().wrap_socket
        except Exception:
            pass
        return ctx

SSL_CTX = _ssl_context()

# Amazon Associates etiketiniz (ör. "toyscout-20"). Bos birakilirsa
# links.txt icindeki linkte varsa oradaki ?tag= parametresi kullanilir.
AFFILIATE_TAG = ""

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_DIR = ROOT / "products"
CACHE_DIR = PRODUCTS_DIR / ".cache"
IMG_DIR = ROOT / "assets" / "products"
SITE_FILE = ROOT / "ToyScout Home.dc.html"

CATEGORIES = [
    "action-figures", "arts-crafts", "baby-toddler", "building-toys",
    "dolls", "dress-up", "games", "hobbies", "kids-electronics",
    "learning-education", "novelty", "party", "puppets", "puzzles",
    "sports-outdoor", "plush", "rc-vehicles", "ride-ons", "video-games",
]

VALID_AGES = {"0–2", "3–5", "6–8", "9–12", "Teen+"}

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "image/avif,image/webp,*/*;q=0.8"),
    "Accept-Language": "en-US,en;q=0.9",
}


def normalize_age(raw):
    v = raw.strip().replace("-", "–")
    if v.lower() in ("teen", "teen+"):
        v = "Teen+"
    return v if v in VALID_AGES else None


def extract_asin(url):
    for pat in (r"/dp/([A-Z0-9]{10})", r"/gp/product/([A-Z0-9]{10})",
                r"/product/([A-Z0-9]{10})", r"[?&]asin=([A-Z0-9]{10})"):
        m = re.search(pat, url, re.I)
        if m:
            return m.group(1).upper()
    return None


def affiliate_url(asin, original_url):
    tag = AFFILIATE_TAG
    if not tag:
        m = re.search(r"[?&]tag=([\w-]+)", original_url)
        if m:
            tag = m.group(1)
    url = f"https://www.amazon.com/dp/{asin}"
    return f"{url}?tag={tag}" if tag else url


def parse_links_file(path):
    """Her satir: URL [| age=...] [| badge=...]"""
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        url = parts[0]
        if "amazon." not in url and "amzn." not in url:
            print(f"  UYARI: Amazon linki degil, atlandi: {url[:60]}")
            continue
        meta = {}
        for p in parts[1:]:
            if "=" in p:
                k, v = p.split("=", 1)
                meta[k.strip().lower()] = v.strip()
        entries.append((url, meta))
    return entries


def http_get(url, binary=False):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as resp:
        data = resp.read()
        ctype = resp.headers.get("Content-Type", "")
    return (data, ctype) if binary else (data.decode("utf-8", "replace"), ctype)


def strip_tags(s):
    return html_mod.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def parse_product_page(page):
    """Amazon urun sayfasindan alanlari ayiklar."""
    out = {}

    if "captcha" in page[:4000].lower() and "productTitle" not in page:
        raise RuntimeError("Amazon captcha/robot dogrulamasi dondurdu")

    m = re.search(r'id="productTitle"[^>]*>\s*(.*?)\s*</span>', page, re.S)
    if not m:
        raise RuntimeError("urun basligi bulunamadi (sayfa engellenmis olabilir)")
    out["name"] = strip_tags(m.group(1))

    m = re.search(r'class="a-offscreen">\s*\$([0-9,]+(?:\.[0-9]{2})?)', page) or \
        re.search(r'"priceAmount":\s*([0-9]+(?:\.[0-9]{2})?)', page)
    if m:
        val = float(m.group(1).replace(",", ""))
        out["price"] = f"${m.group(1)}"
        out["lo"] = int(val)

    m = re.search(r'([0-9.]+) out of 5 stars', page)
    if m:
        out["rating"] = float(m.group(1))

    m = re.search(r'id="acrCustomerReviewText"[^>]*>\s*([0-9,]+)', page) or \
        re.search(r'([0-9][0-9,]*)\s+(?:global\s+)?ratings', page)
    if m:
        out["rc"] = int(m.group(1).replace(",", ""))

    m = re.search(r'"hiRes":"(https://[^"]+)"', page) or \
        re.search(r'"large":"(https://[^"]+)"', page) or \
        re.search(r'id="landingImage"[^>]*\ssrc="(https://[^"]+)"', page)
    if m:
        out["image_url"] = m.group(1)

    bullets = []
    m = re.search(r'id="feature-bullets".*?</ul>', page, re.S)
    if m:
        for b in re.findall(r'<span class="a-list-item[^"]*">\s*(.*?)\s*</span>', m.group(0), re.S):
            t = strip_tags(b)
            if t and "hide" not in t.lower()[:4]:
                bullets.append(t)
    out["bullets"] = bullets[:6]

    m = re.search(r'id="productDescription".*?<p[^>]*>(.*?)</p>', page, re.S)
    if m:
        out["description"] = strip_tags(m.group(1))[:600]

    return out


def download_image(url, asin):
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    data, ctype = http_get(url, binary=True)
    ext = ".png" if "png" in ctype else ".jpg"
    dest = IMG_DIR / f"{asin}{ext}"
    dest.write_bytes(data)
    return f"assets/products/{asin}{ext}"


def fetch_product(asin, url, refresh=False):
    cache_file = CACHE_DIR / f"{asin}.json"
    if cache_file.exists() and not refresh:
        return json.loads(cache_file.read_text(encoding="utf-8"))

    page_url = f"https://www.amazon.com/dp/{asin}"
    last_err = None
    for attempt in (1, 2):
        try:
            page, _ = http_get(page_url)
            data = parse_product_page(page)
            break
        except (RuntimeError, urllib.error.URLError, urllib.error.HTTPError) as e:
            last_err = e
            if attempt == 1:
                time.sleep(5)
    else:
        raise RuntimeError(f"cekilemedi: {last_err}")

    if data.get("image_url"):
        try:
            data["img"] = download_image(data["image_url"], asin)
        except Exception as e:
            print(f"  UYARI: {asin} fotografi indirilemedi: {e}")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def build_site_entry(asin, url, meta, data):
    entry = {
        "asin": asin,
        "name": data["name"],
        "img": data.get("img", "assets/img-404.png"),
        "url": affiliate_url(asin, url),
    }
    if "price" in data:
        entry["price"] = data["price"]
        entry["lo"] = data["lo"]
    if "rc" in data:
        entry["rc"] = data["rc"]
    if "rating" in data:
        entry["rating"] = data["rating"]
    if data.get("bsr"):
        entry["bsr"] = data["bsr"]
    if data.get("gallery"):
        entry["gallery"] = data["gallery"]
    if data.get("reviews"):
        entry["reviews"] = data["reviews"]
    if data.get("bullets"):
        entry["bullets"] = data["bullets"]
    if data.get("description"):
        entry["desc"] = data["description"]
    if meta.get("age"):
        age = normalize_age(meta["age"])
        if age:
            entry["age"] = age
        else:
            print(f"  UYARI: gecersiz age degeri '{meta['age']}' (gecerli: 0-2, 3-5, 6-8, 9-12, Teen+)")
    if meta.get("badge"):
        entry["badge"] = meta["badge"].upper()
    return entry


def inject_into_site(data, dry_run=False):
    src = SITE_FILE.read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=True, indent=2)
    payload = payload.replace("</", "<\\/")  # script icinde </script> guvenligi
    payload = "\n".join("    " + l if l else l for l in payload.splitlines())
    new_body = f"  realProducts() {{\n    return {payload.lstrip()};\n  }}"
    pattern = re.compile(
        r"(// __PRODUCT_DATA_START__[^\n]*\n).*?(\n  // __PRODUCT_DATA_END__)", re.S)
    if not pattern.search(src):
        sys.exit("HATA: sitede __PRODUCT_DATA_START__ isaretleri bulunamadi.")
    updated = pattern.sub(lambda m: m.group(1) + new_body + m.group(2), src)
    if dry_run:
        print("(dry-run: site dosyasi degistirilmedi)")
        return
    SITE_FILE.write_text(updated, encoding="utf-8")


def main():
    refresh = "--refresh" in sys.argv
    dry_run = "--dry-run" in sys.argv
    site_data = {}
    total = failed = 0

    for cat in CATEGORIES:
        links_file = PRODUCTS_DIR / cat / "links.txt"
        if not links_file.exists():
            continue
        entries = parse_links_file(links_file)
        if not entries:
            continue
        print(f"\n[{cat}] {len(entries)} link")
        products = []
        for url, meta in entries:
            asin = extract_asin(url)
            if not asin:
                print(f"  UYARI: ASIN bulunamadi, atlandi: {url[:70]}")
                continue
            total += 1
            try:
                data = fetch_product(asin, url, refresh=refresh)
                products.append(build_site_entry(asin, url, meta, data))
                print(f"  OK  {asin}  {data['name'][:60]}")
                time.sleep(2)  # Amazon'a nazik davran
            except Exception as e:
                failed += 1
                print(f"  HATA {asin}: {e}")
        if products:
            site_data[cat] = products

    inject_into_site(site_data, dry_run=dry_run)
    n = sum(len(v) for v in site_data.values())
    print(f"\nBitti: {n} urun siteye yazildi ({len(site_data)} kategori)."
          + (f" {failed} urun cekilemedi — tekrar deneyin." if failed else ""))


if __name__ == "__main__":
    main()
