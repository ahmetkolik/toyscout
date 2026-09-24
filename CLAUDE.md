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

**Curated-field preservation:** the scraper's `parse_product_page()` does **not** fetch `bsr`, `gallery`, or `reviews` — those are hand-curated in `js/data.js` (as of 2026-09-24 of 1,004 products: `bsr` on 100%, `gallery` on ~98%, `reviews` on only ~10% — the bulk-imported products have none). Before writing, `load_existing_data()` re-parses the current `window.TS_DATA` and `preserve_curated_fields()` copies those three fields back onto each entry by ASIN (`CURATED_KEYS`). Without this a `--refresh` would wipe them. **If you add a field the scraper can't produce, add its key to `CURATED_KEYS` or the next run drops it.**

**Full-rewrite semantics still apply:** a category whose scrape fully fails (Amazon captcha/503 on every link) produces no entries that run and therefore vanishes from the output. Run `--dry-run` first and keep a backup of `js/data.js` before a real `--refresh`.

### Bulk import from Best Sellers / Hot New Releases (`products/subcat_sync.py`, 2026-09-24)

- Sources: for each of Amazon's 20 Toys & Games sub-categories (node ids in `SUBCATS`), the Best Sellers list (`/Best-Sellers-Toys-Games-<slug>/zgbs/toys-and-games/<node>?pg=1|2`) and Hot New Releases (`/gp/new-releases/toys-and-games/<node>?pg=1|2`). Plain `curl` returns ranks 1–30 (page 1) and 51–80 (page 2); ranks 31–50 are lazy-loaded and not reachable with curl, so 50 candidates per list = ranks 1–30 + 51–70. The site category comes from the source sub-category (`SUBCATS` maps it), not from guessing.
- Quality rules (same as `bestseller_sync.py`): rating ≥ 4.4, ≥ 50 reviews, price present, at least one image, title not ≥ 90 % similar to an existing product. Result of the 2026-09-24 run: 134 → 1,004 products.
- **Product pages must be fetched from a real Chrome session, not curl/urllib** — Amazon captchas ~80 % of scripted product-page requests. Working recipe: open any `https://www.amazon.com/dp/...` tab (Claude in Chrome), define an in-page `fetch('/dp/'+asin)` + `DOMParser` extractor (name, rating, review count, price from `#corePrice_feature_div .a-offscreen`, BSR from the "Best Sellers Rank" text, `#feature-bullets li`, image URLs from the `'colorImages': { 'initial'` blob using `"hiRes":"(https:[^"]+)"` — the URL format changed, the old `m.media-amazon.com/images/I/` regex no longer matches), POST each result as JSON to a tiny local receiver (`http://localhost:8765`, allowed by Amazon's CSP), then import with `bestseller_sync.load_catalog/download_images/is_variant/save_catalog`. **The ready-made pieces live in `products/browser_import/`**: `extract.js` (paste into Chrome), `receiver.py` (`python3 products/browser_import/receiver.py products/browser_import/res`; also serves `browser_import/cands.json` at `GET /` and a `/sleep` endpoint), `import_results.py` (reads `res/*.json` → catalog). Candidate lists come from `subcat_sync.collect_candidates()`. ~4 s per product, 0 captchas in 850 products. **Use a server-side sleep endpoint for the delay** (in-page `setTimeout` is throttled to ~1/min when the tab is hidden) and bring the tab to front (a screenshot call does it) if throughput drops.
- After an import: rebuild `sitemap.xml` and `browse.html` (`build_sitemap.main()`, `build_browse_page.main()`), verify 0 missing image files / 0 duplicate ASINs / all URLs carry `tag=kolico-20`, then commit `js/data.js`, `sitemap.xml`, `browse.html`, `assets/products` only (not `js/data.js.bak-*`, `products/.cache`, `products/__pycache__`, `products/bestseller_sync.log`).
- Cosmetic side effects to expect: ~9 products with a numeric (book) ASIN, ~95 seasonal items (Halloween/Christmas/Easter/Valentine) that will look stale after the season, and product groups that are near-variants (e.g. six Magic: The Gathering Marvel decks in `games`, four Toy Story 5 figures in `action-figures`).

### Search Console indexing requests (browser, logged-in Google account `authuser=0`)

- Property: `https://www.toyscout.net/` (URL-prefix). `/sitemap.xml` is the only sitemap; re-submitting it (Sitemaps → type `sitemap.xml` → SUBMIT) prompts a re-read. `sitemap.xml` has 1,041 URLs; GSC showed 163 discovered / 29 indexed on 2026-09-24, so expect indexing to lag for weeks.
- Request-indexing flow that works: load the Overview page fresh → click the top search box **twice** → type the full URL → verify it landed (zoom on the box) → Enter → wait ~8 s → click REQUEST INDEXING → wait ~30 s for "Indexing requested". Direct `inspect?id=<url>` links 404. Screen layout scale varies between runs, so screenshot before clicking. Max 2 attempts per URL, ~10 requests per rolling 24 h; if the generic "Oops" error appears stop for the day (see `tasks/TASKS.md` B0-A).
- 2026-09-24 requests sent: `/shop/musical-instruments`, `/shop/puzzles`, `/shop/rc-vehicles`, `/shop/kids-electronics`, `/shop/dress-up`, `/shop/puppets`.

### Known issues from the 2026-09-24 audit (unfixed unless noted)

1. **Supabase project `toyscout` (`vijagongnjfddhtlwecu`) is INACTIVE (paused).** `contact_messages`, `newsletter_signups` and `amazon_clicks` inserts are failing silently; `verify.sh` reports HTTP 000. Restore it in the Supabase dashboard (or `restore_project`) and re-run `bash tasks/verify.sh`.
2. **Fake age chips / default badges** — see Data layer above.
3. **`js/data.js` is 1.9 MB (≈600 KB gzipped)**, loaded as a blocking `<script>` on every route, `Cache-Control: public, max-age=0, must-revalidate`. Fine on desktop (TTFB ~170 ms, load ~0.9 s measured), likely slow on mobile. Options: split per category and lazy-load, or `defer` + longer cache with a versioned filename.
4. ~~`sitemap-products.xml` stale~~ — **fixed 2026-09-24**: regenerated (1,004 URLs) so `verify.sh` matches again. It is still not used by GSC/`robots.txt`; re-run `bestseller_sync.write_sitemap(catalog)` after every catalog change to keep `verify.sh` green.
5. **`~/Projects/toyscout` is stale (165 products)** — see the warning at the top.
6. Reviews (`reviews` field) exist for only ~10 % of products; the SPA serves the same shell for every route and sets title/meta/canonical client-side (`updateSeo()`), so Google has to render JS to see per-product titles — expect slow indexing.
7. Business risks recorded in `tasks/TASKS.md` §A9/§B: Amazon Associates tax information missing and the 180-day / 3-qualifying-sales rule (30-day funnel on 2026-08-07: 50 clicks, 0 orders). More catalog does not fix either.

### Client-side routing

- Real paths via `history.pushState`, not hash routing: `/`, `/shop/<cat>`, `/product/<cat>/<idx>`, `/blog`, `/post1`.."/post5", `/contact`, `/privacy`, `/terms`, `/disclosure`. `applyRoute()` parses `location.pathname` on load. A single delegated `document` click listener intercepts any `[data-go]` / `[data-anchor]` link and calls `openView()` instead of a full page load.
- `render()` dispatches on `state.page` to one of the `v*()` functions: `vShop()`, `vProduct()`, `vBlog()`, `vPost(id)`, `vContact()`, `vPrivacy()`, `vTerms()`, `vDisclosure()` — each returns an HTML string that gets assigned to `#view`'s `innerHTML`.
- Adding a new sub-page (e.g. another blog post) touches **~7 places** in `index.html`: the `POSTS` object (if a blog post), `vBlog()`'s `bp()` calls, the home page `#blog-sec` teaser cards, the JSON-LD `blogPost` array in `<head>`, the two routing arrays (`["blog","post1",...]` and the `p==="post1"||...` chain in `render()`), the `updateSeo()` title/description block, **plus** `vercel.json` rewrites and `sitemap.xml`. Grep for an existing post id (e.g. `post3`) and mirror every hit.

### Data layer

- `js/data.js` defines `window.TS_DATA`, keyed by category id. 19 category ids in the `CATS` array in `index.html` (id → display name → emoji); **18 have products** (`hobbies` and `video-games` are empty and therefore hidden). `musical-instruments` was added 2026-09-24 in `index.html`, `build_browse_page.py` and `fetch_products.py`. Current counts: rc-vehicles 83, arts-crafts 73, games 73, dolls 68, party 63, building-toys 62, puzzles 61, sports-outdoor 60, plush 59, action-figures 57, baby-toddler 57, ride-ons 44, kids-electronics 44, dress-up 44, novelty 40, puppets 40, learning-education 39, musical-instruments 37.
- Each product object: `asin, name, img, url` (Amazon `dp` link, always `?tag=kolico-20`), `price, lo` (numeric price used for price-range filtering), `rc` (review count), `rating, bsr, gallery` (image URL array), `reviews, bullets`.
- `productsFor(catId)` (in `index.html`) maps the raw `TS_DATA[catId]` array into display-ready objects — adds `stars` (★ string), formatted `ratings`, badge text and age. **⚠️ The "AGES x–y" chip and the age filter are NOT real data for ~95% of products:** unless a product has an `age` field, `productsFor` assigns `ages[i % ages.length]` from a per-category table (default `["3–5","6–8","9–12"]`), i.e. it cycles by list position. Likewise every product without `badge` shows "SCOUT PICK". Real ages would have to be scraped (Amazon "Manufacturer recommended age") into an `age` field.
- **Product URLs are positional** (`/product/<cat>/<idx>` = index in that category's array). Never insert, remove or reorder products in the middle of an array — that silently changes every later URL (and breaks indexed/shared links). Only append. (Removing the two price-less NeeDoh items once shifted indexes; it was reverted.)
- `stockedCats()` filters the 19-id `CATS` list down to categories that actually have entries in `TS_DATA`. **There is no placeholder/demo-data fallback anymore** — a category with no scraped products simply doesn't render, unlike the old `.dc.html` which showed hard-coded demo items for empty categories.
- Category slugs in `products/<slug>/` must match `CATS` ids in `index.html`. "View on Amazon" CTAs use each product's `url` field directly (or `amazonSearchUrl(name)` — a name-based Amazon search link that also appends `?tag=kolico-20` — used in blog-post body copy where linking a specific ASIN isn't practical).

### Styling

Single `<style>` block in `<head>` (~444 lines). Design tokens in `:root{}`: `--cream:#FAF3E7`, `--ink:#14225A`, `--blue:#1D3FC4`, `--red:#E8442E`, `--gold:#F5B301`, plus `--ink-08/12/22/55` alpha variants. Fonts: **Fraunces** (display/serif headings) + **Nunito** (body), both from Google Fonts. Class-based styling (`.pcard`, `.bpost`, `.v-wrap`, `.a-lede`, etc.) — not inline `style=` attributes like the old `.dc.html`.

### Analytics / backend

Same Supabase project as before (`vijagongnjfddhtlwecu`). `sbInsert(table, row)` POSTs to its REST API for three tables: `contact_messages`, `newsletter_signups`, `amazon_clicks`. The last one fires from a global `document` click listener that matches any outbound `amazon.com` link, extracts the ASIN by regex, and logs it — this is how affiliate-click analytics get recorded.

### Testing

No automated test suite. (The old `testsprite_tests/` scripts predated the vanilla-JS rebuild, were never re-verified against the new markup/selectors, and were removed in the 2026-07-21 cleanup.)

## Tasks and reminders — read `tasks/` first

**`tasks/TASKS.md` is the single source of truth for every recurring task, reminder,
and open item on this project.** Session-scoped schedulers (cron jobs created inside a
Claude session) do NOT survive closing the project, so nothing lives there — recurring
work is bound to macOS `launchd` agents, and everything is written down in `tasks/`.

At the start of any session that touches scheduling, SEO, the product catalog, or the
video campaign: **run `bash tasks/verify.sh`**. It compares what `TASKS.md` claims
against what is actually on the machine — launchd agents loaded, scripts present, last
run times, catalog/sitemap counts matching, and whether the live site is behind local
changes. Do not trust `TASKS.md` alone; the script is what catches a silently unloaded
agent.

Currently registered (details, schedules and stop commands in `tasks/TASKS.md`):
- `net.toyscout.bestsellers` — Amazon Best Sellers sync every 5 days, fully automatic
  via `products/bestseller_sync.py`. **It does not deploy** — changes stay local until
  someone pushes.
- `net.toyscout.gsc` — daily 22:15 reminder for the Google Search Console round.
  Reminder only; the GSC indexing flow needs a logged-in browser and cannot be scripted.

`tasks/` is in `.vercelignore` — it lives in the repo but 404s on the live site.

## Deploying

Push to `master` → Vercel auto-deploys (no in-repo CI config; deploys are Vercel's git integration; ~1–2 min after the push finishes — poll `https://www.toyscout.net/sitemap.xml` or the Vercel MCP `list_deployments`, team `kolik`, project `toyscout`). If `git push` fails with "Invalid username or token" although `gh auth status` is fine, push with `git -c credential.helper= -c credential.helper='!gh auth git-credential' push origin master` (or run `gh auth setup-git` once). `vercel.json`'s `redirects` block also permanently 301s `toyscout.vercel.app` and `toyscout-kolik.vercel.app` traffic to `www.toyscout.net`. The `p:domain_verify` meta tag in `<head>` must stay in place (Pinterest domain-claim verification — removing it un-claims the domain on Pinterest).
