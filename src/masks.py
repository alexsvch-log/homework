import logging
from pathlib import Path

# --- УЧЕБНАЯ НАСТРОЙКА ЛОГИРОВАНИЯ ВНУТРИ МОДУЛЯ (потом переделать в глобальную настройку в main.py и conftest.py)---
# Находим корень проекта (поднимаемся на две папки вверх от текущего файла masks.py)
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "masks.log"

# Гарантируем, что папка log существует
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Создаем персональный логгер именно для этого модуля
# Основная конфигурация logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
    filename=str(LOG_FILE),  # Запись логов в файл
    filemode="w",
    encoding="utf-8",
)  # Перезапись файла при каждом запуске

# Создаем логеры для различных компонентов программы
number_logger = logging.getLogger("app.number")
account_logger = logging.getLogger("app.account")


def get_mask_card_number(card_number: str) -> str:
    """Функция  принимает на вход номер карты и возвращает ее маску. Номер карты замаскирован и отображается в формате
    XXXX XX** **** XXXX, где X — это цифра номера. То есть видны первые 6 цифр и последние 4 цифры, остальные символы
    отображаются звездочками, номер разбит по блокам по 4 цифры, разделенным пробелами."""

    # Убираем пробелы, если они есть, переводим в формат str и проверяем длину
    clean_card_number: str = str(card_number).replace(" ", "")
    number_logger.info("убраны лишние пробелы")
    # Проверяем длину номера карты
    if len(clean_card_number) != 16:
        number_logger.error(f"Ошибка - длина номера {clean_card_number} карты не соответсвует 16 символам")
        raise ValueError("Ошибка - длина номера карты должна быть ровно 16 символов.")

    # Проверяем, что в номере нет посторонних символов (букв, спецсимволов)
    if not clean_card_number.isdigit():
        number_logger.error(f"Ошибка - в номере карты {clean_card_number} присутствуют посторонние спецсимволы")
        raise ValueError("Ошибка - номер карты должен состоять только из цифр.")

    # Маскируем части (заменяем * цифры с 7 по 12)
    # Формат: 7000 92** **** 6361
    masked_card_number = f"{clean_card_number[0:4]} {clean_card_number[4:6]}** **** {clean_card_number[12:16]}"
    number_logger.info(f"Произведена маскировка номера карты {masked_card_number}")
    return masked_card_number


def get_mask_account(account_number: str) -> str:
    """Функция принимает на вход номер счета и возвращает его маску. Номер счета замаскирован и отображается в формате
    **XXXX, где X — это цифра номера. То есть видны только последние 4 цифры номера, а перед ними — две звездочки."""

    # Убираем пробелы, если они есть, переводим в формат str и проверяем длину
    clean_account_number: str = str(account_number).replace(" ", "")
    account_logger.info("убраны лишние пробелы")

    # Проверяем длину номера счета
    if len(clean_account_number) != 20:
        account_logger.error(f"Ошибка - длина номера {clean_account_number} счета не соответсвует 20 символам")
        raise ValueError("Ошибка - длина номера счета должна быть ровно 20 символов.")

    # Проверяем, что в номере нет посторонних символов (букв, спецсимволов)
    if not clean_account_number.isdigit():
        account_logger.error(f"Ошибка - в номере счета {clean_account_number} присутствуют посторонние спецсимволы")
        raise ValueError("Ошибка - номер счета должен состоять только из цифр.")

    # Маскируем части (оставляем только последние 4 цифры и перед ними два знака *)
    # Формат: **XXXX
    masked_account_number = f"**{clean_account_number[-4:]}"
    account_logger.info(f"Произведена маскировка номера счета {masked_account_number}")
    return masked_account_number
