from masks import get_mask_card_number
from masks import get_mask_account


def mask_account_card(card_account_number: str) -> str:
    """Функция обрабатывает информацию как о картах, так и о счетах. Принимает один аргумент — строку, содержащую тип
    и номер карты или счета. Возвращает строку с замаскированным номером"""

    if "Счет" in card_account_number:
        account_number: str = card_account_number.split()[-1]
        return f"Счет {get_mask_account(account_number)}"

    parts: list[str] = card_account_number.split()
    cart_number: str = parts[-1]
    cart_name: str = " ".join(parts[:-1])
    return f"{cart_name} {get_mask_card_number(cart_number)}"


print(mask_account_card("Visa Platinum 7000792289606361"))
print(mask_account_card("Счет 73654108430135874305"))


def get_date(data_time: str) -> str:
    """Функция принимает на вход строку с датой в формате "2024-03-11T02:26:18.671407" и возвращает строку с датой
    в формате "ДД.ММ.ГГГГ" ("11.03.2024")"""

    date: str = data_time.replace("-", "")[0:8]
    return f"{date[6:8]}.{date[4:6]}.{date[0:4]}"


print(get_date("2024-03-11T02:26:18.671407"))
