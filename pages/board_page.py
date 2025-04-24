import os
import allure
from pages.base_page import BasePage
from playwright.sync_api import expect
import json


@allure.feature("Board Page")
class BoardPage(BasePage):
    TEAM_ID = os.getenv("CLICKUP_TEAM_ID", "90131041433")
    _endpoint = f"{TEAM_ID}/v/b/t/{TEAM_ID}"
    BOARD_BUTTON = '[data-test="data-view-item__Board"]'
    BOARD_HEADER = "[data-test='board-header']"
    CREATE_BUTTON = '[data-test="board-group-header__create-task-button__to do"]'
    TASK_INPUT = '[data-test="quick-create-task-panel__panel-board__input"]'
    SAVE_BUTTON = '[data-test="quick-create-task-panel__panel-board__enter-button"]'
    DELETE_MENU_ITEM = ".nav-menu-item__name >> text='Delete'"
    VIRTUAL_SCROLL = 'cdk-virtual-scroll-viewport'
    TASK_LINK_TEMPLATE = '[data-test="board-task__name-link__{name}"]'
    ELLIPSIS_MENU_TEMPLATE = '[data-test="board-actions-menu__ellipsis__{name}"]'

    @allure.step("Навигация на доску")
    def navigate_to_board(self):
        with allure.step("Открытие доски"):
            self.page.goto(f"https://app.clickup.com/{self._endpoint}")
            self.page.wait_for_load_state("load")
            expect(self.page).to_have_url(f"https://app.clickup.com/{self._endpoint}")
        with allure.step("Клик по табу Board"):
            self.wait_for_selector_and_click(self.BOARD_BUTTON)
        with allure.step("Скролл до списка задач"):
            viewport = self.page.locator(self.VIRTUAL_SCROLL)
            if viewport.is_visible():
                viewport.scroll_to(0, 1000)

    @allure.step("Ожидание видимости задачи {task_name}")
    def wait_for_task_visible(self, task_name: str, timeout: int = 15000):
        self.page.wait_for_selector(f"text={json.dumps(task_name)}", state="visible", timeout=timeout)

    @allure.step("Проверка видимости задачи {task_name}")
    def is_task_visible(self, task_name: str) -> bool:
        selector = self.TASK_LINK_TEMPLATE.format(name=json.dumps(task_name))
        return self.page.locator(selector).is_visible()

    @allure.step("Создание задачи через UI: {task_name}")
    def create_task_ui(self, task_name: str):
        self.wait_for_selector_and_click(self.CREATE_BUTTON)
        self.wait_for_selector_and_type(self.TASK_INPUT, task_name, delay=100)
        self.wait_for_selector_and_click(self.SAVE_BUTTON)
        self.page.wait_for_selector(self.TASK_LINK_TEMPLATE.format(name=json.dumps(task_name)))

    @allure.step("Удаление задачи {task_name}")
    def delete_task(self, task_name: str):
        task_selector = self.TASK_LINK_TEMPLATE.format(name=task_name)
        ellipsis_selector = self.ELLIPSIS_MENU_TEMPLATE.format(name=task_name)

        with allure.step("Наведение на задачу"):
            self.page.locator(task_selector).hover()
        with allure.step("Клик по кнопке ellipsis для задачи"):
            self.wait_for_selector_and_click(ellipsis_selector)
        with allure.step("Клик по пункту Delete"):
            self.wait_for_selector_and_click(self.DELETE_MENU_ITEM)
        with allure.step("Проверка исчезновения задачи"):
            self.page.wait_for_selector(task_selector, state="detached", timeout=10000)
