def get_mask_card_number(card_number: str) -> str:
    """Функция  принимает на вход номер карты и возвращает ее маску. Номер карты замаскирован и отображается в формате
    XXXX XX** **** XXXX, где X — это цифра номера. То есть видны первые 6 цифр и последние 4 цифры, остальные символы
    отображаются звездочками, номер разбит по блокам по 4 цифры, разделенным пробелами."""

    # Убираем пробелы, если они есть, переводим в формат str и проверяем длину
    clean_card_number: str = str(card_number).replace(" ", "")

    if len(clean_card_number) != 16:
        return "Ошибка: Неверная длина номера карты"

    # Маскируем части (заменяем * цифры с 7 по 12)
    # Формат: 7000 92** **** 6361
    masked_card_number = f"{clean_card_number[0:4]} {clean_card_number[5:7]}** **** {clean_card_number[12:16]}"
    return masked_card_number


# print(get_mask_card_number("700 0792289 60636 1"))


def get_mask_account(account_number: str) -> str:
    """Функция принимает на вход номер счета и возвращает его маску. Номер счета замаскирован и отображается в формате
    **XXXX, где X — это цифра номера. То есть видны только последние 4 цифры номера, а перед ними — две звездочки."""

    # Убираем пробелы, если они есть, переводим в формат str и проверяем длину
    clean_account_number: str = str(account_number).replace(" ", "")

    if len(clean_account_number) != 20:
        return "Ошибка: Неверная длина номера счета"

    # Маскируем части (оставляем только последние 4 цифры и перед ними два знака *)
    # Формат: **XXXX
    masked_account_number = f"**{clean_account_number[16:21]}"
    return masked_account_number


# print(get_mask_account("73654108430135874305"))
