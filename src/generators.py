from collections.abc import Iterator

""" Конструкция для Python версии 3.9 и новее. Вместо общего Any добавлен точный Iterator[dict]. При этом вместо
модуля typing используются встроенные типы и классы из стандартной библиотеки collections.abc"""
# Вход: list[dict] с маленькой буквы (вместо typing.List)
# Выход: Iterator[dict] из collections.abc


def filter_by_currency(list_of_transactions: list[dict], currency_key: str) -> Iterator[dict]:
    """Функция принимает на вход список словарей, представляющих транзакции.
    Функция возвращает итератор, который поочередно выдает транзакции,
    где код валюты операции соответствует заданному.
    """
    for transaction in list_of_transactions:
        # Безопасно извлекаем код валюты с помощью метода .get по шагам.
        operation_amount = transaction.get("operationAmount", {})
        currency_info = operation_amount.get("currency", {})
        currency_code = currency_info.get("code")

        if currency_code == currency_key:
            yield transaction


# usd_transactions = filter_by_currency(list_of_transactions, "USD")
# for _ in range(2):
#     result = next(usd_transactions, "Транзакций больше нет")
#     print(result)


def transaction_descriptions(list_of_transactions: list[dict]) -> Iterator[str]:
    """Функция принимает список словарей с транзакциями и возвращает описание каждой операции по очереди."""
    for transaction in list_of_transactions:
        # Безопасно извлекаем значения транзакций с помощью метода .get
        operation_amount = transaction.get("description", "Без описания")
        yield operation_amount


# descriptions = transaction_descriptions(list_of_transactions)
# for _ in range(6):
#     result = next(descriptions, "Транзакций больше нет")
#     print(result)


def card_number_generator(start: int, end: int) -> Iterator[str]:
    """Функция - генератор, который выдает номера банковских карт в формате XXXX XXXX XXXX XXXX, где X — цифра номера
    карты. Генератор может генерировать номера карт в заданном диапазоне от 0000 0000 0000 0001 до 9999 9999 9999 9999.
    Генератор должен принимать начальное и конечное значения для генерации диапазона номеров.
    """
    if start <= 0 or end > 9999999999999999:
        raise ValueError("Входные данные выходят за рамки заданного диапазона")

    for number in range(start, end + 1):
        # 1. f"{number:016}" дополняет число нулями слева до 16 символов (0000000000000021)
        card_number = f"{number:016}"

        # 2. Разрезаем строку на части по 4 символа и соединяем пробелом
        card_number_formatted = f"{card_number[0:4]} {card_number[4:8]} {card_number[8:12]} {card_number[12:16]}"

        yield card_number_formatted


# for card_number in card_number_generator(0, 5):
#     print(card_number)
