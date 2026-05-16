# файл: tests/test_processing.py

# Импортируем функции, код которых нужно протестировать
from src.processing import filter_by_state, sort_by_date


# Функция теста с использованием фикстуры list_for_processing
def test_filter_by_state(list_for_processing: list) -> None:
    # Проверка: ожидаемый результат == фактический
    assert filter_by_state(
        list_for_processing,
        "CANCELED",
    ) == [
        {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
    ]
    assert filter_by_state(list_for_processing) == [
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
    ]


# Функция теста с использованием фикстуры list_for_processing
def test_sort_by_date(list_for_processing: list) -> None:
    # Проверка: ожидаемый результат == фактический
    assert sort_by_date(
        list_for_processing,
        False,
    ) == [
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
        {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
    ]
    assert sort_by_date(list_for_processing) == [
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
        {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
    ]
