from pathlib import Path

from src.added_functions import format_transactions_generator, get_optional_iso_date
from src.process_bank import process_bank_search
from src.processing import filter_by_state, sort_by_date
from src.transaction_reader_in_csv_xlsx import transaction_reader_in_csv, transaction_reader_in_xlsx
from src.utils import list_of_input_transaction


def main() -> None:
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями. ")

    # Находим базовую папку данных
    project_root = Path(__file__).resolve().parent
    data_dir = project_root / "data"

    # I . ВЫБОР ФАЙЛА ДЛЯ ПОЛУЧЕНИЯ ИНФОРМАЦИИ О ТРАНЗАКЦИЯХ
    # Получаем информацию от пользователя о формате исходного файла. Поскольку по условиям задачи пользователь
    # путь к файлу сам не задает, выбираем тот путь к файлу, который нам удобней. Все файлы лежат в директории проекта
    # 'data\file_name'
    # Переменная transactions: list[dict] - это изначальный список со словарями транзакций, из которого потом будет
    # формироваться новый список по запросу пользователя.
    # 1. Заранее объявляем переменную transactions с Union-типом для mypy
    transactions: list[dict] | str
    while True:
        choice_file = str(
            input(
                "Выберите необходимый пункт меню:\n"
                "1. Получить информацию о транзакциях из JSON-файла\n"
                "2. Получить информацию о транзакциях из CSV-файла\n"
                "3. Получить информацию о транзакциях из XLSX-файла\n"
                "   Что бы выйти из програмы нажмите 'Enter'\n __: "
            )
        )
        if choice_file == "1":
            file_path: Path = data_dir / "operations.json"  # Выбираем конкретный файл с расширением .json
            transactions = list_of_input_transaction(file_path)
            break  # Выходим из цикла выбора файла, так как файл успешно выбран
        elif choice_file == "2":
            file_path = data_dir / "transactions.csv"  # Выбираем конкретный файл с расширением .csv
            transactions = transaction_reader_in_csv(file_path)
            break  # Выходим из цикла выбора файла, так как файл успешно выбран
        elif choice_file == "3":
            file_path = data_dir / "transactions_excel.xlsx"  # Выбираем конкретный файл с расширением .xlsx
            transactions = transaction_reader_in_xlsx(file_path)
            break  # Выходим из цикла выбора файла, так как файл успешно выбран
        elif choice_file == "":
            print("До свидания!")
            return
        else:
            print("Неверный ввод. Пожалуйста, выберите пункт от 1 до 3 или нажмите Enter для выхода.\n")

    # Защитный барьер: если transactions — это строка (ошибка)
    # После этой проверки mypy на 100% уверен, что в transactions остался ТОЛЬКО список!
    if transactions is None or isinstance(transactions, str):
        if isinstance(transactions, str):
            print(f"Критическая ошибка при чтении файла: {transactions}")
        return
    # === КОНЕЦ БЛОКА ВЫБОРА ФАЙЛА ===

    # II . ВЫБОР СТАТУСА ТРАНЗАКЦИЙ ДЛЯ ФИЛЬТРАЦИИ
    # по условиям задачи можно выбрать транзакции только с одним статусом. Статус находится в словаре с параметрами
    # транзакции по ключу "state".
    # Создаем множество возможных статусов для более быстрой проверки. Вводимые статусы приводим к верхнему регистру,
    # поскольку функция фильтрации по ключу "state" этого не делает, а статусы приведены в исходном файле
    # заглавными буквами.
    # Интересно, хоть один пользователь поведется на это?.
    choice_status_set = {"EXECUTED", "CANCELED", "PENDING", ""}

    # Теперь нужно добиться от пользователя нужного статуса. Делаем цикл, вопрос задается до того момента,
    # пока пользователь не наберет ручками нужный статус.
    print("--- Настройка фильтра по статусу (нажмите Enter, чтобы пропустить) ---")
    while True:
        choice_status: str = input(
            "Введите статус, по которому необходимо выполнить фильтрацию.\n"
            "Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING.\n__:"
        ).upper()
        if choice_status not in choice_status_set:
            print(f"Статус операции {choice_status} недоступен.")
        else:
            break

    # делаем фильтрацию по статусу "state"
    if choice_status == "":
        print("Фильтрация по статусу пропущена.\n")
        filtered_transactions = transactions
    else:
        filtered_transactions = filter_by_state(transactions, choice_status)
        print(f"Операции отфильтрованы по статусу {choice_status}\n")

    # III . ВЫБОР ПЕРИОДА И ПОРЯДКА ВЫВОДА ДЛЯ ФИЛЬТРАЦИИ ТРАНЗАКЦИЙ
    # Пытаемся добиться от пользователя хочет ли он что-то от даты. В задании диалог максимально непонятен:
    # Программа: Отсортировать операции по дате? Да/Нет
    # Пользователь: да
    # Программа: Отсортировать по возрастанию или по убыванию?
    # Пользователь: по возрастанию/по убыванию
    # Может имеется в виду, что пользователь может задать период, за который ему транзакции выводить, тогда понятно.
    # Но кто ж так спрашивает?
    # Первый вопрос должен быть: Введите период, за который вы хотите посмотреть транзакциии:
    # 1. Введите начальную дату (ГГГГ-ММ-ДД):
    # 2. Введите конечную дату (ГГГГ-ММ-ДД):
    # Если период не задан (пользоватеь нажал Enter на все даты) - выводятся все заявленные транзакции за все даты
    # Если задано только начало или конец периода, то заявленные транзакции выводятся только на заданную дату.
    # Для ввода и перевода введенных дат в ISO формат пишем отдельную функцию
    # get_optional_iso_date(prompt_text) в модуле added_functions. Фильтр нужно потом вынести в отдельную функцию,
    # поскольку до этого мы ничего такого не писали.

    # Запрос дат у пользователя
    print("--- Настройка фильтра по датам (нажмите Enter, чтобы пропустить) ---")
    start_date = get_optional_iso_date("Введите начальную дату (ГГГГ-ММ-ДД): ")
    end_date = get_optional_iso_date("Введите конечную дату (ГГГГ-ММ-ДД): ")
    reverse_choice: str = input(
        "Если вы хотите вывести список по принципу 'сначала более поздние транзакции' (по убыванию), нажмите 'Enter'\n"
        "Если вы хотите вывести список по принципу 'сначала более ранние транзакции' (по возрастанию), нажмите '1' \n"
        "__:"
    )
    # Сначала поздние (убывание) -> reverse = True
    # Сначала ранние (возрастание) -> reverse = False
    if reverse_choice == "1":
        reverse: bool = False
    else:
        reverse = True

    # Вариант 1: Оба поля пустые -> Выводим всё
    if not start_date and not end_date:
        filtered_transactions = filtered_transactions
        print("\n[Все даты]: Выводятся все транзакции.")

    # Вариант 2: Заданы ОБЕ даты -> Фильтруем период (от и до)
    elif start_date and end_date:
        # Автоматически исправляем порядок, если пользователь перепутал даты местами
        actual_start = min(start_date, end_date)
        actual_end = max(start_date, end_date)
        # Берем первые 10 символов от даты транзакции (ГГГГ-ММ-ДД)
        filtered_transactions = [
            op
            for op in filtered_transactions
            if (tx_datetime := op.get("date")) and actual_start <= tx_datetime[:10] <= actual_end
        ]
        print(f"\n[Период]: Выводятся транзакции с {actual_start} по {actual_end}")

    # Вариант 3: Задана ТОЛЬКО ОДНА любая дата
    else:
        target_date = start_date if start_date else end_date

        # Проверяем, что дата транзакции начинается с введенной пользователем даты
        filtered_transactions = [
            op
            for op in filtered_transactions
            if (tx_datetime := op.get("date")) and tx_datetime.startswith(target_date)
        ]
        print(f"\n[Конкретный день]: Выводятся транзакции только за {target_date}")

    # Сортируем список сформированных транзакцй по возрастанию или убыванию в зависимости от выбора пользователя.
    filtered_transactions = sort_by_date(filtered_transactions, reverse)

    # IV . ВЫБОР ВАЛЮТЫ ДЛЯ ФИЛЬТРАЦИИ ТРАНЗАКЦИЙ
    # Узнаем у пользователя по какой валюте он хочет видеть транзакции. Данные нахдятся в словаре по ключу "code"
    # Заранее готовим set валют "RUB", "USD", "EUR". Поскольку в файлах разное содержимое (.csv, .xlsx, .json),
    # берем только три валюты. И еще даем вариант - если не вводит ни одну валюту, тогда по всем валютам.
    # Проблема в том, что в .json файле структура словаря валюты отличается от файлов .csv и .xlsx.
    # В JSON валюта «спрятана» внутри вложенного словаря operationAmount -> currency -> code,
    # а в CSV/XLSX лежит на поверхности в currency_code. Предварительно написанные функции не подходят,
    # к тому же генераторы здесь не нужны. Поэтому быстрее написать код фильтрации здесь.
    # Потом нужно вынести в отдельную функцию.
    print("\n--- Настройка фильтра по валюте (нажмите Enter, чтобы пропустить) ---")
    choice_currency_set = {"RUB", "USD", "EUR", ""}
    # Запускаем цикл, пока пользователь не введет корректное значение
    while True:
        choice_currency = (
            input(
                "Введите валюту, по которой транзакции должны быть включены в выборку.\n "
                "Доступные валюты: RUB, USD, EUR.\n__:"
            )
            .strip()
            .upper()
        )

        if choice_currency in choice_currency_set:
            break
        print("Ошибка! Доступны только валюты: RUB, USD, EUR или нажатие Enter. Попробуйте еще раз.")

    # Применяем универсальную фильтрацию, если пользователь выбрал валюту.
    # Функция, которую писали для домашки по фильтрации валют не подошла.
    if choice_currency:
        filtered_transactions = [
            op
            for op in filtered_transactions
            if (
                # Путь для JSON структуры
                (op.get("operationAmount", {}).get("currency", {}).get("code") == choice_currency)
                or
                # Путь для CSV/XLSX структуры
                (op.get("currency_code") == choice_currency)
            )
        ]
        print(f"[Валюта]: Выводятся транзакции только для {choice_currency}")
    else:
        print("[Все валюты]: Фильтр по валюте пропущен.")

    # V . ФИЛЬТРАЦИЯ ПО ТЕКСТУ ОПИСАНИЯ ТРАНЗАКЦИЙ
    # Настройка фильтра транзакций по заданному слову в описании
    # Ввод строки, по которой надо делать поиск (пользователь может задать любой текст, либо если строка пуста
    # (пользователь нажал Enter), фильтрация не производится.
    print("\n--- Настройка фильтра по описанию транзакций (нажмите Enter, чтобы пропустить)---")
    choice_description = input(
        "Введите текст описания, по которому транзакции должны быть включены в выборку.\n__:"
    ).lower()
    print(f"В выборку будут включены транзакции, содержащие в описании {choice_description}\n")

    # Применяем универсальную фильтрацию, если пользователь выбрал текст
    if choice_description:
        filtered_transactions = process_bank_search(filtered_transactions, choice_description)
        print(f" Выводятся транзакции, содержащие в описании '{choice_description}'")
    else:
        print("Фильтр по описанию пропущен.")

    # VI . ПОДСЧЕТ КОЛИЧЕСТВА ИТОГОВЫХ ТРАНЗАКЦИЙ

    counted_transaction = len(filtered_transactions)
    print(f"Всего банковских операций в выборке:{counted_transaction}")

    # VII . ФОРМИРОВАНИЕ КОНЕЧНОГО ВЫВОДА СПИСКА ТРАНЗАКЦИЙ С УЧЕТОМ ФИЛЬТРОВ.
    # Условия: номера счетов и карт должны быть замаскированы, дата выводится в формате ДД.ММ.ГГГ
    # Что бы не засорять функцию main() пришлось написать отдельно генератор для форматирования вывода.
    # Генератор, который писали для домашки не подошел.
    if not filtered_transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации.")
        return

    # Создаем генератор
    transactions_output = format_transactions_generator(filtered_transactions)

    # Итератор поочередно забирает отформатированные блоки и печатает их
    for txt_block in transactions_output:
        print(txt_block)

    return


if __name__ == "__main__":
    main()
