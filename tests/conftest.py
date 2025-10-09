from datetime import datetime

import pandas as pd
import pytest
from pandas.core.interchange.dataframe_protocol import DataFrame

from config import PATH_TO_EXCEL


@pytest.fixture
def fixture_xlsx() -> DataFrame:
    df = pd.read_excel(PATH_TO_EXCEL)
    return df


@pytest.fixture
def dataframe() -> DataFrame:
    """Фикстура с тестовыми данными"""
    data = {
        "Дата операции": [
            datetime(2021, 1, 1),
            datetime(2021, 1, 2),
            datetime(2021, 1, 3),
            datetime(2021, 1, 4),
            datetime(2021, 1, 5),
        ],
        "Дата платежа": ["2021-01-01", "2021-01-02", "2021-01-03", "2021-01-04", "2021-01-05"],
        "Сумма операции": [-1000, 500, -2500, -150, 300],
        "Сумма операции с округлением": [1000.0, 500.0, 2500.0, 150.0, 300.0],
        "Номер карты": [
            "123456******7890",
            "123456******7890",
            "987654******3210",
            "123456******7890",
            "987654******3210",
        ],
        "Категория": ["Супермаркеты", "Пополнения", "Транспорт", "Различные товары", "Зарплата"],
        "Описание": ["Магнит", "Т-Банк", "Метро", "Zhenskiy Trikotazh", "ООО-GDL"],
    }
    return pd.DataFrame(data)
