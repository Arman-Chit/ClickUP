import allure
from datetime import datetime
from pages.board_page import BoardPage

@allure.feature("Задачи - UI и API")
class TestBoardPage:

    @allure.description("Удаление задачи через UI и проверка её удаления через API.")
    def test_task_delete(self, logged_in_page, create_task_fixture, task_api):
        task_id = create_task_fixture['id']
        task_name = create_task_fixture['name']
        board_page = BoardPage(logged_in_page)

        board_page.navigate_to_board()
        board_page.wait_for_task_visible(task_name)

        with allure.step(f"Удаление задачи '{task_name}' через UI"):
            board_page.delete_task(task_name)

        task_link_selector = f'[data-test="board-task__name-link__{task_name}"]'
        board_page.page.locator(task_link_selector).wait_for(state='detached', timeout=5000)

        assert not board_page.page.locator(task_link_selector).is_visible(), \
            f"Задача {task_name} все еще видна через UI"

        with allure.step(f"Проверка статуса удаления задачи ID {task_id} через API"):
            response = task_api.get_task(task_id)
            assert response.status_code == 404, "Ожидали 404, задача все еще доступна"

    @allure.description("Создание задачи через UI, проверка её наличия через UI и удаление через API")
    def test_create_task_ui(self, logged_in_page, task_api, get_list_fixture):
        unique_name = f"UI Created Task {datetime.now().strftime('%H%M%S')}"
        board_page = BoardPage(logged_in_page)

        board_page.navigate_to_board()
        with allure.step(f"Создание задачи через UI с именем '{unique_name}'"):
            board_page.create_task_ui(unique_name)

        task_link_selector = f'[data-test="board-task__name-link__{unique_name}"]'
        board_page.page.locator(task_link_selector).wait_for(state='visible', timeout=5000)
        assert board_page.page.locator(task_link_selector).is_visible(), \
            "Созданная задача не отображается через UI"

        list_id = get_list_fixture['id']
        with allure.step(f"Получение задач списка ID {list_id} через API"):
            response = task_api.session.get(f"{task_api.base_url}/list/{list_id}/task")
            assert response.status_code == 200, f"GET /list/{list_id}/task вернул {response.status_code}"
            tasks = response.json().get('tasks', [])

        with allure.step(f"Поиск задачи '{unique_name}' в ответе API"):
            created = next((t for t in tasks if t['name'] == unique_name), None)
            assert created, f"Задача '{unique_name}' не найдена через API"
            task_id = created['id']

        with allure.step(f"Удаление задачи ID {task_id} через API"):
            delete_resp = task_api.delete_task(task_id)
            assert delete_resp.status_code == 204, \
                f"DELETE /task/{task_id} вернул {delete_resp.status_code}"

        with allure.step(f"Проверка отсутствия задачи ID {task_id} через API"):
            check_resp = task_api.get_task(task_id)
            assert check_resp.status_code == 404, \
                f"Ожидали 404, получили {check_resp.status_code}"