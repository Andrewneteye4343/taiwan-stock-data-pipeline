import pandas as pd

from src.database.query import get_latest_dividend_data


def test_get_latest_dividend_data():
    result = get_latest_dividend_data("2330")

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1

    assert list(result.columns) == [
        "symbol",
        "dividend_year",
        "cash_dividend",
        "ex_dividend_date",
        "payment_date",
    ]

    assert result.loc[0, "symbol"] == "2330"

def test_get_latest_dividend_data_unknown_symbol():
    result = get_latest_dividend_data("9999")

    assert isinstance(result, pd.DataFrame)
    assert result.empty

    assert list(result.columns) == [
        "symbol",
        "dividend_year",
        "cash_dividend",
        "ex_dividend_date",
        "payment_date",
    ]

def test_get_latest_dividend_data_without_dividend_record():
    result = get_latest_dividend_data("2454")

    assert isinstance(result, pd.DataFrame)
    assert result.empty

    assert list(result.columns) == [
        "symbol",
        "dividend_year",
        "cash_dividend",
        "ex_dividend_date",
        "payment_date",
    ]

def test_get_latest_dividend_data_returns_latest_year():
    result = get_latest_dividend_data("2330")

    assert len(result) == 1

    assert result.loc[0, "symbol"] == "2330"

    latest_year = result.loc[0, "dividend_year"]

    assert latest_year == 2027