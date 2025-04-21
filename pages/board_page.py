import allure
from pages.base_page import BasePage
from playwright.sync_api import expect
import json


@allure.feature("Board Page")
class BoardPage(BasePage):
    BOARD_BUTTON_SELECTOR = '[data-test="data-view-item__Board"]'
    COMPLETE_SELECTOR = "[data-test='board-header']"
    DELETE_TASK_SELECTOR = ".nav-menu-item__name >> text='Delete'"
    TASK_NAME = '.open-task-clickable-area.ng-star-inserted'
    CREATE_BUTTON_SELECTOR = '[data-test="board-group-header__create-task-button__to do"]'
    TASK_NAME_INPUT = '[data-test="quick-create-task-panel__panel-board__input"]'
    SAVE_BUTTON_SELECTOR = '[data-test="quick-create-task-panel__panel-board__enter-button"]'

    def __init__(self, page):
        super().__init__(page)
        self._endpoint = '90131041433/v/l/2ky3n34t-313'

    @allure.step("Навигация на доску")
    def navigate_to_board(self):
        with allure.step("Переход на главную страницу доски"):
            self.navigate_to()
        with allure.step("Клик по кнопке 'Board'"):
            self.wait_for_selector_and_click(self.BOARD_BUTTON_SELECTOR)

    @staticmethod
    @allure.step("Получение селектора для опций задачи: {task_name}")
    def get_task_option_selector(task_name):
        return f'[data-test="board-task__ellipsis-menu__{task_name}"]'

    @allure.step("Ожидание, пока задача {task_name} станет видимой")
    def wait_for_task_visible(self, task_name: str, timeout=15000):
        with allure.step(f"Ожидание видимости задачи {task_name}"):
            selector = f"text={json.dumps(task_name)}"
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)

    @allure.step("Проверка видимости задачи {task_name}")
    def is_task_visible(self, task_name: str):
        with allure.step(f"Проверка, что задача {task_name} видима на доске"):
            expect(self.page.locator(f"text={json.dumps(task_name)}")).to_be_visible()

    @allure.step("Удаление задачи {task_name}")
    def delete_task(self, task_name: str):
        task_selector = f'[data-test="board-task__name-link__{task_name}"]'
        with allure.step(f"Наведение на задачу '{task_name}'"):
            self.page.locator(task_selector).hover()

        more_button_selector = f'[data-test="board-actions-menu__ellipsis__{task_name}"]'
        with allure.step("Клик по кнопке меню '...'"):
            self.wait_for_selector_and_click(more_button_selector)

        with allure.step("Клик по пункту 'Delete'"):
            self.wait_for_selector_and_click(self.DELETE_TASK_SELECTOR)

        with allure.step(f"Проверка, что задача '{task_name}' исчезла"):
            self.page.wait_for_selector(task_selector, state="detached", timeout=10000)

    @allure.step("Создание задачи через UI с именем: {task_name}")
    def create_task_ui(self, task_name):
        with allure.step("Клик по кнопке создания задачи"):
            self.wait_for_selector_and_click(self.CREATE_BUTTON_SELECTOR)

        with allure.step(f"Ввод имени задачи: {task_name}"):
            self.wait_for_selector_and_type(self.TASK_NAME_INPUT, task_name, delay=100)

        with allure.step("Клик по кнопке сохранения задачи"):
            self.wait_for_selector_and_click(self.SAVE_BUTTON_SELECTOR)