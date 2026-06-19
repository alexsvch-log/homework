import re
from collections import Counter


def process_bank_search(data: list[dict], search: str) -> list[dict]:
    """Функция принимает список словарей с данными о банковских операциях и строку поиска,

    а возвращает список словарей, у которых в описании (категории) есть данная строка.
    Категории операций хранятся в поле description
    """

    # 1. Проверяем входные данные на корректность типов
    if data is None or not isinstance(data, list):
        print(f"Данные операций некорректны: {data}")
        return []

    if not isinstance(search, str):
        print(f"Поисковая строка должна быть текстом: {search}")
        return []

    # 2. Компилируем регулярное выражение.
    # Если search == "", паттерн будет успешно находить совпадение в любой строке.
    pattern = re.compile(re.escape(search), re.IGNORECASE)
    target_key: str = "description"

    # 3. Фильтруем список. Брак отсекается, а пустой поиск вернет все валидные транзакции.
    return [
        item
        for item in data
        if isinstance(item, dict) and isinstance(desc := item.get(target_key), str) and pattern.search(desc)
    ]


def process_bank_operations(data: list[dict], categories: list) -> dict:
    """Функция принимаетсписок словарей с данными о банковских операциях и список категорий операций,
    а возвращает словарь, в котором ключи — это названия категорий, а значения — это количество операций
    в каждой категории. Категории операций хранятся в поле description"""

    # 1. Проверяем входные данные на корректность
    if data is None or not isinstance(data, list):
        print(f"Данные операций некорректны: {data}")
        return {}

    if categories is None or not isinstance(categories, list):
        print(f"Список категорий некорректный: {categories}")
        return {}

    # Ключ, который отвечает за описание операции в банковских данных
    target_key: str = "description"

    # 2. Выбираем только те описания, которые есть в списке разрешенных категорий
    categories_set = set(categories)

    # 3. Фильтруем и собираем только валидные строки
    # Проверка isinstance(item, dict) защищает от падения, если внутри data лежит не словарь
    filtered_descriptions = [
        item[target_key]
        for item in data
        if isinstance(item, dict) and isinstance(item.get(target_key), str) and item[target_key] in categories_set
    ]

    # 4. Подсчитываем количество с помощью Counter и возвращаем dict
    return dict(Counter(filtered_descriptions))
