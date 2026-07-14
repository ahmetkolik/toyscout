# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

ToyScout — a single-page Amazon affiliate website (toy curation site). The live site is a **hand-written, framework-free vanilla JS SPA**: `index.html` (markup + inline `<style>` + inline `<script>`) plus `js/data.js` (product catalog). There is no package.json, no build step, no bundler, no React — everything is plain HTML/CSS/JS.

**Watch out:** the project directory name ends with a trailing space (`.../Amazon Affiliate Website `). Always quote paths in shell commands.

**⚠️ Legacy file — do not edit expecting it to go live:** `ToyScout Home.dc.html` (plus `support.js`) was the *original* implementation — a Design Canvas doc rendered client-side via React/Babel loaded from unpkg. It was fully replaced by the vanilla-JS rebuild in commit `77f6ec2` ("Award-grade rebuild... vanilla JS SPA replacing Design Canvas runtime", 2026-07-13/14). Both files are still in the repo but the live site does not load `support.js` at all — verified via `curl https://www.toyscout.net/ | grep -o 'support.js\|js/data.js'` returning only `js/data.js`. **Any content or feature change must go into `index.html` / `js/data.js`, not the `.dc.html` file.**

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
- `assets/` — product photos (`assets/products/<ASIN>.jpg` + `_1`…`_5` gallery variants), blog post images, hero stills, logo. Referenced as absolute `/assets/*` paths.
- `products/fetch_products.py` + `products/<category-slug>/links.txt` — the scraping workflow. **See the warning below — it currently writes to the wrong file.**

### ⚠️ Known gap: `fetch_products.py` still targets the legacy file

`products/fetch_products.py`'s `SITE_FILE` constant points at `ToyScout Home.dc.html` and rewrites its `__PRODUCT_DATA_START__`/`__PRODUCT_DATA_END__` block — the file the live site no longer reads. It does **not** touch `js/data.js`. Until this is fixed, running `python3 products/fetch_products.py --refresh` silently updates a dead file; `js/data.js` (and therefore the live prices/ratings) stays frozen at whatever it contained when the rebuild happened. Before relying on the weekly refresh routine again, point the script at `js/data.js`'s `window.TS_DATA={...}` assignment instead (same per-category JSON array shape, so the diff should be small — mainly the regex/target-file constant and the output format wrapper).

### Client-side routing

- Real paths via `history.pushState`, not hash routing: `/`, `/shop/<cat>`, `/product/<cat>/<idx>`, `/blog`, `/post1`.."/post5", `/contact`, `/privacy`, `/terms`, `/disclosure`. `applyRoute()` parses `location.pathname` on load. A single delegated `document` click listener intercepts any `[data-go]` / `[data-anchor]` link and calls `openView()` instead of a full page load.
- `render()` dispatches on `state.page` to one of the `v*()` functions: `vShop()`, `vProduct()`, `vBlog()`, `vPost(id)`, `vContact()`, `vPrivacy()`, `vTerms()`, `vDisclosure()` — each returns an HTML string that gets assigned to `#view`'s `innerHTML`.
- Adding a new sub-page (e.g. another blog post) touches **~7 places** in `index.html`: the `POSTS` object (if a blog post), `vBlog()`'s `bp()` calls, the home page `#blog-sec` teaser cards, the JSON-LD `blogPost` array in `<head>`, the two routing arrays (`["blog","post1",...]` and the `p==="post1"||...` chain in `render()`), the `updateSeo()` title/description block, **plus** `vercel.json` rewrites and `sitemap.xml`. Grep for an existing post id (e.g. `post3`) and mirror every hit.

### Data layer

- `js/data.js` defines `window.TS_DATA`, keyed by category id. 19 category ids total (see the `CATS` array in `index.html` for id → display name → emoji mapping — same 19 as Amazon's Toys & Games taxonomy).
- Each product object: `asin, name, img, url` (Amazon `dp` link, always `?tag=kolico-20`), `price, lo` (numeric price used for price-range filtering), `rc` (review count), `rating, bsr, gallery` (image URL array), `reviews, bullets`.
- `productsFor(catId)` (in `index.html`) maps the raw `TS_DATA[catId]` array into display-ready objects — adds `stars` (★ string), formatted `ratings`, a per-category age-bracket override table, badge text.
- `stockedCats()` filters the 19-id `CATS` list down to categories that actually have entries in `TS_DATA`. **There is no placeholder/demo-data fallback anymore** — a category with no scraped products simply doesn't render, unlike the old `.dc.html` which showed hard-coded demo items for empty categories.
- Category slugs in `products/<slug>/` must match `CATS` ids in `index.html`. "View on Amazon" CTAs use each product's `url` field directly (or `amazonSearchUrl(name)` — a name-based Amazon search link that also appends `?tag=kolico-20` — used in blog-post body copy where linking a specific ASIN isn't practical).

### Styling

Single `<style>` block in `<head>` (~444 lines). Design tokens in `:root{}`: `--cream:#FAF3E7`, `--ink:#14225A`, `--blue:#1D3FC4`, `--red:#E8442E`, `--gold:#F5B301`, plus `--ink-08/12/22/55` alpha variants. Fonts: **Fraunces** (display/serif headings) + **Nunito** (body), both from Google Fonts. Class-based styling (`.pcard`, `.bpost`, `.v-wrap`, `.a-lede`, etc.) — not inline `style=` attributes like the old `.dc.html`.

### Analytics / backend

Same Supabase project as before (`vijagongnjfddhtlwecu`). `sbInsert(table, row)` POSTs to its REST API for three tables: `contact_messages`, `newsletter_signups`, `amazon_clicks`. The last one fires from a global `document` click listener that matches any outbound `amazon.com` link, extracts the ASIN by regex, and logs it — this is how affiliate-click analytics get recorded.

### Testing

`testsprite_tests/` holds TestSprite-generated Python test scripts (home/shop/product/blog flows). These predate the vanilla-JS rebuild and haven't been re-verified against the new markup/selectors.

## Deploying

Push to `master` → Vercel auto-deploys (no in-repo CI config; deploys are Vercel's git integration). `vercel.json`'s `redirects` block also permanently 301s `toyscout.vercel.app` and `toyscout-kolik.vercel.app` traffic to `www.toyscout.net`. The `p:domain_verify` meta tag in `<head>` must stay in place (Pinterest domain-claim verification — removing it un-claims the domain on Pinterest).
