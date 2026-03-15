import os

from playwright.sync_api import sync_playwright, expect


BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8081/")


def _launch_browser(p):
    headless_env = os.getenv("PLAYWRIGHT_HEADLESS")
    if headless_env is None:
        headless = bool(os.getenv("CI"))
    else:
        headless = headless_env == "1"

    slow_mo = int(os.getenv("PLAYWRIGHT_SLOW_MO", "0" if headless else "500"))
    return p.chromium.launch(headless=headless, slow_mo=slow_mo)


def test_duplicate_todo_issue():
    """自动化复现并验证「重复添加无提示」Issue"""
    with sync_playwright() as p:
        browser = _launch_browser(p)
        page = browser.new_page()
        page.goto(BASE_URL, timeout=10000)

        input_box = page.get_by_placeholder("What needs to be done?")
        input_box.fill("测试任务")
        page.keyboard.press("Enter")

        input_box.fill("测试任务")
        page.keyboard.press("Enter")

        todo_items = page.locator(".todo-list li")
        expect(todo_items).to_have_count(2, timeout=5000)

        warning_msg = page.locator(".warning, .error")
        expect(warning_msg).to_have_count(0, timeout=5000)

        print("✅ 复现「重复添加无提示」Issue成功！")


if __name__ == "__main__":
    test_duplicate_todo_issue()
