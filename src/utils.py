import json
import logging
from pathlib import Path

# --- УЧЕБНАЯ НАСТРОЙКА ЛОГИРОВАНИЯ ВНУТРИ МОДУЛЯ (потом переделать в глобальную настройку в main.py и conftest.py)---
# Находим корень проекта (поднимаемся на две папки вверх от текущего файла masks.py)
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "utils.log"

# Гарантируем, что папка log существует
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Создаем персональный логгер именно для этого модуля
# Основная конфигурация logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
    filename=str(LOG_FILE),  # Запись логов в файл
    filemode="w",
    encoding="utf-8",
)  # Перезапись файла при каждом запуске

# Создаем логеры для различных компонентов программы
utils_logger = logging.getLogger("app.utils")


def list_of_input_transaction(file_path: Path) -> list:
    """Функция принимает на вход путь до JSON-файла и возвращает список словарей с данными о финансовых транзакциях.
    Если файл пустой, содержит не список или не найден, функция возвращает пустой список. Файл с данными о финансовых
    транзациях operations.json находится в директорию data/ в корне проекта.
    Если JSON-файл пустой, содержит не-список или не найден, возвращается пустой список.
    Функция не проверяет считанный JSON-файл на правильность информации по всем транзакциям
    (наличие всех ключей и т.п.)"""

    try:
        with open(file_path, encoding="utf-8") as file:
            list_data = json.load(file)
            utils_logger.info(f"Считан файл {file_path}")
            # Проверяем, что внутри JSON именно список (list), а не словарь или строка
            if isinstance(list_data, list):
                utils_logger.info(f"Внутри файла {file_path} правильный формат list")
                return list_data
            else:
                utils_logger.error(f"Внутри файла {file_path} некорректный формат")
                return []  # Возвращаем пустой список, если там не-список

    except (FileNotFoundError, json.JSONDecodeError):
        utils_logger.error(f"Файл {file_path} пуст или сломан")
        # json.JSONDecodeError перехватит пустой или сломанный JSON-файл
        # FileNotFoundError перехватит отсутствие файла
        return []
