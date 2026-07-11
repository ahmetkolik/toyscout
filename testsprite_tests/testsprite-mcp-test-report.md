# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** Amazon Affiliate Website (ToyScout)
- **Date:** 2026-07-11
- **Prepared by:** TestSprite AI Team
- **Run context:** Post-migration regression run. Since the previous full run (17/17 passing), the site migrated from `toyscout.vercel.app` to its permanent domain `https://www.toyscout.net` (all canonical/OG/JSON-LD/sitemap URLs swapped, `vercel.json` host redirects added) and the Amazon Associates tag `kolico-20` was wired into all product links. 10 representative tests were selected to cover every requirement group within the account's credit budget.

---

## 2️⃣ Requirement Validation Summary

### R1 — Home page storefront
#### Test TC001 Browse the home page storefront
- **Test Code:** [TC001_Browse_the_home_page_storefront.py](./TC001_Browse_the_home_page_storefront.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0be3d242-4497-46a9-b892-a4cd8252fa2a/a2587f2b-9921-49aa-a979-f59d459cff7f
- **Status:** ✅ Passed
- **Analysis / Findings:** Hero, trust strip, Top Picks, categories, Scout process, blog and newsletter sections all render; domain migration did not affect the storefront bootstrap (vendored React, no CDN dependency).
---

#### Test TC002 Browse the home storefront and open a featured product
- **Test Code:** [TC002_Browse_the_home_storefront_and_open_a_featured_product.py](./TC002_Browse_the_home_storefront_and_open_a_featured_product.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0be3d242-4497-46a9-b892-a4cd8252fa2a/31abd85b-8d7e-4147-8027-f9994152b7f4
- **Status:** ✅ Passed
- **Analysis / Findings:** Clicking a Top Picks card image/title opens the internal ToyScout product detail view (openPick0–openPick5 wiring), while the separate "View on Amazon" CTA links externally. The fix from the previous session remains intact.
---

### R2 — Shop category browsing & product detail
#### Test TC005 Inspect a shop category product and open the affiliate link
- **Test Code:** [TC005_Inspect_a_shop_category_product_and_open_the_affiliate_link.py](./TC005_Inspect_a_shop_category_product_and_open_the_affiliate_link.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0be3d242-4497-46a9-b892-a4cd8252fa2a/68a80835-f288-40db-bcd1-8dbdcca8f9a9
- **Status:** ✅ Passed
- **Analysis / Findings:** Category grids render real scraped products; "View on Amazon" resolves to a real `amazon.com/dp/<ASIN>` URL (now carrying the `kolico-20` Associates tag as of this session's follow-up change).
---

#### Test TC008 Review the full product details before buying
- **Test Code:** [TC008_Review_the_full_product_details_before_buying.py](./TC008_Review_the_full_product_details_before_buying.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0be3d242-4497-46a9-b892-a4cd8252fa2a/a4107450-c0cc-4f3d-8ab8-c8179c720af2
- **Status:** ✅ Passed
- **Analysis / Findings:** Product detail page shows title, price, rating, review count, sales rank, gallery images, bullets and reviews sourced from the scraped Amazon data.
---

### R3 — Blog
#### Test TC012 Read a full blog post and return to the blog list
- **Test Code:** [TC012_Read_a_full_blog_post_and_return_to_the_blog_list.py](./TC012_Read_a_full_blog_post_and_return_to_the_blog_list.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0be3d242-4497-46a9-b892-a4cd8252fa2a/87e87ee2-5486-400a-9311-bcde983b0eda
- **Status:** ✅ Passed
- **Analysis / Findings:** Blog list → post → back navigation works with hash routing preserved.
---

### R4 — Legal & compliance pages
#### Test TC015 Open a legal page from the footer and return home
- **Test Code:** [TC015_Open_a_legal_page_from_the_footer_and_return_home.py](./TC015_Open_a_legal_page_from_the_footer_and_return_home.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0be3d242-4497-46a9-b892-a4cd8252fa2a/c084ac7d-c00a-458f-b9b3-527eaf7a2952
- **Status:** ✅ Passed
- **Analysis / Findings:** Privacy/Terms/Disclosure footer links open the correct overlay views and return home cleanly.
---

### R5 — Newsletter signup
#### Test TC017 Subscribe to the newsletter successfully
- **Test Code:** [TC017_Subscribe_to_the_newsletter_successfully.py](./TC017_Subscribe_to_the_newsletter_successfully.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0be3d242-4497-46a9-b892-a4cd8252fa2a/bd1252d0-54cc-4b5f-b83a-f42428bce029
- **Status:** ✅ Passed
- **Analysis / Findings:** Valid email shows the success state.
---

#### Test TC024 Prevent newsletter submission with an empty email
- **Test Code:** [TC024_Prevent_newsletter_submission_with_an_empty_email.py](./TC024_Prevent_newsletter_submission_with_an_empty_email.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0be3d242-4497-46a9-b892-a4cd8252fa2a/462230e4-65c9-490a-a977-5516ac3f14c8
- **Status:** ✅ Passed
- **Analysis / Findings:** Empty/invalid email shows the inline validation error instead of false success (isValidEmail guard still effective).
---

### R6 — Contact form
#### Test TC021 Submit a contact message successfully
- **Test Code:** [TC021_Submit_a_contact_message_successfully.py](./TC021_Submit_a_contact_message_successfully.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0be3d242-4497-46a9-b892-a4cd8252fa2a/f6bd07a6-b474-45da-9b30-17025026b134
- **Status:** ✅ Passed
- **Analysis / Findings:** Complete submission shows the sent state.
---

#### Test TC025 Show validation when contact fields are incomplete
- **Test Code:** [TC025_Show_validation_when_contact_fields_are_incomplete.py](./TC025_Show_validation_when_contact_fields_are_incomplete.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0be3d242-4497-46a9-b892-a4cd8252fa2a/e819da40-6016-4798-9de8-d4d5ab22f048
- **Status:** ✅ Passed
- **Analysis / Findings:** Incomplete contact submission shows the inline error; direct navigation to `/contact/` (static fallback + `<base href="/">`) still resolves correctly.
---

## 3️⃣ Coverage & Matching Metrics

**10 / 10 tests passing — 100%**

| Requirement | Total Tests | ✅ Passed | ❌ Failed |
|---|---|---|---|
| R1 — Home page storefront | 2 | 2 | 0 |
| R2 — Shop category & product detail | 2 | 2 | 0 |
| R3 — Blog | 1 | 1 | 0 |
| R4 — Legal & compliance pages | 1 | 1 | 0 |
| R5 — Newsletter signup | 2 | 2 | 0 |
| R6 — Contact form | 2 | 2 | 0 |
| **Total** | **10** | **10** | **0** |

*(This run re-executed a representative subset of the 17-test suite that fully passed on the previous run; the 7 omitted tests — TC004, TC007, TC009, TC011, TC018, TC019, TC020 — cover navigation/footer flows already exercised by the passing tests above and were skipped to stay within the account's remaining TestSprite credits. The originally generated plan's 8 near-duplicate cases remain intentionally skipped.)*

---

## 4️⃣ Key Gaps / Risks

1. **Affiliate monetization gap — closed this session.** All 65+ Amazon product links previously carried no Associates tag (no commission would have been earned). The tag `kolico-20` is now applied to every `amazon.com/dp/...` link (scraped products via `AFFILIATE_TAG` in `products/fetch_products.py`, static Top Picks CTAs, JSON-LD offer URLs) and to search-fallback links via `affiliateTag()`.
2. **Forms remain local-state only (by design).** Newsletter/contact submissions are not persisted anywhere — matches the project's stated no-backend scope.
3. **Domain migration verified.** The app under test behaves identically after the `www.toyscout.net` migration; canonical/OG/JSON-LD URLs point to the new domain and all host-level redirects (apex + vercel.app) are live with valid TLS.

**Final result: all 10 executed regression tests pass. Zero known functional defects remain open.**
