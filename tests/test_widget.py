# файл: tests/test_widget.py
import pytest

# Импортируем функции, код которых нужно протестировать
from src.widget import get_date, mask_account_card


# Функция теста с использованием параметризации
@pytest.mark.parametrize(
    "card_number, expected_result",
    [
        ("Maestro 1596837868705199", "Maestro 1596 83** **** 5199"),
        ("Счет 64686473678894779589", "Счет **9589"),
        ("MasterCard 7158300734726758", "MasterCard 7158 30** **** 6758"),
        ("Счет 35383033474447895560", "Счет **5560"),
        ("Visa Classic 6831982476737658", "Visa Classic 6831 98** **** 7658"),
        ("Visa Platinum 8990922113665229", "Visa Platinum 8990 92** **** 5229"),
        ("Visa Gold 5999414228426353", "Visa Gold 5999 41** **** 6353"),
        ("Счет 73654108430135874305", "Счет **4305"),
    ],
)
def test_mask_account_card_success(card_number: str, expected_result: str) -> None:
    # Проверка: ожидаемый результат == фактический
    assert mask_account_card(card_number) == expected_result


def test_mask_account_card_error() -> None:  # тест на вызываемые ошибки
    with pytest.raises(ValueError) as err:
        mask_account_card()
        assert str(err.value) == "Ошибка - входные данные отсутствуют"

    with pytest.raises(ValueError) as err:
        mask_account_card("")
        assert str(err.value) == "Ошибка - передана пустая строка"

    with pytest.raises(ValueError) as err:
        mask_account_card("Visa Platinum 8990922113665229, Счет 73654108430135874305")
        assert str(err.value) == "Ошибка - слишком много входных данных"


# Функция теста с использованием параметризации
@pytest.mark.parametrize(
    "data_list, expected_result",
    [
        ("2024-03-11T02:26:18.671407", "11.03.2024"),
        ("2023-12-31T23:59:59.999999", "31.12.2023"),
        ("2025-01-01T00:00:00.000001", "01.01.2025"),
        ("2024-05-20T14:30:15.123456", "20.05.2024"),
    ],
)
def test_get_date(data_list: str, expected_result: str) -> None:
    # Проверка: ожидаемый результат == фактический
    assert get_date(data_list) == expected_result
