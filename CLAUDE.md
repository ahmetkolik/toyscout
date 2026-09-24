# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> ⚠️ **Two copies exist and they have diverged (2026-09-24).** This folder (`~/Downloads/Toyscout`) is a real git clone of `github.com/ahmetkolik/toyscout` and is where the **1,004-product catalog** (18 categories) was built and pushed live (commits `098fd9c`, `b5bb54b`). `~/Projects/toyscout` — the plain (non-git) folder that `launchd` agents, `bestseller_sync.py` and `verify.sh` originally targeted, deployed via the GitHub Data API — still holds the **old 165-product** catalog. **Do not deploy from `~/Projects/toyscout` and do not copy its `js/data.js` over this one** — it would wipe ~840 products on the live site. Before using that folder again, sync it from this clone (or retire it and point the agents here). `tasks/TASKS.md` §A0/§B0-AGU7 still says stray Downloads copies should be deleted; that rule predates this decision and is superseded until the user says otherwise (past incident: a forked Downloads copy silently diverged and 5 products never went live).

## What this is

ToyScout — a single-page Amazon affiliate website (toy curation site). The live site is a **hand-written, framework-free vanilla JS SPA**: `index.html` (markup + inline `<style>` + inline `<script>`) plus `js/data.js` (product catalog). There is no package.json, no build step, no bundler, no React — everything is plain HTML/CSS/JS.

**Watch out:** the project directory name ends with a trailing space (`.../Amazon Affiliate Website `). Always quote paths in shell commands.

**Legacy Design Canvas implementation removed (2026-07-21):** `ToyScout Home.dc.html`, `support.js`, `vendor/` (React/Babel), and other dead files (`uploads/`, `products/__pycache__`, `testsprite_tests/`) were deleted during a repo cleanup — they were remnants of the *original* implementation (a Design Canvas doc rendered client-side via React/Babel loaded from unpkg), fully replaced by the vanilla-JS rebuild in commit `77f6ec2` ("Award-grade rebuild... vanilla JS SPA replacing Design Canvas runtime", 2026-07-13/14) and confirmed unreferenced by `index.html` before removal. **Any content or feature change goes into `index.html` / `js/data.js` — there is no other implementation to worry about touching by mistake.**

## Running it

Serve the folder and open the root:

```bash
python3 -m http.server 8000   # then open http://localhost:8000/
```

No CDN dependency, no internet access required to run locally. **Caveat:** routing uses real paths via `history.pushState` (not hash fragments), and only `vercel.json` (production) knows how to rewrite deep links like `/blog` or `/product/games/3` back to `/index.html`. Typing such a path directly into a local `python3 -m http.server` gives a 404 — this is expected. To test a route locally, load `/` and click through the UI (client-side nav intercepts the click); don't type the path into the address bar.

## Architecture

### Files that matter

- `index.html` — the entire app: HTML skeleton, one `<style>` block (~444 lines, plain CSS with custom properties, no Tailwind/CSS-in-JS), one inline `<script>` (~700 lines, IIFE) with all routing, rendering, and data logic.
- `js/data.js` — `window.TS_DATA = {...}`, the product catalog, one array per category id. Same JSON shape as before (see Data layer below).
- `vercel.json` — `rewrites` map every client route (`/shop/:path*`, `/product/:path*`, `/blog`, `/post1`…`/post5`, `/contact`, `/privacy`, `/terms`, `/disclosure`) to `/index.html`; also permanently redirects the old `toyscout.vercel.app` / `toyscout-kolik.vercel.app` hosts to `www.toyscout.net`. **Every new sub-page needs a rewrite entry here or it 404s in production on direct load/refresh.**
- `sitemap.xml`, `robots.txt` — hand-maintained; add a `<url>` entry when adding a route.
- `frames/{desktop,mobile}/` + `frames/manifest.json` — sequential image frames for the scroll-scrubbed hero animation (AI-generated per the rebuild commit message). `index.html`'s `heroLoop()` steps through `FRAME_COUNT=120` frames as the user scrolls the intro section.
- `assets/` — product photos (`assets/products/<ASIN>.jpg` + `_1`…`_5` gallery variants), blog post images, hero stills, logo. Referenced as absolute `/assets/*` paths. **~1.1 GB / ~4,000 product images as of 2026-09-24** (≈190 KB each, 1000–1500 px); a full push takes ~10 min and Vercel still deployed fine, but the repo grows ~0.2 MB per image forever — consider downscaling before adding thousands more.
- `products/fetch_products.py` + `products/<category-slug>/links.txt` — the per-link scraping workflow. Writes directly to `js/data.js` (see below). **Amazon captchas ~80% of its product-page requests now; do not run `--refresh`** (full-rewrite semantics can drop products).
- `products/subcat_sync.py` — bulk import from the Best Sellers + Hot New Releases lists of all 20 Toys & Games sub-categories (see "Bulk import" below). `products/bestseller_sync.py` — the older top-level Best Sellers sync (updates price/rating/BSR of existing products, adds new ones).

### `fetch_products.py` → `js/data.js` (curated fields are preserved)

`products/fetch_products.py`'s `SITE_FILE` now points at `js/data.js`, the file the live site actually reads. `inject_into_site()` rewrites the whole file as a single-line `window.TS_DATA={...};` assignment (compact JSON, no `__PRODUCT_DATA_START/END__` markers anymore — that scheme belonged to the dead `.dc.html`).

**Curated-field preservation:** the scraper's `parse_product_page()` does **not** fetch `bsr`, `gallery`, or `reviews` — those are hand-curated in `js/data.js` (as of 2026-09-24 of 1,004 products: `bsr` 100 %, `gallery` ~98 %, `reviews` ~99.6 % — top ≤ 3 four/five-star Amazon reviews per product, added by `browser_import/apply_age_reviews.py`; `age` ~62 %). Before writing, `load_existing_data()` re-parses the current `window.TS_DATA` and `preserve_curated_fields()` copies those three fields back onto each entry by ASIN (`CURATED_KEYS`). Without this a `--refresh` would wipe them. **If you add a field the scraper can't produce, add its key to `CURATED_KEYS` or the next run drops it.**

**Full-rewrite semantics still apply:** a category whose scrape fully fails (Amazon captcha/503 on every link) produces no entries that run and therefore vanishes from the output. Run `--dry-run` first and keep a backup of `js/data.js` before a real `--refresh`.

### Bulk import from Best Sellers / Hot New Releases (`products/subcat_sync.py`, 2026-09-24)

- Sources: for each of Amazon's 20 Toys & Games sub-categories (node ids in `SUBCATS`), the Best Sellers list (`/Best-Sellers-Toys-Games-<slug>/zgbs/toys-and-games/<node>?pg=1|2`) and Hot New Releases (`/gp/new-releases/toys-and-games/<node>?pg=1|2`). Plain `curl` returns ranks 1–30 (page 1) and 51–80 (page 2); ranks 31–50 are lazy-loaded and not reachable with curl, so 50 candidates per list = ranks 1–30 + 51–70. The site category comes from the source sub-category (`SUBCATS` maps it), not from guessing.
- Quality rules (same as `bestseller_sync.py`): rating ≥ 4.4, ≥ 50 reviews, price present, at least one image, title not ≥ 90 % similar to an existing product. Result of the 2026-09-24 run: 134 → 1,004 products.
- **Product pages must be fetched from a real Chrome session, not curl/urllib** — Amazon captchas ~80 % of scripted product-page requests. Working recipe: open any `https://www.amazon.com/dp/...` tab (Claude in Chrome), define an in-page `fetch('/dp/'+asin)` + `DOMParser` extractor (name, rating, review count, price from `#corePrice_feature_div .a-offscreen`, BSR from the "Best Sellers Rank" text, `#feature-bullets li`, image URLs from the `'colorImages': { 'initial'` blob using `"hiRes":"(https:[^"]+)"` — the URL format changed, the old `m.media-amazon.com/images/I/` regex no longer matches), POST each result as JSON to a tiny local receiver (`http://localhost:8765`, allowed by Amazon's CSP), then import with `bestseller_sync.load_catalog/download_images/is_variant/save_catalog`. **The ready-made pieces live in `products/browser_import/`**: `extract.js` (paste into Chrome), `receiver.py` (`python3 products/browser_import/receiver.py products/browser_import/res`; also serves `browser_import/cands.json` at `GET /` and a `/sleep` endpoint), `import_results.py` (reads `res/*.json` → catalog). Candidate lists come from `subcat_sync.collect_candidates()`. ~4 s per product, 0 captchas in 850 products. **Use a server-side sleep endpoint for the delay** (in-page `setTimeout` is throttled to ~1/min when the tab is hidden) and bring the tab to front (a screenshot call does it) if throughput drops.
- After an import: rebuild `sitemap.xml` and `browse.html` (`build_sitemap.main()`, `build_browse_page.main()`), verify 0 missing image files / 0 duplicate ASINs / all URLs carry `tag=kolico-20`, then run `python3 products/stamp_data_version.py`, `bestseller_sync.write_sitemap(catalog)`, and commit `js/data.js`, `index.html`, `sitemap.xml`, `sitemap-products.xml`, `browse.html`, `assets/products` only (not `js/data.js.bak-*`, `products/.cache`, `products/__pycache__`, `products/bestseller_sync.log`).
- Cosmetic side effects to expect: ~9 products with a numeric (book) ASIN, ~95 seasonal items (Halloween/Christmas/Easter/Valentine) that will look stale after the season, and product groups that are near-variants (e.g. six Magic: The Gathering Marvel decks in `games`, four Toy Story 5 figures in `action-figures`).

### Search Console indexing requests (browser, logged-in Google account `authuser=0`)

- Property: `https://www.toyscout.net/` (URL-prefix). `/sitemap.xml` is the only sitemap; re-submitting it (Sitemaps → type `sitemap.xml` → SUBMIT) prompts a re-read. `sitemap.xml` has 1,041 URLs; GSC showed 163 discovered / 29 indexed on 2026-09-24, so expect indexing to lag for weeks.
- Request-indexing flow that works: load the Overview page fresh → click the top search box **twice** → type the full URL → verify it landed (zoom on the box) → Enter → wait ~8 s → click REQUEST INDEXING → wait ~30 s for "Indexing requested". Direct `inspect?id=<url>` links 404. Screen layout scale varies between runs, so screenshot before clicking. Max 2 attempts per URL, ~10 requests per rolling 24 h; if the generic "Oops" error appears stop for the day (see `tasks/TASKS.md` B0-A).
- 2026-09-24 requests sent: `/shop/musical-instruments`, `/shop/puzzles`, `/shop/rc-vehicles`, `/shop/kids-electronics`, `/shop/dress-up`, `/shop/puppets`.

### Known issues from the 2026-09-24 audit (unfixed unless noted)

1. **Supabase project `toyscout` (`vijagongnjfddhtlwecu`) is INACTIVE (paused).** `contact_messages`, `newsletter_signups` and `amazon_clicks` inserts are failing silently; `verify.sh` reports HTTP 000. Restore it in the Supabase dashboard (or `restore_project`) and re-run `bash tasks/verify.sh`.
2. ~~Fake age chips / default badges / canned pros-cons~~ — **fixed 2026-09-24** (see Data layer).
3. **`js/data.js` is ~2 MB (≈600 KB gzipped)** and still a blocking `<script>` on every route. Mitigated 2026-09-24: `index.html` loads `/js/data.js?v=<md5[:8]>` and `vercel.json` serves that URL with `Cache-Control: public, max-age=31536000, immutable` (repeat visits cost 0 bytes). **After ANY change to `js/data.js` run `python3 products/stamp_data_version.py`** and commit `index.html` too, otherwise returning visitors keep the old catalog for up to a year. Still open: first-visit cost on mobile — split per category / lazy-load detail fields (`bullets`, `gallery`, `reviews`) if needed.
4. ~~`sitemap-products.xml` stale~~ — **fixed 2026-09-24**: regenerated (1,004 URLs) so `verify.sh` matches again. It is still not used by GSC/`robots.txt`; re-run `bestseller_sync.write_sitemap(catalog)` after every catalog change to keep `verify.sh` green.
5. **`~/Projects/toyscout` is stale (165 products)** — see the warning at the top.
6. The SPA serves the same shell for every route and sets title/meta/canonical client-side (`updateSeo()`), so Google has to render JS to see per-product titles — expect slow indexing. (Reviews are no longer missing; see Data layer.)
7. **Marketing copy on the home page needs an owner decision** (not changed): "Only 4.5★+ picks" (136 products are below 4.5; the catalog rule is ≥ 4.4), "1M+ Reviews analyzed", and the named testimonial "Rachel S." are not backed by data in the repo — unverifiable claims on an affiliate site are an FTC/Amazon-Associates compliance risk.