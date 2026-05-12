#!/usr/bin/env python3
"""Drive the local fake Jira UI with an OpenAI Agents SDK agent."""

from __future__ import annotations

import asyncio
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

try:
    from agents import Agent, Runner, function_tool
except ImportError as exc:  # pragma: no cover - startup guard
    raise SystemExit(
        "The OpenAI Agents SDK is not installed. Run: pip install -r requirements.txt"
    ) from exc

try:
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError
    from playwright.async_api import async_playwright
except ImportError as exc:  # pragma: no cover - startup guard
    raise SystemExit(
        "Playwright is not installed. Run: pip install -r requirements.txt && playwright install chromium"
    ) from exc


BASE_URL = os.getenv("JIRA_DEMO_URL", "http://127.0.0.1:8000").rstrip("/")
TARGET_ISSUE = os.getenv("JIRA_DEMO_ISSUE", "JEL-102")
TARGET_STATUS = os.getenv("JIRA_DEMO_STATUS", "In Progress")


@dataclass
class BrowserState:
    playwright: object | None = None
    browser: object | None = None
    page: object | None = None


state = BrowserState()


def _read_json(url: str, *, method: str = "GET") -> dict:
    request = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def _preflight() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is not set. Start the FastAPI app, export OPENAI_API_KEY, then run this script."
        )

    try:
        _read_json(f"{BASE_URL}/api/issues")
    except urllib.error.URLError as exc:
        raise SystemExit(
            f"Could not reach {BASE_URL}. Start the app with: uvicorn app:app --reload"
        ) from exc


async def _page():
    if state.page is not None:
        return state.page

    headless = os.getenv("JIRA_DEMO_HEADLESS", "1") != "0"
    state.playwright = await async_playwright().start()
    state.browser = await state.playwright.chromium.launch(headless=headless)
    state.page = await state.browser.new_page(viewport={"width": 1440, "height": 900})
    return state.page


async def _close_browser() -> None:
    if state.browser is not None:
        await state.browser.close()
        state.browser = None
        state.page = None
    if state.playwright is not None:
        await state.playwright.stop()
        state.playwright = None


async def _selected_issue_text() -> str:
    page = await _page()
    key = await page.locator('[data-testid="selected-issue-key"]').inner_text()
    summary = await page.locator('[data-testid="selected-issue-summary"]').inner_text()
    status = await page.locator('[data-testid="selected-issue-status"]').inner_text()
    assignee = await page.locator('[data-testid="selected-issue-assignee"]').inner_text()
    return f"{key} | {status} | {assignee} | {summary}"


@function_tool
async def reset_fake_jira() -> str:
    """Reset the local fake Jira demo data to its seed state."""
    payload = await asyncio.to_thread(_read_json, f"{BASE_URL}/api/reset", method="POST")
    issue_count = len(payload["issues"])
    return f"Reset fake Jira to {issue_count} seed issues."


@function_tool
async def open_fake_jira() -> str:
    """Open the fake Jira UI in a browser."""
    page = await _page()
    await page.goto(f"{BASE_URL}/jira", wait_until="networkidle")
    await page.wait_for_selector('[data-testid="issue-list"]', timeout=5000)
    return f"Opened fake Jira at {BASE_URL}/jira."


@function_tool
async def read_visible_issues() -> str:
    """Read the visible issues from the fake Jira issue list."""
    page = await _page()
    rows = page.locator('[data-issue-key]')
    lines = []
    for index in range(await rows.count()):
        row = rows.nth(index)
        key = await row.get_attribute("data-issue-key")
        status = await row.locator('[data-testid="issue-status"]').inner_text()
        summary = await row.locator('[data-testid="issue-summary"]').inner_text()
        lines.append(f"{key} | {status} | {summary}")
    return "\n".join(lines)


@function_tool
async def open_issue(issue_key: str) -> str:
    """Open an issue by key in the fake Jira UI."""
    page = await _page()
    selector = f'[data-testid="issue-row-{issue_key}"]'
    try:
        await page.locator(selector).click(timeout=5000)
        await page.wait_for_selector('[data-testid="selected-issue-key"]', timeout=5000)
    except PlaywrightTimeoutError as exc:
        raise RuntimeError(f"Could not open issue {issue_key}") from exc
    return await _selected_issue_text()


@function_tool
async def transition_selected_issue(target_status: str) -> str:
    """Transition the currently selected issue to the requested status using the UI controls."""
    page = await _page()
    try:
        await page.locator('[data-testid="status-select"]').select_option(target_status)
        await page.locator('[data-testid="transition-button"]').click()
        await page.wait_for_selector(
            f'[data-testid="selected-issue-status"]:has-text("{target_status}")',
            timeout=5000,
        )
    except PlaywrightTimeoutError as exc:
        raise RuntimeError(f"Could not transition selected issue to {target_status}") from exc
    return await _selected_issue_text()


@function_tool
async def read_selected_issue() -> str:
    """Read the issue currently selected in the fake Jira UI."""
    return await _selected_issue_text()


async def main() -> int:
    _preflight()

    model = os.getenv("OPENAI_AGENT_MODEL") or None
    agent = Agent(
        name="Fake Jira browser operator",
        model=model,
        instructions=(
            "You operate a local fake Jira UI through browser tools. "
            "Use the browser tools to reset the demo, open the UI, inspect the visible issues, "
            "open the requested issue, transition it to the requested status, and verify the final status. "
            "Keep the final answer to one concise sentence with the issue key and final status."
        ),
        tools=[
            reset_fake_jira,
            open_fake_jira,
            read_visible_issues,
            open_issue,
            transition_selected_issue,
            read_selected_issue,
        ],
    )

    try:
        result = await Runner.run(
            agent,
            input=(
                f"Transition {TARGET_ISSUE} to {TARGET_STATUS} in the fake Jira UI, "
                "then verify the selected issue status."
            ),
            max_turns=12,
        )
        print(result.final_output)
    finally:
        await _close_browser()

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
