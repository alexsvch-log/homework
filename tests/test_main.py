from typing import Any

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

import main


# Передаем строго: выбор меню, имя функции
@pytest.mark.parametrize(
    "menu_choice, target_function_name",
    [("1", "list_of_input_transaction"), ("2", "transaction_reader_in_csv"), ("3", "transaction_reader_in_xlsx")],
)
def test_main_handles_different_formats(
    monkeypatch: MonkeyPatch, capsys: CaptureFixture[str], menu_choice: str, target_function_name: str
) -> None:
    # 1. Формируем список ответов
    user_responses = [
        menu_choice,  # Сюда прилетит "1", "2" или "3"
        "EXECUTED",  # Фильтры
        "2018-02-01",  # Введите начальную дату (ГГГГ-ММ-ДД)
        "2019-02-01",  # Введите конечную дату (ГГГГ-ММ-ДД)
        "",  # Сначала поздние (убывание)
        "RUB",  # Валюта (в fake_data у вас RUR, ниже мы это исправим на RUB)
        "",  # Финальный пустой ввод, если программа его ждет
    ]

    # Подменяем input
    monkeypatch.setattr("builtins.input", lambda _: user_responses.pop(0))

    # 2. Создаем фейковые данные для фильтрации (добавили описание, карту и исправили RUR на RUB)
    fake_data = [
        {
            "id": 879660146,
            "state": "EXECUTED",
            "date": "2018-07-22T07:42:32.953324",
            "operationAmount": {
                "amount": "92130.50",
                "currency": {
                    "name": "руб.",
                    "code": "RUB",  # Исправили RUR на RUB, чтобы совпало с фильтром пользователя
                },
            },
            "description": "Перевод организации",
            "from": "Счет 19628854383215954147",
            "to": "Счет 90887717138446397473",
        }
    ]

    was_called = False

    def fake_reader(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        nonlocal was_called
        was_called = True
        return fake_data

    # 3. Подменяем функции внутри пространства имен самого main
    monkeypatch.setattr(main, target_function_name, fake_reader)

    # 4. Запускаем main()
    main.main()

    # 5. Проверяем вызов
    assert was_called is True, f"Функция {target_function_name} не была вызвана"

    # 6. Проверяем вывод на экран (ищем именно те данные, которые лежат в fake_data)
    captured = capsys.readouterr()

    # Защищаем тест от падения из-за пробелов, проверяя ключевые элементы по отдельности:
    assert "22.07.2018" in captured.out
    assert "92130.50" in captured.out
    assert "Перевод организации" in captured.out


def test_main_exit_immediately(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    # Пользователь сразу нажал Enter
    user_responses = [""]
    monkeypatch.setattr("builtins.input", lambda _: user_responses.pop(0))

    # Запускаем main — он должен мгновенно завершиться
    main.main()

    captured = capsys.readouterr()
    assert "До свидания!" in captured.out


def test_main_invalid_menu_choice(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    # Сначала вводим "5" (ошибка), а затем "" (выход)
    user_responses = ["5", ""]
    monkeypatch.setattr("builtins.input", lambda _: user_responses.pop(0))

    main.main()

    captured = capsys.readouterr()
    # Проверяем, что текст из ветки else вывелся на экран
    assert "Неверный ввод. Пожалуйста, выберите пункт от 1 до 3" in captured.out
    assert "До свидания!" in captured.out


def test_main_with_empty_transactions(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    # 1. Передаем точно такие же работающие ответы пользователей, как в успешном тесте
    user_responses = [
        "1",  # Выбор JSON
        "EXECUTED",  # Статус
        "2018-02-01",  # Начальная дата
        "2019-02-01",  # Конечная дата
        "",  # Сортировка
        "RUB",  # Валюта
        "",  # Финал (если есть)
    ]
    monkeypatch.setattr("builtins.input", lambda _: user_responses.pop(0))

    # 2. Подменяем функцию чтения так, чтобы она вернула пустой список
    # Программа попытается отфильтровать этот пустой список и на выходе получит 0 результатов
    monkeypatch.setattr(main, "list_of_input_transaction", lambda *args, **kwargs: [])

    # 3. Запускаем main()
    main.main()

    # 4. Проверяем, что программа вежливо сообщила о пустом результате
    captured = capsys.readouterr()

    # Склеиваем пробелы, чтобы тест не упал из-за случайных отступов в консоли
    clean_output = captured.out.replace(" ", "")

    assert "Всегобанковскихоперацийввыборке:0" in clean_output
    assert "Ненайденониоднойтранзакции" in clean_output
