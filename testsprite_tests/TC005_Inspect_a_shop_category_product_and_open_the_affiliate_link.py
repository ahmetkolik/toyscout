import asyncio
import re
from playwright import async_api
from playwright.async_api import expect

async def run_test():
    pw = None
    browser = None
    context = None

    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()

        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",
                "--disable-dev-shm-usage",
                "--ipc=host",
                "--single-process"
            ],
        )

        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        # Wider default timeout to match the agent's DOM-stability budget;
        # auto-waiting Playwright APIs (expect, locator.wait_for) inherit this.
        context.set_default_timeout(15000)

        # Open a new page in the browser context
        page = await context.new_page()

        # Interact with the page elements to simulate user flow
        # -> navigate
        await page.goto("http://localhost:8000")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Load the homepage (http://localhost:8000) and wait for the SPA to render so the 'Shop' link and product list appear.
        await page.goto("http://localhost:8000/")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Click the 'Shop' link in the top navigation to open the Shop view.
        # Shop link
        elem = page.get_by_role('link', name='Shop', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the 'Action Figures & Statues' category button to open that category's product list.
        # Action Figures & Statues button
        elem = page.locator('xpath=/html/body/div/div/div/div/div/div[3]/button')
        await elem.click(timeout=10000)
        
        # -> Open the 'Disney Store Official Buzz Lightyear Interactive Talking Action Figure' product detail by clicking its product title on the category page.
        # Disney Store Official Buzz Lightyear Interactive...
        elem = page.locator('xpath=/html/body/div/div/div/div/div/div[5]/article/h3')
        await elem.click(timeout=10000)
        
        # -> Click the 'View on Amazon' button to follow the affiliate link to Amazon and verify the navigation.
        # View on Amazon link
        elem = page.get_by_text('$39.95 · 4.7★ 7,141 ratings', exact=True).locator("xpath=ancestor-or-self::*[.//a][1]").get_by_role('link', name='View on Amazon', exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Verify the product detail view is displayed
        # Assert: The product summary header is present on the product detail view.
        await expect(page.locator("xpath=/html/body/div[1]/div[1]/div[1]/h1").nth(0)).to_contain_text("Product summary presents key product information", timeout=15000), "The product summary header is present on the product detail view."
        # Assert: The breadcrumb shows the product is in the Action Figures category.
        await expect(page.locator("xpath=/html/body/div[1]/div[1]/div[2]/div[1]/div[4]/div/div/div").nth(0)).to_contain_text("Action Figures", timeout=15000), "The breadcrumb shows the product is in the Action Figures category."
        await page.locator("xpath=/html/body/div[1]/div[1]/div[2]/div[5]/div[4]/div[3]/div/a").nth(0).scroll_into_view_if_needed()
        # Assert: The 'Visit the Disney Store Store' link is visible on the product detail view.
        await expect(page.locator("xpath=/html/body/div[1]/div[1]/div[2]/div[5]/div[4]/div[3]/div/a").nth(0)).to_be_visible(timeout=15000), "The 'Visit the Disney Store Store' link is visible on the product detail view."
        
        # --> Verify the affiliate call to action is available
        # Assert: Affiliate link opened the Amazon product URL amazon.com/dp/B07PQFT83F.
        await expect(page).to_have_url(re.compile("amazon\\.com/dp/B07PQFT83F"), timeout=15000), "Affiliate link opened the Amazon product URL amazon.com/dp/B07PQFT83F."
        await page.locator("xpath=/html/body/div[1]/div[1]/div[2]/div[5]/div[4]/div[3]/div/a").nth(0).scroll_into_view_if_needed()
        # Assert: The Amazon product page shows the 'Visit the Disney Store Store' link, confirming the affiliate destination loaded product content.
        await expect(page.locator("xpath=/html/body/div[1]/div[1]/div[2]/div[5]/div[4]/div[3]/div/a").nth(0)).to_be_visible(timeout=15000), "The Amazon product page shows the 'Visit the Disney Store Store' link, confirming the affiliate destination loaded product content."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    