# файл: tests/test_widget.py

# Импортируем функции, код которых нужно протестировать
from src.widget import mask_account_card
from src.widget import get_date


# Функция теста
def test_mask_account_card() -> None:
    # Проверка: ожидаемый результат == фактический
    assert mask_account_card("Maestro 1596837868705199") == "Maestro 1596 83** **** 5199"
    assert mask_account_card("Счет 64686473678894779589") == "Счет **9589"
    assert mask_account_card("MasterCard 7158300734726758") == "MasterCard 7158 30** **** 6758"
    assert mask_account_card("Счет 35383033474447895560") == "Счет **5560"
    assert mask_account_card("Visa Classic 6831982476737658") == "Visa Classic 6831 98** **** 7658"
    assert mask_account_card("Visa Platinum 8990922113665229") == "Visa Platinum 8990 92** **** 5229"
    assert mask_account_card("Visa Gold 5999414228426353") == "Visa Gold 5999 41** **** 6353"
    assert mask_account_card("Счет 73654108430135874305") == "Счет **4305"
    assert mask_account_card() == "Ошибка: Входные данные отсутствуют"
    assert mask_account_card("") == "Ошибка: Строка пуста"
    assert (
        mask_account_card("Visa Platinum 8990922113665229, Счет 73654108430135874305")
        == "Ошибка: Слишком много входных данных"
    )


# Функция теста
def test_get_date() -> None:
    # Проверка: ожидаемый результат == фактический
    assert get_date("2024-03-11T02:26:18.671407") == "11.03.2024"
    assert get_date("2023-12-31T23:59:59.999999") == "31.12.2023"
    assert get_date("2025-01-01T00:00:00.000001") == "01.01.2025"
    assert get_date("2024-05-20T14:30:15.123456") == "20.05.2024"
