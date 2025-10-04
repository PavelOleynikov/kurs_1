import json

from config import PATH_TO_EXCEL, PATH_TO_JSON
from src.utils import (current_time_greeting, get_card_with_spent, get_currency_rates, get_cut_from_excel,
                       get_slice_data, get_stock_prices, get_transactions_by_pay)


def main_page(date_str: str) -> dict[str, str | list[dict[str, str | float]]]:
    """функция получает дату и время и возвращает json-ответ с операциями за указанный период"""

    time_period = get_slice_data(date_str)  # выбранный период для фильтрации
    data_frame_cut = get_cut_from_excel(PATH_TO_EXCEL, time_period)  # срез операций за период по возрастанию

    # 1. Приветствие
    greeting = current_time_greeting()

    # 2. По каждой карте
    cards = get_card_with_spent(data_frame_cut)

    # 3. Топ-5 транзакций по сумме платежа
    top_5_transactions = get_transactions_by_pay(data_frame_cut)

    # 4. Курс валют.
    currency_rates = get_currency_rates(PATH_TO_JSON)

    # 5. Стоимость акций из S&P500.
    stock_prices = get_stock_prices(PATH_TO_JSON)

    result = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_5_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    json_result = json.dumps(result, ensure_ascii=False, indent=4)  # упорядоченный вывод json

    return json_result
