from pathlib import Path

import pytest

# Импортируем декоратор и базовую функцию
from src.decorators import log
from src.processing import filter_by_state

# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ НАСТРОЕК ТЕСТА ---
FILENAME_SUCCESS: str = "test_success"
FILENAME_ERROR: str = "test_error"

# Пути к файлам логов в корне проекта
LOG_FILE_SUCCESS: Path = Path.cwd() / "logs" / f"{FILENAME_SUCCESS}.txt"
LOG_FILE_ERROR: Path = Path.cwd() / "logs" / f"{FILENAME_ERROR}.txt"


# ==============================================================================
# БЛОК 1: ТЕСТЫ С ЗАПИСЬЮ В ФАЙЛ (FILENAME ЗАДАН)
# ==============================================================================


def test_filter_by_state_file_success(capsys: pytest.CaptureFixture[str], list_for_processing: list) -> None:
    """Проверяет успешное логирование в файл при передаче имени файла."""
    if LOG_FILE_SUCCESS.exists():
        LOG_FILE_SUCCESS.unlink()  # Связка .exists() и .unlink() оеспечивает обязательное стриане файла перед тестом,
        # и в итоге проверяются только те логи, которые функция сгенерировала прямо сейчас.

    # Оборачиваем чистую функцию для записи в файл успешных логов
    func_to_test = log(filename=FILENAME_SUCCESS)(filter_by_state)  # альтернативный, способ применить декоратор
    # к функции без использования знака @. Удобен в тестах, когда нужно изменять входящие параметры декоратора.

    result = func_to_test(list_for_processing, state="EXECUTED")
    assert len(result) == 2

    # 1. Проверяем, что файл создался и наполнился
    assert LOG_FILE_SUCCESS.exists()
    file_content = LOG_FILE_SUCCESS.read_text(encoding="utf-8")
    assert "filter_by_state ok." in file_content
    assert "Result:" in file_content

    # 2. Убеждаемся с помощью capsys, что в консоли пусто
    captured = capsys.readouterr()
    assert captured.out == ""


def test_filter_by_state_file_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Проверяет запись TypeError в файл лога ошибок."""
    if LOG_FILE_ERROR.exists():
        LOG_FILE_ERROR.unlink()

    # Оборачиваем чистую функцию для записи ошибок в отдельный файл
    func_to_test = log(filename=FILENAME_ERROR)(filter_by_state)

    with pytest.raises(TypeError):
        func_to_test(12345, state="EXECUTED")

    # 1. Проверяем, что файл ошибок создался и содержит TypeError
    assert LOG_FILE_ERROR.exists()
    file_content = LOG_FILE_ERROR.read_text(encoding="utf-8")
    assert "filter_by_state error: TypeError" in file_content
    assert "Inputs: args=(12345,)" in file_content

    # 2. Консоль должна оставаться пустой
    captured = capsys.readouterr()
    assert captured.out == ""


# ==============================================================================
# БЛОК 2: ТЕСТЫ С ВЫВОДОМ В КОНСОЛЬ (FILENAME = NONE)
# ==============================================================================


def test_filter_by_state_console_success(capsys: pytest.CaptureFixture[str], list_for_processing: list) -> None:
    """Проверяет вывод успешного лога строго в консоль, когда filename=None."""
    # Оборачиваем чистую функцию с параметром None
    func_to_test = log(filename=None)(filter_by_state)

    result = func_to_test(list_for_processing, state="EXECUTED")
    assert len(result) == 2

    # С помощью capsys ловим то, что ушло в стандартный print()
    captured = capsys.readouterr()
    assert "Старт:" in captured.out
    assert "filter_by_state ok." in captured.out
    assert "Конец:" in captured.out

    # ПРИНУДИТЕЛЬНО ВЫВОДИМ РЕЗУЛЬТАТ НА ЭКРАН ДЛЯ ПРОСМОТРА
    print("\n--- ВИЗУАЛЬНЫЙ ТЕСТ УСПЕХА ---")
    print(captured.out)


def test_filter_by_state_console_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Проверяет вывод лога ошибки строго в консоль, когда filename=None."""
    # Оборачиваем чистую функцию с параметром None
    func_to_test = log(filename=None)(filter_by_state)

    with pytest.raises(TypeError):
        func_to_test(12345, state="EXECUTED")

    # Перехватываем вывод ошибки из консоли
    captured = capsys.readouterr()
    assert "filter_by_state error: TypeError" in captured.out
    assert "Inputs: args=(12345,)" in captured.out

    # ПРИНУДИТЕЛЬНО ВЫВОДИМ ОШИБКУ НА ЭКРАН ДЛЯ ПРОСМОТРА
    print("\n--- ВИЗУАЛЬНЫЙ ТЕСТ ОШИБКИ ---")
    print(captured.out)
