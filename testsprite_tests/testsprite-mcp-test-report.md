# TestSprite AI Testing Report (MCP) — Final

---

## 1️⃣ Document Metadata
- **Project Name:** Amazon Affiliate Website (ToyScout)
- **Date:** 2026-07-08
- **Prepared by:** TestSprite AI Team + Claude Code
- **Runs:** 3 (initial full run of 17 tests → fix CDN bootstrap, re-run 11 blocked tests → fix 3 newly-surfaced issues, re-run those 3)

---

## 2️⃣ Requirement Validation Summary

### R1 — Home page storefront
| Test | Title | Status |
|---|---|---|
| TC001 | Browse the home page storefront | ✅ Passed |
| TC002 | Browse the home storefront and open a featured product | ✅ Passed (fixed) |

**TC002 finding & fix:** Originally failed — clicking a "Top Picks" card on the home page only opened the external "View on Amazon" link; there was no internal ToyScout product detail view reachable from the home page. Wired each of the 6 Top Picks cards' image + title to `openProduct(idx, e, catId)`, opening the matching internal product detail page (the external CTA button is untouched and still opens Amazon directly). Re-verified: passing.

### R2 — Client-side navigation & routing
| Test | Title | Status |
|---|---|---|
| TC004 | Open the Shop view and return home | ✅ Passed |
| TC007 | Open the Blog view and return home | ✅ Passed |
| TC009 | Open the Contact view and return home | ✅ Passed |
| TC015 | Open a legal page from the footer and return home | ✅ Passed |
| TC018 | Open the affiliate disclosure from the footer | ✅ Passed |
| TC019 | Open the privacy policy from the footer | ✅ Passed |
| TC020 | Open the terms of service from the footer | ✅ Passed |
| TC025 | Show validation when contact fields are incomplete | ✅ Passed (fixed) |

**TC025 finding & fix:** Originally blocked — direct navigation to `/contact` returned a 404 ("File not found"), so the contact form couldn't be reached to test validation. Root cause was two-fold: (1) the static file server had no route for bare paths like `/contact`, and (2) once a matching `contact/index.html` fallback was added, the page's script/image tags used paths relative to the document (`./vendor/...`, `assets/...`), which broke when served from a subdirectory. Fixed by adding static fallback directories (`contact/`, `shop/`, `blog/`, `privacy/`, `terms/`, `disclosure/`, `post1/`, `post2/`, `post3/`, each with an `index.html` symlink to the main document) plus `<base href="/">` in the document head so all relative asset/script paths resolve to the site root regardless of the requested path's depth. Re-verified: passing.

### R3 — Shop category browsing & product detail
| Test | Title | Status |
|---|---|---|
| TC005 | Inspect a shop category product and open the affiliate link | ✅ Passed |
| TC008 | Review the full product details before buying | ✅ Passed |
| TC011 | Browse products within a shop category | ✅ Passed |

### R4 — Blog
| Test | Title | Status |
|---|---|---|
| TC012 | Read a full blog post and return to the blog list | ✅ Passed |

### R5 — Newsletter signup
| Test | Title | Status |
|---|---|---|
| TC017 | Subscribe to the newsletter successfully | ✅ Passed |
| TC024 | Prevent newsletter submission with an empty email | ✅ Passed (fixed) |

**TC024 finding & fix:** Originally failed — submitting the newsletter form with an empty email field showed the same success message as a valid submission ("You're in! First drop lands Monday.") instead of rejecting it. Added `isValidEmail()` validation: an empty/invalid email now shows an inline error ("Please enter a valid email address.") and does not flip the subscribed state. Re-verified: passing.

### R6 — Contact form
| Test | Title | Status |
|---|---|---|
| TC021 | Submit a contact message successfully | ✅ Passed |

*(TC025's validation scenario is grouped under R2 above since its root-cause fix was routing-related, but it also exercises this requirement.)*

---

## 3️⃣ Coverage & Matching Metrics

**17 / 17 tests passing — 100%**

| Requirement | Total Tests | ✅ Passed | ❌ Failed |
|---|---|---|---|
| R1 — Home page storefront | 2 | 2 | 0 |
| R2 — Client-side navigation & routing | 8 | 8 | 0 |
| R3 — Shop category browsing & product detail | 3 | 3 | 0 |
| R4 — Blog | 1 | 1 | 0 |
| R5 — Newsletter signup | 2 | 2 | 0 |
| R6 — Contact form | 1 | 1 | 0 |
| **Total** | **17** | **17** | **0** |

*(8 near-duplicate cases from the original 25-case generated plan — TC003, TC006, TC010, TC013, TC014, TC016, TC022, TC023 — were intentionally skipped as redundant with the above to conserve TestSprite credits; they exercise the same flows as passing tests above.)*

---

## 4️⃣ Key Gaps / Risks — resolved this session

1. ~~**Fragile client-side bootstrap.**~~ **Fixed.** React 18 and ReactDOM are now vendored locally (`vendor/`) instead of loaded from the unpkg CDN. Confirmed via network inspection that no CDN requests occur at all; the main component script needs no Babel (it's plain JS executed via `new Function`, not JSX), so this fully removes the external dependency that caused 11/17 tests to previously fail with a blank page.
2. ~~**Affiliate link verification gap.**~~ **Fixed.** All product CTAs (Shop, product detail, and home page Top Picks) now resolve to a real `amazon.com` URL — either the scraped affiliate link, or a `amazon.com/s?k=...` search fallback for placeholder products — instead of dead `#` links.
3. ~~**Contact and Newsletter had zero verified coverage.**~~ **Fixed and verified**, including validation paths (empty email / incomplete contact form now show inline errors instead of false success).
4. ~~**No URL routing.**~~ **Fixed.** Added hash-based routing (`state.page` ↔ `location.hash`) plus static fallback directories, so refresh, browser back/forward, and direct deep links to any view now restore the correct page.
5. **Forms remain local-state only (by design, unchanged).** Newsletter/contact submissions still are not sent or persisted anywhere — this matches the project's stated scope (no backend) and was not something this session was asked to change.
6. **Residual scope note:** the static-directory routing fix covers the 9 top-level views (contact, shop, blog, post1–3, privacy, terms, disclosure). Deep-linking directly to a specific category or product path (e.g. `/product/plush/2` without a hash) still requires the hash form, since generating physical directories for every category/product combination isn't practical for a static, backend-less site. This wasn't a failing test and is left as-is.

**Final result: all 17 executed TestSprite test cases pass. Zero known functional defects remain open.**
