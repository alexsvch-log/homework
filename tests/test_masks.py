# файл: tests/test_mask.py
import pytest

# Импортируем функци, код которых нужно протестировать
from src.masks import get_mask_account, get_mask_card_number


# Функция теста с использованием параметризации
@pytest.mark.parametrize(
    "card_number, expected_result",
    [
        ("7000792289606361", "7000 79** **** 6361"),
        ("700 07922 8960 63 61", "7000 79** **** 6361"),
    ],
)
def test_get_mask_card_number_success(card_number: str, expected_result: str) -> None:
    assert get_mask_card_number(card_number) == expected_result


def test_get_mask_card_number_error() -> None:  # тест на вызываемые ошибки
    with pytest.raises(ValueError) as err:
        get_mask_card_number("")
        assert str(err.value) == "Ошибка - длина номера карты должна быть ровно 16 символов."

    with pytest.raises(ValueError) as err:
        get_mask_card_number("700 0922- bvs 60631")
        assert str(err.value) == "Ошибка - номер карты должен состоять только из цифр."


# Функция теста с использованием параметризации
@pytest.mark.parametrize(
    "account_number, expected_result",
    [("73654108430135874305", "**4305"), ("736 541 0843 01 3587 4305", "**4305")],
)
def test_get_mask_account_success(account_number: str, expected_result: str) -> None:
    # Проверка: ожидаемый результат == фактический
    assert get_mask_account(account_number) == expected_result


def test_get_mask_account_number_error() -> None:  # тест на вызываемые ошибки
    with pytest.raises(ValueError) as err:
        get_mask_account("")
    assert str(err.value) == "Ошибка - длина номера счета должна быть ровно 20 символов."

    with pytest.raises(ValueError) as err:
        get_mask_account("73084 3dg01 35511 -5468")
    assert str(err.value) == "Ошибка - номер счета должен состоять только из цифр."
