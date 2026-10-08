# Impact check — 2026-10-08

Sources: GSC (Performance 3 months, Page indexing), Vercel Analytics (30 days), Amazon Associates (30 days, kolico-20).

| Source | Metric | Baseline 10-01/10-05 | 10-07/08 |
|---|---|---|---|
| GSC 3 months | clicks / impressions / avg pos | 7 / 1.43K / 28.9 (10-01) | 8 / 1.77K / 28.7 |
| GSC Page indexing | indexed / not indexed | 29 / 136 | 46 / 1.03K (1,021 "Discovered – not indexed") |
| Vercel 30d | visitors / views / bounce | 44 / 81 / 82% (10-05) | 56 / 126 / 70% |
| Vercel referrers | | — | google.com 7, bing.com 1 |
| Associates 30d | clicks / orders / earnings | 48 / 0 / $0 | 48 / 0 / $0 (34 clicks = 09-10 + 09-21 spikes; real ≈1/day) |

GSC top pages (3 months): /post8 6 clicks · 412 impr · pos 20.1; /blog 1 · 106; /post14 1 · 8 · pos 6.9; /product/arts-crafts/1 132 · pos 14.3; /shop/games 122 · pos 14.4.
Full query/page export: see the 2026-10-07 session (gsc-3m-2026-10-07).

## Diagnosis (3 parallel audits, 2026-10-07)
1. ~1,031 product pages are Amazon-copied text only (0 original words) → 1,021 "Discovered – not indexed" and site-wide quality drag.
2. Pre-rendered product/shop pages were home-page clones (2 H1s, home hero text, 220 KB), JSON-LD image URL broken (`toyscout.netassets`), Amazon ratings in aggregateRating.
3. Hero film + full-screen loader ran on every route; 480vh hero; all CTAs → /shop/sports-outdoor; dead Supabase forms; no direct Amazon button on cards.
4. Only real demand cluster: squishy/NeeDoh (post8). Head terms (best building toys, family board games) sit at pos 50–75 against big publishers.
5. Amazon Associates 180-day rule: tag live ~2026-07-11 → 3 sales needed by ~2027-01-04..07 (owner to confirm in Associates; tax interview open).

## Actions 2026-10-08
- post8 rewritten (best squishy toys 2026, 10 picks, by type/age, FAQ, dateModified 10-08); new post19 (NeeDoh vs Slimygloop vs slow-rise, comparison table, alternatives).
- 4 specific price mentions removed from post9/10/11/12 (no-price rule).
- Technical SEO + UX fixes: see commits of 2026-10-08.
