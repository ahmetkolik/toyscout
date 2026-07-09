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
        
        # -> Click the 'Blog' link in the top navigation to open the blog view.
        # Blog link
        elem = page.get_by_text('Home', exact=True).locator("xpath=ancestor-or-self::*[.//a][1]").get_by_role('link', name='Blog', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the 'Home' link in the top navigation to return to the main landing page.
        # Home link
        elem = page.get_by_text('Shop', exact=True).locator("xpath=ancestor-or-self::*[.//a][1]").get_by_role('link', name='Home', exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Verify the home page is displayed
        # Assert: The URL contains '#top', confirming the homepage anchor is shown.
        await expect(page).to_have_url(re.compile("\\#top"), timeout=15000), "The URL contains '#top', confirming the homepage anchor is shown."
        # Assert: The 'ToyScout' logo text is visible on the home page.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/nav/a").nth(0)).to_have_text("ToyScout", timeout=15000), "The 'ToyScout' logo text is visible on the home page."
        # Assert: The 'Home' navigation link is visible on the home page.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/nav/div/a[1]").nth(0)).to_have_text("Home", timeout=15000), "The 'Home' navigation link is visible on the home page."
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
    