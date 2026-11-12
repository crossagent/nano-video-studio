import sys
import os
import time
from playwright.sync_api import sync_playwright

profile_dir = r"D:\nano-video-studio\.browser_data"
os.makedirs(profile_dir, exist_ok=True)
screenshot_path = r"C:\Users\zhouxy\.gemini\antigravity\brain\8a8b1a5d-37b3-41a0-9766-7d40d49fda25\jimeng_initial.png"

print("Starting Edge browser for Jimeng (即梦)...")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        headless=False,
        args=["--start-maximized"],
        no_viewport=True
    )

    page = browser.pages[0] if browser.pages else browser.new_page()
    print("Navigating to https://jimeng.jianying.com/ai-tool/video/generate ...")
    page.goto("https://jimeng.jianying.com/ai-tool/video/generate", timeout=60000)
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(3)

    title = page.title()
    url = page.url
    print(f"Loaded page: {title} ({url})")

    page.screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")

    # Keep browser open for inspection / login
    print("Edge browser is open.")
