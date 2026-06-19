# файл: tests/test_added_functions.py
from unittest.mock import patch

import pytest

# Импортируем функции, код которых нужно протестировать
from src.added_functions import format_transactions_generator, get_optional_iso_date

# =====================================================================
# ТЕСТЫ ДЛЯ ФУНКЦИИ get_optional_iso_date
# =====================================================================


# 1. Параметризованный тест для успешных сценариев (валидная дата или пустой ввод)
@pytest.mark.parametrize(
    "user_input, expected_result",
    [
        ("", None),  # Пользователь просто нажал Enter
        ("   ", None),  # Пользователь ввел пробелы и нажал Enter
        ("2026-06-18", "2026-06-18"),  # Идеальный формат даты
        ("2023-01-01", "2023-01-01"),  # Другая валидная дата
    ],
)
def test_get_optional_iso_date_success(user_input: str, expected_result: str | None) -> None:
    # Патчим (подменяем) встроенную функцию input, чтобы она возвращала user_input
    with patch("builtins.input", return_value=user_input):
        result = get_optional_iso_date("Введите дату: ")
        assert result == expected_result


# 2. Тест на обработку ошибок и повторный ввод (проверка цикла while True)
def test_get_optional_iso_date_retry_on_error() -> None:
    # Имитируем последовательность ввода:
    # 1. Сначала вводим полную ерунду (вызовет ошибку)
    # 2. Потом вводим дату с неправильными разделителями (вызовет ошибку)
    # 3. В конце вводим корректную дату (функция должна завершить цикл и вернуть её)
    inputs = ["invalid-text", "18.06.2026", "2026-06-18"]

    # side_effect вместо return_value позволяет возвращать элементы из списка по очереди при каждом вызове input()
    with patch("builtins.input", side_effect=inputs), patch("builtins.print") as mock_print:

        result = get_optional_iso_date("Введите дату: ")

        # Проверяем, что в итоге вернулась правильная дата
        assert result == "2026-06-18"

        # Проверяем, что print вывелся ровно 2 раза (для первых двух неверных вводов)
        assert mock_print.call_count == 2

        # Можно даже проверить текст ошибки, который увидел пользователь
        mock_print.assert_any_call("Ошибка: неверный формат. Используйте ГГГГ-ММ-ДД или нажмите Enter для пропуска.\n")


# =====================================================================
# ТЕСТЫ ДЛЯ ФУНКЦИИ format_transactions_generator
# =====================================================================


@pytest.mark.parametrize(
    "transaction, expected_block",
    [
        (
            {
                "id": 939719570,
                "state": "EXECUTED",
                "date": "2018-06-30T02:08:58.425572",
                "operationAmount": {"amount": "9824.07", "currency": {"name": "USD", "code": "USD"}},
                "description": "Перевод организации",
                "from": "Счет 75106830613657916952",
                "to": "Счет 11776614605963066702",
            },
            # Пишем ровно то, что реально возвращает программа (из текста ошибки)
            "30.06.2018 Перевод организации\nСчет **6952 -> Счет **6702\nСумма: 9824.07 USD\n",
        ),
        (
            {
                "id": 939719570,
                "state": "EXECUTED",
                "date": "2018-06-30T02:08:58.425572",
                "operationAmount": {"amount": "9824.07", "currency": {"name": "USD", "code": "USD"}},
                "description": "Перевод организации",
                "from": "Счет 75106830613657916952",
                "to": "",
            },
            # Проверяем отсутствие входящего и исходящего счетов (карт)
            "30.06.2018 Перевод организации\nСчет **6952\nСумма: 9824.07 USD\n",
        ),
        (
            {
                "id": 939719570,
                "state": "EXECUTED",
                "date": "2018-06-30T02:08:58.425572",
                "operationAmount": {"amount": "9824.07", "currency": {"name": "USD", "code": "USD"}},
                "description": "Перевод организации",
                "from": "",
                "to": "Счет 11776614605963066702",
            },
            # Проверяем отсутствие входящего и исходящего счетов (карт)
            "30.06.2018 Перевод организации\n -> Счет **6702\nСумма: 9824.07 USD\n",
        ),
    ],
)
def test_format_transactions_happy_path(transaction: dict, expected_block: str) -> None:
    generator = format_transactions_generator([transaction])
    result = list(generator)

    assert result == [expected_block]


# 2. Негативные кейсы: Пустые данные, "битые" строки и отсутствие полей счетов
@pytest.mark.parametrize(
    "bad_input, expected_output",
    [
        # 1. Пустой словарь в списке (должен быть пропущен)
        ({}, None),
        # 2. None вместо словаря (должен быть пропущен)
        (None, None),
        # 3. Строка вместо словаря (должен быть пропущен)
        ("неверный_тип_данных", None),
        # 4. Нет полей from и to вообще (строка направления полностью отсутствует,
        # дата форматируется в 01.01.2026, в конце \n)
        (
            {"date": "2026-01-01T00:00:00", "description": "Покупка", "amount": "100", "currency_name": "EUR"},
            "01.01.2026 Покупка\nСумма: 100.00 EUR\n",
        ),
        # 5. Некорректная сумма, которую нельзя перевести во float (выводится как есть, в конце \n)
        (
            {
                "date": "2026-01-01T00:00:00",
                "description": "Сбой цены",
                "amount": "NOT_A_NUMBER",
                "currency_name": "RUB",
            },
            "01.01.2026 Сбой цены\nСумма: NOT_A_NUMBER RUB\n",
        ),
    ],
)
def test_format_transactions_edge_cases_no_mocks(bad_input: dict, expected_output: str) -> None:
    generator = format_transactions_generator([bad_input])
    result = list(generator)

    if expected_output is None:
        assert result == []
    else:
        assert result == [expected_output]


# 3. Тест на обработку пустого списка транзакций
def test_format_transactions_generator_empty_list() -> None:
    generator = format_transactions_generator([])
    result = list(generator)
    assert result == []


# 4. Тест с использованием фикстуры list_of_transactions из conftest.py
def test_with_conftest_fixture_no_mocks(list_of_transactions: list[dict]) -> None:
    # 1. Запускаем генератор со всем списком транзакций из conftest
    generator = format_transactions_generator(list_of_transactions)
    result = list(generator)

    # 2. Проверяем количество: должно быть ровно столько, сколько валидных словарей в фикстуре (6 штук)
    valid_count = len([op for op in list_of_transactions if op and isinstance(op, dict)])
    assert len(result) == valid_count

    # 3. Точечно проверяем самый первый блок, чтобы убедиться в правильности форматирования данных
    # Подставляем реальный вывод (дата 30.06.2018, маски счетов, валюта USD и \n на конце)
    expected_first_block = "30.06.2018 Перевод организации\n" "Счет **6952 -> Счет **6702\n" "Сумма: 9824.07 USD\n"

    assert result[0] == expected_first_block
