# файл: tests/test_transaction_reader_in_csv_xlsx.py
import csv
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest

# Импортируем функции, код которых нужно протестировать
from src.transaction_reader_in_csv_xlsx import transaction_reader_in_csv, transaction_reader_in_xlsx


# Фиктивный путь для передачи в функцию transaction_reader_in_csv во время тестов (file_path).
@pytest.fixture
def fake_path() -> Path:
    return Path("fake_dir/transactions.csv")


# --- ГРУППА ТЕСТОВ для функции transaction_reader_in_csv: СЧИТЫВАНИЕ И ВАЛИДАЦИЯ CSV (1 - 5)
# И ИСКЛЮЧЕНИЯ И ОТКРЫТИЕ ФАЙЛА (EXCEPT)(6 - 8)---


# 1. Функция успешного теста transaction_reader_in_csv (успешное чтение правильного CSV файла).
def test_successful_read_csv(fake_path: Path) -> None:
    csv_content = (
        "id;state;date;amount;currency_name;currency_code;from;to;description\n650703;"
        "EXECUTED;2023-01-01;100.0;Рубль;RUB;card;account;Перевод\n"
    )

    # Изолируем open и передаем содержимое файла
    with patch("builtins.open", mock_open(read_data=csv_content)):
        result = transaction_reader_in_csv(fake_path)

        assert len(result) == 1  # Функция нашла и успешно обработала ровно одну строку с транзакцией
        # (в одной строке лежит один словарь).
        assert result[0]["id"] == "650703"  # Берем первый элемент списка (словарь под индексом 0) и проверяем,
        # что в нем значение под ключом "id" строго равно строке "650703".
        assert result[0]["state"] == "EXECUTED"  # Берем первый элемент списка (словарь под индексом 0) и проверяем,
        # что в нем значение под ключом "state" строго равно строке "EXECUTED".
        assert result[0]["amount"] == "100.0"  # Берем первый элемент списка (словарь под индексом 0) и проверяем,
        # что в нем значение под ключом "amount" строго равно строке "100.0".


# 2. Функция неудачного теста transaction_reader_in_csv (SCV файл абсолютно пустой (нет заголовков)).
def test_empty_file(fake_path: Path) -> None:
    with patch("builtins.open", mock_open(read_data="")):
        result = transaction_reader_in_csv(fake_path)
        assert result == []


# 3. Функция неудачного теста transaction_reader_in_csv когда в заголовках есть пустые поля или None).
def test_empty_or_none_headers(fake_path: Path) -> None:
    # Заголовки содержат пустую строку между id и date (id;;date)
    csv_content = (
        "id;;date;amount;currency_name;currency_code;from;to;description\n"
        "650703;;2023-01-01;100.0;RUB;RUB;card;account;test"
    )
    with patch("builtins.open", mock_open(read_data=csv_content)):
        result = transaction_reader_in_csv(fake_path)
        assert result == []


# 4. Функция неудачного теста transaction_reader_in_csv пропуска строк, которые содержат лишние неразмеченные колонки
# (row.get(None) is not None).
def test_row_with_extra_columns(fake_path: Path) -> None:
    # В первой строчке данных на одно значение больше, чем заголовков (лишнее ';extra')
    csv_content = (
        "id;state;date;amount;currency_name;currency_code;from;to;description\n"
        "1;EXECUTED;2023-01-01;100.0;Рубль;RUB;card;account;Перевод;extra\n"
        "2;PENDING;2023-01-02;200.0;Рубль;RUB;card;account;Оплата\n"
    )

    with patch("builtins.open", mock_open(read_data=csv_content)):
        result = transaction_reader_in_csv(fake_path)
        # Первая строка должна отброситься, вторая — успешно записаться
        assert len(result) == 1
        assert result[0]["id"] == "2"


# 5. Функция неудачного теста transaction_reader_in_csv пропуска строки, если DictReader по какой-то
# причине вернул не словарь (not isinstance(row, dict)).
def test_row_is_not_dict(fake_path: Path) -> None:
    csv_content = "id;state\n1;EXECUTED"

    with patch("builtins.open", mock_open(read_data=csv_content)):
        # Мокаем поведение итератора DictReader, чтобы он принудительно выдал список вместо словаря
        with patch("csv.DictReader") as mock_reader:
            mock_instance = MagicMock()
            mock_instance.fieldnames = ["id", "state"]  # Данная строка принудительно говорит mock-объекту:
            # "Когда код во время теста спросит у тебя fieldnames, ответь ему списком ["id", "state"]".
            # Возвращаем сначала список (не словарь), а затем обычный словарь
            mock_instance.__iter__.return_value = [
                ["1", "EXECUTED"],
                {"id": "2", "state": "PENDING"},
            ]  # Магический метод
            # __iter__ отвечает за то, чтобы объект можно было перебирать в цикле for (делать его итерируемым).
            # когда Python вызывает метод __iter__ у объекта reader в коде тестируемой функции :for row in reader:
            # в тесте идет замена через обращение (mock_instance.__iter__ )  к mock-версии этого магического метода.
            mock_reader.return_value = mock_instance

            result = transaction_reader_in_csv(fake_path)
            # Список должен проигнорироваться, считаться должен только словарь со id=2
            assert len(result) == 1
            assert result[0]["id"] == "2"


# 6. Функция неудачного теста transaction_reader_in_csv обработки исключения FileNotFoundError.
def test_file_not_found_exception(fake_path: Path) -> None:
    with patch("builtins.open", side_effect=FileNotFoundError):  # Параметр side_effect
        # используется для выбрасывания исключение (ошибки).
        result = transaction_reader_in_csv(fake_path)
        assert result == []


# 7. Функция неудачного теста transaction_reader_in_csv обработки исключения UnicodeDecodeError.
def test_unicode_decode_exception(fake_path: Path) -> None:
    with patch("builtins.open", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid")):  # в Python исключение
        # UnicodeDecodeError нельзя создать «пустым» — в отличие от FileNotFoundError.
        # Его конструктор строго требует передать детали ошибки, иначе сам тест упадет
        # с синтаксической ошибкой еще до начала проверки.
        result = transaction_reader_in_csv(fake_path)
        assert result == []


# 8. Функция неудачного теста transaction_reader_in_csv обработки внутренних ошибок модуля csv (csv.Error).
# Файл открылся, но в нем сломаные данные.
def test_csv_error_exception(fake_path: Path) -> None:
    # 1. Имитируем, что файл успешно открылся и в нем есть какие-то данные
    with patch("builtins.open", mock_open(read_data="id;state")):
        with patch("csv.DictReader") as mock_reader:
            # 2. Настраиваем заглушку для DictReader
            mock_instance = MagicMock()
            # Говорим, что при чтении строк (итерации) вылетит csv.Error
            mock_instance.__iter__.side_effect = csv.Error("Симуляция ошибки структуры CSV")

            # 3. Связываем: при вызове csv.DictReader() вернется наш mock_instance
            mock_reader.return_value = mock_instance

            # 4. Запускаем функцию
            result = transaction_reader_in_csv(fake_path)

            # 5. Проверяем результат
            assert result == []

            # --- ГРУППА ТЕСТОВ: СЧИТЫВАНИЕ И ВАЛИДАЦИЯ XLSX ---


# 1. Функция успешного теста transaction_reader_in_xlsx (успешное чтение правильного xlsx файла
# - возврат списка словарей).
@patch("src.transaction_reader_in_csv_xlsx.pd.read_excel")
@patch("src.transaction_reader_in_csv_xlsx.Path.exists")
def test_successful_read_xlsx(mock_exists: MagicMock, mock_read_excel: MagicMock) -> None:
    mock_exists.return_value = True
    df = pd.DataFrame([{"id": 1, "amount": 100}])
    mock_read_excel.return_value = {"Sheet1": df}

    result = transaction_reader_in_xlsx(Path("valid.xlsx"))

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == {"id": 1, "amount": 100}


# 2. Функция успешного теста transaction_reader_in_xls (успешное чтение правильного xls файла
# - возврат списка словарей).
@patch("src.transaction_reader_in_csv_xlsx.pd.read_excel")
@patch("src.transaction_reader_in_csv_xlsx.Path.exists")
def test_successful_read_xls(mock_exists: MagicMock, mock_read_excel: MagicMock) -> None:
    mock_exists.return_value = True
    df = pd.DataFrame([{"id": 1, "amount": 100}])
    mock_read_excel.return_value = {"Sheet1": df}

    result = transaction_reader_in_xlsx(Path("valid.xls"))

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == {"id": 1, "amount": 100}


# 3. Функция неудачного теста transaction_reader_in_xlsx (по заданному пути файл не найден)
@patch("src.transaction_reader_in_csv_xlsx.Path.exists")
def test_file_not_found(mock_exists: MagicMock) -> None:
    mock_exists.return_value = False

    result = transaction_reader_in_xlsx(Path("fake_file.xlsx"))

    assert isinstance(result, str)
    assert "Файл не найден" in result  # Эта строчка кода буквально означает: «Проверь, содержится ли маленькая фраза
    # "Файл не найден" внутри большой строки result». Поскольку фраза там есть, Python считает это утверждение истинным
    # (True), и тест проходит. Полный текст ошибки зависит от имени файла (в данном случае fake_file.xlsx).
    # Если вы завтра решите изменить в тесте имя файла на test_data.xlsx, вам пришлось бы переписывать и строку assert.
    # Использование in избавляет от этого.


# 4. Функция неудачного теста transaction_reader_in_xlsx (у файла не соответсвующее расширение)
def test_unsupported_extension() -> None:
    with patch("src.transaction_reader_in_csv_xlsx.Path.exists", return_value=True):
        result = transaction_reader_in_xlsx(Path("data.txt"))

        assert isinstance(result, str)
        assert "Неподдерживаемый формат" in result


# 5. Функция неудачного теста transaction_reader_in_xlsx (файл сломан или поврежден)
@patch("src.transaction_reader_in_csv_xlsx.pd.read_excel")
@patch("src.transaction_reader_in_csv_xlsx.Path.exists")
def test_exception_handling_corrupted_file(mock_exists: MagicMock, mock_read_excel: MagicMock) -> None:
    mock_exists.return_value = True
    # Имитируем критический сбой парсера pandas (сломанный zip-архив)
    mock_read_excel.side_effect = Exception("Bad zip file")

    result = transaction_reader_in_xlsx(Path("corrupted.xlsx"))

    assert isinstance(result, str)
    assert "Ошибка при чтении файла" in result


# 6. Функция неудачного теста transaction_reader_in_xlsx (файл успешно прочитан, но все листы пустые)
@patch("src.transaction_reader_in_csv_xlsx.pd.read_excel")
@patch("src.transaction_reader_in_csv_xlsx.Path.exists")
def test_empty_file_returns_empty_list(mock_exists: MagicMock, mock_read_excel: MagicMock) -> None:

    mock_exists.return_value = True
    # Симулируем файл, в котором есть два листа, но оба абсолютно пустые
    mock_read_excel.return_value = {"Sheet1": pd.DataFrame(), "Sheet2": pd.DataFrame()}

    result = transaction_reader_in_xlsx(Path("empty_book.xlsx"))

    # Сверяем, что вернулся именно список, и он пуст
    assert isinstance(result, list)
    assert result == []
