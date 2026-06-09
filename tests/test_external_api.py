# файл: tests/test_external_api.py
from unittest.mock import MagicMock, patch

from requests.exceptions import RequestException

# Импортируем функции, код которых нужно протестировать
from src.external_api import conversion_of_transactions_to_rub, rates_of_usd_eur_by_date

# Готовый шаблон успешного ответа от API ЦБ
MOCK_SUCCESS_DATA = {"Valute": {"USD": {"Value": 75.50}, "EUR": {"Value": 85.20}}}


# 1. Функция успешного теста rates_of_usd_eur_by_date (успешный запрос курса валюты (код 200))
@patch("src.external_api.requests.get")
def test_rates_of_usd_eur_by_date_success(mock_get: MagicMock) -> None:
    # Настраиваем mock для requests.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_SUCCESS_DATA
    mock_get.return_value = mock_response

    # Вызываем функцию
    result = rates_of_usd_eur_by_date("2026-06-05T12:00:00.000000", "USD")

    # Проверка
    assert result == 75.50
    mock_get.assert_called_once_with("https://cbr-xml-daily.ru/archive/2026/06/05/daily_json.js", timeout=5)


# 2. Функция успешного теста rates_of_usd_eur_by_date (смещение даты назад, если выпал выходной (код 404))
@patch("src.external_api.requests.get")
def test_rates_weekend_fallback(mock_get: MagicMock) -> None:
    # Первый вызов вернет 404 (выходной), второй — 200 (рабочий день)
    mock_response_404 = MagicMock()
    mock_response_404.status_code = 404

    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200
    mock_response_200.json.return_value = MOCK_SUCCESS_DATA

    # side_effect позволяет возвращать разные ответы при последовательных вызовах
    mock_get.side_effect = [mock_response_404, mock_response_200]

    result = rates_of_usd_eur_by_date("2026-06-07T12:00:00.000000", "EUR")

    # Проверяем, что вернулся курс за предыдущий день
    assert result == 85.20
    # Проверяем, что было сделано ровно 2 запроса
    assert mock_get.call_count == 2


# 3. Функция неудачного теста rates_of_usd_eur_by_date (передача даты в неверном формате (сразу возвращает None))
def test_rates_invalid_date_format() -> None:
    # Здесь patch не нужен, так как до запроса в сеть код не дойдет
    result = rates_of_usd_eur_by_date("2026-06-07", "USD")
    assert result is None


# 4. Функция неудачного теста rates_of_usd_eur_by_date (ошибка сервера (код 500))
@patch("src.external_api.requests.get")
def test_rates_server_error(mock_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    result = rates_of_usd_eur_by_date("2026-06-05T12:00:00.000000", "USD")
    assert result is None


# 5. Функция неудачного теста rates_of_usd_eur_by_date (заданной валюты нет в базе ЦБ)
@patch("src.external_api.requests.get")
def test_rates_currency_out_of_base(mock_get: MagicMock) -> None:
    # 1. Готовим ответ API, в котором есть USD, но нет запрашиваемого KZT
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Valute": {"USD": {"Value": 75.50}}}
    # 2. Передаем этот ответ в mock
    mock_get.return_value = mock_response

    # 3. Вызываем функцию с отсутствующей в базе валютой KZT
    result = rates_of_usd_eur_by_date("2026-06-05T12:00:00.000000", "KZT")

    # 4. Проверяем результат
    assert result is None

    # 5. Проверяем, что запрос ушел по правильному адресу
    mock_get.assert_called_once_with("https://cbr-xml-daily.ru/archive/2026/06/05/daily_json.js", timeout=5)


# 6. Функция неудачного теста rates_of_usd_eur_by_date (заданная дата раньше, чем 01.01.1992)
@patch("src.external_api.requests.get")
def test_rates_currency_date_too_early(mock_get: MagicMock) -> None:
    # 1. API возвращает 404 (в 1991 году этой страницы на сайте ЦБ просто нет)
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    # 2. Вызываем функцию с датой из 1991 года
    result = rates_of_usd_eur_by_date("1991-12-31T12:00:00.000000", "USD")

    # 3. Проверяем, что функция вернула None, так как дата ушла глубже 1992 года
    assert result is None

    # 4. Проверяем, что запрос ушел по адресу с реальной переданной датой (1991/12/31)
    mock_get.assert_called_once_with("https://cbr-xml-daily.ru/archive/1991/12/31/daily_json.js", timeout=5)


# 7. Функция неудачного теста rates_of_usd_eur_by_date (критическая ошибка сети (исключение при запросе))
@patch("src.external_api.requests.get")
def test_rates_network_exception(mock_get: MagicMock) -> None:
    # Вместо возврата ответа заставляем mock выбросить ошибку сети
    mock_get.side_effect = RequestException("Connection refused")

    # Вызываем функцию
    result = rates_of_usd_eur_by_date("2026-06-05T12:00:00.000000", "USD")

    # Проверяем, что функция безопасно обработала ошибку и вернула None
    assert result is None

    # Проверяем, что попытка запроса всё же была совершена
    mock_get.assert_called_once_with("https://cbr-xml-daily.ru/archive/2026/06/05/daily_json.js", timeout=5)


# ======================================================================
# 1. Функция удачного теста conversion_of_transactions_to_rub (транзакция изначально в RUB
# (внешняя функция курса не должна вызываться))
def test_conversion_to_rub() -> None:
    transaction = {
        "date": "2026-06-05T12:00:00.000000",
        "operationAmount": {"amount": "150.50", "currency": {"code": "RUB"}},
    }

    # Задаем patch как контекстный менеджер, чтобы убедиться, что он НЕ вызвался
    with patch("src.external_api.rates_of_usd_eur_by_date") as mock_get_rate:
        result = conversion_of_transactions_to_rub(transaction)

        assert result == 150.50
        mock_get_rate.assert_not_called()  # Проверяем, что к функции курса не было обращений


# 2. Функция удачного теста conversion_of_transactions_to_rub (транзакция в USD
# (проверяем конвертацию и округление до копеек))
@patch("src.external_api.rates_of_usd_eur_by_date")
def test_conversion_of_transactions_to_rub(mock_get_rate: MagicMock) -> None:
    transaction = {
        "date": "2026-06-05T12:00:00.000000",
        "operationAmount": {"amount": "100.00", "currency": {"code": "USD"}},
    }
    # Настраиваем фейковый курс доллара
    mock_get_rate.return_value = 75.1234

    result = conversion_of_transactions_to_rub(transaction)

    # 100.00 * 75.1234 = 7512.34
    assert result == 7512.34
    # Проверяем, что функция курса была вызвана с правильными аргументами
    mock_get_rate.assert_called_once_with("2026-06-05T12:00:00.000000", "USD")


# 3. Функция неудачного теста conversion_of_transactions_to_rub (в словаре транзакции отсутствует ключ 'date')
def test_conversion_rub_bad_date() -> None:
    transaction = {
        1: "2026-06-05T12:00:00.000000",
        "operationAmount": {"amount": "150.50", "currency": {"code": "USD"}},
    }

    # Задаем patch как контекстный менеджер, чтобы убедиться, что он НЕ вызвался
    with patch("src.external_api.rates_of_usd_eur_by_date") as mock_get_rate:
        result = conversion_of_transactions_to_rub(transaction)

        assert result == 0.0
        mock_get_rate.assert_not_called()  # Проверяем, что к функции курса не было обращений


# 4. Функция неудачного теста conversion_of_transactions_to_rub (обработка ошибки, если функция курса вернула None)
@patch("src.external_api.rates_of_usd_eur_by_date")
def test_conversion_of_transactions_to_rub_not_found(mock_get_rate: MagicMock) -> None:
    transaction = {
        "date": "2026-06-05T12:00:00.000000",
        "operationAmount": {"amount": "50.00", "currency": {"code": "EUR"}},
    }
    # Имитируем, что курс не найден (например, ошибка сети внутри rates_of_usd_eur_by_date)
    mock_get_rate.return_value = None
    result = conversion_of_transactions_to_rub(transaction)
    assert result == 0.0
