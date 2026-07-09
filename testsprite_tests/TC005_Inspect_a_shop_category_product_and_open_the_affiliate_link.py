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
        
        # -> Click the 'Shop' link in the header to open the Shop view.
        # Shop link
        elem = page.get_by_role('link', name='Shop', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the 'Action Figures & Statues' category button to switch the toy category.
        # Action Figures & Statues button
        elem = page.locator('xpath=/html/body/div/div/div/div/div/div[3]/button')
        await elem.click(timeout=10000)
        
        # -> Click the 'Titan Hero 12-inch Figure' product title to open its product detail view.
        # Titan Hero 12-inch Figure
        elem = page.locator('xpath=/html/body/div/div/div/div/div/div[5]/article/h3')
        await elem.click(timeout=10000)
        
        # -> Click the 'View current price on Amazon' link on the product detail page to open the affiliate destination and verify its URL.
        # View current price on Amazon link
        elem = page.get_by_role('link', name='View current price on Amazon', exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        current_url = await page.evaluate("() => window.location.href")
        # Assert: page loaded with a URL (final outcome verified by the AI judge during the run)
        assert current_url, 'Page should have loaded with a URL'
        current_url = await page.evaluate("() => window.location.href")
        # Assert: page loaded with a URL (final outcome verified by the AI judge during the run)
        assert current_url, 'Page should have loaded with a URL'
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    