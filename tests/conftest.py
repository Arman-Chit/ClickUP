import pytest
from api_clients.task_api import TaskAPI
from utils.helpers import CLICKUP_API_KEY, CLICKUP_API

@pytest.fixture(scope="session")
def task_api():
    api = TaskAPI(CLICKUP_API, CLICKUP_API_KEY)
    r = api.get_team()
    if r.status_code != 200:
        pytest.fail(f"Не удалось подключиться к API: {r.status_code} / {r.text}")
    return api

@pytest.fixture
def get_team_fixture(task_api):
    r = task_api.get_team()
    assert r.status_code == 200, f"GET /team вернул {r.status_code}"
    teams = r.json().get("teams") or []
    assert teams, "Список teams пуст или отсутствует"
    return teams[0]

@pytest.fixture
def get_space_fixture(task_api, get_team_fixture):
    r = task_api.get_space(get_team_fixture["id"])
    assert r.status_code == 200, f"GET /team/{get_team_fixture['id']}/space вернул {r.status_code}"
    spaces = r.json().get("spaces") or []
    assert spaces, "Список spaces пуст или отсутствует"
    return spaces[0]

@pytest.fixture
def get_folder_fixture(task_api, get_space_fixture):
    r = task_api.get_folder(get_space_fixture["id"])
    assert r.status_code == 200, f"GET /space/{get_space_fixture['id']}/folder вернул {r.status_code}"
    folders = r.json().get("folders") or []
    assert folders, "Список folders пуст или отсутствует"
    return folders[0]

@pytest.fixture
def get_list_fixture(task_api, get_folder_fixture):
    r = task_api.get_list(get_folder_fixture["id"])
    assert r.status_code == 200, f"GET /folder/{get_folder_fixture['id']}/list вернул {r.status_code}"
    lists = r.json().get("lists") or []
    assert lists, "Список lists пуст или отсутствует"
    return lists[0]

@pytest.fixture
def create_task_fixture(task_api, get_list_fixture):
    task_data = {"name": "Test Task", "description": "Test"}
    r = task_api.create_task(get_list_fixture["id"], task_data)
    assert r.status_code == 200, f"POST /list/{get_list_fixture['id']}/task вернул {r.status_code}"
    task = r.json()
    yield task
    dr = task_api.delete_task(task["id"])
    assert dr.status_code in (204, 404), f"DELETE /task/{task['id']} вернул {dr.status_code}"
