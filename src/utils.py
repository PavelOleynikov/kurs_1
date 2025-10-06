import json
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame
import logging


load_dotenv()  # загрузка переменных из .env-файла

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
log_file = os.path.join(log_dir, "utils.log")

logger = logging.getLogger("utils")  # создаем логер с именем модуля
logger.setLevel(logging.DEBUG)  # устанавливаем уровень логирования
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")  # путь записи логов
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)  # устанавливаем формат вывода логов
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def current_time_greeting() -> str:
    """функция возвращает приветствие исходя из времени суток"""

    user_datetime = datetime.now()  # актуальное время
    user_hour = user_datetime.hour  # актуальный час

    if 6 <= user_hour < 12:
        logger.info("актуальное время суток")
        return "Доброе утро"
    elif 12 <= user_hour < 18:
        logger.info("актуальное время суток")
        return "Добрый день"
    elif 18 <= user_hour < 23:
        logger.info("актуальное время суток")
        return "Добрый вечер"
    else:
        logger.info("актуальное время суток")
        return "Доброй ночи"


def get_slice_data(date_time: str) -> list[str]:
    """преобразует формат и возвращает список среза дат от 01 числа месяца до указанного"""

    dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")  # задаем входной формат
    start_month = dt.replace(day=1)  # получаем 1-е число месяца

    # возвращаем список дат периода ["01.01.2021 00:00:00", "15.01.2021 00:00:00"]
    logger.info("выбранный период дат для фильтрации")
    return [start_month.strftime("%d.%m.%Y %H:%M:%S"), dt.strftime("%d.%m.%Y %H:%M:%S")]


def get_cut_from_excel(path_to_file: str, period_date: list[str]) -> DataFrame:
    """читает файл xlsx и фильтрует операции за выбранный период"""

    logger.info(f"получение данных из файла {path_to_file}")
    df = pd.read_excel(path_to_file)  # читаем файл xlsx и получаем объект DataFrame

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)  # перевод строки в объект pd
    start_date = datetime.strptime(period_date[0], "%d.%m.%Y %H:%M:%S")
    end_date = datetime.strptime(period_date[1], "%d.%m.%Y %H:%M:%S")

    # фильтруем и получаем срез по интервалу дат
    filtered_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]

    # сортируем полученный срез по возрастанию даты
    sorted_df = filtered_df.sort_values(by="Дата операции", ascending=True)
    logger.info("список операций за выбранный период")
    return sorted_df


def get_card_with_spent(sorted_df: DataFrame) -> list[dict]:
    """функция возвращает список карт с расходами и кэшбэком"""

    dict_list = sorted_df.to_dict(orient="records")  # преобразуем sorted_df в список словарей

    operations_spent = []

    for el in dict_list:
        el["Сумма операции"] = int(el["Сумма операции"])
        if el["Сумма операции"] < 0:
            last_digits = str(el["Номер карты"].replace("*", ""))
            total_spent = el["Сумма операции с округлением"]
            cashback = round(total_spent / 100, 2)
            row = {"last_digits": last_digits, "total_spent": total_spent, "cashback": cashback}
            operations_spent.append(row)

    logger.info("список карт с расходами и кэшбэком")
    return operations_spent


def get_transactions_by_pay(sorted_df: DataFrame) -> list[dict]:
    """функция возвращает ТОП-5 транзакций по сумме платежа"""

    # сортируем df по убыванию суммы операции
    filtered_df = sorted_df.sort_values(by="Сумма операции", ascending=True)

    top_transactions = []
    for index, row in filtered_df.iterrows():
        date = row["Дата платежа"]
        amount = row["Сумма операции"]
        category = row["Категория"]
        description = row["Описание"]
        row = {"date": date, "amount": amount, "category": category, "description": description}
        top_transactions.append(row)

    top_5 = top_transactions[:5]

    logger.info("ТОП-5 транзакций по сумме платежа")
    return top_5


def get_currency_rates(path_to_file: str) -> list[dict]:
    """функция возвращает текущий курс заданных валют в рублях через внешний API"""

    api_key = os.getenv("API_KEY")  # Получение значения переменной API_KEY из .env-файла

    if not api_key:
        logger.error("API_KEY не найден")
        raise Exception("API_KEY не найден в переменных окружения")

    currency_rates = []
    logger.info(f"получение данных из файла {path_to_file}")
    with open(path_to_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        for cur in data["user_currencies"]:

            headers = {"apikey": api_key}
            url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={cur}&amount=1"

            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                logger.error(f"API error: {response.status_code}")
                raise Exception(f"API error: {response.status_code}")

            response_currency = response.json()
            currency = response_currency["query"]["from"]
            rate = round(response_currency["result"], 2)
            currency_rates.append({"currency": currency, "rate": rate})
    logger.info("текущий курс валют")
    return currency_rates


def get_stock_prices(path_to_file: str) -> list[dict]:
    """функция возвращает стоимость акций из S&P500 в рублях через внешний API"""

    api_key = os.getenv("API_KEY_TD")  # Получение значения переменной API_KEY из .env-файла

    if not api_key:
        logger.error("API_KEY не найден")
        raise Exception("API_KEY_TD не найден в переменных окружения")

    stock_prices = []
    logger.info(f"получение данных из файла {path_to_file}")
    with open(path_to_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        for stock in data["user_stocks"]:
            url = f"https://api.twelvedata.com/time_series?apikey={api_key}&symbol={stock}&interval=1min&format=JSON&dp=2"

            response = requests.get(url)

            if response.status_code != 200:
                logger.error(f"API error: {response.status_code}")
                raise Exception(f"API error: {response.status_code}")

            response_stocks = response.json()
            stock = response_stocks["meta"]["symbol"]
            price = round((float(response_stocks["values"][0]["open"])), 2)
            stock_prices.append({"stock": stock, "price": price})
    logger.info("текущая стоимость акций")
    return stock_prices
