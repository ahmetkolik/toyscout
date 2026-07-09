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
        
        # -> Scroll down to reveal the 'Trending this week' / Top Picks section and click the 'Coast Wooden Balance Bike' product image to open its product detail view.
        await page.mouse.wheel(0, 300)
        
        # -> Scroll down to reveal the 'Trending this week' / Top Picks section and click the 'Coast Wooden Balance Bike' product image to open its product detail view.
        # Coast Wooden Balance Bike
        elem = page.locator('xpath=/html/body/div/div/div/section[2]/div/div[3]/article/div/img')
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Verify the product detail view is displayed
        # Assert: The URL shows the product detail path for the clicked item.
        await expect(page).to_have_url(re.compile("\\#/product/sports\\-outdoor/0"), timeout=15000), "The URL shows the product detail path for the clicked item."
        # Assert: The product detail page displays the 'View current price on Amazon' link.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div[3]/a").nth(0)).to_have_text("View current price on Amazon", timeout=15000), "The product detail page displays the 'View current price on Amazon' link."
        # Assert: The product detail page shows the product ratings count '9,214'.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div[1]/div[3]/div[2]/div/div[10]/span").nth(0)).to_have_text("9,214", timeout=15000), "The product detail page shows the product ratings count '9,214'."
        
        # --> Verify the product information is displayed
        # Assert: The product age range '3–5' is displayed on the product detail page.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div[1]/span[2]/span").nth(0)).to_have_text("3\u20135", timeout=15000), "The product age range '3\u20135' is displayed on the product detail page."
        # Assert: The product ratings count '9,214' is displayed on the product detail page.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div[2]/div/div/div[2]/span[2]").nth(0)).to_have_text("9,214", timeout=15000), "The product ratings count '9,214' is displayed on the product detail page."
        # Assert: The 'View current price on Amazon' affiliate button is visible on the product detail page.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div[3]/a").nth(0)).to_have_text("View current price on Amazon", timeout=15000), "The 'View current price on Amazon' affiliate button is visible on the product detail page."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    