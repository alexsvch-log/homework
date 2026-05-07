from datetime import datetime

from src.masks import get_mask_card_number
from src.masks import get_mask_account


def mask_account_card(card_account_number: str | None = None) -> str:
    """Функция обрабатывает информацию как о картах, так и о счетах. Принимает один аргумент — строку, содержащую тип
    и номер карты или счета. Возвращает строку с замаскированным номером.
    Логика проверки ошибок:
    1. Входные данные отстствуют (переменной по умолчанию присваивается None. Если другого значения нет,
    то данные не введены).
    2. Во входных данных передана пустая строка ''. В этом случае значение parts будет пустым.
    3. Входные данные состоят из более двух строк. Преополагается, что каждая строка может быть строго
    либо 'Наименование карты + номер карты', либо 'Счет + номер счета'. перестановка внури строки, либо вторая строка,
    состоящая только из наименования карты, либо только из слова 'Счет',
    либо из только из набора цифр, не рассматривается"""

    if card_account_number is None:  # Проверка - передано ли хоть что-то
        return "Ошибка: Входные данные отсутствуют"

    parts: list[str] = card_account_number.split()

    if not parts:  # Если передана пустая строка ""
        return "Ошибка: Строка пуста"

    if len(parts) not in [2, 3]:  # Если передано более двух строк
        return "Ошибка: Слишком много входных данных"

    if "Счет" in card_account_number:  # Если в строке присутствует слово 'Счет', то это номер расчетного счета
        account_number: str = card_account_number.split()[-1]
        return f"Счет {get_mask_account(account_number)}"

    card_number: str = parts[-1]
    card_name: str = " ".join(parts[:-1])
    return f"{card_name} {get_mask_card_number(card_number)}"


# print(mask_account_card("MasterCard 7158300734726758"))
# print(mask_account_card("Счет 73654108430135874305"))
# print(mask_account_card())
# print(mask_account_card(""))
# print(mask_account_card("Счет 73654108430135874305, MasterCard 7158300734726758"))


def get_date(data_time: str) -> str:
    """Функция принимает на вход строку с датой в формате "2024-03-11T02:26:18.671407" и возвращает строку с датой
    в ISO формате "ДД.ММ.ГГГГ" ("11.03.2024")"""

    date: datetime = datetime.fromisoformat(data_time)
    return date.strftime("%d.%m.%Y")


# print(get_date("2024-03-11T02:26:18.671407"))
