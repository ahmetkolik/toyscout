# ToyScout — Product Specification

## Overview
ToyScout is a single-page Amazon affiliate website that curates trending toys. It is built as a Design Canvas document (`ToyScout Home.dc.html`) rendered client-side with React 18 (loaded from CDN). There is no backend, no login, and no URL routing — all navigation is client-side state.

## Target URL
- Local: http://localhost:8000 (single entry point, all views under "/")

## Views (client-side, state-driven)
1. **Home** — hero with headline and CTA, trust strip, "Top Picks" product grid, category grid (19 Amazon Toys & Games categories), "Scout Process" section, blog teasers, newsletter signup, footer.
2. **Shop** — full category grid; clicking a category shows its product list.
3. **Product detail** — title, price, star rating, review count, feature bullets, product image, and a "View on Amazon" CTA linking to the Amazon affiliate URL (placeholder products link to "#").
4. **Blog** — list of 3 articles; each opens a full post view (post1, post2, post3).
5. **Contact** — name/email/message form; on submit shows a local thank-you message (no network request).
6. **Legal** — Privacy Policy, Terms of Service, Affiliate Disclosure pages reachable from footer links.

## Key user flows to test
- Home page loads with hero, top picks and categories visible.
- Nav links (Shop, Blog, Contact) open the corresponding overlay views; logo/home returns to the home view.
- Selecting a category in Shop shows products; clicking a product opens the product detail view.
- Product detail shows title, price, rating and image; "View on Amazon" CTA points to an amazon.com URL containing the affiliate tag (real products) or "#" (placeholders).
- Blog cards open full posts and back navigation returns to the list/home.
- Newsletter form: entering an email and subscribing shows a success confirmation (local state only).
- Contact form: filling all fields and sending shows a thank-you confirmation (local state only).
- Footer links open Privacy, Terms and Affiliate Disclosure pages.

## Known limitations (expected behavior, not bugs)
- No URL routing: refresh always returns to Home; browser back exits the site.
- Newsletter/contact forms do not persist or send data anywhere.
- Requires internet access at runtime (React/Babel from unpkg CDN).
- Placeholder products (categories without scraped data) have "#" as their Amazon link.

## Non-goals
- No authentication, no checkout/cart, no backend APIs, no database.
