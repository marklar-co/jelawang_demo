from __future__ import annotations

import os


async def run_jira_browser_search(base_url: str, query: str, open_top: bool = True) -> dict[str, object]:
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError(
            "Playwright is not installed. Run: pip install -r requirements.txt && playwright install chromium"
        ) from exc

    default_headless = "0" if os.getenv("DISPLAY") else "1"
    headless = os.getenv("BROWSER_DEMO_HEADLESS", default_headless) != "0"
    slow_mo = 250 if not headless else 0
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=headless, slow_mo=slow_mo)
        page = await browser.new_page(viewport={"width": 1360, "height": 860})
        try:
            await page.goto(f"{base_url.rstrip('/')}/jira", wait_until="networkidle")
            await page.locator('[data-testid="jira-search-input"]').fill(query)
            await page.wait_for_timeout(250)

            rows = page.locator("[data-issue-key]")
            matches = []
            for index in range(await rows.count()):
                row = rows.nth(index)
                key = await row.get_attribute("data-issue-key")
                status = await row.locator('[data-testid="issue-status"]').inner_text()
                summary = await row.locator('[data-testid="issue-summary"]').inner_text()
                matches.append({"key": key, "status": status, "summary": summary})

            opened = None
            if open_top and matches:
                await rows.first.click()
                await page.wait_for_selector('[data-testid="selected-issue-key"]')
                opened = {
                    "key": await page.locator('[data-testid="selected-issue-key"]').inner_text(),
                    "summary": await page.locator('[data-testid="selected-issue-summary"]').inner_text(),
                    "status": await page.locator('[data-testid="selected-issue-status"]').inner_text(),
                }
                if not headless:
                    await page.wait_for_timeout(1200)

            return {"query": query, "matches": matches, "opened": opened, "headless": headless}
        finally:
            await browser.close()
