import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

profile_dir = r"D:\nano-video-studio\.browser_data"
os.makedirs(profile_dir, exist_ok=True)

screenshot_live = r"C:\Users\zhouxy\.gemini\antigravity\brain\8a8b1a5d-37b3-41a0-9766-7d40d49fda25\jimeng_live.png"
status_file = r"D:\nano-video-studio\tasks\comfyui\video-act01-shot02-reference-test\jimeng_status.json"

def log(msg):
    print(f"[Jimeng Agent] {msg}", flush=True)

def update_status(data):
    try:
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"Status write error: {e}")

log("启动 Edge 浏览器 (已指定独立持久化用户数据目录)...")
update_status({"status": "starting", "time": time.time()})

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        headless=False,
        args=["--start-maximized"],
        no_viewport=True
    )

    page = browser.pages[0] if browser.pages else browser.new_page()
    log("正在导航至: https://jimeng.jianying.com/ai-tool/video/generate ...")

    try:
        page.goto("https://jimeng.jianying.com/ai-tool/video/generate", timeout=60000)
    except Exception as e:
        log(f"Navigation warning: {e}")

    time.sleep(3)
    page.screenshot(path=screenshot_live)
    log(f"初始页面截图已保存至: {screenshot_live}")

    log(f"当前页面标题: {page.title()} | URL: {page.url}")

    # Loop to monitor login status
    while True:
        try:
            curr_url = page.url
            curr_title = page.title()
            page.screenshot(path=screenshot_live)

            # Check login indicators
            # On jimeng, when logged in: URL stays on /ai-tool/video/generate, or has user avatar / points
            # If not logged in, usually redirected or has '去登录' button
            buttons = page.locator("button, a").all_inner_texts()
            buttons = [b.strip() for b in buttons if b and b.strip()]

            is_login_needed = any("登录" in b for b in buttons[:20])
            is_video_tool = "ai-tool/video" in curr_url

            # Check if login modal is already open
            modal_open = page.locator(".lv-modal-wrapper").count() > 0

            # If login button exists and modal not yet open, click it to pop up the login window for user
            if is_login_needed and not modal_open:
                login_btn = page.locator("text=请先登录").first
                if login_btn.count() > 0 and login_btn.is_visible():
                    log("发现【请先登录】按钮，正在自动点击弹出登录窗口以便扫码...")
                    try:
                        login_btn.click(timeout=3000)
                    except Exception as ce:
                        log(f"Click login button info: {ce}")
            elif modal_open:
                log("登录弹窗（扫码/手机号）已在屏幕上显示，等待用户完成登录...")

            status_data = {
                "status": "ready" if (is_video_tool and not is_login_needed) else "waiting_login",
                "url": curr_url,
                "title": curr_title,
                "login_needed": is_login_needed,
                "buttons_sample": buttons[:10],
                "time": time.time()
            }
            update_status(status_data)

            if is_video_tool and not is_login_needed:
                log("检测到已登录且位于视频生成页面！")
                break
            else:
                log(f"状态: 等待登录/就绪 | URL: {curr_url}")

        except Exception as e:
            log(f"Loop error: {e}")

        time.sleep(5)

    log("进入创作组件解析流程...")
    time.sleep(3)
    page.screenshot(path=screenshot_live)

    # Inspect model selectors, upload controls, textareas
    inputs_info = page.locator("input, textarea, button").evaluate_all("""
        elements => elements.map(e => ({
            tag: e.tagName,
            type: e.type || '',
            placeholder: e.placeholder || '',
            text: (e.innerText || '').slice(0, 30),
            id: e.id || '',
            className: e.className || ''
        }))
    """)

    update_status({
        "status": "analyzing_ui",
        "url": page.url,
        "title": page.title(),
        "elements_count": len(inputs_info),
        "inputs_info": inputs_info[:30],
        "time": time.time()
    })

    log("UI 组件解析完成，保持浏览器运行...")
    while True:
        time.sleep(10)
