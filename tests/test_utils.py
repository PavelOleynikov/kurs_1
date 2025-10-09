import json
from unittest.mock import patch, Mock, mock_open

from pandas.core.interchange.dataframe_protocol import DataFrame

from src.utils import (
    current_time_greeting,
    get_slice_data,
    get_cut_from_excel,
    get_card_with_spent,
    get_transactions_by_pay,
    get_currency_rates,
    get_stock_prices,
)
from config import PATH_TO_EXCEL, PATH_TO_JSON
import pandas as pd


def test_current_time_greeting() -> None:
    """тест на корректность приветствия от времени суток"""

    assert current_time_greeting() == "Добрый вечер"  # результат меняется
    # в зависимости от времени суток


def test_get_slice_data() -> None:
    """тест на корректность возврата результата функции(список дат периода)"""

    assert get_slice_data("2021-05-15 15:30:00") == ["01.05.2021 15:30:00", "15.05.2021 15:30:00"]


def test_get_cut_from_excel(fixture_xlsx: DataFrame) -> None:
    """тест на проверку количества операций по выборке, корректность даты и суммы операции"""

    result = get_cut_from_excel(PATH_TO_EXCEL, ["01.05.2021 15:30:00", "02.05.2021 15:30:00"])

    assert len(result) == 6
    assert result["Дата операции"].iloc[0].strftime("%d.%m.%Y %H:%M:%S") == "01.05.2021 15:52:08"
    assert result["Сумма операции"].iloc[0] == float(-11.8)


def test_get_card_with_spent(dataframe: DataFrame) -> None:
    """Тест на корректность количества расходных операций"""

    result = get_card_with_spent(dataframe)
    assert len(result) == 3  # Только 3 операции с отрицательной суммой


def test_correct_card_number(dataframe: DataFrame) -> None:
    """Тест корректной обработки номера карты"""

    result = get_card_with_spent(dataframe)
    card_numbers = {item["last_digits"] for item in result}
    expected_numbers = {"1234567890", "9876543210"}
    assert card_numbers == expected_numbers


def test_correct_cashback(dataframe: DataFrame) -> None:
    """Тест корректного расчета кэшбэка"""

    result = get_card_with_spent(dataframe)
    for item in result:
        expected_cashback = round(item["total_spent"] / 100, 2)
        assert item["cashback"] == expected_cashback


def test_get_transactions_by_pay_five(dataframe: DataFrame) -> None:
    """Тест, что функция возвращает ровно 5 операций"""

    result = get_transactions_by_pay(dataframe)
    assert len(result) == 5


def test_transactions_sorted(dataframe: DataFrame) -> None:
    """Тест, что операции отсортированы корректно"""

    df = pd.DataFrame(dataframe)
    result = get_transactions_by_pay(df)
    amounts = [transaction["amount"] for transaction in result]
    expected_amounts = [-2500, -1000, -150, 300, 500]
    assert amounts == expected_amounts


@patch("requests.get")
@patch("os.getenv")
def test_get_currency_rates(mock_getenv=None, mock_requests=None):
    """тест успешного получения курса валют"""

    mock_getenv.return_value = "test_api_key"
    mock_file_data = {"user_currencies": ["USD", "EUR"]}

    # Создаем mock объект для response USD
    mock_response_usd = Mock()
    mock_response_usd.status_code = 200
    mock_response_usd.json.return_value = {"query": {"from": "USD"}, "result": 81.25}

    # Создаем mock объект для response EUR
    mock_response_eur = Mock()
    mock_response_eur.status_code = 200
    mock_response_eur.json.return_value = {"query": {"from": "EUR"}, "result": 93.95}

    # Настраиваем mock request для последовательных вызовов и получения mock response
    mock_requests.side_effect = [mock_response_usd, mock_response_eur]

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_file_data))):
        result = get_currency_rates(PATH_TO_JSON)

    expected_result = [{"currency": "USD", "rate": 81.25}, {"currency": "EUR", "rate": 93.95}]
    assert result == expected_result
    # Проверяем вызовы API
    assert mock_requests.call_count == 2


@patch("requests.get")
@patch("os.getenv")
def test_get_stock_prices_success_alternative(mock_getenv, mock_requests_get):
    """тест успешного получения цен акций"""

    mock_getenv.return_value = "test_api_key"
    mock_file_data = {"user_stocks": ["AAPL", "GOOGL"]}

    # Создаем mock объект для response AAPL
    mock_response_aapl = Mock()
    mock_response_aapl.status_code = 200
    mock_response_aapl.json.return_value = {"meta": {"symbol": "AAPL"}, "values": [{"open": "150.25"}]}

    # Создаем mock объект для response GOOGL
    mock_response_googl = Mock()
    mock_response_googl.status_code = 200
    mock_response_googl.json.return_value = {"meta": {"symbol": "GOOGL"}, "values": [{"open": "2750.80"}]}

    mock_requests_get.side_effect = [mock_response_aapl, mock_response_googl]

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_file_data))):
        result = get_stock_prices(PATH_TO_JSON)

    expected_result = [{"stock": "AAPL", "price": 150.25}, {"stock": "GOOGL", "price": 2750.80}]

    assert result == expected_result
    # Проверяем вызовы API
    assert mock_requests_get.call_count == 2
