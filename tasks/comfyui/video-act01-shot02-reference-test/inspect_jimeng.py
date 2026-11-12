import json
import time
from playwright.sync_api import sync_playwright

screenshot_path = r"C:\Users\zhouxy\.gemini\antigravity\brain\8a8b1a5d-37b3-41a0-9766-7d40d49fda25\jimeng_page.png"

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        headless=True
    )
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()

    print("Navigating to https://jimeng.jianying.com/ai-tool/video/generate ...")
    page.goto("https://jimeng.jianying.com/ai-tool/video/generate", wait_until="networkidle", timeout=45000)
    time.sleep(3)

    print("Current URL:", page.url)
    print("Page Title:", page.title())

    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")

    # Check for login buttons or user profile
    buttons = page.locator("button, a").all_inner_texts()
    buttons = [b.strip() for b in buttons if b.strip()]
    print("Buttons found (sample):", buttons[:25])

    # Check for textareas or inputs
    placeholders = page.locator("textarea, input").evaluate_all(
        "elements => elements.map(e => ({tag: e.tagName, type: e.type, placeholder: e.placeholder, id: e.id, class: e.className}))"
    )
    print("Inputs/Textareas found:", json.dumps(placeholders[:10], indent=2, ensure_ascii=False))

    browser.close()
