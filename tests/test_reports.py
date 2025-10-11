from datetime import datetime

import pytest
from pandas.core.interchange.dataframe_protocol import DataFrame

from src.reports import spending_by_category


def test_spending_by_category(dataframe: DataFrame) -> None:
    """тест на корректность фильтрации трат по заданной категории"""

    result = spending_by_category(dataframe, "Супермаркеты", "05.01.2021")
    assert len(result) == 1
    assert result.iloc[0]["Категория"] == "Супермаркеты"
    assert result.iloc[0]["Описание"] == "Магнит"
    assert result.iloc[0]["Сумма операции"] == -1000
    assert result.iloc[0]["Дата операции"] == datetime(2021, 1, 1)


@pytest.mark.parametrize(
    "category, description, test_date",
    [
        ("Пополнения", "Т-Банк", "02.01.2021"),
        ("Транспорт", "Метро", "03.01.2021"),
    ],
)
def test_spending_by_category_param(dataframe: DataFrame,
                                    category: str,
                                    description: str,
                                    test_date: str) -> None:
    """параметризованный тест фильтрации трат по категории"""

    result = spending_by_category(dataframe, category, test_date)

    assert result.iloc[0]["Описание"] == description
    assert result.iloc[0]["Категория"] == category
