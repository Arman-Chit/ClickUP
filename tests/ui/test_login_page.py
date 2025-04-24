import allure
from pages.login_page import LoginPage
from utils.helpers import CLICKUP_EMAIL

@allure.feature("Авторизация")
class TestLoginPage:

    @allure.description("Проверка успешной авторизации и наличия элемента 'Board' после входа.")
    def test_login_success(self, logged_in_page):
        content = logged_in_page.content()
        assert 'Board' in content, "Элемент 'Board' не найден после успешного входа"

    @allure.description("Проверка невозможности авторизации с некорректными данными (негативный тест).")
    def test_login_negative(self, browser):
        page = browser.new_page()
        login_page = LoginPage(page)

        login_page.login_negative(CLICKUP_EMAIL, 'wrong_password')

        assert not page.locator("text=Board").is_visible(timeout=3000), "Невозможно залогиниться с неверными данными, но 'Board' найден"

        error_locator = page.locator("text=Incorrect email or password")
        if error_locator.count() > 0:
            assert error_locator.is_visible(), "Сообщение об ошибке авторизации не отображается"
        else:
            allure.attach(page.screenshot(), name="login_fail_screenshot", attachment_type=allure.attachment_type.PNG)
            pass
