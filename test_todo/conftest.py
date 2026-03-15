import allure
import pytest

from test_todo.test_todo_simple import _allure_get_page_by_nodeid


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    if report.failed:
        nodeid = (item.nodeid or "").replace("\\", "/")
        page = _allure_get_page_by_nodeid(nodeid)
        if page is None:
            print(f"[allure-screenshot] page not found for nodeid={nodeid}")
            return

        try:
            allure.attach(
                page.screenshot(full_page=True),
                name="失败截图",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as e:
            print(f"[allure-screenshot] attach failed for nodeid={nodeid}: {e}")
