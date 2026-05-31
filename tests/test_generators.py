# файл: tests/test_generators.py
from collections.abc import Iterator

import pytest

# Импортируем функции, код которых нужно протестировать
from src.generators import card_number_generator, filter_by_currency, transaction_descriptions


# Функция теста с использованием фикстуры list_of_transactions
def test_filter_by_currency_success(list_of_transactions: list[dict]) -> None:
    # Проверка: ожидаемый результат == фактический
    # Проверяем фильтрацию транзакций по USD.
    # Для лучшей читаемости кода проверка проводится по известному количеству транзакций и по признаку "id"
    generator = filter_by_currency(list_of_transactions, "USD")
    result = list(generator)

    assert len(result) == 2  # Проверяем, что отфильтровалось ровно 2 транзакции
    assert result[0]["id"] == 939719570  # Проверяем, что первая из них — это действительно транзакция с id 939719570
    assert result[1]["id"] == 142264268  # Проверяем, что вторая — с id 142264268


# Функция теста с использованием фикстуры list_of_bad_transactions
def test_filter_by_currency_error(list_of_bad_transactions: list[dict]) -> None:
    # Тест проверяет, что функция не падает, если в словаре нет нужных ключей.
    generator = filter_by_currency(list_of_bad_transactions, "USD")
    result = list(generator)

    # Результат должен быть пустым списком, а программа НЕ должна выбросить KeyError
    assert result == []


# Функция теста с использованием фикстуры list_of_transactions
def test_transaction_descriptions_success(list_of_transactions: list[dict]) -> None:
    # Проверяем, что функция поочередно выдает описания.
    generator = transaction_descriptions(list_of_transactions)
    result = list(generator)

    assert result == [
        "Перевод организации",
        "Оплата услуг",
        "Перевод со счета на счет",
        "Перевод со счета на счет",
        "Перевод с карты на карту",
        "Перевод со счета на счет",
    ]


# Функция теста с использованием фикстуры list_of_bad_transactions
def test_transaction_descriptions_error(list_of_bad_transactions: list[dict]) -> None:
    # Тест проверяет, что функция не падает, если в словаре нет нужных ключей.
    generator = transaction_descriptions(list_of_bad_transactions)
    result = list(generator)

    # Результат должен быть дефолтным значением метода .get, описанного в функции transaction_descriptions
    assert result == ["Без описания"]


# Функция теста с использованием параметризации для card_number_generator
@pytest.mark.parametrize(
    "start, end, expected",
    [
        (
            1,
            5,
            [
                "0000 0000 0000 0001",
                "0000 0000 0000 0002",
                "0000 0000 0000 0003",
                "0000 0000 0000 0004",
                "0000 0000 0000 0005",
            ],
        ),
        (
            99994,
            100000,
            [
                "0000 0000 0009 9994",
                "0000 0000 0009 9995",
                "0000 0000 0009 9996",
                "0000 0000 0009 9997",
                "0000 0000 0009 9998",
                "0000 0000 0009 9999",
                "0000 0000 0010 0000",
            ],
        ),
    ],
)
def test_card_number_generator_success(start: int, end: int, expected: list[str]) -> None:
    generator = card_number_generator(start, end)
    assert isinstance(generator, Iterator)  # Дополнительно проверяем, что это итератор
    assert list(generator) == expected


def test_card_number_generator_error() -> None:
    with pytest.raises(ValueError):  # Пайтест сам поймает ваш raise
        next(card_number_generator(0, 5))
