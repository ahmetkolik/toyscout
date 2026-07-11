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
        
        # -> Scroll to the page footer and look for legal links such as 'Privacy' or 'Terms of Use'.
        await page.mouse.wheel(0, 300)
        
        # -> Click the 'Privacy Policy' link in the footer and verify the legal page appears.
        # Privacy Policy link
        elem = page.get_by_role('link', name='Privacy Policy', exact=True)
        await elem.click(timeout=10000)
        
        # -> Click the '← Back to home' button to return to the home page and verify the home storefront appears.
        # ← Back to home button
        elem = page.get_by_role('button', name='← Back to home', exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Verify the home page is displayed
        # Assert: The URL contains '#/' indicating the home page is displayed.
        await expect(page).to_have_url(re.compile("http://localhost:8000/\\#/"), timeout=15000), "The URL contains '#/' indicating the home page is displayed."
        await page.locator("xpath=/html/body/div[1]/div/div/section[6]/div[2]/div/input").nth(0).scroll_into_view_if_needed()
        # Assert: The newsletter email input is visible on the home page.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/section[6]/div[2]/div/input").nth(0)).to_be_visible(timeout=15000), "The newsletter email input is visible on the home page."
        await page.locator("xpath=/html/body/div[1]/div/div/nav/div/a[1]").nth(0).scroll_into_view_if_needed()
        # Assert: The 'Home' navigation link is visible in the header, confirming the home storefront is shown.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/nav/div/a[1]").nth(0)).to_be_visible(timeout=15000), "The 'Home' navigation link is visible in the header, confirming the home storefront is shown."
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
    