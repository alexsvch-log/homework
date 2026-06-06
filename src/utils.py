import json

def list_of_input_transaction():
    """Функция принимает на вход путь до JSON-файла и возвращает список словарей с данными о финансовых транзакциях.
    Если файл пустой, содержит не список или не найден, функция возвращает пустой список. Файл с данными о финансовых
     транзациях operations.json находится в директорию data/ в корне проекта."""
    with open('operation.json') as file:
        data = json.load(file)

    print(data)  # data - словарь, тип dict

list_of_input_transaction()