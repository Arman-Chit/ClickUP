import allure
from pages.base_page import BasePage


@allure.feature("Login Page")
class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self._endpoint = 'login'

    USERNAME_SELECTOR = '#login-email-input'
    PASSWORD_SELECTOR = '#login-password-input'
    LOGIN_BUTTON_SELECTOR = '[data-test="login-submit"]'
    PASSWORD_INVALID_SELECTOR = '#login-password-input'
    CONTINUE_SELECTOR = "text='Continue on web anyway'"

    @allure.step("Авторизация с логином: {username} и паролем: {password}")
    def login(self, username, password):
        with allure.step("Переход на страницу входа"):
            self.navigate_to()
        with allure.step("Проверка текста 'Welcome back!' на странице"):
            self.assert_text_present_on_page('Welcome back!')
        with allure.step(f"Ввод имени пользователя {username}"):
            self.wait_for_selector_and_type(self.USERNAME_SELECTOR, username, 100)
        with allure.step(f"Заполнение поля пароля для пользователя {username}"):
            self.wait_for_selector_and_fill(self.PASSWORD_SELECTOR, password)
        with allure.step(f"Проверка значения поля с логином {username}"):
            self.assert_input_value(self.USERNAME_SELECTOR, username)
        with allure.step(f"Проверка значения поля с паролем {password}"):
            self.assert_input_value(self.PASSWORD_SELECTOR, password)
        with allure.step("Ожидание навигации после клика на кнопку входа"):
            with self.page.expect_navigation(timeout=15000):
                self.wait_for_selector_and_click(self.LOGIN_BUTTON_SELECTOR)
        with allure.step("Клик по кнопке 'Continue on web anyway', если она видна"):
            if self.page.is_visible(self.CONTINUE_SELECTOR, timeout=5000):
                self.page.click(self.CONTINUE_SELECTOR)

    @allure.step("Неудачная авторизация с логином: {username} и неверным паролем: {password_invalid}")
    def login_negative(self, username, password_invalid):
        with allure.step("Переход на страницу входа"):
            self.navigate_to()
        with allure.step(f"Ввод имени пользователя {username}"):
            self.wait_for_selector_and_type(self.USERNAME_SELECTOR, username, 100)
        with allure.step(f"Заполнение поля пароля неверным паролем {password_invalid}"):
            self.wait_for_selector_and_fill(self.PASSWORD_INVALID_SELECTOR, password_invalid)