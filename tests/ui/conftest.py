import pytest
import allure
from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage
from utils.helpers import CLICKUP_EMAIL, CLICKUP_PASSWORD

@ pytest.fixture(scope="session")
def playwright_instance():
    with allure.step("Инициализация Playwright"):
        playwright = sync_playwright().start()
    yield playwright
    with allure.step("Остановка Playwright"):
        playwright.stop()

@ pytest.fixture(scope="session")
def browser(playwright_instance):
    with allure.step("Запуск браузера Chromium (headful режим)"):
        # Всегда запускаем браузер с интерфейсом (headful)
        browser = playwright_instance.chromium.launch(headless=False, slow_mo=1000)
    yield browser
    with allure.step("Закрытие браузера"):
        browser.close()

@ pytest.fixture(scope="session")
def logged_in_page(browser):
    with allure.step("Создание контекста и новой страницы"):
        context = browser.new_context()
        page = context.new_page()
    with allure.step("Авторизация на сайте"):
        LoginPage(page).login(CLICKUP_EMAIL, CLICKUP_PASSWORD)

    yield page

    with allure.step("Закрытие браузерного контекста"):
        context.close()