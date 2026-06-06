from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional


def log(filename: Optional[str] = None) -> Callable[..., Any]:
    """Декоратор будет автоматически логировать начало и конец выполнения функции, а также ее результаты
    или возникшие ошибки.
    Декоратор должен принимать необязательный аргумент filename, который определяет, куда будут записываться логи
    (в файл или в консоль):
    Если filename задан, логи записываются в указанный файл. Если
    filename не задан, логи выводятся в консоль.
    Логирование должно включать:
    Дату и время начала работы функци, имя функции, результат выполнения при успешной операции, дату и время
    завершения работы функции.
    Дату и время начала работы функци, имя функции, тип возникшей ошибки и входные параметры, если выполнение функции
    привело к ошибке, дату и время завершения работы функции."""

    def log_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name = func.__name__
            start_time = datetime.now()
            start_str = start_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            target_file = None
            if filename:
                logs_dir = Path.cwd() / "logs"  # метод возвращает абсолютный путь к папке,
                # из которой была запущена программа или тест.
                logs_dir.mkdir(exist_ok=True)  # Флаг exist_ok=True проверяет, создана ли уже папка "logs". Если да,
                # то код выполняется дальше и метод mkdir() не выдает ошибки.
                target_file = logs_dir / f"{filename}.txt"  # Формирует финальный путь к конкретному текстовому файлу,
                # в который декоратор будет записывать информацию. В переменной target_file оказывается точный и полный
                # адрес файла на компьютере. Адрес затем передается в команду with open(target_file, 'a').

            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()
                end_str = end_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                message = f"{func_name} ok. Result: {result}"
                log_msg = f"Старт: {start_str}\n" f"{message}\n" f"Конец: {end_str}\n"

                if target_file:
                    with open(target_file, "a", encoding="utf-8") as file:
                        file.write(log_msg)
                else:
                    print(log_msg, end="")

                return result

            except Exception as e:
                # Фиксируем точное время, когда произошла ошибка
                error_time = datetime.now()
                error_str = error_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                error_type = type(e).__name__

                # Добавляем блоки "Старт" и "Конец" в сообщение об ошибке
                error_msg = (
                    f"Старт: {start_str}\n"
                    f"{func_name} error: {error_type} ({e}).\n"
                    f"Inputs: args={args}, kwargs={kwargs}\n"
                    f"Конец (ошибка): {error_str}\n"
                )

                if target_file:
                    with open(target_file, "a", encoding="utf-8") as file:
                        file.write(error_msg)
                else:
                    print(error_msg, end="")

                raise e

        return wrapper

    return log_decorator
