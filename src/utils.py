import json
from pathlib import Path


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

            # Проверяем, что внутри JSON именно список (list), а не словарь или строка
            if isinstance(list_data, list):
                return list_data
            else:
                return []  # Возвращаем пустой список, если там не-список

    except (FileNotFoundError, json.JSONDecodeError):
        # json.JSONDecodeError перехватит пустой или сломанный JSON-файл
        # FileNotFoundError перехватит отсутствие файла
        return []
