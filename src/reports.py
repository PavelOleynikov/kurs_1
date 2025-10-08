from typing import Optional

import pandas as pd
from datetime import datetime
import logging
import os

from dateutil.relativedelta import relativedelta


log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
log_file = os.path.join(log_dir, "reports.log")

logger = logging.getLogger("reports")  # создаем логер с именем модуля
logger.setLevel(logging.DEBUG)  # устанавливаем уровень логирования
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")  # путь записи логов
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)  # устанавливаем формат вывода логов
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def write_to_file(filename=None):
    """Декоратор для функций-отчетов, который записывает в файл результат
    работы функции, формирующей отчет.
    Если задан filename, принимает имя файла в качестве параметра.
    """

    def decorator(func):
        """Возвращает обёртку, которая записывает в файл результат работы функции func"""

        def wrapper(*args, **kwargs):
            """Обёртка для выполнения функции func с записью её результата"""

            result = func(*args, **kwargs)
            if filename:
                file = open(filename, mode="w", encoding="utf-8")
                file.write(f"{result}\n")
                file.close()
            else:
                file = open("./data/report.txt", mode="w", encoding="utf-8")
                file.write(f"{result}\n")
                file.close()
            return result

        return wrapper

    logger.info("произведена запись результата работы функции в файл")
    return decorator


@write_to_file(filename="")  # запись результата в файл
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Функция возвращает траты по заданной категории за последние три месяца (от переданной даты).
    """

    if date is None:
        dt = datetime.now()  # актуальное время
    else:
        dt = datetime.strptime(date, "%d.%m.%Y")  # задаем входной формат
    start_month = dt - relativedelta(months=3)  # получаем дату начала трехмесячного периода

    # возвращаем список дат периода ["15.01.2020", "15.04.2020"]
    logger.info("задан период дат для фильтрации")
    time_period = [start_month.strftime("%d.%m.%Y"), dt.strftime("%d.%m.%Y")]

    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], dayfirst=True
    )  # перевод строки в объект pd
    start_date = datetime.strptime(time_period[0], "%d.%m.%Y")
    end_date = datetime.strptime(time_period[1], "%d.%m.%Y")

    # фильтруем и получаем срез по интервалу дат
    logger.info("получен срез операций по интервалу дат")
    filtered_df = transactions[
        (transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= end_date)
    ]

    list_dict = filtered_df.to_dict(orient="records")  # преобразуем df в список словарей
    result_by_category = []
    total_spend = 0
    for operation in list_dict:
        if operation["Категория"] == category:
            result_by_category.append(operation)
    for transaction in result_by_category:
        total_spend += transaction["Сумма операции с округлением"]
    result_pd = pd.DataFrame(result_by_category)  # преобразуем в DataFrame
    print(f"Траты по категории '{category}' {round(total_spend, 2)}")
    logger.info("получен список трат по категории")
    return result_pd
