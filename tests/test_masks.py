# файл: tests/test_mask.py

# Импортируем функци, код которых нужно протестировать
from src.masks import get_mask_card_number, get_mask_account


# Функция теста
def test_get_mask_card_number() -> None:
    # Проверка: ожидаемый результат == фактический
    assert get_mask_card_number("7000792289606361") == "7000 92** **** 6361"
    assert get_mask_card_number("700 07922 8960 63 61") == "7000 92** **** 6361"
    assert get_mask_card_number("700 07922 8960 6333 61") == "Ошибка: Неверная длина номера карты"


# Импортируем функцию, код которой нужно протестировать
# Функция теста
def test_get_mask_account() -> None:
    # Проверка: ожидаемый результат == фактический
    assert get_mask_account("73654108430135874305") == "**4305"
    assert get_mask_account("736 541 0843 01 3587 4305") == "**4305"
    assert get_mask_account("73654108430135511546874305") == "Ошибка: Неверная длина номера счета"
