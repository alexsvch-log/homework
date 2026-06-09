from datetime import datetime, timedelta

import requests
from requests import Response


def conversion_of_transactions_to_rub(transaction: dict) -> float:
    """Функция принимает на вход транзакцию и возвращает сумму транзакции (amount) в рублях, округленную до копеек,
    тип данных — float. Если транзакция была в USD или EUR, происходит конвертация суммы отранзакции в рубли по курсу
     на дату транзакции. Для получения данных о курсе валюты транзакции на дату транзакции используется
     функция rates_of_usd_eur_by_date"""

    operation_amount = transaction.get("operationAmount", {})
    currency_info = operation_amount.get("currency", {})
    currency_code = currency_info.get("code")
    date_of_transaction = transaction.get("date")
    if currency_code == "RUB":
        amount_rub = float(operation_amount.get("amount", 0.0))
    else:
        # Проверяем, что дата существует и является строкой
        if not date_of_transaction or not isinstance(date_of_transaction, str):
            print("Ошибка: В транзакции отсутствует дата")
            return 0.0  # Чтобы  mypy на 100% уверен, что date_of_transaction — это str

        currency_rate = rates_of_usd_eur_by_date(date_of_transaction, currency_code)

        if currency_rate is None:
            amount_rub = 0.0
            print("Ошибка, курс валюты не найден")
        else:
            amount_rub = round(float(operation_amount.get("amount")) * currency_rate, 2)
    return amount_rub


def rates_of_usd_eur_by_date(required_date: str, currency_code: str) -> float | None:
    """Функция принимает на вход дату в формате "YYYY-MM-DDTHH:MM:SS.ffffff" и код требуемой валюты и возвращает курс
    заданной валюты на заданную дату. В случае, если входящая дата попадает на выходной день и курс валюты отсутствует,
    берется курс валюты на ближайщий предыдущий рабочий день.
    Для получения данных по курсам валют используется ресурс ЦБ РФ API: https://cbr-xml-daily.ru
    с обращением к архивному блоку."""

    # 1. Парсим входящий формат "YYYY-MM-DDTHH:MM:SS.ffffff"
    try:
        current_date = datetime.strptime(required_date, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        print("Ошибка: Неверный формат даты. Ожидается YYYY-MM-DDTHH:MM:SS.ffffff")
        return None

    # 2. Запускаем цикл для поиска рабочей даты
    while True:
        # Для URL API нужен формат со слэшами "YYYY/MM/DD"
        date_str_url = current_date.strftime("%Y/%m/%d")
        url = f"https://cbr-xml-daily.ru/archive/{date_str_url}/daily_json.js"

        try:
            response: Response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()

                if currency_code in data["Valute"]:
                    rate_value = float(data["Valute"][currency_code]["Value"])
                    return rate_value
                else:
                    print(f"Валюта {currency_code} не найдена в базе ЦБ.")
                    return None

            # Если выходной (404), уменьшаем дату на 1 день
            elif response.status_code == 404:
                current_date -= timedelta(days=1)
                if current_date < datetime(1992, 1, 1):
                    print("Архив ЦБ РФ доступен только с 1992 года.")
                    return None
            else:
                print(f"Ошибка сервера: {response.status_code}")
                return None

        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None
