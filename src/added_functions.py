from datetime import datetime
from typing import Iterator

from src.widget import get_date, mask_account_card


# 2. Функция для валидации ввода дат
def get_optional_iso_date(prompt_text: str) -> str | None:
    """Запрашивает у пользователя дату и озвращает дату в формате ISO или None, если пользователь нажал Enter."""
    while True:
        user_input = input(prompt_text).strip()
        if not user_input:  # Если строка пустая, период не задан
            return None
        try:
            # Проверяем корректность даты
            valid_date = datetime.strptime(user_input, "%Y-%m-%d")
            return valid_date.date().isoformat()
        except ValueError:
            print("Ошибка: неверный формат. Используйте ГГГГ-ММ-ДД или нажмите Enter для пропуска.\n")


def format_transactions_generator(transactions: list[dict]) -> Iterator[str]:
    """Принимает список словарей с транзакциями, поочередно форматирует их, маскирует номера карт/счетов
    и возвращает готовые для вывода текстовые блоки. Функция устойчива к некорректным данным: пропускает
    пустые элементы и обрабатывает ошибки преобразования сумм."""

    for op in transactions:
        # Проверяем, что элемент является непустым словарем
        if not op or not isinstance(op, dict):
            continue

        # 1. Форматируем дату
        raw_date = op.get("date")
        formatted_date = get_date(raw_date) if raw_date else "00.00.0000"

        # 2. Получаем описание
        description = op.get("description", "Неизвестная операция")

        # 3. Извлекаем сумму и валюту
        op_amount = op.get("operationAmount", {})
        amount = op_amount.get("amount") or op.get("amount", "0")
        currency = op_amount.get("currency", {}).get("name") or op.get("currency_name", "")

        try:
            display_amount = f"{float(amount):.2f}"
        except (ValueError, TypeError):
            display_amount = str(amount)

        # 4. Маскируем карты/счета
        raw_from = op.get("from")
        raw_to = op.get("to")
        masked_from = mask_account_card(raw_from) if raw_from else ""
        masked_to = mask_account_card(raw_to) if raw_to else ""

        # 5. Собираем финальный текстовый блок
        lines = [f"{formatted_date} {description}"]

        if masked_from and masked_to:
            lines.append(f"{masked_from} -> {masked_to}")
        elif masked_to:
            lines.append(f" -> {masked_to}")
        elif masked_from:
            lines.append(masked_from)

        lines.append(f"Сумма: {display_amount} {currency}\n")

        yield "\n".join(lines)
