import pytest
import allure
from api_clients.task_api import TaskAPI
from utils.helpers import CLICKUP_API

@allure.feature("Команды")
@allure.description("Проверка получения списка команд через API.")
def test_get_team(task_api):
    response = task_api.get_team()
    assert response.status_code == 200, f"GET /team failed: {response.status_code}"
    teams = response.json().get("teams")
    assert isinstance(teams, list), "Expected 'teams' to be a list"
    assert teams, "Expected at least one team"


@allure.feature("Пространства")
@allure.description("Проверка получения пространств по команде через API.")
def test_get_space(task_api, get_team_fixture):
    team_id = get_team_fixture["id"]
    response = task_api.get_space(team_id)
    assert response.status_code == 200, f"GET /team/{team_id}/space failed: {response.status_code}"
    spaces = response.json().get("spaces")
    assert isinstance(spaces, list), "Expected 'spaces' to be a list"
    assert spaces, "Expected at least one space"


@allure.feature("Задачи")
@allure.description("Создание новой задачи через API и проверка возвращаемого ID и имени.")
def test_create_task(task_api, get_list_fixture):
    list_id = get_list_fixture["id"]
    task_data = {"name": "Test Task", "description": "Test description"}
    response = task_api.create_task(list_id, task_data)
    assert response.status_code == 200, f"POST /list/{list_id}/task failed: {response.status_code}"
    task = response.json()
    assert task.get("id"), "Task ID should not be empty"
    assert task.get("name") == task_data["name"], "Task name mismatch"

    del_resp = task_api.delete_task(task["id"])
    assert del_resp.status_code == 204, f"Cleanup failed: {del_resp.status_code}"


@allure.feature("Задачи")
@allure.description("Получение ранее созданной задачи по ID через API.")
def test_get_task(task_api, create_task_fixture):
    task_id = create_task_fixture["id"]
    response = task_api.get_task(task_id)
    assert response.status_code == 200, f"GET /task/{task_id} failed: {response.status_code}"
    task = response.json()
    assert task.get("id") == task_id
    assert task.get("name") == create_task_fixture["name"]


@allure.feature("Задачи")
@allure.description("Обновление задачи и проверка изменений.")
def test_update_task(task_api, create_task_fixture):
    task_id = create_task_fixture["id"]
    new_name = "Updated Task Name"
    update_data = {"name": new_name, "description": "New Description"}

    response = task_api.update_task(task_id, update_data)
    assert response.status_code == 200, f"PUT /task/{task_id} failed: {response.status_code}"
    updated = response.json()
    assert updated.get("name") == new_name, "Task name was not updated"


@allure.feature("Задачи")
@allure.description("Удаление задачи и проверка, что она недоступна.")
def test_delete_task(task_api, create_task_fixture):
    task_id = create_task_fixture["id"]

    response = task_api.delete_task(task_id)
    assert response.status_code == 204, f"DELETE /task/{task_id} failed: {response.status_code}"

    check = task_api.get_task(task_id)
    assert check.status_code == 404, "Expected 404 after deletion"


@allure.feature("Авторизация")
@allure.description("Проверка отказа в доступе при использовании недействительного API ключа.")
def test_unauthorized_access():
    invalid_api = TaskAPI(CLICKUP_API, "invalid_key")
    response = invalid_api.get_task("nonexistent_id")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


@allure.feature("Задачи")
@allure.description("Негативный тест: передача некорректных данных при обновлении задачи.")
def test_update_task_negative(task_api, create_task_fixture):
    task_id = create_task_fixture["id"]
    response = task_api.update_task(task_id, "invalid_payload")
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"


@allure.feature("Задачи")
@allure.description("Негативный тест: удаление задачи с некорректным ID.")
def test_delete_task_negative(task_api):
    invalid_id = "invalid_id_123"
    response = task_api.delete_task(invalid_id)
    assert response.status_code in (400, 401, 404), (
        f"Expected 400, 401 or 404, got {response.status_code}"
    )


@allure.feature("Задачи")
@allure.description("Негативные тесты создания задач с некорректными данными.")
@pytest.mark.parametrize(
    "task_data, expected_status, expected_ecode",
    [
        ({}, 400, "input_005"),
        ({"invalid_field": "Test name"}, 400, "input_005"),
        ({"name": "Valid", "status": "invalid_status"}, 400, "CRTSK_001"),
        ({"name": "Valid", "due_date": "2024-01-01"}, 400, "input_006"),
        (None, 400, "input_005"),
        ({"list_id": "invalid_list_123"}, 400, "INPUT_003"),
    ]
)
def test_create_task_negative(task_api, get_list_fixture, task_data, expected_status, expected_ecode):
    list_id = get_list_fixture["id"]
    payload = {} if task_data is None else dict(task_data)
    payload.setdefault("list_id", list_id)

    response = task_api.create_task(payload.pop("list_id"), payload)

    assert response.status_code == expected_status, (
        f"Expected {expected_status}, got {response.status_code}"
    )

    response_json = response.json()
    ecode_value = response_json.get("ECODE") or response_json.get("ecode")
    assert ecode_value, f"Поле 'ECODE' отсутствует в ответе: {response_json}"
    assert ecode_value.lower() == expected_ecode.lower(), (
        f"Expected ecode '{expected_ecode}', got '{ecode_value}'"
    )
