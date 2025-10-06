import json
import logging
import os

import pandas as pd
import re
from config import PATH_TO_EXCEL


log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
log_file = os.path.join(log_dir, "services.log")

logger = logging.getLogger("services")  # создаем логер с именем модуля
logger.setLevel(logging.DEBUG)  # устанавливаем уровень логирования
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")  # путь записи логов
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)  # устанавливаем формат вывода логов
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

logger.info(f"получение данных из файла {PATH_TO_EXCEL}")
df = pd.read_excel(PATH_TO_EXCEL)  # читаем файл xlsx и получаем объект DataFrame
list_dict = df.to_dict(orient="records")  # преобразуем df в список словарей


def service_search(operations_list: list[dict], search: str) -> json:
    """функция фильтрации операций по строке поиска"""

    result = []
    pattern = re.compile(search, re.IGNORECASE)
    # компилированный (регистро-независимый) шаблон для поиска

    for operation in operations_list:
        category_ = operation.get("Категория", "")
        if category_ is not None and pattern.search(str(category_)):
            result.append(operation)
    # упорядоченный вывод json
    json_result = json.dumps(result, ensure_ascii=False, indent=4, sort_keys=True)
    logger.info("получен список операций по строке поиска")
    return json_result


if __name__ == "__main__":
    print(service_search(list_dict, "жкх"))
