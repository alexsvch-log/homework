# файл: tests/test_process_bank.py
import pytest

# Импортируем функции, код которых нужно протестировать
from src.process_bank import process_bank_operations, process_bank_search


# Локальная фикстура: живет только в этом файле и не мешает другим тестам
# Сделана под тест функции process_bank_operations
@pytest.fixture
def dirty_transactions(list_of_transactions: list) -> list:
    # Делаем копию, чтобы случайно не испортить данные в conftest.py
    corrupted_data = list_of_transactions.copy()

    # Подмешиваем брак
    corrupted_data.extend(
        [
            "not_a_dict_string",  # Брак: не словарь
            12345,  # Брак: число вместо словаря
            {"amount": 500},  # Брак: нет ключа description
            {"description": None},  # Брак: description не строка
        ]
    )
    return corrupted_data


# =====================================================================
# ТЕСТЫ ДЛЯ ФУНКЦИИ process_bank_operations
# =====================================================================


# 1. Позитивный тест с использованием фикстур из conftest
def test_process_bank_operations_happy_path(list_of_transactions: list[dict], valid_categories: list) -> None:
    result = process_bank_operations(list_of_transactions, valid_categories)
    expected = {
        "Оплата услуг": 1,
        "Перевод организации": 1,
        "Перевод с карты на карту": 1,
        "Перевод со счета на счет": 3,
    }
    assert result == expected


# 1.1. Тот самый новый тест: проверяем, что грязные данные игнорируются,
# а хорошие транзакции из list_of_transactions всё равно считаются корректно
def test_process_bank_operations_with_dirty_data(dirty_transactions: list[dict], valid_categories: list) -> None:
    result = process_bank_operations(dirty_transactions, valid_categories)

    # Ожидаем точно такой же результат, так как брак должен быть отфильтрован
    expected = {
        "Оплата услуг": 1,
        "Перевод организации": 1,
        "Перевод с карты на карту": 1,
        "Перевод со счета на счет": 3,
    }
    assert result == expected


# 2. Параметризованный тест для проверки невалидных типов аргументов
@pytest.mark.parametrize(
    "invalid_data, invalid_categories",
    [
        (None, ["Оплата услуг"]),  # data - None
        ([{"description": "Оплата услуг"}], None),  # categories - None
        ("not_a_list", ["Оплата услуг"]),  # data - строка
        ([{"description": "Оплата услуг"}], "not_a_list"),  # categories - строка
    ],
)
def test_process_bank_operations_invalid_arguments(invalid_data: list, invalid_categories: list) -> None:
    result = process_bank_operations(invalid_data, invalid_categories)
    assert result == {}


# 3. Тест на пустые списки
def test_process_bank_operations_empty_inputs() -> None:
    assert process_bank_operations([], ["Оплата услуг"]) == {}
    assert process_bank_operations([{"description": "Оплата услуг"}], []) == {}


# 4. Тест на дубликаты в категориях
def test_process_bank_operations_duplicate_categories() -> None:
    data = [{"description": "Оплата услуг"}]
    categories = ["Оплата услуг", "Оплата услуг", "Оплата услуг"]
    # Благодаря set() внутри функции, дубликаты не сломают логику
    assert process_bank_operations(data, categories) == {"Оплата услуг": 1}


# =====================================================================
# ТЕСТЫ ДЛЯ ФУНКЦИИ process_bank_search
# =====================================================================


# 1. Тест на пустую строку поиска
def test_process_bank_search_empty_search_string(dirty_transactions: list, list_of_transactions: list[dict]) -> None:
    # Передаем ГРЯЗНЫЕ данные и ПУСТУЮ строку поиска
    result = process_bank_search(dirty_transactions, "")

    # Ожидаем, что вернутся ВСЕ ХОРОШИЕ транзакции, а весь брак успешно отфильтруется
    assert len(result) == len(list_of_transactions)

    # Гарантируем, что функция вернула НОВЫЙ список в памяти, а не изменила оригинал
    assert result is not list_of_transactions


# 2. Параметризованный тест для обычного поиска по тексту (Happy Path)
# Передаем поисковый запрос и ожидаемое количество найденных записей
@pytest.mark.parametrize(
    "search_term, expected_count",
    [
        ("оплата", 1),  # Регистронезависимость ("Оплата услуг")
        ("карт", 1),  # Поиск по части слова ("Перевод с карты на карту")
        (
            "перевод",
            5,
        ),  # Найдет все виды переводов (1 организации + 1 с карты + 3 со счета)
        ("НЕ СУЩЕСТВУЕТ", 0),  # Ничего не найдено
    ],
)
def test_process_bank_search_valid_queries(
    list_of_transactions: list[dict], search_term: str, expected_count: int
) -> None:
    result = process_bank_search(list_of_transactions, search_term)
    assert len(result) == expected_count


# 3. Тест устойчивости к "грязным" данным при обычном поиске
def test_process_bank_search_ignores_dirty_data(dirty_transactions: list) -> None:
    # Ищем слово "перевод" в грязном списке. Функция должна просто пропустить брак и не упасть
    result = process_bank_search(dirty_transactions, "перевод")

    # Ожидаем ровно 5 хороших переводов
    assert len(result) == 5


# 4. Параметризованный тест для проверки невалидных типов аргументов
@pytest.mark.parametrize(
    "invalid_data, invalid_search",
    [
        (None, "оплата"),  # data - None
        ([{"description": "оплата"}], None),  # search - None
        ("not_a_list", "оплата"),  # data - строка вместо списка
        ([{"description": "оплата"}], 12345),  # search - число вместо строки
    ],
)
def test_process_bank_search_invalid_arguments(invalid_data: list[dict], invalid_search: str) -> None:
    result = process_bank_search(invalid_data, invalid_search)
    assert result == []
