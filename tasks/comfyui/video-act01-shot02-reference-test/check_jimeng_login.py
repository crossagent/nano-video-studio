import time
from playwright.sync_api import sync_playwright

screenshot_path = r"C:\Users\zhouxy\.gemini\antigravity\brain\8a8b1a5d-37b3-41a0-9766-7d40d49fda25\jimeng_login_modal.png"

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        headless=True
    )
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()

    page.goto("https://jimeng.jianying.com/ai-tool/home", wait_until="networkidle", timeout=45000)
    time.sleep(2)

    # Click login button
    login_btn = page.locator("text=去登录").first
    if login_btn.count() > 0:
        print("Found login button, clicking...")
        login_btn.click()
        time.sleep(3)
        page.screenshot(path=screenshot_path)
        print(f"Login modal screenshot saved to {screenshot_path}")
    else:
        print("Login button not found directly.")
        page.screenshot(path=screenshot_path)

    browser.close()
