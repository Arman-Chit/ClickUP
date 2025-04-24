import pytest
import allure
from api_clients.task_api import TaskAPI
from utils.helpers import CLICKUP_API


@allure.feature("Команды")
@allure.description("Проверка получения списка команд через API.")
def test_get_team(task_api):
    with allure.step("Отправка запроса на получение списка команд"):
        response = task_api.get_team()
    with allure.step("Проверка, что статус код равен 200"):
        assert response.status_code == 200, f"Не удалось получить список команд: {response.status_code}"
    with allure.step("Проверка, что в ответе есть список команд"):
        teams = response.json().get("teams")
        assert isinstance(teams, list), "Ожидался список команд, но получен: {type(teams)}"
        assert teams, "Список команд не должен быть пустым, но он оказался пустым."


@allure.feature("Пространства")
@allure.description("Проверка получения пространств по команде через API.")
def test_get_space(task_api, get_team_fixture):
    with allure.step("Получение team_id из фикстуры"):
        team_id = get_team_fixture["id"]
    with allure.step("Отправка запроса на получение пространств"):
        response = task_api.get_space(team_id)
    with allure.step("Проверка, что статус код равен 200"):
        assert response.status_code == 200, f"Не удалось получить пространства команды: {response.status_code}"
    with allure.step("Проверка, что в ответе есть список пространств"):
        spaces = response.json().get("spaces")
        assert isinstance(spaces, list), "Ожидался список пространств, но получен: {type(spaces)}"
        assert spaces, "Список пространств не должен быть пустым, но он оказался пустым."


@allure.feature("Задачи")
@allure.description("Создание новой задачи через API и проверка возвращаемого ID и имени.")
def test_create_task(task_api, get_list_fixture):
    with allure.step("Получение list_id из фикстуры"):
        list_id = get_list_fixture["id"]
    with allure.step("Создание задачи"):
        task_data = {"name": "Test Task", "description": "Test description"}
        response = task_api.create_task(list_id, task_data)
    with allure.step("Проверка, что задача успешно создана"):
        assert response.status_code == 200, f"Не удалось создать задачу: {response.status_code}"
        task = response.json()
        assert task.get("id"), "ID задачи не должен быть пустым"
        assert task.get("name") == task_data["name"], f"Имя задачи не совпадает. Ожидалось: {task_data['name']}, но получено: {task.get('name')}"
    with allure.step("Удаление задачи в рамках очистки"):
        del_resp = task_api.delete_task(task["id"])
        assert del_resp.status_code == 204, f"Не удалось удалить задачу после теста: {del_resp.status_code}"


@allure.feature("Задачи")
@allure.description("Получение ранее созданной задачи по ID через API.")
def test_get_task(task_api, create_task_fixture):
    with allure.step("Получение task_id из фикстуры"):
        task_id = create_task_fixture["id"]
    with allure.step("Отправка запроса на получение задачи"):
        response = task_api.get_task(task_id)
    with allure.step("Проверка, что задача получена корректно"):
        assert response.status_code == 200, f"Не удалось получить задачу: {response.status_code}"
        task = response.json()
        assert task.get("id") == task_id, f"ID задачи не совпадает. Ожидался: {task_id}, но получено: {task.get('id')}"
        assert task.get("name") == create_task_fixture["name"], f"Имя задачи не совпадает. Ожидалось: {create_task_fixture['name']}, но получено: {task.get('name')}"


@allure.feature("Задачи")
@allure.description("Обновление задачи и проверка изменений.")
def test_update_task(task_api, create_task_fixture):
    with allure.step("Подготовка данных для обновления"):
        task_id = create_task_fixture["id"]
        new_name = "Updated Task Name"
        update_data = {"name": new_name, "description": "New Description"}
    with allure.step("Обновление задачи"):
        response = task_api.update_task(task_id, update_data)
    with allure.step("Проверка, что задача обновлена"):
        assert response.status_code == 200, f"Не удалось обновить задачу: {response.status_code}"
        updated = response.json()
        assert updated.get("name") == new_name, f"Имя задачи не обновлено. Ожидалось: {new_name}, но получено: {updated.get('name')}"


@allure.feature("Задачи")
@allure.description("Удаление задачи и проверка, что она недоступна.")
def test_delete_task(task_api, create_task_fixture):
    with allure.step("Получение task_id из фикстуры"):
        task_id = create_task_fixture["id"]
    with allure.step("Удаление задачи"):
        response = task_api.delete_task(task_id)
        assert response.status_code == 204, f"Не удалось удалить задачу: {response.status_code}"
    with allure.step("Проверка, что задача недоступна после удаления"):
        check = task_api.get_task(task_id)
        assert check.status_code == 404, f"Ожидался код 404 после удаления задачи, но получен: {check.status_code}"


@allure.feature("Авторизация")
@allure.description("Проверка отказа в доступе при использовании недействительного API ключа.")
def test_unauthorized_access():
    with allure.step("Создание клиента с недействительным ключом"):
        invalid_api = TaskAPI(CLICKUP_API, "invalid_key")
    with allure.step("Попытка получить задачу с недействительным ключом"):
        response = invalid_api.get_task("nonexistent_id")
    with allure.step("Проверка, что доступ запрещён"):
        assert response.status_code == 401, f"Ожидался статус 401, получен: {response.status_code}"


@allure.feature("Задачи")
@allure.description("Негативный тест: передача некорректных данных при обновлении задачи.")
def test_update_task_negative(task_api, create_task_fixture):
    with allure.step("Получение task_id из фикстуры"):
        task_id = create_task_fixture["id"]
    with allure.step("Попытка обновления задачи с некорректными данными"):
        response = task_api.update_task(task_id, "invalid_payload")
    with allure.step("Проверка, что вернулся статус 400"):
        assert response.status_code == 400, f"Ожидался статус 400, получен: {response.status_code}"


@allure.feature("Задачи")
@allure.description("Негативный тест: удаление задачи с некорректным ID.")
def test_delete_task_negative(task_api):
    with allure.step("Попытка удаления задачи с невалидным ID"):
        invalid_id = "invalid_id_123"
        response = task_api.delete_task(invalid_id)
    with allure.step("Проверка, что возвращён статус 401"):
        assert response.status_code == 401, (
            f"Ожидался статус 401, получен: {response.status_code}"
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
    with allure.step("Подготовка payload для создания задачи"):
        list_id = get_list_fixture["id"]
        payload = {} if task_data is None else dict(task_data)
        payload.setdefault("list_id", list_id)

    with allure.step("Попытка создать задачу с некорректными данными"):
        response = task_api.create_task(payload.pop("list_id"), payload)

    with allure.step("Проверка, что возвращён ожидаемый статус ошибки"):
        assert response.status_code == expected_status, (
            f"Ожидался статус {expected_status}, получен: {response.status_code}"
        )

    with allure.step("Проверка наличия и корректности поля ECODE в ответе"):
        response_json = response.json()
        ecode_value = response_json.get("ECODE") or response_json.get("ecode")
        assert ecode_value, f"Поле 'ECODE' отсутствует в ответе: {response_json}"
        assert ecode_value.lower() == expected_ecode.lower(), (
            f"Ожидался ECODE '{expected_ecode}', получен '{ecode_value}'"
        )
