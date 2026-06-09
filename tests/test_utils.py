# файл: tests/test_utils.py
import json
from pathlib import Path
from typing import Any

import pytest

# Импортируем функции, код которых нужно протестировать
from src.utils import list_of_input_transaction

# Формируем путь до файла для аргумента file_path
# 1. В главном коде вычисляем, где мы находимся
current_dir = Path(__file__).resolve().parent

# 2. Собираем относительный путь до файла данных
file_path = current_dir.parent / "data" / "operations.json"


# Функция успешного теста list_of_input_transaction
def test_list_of_input_transaction_success() -> None:
    transactions = list_of_input_transaction(file_path)
    assert isinstance(transactions, list)  # Проверяем тип данных, что он действительно list.
    if len(transactions) >= 3:  # Обращаемся напрямую к списку транзакций по индексам. Проверяем,
        # что вторая транзакция — это действительно транзакция с id 41428829,
        # а третья — с id 939719570, что подтверждаеи корректное считывание файла.
        assert transactions[1]["id"] == 41428829
        assert transactions[2]["id"] == 939719570
        print(transactions)


# Функция неудачного теста list_of_input_transaction (не найден файл)
def test_list_of_input_transaction_file_not_found() -> None:
    # Тест проверяет, что если файл не найден, функция возвращает пустой список.
    # Создаем заведомо несуществующий путь
    fake_path = Path("this/file/does/not/exist.json")

    # Вызываем функцию
    result = list_of_input_transaction(fake_path)

    # Проверяем, что функция перехватила FileNotFoundError и вернула []
    assert result == []


# Функция неудачного теста list_of_input_transaction (если JSON-файл сломан)
def test_list_of_input_transaction_invalid_json(tmp_path: Path) -> None:
    # tmp_path — это встроенная фикстура pytest, которая создает временную папку для теста.
    # Создаем временный файл со сломанным (некорректным) JSON-кодом
    broken_file = tmp_path / "broken.json"
    broken_file.write_text("{invalid json: [missing quotes}", encoding="utf-8")

    # Вызываем функцию
    result = list_of_input_transaction(broken_file)

    # Проверяем, что функция перехватила json.JSONDecodeError и вернула пустой список[]
    assert result == []


# Функция неудачного теста list_of_input_transaction с применением параметризации
# (файл содержит валидный JSON, но внутри не список (list))
@pytest.mark.parametrize(
    "invalid_content",
    [
        {"dict_key": "value"},  # Словать вместо списка
        "just a string",  # Строка
        12345,  # Число
        True,  # Булево значение
    ],
)
def test_list_of_input_transaction_not_a_list(tmp_path: Path, invalid_content: Any) -> None:
    # tmp_path — это специальная фикстура, которая автоматически создает уникальную временную папку на компьютере
    # специально для этого теста. Старые временные папки pytest удаляет автоматически при следующих запусках.
    not_list_file = tmp_path / "not_list.json"

    # Записываем не-список во временный файл
    with open(not_list_file, "w", encoding="utf-8") as f:
        json.dump(invalid_content, f)

    result = list_of_input_transaction(not_list_file)
    assert result == []
