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
        
        # -> Wait for the site to finish loading and display navigation (for example a 'Blog' link or site header).
        await page.goto("http://localhost:8000/")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Click the 'Blog' navigation link in the site header to open the blog listing.
        # Blog link
        elem = page.get_by_text('Home', exact=True).locator("xpath=ancestor-or-self::*[.//a][1]").get_by_role('link', name='Blog', exact=True)
        await elem.click(timeout=10000)
        
        # -> Open the article titled 'Prime Day 2026: the toy deals actually worth grabbing' by clicking its 'Read the article ⇢' link or the article card.
        # DEALS · JUL 8, 2026 Prime Day 2026: the toy deals... link
        elem = page.locator('xpath=/html/body/div/div/div/div/div/div[2]/a')
        await elem.click(timeout=10000)
        
        # -> Verify the article title "Prime Day 2026: the toy deals actually worth grabbing" is visible, then click the "← All articles" button to return to the blog list.
        # ← All articles button
        elem = page.get_by_role('button', name='← All articles', exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> Verify the blog post content is displayed
        # Assert: The article title 'Prime Day 2026: the toy deals actually worth grabbing' is visible on the blog listing.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div/div[2]/a[1]").nth(0)).to_contain_text("Prime Day 2026: the toy deals actually worth grabbing", timeout=15000), "The article title 'Prime Day 2026: the toy deals actually worth grabbing' is visible on the blog listing."
        
        # --> Verify the blog list is displayed
        await page.locator("xpath=/html/body/div[1]/div/div/div/div/div[2]/a[1]").nth(0).scroll_into_view_if_needed()
        # Assert: The blog list shows the 'Prime Day 2026: the toy deals actually worth grabbing' article card.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div/div[2]/a[1]").nth(0)).to_be_visible(timeout=15000), "The blog list shows the 'Prime Day 2026: the toy deals actually worth grabbing' article card."
        await page.locator("xpath=/html/body/div[1]/div/div/div/div/div[2]/a[2]").nth(0).scroll_into_view_if_needed()
        # Assert: The blog list shows the 'The 7 best-selling STEM kits on Amazon right now' article card.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div/div[2]/a[2]").nth(0)).to_be_visible(timeout=15000), "The blog list shows the 'The 7 best-selling STEM kits on Amazon right now' article card."
        await page.locator("xpath=/html/body/div[1]/div/div/div/div/div[2]/a[3]").nth(0).scroll_into_view_if_needed()
        # Assert: The blog list shows the 'Screen-free summer: the outdoor toys trending this July' article card.
        await expect(page.locator("xpath=/html/body/div[1]/div/div/div/div/div[2]/a[3]").nth(0)).to_be_visible(timeout=15000), "The blog list shows the 'Screen-free summer: the outdoor toys trending this July' article card."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    