def filter_by_state(transactions_original_list: list, state: str = "EXECUTED") -> list:
    """Функция принимает словарь с транзакциями и выбирает только те транзакции,
    которые заданы в ключе state (по умолчанию значение state = 'EXECUTED')"""
    transactions_filtered_by_state: list = []
    for transaction in transactions_original_list:
        if transaction["state"] == state:
            transactions_filtered_by_state.append(transaction)
    return transactions_filtered_by_state


def sort_by_date(transactions_original_list: list, reverse: bool = True) -> list:
    """Функция принимает список словарей с транзакциями и возвращает список словарей с транзакциями,
    отсортированными по дате (ключ 'date')"""
    transactions_sorted_by_date: list = sorted(
        transactions_original_list, key=lambda transaction: transaction["date"], reverse=reverse
    )
    return transactions_sorted_by_date
