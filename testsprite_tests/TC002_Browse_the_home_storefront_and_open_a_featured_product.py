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
        
        # -> Scroll down to the 'Trending this week' (best sellers) home section and click the product title 'PartyWoo White Balloons 140 pcs...' to open the featured product.
        await page.mouse.wheel(0, 300)
        
        # -> Scroll down to the 'Trending this week' (best sellers) home section and click the product title 'PartyWoo White Balloons 140 pcs...' to open the featured product.
        # PartyWoo White Balloons 140 pcs Different Sizes...
        elem = page.get_by_text('PartyWoo White Balloons 140 pcs Different Sizes of 18 12 10…', exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Verify the product detail view is displayed
        # Assert: The URL contains '#/product/party/0', indicating the product detail view is open.
        await expect(page).to_have_url(re.compile("\\#/product/party/0"), timeout=15000), "The URL contains '#/product/party/0', indicating the product detail view is open."
        # Assert: The product price '$8.99' is visible on the product detail page.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div[1]/div[3]/div[1]/div/div[2]/span[2]/span").nth(0)).to_have_text("$8.99", timeout=15000), "The product price '$8.99' is visible on the product detail page."
        # Assert: The product rating '4.5' is displayed on the product detail page.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div[2]/span[2]/span[1]").nth(0)).to_have_text("4.5", timeout=15000), "The product rating '4.5' is displayed on the product detail page."
        # Assert: The affiliate link 'View current price on Amazon' is present on the product detail page.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div[4]/a").nth(0)).to_have_text("View current price on Amazon", timeout=15000), "The affiliate link 'View current price on Amazon' is present on the product detail page."
        
        # --> Verify the product information is displayed
        # Assert: Product price $8.99 is visible on the product page.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div[1]/div[3]/div[1]/div/div[2]/span[2]/span").nth(0)).to_have_text("$8.99", timeout=15000), "Product price $8.99 is visible on the product page."
        # Assert: Product rating 4.5 is visible on the product page.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div[2]/span[2]/span[1]").nth(0)).to_have_text("4.5", timeout=15000), "Product rating 4.5 is visible on the product page."
        # Assert: Product ratings count 6,605 is visible on the product page.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div[2]/span[2]/span[2]").nth(0)).to_have_text("6,605", timeout=15000), "Product ratings count 6,605 is visible on the product page."
        # Assert: The affiliate 'View on Amazon' link is visible on the product page.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div[2]/div/a").nth(0)).to_have_text("View on Amazon", timeout=15000), "The affiliate 'View on Amazon' link is visible on the product page."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    