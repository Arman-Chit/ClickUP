import os
from dotenv import load_dotenv

load_dotenv()

def get_env_variable(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Переменная окружения '{name}' не установлена. Пожалуйста, убедитесь, что она задана в файле .env.")
    return value

try:
    CLICKUP_API_KEY = get_env_variable("CLICKUP_API_KEY")
    CLICKUP_API = get_env_variable("CLICKUP_API")
    CLICKUP_EMAIL = get_env_variable("CLICKUP_EMAIL")
    CLICKUP_PASSWORD = get_env_variable("CLICKUP_PASSWORD")
except ValueError as e:
    print(e)
    exit(1)
