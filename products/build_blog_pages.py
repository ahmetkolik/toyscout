#!/usr/bin/env python3
"""
post1.html … post9.html uretici — blog yazilarinin STATIK sayfalari.

NEDEN VAR (30 Tem 2026 tespiti):
  `curl https://www.toyscout.net/post9` ana sayfayla BIREBIR AYNI HTML donuyordu:
  <title> ana sayfanin basligi, #view kapsayicisi bos, yazinin tek satiri bile ham
  HTML'de yok, canonical yok. 9 yazinin hepsi boyleydi.

  Yani JS calistirmayan bir tarayici icin 9 blog yazisi = ana sayfanin 9 kopyasi.
  GSC'deki "Alternate page with proper canonical tag" uyarisinin kaynagi buydu.
  Blog yazilari bu sitenin asil organik trafik kaldiraci — urun sayfalari genis
  rekabette sirala(ya)maz, uzun kuyruk sorgulari yazilardan gelir.

NE YAPAR:
  index.html icindeki `var POSTS={...}`'i (Node ile, extract_posts.js araciligiyla)
  cikarir ve her yazi icin JS gerektirmeyen tam bir HTML sayfasi uretir:
  benzersiz <title>, meta description, canonical, OG + Twitter, BlogPosting ve
  BreadcrumbList JSON-LD, gercek <a href> gezinme, ilgili yazi linkleri.

  vercel.json'da /postN -> /postN.html olarak yonlendirilir; kullanicinin gordugu
  adres /postN olarak kalir, canonical de oraya isaret eder.

Calistirma: python3 products/build_blog_pages.py
  (blog icerigi degistiginde yeniden calistir — katalogla ilgisi yok, bu yuzden
   bestseller_sync.py'ye baglanmadi.)
"""
from __future__ import annotations

import html as H
import json
import os
import re
import subprocess

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(SITE, 'index.html')

CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{--cream:#FAF3E7;--ink:#14225A;--blue:#1D3FC4;--red:#E8442E;--gold:#F5B301;
--ink-08:rgba(20,34,90,.08);--ink-55:rgba(20,34,90,.55)}
body{margin:0;background:var(--cream);color:var(--ink);
font-family:Nunito,system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.7;
font-size:17px}
.wrap{max-width:760px;margin:0 auto;padding:28px 20px 64px}
header.site{border-bottom:2px solid var(--ink-08);padding-bottom:18px;margin-bottom:26px;
display:flex;gap:18px;align-items:baseline;flex-wrap:wrap}
.brand{font-family:Fraunces,Georgia,serif;font-weight:800;font-size:1.4rem;
text-decoration:none;color:var(--ink)}
.brand .dot{color:var(--red)}
header.site nav a{color:var(--ink-55);text-decoration:none;font-weight:700;
font-size:.92rem;margin-right:14px}
header.site nav a:hover{color:var(--blue)}
.crumb{font-size:.85rem;color:var(--ink-55);margin:0 0 10px}
.crumb a{color:var(--blue);text-decoration:none}
h1{font-family:Fraunces,Georgia,serif;font-size:clamp(1.8rem,4.5vw,2.6rem);
line-height:1.15;margin:.1em 0 .2em}
.pmeta{color:var(--ink-55);font-size:.9rem;font-weight:700;margin:0 0 22px}
.hero{width:100%;height:auto;border-radius:14px;margin:0 0 26px;
border:1px solid var(--ink-08)}
article h2{font-family:Fraunces,Georgia,serif;font-size:1.42rem;margin:1.9em 0 .4em;
line-height:1.25}
article p{margin:0 0 1.15em}
article .a-lede{font-size:1.12rem;color:var(--ink)}
article ul,article ol{margin:0 0 1.2em;padding-left:1.3em}
article li{margin:0 0 .5em}
.a-prod{background:#fff;border:1px solid var(--ink-08);border-radius:14px;
padding:16px 18px;margin:1.4em 0;display:flex;gap:16px;align-items:center;
justify-content:space-between;flex-wrap:wrap}
.a-prod .t b{display:block;font-size:1.02rem}
.a-prod .t span{color:var(--ink-55);font-size:.88rem}
.btn{display:inline-block;text-decoration:none;border-radius:999px;font-weight:800}
.btn-blue{background:var(--blue);color:#fff}
.more{margin:44px 0 0;padding-top:22px;border-top:2px solid var(--ink-08)}
.more h2{font-family:Fraunces,Georgia,serif;font-size:1.2rem;margin:0 0 12px}
.more ul{list-style:none;padding:0;margin:0;display:grid;gap:8px}
.more a{color:var(--blue);text-decoration:none;font-weight:700}
footer{margin-top:46px;padding-top:20px;border-top:2px solid var(--ink-08);
font-size:.86rem;color:var(--ink-55)}
footer a{color:var(--blue)}
@media (prefers-color-scheme:dark){
:root{--cream:#12162a;--ink:#e8ecff;--ink-08:rgba(232,236,255,.12);
--ink-55:rgba(232,236,255,.62);--blue:#8fa8ff}
.a-prod{background:rgba(255,255,255,.04)}}
"""


def esc(s):
    return H.escape(str(s), quote=True)


def text_of(html_str, limit=None):
    t = re.sub(r'<[^>]+>', ' ', html_str)
    t = re.sub(r'\s+', ' ', H.unescape(t)).strip()
    return t[:limit] if limit else t


def load_posts():
    r = subprocess.run(['node', os.path.join(SITE, 'products', 'extract_posts.js')],
                       capture_output=True, text=True, cwd=SITE)
    if r.returncode != 0:
        raise SystemExit(f'extract_posts.js hatasi:\n{r.stderr[:500]}')
    return json.loads(r.stdout)


def load_ld_meta():
    """index.html'deki blogPost JSON-LD'sinden gorsel + yayin tarihi eslemesi."""
    src = open(INDEX, encoding='utf-8').read()
    out = {}
    for m in re.finditer(
            r'"headline"\s*:\s*"(.*?)"\s*,\s*"datePublished"\s*:\s*"(.*?)".*?'
            # \d+ sart: tek hane olsaydi post10, post1 diye eslenirdi (31 Tem 2026'da yakalandi).
            r'"image"\s*:\s*"(.*?)".*?"url"\s*:\s*"https://www\.toyscout\.net/(post\d+)"',
            src, re.S):
        out[m.group(4)] = {'headline': m.group(1), 'date': m.group(2), 'image': m.group(3)}
    return out


def main():
    posts = load_posts()
    ld = load_ld_meta()
    keys = sorted(posts, key=lambda k: int(k.replace('post', '')))
    written = 0

    for key in keys:
        p = posts[key]
        info = ld.get(key, {})
        title = H.unescape(p['h'])
        date = info.get('date', '')
        image = info.get('image', 'https://www.toyscout.net/assets/hero-flying-blue.png')
        url = f'https://www.toyscout.net/{key}'

        desc = text_of(p['body'], 300)
        desc = (desc[:152].rsplit(' ', 1)[0] + '…') if len(desc) > 155 else desc

        # ilgili yazilar — onceki/sonraki uc yazi
        others = [k for k in keys if k != key]
        idx = keys.index(key)
        rel = ([keys[idx - 1]] if idx > 0 else []) + \
              ([keys[idx + 1]] if idx < len(keys) - 1 else [])
        rel += [k for k in reversed(others) if k not in rel][:2]
        rel_html = '\n'.join(
            f'      <li><a href="/{k}">{esc(H.unescape(posts[k]["h"]))}</a></li>'
            for k in rel[:4])

        ldjson = {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "BlogPosting", "headline": title,
                 "description": desc, "image": image,
                 "datePublished": date, "dateModified": date,
                 "author": {"@type": "Organization", "name": "ToyScout Editors"},
                 "publisher": {"@type": "Organization", "name": "ToyScout",
                               "url": "https://www.toyscout.net/"},
                 "mainEntityOfPage": {"@type": "WebPage", "@id": url},
                 "url": url,
                 "isPartOf": {"@type": "Blog", "name": "The ToyScout Radar Blog",
                              "url": "https://www.toyscout.net/blog"}},
                {"@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home",
                     "item": "https://www.toyscout.net/"},
                    {"@type": "ListItem", "position": 2, "name": "Blog",
                     "item": "https://www.toyscout.net/blog"},
                    {"@type": "ListItem", "position": 3, "name": title, "item": url}]},
            ]}

        page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | ToyScout</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{esc(image)}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="ToyScout">
<meta property="article:published_time" content="{date}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{esc(image)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700..900&family=Nunito:wght@400;700;800&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ldjson, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">

<header class="site">
  <a class="brand" href="/">Toy<span class="dot">·</span>Scout</a>
  <nav>
    <a href="/blog">Blog</a>
    <a href="/browse.html">All Toys</a>
    <a href="/contact">Contact</a>
  </nav>
</header>

<p class="crumb"><a href="/">Home</a> › <a href="/blog">Blog</a> › {esc(title)}</p>

<article>
  <h1>{esc(title)}</h1>
  <p class="pmeta">{esc(H.unescape(p['meta']))}</p>
  <img class="hero" src="{esc(image)}" alt="{esc(title)}" width="760" height="428" loading="eager">

{p['body']}
</article>

<section class="more">
  <h2>More from the ToyScout Radar</h2>
  <ul>
{rel_html}
      <li><a href="/browse.html">Browse all {len(keys)}+ curated toys →</a></li>
  </ul>
</section>

<footer>
  <p><a href="/">ToyScout home</a> · <a href="/blog">All posts</a> ·
  <a href="/disclosure">Affiliate Disclosure</a> · <a href="/privacy">Privacy</a></p>
  <p>As an Amazon Associate, ToyScout earns from qualifying purchases,
  at no extra cost to you. © 2026 ToyScout</p>
</footer>

</div>
</body>
</html>
"""
        open(os.path.join(SITE, f'{key}.html'), 'w', encoding='utf-8').write(page)
        written += 1
        print(f'  {key}.html  {len(page):>6,} bayt  "{title[:48]}"')

    print(f'\n{written} blog sayfasi uretildi.')
    return written


if __name__ == '__main__':
    main()
