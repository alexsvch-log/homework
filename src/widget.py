from datetime import datetime

from src.masks import get_mask_account, get_mask_card_number


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

    # 1. Безопасная проверка на None или пустую строку
    if not card_account_number or not isinstance(card_account_number, str):
        return ""

    parts: list[str] = card_account_number.split()

    # 2. Если в строке нет цифр или только одно слово (нет номера)
    if len(parts) < 2:
        return card_account_number  # Возвращаем как есть, чтобы не потерять текст

    # Извлекаем сам номер (всегда последнее слово в строке)
    number_part: str = parts[-1]

    # Извлекаем название (все слова до номера)
    name_part: str = " ".join(parts[:-1])

    # 3. Логика для Счета
    if "Счет" in name_part:
        return f"Счет {get_mask_account(number_part)}"

    # 4. Логика для Карты
    return f"{name_part} {get_mask_card_number(number_part)}"


def get_date(data_time: str) -> str:
    """Функция принимает на вход строку с датой в формате "2024-03-11T02:26:18.671407" и возвращает строку с датой
    в ISO формате "ДД.ММ.ГГГГ" ("11.03.2024")"""
    if not data_time or not isinstance(data_time, str):
        return "00.00.0000"
    try:
        # Срез [:19] отсекает микросекунды, оставляя 'ГГГГ-ММ-ДДTЧЧ:ММ:СС'
        # Это приводит все даты к одному стандарту для старых версий Python
        clean_date = data_time[:19]
        date_obj = datetime.fromisoformat(clean_date)
        return date_obj.strftime("%d.%m.%Y")
    except ValueError:
        return "00.00.0000"
