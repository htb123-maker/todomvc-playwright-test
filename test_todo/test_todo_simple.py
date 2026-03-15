# 导入核心playwright的核心库 sync_playwright(同步操作浏览器）、expect(断言）,导入allure库生成测试报告
from playwright.sync_api import sync_playwright, expect
import allure
import re
import time
import os


def _retry(fn, retries=3, delay_seconds=0.5):
    last_err = None
    for _ in range(retries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            time.sleep(delay_seconds)
    raise last_err


def todo_input(page):
    return page.get_by_placeholder("What needs to be done?")


def todo_items(page):
    return page.locator(".todo-list li")


def todo_item_by_text(page, text):
    return page.locator(".todo-list li", has_text=text)


def add_todo(page, text):
    input_box = todo_input(page)
    input_box.fill(text)
    page.keyboard.press("Enter")
    return input_box


def filter_links(page):
    return page.locator(".filters a")


def footer(page):
    return page.locator("footer.footer")


_ALLURE_PAGE_BY_NODEID = {}


def _allure_register_page(page):
    current = os.environ.get("PYTEST_CURRENT_TEST", "")
    nodeid = current.split(" ")[0] if current else ""
    if nodeid:
        nodeid = nodeid.replace("\\", "/")
        _ALLURE_PAGE_BY_NODEID[nodeid] = page


def _allure_get_page_by_nodeid(nodeid):
    if not nodeid:
        return None
    nodeid = nodeid.replace("\\", "/")
    return _ALLURE_PAGE_BY_NODEID.get(nodeid)
# 用例函数
# 命名语义话：test_1_single_todo ->test_前缀+序号+操作+场景，这样子可以被pytest识别
# 给用例分组，多线程执行后报告看结果
@allure.feature("核心功能测试")
# 用例标题，多线程日志日志里能快速识别
@allure.title("正常添加单个Todo")
# 多线程关键1.函数必须以test开头，pytest能快速识别，多线程也认识这个规则
def test_1_add_single_todo():
    print("🚀 测试开始：添加单个Todo")
    # 启动playwright(with语句：自动清理资源，多线程时不会残留进程
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        # 打开新的浏览器页面（多线程时，每个线程会创建独立页面，互不干扰）
        page = browser.new_page()
        _allure_register_page(page)
        print("📱 浏览器已打开")
        # 写入页面地址，设置超时时间
        page.goto("http://127.0.0.1:8081/dist/", timeout=10000)
        # 多线程关键：用语义化定位（而非硬编码xpath），避免多线程执行时元素定位失败
        # get_by_placeholder:根据输入框提示文字定位，页面布局变了也能找到，多线程更稳定
        input_box = page.get_by_placeholder("What needs to be done?")
        # 输入代办文本；多线程时每个用例输入的文本唯一
        input_box.fill("买牛奶")
        print("📝 已输入：买牛奶")
        page.keyboard.press("Enter")
        print("⏎ 按下回车")
        # 断言（验证用例是否成功，测试的核心）
        # 定位代办列表：.todo-list li是TodoMVC的代办元素
        todo_items = page.locator(".todo-list li")
        # expect:Playwright的断言
        expect(todo_items).to_have_count(1, timeout=5000)
        print("✅ 断言通过：列表中有1条Todo")
        expect(todo_items).to_have_text("买牛奶")
        print("✅ 断言通过：文本内容是'买牛奶'")
        print("🎉 测试执行成功！")
        import time
        time.sleep(3)  # 停留3秒让你看到结果
        browser.close()
        print("🔚 浏览器已关闭")

@allure.feature("核心功能测试")
@allure.title("正常添加第二个Todo（多线程测试）")
def test_2_add_second_todo():
    print("\n🚀 测试开始：添加第二个Todo")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        _allure_register_page(page)
        print("📱 浏览器已打开")
        page.goto("http://127.0.0.1:8081/dist/", timeout=10000)

        input_box = page.get_by_placeholder("What needs to be done?")
        input_box.fill("买面包")
        print("📝 已输入：买面包")
        page.keyboard.press("Enter")
        print("⏎ 按下回车")
        todo_items = page.locator(".todo-list li")
        expect(todo_items).to_have_count(1, timeout=5000)
        print("✅ 断言通过：列表中有1条Todo")
        expect(todo_items).to_have_text("买面包")
        print("✅ 断言通过：文本内容是'买面包'")
        print("🎉 测试执行成功！")
        import time
        time.sleep(3)
        browser.close()
        print("🔚 浏览器已关闭")

@allure.feature("核心功能测试")
@allure.title("正常删除单个Todo（进阶用例）")
def test_3_delete_single_todo():
    print("\n🚀 测试开始：删除单个Todo")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        _allure_register_page(page)
        print("📱 浏览器已打开")
        page.goto("http://127.0.0.1:8081/dist/", timeout=10000)

        # 先添加1个Todo
        input_box = page.get_by_placeholder("What needs to be done?")
        input_box.fill("要删除的待办")
        print("📝 已输入：要删除的待办")
        page.keyboard.press("Enter")
        print("⏎ 按下回车")

        # 验证添加成功
        todo_items = page.locator(".todo-list li")
        expect(todo_items).to_have_count(1, timeout=5000)
        print("✅ 断言通过：列表中有1条Todo")

        # 定位并删除
        todo_item = page.locator(".todo-list li").nth(0)
        todo_item.hover()
        print("👆 悬浮显示删除按钮")
        delete_btn = todo_item.locator(".destroy")
        delete_btn.click()
        print("🗑️ 点击删除按钮")

        # 断言删除成功
        expect(page.locator(".todo-list li")).to_have_count(0, timeout=5000)
        print("✅ 断言通过：列表已为空")
        count_text = page.locator(".todo-count")
        expect(count_text).to_have_text("0 items left")
        print("✅ 断言通过：统计文本正确")
        print("🎉 测试执行成功！")
        import time
        time.sleep(3)
        browser.close()
        print("🔚 浏览器已关闭")

@allure.feature("典型bug复现")
@allure.title("添加Todo后刷新页面，验证数据丢失（持久化bug复现）")
@allure.severity(allure.severity_level.CRITICAL)
def test_4_refresh_lost_todo():
    print("\n� 测试开始：刷新后数据丢失bug复现")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        _allure_register_page(page)
        print("📱 浏览器已打开")
        page.goto("http://127.0.0.1:8081/dist/", timeout=10000)

        input_box = page.get_by_placeholder("What needs to be done?")
        input_box.fill("持久化测试任务")
        print("📝 已输入：持久化测试任务")
        page.keyboard.press("Enter")
        print("⏎ 按下回车")

        todo_items_before = page.locator(".todo-list li")
        expect(todo_items_before).to_have_count(1, timeout=5000)
        print("✅ 断言通过：刷新前列表中有1条Todo")

        page.reload(timeout=10000)
        print("🔄 页面已刷新")
        import time
        time.sleep(3)

        todo_items_after = page.locator(".todo-list li")
        expect(todo_items_after).to_have_count(0, timeout=5000)
        print("✅ 断言通过：刷新后列表为空，bug复现成功")
        print("🎉 测试执行成功！")
        browser.close()
        print("🔚 浏览器已关闭")
# ====================== 5. 重复添加相同Todo（bug复现） ======================
@allure.feature("典型bug复现")
@allure.title("重复添加相同Todo，验证重复项存在（bug复现）")
@allure.severity(allure.severity_level.CRITICAL)
def test_5_add_duplicate_todo():
    print("\n🚀 测试开始：重复添加Todo bug复现")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        _allure_register_page(page)
        print("📱 浏览器已打开")
        page.goto("http://127.0.0.1:8081/dist/", timeout=10000)

        input_box = page.get_by_placeholder("What needs to be done?")
        input_box.fill("重复测试任务")
        print("📝 已输入：重复测试任务（第1次）")
        page.keyboard.press("Enter")
        print("⏎ 按下回车")

        input_box.fill("重复测试任务")
        print("📝 已输入：重复测试任务（第2次）")
        page.keyboard.press("Enter")
        print("⏎ 按下回车")

        todo_items = page.locator(".todo-list li")
        expect(todo_items).to_have_count(2, timeout=5000)
        print("✅ 断言通过：列表中有2条Todo（重复项存在）")
        expect(todo_items.nth(0)).to_have_text("重复测试任务")
        expect(todo_items.nth(1)).to_have_text("重复测试任务")
        print("✅ 断言通过：两条都是重复测试任务")
        print("🎉 测试执行成功！")
        import time
        time.sleep(3)
        browser.close()
        print("🔚 浏览器已关闭")


# ====================== 6. 筛选Active Todo失效（核心功能bug复现） ======================
@allure.feature("核心功能测试")
@allure.title("点击Active筛选，验证仍显示已完成Todo（筛选功能bug复现）")
@allure.severity(allure.severity_level.NORMAL)
def test_6_filter_active_todo():
    print("\n🚀 测试开始：Active筛选bug复现")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        _allure_register_page(page)
        print("📱 浏览器已打开")
        page.goto("http://127.0.0.1:8081/dist/", timeout=10000)

        input_box = page.get_by_placeholder("What needs to be done?")
        input_box.fill("未完成任务")
        print("📝 已输入：未完成任务")
        page.keyboard.press("Enter")
        print("⏎ 按下回车")

        input_box.fill("已完成任务")
        print("📝 已输入：已完成任务")
        page.keyboard.press("Enter")
        print("⏎ 按下回车")

        completed_todo_toggle = page.locator(".todo-list li").nth(1).locator(".toggle")
        completed_todo_toggle.click()
        print("✅ 标记第二个Todo为完成")

        active_filter_btn = page.get_by_text("Active")
        active_filter_btn.click()
        print("🔍 点击Active筛选按钮")

        completed_todo = page.locator(".todo-list li.completed")
        expect(completed_todo).to_have_count(0, timeout=5000)
        print("✅ 断言通过：Active筛选正常工作，已完成Todo已被隐藏")
        print("🎉 测试执行成功！")
        import time
        time.sleep(3)
        browser.close()
        print("🔚 浏览器已关闭")
# ====================== 7. 超长文本添加Todo（边界值测试） ======================
@allure.feature("边界值测试")
@allure.title("添加50+字符超长文本Todo，验证页面布局与显示正常")
@allure.severity(allure.severity_level.NORMAL)
def test_7_add_long_text_todo():
    print("\n🚀 测试开始：超长文本Todo边界值测试")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        _allure_register_page(page)
        print("📱 浏览器已打开")
        page.goto("http://127.0.0.1:8081/dist/", timeout=10000)

        long_text = "这是一个超过50个字符的超长待办事项文本，用于测试输入框的边界值兼容性——测试文本长度足够长，验证页面布局是否混乱"
        print(f"📝 超长文本长度：{len(long_text)}")

        input_box = page.get_by_placeholder("What needs to be done?")
        input_box.fill(long_text)
        print("📝 已输入超长文本")
        page.keyboard.press("Enter")
        print("⏎ 按下回车")

        todo_item = page.locator(".todo-list li").nth(0)
        todo_label = todo_item.locator("label")
        expect(todo_label).to_contain_text(long_text[:30])
        print("✅ 断言通过：文本未完全截断，前30个字符可见")
        expect(todo_item).to_be_in_viewport()
        print("✅ 断言通过：Todo项在视口内，布局未混乱")
        print("🎉 测试执行成功！")
        import time
        time.sleep(3)
        browser.close()
        print("🔚 浏览器已关闭")


# ====================== 8. ESC快捷键清空输入框失效（交互bug复现） ======================
@allure.feature("交互测试")
@allure.title("输入内容后按ESC，验证输入框未清空（快捷键交互bug复现）")
@allure.severity(allure.severity_level.MINOR)
def test_8_esc_shortcut_todo():
    print("\n🚀 测试开始：ESC快捷键交互测试")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        _allure_register_page(page)
        print("📱 浏览器已打开")
        page.goto("http://127.0.0.1:8081/dist/", timeout=10000)

        input_box = page.get_by_placeholder("What needs to be done?")
        test_text = "ESC快捷键测试内容"
        input_box.fill(test_text)
        print(f"📝 已输入：{test_text}")

        page.keyboard.press("Escape")
        print("⌨️ 按下ESC键")

        expect(input_box).to_have_value(test_text)
        print("✅ 断言通过：输入框内容未清空，ESC快捷键失效")
        print("🎉 测试执行成功！")
        import time
        time.sleep(3)
        browser.close()
        print("🔚 浏览器已关闭")


# ====================== 9. 批量删除已完成Todo（批量操作测试） ======================
@allure.feature("批量操作测试")
@allure.title("批量删除已完成Todo，验证仅删除已完成项、保留未完成项")
@allure.severity(allure.severity_level.NORMAL)
def test_9_batch_delete_todo():
    print("\n🚀 测试开始：批量删除已完成Todo测试")
    import time
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        _allure_register_page(page)
        print("📱 浏览器已打开")
        page.goto("http://127.0.0.1:8081/dist/", timeout=10000)

        input_box = page.get_by_placeholder("What needs to be done?")
        input_box.fill("未完成Todo-保留")
        print("📝 已输入：未完成Todo-保留")
        page.keyboard.press("Enter")
        print("⏎ 按下回车")

        input_box.fill("已完成Todo-删除1")
        print("📝 已输入：已完成Todo-删除1")
        page.keyboard.press("Enter")
        print("⏎ 按下回车")

        input_box.fill("已完成Todo-删除2")
        print("📝 已输入：已完成Todo-删除2")
        page.keyboard.press("Enter")
        print("⏎ 按下回车")

        todo_delete_1 = page.locator('.todo-list li', has_text='已完成Todo-删除1')
        todo_delete_1_checkbox = todo_delete_1.locator('.toggle')
        todo_delete_1_checkbox.check()
        print("✅ 标记Todo '已完成Todo-删除1' 为完成")

        expect(todo_delete_1_checkbox).to_be_checked(timeout=5000)
        print("✅ '已完成Todo-删除1' 复选框已选中")
        expect(todo_delete_1).to_have_attribute("class", re.compile(r".*\bcompleted\b.*"), timeout=5000)
        print(f"🔍 '已完成Todo-删除1' li class: {todo_delete_1.get_attribute('class')}")

        todo_delete_2 = page.locator('.todo-list li', has_text='已完成Todo-删除2')
        todo_delete_2_checkbox = todo_delete_2.locator('.toggle')
        todo_delete_2_checkbox.check()
        print("✅ 标记Todo '已完成Todo-删除2' 为完成")

        expect(todo_delete_2_checkbox).to_be_checked(timeout=5000)
        print("✅ '已完成Todo-删除2' 复选框已选中")
        expect(todo_delete_2).to_have_attribute("class", re.compile(r".*\bcompleted\b.*"), timeout=5000)
        print(f"🔍 '已完成Todo-删除2' li class: {todo_delete_2.get_attribute('class')}")

        time.sleep(2)

        # 等待Clear completed按钮出现（确保有已完成项）
        clear_completed_btn = page.locator(".clear-completed")
        expect(clear_completed_btn).to_be_visible(timeout=5000)
        print("👀 Clear completed按钮已可见")
        clear_completed_btn.click()
        print("🗑️ 点击Clear completed批量删除按钮")
        time.sleep(2)

        todo_items = page.locator(".todo-list li")
        count = todo_items.count()
        print(f"🔍 删除后列表数量: {count}")
        if count > 0:
            actual_text = todo_items.nth(0).inner_text()
            print(f"🔍 第1条内容: {actual_text}")
        expect(todo_items).to_have_count(1, timeout=5000)
        print("✅ 断言通过：剩余1条Todo")
        remaining_label = todo_items.nth(0).locator("label")
        expect(remaining_label).to_have_text("未完成Todo-保留", timeout=5000)
        print("✅ 断言通过：保留的是未完成的Todo")

        if os.getenv("FORCE_TEST_9_FAIL") == "1":
            print("🧪 已开启 FORCE_TEST_9_FAIL=1，本用例将故意失败以触发Allure失败截图")
            allure.attach(
                page.screenshot(full_page=True),
                name="强制失败截图(test_9)",
                attachment_type=allure.attachment_type.PNG,
            )
            assert False, "FORCE_TEST_9_FAIL enabled"

        print("🎉 测试执行成功！")
        time.sleep(3)
        browser.close()
        print("🔚 浏览器已关闭")


# ====================== 10. 模拟iPhone 14访问TodoMVC（移动端兼容性测试） ======================
@allure.feature("移动端兼容性测试")
@allure.title("模拟iPhone 14访问TodoMVC，验证布局与交互正常")
@allure.severity(allure.severity_level.CRITICAL)  # 级别：严重（移动端是核心场景）
def test_10_mobile_iphone14_todo():
    print("\n🚀 测试开始：iPhone 14移动端兼容性测试")
    # 🔴 多线程核心：用例完全独立，每个线程独立模拟iPhone 14设备
    with sync_playwright() as p:
        # 1. 核心：模拟iPhone 14设备（Playwright内置设备配置，无需手动设置尺寸）
        # playwright.devices["iPhone 14"] 包含：屏幕尺寸390x844、像素比3、移动端UA等
        iphone_14 = p.devices["iPhone 14"]
        # 启动浏览器并应用iPhone 14配置（多线程：每个用例独立的设备模拟）
        browser = p.chromium.launch(headless=False, slow_mo=500)
        # 新建上下文：绑定iPhone 14的设备配置（关键！模拟移动端的核心）
        context = browser.new_context(**iphone_14)
        # 新建页面（基于移动端上下文）
        page = context.new_page()
        _allure_register_page(page)
        print("📱 浏览器已打开（iPhone 14设备模拟）")

        # 2. 访问TodoMVC（移动端模式）
        page.goto("http://127.0.0.1:8081/dist/", timeout=10000)  # 注意端口改成你现在用的8081
        print("🌐 已打开TodoMVC页面")

        # 3. 移动端布局验证（核心：适配性）
        # 验证1：输入框在视口内（移动端最易出“输入框被遮挡”的问题）
        input_box = todo_input(page)
        _retry(lambda: expect(input_box).to_be_in_viewport(timeout=5000))
        print("✅ 断言通过：输入框在视口内")

        # 4. 移动端交互验证（添加Todo）
        add_todo(page, "iPhone 14测试Todo")
        print("📝 已输入：iPhone 14测试Todo")
        print("⏎ 按下回车")
        # 断言添加成功（数量=1）
        items = todo_items(page)
        _retry(lambda: expect(items).to_have_count(1, timeout=5000))
        print("✅ 断言通过：列表中有1条Todo")
        # 验证2：筛选按钮（All/Active/Completed）横向排列且可见（移动端布局关键）
        # TodoMVC默认在列表为空时会隐藏footer/filters，因此必须先创建1条Todo再校验可见性
        _retry(lambda: expect(footer(page)).to_be_visible(timeout=5000))
        filters = filter_links(page)
        _retry(lambda: expect(filters).to_have_count(3, timeout=5000))
        _retry(lambda: expect(filters.nth(0)).to_be_visible(timeout=5000))
        _retry(lambda: expect(filters.nth(1)).to_be_visible(timeout=5000))
        _retry(lambda: expect(filters.nth(2)).to_be_visible(timeout=5000))
        print("✅ 断言通过：筛选按钮可见")
        # 断言Todo文本适配（未超出屏幕）
        _retry(lambda: expect(items.nth(0)).to_be_in_viewport(timeout=5000))
        print("✅ 断言通过：Todo项在视口内")
        print("🎉 测试执行成功！")
        time.sleep(3)

        # 5. 关闭资源（多线程：清理上下文+浏览器，避免内存泄漏）
        context.close()  # 移动端必须先关上下文，再关浏览器
        browser.close()
        print("🔚 浏览器已关闭")
if __name__ == "__main__":
    test_1_add_single_todo()
    test_2_add_second_todo()
    test_3_delete_single_todo()
    test_4_refresh_lost_todo()
    test_5_add_duplicate_todo()
    test_6_filter_active_todo()
    test_7_add_long_text_todo()
    test_8_esc_shortcut_todo()
    test_9_batch_delete_todo()
    test_10_mobile_iphone14_todo()
