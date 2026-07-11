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
        
        # -> Click the 'Shop' link in the top navigation to open the Shop view.
        # Shop link
        elem = page.get_by_role('link', name='Shop', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the 'Action Figures & Statues' category button to open that category's product list and let the page update.
        # Action Figures & Statues button
        elem = page.locator('xpath=/html/body/div/div/div/div/div/div[3]/button')
        await elem.click(timeout=10000)
        
        # -> Open the product 'Disney Store Official Buzz Lightyear Interactive Talking Action Figure' by clicking its product title to load the product detail page.
        # Disney Store Official Buzz Lightyear Interactive...
        elem = page.locator('xpath=/html/body/div/div/div/div/div/div[5]/article/h3')
        await elem.click(timeout=10000)
        
        # -> Extract and verify the product title, price, rating, review count, the 'What we love' and 'Keep in mind' bullets, and the main product image from the product detail page.
        # [internal] extract_content: 
        
        # -> Click the first 'Product photo' thumbnail button beneath the main image to open the image viewer or load the full product image.
        # Product photo button
        elem = page.locator('xpath=/html/body/div/div/div/div/div/div[2]/div/div[2]/button')
        await elem.click(timeout=10000)
        
        # -> Click the second product photo thumbnail (a button labeled 'Product photo') to try to open the image viewer or load the full product image.
        # Product photo button
        elem = page.locator('xpath=/html/body/div/div/div/div/div/div[2]/div/div[2]/button[2]')
        await elem.click(timeout=10000)
        
        # -> Click the third 'Product photo' thumbnail (the next thumbnail beneath the main image) to open the image viewer or load the full product image, then wait for the UI to update.
        # Product photo button
        elem = page.locator('xpath=/html/body/div/div/div/div/div/div[2]/div/div[2]/button[3]')
        await elem.click(timeout=10000)
        
        # -> Extract image URLs and descriptive attributes from all visible product images on the product detail page.
        await page.mouse.wheel(0, 300)
        
        # -> Run a structured page extract to retrieve the product title, price, rating, review count, both bullet lists ('What we love' and 'Keep in mind'), and all product image URLs and descriptive attributes.
        # [internal] extract_content: 
        
        # --> Assertions to verify final state
        
        # --> Verify the product title, price, rating, review count, bullets, and image are displayed
        # Assert: The product title 'Disney Store Official Buzz Lightyear' is visible.
        await expect(page.locator("xpath=/html/body/div/div/div/section[2]/div/div[3]/article[3]/h3").nth(0)).to_contain_text("Disney Store Official Buzz Lightyear", timeout=15000), "The product title 'Disney Store Official Buzz Lightyear' is visible."
        # Assert: The product price $39.95 is displayed.
        await expect(page.locator("xpath=/html/body/div/div/div/div/div[2]/div/div/div[2]/span[1]").nth(0)).to_have_text("$39.95", timeout=15000), "The product price $39.95 is displayed."
        # Assert: The product rating 4.7 is displayed.
        await expect(page.locator("xpath=/html/body/div/div/div/div/div[2]/div/div/div[2]/span[2]").nth(0)).to_have_text("4.7", timeout=15000), "The product rating 4.7 is displayed."
        # Assert: The product review count 7,141 is displayed.
        await expect(page.locator("xpath=/html/body/div/div/div/div/div[2]/div/div/div[2]/span[3]").nth(0)).to_have_text("7,141", timeout=15000), "The product review count 7,141 is displayed."
        
        # --> Verify the product detail content is complete
        # Assert: The product price $39.95 is shown on the product detail page.
        await expect(page.locator("xpath=/html/body/div/div/div/div/div[2]/div/div/div[2]/span[1]").nth(0)).to_have_text("$39.95", timeout=15000), "The product price $39.95 is shown on the product detail page."
        # Assert: The product rating '4.7' is shown on the product detail page.
        await expect(page.locator("xpath=/html/body/div/div/div/div/div[2]/div/div/div[2]/span[2]").nth(0)).to_have_text("4.7", timeout=15000), "The product rating '4.7' is shown on the product detail page."
        # Assert: The product review count '7,141' is shown on the product detail page.
        await expect(page.locator("xpath=/html/body/div/div/div/div/div[2]/div/div/div[2]/span[3]").nth(0)).to_have_text("7,141", timeout=15000), "The product review count '7,141' is shown on the product detail page."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    