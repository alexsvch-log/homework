import csv
from pathlib import Path
from typing import Literal

import pandas as pd


def transaction_reader_in_csv(file_path: Path) -> list[dict]:
    """Функция принимает на вход путь до csv-файла и возвращает список словарей с данными о финансовых транзакциях.
    Если файл пустой, содержит не список или не найден, функция возвращает пустой список.
    Если csv-файл пустой, содержит не-список или не найден, возвращается пустой список.
    Функция не проверяет считанный csv-файл на правильность информации по всем транзакциям
    (наличие всех ключей и т.п.)"""

    try:
        with open(file_path, encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=";")

            # Получаем список заголовков для универсальности
            headers = reader.fieldnames

            # Проверяем, если файл абсолютно пустой
            if not headers:
                print("Ошибка: Файл пустой или в нем нет строки заголовков.")
                return []

            # Проверяем на пустые названия колонок (например, ";;заголовок" или "id;;date")
            if None in headers or "" in headers:
                print("Ошибка: В файле обнаружены колонки без названия (пустые заголовки).")
                return []

            list_data = []
            for row in reader:
                # Проверяем, что строка прочиталась как словарь
                if not isinstance(row, dict):
                    continue

                # Проверяем, нет ли лишних «безымянных» колонок в самой строке данных, если есть, пропускаем
                if row.get(None) is not None:
                    print("Предупреждение: Пропущена строка с лишними неразмеченными данными.")
                    continue

                # Добавляем словарь в итоговый список (по условиям задачи нужен вывод в виде словаря)
                list_data.append(dict(row))

            return list_data

    except FileNotFoundError:
        print("Ошибка: Файл не найден.")
        return []
    except UnicodeDecodeError:
        print("Ошибка: Неверная кодировка файла. Ожидается UTF-8.")
        return []
    except csv.Error as e:  # Стандартное исключение встроенного модуля csv для ошибок структуры
        print(f"Ошибка: Нарушена структура CSV-таблицы ({e}).")
        return []


def transaction_reader_in_xlsx(file_path: Path) -> list[dict] | str:
    """Функция принимает на вход путь до xlsx-файла и возвращает список словарей с данными о финансовых транзакциях.
    Если файл пустой, содержит не список или не найден, функция возвращает пустой список.
    Если xlsx-файл пустой, содержит не-список или не найден, возвращается пустой список.
    Функция не проверяет считанный xlsx-файл на правильность информации по всем транзакциям
    (наличие всех ключей и т.п.)"""

    # 1. Если файл не существует
    if not file_path.exists():
        return f"Ошибка: Файл не найден по пути {file_path}"

    # 2. Если неверное расширение
    ext = file_path.suffix.lower()
    engine: Literal["openpyxl", "xlrd"]

    if ext == ".xlsx":
        engine = "openpyxl"
    elif ext == ".xls":
        engine = "xlrd"
    else:
        return f"Ошибка: Неподдерживаемый формат файла '{ext}'."

    try:
        # 3. Читаем листы
        excel_data = pd.read_excel(str(file_path), sheet_name=None, engine=engine)

        transactions_list = []

        # 4. Собираем данные
        sheet_name: str
        df: pd.DataFrame
        for sheet_name, df in excel_data.items():
            if df.empty:
                continue
            sheet_dicts = df.to_dict(orient="records")
            transactions_list.extend(sheet_dicts)

        # Возвращает список (он будет [], если все листы были пустые)
        return transactions_list

    except Exception as e:
        # 5. Если файл сломан или поврежден
        return f"Ошибка при чтении файла: {e}"
